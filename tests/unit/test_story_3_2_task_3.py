"""Unit tests for Story 3.2 Task 3: Implement External Tool Error Detection

Tests for LogViewer external tool error detection functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.log_viewer import LogViewer


class TestStory32Task3(unittest.TestCase):
    """测试 Story 3.2 任务 3: 实现外部工具错误检测"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.viewer = LogViewer()

    def setUp(self):
        """每个测试前的设置"""
        self.viewer.clear_log()

    def test_3_1_detect_external_tool_error_method_exists(self):
        """测试 3.1: _detect_external_tool_error() 方法存在"""
        self.assertTrue(hasattr(self.viewer, '_detect_external_tool_error'))
        self.assertTrue(callable(self.viewer._detect_external_tool_error))

    def test_3_2_detect_matlab_error(self):
        """测试 3.2: 检测 MATLAB 错误"""
        matlab_errors = [
            "Error: Undefined function 'foo'",
            "Error: Undefined variable 'bar'",
            "MATLAB:undefined function",
            "Attempt to execute script 'script.m' as a function",
            "Undefined function or variable 'test'",
            "Error using *",
            "Error in line 10",
        ]

        for error_msg in matlab_errors:
            self.assertTrue(
                self.viewer._detect_external_tool_error(error_msg),
                f"Failed to detect MATLAB error: {error_msg}"
            )

    def test_3_3_detect_iar_error(self):
        """测试 3.3: 检测 IAR 编译器错误"""
        iar_errors = [
            "Error[Li001]: No space in destination memory",
            "Fatal error: Could not open file",
            "Error Li002: Undefined symbol",
            "error [E001]: Compilation failed",
            "Error[Pe111]: expression must be a modifiable lvalue",
            "Fatal error C1083: Cannot open include file",
        ]

        for error_msg in iar_errors:
            self.assertTrue(
                self.viewer._detect_external_tool_error(error_msg),
                f"Failed to detect IAR error: {error_msg}"
            )

    def test_3_4_detect_compilation_error(self):
        """测试 3.4: 检测一般编译错误"""
        compilation_errors = [
            "Undefined reference to 'foo'",
            "Syntax error in file.c",
            "Link error: unresolved symbols",
            "Compilation error: invalid syntax",
            "Build failed: linking errors",
            "undefined reference to `printf'",
            "undefined symbol _main",
        ]

        for error_msg in compilation_errors:
            self.assertTrue(
                self.viewer._detect_external_tool_error(error_msg),
                f"Failed to detect compilation error: {error_msg}"
            )

    def test_3_5_no_false_positive_external_error(self):
        """测试 3.5: 避免外部工具错误检测的误报"""
        non_errors = [
            "INFO: Build started",
            "WARNING: Low memory",
            "Debug: Step 1 complete",
            "Processing file...",
            "Build completed successfully",
            "All tests passed",
            "This is just a normal message",
            "Note: configuration loaded",
        ]

        for message in non_errors:
            self.assertFalse(
                self.viewer._detect_external_tool_error(message),
                f"False positive for: {message}"
            )

    def test_3_6_case_insensitive_detection(self):
        """测试 3.6: 外部工具错误检测不区分大小写"""
        error_variants = [
            "Error: test",
            "error: test",
            "ERROR: test",
            "eRrOr: test",
        ]

        for error_msg in error_variants:
            self.assertTrue(
                self.viewer._detect_external_tool_error(error_msg),
                f"Failed for case variant: {error_msg}"
            )

    def test_3_7_external_error_sets_error_level(self):
        """测试 3.7: 外部工具错误被分类为 ERROR 级别"""
        external_errors = [
            "Error[Li001]: No space",
            "Error: Undefined function",
            "Undefined reference to 'foo'",
            "Syntax error in file.c",
        ]

        for error_msg in external_errors:
            level = self.viewer._detect_log_level(error_msg)
            self.assertEqual(
                level,
                LogViewer.LOG_LEVEL_ERROR,
                f"External error not classified as ERROR: {error_msg}"
            )

    def test_3_8_partial_pattern_matching(self):
        """测试 3.8: 部分模式匹配（错误关键词出现在消息中间）"""
        messages_with_errors = [
            "The build failed because Error[Li001]: No space",
            "Warning: There was an Error: Undefined function",
            "Processing... Error Li002: Undefined symbol ... continuing",
        ]

        for message in messages_with_errors:
            self.assertTrue(
                self.viewer._detect_external_tool_error(message),
                f"Failed to detect error in: {message}"
            )

    def test_3_9_unit_test_verify_external_tool_error_detection(self):
        """测试 3.9: 添加单元测试验证外部工具错误检测"""
        # 测试 MATLAB 错误
        matlab_messages = [
            ("Error: Undefined function 'foo'", True),
            ("Undefined variable 'bar'", True),
            ("MATLAB:undefined function", True),
            ("Normal MATLAB message", False),
        ]

        for msg, should_detect in matlab_messages:
            detected = self.viewer._detect_external_tool_error(msg)
            self.assertEqual(
                detected,
                should_detect,
                f"MATLAB error detection failed for: {msg}"
            )

        # 测试 IAR 错误
        iar_messages = [
            ("Error[Li001]: No space", True),
            ("Fatal error: Could not open file", True),
            ("Error Li002: Undefined symbol", True),
            ("IAR compilation successful", False),
        ]

        for msg, should_detect in iar_messages:
            detected = self.viewer._detect_external_tool_error(msg)
            self.assertEqual(
                detected,
                should_detect,
                f"IAR error detection failed for: {msg}"
            )

        # 测试编译错误
        compile_messages = [
            ("Undefined reference to 'foo'", True),
            ("Syntax error in file.c", True),
            ("Link error: unresolved symbols", True),
            ("Compilation complete", False),
        ]

        for msg, should_detect in compile_messages:
            detected = self.viewer._detect_external_tool_error(msg)
            self.assertEqual(
                detected,
                should_detect,
                f"Compilation error detection failed for: {msg}"
            )

    def test_3_10_multiple_error_patterns_in_one_message(self):
        """测试 3.10: 一条消息包含多个错误模式"""
        # 包含多个错误关键词的消息应该被检测到
        multi_error_msg = "Error[Li001]: No space and Error: Undefined function"
        self.assertTrue(
            self.viewer._detect_external_tool_error(multi_error_msg),
            "Failed to detect message with multiple error patterns"
        )

        # 验证该消息被分类为 ERROR 级别
        level = self.viewer._detect_log_level(multi_error_msg)
        self.assertEqual(level, LogViewer.LOG_LEVEL_ERROR)


if __name__ == '__main__':
    unittest.main()
