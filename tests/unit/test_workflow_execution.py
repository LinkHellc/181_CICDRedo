"""Unit tests for workflow execution (Story 2.4).

Tests the workflow execution framework including:
- WorkflowThread functionality
- Signal emission
- execute_workflow function
- BuildContext usage
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from core.workflow import execute_workflow
from core.models import (
    WorkflowConfig, StageConfig, BuildContext,
    StageResult, StageStatus, ProjectConfig
)


class TestExecuteWorkflow:
    """测试 execute_workflow 函数"""

    def test_execute_workflow_with_no_stages(self):
        """测试没有启用阶段的情况 (Story 2.4 Task 8.1)"""
        config = WorkflowConfig(stages=[])
        context = BuildContext()

        result = execute_workflow(config, context)

        assert result is False

    def test_execute_workflow_with_disabled_stages(self):
        """测试所有阶段都禁用的情况"""
        stages = [
            StageConfig(name="test_stage", enabled=False)
        ]
        config = WorkflowConfig(stages=stages)
        context = BuildContext()

        result = execute_workflow(config, context)

        assert result is False

    def test_execute_workflow_progress_callback(self):
        """测试进度回调 (Story 2.4 Task 8.1)"""
        stages = [
            StageConfig(name="test_stage", enabled=True)
        ]
        config = WorkflowConfig(stages=stages)
        context = BuildContext()

        progress_mock = Mock()
        execute_workflow(config, context, progress_callback=progress_mock)

        # 验证进度回调被调用
        assert progress_mock.call_count > 0

        # 验证最终进度是 100%
        last_call = progress_mock.call_args_list[-1]
        assert last_call[0][0] == 100  # 进度百分比

    def test_execute_workflow_stage_callback(self):
        """测试阶段完成回调 (Story 2.4 Task 8.1)"""
        stages = [
            StageConfig(name="test_stage", enabled=True)
        ]
        config = WorkflowConfig(stages=stages)
        context = BuildContext()

        stage_mock = Mock()
        execute_workflow(config, context, stage_callback=stage_mock)

        # 验证阶段回调被调用
        assert stage_mock.call_count == 1

        # 验证回调参数
        call_args = stage_mock.call_args_list[0]
        assert call_args[0][0] == "test_stage"  # 阶段名
        assert call_args[0][1] is True  # 成功标志

    def test_execute_workflow_cancel_check(self):
        """测试取消检查 (Story 2.4 Task 8.2)"""
        stages = [
            StageConfig(name="test_stage1", enabled=True),
            StageConfig(name="test_stage2", enabled=True)
        ]
        config = WorkflowConfig(stages=stages)
        context = BuildContext()

        # 设置取消检查返回 True
        cancel_check = Mock(return_value=True)

        result = execute_workflow(config, context, cancel_check=cancel_check)

        # 验证工作流被取消
        assert result is False
        assert context.state.get("cancel_reason") == "user_requested"

    def test_execute_workflow_build_context(self):
        """测试 BuildContext 状态传递 (Story 2.4 Task 1.3)"""
        stages = [
            StageConfig(name="test_stage", enabled=True)
        ]
        config = WorkflowConfig(stages=stages)
        context = BuildContext()

        execute_workflow(config, context)

        # 验证开始时间被记录
        assert "build_start_time" in context.state

        # 验证执行时间被记录
        assert "build_duration" in context.state

        # 验证阶段输出被保存
        assert "test_stage_output" in context.state

    def test_execute_workflow_uses_monotonic_time(self):
        """测试使用 time.monotonic() 而非 time.time() (Story 2.4 架构要求)"""
        stages = [
            StageConfig(name="test_stage", enabled=True)
        ]
        config = WorkflowConfig(stages=stages)
        context = BuildContext()

        with patch('time.monotonic') as mock_monotonic:
            mock_monotonic.return_value = 100.0

            execute_workflow(config, context)

            # 验证使用了 monotonic 时间
            assert context.state["build_start_time"] == 100.0


class TestBuildContext:
    """测试 BuildContext 类"""

    def test_build_context_initialization(self):
        """测试 BuildContext 初始化 (Story 2.4 Task 1.3)"""
        context = BuildContext()

        assert context.config == {}
        assert context.state == {}
        assert context.log_callback is None

    def test_build_context_with_values(self):
        """测试带参数的 BuildContext 初始化"""
        config = {"key": "value"}
        state = {"state_key": "state_value"}
        log_callback = Mock()

        context = BuildContext(config=config, state=state, log_callback=log_callback)

        assert context.config == config
        assert context.state == state
        assert context.log_callback == log_callback

    def test_build_context_get(self):
        """测试 BuildContext.get() 方法"""
        context = BuildContext()
        context.state["key"] = "value"

        assert context.get("key") == "value"
        assert context.get("nonexistent") is None
        assert context.get("nonexistent", "default") == "default"

    def test_build_context_set(self):
        """测试 BuildContext.set() 方法"""
        context = BuildContext()
        context.set("key", "value")

        assert context.state["key"] == "value"

    def test_build_context_log(self):
        """测试 BuildContext.log() 方法"""
        log_callback = Mock()
        context = BuildContext(log_callback=log_callback)

        context.log("test message")

        log_callback.assert_called_once_with("test message")

    def test_build_context_log_without_callback(self):
        """测试没有回调时的 log() 方法"""
        context = BuildContext()

        # 不应抛出异常
        context.log("test message")


class TestStageResult:
    """测试 StageResult 类"""

    def test_stage_result_default_values(self):
        """测试 StageResult 默认值"""
        result = StageResult()

        assert result.status == StageStatus.PENDING
        assert result.message == ""
        assert result.output_files == []
        assert result.error is None
        assert result.suggestions == []
        assert result.execution_time == 0.0

    def test_stage_result_to_dict(self):
        """测试 StageResult.to_dict() 方法"""
        result = StageResult(
            status=StageStatus.COMPLETED,
            message="Success",
            output_files=["file1.txt", "file2.txt"],
            execution_time=10.5
        )

        data = result.to_dict()

        assert data["status"] == "completed"
        assert data["message"] == "Success"
        assert data["output_files"] == ["file1.txt", "file2.txt"]
        assert data["execution_time"] == 10.5

    def test_stage_result_from_dict(self):
        """测试 StageResult.from_dict() 方法"""
        data = {
            "status": "completed",
            "message": "Success",
            "output_files": ["file1.txt"],
            "execution_time": 5.0
        }

        result = StageResult.from_dict(data)

        assert result.status == StageStatus.COMPLETED
        assert result.message == "Success"
        assert result.output_files == ["file1.txt"]
        assert result.execution_time == 5.0


class TestStageStatus:
    """测试 StageStatus 枚举"""

    def test_stage_status_values(self):
        """测试 StageStatus 枚举值"""
        assert StageStatus.PENDING.value == "pending"
        assert StageStatus.RUNNING.value == "running"
        assert StageStatus.COMPLETED.value == "completed"
        assert StageStatus.FAILED.value == "failed"
        assert StageStatus.CANCELLED.value == "cancelled"


@pytest.mark.skip(reason="需要 PyQt6 事件循环，需要在集成测试中运行")
class TestWorkflowThread:
    """测试 WorkflowThread 类 (Story 2.4 Task 1.4)

    注意: 这些测试需要 PyQt6 事件循环，通常需要在集成测试中运行
    """

    def test_workflow_thread_initialization(self):
        """测试 WorkflowThread 初始化"""
        from ui.main_window import WorkflowThread

        project_config = ProjectConfig(name="Test")
        workflow_config = WorkflowConfig(stages=[])

        thread = WorkflowThread(project_config, workflow_config)

        assert thread.project_config == project_config
        assert thread.workflow_config == workflow_config
        assert thread._is_cancelled is False

    def test_workflow_thread_cancel(self):
        """测试 WorkflowThread.cancel() 方法"""
        from ui.main_window import WorkflowThread

        project_config = ProjectConfig(name="Test")
        workflow_config = WorkflowConfig(stages=[])

        thread = WorkflowThread(project_config, workflow_config)
        thread.cancel()

        assert thread._is_cancelled is True

    def test_workflow_thread_signals_defined(self):
        """测试 WorkflowThread 信号定义 (Story 2.4 Task 1.2)"""
        from ui.main_window import WorkflowThread

        project_config = ProjectConfig(name="Test")
        workflow_config = WorkflowConfig(stages=[])

        thread = WorkflowThread(project_config, workflow_config)

        # 验证所有信号都存在
        assert hasattr(thread, 'progress_update')
        assert hasattr(thread, 'stage_complete')
        assert hasattr(thread, 'log_message')
        assert hasattr(thread, 'error_occurred')
        assert hasattr(thread, 'finished')
