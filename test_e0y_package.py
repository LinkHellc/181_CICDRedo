"""E0Y 项目打包阶段测试脚本

直接测试打包阶段功能（创建时间戳文件夹 + 移动 HEX/A2L 文件）

运行方式：
    python test_e0y_package.py
"""

import sys
import logging
from pathlib import Path
import io

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
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

from core.models import StageConfig, BuildContext, StageStatus
from core.config import load_config
from stages.package import execute_stage


def test_e0y_package_stage():
    """测试 E0Y 项目的打包阶段"""

    print("=" * 70)
    print("E0Y 项目打包阶段测试")
    print("=" * 70)

    # 1. 加载 E0Y 项目配置
    print("\n[1] 加载 E0Y 项目配置...")
    try:
        config = load_config("E0Y")
        print(f"    ✅ 成功加载配置: {config.name}")
        print(f"       - 目标路径: {config.target_path}")
        print(f"       - IAR 工程路径: {config.iar_project_path}")
        print(f"       - A2L 路径: {config.a2l_path}")
    except Exception as e:
        print(f"    ❌ 加载配置失败: {e}")
        return False

    # 2. 创建构建上下文
    print("\n[2] 创建构建上下文...")

    # 设置源文件路径（根据实际 E0Y 项目结构）
    hex_source_path = Path(config.iar_project_path).parent / "HexMerge"
    a2l_source_path = Path("D:/IDE/E0Y/600-CICD/04_genA2L/output")

    # 检查源路径是否存在
    print(f"    HEX 源路径: {hex_source_path}")
    print(f"        {'✅ 存在' if hex_source_path.exists() else '❌ 不存在'}")
    if hex_source_path.exists():
        hex_files = list(hex_source_path.glob("*.hex"))
        print(f"        HEX 文件: {len(hex_files)} 个")
        for f in hex_files[:3]:
            print(f"          - {f.name}")

    print(f"    A2L 源路径: {a2l_source_path}")
    print(f"        {'✅ 存在' if a2l_source_path.exists() else '❌ 不存在'}")
    if a2l_source_path.exists():
        a2l_files = list(a2l_source_path.glob("*.a2l"))
        print(f"        A2L 文件: {len(a2l_files)} 个")
        for f in a2l_files[:3]:
            print(f"          - {f.name}")

    # 准备配置字典
    config_dict = {
        "target_file_path": config.target_path,
        "target_folder_prefix": "MBD_CICD_Obj",
        "hex_source_path": str(hex_source_path),
        "a2l_source_path": str(a2l_source_path),
    }

    # 创建日志回调
    logs = []
    def log_callback(msg):
        logs.append(msg)
        print(f"    [LOG] {msg}")

    # 创建构建上下文
    context = BuildContext(
        config=config_dict,
        log_callback=log_callback
    )

    # 3. 创建打包阶段配置
    print("\n[3] 创建打包阶段配置...")
    stage_config = StageConfig(
        name="package",
        enabled=True,
        timeout=60
    )
    print(f"    ✅ 阶段配置: {stage_config.name}")

    # 4. 执行打包阶段
    print("\n[4] 执行打包阶段...")
    print("-" * 70)

    result = execute_stage(stage_config, context)

    print("-" * 70)

    # 5. 显示执行结果
    print("\n[5] 执行结果:")
    print(f"    状态: {result.status.value}")
    print(f"    消息: {result.message}")
    print(f"    执行时间: {result.execution_time:.2f} 秒")

    if result.output_files:
        print(f"    输出文件:")
        for f in result.output_files:
            print(f"      - {f}")

    if result.error:
        print(f"    错误: {result.error}")

    if result.suggestions:
        print(f"    建议:")
        for s in result.suggestions:
            print(f"      - {s}")

    # 6. 检查上下文状态
    print("\n[6] 上下文状态:")
    if "target_folder" in context.state:
        target_folder = context.state["target_folder"]
        print(f"    目标文件夹: {target_folder}")
        target_path = Path(target_folder)
        if target_path.exists():
            print(f"      ✅ 文件夹存在")
            files = list(target_path.glob("*"))
            print(f"      文件数: {len(files)}")
            for f in files:
                print(f"        - {f.name} ({f.stat().st_size} bytes)")
        else:
            print(f"      ❌ 文件夹不存在")

    if "output_files" in context.state:
        output_files = context.state["output_files"]
        print(f"    输出文件:")
        if "hex" in output_files:
            print(f"      HEX: {output_files['hex']}")
        if "a2l" in output_files:
            print(f"      A2L: {output_files['a2l']}")

    # 7. 测试结论
    print("\n" + "=" * 70)
    if result.status == StageStatus.COMPLETED:
        print("✅ 打包阶段测试成功！")
    else:
        print("❌ 打包阶段测试失败！")
    print("=" * 70)

    return result.status == StageStatus.COMPLETED


if __name__ == "__main__":
    success = test_e0y_package_stage()
    sys.exit(0 if success else 1)
