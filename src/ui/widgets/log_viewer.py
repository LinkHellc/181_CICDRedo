"""
Log Viewer Widget

Provides real-time log display with highlighting for errors and warnings.
"""

from typing import Optional
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt


class LogViewer(QTextEdit):
    """Log viewer widget with error and warning highlighting."""

    # Log level constants
    LOG_LEVEL_ERROR = "ERROR"
    LOG_LEVEL_WARNING = "WARNING"
    LOG_LEVEL_INFO = "INFO"
    LOG_LEVEL_DEBUG = "DEBUG"

    # Highlight color constants
    COLOR_ERROR_BG = QColor(255, 200, 200)  # Light red background
    COLOR_ERROR_TEXT = QColor(139, 0, 0)   # Dark red text
    COLOR_WARNING_BG = QColor(255, 255, 200)  # Light yellow background
    COLOR_WARNING_TEXT = QColor(184, 134, 11)  # Dark yellow/orange text
    COLOR_INFO_TEXT = QColor(0, 0, 0)  # Black text
    COLOR_DEBUG_TEXT = QColor(100, 100, 100)  # Gray text

    # Maximum number of log lines to keep
    MAX_LOG_LINES = 1000

    def __init__(self, parent=None):
        """Initialize log viewer."""
        super().__init__(parent)

        # Set read-only
        self.setReadOnly(True)

        # Set monospace font
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.setFont(font)

        # Set background color
        self.setStyleSheet("background-color: #ffffff;")

    def append_log(self, message: str) -> None:
        """
        Append a log message to the viewer with appropriate highlighting.

        Args:
            message: Log message to append
        """
        # Detect log level
        level = self._detect_log_level(message)

        # Apply highlighting based on level
        highlighted_text = self._apply_highlighting(message, level)

        # Move cursor to end
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Insert text with formatting
        cursor.insertHtml(highlighted_text)

        # Ensure cursor is at end
        self.setTextCursor(cursor)

        # Scroll to bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

        # Trim log if too large
        self._trim_log()

    def _detect_log_level(self, message: str) -> str:
        """
        Detect the log level from the message.

        Args:
            message: Log message to analyze

        Returns:
            Log level string (ERROR, WARNING, INFO, DEBUG)
        """
        message_lower = message.lower()

        # Check for external tool errors first
        if self._detect_external_tool_error(message):
            return self.LOG_LEVEL_ERROR

        # Check for ERROR
        if "error" in message_lower or "失败" in message or "异常" in message:
            return self.LOG_LEVEL_ERROR

        # Check for WARNING
        if "warning" in message_lower or "警告" in message or "warn" in message_lower:
            return self.LOG_LEVEL_WARNING

        # Check for DEBUG (before INFO to avoid misclassifying "调试信息" as INFO)
        if "debug" in message_lower or "调试" in message:
            return self.LOG_LEVEL_DEBUG

        # Check for INFO
        if "info" in message_lower or "信息" in message:
            return self.LOG_LEVEL_INFO

        # Default to INFO
        return self.LOG_LEVEL_INFO

    def _detect_external_tool_error(self, message: str) -> bool:
        """
        Detect if message contains external tool error patterns.

        Args:
            message: Log message to analyze

        Returns:
            True if external tool error detected
        """
        message_lower = message.lower()

        # MATLAB error patterns
        matlab_patterns = [
            "error:",
            "undefined function",
            "undefined variable",
            "matlab:undefined",
            "attempt to execute script"
        ]

        # IAR error patterns
        iar_patterns = [
            "error[",
            "fatal error",
            "error li",
            "error [",
        ]

        # General compilation errors
        compilation_patterns = [
            "undefined reference",
            "syntax error",
            "link error",
            "compilation error",
            "build failed"
        ]

        all_patterns = matlab_patterns + iar_patterns + compilation_patterns

        return any(pattern in message_lower for pattern in all_patterns)

    def _apply_highlighting(self, text: str, level: str) -> str:
        """
        Apply highlighting to text based on log level.

        Args:
            text: Log text to highlight
            level: Log level (ERROR, WARNING, INFO, DEBUG)

        Returns:
            HTML formatted text with highlighting
        """
        # Escape HTML special characters
        escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if level == self.LOG_LEVEL_ERROR:
            # Red background, bold error keywords
            highlighted = self._highlight_keywords(
                escaped_text,
                ["error", "error:", "error[", "失败", "异常"],
                "font-weight:bold; color:#8b0000;"
            )
            bg_color = self.COLOR_ERROR_BG.name()
            return f'<div style="background-color:{bg_color}; padding:2px;">{highlighted}</div>'

        elif level == self.LOG_LEVEL_WARNING:
            # Yellow background, bold warning keywords
            highlighted = self._highlight_keywords(
                escaped_text,
                ["warning", "warn:", "警告"],
                "font-weight:bold; color:#b8860b;"
            )
            bg_color = self.COLOR_WARNING_BG.name()
            return f'<div style="background-color:{bg_color}; padding:2px;">{highlighted}</div>'

        elif level == self.LOG_LEVEL_INFO:
            # Black text, no background
            return f'<div style="color:#000000;">{escaped_text}</div>'

        elif level == self.LOG_LEVEL_DEBUG:
            # Gray text, no background
            return f'<div style="color:#666666;">{escaped_text}</div>'

        else:
            # Default formatting
            return f'<div>{escaped_text}</div>'

    def _highlight_keywords(self, text: str, keywords: list[str], style: str) -> str:
        """
        Highlight specific keywords in text.

        Args:
            text: Text to highlight
            keywords: List of keywords to highlight
            style: CSS style for highlighting

        Returns:
            Text with highlighted keywords
        """
        result = text
        for keyword in keywords:
            # Case-insensitive replacement
            result = result.replace(
                keyword,
                f'<span style="{style}">{keyword}</span>'
            )
            result = result.replace(
                keyword.upper(),
                f'<span style="{style}">{keyword.upper()}</span>'
            )
            result = result.replace(
                keyword.lower(),
                f'<span style="{style}">{keyword.lower()}</span>'
            )
        return result

    def _trim_log(self) -> None:
        """Trim log to maximum number of lines."""
        text = self.toPlainText()
        lines = text.split('\n')

        if len(lines) > self.MAX_LOG_LINES:
            # Keep only the most recent MAX_LOG_LINES
            trimmed_lines = lines[-self.MAX_LOG_LINES:]
            trimmed_text = '\n'.join(trimmed_lines)

            self.setPlainText(trimmed_text)

            # Move cursor to end
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

    def clear_log(self) -> None:
        """Clear all log messages."""
        self.clear()

    def get_log_text(self) -> str:
        """
        Get all log text.

        Returns:
            Complete log text
        """
        return self.toPlainText()
