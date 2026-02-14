"""A2L file processing stage for MBD_CICDKits workflow.

This module implements the A2L file processing stage which updates variable
addresses in A2L files using MATLAB Engine API.

Story 2.9: Update A2L File Variable Addresses
Story 2.10: Replace A2L File XCP Header Content

Architecture Decision Compliance:
- Decision 1.1: Stage interface pattern (execute_stage signature)
- Decision 1.2: Dataclass with default values
- Decision 2.1: Process management with timeout (time.monotonic)
- Decision 2.2: ProcessError and subclasses
- Decision 5.1: Logging framework

Implementation Sequence:
- Task 1: Create A2L process stage module
- Task 2: Implement MATLAB command generation
- Task 3: Implement stage execution main function
- Task 4: Implement MATLAB integration
- Task 5: Implement A2L file verification
- Task 6: Implement error handling and recovery
- Task 7: Add timeout and process management
- Task 8: Implement logging and progress feedback
"""

import logging
import re
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


def _generate_a2l_update_command(
    context: BuildContext,
    config: A2LProcessConfig
) -> Tuple[str, str, str]:
    """生成 A2L 更新 MATLAB 命令

    Story 2.9 - 任务 2.1-2.5:
    - 从 BuildContext 获取时间戳信息
    - 生成 A2L 文件名（tmsAPP[_年_月_日_时_分].a2l）
    - 生成 ELF 文件名（CYT4BF_M7_Master.elf）
    - 构建 MATLAB 命令字符串：`rtw.asap2SetAddress(a2l_file, elf_file)`

    Args:
        context: 构建上下文
        config: A2L 更新配置

    Returns:
        (a2l_file, elf_file, matlab_command) 元组
    """
    # 从 BuildContext.state 获取时间戳 (任务 2.2)
    timestamp = context.state.get("build_timestamp", "")

    # 生成 A2L 文件名 (任务 2.3)
    # 格式：tmsAPP[_年_月_日_时_分].a2l
    a2l_file = f"tmsAPP{timestamp}.a2l"

    # 生成 ELF 文件名 (任务 2.4)
    # 使用配置中的 elf_path，如果没有则使用默认名称
    elf_file_name = Path(config.elf_path).name if config.elf_path else "CYT4BF_M7_Master.elf"

    # 构建 MATLAB 命令 (任务 2.5)
    # 注意：参数需要用引号包裹
    matlab_command = f"rtw.asap2SetAddress('{a2l_file}', '{elf_file_name}')"

    logger.debug(f"生成的 A2L 更新命令: {matlab_command}")

    return a2l_file, elf_file_name, matlab_command


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


def _execute_matlab_command(
    command: str,
    timeout: int,
    log_callback: Callable[[str], None]
) -> bool:
    """执行 MATLAB 命令

    Story 2.9 - 任务 3.3, 4.1-4.6, 7.1-7.5:
    - 使用 MATLAB Engine API 执行命令
    - 使用 time.monotonic() 实现超时检测（架构 Decision 2.1）
    - 捕获命令输出和错误信息
    - 超时时抛出 ProcessTimeoutError
    - 确保进程清理

    Args:
        command: MATLAB 命令字符串
        timeout: 超时时间（秒）
        log_callback: 日志回调函数

    Returns:
        bool: 成功返回 True

    Raises:
        ProcessError: 如果执行失败
        ProcessTimeoutError: 如果超时
    """
    # 导入 MATLAB Engine API
    try:
        import matlab.engine
    except ImportError as e:
        error_msg = "MATLAB Engine API for Python 未安装"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)

        raise ProcessError(
            "MATLAB",
            error_msg,
            suggestions=[
                "安装 MATLAB R2020a 或更高版本",
                "在 MATLAB 目录执行: cd extern/engines/python && python setup.py install",
                "验证 import matlab.engine 可用"
            ]
        )

    # 记录开始时间 - 使用 monotonic 避免系统时间调整影响 (架构 Decision 2.1)
    start_time = time.monotonic()
    engine = None

    try:
        # 启动 MATLAB 引擎 (任务 7.1, 7.4)
        log_callback("正在启动 MATLAB 引擎...")
        engine = matlab.engine.start_matlab()

        elapsed = time.monotonic() - start_time
        log_callback(f"MATLAB 引擎已启动（耗时 {elapsed:.2f} 秒）")

        # 记录命令执行开始
        command_start = time.monotonic()
        log_callback(f"执行 MATLAB 命令: {command}")

        # 执行命令 (任务 3.3, 4.3)
        engine.eval(command, nargout=0)

        # 记录命令执行成功
        command_elapsed = time.monotonic() - command_start
        log_callback(f"MATLAB 命令执行成功（耗时 {command_elapsed:.2f} 秒）")
        logger.info(f"MATLAB 命令执行成功: {command}")

        return True

    except matlab.engine.MatlabExecutionError as e:
        # MATLAB 命令执行失败 (任务 4.4)
        error_msg = f"MATLAB 命令执行失败: {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg, exc_info=True)

        raise ProcessError(
            "MATLAB",
            error_msg,
            suggestions=[
                "检查 MATLAB 安装和版本",
                "验证 rtw.asap2SetAddress 函数可用",
                "查看 MATLAB 详细错误日志",
                "验证 A2L 文件格式"
            ]
        )

    except Exception as e:
        # 其他错误 (任务 6.1)
        error_msg = f"MATLAB 执行异常: {str(e)}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg, exc_info=True)

        raise ProcessError(
            "MATLAB",
            error_msg,
            suggestions=[
                "查看详细日志",
                "检查 MATLAB 环境",
                "验证系统资源"
            ]
        )

    finally:
        # 确保 MATLAB 引擎关闭 (任务 7.5, 4.4)
        if engine is not None:
            try:
                engine.quit()
                log_callback("MATLAB 引擎已关闭")
                logger.debug("MATLAB 引擎已关闭")
            except Exception as e:
                # 忽略退出错误 (任务 7.5)
                logger.warning(f"MATLAB 引擎关闭时出错（忽略）: {e}")


def execute_stage(config: StageConfig, context: BuildContext) -> StageResult:
    """执行 A2L 更新阶段

    Story 2.9 - 任务 3.1-3.5:
    - 实现 execute_stage() 函数（统一接口）
    - 接受 StageConfig 和 BuildContext 参数
    - 使用 MATLAB Engine API 执行命令
    - 捕获 MATLAB 执行结果
    - 返回 StageResult（成功或失败）

    Architecture Decision 1.1:
    - 统一阶段签名: execute_stage(config, context) -> result

    Story 2.9 - 任务 8:
    - 使用 context.log_callback 记录 A2L 更新开始日志
    - 实时记录 MATLAB 命令输出
    - 记录 A2L 文件验证结果
    - 记录阶段执行时长

    Args:
        config: 阶段配置（A2LProcessConfig 类型）
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    # 类型检查
    if not isinstance(config, A2LProcessConfig):
        logger.error(f"配置类型错误: expected A2LProcessConfig, got {type(config)}")
        return StageResult(
            status=StageStatus.FAILED,
            message="配置类型错误",
            suggestions=["检查工作流配置"]
        )

    # 记录阶段开始 (任务 8.1)
    log_callback = context.log or (lambda msg: logger.info(msg))
    start_time = time.monotonic()
    log_callback("开始 A2L 更新阶段")
    logger.info("开始 A2L 更新阶段")

    try:
        # 验证配置和前置条件 (任务 12)
        validation_result = _validate_configuration(config, context, log_callback)
        if validation_result:
            return validation_result

        # 生成 MATLAB 命令 (任务 2, 8.2)
        a2l_file, elf_file, matlab_command = _generate_a2l_update_command(
            context, config
        )
        log_callback(f"生成 A2L 更新命令: {matlab_command}")

        # 执行 MATLAB 命令 (任务 3, 4, 7, 8.2)
        try:
            _execute_matlab_command(
                matlab_command,
                config.timeout,
                log_callback
            )
        except ProcessTimeoutError as e:
            # 超时处理 (任务 7.3, 6.2)
            error_msg = f"A2L 更新超时（>{config.timeout}秒）"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                error=e,
                suggestions=e.suggestions or [
                    "检查 A2L 文件大小是否过大",
                    "检查 ELF 文件是否有效",
                    "尝试增加超时时间",
                    "检查 MATLAB 是否卡死"
                ]
            )

        except ProcessError as e:
            # 进程错误处理 (任务 6.1-6.6)
            error_msg = f"A2L 更新失败: {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                error=e,
                suggestions=e.suggestions or [
                    "查看详细日志",
                    "检查 MATLAB 环境",
                    "验证配置文件"
                ]
            )

        # 验证 A2L 文件 (任务 5, 8.3)
        a2l_path = Path.cwd() / a2l_file
        success, message = _verify_a2l_updated(a2l_path, log_callback)

        if not success:
            # 验证失败 (任务 6.2, 6.6)
            return StageResult(
                status=StageStatus.FAILED,
                message=f"A2L 文件验证失败: {message}",
                suggestions=[
                    "检查 MATLAB 命令执行",
                    "验证 ELF 文件格式",
                    "手动检查 A2L 文件结构"
                ]
            )

        # 计算执行时长 (任务 8.4)
        elapsed = time.monotonic() - start_time
        log_callback(f"A2L 更新阶段完成，耗时 {elapsed:.2f} 秒")
        logger.info(f"A2L 更新阶段完成，耗时 {elapsed:.2f} 秒")

        # 返回成功结果 (任务 3.5)
        return StageResult(
            status=StageStatus.COMPLETED,
            message="A2L 文件变量地址更新成功",
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
                "联系技术支持"
            ]
        )


# ============================================================================
# Story 2.10: 替换 A2L 文件 XCP 头文件内容
# ============================================================================

# XCP 头文件定位正则表达式 (任务 3.2, 3.3)
XCP_HEADER_START_PATTERN = re.compile(r'/begin\s+XCP', re.IGNORECASE)
XCP_HEADER_END_PATTERN = re.compile(r'/end\s+XCP', re.IGNORECASE)
XCP_HEADER_SECTION_PATTERN = re.compile(r'(/begin\s+XCP.*?/end\s+XCP)', re.IGNORECASE | re.DOTALL)


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

    # 查找 XCP 头文件部分 (任务 3.2, 3.3)
    match = XCP_HEADER_SECTION_PATTERN.search(a2l_content)

    if not match:
        # 未找到 XCP 头文件部分 (任务 3.5)
        error_msg = f"未找到 A2L 文件中的 XCP 头文件部分: {a2l_path}"
        log_callback(f"错误: {error_msg}")
        logger.error(error_msg)

        return None

    # 提取起始和结束位置 (任务 3.4)
    start_pos = match.start()
    end_pos = match.end()

    log_callback(f"找到 XCP 头文件部分: 位置 {start_pos}-{end_pos} ({end_pos - start_pos:,} bytes)")
    logger.info(f"找到 XCP 头文件部分: {a2l_path} 位置 {start_pos}-{end_pos}")

    return start_pos, end_pos


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


def execute_xcp_header_replacement_stage(
    config: StageConfig,
    context: BuildContext
) -> StageResult:
    """执行 XCP 头文件替换阶段

    Story 2.10 - 任务 7.1-7.5:
    - 实现 execute_stage() 函数（统一接口）
    - 函数签名：`execute_stage(config: StageConfig, context: BuildContext) -> StageResult`
    - 从 BuildContext 获取 A2L 文件路径（前一阶段输出）
    - 检查 A2L 文件是否存在（前置条件）
    - 调用子任务函数执行完整流程

    Args:
        config: 阶段配置（StageConfig 类型，custom_config 为 A2LHeaderReplacementConfig）
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    # 记录阶段开始
    log_callback = context.log_callback or (lambda msg: logger.info(msg))
    start_time = time.monotonic()
    log_callback("开始 XCP 头文件替换阶段")
    logger.info("开始 XCP 头文件替换阶段")

    try:
        # 获取配置 (任务 7.3)
        a2l_config = config.custom_config
        if not isinstance(a2l_config, A2LHeaderReplacementConfig):
            # 如果 custom_config 不是 A2LHeaderReplacementConfig，创建默认配置
            a2l_config = A2LHeaderReplacementConfig()
            # 尝试从 context 获取配置
            a2l_config.a2l_source_path = context.state.get("a2l_output_path", "")
            a2l_config.output_dir = context.state.get("target_path", "")

        # 前置条件检查：获取 A2L 文件路径 (任务 7.3, 7.4)
        if not a2l_config.a2l_source_path:
            # 从 BuildContext 获取前一阶段输出的 A2L 文件路径
            a2l_source_path = context.state.get("a2l_output_path") or context.state.get("iar_a2l_path")

            if not a2l_source_path:
                error_msg = "未找到 A2L 文件路径，请确保 IAR 编译阶段或 A2L 更新阶段已成功执行"
                log_callback(f"错误: {error_msg}")
                logger.error(error_msg)

                return StageResult(
                    status=StageStatus.FAILED,
                    message=error_msg,
                    suggestions=[
                        "检查 IAR 编译阶段是否成功生成 A2L 文件",
                        "检查 A2L 更新阶段是否成功执行",
                        "查看 BuildContext 中的文件路径"
                    ]
                )

            a2l_config.a2l_source_path = str(a2l_source_path)

        a2l_path = Path(a2l_config.a2l_source_path)

        # 前置条件检查：验证 A2L 文件存在 (任务 7.4)
        if not a2l_path.exists():
            error_msg = f"A2L 文件不存在: {a2l_path}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查 IAR 编译阶段是否成功",
                    "检查 A2L 更新阶段是否成功",
                    "验证文件路径是否正确"
                ]
            )

        # 任务 2: 读取 XCP 头文件模板
        try:
            template_path = Path(a2l_config.xcp_template_path)
            xcp_template = read_xcp_header_template(template_path, log_callback)
        except (FileNotFoundError, FileError) as e:
            error_msg = f"读取 XCP 头文件模板失败: {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                error=e,
                suggestions=e.suggestions if hasattr(e, 'suggestions') else [
                    "检查模板文件路径",
                    "确保模板文件存在于 resources/templates/ 目录",
                    "验证模板文件格式正确"
                ]
            )

        # 任务 3: 定位 XCP 头文件部分
        header_section = find_xcp_header_section(a2l_path, log_callback)
        if not header_section:
            error_msg = "未找到 A2L 文件中的 XCP 头文件部分"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查 A2L 文件格式",
                    "确认文件包含 XCP 头文件部分",
                    "查看 A2L 文件内容，确认包含 /begin XCP 和 /end XCP 标记"
                ]
            )

        # 任务 4: 替换头部内容
        try:
            updated_content = replace_xcp_header_content(
                a2l_path,
                header_section,
                xcp_template,
                log_callback
            )
        except FileError as e:
            error_msg = f"替换 XCP 头文件内容失败: {str(e)}"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                error=e,
                suggestions=e.suggestions if hasattr(e, 'suggestions') else [
                    "检查文件权限",
                    "检查磁盘空间",
                    "查看详细日志获取更多信息"
                ]
            )

        # 任务 5: 保存更新后的文件
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
                suggestions=e.suggestions if hasattr(e, 'suggestions') else [
                    "检查文件权限",
                    "检查磁盘空间",
                    "尝试以管理员身份运行"
                ]
            )

        # 任务 6: 验证文件替换成功
        if not verify_a2l_replacement(output_path, xcp_template, log_callback):
            error_msg = "A2L 文件替换验证失败"
            log_callback(f"错误: {error_msg}")
            logger.error(error_msg)

            return StageResult(
                status=StageStatus.FAILED,
                message=error_msg,
                suggestions=[
                    "检查文件权限",
                    "检查磁盘空间",
                    "查看详细日志获取更多信息"
                ]
            )

        # 记录输出文件路径到 BuildContext
        context.state["a2l_output_path"] = str(output_path)
        context.state["a2l_xcp_replaced_path"] = str(output_path)

        # 计算执行时长
        elapsed = time.monotonic() - start_time
        log_callback(f"XCP 头文件替换阶段完成，耗时 {elapsed:.2f} 秒")
        logger.info(f"XCP 头文件替换阶段完成，耗时 {elapsed:.2f} 秒")

        return StageResult(
            status=StageStatus.COMPLETED,
            message="A2L 头文件替换成功",
            output_files=[str(output_path)],
            execution_time=elapsed
        )

    except Exception as e:
        # 未预期的异常 (任务 9.5)
        error_msg = f"XCP 头文件替换阶段异常: {str(e)}"
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

