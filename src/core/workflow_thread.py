"""Workflow thread for background execution (Story 2.4 Task 2)

This module implements a PyQt6 QThread for executing workflows in the background
following Architecture Decision 3.1 (PyQt6 Threading).
"""

import logging
import time
from typing import Optional, Callable, TYPE_CHECKING

from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt

from core.models import (
    WorkflowConfig,
    ProjectConfig,
    BuildContext,
    BuildState,
    StageResult,
    StageExecution,
    BuildExecution
)

# 类型注解导入（仅在类型检查时使用）
if TYPE_CHECKING:
    from core.models import StageConfig

logger = logging.getLogger(__name__)


class WorkflowThread(QThread):
    """工作流执行线程 (Story 2.4 Task 2.1, 2.2)

    继承 PyQt6 QThread，用于在后台执行工作流，避免阻塞 UI。

    Architecture Decision 3.1:
    - 使用 QThread + pyqtSignal 实现线程通信
    - 跨线程信号使用 QueuedConnection（在连接时设置）

    Signals (Story 2.4 Task 2.3):
        progress_update(int, str): 进度百分比, 消息
        stage_started(str): 阶段名称
        stage_complete(str, bool): 阶段名, 成功
        log_message(str): 日志内容
        error_occurred(str, list): 错误消息, 建议列表
        build_finished(BuildState): 构建最终状态
    """

    # 定义信号 (Story 2.4 Task 2.3)
    progress_update = pyqtSignal(int, str)  # 进度百分比, 消息
    stage_started = pyqtSignal(str)  # 阶段名称
    stage_complete = pyqtSignal(str, bool)  # 阶段名, 成功
    log_message = pyqtSignal(str)  # 日志内容
    error_occurred = pyqtSignal(str, list)  # 错误消息, 建议列表
    build_finished = pyqtSignal(BuildState)  # 构建最终状态

    def __init__(self, project_config: ProjectConfig, workflow_config: WorkflowConfig, parent: Optional[QObject] = None):
        """初始化工作流线程

        Args:
            project_config: 项目配置
            workflow_config: 工作流配置
            parent: 父对象
        """
        super().__init__(parent)

        self.project_config = project_config
        self.workflow_config = workflow_config

        # 构建执行信息
        self._build_execution = BuildExecution(
            project_name=project_config.name,
            workflow_id=workflow_config.id,
            state=BuildState.IDLE
        )

        logger.info(f"工作流线程初始化: 项目={project_config.name}, 工作流={workflow_config.name}")

    def run(self) -> None:
        """工作流执行入口 (Story 2.4 Task 2.4)

        此方法在线程启动时被调用，执行工作流逻辑。

        Architecture Decision 2.1:
        - 使用 time.monotonic() 记录时间
        - 支持中断检测
        """
        try:
            # 记录开始时间 (Story 2.4 Task 6.1)
            start_time = time.monotonic()
            self._build_execution.start_time = start_time
            self._build_execution.state = BuildState.RUNNING

            logger.info(f"工作流开始执行: {self.workflow_config.name}")
            self.log_message.emit(f"工作流开始: {self.workflow_config.name}")

            # 执行工作流 (Story 2.4 Task 2.5)
            success = self._execute_workflow_internal()

            # 计算总执行时长 (Story 2.4 Task 6.4)
            elapsed = time.monotonic() - start_time
            self._build_execution.end_time = time.monotonic()
            self._build_execution.duration = elapsed

            # 确定最终状态
            if self.isInterruptionRequested():
                final_state = BuildState.CANCELLED
                self._build_execution.state = BuildState.CANCELLED
                self._build_execution.error_message = "构建被用户取消"
                logger.info("工作流已取消")
                self.log_message.emit("工作流已被用户取消")
            elif success:
                final_state = BuildState.COMPLETED
                self._build_execution.state = BuildState.COMPLETED
                logger.info(f"工作流执行成功，耗时: {elapsed:.2f} 秒")
                self.log_message.emit(f"工作流执行完成，耗时: {elapsed:.2f} 秒")
            else:
                final_state = BuildState.FAILED
                self._build_execution.state = BuildState.FAILED
                logger.error(f"工作流执行失败，耗时: {elapsed:.2f} 秒")
                self.log_message.emit(f"工作流执行失败: {self._build_execution.error_message}")

            # 发送完成信号
            self.build_finished.emit(final_state)

        except Exception as e:
            # 捕获未预期的异常
            logger.exception("工作流执行过程中发生未预期异常")
            self._build_execution.state = BuildState.FAILED
            self._build_execution.error_message = f"未预期错误: {str(e)}"
            self.error_occurred.emit(f"未预期错误: {str(e)}", ["查看日志获取详细信息"])
            self.build_finished.emit(BuildState.FAILED)

    def _execute_workflow_internal(self) -> bool:
        """执行工作流内部实现 (Story 2.4 Task 2.5)

        按顺序执行工作流中所有启用的阶段。

        Returns:
            bool: 是否全部成功
        """
        from core.workflow import STAGE_EXECUTORS  # 动态导入避免循环依赖

        # 获取启用的阶段
        enabled_stages = [
            s for s in self.workflow_config.stages
            if s.enabled
        ]

        if not enabled_stages:
            logger.warning("没有启用的阶段")
            self.log_message.emit("警告: 没有启用的阶段")
            return False

        total_stages = len(enabled_stages)
        logger.info(f"工作流包含 {total_stages} 个启用阶段")

        # 初始化构建上下文
        context = BuildContext(
            config=self.project_config.to_dict(),
            state={
                "build_start_time": self._build_execution.start_time
            },
            log_callback=lambda msg: self.log_message.emit(msg)
        )

        # 执行每个阶段
        for i, stage_config in enumerate(enabled_stages):
            # 检查中断标志 (Story 2.4 Task 7.4)
            if self.isInterruptionRequested():
                logger.info("检测到中断请求，停止工作流执行")
                self.log_message.emit("正在取消构建...")
                return False

            # 更新当前阶段
            stage_name = stage_config.name
            self._build_execution.current_stage = stage_name

            # 记录阶段执行信息 (Story 2.4 Task 6.3)
            stage_execution = StageExecution(
                name=stage_name,
                status=BuildState.RUNNING,
                start_time=time.monotonic()
            )
            self._build_execution.stages.append(stage_execution)

            # 计算进度 (Story 2.4 Task 6.2)
            progress = int((i / total_stages) * 100)
            self._build_execution.progress_percent = progress

            # 发送进度更新信号
            self.progress_update.emit(progress, f"执行阶段: {stage_name}")
            self.stage_started.emit(stage_name)
            logger.info(f"开始执行阶段 {i+1}/{total_stages}: {stage_name}")

            # 执行阶段
            result = self._execute_stage(stage_config, context)

            # 记录阶段结束信息
            stage_execution.end_time = time.monotonic()
            stage_execution.duration = stage_execution.end_time - stage_execution.start_time

            # 更新阶段状态
            if result.status.value == "completed":
                stage_execution.status = BuildState.COMPLETED
            elif result.status.value == "failed":
                stage_execution.status = BuildState.FAILED
                stage_execution.error_message = result.message
            elif result.status.value == "cancelled":
                stage_execution.status = BuildState.CANCELLED

            # 保存输出文件
            stage_execution.output_files = result.output_files or []

            # 发送阶段完成信号
            success = (result.status.value == "completed")
            self.stage_complete.emit(stage_name, success)

            # 检查阶段是否失败
            if result.status.value == "failed":
                error_msg = f"阶段 {stage_name} 失败: {result.message}"
                logger.error(error_msg)
                self.log_message.emit(error_msg)
                self._build_execution.error_message = error_msg

                # 发送错误信号
                self.error_occurred.emit(
                    error_msg,
                    result.suggestions or ["检查日志获取详细信息"]
                )

                return False

        # 所有阶段完成，更新进度到 100%
        self._build_execution.progress_percent = 100
        self.progress_update.emit(100, "工作流完成")

        return True

    def _execute_stage(self, stage_config: 'StageConfig', context: BuildContext) -> StageResult:
        """执行单个阶段

        Args:
            stage_config: 阶段配置
            context: 构建上下文

        Returns:
            StageResult: 阶段执行结果
        """
        from core.workflow import STAGE_EXECUTORS  # 动态导入避免循环依赖

        stage_name = stage_config.name

        # 检查是否有对应的执行器
        if stage_name not in STAGE_EXECUTORS:
            logger.warning(f"阶段 {stage_name} 没有注册的执行器，使用占位实现")
            self.log_message.emit(f"阶段 {stage_name} 尚未实现（占位实现）")

            return StageResult(
                status=StageResult.__annotations__["status"].__class__.COMPLETED,
                message=f"阶段 {stage_name} 执行成功 (占位实现)"
            )

        # 使用注册的执行器
        executor = STAGE_EXECUTORS[stage_name]

        try:
            result = executor(stage_config, context)

            # 确保返回的是 StageResult
            if not isinstance(result, StageResult):
                logger.warning(f"阶段 {stage_name} 返回的不是 StageResult，转换为默认值")
                result = StageResult(
                    status=StageResult.__annotations__["status"].__class__.COMPLETED,
                    message=f"阶段 {stage_name} 完成"
                )

            return result

        except Exception as e:
            logger.exception(f"阶段 {stage_name} 执行异常: {e}")
            return StageResult(
                status=StageResult.__annotations__["status"].__class__.FAILED,
                message=f"阶段 {stage_name} 执行异常: {str(e)}",
                error=e,
                suggestions=["检查阶段配置", "查看日志获取详细信息"]
            )

    def get_build_execution(self) -> BuildExecution:
        """获取构建执行信息

        Returns:
            BuildExecution: 构建执行信息
        """
        return self._build_execution
