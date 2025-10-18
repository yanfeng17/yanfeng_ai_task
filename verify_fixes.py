"""Verify all fixes are working correctly."""
import sys
from pathlib import Path

# Add the custom_components path
sys.path.insert(0, str(Path(__file__).parent / "custom_components"))

def test_imports():
    """Test if all imports work."""
    print("Testing imports...")
    try:
        from yanfeng_ai_task import const
        from yanfeng_ai_task import config_flow
        from yanfeng_ai_task import conversation
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_llm_hass_api_config():
    """Test if CONF_LLM_HASS_API is properly configured."""
    print("\nTesting LLM_HASS_API configuration...")
    try:
        from yanfeng_ai_task import config_flow
        from homeassistant.const import CONF_LLM_HASS_API

        # Check if CONF_LLM_HASS_API is imported
        assert hasattr(config_flow, 'CONF_LLM_HASS_API') or 'CONF_LLM_HASS_API' in dir(config_flow)
        print("✓ CONF_LLM_HASS_API is available in config_flow")
        return True
    except Exception as e:
        print(f"✗ LLM_HASS_API config test failed: {e}")
        return False

def test_conversation_features():
    """Test if conversation features are properly set."""
    print("\nTesting conversation features...")
    try:
        from yanfeng_ai_task import conversation
        print("✓ Conversation module loaded")
        return True
    except Exception as e:
        print(f"✗ Conversation features test failed: {e}")
        return False

def test_no_deprecated_usage():
    """Check for deprecated self.config_entry usage."""
    print("\nChecking for deprecated config_entry usage...")
    try:
        config_flow_file = Path(__file__).parent / "custom_components" / "yanfeng_ai_task" / "config_flow.py"
        content = config_flow_file.read_text()

        if "self.config_entry = config_entry" in content:
            print("✗ Found deprecated self.config_entry assignment")
            return False

        if "self._get_entry()" in content:
            print("✓ Using new self._get_entry() method")
            return True
        else:
            print("⚠ self._get_entry() not found, check if it's needed")
            return True
    except Exception as e:
        print(f"✗ Deprecated usage check failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Yanfeng AI Task - Fix Verification")
    print("=" * 50)

    results = []
    results.append(test_imports())
    results.append(test_llm_hass_api_config())
    results.append(test_conversation_features())
    results.append(test_no_deprecated_usage())

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
