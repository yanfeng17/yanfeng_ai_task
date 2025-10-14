"""Config flow for Yanfeng AI Task integration."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
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

    VERSION = 1

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
                return self.async_create_entry(title=info["title"], data=user_input)

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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> YanfengAITaskOptionsFlow:
        """Create the options flow."""
        return YanfengAITaskOptionsFlow(config_entry)


class YanfengAITaskOptionsFlow(OptionsFlow):
    """Yanfeng AI Task config flow options handler."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PROMPT,
                        default=options.get(CONF_PROMPT, DEFAULT_PROMPT),
                    ): TextSelector(TextSelectorConfig(multiline=True)),
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