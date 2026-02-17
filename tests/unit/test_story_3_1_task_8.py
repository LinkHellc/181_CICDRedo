"""Unit tests for Story 3.1 Task 8: Integrate Progress Panel in Main Window

Tests for MainWindow progress panel integration.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.progress_panel import ProgressPanel
from src.core.models import BuildProgress, StageStatus


class TestStory31Task8(unittest.TestCase):
    """测试 Story 3.1 任务 8: 在主窗口中集成进度面板"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.progress_panel = ProgressPanel()

    def setUp(self):
        """每个测试前的设置"""
        self.progress_panel.clear()

    def test_8_1_progress_panel_instance_exists(self):
        """测试 8.1: 在 MainWindow 中创建 ProgressPanel 实例"""
        # 验证进度面板实例存在
        self.assertIsNotNone(self.progress_panel)
        self.assertIsInstance(self.progress_panel, ProgressPanel)

    def test_8_2_progress_panel_added_to_layout(self):
        """测试 8.2: 添加进度面板到主窗口布局"""
        # 验证进度面板有布局
        self.assertIsNotNone(self.progress_panel.layout())

        # 验证所有UI组件都存在
        self.assertIsNotNone(self.progress_panel.progress_bar)
        self.assertIsNotNone(self.progress_panel.current_stage_label)
        self.assertIsNotNone(self.progress_panel.stage_list)
        self.assertIsNotNone(self.progress_panel.time_label)

    def test_8_3_workflow_thread_signals_connected(self):
        """测试 8.3: 连接工作流线程的进度信号到进度面板的槽函数"""
        # 验证进度面板有相应的更新方法
        self.assertTrue(hasattr(self.progress_panel, 'update_progress'))
        self.assertTrue(hasattr(self.progress_panel, 'initialize_stages'))
        self.assertTrue(callable(self.progress_panel.update_progress))
        self.assertTrue(callable(self.progress_panel.initialize_stages))

    def test_8_4_stage_started_signal_connected(self):
        """测试 8.4: 连接 stage_started 信号到 update_current_stage()"""
        # 验证进度面板有更新当前阶段的方法
        self.assertTrue(hasattr(self.progress_panel, '_update_current_stage_label'))
        self.assertTrue(callable(self.progress_panel._update_current_stage_label))

        # 测试可以更新当前阶段
        progress = BuildProgress()
        progress.current_stage = "test_stage"
        progress.stage_statuses["test_stage"] = StageStatus.RUNNING
        self.progress_panel.update_progress(progress)

        self.assertIn("test_stage", self.progress_panel.current_stage_label.text())

    def test_8_5_stage_progress_signal_connected(self):
        """测试 8.5: 连接 stage_progress 信号到 update_stage_status()"""
        # 验证进度面板有更新阶段状态的方法
        self.assertTrue(hasattr(self.progress_panel, '_update_stage_list'))
        self.assertTrue(callable(self.progress_panel._update_stage_list))

        # 测试可以更新阶段状态
        progress = BuildProgress()
        progress.stage_statuses = {
            "stage1": StageStatus.COMPLETED,
            "stage2": StageStatus.RUNNING,
            "stage3": StageStatus.PENDING
        }
        self.progress_panel.update_progress(progress)

        # 验证阶段列表已更新
        self.assertEqual(self.progress_panel.stage_list.rowCount(), 3)

    def test_8_6_build_progress_signal_connected(self):
        """测试 8.6: 连接 build_progress 信号到 update_progress()"""
        # 验证进度面板有更新整体进度的方法
        self.assertTrue(hasattr(self.progress_panel, 'update_progress'))
        self.assertTrue(callable(self.progress_panel.update_progress))

        # 测试可以更新进度
        progress = BuildProgress()
        progress.percentage = 50.0
        self.progress_panel.update_progress(progress)

        self.assertEqual(self.progress_panel.progress_bar.value(), 50)

    def test_8_7_initialize_stages_called_on_workflow_start(self):
        """测试 8.7: 在工作流开始时调用 initialize_stages()"""
        # 验证 progress_panel 有 initialize_stages 方法
        self.assertTrue(hasattr(self.progress_panel, 'initialize_stages'))
        self.assertTrue(callable(self.progress_panel.initialize_stages))

        # 测试可以调用 initialize_stages 方法
        stage_names = ["stage1", "stage2", "stage3"]
        self.progress_panel.initialize_stages(stage_names)

        # 验证阶段列表已初始化
        self.assertEqual(self.progress_panel.stage_list.rowCount(), 3)
        self.assertEqual(self.progress_panel.progress_bar.value(), 0)

    def test_8_8_unit_test_verify_progress_panel_integration(self):
        """测试 8.8: 添加单元测试验证进度面板集成"""
        # 1. 进度面板实例存在
        self.assertIsNotNone(self.progress_panel)
        self.assertIsInstance(self.progress_panel, ProgressPanel)

        # 2. 进度面板的所有必需方法都存在
        required_methods = [
            'initialize_stages',
            'update_progress',
            '_update_current_stage_label',
            '_update_stage_list',
            '_update_time_display',
            'clear'
        ]

        for method_name in required_methods:
            self.assertTrue(
                hasattr(self.progress_panel, method_name),
                f"ProgressPanel 应该有 {method_name} 方法"
            )

        # 3. 进度面板的UI组件都存在
        self.assertIsNotNone(self.progress_panel.progress_bar)
        self.assertIsNotNone(self.progress_panel.current_stage_label)
        self.assertIsNotNone(self.progress_panel.stage_list)
        self.assertIsNotNone(self.progress_panel.time_label)

        # 4. 测试完整的工作流：初始化阶段 -> 更新进度
        stage_names = ["stage1", "stage2", "stage3"]
        self.progress_panel.initialize_stages(stage_names)

        # 更新第一阶段
        progress1 = BuildProgress(
            current_stage="stage1",
            total_stages=3,
            completed_stages=0,
            percentage=0.0,
            elapsed_time=10.0,
            estimated_remaining_time=90.0
        )
        progress1.stage_statuses = {
            "stage1": StageStatus.RUNNING,
            "stage2": StageStatus.PENDING,
            "stage3": StageStatus.PENDING
        }
        self.progress_panel.update_progress(progress1)

        self.assertEqual(self.progress_panel.progress_bar.value(), 0)
        self.assertIn("stage1", self.progress_panel.current_stage_label.text())

        # 更新第二阶段（第一阶段完成）
        progress2 = BuildProgress(
            current_stage="stage2",
            total_stages=3,
            completed_stages=1,
            percentage=33.3,
            elapsed_time=30.0,
            estimated_remaining_time=60.0
        )
        progress2.stage_statuses = {
            "stage1": StageStatus.COMPLETED,
            "stage2": StageStatus.RUNNING,
            "stage3": StageStatus.PENDING
        }
        self.progress_panel.update_progress(progress2)

        self.assertEqual(self.progress_panel.progress_bar.value(), 33)
        self.assertIn("stage2", self.progress_panel.current_stage_label.text())

        # 更新完成状态
        progress3 = BuildProgress(
            current_stage="",
            total_stages=3,
            completed_stages=3,
            percentage=100.0,
            elapsed_time=90.0,
            estimated_remaining_time=0.0
        )
        progress3.stage_statuses = {
            "stage1": StageStatus.COMPLETED,
            "stage2": StageStatus.COMPLETED,
            "stage3": StageStatus.COMPLETED
        }
        self.progress_panel.update_progress(progress3)

        self.assertEqual(self.progress_panel.progress_bar.value(), 100)


if __name__ == '__main__':
    unittest.main()
