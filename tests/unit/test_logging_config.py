import json
import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.utils.logging_config import (
    AuditJSONFormatter,
    get_logger,
    log_function_call,
    log_performance,
    setup_logging,
)


def test_audit_json_formatter_includes_audit_payload():
    formatter = AuditJSONFormatter()
    record = logging.LogRecord(
        name="wizard.audit",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="audit",
        args=(),
        exc_info=None,
    )
    record.audit = {"event": "secret_created", "project": "Test"}

    formatted = formatter.format(record)
    payload = json.loads(formatted)
    assert payload["event"] == "secret_created"
    assert payload["project"] == "Test"
    assert payload["message"] == "audit"


def test_setup_logging_creates_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    setup_logging(log_level="INFO", log_dir=str(tmp_path))

    expected_files = [
        "wizard_app.log",
        "wizard_debug.log",
        "wizard_error.log",
        "wizard_server.log",
        "audit/wizard_audit.log",
    ]
    for rel_path in expected_files:
        assert (tmp_path / rel_path).exists()

    audit_logger = logging.getLogger("wizard.audit")
    audit_logger.info("Test audit entry", extra={"audit": {"event": "test"}})

    audit_log_path = tmp_path / "audit" / "wizard_audit.log"
    contents = audit_log_path.read_text(encoding="utf-8")
    assert "Test audit entry" in contents
    assert "\"event\": \"test\"" in contents


def test_get_logger_returns_logger():
    logger = get_logger("test.logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.logger"


def test_log_function_call_decorator_logs_debug(caplog):
    caplog.set_level(logging.DEBUG)

    @log_function_call
    def sample(a, b):
        return a + b

    result = sample(1, 2)
    assert result == 3
    assert any("Calling sample" in record.message for record in caplog.records)


def test_log_performance_decorator_logs_duration(caplog):
    caplog.set_level(logging.INFO)

    @log_performance
    def sample_task():
        return "done"

    assert sample_task() == "done"
    assert any("sample_task completed" in record.message for record in caplog.records)
