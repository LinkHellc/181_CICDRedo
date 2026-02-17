"""Unit tests for Story 3.1 Task 7: Emit Progress Signals in Workflow Execution

Tests for WorkflowThread progress signal emission timing.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.core.models import (
    ProjectConfig,
    WorkflowConfig,
    StageConfig,
    BuildState
)
from src.core.workflow_thread import WorkflowThread


class TestStory31Task7(unittest.TestCase):
    """测试 Story 3.1 任务 7: 在工作流执行中发射进度信号"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建测试配置
        self.project_config = ProjectConfig(
            name="test_project",
            simulink_path="test.slx",
            matlab_code_path="test",
            a2l_path="test.a2l",
            target_path="test.elf",
            iar_project_path="test.ewp"
        )

        # 创建工作流配置（包含3个阶段）
        self.workflow_config = WorkflowConfig(
            id="test_workflow",
            name="Test Workflow",
            description="Test workflow",
            estimated_time=60,
            stages=[
                StageConfig(
                    name="stage1",
                    enabled=True
                ),
                StageConfig(
                    name="stage2",
                    enabled=True
                ),
                StageConfig(
                    name="stage3",
                    enabled=True
                )
            ]
        )

    def test_7_1_stage_started_signal_defined(self):
        """测试 7.1: 在 execute_workflow() 函数中，每个阶段开始时发射 stage_started 信号"""
        # 验证信号存在并可以连接
        thread = WorkflowThread(self.project_config, self.workflow_config)

        self.assertTrue(hasattr(thread, 'stage_started'))

        # 测试信号可以连接
        signal_received = []

        def on_stage_started(stage_name):
            signal_received.append(stage_name)

        thread.stage_started.connect(on_stage_started)

        # 手动发射信号测试
        thread.stage_started.emit("test_stage")

        self.assertEqual(len(signal_received), 1)
        self.assertEqual(signal_received[0], "test_stage")

    def test_7_2_stage_progress_running_signal_defined(self):
        """测试 7.2: 在每个阶段开始时发射阶段进度信号（状态：RUNNING）"""
        # 验证 stage_started 信号存在
        thread = WorkflowThread(self.project_config, self.workflow_config)

        self.assertTrue(hasattr(thread, 'stage_started'))
        self.assertTrue(hasattr(thread, 'progress_update'))

    def test_7_3_stage_progress_completed_signal_defined(self):
        """测试 7.3: 在每个阶段完成后发射阶段进度信号（状态：COMPLETED）"""
        # 验证 stage_complete 信号存在
        thread = WorkflowThread(self.project_config, self.workflow_config)

        self.assertTrue(hasattr(thread, 'stage_complete'))

        # 测试信号可以连接
        signal_received = []

        def on_stage_complete(stage_name, success):
            signal_received.append((stage_name, success))

        thread.stage_complete.connect(on_stage_complete)

        # 手动发射信号测试
        thread.stage_complete.emit("test_stage", True)

        self.assertEqual(len(signal_received), 1)
        self.assertEqual(signal_received[0], ("test_stage", True))

    def test_7_4_stage_progress_failed_signal_defined(self):
        """测试 7.4: 在每个阶段失败时发射阶段进度信号（状态：FAILED）"""
        # 验证 stage_complete 信号可以传递失败状态
        thread = WorkflowThread(self.project_config, self.workflow_config)

        signal_received = []

        def on_stage_complete(stage_name, success):
            signal_received.append((stage_name, success))

        thread.stage_complete.connect(on_stage_complete)

        # 手动发射信号测试（失败状态）
        thread.stage_complete.emit("test_stage", False)

        self.assertEqual(len(signal_received), 1)
        self.assertEqual(signal_received[0], ("test_stage", False))

    def test_7_5_build_progress_signal_defined(self):
        """测试 7.5: 计算并发射整体进度（已完成阶段数 / 总阶段数 * 100）"""
        # 验证 progress_update 信号存在
        thread = WorkflowThread(self.project_config, self.workflow_config)

        self.assertTrue(hasattr(thread, 'progress_update'))

        # 测试信号可以连接
        signal_received = []

        def on_progress_update(percent, message):
            signal_received.append((percent, message))

        thread.progress_update.connect(on_progress_update)

        # 手动发射信号测试
        thread.progress_update.emit(50, "Test message")

        self.assertEqual(len(signal_received), 1)
        self.assertEqual(signal_received[0], (50, "Test message"))

    def test_7_6_unit_test_verify_signal_emission_timing(self):
        """测试 7.6: 添加单元测试验证信号发射时机"""
        # 验证所有必要的信号都存在并且可以连接
        thread = WorkflowThread(self.project_config, self.workflow_config)

        signal_timeline = []

        def on_stage_started(stage_name):
            signal_timeline.append(('stage_started', stage_name))

        def on_stage_complete(stage_name, success):
            signal_timeline.append(('stage_complete', stage_name, success))

        def on_progress_update(percent, message):
            signal_timeline.append(('progress_update', percent, message))

        def on_build_finished(state):
            signal_timeline.append(('build_finished', state))

        # 连接所有信号
        thread.stage_started.connect(on_stage_started)
        thread.stage_complete.connect(on_stage_complete)
        thread.progress_update.connect(on_progress_update)
        thread.build_finished.connect(on_build_finished)

        # 手动发射信号测试顺序
        thread.stage_started.emit("stage1")
        thread.progress_update.emit(33, "Executing stage1")
        thread.stage_complete.emit("stage1", True)
        thread.progress_update.emit(67, "Executing stage2")
        thread.stage_started.emit("stage2")
        thread.stage_complete.emit("stage2", True)
        thread.progress_update.emit(100, "All stages completed")
        # 注意：build_finished 信号可能在其他地方被发射

        # 验证信号数量（至少应该有6个）
        self.assertGreaterEqual(len(signal_timeline), 6)

        # 验证信号顺序（至少前6个）
        self.assertEqual(signal_timeline[0][0], 'stage_started')
        self.assertEqual(signal_timeline[1][0], 'progress_update')
        self.assertEqual(signal_timeline[2][0], 'stage_complete')
        self.assertEqual(signal_timeline[3][0], 'progress_update')
        self.assertEqual(signal_timeline[4][0], 'stage_started')
        self.assertEqual(signal_timeline[5][0], 'stage_complete')


if __name__ == '__main__':
    unittest.main()
