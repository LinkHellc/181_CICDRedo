"""New Project Dialog for MBD_CICDKits.

This module implements the new project configuration dialog
following Architecture Decision 3.1 (PyQt6 UI Patterns).

Updated with Industrial Precision Theme (v4.0 - 2026-02-24)
- 响应式布局优化
- 按钮尺寸适配
- 工业精密美学
"""

import logging
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
    QFrame,
    QGridLayout,
    QScrollArea,
    QWidget,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from core.models import ProjectConfig
from core.config import save_config, config_exists, update_config
from utils.path_utils import sanitize_filename
from utils.path_detector import auto_detect_paths
from ui.styles.industrial_theme import FontManager

logger = logging.getLogger(__name__)


class NewProjectDialog(QDialog):
    """新建项目配置对话框 - 工业精密风格

    设计理念：
    - 响应式布局，按钮不会超出边框
    - 清晰的视觉层次
    - 紧凑但舒适的间距
    - 工业控制面板美学
    """

    config_saved = pyqtSignal(str)
    config_updated = pyqtSignal(str)

    FIELD_ICONS = {
        "name": "📋",
        "simulink_path": "📊",
        "matlab_code_path": "🔬",
        "a2l_path": "📝",
        "target_path": "🎯",
        "iar_project_path": "🔧",
        "a2l_tool_path": "🛠️",
    }

    def __init__(self, parent=None, edit_mode: bool = False):
        super().__init__(parent)
        self._edit_mode = edit_mode
        self._original_project_name = ""

        title = "✏️ 编辑项目配置" if edit_mode else "➕ 新建项目配置"
        self.setWindowTitle(title)

        # 优化窗口尺寸 - 确保按钮不会超出
        self.setMinimumSize(800, 650)
        self.resize(850, 700)

        # 工业精密风格样式
        self.setStyleSheet(self._get_stylesheet())

        self._init_ui()

    def _get_stylesheet(self) -> str:
        """获取工业精密风格样式表"""
        return """
            QDialog {
                background-color: #0f172a;
            }

            QFrame {
                background-color: transparent;
            }

            QFrame#card {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }

            QFrame#fieldCard {
                background-color: rgba(30, 41, 59, 0.5);
                border: 1px solid #334155;
                border-radius: 6px;
            }

            QLabel#title {
                color: #f8fafc;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#desc {
                color: #64748b;
                font-size: 13px;
            }

            QLabel#label {
                color: #cbd5e1;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#hint {
                color: #475569;
                font-size: 11px;
            }

            QLabel#required {
                color: #f97316;
                font-size: 11px;
            }

            QLineEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 10px 14px;
                color: #f1f5f9;
                font-size: 13px;
                selection-background-color: #f97316;
            }

            QLineEdit:hover {
                border-color: #475569;
            }

            QLineEdit:focus {
                border-color: #f97316;
                background-color: #1e293b;
            }

            QLineEdit:read-only {
                background-color: rgba(15, 23, 42, 0.5);
                color: #64748b;
                border-style: dashed;
            }

            QPushButton {
                background-color: #334155;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                color: #e2e8f0;
                font-size: 13px;
                font-weight: 500;
            }

            QPushButton:hover {
                background-color: #475569;
            }

            QPushButton:pressed {
                background-color: #64748b;
            }

            QPushButton#primary {
                background-color: #f97316;
                color: #0f172a;
                font-weight: 600;
            }

            QPushButton#primary:hover {
                background-color: #fb923c;
            }

            QPushButton#primary:pressed {
                background-color: #ea580c;
            }

            QPushButton#browse {
                background-color: #1e40af;
                min-width: 70px;
            }

            QPushButton#browse:hover {
                background-color: #1d4ed8;
            }

            QPushButton#detect {
                background-color: #047857;
                min-width: 36px;
                max-width: 36px;
            }

            QPushButton#detect:hover {
                background-color: #059669;
            }

            QPushButton#detectAll {
                background-color: #7c3aed;
            }

            QPushButton#detectAll:hover {
                background-color: #8b5cf6;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }

            QScrollBar:vertical {
                background-color: #1e293b;
                width: 10px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 5px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #64748b;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """

    def _init_ui(self):
        """初始化 UI - 优化后的响应式布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # ===== 标题区域 =====
        header = self._create_header()
        main_layout.addWidget(header)

        # ===== 表单区域 =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(0, 0, 8, 0)

        # 项目名称
        form_layout.addWidget(self._create_name_field())

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #334155; max-height: 1px;")
        form_layout.addWidget(separator)

        # 路径字段
        path_fields = [
            ("simulink_path", "Simulink 工程路径"),
            ("matlab_code_path", "MATLAB 代码路径"),
            ("a2l_path", "A2L 文件路径"),
            ("target_path", "目标文件路径"),
            ("iar_project_path", "IAR 工程路径"),
            ("a2l_tool_path", "A2L 工具路径"),
        ]

        self.path_inputs: dict[str, QLineEdit] = {}
        for field_key, label_text in path_fields:
            form_layout.addWidget(self._create_path_field(field_key, label_text))

        # 智能检测区域
        form_layout.addWidget(self._create_detect_section())

        form_layout.addStretch()
        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll, 1)

        # ===== 底部按钮 =====
        main_layout.addWidget(self._create_button_bar())

    def _create_header(self) -> QFrame:
        """创建标题区域"""
        header = QFrame()
        header.setObjectName("card")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(6)

        title = QLabel("📋 项目配置")
        title.setObjectName("title")
        header_layout.addWidget(title)

        desc_text = "修改项目配置信息" if self._edit_mode else "填写以下信息创建新的项目配置"
        desc = QLabel(desc_text)
        desc.setObjectName("desc")
        header_layout.addWidget(desc)

        return header

    def _create_name_field(self) -> QFrame:
        """创建项目名称输入字段"""
        card = QFrame()
        card.setObjectName("fieldCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 12, 16, 12)

        # 标签行
        label_row = QHBoxLayout()
        label_row.setSpacing(8)

        icon = QLabel(self.FIELD_ICONS["name"])
        label_row.addWidget(icon)

        label = QLabel("项目名称")
        label.setObjectName("label")
        label_row.addWidget(label)

        label_row.addStretch()

        layout.addLayout(label_row)

        # 输入框 - 编辑模式也可修改
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如：MyProject_2024")
        layout.addWidget(self.name_input)

        # 帮助文本
        help_text = QLabel("💡 项目名称用于标识配置文件，支持中文、英文、数字和下划线")
        help_text.setObjectName("hint")
        layout.addWidget(help_text)

        return card

    def _create_path_field(self, field_key: str, label_text: str) -> QFrame:
        """创建路径输入字段 - 优化按钮布局"""
        card = QFrame()
        card.setObjectName("fieldCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 12, 16, 12)

        # 标签行
        label_row = QHBoxLayout()
        label_row.setSpacing(8)

        icon = QLabel(self.FIELD_ICONS.get(field_key, "📁"))
        label_row.addWidget(icon)

        label = QLabel(label_text)
        label.setObjectName("label")
        label_row.addWidget(label)

        label_row.addStretch()

        required = QLabel("* 必填")
        required.setObjectName("required")
        label_row.addWidget(required)

        layout.addLayout(label_row)

        # 输入和按钮行 - 优化比例
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        # 输入框 - 占据大部分空间
        input_field = QLineEdit()
        input_field.setPlaceholderText(f"点击浏览选择或手动输入路径...")
        input_row.addWidget(input_field, 1)

        # 浏览按钮 - 固定宽度
        browse_btn = QPushButton("📂")
        browse_btn.setObjectName("browse")
        browse_btn.setToolTip("浏览选择路径")
        browse_btn.setFixedWidth(44)
        browse_btn.setFixedHeight(40)
        browse_btn.clicked.connect(
            lambda checked, key=field_key, inp=input_field: self._browse_folder(key, inp)
        )
        input_row.addWidget(browse_btn)

        # 自动检测按钮（仅针对 MATLAB 和 IAR）
        if field_key in ("matlab_code_path", "iar_project_path"):
            detect_key = "matlab" if field_key == "matlab_code_path" else "iar"
            detect_btn = QPushButton("🔍")
            detect_btn.setObjectName("detect")
            detect_btn.setToolTip(f"自动检测{label_text}")
            detect_btn.setFixedHeight(40)
            detect_btn.clicked.connect(
                lambda checked, key=detect_key, inp=input_field: self._auto_detect_single_path(
                    key, inp
                )
            )
            input_row.addWidget(detect_btn)

        layout.addLayout(input_row)

        # 保存引用
        self.path_inputs[field_key] = input_field

        return card

    def _create_detect_section(self) -> QFrame:
        """创建智能检测区域"""
        card = QFrame()
        card.setObjectName("card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)

        # 左侧说明
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        info_title = QLabel("🔧 智能路径检测")
        info_title.setStyleSheet("color: #f8fafc; font-weight: 600; font-size: 13px;")
        info_layout.addWidget(info_title)

        info_desc = QLabel("自动扫描系统中的 MATLAB 和 IAR 安装路径")
        info_desc.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(info_desc)

        layout.addLayout(info_layout)
        layout.addStretch()

        # 检测按钮
        detect_all_btn = QPushButton("🔍 一键检测")
        detect_all_btn.setObjectName("detectAll")
        detect_all_btn.setFixedHeight(38)
        detect_all_btn.clicked.connect(self._auto_detect_all_paths)
        layout.addWidget(detect_all_btn)

        return card

    def _create_button_bar(self) -> QFrame:
        """创建底部按钮栏"""
        bar = QFrame()
        bar.setObjectName("card")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(12)

        layout.addStretch()

        cancel_btn = QPushButton("取 消")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 保存配置")
        save_btn.setObjectName("primary")
        save_btn.setFixedSize(120, 40)
        save_btn.clicked.connect(self._save_config)
        layout.addWidget(save_btn)

        return bar

    def _browse_folder(self, field_key: str, input_field: QLineEdit):
        """浏览选择文件或目录"""
        if field_key == "iar_project_path":
            file, _ = QFileDialog.getOpenFileName(
                self,
                "选择 IAR 工程文件",
                "",
                "IAR 工程文件 (*.eww);;所有文件 (*.*)"
            )
            if file:
                input_field.setText(file)
        elif field_key == "a2l_path":
            # A2L 路径应该是文件
            file, _ = QFileDialog.getOpenFileName(
                self,
                "选择 A2L 文件",
                "",
                "A2L 文件 (*.a2l);;所有文件 (*.*)"
            )
            if file:
                input_field.setText(file)
        else:
            folder = QFileDialog.getExistingDirectory(
                self,
                f"选择文件夹",
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            if folder:
                input_field.setText(folder)

    def _mark_field_validated(self, input_field: QLineEdit, valid: bool):
        """标记字段验证状态"""
        if valid:
            input_field.setStyleSheet(
                "QLineEdit { border-color: #22c55e; background-color: rgba(34, 197, 94, 0.1); }"
            )
        else:
            input_field.setStyleSheet("")

    def set_config(self, config: ProjectConfig):
        """加载现有配置到 UI 字段"""
        self._original_project_name = config.name
        self.name_input.setText(config.name)
        self.path_inputs["simulink_path"].setText(config.simulink_path)
        self.path_inputs["matlab_code_path"].setText(config.matlab_code_path)
        self.path_inputs["a2l_path"].setText(config.a2l_path)
        self.path_inputs["target_path"].setText(config.target_path)
        self.path_inputs["iar_project_path"].setText(config.iar_project_path)
        self.path_inputs["a2l_tool_path"].setText(getattr(config, 'a2l_tool_path', ''))

    def _validate_paths(self) -> list[str]:
        """验证所有路径已填写且存在"""
        errors = []

        # 只验证路径字段，项目名称单独处理
        path_fields = [
            ("simulink_path", "Simulink 工程路径"),
            ("matlab_code_path", "MATLAB 代码路径"),
            ("a2l_path", "A2L 文件路径"),
            ("target_path", "目标文件路径"),
            ("iar_project_path", "IAR 工程路径"),
            ("a2l_tool_path", "A2L 工具路径"),
        ]

        for field_key, field_name in path_fields:
            value = self.path_inputs[field_key].text().strip()
            if not value:
                errors.append(f"{field_name} 不能为空")

        # 检查路径是否存在
        for field_key, input_field in self.path_inputs.items():
            path_str = input_field.text().strip()
            if path_str:
                path = Path(path_str)
                if not path.exists():
                    errors.append(f"{field_key}: 路径不存在 - {path_str}")

        return errors

    def _save_config(self):
        """保存配置"""
        errors = self._validate_paths()
        if errors:
            QMessageBox.warning(
                self,
                "⚠️ 验证失败",
                "以下项目需要修正：\n\n" + "\n".join(f"• {e}" for e in errors)
            )
            return

        # 统一从输入框获取项目名称
        raw_name = self.name_input.text().strip()
        if not raw_name:
            # 如果用户没有输入项目名称，从 Simulink 路径自动提取
            simulink_path = self.path_inputs["simulink_path"].text()
            raw_name = Path(simulink_path).name

        filename = sanitize_filename(raw_name)

        if not filename or filename == "unnamed_project":
            QMessageBox.warning(
                self,
                "⚠️ 无效的项目名称",
                "项目名称不能为空或仅包含非法字符。"
            )
            return

        config = ProjectConfig(
            name=filename,
            simulink_path=self.path_inputs["simulink_path"].text(),
            matlab_code_path=self.path_inputs["matlab_code_path"].text(),
            a2l_path=self.path_inputs["a2l_path"].text(),
            target_path=self.path_inputs["target_path"].text(),
            iar_project_path=self.path_inputs["iar_project_path"].text(),
            a2l_tool_path=self.path_inputs["a2l_tool_path"].text(),
        )

        try:
            if self._edit_mode:
                # 编辑模式：检查是否重命名
                name_changed = (filename != self._original_project_name)

                if name_changed:
                    # 项目名称改变，需要删除旧配置并保存新配置
                    from core.config import delete_config
                    delete_config(self._original_project_name)

                if save_config(config, filename, overwrite=True):
                    QMessageBox.information(self, "✅ 更新成功", f"配置已保存：{filename}")
                    logger.info(f"配置已更新: {filename}")
                    self.config_updated.emit(filename)
                    self.accept()
                else:
                    QMessageBox.critical(self, "❌ 更新失败", "配置保存失败，请查看日志。")
            else:
                if config_exists(filename):
                    reply = QMessageBox.question(
                        self,
                        "📋 配置已存在",
                        f"配置文件 '{filename}' 已存在。\n\n是否覆盖？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return

                if save_config(config, filename, overwrite=True):
                    QMessageBox.information(
                        self,
                        "✅ 保存成功",
                        f"配置已保存：{filename}\n\n您现在可以从主窗口选择此项目。"
                    )
                    logger.info(f"配置已保存: {filename}")
                    self.config_saved.emit(filename)
                    self.accept()
                else:
                    QMessageBox.critical(self, "❌ 保存失败", "配置保存失败，请查看日志。")

        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ 操作失败",
                f"配置{'更新' if self._edit_mode else '保存'}失败：\n\n{str(e)}"
            )

    def _auto_detect_single_path(self, detect_key: str, input_field: QLineEdit):
        """检测单个路径"""
        from utils.path_detector import detect_matlab_installations, detect_iar_installations

        detected_path = None
        if detect_key == "matlab":
            detected_path = detect_matlab_installations()
        elif detect_key == "iar":
            detected_path = detect_iar_installations()

        if detected_path:
            input_field.setText(str(detected_path))
            self._mark_field_validated(input_field, True)
            logger.info(f"自动检测到 {detect_key} 路径: {detected_path}")
        else:
            QMessageBox.information(
                self,
                "🔍 未检测到安装",
                f"未能自动检测到 {'MATLAB' if detect_key == 'matlab' else 'IAR'} 安装。"
            )

    def _auto_detect_all_paths(self):
        """检测所有路径"""
        results = auto_detect_paths()

        detected_count = 0
        if results["matlab"]:
            self.path_inputs["matlab_code_path"].setText(str(results["matlab"]))
            self._mark_field_validated(self.path_inputs["matlab_code_path"], True)
            detected_count += 1

        if results["iar"]:
            self.path_inputs["iar_project_path"].setText(str(results["iar"]))
            self._mark_field_validated(self.path_inputs["iar_project_path"], True)
            detected_count += 1

        if detected_count > 0:
            QMessageBox.information(
                self,
                "✅ 检测完成",
                f"成功检测到 {detected_count} 个工具路径！"
            )
            logger.info(f"自动检测完成，检测到 {detected_count} 个工具路径")
        else:
            QMessageBox.warning(
                self,
                "⚠️ 未检测到安装",
                "未能自动检测到任何工具安装。"
            )
