"""Unit tests for BuildProgress data model (Story 2.14)

Tests for BuildProgress dataclass initialization and methods.
"""

import unittest

from src.core.models import BuildProgress, StageStatus


class TestBuildProgress(unittest.TestCase):
    """测试 BuildProgress 数据模型 (Story 2.14 - 任务 1.5, 1.6)"""

    def test_default_initialization(self):
        """测试默认初始化"""
        progress = BuildProgress()

        self.assertEqual(progress.current_stage, "")
        self.assertEqual(progress.total_stages, 0)
        self.assertEqual(progress.completed_stages, 0)
        self.assertEqual(progress.percentage, 0.0)
        self.assertEqual(progress.start_time, 0.0)
        self.assertEqual(progress.elapsed_time, 0.0)
        self.assertEqual(progress.estimated_remaining_time, 0.0)
        self.assertEqual(progress.stage_statuses, {})
        self.assertEqual(progress.stage_errors, {})

    def test_custom_initialization(self):
        """测试自定义初始化"""
        progress = BuildProgress(
            current_stage="file_process",
            total_stages=5,
            completed_stages=2,
            percentage=40.0,
            stage_statuses={
                "matlab_gen": StageStatus.COMPLETED,
                "file_process": StageStatus.RUNNING
            },
            start_time=100.0,
            elapsed_time=60.0,
            estimated_remaining_time=90.0
        )

        self.assertEqual(progress.current_stage, "file_process")
        self.assertEqual(progress.total_stages, 5)
        self.assertEqual(progress.completed_stages, 2)
        self.assertEqual(progress.percentage, 40.0)
        self.assertEqual(progress.start_time, 100.0)
        self.assertEqual(progress.elapsed_time, 60.0)
        self.assertEqual(progress.estimated_remaining_time, 90.0)
        self.assertEqual(len(progress.stage_statuses), 2)
        self.assertEqual(progress.stage_statuses["matlab_gen"], StageStatus.COMPLETED)
        self.assertEqual(progress.stage_statuses["file_process"], StageStatus.RUNNING)

    def test_percentage_calculation(self):
        """测试百分比计算 (Story 2.14 - 任务 1.6)"""
        progress = BuildProgress(
            total_stages=5,
            completed_stages=2
        )

        # 手动计算百分比
        from src.utils.progress import calculate_progress
        progress.percentage = calculate_progress(progress.completed_stages, progress.total_stages)

        self.assertAlmostEqual(progress.percentage, 40.0)

    def test_percentage_calculation_edge_cases(self):
        """测试百分比计算的边界情况"""
        # 0个完成
        progress = BuildProgress(total_stages=5, completed_stages=0)
        from src.utils.progress import calculate_progress
        progress.percentage = calculate_progress(progress.completed_stages, progress.total_stages)
        self.assertEqual(progress.percentage, 0.0)

        # 全部完成
        progress = BuildProgress(total_stages=5, completed_stages=5)
        progress.percentage = calculate_progress(progress.completed_stages, progress.total_stages)
        self.assertEqual(progress.percentage, 100.0)

    def test_stage_statuses_mutability(self):
        """测试 stage_statuses 字典的可变性"""
        progress = BuildProgress()
        progress.stage_statuses["stage1"] = StageStatus.PENDING
        progress.stage_statuses["stage2"] = StageStatus.RUNNING

        self.assertEqual(len(progress.stage_statuses), 2)
        self.assertEqual(progress.stage_statuses["stage1"], StageStatus.PENDING)
        self.assertEqual(progress.stage_statuses["stage2"], StageStatus.RUNNING)

    def test_stage_errors_mutability(self):
        """测试 stage_errors 字典的可变性"""
        progress = BuildProgress()
        progress.stage_errors["stage1"] = "Error: file not found"

        self.assertEqual(len(progress.stage_errors), 1)
        self.assertEqual(progress.stage_errors["stage1"], "Error: file not found")

    def test_to_dict(self):
        """测试 to_dict 方法"""
        progress = BuildProgress(
            current_stage="file_process",
            total_stages=5,
            completed_stages=2,
            percentage=40.0,
            stage_statuses={
                "matlab_gen": StageStatus.COMPLETED,
                "file_process": StageStatus.RUNNING
            },
            stage_errors={"stage1": "error"},
            start_time=100.0,
            elapsed_time=60.0,
            estimated_remaining_time=90.0
        )

        result = progress.to_dict()

        self.assertEqual(result["current_stage"], "file_process")
        self.assertEqual(result["total_stages"], 5)
        self.assertEqual(result["completed_stages"], 2)
        self.assertEqual(result["percentage"], 40.0)
        self.assertEqual(result["start_time"], 100.0)
        self.assertEqual(result["elapsed_time"], 60.0)
        self.assertEqual(result["estimated_remaining_time"], 90.0)

        # 验证 stage_statuses 被转换为字符串
        self.assertEqual(result["stage_statuses"]["matlab_gen"], "completed")
        self.assertEqual(result["stage_statuses"]["file_process"], "running")
        self.assertEqual(result["stage_errors"]["stage1"], "error")

    def test_from_dict(self):
        """测试 from_dict 方法"""
        data = {
            "current_stage": "file_process",
            "total_stages": 5,
            "completed_stages": 2,
            "percentage": 40.0,
            "stage_statuses": {
                "matlab_gen": "completed",
                "file_process": "running"
            },
            "stage_errors": {"stage1": "error"},
            "start_time": 100.0,
            "elapsed_time": 60.0,
            "estimated_remaining_time": 90.0
        }

        progress = BuildProgress.from_dict(data)

        self.assertEqual(progress.current_stage, "file_process")
        self.assertEqual(progress.total_stages, 5)
        self.assertEqual(progress.completed_stages, 2)
        self.assertEqual(progress.percentage, 40.0)

        # 验证 stage_statuses 被转换为枚举
        self.assertEqual(progress.stage_statuses["matlab_gen"], StageStatus.COMPLETED)
        self.assertEqual(progress.stage_statuses["file_process"], StageStatus.RUNNING)
        self.assertEqual(progress.stage_errors["stage1"], "error")

    def test_from_dict_with_unknown_fields(self):
        """测试从包含未知字段的字典创建对象"""
        data = {
            "current_stage": "file_process",
            "total_stages": 5,
            "completed_stages": 2,
            "percentage": 40.0,
            "stage_statuses": {},
            "stage_errors": {},
            "start_time": 100.0,
            "elapsed_time": 60.0,
            "estimated_remaining_time": 90.0,
            "unknown_field": "should_be_ignored"
        }

        progress = BuildProgress.from_dict(data)

        # 未知字段应该被忽略
        self.assertEqual(progress.current_stage, "file_process")
        self.assertFalse(hasattr(progress, "unknown_field"))

    def test_from_dict_without_optional_fields(self):
        """测试从缺少可选字段的字典创建对象"""
        data = {
            "current_stage": "file_process",
            "total_stages": 5
        }

        progress = BuildProgress.from_dict(data)

        self.assertEqual(progress.current_stage, "file_process")
        self.assertEqual(progress.total_stages, 5)
        # 缺失字段使用默认值
        self.assertEqual(progress.completed_stages, 0)
        self.assertEqual(progress.percentage, 0.0)
        self.assertEqual(progress.stage_statuses, {})


if __name__ == '__main__':
    unittest.main()
