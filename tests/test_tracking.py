import pytest

def test_tracking_import():
    """Проверка импорта модуля отслеживания"""
    try:
        with open('module_b_tracking.py', 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, 'module_b_tracking.py', 'exec')
        assert True
    except SyntaxError as e:
        pytest.fail(f"Syntax error: {e}")
    except FileNotFoundError:
        pytest.fail("File module_b_tracking.py not found")
    except UnicodeDecodeError as e:
        pytest.fail(f"Encoding error: {e}")
