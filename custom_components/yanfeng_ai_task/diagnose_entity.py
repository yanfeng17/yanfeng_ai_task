#!/usr/bin/env python3
"""
诊断 Yanfeng AI Task 实体注册问题
"""

import json
import os

def check_manifest():
    """检查 manifest.json 配置"""
    print("=" * 60)
    print("检查 manifest.json 配置")
    print("=" * 60)
    
    try:
        with open("manifest.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        print(f"✓ Domain: {manifest.get('domain')}")
        print(f"✓ Name: {manifest.get('name')}")
        print(f"✓ Config Flow: {manifest.get('config_flow')}")
        print(f"✓ Integration Type: {manifest.get('integration_type')}")
        print(f"✓ Dependencies: {manifest.get('dependencies', [])}")
        print(f"✓ After Dependencies: {manifest.get('after_dependencies', [])}")
        
        # 检查是否有 ai_task 相关依赖
        deps = manifest.get('dependencies', []) + manifest.get('after_dependencies', [])
        if 'ai_task' in deps:
            print("✓ ai_task 依赖已声明")
        else:
            print("⚠ ai_task 依赖未在 dependencies 中声明")
            
        return True
        
    except Exception as e:
        print(f"✗ 读取 manifest.json 失败: {e}")
        return False

def check_init_file():
    """检查 __init__.py 平台设置"""
    print("\n" + "=" * 60)
    print("检查 __init__.py 平台设置")
    print("=" * 60)
    
    try:
        with open("__init__.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查平台声明
        if "Platform.AI_TASK" in content:
            print("✓ Platform.AI_TASK 已声明")
        else:
            print("✗ Platform.AI_TASK 未声明")
            
        if "PLATFORMS" in content:
            print("✓ PLATFORMS 常量已定义")
        else:
            print("✗ PLATFORMS 常量未定义")
            
        # 检查平台设置调用
        if "async_forward_entry_setups" in content:
            print("✓ async_forward_entry_setups 调用已存在")
        else:
            print("✗ async_forward_entry_setups 调用缺失")
            
        return True
        
    except Exception as e:
        print(f"✗ 读取 __init__.py 失败: {e}")
        return False

def check_ai_task_file():
    """检查 ai_task.py 实体定义"""
    print("\n" + "=" * 60)
    print("检查 ai_task.py 实体定义")
    print("=" * 60)
    
    try:
        with open("ai_task.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键函数和类
        checks = [
            ("async_setup_entry", "平台设置函数"),
            ("YanfengAITaskEntity", "AI Task 实体类"),
            ("async_generate_data", "数据生成方法"),
            ("async_generate_image", "图像生成方法"),
            ("from homeassistant.components import ai_task", "ai_task 组件导入"),
            ("AITaskEntity", "AI Task 基类"),
        ]
        
        for check, desc in checks:
            if check in content:
                print(f"✓ {desc}: {check}")
            else:
                print(f"✗ {desc}: {check} 缺失")
        
        # 检查实体注册逻辑
        if "async_add_entities" in content:
            print("✓ async_add_entities 调用已存在")
        else:
            print("✗ async_add_entities 调用缺失")
            
        # 检查主实体创建
        if "YanfengAITaskEntity(hass, config_entry, None)" in content or "YanfengAITaskEntity(hass, entry, None)" in content:
            print("✓ 主实体创建逻辑已存在")
        else:
            print("✗ 主实体创建逻辑缺失")
            
        return True
        
    except Exception as e:
        print(f"✗ 读取 ai_task.py 失败: {e}")
        return False

def check_entity_file():
    """检查 entity.py 基类定义"""
    print("\n" + "=" * 60)
    print("检查 entity.py 基类定义")
    print("=" * 60)
    
    try:
        with open("entity.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查基类
        if "YanfengAIBaseEntity" in content:
            print("✓ YanfengAIBaseEntity 基类已定义")
        else:
            print("✗ YanfengAIBaseEntity 基类缺失")
            
        # 检查必要属性
        attrs = ["unique_id", "name", "device_info"]
        for attr in attrs:
            if f"def {attr}" in content or f"def {attr}(" in content:
                print(f"✓ {attr} 属性已定义")
            else:
                print(f"⚠ {attr} 属性可能缺失")
                
        return True
        
    except Exception as e:
        print(f"✗ 读取 entity.py 失败: {e}")
        return False

def check_file_structure():
    """检查文件结构"""
    print("\n" + "=" * 60)
    print("检查文件结构")
    print("=" * 60)
    
    required_files = [
        "__init__.py",
        "ai_task.py", 
        "entity.py",
        "manifest.json",
        "config_flow.py",
        "const.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} 缺失")

def main():
    """主诊断函数"""
    print("Yanfeng AI Task 实体注册诊断")
    print("=" * 60)
    
    # 检查当前目录
    print(f"当前目录: {os.getcwd()}")
    
    # 执行各项检查
    check_file_structure()
    check_manifest()
    check_init_file()
    check_ai_task_file()
    check_entity_file()
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    print("\n如果所有检查都通过，但实体仍未显示，可能的原因：")
    print("1. Home Assistant 需要重启")
    print("2. 集成配置条目需要重新加载")
    print("3. 日志中可能有错误信息")
    print("4. API 密钥配置问题")
    print("\n建议检查 Home Assistant 日志：")
    print("设置 -> 系统 -> 日志 -> 搜索 'yanfeng_ai_task'")

if __name__ == "__main__":
    main()