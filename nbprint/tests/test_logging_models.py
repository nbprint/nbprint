import logging

import pytest

from nbprint.models.logging import LoggingConfig


@pytest.fixture
def restore_root_logger():
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    root.handlers[:] = handlers
    root.setLevel(level)


@pytest.mark.usefixtures("restore_root_logger")
def test_logging_config_applies_dict_config():
    LoggingConfig()()

    root = logging.getLogger()
    assert root.level == logging.DEBUG
    assert any(h.level == logging.WARNING for h in root.handlers)
