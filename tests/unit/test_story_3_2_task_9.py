"""Unit tests for Story 3.2 Task 9: Comprehensive Log Viewer Tests

Comprehensive tests for LogViewer functionality integration.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QScrollBar
from PyQt6.QtCore import Qt

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.log_viewer import LogViewer


class TestStory32Task9(unittest.TestCase):
    """测试 Story 3.2 任务 9: 添加单元测试验证日志查看器功能"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.viewer = LogViewer()

    def setUp(self):
        """每个测试前的设置"""
        self.viewer.clear_log()

    def test_9_1_full_log_flow(self):
        """测试 9.1: 完整的日志流程（追加、显示、清理）"""
        # 追加日志
        self.viewer.append_log("INFO: Build started")
        self.viewer.append_log("INFO: Step 1 complete")
        self.viewer.append_log("WARNING: Low memory")
        self.viewer.append_log("ERROR: Build failed")

        # 验证日志被正确追加
        log_text = self.viewer.get_log_text()
        self.assertIn("INFO: Build started", log_text)
        self.assertIn("INFO: Step 1 complete", log_text)
        self.assertIn("WARNING: Low memory", log_text)
        self.assertIn("ERROR: Build failed", log_text)

        # 清理日志
        self.viewer.clear_log()

        # 验证日志被清空
        self.assertEqual(self.viewer.get_log_text(), "")

    def test_9_2_multiple_log_levels_integration(self):
        """测试 9.2: 多种日志级别的集成测试"""
        messages = [
            ("ERROR: Critical failure", LogViewer.LOG_LEVEL_ERROR),
            ("WARNING: Warning message", LogViewer.LOG_LEVEL_WARNING),
            ("INFO: Information", LogViewer.LOG_LEVEL_INFO),
            ("DEBUG: Debug info", LogViewer.LOG_LEVEL_DEBUG),
        ]

        for message, expected_level in messages:
            # 追加日志
            self.viewer.append_log(message)

            # 验证日志级别检测
            detected_level = self.viewer._detect_log_level(message)
            self.assertEqual(detected_level, expected_level)

        # 验证所有日志都被正确存储
        log_text = self.viewer.get_log_text()
        for message, _ in messages:
            self.assertIn(message, log_text)

    def test_9_3_long_running_log_session(self):
        """测试 9.3: 长时间运行的日志会话"""
        # 模拟长时间运行的日志会话
        for cycle in range(3):
            # 清理并重新开始
            self.viewer.clear_log()

            # 追加一批日志
            for i in range(100):
                level = ["ERROR", "WARNING", "INFO", "DEBUG"][i % 4]
                self.viewer.append_log(f"{level}: Cycle {cycle} - Message {i}")

            # 验证日志被正确处理
            log_text = self.viewer.get_log_text()
            self.assertIn(f"Cycle {cycle} - Message 0", log_text)
            self.assertIn(f"Cycle {cycle} - Message 99", log_text)

    def test_9_4_error_recovery(self):
        """测试 9.4: 错误恢复能力"""
        # 追加正常日志
        self.viewer.append_log("INFO: Normal operation")

        # 追加错误日志
        self.viewer.append_log("ERROR: Something went wrong")

        # 验证日志仍然可读
        log_text = self.viewer.get_log_text()
        self.assertIn("INFO: Normal operation", log_text)
        self.assertIn("ERROR: Something went wrong", log_text)

        # 清理并继续
        self.viewer.clear_log()
        self.viewer.append_log("INFO: Recovered")

        # 验证恢复后的日志
        log_text = self.viewer.get_log_text()
        self.assertIn("INFO: Recovered", log_text)
        self.assertNotIn("ERROR: Something went wrong", log_text)

    def test_9_5_special_characters_and_unicode(self):
        """测试 9.5: 特殊字符和 Unicode 的处理"""
        special_messages = [
            "中文字符消息",
            "日本語のメッセージ",
            "한국어 메시지",
            "Emoji: 🚀 🎉 ⚠️ ❌",
            "HTML: <test> &amp; entities",
            "Quotes: \"single\" and 'double'",
        ]

        for msg in special_messages:
            self.viewer.append_log(f"INFO: {msg}")

        # 验证所有消息都被正确处理
        log_text = self.viewer.get_log_text()
        for msg in special_messages:
            self.assertIn(msg, log_text)

    def test_9_6_memory_efficiency(self):
        """测试 9.6: 内存效率测试"""
        # 追加大量日志
        for i in range(self.viewer.MAX_LOG_LINES + 500):
            self.viewer.append_log(f"INFO: Message {i}")

        # 验证日志被截断
        log_text = self.viewer.get_log_text()
        lines = log_text.split('\n')

        # 验证行数不超过 MAX_LOG_LINES
        self.assertLessEqual(len(lines), self.viewer.MAX_LOG_LINES + 10)

        # 验证仍然可以正常工作
        self.viewer.append_log("INFO: After large log")
        self.assertIn("INFO: After large log", log_text)

    def test_9_7_ui_responsiveness(self):
        """测试 9.7: UI 响应性测试"""
        # 快速追加大量日志
        import time

        start_time = time.time()

        for i in range(200):
            self.viewer.append_log(f"INFO: Message {i}")

        elapsed = time.time() - start_time

        # 验证性能：应该在 2 秒内完成
        self.assertLess(elapsed, 2.0,
                      f"Appending 200 messages took too long: {elapsed}s")

        # 验证日志被正确追加
        log_text = self.viewer.get_log_text()
        self.assertIn("INFO: Message 0", log_text)
        self.assertIn("INFO: Message 199", log_text)

    def test_9_8_external_tool_errors(self):
        """测试 9.8: 外部工具错误的集成测试"""
        # 追加不同工具的错误
        external_errors = [
            "Error: Undefined function 'foo'",
            "Error[Li001]: No space in destination memory",
            "Undefined reference to 'bar'",
            "Syntax error in file.c",
        ]

        for error_msg in external_errors:
            self.viewer.append_log(error_msg)

        # 验证所有错误被检测
        log_text = self.viewer.get_log_text()
        for error_msg in external_errors:
            self.assertIn(error_msg, log_text)

        # 验证所有错误被分类为 ERROR 级别
        for error_msg in external_errors:
            level = self.viewer._detect_log_level(error_msg)
            self.assertEqual(level, LogViewer.LOG_LEVEL_ERROR)

    def test_9_9_highlighting_integration(self):
        """测试 9.9: 高亮显示的集成测试"""
        # 追加不同级别的日志
        messages = [
            "ERROR: Critical error",
            "WARNING: Warning message",
            "INFO: Info message",
            "DEBUG: Debug message",
        ]

        for msg in messages:
            self.viewer.append_log(msg)

        # 获取 HTML 内容
        html_content = self.viewer.toHtml()

        # 验证包含高亮样式
        self.assertIn("background-color", html_content)
        self.assertIn("font-weight:bold", html_content)

        # 验证所有消息都在 HTML 中
        for msg in messages:
            self.assertIn(msg, html_content)

    def test_9_10_auto_scroll_integration(self):
        """测试 9.10: 自动滚动的集成测试"""
        # 追加足够多的日志以产生滚动条
        for i in range(50):
            self.viewer.append_log(f"INFO: Message {i}")

        # 获取垂直滚动条
        scroll_bar = self.viewer.verticalScrollBar()

        # 验证滚动条在底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

        # 追加新日志
        self.viewer.append_log("INFO: New message")

        # 验证滚动条仍然在底部
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

    def test_9_11_comprehensive_test_suite(self):
        """测试 9.11: 综合测试套件"""
        # 测试所有主要功能一起工作

        # 1. 追加不同类型的日志
        self.viewer.append_log("INFO: Build started")
        self.viewer.append_log("DEBUG: Loading config")
        self.viewer.append_log("INFO: Processing files")
        self.viewer.append_log("WARNING: Low memory")
        self.viewer.append_log("INFO: Compilation started")
        self.viewer.append_log("Error: Compilation error")
        self.viewer.append_log("ERROR: Build failed")

        # 2. 验证所有日志被正确追加
        log_text = self.viewer.get_log_text()
        expected_messages = [
            "Build started",
            "Loading config",
            "Processing files",
            "Low memory",
            "Compilation started",
            "Compilation error",
            "Build failed"
        ]

        for msg in expected_messages:
            self.assertIn(msg, log_text)

        # 3. 验证日志级别正确
        self.assertEqual(
            self.viewer._detect_log_level("ERROR: Build failed"),
            LogViewer.LOG_LEVEL_ERROR
        )
        self.assertEqual(
            self.viewer._detect_log_level("WARNING: Low memory"),
            LogViewer.LOG_LEVEL_WARNING
        )
        self.assertEqual(
            self.viewer._detect_log_level("INFO: Build started"),
            LogViewer.LOG_LEVEL_INFO
        )
        self.assertEqual(
            self.viewer._detect_log_level("DEBUG: Loading config"),
            LogViewer.LOG_LEVEL_DEBUG
        )

        # 4. 验证外部工具错误被检测
        self.assertTrue(
            self.viewer._detect_external_tool_error("Error: Compilation error")
        )

        # 5. 验证滚动条在底部
        scroll_bar = self.viewer.verticalScrollBar()
        self.assertEqual(scroll_bar.value(), scroll_bar.maximum())

        # 6. 清理并验证
        self.viewer.clear_log()
        self.assertEqual(self.viewer.get_log_text(), "")

        # 7. 验证可以继续追加
        self.viewer.append_log("INFO: New build started")
        self.assertIn("New build started", self.viewer.get_log_text())

    def test_9_12_edge_cases(self):
        """测试 9.12: 边界情况测试"""
        # 空消息
        self.viewer.append_log("")
        self.viewer.append_log("   ")

        # 非常长的消息
        long_msg = "A" * 10000
        self.viewer.append_log(f"INFO: {long_msg}")

        # 特殊字符
        self.viewer.append_log("INFO: <html> &amp; \"quotes\" 'apostrophe'")

        # Unicode
        self.viewer.append_log("INFO: 中文 🚀 日本語 한글 مرحبا Привет")

        # 换行符
        self.viewer.append_log("INFO: Line 1\nLine 2\nLine 3")

        # 验证没有崩溃
        log_text = self.viewer.get_log_text()
        self.assertIsNotNone(log_text)

        # 验证仍然可以追加新消息
        self.viewer.append_log("INFO: Final message")
        self.assertIn("Final message", log_text)


if __name__ == '__main__':
    unittest.main()
