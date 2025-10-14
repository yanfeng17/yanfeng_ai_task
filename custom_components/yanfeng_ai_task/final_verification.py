#!/usr/bin/env python3
"""
最终验证 Yanfeng AI Task 集成的完整性
"""

import json

def final_verification():
    """执行最终验证"""
    print("=" * 70)
    print("Yanfeng AI Task 集成最终验证")
    print("=" * 70)
    
    all_checks_passed = True
    
    # 1. 检查 manifest.json
    print("\n1. Manifest 配置检查:")
    try:
        with open("manifest.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        checks = [
            ("domain", "yanfeng_ai_task"),
            ("config_flow", True),
            ("integration_type", "service"),
        ]
        
        for key, expected in checks:
            if manifest.get(key) == expected:
                print(f"   ✓ {key}: {manifest.get(key)}")
            else:
                print(f"   ✗ {key}: {manifest.get(key)} (期望: {expected})")
                all_checks_passed = False
        
        # 检查依赖
        deps = manifest.get('dependencies', [])
        if 'ai_task' in deps and 'conversation' in deps:
            print(f"   ✓ dependencies: {deps}")
        else:
            print(f"   ✗ dependencies: {deps} (缺少 ai_task 或 conversation)")
            all_checks_passed = False
            
    except Exception as e:
        print(f"   ✗ manifest.json 检查失败: {e}")
        all_checks_passed = False
    
    # 2. 检查平台注册
    print("\n2. 平台注册检查:")
    try:
        with open("__init__.py", "r", encoding="utf-8") as f:
            init_content = f.read()
        
        platform_checks = [
            ("Platform.AI_TASK", "AI Task 平台"),
            ("Platform.CONVERSATION", "对话平台"),
            ("async_forward_entry_setups", "平台设置调用"),
        ]
        
        for check, desc in platform_checks:
            if check in init_content:
                print(f"   ✓ {desc}")
            else:
                print(f"   ✗ {desc} 缺失")
                all_checks_passed = False
                
    except Exception as e:
        print(f"   ✗ __init__.py 检查失败: {e}")
        all_checks_passed = False
    
    # 3. 检查实体注册
    print("\n3. 实体注册检查:")
    try:
        with open("ai_task.py", "r", encoding="utf-8") as f:
            ai_task_content = f.read()
        
        entity_checks = [
            ("async def async_setup_entry", "平台设置函数"),
            ("class YanfengAITaskEntity", "AI Task 实体类"),
            ("ai_task.AITaskEntity", "AI Task 基类继承"),
            ("async_add_entities(", "实体添加调用"),
            ("YanfengAITaskEntity(hass, config_entry, None)", "主实体创建"),
            ("for subentry in config_entry.subentries.values()", "子实体处理"),
        ]
        
        for check, desc in entity_checks:
            if check in ai_task_content:
                print(f"   ✓ {desc}")
            else:
                print(f"   ✗ {desc} 缺失")
                all_checks_passed = False
                
    except Exception as e:
        print(f"   ✗ ai_task.py 检查失败: {e}")
        all_checks_passed = False
    
    # 4. 检查实体功能
    print("\n4. 实体功能检查:")
    try:
        with open("ai_task.py", "r", encoding="utf-8") as f:
            ai_task_content = f.read()
        
        feature_checks = [
            ("async def _async_generate_data", "数据生成功能"),
            ("async def _async_generate_image", "图像生成功能"),
            ("AITaskEntityFeature.GENERATE_DATA", "数据生成特性"),
            ("AITaskEntityFeature.GENERATE_IMAGE", "图像生成特性"),
            ("GenImageTaskResult", "图像结果格式"),
            ("image_data", "图像数据字段"),
        ]
        
        for check, desc in feature_checks:
            if check in ai_task_content:
                print(f"   ✓ {desc}")
            else:
                print(f"   ⚠ {desc} 可能缺失")
                
    except Exception as e:
        print(f"   ✗ 功能检查失败: {e}")
        all_checks_passed = False
    
    # 5. 检查必要导入
    print("\n5. 导入检查:")
    try:
        with open("ai_task.py", "r", encoding="utf-8") as f:
            ai_task_content = f.read()
        
        import_checks = [
            ("from homeassistant.components import ai_task", "AI Task 组件"),
            ("import aiohttp", "HTTP 客户端"),
            ("YanfengAILLMBaseEntity", "基类导入"),
        ]
        
        for check, desc in import_checks:
            if check in ai_task_content:
                print(f"   ✓ {desc}")
            else:
                print(f"   ✗ {desc} 缺失")
                all_checks_passed = False
                
    except Exception as e:
        print(f"   ✗ 导入检查失败: {e}")
        all_checks_passed = False
    
    # 总结
    print("\n" + "=" * 70)
    if all_checks_passed:
        print("🎉 所有检查通过！集成已准备就绪")
        print("\n下一步操作:")
        print("1. 重启 Home Assistant")
        print("2. 在集成页面重新加载 Yanfeng AI Task 集成")
        print("3. 检查开发者工具 -> 服务 中是否有 ai_task.generate_data 和 ai_task.generate_image")
        print("4. 查看 Home Assistant 日志确认没有错误")
    else:
        print("❌ 部分检查未通过，请检查上述错误")
    print("=" * 70)
    
    return all_checks_passed

if __name__ == "__main__":
    final_verification()