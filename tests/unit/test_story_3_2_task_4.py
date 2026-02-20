"""Unit tests for Story 3.2 Task 4: Implement Log Highlighting

Tests for LogViewer log highlighting functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.log_viewer import LogViewer


class TestStory32Task4(unittest.TestCase):
    """测试 Story 3.2 任务 4: 实现日志高亮显示"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.viewer = LogViewer()

    def setUp(self):
        """每个测试前的设置"""
        self.viewer.clear_log()

    def test_4_1_apply_highlighting_method_exists(self):
        """测试 4.1: _apply_highlighting() 方法存在"""
        self.assertTrue(hasattr(self.viewer, '_apply_highlighting'))
        self.assertTrue(callable(self.viewer._apply_highlighting))

    def test_4_2_highlight_keywords_method_exists(self):
        """测试 4.2: _highlight_keywords() 方法存在"""
        self.assertTrue(hasattr(self.viewer, '_highlight_keywords'))
        self.assertTrue(callable(self.viewer._highlight_keywords))

    def test_4_3_error_level_highlighting(self):
        """测试 4.3: ERROR 级别高亮显示"""
        # ERROR 日志应该有红色背景和粗体错误关键词
        message = "ERROR: Test error message"
        highlighted = self.viewer._apply_highlighting(
            message,
            LogViewer.LOG_LEVEL_ERROR
        )

        # 检查包含 HTML div 标签和背景颜色
        self.assertIn("<div", highlighted)
        self.assertIn("background-color", highlighted)
        self.assertIn(LogViewer.COLOR_ERROR_BG.name(), highlighted)

        # 检查错误关键词被高亮
        self.assertIn("<span", highlighted)
        self.assertIn("font-weight:bold", highlighted)
        self.assertIn("ERROR", highlighted)

    def test_4_4_warning_level_highlighting(self):
        """测试 4.4: WARNING 级别高亮显示"""
        # WARNING 日志应该有黄色背景和粗体警告关键词
        message = "WARNING: Test warning message"
        highlighted = self.viewer._apply_highlighting(
            message,
            LogViewer.LOG_LEVEL_WARNING
        )

        # 检查包含背景颜色
        self.assertIn("<div", highlighted)
        self.assertIn("background-color", highlighted)
        self.assertIn(LogViewer.COLOR_WARNING_BG.name(), highlighted)

        # 检查警告关键词被高亮
        self.assertIn("<span", highlighted)
        self.assertIn("font-weight:bold", highlighted)
        self.assertIn("WARNING", highlighted)

    def test_4_5_info_level_highlighting(self):
        """测试 4.5: INFO 级别高亮显示"""
        # INFO 日志应该是黑色文本，无背景
        message = "INFO: Test info message"
        highlighted = self.viewer._apply_highlighting(
            message,
            LogViewer.LOG_LEVEL_INFO
        )

        # 检查包含黑色文本
        self.assertIn("<div", highlighted)
        self.assertIn("color:#000000", highlighted)

        # 检查不包含背景颜色
        self.assertNotIn("background-color", highlighted)

    def test_4_6_debug_level_highlighting(self):
        """测试 4.6: DEBUG 级别高亮显示"""
        # DEBUG 日志应该是灰色文本，无背景
        message = "DEBUG: Test debug message"
        highlighted = self.viewer._apply_highlighting(
            message,
            LogViewer.LOG_LEVEL_DEBUG
        )

        # 检查包含灰色文本
        self.assertIn("<div", highlighted)
        self.assertIn("color:#666666", highlighted)

        # 检查不包含背景颜色
        self.assertNotIn("background-color", highlighted)

    def test_4_7_highlight_keywords_error(self):
        """测试 4.7: 高亮错误关键词"""
        text = "This is an error message"
        keywords = ["error"]
        style = "font-weight:bold; color:#8b0000;"

        highlighted = self.viewer._highlight_keywords(text, keywords, style)

        self.assertIn("<span", highlighted)
        self.assertIn("error", highlighted)
        self.assertIn(style, highlighted)

    def test_4_8_highlight_keywords_warning(self):
        """测试 4.8: 高亮警告关键词"""
        text = "This is a warning message"
        keywords = ["warning"]
        style = "font-weight:bold; color:#b8860b;"

        highlighted = self.viewer._highlight_keywords(text, keywords, style)

        self.assertIn("<span", highlighted)
        self.assertIn("warning", highlighted)
        self.assertIn(style, highlighted)

    def test_4_9_highlight_keywords_case_insensitive(self):
        """测试 4.9: 关键词高亮不区分大小写"""
        text = "ERROR error Error"
        keywords = ["error"]
        style = "font-weight:bold;"

        highlighted = self.viewer._highlight_keywords(text, keywords, style)

        # 所有大小写变体都应该被高亮
        self.assertGreaterEqual(highlighted.count("<span"), 3)

    def test_4_10_html_escaping(self):
        """测试 4.10: HTML 特殊字符转义"""
        # 测试 HTML 特殊字符被正确转义
        message = "INFO: <test> & message"
        highlighted = self.viewer._apply_highlighting(
            message,
            LogViewer.LOG_LEVEL_INFO
        )

        # HTML 特殊字符应该被转义
        self.assertIn("&lt;test&gt;", highlighted)
        self.assertIn("&amp;", highlighted)

    def test_4_11_unit_test_verify_log_highlighting(self):
        """测试 4.11: 添加单元测试验证日志高亮显示"""
        # 测试所有日志级别的高亮
        test_cases = [
            ("ERROR: Critical failure", LogViewer.LOG_LEVEL_ERROR),
            ("WARNING: Low memory", LogViewer.LOG_LEVEL_WARNING),
            ("INFO: Build started", LogViewer.LOG_LEVEL_INFO),
            ("DEBUG: Step 1", LogViewer.LOG_LEVEL_DEBUG),
        ]

        for message, level in test_cases:
            highlighted = self.viewer._apply_highlighting(message, level)

            # 检查是否包含 HTML 标签
            self.assertIn("<div", highlighted,
                         f"No HTML in highlighted message: {message}")

            # 检查消息内容存在
            self.assertIn(message, highlighted,
                         f"Original message lost: {message}")

            # 检查 HTML 结构完整性
            self.assertIn("</div>", highlighted,
                         f"Unclosed HTML div in: {message}")

    def test_4_12_color_constants_correctness(self):
        """测试 4.12: 验证颜色常量正确性"""
        # ERROR 颜色应该是红色系
        self.assertEqual(self.viewer.COLOR_ERROR_BG.name(), "#ffc8c8")
        self.assertEqual(self.viewer.COLOR_ERROR_TEXT.name(), "#8b0000")

        # WARNING 颜色应该是黄色系
        self.assertEqual(self.viewer.COLOR_WARNING_BG.name(), "#ffffc8")
        self.assertEqual(self.viewer.COLOR_WARNING_TEXT.name(), "#b8860b")

        # INFO 颜色应该是黑色
        self.assertEqual(self.viewer.COLOR_INFO_TEXT.name(), "#000000")

        # DEBUG 颜色应该是灰色
        self.assertEqual(self.viewer.COLOR_DEBUG_TEXT.name(), "#666666")


if __name__ == '__main__':
    unittest.main()
