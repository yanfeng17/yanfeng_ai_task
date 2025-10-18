"""Base entity for Yanfeng AI Task integration."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

import aiohttp
import voluptuous as vol
from voluptuous_openapi import convert

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import device_registry as dr, llm
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import EntityPlatform

from .const import (
    CONF_CHAT_MODEL,
    CONF_CUSTOM_CHAT_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DOMAIN,
    LOGGER,
    RECOMMENDED_CHAT_MODEL,
)
from .helpers import ModelScopeAPIClient, format_messages_for_modelscope

ERROR_GETTING_RESPONSE = "Error getting response from ModelScope"

# Max number of tool iterations to prevent infinite loops
MAX_TOOL_ITERATIONS = 10


def _format_tool(tool: llm.Tool, custom_serializer: Any | None) -> dict[str, Any]:
    """Format HA tool to OpenAI/ModelScope compatible format."""
    tool_spec = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
        }
    }

    # Convert parameters schema if provided
    if tool.parameters and tool.parameters.schema:
        try:
            # Use voluptuous_openapi to convert schema
            schema = convert(tool.parameters, custom_serializer=custom_serializer)
            tool_spec["function"]["parameters"] = schema
            LOGGER.debug("Converted tool %s parameters: %s", tool.name, schema)
        except Exception as err:
            LOGGER.warning("Failed to convert parameters for tool %s: %s", tool.name, err)
            # Fallback to empty parameters
            tool_spec["function"]["parameters"] = {
                "type": "object",
                "properties": {},
            }

    return tool_spec


class YanfengAIBaseEntity:
    """Base entity for Yanfeng AI Task."""

    def __init__(self, entry: ConfigEntry, subentry: ConfigSubentry) -> None:
        """Initialize the entity."""
        self.entry = entry
        self.subentry = subentry
        self._attr_name = subentry.title
        self._attr_unique_id = subentry.subentry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=subentry.title,
            manufacturer="Yanfeng",
            model="AI Task Integration",
            sw_version="2.1.0",
            entry_type=dr.DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.entry.runtime_data is not None

    @property
    def session(self) -> aiohttp.ClientSession:
        """Return the HTTP session."""
        return self.entry.runtime_data

    @property
    def api_key(self) -> str:
        """Return the API key."""
        return self.entry.data[CONF_API_KEY]

    @property
    def client(self) -> ModelScopeAPIClient:
        """Return the ModelScope API client."""
        return ModelScopeAPIClient(self.session, self.api_key)

    def _get_option(self, key: str, default: Any = None) -> Any:
        """Get option from subentry data."""
        return self.subentry.data.get(key, default)


class YanfengAILLMBaseEntity(YanfengAIBaseEntity):
    """Base entity for LLM-based entities."""

    async def _async_handle_chat_log(
        self,
        chat_log: conversation.ChatLog,
        structure: dict[str, Any] | None = None,
    ) -> None:
        """Handle a chat log by calling the ModelScope API with function calling support."""

        # Get configuration
        # Priority: custom_chat_model > chat_model > default
        custom_model = self._get_option(CONF_CUSTOM_CHAT_MODEL)
        if custom_model and custom_model.strip():
            model = custom_model.strip()
            LOGGER.debug("Using custom chat model: %s", model)
        else:
            model = self._get_option(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)
            LOGGER.debug("Using predefined chat model: %s", model)

        temperature = self._get_option(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
        top_p = self._get_option(CONF_TOP_P, DEFAULT_TOP_P)
        max_tokens = self._get_option(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)
        prompt = self._get_option(CONF_PROMPT, DEFAULT_PROMPT)

        # Extract tools from chat_log if available
        tools = None
        custom_serializer = llm.selector_serializer
        if chat_log.llm_api:
            tools = [
                _format_tool(tool, chat_log.llm_api.custom_serializer)
                for tool in chat_log.llm_api.tools
            ]
            custom_serializer = chat_log.llm_api.custom_serializer
            LOGGER.info("Extracted %d tools from chat_log.llm_api", len(tools))

        # Iterate up to MAX_TOOL_ITERATIONS to handle tool calls
        for iteration in range(MAX_TOOL_ITERATIONS):
            LOGGER.debug("Tool calling iteration %d/%d", iteration + 1, MAX_TOOL_ITERATIONS)

            # Prepare messages from chat_log
            messages = self._prepare_messages_from_chat_log(chat_log, prompt, structure, custom_serializer)

            LOGGER.debug("Sending %d messages to ModelScope (iteration %d)", len(messages), iteration + 1)
            LOGGER.debug("Message roles: %s", [msg.get("role") for msg in messages])

            try:
                # Call ModelScope API with tools
                response = await self.client.generate_text(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    tools=tools,
                )

                LOGGER.debug("Received ModelScope response (iteration %d): %s", iteration + 1, response)

                # Extract response
                if "choices" not in response or not response["choices"]:
                    LOGGER.error("Empty response from ModelScope API: %s", response)
                    from homeassistant.exceptions import HomeAssistantError
                    raise HomeAssistantError(ERROR_GETTING_RESPONSE)

                choice = response["choices"][0]
                message = choice.get("message", {})

                # Check for tool calls
                tool_calls = message.get("tool_calls")
                content = message.get("content")
                finish_reason = choice.get("finish_reason")

                # Handle edge case: finish_reason='tool_calls' but tool_calls is None
                # This can happen with VL models that don't fully support function calling
                if finish_reason == "tool_calls" and not tool_calls:
                    LOGGER.error(
                        "Model returned finish_reason='tool_calls' but tool_calls is None. "
                        "This usually means the model doesn't fully support function calling. "
                        "Consider using Qwen/Qwen2.5-72B-Instruct instead of VL models."
                    )
                    # Treat as final response with empty content
                    assistant_content = conversation.AssistantContent(
                        agent_id=self.entry.entry_id,
                        content="抱歉，我遇到了一个问题。请尝试切换到 Qwen/Qwen2.5-72B-Instruct 模型以获得更好的设备控制支持。"
                    )
                    chat_log.content.append(assistant_content)
                    break

                # Add assistant message to chat_log
                if tool_calls:
                    # Model wants to call tools
                    LOGGER.info("Model requested %d tool calls", len(tool_calls))

                    # Convert to HA ToolInput format
                    ha_tool_calls = []
                    for tool_call in tool_calls:
                        function = tool_call.get("function", {})
                        tool_name = function.get("name")
                        tool_args = function.get("arguments", {})

                        # Parse arguments if it's a string
                        if isinstance(tool_args, str):
                            import json
                            try:
                                tool_args = json.loads(tool_args)
                            except json.JSONDecodeError as err:
                                LOGGER.error("Failed to parse tool arguments: %s", err)
                                tool_args = {}

                        ha_tool_calls.append(
                            llm.ToolInput(tool_name=tool_name, tool_args=tool_args)
                        )

                    # Add assistant content with tool calls
                    assistant_content = conversation.AssistantContent(
                        agent_id=self.entry.entry_id,
                        content=content or "",  # Content may be empty when calling tools
                        tool_calls=ha_tool_calls,
                    )
                    chat_log.content.append(assistant_content)

                    # Execute tools via HA's conversation system
                    if chat_log.llm_api:
                        for i, tool_call_input in enumerate(ha_tool_calls):
                            try:
                                # Get the tool_call_id from the original response
                                tool_call_id = tool_calls[i].get("id", f"call_{i}")

                                # Execute the tool
                                tool_result = await chat_log.llm_api.async_call_tool(tool_call_input)

                                # Add tool result to chat_log with required parameters
                                tool_result_content = conversation.ToolResultContent(
                                    agent_id=self.entry.entry_id,
                                    tool_call_id=tool_call_id,
                                    tool_name=tool_call_input.tool_name,
                                    tool_result=tool_result,
                                )
                                chat_log.content.append(tool_result_content)

                                LOGGER.debug("Tool %s executed successfully", tool_call_input.tool_name)

                            except Exception as err:
                                LOGGER.error("Error executing tool %s: %s", tool_call_input.tool_name, err)
                                # Add error result with required parameters
                                tool_call_id = tool_calls[i].get("id", f"call_{i}") if i < len(tool_calls) else f"call_{i}"
                                error_result = conversation.ToolResultContent(
                                    agent_id=self.entry.entry_id,
                                    tool_call_id=tool_call_id,
                                    tool_name=tool_call_input.tool_name,
                                    tool_result={"error": str(err)},
                                )
                                chat_log.content.append(error_result)

                    # Continue loop to send tool results back to model
                    continue

                else:
                    # No tool calls, final response
                    if content:
                        assistant_content = conversation.AssistantContent(
                            agent_id=self.entry.entry_id,
                            content=content
                        )
                        chat_log.content.append(assistant_content)
                        LOGGER.debug("Added final assistant response to chat_log")
                    else:
                        LOGGER.warning("Empty content in final response")

                    # Done, exit loop
                    break

            except conversation.ConverseError:
                # Re-raise ConverseError as-is
                raise
            except Exception as err:
                LOGGER.error("Error calling ModelScope API (iteration %d): %s", iteration + 1, err, exc_info=True)
                from homeassistant.exceptions import HomeAssistantError
                raise HomeAssistantError(f"Error calling ModelScope API: {err}") from err

        else:
            # Reached MAX_TOOL_ITERATIONS without finishing
            LOGGER.warning("Reached maximum tool iterations (%d), stopping", MAX_TOOL_ITERATIONS)

    def _prepare_messages_from_chat_log(
        self,
        chat_log: conversation.ChatLog,
        prompt: str | None,
        structure: dict[str, Any] | None,
        custom_serializer: Any,
    ) -> list[dict[str, Any]]:
        """Prepare messages list from chat_log content."""
        messages = []

        # Process chat_log content
        for content in chat_log.content:
            if isinstance(content, conversation.SystemContent):
                # Add system content from HA
                messages.append({"role": "system", "content": content.content})
                LOGGER.debug("Added SystemContent: %d chars", len(content.content))

            elif isinstance(content, conversation.UserContent):
                # Add user message
                if content.attachments:
                    # Multi-modal content with images
                    message_content = []
                    if content.content:
                        message_content.append({"type": "text", "text": content.content})

                    # Add image attachments
                    for attachment in content.attachments:
                        import base64
                        try:
                            with open(attachment.path, 'rb') as img_file:
                                image_data = base64.b64encode(img_file.read()).decode('utf-8')
                                message_content.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{attachment.mime_type};base64,{image_data}"
                                    }
                                })
                        except Exception as err:
                            LOGGER.error("Failed to read image %s: %s", attachment.path, err)

                    messages.append({"role": "user", "content": message_content})
                else:
                    # Simple text message
                    messages.append({"role": "user", "content": content.content})

            elif isinstance(content, conversation.AssistantContent):
                # Add assistant message
                message = {"role": "assistant"}

                if content.content:
                    message["content"] = content.content

                # Add tool calls if present
                if content.tool_calls:
                    message["tool_calls"] = [
                        {
                            "id": f"call_{i}",
                            "type": "function",
                            "function": {
                                "name": tc.tool_name,
                                "arguments": tc.tool_args if isinstance(tc.tool_args, str) else str(tc.tool_args),
                            }
                        }
                        for i, tc in enumerate(content.tool_calls)
                    ]

                messages.append(message)

            elif isinstance(content, conversation.ToolResultContent):
                # Add tool result as a tool message
                # OpenAI format expects tool messages with tool_call_id
                messages.append({
                    "role": "tool",
                    "name": content.tool_name,
                    "content": str(content.tool_result) if content.tool_result else "{}",
                })
                LOGGER.debug("Added tool result for %s", content.tool_name)

        # Add custom prompt if no system content yet
        has_system_content = any(isinstance(c, conversation.SystemContent) for c in chat_log.content)
        if prompt and not has_system_content:
            messages.insert(0, {"role": "system", "content": prompt})

        # Add structure prompt if needed
        if structure:
            structure_prompt = self._format_structure_prompt(structure, custom_serializer)
            messages.append({"role": "system", "content": structure_prompt})

        return messages

    def _format_structure_prompt(self, structure: dict[str, Any], custom_serializer: Any) -> str:
        """Format structure requirements into a prompt."""
        prompt_parts = [
            "Please respond with a JSON object that matches the following structure:"
        ]

        # Handle voluptuous Schema objects
        if hasattr(structure, 'schema'):
            # It's a voluptuous Schema object - convert using voluptuous_openapi
            try:
                schema_dict = convert(structure, custom_serializer=custom_serializer)
            except Exception as err:
                LOGGER.warning("Failed to convert schema: %s", err)
                schema_dict = structure.schema if isinstance(structure.schema, dict) else {}

            LOGGER.debug("Processing voluptuous Schema: %s", schema_dict)

            for key, value in schema_dict.items():
                field_name = str(key)
                description = ""
                if isinstance(value, dict) and "description" in value:
                    description = value["description"]

                field_desc = f"- {field_name}"
                if description:
                    field_desc += f": {description}"

                prompt_parts.append(field_desc)
        elif isinstance(structure, dict):
            # It's a regular dictionary
            for field_name, field_info in structure.items():
                field_type = field_info.get("type", "string") if isinstance(field_info, dict) else "string"
                description = field_info.get("description", "") if isinstance(field_info, dict) else str(field_info)
                required = field_info.get("required", False) if isinstance(field_info, dict) else False

                field_desc = f"- {field_name} ({field_type})"
                if required:
                    field_desc += " [REQUIRED]"
                if description:
                    field_desc += f": {description}"

                prompt_parts.append(field_desc)
        else:
            # Unknown structure format, convert to string
            LOGGER.warning("Unknown structure format: %s", type(structure))
            prompt_parts.append(f"Structure: {structure}")

        prompt_parts.append("\nRespond only with valid JSON, no additional text.")

        return "\n".join(prompt_parts)

    def _extract_response_text(self, response: dict[str, Any]) -> str:
        """Extract text content from ModelScope API response."""
        try:
            if "choices" in response and response["choices"]:
                choice = response["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
            
            # Fallback for direct output format
            if "output" in response and "text" in response["output"]:
                return response["output"]["text"]
            
            LOGGER.error("Unable to extract text from response: %s", response)
            return ""
            
        except (KeyError, IndexError, TypeError) as err:
            LOGGER.error("Error extracting response text: %s", err)
            return ""