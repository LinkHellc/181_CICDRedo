"""Unit tests for CancelConfirmationDialog (Story 2.15 - Task 5)

This module contains unit tests for the cancel confirmation dialog.
"""

import pytest
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import Qt

from ui.dialogs.cancel_dialog import CancelConfirmationDialog


@pytest.fixture
def app():
    """创建 QApplication 实例（如果不存在）"""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app
    # 不要退出 app，因为其他测试可能需要它


@pytest.fixture
def dialog(app):
    """创建测试用的对话框实例"""
    return CancelConfirmationDialog()


class TestCancelConfirmationDialog:
    """测试取消确认对话框 (Story 2.15 - Task 5.6)"""

    def test_dialog_title(self, dialog):
        """测试对话框标题 (Task 5.2)"""
        assert dialog.windowTitle() == "确认取消构建"

    def test_dialog_text(self, dialog):
        """测试对话框消息 (Task 5.3)"""
        text = dialog.text()
        assert "确定要取消当前构建吗？" in text

    def test_dialog_informative_text(self, dialog):
        """测试对话框详细信息 (Task 5.3)"""
        informative_text = dialog.informativeText()
        assert "未完成的阶段将被终止" in informative_text

    def test_dialog_icon(self, dialog):
        """测试对话框图标 (Task 5.5)"""
        assert dialog.icon() == QMessageBox.Icon.Warning

    def test_dialog_standard_buttons(self, dialog):
        """测试对话框标准按钮 (Task 5.4)"""
        buttons = dialog.standardButtons()

        # 验证有 Yes 和 No 按钮
        assert QMessageBox.StandardButton.Yes in buttons
        assert QMessageBox.StandardButton.No in buttons

    def test_dialog_button_texts(self, dialog):
        """测试按钮文本 (Task 5.4)"""
        yes_button = dialog.button(QMessageBox.StandardButton.Yes)
        no_button = dialog.button(QMessageBox.StandardButton.No)

        # 验证按钮文本是中文
        assert yes_button.text() == "确定"
        assert no_button.text() == "取消"

    def test_dialog_default_button(self, dialog):
        """测试默认按钮 (Task 5.4)"""
        default_button = dialog.defaultButton()

        # 验证默认按钮是 No（防止误操作）
        assert default_button == QMessageBox.StandardButton.No

    def test_dialog_static_method_confirm(self, dialog, monkeypatch):
        """测试便捷方法 confirm()"""
        # Mock exec() 方法，让它返回 Yes
        def mock_exec():
            return QMessageBox.StandardButton.Yes

        monkeypatch.setattr(dialog, 'exec', mock_exec)

        # 使用便捷方法
        result = CancelConfirmationDialog.confirm()

        # 验证返回 True
        assert result is True

    def test_dialog_static_method_confirm_no(self, dialog, monkeypatch):
        """测试便捷方法 confirm() 返回 False"""
        # Mock exec() 方法，让它返回 No
        def mock_exec():
            return QMessageBox.StandardButton.No

        monkeypatch.setattr(dialog, 'exec', mock_exec)

        # 使用便捷方法
        result = CancelConfirmationDialog.confirm()

        # 验证返回 False
        assert result is False

    def test_dialog_with_parent(self, app):
        """测试对话框带父窗口"""
        # 创建一个父窗口
        parent = app.activeWindow() or QWidget()

        # 创建对话框
        dialog = CancelConfirmationDialog(parent)

        # 验证父窗口设置正确
        assert dialog.parent() is parent

    def test_dialog_inheritance(self, dialog):
        """测试对话框继承关系 (Task 5.1)"""
        # 验证继承自 QMessageBox
        assert isinstance(dialog, QMessageBox)

    def test_dialog_creation(self, dialog):
        """测试对话框创建 (Task 5.1)"""
        # 验证对话框成功创建
        assert dialog is not None
        assert isinstance(dialog, CancelConfirmationDialog)

    def test_dialog_attributes(self, dialog):
        """测试对话框所有属性 (Task 5.2-5.5)"""
        # 标题
        assert dialog.windowTitle() == "确认取消构建"

        # 图标
        assert dialog.icon() == QMessageBox.Icon.Warning

        # 按钮
        buttons = dialog.standardButtons()
        assert QMessageBox.StandardButton.Yes in buttons
        assert QMessageBox.StandardButton.No in buttons

        # 按钮文本
        yes_button = dialog.button(QMessageBox.StandardButton.Yes)
        no_button = dialog.button(QMessageBox.StandardButton.No)
        assert yes_button.text() == "确定"
        assert no_button.text() == "取消"

        # 默认按钮
        assert dialog.defaultButton() == QMessageBox.StandardButton.No

    def test_dialog_multiple_instances(self, app):
        """测试创建多个对话框实例"""
        dialog1 = CancelConfirmationDialog()
        dialog2 = CancelConfirmationDialog()

        # 验证两个对话框是独立的实例
        assert dialog1 is not dialog2
        assert isinstance(dialog1, CancelConfirmationDialog)
        assert isinstance(dialog2, CancelConfirmationDialog)
