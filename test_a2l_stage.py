# -*- coding: utf-8 -*-
"""测试 A2L 处理阶段"""

import sys
import time
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',    errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.models import StageConfig, BuildContext
from stages.a2l_process import execute_stage

from integrations.iar import find_ewp_from_eww

def test_a2l_stage():
    """测试 A2L 处理阶段"""
    print("=" * 60)
    print("A2L 处理阶段测试")
    print("=" * 60)

    # 配置
    iar_eww_path = r"D:\IDE\E0Y\600-CICD\02_genHex\Neusar_CYT4BF.eww"
    iar_ewp_path = find_ewp_from_eww(iar_eww_path)

    if not iar_ewp_path:
        print("错误: 无法找到 IAR 项目文件")
        return

    print(f"IAR 项目文件: {iar_ewp_path}")

    # 查找 ELF 文件
    project_dir = Path(iar_ewp_path).parent.parent
    elf_files = list(project_dir.rglob("**/*.elf"))

    if not elf_files:
        print("错误: 未找到 ELF 文件")
        return

    elf_path = elf_files[0]
    print(f"ELF 文件: {elf_path}")

    # 查找 A2L 文件
    a2l_tool_path = Path(r"D:\IDE\E0Y\600-CICD\04_genA2L")

    # 查找 XCP 头文件模板
    xcp_templates = list(a2l_tool_path.glob("XCP*.txt")) + list(a2l_tool_path.glob("*XCP*.txt"))
    if not xcp_templates:
        print(f"错误: 在 {a2l_tool_path} 中未找到 XCP 头文件模板")
        return

    xcp_template_path = xcp_templates[0]
    print(f"XCP 模板文件: {xcp_template_path}")

    # 创建配置
    config = StageConfig(
        name="a2l_process",
        enabled=True,
        timeout=600,
    )

    # 创建上下文
    logs = []
    def log_callback(msg):
        logs.append(msg)
        print(f"[LOG] {msg}")

    context = BuildContext(
        config={
            "simulink_path": r"D:\MATLAB\Project\E0Y_TMS",
            "matlab_code_path": r"D:\MATLAB\Project\E0Y_TMS\20_Code",
            "a2l_path": r"D:\MATLAB\Project\E0Y_TMS\22_A2L\TmsApp.a2l",
            "target_path": r"D:\IDE\E0Y\600-CICD\05_finObj",
            "iar_project_path": iar_eww_path,
            "a2l_tool_path": str(a2l_tool_path),
            "elf_path": str(elf_path),
        },
        log_callback=log_callback
    )

    # 保存 ELF 路径到 context.state
    context.state["iar_elf_path"] = str(elf_path)

    # 查找示 A2L 源文件
    a2l_files = list(a2l_tool_path.glob("**/*.a2l"))
    if a2l_files:
        context.state["a2l_source_path"] = str(a2l_files[0])
        print(f"A2L 源文件: {a2l_files[0]}")

    print("\n开始执行 A2L 处理阶段...")
    start_time = time.time()

    try:
        result = execute_stage(config, context)

        elapsed = time.time() - start_time
        print(f"\n阶段执行完成， 耗时: {elapsed:.2f} 秒")
        print(f"状态: {result.status}")
        print(f"消息: {result.message}")

        if result.output_files:
            print(f"输出文件: {result.output_files}")

    except Exception as e:
        print(f"\n执行异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_a2l_stage()
