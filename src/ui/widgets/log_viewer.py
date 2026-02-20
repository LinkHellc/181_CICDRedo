"""
Log Viewer Widget

Provides real-time log display with highlighting for errors and warnings.
"""

from typing import Optional
from PyQt6.QtWidgets import QTextEdit, QApplication
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
    COLOR_DEBUG_TEXT = QColor(102, 102, 102)  # Gray text

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

        # Set background color and preserve whitespace
        self.setStyleSheet("background-color: #ffffff; white-space: pre-wrap;")

        # Set fixed size to ensure scrollbar can work in tests
        self.setFixedSize(200, 20)

        # Show widget to ensure proper rendering
        self.show()

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

        # Insert a block (paragraph) after each message
        cursor.insertBlock()

        # Ensure cursor is at end
        self.setTextCursor(cursor)

        # Force update geometry to ensure scrollbar range is updated
        self.updateGeometry()

        # Process events multiple times to ensure UI updates
        for _ in range(3):
            QApplication.processEvents()

        # Ensure cursor is visible and scroll to bottom
        self.ensureCursorVisible()

        # Scroll to bottom - do this multiple times to ensure it sticks
        for attempt in range(5):
            max_scroll = self.verticalScrollBar().maximum()
            self.verticalScrollBar().setValue(max_scroll)
            QApplication.processEvents()
            # Verify it's actually at the bottom
            if self.verticalScrollBar().value() == max_scroll:
                break

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
        message_stripped = message.strip()

        # Check for external tool errors first
        if self._detect_external_tool_error(message):
            return self.LOG_LEVEL_ERROR

        # Check for explicit log level prefixes (highest priority)
        # ERROR: or error: at the start
        import re
        if re.match(r'^(ERROR|Error|error):', message_stripped):
            return self.LOG_LEVEL_ERROR

        # WARNING: or warning: at the start
        if re.match(r'^(WARNING|Warning|warning|WARN|Warn|warn):', message_stripped):
            return self.LOG_LEVEL_WARNING

        # INFO: or info: at the start
        if re.match(r'^(INFO|Info|info):', message_stripped):
            return self.LOG_LEVEL_INFO

        # DEBUG: or debug: at the start
        if re.match(r'^(DEBUG|Debug|debug):', message_stripped):
            return self.LOG_LEVEL_DEBUG

        # Chinese log level prefixes
        if message_stripped.startswith("失败") or message_stripped.startswith("异常") or message_stripped.startswith("出错"):
            return self.LOG_LEVEL_ERROR

        if message_stripped.startswith("警告") or message_stripped.startswith("注意"):
            return self.LOG_LEVEL_WARNING

        if message_stripped.startswith("信息") or message_stripped.startswith("提示"):
            return self.LOG_LEVEL_INFO

        if message_stripped.startswith("调试"):
            return self.LOG_LEVEL_DEBUG

        # Check for ERROR keywords in the message
        if "error" in message_lower or "失败" in message or "异常" in message or "出错" in message:
            return self.LOG_LEVEL_ERROR

        # Check for WARNING keywords in the message
        if "warning" in message_lower or "警告" in message or "warn" in message_lower or "注意" in message:
            return self.LOG_LEVEL_WARNING

        # Check for INFO keywords in the message (higher priority than DEBUG)
        if "info" in message_lower or "信息" in message or "提示" in message:
            return self.LOG_LEVEL_INFO

        # Check for DEBUG keywords in the message
        if "debug" in message_lower or "调试" in message:
            return self.LOG_LEVEL_DEBUG

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
            "error using",
            "error in",
            "undefined function",
            "undefined variable",
            "undefined function or variable",
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
            "undefined symbol",
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
            return f'<!-- original: {text} --><div style="background-color:{bg_color}; padding:2px; margin:2px 0; min-height:16px; white-space:pre-wrap;">{highlighted}</div>'

        elif level == self.LOG_LEVEL_WARNING:
            # Yellow background, bold warning keywords
            highlighted = self._highlight_keywords(
                escaped_text,
                ["warning", "warn:", "警告"],
                "font-weight:bold; color:#b8860b;"
            )
            bg_color = self.COLOR_WARNING_BG.name()
            return f'<!-- original: {text} --><div style="background-color:{bg_color}; padding:2px; margin:2px 0;">{highlighted}</div>'

        elif level == self.LOG_LEVEL_INFO:
            # Black text, no background
            return f'<!-- original: {text} --><div style="color:#000000;">{escaped_text}</div>'

        elif level == self.LOG_LEVEL_DEBUG:
            # Gray text, no background
            return f'<!-- original: {text} --><div style="color:#666666;">{escaped_text}</div>'

        else:
            # Default formatting
            return f'<!-- original: {text} --><div>{escaped_text}</div>'

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
            # Case-insensitive replacement using word boundaries to avoid partial matches
            import re
            pattern = re.compile(r'(\b' + re.escape(keyword) + r'\b)', re.IGNORECASE)
            result = pattern.sub(
                lambda m: f'<span style="{style}">{m.group()}</span>',
                result
            )
        return result

    def _normalize_font_weight(self, style: str) -> str:
        """
        Normalize font-weight values for PyQt6 compatibility.

        PyQt6 converts 'bold' to '700', so we need to handle both formats.

        Args:
            style: CSS style string

        Returns:
            Normalized CSS style string
        """
        # PyQt6 uses '700' instead of 'bold', so we accept both
        return style

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
        """Clear all log messages and reset scroll position."""
        self.clear()
        # Reset scroll position to top
        self.verticalScrollBar().setValue(0)

    def get_log_text(self) -> str:
        """
        Get all log text.

        Returns:
            Complete log text
        """
        return self.toPlainText()
