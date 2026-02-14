"""Unit tests for progress utilities (Story 2.14)

Tests for progress calculation, time estimation, time formatting,
and progress persistence.
"""

import json
import tempfile
import unittest
from pathlib import Path

from src.utils.progress import (
    calculate_progress,
    calculate_time_remaining,
    format_duration,
    save_progress,
    load_progress
)


class TestCalculateProgress(unittest.TestCase):
    """测试 calculate_progress 函数 (Story 2.14 - 任务 3.5, 3.6)"""

    def test_normal_calculation(self):
        """测试正常百分比计算"""
        self.assertAlmostEqual(calculate_progress(2, 5), 40.0)
        self.assertAlmostEqual(calculate_progress(1, 4), 25.0)
        self.assertAlmostEqual(calculate_progress(3, 10), 30.0)

    def test_zero_completed(self):
        """测试0个完成的情况"""
        self.assertEqual(calculate_progress(0, 5), 0.0)

    def test_all_completed(self):
        """测试全部完成的情况"""
        self.assertEqual(calculate_progress(5, 5), 100.0)
        self.assertEqual(calculate_progress(1, 1), 100.0)

    def test_zero_total(self):
        """测试总阶段数为0的边界情况"""
        self.assertEqual(calculate_progress(0, 0), 0.0)
        self.assertEqual(calculate_progress(5, 0), 0.0)

    def test_fractional_progress(self):
        """测试非整数进度"""
        self.assertAlmostEqual(calculate_progress(1, 3), 33.333333, places=5)


class TestCalculateTimeRemaining(unittest.TestCase):
    """测试 calculate_time_remaining 函数 (Story 2.14 - 任务 4.5, 4.6)"""

    def test_normal_estimation(self):
        """测试正常时间估算"""
        # 50% 进度，已用60秒，预计剩余60秒
        self.assertAlmostEqual(calculate_time_remaining(60, 50), 60.0)
        # 75% 进度，已用60秒，预计剩余20秒
        self.assertAlmostEqual(calculate_time_remaining(60, 75), 20.0)
        # 25% 进度，已用60秒，预计剩余180秒
        self.assertAlmostEqual(calculate_time_remaining(60, 25), 180.0)

    def test_zero_percentage(self):
        """测试百分比为0的边界情况"""
        self.assertEqual(calculate_time_remaining(60, 0), 0.0)

    def test_negative_percentage(self):
        """测试百分比为负数的边界情况"""
        self.assertEqual(calculate_time_remaining(60, -10), 0.0)

    def test_completed_percentage(self):
        """测试100%完成的情况"""
        self.assertEqual(calculate_time_remaining(60, 100), 0.0)

    def test_over_100_percentage(self):
        """测试百分比超过100的情况"""
        self.assertEqual(calculate_time_remaining(60, 110), 0.0)


class TestFormatDuration(unittest.TestCase):
    """测试 format_duration 函数 (Story 2.14 - 任务 10.5, 10.6)"""

    def test_seconds_only(self):
        """测试只有秒数的情况"""
        self.assertEqual(format_duration(0), "00:00")
        self.assertEqual(format_duration(5), "00:05")
        self.assertEqual(format_duration(59), "00:59")

    def test_minutes_and_seconds(self):
        """测试分钟和秒数的情况"""
        self.assertEqual(format_duration(60), "01:00")
        self.assertEqual(format_duration(125), "02:05")
        self.assertEqual(format_duration(599), "09:59")

    def test_hours_minutes_seconds(self):
        """测试小时、分钟和秒数的情况"""
        self.assertEqual(format_duration(3600), "01:00:00")
        self.assertEqual(format_duration(3665), "01:01:05")
        self.assertEqual(format_duration(90061), "25:01:01")

    def test_over_24_hours(self):
        """测试超过24小时的情况 (Story 2.14 - 任务 10.4)"""
        self.assertEqual(format_duration(86400), "24:00:00")
        self.assertEqual(format_duration(86461), "24:01:01")
        self.assertEqual(format_duration(25 * 3600 + 61), "25:01:01")

    def test_fractional_seconds(self):
        """测试小数秒数的情况"""
        self.assertEqual(format_duration(0.5), "00:00")
        self.assertEqual(format_duration(59.9), "00:59")
        self.assertEqual(format_duration(60.1), "01:00")


class TestSaveAndLoadProgress(unittest.TestCase):
    """测试进度保存和加载函数 (Story 2.14 - 任务 11.7, 11.8)"""

    def setUp(self):
        """每个测试前的设置"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """每个测试后的清理"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_save_and_load_progress(self):
        """测试进度保存和加载"""
        # 准备测试数据
        progress = {
            "current_stage": "file_process",
            "total_stages": 5,
            "completed_stages": 2,
            "percentage": 40.0,
            "stage_statuses": {
                "matlab_gen": "completed",
                "file_process": "running",
                "iar_compile": "pending"
            },
            "stage_errors": {},
            "start_time": 0.0,
            "elapsed_time": 60.0,
            "estimated_remaining_time": 90.0
        }

        # 保存进度
        saved_file = save_progress(progress, self.temp_dir)
        self.assertIsNotNone(saved_file)
        self.assertTrue(saved_file.exists())

        # 加载进度
        loaded_progress = load_progress(self.temp_dir)
        self.assertIsNotNone(loaded_progress)

        # 验证数据一致性
        self.assertEqual(loaded_progress["current_stage"], progress["current_stage"])
        self.assertEqual(loaded_progress["total_stages"], progress["total_stages"])
        self.assertEqual(loaded_progress["completed_stages"], progress["completed_stages"])
        self.assertEqual(loaded_progress["percentage"], progress["percentage"])
        self.assertEqual(loaded_progress["elapsed_time"], progress["elapsed_time"])

    def test_save_creates_directory(self):
        """测试保存时自动创建目录"""
        nested_dir = self.temp_dir / "nested" / "dir"
        progress = {"test": "data"}

        saved_file = save_progress(progress, nested_dir)
        self.assertIsNotNone(saved_file)
        self.assertTrue(nested_dir.exists())
        self.assertTrue(saved_file.exists())

    def test_load_nonexistent_file(self):
        """测试加载不存在的进度文件"""
        result = load_progress(self.temp_dir)
        self.assertIsNone(result)

    def test_save_empty_progress(self):
        """测试保存空进度"""
        progress = {}
        saved_file = save_progress(progress, self.temp_dir)
        self.assertIsNotNone(saved_file)

        loaded_progress = load_progress(self.temp_dir)
        self.assertEqual(loaded_progress, {})

    def test_save_progress_with_complex_data(self):
        """测试保存包含复杂数据的进度"""
        progress = {
            "current_stage": "test_stage",
            "total_stages": 10,
            "completed_stages": 5,
            "percentage": 50.0,
            "stage_statuses": {
                "stage1": "completed",
                "stage2": "running",
                "stage3": "pending",
                "stage4": "failed",
                "stage5": "skipped"
            },
            "stage_errors": {
                "stage4": "Error: compilation failed"
            },
            "start_time": 100.0,
            "elapsed_time": 300.0,
            "estimated_remaining_time": 300.0
        }

        saved_file = save_progress(progress, self.temp_dir)
        self.assertIsNotNone(saved_file)

        # 验证JSON格式正确
        with open(saved_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            self.assertEqual(loaded["stage_errors"]["stage4"], "Error: compilation failed")


if __name__ == '__main__':
    unittest.main()
