#!/usr/bin/env python3
"""Installation script for Yanfeng AI Task integration."""

import os
import shutil
import sys
from pathlib import Path


def find_homeassistant_config():
    """Find Home Assistant configuration directory."""
    possible_paths = [
        Path.home() / ".homeassistant",
        Path("/config"),  # Docker/HAOS
        Path("/usr/share/hassio/homeassistant"),  # Supervised
        Path.cwd() / "config",  # Development
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "configuration.yaml").exists():
            return path
    
    return None


def install_integration():
    """Install the integration to Home Assistant."""
    print("Yanfeng AI Task Integration Installer")
    print("=" * 40)
    
    # Find Home Assistant config directory
    config_dir = find_homeassistant_config()
    
    if not config_dir:
        print("❌ Could not find Home Assistant configuration directory.")
        print("Please specify the path manually:")
        config_path = input("Enter Home Assistant config path: ").strip()
        config_dir = Path(config_path)
        
        if not config_dir.exists():
            print(f"❌ Directory {config_dir} does not exist.")
            return False
    
    print(f"✓ Found Home Assistant config: {config_dir}")
    
    # Create custom_components directory if it doesn't exist
    custom_components_dir = config_dir / "custom_components"
    custom_components_dir.mkdir(exist_ok=True)
    
    # Create target directory
    target_dir = custom_components_dir / "yanfeng_ai_task"
    
    if target_dir.exists():
        print(f"⚠️  Integration already exists at {target_dir}")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Installation cancelled.")
            return False
        shutil.rmtree(target_dir)
    
    # Copy integration files
    source_dir = Path(__file__).parent
    
    try:
        shutil.copytree(source_dir, target_dir, ignore=shutil.ignore_patterns(
            "*.pyc", "__pycache__", "test_integration.py", "install.py", "README.md"
        ))
        print(f"✓ Integration installed to {target_dir}")
        
        # List installed files
        print("\nInstalled files:")
        for file_path in target_dir.rglob("*"):
            if file_path.is_file():
                print(f"  - {file_path.name}")
        
        print("\n🎉 Installation completed successfully!")
        print("\nNext steps:")
        print("1. Restart Home Assistant")
        print("2. Go to Settings > Devices & Services")
        print("3. Click 'Add Integration'")
        print("4. Search for 'Yanfeng AI Task'")
        print("5. Enter your ModelScope API key")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False


def uninstall_integration():
    """Uninstall the integration from Home Assistant."""
    print("Yanfeng AI Task Integration Uninstaller")
    print("=" * 40)
    
    config_dir = find_homeassistant_config()
    
    if not config_dir:
        print("❌ Could not find Home Assistant configuration directory.")
        return False
    
    target_dir = config_dir / "custom_components" / "yanfeng_ai_task"
    
    if not target_dir.exists():
        print("❌ Integration is not installed.")
        return False
    
    try:
        shutil.rmtree(target_dir)
        print(f"✓ Integration removed from {target_dir}")
        print("\n🎉 Uninstallation completed successfully!")
        print("Please restart Home Assistant to complete the removal.")
        return True
        
    except Exception as e:
        print(f"❌ Uninstallation failed: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall_integration()
    else:
        install_integration()


if __name__ == "__main__":
    main()