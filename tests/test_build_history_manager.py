"""Unit tests for BuildHistoryManager (Story 3.4)

This module contains comprehensive unit tests for the BuildHistoryManager class.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

from src.core.build_history_manager import BuildHistoryManager, get_history_manager, reset_history_manager
from src.core.build_history_models import (
    BuildRecord,
    BuildFilters,
    BuildStatistics,
    BuildState,
    StageStatus
)


class TestBuildHistoryManager(unittest.TestCase):
    """构建历史管理器单元测试"""

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

    def _create_test_record(
        self,
        project_name: str = "test_project",
        workflow_name: str = "test_workflow",
        state: BuildState = BuildState.COMPLETED,
        duration: float = 10.0
    ) -> BuildRecord:
        """创建测试构建记录

        Args:
            project_name: 项目名称
            workflow_name: 工作流名称
            state: 构建状态
            duration: 耗时

        Returns:
            BuildRecord: 测试构建记录
        """
        record = BuildRecord(
            build_id=f"test-{project_name}-{workflow_name}-{state.value}",
            project_name=project_name,
            workflow_name=workflow_name,
            workflow_id="test-workflow-id",
            start_time=datetime.now() - timedelta(seconds=duration),
            end_time=datetime.now(),
            duration=duration,
            state=state,
            progress_percent=100
        )
        return record

    def test_create_build_record(self):
        """测试创建构建记录 (Story 3.4 Task 1)"""
        record = self.manager.create_build_record(
            project_name="test_project",
            workflow_name="test_workflow",
            workflow_id="test-id",
            config_snapshot={"key": "value"}
        )

        self.assertIsNotNone(record)
        self.assertEqual(record.project_name, "test_project")
        self.assertEqual(record.workflow_name, "test_workflow")
        self.assertEqual(record.workflow_id, "test-id")
        self.assertEqual(record.state, BuildState.RUNNING)
        self.assertEqual(record.progress_percent, 0)
        self.assertIsNotNone(record.build_id)

    def test_update_build_record(self):
        """测试更新构建记录 (Story 3.4 Task 2)"""
        # 创建记录
        record = self.manager.create_build_record(
            project_name="test_project",
            workflow_name="test_workflow",
            workflow_id="test-id",
            config_snapshot={}
        )

        # 更新记录
        success = self.manager.update_build_record(
            record.build_id,
            state=BuildState.COMPLETED,
            duration=15.5,
            progress_percent=100,
            error_message=None
        )

        self.assertTrue(success)

        # 验证更新
        updated = self.manager.get_record_by_id(record.build_id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.state, BuildState.COMPLETED)
        self.assertEqual(updated.duration, 15.5)
        self.assertEqual(updated.progress_percent, 100)

    def test_update_nonexistent_record(self):
        """测试更新不存在的记录"""
        success = self.manager.update_build_record(
            "nonexistent-id",
            state=BuildState.COMPLETED
        )
        self.assertFalse(success)

    def test_save_build_record(self):
        """测试保存构建记录 (Story 3.4 Task 3)"""
        # 创建记录
        record = self.manager.create_build_record(
            project_name="test_project",
            workflow_name="test_workflow",
            workflow_id="test-id",
            config_snapshot={}
        )

        # 保存记录
        success = self.manager.save_build_record(record.build_id)
        self.assertTrue(success)

        # 验证文件存在
        self.assertTrue(self.manager._history_file.exists())

        # 重新加载
        self.manager._records = []
        count = self.manager.load_history()

        self.assertEqual(count, 1)

    def test_save_history(self):
        """测试保存所有历史记录 (Story 3.4 Task 4)"""
        # 创建多个记录
        for i in range(5):
            self.manager.create_build_record(
                project_name=f"project_{i}",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )

        # 保存
        success = self.manager.save_history()
        self.assertTrue(success)

        # 重新加载
        self.manager._records = []
        count = self.manager.load_history()

        self.assertEqual(count, 5)

    def test_load_history(self):
        """测试加载历史记录 (Story 3.4 Task 5)"""
        # 创建记录并保存
        for i in range(3):
            record = self.manager.create_build_record(
                project_name=f"project_{i}",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )
            self.manager.save_build_record(record.build_id)

        # 清空并重新加载
        self.manager._records = []
        count = self.manager.load_history()

        self.assertEqual(count, 3)

    def test_load_history_no_file(self):
        """测试加载不存在的文件"""
        self.manager._history_file = Path(self.temp_dir) / "nonexistent.json"
        count = self.manager.load_history()

        self.assertEqual(count, 0)
        self.assertEqual(len(self.manager._records), 0)

    def test_get_record_by_id(self):
        """测试根据 ID 获取记录 (Story 3.4 Task 6)"""
        # 创建记录
        record = self.manager.create_build_record(
            project_name="test_project",
            workflow_name="test_workflow",
            workflow_id="test-id",
            config_snapshot={}
        )

        # 查询记录
        found = self.manager.get_record_by_id(record.build_id)

        self.assertIsNotNone(found)
        self.assertEqual(found.build_id, record.build_id)

    def test_get_record_by_id_not_found(self):
        """测试查询不存在的记录"""
        found = self.manager.get_record_by_id("nonexistent-id")
        self.assertIsNone(found)

    def test_query_records_no_filter(self):
        """测试查询记录（无过滤）(Story 3.4 Task 7)"""
        # 创建多个记录
        for i in range(5):
            self.manager.create_build_record(
                project_name=f"project_{i}",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )

        # 查询所有记录
        records = self.manager.query_records()

        self.assertEqual(len(records), 5)

    def test_query_records_with_filter(self):
        """测试查询记录（带过滤）"""
        # 创建不同项目的记录
        self.manager.create_build_record(
            project_name="project_A",
            workflow_name="workflow_A",
            workflow_id="id_A",
            config_snapshot={}
        )
        self.manager.create_build_record(
            project_name="project_B",
            workflow_name="workflow_B",
            workflow_id="id_B",
            config_snapshot={}
        )

        # 按项目名称过滤
        filters = BuildFilters(project_name="project_A")
        records = self.manager.query_records(filters)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].project_name, "project_A")

    def test_query_records_by_state(self):
        """测试按状态查询"""
        # 创建不同状态的记录
        record1 = self.manager.create_build_record(
            project_name="project_1",
            workflow_name="workflow_1",
            workflow_id="id_1",
            config_snapshot={}
        )
        self.manager.update_build_record(record1.build_id, state=BuildState.COMPLETED)

        record2 = self.manager.create_build_record(
            project_name="project_2",
            workflow_name="workflow_2",
            workflow_id="id_2",
            config_snapshot={}
        )
        self.manager.update_build_record(record2.build_id, state=BuildState.FAILED)

        # 按状态查询
        filters = BuildFilters(state=BuildState.COMPLETED)
        records = self.manager.query_records(filters)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].state, BuildState.COMPLETED)

    def test_get_recent_records(self):
        """测试获取最近的记录 (Story 3.4 Task 8)"""
        # 创建多个记录
        for i in range(10):
            self.manager.create_build_record(
                project_name=f"project_{i}",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )

        # 获取最近的 5 条记录
        recent = self.manager.get_recent_records(limit=5)

        self.assertEqual(len(recent), 5)

    def test_get_statistics(self):
        """测试获取统计信息 (Story 3.4 Task 9)"""
        # 创建不同状态的记录
        for i in range(5):
            record = self.manager.create_build_record(
                project_name="test_project",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )
            if i < 3:
                self.manager.update_build_record(
                    record.build_id,
                    state=BuildState.COMPLETED,
                    duration=10.0 + i
                )
            elif i == 3:
                self.manager.update_build_record(
                    record.build_id,
                    state=BuildState.FAILED,
                    duration=5.0
                )
            else:
                self.manager.update_build_record(
                    record.build_id,
                    state=BuildState.CANCELLED,
                    duration=3.0
                )

        # 获取统计信息
        stats = self.manager.get_statistics()

        self.assertEqual(stats.total_builds, 5)
        self.assertEqual(stats.successful_builds, 3)
        self.assertEqual(stats.failed_builds, 1)
        self.assertEqual(stats.cancelled_builds, 1)
        self.assertAlmostEqual(stats.success_rate, 60.0)
        self.assertIsNotNone(stats.average_duration)

    def test_delete_record(self):
        """测试删除记录 (Story 3.4 Task 10)"""
        # 创建记录
        record = self.manager.create_build_record(
            project_name="test_project",
            workflow_name="test_workflow",
            workflow_id="test-id",
            config_snapshot={}
        )

        # 删除记录
        success = self.manager.delete_record(record.build_id)

        self.assertTrue(success)
        self.assertIsNone(self.manager.get_record_by_id(record.build_id))

    def test_delete_nonexistent_record(self):
        """测试删除不存在的记录"""
        success = self.manager.delete_record("nonexistent-id")
        self.assertFalse(success)

    def test_clear_all_records(self):
        """测试清空所有记录 (Story 3.4 Task 11)"""
        # 创建多个记录
        for i in range(5):
            self.manager.create_build_record(
                project_name=f"project_{i}",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )

        # 清空
        count = self.manager.clear_all_records()

        self.assertEqual(count, 5)
        self.assertEqual(len(self.manager._records), 0)

    def test_compare_records(self):
        """测试对比记录 (Story 3.4 Task 12)"""
        # 创建两个记录
        record1 = self.manager.create_build_record(
            project_name="project_A",
            workflow_name="workflow_A",
            workflow_id="id_A",
            config_snapshot={}
        )
        self.manager.update_build_record(record1.build_id, state=BuildState.COMPLETED, duration=10.0)

        record2 = self.manager.create_build_record(
            project_name="project_A",
            workflow_name="workflow_A",
            workflow_id="id_A",
            config_snapshot={}
        )
        self.manager.update_build_record(record2.build_id, state=BuildState.COMPLETED, duration=12.0)

        # 对比
        comparison = self.manager.compare_records(record1.build_id, record2.build_id)

        self.assertIn('build_1', comparison)
        self.assertIn('build_2', comparison)
        self.assertIn('performance_diff', comparison)
        self.assertIn('duration_diff', comparison['performance_diff'])
        self.assertAlmostEqual(comparison['performance_diff']['duration_diff'], 2.0)

    def test_compare_nonexistent_record(self):
        """测试对比不存在的记录"""
        record = self.manager.create_build_record(
            project_name="test_project",
            workflow_name="test_workflow",
            workflow_id="test-id",
            config_snapshot={}
        )

        with self.assertRaises(ValueError):
            self.manager.compare_records(record.build_id, "nonexistent-id")

    def test_export_records(self):
        """测试导出记录 (Story 3.4 Task 13)"""
        # 创建记录
        self.manager.create_build_record(
            project_name="test_project",
            workflow_name="test_workflow",
            workflow_id="test-id",
            config_snapshot={}
        )

        # 导出
        export_path = Path(self.temp_dir) / "export.json"
        success = self.manager.export_records(export_path)

        self.assertTrue(success)
        self.assertTrue(export_path.exists())

        # 验证导出内容
        with open(export_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)

    def test_max_records_limit(self):
        """测试最大记录数限制"""
        # 创建超过限制的记录
        for i in range(15):  # 创建 15 条记录（限制为 10）
            self.manager.create_build_record(
                project_name=f"project_{i}",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )

        # 保存
        self.manager.save_history()

        # 验证最多只有 10 条
        self.assertLessEqual(len(self.manager._records), 10)

    def test_singleton_pattern(self):
        """测试单例模式 (Story 3.4 Task 14)"""
        # 获取两个实例
        manager1 = get_history_manager()
        manager2 = get_history_manager()

        # 验证是同一个实例
        self.assertIs(manager1, manager2)

    def test_get_all_records(self):
        """测试获取所有记录"""
        # 创建多个记录
        for i in range(5):
            self.manager.create_build_record(
                project_name=f"project_{i}",
                workflow_name="test_workflow",
                workflow_id="test-id",
                config_snapshot={}
            )

        # 获取所有记录
        all_records = self.manager.get_all_records()

        self.assertEqual(len(all_records), 5)

        # 验证返回的是副本
        all_records.clear()
        self.assertEqual(len(self.manager._records), 5)


class TestBuildRecord(unittest.TestCase):
    """构建记录单元测试"""

    def test_to_dict(self):
        """测试转换为字典"""
        record = BuildRecord(
            build_id="test-id",
            project_name="test_project",
            workflow_name="test_workflow",
            workflow_id="test-id",
            start_time=datetime.now(),
            state=BuildState.COMPLETED
        )

        data = record.to_dict()

        self.assertEqual(data['build_id'], "test-id")
        self.assertEqual(data['project_name'], "test_project")
        self.assertEqual(data['state'], BuildState.COMPLETED.value)

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'build_id': 'test-id',
            'project_name': 'test_project',
            'workflow_name': 'test_workflow',
            'workflow_id': 'test-id',
            'start_time': datetime.now().isoformat(),
            'state': BuildState.COMPLETED.value,
            'progress_percent': 100,
            'output_files': [],
            'stage_results': [],
            'config_snapshot': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        record = BuildRecord.from_dict(data)

        self.assertEqual(record.build_id, "test-id")
        self.assertEqual(record.project_name, "test_project")
        self.assertEqual(record.state, BuildState.COMPLETED)


class TestBuildFilters(unittest.TestCase):
    """构建过滤器单元测试"""

    def test_to_dict(self):
        """测试转换为字典"""
        filters = BuildFilters(
            project_name="test_project",
            state=BuildState.COMPLETED
        )

        data = filters.to_dict()

        self.assertEqual(data['project_name'], "test_project")
        self.assertEqual(data['state'], BuildState.COMPLETED.value)

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'project_name': 'test_project',
            'state': BuildState.COMPLETED.value
        }

        filters = BuildFilters.from_dict(data)

        self.assertEqual(filters.project_name, "test_project")
        self.assertEqual(filters.state, BuildState.COMPLETED)


if __name__ == '__main__':
    unittest.main()
