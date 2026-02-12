"""MATLAB code generation stage for MBD_CICDKits.

This module implements the MATLAB code generation stage that:
- Starts MATLAB engine
- Executes genCode.m script
- Captures output and monitors process
- Validates generated files

Story 2.5 - 执行 MATLAB 代码生成阶段

Architecture Decision 1.1:
- 统一阶段签名: execute_stage(config, context) -> result
- 返回 StageResult 对象
- 通过 BuildContext 传递状态

Architecture Decision 2.1:
- 使用 time.monotonic() 记录时间
- 超时检测和资源清理

Architecture Decision 5.1:
- 使用 context.log_callback 实时输出日志
"""

import logging
import time
from pathlib import Path
from typing import Optional, List

from core.models import (
    StageConfig,
    BuildContext,
    StageResult,
    StageStatus
)
from core.constants import get_stage_timeout
from integrations.matlab import MatlabIntegration, MATLAB_ENGINE_AVAILABLE
from utils.errors import ProcessTimeoutError, ProcessError

logger = logging.getLogger(__name__)


def execute_stage(config: StageConfig, context: BuildContext) -> StageResult:
    """执行 MATLAB 代码生成阶段

    Story 2.5 - 任务 2:
    - 实现 execute_stage(config, context) -> StageResult
    - 添加 genCode.m 脚本路径参数（从配置获取）
    - 使用 MATLAB Engine API 调用脚本
    - 指定代码生成输出目录（./20_Code）

    Args:
        config: 阶段配置
        context: 构建上下文

    Returns:
        StageResult: 阶段执行结果
    """
    stage_name = "matlab_gen"
    context.log(f"=== 开始执行阶段: {stage_name} ===")

    # 记录开始时间 (Story 2.5 - 任务 6.1)
    start_time = time.monotonic()

    try:
        # 创建 MATLAB 集成实例
        matlab = MatlabIntegration(
            log_callback=context.log,
            timeout=config.timeout or get_stage_timeout(stage_name)
        )

        # 启动 MATLAB 引擎 (Story 2.5 - 任务 1.4)
        context.log("正在启动 MATLAB 引擎...")
        if not matlab.start_engine():
            return StageResult(
                status=StageStatus.FAILED,
                message="MATLAB 引擎启动失败",
                suggestions=[
                    "检查 MATLAB 是否正确安装",
                    "验证 MATLAB Engine API for Python 是否安装",
                    "查看详细日志获取更多信息"
                ]
            )

        # 获取配置参数 (Story 2.5 - 任务 2.3)
        simulink_path = context.config.get("simulink_path", "")
        matlab_code_path = context.config.get("matlab_code_path", "")
        gencode_script = context.config.get("gencode_script_path", "genCode")  # 支持自定义脚本路径

        if not simulink_path:
            return StageResult(
                status=StageStatus.FAILED,
                message="Simulink 工程路径未配置",
                suggestions=[
                    "在项目配置中设置 simulink_path",
                    "确保路径指向有效的 Simulink 工程文件"
                ]
            )

        context.log(f"Simulink 工程路径: {simulink_path}")
        context.log(f"MATLAB 代码路径: {matlab_code_path}")

        # 执行 genCode.m 脚本 (Story 2.5 - 任务 2.4)
        context.log("正在执行 genCode.m 脚本...")

        try:
            # 调用 genCode.m (Story 2.5 - 任务 2.5)
            # 传递 Simulink 工程路径和输出目录 (Story 2.5 - 任务 2.6)
            # 使用配置的脚本名称（默认 "genCode"）
            matlab.eval_script(gencode_script, simulink_path, matlab_code_path)

        except ProcessTimeoutError as e:
            # 超时处理 (Story 2.5 - 任务 5.3)
            context.log(f"错误: {e}")
            return StageResult(
                status=StageStatus.FAILED,
                message=f"MATLAB 代码生成超时（{e.timeout} 秒）",
                error=e,
                suggestions=e.suggestions
            )

        except ProcessError as e:
            # 其他进程错误
            context.log(f"错误: {e}")
            return StageResult(
                status=StageStatus.FAILED,
                message=f"MATLAB 代码生成失败: {e}",
                error=e,
                suggestions=e.suggestions
            )

        finally:
            # 清理 MATLAB 进程
            matlab.stop_engine()

        # 验证输出文件 (Story 2.5 - 任务 7)
        context.log("正在验证生成的代码文件...")
        validation_result = _validate_output_files(matlab_code_path, context)

        if not validation_result["valid"]:
            return StageResult(
                status=StageStatus.FAILED,
                message=validation_result["message"],
                suggestions=validation_result["suggestions"]
            )

        # 记录结束时间和计算时长 (Story 2.5 - 任务 6.2-6.3)
        end_time = time.monotonic()
        duration = end_time - start_time

        # 保存时间信息到 StageExecution (Story 2.5 - 任务 6.4)
        context.state["matlab_gen_start_time"] = start_time
        context.state["matlab_gen_end_time"] = end_time
        context.state["matlab_gen_duration"] = duration

        context.log(f"代码生成完成，耗时: {duration:.2f} 秒")

        # 通过信号发送阶段完成时间和时长到 UI (Story 2.5 - 任务 6.5)
        context.emit_signal("stage_completed", "matlab_gen", duration, end_time)

        # 保存输出文件列表到 context.state (Story 2.5 - 任务 7.4)
        context.state["matlab_output"] = validation_result["output_files"]

        # 返回成功结果
        return StageResult(
            status=StageStatus.COMPLETED,
            message=f"MATLAB 代码生成成功（耗时 {duration:.2f} 秒）",
            output_files=validation_result["output_files"].get("c_files", []),
            execution_time=duration
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


def _validate_output_files(
    matlab_code_path: str,
    context: BuildContext
) -> dict:
    """验证代码生成输出文件

    Story 2.5 - 任务 7:
    - 验证代码生成输出目录存在（./20_Code）
    - 检查生成的 .c 和 .h 文件数量
    - 验证关键文件存在（至少有代码文件）
    - 将输出文件列表保存到 context.state["matlab_output"]

    Args:
        matlab_code_path: MATLAB 代码路径
        context: 构建上下文

    Returns:
        dict: 包含验证结果的字典
            - valid: 是否验证通过
            - message: 验证消息
            - suggestions: 修复建议列表
            - output_files: 输出文件列表
    """
    # 代码生成输出目录 (Story 2.5 - 任务 7.1)
    code_dir = Path(matlab_code_path) / "20_Code"

    if not code_dir.exists():
        return {
            "valid": False,
            "message": f"代码生成输出目录不存在: {code_dir}",
            "suggestions": [
                "检查 MATLAB 代码路径配置",
                "确认 genCode.m 脚本正确执行",
                "查看 MATLAB 日志输出"
            ],
            "output_files": {}
        }

    # 查找所有 .c 和 .h 文件 (Story 2.5 - 任务 7.2)
    c_files = list(code_dir.glob("*.c"))
    h_files = list(code_dir.glob("*.h"))

    context.log(f"找到 {len(c_files)} 个 .c 文件")
    context.log(f"找到 {len(h_files)} 个 .h 文件")

    # 验证关键文件存在 (Story 2.5 - 任务 7.3)
    if len(c_files) == 0:
        return {
            "valid": False,
            "message": "未生成任何 .c 文件",
            "suggestions": [
                "检查 Simulink 模型配置",
                "查看 MATLAB 错误日志",
                "验证模型编译设置"
            ],
            "output_files": {}
        }

    # 构建输出文件列表 (Story 2.5 - 任务 7.4)
    # 排除 Rte_TmsApp.h（接口文件，需要在下一阶段排除）
    exclude_files = ["Rte_TmsApp.h"]

    output_files = {
        "c_files": [str(f.relative_to(code_dir.parent)) for f in c_files],
        "h_files": [str(f.relative_to(code_dir.parent)) for f in h_files],
        "exclude": exclude_files,
        "base_dir": str(code_dir)
    }

    context.log(f"验证通过: 生成了 {len(c_files)} 个 C 文件和 {len(h_files)} 个头文件")

    return {
        "valid": True,
        "message": f"代码生成验证通过（{len(c_files)} 个 .c 文件，{len(h_files)} 个 .h 文件）",
        "suggestions": [],
        "output_files": output_files
    }


def get_stage_info() -> dict:
    """获取阶段信息

    Returns:
        dict: 阶段信息字典
    """
    return {
        "name": "matlab_gen",
        "display_name": "MATLAB 代码生成",
        "description": "调用 MATLAB 生成 Simulink 模型代码",
        "required_params": ["simulink_path", "matlab_code_path"],
        "optional_params": [],
        "outputs": ["matlab_output"],
        "matlab_engine_available": MATLAB_ENGINE_AVAILABLE
    }
