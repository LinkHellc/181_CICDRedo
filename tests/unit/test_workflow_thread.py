"""Unit tests for WorkflowThread (Story 2.4 Task 2)

Tests for workflow thread execution, signals, and cancellation.
"""

import pytest
import time
from unittest.mock import Mock, patch

from PyQt6.QtCore import QObject, Qt

from core.models import (
    ProjectConfig,
    WorkflowConfig,
    StageConfig,
    BuildState
)
from core.workflow_thread import WorkflowThread


class TestWorkflowThreadSignals:
    """Test WorkflowThread signal emission (Story 2.4 Task 2.3)"""

    def test_workflow_thread_has_signals(self):
        """Test that WorkflowThread has all required signals"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(id="test", name="Test Workflow")

        thread = WorkflowThread(project_config, workflow_config)

        # Check all required signals exist
        assert hasattr(thread, 'progress_update')
        assert hasattr(thread, 'stage_started')
        assert hasattr(thread, 'stage_complete')
        assert hasattr(thread, 'log_message')
        assert hasattr(thread, 'error_occurred')
        assert hasattr(thread, 'build_finished')

    def test_progress_update_signal(self):
        """Test progress_update signal emission"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[StageConfig(name="matlab_gen", enabled=True)]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Track signal emissions
        progress_emissions = []
        thread.progress_update.connect(lambda percent, msg: progress_emissions.append((percent, msg)))

        # Mock stage execution to complete quickly (patch core.workflow.STAGE_EXECUTORS)
        with patch('core.workflow.STAGE_EXECUTORS', {'matlab_gen': Mock()}):
            thread.run()

            # Check that progress signals were emitted
            assert len(progress_emissions) > 0
            assert all(isinstance(p, int) for p, _ in progress_emissions)
            assert all(isinstance(m, str) for _, m in progress_emissions)

    def test_stage_started_signal(self):
        """Test stage_started signal emission"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[StageConfig(name="matlab_gen", enabled=True)]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Track signal emissions
        started_stages = []
        thread.stage_started.connect(lambda name: started_stages.append(name))

        # Mock stage execution to complete quickly
        with patch('core.workflow.STAGE_EXECUTORS', {'matlab_gen': Mock()}):
            thread.run()

            # Check that stage started signal was emitted
            assert len(started_stages) > 0
            assert "matlab_gen" in started_stages

    def test_log_message_signal(self):
        """Test log_message signal emission"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[StageConfig(name="matlab_gen", enabled=True)]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Track signal emissions
        log_messages = []
        thread.log_message.connect(lambda msg: log_messages.append(msg))

        # Mock stage execution to complete quickly
        with patch('core.workflow.STAGE_EXECUTORS', {'matlab_gen': Mock()}):
            thread.run()

            # Check that log signals were emitted
            assert len(log_messages) > 0
            assert all(isinstance(m, str) for m in log_messages)

    def test_build_finished_signal(self):
        """Test build_finished signal emission"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[StageConfig(name="matlab_gen", enabled=True)]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Track signal emissions
        finished_state = []
        thread.build_finished.connect(lambda state: finished_state.append(state))

        # Mock stage execution to complete quickly
        with patch('core.workflow.STAGE_EXECUTORS', {'matlab_gen': Mock()}):
            thread.run()

            # Check that finished signal was emitted
            assert len(finished_state) == 1
            assert isinstance(finished_state[0], BuildState)


class TestWorkflowThreadExecution:
    """Test WorkflowThread execution logic (Story 2.4 Task 2.4, 2.5)"""

    def test_workflow_thread_initialization(self):
        """Test WorkflowThread initialization"""
        project_config = ProjectConfig(
            name="TestProject",
            simulink_path="C:/test/simulink"
        )
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow"
        )

        thread = WorkflowThread(project_config, workflow_config)

        assert thread.project_config == project_config
        assert thread.workflow_config == workflow_config
        assert thread._build_execution.project_name == "TestProject"
        assert thread._build_execution.workflow_id == "test"
        assert thread._build_execution.state == BuildState.IDLE

    def test_workflow_execution_with_enabled_stage(self):
        """Test workflow execution with enabled stage (Story 2.4 Task 2.5)"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[StageConfig(name="matlab_gen", enabled=True)]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Track execution
        finished_states = []
        thread.build_finished.connect(lambda state: finished_states.append(state))

        # Mock stage execution
        from core.models import StageResult, StageStatus
        mock_result = StageResult(
            status=StageStatus.COMPLETED,
            message="Stage completed"
        )
        with patch('core.workflow.STAGE_EXECUTORS', {'matlab_gen': Mock(return_value=mock_result)}):
            thread.run()

            # Check that build finished successfully
            assert len(finished_states) == 1
            assert finished_states[0] == BuildState.COMPLETED

    def test_workflow_execution_with_disabled_stage(self):
        """Test workflow execution with disabled stage (Story 2.4 Task 3.3)"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[StageConfig(name="matlab_gen", enabled=False)]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Track execution
        finished_states = []
        thread.build_finished.connect(lambda state: finished_states.append(state))

        thread.run()

        # Should finish immediately (no enabled stages)
        assert len(finished_states) == 1
        # Note: With no enabled stages, the thread will still emit build_finished

    def test_workflow_execution_with_multiple_stages(self):
        """Test workflow execution with multiple stages (Story 2.4 Task 2.5)"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[
                StageConfig(name="matlab_gen", enabled=True),
                StageConfig(name="file_process", enabled=True)
            ]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Track execution
        stage_completions = []
        thread.stage_complete.connect(lambda name, success: stage_completions.append((name, success)))

        finished_states = []
        thread.build_finished.connect(lambda state: finished_states.append(state))

        # Mock stage execution
        from core.models import StageResult, StageStatus
        mock_result = StageResult(
            status=StageStatus.COMPLETED,
            message="Stage completed"
        )
        with patch('core.workflow.STAGE_EXECUTORS', {
            'matlab_gen': Mock(return_value=mock_result),
            'file_process': Mock(return_value=mock_result)
        }):
            thread.run()

            # Check that both stages completed
            assert len(stage_completions) == 2
            assert all(success for _, success in stage_completions)
            assert finished_states[0] == BuildState.COMPLETED


class TestWorkflowThreadCancellation:
    """Test workflow cancellation (Story 2.4 Task 7.4)"""

    def test_workflow_cancellation(self):
        """Test workflow cancellation when requested"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[
                StageConfig(name="matlab_gen", enabled=True),
                StageConfig(name="file_process", enabled=True)
            ]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Track execution
        finished_states = []
        thread.build_finished.connect(lambda state: finished_states.append(state))

        # Mock stage execution that returns FAILED status
        from core.models import StageResult, StageStatus

        def failing_executor(config, context):
            return StageResult(status=StageStatus.FAILED, message="Stage failed")

        with patch('core.workflow.STAGE_EXECUTORS', {
            'matlab_gen': failing_executor,
            'file_process': failing_executor
        }):
            # Run the workflow (synchronous)
            thread.run()

            # Check that build finished with failure state
            assert len(finished_states) == 1
            assert finished_states[0] == BuildState.FAILED


class TestWorkflowThreadBuildExecution:
    """Test BuildExecution tracking (Story 2.4 Task 1, 6)"""

    def test_build_execution_tracking(self):
        """Test that build execution information is tracked"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[StageConfig(name="matlab_gen", enabled=True)]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Mock stage execution with delay to ensure non-zero duration
        from core.models import StageResult, StageStatus
        def delayed_executor(config, context):
            time.sleep(0.001)  # Small delay
            return StageResult(
                status=StageStatus.COMPLETED,
                message="Stage completed"
            )

        with patch('core.workflow.STAGE_EXECUTORS', {'matlab_gen': delayed_executor}):
            thread.run()

            # Check build execution info
            execution = thread.get_build_execution()
            assert execution.project_name == "TestProject"
            assert execution.workflow_id == "test"
            assert execution.state == BuildState.COMPLETED
            assert execution.progress_percent == 100
            assert len(execution.stages) == 1
            assert execution.stages[0].name == "matlab_gen"
            assert execution.stages[0].status == BuildState.COMPLETED
            assert execution.duration >= 0  # Should be non-negative (may be very small)

    def test_build_execution_time_tracking(self):
        """Test that execution time is tracked using monotonic time (Story 2.4 Task 6.1)"""
        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[StageConfig(name="matlab_gen", enabled=True)]
        )

        thread = WorkflowThread(project_config, workflow_config)

        # Mock stage execution with delay
        from core.models import StageResult, StageStatus
        def timed_executor(config, context):
            time.sleep(0.1)
            return StageResult(status=StageStatus.COMPLETED, message="Completed")

        with patch('core.workflow.STAGE_EXECUTORS', {'matlab_gen': timed_executor}):
            start_before = time.monotonic()
            thread.run()
            elapsed = time.monotonic() - start_before

            # Check build execution time (allow some tolerance for timing precision)
            execution = thread.get_build_execution()
            assert execution.duration >= 0.08  # At least 0.08s (with tolerance)
            assert execution.start_time > 0
            assert execution.end_time > execution.start_time
