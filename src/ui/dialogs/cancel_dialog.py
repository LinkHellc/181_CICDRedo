"""Cancel confirmation dialog for MBD_CICDKits.

This module provides a confirmation dialog for cancelling builds.

Story 2.15 - 任务 5: 创建确认对话框组件
- 创建 CancelConfirmationDialog 类
- 添加标题和消息
- 添加"确定"和"取消"按钮
- 实现警告图标样式

Architecture Decision 3.1:
- 使用 QMessageBox 作为基类
- 提供简洁的 API
"""

from PyQt6.QtWidgets import QMessageBox, QWidget


class CancelConfirmationDialog(QMessageBox):
    """取消构建确认对话框

    Story 2.15 - 任务 5.1-5.5:
    - 继承 QMessageBox
    - 标题："确认取消构建"
    - 消息："确定要取消当前构建吗？未完成的阶段将被终止。"
    - 按钮："确定"和"取消"
    - 样式：警告图标

    Usage:
        >>> dialog = CancelConfirmationDialog(parent)
        >>> result = dialog.exec()
        >>> if result == QMessageBox.StandardButton.Yes:
        ...     # 用户确认取消
        ...     pass
    """

    def __init__(self, parent: QWidget = None):
        """初始化确认对话框

        Args:
            parent: 父窗口（可选）
        """
        super().__init__(parent)

        # 设置标题 (Task 5.2)
        self.setWindowTitle("确认取消构建")

        # 设置消息 (Task 5.3)
        self.setText("确定要取消当前构建吗？")
        self.setInformativeText("未完成的阶段将被终止。")

        # 设置图标 (Task 5.5)
        self.setIcon(QMessageBox.Icon.Warning)

        # 添加按钮 (Task 5.4)
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # 设置默认按钮为"否"（防止误操作）
        self.setDefaultButton(QMessageBox.StandardButton.No)

        # 设置"确定"按钮文本（将 Yes 改为"确定"）
        self.button(QMessageBox.StandardButton.Yes).setText("确定")

        # 设置"取消"按钮文本（将 No 改为"取消"）
        self.button(QMessageBox.StandardButton.No).setText("取消")

    @staticmethod
    def confirm(parent: QWidget = None) -> bool:
        """显示确认对话框并返回用户选择

        这是一个便捷方法，用于快速显示对话框并获取结果。

        Args:
            parent: 父窗口（可选）

        Returns:
            bool: 用户点击"确定"返回 True，点击"取消"返回 False

        Examples:
            >>> if CancelConfirmationDialog.confirm(parent):
            ...     # 用户确认取消
            ...     worker.request_cancellation()
        """
        dialog = CancelConfirmationDialog(parent)
        result = dialog.exec()

        return result == QMessageBox.StandardButton.Yes
