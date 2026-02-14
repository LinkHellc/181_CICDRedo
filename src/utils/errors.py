"""Unified error classes for MBD_CICDKits.

This module provides exception classes with helpful suggestions
for resolving configuration errors.

Story 2.11 - 任务 8.1-8.2:
- 添加 FileOperationError 错误类
- 添加 FolderCreationError 错误类
- 定义权限不足、磁盘空间不足、路径不存在错误建议
"""

from typing import List


class ProcessError(Exception):
    """进程相关错误基类

    Architecture Decision 2.2:
    - 使用 ProcessError 统一管理外部进程错误
    - 提供可操作的修复建议

    Attributes:
        message: 错误消息
        suggestions: 修复建议列表
    """

    def __init__(self, process_name: str, message: str, suggestions: List[str] = None):
        self.process_name = process_name
        default_suggestions = [
            f"检查 {process_name} 是否正确安装",
            "验证进程路径配置",
            "查看详细日志获取更多信息"
        ]
        if suggestions:
            default_suggestions = suggestions
        super().__init__(message)
        self.suggestions = default_suggestions

    def __str__(self):
        base_msg = super().__str__()
        if self.suggestions:
            suggestions = "\n".join(f"  - {s}" for s in self.suggestions)
            return f"{base_msg}\n\n建议:\n{suggestions}"
        return base_msg


class ProcessTimeoutError(ProcessError):
    """进程执行超时

    Architecture Decision 2.1:
    - 使用 time.monotonic() 检测超时
    - 超时时清理进程资源

    Attributes:
        process_name: 进程名称
        timeout: 超时时间（秒）
    """

    def __init__(self, process_name: str, timeout: int):
        super().__init__(
            process_name,
            f"{process_name} 执行超时（超过 {timeout} 秒）",
            suggestions=[
                f"检查 {process_name} 是否卡死",
                "增加超时配置（如果模型复杂度高）",
                "查看进程是否在等待用户输入",
                "检查系统资源是否充足"
            ]
        )
        self.timeout = timeout


class ProcessExitCodeError(ProcessError):
    """进程异常退出

    当进程以非零退出码退出时抛出。

    Attributes:
        process_name: 进程名称
        exit_code: 退出码
    """

    def __init__(self, process_name: str, exit_code: int):
        super().__init__(
            process_name,
            f"{process_name} 异常退出（退出码: {exit_code}）",
            suggestions=[
                f"查看 {process_name} 错误日志",
                "检查输入参数是否正确",
                "验证配置文件格式",
                "确认许可证/授权状态"
            ]
        )
        self.exit_code = exit_code


class ConfigError(Exception):
    """配置相关错误基类

    提供错误消息和可操作的修复建议。
    """

    def __init__(self, message: str, suggestions: List[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []

    def __str__(self):
        base_msg = super().__str__()
        if self.suggestions:
            suggestions = "\n".join(f"  - {s}" for s in self.suggestions)
            return f"{base_msg}\n\n建议:\n{suggestions}"
        return base_msg


class ConfigSaveError(ConfigError):
    """配置保存失败

    当无法保存配置到文件系统时抛出。
    """

    def __init__(self, reason: str):
        super().__init__(
            f"无法保存配置: {reason}",
            suggestions=[
                "检查配置目录权限",
                "确保磁盘空间充足",
                "查看详细日志获取更多信息"
            ]
        )


class ConfigValidationError(ConfigError):
    """配置验证失败

    当配置不符合验证规则时抛出。
    """

    def __init__(self, message: str, suggestions: List[str] = None):
        default_suggestions = [
            "检查所有必填字段是否已填写",
            "确保路径格式正确",
            "查看配置表单中的红色提示"
        ]
        if suggestions:
            default_suggestions.extend(suggestions)
        super().__init__(message, default_suggestions)


class ConfigLoadError(ConfigError):
    """配置加载失败

    当无法从文件加载配置时抛出。
    Code Review Fixes (2026-02-06): 添加自定义 suggestions 支持
    """

    def __init__(self, reason: str, suggestions: List[str] = None):
        default_suggestions = [
            "检查配置文件是否存在",
            "验证文件格式是否正确",
            "确保文件没有被其他程序锁定"
        ]
        if suggestions:
            default_suggestions = suggestions  # 使用自定义建议替代默认建议
        super().__init__(
            f"无法加载配置: {reason}",
            default_suggestions
        )


class FileError(Exception):
    """文件操作错误基类

    Story 2.7 - 任务 5.1-5.5:
    - 使用 FileError 统一管理文件操作错误
    - 提供可操作的修复建议

    Attributes:
        message: 错误消息
        suggestions: 修复建议列表
    """

    def __init__(self, message: str, suggestions: List[str] = None):
        default_suggestions = [
            "检查文件路径是否正确",
            "验证文件权限",
            "查看详细日志获取更多信息"
        ]
        if suggestions:
            default_suggestions = suggestions
        super().__init__(message)
        self.suggestions = default_suggestions

    def __str__(self):
        base_msg = super().__str__()
        if self.suggestions:
            suggestions = "\n".join(f"  - {s}" for s in self.suggestions)
            return f"{base_msg}\n\n建议:\n{suggestions}"
        return base_msg


class DirectoryNotFoundError(FileError):
    """目录不存在错误

    Story 2.7 - 任务 2.4:
    - 处理目录不存在的情况
    - 提供自动创建选项
    """

    def __init__(self, dir_path: str):
        super().__init__(
            f"目标目录不存在: {dir_path}",
            suggestions=[
                "检查目录路径是否正确",
                "系统可以自动创建目录",
                "验证父目录是否存在"
            ]
        )
        self.dir_path = dir_path


class DirectoryNotWritableError(FileError):
    """目录不可写错误

    Story 2.7 - 任务 5.1:
    - 处理目标目录不可写错误
    - 提供权限修复建议
    """

    def __init__(self, dir_path: str):
        super().__init__(
            f"目标目录不可写: {dir_path}",
            suggestions=[
                "检查目录权限设置",
                "以管理员身份运行程序",
                "检查磁盘是否写保护"
            ]
        )
        self.dir_path = dir_path


class DiskSpaceError(FileError):
    """磁盘空间不足错误

    Story 2.7 - 任务 5.2:
    - 处理磁盘空间不足错误
    - 提供空间清理建议
    """

    def __init__(self, needed_mb: float, available_mb: float):
        super().__init__(
            f"磁盘空间不足，需要 {needed_mb:.1f}MB，可用 {available_mb:.1f}MB",
            suggestions=[
                "清理磁盘空间",
                "更换目标磁盘",
                "禁用备份功能以节省空间"
            ]
        )
        self.needed_mb = needed_mb
        self.available_mb = available_mb


class FileVerificationError(FileError):
    """文件验证失败错误

    Story 2.7 - 任务 3.1-3.5:
    - 处理文件移动验证失败
    - 提供重试或跳过选项
    """

    def __init__(self, file_path: str, reason: str):
        super().__init__(
            f"文件验证失败: {file_path} - {reason}",
            suggestions=[
                "检查磁盘完整性",
                "尝试再次移动",
                "跳过验证（不推荐）"
            ]
        )
        self.file_path = file_path
        self.reason = reason


# =============================================================================
# Story 2.11: 文件操作和文件夹创建错误
# =============================================================================

class FileOperationError(Exception):
    """文件操作错误基类

    Story 2.11 - 任务 8.1:
    - 提供统一的错误处理和可操作的修复建议
    - 支持所有文件操作错误的基类

    Attributes:
        message: 错误消息
        suggestions: 修复建议列表
    """

    def __init__(self, message: str, suggestions: List[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []

    def __str__(self):
        msg = super().__str__()
        if self.suggestions:
            msg += "\n建议操作:\n" + "\n".join(f"  - {s}" for s in self.suggestions)
        return msg


class FolderCreationError(FileOperationError):
    """文件夹创建失败

    Story 2.11 - 任务 8.2-8.5:
    - 文件夹创建失败的专用错误类
    - 根据失败原因提供针对性建议

    Attributes:
        folder_path: 文件夹路径
        reason: 失败原因（权限不足、磁盘空间不足、路径不存在等）
    """

    def __init__(self, folder_path: str, reason: str = ""):
        # 根据失败原因提供针对性建议 (Story 2.11 - 任务 8.3-8.5)
        if "权限不足" in reason or "Permission" in reason:
            suggestions = [
                "以管理员身份运行",
                "检查目录权限设置",
                "选择其他目标目录"
            ]
        elif "磁盘空间" in reason or "No space" in reason:
            suggestions = [
                "清理磁盘空间",
                "选择其他目标目录"
            ]
        elif "路径不存在" in reason or "No such file" in reason:
            suggestions = [
                "创建目标目录",
                "检查配置文件中的路径设置"
            ]
        else:
            suggestions = [
                "检查目录权限",
                "检查磁盘空间",
                "验证路径合法性",
                "查看详细日志"
            ]

        super().__init__(
            f"无法创建文件夹: {folder_path} - {reason}",
            suggestions
        )
        self.folder_path = folder_path
        self.reason = reason
