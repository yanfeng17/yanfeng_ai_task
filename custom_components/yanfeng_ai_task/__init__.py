"""The Yanfeng AI Task integration."""

from __future__ import annotations

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryError,
    ConfigEntryNotReady,
    HomeAssistantError,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_PROMPT,
    DEFAULT_AI_TASK_NAME,
    DEFAULT_TITLE,
    DOMAIN,
    LOGGER,
    RECOMMENDED_AI_TASK_OPTIONS,
    RECOMMENDED_CHAT_MODEL,
    TIMEOUT_SECONDS,
)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS = (
    Platform.AI_TASK,
    Platform.CONVERSATION,
)

# Type alias for config entry with runtime data
YanfengAIConfigEntry = ConfigEntry[aiohttp.ClientSession]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Yanfeng AI Task."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: YanfengAIConfigEntry) -> bool:
    """Set up Yanfeng AI Task from a config entry."""

    # Create HTTP session
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
    )

    # Test API connection
    if not await _test_api_connection(session, entry.data[CONF_API_KEY]):
        LOGGER.error("API connection test failed")
        await session.close()
        raise ConfigEntryNotReady("Failed to connect to ModelScope API")

    LOGGER.info("API connection test successful")

    entry.runtime_data = session

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Add update listener to reload when config changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(
    hass: HomeAssistant, entry: YanfengAIConfigEntry
) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: YanfengAIConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        session = entry.runtime_data
        await session.close()
    
    return unload_ok


async def _test_api_connection(session: aiohttp.ClientSession, api_key: str) -> bool:
    """Test the ModelScope API connection."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Test ModelScope API
        modelscope_payload = {
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10,
        }
        
        async with session.post(
            "https://api-inference.modelscope.cn/v1/chat/completions",
            headers=headers,
            json=modelscope_payload,
        ) as response:
            if response.status == 200:
                LOGGER.info("ModelScope API connection successful")
                return True
            else:
                LOGGER.error("ModelScope API test failed with status: %s", response.status)
                return False
            
    except Exception as err:
        LOGGER.error("Failed to test ModelScope API connection: %s", err)
        return False