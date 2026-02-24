"""Progress panel widget for real-time build progress display (Story 2.14)

Redesigned with Industrial Precision Theme (v4.0 - 2026-02-24)
- 工业精密美学
- 清晰的视觉层次
- 紧凑但舒适的布局
- 阶段状态一目了然
"""

import logging
import time
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QProgressBar, QLabel, QFrame, QScrollArea,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPalette, QFont

from src.core.models import BuildProgress, StageStatus

logger = logging.getLogger(__name__)


class StageCard(QFrame):
    """单个阶段卡片组件"""

    STAGE_ICONS = {
        "matlab_gen": "🔬",
        "file_process": "⚙️",
        "file_move": "📦",
        "iar_compile": "🔧",
        "a2l_process": "📝",
        "package": "🎯",
    }

    STAGE_NAMES = {
        "matlab_gen": "MATLAB 代码生成",
        "file_process": "文件处理",
        "file_move": "文件复制",
        "iar_compile": "IAR 编译",
        "a2l_process": "A2L 处理",
        "package": "打包归档",
    }

    STATUS_ICONS = {
        StageStatus.PENDING: "⏳",
        StageStatus.RUNNING: "🔄",
        StageStatus.COMPLETED: "✅",
        StageStatus.FAILED: "❌",
        StageStatus.CANCELLED: "⏹️",
        StageStatus.SKIPPED: "⏭️",
    }

    STATUS_COLORS = {
        StageStatus.PENDING: ("#475569", "#1e293b"),      # 灰色文字，深色背景
        StageStatus.RUNNING: ("#3b82f6", "#1e3a5f"),     # 蓝色文字，蓝色背景
        StageStatus.COMPLETED: ("#22c55e", "#14532d"),   # 绿色文字，绿色背景
        StageStatus.FAILED: ("#ef4444", "#7f1d1d"),      # 红色文字，红色背景
        StageStatus.CANCELLED: ("#6b7280", "#374151"),   # 灰色
        StageStatus.SKIPPED: ("#f97316", "#7c2d12"),     # 橙色
    }

    def __init__(self, stage_name: str, parent=None):
        super().__init__(parent)
        self.stage_name = stage_name
        self._status = StageStatus.PENDING
        self._duration = 0.0

        self.setObjectName("stageCard")
        self.setStyleSheet(self._get_stylesheet())
        self.setFixedHeight(56)

        self._init_ui()

    def _get_stylesheet(self) -> str:
        return """
            QFrame#stageCard {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QFrame#stageCard:hover {
                border-color: #475569;
            }
            QLabel {
                background: transparent;
            }
        """

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # 状态图标
        self.status_icon = QLabel(self.STATUS_ICONS[StageStatus.PENDING])
        self.status_icon.setFixedSize(24, 24)
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_icon)

        # 阶段图标和名称
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        icon = self.STAGE_ICONS.get(self.stage_name, "📋")
        display_name = self.STAGE_NAMES.get(self.stage_name, self.stage_name)

        self.name_label = QLabel(f"{icon} {display_name}")
        self.name_label.setStyleSheet("color: #f1f5f9; font-size: 13px; font-weight: 500;")
        info_layout.addWidget(self.name_label)

        self.duration_label = QLabel("等待中")
        self.duration_label.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(self.duration_label)

        layout.addLayout(info_layout, 1)

        # 状态标签
        self.status_label = QLabel("待执行")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet("""
            color: #94a3b8;
            font-size: 12px;
            padding: 4px 12px;
            background-color: #334155;
            border-radius: 4px;
        """)
        layout.addWidget(self.status_label)

    def set_status(self, status: StageStatus, duration: float = 0.0):
        """设置阶段状态"""
        self._status = status
        self._duration = duration

        # 更新状态图标
        self.status_icon.setText(self.STATUS_ICONS.get(status, "❓"))

        # 更新持续时间
        if status == StageStatus.RUNNING:
            self.duration_label.setText("执行中...")
        elif status == StageStatus.COMPLETED:
            self.duration_label.setText(f"耗时 {duration:.1f}s")
        elif status == StageStatus.FAILED:
            self.duration_label.setText(f"失败 (耗时 {duration:.1f}s)")
        elif status == StageStatus.SKIPPED:
            self.duration_label.setText("已跳过")
        else:
            self.duration_label.setText("等待中")

        # 更新状态标签
        text_color, bg_color = self.STATUS_COLORS.get(status, ("#94a3b8", "#334155"))
        status_texts = {
            StageStatus.PENDING: "待执行",
            StageStatus.RUNNING: "执行中",
            StageStatus.COMPLETED: "已完成",
            StageStatus.FAILED: "失败",
            StageStatus.CANCELLED: "已取消",
            StageStatus.SKIPPED: "已跳过",
        }
        self.status_label.setText(status_texts.get(status, "未知"))
        self.status_label.setStyleSheet(f"""
            color: {text_color};
            font-size: 12px;
            font-weight: 500;
            padding: 4px 12px;
            background-color: {bg_color};
            border-radius: 4px;
        """)


class ProgressPanel(QWidget):
    """构建进度面板组件 - 工业精密风格

    设计理念：
    - 清晰的阶段卡片布局
    - 顶部进度概览
    - 底部时间统计
    - 阶段状态一目了然
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.current_progress = BuildProgress()
        self.stage_cards: dict[str, StageCard] = {}

        # 性能监控
        self.last_update_time = time.monotonic()
        self.update_intervals = []
        self.max_interval_history = 100
        self.last_update_timestamp = time.monotonic()
        self.update_frequency_timer = None

        # 动画
        self.enable_animations = True
        self._animation_value = 0.0

        self._init_ui()
        self.setStyleSheet(self._get_stylesheet())
        logger.debug("进度面板初始化完成")

    def _get_stylesheet(self) -> str:
        return """
            QWidget {
                background-color: transparent;
            }
            QProgressBar {
                background-color: #1e293b;
                border: none;
                border-radius: 6px;
                text-align: center;
                color: #f8fafc;
                font-size: 12px;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f97316, stop:1 #fb923c);
                border-radius: 6px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1e293b;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ===== 顶部进度概览 =====
        overview_frame = QFrame()
        overview_frame.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
        """)
        overview_layout = QVBoxLayout(overview_frame)
        overview_layout.setSpacing(12)
        overview_layout.setContentsMargins(20, 16, 20, 16)

        # 第一行：标题和百分比
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        self.title_label = QLabel("📊 构建进度")
        self.title_label.setStyleSheet("color: #f8fafc; font-size: 14px; font-weight: 600;")
        header_row.addWidget(self.title_label)

        header_row.addStretch()

        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet("color: #f97316; font-size: 18px; font-weight: 700;")
        header_row.addWidget(self.percentage_label)

        overview_layout.addLayout(header_row)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("")
        self.progress_bar.setFixedHeight(8)
        overview_layout.addWidget(self.progress_bar)

        # 第三行：当前阶段
        self.current_stage_label = QLabel("等待开始...")
        self.current_stage_label.setStyleSheet("color: #64748b; font-size: 12px;")
        overview_layout.addWidget(self.current_stage_label)

        main_layout.addWidget(overview_frame)

        # ===== 阶段列表区域 =====
        stages_frame = QFrame()
        stages_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
            }
        """)
        stages_layout = QVBoxLayout(stages_frame)
        stages_layout.setSpacing(8)
        stages_layout.setContentsMargins(12, 12, 12, 12)

        # 阶段列表标题
        stages_header = QLabel("执行阶段")
        stages_header.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 500; padding: 4px;")
        stages_layout.addWidget(stages_header)

        # 阶段卡片容器
        self.stages_container = QWidget()
        self.stages_layout = QVBoxLayout(self.stages_container)
        self.stages_layout.setSpacing(8)
        self.stages_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidget(self.stages_container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(200)
        scroll.setStyleSheet("background: transparent;")
        stages_layout.addWidget(scroll)

        main_layout.addWidget(stages_frame, 1)

        # ===== 底部时间统计 =====
        time_frame = QFrame()
        time_frame.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
        """)
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(20, 12, 20, 12)

        # 已用时间
        elapsed_icon = QLabel("⏱️")
        time_layout.addWidget(elapsed_icon)

        self.elapsed_label = QLabel("00:00:00")
        self.elapsed_label.setStyleSheet("color: #f8fafc; font-size: 14px; font-weight: 500;")
        time_layout.addWidget(self.elapsed_label)

        time_layout.addStretch()

        # 预计剩余
        remaining_icon = QLabel("📈")
        time_layout.addWidget(remaining_icon)

        self.remaining_label = QLabel("--:--:--")
        self.remaining_label.setStyleSheet("color: #64748b; font-size: 14px;")
        time_layout.addWidget(self.remaining_label)

        main_layout.addWidget(time_frame)

    def initialize_stages(self, stage_names: list[str]):
        """初始化阶段列表"""
        # 清空现有卡片
        for card in self.stage_cards.values():
            card.deleteLater()
        self.stage_cards.clear()

        # 清空布局
        while self.stages_layout.count():
            item = self.stages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 创建新卡片
        for stage_name in stage_names:
            card = StageCard(stage_name)
            self.stage_cards[stage_name] = card
            self.stages_layout.addWidget(card)

        # 添加弹性空间
        self.stages_layout.addStretch()

        # 重置进度
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        self.current_stage_label.setText("等待开始...")

        # 重置进度对象
        self.current_progress = BuildProgress(
            total_stages=len(stage_names),
            percentage=0.0
        )
        for stage_name in stage_names:
            self.current_progress.stage_statuses[stage_name] = StageStatus.PENDING

        logger.debug(f"已初始化 {len(stage_names)} 个阶段")

    def update_progress(self, progress: BuildProgress):
        """更新进度"""
        self.current_progress = progress
        self.last_update_timestamp = time.monotonic()

        # 性能监控
        current_time = time.monotonic()
        interval = current_time - self.last_update_time
        self.update_intervals.append(interval)
        if len(self.update_intervals) > self.max_interval_history:
            self.update_intervals.pop(0)

        if interval > 2.0:
            avg = sum(self.update_intervals) / len(self.update_intervals)
            logger.warning(f"进度更新间隔过长: {interval:.2f}s (平均: {avg:.2f}s)")

        self.last_update_time = current_time

        # 更新进度条
        percent = int(progress.percentage)
        if self.enable_animations:
            self._animate_progress(percent)
        else:
            self.progress_bar.setValue(percent)

        self.percentage_label.setText(f"{percent}%")

        # 更新当前阶段
        self._update_current_stage(progress)

        # 更新阶段卡片
        self._update_stage_cards(progress)

        # 更新时间
        self._update_time_display(progress)

    def _animate_progress(self, target_value: int):
        """动画更新进度条"""
        if hasattr(self, '_progress_animation'):
            self._progress_animation.stop()

        self._progress_animation = QPropertyAnimation(
            self.progress_bar, b"value"
        )
        self._progress_animation.setDuration(300)
        self._progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._progress_animation.setStartValue(self.progress_bar.value())
        self._progress_animation.setEndValue(target_value)
        self._progress_animation.start()

    def _update_current_stage(self, progress: BuildProgress):
        """更新当前阶段显示"""
        if not progress.current_stage:
            self.current_stage_label.setText("等待开始...")
            self.current_stage_label.setStyleSheet("color: #64748b; font-size: 12px;")
            return

        stage = progress.current_stage
        status = progress.stage_statuses.get(stage)
        icon = StageCard.STAGE_ICONS.get(stage, "📋")
        name = StageCard.STAGE_NAMES.get(stage, stage)

        if status == StageStatus.RUNNING:
            self.current_stage_label.setText(f"🔄 正在执行: {name}")
            self.current_stage_label.setStyleSheet("color: #3b82f6; font-size: 12px;")
        elif status == StageStatus.COMPLETED:
            self.current_stage_label.setText(f"✅ {name} 完成")
            self.current_stage_label.setStyleSheet("color: #22c55e; font-size: 12px;")
        elif status == StageStatus.FAILED:
            self.current_stage_label.setText(f"❌ {name} 失败")
            self.current_stage_label.setStyleSheet("color: #ef4444; font-size: 12px;")
        elif status == StageStatus.SKIPPED:
            self.current_stage_label.setText(f"⏭️ {name} 已跳过")
            self.current_stage_label.setStyleSheet("color: #f97316; font-size: 12px;")
        else:
            self.current_stage_label.setText(f"⏳ {name}")
            self.current_stage_label.setStyleSheet("color: #64748b; font-size: 12px;")

    def _update_stage_cards(self, progress: BuildProgress):
        """更新阶段卡片"""
        for stage_name, status in progress.stage_statuses.items():
            if stage_name in self.stage_cards:
                duration = progress.elapsed_time  # 简化：使用总时间
                self.stage_cards[stage_name].set_status(status, duration)

    def _update_time_display(self, progress: BuildProgress):
        """更新时间显示"""
        from src.utils.progress import format_duration

        elapsed = format_duration(progress.elapsed_time)
        remaining = format_duration(progress.estimated_remaining_time)

        self.elapsed_label.setText(elapsed)
        self.remaining_label.setText(remaining)

    def clear(self):
        """清空进度显示"""
        for card in self.stage_cards.values():
            card.set_status(StageStatus.PENDING)

        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        self.current_stage_label.setText("等待开始...")
        self.elapsed_label.setText("00:00:00")
        self.remaining_label.setText("--:--:--")

        self.current_progress = BuildProgress()
        logger.debug("进度面板已清空")

    def show_cancelled_state(self):
        """显示取消状态"""
        self.current_stage_label.setText("❌ 构建已取消")
        self.current_stage_label.setStyleSheet("color: #f97316; font-size: 12px;")

        for card in self.stage_cards.values():
            card.set_status(StageStatus.CANCELLED)

        from src.utils.progress import format_duration
        elapsed = format_duration(self.current_progress.elapsed_time)
        self.elapsed_label.setText(elapsed)
        self.remaining_label.setText("已取消")

        logger.debug("进度面板已显示取消状态")

    def set_animations_enabled(self, enabled: bool):
        """启用/禁用动画"""
        self.enable_animations = enabled

    def get_average_update_interval(self) -> float:
        """获取平均更新间隔"""
        if not self.update_intervals:
            return 0.0
        return sum(self.update_intervals) / len(self.update_intervals)
