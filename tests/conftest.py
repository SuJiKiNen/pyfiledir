import pytest
from src.pyfiledir import DEFAULT_PYFILEDIR_ENVS


@pytest.fixture(autouse=True)
def set_pyfiledir_default_envs(monkeypatch):
    for env_name, val in DEFAULT_PYFILEDIR_ENVS.items():
        monkeypatch.setenv(env_name, val)
    monkeypatch.setenv("PYFILEDIR_ADDS_TRAILING_SLASH", "False")
    monkeypatch.setenv("PYFILEDIR_COMPLETES_COMMON_PREFIX", "False")
