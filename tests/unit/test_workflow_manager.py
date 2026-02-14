"""Unit tests for WorkflowManager (Story 2.4 Task 8)

Tests for workflow lifecycle management.
"""

import pytest

from core.models import (
    ProjectConfig,
    WorkflowConfig,
    BuildState
)
from core.workflow_manager import WorkflowManager


class TestWorkflowManagerInitialization:
    """Test WorkflowManager initialization"""

    def test_workflow_manager_initialization(self):
        """Test that WorkflowManager initializes correctly"""
        manager = WorkflowManager()

        assert manager.workflow_thread is None
        assert manager.current_execution is None
        assert not manager.is_running()


class TestWorkflowManagerStart:
    """Test workflow start functionality (Story 2.4 Task 8.2)"""

    def test_start_workflow_creates_thread(self):
        """Test that starting workflow creates a thread"""
        manager = WorkflowManager()

        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[]
        )

        result = manager.start_workflow(project_config, workflow_config)

        assert result is True
        assert manager.workflow_thread is not None
        assert manager.is_running()

        # Cleanup
        if manager.workflow_thread.isRunning():
            manager.workflow_thread.requestInterruption()
            manager.workflow_thread.wait()
        manager.cleanup()

    def test_start_workflow_with_connections(self):
        """Test that starting workflow connects signals (Story 2.4 Task 5.2)"""
        manager = WorkflowManager()

        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[]
        )

        # Track callback invocations
        progress_calls = []
        log_calls = []
        finished_calls = []

        connections = {
            'progress_update': lambda percent, msg: progress_calls.append((percent, msg)),
            'log_message': lambda msg: log_calls.append(msg),
            'build_finished': lambda state: finished_calls.append(state)
        }

        result = manager.start_workflow(project_config, workflow_config, connections)

        assert result is True
        assert manager.workflow_thread is not None

        # Cleanup
        if manager.workflow_thread.isRunning():
            manager.workflow_thread.requestInterruption()
            manager.workflow_thread.wait()
        manager.cleanup()

    def test_start_workflow_when_already_running(self):
        """Test that starting workflow when already running fails"""
        manager = WorkflowManager()

        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[]
        )

        # Start first workflow
        result1 = manager.start_workflow(project_config, workflow_config)
        assert result1 is True

        # Try to start second workflow
        result2 = manager.start_workflow(project_config, workflow_config)
        assert result2 is False

        # Cleanup
        if manager.workflow_thread.isRunning():
            manager.workflow_thread.requestInterruption()
            manager.workflow_thread.wait()
        manager.cleanup()


class TestWorkflowManagerStop:
    """Test workflow stop functionality (Story 2.4 Task 7.3, 8.2)"""

    def test_stop_running_workflow(self):
        """Test stopping a running workflow"""
        manager = WorkflowManager()

        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[]
        )

        # Start workflow
        manager.start_workflow(project_config, workflow_config)
        assert manager.is_running()

        # Stop workflow
        result = manager.stop_workflow()
        assert result is True

        # Cleanup
        manager.cleanup()

    def test_stop_when_not_running(self):
        """Test stopping when no workflow is running"""
        manager = WorkflowManager()

        result = manager.stop_workflow()

        assert result is False


class TestWorkflowManagerIsRunning:
    """Test is_running method (Story 2.4 Task 8.2)"""

    def test_is_running_when_no_thread(self):
        """Test is_running when no thread exists"""
        manager = WorkflowManager()

        assert not manager.is_running()

    def test_is_running_when_thread_not_started(self):
        """Test is_running when thread exists but not started"""
        from core.workflow_thread import WorkflowThread

        manager = WorkflowManager()
        manager.workflow_thread = WorkflowThread(
            ProjectConfig(name="Test"),
            WorkflowConfig(id="test", name="Test")
        )

        assert not manager.is_running()

        # Cleanup
        manager.cleanup()

    def test_is_running_when_thread_running(self):
        """Test is_running when thread is running"""
        manager = WorkflowManager()

        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[]
        )

        manager.start_workflow(project_config, workflow_config)

        assert manager.is_running()

        # Cleanup
        if manager.workflow_thread.isRunning():
            manager.workflow_thread.requestInterruption()
            manager.workflow_thread.wait()
        manager.cleanup()


class TestWorkflowManagerGetCurrentExecution:
    """Test get_current_execution method (Story 2.4 Task 8.2)"""

    def test_get_current_execution_when_no_thread(self):
        """Test get_current_execution when no thread exists"""
        manager = WorkflowManager()

        execution = manager.get_current_execution()

        assert execution is None

    def test_get_current_execution_when_thread_exists(self):
        """Test get_current_execution when thread exists"""
        manager = WorkflowManager()

        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[]
        )

        manager.start_workflow(project_config, workflow_config)

        execution = manager.get_current_execution()

        assert execution is not None
        assert execution.project_name == "TestProject"
        assert execution.workflow_id == "test"

        # Cleanup
        if manager.workflow_thread.isRunning():
            manager.workflow_thread.requestInterruption()
            manager.workflow_thread.wait()
        manager.cleanup()


class TestWorkflowManagerCleanup:
    """Test cleanup method (Story 2.4 Task 8.2)"""

    def test_cleanup_clears_thread_reference(self):
        """Test that cleanup clears thread reference"""
        manager = WorkflowManager()

        project_config = ProjectConfig(name="TestProject")
        workflow_config = WorkflowConfig(
            id="test",
            name="Test Workflow",
            stages=[]
        )

        manager.start_workflow(project_config, workflow_config)
        assert manager.workflow_thread is not None

        # Wait for thread to finish naturally or interrupt it
        if manager.workflow_thread.isRunning():
            manager.workflow_thread.requestInterruption()
            manager.workflow_thread.wait()

        manager.cleanup()

        assert manager.workflow_thread is None
        assert manager.current_execution is None

    def test_cleanup_when_no_thread(self):
        """Test cleanup when no thread exists"""
        manager = WorkflowManager()

        # Should not raise error
        manager.cleanup()

        assert manager.workflow_thread is None
        assert manager.current_execution is None
