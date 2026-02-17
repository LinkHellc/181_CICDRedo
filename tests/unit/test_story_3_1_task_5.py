"""Unit tests for Story 3.1 Task 5: Implement Stage List Initialization

Tests for ProgressPanel stage list initialization functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.core.models import BuildProgress, StageStatus
from src.ui.widgets.progress_panel import ProgressPanel


class TestStory31Task5(unittest.TestCase):
    """测试 Story 3.1 任务 5: 实现阶段列表初始化"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.panel = ProgressPanel()

    def setUp(self):
        """每个测试前的设置"""
        self.panel.clear()

    def test_5_1_initialize_stages_method_exists(self):
        """测试 5.1: 在 ProgressPanel 类中添加 initialize_stages() 方法"""
        self.assertTrue(hasattr(self.panel, 'initialize_stages'))
        self.assertTrue(callable(self.panel.initialize_stages))

    def test_5_2_accept_stage_name_list_parameter(self):
        """测试 5.2: 接受阶段名称列表参数"""
        stage_names = ["stage1", "stage2", "stage3"]

        try:
            self.panel.initialize_stages(stage_names)
        except Exception as e:
            self.fail(f"initialize_stages 方法无法接受阶段名称列表: {e}")

    def test_5_3_clear_stage_list(self):
        """测试 5.3: 清空阶段列表"""
        # 先添加一些阶段
        stage_names1 = ["stage1", "stage2"]
        self.panel.initialize_stages(stage_names1)
        self.assertEqual(self.panel.stage_list.rowCount(), 2)

        # 清空并重新初始化
        stage_names2 = ["stage3", "stage4", "stage5"]
        self.panel.initialize_stages(stage_names2)

        # 验证阶段列表已被清空并重新填充
        self.assertEqual(self.panel.stage_list.rowCount(), 3)

    def test_5_4_create_list_items_for_each_stage(self):
        """测试 5.4: 为每个阶段创建列表项"""
        stage_names = ["matlab_gen", "file_process", "iar_compile"]
        self.panel.initialize_stages(stage_names)

        # 验证行数等于阶段数
        self.assertEqual(self.panel.stage_list.rowCount(), 3)

        # 验证每个阶段的名称正确
        for row, expected_name in enumerate(stage_names):
            name_item = self.panel.stage_list.item(row, 0)
            self.assertIsNotNone(name_item)
            self.assertEqual(name_item.text(), expected_name)

        # 验证每个阶段都有状态项
        for row in range(3):
            status_item = self.panel.stage_list.item(row, 1)
            self.assertIsNotNone(status_item)

    def test_5_5_initial_status_pending(self):
        """测试 5.5: 初始状态设置为 PENDING"""
        stage_names = ["stage1", "stage2", "stage3"]
        self.panel.initialize_stages(stage_names)

        # 验证所有阶段的状态都是 PENDING
        for row in range(3):
            status_item = self.panel.stage_list.item(row, 1)
            self.assertIsNotNone(status_item)

            status_text = self.panel._get_stage_status_text(StageStatus.PENDING)
            self.assertEqual(status_item.text(), status_text)

            # 验证颜色是灰色（PENDING 的颜色）
            color = self.panel._get_stage_color(StageStatus.PENDING)
            self.assertEqual(status_item.foreground().color().name().lower(), color)

    def test_5_6_set_initial_progress_to_zero(self):
        """测试 5.6: 设置初始进度为 0"""
        stage_names = ["stage1", "stage2", "stage3"]
        self.panel.initialize_stages(stage_names)

        # 验证进度条为 0
        self.assertEqual(self.panel.progress_bar.value(), 0)

        # 验证当前阶段标签
        self.assertEqual(self.panel.current_stage_label.text(), "等待开始...")

        # 验证进度对象
        self.assertEqual(self.panel.current_progress.total_stages, 3)
        self.assertEqual(self.panel.current_progress.percentage, 0.0)

    def test_5_7_unit_test_verify_stage_list_initialization(self):
        """测试 5.7: 添加单元测试验证阶段列表初始化"""
        # 测试空列表
        self.panel.initialize_stages([])
        self.assertEqual(self.panel.stage_list.rowCount(), 0)

        # 测试单个阶段
        self.panel.initialize_stages(["single_stage"])
        self.assertEqual(self.panel.stage_list.rowCount(), 1)
        self.assertEqual(self.panel.stage_list.item(0, 0).text(), "single_stage")

        # 测试多个阶段
        stage_names = [
            "matlab_gen",
            "file_process",
            "iar_compile",
            "a2l_process",
            "file_move"
        ]
        self.panel.initialize_stages(stage_names)

        self.assertEqual(self.panel.stage_list.rowCount(), 5)

        for row, expected_name in enumerate(stage_names):
            name_item = self.panel.stage_list.item(row, 0)
            self.assertEqual(name_item.text(), expected_name)

            status_item = self.panel.stage_list.item(row, 1)
            status_text = self.panel._get_stage_status_text(StageStatus.PENDING)
            self.assertEqual(status_item.text(), status_text)

        # 测试初始化后的进度状态
        self.assertEqual(self.panel.progress_bar.value(), 0)
        self.assertEqual(self.panel.current_stage_label.text(), "等待开始...")

        # 测试重新初始化（覆盖之前的设置）
        new_stage_names = ["new_stage1", "new_stage2"]
        self.panel.initialize_stages(new_stage_names)

        self.assertEqual(self.panel.stage_list.rowCount(), 2)
        self.assertEqual(self.panel.stage_list.item(0, 0).text(), "new_stage1")
        self.assertEqual(self.panel.stage_list.item(1, 0).text(), "new_stage2")


if __name__ == '__main__':
    unittest.main()
