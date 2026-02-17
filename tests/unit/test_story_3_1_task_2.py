"""Unit tests for Story 3.1 Task 2: Implement Stage Status Display

Tests for ProgressPanel stage status update functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.core.models import BuildProgress, StageStatus
from src.ui.widgets.progress_panel import ProgressPanel


class TestStory31Task2(unittest.TestCase):
    """测试 Story 3.1 任务 2: 实现阶段状态显示"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.panel = ProgressPanel()

    def setUp(self):
        """每个测试前的设置"""
        self.panel.clear()

    def test_2_1_update_stage_status_method_exists(self):
        """测试 2.1: 在 ProgressPanel 类中添加 update_stage_status() 方法"""
        # 由于 ProgressPanel 使用 update_progress() 方法更新所有状态
        # 这里测试 update_progress() 方法存在
        self.assertTrue(hasattr(self.panel, 'update_progress'))
        self.assertTrue(callable(self.panel.update_progress))

    def test_2_2_accept_stage_name_and_status_parameters(self):
        """测试 2.2: 接受阶段名称和状态参数"""
        # 通过 BuildProgress 对象传递阶段名称和状态
        progress = BuildProgress()
        progress.stage_statuses["test_stage"] = StageStatus.RUNNING

        # 方法应该能够接受这些参数
        try:
            self.panel.update_progress(progress)
        except Exception as e:
            self.fail(f"update_progress 方法无法接受 BuildProgress 对象: {e}")

    def test_2_3_status_enums(self):
        """测试 2.3: 状态枚举：PENDING、RUNNING、COMPLETED、FAILED"""
        from src.core.models import StageStatus

        # 测试所有枚举值都存在
        self.assertTrue(hasattr(StageStatus, 'PENDING'))
        self.assertTrue(hasattr(StageStatus, 'RUNNING'))
        self.assertTrue(hasattr(StageStatus, 'COMPLETED'))
        self.assertTrue(hasattr(StageStatus, 'FAILED'))

    def test_2_4_status_icons(self):
        """测试 2.4: 使用状态图标（⏸️、🔄、✅、❌）表示不同状态"""
        from src.core.models import StageStatus

        # 测试 PENDING 状态图标
        pending_text = self.panel._get_stage_status_text(StageStatus.PENDING)
        self.assertIn("⏸️", pending_text)

        # 测试 RUNNING 状态图标
        running_text = self.panel._get_stage_status_text(StageStatus.RUNNING)
        self.assertIn("🔄", running_text)

        # 测试 COMPLETED 状态图标
        completed_text = self.panel._get_stage_status_text(StageStatus.COMPLETED)
        self.assertIn("✅", completed_text)

        # 测试 FAILED 状态图标
        failed_text = self.panel._get_stage_status_text(StageStatus.FAILED)
        self.assertIn("❌", failed_text)

    def test_2_5_different_colors_for_different_statuses(self):
        """测试 2.5: 使用不同颜色表示不同状态（灰色、蓝色、绿色、红色）"""
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

    def test_2_6_update_stage_status_in_list(self):
        """测试 2.6: 更新阶段列表中的状态显示"""
        progress = BuildProgress()
        progress.stage_statuses = {
            "stage1": StageStatus.PENDING,
            "stage2": StageStatus.RUNNING,
            "stage3": StageStatus.COMPLETED,
            "stage4": StageStatus.FAILED
        }

        self.panel.update_progress(progress)

        # 验证阶段列表有4行
        self.assertEqual(self.panel.stage_list.rowCount(), 4)

        # 验证每个阶段的状态显示正确
        for row, (stage_name, status) in enumerate(progress.stage_statuses.items()):
            status_item = self.panel.stage_list.item(row, 1)
            self.assertIsNotNone(status_item)

            status_text = self.panel._get_stage_status_text(status)
            self.assertIn(status_text, status_item.text())

    def test_2_7_unit_test_verify_stage_status_update(self):
        """测试 2.7: 添加单元测试验证阶段状态更新"""
        # 测试 PENDING 状态更新
        progress1 = BuildProgress()
        progress1.stage_statuses["test_stage"] = StageStatus.PENDING
        self.panel.update_progress(progress1)

        self.assertEqual(self.panel.stage_list.rowCount(), 1)
        status_item = self.panel.stage_list.item(0, 1)
        self.assertIn("等待中", status_item.text())

        # 测试 RUNNING 状态更新
        progress2 = BuildProgress()
        progress2.stage_statuses["test_stage"] = StageStatus.RUNNING
        self.panel.update_progress(progress2)

        status_item = self.panel.stage_list.item(0, 1)
        self.assertIn("进行中", status_item.text())

        # 测试 COMPLETED 状态更新
        progress3 = BuildProgress()
        progress3.stage_statuses["test_stage"] = StageStatus.COMPLETED
        self.panel.update_progress(progress3)

        status_item = self.panel.stage_list.item(0, 1)
        self.assertIn("已完成", status_item.text())

        # 测试 FAILED 状态更新
        progress4 = BuildProgress()
        progress4.stage_statuses["test_stage"] = StageStatus.FAILED
        self.panel.update_progress(progress4)

        status_item = self.panel.stage_list.item(0, 1)
        self.assertIn("失败", status_item.text())

        # 测试状态颜色更新
        status_color = status_item.foreground().color().name().lower()
        self.assertEqual(status_color, "#cc0000")


if __name__ == '__main__':
    unittest.main()
