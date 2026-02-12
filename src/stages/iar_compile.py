"""IAR compile stage for MBD_CICDKits.

This module implements IAR compile stage that:
- Calls IAR iarbuild.exe to compile the project
- Validates ELF and HEX files
- Executes HexMerge.bat to generate HEX file
- Parses and reports compilation errors

Story 2.8: 调用 IAR 命令行编译

Architecture Decision 1.1:
- 统一阶段签名: execute_stage(config, context) -> result
- 返回 StageResult 对象
- 通过 BuildContext 传递状态

Architecture Decision 2.1:
- 使用 time.monotonic() 记录时间
- 超时检测和清理
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
from integrations.iar import IarIntegration
from utils.errors import (
    ProcessError,
    ProcessTimeoutError,
    ProcessExitCodeError
)

logger = logging.getLogger(__name__)


def _validate_iar_project_path(iar_project_path: str) -> None:
    """验证 IAR 工程路径

    Story 2.8 - 任务 6.1:
    - 处理 IAR 工程文件不存在错误

    Args:
        iar_project_path: IAR 工程文件路径

    Raises:
        ProcessError: 如果工程文件不存在
    """
    project_file = Path(iar_project_path)

    if not project_file.exists():
        raise ProcessError(
            "IAR",
            f"IAR 工程文件不存在: {iar_project_path}",
            suggestions=[
                "检查 iar_project_path 配置是否正确",
                "确认 .eww 文件是否存在",
                "验证路径拼写"
            ]
        )

    # 检查文件扩展名
    if project_file.suffix.lower() != ".eww":
        logger.warning(f"IAR 工程文件扩展名不是 .eww: {iar_project_path}")


def _find_elf_file(project_dir: Path) -> Optional[Path]:
    """查找编译生成的 ELF 文件

    Story 2.8 - 任务 2.1:
    - 验证 ELF 文件生成

    Args:
        project_dir: IAR 工程目录

    Returns:
        ELF 文件路径（如果找到）
    """
    # 常见的 ELF 文件位置
    elf_locations = [
        project_dir / "Debug" / "Exe",
        project_dir / "Release" / "Exe",
        project_dir / "Exe",
        project_dir,
    ]

    # 在每个位置查找 .elf 文件
    for location in elf_locations:
        if location.exists() and location.is_dir():
            elf_files = list(location.glob("*.elf"))
            if elf_files:
                # 返回最新修改的 ELF 文件
                return max(elf_files, key=lambda f: f.stat().st_mtime)

    # 递归搜索所有 ELF 文件（如果标准位置没找到）
    for elf_file in project_dir.rglob("*.elf"):
        return elf_file

    return None


def _find_hex_file(project_dir: Path) -> Optional[Path]:
    """查找生成的 HEX 文件

    Story 2.8 - 任务 2.3:
    - 验证 HEX 文件生成

    Args:
        project_dir: IAR 工程目录

    Returns:
        HEX 文件路径（如果找到）
    """
    # 搜索所有 HEX 文件
    for hex_file in project_dir.rglob("*.hex"):
        return hex_file

    return None


def _find_hex_merge_bat(project_dir: Path) -> Optional[Path]:
    """查找 HexMerge.bat 文件

    Args:
        project_dir: IAR 工程目录

    Returns:
        HexMerge.bat 文件路径（如果找到）
    """
    for bat_file in project_dir.rglob("HexMerge.bat"):
        return bat_file

    return None


def execute_stage(config: StageConfig, context: BuildContext) -> StageResult:
    """执行 IAR 编译阶段

    Story 2.8 - 任务 4.1-4.5:
    - 在 src/stages/ 创建 iar_compile.py
    - 实现 execute_stage(config, context) -> StageResult
    - 从 context.state["moved_files"] 读取移动的文件信息
    - 从 context.config 读取 IAR 工程路径
    - 将编译输出文件列表保存到 context.state["build_output"]
    - 处理编译失败，返回失败的 StageResult

    Args:
        config: 阶段配置
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    stage_name = "iar_compile"
    context.log(f"=== 开始执行阶段: {stage_name} ===")

    # 记录开始时间
    start_time = time.monotonic()

    # 初始化 IAR 集成
    iar = None

    try:
        # 读取移动后的文件信息 (Story 2.8 - 任务 4.3)
        moved_files = context.state.get("moved_files", {})

        if not moved_files:
            return StageResult(
                status=StageStatus.FAILED,
                message="未找到移动后的文件",
                suggestions=[
                    "确保文件移动阶段已完成",
                    "检查 context.state['moved_files'] 是否存在"
                ]
            )

        context.log(f"目标目录: {moved_files.get('target_dir', 'N/A')}")

        # 读取 IAR 工程配置 (Story 2.8 - 任务 4.4)
        iar_project_path = context.config.get("iar_project_path", "")

        if not iar_project_path:
            return StageResult(
                status=StageStatus.FAILED,
                message="未配置 IAR 工程路径",
                suggestions=[
                    "在项目配置中设置 iar_project_path",
                    "检查配置文件"
                ]
            )

        # 验证 IAR 工程文件存在 (Story 2.8 - 任务 6.1)
        _validate_iar_project_path(iar_project_path)
        context.log(f"IAR 工程路径: {iar_project_path}")

        # 获取 IAR 工程目录
        project_dir = Path(iar_project_path).parent

        # 获取编译配置（默认 Debug）
        build_config = context.config.get("iar_build_config", "Debug")
        context.log(f"编译配置: {build_config}")

        # 获取超时配置
        timeout = config.timeout or get_stage_timeout("iar_compile")
        context.log(f"超时设置: {timeout} 秒")

        # 初始化 IAR 集成
        iar = IarIntegration(
            log_callback=context.log,
            timeout=timeout
        )

        # 检查 iarbuild.exe 是否可用 (Story 2.8 - 任务 6.2)
        if not iar._check_iarbuild_available():
            return StageResult(
                status=StageStatus.FAILED,
                message="IAR 编译器未找到: iarbuild.exe",
                error=ProcessError(
                    "IAR",
                    "IAR 编译器未找到: iarbuild.exe",
                    suggestions=[
                        "检查 IAR Embedded Workbench 是否正确安装",
                        "验证 IAR 安装目录是否在 PATH 环境变量中",
                        "手动指定 iarbuild.exe 的完整路径"
                    ]
                ),
                suggestions=[
                    "检查 IAR Embedded Workbench 是否正确安装",
                    "验证 IAR 安装目录是否在 PATH 环境变量中",
                    "手动指定 iarbuild.exe 的完整路径"
                ]
            )

        # 执行 IAR 编译 (Story 2.8 - 任务 4.5)
        context.log("开始 IAR 编译...")

        try:
            compile_result = iar.compile_project(
                project_path=iar_project_path,
                build_config=build_config
            )
        except ProcessTimeoutError as e:
            # 处理编译超时 (Story 2.8 - 任务 6.3)
            logger.error(f"IAR 编译超时: {e}")
            context.log(f"错误: {e}")

            return StageResult(
                status=StageStatus.FAILED,
                message=f"IAR 编译超时（>{timeout} 秒）",
                error=e,
                suggestions=[
                    "检查代码量是否过大",
                    "优化编译选项",
                    "增加超时配置"
                ]
            )
        except ProcessExitCodeError as e:
            # 处理编译退出码非零 (Story 2.8 - 任务 6.4)
            logger.error(f"IAR 编译失败: {e}")
            context.log(f"错误: {e}")

            return StageResult(
                status=StageStatus.FAILED,
                message=f"IAR 编译失败 (退出码: {e.exit_code})",
                error=e,
                suggestions=[
                    "查看编译日志",
                    "修复语法错误",
                    "检查链接配置"
                ]
            )

        context.log(f"IAR 编译完成，耗时: {compile_result['execution_time']:.2f} 秒")

        # 验证 ELF 文件 (Story 2.8 - 任务 2.1-2.2)
        context.log("验证 ELF 文件...")

        # 尝试从编译结果中获取 ELF 路径
        elf_path = compile_result.get("elf_file")

        # 如果没有，自动查找
        if not elf_path:
            elf_path = _find_elf_file(project_dir)

        if not elf_path:
            return StageResult(
                status=StageStatus.FAILED,
                message="编译完成但 ELF 文件未生成",
                suggestions=[
                    "检查编译配置",
                    "验证输出目录",
                    "查看 IAR 日志"
                ]
            )

        # 验证 ELF 文件
        elf_verify = iar.verify_elf_file(str(elf_path))

        if not elf_verify["is_valid"]:
            return StageResult(
                status=StageStatus.FAILED,
                message=f"ELF 文件验证失败: {elf_verify.get('error', '未知错误')}",
                suggestions=[
                    "检查编译配置",
                    "验证输出目录",
                    "查看 IAR 日志"
                ]
            )

        context.log(f"ELF 文件验证通过: {elf_path} ({elf_verify['size']} 字节)")

        # 查找并执行 HexMerge.bat (Story 2.8 - 任务 1.7, 2.3)
        execute_hex_merge = context.config.get("iar_execute_hex_merge", True)

        hex_file = None

        if execute_hex_merge:
            context.log("查找 HexMerge.bat...")

            hex_merge_bat = _find_hex_merge_bat(project_dir)

            if hex_merge_bat:
                context.log(f"找到 HexMerge.bat: {hex_merge_bat}")

                try:
                    # 执行 HexMerge.bat
                    hex_merge_timeout = context.config.get("iar_hex_merge_timeout", 300)
                    hex_result = iar.execute_hex_merge(
                        bat_path=str(hex_merge_bat),
                        working_dir=str(hex_merge_bat.parent),
                        timeout=hex_merge_timeout
                    )

                    context.log(f"HexMerge.bat 执行完成，耗时: {hex_result['execution_time']:.2f} 秒")

                    # 查找生成的 HEX 文件
                    hex_file = _find_hex_file(project_dir)

                    if hex_file:
                        # 验证 HEX 文件
                        hex_verify = iar.verify_hex_file(str(hex_file))

                        if hex_verify["is_valid"]:
                            context.log(f"HEX 文件验证通过: {hex_file} ({hex_verify['size']} 字节)")
                        else:
                            context.log(f"警告: HEX 文件验证失败: {hex_verify.get('error', '未知错误')}")
                    else:
                        context.log("警告: 未找到生成的 HEX 文件")

                except ProcessTimeoutError as e:
                    context.log(f"警告: HexMerge.bat 执行超时")
                    logger.warning(f"HexMerge.bat 超时: {e}")
                except ProcessExitCodeError as e:
                    context.log(f"警告: HexMerge.bat 执行失败 (退出码: {e.exit_code})")
                    logger.warning(f"HexMerge.bat 失败: {e}")
                except ProcessError as e:
                    context.log(f"警告: HexMerge.bat 执行失败: {e}")
                    logger.warning(f"HexMerge.bat 失败: {e}")
            else:
                context.log("未找到 HexMerge.bat，跳过 HEX 文件生成")

        # 检查编译错误 (Story 2.8 - 任务 4.6, 3.1-3.4)
        errors = compile_result.get("errors", [])
        warnings = compile_result.get("warnings", [])

        if errors:
            # 生成错误报告
            error_report = iar.get_error_report(errors)
            context.log(f"\n{error_report}")

            return StageResult(
                status=StageStatus.FAILED,
                message=f"IAR 编译发现 {len(errors)} 个错误",
                suggestions=[
                    "查看错误报告获取详细信息",
                    "修复错误后重新编译"
                ]
            )

        if warnings:
            context.log(f"\n编译警告: {len(warnings)} 个")
            for warning in warnings[:5]:  # 最多显示 5 条警告
                context.log(f"  [{warning['code']}] {warning['message']}")

        # 构建编译输出状态 (Story 2.8 - 任务 4.5)
        build_output = {
            "elf_file": str(elf_path),
            "hex_file": str(hex_file) if hex_file else None,
            "success": True,
            "errors": [],
            "warnings": [w["message"] for w in warnings],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time": compile_result["execution_time"]
        }

        # 保存到 context.state (Story 2.8 - 任务 4.5)
        context.state["build_output"] = build_output

        # 计算总执行时间
        duration = time.monotonic() - start_time

        context.log(f"阶段执行完成，耗时: {duration:.2f} 秒")
        context.log(f"  - ELF 文件: {elf_path}")
        if hex_file:
            context.log(f"  - HEX 文件: {hex_file}")

        output_files = [str(elf_path)]
        if hex_file:
            output_files.append(str(hex_file))

        return StageResult(
            status=StageStatus.COMPLETED,
            message=f"IAR 编译成功（耗时 {duration:.2f} 秒）",
            output_files=output_files,
            execution_time=duration
        )

    except ProcessError as e:
        logger.error(f"IAR 集成错误: {e}")
        context.log(f"错误: {e}")

        return StageResult(
            status=StageStatus.FAILED,
            message=f"IAR 集成错误: {e}",
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

    finally:
        # 清理 IAR 集成
        if iar and iar.is_running():
            logger.warning("IAR 进程仍在运行，尝试清理")
            try:
                iar._is_running = False
            except Exception:
                pass


def get_stage_info() -> dict:
    """获取阶段信息

    Returns:
        dict: 阶段信息字典
    """
    return {
        "name": "iar_compile",
        "display_name": "IAR 编译",
        "description": "调用 IAR 编译器编译工程，生成 ELF 和 HEX 文件",
        "required_params": ["iar_project_path", "matlab_code_path"],
        "optional_params": ["iar_build_config", "iar_execute_hex_merge", "iar_hex_merge_timeout"],
        "outputs": ["build_output"],
        "inputs": ["moved_files"]
    }
