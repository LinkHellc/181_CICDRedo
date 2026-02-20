"""Unit tests for Story 3.3 Task 1: Design Data Models

Tests for build history data models including BuildRecord, StageExecutionRecord,
OutputFileRecord, and related models.
"""

import sys
import unittest
from datetime import datetime
import json

from src.core.build_history_models import (
    BuildRecord,
    BuildState,
    BuildFilters,
    BuildStatistics,
    StageExecutionRecord,
    StageStatus,
    OutputFileRecord
)


class TestStory33Task1(unittest.TestCase):
    """测试 Story 3.3 任务 1: 设计数据模型"""

    def test_1_1_build_record_creation(self):
        """测试 1.1: 创建 BuildRecord 实例"""
        record = BuildRecord(
            build_id="test-build-001",
            project_name="TestProject",
            workflow_name="StandardBuild",
            workflow_id="workflow-001",
            start_time=datetime.now()
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.build_id, "test-build-001")
        self.assertEqual(record.project_name, "TestProject")
        self.assertEqual(record.workflow_name, "StandardBuild")
        self.assertEqual(record.workflow_id, "workflow-001")
        self.assertEqual(record.state, BuildState.IDLE)
        self.assertEqual(record.progress_percent, 0)

    def test_1_2_build_record_serialization(self):
        """测试 1.2: BuildRecord 序列化"""
        record = BuildRecord(
            build_id="test-build-002",
            project_name="TestProject",
            workflow_name="StandardBuild",
            workflow_id="workflow-001",
            start_time=datetime.now(),
            state=BuildState.COMPLETED,
            progress_percent=100
        )

        # 测试 to_dict
        data = record.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['build_id'], "test-build-002")
        self.assertEqual(data['state'], "completed")
        self.assertIn('start_time', data)

        # 测试 from_dict
        restored = BuildRecord.from_dict(data)
        self.assertEqual(restored.build_id, record.build_id)
        self.assertEqual(restored.project_name, record.project_name)
        self.assertEqual(restored.state, BuildState.COMPLETED)

    def test_1_3_build_record_json(self):
        """测试 1.3: BuildRecord JSON 序列化"""
        record = BuildRecord(
            build_id="test-build-003",
            project_name="TestProject",
            workflow_name="StandardBuild",
            workflow_id="workflow-001",
            start_time=datetime.now()
        )

        # 测试 to_json
        json_str = record.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn('build_id', json_str)
        self.assertIn('TestProject', json_str)

        # 测试 from_json
        restored = BuildRecord.from_json(json_str)
        self.assertEqual(restored.build_id, record.build_id)
        self.assertEqual(restored.project_name, record.project_name)

    def test_1_4_build_record_with_complete_data(self):
        """测试 1.4: BuildRecord 完整数据"""
        now = datetime.now()
        record = BuildRecord(
            build_id="test-build-004",
            project_name="TestProject",
            workflow_name="StandardBuild",
            workflow_id="workflow-001",
            start_time=now,
            end_time=now,
            duration=120.5,
            state=BuildState.COMPLETED,
            progress_percent=100,
            current_stage="package",
            output_files=["file1.hex", "file2.a2l"],
            error_message=None
        )

        self.assertEqual(record.state, BuildState.COMPLETED)
        self.assertEqual(record.duration, 120.5)
        self.assertEqual(record.progress_percent, 100)
        self.assertEqual(len(record.output_files), 2)
        self.assertIsNone(record.error_message)

    def test_1_5_build_record_with_error(self):
        """测试 1.5: BuildRecord 错误状态"""
        record = BuildRecord(
            build_id="test-build-005",
            project_name="TestProject",
            workflow_name="StandardBuild",
            workflow_id="workflow-001",
            start_time=datetime.now(),
            state=BuildState.FAILED,
            progress_percent=50,
            current_stage="iar_compile",
            error_message="Compilation error: undefined reference to 'foo'"
        )

        self.assertEqual(record.state, BuildState.FAILED)
        self.assertEqual(record.progress_percent, 50)
        self.assertIsNotNone(record.error_message)
        self.assertIn("undefined reference", record.error_message)

    def test_1_6_build_state_enums(self):
        """测试 1.6: BuildState 枚举"""
        self.assertEqual(BuildState.IDLE.value, "idle")
        self.assertEqual(BuildState.RUNNING.value, "running")
        self.assertEqual(BuildState.COMPLETED.value, "completed")
        self.assertEqual(BuildState.FAILED.value, "failed")
        self.assertEqual(BuildState.CANCELLED.value, "cancelled")

    def test_1_7_stage_execution_record_creation(self):
        """测试 1.7: 创建 StageExecutionRecord 实例"""
        now = datetime.now()
        record = StageExecutionRecord(
            stage_id="stage-001",
            build_id="test-build-001",
            stage_name="matlab_gen",
            status=StageStatus.COMPLETED,
            start_time=now,
            end_time=now,
            duration=60.0
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.stage_id, "stage-001")
        self.assertEqual(record.stage_name, "matlab_gen")
        self.assertEqual(record.status, StageStatus.COMPLETED)
        self.assertEqual(record.duration, 60.0)

    def test_1_8_stage_execution_record_serialization(self):
        """测试 1.8: StageExecutionRecord 序列化"""
        now = datetime.now()
        record = StageExecutionRecord(
            stage_id="stage-002",
            build_id="test-build-001",
            stage_name="iar_compile",
            status=StageStatus.FAILED,
            start_time=now,
            end_time=now,
            duration=90.0,
            error_message="Compilation failed"
        )

        # 测试 to_dict
        data = record.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['stage_name'], "iar_compile")
        self.assertEqual(data['status'], "failed")
        self.assertIn('error_message', data)

        # 测试 from_dict
        restored = StageExecutionRecord.from_dict(data)
        self.assertEqual(restored.stage_name, record.stage_name)
        self.assertEqual(restored.status, StageStatus.FAILED)

    def test_1_9_stage_status_enums(self):
        """测试 1.9: StageStatus 枚举"""
        self.assertEqual(StageStatus.PENDING.value, "pending")
        self.assertEqual(StageStatus.RUNNING.value, "running")
        self.assertEqual(StageStatus.COMPLETED.value, "completed")
        self.assertEqual(StageStatus.FAILED.value, "failed")
        self.assertEqual(StageStatus.CANCELLED.value, "cancelled")
        self.assertEqual(StageStatus.SKIPPED.value, "skipped")

    def test_1_10_output_file_record_creation(self):
        """测试 1.10: 创建 OutputFileRecord 实例"""
        record = OutputFileRecord(
            file_id="file-001",
            build_id="test-build-001",
            file_type="hex",
            file_path="/path/to/output.hex",
            file_size=1024,
            file_hash="abc123def456",
            created_at=datetime.now()
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.file_id, "file-001")
        self.assertEqual(record.file_type, "hex")
        self.assertEqual(record.file_size, 1024)

    def test_1_11_output_file_record_serialization(self):
        """测试 1.11: OutputFileRecord 序列化"""
        record = OutputFileRecord(
            file_id="file-002",
            build_id="test-build-001",
            file_type="a2l",
            file_path="/path/to/output.a2l",
            file_size=2048,
            file_hash="xyz789abc123",
            created_at=datetime.now()
        )

        # 测试 to_dict
        data = record.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['file_type'], "a2l")
        self.assertEqual(data['file_size'], 2048)

        # 测试 from_dict
        restored = OutputFileRecord.from_dict(data)
        self.assertEqual(restored.file_type, record.file_type)
        self.assertEqual(restored.file_size, record.file_size)

    def test_1_12_build_filters_creation(self):
        """测试 1.12: 创建 BuildFilters 实例"""
        filters = BuildFilters(
            project_name="TestProject",
            workflow_name="StandardBuild",
            state=BuildState.COMPLETED
        )

        self.assertIsNotNone(filters)
        self.assertEqual(filters.project_name, "TestProject")
        self.assertEqual(filters.workflow_name, "StandardBuild")
        self.assertEqual(filters.state, BuildState.COMPLETED)

    def test_1_13_build_filters_serialization(self):
        """测试 1.13: BuildFilters 序列化"""
        filters = BuildFilters(
            project_name="TestProject",
            keyword="error"
        )

        # 测试 to_dict
        data = filters.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['project_name'], "TestProject")
        self.assertEqual(data['keyword'], "error")
        self.assertNotIn('workflow_name', data)
        self.assertNotIn('state', data)

        # 测试 from_dict
        restored = BuildFilters.from_dict(data)
        self.assertEqual(restored.project_name, filters.project_name)
        self.assertEqual(restored.keyword, filters.keyword)

    def test_1_14_build_statistics_creation(self):
        """测试 1.14: 创建 BuildStatistics 实例"""
        stats = BuildStatistics(
            total_builds=100,
            successful_builds=85,
            failed_builds=10,
            cancelled_builds=5,
            success_rate=85.0,
            average_duration=120.0
        )

        self.assertIsNotNone(stats)
        self.assertEqual(stats.total_builds, 100)
        self.assertEqual(stats.successful_builds, 85)
        self.assertEqual(stats.success_rate, 85.0)

    def test_1_15_build_statistics_serialization(self):
        """测试 1.15: BuildStatistics 序列化"""
        stats = BuildStatistics(
            total_builds=100,
            successful_builds=85,
            failed_builds=10,
            cancelled_builds=5,
            success_rate=85.0
        )

        # 测试 to_dict
        data = stats.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['total_builds'], 100)
        self.assertEqual(data['success_rate'], 85.0)

    def test_1_16_build_record_with_stage_results(self):
        """测试 1.16: BuildRecord 包含阶段结果"""
        now = datetime.now()
        stage1 = StageExecutionRecord(
            stage_id="stage-001",
            build_id="test-build-001",
            stage_name="matlab_gen",
            status=StageStatus.COMPLETED,
            start_time=now,
            end_time=now,
            duration=60.0
        )

        stage2 = StageExecutionRecord(
            stage_id="stage-002",
            build_id="test-build-001",
            stage_name="iar_compile",
            status=StageStatus.COMPLETED,
            start_time=now,
            end_time=now,
            duration=90.0
        )

        record = BuildRecord(
            build_id="test-build-001",
            project_name="TestProject",
            workflow_name="StandardBuild",
            workflow_id="workflow-001",
            start_time=now,
            stage_results=[stage1, stage2]
        )

        self.assertEqual(len(record.stage_results), 2)
        self.assertEqual(record.stage_results[0].stage_name, "matlab_gen")
        self.assertEqual(record.stage_results[1].stage_name, "iar_compile")

    def test_1_17_build_record_serialization_with_stages(self):
        """测试 1.17: BuildRecord 序列化包含阶段结果"""
        now = datetime.now()
        stage = StageExecutionRecord(
            stage_id="stage-001",
            build_id="test-build-001",
            stage_name="matlab_gen",
            status=StageStatus.COMPLETED,
            start_time=now,
            end_time=now,
            duration=60.0
        )

        record = BuildRecord(
            build_id="test-build-001",
            project_name="TestProject",
            workflow_name="StandardBuild",
            workflow_id="workflow-001",
            start_time=now,
            stage_results=[stage]
        )

        # 测试 to_dict
        data = record.to_dict()
        self.assertIn('stage_results', data)
        self.assertEqual(len(data['stage_results']), 1)
        self.assertEqual(data['stage_results'][0]['stage_name'], "matlab_gen")

        # 测试 from_dict
        restored = BuildRecord.from_dict(data)
        self.assertEqual(len(restored.stage_results), 1)
        self.assertEqual(restored.stage_results[0].stage_name, "matlab_gen")
        self.assertIsInstance(restored.stage_results[0], StageExecutionRecord)

    def test_1_18_build_filters_with_time_range(self):
        """测试 1.18: BuildFilters 包含时间范围"""
        start = datetime(2026, 2, 1, 0, 0, 0)
        end = datetime(2026, 2, 28, 23, 59, 59)

        filters = BuildFilters(
            start_time=start,
            end_time=end
        )

        # 测试 to_dict
        data = filters.to_dict()
        self.assertIn('start_time', data)
        self.assertIn('end_time', data)

        # 测试 from_dict
        restored = BuildFilters.from_dict(data)
        self.assertEqual(restored.start_time, start)
        self.assertEqual(restored.end_time, end)

    def test_1_19_build_statistics_with_breakdown(self):
        """测试 1.19: BuildStatistics 包含详细统计"""
        stats = BuildStatistics(
            total_builds=100,
            successful_builds=85,
            failed_builds=10,
            cancelled_builds=5,
            success_rate=85.0,
            average_duration=120.0,
            min_duration=60.0,
            max_duration=300.0,
            builds_per_state={
                "completed": 85,
                "failed": 10,
                "cancelled": 5
            },
            builds_per_workflow={
                "StandardBuild": 70,
                "QuickBuild": 30
            }
        )

        self.assertEqual(len(stats.builds_per_state), 3)
        self.assertEqual(stats.builds_per_state["completed"], 85)
        self.assertEqual(stats.builds_per_workflow["StandardBuild"], 70)

    def test_1_20_all_models_json_compatibility(self):
        """测试 1.20: 所有模型的 JSON 兼容性"""
        # 测试所有模型可以序列化为 JSON
        now = datetime.now()

        build_record = BuildRecord(
            build_id="test-001",
            project_name="Test",
            workflow_name="Standard",
            workflow_id="w-001",
            start_time=now
        )

        stage_record = StageExecutionRecord(
            stage_id="s-001",
            build_id="test-001",
            stage_name="test",
            status=StageStatus.COMPLETED,
            start_time=now,
            end_time=now,
            duration=10.0
        )

        file_record = OutputFileRecord(
            file_id="f-001",
            build_id="test-001",
            file_type="hex",
            file_path="/test.hex",
            file_size=100,
            file_hash="abc",
            created_at=now
        )

        filters = BuildFilters(project_name="Test")
        stats = BuildStatistics(total_builds=10, successful_builds=8)

        # 测试所有 to_dict 不抛出异常
        try:
            build_record.to_dict()
            stage_record.to_dict()
            file_record.to_dict()
            filters.to_dict()
            stats.to_dict()
        except Exception as e:
            self.fail(f"to_dict raised exception: {e}")

        # 测试所有 to_json 不抛出异常
        try:
            json.dumps(build_record.to_dict())
            json.dumps(stage_record.to_dict())
            json.dumps(file_record.to_dict())
            json.dumps(filters.to_dict())
            json.dumps(stats.to_dict())
        except Exception as e:
            self.fail(f"json.dumps raised exception: {e}")


if __name__ == '__main__':
    unittest.main()
