"""Main application window for MBD_CICDKits.

This module implements the main UI window following Architecture Decision 3.1 (UI Layer).
Provides project selection, configuration display, and build workflow initiation.

Updated with Anthropic Brand Theme (v3.0 - 2026-02-07)
- Anthropic 品牌配色（橙色系）
- Poppins/Lora 字体系统
- 智能 fallback 机制
"""

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QMessageBox, QStatusBar, QDialog, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QAction, QFont, QIcon

from core.config import list_saved_projects, load_config
from utils.errors import ConfigLoadError
from core.models import ProjectConfig, WorkflowConfig
from core.workflow import validate_workflow_config
from ui.dialogs.new_project_dialog import NewProjectDialog
from ui.dialogs.validation_result_dialog import show_validation_result
from ui.styles.industrial_theme import apply_industrial_theme, BrandColors, FontManager

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """MBD_CICDKits 主窗口 - Anthropic 品牌风格

    遵循 PyQt6 类模式，提供项目配置管理和构建工作流入口。

    设计理念：
    - Anthropic 品牌配色系统（橙色系）
    - Poppins/Lora 字体系统（智能 fallback）
    - Glassmorphism 玻璃拟态设计
    - 渐变色彩和流畅动画
    - 卡片式布局和微交互

    Signals:
        project_loaded(str): 当项目配置加载成功时发射
    """

    project_loaded = pyqtSignal(str)  # 参数：项目名称

    def __init__(self, theme: str = "dark", use_brand: bool = True):
        """初始化主窗口

        Args:
            theme: 主题选择，"dark" 或 "light"
            use_brand: 是否使用 Anthropic 品牌配色（默认 True）
        """
        super().__init__()
        self.setWindowTitle("MBD_CICDKits - CI/CD 自动化工具")
        self.setMinimumSize(1000, 750)

        # 主题设置
        self._theme = theme
        self._use_brand = use_brand
        apply_industrial_theme(self, theme, use_brand=use_brand)

        # 当前加载的配置
        self._current_config: ProjectConfig | None = None

        # 初始化 UI
        self._init_ui()
        self._init_actions()
        self._init_menu_bar()

        # 加载项目列表
        self._refresh_project_list()

        logger.info(f"主窗口初始化完成 (主题: {theme})")

    def _init_ui(self):
        """初始化 UI 组件 - 现代化卡片布局"""
        # 创建滚动区域以支持小屏幕
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 中央容器
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(24)
        layout.setContentsMargins(32, 32, 32, 32)

        # ===== 顶部欢迎区域 =====
        layout.addWidget(self._create_welcome_header())

        # ===== 项目选择卡片 =====
        layout.addWidget(self._create_project_card())

        # ===== 配置信息卡片 =====
        layout.addWidget(self._create_config_card())

        # ===== 状态概览卡片 =====
        layout.addWidget(self._create_status_card())

        layout.addStretch()

        # ===== 底部状态栏 =====
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✨ 欢迎使用 MBD_CICDKits | 选择或新建项目开始")

    def _create_welcome_header(self) -> QFrame:
        """创建欢迎头部区域"""
        header = QFrame()
        header.setProperty("elevated", True)

        layout = QVBoxLayout(header)
        layout.setSpacing(8)
        layout.setContentsMargins(28, 24, 28, 24)

        # 主标题
        title = QLabel("MBD_CICDKits")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("Simulink 模型 CI/CD 自动化工具")
        subtitle.setProperty("label", True)
        subtitle.setFont(FontManager.get_body_font(14))
        layout.addWidget(subtitle)

        # 右侧工具按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        # 设置按钮
        settings_btn = QPushButton("⚙ 设置")
        settings_btn.setProperty("icon-btn", True)
        settings_btn.setToolTip("打开设置")
        btn_row.addWidget(settings_btn)

        # 帮助按钮
        help_btn = QPushButton("❓ 帮助")
        help_btn.setProperty("icon-btn", True)
        help_btn.setToolTip("查看帮助文档")
        help_btn.clicked.connect(self._show_about)
        btn_row.addWidget(help_btn)

        layout.addLayout(btn_row)

        return header

    def _create_project_card(self) -> QFrame:
        """创建项目选择卡片"""
        card = QFrame()
        card.setProperty("elevated", True)

        layout = QVBoxLayout(card)
        layout.setSpacing(20)
        layout.setContentsMargins(28, 24, 28, 24)

        # 卡片标题
        title_row = QHBoxLayout()
        title = QLabel("📁 项目管理")
        title.setProperty("subheading", True)
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)

        # 项目选择区域
        select_row = QHBoxLayout()
        select_row.setSpacing(12)

        # 下拉选择框
        self.project_combo = QComboBox()
        self.project_combo.setMinimumHeight(48)
        self.project_combo.addItem("🔽 选择项目...")
        self.project_combo.currentTextChanged.connect(self._on_project_selected)
        select_row.addWidget(self.project_combo, 1)

        # 操作按钮组
        for text, prop, callback in [
            ("➕ 新建", None, self._new_project),
            ("🗑 删除", "danger", self._delete_project),
        ]:
            btn = QPushButton(text)
            if prop:
                btn.setProperty(prop, True)
            if callback:
                btn.clicked.connect(callback)
            btn.setMinimumHeight(48)
            btn.setMinimumWidth(90)
            select_row.addWidget(btn)

        layout.addLayout(select_row)

        # 验证配置按钮
        self.validate_btn = QPushButton("🔍 验证配置")
        self.validate_btn.setMinimumHeight(48)
        self.validate_btn.setEnabled(False)
        self.validate_btn.clicked.connect(self._validate_config)
        layout.addWidget(self.validate_btn)

        # 构建按钮（大号主要按钮）
        self.build_btn = QPushButton("🚀 开始构建")
        self.build_btn.setProperty("primary", True)
        self.build_btn.setMinimumHeight(56)
        self.build_btn.setEnabled(False)
        self.build_btn.clicked.connect(self._start_build)
        layout.addWidget(self.build_btn)

        return card

    def _create_config_card(self) -> QFrame:
        """创建配置信息卡片"""
        card = QFrame()
        card.setProperty("elevated", True)

        layout = QVBoxLayout(card)
        layout.setSpacing(20)
        layout.setContentsMargins(28, 24, 28, 24)

        # 卡片标题
        title = QLabel("⚙️ 配置路径")
        title.setProperty("subheading", True)
        layout.addWidget(title)

        # 路径显示网格
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        # 图标映射
        icons = {
            "simulink_path": "📊",
            "matlab_code_path": "🔬",
            "a2l_path": "📝",
            "target_path": "🎯",
            "iar_project_path": "🔧",
        }

        self.path_labels = {}
        path_fields = [
            ("simulink_path", "Simulink 工程"),
            ("matlab_code_path", "MATLAB 代码"),
            ("a2l_path", "A2L 文件"),
            ("target_path", "目标文件"),
            ("iar_project_path", "IAR 工程"),
        ]

        for i, (field_key, label_text) in enumerate(path_fields):
            # 图标 + 标签
            icon_label = QLabel(f"{icons[field_key]} {label_text}")
            icon_label.setProperty("label", True)
            icon_label.setMinimumWidth(130)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(icon_label, i, 0)

            # 路径显示（只读输入框）
            path_input = QLineEdit()
            path_input.setReadOnly(True)
            path_input.setText("—")
            path_input.setPlaceholderText(f"加载项目后显示...")
            path_input.setMinimumHeight(44)
            grid.addWidget(path_input, i, 1)

            self.path_labels[field_key] = path_input

        layout.addLayout(grid)

        return card

    def _create_status_card(self) -> QFrame:
        """创建状态概览卡片"""
        card = QFrame()
        card.setProperty("elevated", True)

        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 24, 28, 24)

        # 卡片标题
        title = QLabel("📊 状态概览")
        title.setProperty("subheading", True)
        layout.addWidget(title)

        # 环境检测状态
        env_row = QHBoxLayout()
        env_icon = QLabel("🔍")
        env_row.addWidget(env_icon)

        env_label = QLabel("环境检测:")
        env_label.setProperty("label", True)
        env_row.addWidget(env_label)

        self.env_status = QLabel("检测中...")
        self.env_status.setStyleSheet("color: #f59e0b; font-weight: 500;")
        env_row.addWidget(self.env_status)
        env_row.addStretch()
        layout.addLayout(env_row)

        # 最近构建状态
        build_row = QHBoxLayout()
        build_icon = QLabel("🕐")
        build_row.addWidget(build_icon)

        build_label = QLabel("最近构建:")
        build_label.setProperty("label", True)
        build_row.addWidget(build_label)

        self.last_build_label = QLabel("—")
        build_row.addWidget(self.last_build_label)
        build_row.addStretch()
        layout.addLayout(build_row)

        # 项目统计
        stats_row = QHBoxLayout()
        stats_icon = QLabel("📈")
        stats_row.addWidget(stats_icon)

        stats_label = QLabel("已保存项目:")
        stats_label.setProperty("label", True)
        stats_row.addWidget(stats_label)

        self.project_count_label = QLabel("0 个")
        stats_row.addWidget(self.project_count_label)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        return card

    def _init_actions(self):
        """初始化动作"""
        # 新建项目
        self.new_action = QAction("新建项目", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self._new_project)

        # 刷新项目列表
        self.refresh_action = QAction("刷新项目列表", self)
        self.refresh_action.setShortcut("F5")
        self.refresh_action.triggered.connect(self._refresh_project_list)

        # 切换主题
        self.theme_action = QAction("切换主题", self)
        self.theme_action.setShortcut("Ctrl+T")
        self.theme_action.triggered.connect(self._toggle_theme)

        # 退出
        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

    def _init_menu_bar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("📁 文件")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.refresh_action)
        file_menu.addSeparator()
        file_menu.addAction(self.theme_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # 帮助菜单
        help_menu = menubar.addMenu("❓ 帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _toggle_theme(self):
        """切换主题"""
        new_theme = "light" if self._theme == "dark" else "dark"
        self._theme = new_theme
        apply_industrial_theme(self, new_theme, use_brand=self._use_brand)
        self.status_bar.showMessage(f"✨ 已切换到{'浅色' if new_theme == 'light' else '深色'}主题", 3000)
        logger.info(f"主题已切换: {new_theme}")

    def _refresh_project_list(self):
        """刷新项目列表下拉框"""
        self.project_combo.clear()
        self.project_combo.addItem("🔽 选择项目...", None)

        projects = list_saved_projects()
        for project_name in projects:
            self.project_combo.addItem(project_name, project_name)

        # 更新统计
        self.project_count_label.setText(f"{len(projects)} 个")

        if projects:
            self.status_bar.showMessage(f"✅ 已加载 {len(projects)} 个项目")
        else:
            self.status_bar.showMessage("💡 暂无项目，请新建一个项目开始")

    def _on_project_selected(self, project_name: str):
        """项目选择变化时的处理

        Args:
            project_name: 选中的项目名称
        """
        if project_name == "🔽 选择项目...":
            self._clear_display()
            self.status_bar.showMessage("💡 请选择或新建项目")
        else:
            self.status_bar.showMessage(f"📌 已选择: {project_name}")
            # 自动加载项目配置
            self._load_project_to_ui(project_name)

    def _load_project_to_ui(self, project_name: str):
        """加载项目配置到 UI

        Args:
            project_name: 项目名称
        """
        try:
            config = load_config(project_name)
        except ConfigLoadError as e:
            error_msg = str(e)
            suggestions = "\n".join(f"  • {s}" for s in e.suggestions) if e.suggestions else "  • 查看日志获取详细信息"

            QMessageBox.warning(
                self,
                "⚠️ 加载失败",
                f"{error_msg}\n\n"
                f"建议操作:\n{suggestions}"
            )
            self._clear_display()
            return

        # 填充所有路径输入框
        self.path_labels["simulink_path"].setText(config.simulink_path)
        self.path_labels["matlab_code_path"].setText(config.matlab_code_path)
        self.path_labels["a2l_path"].setText(config.a2l_path)
        self.path_labels["target_path"].setText(config.target_path)
        self.path_labels["iar_project_path"].setText(config.iar_project_path)

        # 启用"验证配置"和"开始构建"按钮
        self.validate_btn.setEnabled(True)
        self.build_btn.setEnabled(True)

        # 保存当前配置
        self._current_config = config

        # 显示成功状态消息
        self.status_bar.showMessage(f"✅ 已加载项目: {project_name}")

        # 记录加载操作到日志
        logger.info(f"项目配置已加载: {project_name}")

        # 发射信号
        self.project_loaded.emit(project_name)

    def _clear_display(self):
        """清空所有显示字段"""
        for input_field in self.path_labels.values():
            input_field.clear()

        self.validate_btn.setEnabled(False)
        self.build_btn.setEnabled(False)
        self._current_config = None
        self.last_build_label.setText("—")

    def _new_project(self):
        """打开新建项目对话框"""
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh_project_list()
            logger.info("新建项目成功")

    def _delete_project(self):
        """删除选中的项目"""
        current_data = self.project_combo.currentData()
        if current_data is None:
            QMessageBox.warning(self, "⚠️ 未选择项目", "请先选择要删除的项目。")
            return

        project_name = current_data
        reply = QMessageBox.question(
            self,
            "🗑️ 确认删除",
            f"确定要删除项目 '{project_name}' 吗？\n\n此操作无法撤销！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from core.config import delete_config
            if delete_config(project_name):
                self._refresh_project_list()
                self._clear_display()
                self.status_bar.showMessage(f"🗑️ 已删除项目: {project_name}")
                logger.info(f"项目已删除: {project_name}")
            else:
                QMessageBox.warning(self, "⚠️ 删除失败", f"无法删除项目: {project_name}")

    def _validate_config(self):
        """验证工作流配置（Story 2.3 Task 7）"""
        if not self._current_config:
            QMessageBox.warning(self, "⚠️ 未加载项目", "请先加载一个项目配置。")
            return

        try:
            self.status_bar.showMessage("🔍 正在验证配置...")

            # 获取工作流配置（如果有）
            # 优先使用 custom_params 中的 workflow_config
            workflow_config = None
            if "workflow_config" in self._current_config.custom_params:
                workflow_data = self._current_config.custom_params["workflow_config"]
                workflow_config = WorkflowConfig.from_dict(workflow_data)
            else:
                # 如果没有自定义工作流，创建一个默认的空配置
                workflow_config = WorkflowConfig(
                    id="default",
                    name="默认工作流",
                    description="默认工作流配置",
                    estimated_time=0,
                    stages=[]
                )

            # 执行验证
            result = validate_workflow_config(workflow_config, self._current_config)

            # 显示验证结果
            show_validation_result(result, self)

            # 如果验证失败，禁用构建按钮
            if not result.is_valid:
                self.build_btn.setEnabled(False)
                self.status_bar.showMessage(f"❌ 验证失败: {result.error_count} 个错误")
                logger.warning(f"配置验证失败: {result.error_count} 个错误")
            else:
                self.build_btn.setEnabled(True)
                if result.warning_count > 0:
                    self.status_bar.showMessage(f"✅ 验证通过（有警告）: {result.warning_count} 个警告")
                    logger.info(f"配置验证通过但有警告: {result.warning_count} 个警告")
                else:
                    self.status_bar.showMessage("✅ 验证通过")
                    logger.info("配置验证通过")

        except Exception as e:
            logger.error(f"验证配置时发生错误: {e}")
            QMessageBox.critical(
                self,
                "❌ 验证失败",
                f"验证配置时发生错误:\n\n{str(e)}\n\n"
                "请查看日志获取详细信息。"
            )

    def _start_build(self):
        """开始构建流程"""
        if self._current_config:
            # 在开始构建前自动验证配置（Story 2.3 Task 7.4）
            self.status_bar.showMessage("🔍 开始前验证配置...")

            # 获取工作流配置
            workflow_config = None
            if "workflow_config" in self._current_config.custom_params:
                workflow_data = self._current_config.custom_params["workflow_config"]
                workflow_config = WorkflowConfig.from_dict(workflow_data)
            else:
                workflow_config = WorkflowConfig(
                    id="default",
                    name="默认工作流",
                    description="默认工作流配置",
                    estimated_time=0,
                    stages=[]
                )

            # 执行验证
            result = validate_workflow_config(workflow_config, self._current_config)

            # 如果验证失败，显示错误并阻止构建（Story 2.3 Task 7.5）
            if not result.is_valid:
                show_validation_result(result, self)
                self.build_btn.setEnabled(False)
                self.status_bar.showMessage("❌ 配置验证失败，请修复错误后重试")
                logger.warning(f"构建被阻止: 配置验证失败 ({result.error_count} 个错误)")
                return

            # 验证通过，开始构建流程
            self.build_btn.setEnabled(True)
            self.status_bar.showMessage("🚀 构建流程启动...")
            logger.info("构建流程启动")

            # TODO: 实现实际的构建流程
            QMessageBox.information(
                self,
                "🚀 构建启动",
                f"开始构建项目: {self._current_config.name}\n\n"
                "构建流程将在后续 Epic 中实现。\n\n"
                "包含以下步骤：\n"
                "• MATLAB 代码生成\n"
                "• IAR 工程编译\n"
                "• A2L 文件处理\n"
                "• 最终文件打包"
            )

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 MBD_CICDKits",
            """
            <h2 style='color: #6366f1;'>MBD_CICDKits</h2>
            <p style='color: #cbd5e1; font-size: 14px;'>Simulink 模型 CI/CD 自动化工具</p>

            <p style='color: #94a3b8; margin-top: 16px;'>版本: 0.1.0 (开发中)</p>

            <h3 style='color: #8b5cf6; margin-top: 24px;'>功能特性</h3>
            <ul style='color: #cbd5e1;'>
                <li>📊 项目配置管理</li>
                <li>🔬 MATLAB 代码生成</li>
                <li>🔧 IAR 工程编译</li>
                <li>📝 A2L 文件处理</li>
                <li>📦 自动化打包发布</li>
            </ul>
            """
        )

    def get_current_config(self) -> ProjectConfig | None:
        """获取当前加载的项目配置

        Returns:
            当前 ProjectConfig 对象，如果未加载则返回 None
        """
        return self._current_config
