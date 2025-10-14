"""AI Task integration for Yanfeng AI Task."""

from __future__ import annotations

import aiohttp
from json import JSONDecodeError
from typing import TYPE_CHECKING

from homeassistant.components import ai_task, conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.json import json_loads

from .const import (
    CONF_CHAT_MODEL,
    CONF_IMAGE_MODEL,
    CONF_RECOMMENDED,
    IMAGE_EDITING_MODELS,
    LOGGER,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_IMAGE_MODEL,
    SUPPORTED_IMAGE_MODELS,
)
from .entity import (
    ERROR_GETTING_RESPONSE,
    YanfengAILLMBaseEntity,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigSubentry

    from . import YanfengAIConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up AI Task entities."""
    # Create AI Task entity for the main config entry
    async_add_entities([YanfengAITaskEntity(hass, config_entry, None)])
    
    # Also handle subentries if they exist
    for subentry in config_entry.subentries.values():
        if subentry.subentry_type != "ai_task_data":
            continue

        async_add_entities(
            [YanfengAITaskEntity(hass, config_entry, subentry)],
            config_subentry_id=subentry.subentry_id,
        )


class YanfengAITaskEntity(
    ai_task.AITaskEntity,
    YanfengAILLMBaseEntity,
):
    """Yanfeng AI Task entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: YanfengAIConfigEntry,
        subentry: ConfigSubentry | None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(entry, subentry)
        self.subentry = subentry
        # Enable all supported features by default
        self._attr_supported_features = (
            ai_task.AITaskEntityFeature.GENERATE_DATA
            | ai_task.AITaskEntityFeature.GENERATE_IMAGE
            | ai_task.AITaskEntityFeature.SUPPORT_ATTACHMENTS
        )

    async def _async_generate_data(
        self,
        task: ai_task.GenDataTask,
        chat_log: conversation.ChatLog,
    ) -> ai_task.GenDataTaskResult:
        """Handle a generate data task."""
        LOGGER.debug("Starting generate_data task. Chat log has %d items before processing",
                    len(chat_log.content))

        try:
            await self._async_handle_chat_log(chat_log, task.structure)
        except Exception as err:
            LOGGER.error("Error in _async_handle_chat_log: %s", err, exc_info=True)
            raise HomeAssistantError(f"Error processing chat: {err}") from err

        LOGGER.debug("After _async_handle_chat_log. Chat log has %d items",
                    len(chat_log.content))

        if not chat_log.content:
            LOGGER.error("Chat log is empty after processing")
            raise HomeAssistantError("No response generated - empty chat log")

        if not isinstance(chat_log.content[-1], conversation.AssistantContent):
            LOGGER.error(
                "Last content in chat log is not an AssistantContent: %s. "
                "This could be due to the model not returning a valid response. "
                "Chat log contents: %s",
                chat_log.content[-1],
                [type(c).__name__ for c in chat_log.content],
            )
            raise HomeAssistantError(ERROR_GETTING_RESPONSE)

        text = chat_log.content[-1].content or ""
        LOGGER.debug("Extracted text from AssistantContent: %s", text[:100])

        if not task.structure:
            return ai_task.GenDataTaskResult(
                conversation_id=chat_log.conversation_id,
                data=text,
            )

        try:
            data = json_loads(text)
        except JSONDecodeError as err:
            LOGGER.error(
                "Failed to parse JSON response: %s. Response: %s",
                err,
                text,
            )
            raise HomeAssistantError(
                f"Failed to parse JSON response: {err}"
            ) from err

        return ai_task.GenDataTaskResult(
            conversation_id=chat_log.conversation_id,
            data=data,
        )

    async def _async_generate_image(
        self,
        task: ai_task.GenImageTask,
        chat_log: conversation.ChatLog,
    ) -> ai_task.GenImageTaskResult:
        """Handle a generate image task."""

        # Extract prompt from the last user message
        prompt = ""
        image_attachment_path = None

        for content in reversed(chat_log.content):
            if isinstance(content, conversation.UserContent):
                prompt = content.content

                # Check for image attachments (for image editing)
                if content.attachments:
                    for attachment in content.attachments:
                        # Check if it's an image attachment
                        if attachment.mime_type and attachment.mime_type.startswith("image/"):
                            image_attachment_path = attachment.path
                            LOGGER.debug("Found image attachment for editing: %s", attachment.path)
                            break
                break

        if not prompt:
            raise HomeAssistantError("No prompt found for image generation")

        # Get configured image model from options or data, fallback to recommended
        image_model = (
            self.entry.options.get(CONF_IMAGE_MODEL)
            or self.entry.data.get(CONF_IMAGE_MODEL)
            or RECOMMENDED_IMAGE_MODEL
        )

        # Handle image URL for editing models
        image_url = None

        # First, try to extract URL from prompt text
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        url_matches = re.findall(url_pattern, prompt)

        if url_matches:
            # Use the first URL found as the image URL
            image_url = url_matches[0]
            # Remove the URL from the prompt
            prompt = re.sub(url_pattern, '', prompt).strip()
            LOGGER.info("Extracted image URL from prompt: %s", image_url)
        elif image_attachment_path and image_model in IMAGE_EDITING_MODELS:
            # Upload the local file to ModelScope
            try:
                LOGGER.info("Uploading image attachment to ModelScope: %s", image_attachment_path)
                image_url = await self.client.upload_file(
                    str(image_attachment_path),
                    "image/jpeg"  # Default to JPEG, ModelScope should auto-detect
                )
                LOGGER.info("Image uploaded successfully: %s", image_url)
            except Exception as err:
                LOGGER.error("Failed to upload image: %s", err)
                raise HomeAssistantError(
                    f"Failed to upload image for editing: {err}. "
                    f"Alternatively, you can provide a public image URL in your prompt."
                ) from err

        # Check if editing model is used without an image URL
        if not image_url and image_model in IMAGE_EDITING_MODELS:
            LOGGER.warning(
                f"{image_model} is an image editing model but no image provided. "
                f"Will attempt generation, but may fail."
            )

        LOGGER.debug("Using image model: %s for prompt: %s (image_url: %s)",
                    image_model, prompt[:100], image_url or "none")

        try:
            # Use image generation model
            response = await self.client.generate_image(
                model=image_model,
                prompt=prompt,
                image_url=image_url,
                size="1024*1024",
                n=1,
            )

            # Extract image URLs from ModelScope response
            image_urls = []
            if "data" in response:
                for item in response["data"]:
                    if "url" in item:
                        image_urls.append(item["url"])

            if not image_urls:
                LOGGER.error("No image URLs found in response: %s", response)
                raise HomeAssistantError("Failed to generate image")

            # Download the first image
            image_url_result = image_urls[0]
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url_result) as img_response:
                    if img_response.status != 200:
                        raise HomeAssistantError(f"Failed to download image: HTTP {img_response.status}")

                    image_data = await img_response.read()
                    content_type = img_response.headers.get("content-type", "image/png")

            return ai_task.GenImageTaskResult(
                conversation_id=chat_log.conversation_id,
                image_data=image_data,
                mime_type=content_type,
                model=image_model,
                revised_prompt=prompt,
            )

        except Exception as err:
            LOGGER.error("Error generating image: %s", err)
            if image_model in IMAGE_EDITING_MODELS and not image_url:
                raise HomeAssistantError(
                    f"{image_model} requires an input image. "
                    f"Please attach an image or include a public image URL in your prompt."
                ) from err
            raise HomeAssistantError(f"Error generating image: {err}") from err