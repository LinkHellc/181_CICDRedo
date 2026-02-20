"""Unit tests for Story 3.2 Task 8: Implement Log Trimming (Memory Management)

Tests for LogViewer log trimming functionality to prevent memory overflow.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.log_viewer import LogViewer


class TestStory32Task8(unittest.TestCase):
    """测试 Story 3.2 任务 8: 实现日志截断（防止内存溢出）"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.viewer = LogViewer()

    def setUp(self):
        """每个测试前的设置"""
        self.viewer.clear_log()

    def test_8_1_trim_log_method_exists(self):
        """测试 8.1: _trim_log() 方法存在"""
        self.assertTrue(hasattr(self.viewer, '_trim_log'))
        self.assertTrue(callable(self.viewer._trim_log))

    def test_8_2_max_log_lines_constant(self):
        """测试 8.2: MAX_LOG_LINES 常量已定义"""
        self.assertTrue(hasattr(self.viewer, 'MAX_LOG_LINES'))
        self.assertEqual(self.viewer.MAX_LOG_LINES, 1000)

    def test_8_3_trim_when_exceeds_max(self):
        """测试 8.3: 超过最大行数时自动截断"""
        # 追加超过 MAX_LOG_LINES 的日志
        for i in range(self.viewer.MAX_LOG_LINES + 100):
            self.viewer.append_log(f"INFO: Message {i}")

        # 获取日志文本
        log_text = self.viewer.get_log_text()
        lines = log_text.split('\n')

        # 验证日志行数不超过 MAX_LOG_LINES（考虑可能的空行）
        self.assertLessEqual(len(lines), self.viewer.MAX_LOG_LINES + 10)

    def test_8_4_keep_recent_messages(self):
        """测试 8.4: 保留最近的消息"""
        # 追加超过 MAX_LOG_LINES 的日志
        for i in range(self.viewer.MAX_LOG_LINES + 100):
            self.viewer.append_log(f"INFO: Message {i}")

        # 获取日志文本
        log_text = self.viewer.get_log_text()

        # 验证包含最近的消息（最后 1000 条）
        self.assertIn(f"Message {self.viewer.MAX_LOG_LINES}", log_text)
        self.assertIn(f"Message {self.viewer.MAX_LOG_LINES + 99}", log_text)

        # 验证不包含最早的消息（前 100 条应该被删除）
        self.assertNotIn("Message 0", log_text)
        self.assertNotIn("Message 99", log_text)

    def test_8_5_trim_preserves_last_n_lines(self):
        """测试 8.5: 截断保留最后 N 行"""
        # 追加超过 MAX_LOG_LINES 的日志
        total_messages = self.viewer.MAX_LOG_LINES + 200
        for i in range(total_messages):
            self.viewer.append_log(f"INFO: Message {i}")

        # 获取日志文本
        log_text = self.viewer.get_log_text()
        lines = log_text.split('\n')

        # 验证保留大约 MAX_LOG_LINES 行
        # 考虑空行和格式差异，允许一定的误差
        self.assertGreaterEqual(len(lines), self.viewer.MAX_LOG_LINES - 50)
        self.assertLessEqual(len(lines), self.viewer.MAX_LOG_LINES + 50)

    def test_8_6_no_trim_when_under_max(self):
        """测试 8.6: 未超过最大行数时不截断"""
        # 追加少于 MAX_LOG_LINES 的日志
        for i in range(100):
            self.viewer.append_log(f"INFO: Message {i}")

        # 获取日志文本
        log_text = self.viewer.get_log_text()
        lines = log_text.split('\n')

        # 验证包含所有消息
        self.assertIn("Message 0", log_text)
        self.assertIn("Message 99", log_text)

        # 验证行数接近添加的消息数（考虑格式差异）
        self.assertGreater(len(lines), 90)
        self.assertLess(len(lines), 110)

    def test_8_7_trim_at_boundary(self):
        """测试 8.7: 在边界处截断"""
        # 追加正好 MAX_LOG_LINES 条日志
        for i in range(self.viewer.MAX_LOG_LINES):
            self.viewer.append_log(f"INFO: Message {i}")

        # 追加一条触发截断的日志
        self.viewer.append_log("INFO: Trigger trim")

        # 获取日志文本
        log_text = self.viewer.get_log_text()

        # 验证第一条消息被删除
        self.assertNotIn("Message 0", log_text)

        # 验证最后一条消息存在
        self.assertIn("Trigger trim", log_text)

    def test_8_8_trim_maintains_format(self):
        """测试 8.8: 截断后保持格式"""
        # 追加不同级别的日志
        for i in range(self.viewer.MAX_LOG_LINES + 100):
            level = ["ERROR", "WARNING", "INFO", "DEBUG"][i % 4]
            self.viewer.append_log(f"{level}: Message {i}")

        # 获取日志文本
        log_text = self.viewer.get_log_text()

        # 验证格式保持一致
        self.assertIn("ERROR:", log_text)
        self.assertIn("WARNING:", log_text)
        self.assertIn("INFO:", log_text)
        self.assertIn("DEBUG:", log_text)

    def test_8_9_trim_with_long_messages(self):
        """测试 8.9: 长消息的截断"""
        # 追加包含长消息的日志
        long_message = "A" * 500 + " END"
        for i in range(self.viewer.MAX_LOG_LINES + 50):
            self.viewer.append_log(f"INFO: {long_message} {i}")

        # 获取日志文本
        log_text = self.viewer.get_log_text()

        # 验证不会崩溃
        self.assertIsNotNone(log_text)

        # 验证包含最新的长消息
        self.assertIn(f"END {self.viewer.MAX_LOG_LINES + 49}", log_text)

    def test_8_10_trim_after_clear(self):
        """测试 8.10: 清理后追加大量日志的截断"""
        # 清理日志
        self.viewer.clear_log()

        # 追加大量日志
        for i in range(self.viewer.MAX_LOG_LINES + 100):
            self.viewer.append_log(f"INFO: Message {i}")

        # 验证被截断
        log_text = self.viewer.get_log_text()
        lines = log_text.split('\n')
        self.assertLessEqual(len(lines), self.viewer.MAX_LOG_LINES + 10)

    def test_8_11_unit_test_verify_log_trim(self):
        """测试 8.11: 添加单元测试验证日志截断功能"""
        # 测试超过最大行数时的截断
        for i in range(self.viewer.MAX_LOG_LINES + 200):
            self.viewer.append_log(f"INFO: Message {i}")

        log_text = self.viewer.get_log_text()
        lines = log_text.split('\n')

        # 验证行数限制
        self.assertLessEqual(len(lines), self.viewer.MAX_LOG_LINES + 10)

        # 验证保留最近的消息
        self.assertIn(f"Message {self.viewer.MAX_LOG_LINES}", log_text)
        self.assertNotIn("Message 0", log_text)

        # 测试未超过限制时不截断
        self.viewer.clear_log()
        for i in range(100):
            self.viewer.append_log(f"INFO: Message {i}")

        log_text = self.viewer.get_log_text()
        self.assertIn("Message 0", log_text)
        self.assertIn("Message 99", log_text)

    def test_8_12_performance_with_large_log(self):
        """测试 8.12: 大量日志的性能"""
        import time

        # 记录开始时间
        start_time = time.time()

        # 追加大量日志
        for i in range(self.viewer.MAX_LOG_LINES + 500):
            self.viewer.append_log(f"INFO: Message {i}")

        # 记录结束时间
        end_time = time.time()
        elapsed = end_time - start_time

        # 验证性能：应该能在合理时间内完成（例如 5 秒内）
        self.assertLess(elapsed, 5.0,
                      f"Appending {self.viewer.MAX_LOG_LINES + 500} messages took too long: {elapsed}s")

        # 验证日志被正确截断
        log_text = self.viewer.get_log_text()
        lines = log_text.split('\n')
        self.assertLessEqual(len(lines), self.viewer.MAX_LOG_LINES + 10)


if __name__ == '__main__':
    unittest.main()
