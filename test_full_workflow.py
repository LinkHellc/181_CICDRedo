# -*- coding: utf-8 -*-
"""测试完整的 E0Y 工作流"""

import subprocess
import sys
import time
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.models import ProjectConfig, WorkflowConfig, StageConfig, BuildContext
from core.workflow import execute_workflow

# E0Y 项目配置
def get_e0y_config():
    return ProjectConfig(
        name="E0Y",
        simulink_path=r"D:\MATLAB\Project\E0Y_TMS",
        matlab_code_path=r"D:\MATLAB\Project\E0Y_TMS\20_Code",
        a2l_path=r"D:\MATLAB\Project\E0Y_TMS\22_A2L\TmsApp.a2l",
        target_path=r"D:\IDE\E0Y\600-CICD\05_finObj",
        iar_project_path=r"D:\IDE\E0Y\600-CICD\02_genHex\Neusar_CYT4BF.eww",
    )

def get_e0y_workflow():
    return WorkflowConfig(
        id="e0y_workflow",
        name="E0Y 构建流程",
        description="跳过 MATLAB 代码生成，从文件处理开始",
        estimated_time=15,
        stages=[
            StageConfig(name="matlab_gen", enabled=False, timeout=1800),
            StageConfig(name="file_process", enabled=True, timeout=300),
            StageConfig(name="file_move", enabled=True, timeout=300),
            StageConfig(name="iar_compile", enabled=True, timeout=1200),
            # 暂时跳过后续阶段以加快测试
            StageConfig(name="a2l_process", enabled=False, timeout=600),
            StageConfig(name="package", enabled=False, timeout=60),
        ]
    )

def test_full_workflow():
    """测试完整工作流"""
    print("=" * 60)
    print("E0Y 完整工作流测试")
    print("=" * 60)

    config = get_e0y_config()
    workflow = get_e0y_workflow()

    print(f"\n项目配置:")
    print(f"  - 名称: {config.name}")
    print(f"  - Simulink 路径: {config.simulink_path}")
    print(f"  - IAR 工程路径: {config.iar_project_path}")

    # 创建构建上下文
    logs = []
    def log_callback(msg):
        logs.append(msg)
        print(f"[LOG] {msg}")

    def progress_callback(percent, msg):
        print(f"[进度 {percent}%] {msg}")

    def stage_callback(stage_name, success):
        status = "[OK]" if success else "[FAIL]"
        print(f"[阶段] {status} {stage_name}")

    context = BuildContext(
        config={
            "simulink_path": config.simulink_path,
            "matlab_code_path": config.matlab_code_path,
            "a2l_path": config.a2l_path,
            "target_path": config.target_path,
            "iar_project_path": config.iar_project_path,
        },
        log_callback=log_callback
    )

    # 执行工作流
    print("\n开始执行工作流...")
    start_time = time.time()

    try:
        result = execute_workflow(
            workflow,
            context,
            progress_callback=progress_callback,
            stage_callback=stage_callback
        )

        elapsed = time.time() - start_time
        print(f"\n工作流执行完成: {'成功' if result else '失败'}")
        print(f"总耗时: {elapsed:.2f} 秒")

        # 显示上下文状态
        print(f"\n上下文状态:")
        for key, value in context.state.items():
            if isinstance(value, dict):
                print(f"  {key}: {{...}}")
            else:
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"\n工作流执行异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_workflow()
