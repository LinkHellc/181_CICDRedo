"""Workflow manager for MBD_CICDKits (Story 2.4 Task 8)

This module manages the workflow thread lifecycle and coordinates
between UI and workflow execution.
"""

import logging
from typing import Optional

from PyQt6.QtCore import QObject, Qt

from core.models import (
    ProjectConfig,
    WorkflowConfig,
    BuildExecution,
    BuildState
)
from core.workflow_thread import WorkflowThread

logger = logging.getLogger(__name__)


class WorkflowManager(QObject):
    """工作流管理器 (Story 2.4 Task 8.1)

    管理工作流线程的生命周期，协调 UI 与工作流线程之间的通信。

    Architecture Decision 3.1:
    - 使用 QThread + pyqtSignal 实现线程通信
    - 跨线程信号使用 QueuedConnection（在连接时设置）

    Responsibilities (Story 2.4 Task 8.2):
    - 启动工作流
    - 停止工作流
    - 清理工作流资源
    - 维护构建状态信息

    Attributes:
        parent: 父对象
        workflow_thread: 工作流线程实例
        current_execution: 当前构建执行信息
    """

    def __init__(self, parent: Optional[QObject] = None):
        """初始化工作流管理器

        Args:
            parent: 父对象（通常是主窗口）
        """
        super().__init__(parent)

        self.workflow_thread: Optional[WorkflowThread] = None
        self.current_execution: Optional[BuildExecution] = None

        logger.info("工作流管理器初始化完成")

    def start_workflow(
        self,
        project_config: ProjectConfig,
        workflow_config: WorkflowConfig,
        connections: Optional[dict] = None
    ) -> bool:
        """启动工作流 (Story 2.4 Task 8.2)

        创建并启动工作流线程，连接信号到回调函数。

        Args:
            project_config: 项目配置
            workflow_config: 工作流配置
            connections: 信号连接字典 {signal_name: callback}

        Returns:
            bool: 是否成功启动
        """
        # 检查是否已有运行中的工作流
        if self.is_running():
            logger.warning("工作流已在运行中，无法启动新工作流")
            return False

        # 创建工作流线程
        self.workflow_thread = WorkflowThread(project_config, workflow_config, self)

        # 连接信号（使用 QueuedConnection 确保线程安全）
        # Story 2.4 Task 5.2: 使用 QueuedConnection
        if connections:
            if 'progress_update' in connections:
                self.workflow_thread.progress_update.connect(
                    connections['progress_update'],
                    Qt.ConnectionType.QueuedConnection
                )
            if 'stage_started' in connections:
                self.workflow_thread.stage_started.connect(
                    connections['stage_started'],
                    Qt.ConnectionType.QueuedConnection
                )
            if 'stage_complete' in connections:
                self.workflow_thread.stage_complete.connect(
                    connections['stage_complete'],
                    Qt.ConnectionType.QueuedConnection
                )
            if 'log_message' in connections:
                self.workflow_thread.log_message.connect(
                    connections['log_message'],
                    Qt.ConnectionType.QueuedConnection
                )
            if 'error_occurred' in connections:
                self.workflow_thread.error_occurred.connect(
                    connections['error_occurred'],
                    Qt.ConnectionType.QueuedConnection
                )
            if 'build_finished' in connections:
                self.workflow_thread.build_finished.connect(
                    connections['build_finished'],
                    Qt.ConnectionType.QueuedConnection
                )

        # 启动线程
        logger.info(f"启动工作流: {workflow_config.name}")
        self.workflow_thread.start()

        return True

    def stop_workflow(self) -> bool:
        """停止工作流 (Story 2.4 Task 7.3, 8.2)

        请求中断正在运行的工作流。

        Returns:
            bool: 是否成功请求停止
        """
        if not self.is_running():
            logger.warning("没有运行中的工作流，无法停止")
            return False

        logger.info("请求停止工作流")
        self.workflow_thread.requestInterruption()

        return True

    def is_running(self) -> bool:
        """检查是否运行中 (Story 2.4 Task 8.2)

        Returns:
            bool: 工作流是否正在运行
        """
        return (
            self.workflow_thread is not None and
            self.workflow_thread.isRunning()
        )

    def get_current_execution(self) -> Optional[BuildExecution]:
        """获取当前构建执行信息 (Story 2.4 Task 8.2)

        Returns:
            BuildExecution: 当前构建执行信息，如果没有则返回 None
        """
        if self.workflow_thread:
            return self.workflow_thread.get_build_execution()
        return None

    def cleanup(self):
        """清理工作流资源 (Story 2.4 Task 8.2)

        在工作流完成后清理线程引用。
        """
        if self.workflow_thread:
            # 如果线程还在运行，等待它完成
            if self.workflow_thread.isRunning():
                self.workflow_thread.wait()

            # 清理引用
            self.workflow_thread.deleteLater()
            self.workflow_thread = None

        self.current_execution = None

        logger.info("工作流资源已清理")
