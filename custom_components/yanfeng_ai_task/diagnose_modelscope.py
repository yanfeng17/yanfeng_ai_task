#!/usr/bin/env python3
"""
ModelScope API 诊断脚本
用于检查 API 连接、配置和响应格式
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path

# 模拟 Home Assistant 环境
class MockLogger:
    def debug(self, msg, *args):
        print(f"🔍 DEBUG: {msg % args if args else msg}")
    
    def info(self, msg, *args):
        print(f"ℹ️  INFO: {msg % args if args else msg}")
    
    def warning(self, msg, *args):
        print(f"⚠️  WARNING: {msg % args if args else msg}")
    
    def error(self, msg, *args):
        print(f"❌ ERROR: {msg % args if args else msg}")

LOGGER = MockLogger()

async def test_modelscope_api():
    """测试 ModelScope API 连接和响应"""
    
    print("🚀 开始 ModelScope API 诊断...")
    print("=" * 50)
    
    # 1. 检查环境变量
    print("🔍 检查环境变量...")
    api_key = os.getenv("MODELSCOPE_API_KEY")
    if not api_key:
        print("❌ 未找到 MODELSCOPE_API_KEY 环境变量")
        print("💡 请设置环境变量: export MODELSCOPE_API_KEY=your_api_key")
        return False
    else:
        print(f"✅ API Key 已配置 (长度: {len(api_key)})")
    
    # 2. 测试 API 连接
    print("\n🔍 测试 ModelScope API 连接...")
    
    base_url = "https://api.modelscope.cn/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # 测试简单的文本生成
    payload = {
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 100,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}v1/chat/completions"
            print(f"📡 发送请求到: {url}")
            print(f"📦 请求载荷: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"📊 响应状态码: {response.status}")
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ API 错误: {error_text}")
                    return False
                
                result = await response.json()
                print(f"📥 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                # 3. 验证响应格式
                print("\n🔍 验证响应格式...")
                if "choices" in result and result["choices"]:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        content = choice["message"]["content"]
                        print(f"✅ 成功提取响应内容: {content}")
                        return True
                    else:
                        print("❌ 响应格式不正确: 缺少 message.content")
                elif "output" in result and "text" in result["output"]:
                    content = result["output"]["text"]
                    print(f"✅ 成功提取响应内容 (output格式): {content}")
                    return True
                else:
                    print("❌ 未知的响应格式")
                    return False
                    
    except aiohttp.ClientError as err:
        print(f"❌ 网络错误: {err}")
        return False
    except json.JSONDecodeError as err:
        print(f"❌ JSON 解析错误: {err}")
        return False
    except Exception as err:
        print(f"❌ 未知错误: {err}")
        return False

async def main():
    """主函数"""
    success = await test_modelscope_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ModelScope API 诊断通过！")
        print("\n📋 建议的下一步操作:")
        print("1. 检查 Home Assistant 中的 API Key 配置")
        print("2. 确认集成配置中的模型名称正确")
        print("3. 查看 Home Assistant 完整日志获取更多信息")
    else:
        print("💥 ModelScope API 诊断失败！")
        print("\n🔧 可能的解决方案:")
        print("1. 检查 API Key 是否正确")
        print("2. 确认网络连接正常")
        print("3. 检查 ModelScope 服务状态")
        print("4. 验证模型名称是否支持")

if __name__ == "__main__":
    asyncio.run(main())