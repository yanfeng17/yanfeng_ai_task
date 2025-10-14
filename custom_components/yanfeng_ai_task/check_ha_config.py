#!/usr/bin/env python3
"""
检查 Home Assistant 中 Yanfeng AI Task 集成的配置
"""

import json
import os
from pathlib import Path

def check_ha_config():
    """检查 Home Assistant 配置"""
    
    print("🔍 检查 Home Assistant 集成配置...")
    print("=" * 50)
    
    # 常见的 Home Assistant 配置路径
    possible_config_paths = [
        "/config",
        "C:\\Users\\%USERNAME%\\AppData\\Roaming\\.homeassistant",
        "C:\\homeassistant",
        os.path.expanduser("~/.homeassistant"),
    ]
    
    config_path = None
    for path in possible_config_paths:
        expanded_path = os.path.expandvars(path)
        if os.path.exists(expanded_path):
            config_path = Path(expanded_path)
            break
    
    if not config_path:
        print("❌ 未找到 Home Assistant 配置目录")
        print("💡 请确认 Home Assistant 安装路径")
        return
    
    print(f"✅ 找到配置目录: {config_path}")
    
    # 检查集成配置
    config_entries_path = config_path / ".storage" / "core.config_entries"
    
    if not config_entries_path.exists():
        print("❌ 未找到集成配置文件")
        return
    
    try:
        with open(config_entries_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 查找 Yanfeng AI Task 集成
        yanfeng_entries = []
        for entry in config_data.get("data", {}).get("entries", []):
            if entry.get("domain") == "yanfeng_ai_task":
                yanfeng_entries.append(entry)
        
        if not yanfeng_entries:
            print("❌ 未找到 Yanfeng AI Task 集成配置")
            print("💡 请在 Home Assistant 中添加 Yanfeng AI Task 集成")
            return
        
        print(f"✅ 找到 {len(yanfeng_entries)} 个 Yanfeng AI Task 配置")
        
        # 检查每个配置的 API Key
        for i, entry in enumerate(yanfeng_entries):
            print(f"\n📋 配置 {i+1}:")
            print(f"   标题: {entry.get('title', 'N/A')}")
            print(f"   状态: {entry.get('state', 'N/A')}")
            
            data = entry.get("data", {})
            api_key = data.get("api_key")
            
            if not api_key:
                print("   ❌ API Key: 未配置")
                print("   💡 需要在集成设置中配置 API Key")
            else:
                print(f"   ✅ API Key: 已配置 (长度: {len(api_key)})")
                print(f"   🔑 API Key 预览: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
            
            # 检查其他配置
            chat_model = data.get("chat_model", "N/A")
            print(f"   🤖 聊天模型: {chat_model}")
            
            temperature = data.get("temperature", "N/A")
            print(f"   🌡️  温度: {temperature}")
    
    except Exception as err:
        print(f"❌ 读取配置文件时出错: {err}")

def main():
    """主函数"""
    check_ha_config()
    
    print("\n" + "=" * 50)
    print("📋 解决 API 调用问题的步骤:")
    print("1. 确保在 Home Assistant 集成设置中配置了正确的 ModelScope API Key")
    print("2. 重新加载 Yanfeng AI Task 集成")
    print("3. 检查 Home Assistant 日志确认 API Key 验证通过")
    print("4. 测试生成数据功能")
    
    print("\n🔗 获取 ModelScope API Key:")
    print("   访问: https://modelscope.cn/my/myaccesstoken")

if __name__ == "__main__":
    main()