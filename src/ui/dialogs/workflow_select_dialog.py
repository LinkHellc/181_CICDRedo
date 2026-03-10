"""Workflow Selection Dialog for MBD_CICDKits.

This module implements the workflow/stage selection dialog
following Architecture Decision 3.1 (PyQt6 UI Patterns).

Story 2.1: Select predefined workflow template
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QWidget,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QGroupBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from core.models import WorkflowConfig, StageConfig
from core.config import load_workflow_templates, load_custom_workflow
from ui.styles.industrial_theme import FontManager

logger = logging.getLogger(__name__)


# 阶段定义
STAGE_DEFINITIONS = {
    "matlab_gen": {
        "name": "MATLAB 代码生成",
        "icon": "🔬",
        "description": "调用 MATLAB 生成 Simulink 模型代码",
        "dependencies": []
    },
    "file_process": {
        "name": "文件处理",
        "icon": "⚙️",
        "description": "处理 Cal.c 文件，添加内存区域定义",
        "dependencies": ["matlab_gen"]
    },
    "file_move": {
        "name": "文件复制",
        "icon": "📦",
        "description": "复制代码文件到 IAR 工程目录",
        "dependencies": ["file_process"]
    },
    "iar_compile": {
        "name": "IAR 编译",
        "icon": "🔧",
        "description": "执行 IAR 编译生成 ELF/HEX 文件",
        "dependencies": ["file_move"]
    },
    "a2l_process": {
        "name": "A2L 文件处理",
        "icon": "📝",
        "description": "更新 A2L 变量地址并替换 XCP 头文件",
        "dependencies": ["iar_compile"]
    },
    "package": {
        "name": "打包归档",
        "icon": "🎯",
        "description": "归档 HEX 和 A2L 文件到目标文件夹",
        "dependencies": ["a2l_process"]
    }
}


class WorkflowSelectDialog(QDialog):
    """阶段选择对话框

    允许用户选择要执行的阶段，自动处理依赖关系。
    """

    # 定义信号：工作流选择确认时发射
    workflow_selected = pyqtSignal(WorkflowConfig)

    def __init__(self, current_workflow: WorkflowConfig = None, parent=None):
        """初始化对话框

        Args:
            current_workflow: 当前的工作流配置
            parent: 父窗口
        """
        super().__init__(parent)

        self.setWindowTitle("📋 选择执行阶段")
        self.setMinimumWidth(500)  # 降低最小宽度，适应小屏幕
        self.setMinimumHeight(400)  # 降低最小高度，适应小屏幕
        # 设置初始大小为合理尺寸
        self.resize(650, 550)

        # 应用主题样式
        self.setStyleSheet("""
            QDialog {
                background-color: #16213e;
            }
        """)

        self._current_workflow = current_workflow
        self._stage_checkboxes: dict[str, QCheckBox] = {}

        # 初始化 UI
        self._init_ui()

        # 加载当前配置
        if current_workflow:
            self._load_current_config()

    def _init_ui(self):
        """初始化 UI 组件"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # ===== 标题区域 =====
        title_label = QLabel("📋 选择执行阶段")
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #f1f5f9;")
        main_layout.addWidget(title_label)

        desc_label = QLabel("勾选要执行的阶段，各阶段独立运行")
        desc_label.setStyleSheet("color: #94a3b8; font-size: 13px;")
        main_layout.addWidget(desc_label)

        # ===== 阶段列表区域（添加滚动支持）=====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1e293b;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #64748b;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # 阶段容器
        stages_frame = QFrame()
        stages_frame.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
        """)
        stages_layout = QVBoxLayout(stages_frame)
        stages_layout.setSpacing(8)
        stages_layout.setContentsMargins(16, 16, 16, 16)

        # 创建阶段复选框
        for stage_id, stage_info in STAGE_DEFINITIONS.items():
            # 阶段卡片
            stage_card = QFrame()
            stage_card.setStyleSheet("""
                QFrame {
                    background-color: #0f172a;
                    border-radius: 6px;
                    padding: 8px;
                }
            """)
            card_layout = QVBoxLayout(stage_card)
            card_layout.setSpacing(4)
            card_layout.setContentsMargins(12, 8, 12, 8)

            checkbox = QCheckBox(f"{stage_info['icon']} {stage_info['name']}")
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #f1f5f9;
                    font-size: 14px;
                    font-weight: 600;
                    spacing: 8px;
                    padding: 4px 0;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                    border: 2px solid #475569;
                    background-color: #1e293b;
                }
                QCheckBox::indicator:checked {
                    background-color: #f97316;
                    border-color: #f97316;
                }
                QCheckBox::indicator:hover {
                    border-color: #f97316;
                }
            """)
            checkbox.setToolTip(stage_info['description'])
            checkbox.stateChanged.connect(lambda state, sid=stage_id: self._on_stage_changed(sid, state))

            self._stage_checkboxes[stage_id] = checkbox
            card_layout.addWidget(checkbox)

            # 添加描述标签
            desc = QLabel(f"    {stage_info['description']}")
            desc.setStyleSheet("color: #94a3b8; font-size: 12px; margin-left: 28px; margin-top: 2px;")
            desc.setWordWrap(True)  # 支持文本换行
            card_layout.addWidget(desc)

            stages_layout.addWidget(stage_card)

        # 添加底部弹性空间
        stages_layout.addStretch()

        # 设置滚动区域的内容
        scroll_area.setWidget(stages_frame)

        # 设置滚动区域的最小高度，确保在小屏幕上也能显示部分内容
        scroll_area.setMinimumHeight(300)

        main_layout.addWidget(scroll_area, 1)  # 添加伸展因子

        # ===== 快捷操作按钮 =====
        quick_actions = QHBoxLayout()
        quick_actions.setSpacing(8)

        select_all_btn = QPushButton("✓ 全选")
        select_all_btn.setProperty("secondary", True)
        select_all_btn.setMinimumHeight(36)
        select_all_btn.clicked.connect(self._select_all)
        quick_actions.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("✗ 全不选")
        deselect_all_btn.setProperty("secondary", True)
        deselect_all_btn.setMinimumHeight(36)
        deselect_all_btn.clicked.connect(self._deselect_all)
        quick_actions.addWidget(deselect_all_btn)

        quick_actions.addStretch()

        main_layout.addLayout(quick_actions)

        # ===== 按钮区域 =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        confirm_btn = QPushButton("✓ 确认选择")
        confirm_btn.setProperty("primary", True)
        confirm_btn.setMinimumHeight(44)
        confirm_btn.setMinimumWidth(140)
        confirm_btn.clicked.connect(self._confirm_selection)
        button_layout.addWidget(confirm_btn)

        main_layout.addLayout(button_layout)

    def _load_current_config(self):
        """加载当前配置到复选框"""
        if not self._current_workflow:
            return

        for stage in self._current_workflow.stages:
            if stage.name in self._stage_checkboxes:
                self._stage_checkboxes[stage.name].setChecked(stage.enabled)

    def _on_stage_changed(self, stage_id: str, state: int):
        """处理阶段选择变化

        各阶段独立选择，不级联依赖关系。
        """
        pass

    def _select_all(self):
        """全选所有阶段"""
        for checkbox in self._stage_checkboxes.values():
            checkbox.setChecked(True)

    def _deselect_all(self):
        """取消选择所有阶段"""
        for checkbox in self._stage_checkboxes.values():
            checkbox.setChecked(False)

    def _confirm_selection(self):
        """确认选择"""
        self.accept()

    def get_selected_workflow(self) -> WorkflowConfig:
        """获取选中的工作流配置

        Returns:
            WorkflowConfig: 包含用户选择的阶段配置
        """
        stages = []
        for stage_id, checkbox in self._stage_checkboxes.items():
            stage_config = StageConfig(
                name=stage_id,
                enabled=checkbox.isChecked(),
                timeout=300  # 默认超时
            )
            stages.append(stage_config)

        return WorkflowConfig(
            id="custom_selection",
            name="自定义选择",
            description="用户手动选择的阶段组合",
            stages=stages,
            estimated_time=0
        )
