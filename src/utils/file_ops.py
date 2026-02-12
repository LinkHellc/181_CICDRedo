"""File operations utility module for MBD_CICDKits.

This module provides file operation utilities for the build workflow.

Story 2.6 - 任务 1: 创建文件处理工具模块
- 实现 extract_source_files() 函数
- 使用 pathlib.Path 处理路径
- 支持递归文件搜索
- 支持排除指定文件

Architecture Decision 4.2:
- 使用 pathlib.Path 处理 Windows 长路径
- 提供可预测的排序输出
"""

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def extract_source_files(
    base_dir: Path,
    extensions: List[str],
    exclude: Optional[List[str]] = None
) -> List[Path]:
    """从指定目录递归提取源文件

    Story 2.6 - 任务 1.2-1.6:
    - 使用 Path.rglob() 递归搜索文件
    - 按扩展名过滤文件
    - 排除指定文件（默认排除 Rte_TmsApp.h）
    - 返回排序后的文件列表

    Args:
        base_dir: 基础搜索目录
        extensions: 要提取的文件扩展名列表（如 [".c", ".h"]）
        exclude: 要排除的文件名列表（可选，默认排除 Rte_TmsApp.h）

    Returns:
        排序后的文件路径列表（相对于 base_dir）

    Examples:
        >>> base = Path("/project")
        >>> files = extract_source_files(base, [".c", ".h"])
        >>> len(files)
        42

        >>> # 自定义排除文件
        >>> files = extract_source_files(base, [".c"], exclude=["test.c"])
    """
    # 默认排除 Rte_TmsApp.h（Story 2.6 - 任务 1.5）
    if exclude is None:
        exclude = ["Rte_TmsApp.h"]

    # 如果目录不存在，返回空列表
    if not base_dir.exists():
        logger.warning(f"目录不存在: {base_dir}")
        return []

    # 确保扩展名格式统一（以点开头）
    normalized_extensions = []
    for ext in extensions:
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized_extensions.append(ext.lower())

    # 递归搜索所有文件 (Story 2.6 - 任务 1.3)
    all_files = base_dir.rglob("*")

    # 按扩展名和排除列表过滤 (Story 2.6 - 任务 1.4, 1.5)
    matched_files = []
    for file_path in all_files:
        # 只处理文件（跳过目录）
        if not file_path.is_file():
            continue

        # 检查扩展名是否匹配
        if file_path.suffix.lower() not in normalized_extensions:
            continue

        # 检查是否在排除列表中
        if file_path.name in exclude:
            logger.debug(f"排除文件: {file_path}")
            continue

        matched_files.append(file_path)

    # 返回排序后的文件列表 (Story 2.6 - 任务 1.6)
    # 排序确保可预测的处理顺序
    matched_files.sort()

    logger.info(f"从 {base_dir} 提取了 {len(matched_files)} 个文件（扩展名: {extensions}）")

    return matched_files


def backup_file(file_path: Path) -> Path:
    """创建文件备份

    Story 2.6 - 任务 7.1-7.3:
    - 创建 .bak 备份文件
    - 验证备份创建成功

    Args:
        file_path: 要备份的文件路径

    Returns:
        备份文件路径

    Raises:
        FileNotFoundError: 原文件不存在
        OSError: 备份创建失败
    """
    if not file_path.exists():
        raise FileNotFoundError(f"无法备份不存在的文件: {file_path}")

    backup_path = Path(str(file_path) + ".bak")

    # 如果备份已存在，先删除
    if backup_path.exists():
        backup_path.unlink()

    # 复制文件到备份位置
    import shutil
    shutil.copy2(file_path, backup_path)

    # 验证备份创建成功
    if not backup_path.exists():
        raise OSError(f"备份文件创建失败: {backup_path}")

    logger.debug(f"创建备份: {backup_path}")
    return backup_path


def restore_from_backup(file_path: Path, backup_path: Path) -> bool:
    """从备份恢复文件

    Story 2.6 - 任务 7.4:
    - 修改失败时从备份恢复

    Args:
        file_path: 要恢复的文件路径
        backup_path: 备份文件路径

    Returns:
        是否恢复成功
    """
    if not backup_path.exists():
        logger.warning(f"备份文件不存在，无法恢复: {backup_path}")
        return False

    try:
        import shutil
        shutil.copy2(backup_path, file_path)
        logger.debug(f"从备份恢复: {file_path}")
        return True
    except Exception as e:
        logger.error(f"恢复失败: {e}")
        return False


def detect_file_encoding(file_path: Path) -> str:
    """检测文件编码

    Story 2.6 - 任务 2.6:
    - 处理 UTF-8, UTF-8-BOM, GBK 等编码

    Args:
        file_path: 文件路径

    Returns:
        检测到的编码名称（默认 utf-8）
    """
    # 尝试常见编码
    encodings = ["utf-8", "utf-8-sig", "gbk", "latin-1"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                # 读取一小块内容测试
                f.read(1024)
            return encoding
        except UnicodeDecodeError:
            continue

    # 如果都失败，使用 utf-8 并替换错误字符
    logger.warning(f"无法确定文件编码，使用 utf-8 替换模式: {file_path}")
    return "utf-8"


def read_file_with_encoding(file_path: Path) -> str:
    """读取文件内容（自动检测编码）

    Args:
        file_path: 文件路径

    Returns:
        文件内容字符串

    Raises:
        FileNotFoundError: 文件不存在
        UnicodeDecodeError: 所有编码尝试失败
    """
    encoding = detect_file_encoding(file_path)
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


def write_file_with_encoding(
    file_path: Path,
    content: str,
    encoding: str = "utf-8"
) -> None:
    """写入文件内容（指定编码）

    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 文件编码（默认 utf-8）

    Raises:
        OSError: 写入失败
    """
    with open(file_path, "w", encoding=encoding, newline="\n") as f:
        f.write(content)


def clear_directory_safely(
    target_dir: Path,
    backup: bool = False,
    create_if_missing: bool = False
) -> list:
    """安全清空目录

    Story 2.7 - 任务 2.1-2.5:
    - 支持可选备份功能
    - 记录清空的文件列表
    - 处理目录不存在的情况（自动创建）
    - 使用 pathlib.Path 处理所有路径

    Args:
        target_dir: 目标目录路径
        backup: 是否在清空前备份（默认 False）
        create_if_missing: 目录不存在时是否自动创建（默认 False）

    Returns:
        清空的文件路径列表

    Raises:
        OSError: 目录创建失败
    """
    import shutil

    cleared_files = []

    # 处理目录不存在的情况 (Story 2.7 - 任务 2.4)
    if not target_dir.exists():
        if create_if_missing:
            target_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录: {target_dir}")
            return cleared_files
        else:
            logger.warning(f"目录不存在: {target_dir}")
            return cleared_files

    # 确保是目录
    if not target_dir.is_dir():
        logger.warning(f"路径不是目录: {target_dir}")
        return cleared_files

    # 如果目录为空，直接返回
    try:
        items = list(target_dir.iterdir())
        if not items:
            logger.debug(f"目录已为空: {target_dir}")
            return cleared_files
    except PermissionError:
        logger.error(f"无权限访问目录: {target_dir}")
        return cleared_files

    # 创建备份 (Story 2.7 - 任务 2.2)
    backup_dir = None
    if backup:
        backup_dir = Path(str(target_dir) + ".bak")
        # 删除旧备份
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        # 创建新备份
        shutil.copytree(target_dir, backup_dir)
        logger.info(f"创建备份: {backup_dir}")

    # 清空目录 (Story 2.7 - 任务 2.1)
    try:
        for item in items:
            cleared_files.append(item)
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        logger.info(f"清空目录: {target_dir} ({len(cleared_files)} 项)")
        return cleared_files

    except Exception as e:
        logger.error(f"清空目录失败: {e}")
        # 如果失败且已备份，尝试恢复
        if backup and backup_dir and backup_dir.exists():
            try:
                # 恢复备份
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(backup_dir, target_dir)
                logger.info(f"从备份恢复: {target_dir}")
            except Exception as restore_error:
                logger.error(f"恢复备份失败: {restore_error}")
        raise


def verify_file_moved(src_file: Path, dst_file: Path) -> dict:
    """验证文件移动成功性

    Story 2.7 - 任务 3.1-3.5:
    - 验证文件存在性
    - 验证文件大小一致性
    - 验证文件可读性
    - 生成验证报告

    Args:
        src_file: 源文件路径
        dst_file: 目标文件路径

    Returns:
        验证报告字典，包含:
        - verified: 总体验证结果
        - exists: 目标文件是否存在
        - size_match: 文件大小是否一致
        - readable: 文件是否可读
        - src_size: 源文件大小
        - dst_size: 目标文件大小
        - error: 错误信息（仅当验证失败时）
    """
    report = {
        "verified": False,
        "exists": False,
        "size_match": False,
        "readable": False,
        "src_size": 0,
        "dst_size": 0
    }

    try:
        # 获取源文件大小
        if src_file.exists():
            report["src_size"] = src_file.stat().st_size
        else:
            report["error"] = "源文件不存在"
            return report

        # 验证目标文件存在性 (Story 2.7 - 任务 3.2)
        if not dst_file.exists():
            report["error"] = "目标文件不存在"
            return report
        report["exists"] = True

        # 验证文件大小一致性 (Story 2.7 - 任务 3.3)
        report["dst_size"] = dst_file.stat().st_size
        if report["src_size"] != report["dst_size"]:
            report["error"] = f"文件大小不匹配 (源: {report['src_size']}, 目标: {report['dst_size']})"
            return report
        report["size_match"] = True

        # 验证文件可读性 (Story 2.7 - 任务 3.4)
        try:
            with open(dst_file, "rb") as f:
                f.read(1)  # 尝试读取1字节
            report["readable"] = True
        except Exception as e:
            report["error"] = f"文件不可读: {e}"
            return report

        # 所有验证通过
        report["verified"] = True
        logger.debug(f"文件验证通过: {dst_file.name}")
        return report

    except Exception as e:
        report["error"] = f"验证过程异常: {e}"
        logger.error(f"文件验证异常: {e}")
        return report


def move_code_files(
    source_files: list,
    target_dir: Path,
    clear_target_first: bool = True,
    backup_before_clear: bool = True,
    create_target_if_missing: bool = True,
    verify_after_move: bool = True,
    skip_verification: bool = False
) -> dict:
    """移动代码文件到目标目录

    Story 2.7 - 任务 1.1-1.5:
    - 实现原子性文件移动（复制-验证-删除）
    - 验证每个文件移动的成功性
    - 使用 pathlib.Path 处理所有路径
    - 支持清空目标目录
    - 支持备份功能

    Args:
        source_files: 源文件路径列表（Path 对象）
        target_dir: 目标目录路径
        clear_target_first: 移动前是否清空目标目录（默认 True）
        backup_before_clear: 清空前是否备份（默认 True）
        create_target_if_missing: 目标目录不存在时是否创建（默认 True）
        verify_after_move: 移动后是否验证（默认 True）
        skip_verification: 跳过验证（默认 False，不推荐）

    Returns:
        移动结果字典，包含:
        - success: 总体是否成功
        - moved_count: 成功移动的文件数量
        - failed_count: 失败的文件数量
        - moved_files: 成功移动的文件路径列表
        - failed_files: 失败的文件路径列表
        - target_dir: 目标目录路径
        - timestamp: 操作时间戳
    """
    import shutil
    import time

    result = {
        "success": False,
        "moved_count": 0,
        "failed_count": 0,
        "moved_files": [],
        "failed_files": [],
        "target_dir": target_dir,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        # 确保目标目录存在 (Story 2.7 - 任务 1.2)
        if not target_dir.exists():
            if create_target_if_missing:
                target_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建目标目录: {target_dir}")
            else:
                result["error"] = f"目标目录不存在: {target_dir}"
                return result

        # 清空目标目录 (Story 2.7 - 任务 1.2)
        if clear_target_first:
            logger.info(f"清空目标目录: {target_dir}")
            clear_directory_safely(
                target_dir,
                backup=backup_before_clear,
                create_if_missing=True
            )

        # 移动每个文件 (Story 2.7 - 任务 1.3 - 原子性操作)
        moved_in_session = []  # 跟踪本次会话移动的文件

        for src_file in source_files:
            try:
                # 确保是 Path 对象
                if not isinstance(src_file, Path):
                    src_file = Path(src_file)

                # 检查源文件是否存在
                if not src_file.exists():
                    logger.warning(f"源文件不存在，跳过: {src_file}")
                    result["failed_files"].append(str(src_file))
                    result["failed_count"] += 1
                    continue

                # 目标文件路径
                dst_file = target_dir / src_file.name

                # 第一步：复制文件到目标 (Story 2.7 - 任务 1.3)
                shutil.copy2(src_file, dst_file)
                logger.debug(f"复制文件: {src_file} -> {dst_file}")

                # 第二步：验证移动 (Story 2.7 - 任务 1.4)
                if verify_after_move and not skip_verification:
                    verify_report = verify_file_moved(src_file, dst_file)
                    if not verify_report["verified"]:
                        # 验证失败，删除目标文件
                        if dst_file.exists():
                            dst_file.unlink()
                        result["failed_files"].append(str(src_file))
                        result["failed_count"] += 1
                        logger.error(f"文件验证失败: {src_file} - {verify_report.get('error')}")
                        continue

                # 第三步：删除源文件 (Story 2.7 - 任务 1.3)
                src_file.unlink()
                moved_in_session.append(dst_file)
                result["moved_files"].append(str(dst_file))
                result["moved_count"] += 1
                logger.debug(f"删除源文件: {src_file}")

            except Exception as e:
                # 单个文件移动失败，进行回滚
                logger.error(f"移动文件失败: {src_file} - {e}")

                # 回滚已移动的文件 (Story 2.7 - 任务 5.3)
                if moved_in_session:
                    logger.info(f"回滚已移动的 {len(moved_in_session)} 个文件")
                    for moved_file in moved_in_session:
                        try:
                            if moved_file.exists():
                                moved_file.unlink()
                                logger.debug(f"回滚删除: {moved_file}")
                        except Exception as rollback_error:
                            logger.error(f"回滚失败: {moved_file} - {rollback_error}")

                result["failed_files"].append(str(src_file))
                result["failed_count"] += 1
                result["error"] = f"文件移动失败: {e}"
                return result

        # 所有文件移动成功
        result["success"] = True
        logger.info(f"文件移动完成: {result['moved_count']} 个成功")

        return result

    except Exception as e:
        logger.error(f"文件移动异常: {e}")
        result["error"] = f"移动过程异常: {e}"
        result["success"] = False
        return result
