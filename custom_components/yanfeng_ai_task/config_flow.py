"""Config flow for Yanfeng AI Task integration."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_API_KEY, CONF_LLM_HASS_API
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import llm
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TemplateSelector,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_CHAT_MODEL,
    CONF_IMAGE_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_RECOMMENDED,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DEFAULT_AI_TASK_NAME,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TITLE,
    DEFAULT_TOP_P,
    DOMAIN,
    LOGGER,
    RECOMMENDED_AI_TASK_OPTIONS,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_IMAGE_MODEL,
    SUPPORTED_CHAT_MODELS,
    SUPPORTED_IMAGE_MODELS,
    TIMEOUT_SECONDS,
)
from .helpers import ModelScopeAPIClient


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
    )
    
    try:
        client = ModelScopeAPIClient(session, data[CONF_API_KEY])
        
        # Test API connection with selected model
        test_model = data.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)
        await client.generate_text(
            model=test_model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
    except Exception as err:
        LOGGER.error("Failed to validate API key with model %s: %s", 
                    data.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL), err)
        raise InvalidAuth from err
    finally:
        await session.close()
    
    return {"title": DEFAULT_TITLE}


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class YanfengAITaskConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Yanfeng AI Task."""

    VERSION = 2
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create entry with subentries for both conversation and ai_task
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                    subentries=[
                        {
                            "subentry_type": "conversation",
                            "data": user_input,
                            "title": DEFAULT_AI_TASK_NAME + " Conversation",
                            "unique_id": None,
                        },
                        {
                            "subentry_type": "ai_task_data",
                            "data": RECOMMENDED_AI_TASK_OPTIONS,
                            "title": DEFAULT_AI_TASK_NAME,
                            "unique_id": None,
                        },
                    ],
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                    vol.Optional(
                        CONF_CHAT_MODEL,
                        default=RECOMMENDED_CHAT_MODEL,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=SUPPORTED_CHAT_MODELS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_IMAGE_MODEL,
                        default=RECOMMENDED_IMAGE_MODEL,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=SUPPORTED_IMAGE_MODELS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_TEMPERATURE,
                        default=DEFAULT_TEMPERATURE,
                    ): vol.All(vol.Coerce(float), vol.Range(min=0, max=2)),
                    vol.Optional(
                        CONF_MAX_TOKENS,
                        default=DEFAULT_MAX_TOKENS,
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=8192)),
                }
            ),
            errors=errors,
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this integration."""
        return {
            "conversation": YanfengAISubentryFlowHandler,
            "ai_task_data": YanfengAISubentryFlowHandler,
        }


class YanfengAISubentryFlowHandler(ConfigSubentryFlow):
    """Flow for managing subentries."""

    async def async_step_set_options(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Set options."""
        if user_input is not None:
            # Handle LLM_HASS_API - remove if empty
            if not user_input.get(CONF_LLM_HASS_API):
                user_input.pop(CONF_LLM_HASS_API, None)
            return self.async_create_subentry(data=user_input)

        # Get current subentry data
        if self.source == "user":
            # New subentry
            if self._subentry_type == "ai_task_data":
                options = RECOMMENDED_AI_TASK_OPTIONS.copy()
            else:
                options = {}
        else:
            # Reconfiguring existing subentry
            options = self._get_reconfigure_subentry().data.copy()

        # Get available LLM APIs
        hass_apis = [
            {"label": api.name, "value": api.id}
            for api in llm.async_get_apis(self.hass)
        ]

        # Get suggested values for LLM_HASS_API
        suggested_llm_apis = options.get(CONF_LLM_HASS_API)
        if isinstance(suggested_llm_apis, str):
            suggested_llm_apis = [suggested_llm_apis]

        return self.async_show_form(
            step_id="set_options",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PROMPT,
                        description={
                            "suggested_value": options.get(CONF_PROMPT, DEFAULT_PROMPT)
                        },
                    ): TemplateSelector(),
                    vol.Optional(
                        CONF_LLM_HASS_API,
                        description={"suggested_value": suggested_llm_apis},
                    ): SelectSelector(
                        SelectSelectorConfig(options=hass_apis, multiple=True)
                    ),
                    vol.Optional(
                        CONF_CHAT_MODEL,
                        default=options.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=SUPPORTED_CHAT_MODELS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_IMAGE_MODEL,
                        default=options.get(CONF_IMAGE_MODEL, RECOMMENDED_IMAGE_MODEL),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=SUPPORTED_IMAGE_MODELS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_TEMPERATURE,
                        default=options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0, max=2)),
                    vol.Optional(
                        CONF_TOP_P,
                        default=options.get(CONF_TOP_P, DEFAULT_TOP_P),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                    vol.Optional(
                        CONF_MAX_TOKENS,
                        default=options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=8192)),
                }
            ),
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle user step."""
        return await self.async_step_set_options(user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle reconfigure step."""
        return await self.async_step_set_options(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> YanfengAITaskOptionsFlow:
        """Create the options flow."""
        return YanfengAITaskOptionsFlow(config_entry)


class YanfengAITaskOptionsFlow(OptionsFlow):
    """Yanfeng AI Task config flow options handler."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            # Handle LLM_HASS_API - remove if empty
            if not user_input.get(CONF_LLM_HASS_API):
                user_input.pop(CONF_LLM_HASS_API, None)
            return self.async_create_entry(title="", data=user_input)

        # Use self._get_entry() to access config_entry (new method)
        options = self._get_entry().options

        # Get available LLM APIs
        hass_apis = [
            {"label": api.name, "value": api.id}
            for api in llm.async_get_apis(self.hass)
        ]

        # Get suggested values for LLM_HASS_API
        suggested_llm_apis = options.get(CONF_LLM_HASS_API)
        if isinstance(suggested_llm_apis, str):
            suggested_llm_apis = [suggested_llm_apis]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PROMPT,
                        description={
                            "suggested_value": options.get(CONF_PROMPT, DEFAULT_PROMPT)
                        },
                    ): TemplateSelector(),
                    vol.Optional(
                        CONF_LLM_HASS_API,
                        description={"suggested_value": suggested_llm_apis},
                    ): SelectSelector(
                        SelectSelectorConfig(options=hass_apis, multiple=True)
                    ),
                    vol.Optional(
                        CONF_CHAT_MODEL,
                        default=options.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=SUPPORTED_CHAT_MODELS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_IMAGE_MODEL,
                        default=options.get(CONF_IMAGE_MODEL, RECOMMENDED_IMAGE_MODEL),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=SUPPORTED_IMAGE_MODELS,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_TEMPERATURE,
                        default=options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0, max=2)),
                    vol.Optional(
                        CONF_TOP_P,
                        default=options.get(CONF_TOP_P, DEFAULT_TOP_P),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                    vol.Optional(
                        CONF_MAX_TOKENS,
                        default=options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=8192)),
                }
            ),
        )