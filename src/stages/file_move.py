"""File move stage for MBD_CICDKits.

This module implements file move stage that:
- Moves processed code files to MATLAB code directory
- Clears target directory before moving (optional backup)
- Verifies each file move operation
- Implements atomic copy-verify-delete pattern

Story 2.7 - 移动代码文件到指定目录

Architecture Decision 1.1:
- 统一阶段签名: execute_stage(config, context) -> result
- 返回 StageResult 对象
- 通过 BuildContext 传递状态

Architecture Decision 4.1:
- 原子性文件操作（复制-验证-删除）
- 失败时回滚已移动的文件
"""

import logging
import time
from pathlib import Path
from typing import Optional

from core.models import (
    StageConfig,
    BuildContext,
    StageResult,
    StageStatus
)
from core.constants import get_stage_timeout
from utils.file_ops import (
    move_code_files,
    clear_directory_safely
)
from utils.errors import (
    FileError,
    DirectoryNotWritableError,
    DiskSpaceError,
    FileVerificationError
)

logger = logging.getLogger(__name__)


def _check_disk_space(source_files: list, target_dir: Path) -> tuple:
    """检查磁盘空间是否足够

    Story 2.7 - 任务 5.2:
    - 计算源文件总大小
    - 检查目标磁盘可用空间
    - 空间不足时抛出错误

    Args:
        source_files: 源文件列表
        target_dir: 目标目录

    Returns:
        (needed_mb, available_mb) 磁盘空间信息

    Raises:
        DiskSpaceError: 磁盘空间不足
    """
    import shutil

    # 计算源文件总大小
    total_size = 0
    for file_path in source_files:
        if isinstance(file_path, str):
            file_path = Path(file_path)
        if file_path.exists():
            total_size += file_path.stat().st_size

    needed_mb = total_size / (1024 * 1024)

    # 检查目标磁盘可用空间
    try:
        stat = shutil.disk_usage(target_dir)
        available_mb = stat.free / (1024 * 1024)

        # 检查空间是否足够（保留 10% 缓冲）
        if needed_mb > available_mb * 0.9:
            raise DiskSpaceError(needed_mb, available_mb)

        return needed_mb, available_mb

    except Exception as e:
        logger.warning(f"无法检查磁盘空间: {e}")
        return needed_mb, 0


def _check_target_writable(target_dir: Path) -> bool:
    """检查目标目录是否可写

    Story 2.7 - 任务 5.1:
    - 尝试在目标目录创建测试文件
    - 验证目录权限

    Args:
        target_dir: 目标目录路径

    Returns:
        是否可写

    Raises:
        DirectoryNotWritableError: 目录不可写
    """
    if not target_dir.exists():
        return True  # 目录不存在，后续会创建

    try:
        # 尝试创建测试文件
        test_file = target_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True
    except (PermissionError, OSError) as e:
        raise DirectoryNotWritableError(str(target_dir))


def execute_stage(config: StageConfig, context: BuildContext) -> StageResult:
    """执行文件移动阶段

    Story 2.7 - 任务 4.1-4.5:
    - 从 context.state["processed_files"] 读取文件列表
    - 从 context.config 读取目标目录路径
    - 调用 move_code_files() 移动文件
    - 将移动后的文件列表保存到 context.state["moved_files"]
    - 记录操作日志

    Args:
        config: 阶段配置
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    stage_name = "file_move"
    context.log(f"=== 开始执行阶段: {stage_name} ===")

    # 记录开始时间
    start_time = time.monotonic()

    try:
        # 获取处理后的文件列表 (Story 2.7 - 任务 4.3)
        processed_files = context.state.get("processed_files", {})

        if not processed_files:
            return StageResult(
                status=StageStatus.FAILED,
                message="未找到处理后的文件",
                suggestions=[
                    "确保文件处理阶段已完成",
                    "检查 context.state['processed_files'] 是否存在"
                ]
            )

        # 收集所有源文件
        c_files = processed_files.get("c_files", [])
        h_files = processed_files.get("h_files", [])

        # 转换为 Path 对象
        source_files = []
        for f in c_files + h_files:
            if isinstance(f, str):
                source_files.append(Path(f))
            elif isinstance(f, Path):
                source_files.append(f)

        if not source_files:
            return StageResult(
                status=StageStatus.FAILED,
                message="没有需要移动的文件",
                suggestions=[
                    "检查文件处理阶段输出",
                    "验证 processed_files 配置"
                ]
            )

        context.log(f"找到 {len(source_files)} 个文件需要移动")

        # 获取目标目录 (Story 2.7 - 任务 4.4)
        target_dir_str = context.config.get("matlab_code_path", "")

        if not target_dir_str:
            return StageResult(
                status=StageStatus.FAILED,
                message="未配置 MATLAB 代码路径",
                suggestions=[
                    "在项目配置中设置 matlab_code_path",
                    "检查配置文件"
                ]
            )

        target_dir = Path(target_dir_str)

        context.log(f"目标目录: {target_dir}")

        # 检查目标目录可写性 (Story 2.7 - 任务 5.1)
        context.log("检查目标目录权限...")
        _check_target_writable(target_dir)
        context.log("目标目录权限检查通过")

        # 检查磁盘空间 (Story 2.7 - 任务 5.2)
        context.log("检查磁盘空间...")
        needed_mb, available_mb = _check_disk_space(source_files, target_dir)
        context.log(f"磁盘空间: 需要 {needed_mb:.1f}MB，可用 {available_mb:.1f}MB")

        # 移动文件 (Story 2.7 - 任务 4.5)
        context.log("开始移动文件...")
        move_result = move_code_files(
            source_files=source_files,
            target_dir=target_dir,
            clear_target_first=True,  # 清空目标目录
            backup_before_clear=True,  # 清空前备份
            create_target_if_missing=True,  # 自动创建目录
            verify_after_move=True  # 验证移动
        )

        # 检查移动结果
        if not move_result["success"]:
            error_msg = move_result.get("error", "未知错误")
            failed_count = move_result.get("failed_count", 0)

            context.log(f"文件移动失败: {error_msg}")

            return StageResult(
                status=StageStatus.FAILED,
                message=f"文件移动失败: {failed_count} 个文件移动失败",
                suggestions=[
                    "检查磁盘空间",
                    "验证文件权限",
                    "查看日志获取详细信息"
                ]
            )

        # 保存移动后的文件列表到 context.state (Story 2.7 - 任务 4.5)
        moved_files_info = {
            "c_files": [str(f) for f in source_files if f.suffix == ".c"],
            "h_files": [str(f) for f in source_files if f.suffix == ".h"],
            "target_dir": str(target_dir),
            "move_count": move_result["moved_count"],
            "timestamp": move_result["timestamp"]
        }

        context.state["moved_files"] = moved_files_info

        # 计算执行时间
        duration = time.monotonic() - start_time

        context.log(f"文件移动完成，耗时: {duration:.2f} 秒")
        context.log(f"  - 移动文件: {move_result['moved_count']} 个")
        context.log(f"  - C 文件: {len(moved_files_info['c_files'])} 个")
        context.log(f"  - 头文件: {len(moved_files_info['h_files'])} 个")

        return StageResult(
            status=StageStatus.COMPLETED,
            message=f"文件移动成功（耗时 {duration:.2f} 秒）",
            output_files=moved_files_info["c_files"] + moved_files_info["h_files"],
            execution_time=duration
        )

    except DirectoryNotWritableError as e:
        logger.error(f"目标目录不可写: {e}")
        context.log(f"错误: {e}")
        return StageResult(
            status=StageStatus.FAILED,
            message="目标目录不可写",
            error=e,
            suggestions=e.suggestions
        )

    except DiskSpaceError as e:
        logger.error(f"磁盘空间不足: {e}")
        context.log(f"错误: {e}")
        return StageResult(
            status=StageStatus.FAILED,
            message="磁盘空间不足",
            error=e,
            suggestions=e.suggestions
        )

    except FileError as e:
        logger.error(f"文件操作错误: {e}")
        context.log(f"错误: {e}")
        return StageResult(
            status=StageStatus.FAILED,
            message="文件操作失败",
            error=e,
            suggestions=e.suggestions
        )

    except Exception as e:
        logger.error(f"阶段执行异常: {e}", exc_info=True)
        context.log(f"阶段执行异常: {e}")

        return StageResult(
            status=StageStatus.FAILED,
            message=f"阶段执行异常: {str(e)}",
            error=e,
            suggestions=["查看日志获取详细信息", "检查配置和环境"]
        )


def get_stage_info() -> dict:
    """获取阶段信息

    Returns:
        dict: 阶段信息字典
    """
    return {
        "name": "file_move",
        "display_name": "文件移动",
        "description": "移动处理后的代码文件到 MATLAB 代码目录",
        "required_params": ["matlab_code_path"],
        "optional_params": [],
        "outputs": ["moved_files"],
        "inputs": ["processed_files"]
    }
