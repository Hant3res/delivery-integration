import pytest

def test_notify_import():
    """Проверка импорта модуля уведомлений"""
    try:
        with open('module_c_notify.py', 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, 'module_c_notify.py', 'exec')
        assert True
    except SyntaxError as e:
        pytest.fail(f"Syntax error: {e}")
    except FileNotFoundError:
        pytest.fail("File module_c_notify.py not found")
    except UnicodeDecodeError as e:
        pytest.fail(f"Encoding error: {e}")
