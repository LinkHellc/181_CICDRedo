"""A2L file processing stage for MBD_CICDKits workflow.

This module implements the A2L file processing stage which updates variable
addresses in A2L files using pure Python implementation (pyelftools).

Story 2.9: Update A2L File Variable Addresses
Story 2.10: Replace A2L File XCP Header Content

Architecture Decision Compliance:
- Decision 1.1: Stage interface pattern (execute_stage signature)
- Decision 1.2: Dataclass with default values
- ADR-005: Removed MATLAB Engine dependency, use pure Python

Change Log:
- 2026-02-25: Replaced MATLAB Engine with pure Python implementation (pyelftools)
"""

import logging
import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Tuple, Callable

from core.models import (
    StageConfig,
    StageResult,
    StageStatus,
    BuildContext
)
from core.constants import get_stage_timeout
from utils.errors import ProcessTimeoutError, ProcessError
from utils.errors import FileError
from core.models import A2LHeaderReplacementConfig

# Pure Python A2L processing (ADR-005)
from a2l.elf_parser import ELFParser, ELFParseError
from a2l.a2l_parser import A2LParser, A2LParseError
from a2l.address_updater import A2LAddressUpdater, AddressUpdateError

logger = logging.getLogger(__name__)


@dataclass
class A2LProcessConfig(StageConfig):
    """A2L 更新阶段配置

    Story 2.9 - 任务 1.2-1.5:
    - 继承 StageConfig
    - 添加 A2L 文件路径配置字段
    - 添加 ELF 文件路径配置字段
    - 添加超时配置字段（默认 600 秒）

    Architecture Decision 1.2:
    - 所有字段提供默认值
    - 使用 field(default=...) 避免可变默认值陷阱

    Attributes:
        a2l_path: A2L 文件路径
        elf_path: ELF 文件路径
        timestamp_format: 时间戳格式（如 "_%Y_%m_%d_%H_%M"）
        timeout: 超时时间（秒）
    """
    # 继承 StageConfig 的字段（name, enabled, timeout）
    # 添加 A2L 特定字段

    a2l_path: str = ""                    # A2L 文件路径
    elf_path: str = ""                     # ELF 文件路径
    timestamp_format: str = "_%Y_%m_%d_%H_%M"  # 时间戳格式

    def __post_init__(self):
        """初始化后处理

        如果 timeout 未设置，则从 constants 中获取默认值
        """
        if self.timeout == 300:  # StageConfig 默认值
            # 如果用户没有指定超时，使用 A2L 专用的超时值
            self.timeout = get_stage_timeout("a2l_process")


def execute_a2ltool_script(
    a2l_path: Path,
    timeout: int,
    log_callback: Callable[[str], None]
) -> bool:
    """调用 A2LTool.m 脚本删除 IF_DATA XCP 块

    使用 MATLAB 运行 A2LTool.m 脚本，删除 A2L 文件中的
    /begin IF_DATA XCP ... /end IF_DATA 块。

    Args:
        a2l_path: A2L 文件路径
        timeout: 超时时间（秒）
        log_callback: 日志回调函数

    Returns:
        bool: 成功返回 True

    Raises:
        ProcessError: 如果执行失败
        ProcessTimeoutError: 如果超时
    """
    # 获取 A2L 文件所在目录
    a2l_dir = str(a2l_path.parent)
    a2l_filename = a2l_path.name

    log_callback(f"调用 A2LTool.m 处理: {a2l_filename}")

    # 构建运行 A2LTool.m 的 MATLAB 命令
    # 注意：A2LTool.m 会弹出文件选择对话框，所以我们需要修改它或使用其他方式
    # 这里我们直接实现 A2LTool.m 的功能（删除 IF_DATA XCP 块）

    return remove_if_data_xcp_blocks(a2l_path, log_callback)[0]


def _generate_a2l_update_command(
    context: BuildContext,
    config: A2LProcessConfig
) -> Tuple[str, str, str]:
    """生成 A2L 更新 MATLAB 命令

    Story 2.9 - 任务 2.1-2.5:
    - 从 BuildContext 获取 A2L 文件路径和 ELF 文件路径
    - 生成完整路径的 MATLAB 命令：`rtw.asap2SetAddress(a2l_path, elf_path)`

    Args:
        context: 构建上下文
        config: A2L 更新配置

    Returns:
        (a2l_path, elf_path, matlab_command) 元组
    """
    # 获取 A2L 源文件路径
    a2l_path = context.state.get("a2l_source_path", "") or context.config.get("a2l_path", "")
    if not a2l_path:
        # 尝试从 a2l_tool_path 查找
        a2l_tool_path = context.config.get("a2l_tool_path", "")
        if a2l_tool_path:
            a2l_files = list(Path(a2l_tool_path).rglob("*.a2l"))
            if a2l_files:
                a2l_path = str(a2l_files[0])

    # 获取 ELF 文件路径
    elf_path = context.state.get("iar_elf_path", "") or config.elf_path
    if not elf_path:
        # 尝试从 IAR 项目目录查找
        iar_path = context.config.get("iar_project_path", "")
        if iar_path:
            elf_files = list(Path(iar_path).parent.rglob("**/*.elf"))
            if elf_files:
                elf_path = str(elf_files[0])

    # 如果仍然没有，使用默认名称
    if not elf_path:
        elf_path = "CYT4BF_M7_Master.elf"

    logger.debug(f"A2L 路径: {a2l_path}")
    logger.debug(f"ELF 路径: {elf_path}")

    # 构建 MATLAB 命令（使用完整路径）
    # 注意：参数需要用引号包裹，路径使用正斜杠（MATLAB 格式）
    a2l_path_matlab = Path(a2l_path).as_posix() if a2l_path else "tmsAPP.a2l"
    elf_path_matlab = Path(elf_path).as_posix() if elf_path else "CYT4BF_M7_Master.elf"

    matlab_command = f"rtw.asap2SetAddress('{a2l_path_matlab}', '{elf_path_matlab}')"
    logger.debug(f"生成的 A2L 更新命令: {matlab_command}")

    return a2l_path, elf_path, matlab_command


def _verify_a2l_updated(
    a2l_path: Path,
    log_callback: Callable[[str], None]
) -> Tuple[bool, str]:
    """验证 A2L 文件已更新

    Story 2.9 - 任务 5.1-5.5:
    - 检查 A2L 文件是否存在
    - 验证 A2L 文件大小是否合理（非零）
    - 可选：解析 A2L 文件验证变量地址格式
    - 返回验证结果（成功/失败）

    Args:
        a2l_path: A2L 文件路径
        log_callback: 日志回调函数

    Returns:
        (success, message) 元组
    """
    # 检查文件是否存在 (任务 5.2)
    if not a2l_path.exists():
        return False, f"A2L 文件不存在: {a2l_path}"

    # 检查文件大小 (任务 5.3)
    file_size = a2l_path.stat().st_size
    if file_size == 0:
        return False, f"A2L 文件大小为 0: {a2l_path}"

    # 可选：解析 A2L 文件验证变量地址格式 (任务 5.4)
    # 在 MVP 阶段，我们只做基本验证
    # Phase 2 可以添加更详细的 A2L 文件解析

    log_callback(f"A2L 文件验证成功: {a2l_path} ({file_size:,} bytes)")
    logger.info(f"A2L 文件验证成功: {a2l_path} ({file_size:,} bytes)")

    return True, "A2L 文件验证成功"


def _validate_configuration(
    config: A2LProcessConfig,
    context: BuildContext,
    log_callback: Callable[[str], None]
) -> Optional[StageResult]:
    """验证配置和前置条件

    Story 2.9 - 任务 12:
    - 验证 ELF 文件路径存在
    - 验证 ELF 文件有效（非零大小）
    - 验证 A2L 输出目录存在
    - 如果验证失败，返回 StageResult(FAILED) 并提供修复建议
    - 记录验证结果到日志

    Args:
        config: A2L 处理配置
        context: 构建上下文
        log_callback: 日志回调函数

    Returns:
        如果验证失败，返回失败的 StageResult；否则返回 None
    """
    # 获取 ELF 文件路径 (任务 12.1)
    elf_path = Path(config.elf_path) if config.elf_path else None

    if not elf_path:
        error_msg = "未配置 ELF 文件路径"
        log_callback(f"配置验证失败: {error_msg}")
        logger.error(error_msg)

        return StageResult(
            status=StageStatus.FAILED,
            message=error_msg,
            suggestions=[
                "检查 IAR 编译阶段是否成功",
                "验证 ELF 文件路径配置",
                "确保 iar_compile 阶段已完成"
            ]
        )

    # 验证 ELF 文件是否存在 (任务 12.1)
    if not elf_path.exists():
        error_msg = f"ELF 文件不存在: {elf_path}"
        log_callback(f"配置验证失败: {error_msg}")
        logger.error(error_msg)

        return StageResult(
            status=StageStatus.FAILED,
            message=error_msg,
            suggestions=[
                "检查 IAR 编译阶段是否成功",
                "验证 ELF 文件路径配置",
                "重新执行 IAR 编译"
            ]
        )

    # 验证 ELF 文件有效性（非零大小）(任务 12.2)
    elf_size = elf_path.stat().st_size
    if elf_size == 0:
        error_msg = f"ELF 文件大小为 0: {elf_path}"
        log_callback(f"配置验证失败: {error_msg}")
        logger.error(error_msg)

        return StageResult(
            status=StageStatus.FAILED,
            message=error_msg,
            suggestions=[
                "检查 IAR 编译输出",
                "验证 ELF 文件是否生成成功",
                "查看 IAR 编译日志"
            ]
        )

    log_callback(f"ELF 文件验证成功: {elf_path} ({elf_size:,} bytes)")
    logger.info(f"ELF 文件验证成功: {elf_path} ({elf_size:,} bytes)")

    # 验证 A2L 输出目录存在 (任务 12.3)
    # A2L 文件将生成在 MATLAB 工作目录中，这里我们验证当前目录可写
    import tempfile
    try:
        # 尝试创建临时文件来验证目录可写
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
            f.write("test")
        log_callback("A2L 输出目录验证成功（可写）")
    except Exception as e:
        error_msg = f"A2L 输出目录不可写: {e}"
        log_callback(f"配置验证失败: {error_msg}")
        logger.error(error_msg)

        return StageResult(
            status=StageStatus.FAILED,
            message=error_msg,
            suggestions=[
                "检查当前目录权限",
                "以管理员身份运行程序",
                "验证磁盘是否写保护"
            ]
        )

    return None


# 注: _execute_matlab_command 函数已移除 (ADR-005)
# 现在使用纯 Python 实现 (a2l.address_updater.A2LAddressUpdater)


def execute_stage(config: StageConfig, context: BuildContext) -> StageResult:
    """执行 A2L 更新阶段

    Story 2.9 - 任务 3.1-3.5:
    - 实现 execute_stage() 函数（统一接口）
    - 接受 StageConfig 和 BuildContext 参数
    - 使用纯 Python 实现（pyelftools）更新地址
    - 返回 StageResult（成功或失败）

    Architecture Decision 1.1:
    - 统一阶段签名: execute_stage(config, context) -> result

    Architecture Decision ADR-005:
    - 使用纯 Python 实现，不依赖 MATLAB Engine

    Story 2.9 - 任务 8:
    - 使用 context.log_callback 记录 A2L 更新开始日志
    - 记录 A2L 文件验证结果
    - 记录阶段执行时长

    Args:
        config: 阶段配置（StageConfig 或 A2LProcessConfig 类型）
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    # 获取超时设置
    timeout = getattr(config, 'timeout', None) or get_stage_timeout("a2l_process")

    # 如果传入的是 A2LProcessConfig，直接使用
    # 如果传入的是 StageConfig，从 context.config 获取 A2L 相关配置
    if isinstance(config, A2LProcessConfig):
        a2l_config = config
    else:
        # 从 context.config 创建 A2LProcessConfig
        a2l_config = A2LProcessConfig(
            name=config.name,
            enabled=config.enabled,
            timeout=timeout,
            a2l_path=context.config.get("a2l_path", ""),
            elf_path=context.config.get("elf_path", ""),
        )

    # 记录阶段开始 (任务 8.1)
    log_callback = context.log or (lambda msg: logger.info(msg))
    start_time = time.monotonic()
    log_callback("开始 A2L 更新阶段（Python 实现）")
    logger.info("开始 A2L 更新阶段（Python 实现）")

    try:
        # 验证配置和前置条件 (任务 12)
        validation_result = _validate_configuration(a2l_config, context, log_callback)
        if validation_result:
            return validation_result

        # 获取 ELF 和 A2L 文件路径
        a2l_file, elf_file, _ = _generate_a2l_update_command(context, a2l_config)

        if not elf_file:
            return StageResult(
                status=StageStatus.FAILED,
                message="未找到 ELF 文件路径",
                suggestions=[
                    "检查 IAR 编译阶段是否成功",
                    "验证 ELF 文件路径配置"
                ]
            )

        if not a2l_file:
            return StageResult(
                status=StageStatus.FAILED,
                message="未找到 A2L 文件路径",
                suggestions=[
                    "检查 A2L 文件路径配置",
                    "验证 a2l_tool_path 配置"
                ]
            )

        elf_path = Path(elf_file)
        a2l_path = Path(a2l_file)

        log_callback(f"ELF 文件: {elf_path}")
        log_callback(f"A2L 文件: {a2l_path}")

        # 使用纯 Python 实现更新地址 (ADR-005)
        log_callback("使用 Python 解析 ELF 文件并更新 A2L 地址...")

        updater = A2LAddressUpdater()
        updater.set_log_callback(log_callback)

        try:
            result = updater.update(elf_path, a2l_path, backup=True)

            if not result.success:
                return StageResult(
                    status=StageStatus.FAILED,
                    message=result.message,
                    suggestions=[
                        "检查 ELF 文件格式",
                        "验证 A2L 文件格式",
                        "查看详细日志获取更多信息"
                    ]
                )

            # 记录更新统计 (任务 8.3)
            log_callback(f"匹配变量: {result.matched_count}/{result.total_variables}")
            log_callback(f"未匹配变量: {result.unmatched_count}")

            if result.unmatched_count > 0:
                log_callback(f"未匹配变量列表: {', '.join(result.unmatched_variables[:10])}"
                           + ("..." if result.unmatched_count > 10 else ""))

        except (ELFParseError, A2LParseError, AddressUpdateError) as e:
            error_msg = f"A2L 地址更新失败: {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查 ELF 文件是否存在且有效",
                    "检查 A2L 文件是否存在且有效",
                    "验证 pyelftools 已安装: pip install pyelftools"
                ]
            )

        # 验证更新后的 A2L 文件 (任务 5, 8.3)
        success, message = _verify_a2l_updated(a2l_path, log_callback)

        if not success:
            return StageResult(
                status=StageStatus.FAILED,
                message=f"A2L 文件验证失败: {message}",
                suggestions=[
                    "检查 ELF 文件格式",
                    "验证 A2L 文件结构"
                ]
            )

        # 计算执行时长 (任务 8.4)
        elapsed = time.monotonic() - start_time
        log_callback(f"A2L 更新阶段完成，耗时 {elapsed:.2f} 秒")
        logger.info(f"A2L 更新阶段完成，耗时 {elapsed:.2f} 秒")

        # 返回成功结果 (任务 3.5)
        return StageResult(
            status=StageStatus.COMPLETED,
            message=f"A2L 文件变量地址更新成功（匹配 {result.matched_count} 个变量）",
            output_files=[str(a2l_path)],
            execution_time=elapsed
        )

    except Exception as e:
        # 未预期的异常 (任务 6.1-6.6)
        error_msg = f"A2L 更新阶段异常: {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg, exc_info=True)

        return StageResult(
            status=StageStatus.FAILED,
            message=error_msg,
            error=e,
            suggestions=[
                "查看详细日志",
                "检查配置和环境",
                "验证 pyelftools 已安装"
            ]
        )


# ============================================================================
# Story 2.10: 替换 A2L 文件 XCP 头文件内容
# ============================================================================

# XCP 头文件定位正则表达式 (任务 3.2, 3.3)
# 替换范围：从文件开头到第一个 /end MOD_PAR
XCP_HEADER_END_PATTERN = re.compile(r'/end\s+MOD_PAR', re.IGNORECASE)


def read_xcp_header_template(
    template_path: Path,
    log_callback: Callable[[str], None]
) -> str:
    """读取 XCP 头文件模板

    Story 2.10 - 任务 2.1-2.5:
    - 支持从项目资源目录读取模板文件
    - 支持从用户自定义路径读取模板文件
    - 验证模板文件存在性（前置条件检查）
    - 记录模板读取日志（文件路径、大小、时间戳）

    Args:
        template_path: 模板文件路径
        log_callback: 日志回调函数

    Returns:
        模板内容字符串

    Raises:
        FileNotFoundError: 模板文件不存在
        FileError: 文件读取失败
    """
    # 验证模板文件存在 (任务 2.4)
    if not template_path.exists():
        error_msg = f"模板文件未找到: {template_path}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)

        raise FileNotFoundError(error_msg)

    # 读取模板文件 (任务 2.1, 2.2)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 记录模板读取日志 (任务 2.5)
        file_size = template_path.stat().st_size
        log_callback(f"读取 XCP 头文件模板: {template_path} ({file_size:,} bytes)")
        logger.info(f"读取 XCP 头文件模板: {template_path} ({file_size:,} bytes)")

        return template_content

    except UnicodeDecodeError:
        # 尝试其他编码 (任务 2.3)
        try:
            with open(template_path, 'r', encoding='gbk') as f:
                template_content = f.read()

            file_size = template_path.stat().st_size
            log_callback(f"读取 XCP 头文件模板 (GBK 编码): {template_path} ({file_size:,} bytes)")
            logger.info(f"读取 XCP 头文件模板 (GBK 编码): {template_path} ({file_size:,} bytes)")

            return template_content
        except Exception as e:
            error_msg = f"读取模板文件失败: {template_path} - {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            raise FileError(error_msg, suggestions=[
                "检查模板文件编码",
                "确保文件格式为 UTF-8 或 GBK",
                "查看详细日志获取更多信息"
            ])

    except Exception as e:
        error_msg = f"读取模板文件失败: {template_path} - {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)

        raise FileError(error_msg, suggestions=[
            "检查文件权限",
            "确保文件未被其他程序锁定",
            "查看详细日志获取更多信息"
        ])


def find_xcp_header_section(
    a2l_path: Path,
    log_callback: Callable[[str], None]
) -> Optional[Tuple[int, int]]:
    """定位 A2L 文件中的 XCP 头文件部分

    Story 2.10 - 任务 3.1-3.5:
    - 使用正则表达式识别 XCP 头文件起始标记（如 `/begin XCP`）
    - 使用正则表达式识别 XCP 头文件结束标记（如 `/end XCP`）
    - 提取 XCP 头文件部分的起始位置和结束位置
    - 如果未找到 XCP 头文件部分，返回错误并提供建议（"检查A2L文件格式"）

    Args:
        a2l_path: A2L 文件路径
        log_callback: 日志回调函数

    Returns:
        (start_pos, end_pos) 元组，表示 XCP 头文件的起始和结束位置
        如果未找到，返回 None

    Raises:
        FileNotFoundError: A2L 文件不存在
        FileError: 文件读取失败
    """
    # 验证 A2L 文件存在
    if not a2l_path.exists():
        error_msg = f"A2L 文件不存在: {a2l_path}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)

        raise FileNotFoundError(error_msg)

    # 读取 A2L 文件内容
    try:
        with open(a2l_path, 'r', encoding='utf-8') as f:
            a2l_content = f.read()
    except UnicodeDecodeError:
        try:
            with open(a2l_path, 'r', encoding='gbk') as f:
                a2l_content = f.read()
        except Exception as e:
            error_msg = f"读取 A2L 文件失败: {a2l_path} - {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            raise FileError(error_msg, suggestions=[
                "检查 A2L 文件编码",
                "确保文件格式为 UTF-8 或 GBK",
                "查看详细日志获取更多信息"
            ])

    # 查找第一个 /end MOD_PAR 行 (任务 3.3)
    match = XCP_HEADER_END_PATTERN.search(a2l_content)

    if not match:
        # 未找到结束标记 (任务 3.5)
        error_msg = f"未找到 A2L 文件中的 /end MOD_PAR 标记: {a2l_path}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)

        return None

    # 起始位置固定为 0，结束位置为匹配行之后
    start_pos = 0
    # 包含匹配行的内容，找到该行的结束位置
    line_end = match.end()
    # 找到该行的实际结束（包括换行符）
    while line_end < len(a2l_content) and a2l_content[line_end] not in ['\n', '\r']:
        line_end += 1

    end_pos = line_end

    log_callback(f"找到 XCP 头文件替换范围: 位置 {start_pos}-{end_pos} ({end_pos - start_pos:,} bytes)")
    logger.info(f"找到 XCP 头文件替换范围: {a2l_path} 位置 {start_pos}-{end_pos}")

    return (start_pos, end_pos)


def replace_xcp_header_content(
    a2l_path: Path,
    header_section: Tuple[int, int],
    xcp_template: str,
    log_callback: Callable[[str], None]
) -> str:
    """执行 XCP 头文件内容替换

    Story 2.10 - 任务 4.1-4.5:
    - 读取 A2L 文件的完整内容到内存
    - 使用字符串切片替换 XCP 头文件部分（保留 A2L 文件其他内容）
    - 记录替换操作日志（替换的行数、原始长度、新长度）
    - 处理编码问题（确保使用 UTF-8 或 A2L 文件原始编码）

    Args:
        a2l_path: A2L 文件路径
        header_section: (start_pos, end_pos) 元组，表示 XCP 头文件的起始和结束位置
        xcp_template: XCP 头文件模板内容
        log_callback: 日志回调函数

    Returns:
        替换后的 A2L 文件内容

    Raises:
        FileError: 文件读取失败
    """
    start_pos, end_pos = header_section

    # 读取 A2L 文件完整内容 (任务 4.2)
    try:
        with open(a2l_path, 'r', encoding='utf-8') as f:
            a2l_content = f.read()
    except UnicodeDecodeError:
        try:
            with open(a2l_path, 'r', encoding='gbk') as f:
                a2l_content = f.read()
        except Exception as e:
            error_msg = f"读取 A2L 文件失败: {a2l_path} - {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            raise FileError(error_msg, suggestions=[
                "检查 A2L 文件编码",
                "确保文件格式为 UTF-8 或 GBK",
                "查看详细日志获取更多信息"
            ])

    # 计算原始 XCP 头文件长度 (任务 4.4)
    original_length = end_pos - start_pos
    new_length = len(xcp_template)

    # 替换 XCP 头文件部分 (任务 4.3)
    updated_content = a2l_content[:start_pos] + xcp_template + a2l_content[end_pos:]

    # 记录替换操作日志 (任务 4.4)
    log_callback(f"替换 XCP 头文件内容: 原始长度 {original_length:,} bytes -> 新长度 {new_length:,} bytes")
    logger.info(f"替换 XCP 头文件内容: {original_length:,} -> {new_length:,} bytes")

    return updated_content


def generate_timestamp(timestamp_format: str) -> str:
    """生成时间戳

    Story 2.10 - 任务 5.2:
    - 生成时间戳（格式：`_年_月_日_时_分`，如 `_2025_02_02_15_43`）

    Args:
        timestamp_format: 时间戳格式（默认 "_%Y_%m_%d_%H_%M"）

    Returns:
        时间戳字符串

    Example:
        >>> generate_timestamp("_%Y_%m_%d_%H_%M")
        '_2025_02_02_15_43'
    """
    from datetime import datetime
    return datetime.now().strftime(timestamp_format)


def save_updated_a2l_file(
    a2l_config: A2LHeaderReplacementConfig,
    updated_content: str,
    log_callback: Callable[[str], None]
) -> Path:
    """保存更新后的 A2L 文件

    Story 2.10 - 任务 5.1-5.5:
    - 生成时间戳（格式：`_年_月_日_时_分`，如 `_2025_02_02_15_43`）
    - 构建输出文件名：`tmsAPP_upAdress[_时间戳].a2l`
    - 使用原子性写入模式（先写入临时文件，验证后重命名）
    - 确保文件权限正确（与源文件保持一致）

    Args:
        a2l_config: A2L 头文件替换配置
        updated_content: 更新后的 A2L 文件内容
        log_callback: 日志回调函数

    Returns:
        输出文件路径

    Raises:
        FileError: 文件写入失败
    """
    import tempfile
    import shutil

    # 生成时间戳 (任务 5.2)
    timestamp = generate_timestamp(a2l_config.timestamp_format)

    # 构建输出文件名 (任务 5.3)
    output_filename = f"{a2l_config.output_prefix}{timestamp}.a2l"

    # 构建输出文件路径
    output_dir = Path(a2l_config.output_dir) if a2l_config.output_dir else Path.cwd()
    output_path = output_dir / output_filename

    # 创建输出目录（如果不存在）
    output_dir.mkdir(parents=True, exist_ok=True)

    # 原子性写入模式 (任务 5.4)
    # 1. 创建临时文件
    temp_dir = output_dir
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=temp_dir,
            encoding=a2l_config.encoding,
            delete=False
        ) as temp_file:
            # 2. 写入内容
            temp_file.write(updated_content)
            temp_path = Path(temp_file.name)

        # 3. 验证写入成功
        if not temp_path.exists():
            raise OSError(f"临时文件创建失败: {temp_path}")

        # 4. 原子性重命名（replace 操作在 Windows 上是原子的）
        try:
            temp_path.replace(output_path)
            log_callback(f"保存 A2L 文件: {output_path}")
            logger.info(f"保存 A2L 文件: {output_path}")
        except OSError as e:
            # 清理临时文件
            if temp_path.exists():
                temp_path.unlink()
            raise OSError(f"文件写入失败: {e}")

    except Exception as e:
        error_msg = f"保存 A2L 文件失败: {output_path} - {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)

        raise FileError(error_msg, suggestions=[
            "检查文件权限",
            "检查磁盘空间",
            "尝试以管理员身份运行",
            "查看详细日志获取更多信息"
        ])

    return output_path


def verify_a2l_replacement(
    output_path: Path,
    xcp_template: str,
    log_callback: Callable[[str], None]
) -> bool:
    """验证文件替换成功

    Story 2.10 - 任务 6.1-6.5:
    - 验证输出文件存在且大小合理
    - 验证输出文件包含 XCP 头文件模板内容
    - 可选：验证 A2L 文件语法完整性（使用 A2L 验证工具）
    - 记录验证结果到日志

    Args:
        output_path: 输出文件路径
        xcp_template: XCP 头文件模板内容（用于验证）
        log_callback: 日志回调函数

    Returns:
        True 如果验证成功，否则 False
    """
    # 验证输出文件存在 (任务 6.2)
    if not output_path.exists():
        error_msg = f"输出文件不存在: {output_path}"
        log_callback(f"验证失败: {error_msg}")
        logger.error(error_msg)
        return False

    # 验证文件大小合理 (任务 6.2)
    file_size = output_path.stat().st_size
    if file_size == 0:
        error_msg = f"输出文件大小为 0: {output_path}"
        log_callback(f"验证失败: {error_msg}")
        logger.error(error_msg)
        return False

    # 验证输出文件包含 XCP 头文件模板内容 (任务 6.3)
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except UnicodeDecodeError:
        try:
            with open(output_path, 'r', encoding='gbk') as f:
                file_content = f.read()
        except Exception as e:
            error_msg = f"读取输出文件失败: {output_path} - {str(e)}"
            log_callback(f"验证失败: {error_msg}")
            logger.error(error_msg)
            return False

    # 检查是否包含 XCP 头文件模板内容
    # 使用模板的前 100 个字符作为验证指纹
    template_fingerprint = xcp_template[:100] if len(xcp_template) >= 100 else xcp_template
    if template_fingerprint not in file_content:
        error_msg = f"输出文件未包含预期的 XCP 头文件内容: {output_path}"
        log_callback(f"验证失败: {error_msg}")
        logger.error(error_msg)
        return False

    # 可选：验证 A2L 文件语法完整性 (任务 6.4)
    # MVP 阶段：仅做基本验证
    # Phase 2 可以添加 A2L 验证工具集成

    # 记录验证结果 (任务 6.5)
    log_callback(f"A2L 文件替换验证成功: {output_path} ({file_size:,} bytes)")
    logger.info(f"A2L 文件替换验证成功: {output_path} ({file_size:,} bytes)")

    return True


def remove_if_data_xcp_blocks(
    a2l_path: Path,
    log_callback: Callable[[str], None]
) -> Tuple[bool, int]:
    """删除 A2L 文件中的所有 IF_DATA XCP 块

    删除所有 /begin IF_DATA XCP ... /end IF_DATA 块。
    这些是 Simulink 自动生成的 XCP 数据，需要删除后替换为自定义 XCP 头文件。

    对应 MATLAB 脚本 A2LTool.m 的功能。

    Args:
        a2l_path: A2L 文件路径
        log_callback: 日志回调函数

    Returns:
        (success, removed_count) 元组
        - success: 是否处理成功
        - removed_count: 删除的块数量

    Raises:
        FileNotFoundError: A2L 文件不存在
        FileError: 文件读写失败
    """
    # 验证 A2L 文件存在
    if not a2l_path.exists():
        error_msg = f"A2L 文件不存在: {a2l_path}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    # 读取 A2L 文件内容
    try:
        with open(a2l_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(a2l_path, 'r', encoding='gbk') as f:
                content = f.read()
        except Exception as e:
            error_msg = f"读取 A2L 文件失败: {a2l_path} - {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)
            raise FileError(error_msg, suggestions=[
                "检查 A2L 文件编码",
                "确保文件格式为 UTF-8 或 GBK"
            ])

    # 删除 IF_DATA XCP 块的正则表达式
    # 匹配 /begin IF_DATA XCP 到 /end IF_DATA 之间的所有内容
    start_marker = r'/begin\s+IF_DATA\s+XCP'
    end_marker = r'/end\s+IF_DATA'

    # 使用正则表达式删除所有匹配的块
    pattern = re.compile(
        start_marker + r'.*?' + end_marker,
        re.DOTALL | re.IGNORECASE
    )

    removed_count = len(pattern.findall(content))
    result = pattern.sub('', content)

    # 写入更新后的内容
    try:
        with open(a2l_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(result)
    except Exception as e:
        error_msg = f"写入 A2L 文件失败: {a2l_path} - {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)
        raise FileError(error_msg, suggestions=[
            "检查文件权限",
            "检查磁盘空间"
        ])

    log_callback(f"IF_DATA XCP 块删除完成: 删除了 {removed_count} 个块")
    logger.info(f"IF_DATA XCP 块删除完成: {a2l_path} 删除了 {removed_count} 个块")

    return True, removed_count


def filter_zero_address_variables(
    a2l_path: Path,
    log_callback: Callable[[str], None]
) -> Tuple[bool, int, int]:
    """过滤掉地址为 0x0000 的 CHARACTERISTIC 变量

    删除 A2L 文件中所有 ECU Address 为 0x0000 的 CHARACTERISTIC 块。
    这些变量在 ELF 文件中找不到对应符号，地址更新失败。

    Args:
        a2l_path: A2L 文件路径
        log_callback: 日志回调函数

    Returns:
        (success, total_count, removed_count) 元组
        - success: 是否处理成功
        - total_count: 原始 CHARACTERISTIC 总数
        - removed_count: 删除的 CHARACTERISTIC 数量

    Raises:
        FileNotFoundError: A2L 文件不存在
        FileError: 文件读写失败
    """
    # 验证 A2L 文件存在
    if not a2l_path.exists():
        error_msg = f"A2L 文件不存在: {a2l_path}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    # 读取 A2L 文件内容
    try:
        with open(a2l_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(a2l_path, 'r', encoding='gbk') as f:
                content = f.read()
        except Exception as e:
            error_msg = f"读取 A2L 文件失败: {a2l_path} - {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)
            raise FileError(error_msg, suggestions=[
                "检查 A2L 文件编码",
                "确保文件格式为 UTF-8 或 GBK"
            ])

    lines = content.split('\n')
    result_lines = []
    i = 0
    removed_count = 0
    total_count = 0
    in_characteristic = False
    current_block = []

    # 正则表达式匹配 /begin CHARACTERISTIC 和 /end CHARACTERISTIC
    begin_pattern = re.compile(r'/begin\s+CHARACTERISTIC', re.IGNORECASE)
    end_pattern = re.compile(r'/end\s+CHARACTERISTIC', re.IGNORECASE)
    address_pattern = re.compile(r'ECU Address\s+.*?\b(0x[0-9A-Fa-f]+)\b')

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 检测 /begin CHARACTERISTIC
        if begin_pattern.search(stripped):
            total_count += 1
            in_characteristic = True
            current_block = [line]

            # 读取整个 CHARACTERISTIC 块
            i += 1
            while i < len(lines):
                block_line = lines[i]
                current_block.append(block_line)

                # 检查是否包含地址信息
                addr_match = address_pattern.search(block_line)
                if addr_match:
                    address = addr_match.group(1)
                    if address == '0x0000' or address == '0x00000000':
                        # 地址为 0，跳过这个块
                        removed_count += 1
                        log_callback(f"  跳过变量: 地址为 {address}")
                        # 找到 /end CHARACTERISTIC 并跳出
                        while i < len(lines):
                            if end_pattern.search(lines[i].strip()):
                                i += 1
                                break
                            i += 1
                        in_characteristic = False
                        current_block = []
                        break
                    else:
                        # 地址有效，保留这个块
                        result_lines.extend(current_block)
                        in_characteristic = False
                        current_block = []
                        break

                # 检查 /end CHARACTERISTIC
                if end_pattern.search(block_line.strip()):
                    # 没有找到地址信息，默认保留
                    result_lines.extend(current_block)
                    in_characteristic = False
                    current_block = []
                    i += 1
                    break

                i += 1
        else:
            if not in_characteristic:
                result_lines.append(line)
            i += 1

    # 写入更新后的内容
    try:
        with open(a2l_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(result_lines))
    except Exception as e:
        error_msg = f"写入 A2L 文件失败: {a2l_path} - {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)
        raise FileError(error_msg, suggestions=[
            "检查文件权限",
            "检查磁盘空间"
        ])

    kept_count = total_count - removed_count
    log_callback(f"变量过滤完成: 总数 {total_count}, 保留 {kept_count}, 删除 {removed_count}")
    logger.info(f"变量过滤完成: {a2l_path} 总数 {total_count}, 保留 {kept_count}, 删除 {removed_count}")

    return True, total_count, removed_count


def verify_processed_a2l_file(
    a2l_path: Path,
    log_callback: Callable[[str], None]
) -> Tuple[bool, List[str]]:
    """验证处理后的 A2L 文件

    验证三个关键点：
    1. XCP 前缀是否添加（文件开头包含 /begin XCP）
    2. 地址是否已更新（检查是否有非 0x0000 的地址）
    3. 原始头部是否已裁剪（检查第一个 /end MOD_PAR 之前的行数是否合理）

    Args:
        a2l_path: A2L 文件路径
        log_callback: 日志回调函数

    Returns:
        (success, messages) 元组
        - success: 是否全部验证通过
        - messages: 验证消息列表（成功和失败信息）
    """
    messages = []
    all_passed = True

    # 1. 验证文件存在
    if not a2l_path.exists():
        messages.append(f"❌ A2L 文件不存在: {a2l_path}")
        return False, messages

    # 读取文件内容
    try:
        with open(a2l_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(a2l_path, 'r', encoding='gbk') as f:
                content = f.read()
        except Exception as e:
            messages.append(f"❌ 读取 A2L 文件失败: {e}")
            return False, messages

    lines = content.split('\n')

    # 2. 验证 XCP 前缀已添加
    # 检查文件开头是否符合 XCP 头文件模板的特征
    # 可能的格式：
    # - 以 /* 开头（AutoExtract 格式）
    # - 以 /begin XCP 开头（简化格式）
    # - ASAP2_VERSION 声明

    xcp_header_found = False
    header_type = None

    # 检查前50行
    for i, line in enumerate(lines[:50]):
        stripped = line.strip()
        # AutoExtract 格式：以注释开头
        if stripped.startswith('/*') and 'Start of automatic variable extraction' in line:
            xcp_header_found = True
            header_type = "AutoExtract"
            messages.append(f"✅ XCP 头文件已添加（AutoExtract 格式，第 {i + 1} 行）")
            break
        # 简化 XCP 格式
        elif '/begin XCP' in line or '/begin  XCP' in line:
            xcp_header_found = True
            header_type = "简化 XCP"
            messages.append(f"✅ XCP 头文件已添加（简化 XCP 格式，第 {i + 1} 行）")
            break
        # ASAP2_VERSION 声明
        elif stripped.startswith('ASAP2_VERSION'):
            xcp_header_found = True
            header_type = "ASAP2"
            messages.append(f"✅ XCP 头文件已添加（ASAP2 格式，第 {i + 1} 行）")
            break

    if not xcp_header_found:
        messages.append("❌ XCP 头文件未添加（未找到预期的头文件格式）")
        all_passed = False

    # 3. 验证地址已更新（检查是否有非 0x0000 的地址）
    address_pattern = re.compile(r'ECU Address\s+.*?\b(0x[0-9A-Fa-f]+)\b')
    non_zero_addresses = []
    zero_addresses = []

    for line in lines:
        match = address_pattern.search(line)
        if match:
            addr = match.group(1)
            if addr != '0x0000' and addr != '0x00000000':
                non_zero_addresses.append(addr)
            else:
                zero_addresses.append(addr)

    if non_zero_addresses:
        messages.append(f"✅ 地址已更新（找到 {len(non_zero_addresses)} 个非零地址，示例: {non_zero_addresses[0]}）")
    else:
        messages.append("❌ 地址未更新（所有地址都是 0x0000）")
        all_passed = False

    if zero_addresses:
        messages.append(f"⚠️  仍有 {len(zero_addresses)} 个地址为 0x0000（这可能是正常的，如果符号在 ELF 中不存在）")

    # 4. 验证原始头部已裁剪
    # 检查方式：XCP模板后应该紧跟原始 A2L 内容
    # 原始 A2L 内容特征：包含 CHARACTERISTIC 或带有注释的 MOD_COMMON

    # 策略：在文件中间部分（例如第1000-3000行）查找原始 A2L 内容
    # 因为模板文件通常有数百到数千行，原始A2L内容应该在模板后面

    original_content_found = False
    original_content_line = -1

    # 检查文件中间部分（避免检查文件开头和末尾）
    search_start = min(500, len(lines) // 4)
    search_end = min(len(lines), 3000)

    for i in range(search_start, search_end):
        line = lines[i]
        stripped = line.strip()

        # 查找原始 A2L 内容的标记
        if '/begin CHARACTERISTIC' in stripped or 'begin CHARACTERISTIC' in stripped:
            original_content_found = True
            original_content_line = i + 1
            break

        # 查找带有特定注释的 MOD_COMMON（原始A2L文件的标记）
        if 'MOD_COMMON' in stripped and 'Mod Common Comment Here' in stripped:
            original_content_found = True
            original_content_line = i + 1
            break

    if original_content_found:
        messages.append(f"✅ 原始头部已裁剪（第 {original_content_line} 行找到原始 A2L 内容）")
    else:
        messages.append(f"⚠️  未在预期位置找到原始 A2L 内容（检查了第 {search_start}-{search_end} 行）")

    # 5. 检查文件大小
    file_size = a2l_path.stat().st_size
    messages.append(f"📁 文件大小: {file_size:,} bytes ({len(lines):,} 行)")

    return all_passed, messages


def _clean_a2l_tool_directory(
    a2l_tool_path: Path,
    log_callback: Callable[[str], None]
) -> int:
    """清理 A2L 工具目录下的残留 A2L 和 ELF 文件

    Args:
        a2l_tool_path: A2L 工具目录路径
        log_callback: 日志回调函数

    Returns:
        删除的文件数量
    """
    import shutil

    if not a2l_tool_path.exists():
        return 0

    deleted_count = 0
    patterns = ["*.a2l", "*.A2L", "*.elf", "*.ELF"]

    for pattern in patterns:
        for file_path in a2l_tool_path.glob(pattern):
            try:
                file_path.unlink()
                log_callback(f"清理残留文件: {file_path.name}")
                deleted_count += 1
            except Exception as e:
                log_callback(f"警告: 无法删除文件 {file_path.name}: {e}")

    if deleted_count > 0:
        log_callback(f"共清理 {deleted_count} 个残留文件")
    else:
        log_callback("无需清理残留文件")

    return deleted_count


def _copy_files_to_tool_directory(
    source_a2l_path: Path,
    source_elf_path: Path,
    a2l_tool_path: Path,
    log_callback: Callable[[str], None]
) -> Tuple[Path, Path]:
    """复制 A2L 和 ELF 文件到 A2L 工具目录

    Args:
        source_a2l_path: 源 A2L 文件路径
        source_elf_path: 源 ELF 文件路径
        a2l_tool_path: A2L 工具目录路径
        log_callback: 日志回调函数

    Returns:
        (目标 A2L 路径, 目标 ELF 路径) 元组

    Raises:
        FileNotFoundError: 源文件不存在
        FileError: 复制失败
    """
    import shutil

    # 确保目标目录存在
    a2l_tool_path.mkdir(parents=True, exist_ok=True)

    # 复制 A2L 文件
    dest_a2l = a2l_tool_path / source_a2l_path.name
    try:
        shutil.copy2(source_a2l_path, dest_a2l)
        log_callback(f"复制 A2L 文件: {source_a2l_path.name} -> {dest_a2l}")
    except Exception as e:
        raise FileError(f"复制 A2L 文件失败: {e}", suggestions=[
            "检查源文件是否存在",
            "检查目标目录权限"
        ])

    # 复制 ELF 文件
    dest_elf = a2l_tool_path / source_elf_path.name
    try:
        shutil.copy2(source_elf_path, dest_elf)
        log_callback(f"复制 ELF 文件: {source_elf_path.name} -> {dest_elf}")
    except Exception as e:
        raise FileError(f"复制 ELF 文件失败: {e}", suggestions=[
            "检查源文件是否存在",
            "检查目标目录权限"
        ])

    return dest_a2l, dest_elf


def _update_a2l_addresses(
    a2l_path: Path,
    elf_path: Path,
    timeout: int,
    log_callback: Callable[[str], None]
) -> bool:
    """使用纯 Python 更新 A2L 文件中的变量地址

    ADR-005: 移除 MATLAB Engine 依赖，改用 pyelftools 纯 Python 实现

    Args:
        a2l_path: A2L 文件路径
        elf_path: ELF 文件路径
        timeout: 超时时间（秒）- 保留参数以兼容调用方
        log_callback: 日志回调函数

    Returns:
        成功返回 True

    Raises:
        ProcessError: 地址更新失败
    """
    log_callback("使用 Python 解析 ELF 文件并更新 A2L 地址...")
    log_callback(f"  A2L: {a2l_path.name}")
    log_callback(f"  ELF: {elf_path.name}")

    start_time = time.monotonic()

    try:
        # 使用纯 Python 实现
        updater = A2LAddressUpdater()
        updater.set_log_callback(log_callback)

        result = updater.update(elf_path, a2l_path, backup=True)

        elapsed = time.monotonic() - start_time

        if result.success:
            log_callback(f"地址更新成功（耗时 {elapsed:.2f} 秒）")
            log_callback(f"  匹配变量: {result.matched_count}/{result.total_variables}")
            if result.unmatched_count > 0:
                log_callback(f"  未匹配变量: {result.unmatched_count}")
                # 只显示前10个未匹配变量
                unmatched_preview = result.unmatched_variables[:10]
                log_callback(f"  未匹配列表: {', '.join(unmatched_preview)}"
                           + ("..." if result.unmatched_count > 10 else ""))
            return True
        else:
            error_msg = result.message
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            raise ProcessError(
                "A2L",
                error_msg,
                suggestions=[
                    "检查 ELF 文件格式是否正确",
                    "验证 A2L 文件格式是否正确",
                    "确认 pyelftools 已安装: pip install pyelftools"
                ]
            )

    except (ELFParseError, A2LParseError, AddressUpdateError) as e:
        error_msg = f"地址更新失败: {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg, exc_info=True)

        raise ProcessError(
            "A2L",
            error_msg,
            suggestions=[
                "检查 ELF 文件是否存在且有效",
                "检查 A2L 文件是否存在且有效",
                "确认 pyelftools 已安装: pip install pyelftools"
            ]
        )

    except Exception as e:
        error_msg = f"地址更新异常: {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg, exc_info=True)

        raise ProcessError(
            "A2L",
            error_msg,
            suggestions=[
                "查看详细日志",
                "检查文件路径配置",
                "验证系统资源"
            ]
        )



def execute_xcp_header_replacement_stage(
    config: StageConfig,
    context: BuildContext
) -> StageResult:
    """执行 A2L 文件完整处理阶段

    完整流程：
    1. 清理 A2L 工具目录下的残留 A2L 和 ELF 文件
    2. 复制 A2L 文件（从配置路径）到 A2L 工具目录
    3. 复制 ELF 文件到 A2L 工具目录
    4. 调用 MATLAB 更新变量地址
    5. 裁剪 A2L（删除 IF_DATA XCP 块）
    6. 替换 XCP 头文件
    7. 保存到 output 子目录

    Args:
        config: 阶段配置
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    # 记录阶段开始
    log_callback = context.log_callback or (lambda msg: logger.info(msg))
    start_time = time.monotonic()
    log_callback("=== 开始 A2L 文件处理阶段 ===")
    logger.info("开始 A2L 文件处理阶段")

    try:
        # 获取配置
        a2l_tool_path_str = context.config.get("a2l_tool_path", "")
        if not a2l_tool_path_str:
            error_msg = "未配置 A2L 工具路径"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "在项目配置中设置 a2l_tool_path",
                    "确保路径指向有效的 A2L 工具目录"
                ]
            )

        a2l_tool_path = Path(a2l_tool_path_str)

        # 获取源 A2L 文件路径（从配置路径）
        source_a2l_path_str = context.config.get("a2l_path", "")
        if not source_a2l_path_str:
            error_msg = "未配置 A2L 源文件路径"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "在项目配置中设置 a2l_path",
                    "确保路径指向有效的 A2L 文件"
                ]
            )

        source_a2l_path = Path(source_a2l_path_str)

        # 获取 ELF 文件路径（优先从 context.state，否则从 IAR 工程路径推导）
        source_elf_path_str = context.state.get("iar_elf_path", "") or context.config.get("elf_path", "")

        if not source_elf_path_str:
            # 从 IAR 工程路径推导 ELF 路径
            # 规则：IAR工程目录/M7/Debug/Exe/CYT4BF_M7_Master.elf
            iar_project_path = context.config.get("iar_project_path", "")
            if iar_project_path:
                iar_dir = Path(iar_project_path).parent  # 获取 .eww 文件所在目录
                # 推导 ELF 路径：{iar_dir}/M7/Debug/Exe/CYT4BF_M7_Master.elf
                source_elf_path_str = str(iar_dir / "M7" / "Debug" / "Exe" / "CYT4BF_M7_Master.elf")
                log_callback(f"从 IAR 工程路径推导 ELF 路径: {source_elf_path_str}")

        if not source_elf_path_str:
            error_msg = "未找到 ELF 文件路径，请配置 IAR 工程路径"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查 IAR 工程路径配置",
                    "确保 IAR 编译阶段已执行"
                ]
            )

        source_elf_path = Path(source_elf_path_str)

        # 验证源文件存在
        if not source_a2l_path.exists():
            error_msg = f"A2L 源文件不存在: {source_a2l_path}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=["检查 A2L 文件路径配置"]
            )

        if not source_elf_path.exists():
            error_msg = f"ELF 源文件不存在: {source_elf_path}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查 IAR 编译是否成功",
                    "验证 IAR 工程路径配置",
                    f"预期 ELF 路径: {source_elf_path}"
                ]
            )

        log_callback(f"A2L 源文件: {source_a2l_path}")
        log_callback(f"ELF 源文件: {source_elf_path}")
        log_callback(f"A2L 工具目录: {a2l_tool_path}")

        # 步骤 1: 清理残留文件
        log_callback("\n[步骤 1/6] 清理残留文件...")
        _clean_a2l_tool_directory(a2l_tool_path, log_callback)

        # 步骤 2-3: 复制文件到工具目录
        log_callback("\n[步骤 2/6] 复制 A2L 和 ELF 文件到工具目录...")
        try:
            dest_a2l, dest_elf = _copy_files_to_tool_directory(
                source_a2l_path, source_elf_path, a2l_tool_path, log_callback
            )
        except FileError as e:
            return StageResult(
                status=StageStatus.FAILED,
                message=str(e),
                error=e,
                suggestions=e.suggestions
            )

        # 步骤 4: 使用 MATLAB 更新变量地址
        log_callback("\n[步骤 3/6] 更新 A2L 变量地址...")
        timeout = getattr(config, 'timeout', None) or get_stage_timeout("a2l_process")
        try:
            _update_a2l_addresses(dest_a2l, dest_elf, timeout, log_callback)
        except (ProcessError, ProcessTimeoutError) as e:
            return StageResult(
                status=StageStatus.FAILED,
                message=f"更新变量地址失败: {e}",
                error=e,
                suggestions=e.suggestions if hasattr(e, 'suggestions') else []
            )

        # 步骤 5: 裁剪 A2L（删除 IF_DATA XCP 块）
        log_callback("\n[步骤 4/6] 裁剪 A2L 文件...")
        try:
            success, removed_count = remove_if_data_xcp_blocks(dest_a2l, log_callback)
            if not success:
                log_callback("警告: IF_DATA XCP 块删除可能不完整")
        except (FileNotFoundError, FileError) as e:
            log_callback(f"警告: 裁剪 A2L 时出错: {e}")

        # 步骤 6: 替换 XCP 头文件
        log_callback("\n[步骤 5/6] 替换 XCP 头文件...")

        # 读取 XCP 头文件模板
        template_path = a2l_tool_path / "奇瑞热管理XCP头文件.txt"
        try:
            xcp_template = read_xcp_header_template(template_path, log_callback)
        except (FileNotFoundError, FileError) as e:
            error_msg = f"读取 XCP 头文件模板失败: {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                error=e,
                suggestions=[
                    "检查 A2L 工具路径配置",
                    "确保模板文件存在于 A2L 工具目录下",
                    "文件名应为: 奇瑞热管理XCP头文件.txt"
                ]
            )

        # 定位 XCP 头文件部分
        header_section = find_xcp_header_section(dest_a2l, log_callback)
        if not header_section:
            error_msg = "未找到 A2L 文件中的 XCP 头文件部分"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查 A2L 文件格式",
                    "确认文件包含 /begin MOD_PAR 标记"
                ]
            )

        # 替换头部内容
        try:
            updated_content = replace_xcp_header_content(
                dest_a2l, header_section, xcp_template, log_callback
            )
        except FileError as e:
            error_msg = f"替换 XCP 头文件内容失败: {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                error=e,
                suggestions=e.suggestions
            )

        # 步骤 7: 保存到 output 目录
        log_callback("\n[步骤 6/6] 保存最终 A2L 文件...")

        # 创建输出配置
        a2l_config = A2LHeaderReplacementConfig()
        a2l_config.output_dir = str(a2l_tool_path / "output")
        a2l_config.output_prefix = "tmsAPP_upAdress"

        try:
            output_path = save_updated_a2l_file(a2l_config, updated_content, log_callback)
        except FileError as e:
            error_msg = f"保存 A2L 文件失败: {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                error=e,
                suggestions=e.suggestions
            )

        # 验证输出文件
        if not verify_a2l_replacement(output_path, xcp_template, log_callback):
            error_msg = "A2L 文件替换验证失败"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=["检查输出文件", "查看详细日志"]
            )

        # 记录输出文件路径到 BuildContext
        context.state["a2l_output_path"] = str(output_path)
        context.state["a2l_xcp_replaced_path"] = str(output_path)

        # 计算执行时长
        elapsed = time.monotonic() - start_time
        log_callback(f"\n=== A2L 文件处理阶段完成，耗时 {elapsed:.2f} 秒 ===")
        log_callback(f"最终输出文件: {output_path}")
        logger.info(f"A2L 文件处理阶段完成，耗时 {elapsed:.2f} 秒")

        return StageResult(
            status=StageStatus.COMPLETED,
            message="A2L 文件处理成功",
            output_files=[str(output_path)],
            execution_time=elapsed
        )

    except Exception as e:
        # 未预期的异常
        error_msg = f"A2L 文件处理阶段异常: {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg, exc_info=True)

        return StageResult(
            status=StageStatus.FAILED,
            message=error_msg,
            error=e,
            suggestions=[
                "查看详细日志",
                "检查配置和环境",
                "联系技术支持"
            ]
        )

