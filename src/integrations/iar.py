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

IAR 返回码说明:
- 0: 编译成功
- 1: 编译警告（有警告但编译成功）
- 2: 编译错误
- 3: 致命错误
"""

import logging
import subprocess
import time
import re
import os
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any

from core.constants import get_stage_timeout
from utils.errors import ProcessTimeoutError, ProcessExitCodeError, ProcessError

logger = logging.getLogger(__name__)


def find_iar_build_exe() -> Optional[str]:
    """查找 IarBuild.exe 的安装路径

    Returns:
        IarBuild.exe 的完整路径，如果未找到返回 None
    """
    # 常见的 IAR 安装路径
    common_paths = [
        r"D:\IDE\common\bin\IarBuild.exe",
        r"C:\Program Files\IAR Systems\Embedded Workbench\common\bin\IarBuild.exe",
        r"C:\Program Files (x86)\IAR Systems\Embedded Workbench\common\bin\IarBuild.exe",
    ]

    for path in common_paths:
        if Path(path).exists():
            return path

    # 尝试从 PATH 环境变量中查找
    try:
        result = subprocess.run(
            ["where", "IarBuild.exe"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0].strip()
    except Exception:
        pass

    return None


def find_ewp_from_eww(eww_path: str) -> Optional[str]:
    """从 .eww 工作区文件查找对应的 .ewp 项目文件

    Args:
        eww_path: .eww 工作区文件路径

    Returns:
        .ewp 项目文件路径，如果未找到返回 None
    """
    eww_file = Path(eww_path)

    # 如果已经是 .ewp 文件，直接返回
    if eww_file.suffix.lower() == '.ewp':
        return str(eww_file)

    # 如果是 .eww 文件，查找同目录或子目录中的 .ewp 文件
    if eww_file.suffix.lower() == '.eww':
        project_dir = eww_file.parent

        # 首先检查同目录
        ewp_files = list(project_dir.glob("*.ewp"))
        if ewp_files:
            return str(ewp_files[0])

        # 检查子目录
        for subdir in project_dir.iterdir():
            if subdir.is_dir():
                ewp_files = list(subdir.glob("*.ewp"))
                if ewp_files:
                    return str(ewp_files[0])

    return None


class IarIntegration:
    """IAR 编译器集成

    提供与 IAR 编译器的交互接口，包括：
    - 调用 IarBuild.exe 编译工程
    - 捕获编译输出
    - 验证 ELF/HEX 文件生成
    - 执行 HexMerge.bat
    - 超时检测和错误处理
    - 解析 IAR 编译错误
    """

    # IAR 返回码含义
    IAR_RETURN_CODES = {
        0: "编译成功",
        1: "编译警告（有警告但编译成功）",
        2: "编译错误（存在编译错误）",
        3: "致命错误（无法继续编译）",
        4: "用户中止",
        5: "内部错误（IAR工具内部错误）",
    }

    def __init__(
        self,
        log_callback: Optional[Callable[[str], None]] = None,
        timeout: Optional[int] = None,
        iar_build_path: Optional[str] = None
    ):
        """初始化 IAR 集成

        Args:
            log_callback: 日志回调函数，用于实时输出
            timeout: 超时时间（秒），如果为 None 则使用默认配置
            iar_build_path: IarBuild.exe 的路径，如果为 None 则自动查找
        """
        self.log_callback = log_callback or (lambda msg: None)
        self.timeout = timeout if timeout is not None else get_stage_timeout("iar_compile")
        self._is_running = False

        # 查找 IarBuild.exe
        self.iar_build_exe = iar_build_path or find_iar_build_exe()

        if self.iar_build_exe:
            self._log(f"IAR 集成初始化完成，IarBuild.exe: {self.iar_build_exe}")
        else:
            self._log("警告: 未找到 IarBuild.exe，IAR 编译将不可用")

        self._log(f"超时设置: {self.timeout} 秒")

    def _log(self, message: str) -> None:
        """记录日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        formatted_message = f"{timestamp} {message}"
        self.log_callback(formatted_message)
        logger.debug(f"IAR: {message}")

    def is_running(self) -> bool:
        """检查 IAR 编译进程是否正在运行"""
        return self._is_running

    def is_available(self) -> bool:
        """检查 IAR 编译器是否可用"""
        return self.iar_build_exe is not None and Path(self.iar_build_exe).exists()

    def compile_project(
        self,
        project_path: str,
        build_config: str = "Debug",
        target: Optional[str] = None,
        extra_args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """编译 IAR 工程

        Args:
            project_path: IAR 工程文件路径（.eww 或 .ewp）
            build_config: 编译配置（如 Debug, Release）
            target: 编译目标（可选）
            extra_args: 额外的命令行参数（可选）

        Returns:
            编译结果字典
        """
        start_time = time.monotonic()

        # 检查 IAR 是否可用
        if not self.is_available():
            return {
                "success": False,
                "exit_code": -1,
                "output": "",
                "errors": ["IAR 编译器不可用: 未找到 IarBuild.exe"],
                "warnings": [],
                "elf_file": None,
                "execution_time": 0.0
            }

        # 处理项目文件路径
        actual_project_path = project_path
        if project_path.endswith('.eww'):
            # 尝试从 .eww 查找 .ewp
            ewp_path = find_ewp_from_eww(project_path)
            if ewp_path:
                self._log(f"使用项目文件: {ewp_path}")
                actual_project_path = ewp_path
            else:
                self._log(f"警告: 无法从工作区 {project_path} 找到项目文件")

        # 构建命令
        cmd = f'"{self.iar_build_exe}" "{actual_project_path}" -build {build_config}'

        self._log(f"开始 IAR 编译: {Path(actual_project_path).name}")
        self._log(f"编译配置: {build_config}")

        # 执行编译
        result = self._execute_command(cmd)

        # 计算执行时间
        execution_time = time.monotonic() - start_time
        result["execution_time"] = execution_time

        # 根据返回码判断成功/失败
        exit_code = result["exit_code"]
        if exit_code == 0:
            result["success"] = True
            self._log(f"编译成功，耗时: {execution_time:.2f} 秒")
        elif exit_code == 1:
            # 退出码 1 表示有警告但编译成功
            result["success"] = True
            self._log(f"编译成功（有警告），耗时: {execution_time:.2f} 秒")
        else:
            result["success"] = False
            error_msg = self.IAR_RETURN_CODES.get(exit_code, f"未知错误 (退出码: {exit_code})")
            self._log(f"编译失败: {error_msg}")

        return result

    def _execute_command(self, cmd: str) -> Dict[str, Any]:
        """执行 IAR 命令并捕获输出"""
        self._is_running = True
        start_time = time.monotonic()
        output_lines = []

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )

            self._log(f"IAR 进程已启动（PID: {process.pid}）")

            # 实时读取输出
            while True:
                # 检查超时
                elapsed = time.monotonic() - start_time
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
                    if process.poll() is not None:
                        break
                    time.sleep(0.1)
                    continue

                line = line.rstrip('\r\n')
                output_lines.append(line)

                # 实时输出（过滤空行）
                if line.strip():
                    self._log(line)

            # 获取退出码
            exit_code = process.wait()
            self._log(f"IAR 进程结束，退出码: {exit_code}")

            # 解析输出
            output_text = "\n".join(output_lines)
            errors = self._parse_errors(output_lines)
            warnings = self._parse_warnings(output_lines)

            return {
                "exit_code": exit_code,
                "output": output_text,
                "errors": errors,
                "warnings": warnings,
                "elf_file": self._extract_elf_path(output_lines),
            }

        except ProcessTimeoutError:
            raise
        except Exception as e:
            logger.error(f"IAR 命令执行失败: {e}", exc_info=True)
            self._log(f"IAR 命令执行失败: {e}")
            return {
                "exit_code": -1,
                "output": "\n".join(output_lines),
                "errors": [str(e)],
                "warnings": [],
                "elf_file": None,
            }
        finally:
            self._is_running = False

    def _parse_errors(self, output_lines: List[str]) -> List[Dict[str, Any]]:
        """解析 IAR 编译错误"""
        errors = []
        error_pattern = r'Error\[(\w+)\]:\s*(.+)'

        for line in output_lines:
            match = re.match(error_pattern, line)
            if match:
                errors.append({
                    "code": match.group(1),
                    "message": match.group(2),
                    "type": self._classify_error(match.group(1), match.group(2))
                })

        return errors

    def _parse_warnings(self, output_lines: List[str]) -> List[Dict[str, Any]]:
        """解析 IAR 编译警告"""
        warnings = []
        warning_pattern = r'Warning\[(\w+)\]:\s*(.+)'

        for line in output_lines:
            match = re.match(warning_pattern, line)
            if match:
                warnings.append({
                    "code": match.group(1),
                    "message": match.group(2)
                })

        # 也检查 "Total number of warnings" 行
        for line in output_lines:
            match = re.search(r'Total number of warnings:\s*(\d+)', line)
            if match:
                count = int(match.group(1))
                if count > 0 and len(warnings) == 0:
                    warnings.append({"code": "Summary", "message": f"共 {count} 个警告"})

        return warnings

    def _classify_error(self, error_code: str, message: str) -> str:
        """分类错误类型"""
        if error_code.startswith("Pe"):
            return "syntax"
        elif error_code.startswith("Li"):
            return "linker"
        elif error_code.startswith("Me"):
            return "memory"
        else:
            return "other"

    def _extract_elf_path(self, output_lines: List[str]) -> Optional[str]:
        """从编译输出中提取 ELF 文件路径"""
        for line in output_lines:
            if '.elf' in line.lower():
                match = re.search(r'([a-zA-Z]:\\[^"\s]+\.elf)', line, re.IGNORECASE)
                if match:
                    return match.group(1)
        return None

    def verify_elf_file(self, elf_path: str) -> Dict[str, Any]:
        """验证 ELF 文件"""
        result = {"exists": False, "is_valid": False, "size": 0, "error": None}

        elf_file = Path(elf_path)
        if not elf_file.exists():
            result["error"] = f"ELF 文件不存在: {elf_path}"
            return result

        result["exists"] = True
        try:
            size = elf_file.stat().st_size
            result["size"] = size
            if size == 0:
                result["error"] = f"ELF 文件大小为 0"
                return result
            result["is_valid"] = True
            self._log(f"ELF 文件验证通过: {elf_path} ({size:,} 字节)")
        except Exception as e:
            result["error"] = f"ELF 文件验证失败: {e}"

        return result

    def verify_hex_file(self, hex_path: str) -> Dict[str, Any]:
        """验证 HEX 文件"""
        result = {"exists": False, "is_valid": False, "size": 0, "error": None}

        hex_file = Path(hex_path)
        if not hex_file.exists():
            result["error"] = f"HEX 文件不存在: {hex_path}"
            return result

        result["exists"] = True
        try:
            size = hex_file.stat().st_size
            result["size"] = size
            if size == 0:
                result["error"] = f"HEX 文件大小为 0"
                return result
            result["is_valid"] = True
            self._log(f"HEX 文件验证通过: {hex_path} ({size:,} 字节)")
        except Exception as e:
            result["error"] = f"HEX 文件验证失败: {e}"

        return result

    def execute_hex_merge(
        self,
        bat_path: str,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """执行 HexMerge.bat 生成 HEX 文件"""
        timeout = timeout or 300
        start_time = time.monotonic()

        bat_file = Path(bat_path)
        if not bat_file.exists():
            raise ProcessError("HexMerge", f"HexMerge.bat 不存在: {bat_path}")

        self._log(f"开始执行 HexMerge.bat: {bat_file.name}")

        cwd = working_dir if working_dir else bat_file.parent

        try:
            process = subprocess.run(
                [str(bat_file)],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )

            output = process.stdout
            if process.stderr:
                output += "\n" + process.stderr

            for line in output.split('\n'):
                if line.strip():
                    self._log(line)

            if process.returncode != 0:
                raise ProcessExitCodeError("HexMerge.bat", process.returncode, output)

            execution_time = time.monotonic() - start_time
            self._log(f"HexMerge.bat 执行完成，耗时: {execution_time:.2f} 秒")

            return {
                "success": True,
                "exit_code": process.returncode,
                "output": output,
                "execution_time": execution_time
            }

        except subprocess.TimeoutExpired:
            raise ProcessTimeoutError("HexMerge.bat", timeout)
        except ProcessExitCodeError:
            raise
        except Exception as e:
            raise ProcessError("HexMerge", f"HexMerge.bat 执行失败: {e}")

    def get_error_report(self, errors: List[Dict[str, Any]]) -> str:
        """生成结构化错误报告"""
        if not errors:
            return "未发现编译错误"

        lines = ["=" * 60, "IAR 编译错误报告", "=" * 60]

        for error in errors:
            lines.append(f"[{error.get('code', '?')}] {error.get('message', '')}")

        lines.append(f"\n总计: {len(errors)} 个错误")
        return "\n".join(lines)

    def get_integration_info(self) -> Dict[str, Any]:
        """获取集成信息"""
        return {
            "is_running": self.is_running(),
            "is_available": self.is_available(),
            "iar_build_exe": self.iar_build_exe,
            "timeout": self.timeout,
        }
