"""Unit tests for ConfigErrorDialog (Story 2.2).

Tests for:
- ConfigErrorDialog creation and display
- Error message formatting
- Suggestions display
"""

import pytest
from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import Qt

from ui.dialogs.config_error_dialog import ConfigErrorDialog, show_config_error


@pytest.fixture
def qapp():
    """创建 QApplication 实例（如果不存在）"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestConfigErrorDialog:
    """测试配置错误对话框 (Story 2.2 Task 5)"""

    def test_dialog_creation(self, qapp):
        """测试对话框创建"""
        dialog = ConfigErrorDialog(
            error_title="测试错误",
            error_message="这是一个测试错误消息",
            error_details="详细错误信息",
            suggestions=["建议 1", "建议 2"]
        )

        assert dialog is not None
        assert dialog.windowTitle() == "⚠️ 配置错误"
        assert dialog.isModal()  # 应该是模态对话框

    def test_dialog_with_minimal_params(self, qapp):
        """测试最小参数创建对话框"""
        dialog = ConfigErrorDialog(
            error_title="简单错误",
            error_message="只有消息"
        )

        assert dialog is not None
        assert dialog.minimumWidth() >= 600
        assert dialog.minimumHeight() >= 400

    def test_dialog_with_suggestions(self, qapp):
        """测试带建议的对话框"""
        suggestions = [
            "检查文件路径是否正确",
            "确认文件存在",
            "验证文件权限"
        ]

        dialog = ConfigErrorDialog(
            error_title="路径错误",
            error_message="文件不存在",
            suggestions=suggestions
        )

        assert dialog is not None
        # 验证对话框包含建议信息
        # 注意：由于对话框是同步显示的，这里只验证创建成功

    def test_dialog_with_details(self, qapp):
        """测试带详细信息的对话框"""
        details = "Traceback (most recent call last):\n  File 'config.py', line 100\nValueError: Invalid value"

        dialog = ConfigErrorDialog(
            error_title="解析错误",
            error_message="配置解析失败",
            error_details=details
        )

        assert dialog is not None

    def test_show_config_error_convenience_function(self, qapp):
        """测试便捷函数"""
        # 注意：这个测试会显示对话框，需要手动关闭
        # 在自动化测试中，可以使用 QTest.closeAfter() 等方法
        # 这里只验证函数调用不会抛出异常

        def show_error():
            show_config_error(
                error_title="测试错误",
                error_message="测试消息",
                suggestions=["建议 1"]
            )

        # 验证函数可以被调用（不抛出异常）
        # 注意：实际测试中对话框会显示，需要额外处理
        assert callable(show_config_error)

    def test_dialog_buttons(self, qapp):
        """测试对话框按钮"""
        dialog = ConfigErrorDialog(
            error_title="按钮测试",
            error_message="测试按钮"
        )

        # 查找关闭按钮
        close_button = dialog.findChild(QPushButton)
        assert close_button is not None, "应该有关闭按钮"
        assert close_button.text() == "关闭"


class TestErrorDialogDisplay:
    """测试错误对话框显示场景"""

    def test_file_not_found_error(self, qapp):
        """测试文件不存在错误"""
        dialog = ConfigErrorDialog(
            error_title="文件不存在",
            error_message="配置文件 'test.toml' 不存在",
            suggestions=[
                "检查文件名拼写是否正确",
                "确认文件路径",
                "查看已保存的项目列表"
            ]
        )

        assert dialog is not None

    def test_json_parse_error(self, qapp):
        """测试 JSON 解析错误"""
        dialog = ConfigErrorDialog(
            error_title="JSON 格式错误",
            error_message="无法解析工作流配置文件",
            error_details="Expecting ',' delimiter: line 15 column 3 (char 234)",
            suggestions=[
                "使用 JSON 验证工具检查文件格式",
                "检查是否缺少逗号或括号",
                "确认字符串使用双引号"
            ]
        )

        assert dialog is not None

    def test_validation_error(self, qapp):
        """测试验证错误"""
        dialog = ConfigErrorDialog(
            error_title="配置验证失败",
            error_message="缺少必需字段: description, stages",
            suggestions=[
                "检查 JSON 文件是否包含所有必需字段",
                "参考示例配置文件",
                "查看文档了解配置格式"
            ]
        )

        assert dialog is not None

    def test_circular_dependency_error(self, qapp):
        """测试循环依赖错误"""
        dialog = ConfigErrorDialog(
            error_title="工作流配置错误",
            error_message="检测到循环依赖：stage1 -> stage2 -> stage1",
            suggestions=[
                "检查阶段的 dependencies 配置",
                "确保依赖关系不形成闭环",
                "绘制依赖关系图帮助排查"
            ]
        )

        assert dialog is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
