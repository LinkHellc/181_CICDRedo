"""Unit tests for workflow cancellation (Story 2.15 - Task 2)

This module contains unit tests for the WorkflowThread cancellation mechanism.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QThread, QObject, pyqtSignal

from core.models import (
    WorkflowConfig,
    ProjectConfig,
    BuildContext,
    BuildState,
    StageConfig,
    StageResult,
    StageStatus
)
from core.workflow_thread import WorkflowThread


class TestWorkflowCancellation:
    """测试工作流取消功能 (Story 2.15 - Task 2.7-2.9)"""

    @pytest.fixture
    def project_config(self):
        """创建测试用的项目配置"""
        return ProjectConfig(
            name="TestProject",
            simulink_path="C:/test/test.slx",
            matlab_code_path="C:/test/code",
            a2l_path="C:/test/test.a2l",
            target_path="C:/test/target",
            iar_project_path="C:/test/test.ewp"
        )

    @pytest.fixture
    def workflow_config(self):
        """创建测试用的工作流配置"""
        return WorkflowConfig(
            id="test_workflow",
            name="Test Workflow",
            stages=[
                StageConfig(name="matlab_gen", enabled=True, timeout=60),
                StageConfig(name="iar_compile", enabled=True, timeout=120),
                StageConfig(name="file_process", enabled=True, timeout=30)
            ]
        )

    @pytest.fixture
    def worker(self, project_config, workflow_config):
        """创建测试用的 WorkflowThread"""
        return WorkflowThread(project_config, workflow_config)

    def test_cancel_requested_property(self, worker):
        """测试 cancel_requested 属性默认为 False (Task 2.1)"""
        assert worker._context.cancel_requested is False

    def test_request_cancellation_sets_flag(self, worker):
        """测试 request_cancellation() 方法设置取消标志 (Task 2.2)"""
        # 调用 request_cancellation
        worker.request_cancellation()

        # 验证标志已设置
        assert worker._context.cancel_requested is True

    def test_request_cancel_sets_flag(self, worker):
        """测试 request_cancel() 方法设置取消标志 (Task 2.2)"""
        # 调用 request_cancel
        worker.request_cancel()

        # 验证标志已设置
        assert worker._context.cancel_requested is True

    def test_request_cancellation_calls_interrupt(self, worker):
        """测试 request_cancellation() 调用 QThread 中断机制 (Task 2.2)"""
        with patch.object(worker, 'requestInterruption') as mock_interrupt:
            worker.request_cancellation()
            mock_interrupt.assert_called_once()

    def test_request_cancellation_sets_context_flag(self, worker):
        """测试 request_cancellation() 设置 context.cancel_requested (Task 2.2)"""
        worker.request_cancellation()
        assert worker._context.cancel_requested is True

    def test_cancelled_signal_exists(self, worker):
        """测试 build_cancelled 信号存在 (Task 2.5)"""
        assert hasattr(worker, 'build_cancelled')
        # 验证信号可以连接
        worker.build_cancelled.connect(lambda: None)
        # 验证信号可以断开
        worker.build_cancelled.disconnect()

    def test_cancelled_signal_emission(self, worker):
        """测试取消信号发射 (Task 2.6)"""
        # 连接信号监听器
        received_signals = []
        def on_cancelled(stage_name, message):
            received_signals.append((stage_name, message))

        worker.build_cancelled.connect(on_cancelled)

        # 设置取消标志
        worker._context.cancel_requested = True
        worker._build_execution.current_stage = "test_stage"

        # 发射信号
        worker._cleanup_on_cancel()

        # 验证信号发射
        assert len(received_signals) == 1
        assert received_signals[0] == ("test_stage", "构建已取消")

    def test_cancelled_flag_check_in_execute_stage(self, worker):
        """测试 execute_stage() 中检查取消标志 (Task 2.4)"""
        stage_config = StageConfig(name="test_stage", enabled=True)

        # 设置取消标志
        worker._context.is_cancelled = True

        # 执行阶段（应返回 CANCELLED）
        result = worker._execute_stage(stage_config, worker._context)

        # 验证结果
        assert result.status == StageStatus.CANCELLED
        assert "已取消" in result.message

    def test_cancelled_flag_check_after_stage_execution(self, worker):
        """测试阶段执行后检查取消标志 (Task 2.4)"""
        stage_config = StageConfig(name="test_stage", enabled=True)

        # Mock 执行器返回成功
        mock_executor = Mock(return_value=StageResult(
            status=StageStatus.COMPLETED,
            message="Success"
        ))

        with patch.dict('core.workflow.STAGE_EXECUTORS', {'test_stage': mock_executor}):
            # 设置取消标志
            worker._context.is_cancelled = True

            # 执行阶段（应返回 CANCELLED，即使执行器返回成功）
            result = worker._execute_stage(stage_config, worker._context)

            # 验证结果（应该被覆盖为 CANCELLED）
            assert result.status == StageStatus.CANCELLED

    def test_interruption_request_propagates_to_context(self, worker):
        """测试中断请求传播到 context (Task 2.4)"""
        # Mock isInterruptionRequested 方法
        with patch.object(worker, 'isInterruptionRequested', return_value=True):
            # 调用中断
            worker.request_cancellation()

            # 验证 context 状态
            assert worker._context.cancel_requested is True
            assert worker.isInterruptionRequested()

    def test_execute_stage_with_cancellation_before(self, worker):
        """测试阶段执行前取消 (Task 2.4)"""
        stage_config = StageConfig(name="test_stage", enabled=True)

        # Mock 执行器（不应该被调用）
        mock_executor = Mock(return_value=StageResult(
            status=StageStatus.COMPLETED,
            message="Success"
        ))

        with patch.dict('core.workflow.STAGE_EXECUTORS', {'test_stage': mock_executor}):
            # 设置取消标志
            worker._context.is_cancelled = True

            # 执行阶段
            result = worker._execute_stage(stage_config, worker._context)

            # 验证：执行器不应被调用
            mock_executor.assert_not_called()

            # 验证结果
            assert result.status == StageStatus.CANCELLED

    def test_execute_stage_without_cancellation(self, worker):
        """测试正常阶段执行（未取消）(Task 2.4)"""
        stage_config = StageConfig(name="test_stage", enabled=True)

        # Mock 执行器返回成功
        mock_executor = Mock(return_value=StageResult(
            status=StageStatus.COMPLETED,
            message="Success",
            output_files=["test.c"]
        ))

        with patch.dict('core.workflow.STAGE_EXECUTORS', {'test_stage': mock_executor}):
            # 不设置取消标志
            worker._context.is_cancelled = False

            # 执行阶段
            result = worker._execute_stage(stage_config, worker._context)

            # 验证：执行器应被调用
            mock_executor.assert_called_once_with(stage_config, worker._context)

            # 验证结果
            assert result.status == StageStatus.COMPLETED
            assert result.output_files == ["test.c"]

    def test_multiple_cancellation_requests(self, worker):
        """测试多次取消请求 (Task 2.7)"""
        # 第一次取消
        worker.request_cancellation()
        assert worker._context.cancel_requested is True

        # 第二次取消（应该保持 True）
        worker.request_cancellation()
        assert worker._context.cancel_requested is True

    def test_cleanup_on_cancel_terminates_processes(self, worker):
        """测试取消时终止进程 (Task 2.9)"""
        # Mock 终止进程
        mock_process = Mock()
        worker._context.active_processes = {"test_proc": mock_process}

        with patch.object(worker._context, 'terminate_processes') as mock_terminate:
            mock_terminate.return_value = 1
            worker._cleanup_on_cancel()

            # 验证终止进程被调用
            mock_terminate.assert_called_once()

    def test_cleanup_on_cancel_cleans_temp_files(self, worker):
        """测试取消时清理临时文件 (Task 2.9)"""
        # Mock 清理文件
        with patch.object(worker._context, 'cleanup_temp_files') as mock_cleanup:
            mock_cleanup.return_value = 5
            worker._cleanup_on_cancel()

            # 验证清理文件被调用
            mock_cleanup.assert_called_once()

    def test_cleanup_on_cancel_sends_signal(self, worker):
        """测试取消时发送信号 (Task 2.9)"""
        # 连接信号监听器
        received = []

        def on_cancelled(stage, message):
            received.append((stage, message))

        worker.build_cancelled.connect(on_cancelled)
        worker._build_execution.current_stage = "test_stage"

        worker._cleanup_on_cancel()

        # 验证信号发送
        assert len(received) == 1
        assert received[0][0] == "test_stage"
        assert "构建已取消" in received[0][1]
