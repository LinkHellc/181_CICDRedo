"""Validation Result Dialog for MBD_CICDKits.

This module implements the validation result display dialog
following Architecture Decision 3.1 (PyQt6 UI Patterns).

Story 2.3: Display validation results with actionable error messages
"""

import logging
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QWidget,
    QTreeWidgetItem,
    QTreeWidget,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from core.models import ValidationResult, ValidationSeverity, ValidationError
from ui.styles.industrial_theme import FontManager

logger = logging.getLogger(__name__)


class ValidationResultDialog(QDialog):
    """验证结果对话框

    遵循 PyQt6 类模式，显示工作流配置验证结果。

    功能：
    - 显示验证结果摘要（成功/失败，错误数量）
    - 列表显示所有验证错误（按严重级别排序）
    - 显示每个错误的详细信息和修复建议
    - 支持双击错误项查看详细信息

    Architecture Decision 3.1:
    - 继承 QDialog
    - 使用清晰的视觉层次
    - 提供可操作的修复建议（ADR-002）
    """

    def __init__(self, result: ValidationResult, parent=None):
        """初始化对话框

        Args:
            result: 验证结果对象
            parent: 父窗口
        """
        super().__init__(parent)

        self._result = result

        self.setWindowTitle("🔍 配置验证结果")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        # 初始化 UI
        self._init_ui()
        self._display_result()

    def _init_ui(self):
        """初始化 UI 组件"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # ===== 结果摘要区域 =====
        self._summary_card = self._create_summary_card()
        main_layout.addWidget(self._summary_card)

        # ===== 错误列表区域 =====
        error_card = QFrame()
        error_layout = QVBoxLayout(error_card)
        error_layout.setContentsMargins(24, 20, 24, 20)

        # 标题
        title = QLabel("📋 验证详情")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #f1f5f9;")
        error_layout.addWidget(title)

        # 错误树形列表
        self._error_tree = QTreeWidget()
        self._error_tree.setHeaderLabels(["严重级别", "字段", "阶段", "错误消息"])
        self._error_tree.setColumnWidth(0, 100)
        self._error_tree.setColumnWidth(1, 200)
        self._error_tree.setColumnWidth(2, 100)
        self._error_tree.setColumnWidth(3, 350)
        self._error_tree.setAlternatingRowColors(True)
        self._error_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #334155;
            }
            QTreeWidget::item:selected {
                background-color: #6366f1;
            }
            QTreeWidget::header::section {
                background-color: #334155;
                color: #f1f5f9;
                padding: 8px;
                border: none;
                font-weight: 600;
            }
        """)
        self._error_tree.itemDoubleClicked.connect(self._on_item_double_clicked)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidget(self._error_tree)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        error_layout.addWidget(scroll)
        main_layout.addWidget(error_card)

        # ===== 建议信息区域 =====
        suggestion_card = QFrame()
        suggestion_layout = QVBoxLayout(suggestion_card)
        suggestion_layout.setContentsMargins(24, 20, 24, 20)

        suggestion_title = QLabel("💡 修复建议")
        suggestion_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #f1f5f9;")
        suggestion_layout.addWidget(suggestion_title)

        self._suggestion_label = QLabel("选择一个错误项查看详细建议")
        self._suggestion_label.setWordWrap(True)
        self._suggestion_label.setStyleSheet("""
            QLabel {
                background-color: #1e293b;
                color: #e2e8f0;
                padding: 16px;
                border-radius: 8px;
                border: 1px solid #334155;
                font-size: 13px;
            }
        """)
        self._suggestion_label.setMinimumHeight(100)

        suggestion_layout.addWidget(self._suggestion_label)
        main_layout.addWidget(suggestion_card)

        # ===== 按钮区域 =====
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setMinimumSize(120, 44)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #f1f5f9;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:pressed {
                background-color: #1e293b;
            }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        main_layout.addLayout(btn_layout)

    def _create_summary_card(self) -> QFrame:
        """创建结果摘要卡片

        Returns:
            摘要卡片 QFrame
        """
        card = QFrame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)

        # 判断验证是否通过
        if self._result.is_valid:
            # 验证通过
            status_icon = "✅"
            status_text = "验证通过"
            status_color = "#10b981"  # 绿色
            status_desc = "工作流配置有效，可以开始构建"
        else:
            # 验证失败
            status_icon = "❌"
            status_text = "验证失败"
            status_color = "#ef4444"  # 红色
            status_desc = f"发现 {self._result.error_count} 个错误，{self._result.warning_count} 个警告"

        # 状态图标和标题
        title_row = QHBoxLayout()
        icon_label = QLabel(status_icon)
        icon_label.setStyleSheet("font-size: 32px;")
        title_row.addWidget(icon_label)

        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {status_color};")
        title_row.addWidget(status_label)
        title_row.addStretch()

        layout.addLayout(title_row)

        # 状态描述
        desc_label = QLabel(status_desc)
        desc_label.setStyleSheet("font-size: 14px; color: #94a3b8;")
        layout.addWidget(desc_label)

        # 统计信息
        stats_row = QHBoxLayout()
        stats_row.setSpacing(24)

        # 错误数量
        error_icon = QLabel("❌")
        error_text = QLabel(f"{self._result.error_count} 个错误")
        error_text.setStyleSheet(f"color: {status_color}; font-weight: 600; font-size: 16px;")
        stats_row.addWidget(error_icon)
        stats_row.addWidget(error_text)

        # 警告数量
        warning_icon = QLabel("⚠️")
        warning_text = QLabel(f"{self._result.warning_count} 个警告")
        warning_text.setStyleSheet("color: #f59e0b; font-weight: 600; font-size: 16px;")
        stats_row.addWidget(warning_icon)
        stats_row.addWidget(warning_text)

        stats_row.addStretch()
        layout.addLayout(stats_row)

        # 卡片样式
        if self._result.is_valid:
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(16, 185, 129, 0.1);
                    border: 2px solid {status_color};
                    border-radius: 12px;
                }}
            """)
        else:
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(239, 68, 68, 0.1);
                    border: 2px solid {status_color};
                    border-radius: 12px;
                }}
            """)

        return card

    def _display_result(self):
        """显示验证结果"""
        # 按严重级别排序：ERROR > WARNING > INFO
        sorted_errors = sorted(
            self._result.errors,
            key=lambda e: (
                0 if e.severity == ValidationSeverity.ERROR else
                1 if e.severity == ValidationSeverity.WARNING else
                2
            )
        )

        # 添加错误到树形列表
        for error in sorted_errors:
            item = QTreeWidgetItem()

            # 严重级别
            severity_text = self._get_severity_text(error.severity)
            severity_icon = self._get_severity_icon(error.severity)
            item.setText(0, f"{severity_icon} {severity_text}")
            self._style_severity_item(item, error.severity, 0)

            # 字段
            item.setText(1, error.field or "—")

            # 阶段
            item.setText(2, error.stage or "—")

            # 错误消息
            item.setText(3, error.message or "—")

            # 存储错误对象，方便后续使用
            item.setData(0, Qt.ItemDataRole.UserRole, error)

            self._error_tree.addTopLevelItem(item)

        # 如果没有错误
        if not sorted_errors:
            item = QTreeWidgetItem()
            item.setText(0, "")
            item.setText(1, "")
            item.setText(2, "")
            item.setText(3, "✨ 未发现验证错误")
            self._error_tree.addTopLevelItem(item)
            self._suggestion_label.setText("配置验证完全通过，可以开始构建流程！")

    def _get_severity_text(self, severity: ValidationSeverity) -> str:
        """获取严重级别文本

        Args:
            severity: 验证严重级别

        Returns:
            级别文本
        """
        if severity == ValidationSeverity.ERROR:
            return "错误"
        elif severity == ValidationSeverity.WARNING:
            return "警告"
        else:
            return "信息"

    def _get_severity_icon(self, severity: ValidationSeverity) -> str:
        """获取严重级别图标

        Args:
            severity: 验证严重级别

        Returns:
            级别图标
        """
        if severity == ValidationSeverity.ERROR:
            return "❌"
        elif severity == ValidationSeverity.WARNING:
            return "⚠️"
        else:
            return "ℹ️"

    def _style_severity_item(self, item: QTreeWidgetItem, severity: ValidationSeverity, column: int):
        """根据严重级别设置样式

        Args:
            item: 树形列表项
            severity: 验证严重级别
            column: 列索引
        """
        if severity == ValidationSeverity.ERROR:
            item.setForeground(column, Qt.GlobalColor.red)
        elif severity == ValidationSeverity.WARNING:
            item.setForeground(column, Qt.GlobalColor.yellow)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """错误项双击事件处理

        显示错误的详细信息和修复建议。

        Args:
            item: 被双击的树形列表项
            column: 点击的列索引
        """
        # 获取错误对象
        error = item.data(0, Qt.ItemDataRole.UserRole)

        if not error or not isinstance(error, ValidationError):
            return

        # 构建建议文本
        suggestions_html = "<strong>错误消息：</strong><br>"
        suggestions_html += f"{error.message}<br><br>"

        if error.suggestions:
            suggestions_html += "<strong>建议操作：</strong><br>"
            for idx, suggestion in enumerate(error.suggestions, 1):
                suggestions_html += f"{idx}. {suggestion}<br>"
        else:
            suggestions_html += "<strong>建议操作：</strong><br>"
            suggestions_html += "请联系技术支持获取帮助"

        # 更新建议标签
        self._suggestion_label.setText(suggestions_html)


def show_validation_result(result: ValidationResult, parent=None) -> None:
    """显示验证结果对话框

    这是一个便捷函数，用于快速显示验证结果。

    Args:
        result: 验证结果对象
        parent: 父窗口
    """
    dialog = ValidationResultDialog(result, parent)
    dialog.exec()
