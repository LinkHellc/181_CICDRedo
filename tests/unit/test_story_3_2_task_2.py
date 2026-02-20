"""Unit tests for Story 3.2 Task 2: Implement Log Level Detection

Tests for LogViewer log level detection functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.log_viewer import LogViewer


class TestStory32Task2(unittest.TestCase):
    """测试 Story 3.2 任务 2: 实现日志级别检测"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.viewer = LogViewer()

    def setUp(self):
        """每个测试前的设置"""
        self.viewer.clear_log()

    def test_2_1_detect_log_level_method_exists(self):
        """测试 2.1: _detect_log_level() 方法存在"""
        self.assertTrue(hasattr(self.viewer, '_detect_log_level'))
        self.assertTrue(callable(self.viewer._detect_log_level))

    def test_2_2_detect_error_level(self):
        """测试 2.2: 检测 ERROR 级别"""
        # 英文
        self.assertEqual(
            self.viewer._detect_log_level("ERROR: Something went wrong"),
            LogViewer.LOG_LEVEL_ERROR
        )
        self.assertEqual(
            self.viewer._detect_log_level("Error: Something went wrong"),
            LogViewer.LOG_LEVEL_ERROR
        )
        self.assertEqual(
            self.viewer._detect_log_level("error: Something went wrong"),
            LogViewer.LOG_LEVEL_ERROR
        )

        # 中文
        self.assertEqual(
            self.viewer._detect_log_level("操作失败"),
            LogViewer.LOG_LEVEL_ERROR
        )
        self.assertEqual(
            self.viewer._detect_log_level("发生异常"),
            LogViewer.LOG_LEVEL_ERROR
        )
        self.assertEqual(
            self.viewer._detect_log_level("执行出错"),
            LogViewer.LOG_LEVEL_ERROR
        )

    def test_2_3_detect_warning_level(self):
        """测试 2.3: 检测 WARNING 级别"""
        # 英文
        self.assertEqual(
            self.viewer._detect_log_level("WARNING: Something to note"),
            LogViewer.LOG_LEVEL_WARNING
        )
        self.assertEqual(
            self.viewer._detect_log_level("Warning: Something to note"),
            LogViewer.LOG_LEVEL_WARNING
        )
        self.assertEqual(
            self.viewer._detect_log_level("warning: Something to note"),
            LogViewer.LOG_LEVEL_WARNING
        )
        self.assertEqual(
            self.viewer._detect_log_level("WARN: Something"),
            LogViewer.LOG_LEVEL_WARNING
        )

        # 中文
        self.assertEqual(
            self.viewer._detect_log_level("警告：注意"),
            LogViewer.LOG_LEVEL_WARNING
        )
        self.assertEqual(
            self.viewer._detect_log_level("请注意"),
            LogViewer.LOG_LEVEL_WARNING
        )
        self.assertEqual(
            self.viewer._detect_log_level("警告信息"),
            LogViewer.LOG_LEVEL_WARNING
        )

    def test_2_4_detect_info_level(self):
        """测试 2.4: 检测 INFO 级别"""
        # 英文
        self.assertEqual(
            self.viewer._detect_log_level("INFO: Information message"),
            LogViewer.LOG_LEVEL_INFO
        )
        self.assertEqual(
            self.viewer._detect_log_level("Info: Information message"),
            LogViewer.LOG_LEVEL_INFO
        )
        self.assertEqual(
            self.viewer._detect_log_level("info: Information message"),
            LogViewer.LOG_LEVEL_INFO
        )

        # 中文
        self.assertEqual(
            self.viewer._detect_log_level("信息提示"),
            LogViewer.LOG_LEVEL_INFO
        )
        self.assertEqual(
            self.viewer._detect_log_level("信息：系统启动"),
            LogViewer.LOG_LEVEL_INFO
        )
        self.assertEqual(
            self.viewer._detect_log_level("普通消息"),
            LogViewer.LOG_LEVEL_INFO
        )

    def test_2_5_detect_debug_level(self):
        """测试 2.5: 检测 DEBUG 级别"""
        # 英文
        self.assertEqual(
            self.viewer._detect_log_level("DEBUG: Debug message"),
            LogViewer.LOG_LEVEL_DEBUG
        )
        self.assertEqual(
            self.viewer._detect_log_level("Debug: Debug message"),
            LogViewer.LOG_LEVEL_DEBUG
        )
        self.assertEqual(
            self.viewer._detect_log_level("debug: Debug message"),
            LogViewer.LOG_LEVEL_DEBUG
        )

        # 中文
        self.assertEqual(
            self.viewer._detect_log_level("调试信息"),
            LogViewer.LOG_LEVEL_DEBUG
        )
        self.assertEqual(
            self.viewer._detect_log_level("调试：步骤 1"),
            LogViewer.LOG_LEVEL_DEBUG
        )
        self.assertEqual(
            self.viewer._detect_log_level("Debug 输出"),
            LogViewer.LOG_LEVEL_DEBUG
        )

    def test_2_6_default_to_info_level(self):
        """测试 2.6: 未知消息默认为 INFO 级别"""
        self.assertEqual(
            self.viewer._detect_log_level("Some random message"),
            LogViewer.LOG_LEVEL_INFO
        )
        self.assertEqual(
            self.viewer._detect_log_level("Build started"),
            LogViewer.LOG_LEVEL_INFO
        )
        self.assertEqual(
            self.viewer._detect_log_level("Processing file..."),
            LogViewer.LOG_LEVEL_INFO
        )

    def test_2_7_case_insensitive_detection(self):
        """测试 2.7: 日志级别检测不区分大小写"""
        messages = [
            "ERROR: test",
            "Error: test",
            "error: test",
            "eRrOr: test"
        ]

        for msg in messages:
            self.assertEqual(
                self.viewer._detect_log_level(msg),
                LogViewer.LOG_LEVEL_ERROR,
                f"Failed for message: {msg}"
            )

    def test_2_8_priority_order(self):
        """测试 2.8: 日志级别检测优先级顺序"""
        # ERROR 应该有最高优先级
        self.assertEqual(
            self.viewer._detect_log_level("ERROR in DEBUG message"),
            LogViewer.LOG_LEVEL_ERROR
        )

        # WARNING 应该比 INFO 优先级高
        self.assertEqual(
            self.viewer._detect_log_level("WARNING about INFO message"),
            LogViewer.LOG_LEVEL_WARNING
        )

        # DEBUG 应该比 INFO 优先级低
        self.assertEqual(
            self.viewer._detect_log_level("INFO message with DEBUG details"),
            LogViewer.LOG_LEVEL_INFO
        )

    def test_2_9_unit_test_verify_log_level_detection(self):
        """测试 2.9: 添加单元测试验证日志级别检测"""
        # 测试所有已知日志级别
        test_cases = [
            ("ERROR: Critical failure", LogViewer.LOG_LEVEL_ERROR),
            ("Error: Minor error", LogViewer.LOG_LEVEL_ERROR),
            ("error: lowercase error", LogViewer.LOG_LEVEL_ERROR),
            ("操作失败", LogViewer.LOG_LEVEL_ERROR),
            ("发生异常", LogViewer.LOG_LEVEL_ERROR),

            ("WARNING: Low memory", LogViewer.LOG_LEVEL_WARNING),
            ("Warning: Check this", LogViewer.LOG_LEVEL_WARNING),
            ("warning: attention needed", LogViewer.LOG_LEVEL_WARNING),
            ("警告：注意", LogViewer.LOG_LEVEL_WARNING),

            ("INFO: Build started", LogViewer.LOG_LEVEL_INFO),
            ("Info: Normal message", LogViewer.LOG_LEVEL_INFO),
            ("info: informational", LogViewer.LOG_LEVEL_INFO),
            ("信息提示", LogViewer.LOG_LEVEL_INFO),

            ("DEBUG: Step 1", LogViewer.LOG_LEVEL_DEBUG),
            ("Debug: Debugging", LogViewer.LOG_LEVEL_DEBUG),
            ("debug: debug info", LogViewer.LOG_LEVEL_DEBUG),
            ("调试信息", LogViewer.LOG_LEVEL_DEBUG),

            ("Random message", LogViewer.LOG_LEVEL_INFO),
            ("Build completed", LogViewer.LOG_LEVEL_INFO),
        ]

        for message, expected_level in test_cases:
            actual_level = self.viewer._detect_log_level(message)
            self.assertEqual(
                actual_level,
                expected_level,
                f"Expected {expected_level} for '{message}', got {actual_level}"
            )


if __name__ == '__main__':
    unittest.main()
