"""Integration tests for Build History functionality (Story 3.4)

This module contains integration tests for build history functionality.
"""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

from src.core.build_history_manager import BuildHistoryManager, get_history_manager, reset_history_manager
from src.core.build_history_models import (
    BuildRecord,
    BuildFilters,
    BuildStatistics,
    BuildState,
    StageStatus,
    StageExecutionRecord
)


class TestBuildHistoryIntegration(unittest.TestCase):
    """构建历史集成测试"""

    def setUp(self):
        """设置测试环境"""
        # 重置单例
        reset_history_manager()

        # 使用临时目录
        self.temp_dir = tempfile.mkdtemp()

        # 创建测试实例
        self.manager = BuildHistoryManager(max_records=10)

        # 覆盖存储路径
        self.manager._history_file = Path(self.temp_dir) / "test_build_history.json"

    def tearDown(self):
        """清理测试环境"""
        # 清理临时文件
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        # 重置单例
        reset_history_manager()

    def test_full_build_lifecycle(self):
        """测试完整的构建生命周期集成"""
        # 1. 创建构建记录
        record = self.manager.create_build_record(
            project_name="test_project",
            workflow_name="test_workflow",
            workflow_id="test-id",
            config_snapshot={"key": "value"}
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.state, BuildState.RUNNING)
        self.assertEqual(record.progress_percent, 0)

        # 2. 添加阶段执行记录
        stage1 = StageExecutionRecord(
            stage_id=f"{record.build_id}_stage1",
            build_id=record.build_id,
            stage_name="matlab_gen",
            status=StageStatus.COMPLETED,
            start_time=datetime.now() - timedelta(seconds=5),
            end_time=datetime.now(),
            duration=5.0
        )

        stage2 = StageExecutionRecord(
            stage_id=f"{record.build_id}_stage2",
            build_id=record.build_id,
            stage_name="iar_compile",
            status=StageStatus.COMPLETED,
            start_time=datetime.now() - timedelta(seconds=3),
            end_time=datetime.now(),
            duration=3.0
        )

        # 3. 更新构建记录为完成状态
        self.manager.update_build_record(
            record.build_id,
            state=BuildState.COMPLETED,
            end_time=datetime.now(),
            duration=8.0,
            progress_percent=100,
            stage_results=[stage1, stage2],
            output_files=["/path/to/output.hex", "/path/to/output.a2l"]
        )

        # 4. 保存构建记录
        success = self.manager.save_build_record(record.build_id)
        self.assertTrue(success)

        # 5. 查询并验证记录
        saved_record = self.manager.get_record_by_id(record.build_id)
        self.assertIsNotNone(saved_record)
        self.assertEqual(saved_record.state, BuildState.COMPLETED)
        self.assertEqual(saved_record.duration, 8.0)
        self.assertEqual(len(saved_record.stage_results), 2)
        self.assertEqual(len(saved_record.output_files), 2)

        # 6. 验证 stage_results 被正确保存和加载
        self.assertEqual(saved_record.stage_results[0].stage_name, "matlab_gen")
        self.assertEqual(saved_record.stage_results[1].stage_name, "iar_compile")

    def test_multiple_builds_statistics(self):
        """测试多个构建的统计信息集成"""
        # 创建多个不同状态的构建
        for i in range(10):
            record = self.manager.create_build_record(
                project_name=f"project_{i % 3}",  # 3 个不同项目
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )

            if i < 5:
                state = BuildState.COMPLETED
                duration = 10.0 + i
            elif i < 8:
                state = BuildState.FAILED
                duration = 5.0 + i
            else:
                state = BuildState.CANCELLED
                duration = 3.0 + i

            self.manager.update_build_record(
                record.build_id,
                state=state,
                end_time=datetime.now(),
                duration=duration,
                progress_percent=100 if state == BuildState.COMPLETED else 50
            )

        # 保存所有记录
        self.manager.save_history()

        # 获取统计信息
        stats = self.manager.get_statistics()

        # 验证统计信息
        self.assertEqual(stats.total_builds, 10)
        self.assertEqual(stats.successful_builds, 5)
        self.assertEqual(stats.failed_builds, 3)
        self.assertEqual(stats.cancelled_builds, 2)
        self.assertAlmostEqual(stats.success_rate, 50.0)
        self.assertIsNotNone(stats.average_duration)
        self.assertIsNotNone(stats.min_duration)
        self.assertIsNotNone(stats.max_duration)

        # 验证按工作流分组统计
        self.assertEqual(len(stats.builds_per_workflow), 1)
        self.assertEqual(stats.builds_per_workflow["test_workflow"], 10)

    def test_build_comparison_integration(self):
        """测试构建对比功能集成"""
        # 创建两个成功的构建
        record1 = self.manager.create_build_record(
            project_name="project_A",
            workflow_name="workflow_A",
            workflow_id="id_A",
            config_snapshot={}
        )
        self.manager.update_build_record(
            record1.build_id,
            state=BuildState.COMPLETED,
            end_time=datetime.now(),
            duration=10.0,
            stage_results=[
                StageExecutionRecord(
                    stage_id=f"{record1.build_id}_stage1",
                    build_id=record1.build_id,
                    stage_name="matlab_gen",
                    status=StageStatus.COMPLETED,
                    start_time=datetime.now() - timedelta(seconds=5),
                    end_time=datetime.now(),
                    duration=5.0
                )
            ]
        )

        record2 = self.manager.create_build_record(
            project_name="project_A",
            workflow_name="workflow_A",
            workflow_id="id_A",
            config_snapshot={}
        )
        self.manager.update_build_record(
            record2.build_id,
            state=BuildState.COMPLETED,
            end_time=datetime.now(),
            duration=12.0,
            stage_results=[
                StageExecutionRecord(
                    stage_id=f"{record2.build_id}_stage1",
                    build_id=record2.build_id,
                    stage_name="matlab_gen",
                    status=StageStatus.COMPLETED,
                    start_time=datetime.now() - timedelta(seconds=6),
                    end_time=datetime.now(),
                    duration=6.0
                )
            ]
        )

        # 对比两个构建
        comparison = self.manager.compare_records(record1.build_id, record2.build_id)

        # 验证对比结果
        self.assertIn('build_1', comparison)
        self.assertIn('build_2', comparison)
        self.assertIn('performance_diff', comparison)
        self.assertIn('stage_diff', comparison)
        self.assertIn('config_diff', comparison)

        # 验证性能差异
        perf_diff = comparison['performance_diff']
        self.assertIn('duration_diff', perf_diff)
        self.assertAlmostEqual(perf_diff['duration_diff'], 2.0)
        self.assertAlmostEqual(perf_diff['duration_diff_percent'], 20.0)

    def test_filter_and_search_integration(self):
        """测试过滤和搜索功能集成"""
        # 创建不同状态的构建
        for i in range(5):
            record = self.manager.create_build_record(
                project_name="test_project",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )

            if i < 2:
                state = BuildState.COMPLETED
            elif i < 4:
                state = BuildState.FAILED
            else:
                state = BuildState.CANCELLED

            self.manager.update_build_record(
                record.build_id,
                state=state,
                end_time=datetime.now(),
                duration=10.0,
                error_message="Test error" if state == BuildState.FAILED else None
            )

        # 按状态过滤
        completed_filters = BuildFilters(state=BuildState.COMPLETED)
        completed_records = self.manager.query_records(completed_filters)
        self.assertEqual(len(completed_records), 2)

        # 按关键字搜索
        keyword_filters = BuildFilters(keyword="Test error")
        error_records = self.manager.query_records(keyword_filters)
        self.assertGreaterEqual(len(error_records), 2)

    def test_max_records_limit_with_save_load(self):
        """测试最大记录数限制和保存/加载集成"""
        # 创建超过限制的记录
        for i in range(15):
            record = self.manager.create_build_record(
                project_name=f"project_{i}",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )
            self.manager.save_build_record(record.build_id)

        # 验证最多只有 10 条
        self.assertLessEqual(len(self.manager._records), 10)

        # 保存到文件
        self.manager.save_history()

        # 重新加载
        self.manager._records = []
        self.manager.load_history()

        # 验证仍然只有 10 条
        self.assertEqual(len(self.manager._records), 10)

    def test_export_and_import_integration(self):
        """测试导出和导入集成"""
        # 创建一些记录
        for i in range(3):
            record = self.manager.create_build_record(
                project_name=f"project_{i}",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )
            self.manager.save_build_record(record.build_id)

        # 导出记录
        export_path = Path(self.temp_dir) / "exported_history.json"
        success = self.manager.export_records(export_path)
        self.assertTrue(success)
        self.assertTrue(export_path.exists())

        # 创建新的管理器并加载导出的记录
        new_manager = BuildHistoryManager(max_records=100)
        new_manager._history_file = export_path

        # 加载导出的记录
        count = new_manager.load_history()

        # 验证加载的记录数
        self.assertEqual(count, 3)

        # 验证记录内容
        all_records = new_manager.get_all_records()
        self.assertEqual(len(all_records), 3)


if __name__ == '__main__':
    unittest.main()
