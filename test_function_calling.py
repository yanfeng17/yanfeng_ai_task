#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to verify ModelScope API function calling support."""

import asyncio
import json
import os
import sys
from typing import Any

import aiohttp

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None


# 测试用的工具定义（模拟GetLiveContext）
TEST_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_temperature",
            "description": "Get the current temperature of a room",
            "parameters": {
                "type": "object",
                "properties": {
                    "room": {
                        "type": "string",
                        "description": "The name of the room (e.g., bedroom, living room, study)",
                    }
                },
                "required": ["room"],
            },
        },
    }
]


async def test_modelscope_function_calling(api_key: str):
    """Test ModelScope API with function calling."""

    print("=" * 80)
    print("测试 ModelScope API Function Calling 支持")
    print("=" * 80)
    print()

    # 创建HTTP会话
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        url = "https://api-inference.modelscope.cn/v1/chat/completions"

        # ==================== 测试1: 不带工具的普通调用 ====================
        print("测试 1: 普通调用（不带工具）")
        print("-" * 80)

        payload_simple = {
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "messages": [
                {"role": "user", "content": "你好，请问1+1等于几？"}
            ],
            "max_tokens": 100,
        }

        print(f"请求: {json.dumps(payload_simple, ensure_ascii=False, indent=2)}")
        print()

        try:
            async with session.post(url, headers=headers, json=payload_simple) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 响应状态: {response.status}")
                    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

                    # 提取回复
                    if "choices" in result and result["choices"]:
                        content = result["choices"][0]["message"]["content"]
                        print(f"\n模型回复: {content}")
                else:
                    error_text = await response.text()
                    print(f"❌ 响应状态: {response.status}")
                    print(f"错误: {error_text}")
                    return False
        except Exception as err:
            print(f"❌ 异常: {err}")
            return False

        print("\n")

        # ==================== 测试2: 带工具的调用 ====================
        print("测试 2: 带工具调用（Function Calling）")
        print("-" * 80)

        payload_with_tools = {
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can get room temperatures. When user asks about temperature, use the get_temperature function."
                },
                {"role": "user", "content": "现在书房的温度是多少？"}
            ],
            "tools": TEST_TOOLS,
            "tool_choice": "auto",
            "max_tokens": 500,
        }

        print(f"请求: {json.dumps(payload_with_tools, ensure_ascii=False, indent=2)}")
        print()

        try:
            async with session.post(url, headers=headers, json=payload_with_tools) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 响应状态: {response.status}")
                    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

                    # 检查是否有tool_calls
                    if "choices" in result and result["choices"]:
                        message = result["choices"][0]["message"]

                        if "tool_calls" in message:
                            print(f"\n✅ 模型返回了 {len(message['tool_calls'])} 个工具调用!")

                            for i, tool_call in enumerate(message["tool_calls"]):
                                print(f"\n工具调用 {i+1}:")
                                print(f"  - 函数名: {tool_call['function']['name']}")
                                print(f"  - 参数: {tool_call['function']['arguments']}")

                            # 模拟工具执行结果
                            print("\n" + "=" * 80)
                            print("测试 3: 发送工具执行结果回模型")
                            print("-" * 80)

                            # 构建包含工具结果的消息
                            messages_with_result = payload_with_tools["messages"].copy()

                            # 添加助手的工具调用消息
                            messages_with_result.append({
                                "role": "assistant",
                                "content": message.get("content", ""),
                                "tool_calls": message["tool_calls"]
                            })

                            # 添加工具执行结果
                            for tool_call in message["tool_calls"]:
                                # 模拟工具返回结果
                                mock_result = {
                                    "temperature": 30.8,
                                    "unit": "°C",
                                    "room": "书房"
                                }

                                messages_with_result.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.get("id", "call_1"),
                                    "name": tool_call["function"]["name"],
                                    "content": json.dumps(mock_result, ensure_ascii=False)
                                })

                            # 发送包含工具结果的请求
                            payload_with_result = {
                                "model": "Qwen/Qwen2.5-72B-Instruct",
                                "messages": messages_with_result,
                                "tools": TEST_TOOLS,
                                "max_tokens": 500,
                            }

                            print(f"请求（包含工具结果）:")
                            print(f"消息数量: {len(messages_with_result)}")
                            for msg in messages_with_result[-2:]:
                                print(f"  {msg['role']}: {str(msg)[:100]}...")
                            print()

                            async with session.post(url, headers=headers, json=payload_with_result) as response2:
                                if response2.status == 200:
                                    result2 = await response2.json()
                                    print(f"✅ 响应状态: {response2.status}")
                                    print(f"响应: {json.dumps(result2, ensure_ascii=False, indent=2)}")

                                    if "choices" in result2 and result2["choices"]:
                                        final_content = result2["choices"][0]["message"]["content"]
                                        print(f"\n✅ 模型最终回复: {final_content}")

                                        return True
                                else:
                                    error_text = await response2.text()
                                    print(f"❌ 响应状态: {response2.status}")
                                    print(f"错误: {error_text}")
                                    return False

                        else:
                            print(f"\n⚠️  模型没有调用工具，直接回复:")
                            print(f"   {message.get('content', '(无内容)')}")
                            print("\n这可能意味着:")
                            print("  1. 模型认为不需要调用工具")
                            print("  2. ModelScope API不支持function calling")
                            print("  3. 工具定义有问题")
                            return False
                else:
                    error_text = await response.text()
                    print(f"❌ 响应状态: {response.status}")
                    print(f"错误: {error_text}")

                    if response.status == 400:
                        print("\n可能的原因:")
                        print("  - ModelScope API不支持tools参数")
                        print("  - 工具定义格式错误")

                    return False
        except Exception as err:
            print(f"❌ 异常: {err}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """主函数."""
    # 从环境变量获取API key
    api_key = os.getenv("MODELSCOPE_API_KEY")

    if not api_key:
        print("❌ 错误: 未找到 MODELSCOPE_API_KEY 环境变量")
        print()
        print("使用方法:")
        print("  1. 设置环境变量:")
        print("     export MODELSCOPE_API_KEY='your-api-key'")
        print("  2. 或者直接传入:")
        print("     python test_function_calling.py YOUR_API_KEY")
        print()

        # 尝试从命令行参数获取
        if len(sys.argv) > 1:
            api_key = sys.argv[1]
            print(f"✅ 使用命令行参数中的API Key: {api_key[:10]}...")
        else:
            sys.exit(1)
    else:
        print(f"✅ 使用环境变量中的API Key: {api_key[:10]}...")
        print()

    # 运行测试
    success = await test_modelscope_function_calling(api_key)

    print("\n" + "=" * 80)
    if success:
        print("✅ 测试通过! ModelScope API 支持 Function Calling!")
    else:
        print("❌ 测试失败! ModelScope API 可能不支持 Function Calling 或配置有问题")
    print("=" * 80)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
