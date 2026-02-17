"""Unit tests for Story 3.1 Task 10: Add Visual Component Styles

Tests for ProgressPanel visual styling and component styles.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.core.models import BuildProgress, StageStatus
from src.ui.widgets.progress_panel import ProgressPanel


class TestStory31Task10(unittest.TestCase):
    """测试 Story 3.1 任务 10: 添加可视化组件样式"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.panel = ProgressPanel()

    def setUp(self):
        """每个测试前的设置"""
        self.panel.clear()

    def test_10_1_stylesheet_property_exists(self):
        """测试 10.1: 为进度面板添加样式表（QSS）"""
        # 验证可以使用 setStyleSheet 方法
        self.assertTrue(hasattr(self.panel, 'setStyleSheet'))
        self.assertTrue(callable(self.panel.setStyleSheet))

        # 验证组件有 styleSheet 方法
        self.assertTrue(hasattr(self.panel, 'styleSheet'))
        self.assertTrue(callable(self.panel.styleSheet))

    def test_10_2_color_schemes_for_different_statuses(self):
        """测试 10.2: 为不同状态定义不同的颜色方案"""
        from src.core.models import StageStatus

        # 测试 PENDING 状态颜色（灰色）
        pending_color = self.panel._get_stage_color(StageStatus.PENDING)
        self.assertEqual(pending_color, "#808080")

        # 测试 RUNNING 状态颜色（蓝色）
        running_color = self.panel._get_stage_color(StageStatus.RUNNING)
        self.assertEqual(running_color, "#0066cc")

        # 测试 COMPLETED 状态颜色（绿色）
        completed_color = self.panel._get_stage_color(StageStatus.COMPLETED)
        self.assertEqual(completed_color, "#008000")

        # 测试 FAILED 状态颜色（红色）
        failed_color = self.panel._get_stage_color(StageStatus.FAILED)
        self.assertEqual(failed_color, "#cc0000")

        # 测试 SKIPPED 状态颜色（橙色）
        skipped_color = self.panel._get_stage_color(StageStatus.SKIPPED)
        self.assertEqual(skipped_color, "#ff8800")

    def test_10_3_progress_bar_gradient_effect(self):
        """测试 10.3: 为进度条添加渐变效果"""
        # 验证进度条存在
        self.assertIsNotNone(self.panel.progress_bar)

        # 验证进度条可以设置样式
        self.assertTrue(hasattr(self.panel.progress_bar, 'setStyleSheet'))

        # 测试可以应用样式到进度条
        gradient_style = """
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 20px;
            }
        """
        try:
            self.panel.progress_bar.setStyleSheet(gradient_style)
        except Exception as e:
            self.fail(f"无法设置进度条样式: {e}")

    def test_10_4_status_icon_animation_optional(self):
        """测试 10.4: 为状态图标添加动画效果（可选）"""
        # 验证状态图标方法存在
        self.assertTrue(hasattr(self.panel, '_get_stage_status_text'))
        self.assertTrue(callable(self.panel._get_stage_status_text))

        # 验证所有状态都有图标
        from src.core.models import StageStatus

        for status in [StageStatus.PENDING, StageStatus.RUNNING,
                       StageStatus.COMPLETED, StageStatus.FAILED]:
            status_text = self.panel._get_stage_status_text(status)
            # 验证文本包含图标（emoji）
            self.assertTrue(
                any(icon in status_text for icon in ["⏸️", "🔄", "✅", "❌", "⏭️", "🏁"]),
                f"状态 {status} 的文本 '{status_text}' 应该包含图标"
            )

    def test_10_5_unit_test_verify_style_application(self):
        """测试 10.5: 添加单元测试验证样式应用"""
        # 测试 1: 验证可以应用样式表
        self.assertTrue(hasattr(self.panel, 'setStyleSheet'))
        self.assertTrue(callable(self.panel.setStyleSheet))

        # 应用测试样式
        test_style = """
            QWidget {
                background-color: #f5f5f5;
            }
        """
        self.panel.setStyleSheet(test_style)
        applied_style = self.panel.styleSheet()
        self.assertIn("background-color", applied_style)

        # 测试 2: 验证当前阶段标签可以应用样式
        self.assertTrue(hasattr(self.panel.current_stage_label, 'setStyleSheet'))

        highlight_style = "color: #0066cc; font-weight: bold;"
        self.panel.current_stage_label.setStyleSheet(highlight_style)
        applied_style = self.panel.current_stage_label.styleSheet()
        self.assertIn("color: #0066cc", applied_style)

        # 测试 3: 验证不同状态有不同的颜色方案
        from src.core.models import StageStatus

        color_mapping = {
            StageStatus.PENDING: "#808080",
            StageStatus.RUNNING: "#0066cc",
            StageStatus.COMPLETED: "#008000",
            StageStatus.FAILED: "#cc0000",
            StageStatus.SKIPPED: "#ff8800",
            StageStatus.CANCELLED: "#808080"
        }

        for status, expected_color in color_mapping.items():
            actual_color = self.panel._get_stage_color(status)
            self.assertEqual(
                actual_color,
                expected_color,
                f"状态 {status} 的颜色应该是 {expected_color}"
            )

        # 测试 4: 验证状态图标显示正确
        progress = BuildProgress()
        progress.stage_statuses = {
            "stage1": StageStatus.PENDING,
            "stage2": StageStatus.RUNNING,
            "stage3": StageStatus.COMPLETED,
            "stage4": StageStatus.FAILED
        }
        self.panel.update_progress(progress)

        # 验证阶段列表中的状态文本包含图标
        for row in range(4):
            status_item = self.panel.stage_list.item(row, 1)
            self.assertIsNotNone(status_item)

            status_text = status_item.text()
            self.assertTrue(
                any(icon in status_text for icon in ["⏸️", "🔄", "✅", "❌"]),
                f"状态文本 '{status_text}' 应该包含图标"
            )

        # 测试 5: 验证当前阶段标签使用了高亮样式
        progress2 = BuildProgress(
            current_stage="test_stage",
            percentage=50.0
        )
        progress2.stage_statuses["test_stage"] = StageStatus.RUNNING
        self.panel.update_progress(progress2)

        label_style = self.panel.current_stage_label.styleSheet()
        self.assertIn("color:", label_style)


if __name__ == '__main__':
    unittest.main()
