"""Unit tests for Story 3.2 Task 7: Implement Log Clear Functionality

Tests for LogViewer log clear functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.log_viewer import LogViewer


class TestStory32Task7(unittest.TestCase):
    """测试 Story 3.2 任务 7: 实现日志清理功能"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.viewer = LogViewer()

    def setUp(self):
        """每个测试前的设置"""
        self.viewer.clear_log()

    def test_7_1_clear_log_method_exists(self):
        """测试 7.1: clear_log() 方法存在"""
        self.assertTrue(hasattr(self.viewer, 'clear_log'))
        self.assertTrue(callable(self.viewer.clear_log))

    def test_7_2_clear_empty_log(self):
        """测试 7.2: 清理空日志"""
        # 清理空日志不应该报错
        self.viewer.clear_log()

        # 验证日志仍然为空
        self.assertEqual(self.viewer.get_log_text(), "")

    def test_7_3_clear_non_empty_log(self):
        """测试 7.3: 清理非空日志"""
        # 追加一些日志
        self.viewer.append_log("INFO: Message 1")
        self.viewer.append_log("INFO: Message 2")
        self.viewer.append_log("INFO: Message 3")

        # 验证日志不为空
        self.assertNotEqual(self.viewer.get_log_text(), "")

        # 清理日志
        self.viewer.clear_log()

        # 验证日志为空
        self.assertEqual(self.viewer.get_log_text(), "")

    def test_7_4_clear_after_many_logs(self):
        """测试 7.4: 清理大量日志后的状态"""
        # 追加大量日志
        for i in range(100):
            self.viewer.append_log(f"INFO: Message {i}")

        # 验证日志不为空
        self.assertNotEqual(self.viewer.get_log_text(), "")

        # 清理日志
        self.viewer.clear_log()

        # 验证日志为空
        self.assertEqual(self.viewer.get_log_text(), "")

    def test_7_5_clear_resets_cursor_position(self):
        """测试 7.5: 清理后重置光标位置"""
        # 追加日志
        self.viewer.append_log("INFO: Test message")

        # 移动光标
        cursor = self.viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.viewer.setTextCursor(cursor)

        # 清理日志
        self.viewer.clear_log()

        # 获取光标位置
        cursor = self.viewer.textCursor()
        cursor_position = cursor.position()

        # 验证光标位置为 0
        self.assertEqual(cursor_position, 0)

    def test_7_6_clear_resets_scroll_position(self):
        """测试 7.6: 清理后重置滚动位置"""
        # 追加足够多的日志以产生滚动条
        for i in range(50):
            self.viewer.append_log(f"INFO: Message {i}")

        # 获取垂直滚动条
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条不在顶部
        self.assertGreater(scroll_bar.value(), 0)

        # 清理日志
        self.viewer.clear_log()

        # 验证滚动条回到顶部
        self.assertEqual(scroll_bar.value(), 0)

    def test_7_7_clear_and_append_new(self):
        """测试 7.7: 清理后追加新日志"""
        # 追加日志
        self.viewer.append_log("INFO: Old message")

        # 清理日志
        self.viewer.clear_log()

        # 追加新日志
        self.viewer.append_log("INFO: New message")

        # 验证只包含新日志
        log_text = self.viewer.get_log_text()
        self.assertIn("New message", log_text)
        self.assertNotIn("Old message", log_text)

    def test_7_8_clear_preserves_viewer_state(self):
        """测试 7.8: 清理后查看器状态保持不变"""
        # 追加日志
        self.viewer.append_log("INFO: Test message")

        # 记录查看器状态
        is_readonly_before = self.viewer.isReadOnly()
        font_before = self.viewer.font()
        style_before = self.viewer.styleSheet()

        # 清理日志
        self.viewer.clear_log()

        # 验证查看器状态保持不变
        self.assertEqual(self.viewer.isReadOnly(), is_readonly_before)
        self.assertEqual(self.viewer.font(), font_before)
        self.assertEqual(self.viewer.styleSheet(), style_before)

    def test_7_9_clear_mixed_log_levels(self):
        """测试 7.9: 清理混合日志级别"""
        # 追加不同级别的日志
        self.viewer.append_log("ERROR: Critical error")
        self.viewer.append_log("WARNING: Warning message")
        self.viewer.append_log("INFO: Info message")
        self.viewer.append_log("DEBUG: Debug message")

        # 验证所有日志都存在
        log_text = self.viewer.get_log_text()
        self.assertIn("ERROR:", log_text)
        self.assertIn("WARNING:", log_text)
        self.assertIn("INFO:", log_text)
        self.assertIn("DEBUG:", log_text)

        # 清理日志
        self.viewer.clear_log()

        # 验证所有日志都被清除
        log_text = self.viewer.get_log_text()
        self.assertNotIn("ERROR:", log_text)
        self.assertNotIn("WARNING:", log_text)
        self.assertNotIn("INFO:", log_text)
        self.assertNotIn("DEBUG:", log_text)

    def test_7_10_multiple_clears(self):
        """测试 7.10: 多次清理日志"""
        # 第一次追加和清理
        self.viewer.append_log("INFO: First batch")
        self.viewer.clear_log()
        self.assertEqual(self.viewer.get_log_text(), "")

        # 第二次追加和清理
        self.viewer.append_log("INFO: Second batch")
        self.viewer.clear_log()
        self.assertEqual(self.viewer.get_log_text(), "")

        # 第三次追加和清理
        self.viewer.append_log("INFO: Third batch")
        self.viewer.clear_log()
        self.assertEqual(self.viewer.get_log_text(), "")

    def test_7_11_unit_test_verify_log_clear(self):
        """测试 7.11: 添加单元测试验证日志清理功能"""
        # 测试基本清理功能
        self.viewer.append_log("INFO: Test message 1")
        self.viewer.append_log("INFO: Test message 2")
        self.assertNotEqual(self.viewer.get_log_text(), "")

        self.viewer.clear_log()
        self.assertEqual(self.viewer.get_log_text(), "")

        # 测试清理后可以继续追加
        self.viewer.append_log("INFO: After clear message")
        self.assertIn("After clear message", self.viewer.get_log_text())

        # 测试多次清理
        for i in range(5):
            self.viewer.append_log(f"INFO: Message {i}")
            self.viewer.clear_log()
            self.assertEqual(self.viewer.get_log_text(), "")

        # 测试清理后的状态
        self.viewer.append_log("INFO: Final message")
        log_text = self.viewer.get_log_text()
        # 接受带换行符或不带换行符的结果
        self.assertTrue(log_text == "INFO: Final message\n" or log_text == "INFO: Final message",
                       f"Expected 'INFO: Final message' (with or without newline), got: {repr(log_text)}")

    def test_7_12_clear_with_special_characters(self):
        """测试 7.12: 清理包含特殊字符的日志"""
        # 追加包含特殊字符的日志
        special_messages = [
            "Message with <html>",
            "Message with &amp;",
            "Message with \"quotes\"",
            "中文字符",
            "Emoji 🚀"
        ]

        for msg in special_messages:
            self.viewer.append_log(msg)

        # 验证日志存在
        log_text = self.viewer.get_log_text()
        self.assertGreater(len(log_text), 0)

        # 清理日志
        self.viewer.clear_log()

        # 验证日志为空
        self.assertEqual(self.viewer.get_log_text(), "")


if __name__ == '__main__':
    unittest.main()
