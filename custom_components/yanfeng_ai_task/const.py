"""Constants for the Yanfeng AI Task integration."""

import logging

from homeassistant.helpers import llm

DOMAIN = "yanfeng_ai_task"
LOGGER = logging.getLogger(__package__)

# Configuration keys
CONF_API_KEY = "api_key"
CONF_MODEL_ID = "model_id"
CONF_PROMPT = "prompt"
CONF_TEMPERATURE = "temperature"
CONF_TOP_P = "top_p"
CONF_MAX_TOKENS = "max_tokens"
CONF_CHAT_MODEL = "chat_model"
CONF_IMAGE_MODEL = "image_model"
CONF_RECOMMENDED = "recommended"

# Default values
DEFAULT_TITLE = "Yanfeng AI Task"
DEFAULT_AI_TASK_NAME = "Yanfeng AI Task"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_TOKENS = 2048
DEFAULT_PROMPT = "You are a helpful assistant."

# ModelScope API-Inference base URL
MODELSCOPE_API_BASE = "https://api-inference.modelscope.cn/"

# Supported models (ModelScope only)
SUPPORTED_CHAT_MODELS = [
    "Qwen/Qwen2.5-72B-Instruct",
    "Qwen/Qwen2.5-32B-Instruct",
    "Qwen/Qwen2.5-14B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2-VL-72B-Instruct",
    "Qwen/Qwen3-VL-235B-A22B-Instruct",
]

SUPPORTED_IMAGE_MODELS = [
    "Qwen/Qwen-Image",
    "MusePublic/Qwen-Image-Edit",  # Requires input image
    "stable-diffusion-v1-5",
    "stable-diffusion-xl-base-1-0",
    "AI-ModelScope/stable-diffusion-v1-5",
    "AI-ModelScope/stable-diffusion-xl-base-1.0",
]

# Models that require an input image for editing
IMAGE_EDITING_MODELS = [
    "MusePublic/Qwen-Image-Edit",
]

# Recommended models
RECOMMENDED_CHAT_MODEL = "Qwen/Qwen2.5-72B-Instruct"
RECOMMENDED_IMAGE_MODEL = "Qwen/Qwen-Image"

# Task polling settings
TASK_POLL_INTERVAL = 2  # seconds
TASK_MAX_WAIT_TIME = 300  # 5 minutes

# Recommended options for AI Task
RECOMMENDED_AI_TASK_OPTIONS = {
    CONF_CHAT_MODEL: RECOMMENDED_CHAT_MODEL,
    CONF_TEMPERATURE: DEFAULT_TEMPERATURE,
    CONF_TOP_P: DEFAULT_TOP_P,
    CONF_MAX_TOKENS: DEFAULT_MAX_TOKENS,
    CONF_RECOMMENDED: True,
}

# Timeout settings
TIMEOUT_SECONDS = 30

# Error messages
ERROR_API_KEY_REQUIRED = "API key is required"
ERROR_MODEL_NOT_SUPPORTED = "Model not supported"
ERROR_GETTING_RESPONSE = "Error getting response from ModelScope API"
ERROR_INVALID_RESPONSE = "Invalid response from ModelScope API"