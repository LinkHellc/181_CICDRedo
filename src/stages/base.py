"""Base stage interface for MBD_CICDKits workflow stages.

This module defines the base interface for all workflow stages following
Architecture Decision 1.1 (Stage Interface Pattern).

All stages must implement the execute_stage function with the signature:
    def execute_stage(
        config: StageConfig,
        context: BuildContext
    ) -> StageResult
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from core.models import StageConfig, BuildContext, StageResult, StageStatus

logger = logging.getLogger(__name__)


class StageBase(ABC):
    """工作流阶段基类

    定义所有工作流阶段必须实现的接口。

    Architecture Decision 1.1:
    - 统一阶段签名
    - 返回 StageResult 对象
    - 支持取消检查

    Attributes:
        name: 阶段名称
        timeout: 超时时间（秒）
    """

    def __init__(self, name: str, timeout: int = 300):
        """初始化阶段

        Args:
            name: 阶段名称
            timeout: 超时时间（秒）
        """
        self.name = name
        self.timeout = timeout

    @abstractmethod
    def execute(self, config: StageConfig, context: BuildContext) -> StageResult:
        """执行阶段

        子类必须实现此方法。

        Args:
            config: 阶段配置
            context: 构建上下文

        Returns:
            StageResult: 阶段执行结果
        """
        pass

    def validate_preconditions(self, config: StageConfig, context: BuildContext) -> Optional[str]:
        """验证执行前条件

        子类可以重写此方法以添加自定义验证。

        Args:
            config: 阶段配置
            context: 构建上下文

        Returns:
            None 如果验证通过，否则返回错误消息
        """
        return None


def execute_stage(
    config: StageConfig,
    context: BuildContext,
    stage_impl: Optional[StageBase] = None
) -> StageResult:
    """执行阶段的通用入口函数

    这是所有阶段执行的统一入口点。

    Architecture Decision 1.1:
    - 统一阶段签名
    - 返回 StageResult 对象
    - 记录执行日志

    Args:
        config: 阶段配置
        context: 构建上下文
        stage_impl: 阶段实现实例（如果为 None，则查找对应阶段类）

    Returns:
        StageResult: 阶段执行结果
    """
    stage_name = config.name
    context.log(f"开始执行阶段: {stage_name}")

    # 如果没有提供实现，返回占位结果
    # 后续 Story 会实现具体阶段
    if stage_impl is None:
        context.log(f"阶段 {stage_name} 尚未实现（占位实现）")
        return StageResult(
            status=StageStatus.COMPLETED,
            message=f"阶段 {stage_name} 执行成功 (占位实现)"
        )

    try:
        # 验证前条件
        error = stage_impl.validate_preconditions(config, context)
        if error:
            context.log(f"阶段 {stage_name} 前条件验证失败: {error}")
            return StageResult(
                status=StageStatus.FAILED,
                message=f"前条件验证失败: {error}",
                suggestions=["检查配置是否正确", "查看日志获取详细信息"]
            )

        # 执行阶段
        result = stage_impl.execute(config, context)

        context.log(f"阶段 {stage_name} 完成: {result.status.value}")
        return result

    except Exception as e:
        logger.error(f"阶段 {stage_name} 执行异常: {e}", exc_info=True)
        context.log(f"阶段 {stage_name} 执行异常: {e}")

        return StageResult(
            status=StageStatus.FAILED,
            message=f"阶段执行异常: {str(e)}",
            error=e,
            suggestions=["查看日志获取详细信息", "检查配置和环境"]
        )
