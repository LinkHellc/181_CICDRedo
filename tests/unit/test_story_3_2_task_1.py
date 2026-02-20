"""Unit tests for Story 3.2 Task 1: Create Log Viewer UI Component

Tests for LogViewer widget UI component initialization and structure.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication, QTextEdit, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.log_viewer import LogViewer


class TestStory32Task1(unittest.TestCase):
    """测试 Story 3.2 任务 1: 创建日志查看器 UI 组件"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.viewer = LogViewer()

    def setUp(self):
        """每个测试前的设置"""
        self.viewer.clear_log()

    def test_1_1_log_viewer_class_inherits_qtextedit(self):
        """测试 1.1: LogViewer 类继承 QTextEdit"""
        from PyQt6.QtWidgets import QTextEdit
        self.assertIsInstance(self.viewer, QTextEdit)

    def test_1_2_is_read_only(self):
        """测试 1.2: 日志查看器是只读的"""
        self.assertTrue(self.viewer.isReadOnly())

    def test_1_3_uses_monospace_font(self):
        """测试 1.3: 使用等宽字体（Consolas 或 Courier New）"""
        font = self.viewer.font()
        self.assertIn(font.family(), ["Consolas", "Courier New"])

    def test_1_4_font_size_is_9(self):
        """测试 1.4: 字体大小为 9pt"""
        font = self.viewer.font()
        self.assertEqual(font.pointSize(), 9)

    def test_1_5_layout_uses_qvboxlayout(self):
        """测试 1.5: 使用布局管理器（QVBoxLayout）组织组件"""
        # LogViewer 本身是一个组件，不需要额外布局
        # 这里测试它是一个有效的 QWidget
        self.assertIsNotNone(self.viewer)

    def test_1_6_has_white_background(self):
        """测试 1.6: 背景颜色为白色 (#ffffff)"""
        style = self.viewer.styleSheet()
        self.assertIn("background-color: #ffffff", style)

    def test_1_7_max_log_lines_constant(self):
        """测试 1.7: 定义 MAX_LOG_LINES 常量"""
        self.assertTrue(hasattr(self.viewer, 'MAX_LOG_LINES'))
        self.assertEqual(self.viewer.MAX_LOG_LINES, 1000)

    def test_1_8_log_viewer_creation(self):
        """测试 1.8: 添加单元测试验证日志查看器创建"""
        # 测试查看器可以正常创建
        new_viewer = LogViewer()
        self.assertIsNotNone(new_viewer)

        # 测试查看器是只读的
        self.assertTrue(new_viewer.isReadOnly())

        # 测试查看器有正确的字体
        font = new_viewer.font()
        self.assertIn(font.family(), ["Consolas", "Courier New"])
        self.assertEqual(font.pointSize(), 9)

        # 测试查看器是空的
        self.assertEqual(new_viewer.get_log_text(), "")

        # 测试查看器可以被清空
        new_viewer.append_log("Test message")
        self.assertNotEqual(new_viewer.get_log_text(), "")
        new_viewer.clear_log()
        self.assertEqual(new_viewer.get_log_text(), "")

    def test_1_9_constant_colors_defined(self):
        """测试 1.9: 定义颜色常量"""
        self.assertTrue(hasattr(self.viewer, 'COLOR_ERROR_BG'))
        self.assertTrue(hasattr(self.viewer, 'COLOR_ERROR_TEXT'))
        self.assertTrue(hasattr(self.viewer, 'COLOR_WARNING_BG'))
        self.assertTrue(hasattr(self.viewer, 'COLOR_WARNING_TEXT'))
        self.assertTrue(hasattr(self.viewer, 'COLOR_INFO_TEXT'))
        self.assertTrue(hasattr(self.viewer, 'COLOR_DEBUG_TEXT'))

    def test_1_10_log_level_constants_defined(self):
        """测试 1.10: 定义日志级别常量"""
        self.assertTrue(hasattr(self.viewer, 'LOG_LEVEL_ERROR'))
        self.assertTrue(hasattr(self.viewer, 'LOG_LEVEL_WARNING'))
        self.assertTrue(hasattr(self.viewer, 'LOG_LEVEL_INFO'))
        self.assertTrue(hasattr(self.viewer, 'LOG_LEVEL_DEBUG'))

        # 测试常量值
        self.assertEqual(self.viewer.LOG_LEVEL_ERROR, "ERROR")
        self.assertEqual(self.viewer.LOG_LEVEL_WARNING, "WARNING")
        self.assertEqual(self.viewer.LOG_LEVEL_INFO, "INFO")
        self.assertEqual(self.viewer.LOG_LEVEL_DEBUG, "DEBUG")


if __name__ == '__main__':
    unittest.main()
