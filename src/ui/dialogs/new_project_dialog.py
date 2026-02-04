"""New Project Dialog for MBD_CICDKits.

This module implements the new project configuration dialog
following Architecture Decision 3.1 (PyQt6 UI Patterns).
"""

import logging
import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal

from core.models import ProjectConfig
from core.config import save_config, CONFIG_DIR

logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符

    Args:
        name: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除Windows文件名中的非法字符
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 移除前后空格
    cleaned = cleaned.strip()
    # 限制长度
    return cleaned[:50] if cleaned else "project"


class NewProjectDialog(QDialog):
    """新建项目配置对话框

    遵循 PyQt6 类模式，使用信号槽通信。

    Architecture Decision 3.1:
    - 继承 QDialog
    - 使用 pyqtSignal 进行事件通信
    - 跨线程信号使用 Qt.ConnectionType.QueuedConnection
    """

    # 定义信号：配置保存成功时发射
    config_saved = pyqtSignal(str)  # 参数：配置文件名

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建项目配置")
        self.setMinimumWidth(600)

        # 初始化 UI
        self._init_ui()

    def _init_ui(self):
        """初始化 UI 组件"""
        layout = QVBoxLayout(self)

        # 创建路径输入字段
        self.path_inputs: dict[str, QLineEdit] = {}
        path_fields = [
            ("simulink_path", "Simulink 工程路径"),
            ("matlab_code_path", "MATLAB 代码路径"),
            ("a2l_path", "A2L 文件路径"),
            ("target_path", "目标文件路径"),
            ("iar_project_path", "IAR 工程路径"),
        ]

        for field_key, label_text in path_fields:
            # 创建行布局
            row = QHBoxLayout()

            # 标签
            label = QLabel(f"{label_text}:")
            label.setMinimumWidth(150)
            row.addWidget(label)

            # 输入框
            input_field = QLineEdit()
            row.addWidget(input_field)

            # 浏览按钮
            browse_btn = QPushButton("浏览...")
            browse_btn.clicked.connect(
                lambda checked, key=field_key, inp=input_field: self._browse_folder(
                    key, inp
                )
            )
            row.addWidget(browse_btn)

            layout.addLayout(row)
            self.path_inputs[field_key] = input_field

        # 按钮栏
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _browse_folder(self, field_key: str, input_field: QLineEdit):
        """根据字段类型选择文件或目录

        Args:
            field_key: 字段键名
            input_field: 输入框控件
        """
        if field_key == "iar_project_path":
            # IAR工程是文件，不是目录
            file, _ = QFileDialog.getOpenFileName(
                self, "选择IAR工程文件", "", "IAR工程 (*.eww);;所有文件 (*.*)"
            )
            if file:
                input_field.setText(file)
        else:
            # 其他路径是目录
            folder = QFileDialog.getExistingDirectory(
                self, "选择文件夹", "", QFileDialog.Option.ShowDirsOnly
            )
            if folder:
                input_field.setText(folder)

    def _validate_paths(self) -> list[str]:
        """验证所有路径已填写且存在

        Returns:
            错误列表，空列表表示有效
        """
        # 创建临时配置对象进行验证
        temp_config = ProjectConfig(
            simulink_path=self.path_inputs["simulink_path"].text(),
            matlab_code_path=self.path_inputs["matlab_code_path"].text(),
            a2l_path=self.path_inputs["a2l_path"].text(),
            target_path=self.path_inputs["target_path"].text(),
            iar_project_path=self.path_inputs["iar_project_path"].text(),
        )

        # 复用 ProjectConfig 的验证方法
        errors = temp_config.validate_required_fields()

        # 额外检查路径是否存在
        for field_key, input_field in self.path_inputs.items():
            path_str = input_field.text().strip()
            if path_str:
                path = Path(path_str)
                if not path.exists():
                    errors.append(f"{field_key}: {path_str} 不存在")

        return errors

    def _save_config(self):
        """保存配置"""
        # 验证路径
        errors = self._validate_paths()
        if errors:
            QMessageBox.warning(self, "验证失败", "\n".join(errors))
            return

        # 从路径中提取项目名
        simulink_path = self.path_inputs["simulink_path"].text()
        project_name = Path(simulink_path).name

        # 清理文件名
        filename = sanitize_filename(project_name)
        config_file = CONFIG_DIR / f"{filename}.toml"

        # 检查是否已存在同名配置
        if config_file.exists():
            reply = QMessageBox.question(
                self,
                "配置已存在",
                f"配置 '{filename}' 已存在，是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # 创建配置对象
        config = ProjectConfig(
            name=filename,
            simulink_path=self.path_inputs["simulink_path"].text(),
            matlab_code_path=self.path_inputs["matlab_code_path"].text(),
            a2l_path=self.path_inputs["a2l_path"].text(),
            target_path=self.path_inputs["target_path"].text(),
            iar_project_path=self.path_inputs["iar_project_path"].text(),
        )

        # 保存配置
        if save_config(config, filename):
            logger.info(f"配置已保存: {filename}")
            self.config_saved.emit(filename)
            self.accept()
        else:
            QMessageBox.critical(
                self, "保存失败", "配置保存失败，请查看日志。"
            )
