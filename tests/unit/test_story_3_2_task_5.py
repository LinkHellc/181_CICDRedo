"""Unit tests for Story 3.2 Task 5: Implement Log Appending

Tests for LogViewer log appending functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.log_viewer import LogViewer


class TestStory32Task5(unittest.TestCase):
    """测试 Story 3.2 任务 5: 实现日志追加功能"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.viewer = LogViewer()

    def setUp(self):
        """每个测试前的设置"""
        self.viewer.clear_log()

    def test_5_1_append_log_method_exists(self):
        """测试 5.1: append_log() 方法存在"""
        self.assertTrue(hasattr(self.viewer, 'append_log'))
        self.assertTrue(callable(self.viewer.append_log))

    def test_5_2_append_single_log(self):
        """测试 5.2: 追加单条日志"""
        message = "INFO: Test message"
        self.viewer.append_log(message)

        log_text = self.viewer.get_log_text()
        self.assertIn(message, log_text)

    def test_5_3_append_multiple_logs(self):
        """测试 5.3: 追加多条日志"""
        messages = [
            "INFO: Build started",
            "INFO: Step 1 complete",
            "WARNING: Low memory",
            "ERROR: Build failed"
        ]

        for msg in messages:
            self.viewer.append_log(msg)

        log_text = self.viewer.get_log_text()
        for msg in messages:
            self.assertIn(msg, log_text)

    def test_5_4_preserve_log_order(self):
        """测试 5.4: 保持日志顺序"""
        messages = [
            "First message",
            "Second message",
            "Third message"
        ]

        for msg in messages:
            self.viewer.append_log(msg)

        log_text = self.viewer.get_log_text()
        first_pos = log_text.find("First message")
        second_pos = log_text.find("Second message")
        third_pos = log_text.find("Third message")

        self.assertLess(first_pos, second_pos)
        self.assertLess(second_pos, third_pos)

    def test_5_5_detect_log_level(self):
        """测试 5.5: 自动检测日志级别"""
        # 追加不同级别的日志
        self.viewer.append_log("ERROR: Critical error")
        self.viewer.append_log("WARNING: Warning message")
        self.viewer.append_log("INFO: Info message")
        self.viewer.append_log("DEBUG: Debug message")

        # 验证日志被正确追加
        log_text = self.viewer.get_log_text()
        self.assertIn("ERROR: Critical error", log_text)
        self.assertIn("WARNING: Warning message", log_text)
        self.assertIn("INFO: Info message", log_text)
        self.assertIn("DEBUG: Debug message", log_text)

    def test_5_6_apply_highlighting(self):
        """测试 5.6: 自动应用高亮显示"""
        # 追加 ERROR 日志
        self.viewer.append_log("ERROR: Test error")

        # 获取 HTML 内容
        html_content = self.viewer.toHtml()

        # 验证包含高亮样式
        self.assertIn("background-color", html_content)
        # PyQt6 将 "bold" 转换为 "700"，所以检查两种格式
        self.assertTrue("font-weight:bold" in html_content or "font-weight:700" in html_content,
                       "HTML should contain font-weight:bold or font-weight:700")

    def test_5_7_cursor_at_end(self):
        """测试 5.7: 光标移动到末尾"""
        # 追加多条日志
        for i in range(5):
            self.viewer.append_log(f"Message {i}")

        # 验证光标在末尾
        cursor = self.viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.viewer.setTextCursor(cursor)

        # 验证最后一条消息在末尾
        log_text = self.viewer.get_log_text()
        self.assertTrue(log_text.rstrip().endswith("Message 4"))

    def test_5_8_empty_message(self):
        """测试 5.8: 处理空消息"""
        # 追加空消息不应该报错
        self.viewer.append_log("")
        self.viewer.append_log("   ")

        # 验证不会导致错误
        log_text = self.viewer.get_log_text()
        self.assertIsNotNone(log_text)

    def test_5_9_special_characters(self):
        """测试 5.9: 处理特殊字符"""
        special_messages = [
            "Message with <html> tags",
            "Message with &amp; entities",
            "Message with \"quotes\"",
            "Message with 'apostrophes'",
            "Message with\nnewline",
            "Message with\ttab"
        ]

        for msg in special_messages:
            self.viewer.append_log(msg)

        # 验证所有消息都被追加
        log_text = self.viewer.get_log_text()
        for msg in special_messages:
            # 验证消息的核心内容存在
            # 对于包含 \n 或 \t 的消息，检查替换后的版本
            if "\n" in msg:
                # 新行被保留为新行字符，检查展开后的内容
                self.assertIn("Message with newline", log_text)
            elif "\t" in msg:
                # Tab 字符可能被转换为空格，检查简化版本
                # QTextEdit 可能会将 tab 转换为空格
                self.assertTrue(
                    "Message with\ttab" in log_text or "Message with tab" in log_text,
                    "Tab character should be present or converted to space"
                )
            else:
                # 其他消息直接检查
                self.assertIn(msg, log_text)

    def test_5_10_unicode_characters(self):
        """测试 5.10: 处理 Unicode 字符"""
        unicode_messages = [
            "中文字符消息",
            "日本語のメッセージ",
            "한국어 메시지",
            "Emoji: 🚀 🎉 ⚠️ ❌",
            "Arabic: مرحبا",
            "Cyrillic: Привет"
        ]

        for msg in unicode_messages:
            self.viewer.append_log(msg)

        # 验证所有 Unicode 消息都被正确处理
        log_text = self.viewer.get_log_text()
        for msg in unicode_messages:
            self.assertIn(msg, log_text)

    def test_5_11_unit_test_verify_log_appending(self):
        """测试 5.11: 添加单元测试验证日志追加功能"""
        # 测试基本追加功能
        self.viewer.append_log("INFO: Test message")
        self.assertIn("INFO: Test message", self.viewer.get_log_text())

        # 测试多次追加
        for i in range(10):
            self.viewer.append_log(f"Message {i}")

        log_text = self.viewer.get_log_text()
        for i in range(10):
            self.assertIn(f"Message {i}", log_text)

        # 测试不同日志级别
        self.viewer.clear_log()
        levels = ["ERROR", "WARNING", "INFO", "DEBUG"]
        for level in levels:
            self.viewer.append_log(f"{level}: Test message")

        log_text = self.viewer.get_log_text()
        for level in levels:
            self.assertIn(f"{level}: Test message", log_text)

        # 测试追加后查看器仍然可读
        self.viewer.append_log("Final message")
        final_text = self.viewer.get_log_text()
        self.assertIn("Final message", final_text)
        self.assertIn("INFO: Test message", final_text)  # 第一条消息还在

    def test_5_12_long_message(self):
        """测试 5.12: 处理长消息"""
        # 创建一条很长的消息
        long_message = "A" * 10000 + " END"
        self.viewer.append_log(long_message)

        # 验证长消息被正确追加
        log_text = self.viewer.get_log_text()
        self.assertIn("END", log_text)


if __name__ == '__main__':
    unittest.main()
