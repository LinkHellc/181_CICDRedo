"""Unit tests for build execution models (Story 2.4 Task 1)

Tests for BuildExecution, BuildState, and StageExecution models.
"""

import pytest
from core.models import (
    BuildState,
    BuildExecution,
    StageExecution
)


class TestBuildState:
    """Test BuildState enum"""

    def test_build_state_enum_values(self):
        """Test that BuildState enum has correct values"""
        assert BuildState.IDLE.value == "idle"
        assert BuildState.RUNNING.value == "running"
        assert BuildState.COMPLETED.value == "completed"
        assert BuildState.FAILED.value == "failed"
        assert BuildState.CANCELLED.value == "cancelled"

    def test_build_state_comparison(self):
        """Test BuildState comparison"""
        assert BuildState.RUNNING == BuildState.RUNNING
        assert BuildState.RUNNING != BuildState.IDLE


class TestStageExecution:
    """Test StageExecution dataclass"""

    def test_stage_execution_defaults(self):
        """Test StageExecution default values (Story 2.4 Task 1.4)"""
        stage = StageExecution()

        assert stage.name == ""
        assert stage.status == BuildState.IDLE
        assert stage.start_time == 0.0
        assert stage.end_time == 0.0
        assert stage.duration == 0.0
        assert stage.error_message == ""
        assert stage.output_files == []

    def test_stage_execution_with_values(self):
        """Test StageExecution with custom values"""
        stage = StageExecution(
            name="matlab_gen",
            status=BuildState.RUNNING,
            start_time=100.0,
            error_message="Test error",
            output_files=["file1.c", "file2.h"]
        )

        assert stage.name == "matlab_gen"
        assert stage.status == BuildState.RUNNING
        assert stage.start_time == 100.0
        assert stage.end_time == 0.0  # Default value
        assert stage.duration == 0.0  # Default value
        assert stage.error_message == "Test error"
        assert stage.output_files == ["file1.c", "file2.h"]

    def test_stage_execution_mutable_default(self):
        """Test that StageExecution has proper mutable defaults (Story 2.4 Task 1.4)"""
        stage1 = StageExecution()
        stage2 = StageExecution()

        # Modify stage1's output_files
        stage1.output_files.append("test.c")

        # stage2 should not be affected
        assert len(stage2.output_files) == 0
        assert len(stage1.output_files) == 1


class TestBuildExecution:
    """Test BuildExecution dataclass"""

    def test_build_execution_defaults(self):
        """Test BuildExecution default values (Story 2.4 Task 1.4)"""
        build = BuildExecution()

        assert build.project_name == ""
        assert build.workflow_id == ""
        assert build.state == BuildState.IDLE
        assert build.start_time == 0.0
        assert build.end_time == 0.0
        assert build.duration == 0.0
        assert build.current_stage == ""
        assert build.progress_percent == 0
        assert build.stages == []
        assert build.error_message == ""

    def test_build_execution_with_values(self):
        """Test BuildExecution with custom values"""
        stage = StageExecution(name="test_stage", status=BuildState.COMPLETED)

        build = BuildExecution(
            project_name="TestProject",
            workflow_id="test_workflow",
            state=BuildState.RUNNING,
            start_time=100.0,
            current_stage="test_stage",
            progress_percent=50,
            stages=[stage]
        )

        assert build.project_name == "TestProject"
        assert build.workflow_id == "test_workflow"
        assert build.state == BuildState.RUNNING
        assert build.start_time == 100.0
        assert build.current_stage == "test_stage"
        assert build.progress_percent == 50
        assert len(build.stages) == 1
        assert build.stages[0].name == "test_stage"

    def test_build_execution_mutable_defaults(self):
        """Test that BuildExecution has proper mutable defaults (Story 2.4 Task 1.4)"""
        build1 = BuildExecution()
        build2 = BuildExecution()

        # Modify build1's stages
        build1.stages.append(StageExecution(name="test"))

        # build2 should not be affected
        assert len(build2.stages) == 0
        assert len(build1.stages) == 1

    def test_build_execution_progress_range(self):
        """Test BuildExecution progress is within valid range"""
        build = BuildExecution(progress_percent=75)

        assert 0 <= build.progress_percent <= 100

        # Test edge cases
        build.progress_percent = 0
        assert build.progress_percent == 0

        build.progress_percent = 100
        assert build.progress_percent == 100
