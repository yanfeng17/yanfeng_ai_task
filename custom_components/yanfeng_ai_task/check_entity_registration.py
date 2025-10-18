#!/usr/bin/env python3
"""
详细检查 AI Task 实体注册过程
"""

def check_ai_task_registration():
    """检查 ai_task.py 中的实体注册逻辑"""
    print("=" * 60)
    print("检查 AI Task 实体注册详情")
    print("=" * 60)
    
    try:
        with open("ai_task.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        print("1. 检查 async_setup_entry 函数:")
        lines = content.split('\n')
        in_setup_function = False
        setup_function_lines = []
        
        for i, line in enumerate(lines):
            if "async def async_setup_entry" in line:
                in_setup_function = True
                print(f"   ✓ 找到函数定义在第 {i+1} 行")
            elif in_setup_function:
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    # 函数结束
                    break
                setup_function_lines.append(line)
        
        if setup_function_lines:
            print("   函数内容:")
            for line in setup_function_lines[:15]:  # 显示前15行
                print(f"     {line}")
            if len(setup_function_lines) > 15:
                print(f"     ... (还有 {len(setup_function_lines) - 15} 行)")
        
        print("\n2. 检查实体创建逻辑:")
        
        # 检查主实体创建
        main_entity_patterns = [
            "YanfengAITaskEntity(hass, config_entry, None)",
            "YanfengAITaskEntity(hass, entry, None)",
            "entities.append(YanfengAITaskEntity(hass",
        ]
        
        main_entity_found = False
        for pattern in main_entity_patterns:
            if pattern in content:
                print(f"   ✓ 主实体创建: {pattern}")
                main_entity_found = True
                break
        
        if not main_entity_found:
            print("   ✗ 主实体创建逻辑未找到")
        
        # 检查子实体创建
        subentry_patterns = [
            "for subentry in config_entry.subentries.values()",
            "for subentry in entry.subentries.values()",
            "YanfengAITaskEntity(hass, config_entry, subentry)",
            "YanfengAITaskEntity(hass, entry, subentry)",
        ]
        
        subentry_found = False
        for pattern in subentry_patterns:
            if pattern in content:
                print(f"   ✓ 子实体创建: {pattern}")
                subentry_found = True
                break
        
        if not subentry_found:
            print("   ⚠ 子实体创建逻辑未找到")
        
        # 检查 async_add_entities 调用
        if "async_add_entities(" in content:
            print("   ✓ async_add_entities 调用存在")
        else:
            print("   ✗ async_add_entities 调用缺失")
        
        print("\n3. 检查实体类定义:")
        
        # 查找类定义
        class_start = -1
        for i, line in enumerate(lines):
            if "class YanfengAITaskEntity" in line:
                class_start = i
                print(f"   ✓ 类定义在第 {i+1} 行")
                break
        
        if class_start >= 0:
            # 显示类定义的前几行
            print("   类定义:")
            for i in range(class_start, min(class_start + 10, len(lines))):
                if lines[i].strip():
                    print(f"     {lines[i]}")
        
        print("\n4. 检查必要的导入:")
        imports_to_check = [
            "from homeassistant.components import ai_task",
            "from homeassistant.components.ai_task",
            "import aiohttp",
            "AITaskEntity",
            "YanfengAILLMBaseEntity"
        ]
        
        for imp in imports_to_check:
            if imp in content:
                print(f"   ✓ {imp}")
            else:
                print(f"   ✗ {imp} 缺失")
        
        return True
        
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

def check_platform_registration():
    """检查平台注册"""
    print("\n" + "=" * 60)
    print("检查平台注册")
    print("=" * 60)
    
    try:
        with open("__init__.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 查找 PLATFORMS 定义
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "PLATFORMS" in line and "=" in line:
                print(f"PLATFORMS 定义在第 {i+1} 行:")
                # 显示 PLATFORMS 定义及其周围几行
                start = max(0, i-2)
                end = min(len(lines), i+5)
                for j in range(start, end):
                    marker = ">>> " if j == i else "    "
                    print(f"{marker}{lines[j]}")
                break
        
        return True
        
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

def main():
    """主函数"""
    print("Yanfeng AI Task 实体注册详细检查")
    
    check_ai_task_registration()
    check_platform_registration()
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)

if __name__ == "__main__":
    main()