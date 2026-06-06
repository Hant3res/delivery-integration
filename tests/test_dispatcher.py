import pytest

def test_dispatcher_import():
    """Проверка импорта модуля диспетчера"""
    try:
        with open('module_a_dispatcher.py', 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, 'module_a_dispatcher.py', 'exec')
        assert True
    except SyntaxError as e:
        pytest.fail(f"Syntax error: {e}")
    except FileNotFoundError:
        pytest.fail("File module_a_dispatcher.py not found")
    except UnicodeDecodeError as e:
        pytest.fail(f"Encoding error: {e}")
