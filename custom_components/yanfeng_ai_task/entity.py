"""Base entity for Yanfeng AI Task integration."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

import aiohttp

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import EntityPlatform

from .const import (
    CONF_CHAT_MODEL,
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


class YanfengAIBaseEntity:
    """Base entity for Yanfeng AI Task."""

    def __init__(self, entry: ConfigEntry, subentry: ConfigSubentry | None = None) -> None:
        """Initialize the entity."""
        self.entry = entry
        self.subentry = subentry

        # Set unique_id based on subentry
        if subentry:
            self._attr_unique_id = subentry.subentry_id
            # Each subentry gets its own device
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, subentry.subentry_id)},
                name=subentry.title,
                manufacturer="Yanfeng",
                model="AI Task Integration",
                sw_version="1.0.4",
            )
        else:
            # This shouldn't happen with the new architecture, but keep for safety
            self._attr_unique_id = entry.entry_id
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, entry.entry_id)},
                name=entry.title,
                manufacturer="Yanfeng",
                model="AI Task Integration",
                sw_version="1.0.4",
            )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        if self.subentry:
            return self.subentry.title
        return self.entry.title

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
        """Get option from subentry or entry options."""
        if self.subentry:
            return self.subentry.data.get(key, default)
        return self.entry.options.get(key, default)


class YanfengAILLMBaseEntity(YanfengAIBaseEntity):
    """Base entity for LLM-based entities."""

    async def _async_handle_chat_log(
        self,
        chat_log: conversation.ChatLog,
        structure: dict[str, Any] | None = None,
    ) -> None:
        """Handle a chat log by calling the ModelScope API."""

        # Get configuration
        model = self._get_option(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)
        temperature = self._get_option(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
        top_p = self._get_option(CONF_TOP_P, DEFAULT_TOP_P)
        max_tokens = self._get_option(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)
        prompt = self._get_option(CONF_PROMPT, DEFAULT_PROMPT)

        # Prepare messages
        messages = []

        # Add system prompt
        if prompt:
            messages.append({"role": "system", "content": prompt})

        # Add structure prompt if needed
        if structure:
            structure_prompt = self._format_structure_prompt(structure)
            messages.append({"role": "system", "content": structure_prompt})

        # Add conversation history
        for content in chat_log.content:
            if isinstance(content, conversation.UserContent):
                # Check if there are attachments (images)
                if content.attachments:
                    # Build multi-modal message with text and images
                    message_content = []

                    # Add text content
                    if content.content:
                        message_content.append({
                            "type": "text",
                            "text": content.content
                        })

                    # Add image attachments
                    for attachment in content.attachments:
                        # Read image file and convert to base64
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
                                LOGGER.debug("Added image attachment: %s (mime: %s)",
                                           attachment.path, attachment.mime_type)
                        except Exception as err:
                            LOGGER.error("Failed to read image attachment %s: %s",
                                       attachment.path, err)

                    messages.append({"role": "user", "content": message_content})
                else:
                    # Simple text message
                    messages.append({"role": "user", "content": content.content})
            elif isinstance(content, conversation.AssistantContent):
                messages.append({"role": "assistant", "content": content.content})

        # Ensure we have at least one user message
        if not any(msg.get("role") == "user" for msg in messages):
            LOGGER.error("No user message found in chat_log")
            from homeassistant.exceptions import HomeAssistantError
            raise HomeAssistantError("No user message found in conversation")

        # Format messages for ModelScope
        formatted_messages = format_messages_for_modelscope(messages)

        LOGGER.debug("Sending messages to ModelScope: %s", formatted_messages)
        LOGGER.debug("Using model: %s, temperature: %s, top_p: %s, max_tokens: %s",
                    model, temperature, top_p, max_tokens)

        try:
            # Call ModelScope API
            response = await self.client.generate_text(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )

            LOGGER.debug("Received ModelScope response: %s", response)

            # Extract response content
            content = self._extract_response_text(response)

            if not content:
                LOGGER.error("Empty response from ModelScope API: %s", response)
                from homeassistant.exceptions import HomeAssistantError
                raise HomeAssistantError(ERROR_GETTING_RESPONSE)

            LOGGER.debug("Extracted content: %s", content)

            # Add response to chat log manually by creating AssistantContent
            # AssistantContent requires agent_id and content
            assistant_content = conversation.AssistantContent(
                agent_id=self.entry.entry_id,
                content=content
            )
            chat_log.content.append(assistant_content)

            LOGGER.debug("Added assistant content to chat_log. Chat log now has %d items",
                        len(chat_log.content))
            LOGGER.debug("Chat log content types: %s", [type(c).__name__ for c in chat_log.content])

        except conversation.ConverseError:
            # Re-raise ConverseError as-is
            raise
        except Exception as err:
            LOGGER.error("Error calling ModelScope API: %s", err, exc_info=True)
            from homeassistant.exceptions import HomeAssistantError
            raise HomeAssistantError(f"Error calling ModelScope API: {err}") from err

    def _format_structure_prompt(self, structure: dict[str, Any]) -> str:
        """Format structure requirements into a prompt."""
        prompt_parts = [
            "Please respond with a JSON object that matches the following structure:"
        ]

        # Handle voluptuous Schema objects
        if hasattr(structure, 'schema'):
            # It's a voluptuous Schema object
            schema_dict = structure.schema if isinstance(structure.schema, dict) else {}
            LOGGER.debug("Processing voluptuous Schema: %s", schema_dict)

            for key, value in schema_dict.items():
                # Extract the field name (remove voluptuous markers like Required, Optional)
                field_name = str(key)
                if hasattr(key, 'schema'):
                    field_name = str(key.schema)

                # Get description from selector if available
                description = ""
                if isinstance(value, dict) and "description" in value:
                    description = value["description"]
                elif hasattr(value, '__name__'):
                    description = value.__name__

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