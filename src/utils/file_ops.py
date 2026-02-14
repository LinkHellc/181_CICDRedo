"""File operations utility module for MBD_CICDKits.

This module provides file operation utilities for the build workflow.

Story 2.6 - 任务 1: 创建文件处理工具模块
- 实现 extract_source_files() 函数
- 使用 pathlib.Path 处理路径
- 支持递归文件搜索
- 支持排除指定文件

Story 2.11 - 任务 1-4: 创建时间戳目标文件夹
- 实现 generate_timestamp() 函数（时间戳生成）
- 实现 create_target_folder() 函数（文件夹创建）
- 实现 check_folder_exists() 函数（冲突处理）
- 实现 create_target_folder_safe() 函数（安全创建）

Architecture Decision 4.2:
- 使用 pathlib.Path 处理 Windows 长路径
- 提供可预测的排序输出
"""

import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import shutil

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


# =============================================================================
# Story 2.11: 创建时间戳目标文件夹
# =============================================================================

def generate_timestamp() -> str:
    """生成时间戳

    Story 2.11 - 任务 1.1-1.3:
    - 使用 datetime.now() 获取当前时间
    - 格式化时间戳为 _年_月_日_时_分 格式

    Architecture Decision 5.1:
    - 使用 datetime 模块生成标准格式
    - 格式字符串: _%Y_%m_%d_%H_%M

    Returns:
        str: 时间戳格式为 _年_月_日_时_分，如 _2025_02_02_15_43

    Examples:
        >>> ts = generate_timestamp()
        >>> assert ts.startswith("_")
        >>> assert len(ts) == 16  # _YYYY_MM_DD_HH_MM
    """
    return datetime.now().strftime("_%Y_%m_%d_%H_%M")


def create_target_folder(base_path: Path, folder_prefix: str) -> Path:
    """创建目标文件夹（不处理冲突）

    Story 2.11 - 任务 2.1-2.5:
    - 接受基础路径和文件夹名称前缀参数
    - 调用 generate_timestamp() 生成时间戳
    - 拼接完整路径：基础路径/前缀[_时间戳]
    - 使用 pathlib.Path 创建目录（包含父目录）

    Args:
        base_path: 基础路径（如 Path("E:/Projects/BuildOutput")）
        folder_prefix: 文件夹名称前缀（如 "MBD_CICD_Obj"）

    Returns:
        Path: 创建的文件夹路径

    Raises:
        FileExistsError: 文件夹已存在

    Examples:
        >>> from pathlib import Path
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     result = create_target_folder(Path(tmpdir), "TestFolder")
        ...     assert result.exists()
        ...     assert result.name.startswith("TestFolder_")
    """
    timestamp = generate_timestamp()
    folder_name = f"{folder_prefix}{timestamp}"
    folder_path = base_path / folder_name
    folder_path.mkdir(parents=True, exist_ok=False)
    logger.debug(f"创建目标文件夹: {folder_path}")
    return folder_path


def check_folder_exists(folder_path: Path, max_attempts: int = 100) -> Path:
    """检查文件夹是否存在，如果存在则添加后缀

    Story 2.11 - 任务 3.1-3.4:
    - 检查目标路径是否存在
    - 如果不存在，直接返回原路径
    - 如果存在，添加递增后缀：MBD_CICD_Obj[_时间戳]_1, _2, _3...

    Args:
        folder_path: 目标文件夹路径
        max_attempts: 最大重试次数（默认 100）

    Returns:
        Path: 可用的文件夹路径（可能添加了后缀）

    Raises:
        FileOperationError: 已尝试 max_attempts 次仍无法创建

    Examples:
        >>> from pathlib import Path
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     base = Path(tmpdir)
        ...     folder1 = base / "TestFolder_2025_02_02_15_43"
        ...     folder1.mkdir()
        ...     # 第一个已存在，应该添加 _1 后缀
        ...     result = check_folder_exists(folder1)
        ...     assert result.name == "TestFolder_2025_02_02_15_43_1"
    """
    if not folder_path.exists():
        return folder_path

    base = folder_path.stem
    suffix = folder_path.suffix
    parent = folder_path.parent

    for i in range(1, max_attempts + 1):
        new_name = f"{base}_{i}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            logger.debug(f"检测到冲突，使用后缀: {new_name}")
            return new_path

    # 所有重试都失败
    from utils.errors import FileOperationError
    raise FileOperationError(
        f"无法创建文件夹，已尝试 {max_attempts} 次",
        suggestions=[
            f"检查是否有大量同名文件夹",
            f"手动清理 {parent}",
            "选择其他目标目录"
        ]
    )


def create_target_folder_safe(
    base_path: Path,
    folder_prefix: str = "MBD_CICD_Obj",
    max_attempts: int = 100
) -> Path:
    """安全创建目标文件夹（处理冲突和错误）

    Story 2.11 - 任务 4.1-4.5:
    - 集成时间戳生成、文件夹创建、冲突处理逻辑
    - 返回最终创建的文件夹路径
    - 使用 try-except 捕获文件系统错误
    - 使用 logging 模块记录操作日志

    Args:
        base_path: 基础路径
        folder_prefix: 文件夹名称前缀（默认 "MBD_CICD_Obj"）
        max_attempts: 最大重试次数（默认 100）

    Returns:
        Path: 最终创建的文件夹路径

    Raises:
        FileOperationError: 文件操作失败
        FolderCreationError: 文件夹创建失败

    Examples:
        >>> from pathlib import Path
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     result = create_target_folder_safe(Path(tmpdir), "TestFolder")
        ...     assert result.exists()
        ...     assert result.name.startswith("TestFolder_")
    """
    try:
        timestamp = generate_timestamp()
        folder_name = f"{folder_prefix}{timestamp}"
        folder_path = base_path / folder_name

        # 检查冲突 (Story 2.11 - 任务 4.2)
        folder_path = check_folder_exists(folder_path, max_attempts)

        # 创建文件夹 (Story 2.11 - 任务 4.2)
        folder_path.mkdir(parents=True, exist_ok=False)

        logger.info(f"目标文件夹创建成功: {folder_path}")
        return folder_path

    except PermissionError as e:
        logger.error(f"文件夹创建失败（权限不足）: {folder_path} - {e}")
        from utils.errors import FolderCreationError
        raise FolderCreationError(
            str(folder_path),
            reason="权限不足"
        )

    except OSError as e:
        # 检查是否是磁盘空间不足
        if "No space left" in str(e):
            logger.error(f"文件夹创建失败（磁盘空间不足）: {folder_path} - {e}")
            from utils.errors import FolderCreationError
            raise FolderCreationError(
                str(folder_path),
                reason="磁盘空间不足"
            )
        # 检查是否是路径不存在
        elif "No such file" in str(e):
            logger.error(f"文件夹创建失败（路径不存在）: {folder_path} - {e}")
            from utils.errors import FolderCreationError
            raise FolderCreationError(
                str(folder_path),
                reason="路径不存在"
            )
        else:
            logger.error(f"文件夹创建失败: {folder_path} - {e}")
            from utils.errors import FileOperationError
            raise FileOperationError(
                f"文件夹创建失败: {e}",
                suggestions=[
                    "检查磁盘空间",
                    "检查目录权限",
                    "查看详细日志"
                ]
            )

    except Exception as e:
        logger.error(f"文件夹创建失败（未知错误）: {folder_path} - {e}")
        from utils.errors import FileOperationError
        raise FileOperationError(
            f"文件夹创建失败: {e}",
            suggestions=[
                "查看详细日志",
                "联系技术支持"
            ]
        )


# =============================================================================
# Story 2.12: 移动 HEX 和 A2L 文件到目标文件夹
# =============================================================================

def locate_output_files(source_path: Path, file_type: str = "hex") -> List[Path]:
    """定位输出文件

    Story 2.12 - 任务 1.1-1.5:
    - 接受源路径和文件类型参数（HEX/A2L）
    - 使用 pathlib.Path.glob() 查找匹配的文件（支持通配符）
    - 返回找到的文件路径列表

    Args:
        source_path: 源路径
        file_type: 文件类型（hex 或 a2l，默认 hex）

    Returns:
        List[Path]: 找到的文件路径列表

    Raises:
        ValueError: 不支持的文件类型

    Examples:
        >>> from pathlib import Path
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     base = Path(tmpdir)
        ...     (base / "test.hex").touch()
        ...     files = locate_output_files(base, "hex")
        ...     assert len(files) == 1
        ...     assert files[0].name == "test.hex"
    """
    if file_type.lower() == "hex":
        pattern = "*.hex"
    elif file_type.lower() == "a2l":
        pattern = "*.a2l"
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")

    files = list(source_path.glob(pattern))
    logger.debug(f"定位 {file_type.upper()} 文件: 找到 {len(files)} 个文件")
    return files


def rename_output_file(source_file: Path, target_folder: Path, timestamp: str) -> Path:
    """重命名输出文件

    Story 2.12 - 任务 2.1-2.5:
    - 接受源文件路径、目标文件夹路径、时间戳参数
    - 按命名规范生成新文件名：
      - A2L: tmsAPP_upAdress[_时间戳].a2l
      - HEX: VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB[_时间戳：_YYYYMMDD_V99_HH_MM].hex
    - 返回目标文件路径

    Args:
        source_file: 源文件路径
        target_folder: 目标文件夹
        timestamp: 时间戳（格式：_YYYY_MM_DD_HH_MM）

    Returns:
        Path: 目标文件路径

    Examples:
        >>> from pathlib import Path
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     base = Path(tmpdir)
        ...     target = base / "output"
        ...     target.mkdir()
        ...     source = base / "test.a2l"
        ...     source.touch()
        ...     result = rename_output_file(source, target, "_2026_02_14_16_35")
        ...     assert "2026_02_14_16_35" in result.name
    """
    # 获取文件扩展名
    ext = source_file.suffix.lower()

    # 根据文件类型生成新文件名
    if ext == ".a2l":
        # A2L 文件命名: tmsAPP_upAdress[_时间戳].a2l
        new_name = f"tmsAPP_upAdress{timestamp}{ext}"
    elif ext == ".hex":
        # HEX 文件命名: VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB[_时间戳：_YYYYMMDD_V99_HH_MM].hex
        # 转换时间戳格式: _YYYY_MM_DD_HH_MM -> _YYYYMMDD_V99_HH_MM
        parts = timestamp.split("_")
        if len(parts) >= 6:
            hex_timestamp = f"_{parts[1]}{parts[2]}{parts[3]}_V99_{parts[4]}_{parts[5]}"
        else:
            hex_timestamp = timestamp
        new_name = f"VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB{hex_timestamp}{ext}"

        # 处理文件名冲突：如果目标文件已存在，添加源文件名作为后缀
        target_file = target_folder / new_name
        if target_file.exists():
            # 使用源文件名（不含扩展名）作为后缀
            stem = source_file.stem
            # 插入源文件名到时间戳之前
            if hex_timestamp:
                new_name = f"VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB_{stem}{hex_timestamp}{ext}"
            else:
                new_name = f"VIU_Chery_E0Y_FL1_R_CYT4BFV3_AB_{stem}{ext}"
    else:
        new_name = source_file.name

    target_file = target_folder / new_name
    return target_file


def move_output_file(source_file: Path, target_folder: Path, timestamp: str) -> Path:
    """移动输出文件

    Story 2.12 - 任务 3.1-3.6:
    - 接受源文件路径、目标文件夹路径、新文件名参数
    - 使用 pathlib.Path.rename() 移动文件（跨卷使用 shutil.move）
    - 验证移动后的文件存在
    - 验证移动后的文件大小正确
    - 返回目标文件路径

    Args:
        source_file: 源文件路径
        target_folder: 目标文件夹
        timestamp: 时间戳

    Returns:
        Path: 目标文件路径

    Raises:
        FileNotFoundError: 源文件不存在
        FileMoveError: 文件移动失败

    Examples:
        >>> from pathlib import Path
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     base = Path(tmpdir)
        ...     target = base / "output"
        ...     target.mkdir()
        ...     source = base / "test.hex"
        ...     source.write_text("test content")
        ...     result = move_output_file(source, target, "_2026_02_14_16_35")
        ...     assert result.exists()
        ...     assert not source.exists()
    """
    if not source_file.exists():
        logger.error(f"源文件不存在: {source_file}")
        raise FileNotFoundError(f"源文件不存在: {source_file}")

    # 记录原始文件大小
    original_size = source_file.stat().st_size

    # 生成目标文件路径
    target_file = rename_output_file(source_file, target_folder, timestamp)

    logger.debug(f"移动文件: {source_file} -> {target_file}")

    try:
        # 移动文件（跨卷使用 shutil.move）
        shutil.move(str(source_file), str(target_file))
    except Exception as e:
        logger.error(f"文件移动失败: {source_file} -> {target_file} - {e}")
        from utils.errors import FileMoveError
        raise FileMoveError(
            f"文件移动失败: {source_file} -> {target_file}",
            suggestions=[
                "检查目标文件夹权限",
                "检查磁盘空间",
                "检查文件是否被占用"
            ]
        ) from e

    # 验证移动成功 (Story 2.12 - 任务 3.4, 3.5)
    if not target_file.exists():
        from utils.errors import FileMoveError
        raise FileMoveError(
            f"文件移动后验证失败: {target_file}",
            suggestions=["查看详细日志", "联系技术支持"]
        )

    # 验证文件大小正确
    new_size = target_file.stat().st_size
    if new_size != original_size:
        from utils.errors import FileMoveError
        raise FileMoveError(
            f"文件移动后大小不一致: 原始 {original_size} 字节，新 {new_size} 字节",
            suggestions=["检查磁盘空间", "检查文件系统错误"]
        )

    logger.debug(f"文件移动成功: {target_file}")
    return target_file


def move_output_files_safe(
    source_path_hex: Path,
    source_path_a2l: Path,
    target_folder: Path,
    timestamp: str
) -> tuple:
    """安全移动所有输出文件

    Story 2.12 - 任务 4.1-4.7:
    - 接受源路径、目标文件夹路径、时间戳参数
    - 调用 locate_output_files() 查找所有 HEX 文件
    - 调用 locate_output_files() 查找所有 A2L 文件
    - 对每个文件调用 move_output_file() 移动并重命名
    - 使用 try-except 捕获移动失败
    - 返回成功和失败的文件列表

    Args:
        source_path_hex: HEX 文件源路径
        source_path_a2l: A2L 文件源路径
        target_folder: 目标文件夹
        timestamp: 时间戳

    Returns:
        tuple: (成功文件列表, 失败文件列表)
            - 成功文件列表: List[Path]
            - 失败文件列表: List[Tuple[Path, Exception]]

    Examples:
        >>> from pathlib import Path
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     base = Path(tmpdir)
        ...     target = base / "output"
        ...     target.mkdir()
        ...     hex_source = base / "hex"
        ...     hex_source.mkdir()
        ...     (hex_source / "test.hex").touch()
        ...     a2l_source = base / "a2l"
        ...     a2l_source.mkdir()
        ...     (a2l_source / "test.a2l").touch()
        ...     success, failed = move_output_files_safe(hex_source, a2l_source, target, "_2026_02_14_16_35")
        ...     assert len(success) == 2
        ...     assert len(failed) == 0
    """
    from typing import Tuple, List

    logger.info("批量移动开始")

    success_files: List[Path] = []
    failed_files: List[Tuple[Path, Exception]] = []

    # 移动 HEX 文件
    hex_files = locate_output_files(source_path_hex, "hex")
    for hex_file in hex_files:
        try:
            target_file = move_output_file(hex_file, target_folder, timestamp)
            success_files.append(target_file)
        except Exception as e:
            logger.error(f"HEX 文件移动失败: {hex_file} - {e}")
            failed_files.append((hex_file, e))

    # 移动 A2L 文件
    a2l_files = locate_output_files(source_path_a2l, "a2l")
    for a2l_file in a2l_files:
        try:
            target_file = move_output_file(a2l_file, target_folder, timestamp)
            success_files.append(target_file)
        except Exception as e:
            logger.error(f"A2L 文件移动失败: {a2l_file} - {e}")
            failed_files.append((a2l_file, e))

    logger.info(f"批量移动完成: 成功 {len(success_files)} 个，失败 {len(failed_files)} 个")
    return success_files, failed_files
