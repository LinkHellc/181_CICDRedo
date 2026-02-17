"""Unit tests for Story 3.1 Task 4: Implement Overall Progress Percentage Display

Tests for ProgressPanel overall progress percentage display functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.core.models import BuildProgress
from src.ui.widgets.progress_panel import ProgressPanel


class TestStory31Task4(unittest.TestCase):
    """测试 Story 3.1 任务 4: 实现整体进度百分比显示"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.panel = ProgressPanel()

    def setUp(self):
        """每个测试前的设置"""
        self.panel.clear()

    def test_4_1_update_progress_method_exists(self):
        """测试 4.1: 在 ProgressPanel 类中添加 update_progress() 方法"""
        self.assertTrue(hasattr(self.panel, 'update_progress'))
        self.assertTrue(callable(self.panel.update_progress))

    def test_4_2_accept_progress_percentage_parameter(self):
        """测试 4.2: 接受进度百分比参数（0-100）"""
        # 测试 0%
        progress0 = BuildProgress(percentage=0.0)
        try:
            self.panel.update_progress(progress0)
        except Exception as e:
            self.fail(f"update_progress 方法无法接受 0% 进度: {e}")

        # 测试 50%
        progress50 = BuildProgress(percentage=50.0)
        try:
            self.panel.update_progress(progress50)
        except Exception as e:
            self.fail(f"update_progress 方法无法接受 50% 进度: {e}")

        # 测试 100%
        progress100 = BuildProgress(percentage=100.0)
        try:
            self.panel.update_progress(progress100)
        except Exception as e:
            self.fail(f"update_progress 方法无法接受 100% 进度: {e}")

    def test_4_3_update_progress_bar(self):
        """测试 4.3: 更新进度条（QProgressBar.setValue()）"""
        # 测试 0%
        progress0 = BuildProgress(percentage=0.0)
        self.panel.update_progress(progress0)
        self.assertEqual(self.panel.progress_bar.value(), 0)

        # 测试 25%
        progress25 = BuildProgress(percentage=25.0)
        self.panel.update_progress(progress25)
        self.assertEqual(self.panel.progress_bar.value(), 25)

        # 测试 50%
        progress50 = BuildProgress(percentage=50.0)
        self.panel.update_progress(progress50)
        self.assertEqual(self.panel.progress_bar.value(), 50)

        # 测试 75%
        progress75 = BuildProgress(percentage=75.0)
        self.panel.update_progress(progress75)
        self.assertEqual(self.panel.progress_bar.value(), 75)

        # 测试 100%
        progress100 = BuildProgress(percentage=100.0)
        self.panel.update_progress(progress100)
        self.assertEqual(self.panel.progress_bar.value(), 100)

    def test_4_4_update_progress_percentage_label(self):
        """测试 4.4: 更新进度百分比显示标签"""
        # 进度百分比显示在 progress_bar 中通过 setFormat 实现
        # 验证格式字符串包含 %p% （百分比）
        self.assertEqual(self.panel.progress_bar.format(), "%p%")

        # 测试 0%
        progress0 = BuildProgress(percentage=0.0)
        self.panel.update_progress(progress0)
        self.assertEqual(self.panel.progress_bar.value(), 0)
        # QProgressBar 的 text() 方法会返回格式化后的文本
        self.assertEqual(self.panel.progress_bar.text(), "0%")

        # 测试 50%
        progress50 = BuildProgress(percentage=50.0)
        self.panel.update_progress(progress50)
        self.assertEqual(self.panel.progress_bar.value(), 50)
        self.assertEqual(self.panel.progress_bar.text(), "50%")

        # 测试 100%
        progress100 = BuildProgress(percentage=100.0)
        self.panel.update_progress(progress100)
        self.assertEqual(self.panel.progress_bar.value(), 100)
        self.assertEqual(self.panel.progress_bar.text(), "100%")

    def test_4_5_unit_test_verify_progress_percentage_update(self):
        """测试 4.5: 添加单元测试验证进度百分比更新"""
        # 测试初始状态
        self.assertEqual(self.panel.progress_bar.value(), 0)

        # 测试从 0% 到 100% 的进度更新
        test_values = [0, 10, 25, 50, 75, 90, 100]
        for percent in test_values:
            progress = BuildProgress(percentage=float(percent))
            self.panel.update_progress(progress)

            self.assertEqual(
                self.panel.progress_bar.value(),
                percent,
                f"进度条值应该为 {percent}%"
            )

            expected_text = f"{percent}%"
            actual_text = self.panel.progress_bar.text()

            self.assertEqual(
                actual_text,
                expected_text,
                f"进度条文本应该为 '{expected_text}'"
            )

        # 测试小数百分比（QProgressBar 截断为整数）
        progress_float = BuildProgress(percentage=33.7)
        self.panel.update_progress(progress_float)
        self.assertEqual(self.panel.progress_bar.value(), 33)  # 截断

        # 测试边界值
        # 测试负值（应该限制为 0）
        progress_negative = BuildProgress(percentage=-10.0)
        self.panel.update_progress(progress_negative)
        # QProgressBar 会自动限制在 0-100 范围内
        self.assertGreaterEqual(self.panel.progress_bar.value(), 0)

        # 测试超过100的值（应该限制为 100）
        progress_over = BuildProgress(percentage=150.0)
        self.panel.update_progress(progress_over)
        # QProgressBar 会自动限制在 0-100 范围内
        self.assertLessEqual(self.panel.progress_bar.value(), 100)


if __name__ == '__main__':
    unittest.main()
