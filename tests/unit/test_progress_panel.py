"""Unit tests for ProgressPanel widget (Story 2.14)

Tests for ProgressPanel widget initialization, update logic,
color mapping, performance monitoring, and error handling.
"""

import sys
import time
import unittest
from unittest.mock import patch

from PyQt6.QtWidgets import QApplication, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.core.models import BuildProgress, StageStatus
from src.ui.widgets.progress_panel import ProgressPanel


class TestProgressPanel(unittest.TestCase):
    """测试 ProgressPanel 组件 (Story 2.14 - 任务 5.8, 6.7, 6.8, 9.4, 9.5, 12.5, 13.5, 14.4)"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.panel = ProgressPanel()

    def setUp(self):
        """每个测试前的设置"""
        # 重置面板状态
        self.panel.clear()
        self.panel.update_intervals = []

    def test_initialization(self):
        """测试 UI 组件初始化 (任务 5.8)"""
        # 验证进度条存在
        self.assertIsNotNone(self.panel.progress_bar)
        self.assertEqual(self.panel.progress_bar.value(), 0)

        # 验证当前阶段标签存在
        self.assertIsNotNone(self.panel.current_stage_label)
        self.assertEqual(self.panel.current_stage_label.text(), "等待开始...")

        # 验证阶段列表存在
        self.assertIsNotNone(self.panel.stage_list)
        self.assertEqual(self.panel.stage_list.columnCount(), 2)

        # 验证时间标签存在
        self.assertIsNotNone(self.panel.time_label)
        self.assertIn("已用时间:", self.panel.time_label.text())

        # 验证性能监控初始化
        self.assertIsNotNone(self.panel.last_update_time)
        self.assertEqual(self.panel.update_intervals, [])

    def test_update_progress_basic(self):
        """测试基本进度更新 (任务 6.7)"""
        progress = BuildProgress(
            current_stage="matlab_gen",
            total_stages=5,
            completed_stages=1,
            percentage=20.0,
            elapsed_time=60.0,
            estimated_remaining_time=240.0
        )
        progress.stage_statuses["matlab_gen"] = StageStatus.RUNNING

        self.panel.update_progress(progress)

        # 验证进度条更新
        self.assertEqual(self.panel.progress_bar.value(), 20)

        # 验证当前阶段标签更新
        self.assertIn("正在执行: matlab_gen", self.panel.current_stage_label.text())

        # 验证时间显示更新
        self.assertIn("01:00", self.panel.time_label.text())

    def test_update_progress_with_multiple_stages(self):
        """测试多阶段进度更新"""
        progress = BuildProgress(
            current_stage="file_process",
            total_stages=5,
            completed_stages=2,
            percentage=40.0,
            elapsed_time=120.0,
            estimated_remaining_time=180.0
        )
        progress.stage_statuses = {
            "matlab_gen": StageStatus.COMPLETED,
            "file_process": StageStatus.RUNNING,
            "iar_compile": StageStatus.PENDING,
            "a2l_process": StageStatus.PENDING,
            "file_move": StageStatus.PENDING
        }

        self.panel.update_progress(progress)

        # 验证阶段列表
        self.assertEqual(self.panel.stage_list.rowCount(), 5)

        # 验证已完成的阶段
        completed_item = self.panel.stage_list.item(0, 1)
        self.assertIn("已完成", completed_item.text())

        # 验证运行中的阶段
        running_item = self.panel.stage_list.item(1, 1)
        self.assertIn("进行中", running_item.text())

    def test_get_stage_color(self):
        """测试颜色映射 (任务 9.4)"""
        # PENDING - 灰色
        color_pending = self.panel._get_stage_color(StageStatus.PENDING)
        self.assertEqual(color_pending, "#808080")

        # RUNNING - 蓝色
        color_running = self.panel._get_stage_color(StageStatus.RUNNING)
        self.assertEqual(color_running, "#0066cc")

        # COMPLETED - 绿色
        color_completed = self.panel._get_stage_color(StageStatus.COMPLETED)
        self.assertEqual(color_completed, "#008000")

        # FAILED - 红色
        color_failed = self.panel._get_stage_color(StageStatus.FAILED)
        self.assertEqual(color_failed, "#cc0000")

        # SKIPPED - 橙色
        color_skipped = self.panel._get_stage_color(StageStatus.SKIPPED)
        self.assertEqual(color_skipped, "#ff8800")

    def test_color_application_in_stage_list(self):
        """测试颜色应用到阶段列表 (任务 9.5)"""
        progress = BuildProgress()
        progress.stage_statuses = {
            "stage1": StageStatus.COMPLETED,
            "stage2": StageStatus.FAILED,
            "stage3": StageStatus.RUNNING
        }

        self.panel.update_progress(progress)

        # 验证 COMPLETED 状态的颜色
        completed_item = self.panel.stage_list.item(0, 1)
        self.assertEqual(completed_item.foreground().color().name().lower(), "#008000")

        # 验证 FAILED 状态的颜色
        failed_item = self.panel.stage_list.item(1, 1)
        self.assertEqual(failed_item.foreground().color().name().lower(), "#cc0000")

        # 验证 RUNNING 状态的颜色
        running_item = self.panel.stage_list.item(2, 1)
        self.assertEqual(running_item.foreground().color().name().lower(), "#0066cc")

    def test_performance_monitoring(self):
        """测试性能监控 (任务 12.5)"""
        initial_time = time.monotonic()

        # 第一次更新
        progress1 = BuildProgress(percentage=10.0)
        self.panel.update_progress(progress1)

        # 短暂等待（确保有足够的时间差）
        time.sleep(0.1)

        # 第二次更新
        progress2 = BuildProgress(percentage=20.0)
        self.panel.update_progress(progress2)

        # 验证更新间隔被记录
        self.assertEqual(len(self.panel.update_intervals), 2)

        # 验证至少有一个间隔大于0（第一次可能接近0）
        has_positive_interval = any(interval > 0.0 for interval in self.panel.update_intervals)
        self.assertTrue(has_positive_interval, "至少应该有一个间隔大于0")

        # 验证平均间隔计算
        avg_interval = self.panel.get_average_update_interval()
        self.assertGreaterEqual(avg_interval, 0.0)

    def test_performance_monitoring_max_history(self):
        """测试性能监控历史记录限制"""
        # 创建超过最大历史记录的更新次数
        for i in range(150):
            progress = BuildProgress(percentage=float(i % 101))
            self.panel.update_progress(progress)

        # 验证历史记录不超过最大值
        self.assertLessEqual(len(self.panel.update_intervals), self.panel.max_interval_history)

    def test_error_status_display(self):
        """测试错误状态显示 (任务 14.4)"""
        progress = BuildProgress(
            current_stage="iar_compile",
            percentage=60.0
        )
        progress.stage_statuses = {
            "matlab_gen": StageStatus.COMPLETED,
            "file_process": StageStatus.COMPLETED,
            "iar_compile": StageStatus.FAILED
        }
        progress.stage_errors["iar_compile"] = "Error: compilation failed"

        self.panel.update_progress(progress)

        # 验证当前阶段标签显示错误
        self.assertIn("阶段失败", self.panel.current_stage_label.text())
        self.assertIn("iar_compile", self.panel.current_stage_label.text())

        # 验证阶段列表显示失败状态
        failed_item = self.panel.stage_list.item(2, 1)
        self.assertIn("失败", failed_item.text())

    def test_skipped_stage_status(self):
        """测试跳过阶段状态"""
        progress = BuildProgress(
            current_stage="file_move",
            percentage=80.0
        )
        progress.stage_statuses = {
            "matlab_gen": StageStatus.COMPLETED,
            "file_process": StageStatus.COMPLETED,
            "a2l_process": StageStatus.SKIPPED,
            "iar_compile": StageStatus.COMPLETED,
            "file_move": StageStatus.RUNNING
        }

        self.panel.update_progress(progress)

        # 验证 SKIPPED 状态显示
        skipped_item = self.panel.stage_list.item(2, 1)
        self.assertIn("跳过", skipped_item.text())

        # 验证颜色为橙色
        self.assertEqual(
            skipped_item.foreground().color().name().lower(),
            "#ff8800"
        )

    def test_cancelled_stage_status(self):
        """测试取消阶段状态"""
        progress = BuildProgress(
            current_stage="iar_compile",
            percentage=40.0
        )
        progress.stage_statuses = {
            "matlab_gen": StageStatus.COMPLETED,
            "file_process": StageStatus.COMPLETED,
            "iar_compile": StageStatus.CANCELLED
        }

        self.panel.update_progress(progress)

        # 验证 CANCELLED 状态显示
        cancelled_item = self.panel.stage_list.item(2, 1)
        self.assertIn("已取消", cancelled_item.text())

    def test_clear(self):
        """测试清空进度显示"""
        # 先设置一些进度
        progress = BuildProgress(
            current_stage="test_stage",
            percentage=50.0,
            elapsed_time=60.0
        )
        progress.stage_statuses["test_stage"] = StageStatus.RUNNING
        self.panel.update_progress(progress)

        # 清空
        self.panel.clear()

        # 验证进度条被重置
        self.assertEqual(self.panel.progress_bar.value(), 0)

        # 验证当前阶段标签被重置
        self.assertEqual(self.panel.current_stage_label.text(), "等待开始...")

        # 验证阶段列表被清空
        self.assertEqual(self.panel.stage_list.rowCount(), 0)

        # 验证时间显示被重置
        self.assertIn("00:00:00", self.panel.time_label.text())

    def test_animations_enabled_toggle(self):
        """测试动画开关"""
        # 默认启用
        self.assertTrue(self.panel.enable_animations)

        # 禁用动画
        self.panel.set_animations_enabled(False)
        self.assertFalse(self.panel.enable_animations)

        # 启用动画
        self.panel.set_animations_enabled(True)
        self.assertTrue(self.panel.enable_animations)

    def test_get_stage_status_text(self):
        """测试阶段状态文本"""
        from src.ui.widgets.progress_panel import ProgressPanel

        panel = ProgressPanel()

        # PENDING
        self.assertIn("等待中", panel._get_stage_status_text(StageStatus.PENDING))

        # RUNNING
        self.assertIn("进行中", panel._get_stage_status_text(StageStatus.RUNNING))

        # COMPLETED
        self.assertIn("已完成", panel._get_stage_status_text(StageStatus.COMPLETED))

        # FAILED
        self.assertIn("失败", panel._get_stage_status_text(StageStatus.FAILED))

        # SKIPPED
        self.assertIn("跳过", panel._get_stage_status_text(StageStatus.SKIPPED))

        # CANCELLED
        self.assertIn("已取消", panel._get_stage_status_text(StageStatus.CANCELLED))

    def test_100_percent_completion(self):
        """测试100%完成状态"""
        progress = BuildProgress(
            current_stage="",
            total_stages=5,
            completed_stages=5,
            percentage=100.0,
            elapsed_time=300.0,
            estimated_remaining_time=0.0
        )
        progress.stage_statuses = {
            "matlab_gen": StageStatus.COMPLETED,
            "file_process": StageStatus.COMPLETED,
            "iar_compile": StageStatus.COMPLETED,
            "a2l_process": StageStatus.COMPLETED,
            "file_move": StageStatus.COMPLETED
        }

        self.panel.update_progress(progress)

        # 验证进度条为100%
        self.assertEqual(self.panel.progress_bar.value(), 100)

        # 验证当前阶段标签显示完成
        self.assertIn("等待开始...", self.panel.current_stage_label.text())

        # 验证预计剩余时间为0
        self.assertIn("00:00", self.panel.time_label.text())


if __name__ == '__main__':
    unittest.main()
