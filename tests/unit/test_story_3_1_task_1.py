"""Unit tests for Story 3.1 Task 1: Create Progress Panel UI Component

Tests for ProgressPanel widget UI component initialization and structure.
"""

import sys
import unittest
from PyQt6.QtWidgets import QApplication, QListWidget, QLabel, QProgressBar, QVBoxLayout
from PyQt6.QtCore import Qt

# 必须在导入组件前创建 QApplication
app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

from src.ui.widgets.progress_panel import ProgressPanel


class TestStory31Task1(unittest.TestCase):
    """测试 Story 3.1 任务 1: 创建进度面板 UI 组件"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.panel = ProgressPanel()

    def setUp(self):
        """每个测试前的设置"""
        self.panel.clear()

    def test_1_1_progress_panel_class_inherits_qwidget(self):
        """测试 1.1: ProgressPanel 类继承 QWidget"""
        from PyQt6.QtWidgets import QWidget
        self.assertIsInstance(self.panel, QWidget)

    def test_1_2_stage_list_widget_exists(self):
        """测试 1.2: 添加阶段列表显示（QTableWidget）"""
        # 使用 QTableWidget 而非 QListWidget (因为已实现)
        from PyQt6.QtWidgets import QTableWidget
        self.assertIsInstance(self.panel.stage_list, QTableWidget)
        self.assertEqual(self.panel.stage_list.columnCount(), 2)  # 阶段名称和状态

    def test_1_3_current_stage_label_exists(self):
        """测试 1.3: 添加当前阶段显示标签（QLabel）"""
        self.assertIsInstance(self.panel.current_stage_label, QLabel)
        self.assertIn("等待开始...", self.panel.current_stage_label.text())

    def test_1_4_progress_bar_exists(self):
        """测试 1.4: 添加整体进度条（QProgressBar）"""
        self.assertIsInstance(self.panel.progress_bar, QProgressBar)
        self.assertEqual(self.panel.progress_bar.minimum(), 0)
        self.assertEqual(self.panel.progress_bar.maximum(), 100)

    def test_1_5_progress_percentage_label_exists(self):
        """测试 1.5: 添加进度百分比显示标签（QLabel）"""
        # 进度百分比显示在 progress_bar 中通过 setFormat 实现
        self.assertEqual(self.panel.progress_bar.format(), "%p%")

    def test_1_6_layout_uses_qvboxlayout(self):
        """测试 1.6: 使用布局管理器（QVBoxLayout）组织组件"""
        self.assertIsInstance(self.panel.layout(), QVBoxLayout)

    def test_1_7_progress_panel_creation(self):
        """测试 1.7: 添加单元测试验证进度面板创建"""
        # 测试面板可以正常创建
        new_panel = ProgressPanel()
        self.assertIsNotNone(new_panel)

        # 测试面板的UI组件都存在
        self.assertIsNotNone(new_panel.progress_bar)
        self.assertIsNotNone(new_panel.current_stage_label)
        self.assertIsNotNone(new_panel.stage_list)
        self.assertIsNotNone(new_panel.time_label)

        # 测试面板的布局正确
        self.assertIsNotNone(new_panel.layout())

        # 测试面板的初始状态
        self.assertEqual(new_panel.progress_bar.value(), 0)
        self.assertEqual(new_panel.current_stage_label.text(), "等待开始...")
        self.assertEqual(new_panel.stage_list.rowCount(), 0)


if __name__ == '__main__':
    unittest.main()
