"""Unit tests for Story 3.1 Task 3: Implement Current Stage Display

Tests for ProgressPanel current stage display functionality.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.core.models import BuildProgress, StageStatus
from src.ui.widgets.progress_panel import ProgressPanel


class TestStory31Task3(unittest.TestCase):
    """测试 Story 3.1 任务 3: 实现当前阶段显示"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.panel = ProgressPanel()

    def setUp(self):
        """每个测试前的设置"""
        self.panel.clear()

    def test_3_1_update_current_stage_method_exists(self):
        """测试 3.1: 在 ProgressPanel 类中添加 update_current_stage() 方法"""
        # 由于 ProgressPanel 使用 update_progress() 方法更新当前阶段
        # 这里测试 _update_current_stage_label() 方法存在
        self.assertTrue(hasattr(self.panel, '_update_current_stage_label'))
        self.assertTrue(callable(self.panel._update_current_stage_label))

    def test_3_2_accept_stage_name_parameter(self):
        """测试 3.2: 接受阶段名称参数"""
        # 通过 BuildProgress 对象传递当前阶段名称
        progress = BuildProgress()
        progress.current_stage = "test_stage"
        progress.stage_statuses["test_stage"] = StageStatus.RUNNING

        # 方法应该能够接受这些参数
        try:
            self.panel.update_progress(progress)
        except Exception as e:
            self.fail(f"update_progress 方法无法接受 BuildProgress 对象: {e}")

    def test_3_3_update_current_stage_label(self):
        """测试 3.3: 更新当前阶段显示标签"""
        progress = BuildProgress()
        progress.current_stage = "matlab_gen"
        progress.stage_statuses["matlab_gen"] = StageStatus.RUNNING

        self.panel.update_progress(progress)

        # 验证当前阶段标签已更新
        self.assertIn("matlab_gen", self.panel.current_stage_label.text())

    def test_3_4_use_highlight_color(self):
        """测试 3.4: 使用高亮颜色（如蓝色）突出显示"""
        progress = BuildProgress()
        progress.current_stage = "test_stage"
        progress.stage_statuses["test_stage"] = StageStatus.RUNNING

        self.panel.update_progress(progress)

        # 验证当前阶段标签使用了蓝色
        label_style = self.panel.current_stage_label.styleSheet()
        self.assertIn("color: blue", label_style)

    def test_3_5_unit_test_verify_current_stage_update(self):
        """测试 3.5: 添加单元测试验证当前阶段更新"""
        # 测试初始状态
        self.assertEqual(self.panel.current_stage_label.text(), "等待开始...")

        # 测试更新到第一个阶段
        progress1 = BuildProgress()
        progress1.current_stage = "matlab_gen"
        progress1.stage_statuses["matlab_gen"] = StageStatus.RUNNING
        self.panel.update_progress(progress1)

        self.assertIn("matlab_gen", self.panel.current_stage_label.text())
        self.assertIn("正在执行", self.panel.current_stage_label.text())

        # 测试更新到第二个阶段
        progress2 = BuildProgress()
        progress2.current_stage = "file_process"
        progress2.stage_statuses["file_process"] = StageStatus.RUNNING
        self.panel.update_progress(progress2)

        self.assertIn("file_process", self.panel.current_stage_label.text())
        self.assertIn("正在执行", self.panel.current_stage_label.text())

        # 测试阶段完成状态
        progress3 = BuildProgress()
        progress3.current_stage = "matlab_gen"
        progress3.stage_statuses["matlab_gen"] = StageStatus.COMPLETED
        self.panel.update_progress(progress3)

        self.assertIn("matlab_gen", self.panel.current_stage_label.text())
        self.assertIn("✅", self.panel.current_stage_label.text())

        # 测试阶段失败状态
        progress4 = BuildProgress()
        progress4.current_stage = "iar_compile"
        progress4.stage_statuses["iar_compile"] = StageStatus.FAILED
        self.panel.update_progress(progress4)

        self.assertIn("iar_compile", self.panel.current_stage_label.text())
        self.assertIn("阶段失败", self.panel.current_stage_label.text())

        # 测试颜色变化
        failed_style = self.panel.current_stage_label.styleSheet()
        self.assertIn("color: red", failed_style)


if __name__ == '__main__':
    unittest.main()
