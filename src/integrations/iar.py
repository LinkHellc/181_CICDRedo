"""IAR Compiler integration for MBD_CICDKits.

This module provides integration with IAR Embedded Workbench compiler.

Architecture Decision 2.1:
- 每次启动/停止 IAR 编译进程
- 超时检测使用 time.monotonic()
- 僵尸进程清理

Architecture Decision 2.2:
- 使用 ProcessError 统一管理错误
- ProcessTimeoutError 超时错误
- ProcessExitCodeError 退出码错误

Story 2.8 - 任务 1: 创建 IAR 集成模块
"""

import logging
import subprocess
import time
import re
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any

from core.constants import get_stage_timeout
from utils.errors import ProcessTimeoutError, ProcessExitCodeError, ProcessError

logger = logging.getLogger(__name__)


class IarIntegration:
    """IAR 编译器集成

    提供与 IAR 编译器的交互接口，包括：
    - 调用 iarbuild.exe 编译工程
    - 捕获编译输出
    - 验证 ELF/HEX 文件生成
    - 执行 HexMerge.bat
    - 超时检测和错误处理
    - 解析 IAR 编译错误

    Story 2.8 - 任务 1.2: 实现 IarIntegration 类，参考 MatlabIntegration 模式
    """

    # IAR 编译器最低版本要求（可选，目前不做严格版本检查）
    MIN_IAR_VERSION = "8.0"

    def __init__(
        self,
        log_callback: Optional[Callable[[str], None]] = None,
        timeout: Optional[int] = None
    ):
        """初始化 IAR 集成

        Story 2.8 - 任务 1.2:
        - 实现初始化方法

        Args:
            log_callback: 日志回调函数，用于实时输出
            timeout: 超时时间（秒），如果为 None 则使用默认配置
        """
        self.log_callback = log_callback or (lambda msg: None)
        self.timeout = timeout if timeout is not None else get_stage_timeout("iar_compile")
        self._is_running = False

        self._log(f"IAR 集成初始化完成，超时设置: {self.timeout} 秒")

    def _log(self, message: str) -> None:
        """记录日志

        Story 2.8 - 任务 1.5:
        - 添加时间戳到每条输出（使用 [HH:MM:SS] 格式）

        Args:
            message: 日志消息
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_message = f"{timestamp} {message}"
        self.log_callback(formatted_message)
        logger.debug(f"IAR: {message}")

    def is_running(self) -> bool:
        """检查 IAR 编译进程是否正在运行

        Story 2.8 - 任务 1.6:
        - 实现进程监控方法

        Returns:
            bool: 如果进程正在运行返回 True
        """
        return self._is_running

    def compile_project(
        self,
        project_path: str,
        build_config: str = "Debug",
        target: Optional[str] = None,
        extra_args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """编译 IAR 工程

        Story 2.8 - 任务 1.3:
        - 实现 compile_project() 方法调用 iarbuild.exe

        Story 2.8 - 任务 1.4:
        - 实现命令行参数构建（工程路径、编译配置）

        Args:
            project_path: IAR 工程文件路径（.eww）
            build_config: 编译配置（如 Debug, Release）
            target: 编译目标（可选）
            extra_args: 额外的命令行参数（可选）

        Returns:
            编译结果字典，包含:
            - success: 是否成功
            - exit_code: 退出码
            - output: 编译输出
            - errors: 错误列表
            - warnings: 警告列表
            - elf_file: ELF 文件路径（如果生成）
            - execution_time: 执行时间（秒）

        Raises:
            ProcessError: 如果编译器未找到
            ProcessTimeoutError: 如果编译超时
            ProcessExitCodeError: 如果编译失败
        """
        # 使用 time.monotonic() 记录开始时间 (Architecture Decision 2.1)
        start_time = time.monotonic()

        # 构建 IAR 编译命令 (Story 2.8 - 任务 1.4)
        cmd = self._build_compile_command(project_path, build_config, target, extra_args)

        self._log(f"开始 IAR 编译: {Path(project_path).name}")
        self._log(f"编译配置: {build_config}")
        self._log(f"命令: {' '.join(cmd[:3])} ...")

        # 执行编译命令 (Story 2.8 - 任务 1.5, 1.6)
        result = self._execute_command(cmd)

        # 计算执行时间
        execution_time = time.monotonic() - start_time
        result["execution_time"] = execution_time

        self._log(f"编译完成，耗时: {execution_time:.2f} 秒")

        return result

    def _build_compile_command(
        self,
        project_path: str,
        build_config: str,
        target: Optional[str],
        extra_args: Optional[List[str]]
    ) -> List[str]:
        """构建 IAR 编译命令

        Story 2.8 - 任务 1.4:
        - 实现命令行参数构建（工程路径、编译配置）

        Args:
            project_path: IAR 工程文件路径
            build_config: 编译配置
            target: 编译目标（可选）
            extra_args: 额外参数（可选）

        Returns:
            命令参数列表

        Raises:
            ProcessError: 如果 iarbuild.exe 未找到
        """
        # 检查 iarbuild.exe 是否可用
        if not self._check_iarbuild_available():
            raise ProcessError(
                "IAR",
                "IAR 编译器未找到: iarbuild.exe",
                suggestions=[
                    "检查 IAR Embedded Workbench 是否正确安装",
                    "验证 IAR 安装目录是否在 PATH 环境变量中",
                    "手动指定 iarbuild.exe 的完整路径"
                ]
            )

        # 构建基础命令
        cmd = ["iarbuild.exe"]

        # 添加工程路径（需要用引号包裹，如果包含空格）
        cmd.append(str(project_path))

        # 添加编译配置
        cmd.append("-build")
        cmd.append(build_config)

        # 添加编译目标（如果指定）
        if target:
            cmd.append("-make")
            cmd.append(f'"{target}"')

        # 添加详细日志
        cmd.append("-log")
        cmd.append("all")

        # 添加额外参数（如果指定）
        if extra_args:
            cmd.extend(extra_args)

        return cmd

    def _check_iarbuild_available(self) -> bool:
        """检查 iarbuild.exe 是否可用

        Returns:
            bool: 如果可用返回 True
        """
        try:
            # 尝试运行 iarbuild.exe --version（或帮助命令）
            result = subprocess.run(
                ["iarbuild.exe", "--help"],
                capture_output=True,
                timeout=5,
                shell=True
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
        except Exception:
            return False

    def _execute_command(self, cmd: List[str]) -> Dict[str, Any]:
        """执行 IAR 命令并捕获输出

        Story 2.8 - 任务 1.5:
        - 实现输出捕获和实时日志

        Story 2.8 - 任务 1.6:
        - 实现进程监控（超时、退出码）

        Args:
            cmd: 命令参数列表

        Returns:
            执行结果字典

        Raises:
            ProcessTimeoutError: 如果执行超时
            ProcessExitCodeError: 如果退出码非零
        """
        self._is_running = True
        self._log_start_time = time.monotonic()  # 记录命令开始时间
        process = None
        output_lines = []

        try:
            # 启动进程并实时捕获输出
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并 stderr 到 stdout
                universal_newlines=True,
                shell=True
            )

            self._log(f"IAR 进程已启动（PID: {process.pid}）")

            # 实时读取输出
            poll_interval = 0.1  # 0.1 秒轮询间隔
            line_buffer = []

            while True:
                # 检查超时 (Story 2.8 - 任务 1.6)
                elapsed = time.monotonic() - self._log_start_time if hasattr(self, '_log_start_time') else 0

                # 如果超时，终止进程
                if elapsed > self.timeout:
                    self._log(f"IAR 编译超时（{elapsed:.1f} 秒），正在终止进程...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    raise ProcessTimeoutError("IAR 编译", self.timeout)

                # 读取输出行
                line = process.stdout.readline()
                if not line:
                    # 检查进程是否结束
                    if process.poll() is not None:
                        break
                    time.sleep(poll_interval)
                    continue

                # 累积行（处理多行输出）
                line = line.rstrip('\r\n')
                line_buffer.append(line)
                output_lines.append(line)

                # 实时输出（过滤空行，减少噪音）
                if line.strip():
                    self._log(line)

            # 获取退出码
            exit_code = process.wait()
            self._log(f"IAR 进程结束，退出码: {exit_code}")

            # 检查退出码 (Story 2.8 - 任务 1.6)
            if exit_code != 0:
                raise ProcessExitCodeError("IAR 编译", exit_code)

            # 解析输出中的错误和警告 (Story 2.8 - 任务 3)
            errors = self._parse_errors(output_lines)
            warnings = self._parse_warnings(output_lines)

            return {
                "success": True,
                "exit_code": exit_code,
                "output": "\n".join(output_lines),
                "errors": errors,
                "warnings": warnings,
                "elf_file": self._extract_elf_path(output_lines),
                "execution_time": 0.0  # 由调用方设置
            }

        except ProcessTimeoutError:
            raise
        except ProcessExitCodeError:
            raise
        except Exception as e:
            logger.error(f"IAR 命令执行失败: {e}", exc_info=True)
            self._log(f"IAR 命令执行失败: {e}")

            return {
                "success": False,
                "exit_code": -1,
                "output": "\n".join(output_lines),
                "errors": [str(e)],
                "warnings": [],
                "elf_file": None,
                "execution_time": 0.0
            }
        finally:
            self._is_running = False
            # 确保进程被清理
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except Exception:
                    try:
                        process.kill()
                    except Exception:
                        pass

    def _parse_errors(self, output_lines: List[str]) -> List[Dict[str, Any]]:
        """解析 IAR 编译错误

        Story 2.8 - 任务 3.1:
        - 解析 IAR 编译错误格式

        Args:
            output_lines: 编译输出行列表

        Returns:
            错误列表，每个错误包含:
            - file: 文件名
            - line: 行号
            - code: 错误代码
            - message: 错误消息
            - type: 错误类型（syntax, linker, memory 等）
        """
        errors = []

        # IAR 错误格式模式:
        # Error[Pe1234]: C:\path\to\file.c 123  : error message
        # Error[Li005]: no space in destination memory
        error_pattern = r'Error\[(\w+)\]:\s*(.+?)(?:\s+(\d+)\s+:)?\s*(.*)'

        for line in output_lines:
            match = re.match(error_pattern, line)
            if match:
                error_code = match.group(1)
                message_part = match.group(2)
                line_num = match.group(3)
                message = match.group(4)

                # 确定错误类型 (Story 2.8 - 任务 3.2)
                error_type = self._classify_error(error_code, message)

                # 构建错误对象
                error = {
                    "code": error_code,
                    "file": "",
                    "line": int(line_num) if line_num else None,
                    "message": message or message_part,
                    "type": error_type,
                    "suggestions": self._get_error_suggestions(error_code, message, error_type)
                }

                # 提取文件名（如果存在）
                if ":\\" in message_part or ":/" in message_part:
                    # 文件路径在 message_part 中
                    file_match = re.search(r'([a-zA-Z]:\\[^:]+)', message_part)
                    if file_match:
                        error["file"] = file_match.group(1)

                errors.append(error)

        return errors

    def _parse_warnings(self, output_lines: List[str]) -> List[Dict[str, Any]]:
        """解析 IAR 编译警告

        Args:
            output_lines: 编译输出行列表

        Returns:
            警告列表
        """
        warnings = []

        # IAR 警告格式模式:
        # Warning[Pe1234]: warning message
        warning_pattern = r'Warning\[(\w+)\]:\s*(.+)'

        for line in output_lines:
            match = re.match(warning_pattern, line)
            if match:
                warning_code = match.group(1)
                message = match.group(2)

                warning = {
                    "code": warning_code,
                    "message": message,
                    "file": "",
                    "line": None
                }

                warnings.append(warning)

        return warnings

    def _classify_error(self, error_code: str, message: str) -> str:
        """分类错误类型

        Story 2.8 - 任务 3.2:
        - 识别常见错误类型（语法错误、链接错误、内存不足）

        Args:
            error_code: 错误代码
            message: 错误消息

        Returns:
            错误类型（syntax, linker, memory, other）
        """
        # 根据错误代码前缀判断
        if error_code.startswith("Pe"):
            return "syntax"  # Parser error
        elif error_code.startswith("Li"):
            return "linker"  # Linker error
        elif error_code.startswith("Me"):
            return "memory"  # Memory error
        else:
            # 根据消息内容判断
            if "no space" in message.lower() or "overflow" in message.lower():
                return "memory"
            elif "undefined" in message.lower() or "unresolved" in message.lower():
                return "linker"
            elif "syntax" in message.lower() or "parse" in message.lower():
                return "syntax"

            return "other"

    def _get_error_suggestions(self, error_code: str, message: str, error_type: str) -> List[str]:
        """获取错误的修复建议

        Story 2.8 - 任务 3.3:
        - 提供可操作的修复建议

        Args:
            error_code: 错误代码
            message: 错误消息
            error_type: 错误类型

        Returns:
            修复建议列表
        """
        # 内存相关错误
        if error_type == "memory":
            if "no space" in message.lower():
                return [
                    "检查模型大小是否超出内存限制",
                    "优化代码以减少内存使用",
                    "调整 IAR 内存配置（.icf 文件）",
                    "禁用不必要的功能或模块"
                ]
            else:
                return [
                    "检查内存分配配置",
                    "验证缓冲区大小",
                    "检查数组和数据结构定义"
                ]

        # 链接相关错误
        elif error_type == "linker":
            if "undefined" in message.lower() or "unresolved" in message.lower():
                return [
                    "检查是否所有源文件都已添加到工程",
                    "验证函数声明和定义是否匹配",
                    "检查库文件是否正确链接",
                    "验证外部引用的拼写"
                ]
            else:
                return [
                    "检查链接器配置文件",
                    "验证输出路径设置",
                    "检查库文件路径"
                ]

        # 语法相关错误
        elif error_type == "syntax":
            return [
                "查看错误行附近的代码",
                "检查拼写和语法",
                "验证括号、分号等标点符号",
                "检查头文件引用"
            ]

        # 其他错误
        return [
            "查看 IAR 文档获取错误代码详细信息",
            "检查工程配置",
            "查看完整编译日志"
        ]

    def _extract_elf_path(self, output_lines: List[str]) -> Optional[str]:
        """从编译输出中提取 ELF 文件路径

        Args:
            output_lines: 编译输出行列表

        Returns:
            ELF 文件路径（如果找到）
        """
        # IAR 输出中可能包含 ELF 文件路径
        elf_pattern = r'\.elf"'

        for line in output_lines:
            if '.elf' in line.lower():
                # 尝试提取完整的 ELF 文件路径
                match = re.search(r'([a-zA-Z]:\\[^"\s]+\.elf)', line, re.IGNORECASE)
                if match:
                    return match.group(1)

        return None

    def execute_hex_merge(
        self,
        bat_path: str,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """执行 HexMerge.bat 生成 HEX 文件

        Story 2.8 - 任务 1.7:
        - 实现 HexMerge.bat 执行

        Args:
            bat_path: HexMerge.bat 文件路径
            working_dir: 工作目录（可选）
            timeout: 超时时间（秒），默认 5 分钟

        Returns:
            执行结果字典

        Raises:
            ProcessError: 如果 bat 文件不存在
            ProcessTimeoutError: 如果执行超时
            ProcessExitCodeError: 如果退出码非零
        """
        timeout = timeout or 300  # 默认 5 分钟
        start_time = time.monotonic()

        bat_file = Path(bat_path)

        # 检查 bat 文件是否存在
        if not bat_file.exists():
            raise ProcessError(
                "HexMerge",
                f"HexMerge.bat 不存在: {bat_path}",
                suggestions=[
                    "检查 HexMerge.bat 文件路径是否正确",
                    "确认 HexMerge.bat 是否已创建",
                    "验证工作目录配置"
                ]
            )

        self._log(f"开始执行 HexMerge.bat: {bat_file.name}")
        self._log(f"工作目录: {working_dir or bat_file.parent}")

        # 设置工作目录
        cwd = working_dir if working_dir else bat_file.parent

        # 执行 bat 文件
        try:
            process = subprocess.run(
                [str(bat_file)],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True
            )

            output = process.stdout
            if process.stderr:
                output += "\n" + process.stderr

            self._log(f"HexMerge.bat 退出码: {process.returncode}")

            # 输出日志
            for line in output.split('\n'):
                if line.strip():
                    self._log(line)

            # 检查退出码
            if process.returncode != 0:
                raise ProcessExitCodeError("HexMerge.bat", process.returncode)

            execution_time = time.monotonic() - start_time
            self._log(f"HexMerge.bat 执行完成，耗时: {execution_time:.2f} 秒")

            return {
                "success": True,
                "exit_code": process.returncode,
                "output": output,
                "execution_time": execution_time
            }

        except subprocess.TimeoutExpired:
            self._log(f"HexMerge.bat 执行超时（>{timeout} 秒）")
            raise ProcessTimeoutError("HexMerge.bat", timeout)
        except ProcessExitCodeError:
            raise
        except Exception as e:
            logger.error(f"HexMerge.bat 执行失败: {e}", exc_info=True)
            self._log(f"HexMerge.bat 执行失败: {e}")

            raise ProcessError(
                "HexMerge",
                f"HexMerge.bat 执行失败: {e}",
                suggestions=[
                    "检查 HexMerge.bat 脚本内容",
                    "验证工作目录权限",
                    "查看详细日志获取更多信息"
                ]
            )

    def verify_elf_file(self, elf_path: str) -> Dict[str, Any]:
        """验证 ELF 文件

        Story 2.8 - 任务 2.1-2.2:
        - 验证 ELF 文件生成
        - 验证 ELF 文件大小非零

        Args:
            elf_path: ELF 文件路径

        Returns:
            验证结果字典，包含:
            - exists: 文件是否存在
            - is_valid: 是否有效
            - size: 文件大小（字节）
            - error: 错误信息（如果验证失败）
        """
        result = {
            "exists": False,
            "is_valid": False,
            "size": 0,
            "error": None
        }

        elf_file = Path(elf_path)

        # 检查文件是否存在 (Story 2.8 - 任务 2.1)
        if not elf_file.exists():
            result["error"] = f"ELF 文件不存在: {elf_path}"
            return result

        result["exists"] = True

        # 检查文件大小 (Story 2.8 - 任务 2.2)
        try:
            size = elf_file.stat().st_size
            result["size"] = size

            if size == 0:
                result["error"] = f"ELF 文件大小为 0: {elf_path}"
                return result

            result["is_valid"] = True
            self._log(f"ELF 文件验证通过: {elf_path} ({size} 字节)")

        except Exception as e:
            result["error"] = f"ELF 文件验证失败: {e}"

        return result

    def verify_hex_file(self, hex_path: str) -> Dict[str, Any]:
        """验证 HEX 文件

        Story 2.8 - 任务 2.3:
        - 验证 HEX 文件生成（如果执行了 HexMerge.bat）

        Args:
            hex_path: HEX 文件路径

        Returns:
            验证结果字典，包含:
            - exists: 文件是否存在
            - is_valid: 是否有效
            - size: 文件大小（字节）
            - error: 错误信息（如果验证失败）
        """
        result = {
            "exists": False,
            "is_valid": False,
            "size": 0,
            "error": None
        }

        hex_file = Path(hex_path)

        # 检查文件是否存在
        if not hex_file.exists():
            result["error"] = f"HEX 文件不存在: {hex_path}"
            return result

        result["exists"] = True

        # 检查文件大小
        try:
            size = hex_file.stat().st_size
            result["size"] = size

            if size == 0:
                result["error"] = f"HEX 文件大小为 0: {hex_path}"
                return result

            result["is_valid"] = True
            self._log(f"HEX 文件验证通过: {hex_path} ({size} 字节)")

        except Exception as e:
            result["error"] = f"HEX 文件验证失败: {e}"

        return result

    def get_error_report(self, errors: List[Dict[str, Any]]) -> str:
        """生成结构化错误报告

        Story 2.8 - 任务 3.4:
        - 生成结构化错误报告

        Args:
            errors: 错误列表

        Returns:
            格式化的错误报告字符串
        """
        if not errors:
            return "未发现编译错误"

        lines = ["=" * 60]
        lines.append("IAR 编译错误报告")
        lines.append("=" * 60)

        # 按类型分组
        error_by_type = {}
        for error in errors:
            error_type = error.get("type", "other")
            if error_type not in error_by_type:
                error_by_type[error_type] = []
            error_by_type[error_type].append(error)

        # 输出各类型错误
        for error_type, type_errors in error_by_type.items():
            lines.append(f"\n{error_type.upper()} 错误 ({len(type_errors)} 个):")
            lines.append("-" * 40)

            for error in type_errors:
                lines.append(f"  [{error['code']}] {error['message']}")
                if error.get("file"):
                    line_info = f"    文件: {error['file']}"
                    if error.get("line"):
                        line_info += f", 行: {error['line']}"
                    lines.append(line_info)

                if error.get("suggestions"):
                    lines.append("    建议:")
                    for suggestion in error["suggestions"][:2]:  # 最多显示 2 条建议
                        lines.append(f"      - {suggestion}")

        lines.append("\n" + "=" * 60)
        lines.append(f"总计: {len(errors)} 个错误")

        return "\n".join(lines)

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        return False

    def get_integration_info(self) -> Dict[str, Any]:
        """获取集成信息

        Returns:
            包含集成状态信息的字典
        """
        return {
            "is_running": self.is_running(),
            "timeout": self.timeout,
            "iarbuild_available": self._check_iarbuild_available(),
            "min_iar_version": self.MIN_IAR_VERSION
        }
