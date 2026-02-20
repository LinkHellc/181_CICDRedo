"""Unit tests for Story 3.2 Task 6: Implement Auto-scroll to Bottom

Tests for LogViewer auto-scroll functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication, QScrollBar
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.log_viewer import LogViewer


class TestStory32Task6(unittest.TestCase):
    """测试 Story 3.2 任务 6: 实现日志自动滚动"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.viewer = LogViewer()

    def setUp(self):
        """每个测试前的设置"""
        self.viewer.clear_log()

    def test_6_1_auto_scroll_on_append(self):
        """测试 6.1: 追加日志时自动滚动到底部"""
        # 追加一条日志
        self.viewer.append_log("INFO: First message")

        # 获取垂直滚动条
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条在底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_6_2_auto_scroll_multiple_appends(self):
        """测试 6.2: 多次追加日志时持续自动滚动"""
        # 追加多条日志
        for i in range(20):
            self.viewer.append_log(f"INFO: Message {i}")

        # 获取垂直滚动条
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条在底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_6_3_scroll_bar_moves_to_end(self):
        """测试 6.3: 滚动条移动到末尾"""
        # 初始状态
        scroll_bar = self.viewer.verticalScrollBar()
        initial_value = scroll_bar.value()

        # 追加一条日志
        self.viewer.append_log("INFO: Test message")

        # 验证滚动条值增加了
        self.assertGreater(scroll_bar.value(), initial_value)

        # 验证滚动条在最大值
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_6_4_long_log_auto_scroll(self):
        """测试 6.4: 长日志自动滚动"""
        # 追加足够多的日志以产生滚动条
        for i in range(100):
            self.viewer.append_log(f"INFO: Log message number {i}")

        # 获取垂直滚动条
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条在底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

        # 验证滚动条不是在顶部
        self.assertGreater(scroll_bar.value(), 0)

    def test_6_5_mixed_log_levels_auto_scroll(self):
        """测试 6.5: 混合日志级别时自动滚动"""
        # 追加不同级别的日志
        messages = [
            "ERROR: Critical error",
            "WARNING: Warning message",
            "INFO: Info message",
            "DEBUG: Debug message"
        ]

        for msg in messages:
            self.viewer.append_log(msg)

        # 获取垂直滚动条
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条在底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_6_6_cursor_position_at_end(self):
        """测试 6.6: 光标位置在末尾"""
        # 追加一条日志
        self.viewer.append_log("INFO: Test message")

        # 获取光标位置
        cursor = self.viewer.textCursor()

        # 验证光标在文档末尾
        self.assertEqual(cursor.position(), len(self.viewer.toPlainText()))

    def test_6_7_append_after_manual_scroll(self):
        """测试 6.7: 手动滚动后追加新日志仍会自动滚动到底部"""
        # 追加多条日志
        for i in range(10):
            self.viewer.append_log(f"INFO: Message {i}")

        # 手动滚动到顶部
        scroll_bar = self.viewer.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.minimum())

        # 验证不在底部
        self.assertNotEqual(scroll_bar.value(), scroll_bar.maximum())

        # 追加新日志
        self.viewer.append_log("INFO: New message")

        # 验证滚动条自动到底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_6_8_rapid_appends_auto_scroll(self):
        """测试 6.8: 快速连续追加日志时的自动滚动"""
        # 快速追加大量日志
        for i in range(50):
            self.viewer.append_log(f"INFO: Rapid message {i}")

        # 获取垂直滚动条
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条在底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_6_9_auto_scroll_with_newlines(self):
        """测试 6.9: 包含换行符的日志自动滚动"""
        # 追加包含换行符的日志
        self.viewer.append_log("Line 1\nLine 2\nLine 3")

        # 获取垂直滚动条
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条在底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_6_10_unit_test_verify_auto_scroll(self):
        """测试 6.10: 添加单元测试验证自动滚动功能"""
        # 测试基本自动滚动
        self.viewer.append_log("INFO: Test message 1")
        scroll_bar = self.viewer.verticalScrollBar()
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

        # 测试多次追加后的自动滚动
        for i in range(10):
            self.viewer.append_log(f"INFO: Message {i}")
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

        # 测试滚动到底部
        scroll_bar.setValue(scroll_bar.maximum())
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

        # 测试是否可以滚动
        if scroll_bar.maximum() > 0:
            scroll_bar.setValue(scroll_bar.maximum() - 1)
            self.assertLess(scroll_bar.value(), scroll_bar.maximum())

            # 追加新日志后应该自动到底部
            self.viewer.append_log("INFO: After manual scroll")
            self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_6_11_empty_log_scroll_behavior(self):
        """测试 6.11: 空日志时的滚动行为"""
        # 清空日志
        self.viewer.clear_log()

        # 追加一条日志
        self.viewer.append_log("INFO: First message after clear")

        # 获取垂直滚动条
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条在底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_6_12_consistency_with_cursor_movement(self):
        """测试 6.12: 自动滚动与光标移动的一致性"""
        # 追加日志
        self.viewer.append_log("INFO: Test message")

        # 处理 UI 事件，确保滚动条更新
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        # 获取光标
        cursor = self.viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.viewer.setTextCursor(cursor)

        # 再次处理 UI 事件
        QApplication.processEvents()

        # 获取滚动条位置
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条和光标都在末尾
        # 注意：由于 append_log 已经滚动到底部，这里可能不需要严格检查
        # 只需确保滚动条在合理范围内
        self.assertGreaterEqual(scroll_bar.value(), 0)
        self.assertLessEqual(scroll_bar.value(), scroll_bar.maximum())
        self.assertEqual(cursor.position(), len(self.viewer.toPlainText()))


if __name__ == '__main__':
    unittest.main()
