"""Helper functions for Yanfeng AI Task integration."""

from __future__ import annotations

import aiohttp
import asyncio
import json
import logging
from typing import Any

from homeassistant.exceptions import HomeAssistantError

from .const import (
    ERROR_GETTING_RESPONSE,
    ERROR_INVALID_RESPONSE,
    LOGGER,
    MODELSCOPE_API_BASE,
    TASK_MAX_WAIT_TIME,
    TASK_POLL_INTERVAL,
)


class ModelScopeAPIClient:
    """Client for ModelScope API-Inference."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        """Initialize the client."""
        self.session = session
        self.api_key = api_key
        self.modelscope_base_url = MODELSCOPE_API_BASE
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def generate_text(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 2048,
        stream: bool = False,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "auto",
    ) -> dict[str, Any]:
        """Generate text using ModelScope API-Inference with optional function calling."""

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }

        # Add tools if provided (OpenAI-compatible function calling)
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
            LOGGER.debug("Added %d tools to payload with tool_choice=%s", len(tools), tool_choice)

        # Handle special models that require extra parameters
        # Qwen3 series models require enable_thinking parameter for non-streaming calls
        if "Qwen3" in model or "QwQ" in model:
            if not stream:
                # For non-streaming calls, must disable thinking
                payload["enable_thinking"] = False
                LOGGER.debug("Added enable_thinking=False for Qwen3/QwQ model in non-streaming mode")

        try:
            url = f"{self.modelscope_base_url}v1/chat/completions"
            headers = {**self.headers}
            
            LOGGER.debug("Sending ModelScope request to %s with payload: %s", url, payload)
            
            async with self.session.post(
                url,
                headers=headers,
                json=payload,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    LOGGER.error(
                        "ModelScope API error: %s - %s", response.status, error_text
                    )
                    raise HomeAssistantError(f"ModelScope API error: {response.status}")

                result = await response.json()
                LOGGER.debug("Received ModelScope response: %s", result)
                
                # Convert ModelScope response to OpenAI format for compatibility
                if "choices" in result:
                    return result
                elif "output" in result and "text" in result["output"]:
                    # Convert to OpenAI format
                    return {
                        "choices": [{
                            "message": {
                                "content": result["output"]["text"],
                                "role": "assistant"
                            }
                        }]
                    }
                else:
                    LOGGER.error("Invalid ModelScope response format: %s", result)
                    raise HomeAssistantError(ERROR_INVALID_RESPONSE)

        except aiohttp.ClientError as err:
            LOGGER.error("Network error calling ModelScope API: %s", err)
            raise HomeAssistantError(ERROR_GETTING_RESPONSE) from err
        except json.JSONDecodeError as err:
            LOGGER.error("Failed to decode ModelScope JSON response: %s", err)
            raise HomeAssistantError(ERROR_INVALID_RESPONSE) from err

    async def upload_file(
        self,
        file_path: str,
        mime_type: str | None = None,
    ) -> str:
        """Upload a file to ModelScope and return the public URL.

        Args:
            file_path: Path to the local file
            mime_type: MIME type of the file

        Returns:
            Public URL of the uploaded file
        """
        import aiofiles

        if mime_type is None:
            import mimetypes
            mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        try:
            # Read file content
            async with aiofiles.open(file_path, 'rb') as f:
                file_data = await f.read()

            # Upload to ModelScope file API
            url = f"{self.modelscope_base_url}v1/files"

            # Create multipart form data
            import aiohttp
            form = aiohttp.FormData()
            form.add_field('file',
                          file_data,
                          filename=file_path.split('/')[-1],
                          content_type=mime_type)

            LOGGER.debug("Uploading file to ModelScope: %s (type: %s)", file_path, mime_type)

            async with self.session.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=form,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    LOGGER.error(
                        "ModelScope file upload error: %s - %s", response.status, error_text
                    )
                    raise HomeAssistantError(f"Failed to upload file: {response.status}")

                result = await response.json()
                LOGGER.debug("File upload response: %s", result)

                # Extract file URL from response
                if "url" in result:
                    return result["url"]
                elif "file_url" in result:
                    return result["file_url"]
                elif "data" in result and "url" in result["data"]:
                    return result["data"]["url"]
                else:
                    LOGGER.error("No URL in upload response: %s", result)
                    raise HomeAssistantError("File upload succeeded but no URL returned")

        except aiohttp.ClientError as err:
            LOGGER.error("Network error uploading file: %s", err)
            raise HomeAssistantError(f"Network error uploading file: {err}") from err
        except Exception as err:
            LOGGER.error("Error uploading file: %s", err)
            raise HomeAssistantError(f"Error uploading file: {err}") from err

    async def generate_image(
        self,
        model: str,
        prompt: str,
        image_url: str | None = None,
        image_path: str | None = None,
        image_mime_type: str | None = None,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
    ) -> dict[str, Any]:
        """Generate image using ModelScope API-Inference with async task polling.

        Args:
            model: The model ID to use for image generation
            prompt: The text prompt for image generation/editing
            image_url: Optional input image URL for image editing models
            image_path: Optional local file path (will be uploaded to ModelScope)
            image_mime_type: MIME type of the image (e.g., image/jpeg, image/png)
            size: Image size (default: 1024x1024)
            quality: Image quality (default: standard)
            n: Number of images to generate (default: 1)
        """

        payload = {
            "model": model,
            "prompt": prompt,
        }

        # Add image_url for image editing models
        if image_url:
            payload["image_url"] = image_url
            LOGGER.debug("Using image_url for image editing: %s", image_url)
        elif image_path:
            # Upload local file to ModelScope to get public URL
            # This is the correct way to handle local files with ModelScope API
            try:
                # Use provided MIME type if available, otherwise guess from file
                mime_type = image_mime_type
                if not mime_type:
                    import mimetypes
                    mime_type = mimetypes.guess_type(image_path)[0]

                # Fallback to common image MIME type if still unknown
                if not mime_type or mime_type == "application/octet-stream":
                    mime_type = "image/jpeg"
                    LOGGER.debug("MIME type not detected or invalid, using default: %s", mime_type)

                # Upload file and get public URL
                uploaded_url = await self.upload_file(image_path, mime_type)
                payload["image_url"] = uploaded_url
                LOGGER.debug("Uploaded local file to ModelScope, using URL: %s", uploaded_url)
            except Exception as err:
                LOGGER.error("Failed to upload local image file: %s", err)
                raise HomeAssistantError(f"Failed to upload image file: {err}") from err

        try:
            # Step 1: Submit image generation task
            url = f"{self.modelscope_base_url}v1/images/generations"
            headers = {
                **self.headers,
                "X-ModelScope-Async-Mode": "true"
            }

            LOGGER.debug("Submitting ModelScope image task to %s with payload keys: %s",
                        url, list(payload.keys()))

            async with self.session.post(
                url,
                headers=headers,
                json=payload,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    LOGGER.error(
                        "ModelScope Image API error: %s - %s", response.status, error_text
                    )
                    raise HomeAssistantError(f"ModelScope Image API error: {response.status}")

                result = await response.json()
                LOGGER.debug("Received ModelScope task response: %s", result)

                if "task_id" not in result:
                    LOGGER.error("Invalid ModelScope task response format: %s", result)
                    raise HomeAssistantError(ERROR_INVALID_RESPONSE)

                task_id = result["task_id"]

            # Step 2: Poll for task completion
            return await self._poll_modelscope_task(task_id)

        except aiohttp.ClientError as err:
            LOGGER.error("Network error calling ModelScope Image API: %s", err)
            raise HomeAssistantError(ERROR_GETTING_RESPONSE) from err
        except json.JSONDecodeError as err:
            LOGGER.error("Failed to decode ModelScope image JSON response: %s", err)
            raise HomeAssistantError(ERROR_INVALID_RESPONSE) from err

    async def _poll_modelscope_task(self, task_id: str) -> dict[str, Any]:
        """Poll ModelScope task until completion."""
        
        headers = {
            **self.headers,
            "X-ModelScope-Task-Type": "image_generation"
        }
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                url = f"{self.modelscope_base_url}v1/tasks/{task_id}"
                LOGGER.debug("Polling ModelScope task: %s", url)
                
                async with self.session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        LOGGER.error(
                            "ModelScope task polling error: %s - %s", response.status, error_text
                        )
                        raise HomeAssistantError(f"ModelScope task polling error: {response.status}")

                    result = await response.json()
                    LOGGER.debug("Task status response: %s", result)
                    
                    task_status = result.get("task_status")
                    
                    if task_status == "SUCCEED":
                        # Convert to OpenAI format for compatibility
                        output_images = result.get("output_images", [])
                        if not output_images:
                            LOGGER.error("No output images in successful task: %s", result)
                            raise HomeAssistantError("No images generated")
                        
                        return {
                            "data": [{"url": url} for url in output_images]
                        }
                    
                    elif task_status == "FAILED":
                        error_msg = result.get("error", "Image generation failed")
                        LOGGER.error("ModelScope image generation failed: %s", error_msg)
                        raise HomeAssistantError(f"Image generation failed: {error_msg}")
                    
                    elif task_status in ["PENDING", "RUNNING", "PROCESSING"]:
                        # Check timeout
                        elapsed_time = asyncio.get_event_loop().time() - start_time
                        if elapsed_time > TASK_MAX_WAIT_TIME:
                            LOGGER.error("ModelScope task timeout after %s seconds", elapsed_time)
                            raise HomeAssistantError("Image generation timeout")
                        
                        # Wait before next poll
                        await asyncio.sleep(TASK_POLL_INTERVAL)
                        continue
                    
                    else:
                        LOGGER.error("Unknown task status: %s", task_status)
                        raise HomeAssistantError(f"Unknown task status: {task_status}")

            except aiohttp.ClientError as err:
                LOGGER.error("Network error polling ModelScope task: %s", err)
                raise HomeAssistantError(ERROR_GETTING_RESPONSE) from err
            except json.JSONDecodeError as err:
                LOGGER.error("Failed to decode ModelScope task JSON response: %s", err)
                raise HomeAssistantError(ERROR_INVALID_RESPONSE) from err


def format_messages_for_modelscope(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Format messages for ModelScope API."""
    formatted = []
    
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        
        # Handle different content types
        if isinstance(content, list):
            # Multi-modal content (text + images) - keep original format for VL models
            formatted.append({
                "role": role,
                "content": content
            })
        else:
            # Simple text content
            formatted.append({
                "role": role,
                "content": str(content)
            })
    
    return formatted