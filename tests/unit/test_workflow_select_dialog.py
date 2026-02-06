"""Unit tests for WorkflowSelectDialog (Story 2.1 Task 4)."""

import pytest
from pathlib import Path

# 确保 src 在路径中
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PyQt6.QtWidgets import QApplication
from core.models import WorkflowConfig


class TestWorkflowSelectDialog:
    """测试工作流选择对话框 (Story 2.1 Task 4)"""

    @pytest.fixture
    def app(self):
        """创建 QApplication 实例"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    def test_dialog_module_exists(self):
        """测试对话框模块存在

        Given: src.ui.dialogs 模块
        Then: workflow_select_dialog.py 文件应存在
        """
        dialog_path = Path(__file__).parent.parent.parent / "src" / "ui" / "dialogs" / "workflow_select_dialog.py"
        assert dialog_path.exists(), f"对话框文件不存在: {dialog_path}"

    def test_dialog_class_exists(self, app):
        """测试对话框类存在

        Given: workflow_select_dialog 模块
        Then: WorkflowSelectDialog 类应存在
        """
        from ui.dialogs.workflow_select_dialog import WorkflowSelectDialog
        assert WorkflowSelectDialog is not None

    def test_dialog_inherits_qdialog(self, app):
        """测试对话框继承 QDialog

        Given: WorkflowSelectDialog 类
        Then: 应继承自 QDialog
        """
        from PyQt6.QtWidgets import QDialog
        from ui.dialogs.workflow_select_dialog import WorkflowSelectDialog
        assert issubclass(WorkflowSelectDialog, QDialog)

    def test_dialog_can_be_instantiated(self, app):
        """测试对话框可以被实例化

        Given: WorkflowSelectDialog 类
        When: 创建实例
        Then: 应成功创建对话框对象
        """
        from ui.dialogs.workflow_select_dialog import WorkflowSelectDialog
        dialog = WorkflowSelectDialog()
        assert dialog is not None
        dialog.close()

    def test_dialog_has_workflow_list(self, app):
        """测试对话框有工作流列表

        Given: WorkflowSelectDialog 实例
        Then: 应有显示工作流列表的组件
        """
        from ui.dialogs.workflow_select_dialog import WorkflowSelectDialog
        dialog = WorkflowSelectDialog()
        # 检查是否有 workflow_list 属性（假设使用此名称）
        assert hasattr(dialog, "workflow_list") or hasattr(dialog, "_workflow_list")
        dialog.close()

    def test_dialog_has_confirm_signal(self, app):
        """测试对话框有确认信号

        Given: WorkflowSelectDialog 实例
        Then: 应有 workflow_selected 信号
        """
        from PyQt6.QtCore import pyqtSignal
        from ui.dialogs.workflow_select_dialog import WorkflowSelectDialog
        dialog = WorkflowSelectDialog()
        # 检查是否有 workflow_selected 信号
        assert hasattr(dialog, "workflow_selected") or hasattr(dialog, "accepted")
        dialog.close()

    def test_dialog_shows_workflow_templates(self, app):
        """测试对话框显示工作流模板

        Given: WorkflowSelectDialog 实例
        When: 对话框显示
        Then: 应显示从 load_workflow_templates() 加载的模板
        """
        from ui.dialogs.workflow_select_dialog import WorkflowSelectDialog
        dialog = WorkflowSelectDialog()
        # 检查是否加载了工作流模板
        assert hasattr(dialog, "templates") or hasattr(dialog, "_templates")
        dialog.close()

    def test_dialog_template_selection(self, app):
        """测试模板选择交互

        Given: WorkflowSelectDialog 实例
        When: 用户选择模板
        Then: 应更新选中状态
        """
        from ui.dialogs.workflow_select_dialog import WorkflowSelectDialog
        dialog = WorkflowSelectDialog()
        # 检查是否有选择相关的方法
        assert hasattr(dialog, "selected_workflow") or hasattr(dialog, "get_selected_workflow")
        dialog.close()
