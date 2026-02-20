"""Build history dialog for MBD_CICDKits.

This module implements the BuildHistoryDialog class which provides:
- Display build history list
- View build details
- Compare two builds
- Export build history

Story 3.4: 构建历史记录和查看
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QSplitter, QTextEdit, QTabWidget, QMessageBox,
    QProgressBar, QFileDialog, QFrame, QGridLayout,
    QHeaderView, QAbstractItemView, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from core.build_history_manager import get_history_manager
from core.build_history_models import BuildRecord, BuildState, StageStatus
from ui.styles.industrial_theme import BrandColors, FontManager

logger = logging.getLogger(__name__)


class BuildHistoryDialog(QDialog):
    """构建历史对话框 (Story 3.4)

    提供构建历史列表、详细信息查看和对比功能。

    Features:
        - 构建历史列表（显示构建 ID、时间、状态、总耗时）
        - 构建详细信息（配置、阶段、日志、产物文件）
        - 构建对比功能
        - 导出历史记录
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """初始化构建历史对话框

        Args:
            parent: 父窗口
        """
        super().__init__(parent)

        self._history_manager = get_history_manager()
        self._selected_builds: List[BuildRecord] = []

        self._init_ui()
        self._load_build_history()

        logger.info("构建历史对话框已打开")

    def _init_ui(self):
        """初始化 UI 组件"""
        self.setWindowTitle("📊 构建历史")
        self.setMinimumSize(1200, 800)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # ===== 顶部工具栏 =====
        main_layout.addWidget(self._create_toolbar())

        # ===== 主内容区域（分割器）=====
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter, 1)

        # 左侧：构建历史列表
        list_widget = self._create_build_list_widget()
        splitter.addWidget(list_widget)

        # 右侧：详细信息视图
        detail_widget = self._create_detail_widget()
        splitter.addWidget(detail_widget)

        # 设置分割器比例
        splitter.setStretchFactor(0, 3)  # 列表占 3/4
        splitter.setStretchFactor(1, 4)  # 详情占 4/7

        # ===== 底部按钮 =====
        main_layout.addWidget(self._create_bottom_buttons())

    def _create_toolbar(self) -> QFrame:
        """创建工具栏"""
        toolbar = QFrame()
        toolbar.setProperty("elevated", True)

        layout = QHBoxLayout(toolbar)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 12, 16, 12)

        # 标题
        title = QLabel("📊 构建历史记录")
        title.setFont(FontManager.get_heading_font(18))
        layout.addWidget(title)

        layout.addStretch()

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self._refresh_history)
        layout.addWidget(refresh_btn)

        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空历史")
        clear_btn.setProperty("danger", True)
        clear_btn.clicked.connect(self._clear_all_history)
        layout.addWidget(clear_btn)

        # 导出按钮
        export_btn = QPushButton("📤 导出")
        export_btn.clicked.connect(self._export_history)
        layout.addWidget(export_btn)

        return toolbar

    def _create_build_list_widget(self) -> QWidget:
        """创建构建历史列表控件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标签
        label = QLabel("构建列表")
        label.setProperty("subheading", True)
        layout.addWidget(label)

        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 搜索:"))
        self.search_input = QLabel()
        # self.search_input = QLineEdit()
        # self.search_input.setPlaceholderText("输入关键字搜索...")
        # self.search_input.textChanged.connect(self._filter_builds)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # 构建历史表格
        self.build_table = QTableWidget()
        self.build_table.setColumnCount(5)
        self.build_table.setHorizontalHeaderLabels([
            "构建 ID", "时间", "状态", "耗时", "选择"
        ])
        self.build_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.build_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.build_table.setSortingEnabled(True)
        self.build_table.setAlternatingRowColors(True)
        self.build_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.build_table.itemDoubleClicked.connect(self._on_item_double_clicked)

        # 设置列宽
        header = self.build_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.build_table)

        # 统计信息
        self.stats_label = QLabel("总计: 0 条记录")
        self.stats_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.stats_label)

        return widget

    def _create_detail_widget(self) -> QWidget:
        """创建详细信息控件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标签
        label = QLabel("构建详情")
        label.setProperty("subheading", True)
        layout.addWidget(label)

        # Tab 控件
        self.detail_tabs = QTabWidget()
        layout.addWidget(self.detail_tabs)

        # Tab 1: 基本信息
        self.info_tab = self._create_info_tab()
        self.detail_tabs.addTab(self.info_tab, "📋 基本信息")

        # Tab 2: 阶段执行
        self.stages_tab = self._create_stages_tab()
        self.detail_tabs.addTab(self.stages_tab, "⚙️ 阶段执行")

        # Tab 3: 构建日志
        self.logs_tab = self._create_logs_tab()
        self.detail_tabs.addTab(self.logs_tab, "📝 构建日志")

        # Tab 4: 产物文件
        self.outputs_tab = self._create_outputs_tab()
        self.detail_tabs.addTab(self.outputs_tab, "📦 产物文件")

        # Tab 5: 构建对比
        self.compare_tab = self._create_compare_tab()
        self.detail_tabs.addTab(self.compare_tab, "📊 构建对比")

        return widget

    def _create_info_tab(self) -> QWidget:
        """创建基本信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        # 构建信息网格
        grid = QGridLayout()
        grid.setSpacing(12)

        # 信息字段
        self.info_fields = {}

        fields = [
            ("build_id", "构建 ID"),
            ("project_name", "项目名称"),
            ("workflow_name", "工作流名称"),
            ("state", "构建状态"),
            ("start_time", "开始时间"),
            ("end_time", "结束时间"),
            ("duration", "总耗时"),
            ("progress", "完成进度"),
            ("error_message", "错误信息")
        ]

        for row, (key, label_text) in enumerate(fields):
            label = QLabel(f"{label_text}:")
            label.setProperty("label", True)
            grid.addWidget(label, row, 0)

            value = QLabel("—")
            value.setProperty("label", True)
            value.setWordWrap(True)
            grid.addWidget(value, row, 1)

            self.info_fields[key] = value

        layout.addLayout(grid)
        layout.addStretch()

        return widget

    def _create_stages_tab(self) -> QWidget:
        """创建阶段执行标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 阶段表格
        self.stages_table = QTableWidget()
        self.stages_table.setColumnCount(4)
        self.stages_table.setHorizontalHeaderLabels([
            "阶段名称", "状态", "耗时(秒)", "错误信息"
        ])
        self.stages_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.stages_table.setAlternatingRowColors(True)
        self.stages_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.stages_table)

        return widget

    def _create_logs_tab(self) -> QWidget:
        """创建构建日志标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 日志查看器
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(FontManager.get_code_font(10))
        self.log_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout.addWidget(self.log_viewer)

        return widget

    def _create_outputs_tab(self) -> QWidget:
        """创建产物文件标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 文件列表
        self.outputs_table = QTableWidget()
        self.outputs_table.setColumnCount(3)
        self.outputs_table.setHorizontalHeaderLabels([
            "文件类型", "文件路径", "大小"
        ])
        self.outputs_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.outputs_table.setAlternatingRowColors(True)
        self.outputs_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.outputs_table)

        return widget

    def _create_compare_tab(self) -> QWidget:
        """创建构建对比标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        # 说明标签
        info_label = QLabel(
            "选择两个构建记录进行对比。\n"
            "在列表中使用 Ctrl 或 Shift 键选择多个构建。"
        )
        info_label.setStyleSheet("color: #94a3b8;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 对比结果显示
        self.compare_viewer = QTextEdit()
        self.compare_viewer.setReadOnly(True)
        self.compare_viewer.setFont(FontManager.get_code_font(10))
        self.compare_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        layout.addWidget(self.compare_viewer)

        return widget

    def _create_bottom_buttons(self) -> QWidget:
        """创建底部按钮"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(12)
        layout.addStretch()

        # 对比按钮
        self.compare_btn = QPushButton("📊 对比选中构建")
        self.compare_btn.setEnabled(False)
        self.compare_btn.clicked.connect(self._compare_selected_builds)
        layout.addWidget(self.compare_btn)

        # 删除按钮
        self.delete_btn = QPushButton("🗑️ 删除选中")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._delete_selected_build)
        layout.addWidget(self.delete_btn)

        # 关闭按钮
        close_btn = QPushButton("❌ 关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        return widget

    def _load_build_history(self):
        """加载构建历史"""
        records = self._history_manager.get_recent_records(100)
        self._populate_table(records)
        self._update_stats(records)

    def _populate_table(self, records: List[BuildRecord]):
        """填充构建历史表格

        Args:
            records: 构建记录列表
        """
        self.build_table.setRowCount(len(records))

        for row, record in enumerate(records):
            # 构建ID
            id_item = QTableWidgetItem(record.build_id[:8])
            id_item.setData(Qt.ItemDataRole.UserRole, record.build_id)
            id_item.setToolTip(record.build_id)
            self.build_table.setItem(row, 0, id_item)

            # 时间
            time_str = record.start_time.strftime("%Y-%m-%d %H:%M:%S")
            time_item = QTableWidgetItem(time_str)
            self.build_table.setItem(row, 1, time_item)

            # 状态
            status_item = QTableWidgetItem(record.state.value)
            self._set_status_color(status_item, record.state)
            self.build_table.setItem(row, 2, status_item)

            # 耗时
            duration_str = "—" if record.duration is None else f"{record.duration:.2f}s"
            duration_item = QTableWidgetItem(duration_str)
            self.build_table.setItem(row, 3, duration_item)

            # 选择复选框
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(
                lambda state, r=record: self._on_checkbox_changed(r, state)
            )
            self.build_table.setCellWidget(row, 4, checkbox)

    def _set_status_color(self, item: QTableWidgetItem, state: BuildState):
        """设置状态项的颜色

        Args:
            item: 表格项
            state: 构建状态
        """
        color_map = {
            BuildState.COMPLETED: "#10b981",  # 绿色
            BuildState.FAILED: "#ef4444",      # 红色
            BuildState.CANCELLED: "#f59e0b",   # 橙色
            BuildState.RUNNING: "#3b82f6",    # 蓝色
            BuildState.IDLE: "#94a3b8",        # 灰色
        }

        color = color_map.get(state, "#94a3b8")
        item.setForeground(QColor(color))
        item.setFont(QFont("Arial", 9, QFont.Weight.Bold))

    def _update_stats(self, records: List[BuildRecord]):
        """更新统计信息

        Args:
            records: 构建记录列表
        """
        stats = self._history_manager.get_statistics()
        self.stats_label.setText(
            f"总计: {stats.total_builds} 条记录 | "
            f"成功: {stats.successful_builds} | "
            f"失败: {stats.failed_builds} | "
            f"取消: {stats.cancelled_builds} | "
            f"成功率: {stats.success_rate:.1f}%"
        )

    def _on_selection_changed(self):
        """选择变化时的处理"""
        selected_rows = self.build_table.selectionModel().selectedRows()

        if not selected_rows:
            self._clear_detail_view()
            self.delete_btn.setEnabled(False)
            return

        # 获取第一行的构建 ID
        row = selected_rows[0].row()
        build_id = self.build_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        # 显示详细信息
        self._show_build_detail(build_id)
        self.delete_btn.setEnabled(True)

    def _on_item_double_clicked(self, item):
        """双击项目时的处理"""
        row = item.row()
        build_id = self.build_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        # 显示详细信息并切换到第一个标签页
        self._show_build_detail(build_id)
        self.detail_tabs.setCurrentIndex(0)

    def _on_checkbox_changed(self, record: BuildRecord, state: int):
        """复选框状态变化时的处理

        Args:
            record: 构建记录
            state: 复选框状态 (0=未选中, 2=选中)
        """
        is_checked = (state == 2)

        if is_checked and record not in self._selected_builds:
            self._selected_builds.append(record)
        elif not is_checked and record in self._selected_builds:
            self._selected_builds.remove(record)

        # 更新对比按钮状态
        self.compare_btn.setEnabled(len(self._selected_builds) == 2)

    def _show_build_detail(self, build_id: str):
        """显示构建详细信息

        Args:
            build_id: 构建 ID
        """
        record = self._history_manager.get_record_by_id(build_id)

        if not record:
            logger.warning(f"未找到构建记录: {build_id}")
            return

        # 更新基本信息
        self._update_info_tab(record)

        # 更新阶段执行
        self._update_stages_tab(record)

        # 更新日志
        self._update_logs_tab(record)

        # 更新产物文件
        self._update_outputs_tab(record)

    def _update_info_tab(self, record: BuildRecord):
        """更新基本信息标签页

        Args:
            record: 构建记录
        """
        self.info_fields["build_id"].setText(record.build_id)
        self.info_fields["project_name"].setText(record.project_name)
        self.info_fields["workflow_name"].setText(record.workflow_name)
        self.info_fields["state"].setText(record.state.value)

        self.info_fields["start_time"].setText(
            record.start_time.strftime("%Y-%m-%d %H:%M:%S")
        )

        end_time_str = "—" if record.end_time is None else record.end_time.strftime("%Y-%m-%d %H:%M:%S")
        self.info_fields["end_time"].setText(end_time_str)

        duration_str = "—" if record.duration is None else f"{record.duration:.2f} 秒"
        self.info_fields["duration"].setText(duration_str)

        self.info_fields["progress"].setText(f"{record.progress_percent}%")

        error_msg = record.error_message or "—"
        self.info_fields["error_message"].setText(error_msg)

    def _update_stages_tab(self, record: BuildRecord):
        """更新阶段执行标签页

        Args:
            record: 构建记录
        """
        self.stages_table.setRowCount(len(record.stage_results))

        for row, stage in enumerate(record.stage_results):
            # 阶段名称
            stage_item = QTableWidgetItem(stage.stage_name)
            self.stages_table.setItem(row, 0, stage_item)

            # 状态
            status_item = QTableWidgetItem(stage.status.value)
            self._set_status_color(status_item, BuildState(stage.status.value))
            self.stages_table.setItem(row, 1, status_item)

            # 耗时
            duration_str = "—" if stage.duration is None else f"{stage.duration:.2f}"
            duration_item = QTableWidgetItem(duration_str)
            self.stages_table.setItem(row, 2, duration_item)

            # 错误信息
            error_msg = stage.error_message or "—"
            error_item = QTableWidgetItem(error_msg)
            self.stages_table.setItem(row, 3, error_item)

    def _update_logs_tab(self, record: BuildRecord):
        """更新构建日志标签页

        Args:
            record: 构建记录
        """
        # 收集所有阶段的日志
        all_logs = []

        for stage in record.stage_results:
            if stage.logs:
                all_logs.append(f"=== {stage.stage_name} ===")
                all_logs.append(stage.logs)
                all_logs.append("")

        if not all_logs:
            all_logs.append("暂无日志")

        self.log_viewer.setText("\n".join(all_logs))

    def _update_outputs_tab(self, record: BuildRecord):
        """更新产物文件标签页

        Args:
            record: 构建记录
        """
        # 如果有 OutputFileRecord，可以使用它们
        # 这里简化处理，仅显示 output_files 中的路径
        self.outputs_table.setRowCount(len(record.output_files))

        for row, file_path in enumerate(record.output_files):
            # 文件类型（从扩展名推断）
            import os
            ext = os.path.splitext(file_path)[1].upper().lstrip('.')
            type_item = QTableWidgetItem(ext if ext else "未知")
            self.outputs_table.setItem(row, 0, type_item)

            # 文件路径
            path_item = QTableWidgetItem(file_path)
            self.outputs_table.setItem(row, 1, path_item)

            # 文件大小（简化处理）
            size_item = QTableWidgetItem("—")
            self.outputs_table.setItem(row, 2, size_item)

    def _clear_detail_view(self):
        """清空详细信息视图"""
        for field in self.info_fields.values():
            field.setText("—")

        self.stages_table.setRowCount(0)
        self.log_viewer.setText("请选择一个构建记录查看详情")
        self.outputs_table.setRowCount(0)
        self.compare_viewer.setText("选择两个构建记录进行对比")

    def _compare_selected_builds(self):
        """对比选中的构建"""
        if len(self._selected_builds) != 2:
            QMessageBox.warning(
                self,
                "⚠️ 选择错误",
                "请选择两个构建记录进行对比"
            )
            return

        build_1 = self._selected_builds[0]
        build_2 = self._selected_builds[1]

        try:
            comparison = self._history_manager.compare_records(
                build_1.build_id,
                build_2.build_id
            )

            # 格式化对比结果
            text = self._format_comparison(comparison)
            self.compare_viewer.setText(text)

            # 切换到对比标签页
            self.detail_tabs.setCurrentIndex(4)

        except Exception as e:
            logger.error(f"对比构建失败: {e}")
            QMessageBox.critical(
                self,
                "❌ 对比失败",
                f"对比构建记录时发生错误:\n\n{str(e)}"
            )

    def _format_comparison(self, comparison: Dict[str, Any]) -> str:
        """格式化对比结果

        Args:
            comparison: 对比结果字典

        Returns:
            str: 格式化的对比文本
        """
        lines = []

        # 构建信息
        lines.append("========== 构建信息 ==========")
        lines.append(f"构建 1: {comparison['build_1']['build_id']} - {comparison['build_1']['project_name']}")
        lines.append(f"  工作流: {comparison['build_1']['workflow_name']}")
        lines.append(f"  时间: {comparison['build_1']['start_time']}")
        lines.append(f"  状态: {comparison['build_1']['state']}")
        lines.append(f"  耗时: {comparison['build_1']['duration']:.2f}s" if comparison['build_1']['duration'] else "  耗时: —")
        lines.append("")
        lines.append(f"构建 2: {comparison['build_2']['build_id']} - {comparison['build_2']['project_name']}")
        lines.append(f"  工作流: {comparison['build_2']['workflow_name']}")
        lines.append(f"  时间: {comparison['build_2']['start_time']}")
        lines.append(f"  状态: {comparison['build_2']['state']}")
        lines.append(f"  耗时: {comparison['build_2']['duration']:.2f}s" if comparison['build_2']['duration'] else "  耗时: —")
        lines.append("")

        # 性能对比
        lines.append("========== 性能对比 ==========")
        perf_diff = comparison.get('performance_diff', {})
        if perf_diff:
            duration_diff = perf_diff.get('duration_diff')
            duration_diff_percent = perf_diff.get('duration_diff_percent')

            if duration_diff is not None:
                if duration_diff > 0:
                    lines.append(f"耗时增加: {duration_diff:.2f}s (+{duration_diff_percent:.1f}%)")
                elif duration_diff < 0:
                    lines.append(f"耗时减少: {abs(duration_diff):.2f}s ({duration_diff_percent:.1f}%)")
                else:
                    lines.append("耗时相同")
        else:
            lines.append("无法对比（缺少耗时数据）")
        lines.append("")

        # 阶段对比
        lines.append("========== 阶段对比 ==========")
        stage_diff = comparison.get('stage_diff', {})
        for stage_name, stage_info in stage_diff.items():
            lines.append(f"[{stage_name}]")
            lines.append(f"  状态 1: {stage_info['status_1'] or '—'}")
            lines.append(f"  状态 2: {stage_info['status_2'] or '—'}")
            lines.append(f"  耗时 1: {stage_info['duration_1']:.2f}s" if stage_info['duration_1'] else "  耗时 1: —")
            lines.append(f"  耗时 2: {stage_info['duration_2']:.2f}s" if stage_info['duration_2'] else "  耗时 2: —")
            if stage_info['duration_diff'] is not None:
                diff = stage_info['duration_diff']
                lines.append(f"  耗时差: {diff:+.2f}s")
            lines.append("")

        # 配置差异
        lines.append("========== 配置差异 ==========")
        config_diff = comparison.get('config_diff', [])
        if config_diff:
            for diff in config_diff:
                lines.append(f"{diff['field']}:")
                lines.append(f"  值 1: {diff['value_1']}")
                lines.append(f"  值 2: {diff['value_2']}")
                lines.append("")
        else:
            lines.append("无配置差异")
            lines.append("")

        return "\n".join(lines)

    def _refresh_history(self):
        """刷新构建历史"""
        self._load_build_history()
        self.statusBar().showMessage("✅ 历史记录已刷新")

    def _clear_all_history(self):
        """清空所有历史记录"""
        reply = QMessageBox.question(
            self,
            "🗑️ 确认清空",
            "确定要清空所有构建历史记录吗？\n\n此操作无法撤销！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            count = self._history_manager.clear_all_records()
            self._load_build_history()
            self._clear_detail_view()
            self._selected_builds = []
            self.compare_btn.setEnabled(False)
            self.statusBar().showMessage(f"✅ 已清空 {count} 条记录")
            logger.info(f"清空所有构建历史: {count} 条记录")

    def _delete_selected_build(self):
        """删除选中的构建"""
        selected_rows = self.build_table.selectionModel().selectedRows()

        if not selected_rows:
            return

        reply = QMessageBox.question(
            self,
            "🗑️ 确认删除",
            f"确定要删除选中的 {len(selected_rows)} 条构建记录吗？\n\n此操作无法撤销！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = 0
            for row in sorted([r.row() for r in selected_rows], reverse=True):
                build_id = self.build_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                if self._history_manager.delete_record(build_id):
                    deleted_count += 1

            self._load_build_history()
            self._clear_detail_view()
            self.statusBar().showMessage(f"✅ 已删除 {deleted_count} 条记录")
            logger.info(f"删除构建记录: {deleted_count} 条")

    def _export_history(self):
        """导出构建历史"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出构建历史",
            "build_history.json",
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )

        if not file_path:
            return

        success = self._history_manager.export_records(Path(file_path))
        if success:
            self.statusBar().showMessage(f"✅ 已导出到: {file_path}")
            logger.info(f"导出构建历史到: {file_path}")
        else:
            QMessageBox.critical(
                self,
                "❌ 导出失败",
                "导出构建历史时发生错误"
            )


def show_build_history(parent: Optional[QWidget] = None) -> int:
    """显示构建历史对话框（便捷函数）

    Args:
        parent: 父窗口

    Returns:
        int: 对话框返回值
    """
    dialog = BuildHistoryDialog(parent)
    return dialog.exec()
