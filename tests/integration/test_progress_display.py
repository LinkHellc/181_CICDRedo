"""Integration tests for progress display (Story 2.14)

Tests for complete progress display workflow, including:
- Complete progress display flow
- Progress updates from workflow start to end
- Multiple stage progress display
- Failure scenarios
- Cancel scenarios
- Skipped stage progress display
- Time estimation accuracy
- Progress persistence and recovery
- UI responsiveness (update frequency)
"""

import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtTest import QTest

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.core.models import (
    BuildProgress, StageStatus, ProjectConfig, WorkflowConfig,
    StageConfig, BuildContext, StageResult
)
from src.core.workflow_thread import WorkflowThread
from src.ui.widgets.progress_panel import ProgressPanel
from src.utils.progress import (
    calculate_progress, calculate_time_remaining,
    format_duration, save_progress, load_progress
)


class TestProgressDisplayIntegration(unittest.TestCase):
    """测试完整的进度显示流程 (Story 2.14 - 任务 15)"""

    def setUp(self):
        """每个测试前的设置"""
        self.progress_panel = ProgressPanel()

    def tearDown(self):
        """每个测试后的清理"""
        if hasattr(self, 'progress_panel'):
            self.progress_panel.clear()

    def test_complete_progress_display_flow(self):
        """测试完整的进度显示流程 (任务 15.2)"""
        # 模拟完整的工作流进度
        stages = ["stage1", "stage2", "stage3", "stage4", "stage5"]
        total_stages = len(stages)

        for i, stage in enumerate(stages):
            # 阶段开始
            progress = BuildProgress(
                current_stage=stage,
                total_stages=total_stages,
                completed_stages=i,
                stage_statuses={s: StageStatus.PENDING for s in stages}
            )
            progress.stage_statuses[stage] = StageStatus.RUNNING

            self.progress_panel.update_progress(progress)

            # 验证进度条（由于动画影响，可能需要多次更新才能达到目标值）
            expected_percentage = (i / total_stages) * 100
            # 宽容的断言，允许动画延迟
            self.assertGreaterEqual(self.progress_panel.progress_bar.value(), int(expected_percentage) - 1)

            # 阶段完成
            time.sleep(0.01)  # 短暂等待
            progress.stage_statuses[stage] = StageStatus.COMPLETED
            progress.completed_stages = i + 1
            progress.percentage = ((i + 1) / total_stages) * 100
            progress.elapsed_time = (i + 1) * 10.0

            self.progress_panel.update_progress(progress)

        # 最终状态
        final_progress = BuildProgress(
            current_stage="",
            total_stages=total_stages,
            completed_stages=total_stages,
            percentage=100.0,
            elapsed_time=50.0,
            estimated_remaining_time=0.0
        )
        final_progress.stage_statuses = {s: StageStatus.COMPLETED for s in stages}

        self.progress_panel.update_progress(final_progress)

        # 验证最终状态
        self.assertEqual(self.progress_panel.progress_bar.value(), 100)
        self.assertIn("等待开始...", self.progress_panel.current_stage_label.text())

    def test_multiple_stage_progress_display(self):
        """测试多个阶段的进度显示 (任务 15.4)"""
        progress = BuildProgress(
            current_stage="stage2",
            total_stages=5,
            completed_stages=1,
            percentage=20.0
        )
        progress.stage_statuses = {
            "stage1": StageStatus.COMPLETED,
            "stage2": StageStatus.RUNNING,
            "stage3": StageStatus.PENDING,
            "stage4": StageStatus.PENDING,
            "stage5": StageStatus.PENDING
        }

        self.progress_panel.update_progress(progress)

        # 验证阶段列表
        self.assertEqual(self.progress_panel.stage_list.rowCount(), 5)

        # 验证各个阶段的状态
        self.assertIn("已完成", self.progress_panel.stage_list.item(0, 1).text())
        self.assertIn("进行中", self.progress_panel.stage_list.item(1, 1).text())
        self.assertIn("等待中", self.progress_panel.stage_list.item(2, 1).text())

    def test_failure_scenario_progress_display(self):
        """测试失败场景的进度显示 (任务 15.5)"""
        progress = BuildProgress(
            current_stage="stage3",
            total_stages=5,
            completed_stages=2,
            percentage=40.0
        )
        progress.stage_statuses = {
            "stage1": StageStatus.COMPLETED,
            "stage2": StageStatus.COMPLETED,
            "stage3": StageStatus.FAILED,
            "stage4": StageStatus.PENDING,
            "stage5": StageStatus.PENDING
        }
        progress.stage_errors = {
            "stage3": "Error: compilation failed"
        }

        self.progress_panel.update_progress(progress)

        # 验证当前阶段标签显示错误
        self.assertIn("阶段失败", self.progress_panel.current_stage_label.text())
        self.assertIn("stage3", self.progress_panel.current_stage_label.text())

        # 验证阶段列表显示失败状态
        failed_item = self.progress_panel.stage_list.item(2, 1)
        self.assertIn("失败", failed_item.text())

    def test_cancel_scenario_progress_display(self):
        """测试取消场景的进度显示 (任务 15.6)"""
        progress = BuildProgress(
            current_stage="stage2",
            total_stages=5,
            completed_stages=1,
            percentage=20.0
        )
        progress.stage_statuses = {
            "stage1": StageStatus.COMPLETED,
            "stage2": StageStatus.CANCELLED,
            "stage3": StageStatus.PENDING,
            "stage4": StageStatus.PENDING,
            "stage5": StageStatus.PENDING
        }

        self.progress_panel.update_progress(progress)

        # 验证取消状态显示
        cancelled_item = self.progress_panel.stage_list.item(1, 1)
        self.assertIn("已取消", cancelled_item.text())

    def test_skipped_stage_progress_display(self):
        """测试跳过阶段的进度显示 (任务 15.7)"""
        progress = BuildProgress(
            current_stage="stage3",
            total_stages=5,
            completed_stages=2,
            percentage=60.0
        )
        progress.stage_statuses = {
            "stage1": StageStatus.COMPLETED,
            "stage2": StageStatus.SKIPPED,
            "stage3": StageStatus.RUNNING,
            "stage4": StageStatus.PENDING,
            "stage5": StageStatus.PENDING
        }

        self.progress_panel.update_progress(progress)

        # 验证跳过状态显示
        skipped_item = self.progress_panel.stage_list.item(1, 1)
        self.assertIn("跳过", skipped_item.text())

        # 验证颜色为橙色
        self.assertEqual(
            skipped_item.foreground().color().name().lower(),
            "#ff8800"
        )

    def test_time_estimation_accuracy(self):
        """测试时间估算准确性 (任务 15.8)"""
        # 模拟一个需要100秒的工作流
        total_time = 100.0
        stages = 5
        time_per_stage = total_time / stages

        for i in range(stages):
            # 已用时间
            elapsed = (i + 1) * time_per_stage

            # 进度百分比
            percentage = ((i + 1) / stages) * 100

            # 预计剩余时间
            remaining = calculate_time_remaining(elapsed, percentage)

            # 实际剩余时间
            actual_remaining = total_time - elapsed

            # 验证估算在合理范围内（误差不超过10%）
            max_error = actual_remaining * 0.1
            self.assertAlmostEqual(remaining, actual_remaining, delta=max_error)

    def test_progress_persistence_and_recovery(self):
        """测试进度持久化和恢复 (任务 15.9)"""
        # 创建进度对象
        progress = BuildProgress(
            current_stage="stage2",
            total_stages=5,
            completed_stages=1,
            percentage=20.0,
            elapsed_time=60.0,
            estimated_remaining_time=240.0
        )
        progress.stage_statuses = {
            "stage1": StageStatus.COMPLETED,
            "stage2": StageStatus.RUNNING
        }
        progress.stage_errors = {}

        # 使用临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 保存进度
            saved_file = save_progress(progress.to_dict(), temp_path)
            self.assertIsNotNone(saved_file)
            self.assertTrue(saved_file.exists())

            # 加载进度
            loaded_data = load_progress(temp_path)
            self.assertIsNotNone(loaded_data)

            # 创建新的进度对象
            recovered_progress = BuildProgress.from_dict(loaded_data)

            # 验证恢复的数据
            self.assertEqual(recovered_progress.current_stage, progress.current_stage)
            self.assertEqual(recovered_progress.total_stages, progress.total_stages)
            self.assertEqual(recovered_progress.completed_stages, progress.completed_stages)
            self.assertEqual(recovered_progress.percentage, progress.percentage)
            self.assertEqual(recovered_progress.elapsed_time, progress.elapsed_time)

            # 验证状态枚举正确恢复
            self.assertEqual(
                recovered_progress.stage_statuses["stage1"],
                StageStatus.COMPLETED
            )
            self.assertEqual(
                recovered_progress.stage_statuses["stage2"],
                StageStatus.RUNNING
            )

    def test_ui_responsiveness(self):
        """测试UI响应性（更新频率）(任务 15.10)"""
        # 模拟高频进度更新
        num_updates = 100
        start_time = time.monotonic()

        for i in range(num_updates):
            progress = BuildProgress(
                percentage=float(i),
                elapsed_time=float(i) * 0.1
            )
            self.progress_panel.update_progress(progress)

        end_time = time.monotonic()
        total_time = end_time - start_time

        # 验证所有更新都能快速完成（应该在1秒内）
        self.assertLess(total_time, 1.0)

        # 验证更新间隔历史记录正确
        self.assertEqual(len(self.progress_panel.update_intervals), num_updates)

        # 验证平均更新间隔（应该很短）
        avg_interval = self.progress_panel.get_average_update_interval()
        self.assertLess(avg_interval, 0.1)


class TestWorkflowThreadProgressSignals(unittest.TestCase):
    """测试工作流线程的进度信号 (Story 2.14 - 任务 7.6, 7.7)"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建简单的测试配置
        self.project_config = ProjectConfig(
            name="Test Project",
            simulink_path="test.slx",
            matlab_code_path="test",
            a2l_path="test.a2l",
            target_path="test.out",
            iar_project_path="test.ewp"
        )

        self.workflow_config = WorkflowConfig(
            id="test_workflow",
            name="Test Workflow",
            description="Test workflow for progress signals",
            estimated_time=1,
            stages=[
                StageConfig(name="stage1", enabled=True),
                StageConfig(name="stage2", enabled=True),
                StageConfig(name="stage3", enabled=True)
            ]
        )

    def test_workflow_thread_emits_progress_signals(self):
        """测试工作流线程发射进度信号 (任务 7.6)"""
        # 创建工作流线程
        thread = WorkflowThread(self.project_config, self.workflow_config)

        # 使用模拟的阶段执行器
        from core.workflow import STAGE_EXECUTORS

        def mock_stage_executor(stage_config, context):
            # 模拟执行时间
            time.sleep(0.1)
            # 正确创建StageResult（使用与workflow_thread相同的导入）
            from core.models import StageResult
            return StageResult(
                status=StageStatus.COMPLETED,
                message="Stage completed"
            )

        # 注册模拟执行器
        for stage in self.workflow_config.stages:
            STAGE_EXECUTORS[stage.name] = mock_stage_executor

        # 收集信号
        progress_updates = []

        def on_progress_update_detailed(progress):
            progress_updates.append(progress)

        thread.progress_update_detailed.connect(on_progress_update_detailed)

        # 启动线程
        thread.start()
        thread.wait()

        # 验证信号被发射
        self.assertGreater(len(progress_updates), 0)

        # 验证至少有初始进度和最终进度
        initial_progress = progress_updates[0]
        final_progress = progress_updates[-1]

        self.assertEqual(initial_progress.total_stages, 3)
        self.assertEqual(initial_progress.completed_stages, 0)

        self.assertEqual(final_progress.total_stages, 3)
        self.assertEqual(final_progress.completed_stages, 3)
        self.assertEqual(final_progress.percentage, 100.0)


if __name__ == '__main__':
    unittest.main()
