#!/usr/bin/env python3
"""
Test script to verify if ModelScope API-Inference supports base64-encoded image URLs.
This helps determine the best approach for handling local images in image editing.
"""

import requests
import time
import json
import base64
from PIL import Image
from io import BytesIO
from pathlib import Path

# Configuration
BASE_URL = 'https://api-inference.modelscope.cn/'
API_KEY = "ms-f5d96da7-0b03-45c5-8418-d5990b0b71c2"  # ModelScope Token

COMMON_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

def test_http_url():
    """Test with HTTP URL (this should work based on official example)"""
    print("\n" + "="*60)
    print("Test 1: HTTP URL (Official Example)")
    print("="*60)

    try:
        response = requests.post(
            f"{BASE_URL}v1/images/generations",
            headers={**COMMON_HEADERS, "X-ModelScope-Async-Mode": "true"},
            data=json.dumps({
                "model": "Qwen/Qwen-Image-Edit",
                "prompt": "turn the girl's hair blue",
                "image_url": "https://resources.modelscope.cn/aigc/image_edit.png"
            }, ensure_ascii=False).encode('utf-8')
        )

        response.raise_for_status()
        task_id = response.json()["task_id"]
        print(f"✅ Task created: {task_id}")

        # Poll for result
        for attempt in range(12):  # Wait up to 60 seconds
            result = requests.get(
                f"{BASE_URL}v1/tasks/{task_id}",
                headers={**COMMON_HEADERS, "X-ModelScope-Task-Type": "image_generation"},
            )
            result.raise_for_status()
            data = result.json()

            print(f"   Poll {attempt+1}: Status = {data['task_status']}")

            if data["task_status"] == "SUCCEED":
                print(f"✅ Success! Generated image URL: {data['output_images'][0]}")
                return True
            elif data["task_status"] == "FAILED":
                print(f"❌ Failed: {data.get('error', 'Unknown error')}")
                return False

            time.sleep(5)

        print("❌ Timeout waiting for result")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_base64_url():
    """Test with base64-encoded data URL"""
    print("\n" + "="*60)
    print("Test 2: Base64 Data URL")
    print("="*60)

    try:
        # Download the example image and encode it as base64
        print("Downloading example image...")
        img_response = requests.get("https://resources.modelscope.cn/aigc/image_edit.png")
        img_response.raise_for_status()

        # Convert to base64
        image_data = base64.b64encode(img_response.content).decode('utf-8')
        base64_url = f"data:image/png;base64,{image_data}"

        print(f"Image encoded to base64 ({len(image_data)} chars)")
        print(f"Testing with: data:image/png;base64,{image_data[:50]}...")

        response = requests.post(
            f"{BASE_URL}v1/images/generations",
            headers={**COMMON_HEADERS, "X-ModelScope-Async-Mode": "true"},
            data=json.dumps({
                "model": "Qwen/Qwen-Image-Edit",
                "prompt": "turn the girl's hair blue",
                "image_url": base64_url
            }, ensure_ascii=False).encode('utf-8')
        )

        response.raise_for_status()
        task_id = response.json()["task_id"]
        print(f"✅ Task created: {task_id}")

        # Poll for result
        for attempt in range(12):  # Wait up to 60 seconds
            result = requests.get(
                f"{BASE_URL}v1/tasks/{task_id}",
                headers={**COMMON_HEADERS, "X-ModelScope-Task-Type": "image_generation"},
            )
            result.raise_for_status()
            data = result.json()

            print(f"   Poll {attempt+1}: Status = {data['task_status']}")

            if data["task_status"] == "SUCCEED":
                print(f"✅ Success! Generated image URL: {data['output_images'][0]}")
                return True
            elif data["task_status"] == "FAILED":
                print(f"❌ Failed: {data.get('error', 'Unknown error')}")
                return False

            time.sleep(5)

        print("❌ Timeout waiting for result")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 ModelScope API Image Editing - Base64 Support Test")
    print("="*60)

    # Test HTTP URL first (should work)
    http_result = test_http_url()

    # Test Base64 (unknown support)
    base64_result = test_base64_url()

    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    print(f"HTTP URL:  {'✅ Supported' if http_result else '❌ Failed'}")
    print(f"Base64 URL: {'✅ Supported' if base64_result else '❌ Not supported'}")

    if http_result and not base64_result:
        print("\n💡 Recommendation: Use HTTP URLs only")
        print("   For local files, you'll need to upload them to a public URL first")
    elif http_result and base64_result:
        print("\n💡 Recommendation: Both methods supported!")
        print("   Use Base64 for local files, HTTP URLs for web images")
    else:
        print("\n⚠️ Neither method works - API may have issues")
