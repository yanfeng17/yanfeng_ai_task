"""Intent handlers for Yanfeng AI Task integration."""

from __future__ import annotations

import re
import os
import yaml
import asyncio
from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import voluptuous as vol

from homeassistant.components import camera
from homeassistant.components.conversation import DOMAIN as CONVERSATION_DOMAIN
from homeassistant.components.timer import DOMAIN as TIMER_DOMAIN
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import area_registry, device_registry, entity_registry, intent
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON,
    STATE_OFF,
)

from .const import DOMAIN, LOGGER

# 缓存 YAML 配置
_YAML_CACHE = {}


async def async_load_yaml_config(hass: HomeAssistant, path: str) -> dict:
    """Load YAML configuration file with caching."""
    if path not in _YAML_CACHE:
        if os.path.exists(path):
            def _load_yaml():
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            _YAML_CACHE[path] = await hass.async_add_executor_job(_load_yaml)
    return _YAML_CACHE.get(path, {})


# Intent type constants
INTENT_CLIMATE_SET_TEMP = "ClimateSetTemperature"
INTENT_CLIMATE_SET_MODE = "ClimateSetMode"
INTENT_CLIMATE_SET_FAN = "ClimateSetFanMode"
INTENT_CLIMATE_SET_HUMIDITY = "ClimateSetHumidity"
INTENT_CLIMATE_SET_SWING = "ClimateSetSwingMode"
INTENT_COVER_CONTROL_ALL = "CoverControlAll"
INTENT_LIGHT_SET_ALL = "HassLightSetAllIntent"
INTENT_TIMER = "HassTimerIntent"
INTENT_NOTIFY = "HassNotifyIntent"
INTENT_SET_STATE = "HassSetStateIntent"  # 新增：通用打开/关闭设备

# Error codes
ERROR_NO_ENTITY = "no_entity"
ERROR_NO_RESPONSE = "no_response"
ERROR_SERVICE_CALL = "service_call_error"
ERROR_INVALID_TEMPERATURE = "invalid_temperature"
ERROR_INVALID_MODE = "invalid_mode"
ERROR_INVALID_POSITION = "invalid_position"
ERROR_NO_TIMER = "no_timer"
ERROR_NO_MESSAGE = "no_message"


async def async_setup_intents(hass: HomeAssistant) -> None:
    """Set up intent handlers."""
    yaml_path = os.path.join(os.path.dirname(__file__), "intents.yaml")
    intents_config = await async_load_yaml_config(hass, yaml_path)
    if intents_config:
        LOGGER.info("从 %s 加载的 intent 配置", yaml_path)

    # Register all intent handlers
    intent.async_register(hass, ClimateSetTemperatureIntent(hass))
    intent.async_register(hass, ClimateSetModeIntent(hass))
    intent.async_register(hass, ClimateSetFanModeIntent(hass))
    intent.async_register(hass, ClimateSetHumidityIntent(hass))
    intent.async_register(hass, ClimateSetSwingModeIntent(hass))
    intent.async_register(hass, CoverControlAllIntent(hass))
    intent.async_register(hass, HassLightSetAllIntent(hass))
    intent.async_register(hass, HassTimerIntent(hass))
    intent.async_register(hass, HassNotifyIntent(hass))
    intent.async_register(hass, HassSetStateIntent(hass))  # 新增


class BaseIntent(intent.IntentHandler):
    """Base class for intent handlers."""

    def __init__(self, hass: HomeAssistant):
        super().__init__()
        self.hass = hass
        self.config = {}
        self._config_loaded = False

    async def _load_config(self):
        """Load configuration from YAML."""
        if not self._config_loaded:
            yaml_path = os.path.join(os.path.dirname(__file__), "intents.yaml")
            config = await async_load_yaml_config(self.hass, yaml_path)
            self.config = config.get(self.intent_type, {})
            self._config_loaded = True

    def get_slot_value(self, slot_data):
        """Extract value from slot data."""
        if not slot_data:
            return None
        if isinstance(slot_data, dict):
            return slot_data.get('value')
        if hasattr(slot_data, 'value'):
            return getattr(slot_data, 'value', None)
        return str(slot_data)

    def _set_error_response(self, response, code, message) -> intent.IntentResponse:
        """Set error response."""
        response.async_set_error(code=code, message=message)
        return response

    def _set_speech_response(self, response, message) -> intent.IntentResponse:
        """Set speech response."""
        response.async_set_speech(message)
        return response

    def find_climate_entity(self, name: str) -> State | None:
        """Find climate entity by name."""
        return next(
            (state for state in self.hass.states.async_all()
             if state.domain == "climate" and (
                 name.lower() in state.attributes.get('friendly_name', '').lower() or
                 name.lower() in state.entity_id.lower()
             )),
            None
        )


class ClimateSetTemperatureIntent(BaseIntent):
    """Handle climate temperature setting intent."""

    intent_type = INTENT_CLIMATE_SET_TEMP
    slot_schema = {
        vol.Required("name"): str,
        vol.Required("temperature"): vol.Any(str, int, float)
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        name = self.get_slot_value(slots.get("name"))
        temperature = int(self.get_slot_value(slots.get("temperature")))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        # Find climate entity
        state = self.find_climate_entity(name)
        if not state:
            return self._set_error_response(
                response, ERROR_NO_ENTITY, f"找不到名为 {name} 的空调设备"
            )

        # Ensure entity is on
        await self.ensure_entity_on(state.entity_id)

        # Get temperature range
        min_temp = float(state.attributes.get('min_temp', 16))
        max_temp = float(state.attributes.get('max_temp', 30))

        if temperature < min_temp or temperature > max_temp:
            return self._set_error_response(
                response, ERROR_INVALID_TEMPERATURE,
                f"温度必须在{min_temp}度到{max_temp}度之间"
            )

        # Smart mode detection: auto set cooling/heating based on current temperature
        current_temp = state.attributes.get('current_temperature')
        if current_temp is not None:
            if current_temp > temperature:
                # Too hot, need cooling
                await self.hass.services.async_call(
                    "climate", "set_hvac_mode",
                    {"entity_id": state.entity_id, "hvac_mode": "cool"},
                    blocking=True
                )
                mode_text = "制冷"
            elif current_temp < temperature:
                # Too cold, need heating
                await self.hass.services.async_call(
                    "climate", "set_hvac_mode",
                    {"entity_id": state.entity_id, "hvac_mode": "heat"},
                    blocking=True
                )
                mode_text = "制热"
            else:
                mode_text = "当前"
        else:
            mode_text = ""

        # Set temperature
        await self.hass.services.async_call(
            "climate", "set_temperature",
            {"entity_id": state.entity_id, "temperature": temperature},
            blocking=True
        )

        return self._set_speech_response(
            response,
            f"已将{name}设置为{mode_text}模式，温度{temperature}度"
        )

    async def ensure_entity_on(self, entity_id: str):
        """Ensure climate entity is turned on."""
        try:
            await self.hass.services.async_call(
                "climate", "turn_on",
                {"entity_id": entity_id},
                blocking=True
            )
        except Exception:
            pass  # Entity might not support turn_on


class ClimateSetModeIntent(BaseIntent):
    """Handle climate mode setting intent."""

    intent_type = INTENT_CLIMATE_SET_MODE
    slot_schema = {
        vol.Required("name"): str,
        vol.Required("mode"): str
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        name = self.get_slot_value(slots.get("name"))
        mode = self.get_slot_value(slots.get("mode"))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        # Find climate entity
        state = self.find_climate_entity(name)
        if not state:
            return self._set_error_response(
                response, ERROR_NO_ENTITY, f"找不到名为 {name} 的空调设备"
            )

        # Mode mapping (Chinese to English)
        mode_maps = {
            "制冷": ["cool", "cooling"],
            "制热": ["heat", "heating"],
            "自动": ["auto", "heat_cool"],
            "除湿": ["dry", "dehumidify"],
            "送风": ["fan_only", "fan"]
        }

        # Find matching mode
        target_mode = None
        for chinese_mode, english_modes in mode_maps.items():
            if mode in chinese_mode or mode in english_modes:
                # Check which mode is supported by the device
                available_modes = state.attributes.get('hvac_modes', [])
                for eng_mode in english_modes:
                    if eng_mode in available_modes:
                        target_mode = eng_mode
                        break
                break

        if not target_mode:
            return self._set_error_response(
                response, ERROR_INVALID_MODE, f"不支持的模式: {mode}"
            )

        # Set mode
        await self.hass.services.async_call(
            "climate", "set_hvac_mode",
            {"entity_id": state.entity_id, "hvac_mode": target_mode},
            blocking=True
        )

        return self._set_speech_response(
            response, f"已将{name}设置为{mode}模式"
        )


class ClimateSetFanModeIntent(BaseIntent):
    """Handle climate fan mode setting intent."""

    intent_type = INTENT_CLIMATE_SET_FAN
    slot_schema = {
        vol.Required("name"): str,
        vol.Required("fan_mode"): str
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        name = self.get_slot_value(slots.get("name"))
        fan_mode = self.get_slot_value(slots.get("fan_mode"))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        # Find climate entity
        state = self.find_climate_entity(name)
        if not state:
            return self._set_error_response(
                response, ERROR_NO_ENTITY, f"找不到名为 {name} 的空调设备"
            )

        # Fan mode mapping
        fan_mode_maps = {
            "自动": ["auto", "auto_low", "auto_high"],
            "低速": ["on_low", "low", "一档", "低风"],
            "中速": ["medium", "mid", "二档", "中风"],
            "高速": ["on_high", "high", "七档", "高风"]
        }

        # Find matching fan mode
        target_fan_mode = None
        for chinese_mode, english_modes in fan_mode_maps.items():
            if fan_mode in chinese_mode or fan_mode in english_modes:
                available_modes = state.attributes.get('fan_modes', [])
                for eng_mode in english_modes:
                    if eng_mode in available_modes:
                        target_fan_mode = eng_mode
                        break
                break

        if not target_fan_mode:
            return self._set_error_response(
                response, ERROR_INVALID_MODE, f"不支持的风速: {fan_mode}"
            )

        # Set fan mode
        await self.hass.services.async_call(
            "climate", "set_fan_mode",
            {"entity_id": state.entity_id, "fan_mode": target_fan_mode},
            blocking=True
        )

        return self._set_speech_response(
            response, f"已将{name}的风速设置为{fan_mode}"
        )


class ClimateSetHumidityIntent(BaseIntent):
    """Handle climate humidity setting intent."""

    intent_type = INTENT_CLIMATE_SET_HUMIDITY
    slot_schema = {
        vol.Required("name"): str,
        vol.Required("humidity"): vol.Any(str, int)
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        name = self.get_slot_value(slots.get("name"))
        humidity = int(self.get_slot_value(slots.get("humidity")))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        # Find climate entity
        state = self.find_climate_entity(name)
        if not state:
            return self._set_error_response(
                response, ERROR_NO_ENTITY, f"找不到名为 {name} 的空调设备"
            )

        # Set humidity
        await self.hass.services.async_call(
            "climate", "set_humidity",
            {"entity_id": state.entity_id, "humidity": humidity},
            blocking=True
        )

        return self._set_speech_response(
            response, f"已将{name}的湿度设置为{humidity}%"
        )


class ClimateSetSwingModeIntent(BaseIntent):
    """Handle climate swing mode setting intent."""

    intent_type = INTENT_CLIMATE_SET_SWING
    slot_schema = {
        vol.Required("name"): str,
        vol.Required("swing_mode"): str
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        name = self.get_slot_value(slots.get("name"))
        swing_mode = self.get_slot_value(slots.get("swing_mode"))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        # Find climate entity
        state = self.find_climate_entity(name)
        if not state:
            return self._set_error_response(
                response, ERROR_NO_ENTITY, f"找不到名为 {name} 的空调设备"
            )

        # Swing mode mapping
        swing_mode_maps = {
            "开启": ["on", "both", "auto"],
            "关闭": ["off"],
            "水平": ["horizontal"],
            "垂直": ["vertical"]
        }

        # Find matching swing mode
        target_swing_mode = None
        for chinese_mode, english_modes in swing_mode_maps.items():
            if swing_mode in chinese_mode or swing_mode in english_modes:
                available_modes = state.attributes.get('swing_modes', [])
                for eng_mode in english_modes:
                    if eng_mode in available_modes:
                        target_swing_mode = eng_mode
                        break
                break

        if not target_swing_mode:
            return self._set_error_response(
                response, ERROR_INVALID_MODE, f"不支持的摆风模式: {swing_mode}"
            )

        # Set swing mode
        await self.hass.services.async_call(
            "climate", "set_swing_mode",
            {"entity_id": state.entity_id, "swing_mode": target_swing_mode},
            blocking=True
        )

        return self._set_speech_response(
            response, f"已将{name}的摆风设置为{swing_mode}"
        )


class CoverControlAllIntent(BaseIntent):
    """Handle control all covers intent."""

    intent_type = INTENT_COVER_CONTROL_ALL
    slot_schema = {
        vol.Required("action"): str
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        action = self.get_slot_value(slots.get("action"))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        # Find all cover entities
        covers = [
            state.entity_id
            for state in self.hass.states.async_all()
            if state.entity_id.startswith("cover.")
            and not any(x in state.entity_id.lower() for x in ["garage", "车库"])
        ]

        if not covers:
            return self._set_error_response(
                response, ERROR_NO_ENTITY, "没有找到窗帘设备"
            )

        # Determine action
        is_close = any(x in action for x in ["关", "close"])
        service = "close_cover" if is_close else "open_cover"

        # Execute batch operation
        success_count = 0
        failed_entities = []

        for entity_id in covers:
            try:
                await self.hass.services.async_call(
                    "cover", service,
                    {"entity_id": entity_id},
                    blocking=True
                )
                success_count += 1
            except Exception:
                try:
                    # Try tilt service for some covers
                    tilt_service = "close_cover_tilt" if is_close else "open_cover_tilt"
                    await self.hass.services.async_call(
                        "cover", tilt_service,
                        {"entity_id": entity_id},
                        blocking=True
                    )
                    success_count += 1
                except Exception:
                    failed_entities.append(entity_id)

        # Generate response message
        if success_count == 0:
            message = "所有设备操作都失败了"
        else:
            action_text = "关闭" if is_close else "打开"
            message = f"已{action_text} {success_count} 个窗帘"
            if failed_entities:
                message += f"，但有 {len(failed_entities)} 个设备失败"

        return self._set_speech_response(response, message)


class HassLightSetAllIntent(BaseIntent):
    """Handle light control with all parameters intent."""

    intent_type = INTENT_LIGHT_SET_ALL
    slot_schema = {
        vol.Required("name"): str,
        vol.Optional("brightness"): vol.Any(str, int),
        vol.Optional("color"): str,
        vol.Optional("color_temp"): vol.Any(str, int)
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        name = self.get_slot_value(slots.get("name"))
        brightness = self.get_slot_value(slots.get("brightness"))
        color = self.get_slot_value(slots.get("color"))
        color_temp = self.get_slot_value(slots.get("color_temp"))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        # Find light entity
        state = next(
            (state for state in self.hass.states.async_all()
             if state.domain == "light" and (
                 name.lower() in state.attributes.get('friendly_name', '').lower() or
                 name.lower() in state.entity_id.lower()
             )),
            None
        )

        if not state:
            return self._set_error_response(
                response, ERROR_NO_ENTITY, f"找不到名为 {name} 的灯光"
            )

        service_data = {"entity_id": state.entity_id}

        # Set brightness (0-100% to 0-255)
        if brightness:
            brightness_int = int(brightness)
            service_data["brightness_pct"] = max(0, min(100, brightness_int))

        # Set color temperature
        if color_temp:
            service_data["color_temp"] = int(color_temp)

        # Set color (simplified, would need color name to RGB mapping)
        if color:
            # This is a simplified version, real implementation would need a color mapping dict
            pass

        # Turn on light with parameters
        await self.hass.services.async_call(
            "light", "turn_on",
            service_data,
            blocking=True
        )

        return self._set_speech_response(
            response, f"已设置{name}的参数"
        )


class HassTimerIntent(BaseIntent):
    """Handle timer intent."""

    intent_type = INTENT_TIMER
    slot_schema = {
        vol.Required("action"): str,
        vol.Optional("duration"): str,
        vol.Optional("timer_name"): str
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        action = self.get_slot_value(slots.get("action"))
        duration = self.get_slot_value(slots.get("duration"))
        timer_name = self.get_slot_value(slots.get("timer_name"))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        # This is a simplified timer handler
        # Full implementation would parse Chinese time expressions

        return self._set_speech_response(
            response, "定时器功能正在开发中"
        )


class HassNotifyIntent(BaseIntent):
    """Handle notification intent."""

    intent_type = INTENT_NOTIFY
    slot_schema = {
        vol.Required("message"): str,
        vol.Optional("title"): str
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        message = self.get_slot_value(slots.get("message"))
        title = self.get_slot_value(slots.get("title"))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        if not message:
            return self._set_error_response(
                response, ERROR_NO_MESSAGE, "缺少通知消息"
            )

        # Send notification
        await self.hass.services.async_call(
            "persistent_notification", "create",
            {
                "title": title or "Yanfeng AI Task",
                "message": message
            },
            blocking=True
        )

        return self._set_speech_response(
            response, "已创建通知"
        )


class HassSetStateIntent(BaseIntent):
    """Handle turn on/off devices intent."""

    intent_type = INTENT_SET_STATE
    slot_schema = {
        vol.Required("name"): str,
        vol.Required("action"): str,
    }

    async def async_handle(self, intent_obj: intent.Intent) -> intent.IntentResponse:
        """Handle the intent."""
        await self._load_config()
        slots = self.async_validate_slots(intent_obj.slots)
        name = self.get_slot_value(slots.get("name"))
        action = self.get_slot_value(slots.get("action"))

        response = intent.IntentResponse(intent=intent_obj, language="zh-cn")

        # Determine if it's turn on or turn off
        is_turn_on = any(x in action for x in ["打开", "开启", "启动", "开", "on"])

        # Search for entity
        found_entity = None
        for state in self.hass.states.async_all():
            friendly_name = state.attributes.get('friendly_name', '')
            if name.lower() in friendly_name.lower() or name.lower() in state.entity_id.lower():
                found_entity = state
                break

        if not found_entity:
            return self._set_error_response(
                response, ERROR_NO_ENTITY, f"找不到名为 {name} 的设备"
            )

        # Determine service based on domain
        domain = found_entity.domain
        service = "turn_on" if is_turn_on else "turn_off"

        # Special handling for climate entities
        if domain == "climate" and is_turn_on:
            # For climate, also set a reasonable mode
            try:
                await self.hass.services.async_call(
                    domain, service,
                    {"entity_id": found_entity.entity_id},
                    blocking=True
                )
                # Try to set to auto mode if available
                hvac_modes = found_entity.attributes.get('hvac_modes', [])
                if 'heat_cool' in hvac_modes:
                    await self.hass.services.async_call(
                        "climate", "set_hvac_mode",
                        {"entity_id": found_entity.entity_id, "hvac_mode": "heat_cool"},
                        blocking=True
                    )
            except Exception as err:
                LOGGER.error("Failed to turn on climate: %s", err)
                return self._set_error_response(
                    response, ERROR_SERVICE_CALL, f"无法操作{name}"
                )
        else:
            # For other entities, just call turn_on/turn_off
            try:
                await self.hass.services.async_call(
                    domain, service,
                    {"entity_id": found_entity.entity_id},
                    blocking=True
                )
            except Exception as err:
                LOGGER.error("Failed to %s %s: %s", service, name, err)
                return self._set_error_response(
                    response, ERROR_SERVICE_CALL, f"无法操作{name}"
                )

        action_text = "已打开" if is_turn_on else "已关闭"
        return self._set_speech_response(
            response, f"{action_text}{name}"
        )
