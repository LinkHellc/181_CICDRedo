"""
Unit tests for LogViewer widget.
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import sys
from src.ui.widgets.log_viewer import LogViewer


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def log_viewer(qapp):
    """Create LogViewer instance for testing."""
    viewer = LogViewer()
    yield viewer
    viewer.deleteLater()


class TestLogViewerInitialization:
    """Tests for LogViewer initialization."""

    def test_log_viewer_creation(self, log_viewer):
        """Test LogViewer can be created."""
        assert log_viewer is not None
        assert isinstance(log_viewer, LogViewer)

    def test_log_viewer_is_read_only(self, log_viewer):
        """Test LogViewer is read-only."""
        assert log_viewer.isReadOnly()

    def test_log_viewer_has_monospace_font(self, log_viewer):
        """Test LogViewer uses monospace font."""
        font = log_viewer.font()
        assert font.family() in ["Consolas", "Courier New"]
        assert font.pointSize() == 9

    def test_log_viewer_max_lines_constant(self, log_viewer):
        """Test MAX_LOG_LINES constant is defined."""
        assert hasattr(log_viewer, 'MAX_LOG_LINES')
        assert log_viewer.MAX_LOG_LINES == 1000


class TestLogLevelDetection:
    """Tests for log level detection."""

    def test_detect_error_level(self, log_viewer):
        """Test ERROR level detection."""
        assert log_viewer._detect_log_level("ERROR: Something went wrong") == LogViewer.LOG_LEVEL_ERROR
        assert log_viewer._detect_log_level("Error: Something went wrong") == LogViewer.LOG_LEVEL_ERROR
        assert log_viewer._detect_log_level("error: Something went wrong") == LogViewer.LOG_LEVEL_ERROR
        assert log_viewer._detect_log_level("操作失败") == LogViewer.LOG_LEVEL_ERROR
        assert log_viewer._detect_log_level("发生异常") == LogViewer.LOG_LEVEL_ERROR

    def test_detect_warning_level(self, log_viewer):
        """Test WARNING level detection."""
        assert log_viewer._detect_log_level("WARNING: Something to note") == LogViewer.LOG_LEVEL_WARNING
        assert log_viewer._detect_log_level("Warning: Something to note") == LogViewer.LOG_LEVEL_WARNING
        assert log_viewer._detect_log_level("warning: Something to note") == LogViewer.LOG_LEVEL_WARNING
        assert log_viewer._detect_log_level("警告：注意") == LogViewer.LOG_LEVEL_WARNING
        assert log_viewer._detect_log_level("WARN: Something") == LogViewer.LOG_LEVEL_WARNING

    def test_detect_info_level(self, log_viewer):
        """Test INFO level detection."""
        assert log_viewer._detect_log_level("INFO: Information message") == LogViewer.LOG_LEVEL_INFO
        assert log_viewer._detect_log_level("Info: Information message") == LogViewer.LOG_LEVEL_INFO
        assert log_viewer._detect_log_level("info: Information message") == LogViewer.LOG_LEVEL_INFO
        assert log_viewer._detect_log_level("信息提示") == LogViewer.LOG_LEVEL_INFO

    def test_detect_debug_level(self, log_viewer):
        """Test DEBUG level detection."""
        assert log_viewer._detect_log_level("DEBUG: Debug message") == LogViewer.LOG_LEVEL_DEBUG
        assert log_viewer._detect_log_level("Debug: Debug message") == LogViewer.LOG_LEVEL_DEBUG
        assert log_viewer._detect_log_level("debug: Debug message") == LogViewer.LOG_LEVEL_DEBUG
        assert log_viewer._detect_log_level("调试信息") == LogViewer.LOG_LEVEL_DEBUG

    def test_detect_default_level(self, log_viewer):
        """Test default level (INFO) for unknown messages."""
        assert log_viewer._detect_log_level("Some random message") == LogViewer.LOG_LEVEL_INFO
        assert log_viewer._detect_log_level("Build started") == LogViewer.LOG_LEVEL_INFO


class TestExternalToolErrorDetection:
    """Tests for external tool error detection."""

    def test_detect_matlab_error(self, log_viewer):
        """Test MATLAB error detection."""
        assert log_viewer._detect_external_tool_error("Error: Undefined function 'foo'")
        assert log_viewer._detect_external_tool_error("Error: Undefined variable 'bar'")
        assert log_viewer._detect_external_tool_error("MATLAB:undefined function")
        assert log_viewer._detect_external_tool_error("Attempt to execute script 'script.m' as a function")

    def test_detect_iar_error(self, log_viewer):
        """Test IAR error detection."""
        assert log_viewer._detect_external_tool_error("Error[Li001]: No space in destination memory")
        assert log_viewer._detect_external_tool_error("Fatal error: Could not open file")
        assert log_viewer._detect_external_tool_error("Error Li002: Undefined symbol")
        assert log_viewer._detect_external_tool_error("error [E001]: Compilation failed")

    def test_detect_compilation_error(self, log_viewer):
        """Test general compilation error detection."""
        assert log_viewer._detect_external_tool_error("Undefined reference to 'foo'")
        assert log_viewer._detect_external_tool_error("Syntax error in file.c")
        assert log_viewer._detect_external_tool_error("Link error: unresolved symbols")
        assert log_viewer._detect_external_tool_error("Compilation error: invalid syntax")
        assert log_viewer._detect_external_tool_error("Build failed: linking errors")

    def test_no_false_positive_external_error(self, log_viewer):
        """Test external tool error detection doesn't have false positives."""
        assert not log_viewer._detect_external_tool_error("INFO: Build started")
        assert not log_viewer._detect_external_tool_error("WARNING: Low memory")
        assert not log_viewer._detect_external_tool_error("Debug: Step 1 complete")
        assert not log_viewer._detect_external_tool_error("Processing file...")

    def test_external_error_sets_error_level(self, log_viewer):
        """Test external tool errors are classified as ERROR level."""
        assert log_viewer._detect_log_level("Error[Li001]: No space") == LogViewer.LOG_LEVEL_ERROR
        assert log_viewer._detect_log_level("Error: Undefined function") == LogViewer.LOG_LEVEL_ERROR


class TestLogHighlighting:
    """Tests for log highlighting."""

    def test_error_highlighting(self, log_viewer):
        """Test ERROR log highlighting."""
        log_viewer.append_log("ERROR: Test error message")

        log_text = log_viewer.get_log_text()
        assert "ERROR: Test error message" in log_text

        # Check if HTML contains styling
        html = log_viewer.toHtml()
        assert "background-color" in html or "div" in html

    def test_warning_highlighting(self, log_viewer):
        """Test WARNING log highlighting."""
        log_viewer.append_log("WARNING: Test warning message")

        log_text = log_viewer.get_log_text()
        assert "WARNING: Test warning message" in log_text

    def test_info_highlighting(self, log_viewer):
        """Test INFO log highlighting."""
        log_viewer.append_log("INFO: Test info message")

        log_text = log_viewer.get_log_text()
        assert "INFO: Test info message" in log_text

    def test_debug_highlighting(self, log_viewer):
        """Test DEBUG log highlighting."""
        log_viewer.append_log("DEBUG: Test debug message")

        log_text = log_viewer.get_log_text()
        assert "DEBUG: Test debug message" in log_text

    def test_multiple_logs_appended(self, log_viewer):
        """Test multiple log messages are appended correctly."""
        messages = [
            "INFO: Build started",
            "INFO: Step 1 complete",
            "WARNING: Low memory",
            "ERROR: Build failed"
        ]

        for msg in messages:
            log_viewer.append_log(msg)

        log_text = log_viewer.get_log_text()
        for msg in messages:
            assert msg in log_text


class TestLogTrimming:
    """Tests for log trimming functionality."""

    def test_log_trim_when_exceeds_max(self, log_viewer):
        """Test log is trimmed when it exceeds MAX_LOG_LINES."""
        # Append more than MAX_LOG_LINES messages
        for i in range(log_viewer.MAX_LOG_LINES + 100):
            log_viewer.append_log(f"INFO: Message {i}")

        # Check that log is trimmed
        log_text = log_viewer.get_log_text()
        lines = log_text.split('\n')

        # Should be at most MAX_LOG_LINES (accounting for empty lines)
        assert len(lines) <= log_viewer.MAX_LOG_LINES + 10

        # Should contain recent messages (last 1000 lines)
        # If we add 1100 messages (0-1099), we should keep messages 100-1099
        assert "Message 100" in log_text
        assert "Message 1099" in log_text

    def test_log_not_trimmed_when_under_max(self, log_viewer):
        """Test log is not trimmed when under MAX_LOG_LINES."""
        # Append fewer than MAX_LOG_LINES messages
        for i in range(100):
            log_viewer.append_log(f"INFO: Message {i}")

        log_text = log_viewer.get_log_text()
        lines = log_text.split('\n')

        # Should have all messages
        assert "Message 0" in log_text
        assert "Message 99" in log_text


class TestLogUtilityMethods:
    """Tests for utility methods."""

    def test_clear_log(self, log_viewer):
        """Test clear_log method."""
        log_viewer.append_log("INFO: Test message")
        assert log_viewer.get_log_text()

        log_viewer.clear_log()
        assert not log_viewer.get_log_text()

    def test_get_log_text(self, log_viewer):
        """Test get_log_text method."""
        messages = ["INFO: Message 1", "INFO: Message 2"]
        for msg in messages:
            log_viewer.append_log(msg)

        log_text = log_viewer.get_log_text()
        for msg in messages:
            assert msg in log_text


class TestLogColorConstants:
    """Tests for color constants."""

    def test_error_color_constants(self, log_viewer):
        """Test ERROR color constants are defined."""
        assert hasattr(log_viewer, 'COLOR_ERROR_BG')
        assert hasattr(log_viewer, 'COLOR_ERROR_TEXT')
        assert log_viewer.COLOR_ERROR_BG is not None
        assert log_viewer.COLOR_ERROR_TEXT is not None

    def test_warning_color_constants(self, log_viewer):
        """Test WARNING color constants are defined."""
        assert hasattr(log_viewer, 'COLOR_WARNING_BG')
        assert hasattr(log_viewer, 'COLOR_WARNING_TEXT')
        assert log_viewer.COLOR_WARNING_BG is not None
        assert log_viewer.COLOR_WARNING_TEXT is not None

    def test_info_debug_color_constants(self, log_viewer):
        """Test INFO/DEBUG color constants are defined."""
        assert hasattr(log_viewer, 'COLOR_INFO_TEXT')
        assert hasattr(log_viewer, 'COLOR_DEBUG_TEXT')
        assert log_viewer.COLOR_INFO_TEXT is not None
        assert log_viewer.COLOR_DEBUG_TEXT is not None


class TestLogKeywordHighlighting:
    """Tests for keyword highlighting."""

    def test_highlight_keywords_error(self, log_viewer):
        """Test error keywords are highlighted."""
        text = "This is an error message"
        highlighted = log_viewer._highlight_keywords(
            text,
            ["error"],
            "font-weight:bold; color:#8b0000;"
        )

        assert "<span" in highlighted
        assert "error" in highlighted
        assert "font-weight:bold" in highlighted

    def test_highlight_keywords_warning(self, log_viewer):
        """Test warning keywords are highlighted."""
        text = "This is a warning message"
        highlighted = log_viewer._highlight_keywords(
            text,
            ["warning"],
            "font-weight:bold; color:#b8860b;"
        )

        assert "<span" in highlighted
        assert "warning" in highlighted
        assert "font-weight:bold" in highlighted

    def test_highlight_keywords_case_insensitive(self, log_viewer):
        """Test keyword highlighting is case-insensitive."""
        text = "ERROR error Error"
        highlighted = log_viewer._highlight_keywords(
            text,
            ["error"],
            "font-weight:bold;"
        )

        # All case variations should be highlighted
        assert highlighted.count("<span") >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
