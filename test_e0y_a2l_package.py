"""E0Y 项目 A2L 处理 + 打包阶段测试脚本

测试 A2L 文件处理和最终打包两个阶段

运行方式：
    python test_e0y_a2l_package.py
"""

import sys
import logging
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from core.models import StageConfig, BuildContext, StageStatus, A2LHeaderReplacementConfig
from core.config import load_config
from stages.a2l_process import execute_stage as execute_a2l_stage, execute_xcp_header_replacement_stage, verify_processed_a2l_file, remove_if_data_xcp_blocks
from stages.package import execute_stage as execute_package_stage


def test_e0y_a2l_and_package():
    """测试 E0Y 项目的 A2L 处理和打包阶段"""

    print("=" * 70)
    print("E0Y 项目 A2L 处理 + 打包阶段测试")
    print("=" * 70)

    # 1. 加载 E0Y 项目配置
    print("\n[1] 加载 E0Y 项目配置...")
    try:
        config = load_config("E0Y")
        print(f"    ✅ 成功加载配置: {config.name}")
    except Exception as e:
        print(f"    ❌ 加载配置失败: {e}")
        return False

    # 2. 创建构建上下文
    print("\n[2] 创建构建上下文...")

    # E0Y 项目的路径配置
    a2l_source_path = Path(config.a2l_path)  # 原始 A2L 文件
    a2l_tool_path = Path("D:/IDE/E0Y/600-CICD/04_genA2L")  # A2L 工具目录
    elf_path = a2l_tool_path / "CYT4BF_M7_Master.elf"  # ELF 文件
    hex_source_path = Path("D:/IDE/E0Y/600-CICD/02_genHex/HexMerge")  # HEX 源目录
    a2l_output_path = a2l_tool_path / "output"  # A2L 输出目录

    print(f"    原始 A2L: {a2l_source_path}")
    print(f"        {'✅ 存在' if a2l_source_path.exists() else '❌ 不存在'}")
    print(f"    ELF 文件: {elf_path}")
    print(f"        {'✅ 存在' if elf_path.exists() else '❌ 不存在'}")
    print(f"    HEX 源目录: {hex_source_path}")
    print(f"        {'✅ 存在' if hex_source_path.exists() else '❌ 不存在'}")
    print(f"    A2L 输出目录: {a2l_output_path}")
    print(f"        {'✅ 存在' if a2l_output_path.exists() else '❌ 不存在'}")

    # 创建日志回调
    logs = []
    def log_callback(msg):
        logs.append(msg)
        print(f"    [LOG] {msg}")

    # 4. 执行 A2L 处理阶段
    print("\n[4] 执行 A2L 处理阶段...")
    print("-" * 70)

    context = BuildContext(
        config={
            "a2l_path": str(a2l_source_path),
            "elf_path": str(elf_path),
            "a2l_tool_path": str(a2l_tool_path),
        },
        log_callback=log_callback
    )

    a2l_stage_config = StageConfig(
        name="a2l_process",
        enabled=True,
        timeout=300
    )

    a2l_result = execute_a2l_stage(a2l_stage_config, context)

    print("-" * 70)

    print(f"\n[4] A2L 处理结果:")
    print(f"    状态: {a2l_result.status.value}")
    print(f"    消息: {a2l_result.message}")
    print(f"    执行时间: {a2l_result.execution_time:.2f} 秒")

    if a2l_result.status == StageStatus.FAILED:
        if a2l_result.suggestions:
            print(f"    建议:")
            for s in a2l_result.suggestions:
                print(f"      - {s}")
        print("\n    ⚠️ A2L 变量地址更新失败，跳过后续阶段")
        return False

    # 4.3 执行 A2LTool（删除 IF_DATA XCP 块）
    print("\n[4.3] 执行 A2LTool（删除 IF_DATA XCP 块）...")
    print("-" * 70)

    # A2LTool 会直接修改 a2l_source_path 指定的文件
    from pathlib import Path as PathLib
    a2l_file_for_tool = PathLib(str(a2l_source_path))

    try:
        success, removed_count = remove_if_data_xcp_blocks(a2l_file_for_tool, log_callback)
        print(f"    删除了 {removed_count} 个 IF_DATA XCP 块")
    except Exception as e:
        print(f"    删除 IF_DATA XCP 块失败: {e}")
        print("    继续后续步骤...")

    print("-" * 70)

    print(f"\n[4] A2L 处理结果:")
    print(f"    状态: {a2l_result.status.value}")
    print(f"    消息: {a2l_result.message}")
    print(f"    执行时间: {a2l_result.execution_time:.2f} 秒")

    if a2l_result.status == StageStatus.FAILED:
        if a2l_result.suggestions:
            print(f"    建议:")
            for s in a2l_result.suggestions:
                print(f"      - {s}")
        print("\n    ⚠️ A2L 变量地址更新失败，跳过后续阶段")
        return False

    # 4.5 执行 XCP 头文件替换阶段
    print("\n[4.5] 执行 XCP 头文件替换阶段...")
    print("-" * 70)

    # 更新 context，添加 A2L 输出路径
    context.state["a2l_output_path"] = str(a2l_source_path)
    context.state["target_path"] = config.target_path

    # XCP 头文件替换配置
    # 使用 A2L 工具目录下的 XCP 头文件模板
    xcp_config = A2LHeaderReplacementConfig(
        xcp_template_path=str(a2l_tool_path / "奇瑞热管理XCP头文件.txt"),
        a2l_source_path=str(a2l_source_path),
        output_dir=str(a2l_tool_path / "output"),
    )

    xcp_stage_config = StageConfig(
        name="a2l_xcp_replacement",
        enabled=True,
        timeout=60
    )
    xcp_stage_config.custom_config = xcp_config

    xcp_result = execute_xcp_header_replacement_stage(xcp_stage_config, context)

    print("-" * 70)

    print(f"\n[4.6] XCP 头文件替换结果:")
    print(f"    状态: {xcp_result.status.value}")
    print(f"    消息: {xcp_result.message}")
    print(f"    执行时间: {xcp_result.execution_time:.2f} 秒")

    if xcp_result.status == StageStatus.FAILED:
        if xcp_result.suggestions:
            print(f"    建议:")
            for s in xcp_result.suggestions:
                print(f"      - {s}")
        print("\n    ⚠️ XCP 头文件替换失败，但继续打包阶段")

    # 4.7 验证处理后的 A2L 文件
    print("\n[4.7] 验证处理后的 A2L 文件...")
    print("-" * 70)

    # 获取处理后的 A2L 文件路径
    processed_a2l_path = None
    if xcp_result.status == StageStatus.COMPLETED and xcp_result.output_files:
        processed_a2l_path = Path(xcp_result.output_files[0])
    elif "a2l_xcp_replaced_path" in context.state:
        processed_a2l_path = Path(context.state["a2l_xcp_replaced_path"])
    elif "a2l_output_path" in context.state:
        processed_a2l_path = Path(context.state["a2l_output_path"])

    if processed_a2l_path and processed_a2l_path.exists():
        print(f"    验证文件: {processed_a2l_path}")
        success, messages = verify_processed_a2l_file(processed_a2l_path, log_callback)
        print()
        for msg in messages:
            print(f"    {msg}")
        print()
        if success:
            print("    ✅ A2L 文件处理验证通过")
        else:
            print("    ⚠️  A2L 文件处理验证发现问题")
    else:
        print(f"    ⚠️  处理后的 A2L 文件未找到: {processed_a2l_path}")

    print("-" * 70)

    # 5. 执行打包阶段
    print("\n[5] 执行打包阶段...")
    print("-" * 70)

    # 使用 XCP 头文件替换后的输出目录作为 A2L 源路径
    a2l_final_output = a2l_tool_path / "output"
    package_context = BuildContext(
        config={
            "target_file_path": config.target_path,
            "target_folder_prefix": "MBD_CICD_Obj",
            "hex_source_path": str(hex_source_path),
            "a2l_source_path": str(a2l_final_output),  # 使用 XCP 处理后的输出目录
        },
        log_callback=log_callback
    )

    package_stage_config = StageConfig(
        name="package",
        enabled=True,
        timeout=60
    )

    package_result = execute_package_stage(package_stage_config, package_context)

    print("-" * 70)

    # 6. 显示打包结果
    print(f"\n[6] 打包结果:")
    print(f"    状态: {package_result.status.value}")
    print(f"    消息: {package_result.message}")
    print(f"    执行时间: {package_result.execution_time:.2f} 秒")

    if package_result.output_files:
        print(f"    输出文件:")
        for f in package_result.output_files:
            print(f"      - {f}")

    if package_result.error:
        print(f"    错误: {package_result.error}")

    if package_result.suggestions:
        print(f"    建议:")
        for s in package_result.suggestions:
            print(f"      - {s}")

    # 7. 显示最终输出
    print("\n[7] 最终输出:")
    if "target_folder" in package_context.state:
        target_folder = package_context.state["target_folder"]
        print(f"    目标文件夹: {target_folder}")
        target_path = Path(target_folder)
        if target_path.exists():
            print(f"      ✅ 文件夹存在")
            files = list(target_path.glob("*"))
            print(f"      文件数: {len(files)}")
            for f in files:
                print(f"        - {f.name} ({f.stat().st_size:,} bytes)")
        else:
            print(f"      ❌ 文件夹不存在")

    # 8. 测试结论
    print("\n" + "=" * 70)
    a2l_ok = a2l_result.status == StageStatus.COMPLETED
    xcp_ok = xcp_result.status == StageStatus.COMPLETED
    package_ok = package_result.status == StageStatus.COMPLETED

    if a2l_ok and xcp_ok and package_ok:
        print("✅ A2L 变量地址更新 + XCP 头文件替换 + 打包阶段测试成功！")
        return True
    else:
        print("❌ 测试失败！")
        if not a2l_ok:
            print("   - A2L 变量地址更新阶段失败")
        if not xcp_ok:
            print("   - XCP 头文件替换阶段失败")
        if not package_ok:
            print("   - 打包阶段失败")
        return False


if __name__ == "__main__":
    success = test_e0y_a2l_and_package()
    sys.exit(0 if success else 1)
