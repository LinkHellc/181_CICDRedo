"""Progress panel widget for real-time build progress display (Story 2.14)

This module implements the ProgressPanel widget that displays build progress,
stage status, and time information in real-time.

Architecture Decision 3.1:
- 使用 PyQt6 QWidget 实现自定义组件
- 跨线程信号使用 QueuedConnection（在连接时设置）
"""

import logging
import time
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QProgressBar, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPalette

from src.core.models import BuildProgress, StageStatus

logger = logging.getLogger(__name__)


class ProgressPanel(QWidget):
    """构建进度面板组件 (Story 2.14 - 任务 5)

    显示构建进度的实时面板，包含进度条、阶段列表、时间信息等。

    Architecture Decision 3.1:
    - 继承 QWidget
    - 使用 QVBoxLayout 进行布局
    - 支持进度更新、状态显示、错误处理等功能

    Tasks:
        任务 5: 创建 PyQt6 进度面板组件
        任务 6: 实现进度更新接口
        任务 9: 实现阶段状态颜色高亮
        任务 12: 添加性能监控
        任务 13: 实现进度动画效果
        任务 14: 添加错误状态处理
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """初始化进度面板

        Args:
            parent: 父窗口
        """
        super().__init__(parent)

        # 当前进度对象
        self.current_progress = BuildProgress()

        # 性能监控 (任务 12)
        self.last_update_time = time.monotonic()
        self.update_intervals = []
        self.max_interval_history = 100

        # 动画配置 (任务 13)
        self.enable_animations = True
        self._animation_value = 0.0  # 用于动画效果的内部值

        # 初始化 UI
        self._init_ui()

        logger.debug("进度面板初始化完成")

    def _init_ui(self):
        """初始化 UI 组件 (任务 5.2-5.7)"""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # ===== 进度条 (任务 5.2) =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(28)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # ===== 当前阶段标签 (任务 5.4) =====
        self.current_stage_label = QLabel("等待开始...")
        self.current_stage_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        layout.addWidget(self.current_stage_label)

        # ===== 分隔线 =====
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # ===== 阶段列表 (任务 5.3) =====
        self.stage_list = QTableWidget()
        self.stage_list.setColumnCount(2)
        self.stage_list.setHorizontalHeaderLabels(["阶段名称", "状态"])
        self.stage_list.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.stage_list.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.stage_list.setMinimumHeight(200)
        self.stage_list.verticalHeader().setVisible(False)
        self.stage_list.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.stage_list.itemClicked.connect(self._on_stage_clicked)
        layout.addWidget(self.stage_list)

        # ===== 时间信息标签 (任务 5.5) =====
        self.time_label = QLabel("已用时间: 00:00:00 | 预计剩余: --:--:--")
        self.time_label.setStyleSheet("font-size: 12px; color: #666; padding: 8px;")
        layout.addWidget(self.time_label)

        # 任务 5.6: 设计布局（进度条在顶部，阶段列表在下方，时间信息在底部）

        self.setLayout(layout)

    def update_progress(self, progress: BuildProgress):
        """更新进度 (任务 6.1-6.7)

        Args:
            progress: 构建进度对象
        """
        self.current_progress = progress

        # 性能监控 (任务 12.1-12.4)
        current_time = time.monotonic()
        interval = current_time - self.last_update_time

        self.update_intervals.append(interval)
        if len(self.update_intervals) > self.max_interval_history:
            self.update_intervals.pop(0)

        avg_interval = sum(self.update_intervals) / len(self.update_intervals)

        if interval > 2.0:
            logger.warning(
                f"进度更新间隔过长: {interval:.2f} 秒（平均: {avg_interval:.2f} 秒）"
            )

        self.last_update_time = current_time

        # 更新进度条 (任务 6.3)
        self.progress_bar.setValue(int(progress.percentage))

        # 更新当前阶段标签 (任务 6.4)
        self._update_current_stage_label(progress)

        # 更新阶段列表 (任务 6.5)
        self._update_stage_list(progress)

        # 更新时间显示 (任务 6.6)
        self._update_time_display(progress)

        # 更新动画 (任务 13)
        if self.enable_animations:
            self._update_animations()

    def _update_current_stage_label(self, progress: BuildProgress):
        """更新当前阶段标签 (任务 6.4)"""
        if progress.current_stage:
            stage_status = progress.stage_statuses.get(progress.current_stage)

            if stage_status == StageStatus.FAILED:
                # 任务 14.2: 为失败阶段显示红色高亮
                self.current_stage_label.setText(f"❌ 阶段失败: {progress.current_stage}")
                self.current_stage_label.setStyleSheet(
                    "font-weight: bold; font-size: 14px; color: red; padding: 8px;"
                )
            elif stage_status == StageStatus.COMPLETED:
                self.current_stage_label.setText(f"✅ {progress.current_stage}")
                self.current_stage_label.setStyleSheet(
                    "font-weight: bold; font-size: 14px; color: green; padding: 8px;"
                )
            elif stage_status == StageStatus.RUNNING:
                self.current_stage_label.setText(f"🔄 正在执行: {progress.current_stage}")
                self.current_stage_label.setStyleSheet(
                    "font-weight: bold; font-size: 14px; color: blue; padding: 8px;"
                )
            elif stage_status == StageStatus.SKIPPED:
                self.current_stage_label.setText(f"⏭️ {progress.current_stage} (跳过)")
                self.current_stage_label.setStyleSheet(
                    "font-weight: bold; font-size: 14px; color: orange; padding: 8px;"
                )
            else:
                self.current_stage_label.setText(f"⏸️ {progress.current_stage}")
                self.current_stage_label.setStyleSheet(
                    "font-weight: bold; font-size: 14px; color: gray; padding: 8px;"
                )
        else:
            self.current_stage_label.setText("等待开始...")
            self.current_stage_label.setStyleSheet(
                "font-weight: bold; font-size: 14px; color: black; padding: 8px;"
            )

    def _update_stage_list(self, progress: BuildProgress):
        """更新阶段列表 (任务 6.5)"""
        self.stage_list.setRowCount(len(progress.stage_statuses))

        for row, (stage_name, status) in enumerate(progress.stage_statuses.items()):
            # 阶段名称
            name_item = QTableWidgetItem(stage_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.stage_list.setItem(row, 0, name_item)

            # 状态
            status_text = self._get_stage_status_text(status)
            status_item = QTableWidgetItem(status_text)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 任务 9.1-9.3: 应用颜色高亮
            color = self._get_stage_color(status)
            status_item.setForeground(QColor(color))

            self.stage_list.setItem(row, 1, status_item)

    def _get_stage_status_text(self, status: StageStatus) -> str:
        """获取阶段状态文本

        Args:
            status: 阶段状态枚举

        Returns:
            str: 状态文本
        """
        status_map = {
            StageStatus.PENDING: "⏸️ 等待中",
            StageStatus.RUNNING: "🔄 进行中",
            StageStatus.COMPLETED: "✅ 已完成",
            StageStatus.FAILED: "❌ 失败",
            StageStatus.CANCELLED: "⏸️ 已取消",
            StageStatus.SKIPPED: "⏭️ 跳过"
        }
        return status_map.get(status, "未知")

    def _get_stage_color(self, status: StageStatus) -> str:
        """获取阶段状态颜色 (任务 9.1-9.2)

        Args:
            status: 阶段状态枚举

        Returns:
            str: 颜色字符串（ QColor 支持的格式）
        """
        # 任务 9.2: 定义颜色映射
        color_map = {
            StageStatus.PENDING: "#808080",  # 灰色
            StageStatus.RUNNING: "#0066cc",  # 蓝色
            StageStatus.COMPLETED: "#008000",  # 绿色
            StageStatus.FAILED: "#cc0000",  # 红色
            StageStatus.CANCELLED: "#808080",  # 灰色
            StageStatus.SKIPPED: "#ff8800"  # 橙色
        }
        return color_map.get(status, "#000000")

    def _update_time_display(self, progress: BuildProgress):
        """更新时间显示 (任务 6.6, 任务 10)"""
        from src.utils.progress import format_duration

        elapsed_text = format_duration(progress.elapsed_time)
        remaining_text = format_duration(progress.estimated_remaining_time)

        self.time_label.setText(
            f"已用时间: {elapsed_text} | 预计剩余: {remaining_text}"
        )

    def _update_animations(self):
        """更新动画效果 (任务 13)"""
        # 任务 13.1: 为进度条添加平滑动画效果
        if hasattr(self, '_progress_animation'):
            self._progress_animation.stop()

        self._progress_animation = QPropertyAnimation(
            self.progress_bar, b"value"
        )
        self._progress_animation.setDuration(300)
        self._progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._progress_animation.setStartValue(self.progress_bar.value())
        self._progress_animation.setEndValue(int(self.current_progress.percentage))
        self._progress_animation.start()

    def _on_stage_clicked(self, item: QTableWidgetItem):
        """处理阶段列表项点击 (任务 14.1-14.3)

        Args:
            item: 被点击的表格项
        """
        row = item.row()
        stage_name_item = self.stage_list.item(row, 0)
        if stage_name_item is None:
            return

        stage_name = stage_name_item.text()
        stage_status = self.current_progress.stage_statuses.get(stage_name)

        # 任务 14.1: 处理 FAILED 状态
        if stage_status == StageStatus.FAILED:
            from PyQt6.QtWidgets import QMessageBox

            # 任务 14.3: 点击失败阶段显示错误详情
            error_message = self.current_progress.stage_errors.get(
                stage_name, "未知错误"
            )

            QMessageBox.critical(
                self,
                "阶段失败",
                f"阶段 '{stage_name}' 执行失败：\n\n{error_message}"
            )
            logger.info(f"显示阶段失败详情: {stage_name}")

    def set_animations_enabled(self, enabled: bool):
        """启用或禁用动画效果 (任务 13.4)

        Args:
            enabled: 是否启用动画
        """
        self.enable_animations = enabled
        logger.debug(f"进度面板动画{'启用' if enabled else '禁用'}")

    def clear(self):
        """清空进度显示"""
        self.current_progress = BuildProgress()
        self.progress_bar.setValue(0)
        self.current_stage_label.setText("等待开始...")
        self.current_stage_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: black; padding: 8px;"
        )
        self.stage_list.setRowCount(0)
        self.time_label.setText("已用时间: 00:00:00 | 预计剩余: --:--:--")
        logger.debug("进度面板已清空")

    def show_cancelled_state(self):
        """显示取消状态 (Story 2.15 - 任务 10.5, 任务 12.1-12.6)

        更新进度面板显示构建已取消的状态。
        """
        # 更新当前阶段标签 (任务 12.3)
        self.current_stage_label.setText("❌ 构建已取消")
        self.current_stage_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: orange; padding: 8px;"
        )

        # 更新所有阶段状态为 CANCELLED (任务 12.1, 12.2)
        for row in range(self.stage_list.rowCount()):
            stage_name_item = self.stage_list.item(row, 0)
            if stage_name_item:
                stage_name = stage_name_item.text()

                # 更新状态文本 (任务 12.3)
                status_text = self._get_stage_status_text(StageStatus.CANCELLED)
                status_item = self.stage_list.item(row, 1)
                if status_item:
                    status_item.setText(status_text)

                    # 应用颜色 (任务 12.4)
                    color = self._get_stage_color(StageStatus.CANCELLED)
                    status_item.setForeground(QColor(color))

        # 更新时间显示：显示取消时的已用时间 (任务 12.5)
        elapsed_text = format_duration(self.current_progress.elapsed_time)
        self.time_label.setText(f"已用时间: {elapsed_text} | 构建已取消")

        logger.debug("进度面板已显示取消状态")

    def get_average_update_interval(self) -> float:
        """获取平均更新间隔 (任务 12.2, 12.3)

        Returns:
            float: 平均更新间隔（秒）
        """
        if not self.update_intervals:
            return 0.0
        return sum(self.update_intervals) / len(self.update_intervals)
