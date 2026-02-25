"""Package stage for MBD_CICDKits workflow.

This module implements the package stage which creates a timestamped target folder
for organizing build output files and moves HEX/A2L files to the target folder.

Story 2.11: 创建时间戳目标文件夹
- 任务 5: 实现文件归纳阶段执行函数
- 任务 10: 添加日志记录

Story 2.12: 移动 HEX 和 A2L 文件到目标文件夹
- 任务 5: 扩展 package 阶段执行函数（添加文件移动逻辑）
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
from utils.file_ops import create_target_folder_safe, generate_timestamp, move_output_files_safe
from utils.errors import FileOperationError, OutputFileNotFoundError

logger = logging.getLogger(__name__)


def execute_stage(config: StageConfig, context: BuildContext) -> StageResult:
    """执行文件归纳阶段 - 创建时间戳目标文件夹并移动输出文件

    Story 2.11 - 任务 5.1-5.7:
    - 接受 StageConfig 和 BuildContext 参数
    - 从 context.config 中读取目标文件路径配置
    - 调用 create_target_folder_safe() 创建目标文件夹
    - 将文件夹路径写入 context.state 供后续阶段使用

    Story 2.12 - 任务 5.1-5.10:
    - 在创建目标文件夹后，读取源文件路径配置
    - 读取 HEX 文件源路径配置
    - 读取 A2L 文件源路径配置
    - 生成时间戳（复用 generate_timestamp()）
    - 调用 move_output_files_safe() 移动所有输出文件
    - 验证所有文件移动成功
    - 将最终文件位置写入 context.state
    - 记录日志（INFO 级别：文件移动成功、最终位置）
    - 返回包含输出文件列表的 StageResult

    Story 2.11 - 任务 10.4-10.5, Story 2.12 - 任务 10.5-10.7:
    - 添加 INFO 级别日志（阶段开始/完成）
    - 添加日志记录（最终文件位置）
    - 确保日志包含时间戳和详细信息

    Args:
        config: 阶段配置参数
            - base_path: 基础路径（从 context.config 读取）
            - folder_prefix: 文件夹名称前缀（从 context.config 读取）
            - hex_source_path: HEX 文件源路径（从 context.config 读取）
            - a2l_source_path: A2L 文件源路径（从 context.config 读取）
        context: 构建上下文
            - config: 全局配置（只读）
            - state: 阶段状态（可写，用于传递目标文件夹和输出文件路径）
            - log_callback: 日志回调

    Returns:
        StageResult: 包含成功/失败、输出、错误信息、建议
            - status: COMPLETED / FAILED
            - message: 阶段执行消息
            - output_files: 创建的文件夹路径和移动的文件路径列表
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
    logger.info(f"开始文件归纳阶段")
    if context.log_callback:
        context.log_callback(f"[INFO] 开始文件归纳阶段")

    try:
        # 读取配置 (Story 2.11 - 任务 5.3, Story 2.12 - 任务 5.2-5.4)
        # 注意：项目配置中使用 target_path，而不是 target_file_path
        target_file_path = context.config.get("target_path", "")
        target_folder_prefix = context.config.get("target_folder_prefix", "MBD_CICD_Obj")

        # 获取或推导 HEX 文件源路径
        hex_source_path_str = context.config.get("hex_source_path", "")
        if not hex_source_path_str:
            # 从 iar_project_path 推导 HEX 源路径
            iar_project_path = context.config.get("iar_project_path", "")
            if iar_project_path:
                iar_path = Path(iar_project_path)
                # HEX 文件通常在 IAR 项目的父目录下的 HexMerge 文件夹
                hex_source_path_str = str(iar_path.parent / "HexMerge")
                logger.info(f"从 iar_project_path 推导 hex_source_path: {hex_source_path_str}")

        # 获取或推导 A2L 文件源路径
        a2l_source_path_str = context.config.get("a2l_source_path", "")
        if not a2l_source_path_str:
            # 优先从 context.state 获取 A2L 输出路径（A2L 处理阶段的输出）
            a2l_source_path_str = context.state.get("a2l_output_path", "")
            if not a2l_source_path_str:
                # 从 a2l_tool_path 推导 A2L 源路径
                a2l_tool_path = context.config.get("a2l_tool_path", "")
                if a2l_tool_path:
                    a2l_source_path_str = str(Path(a2l_tool_path) / "output")
                    logger.info(f"从 a2l_tool_path 推导 a2l_source_path: {a2l_source_path_str}")

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
                    "检查配置文件中的 target_path 字段",
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

        # 验证 HEX 文件源路径配置 (Story 2.12 - 任务 6.2)
        if not hex_source_path_str:
            error_msg = "HEX 文件源路径配置为空，无法自动推导"
            logger.error(error_msg)
            if context.log_callback:
                context.log_callback(f"[ERROR] {error_msg}")

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查配置文件中的 iar_project_path 字段",
                    "或直接配置 hex_source_path",
                    "确保 IAR 编译已完成"
                ]
            )

        hex_source_path = Path(hex_source_path_str)
        if not hex_source_path.exists():
            error_msg = f"HEX 文件源路径不存在: {hex_source_path}"
            logger.error(error_msg)
            if context.log_callback:
                context.log_callback(f"[ERROR] {error_msg}")

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查 IAR 编译是否成功",
                    "检查配置文件中的 hex_source_path 设置",
                    f"确保路径存在: {hex_source_path}"
                ]
            )

        # 验证 A2L 文件源路径配置 (Story 2.12 - 任务 6.3)
        # 注意：A2L 文件可能是可选的，如果没有则跳过 A2L 文件复制
        if a2l_source_path_str:
            a2l_source_path = Path(a2l_source_path_str)
            if not a2l_source_path.exists():
                # A2L 路径不存在时给出警告，但不中断流程
                logger.warning(f"A2L 文件源路径不存在: {a2l_source_path}，将跳过 A2L 文件复制")
                if context.log_callback:
                    context.log_callback(f"[WARNING] A2L 文件源路径不存在，将跳过 A2L 文件复制")
                a2l_source_path = None
        else:
            logger.info("未配置 A2L 源路径，将跳过 A2L 文件复制")
            a2l_source_path = None

        # 创建目标文件夹 (Story 2.11 - 任务 5.4)
        target_folder = create_target_folder_safe(base_path, target_folder_prefix)
        logger.info(f"目标文件夹创建成功: {target_folder}")
        if context.log_callback:
            context.log_callback(f"[INFO] 目标文件夹创建成功: {target_folder}")

        # 写入上下文状态（供后续阶段使用） (Story 2.11 - 任务 5.5)
        context.state["target_folder"] = str(target_folder)

        # 生成时间戳 (Story 2.12 - 任务 5.5)
        timestamp = generate_timestamp()
        logger.debug(f"生成时间戳: {timestamp}")

        # 移动输出文件 (Story 2.12 - 任务 5.6)
        logger.info("开始移动输出文件到目标文件夹")
        if context.log_callback:
            context.log_callback(f"[INFO] 开始移动输出文件到目标文件夹")

        success_files, failed_files = move_output_files_safe(
            hex_source_path,
            a2l_source_path if a2l_source_path else Path(),
            target_folder,
            timestamp
        )

        # 写入上下文状态 (Story 2.12 - 任务 5.8)
        context.state["output_files"] = {}
        hex_files = [f for f in success_files if f.suffix.lower() == ".hex"]
        a2l_files = [f for f in success_files if f.suffix.lower() == ".a2l"]

        if hex_files:
            context.state["output_files"]["hex"] = str(hex_files[0])
        if a2l_files:
            context.state["output_files"]["a2l"] = str(a2l_files[0])

        # 验证所有文件移动成功 (Story 2.12 - 任务 5.7)
        # 判断是否所有文件都失败
        if not success_files:
            # 所有文件都移动失败
            error_msg = "所有文件移动失败"
            suggestions = [f"{src.name}: {err}" for src, err in failed_files]

            logger.error(error_msg)
            if context.log_callback:
                context.log_callback(f"[ERROR] {error_msg}")
                for suggestion in suggestions:
                    context.log_callback(f"[ERROR]   - {suggestion}")

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                output_files=[str(target_folder)],
                error=OutputFileNotFoundError(
                    "HEX/A2L 文件",
                    file_type="HEX/A2L"
                ),
                suggestions=suggestions
            )

        # 判断是否有文件移动失败
        if failed_files:
            # 部分文件移动失败
            total_files = len(success_files) + len(failed_files)
            warning_msg = f"部分文件移动成功 ({len(success_files)}/{total_files})"
            suggestions = [f"{src.name}: {err}" for src, err in failed_files]

            logger.warning(warning_msg)
            if context.log_callback:
                context.log_callback(f"[WARNING] {warning_msg}")
                for suggestion in suggestions:
                    context.log_callback(f"[INFO]   - {suggestion}")

            # 记录最终文件位置 (Story 2.12 - 任务 10.5)
            final_hex = context.state["output_files"].get("hex", "N/A")
            final_a2l = context.state["output_files"].get("a2l", "N/A")
            logger.info(f"最终文件位置: HEX={final_hex}, A2L={final_a2l}")
            if context.log_callback:
                context.log_callback(f"[INFO] 最终文件位置: HEX={final_hex}, A2L={final_a2l}")

            # Story 2.11 - 任务 10.5, Story 2.12 - 任务 10.5: 记录阶段完成
            execution_time = time.monotonic() - start_time
            if context.log_callback:
                context.log_callback(f"[INFO] 文件归纳阶段完成，耗时 {execution_time:.2f} 秒")

            return StageResult(
                status=StageStatus.COMPLETED,
                message=warning_msg,
                output_files=[str(target_folder)] + [str(f) for f in success_files],
                suggestions=suggestions,
                execution_time=execution_time
            )

        # 所有文件移动成功
        success_msg = "文件归纳完成"

        # 记录最终文件位置 (Story 2.12 - 任务 10.5)
        final_hex = context.state["output_files"].get("hex", "N/A")
        final_a2l = context.state["output_files"].get("a2l", "N/A")
        logger.info(f"最终文件位置: HEX={final_hex}, A2L={final_a2l}")
        if context.log_callback:
            context.log_callback(f"[INFO] 最终文件位置: HEX={final_hex}, A2L={final_a2l}")

        # Story 2.11 - 任务 10.5, Story 2.12 - 任务 10.5: 记录阶段完成
        execution_time = time.monotonic() - start_time
        logger.info(success_msg)
        if context.log_callback:
            context.log_callback(f"[INFO] {success_msg}")
            context.log_callback(f"[INFO] 文件归纳阶段完成，耗时 {execution_time:.2f} 秒")

        return StageResult(
            status=StageStatus.COMPLETED,
            message=success_msg,
            output_files=[str(target_folder)] + [str(f) for f in success_files],
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
