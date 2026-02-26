#!/usr/bin/env python3
"""测试阶段选择对话框的响应式布局

测试场景：
1. 默认大小显示
2. 小屏幕显示（模拟小屏幕环境）
3. 滚动功能测试
"""

import sys
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from ui.dialogs.workflow_select_dialog import WorkflowSelectDialog
from core.models import WorkflowConfig, StageConfig


class TestWindow(QWidget):
    """测试窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("阶段选择对话框测试")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 测试按钮 1: 默认大小
        btn1 = QPushButton("打开对话框（默认大小）")
        btn1.setMinimumHeight(50)
        btn1.clicked.connect(self.test_default_size)
        layout.addWidget(btn1)

        # 测试按钮 2: 小屏幕模拟
        btn2 = QPushButton("打开对话框（小屏幕 800x600）")
        btn2.setMinimumHeight(50)
        btn2.clicked.connect(self.test_small_screen)
        layout.addWidget(btn2)

        # 测试按钮 3: 超小屏幕模拟
        btn3 = QPushButton("打开对话框（超小屏幕 640x480）")
        btn3.setMinimumHeight(50)
        btn3.clicked.connect(self.test_tiny_screen)
        layout.addWidget(btn3)

        # 测试按钮 4: 加载已有配置
        btn4 = QPushButton("打开对话框（加载已有配置）")
        btn4.setMinimumHeight(50)
        btn4.clicked.connect(self.test_with_config)
        layout.addWidget(btn4)

        layout.addStretch()

        # 应用样式
        self.setStyleSheet("""
            QWidget {
                background-color: #16213e;
                color: #f1f5f9;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1e293b;
                border: 2px solid #334155;
                border-radius: 8px;
                padding: 12px;
                color: #f1f5f9;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #f97316;
            }
            QPushButton:pressed {
                background-color: #0f172a;
            }
        """)

    def test_default_size(self):
        """测试默认大小"""
        dialog = WorkflowSelectDialog(parent=self)
        result = dialog.exec()
        if result == 1:
            print("用户确认选择")
            workflow = dialog.get_selected_workflow()
            print(f"选中的阶段: {[s.name for s in workflow.stages if s.enabled]}")

    def test_small_screen(self):
        """测试小屏幕（800x600）"""
        dialog = WorkflowSelectDialog(parent=self)
        dialog.resize(800, 600)  # 模拟小屏幕分辨率
        result = dialog.exec()
        if result == 1:
            print("用户确认选择（小屏幕）")
            workflow = dialog.get_selected_workflow()
            print(f"选中的阶段: {[s.name for s in workflow.stages if s.enabled]}")

    def test_tiny_screen(self):
        """测试超小屏幕（640x480）"""
        dialog = WorkflowSelectDialog(parent=self)
        dialog.resize(640, 480)  # 模拟超小屏幕分辨率
        result = dialog.exec()
        if result == 1:
            print("用户确认选择（超小屏幕）")
            workflow = dialog.get_selected_workflow()
            print(f"选中的阶段: {[s.name for s in workflow.stages if s.enabled]}")

    def test_with_config(self):
        """测试加载已有配置"""
        # 创建一个已有配置（跳过 MATLAB 生成，从文件处理开始）
        workflow = WorkflowConfig(
            id="test_workflow",
            name="测试工作流",
            description="跳过MATLAB代码生成的测试配置",
            stages=[
                StageConfig(name="matlab_gen", enabled=False, timeout=1800),
                StageConfig(name="file_process", enabled=True, timeout=300),
                StageConfig(name="file_move", enabled=True, timeout=300),
                StageConfig(name="iar_compile", enabled=True, timeout=1200),
                StageConfig(name="a2l_process", enabled=True, timeout=600),
                StageConfig(name="package", enabled=True, timeout=60),
            ],
            estimated_time=10
        )

        dialog = WorkflowSelectDialog(current_workflow=workflow, parent=self)
        result = dialog.exec()
        if result == 1:
            print("用户确认选择（已有配置）")
            new_workflow = dialog.get_selected_workflow()
            print(f"选中的阶段: {[s.name for s in new_workflow.stages if s.enabled]}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
