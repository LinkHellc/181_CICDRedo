"""Package stage for MBD_CICDKits workflow.

This module implements the package stage which creates a timestamped target folder
for organizing build output files.

Story 2.11: 创建时间戳目标文件夹
- 任务 5: 实现文件归纳阶段执行函数
- 任务 10: 添加日志记录

Architecture Decision 1.1:
- 统一阶段签名: execute_stage(StageConfig, BuildContext) -> StageResult
- 返回 StageResult 对象
- 使用 BuildContext 传递状态

Architecture Decision 5.1:
- 使用 logging 模块记录日志
- 记录 INFO/WARNING/ERROR 级别日志
"""

import logging
import time
from pathlib import Path

from core.models import StageConfig, BuildContext, StageResult, StageStatus
from utils.file_ops import create_target_folder_safe
from utils.errors import FileOperationError

logger = logging.getLogger(__name__)


def execute_stage(config: StageConfig, context: BuildContext) -> StageResult:
    """执行文件归纳阶段 - 创建时间戳目标文件夹

    Story 2.11 - 任务 5.1-5.7:
    - 接受 StageConfig 和 BuildContext 参数
    - 从 context.config 中读取目标文件路径配置
    - 调用 create_target_folder_safe() 创建目标文件夹
    - 将文件夹路径写入 context.state 供后续阶段使用
    - 使用 context.log_callback 记录日志
    - 返回 StageResult 对象

    Story 2.11 - 任务 10.4-10.5:
    - 添加 INFO 级别日志（阶段开始/完成）
    - 确保日志包含时间戳和详细信息

    Args:
        config: 阶段配置参数
            - base_path: 基础路径（从 context.config 读取）
            - folder_prefix: 文件夹名称前缀（从 context.config 读取）
        context: 构建上下文
            - config: 全局配置（只读）
            - state: 阶段状态（可写，用于传递目标文件夹路径）
            - log_callback: 日志回调

    Returns:
        StageResult: 包含成功/失败、输出、错误信息、建议
            - status: COMPLETED / FAILED
            - message: 阶段执行消息
            - output_files: 创建的文件夹路径列表
            - error: 异常对象（失败时）
            - suggestions: 修复建议列表（失败时）

    Examples:
        >>> config = StageConfig(name="package")
        >>> context = BuildContext()
        >>> context.config = {"target_file_path": "/tmp/build", "target_folder_prefix": "MBD_CICD_Obj"}
        >>> result = execute_stage(config, context)
        >>> assert result.status == StageStatus.COMPLETED
        >>> assert "target_folder" in context.state
    """
    stage_name = config.name
    start_time = time.monotonic()

    # Story 2.11 - 任务 10.4: 记录阶段开始
    logger.info(f"开始文件归纳阶段：创建时间戳目标文件夹")
    if context.log_callback:
        context.log_callback(f"[INFO] 开始文件归纳阶段：创建时间戳目标文件夹")

    try:
        # 读取配置 (Story 2.11 - 任务 5.3)
        target_file_path = context.config.get("target_file_path", "")
        target_folder_prefix = context.config.get("target_folder_prefix", "MBD_CICD_Obj")

        # 验证配置 (Story 2.11 - 任务 6.2)
        if not target_file_path:
            error_msg = "目标文件路径配置为空"
            logger.error(error_msg)
            if context.log_callback:
                context.log_callback(f"[ERROR] {error_msg}")

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查配置文件中的 target_file_path 字段",
                    "确保配置已正确保存"
                ]
            )

        base_path = Path(target_file_path)

        # 验证基础路径是否存在
        if not base_path.exists():
            error_msg = f"目标文件路径不存在: {base_path}"
            logger.error(error_msg)
            if context.log_callback:
                context.log_callback(f"[ERROR] {error_msg}")

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "创建目标目录",
                    "检查配置文件中的路径设置",
                    f"确保路径存在: {base_path}"
                ]
            )

        # 创建目标文件夹 (Story 2.11 - 任务 5.4)
        target_folder = create_target_folder_safe(base_path, target_folder_prefix)

        # 写入上下文状态（供后续阶段使用） (Story 2.11 - 任务 5.5)
        context.state["target_folder"] = str(target_folder)

        # Story 2.11 - 任务 10.5: 记录阶段完成
        execution_time = time.monotonic() - start_time
        success_msg = f"目标文件夹创建成功: {target_folder}"
        logger.info(success_msg)
        if context.log_callback:
            context.log_callback(f"[INFO] {success_msg}")
            context.log_callback(f"[INFO] 文件归纳阶段完成，耗时 {execution_time:.2f} 秒")

        return StageResult(
            status=StageStatus.COMPLETED,
            message="目标文件夹创建成功",
            output_files=[str(target_folder)],
            execution_time=execution_time
        )

    except FileOperationError as e:
        # 文件操作错误（包含 FolderCreationError）
        execution_time = time.monotonic() - start_time
        logger.error(f"文件操作失败: {e}")
        if context.log_callback:
            context.log_callback(f"[ERROR] 文件操作失败: {e}")
            if e.suggestions:
                context.log_callback(f"[INFO] 建议操作:")
                for suggestion in e.suggestions:
                    context.log_callback(f"[INFO]   - {suggestion}")

        return StageResult(
            status=StageStatus.FAILED,
            message=str(e),
            error=e,
            suggestions=e.suggestions,
            execution_time=execution_time
        )

    except Exception as e:
        # 未知错误
        execution_time = time.monotonic() - start_time
        logger.error(f"未知错误: {e}", exc_info=True)
        if context.log_callback:
            context.log_callback(f"[ERROR] 未知错误: {e}")

        return StageResult(
            status=StageStatus.FAILED,
            message=f"未知错误: {str(e)}",
            error=e,
            suggestions=["查看详细日志", "联系技术支持"],
            execution_time=execution_time
        )
