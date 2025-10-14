"""Conversation support for the Yanfeng AI Task integration."""

from __future__ import annotations

from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import CONF_LLM_HASS_API, MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_PROMPT, DOMAIN
from .entity import YanfengAILLMBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up conversation entities."""
    # Create conversation entity for the main config entry (default agent)
    async_add_entities([YanfengAIConversationEntity(config_entry, None)])

    # Also handle subentries if they exist
    for subentry in config_entry.subentries.values():
        if subentry.subentry_type != "conversation":
            continue

        async_add_entities(
            [YanfengAIConversationEntity(config_entry, subentry)],
            config_subentry_id=subentry.subentry_id,
        )


class YanfengAIConversationEntity(
    conversation.ConversationEntity,
    conversation.AbstractConversationAgent,
    YanfengAILLMBaseEntity,
):
    """Yanfeng AI conversation agent."""

    _attr_supports_streaming = False  # ModelScope doesn't support streaming yet

    def __init__(self, entry: ConfigEntry, subentry: ConfigSubentry | None) -> None:
        """Initialize the agent."""
        super().__init__(entry, subentry)
        # Check both subentry data and entry options for LLM_HASS_API
        llm_api_enabled = False
        if self.subentry:
            llm_api_enabled = self.subentry.data.get(CONF_LLM_HASS_API, False)
        else:
            llm_api_enabled = self.entry.options.get(CONF_LLM_HASS_API, False)

        if llm_api_enabled:
            self._attr_supported_features = (
                conversation.ConversationEntityFeature.CONTROL
            )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        conversation.async_set_agent(self.hass, self.entry, self)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        """Call the API."""
        # Get options from subentry data or entry options
        if self.subentry:
            options = self.subentry.data
        else:
            options = self.entry.options

        try:
            await chat_log.async_provide_llm_data(
                user_input.as_llm_context(DOMAIN),
                options.get(CONF_LLM_HASS_API),
                options.get(CONF_PROMPT),
                user_input.extra_system_prompt,
            )
        except conversation.ConverseError as err:
            return err.as_conversation_result()

        await self._async_handle_chat_log(chat_log)

        return conversation.async_get_result_from_chat_log(user_input, chat_log)