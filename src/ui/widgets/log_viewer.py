"""
Log Viewer Widget - Industrial Precision Theme

Provides real-time log display with highlighting for errors and warnings.
Redesigned with Industrial Precision Theme (v4.0 - 2026-02-24)
"""

from typing import Optional
from PyQt6.QtWidgets import QTextEdit, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt


class LogViewer(QTextEdit):
    """Log viewer widget with error and warning highlighting - Industrial Precision Theme."""

    LOG_LEVEL_ERROR = "ERROR"
    LOG_LEVEL_WARNING = "WARNING"
    LOG_LEVEL_INFO = "INFO"
    LOG_LEVEL_DEBUG = "DEBUG"

    # Industrial Precision Theme Colors
    COLORS = {
        'error_bg': '#7f1d1d',
        'error_text': '#fca5a5',
        'warning_bg': '#78350f',
        'warning_text': '#fcd34d',
        'info_text': '#94a3b8',
        'debug_text': '#475569',
        'bg': '#0f172a',
        'border': '#334155',
    }

    MAX_LOG_LINES = 1000

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setReadOnly(True)
        self.setAcceptRichText(True)

        # Monospace font
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Industrial Precision Theme styling
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.COLORS['bg']};
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
                padding: 12px;
                color: {self.COLORS['info_text']};
            }}
            QScrollBar:vertical {{
                background-color: #1e293b;
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #475569;
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        self.setMinimumHeight(150)

    def append_log(self, message: str) -> None:
        """Append a log message with appropriate highlighting."""
        level = self._detect_log_level(message)
        highlighted = self._apply_highlighting(message, level)

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(highlighted)
        cursor.insertBlock()
        self.setTextCursor(cursor)

        self.ensureCursorVisible()

        # Scroll to bottom
        for _ in range(3):
            max_scroll = self.verticalScrollBar().maximum()
            self.verticalScrollBar().setValue(max_scroll)
            QApplication.processEvents()

        self._trim_log()

    def _detect_log_level(self, message: str) -> str:
        """Detect the log level from the message."""
        import re
        message_lower = message.lower()
        message_stripped = message.strip()

        # External tool errors
        if self._detect_external_tool_error(message):
            return self.LOG_LEVEL_ERROR

        # Explicit prefixes
        if re.match(r'^(ERROR|Error|error|失败|异常|出错)[:\s]', message_stripped):
            return self.LOG_LEVEL_ERROR
        if re.match(r'^(WARNING|Warning|warning|WARN|Warn|warn|警告|注意)[:\s]', message_stripped):
            return self.LOG_LEVEL_WARNING
        if re.match(r'^(INFO|Info|info|信息|提示)[:\s]', message_stripped):
            return self.LOG_LEVEL_INFO
        if re.match(r'^(DEBUG|Debug|debug|调试)[:\s]', message_stripped):
            return self.LOG_LEVEL_DEBUG

        # Keywords
        if any(kw in message_lower for kw in ["error", "失败", "异常", "出错", "fatal"]):
            return self.LOG_LEVEL_ERROR
        if any(kw in message_lower for kw in ["warning", "warn", "警告", "注意", "deprecated"]):
            return self.LOG_LEVEL_WARNING
        if any(kw in message_lower for kw in ["info", "信息", "提示", "成功", "完成"]):
            return self.LOG_LEVEL_INFO
        if any(kw in message_lower for kw in ["debug", "调试", "trace"]):
            return self.LOG_LEVEL_DEBUG

        return self.LOG_LEVEL_INFO

    def _detect_external_tool_error(self, message: str) -> bool:
        """Detect external tool error patterns."""
        msg = message.lower()
        patterns = [
            "error:", "error using", "error in", "undefined function", "undefined variable",
            "error[", "fatal error", "error li", "undefined reference", "syntax error",
            "link error", "compilation error", "build failed"
        ]
        return any(p in msg for p in patterns)

    def _apply_highlighting(self, text: str, level: str) -> str:
        """Apply highlighting based on log level."""
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if level == self.LOG_LEVEL_ERROR:
            highlighted = self._highlight_keywords(
                escaped, ["error", "失败", "异常", "fatal"],
                f"color: {self.COLORS['error_text']}; font-weight: bold;"
            )
            return f'''<div style="background-color: {self.COLORS['error_bg']};
                padding: 4px 8px; margin: 2px 0; border-radius: 4px;
                border-left: 3px solid #ef4444;">{highlighted}</div>'''

        elif level == self.LOG_LEVEL_WARNING:
            highlighted = self._highlight_keywords(
                escaped, ["warning", "warn", "警告"],
                f"color: {self.COLORS['warning_text']}; font-weight: bold;"
            )
            return f'''<div style="background-color: {self.COLORS['warning_bg']};
                padding: 4px 8px; margin: 2px 0; border-radius: 4px;
                border-left: 3px solid #f59e0b;">{highlighted}</div>'''

        elif level == self.LOG_LEVEL_DEBUG:
            return f'''<div style="color: {self.COLORS['debug_text']};
                padding: 2px 8px;">{escaped}</div>'''

        else:  # INFO
            return f'''<div style="color: {self.COLORS['info_text']};
                padding: 2px 8px;">{escaped}</div>'''

    def _highlight_keywords(self, text: str, keywords: list[str], style: str) -> str:
        """Highlight specific keywords."""
        import re
        result = text
        for kw in keywords:
            pattern = re.compile(r'(\b' + re.escape(kw) + r'\b)', re.IGNORECASE)
            result = pattern.sub(f'<span style="{style}">\\1</span>', result)
        return result

    def _trim_log(self) -> None:
        """Trim log to maximum lines."""
        text = self.toPlainText()
        lines = text.split('\n')
        if len(lines) > self.MAX_LOG_LINES:
            trimmed = '\n'.join(lines[-self.MAX_LOG_LINES:])
            self.setPlainText(trimmed)
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

    def clear_log(self) -> None:
        """Clear all log messages."""
        self.clear()
        self.verticalScrollBar().setValue(0)

    def get_log_text(self) -> str:
        """Get all log text."""
        return self.toPlainText()
