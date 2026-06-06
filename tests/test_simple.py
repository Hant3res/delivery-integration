import pytest

def test_dispatcher_import():
    try:
        with open('module_a_dispatcher.py', 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, 'module_a_dispatcher.py', 'exec')
        assert True
    except Exception as e:
        pytest.fail(f"Failed: {e}")

def test_tracking_import():
    try:
        with open('module_b_tracking.py', 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, 'module_b_tracking.py', 'exec')
        assert True
    except Exception as e:
        pytest.fail(f"Failed: {e}")

def test_notify_import():
    try:
        with open('module_c_notify.py', 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, 'module_c_notify.py', 'exec')
        assert True
    except Exception as e:
        pytest.fail(f"Failed: {e}")
