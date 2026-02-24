# -*- coding: utf-8 -*-
"""直接测试 IAR 编译"""

import subprocess
import os
import sys
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# IAR 配置
IAR_BUILD_EXE = r"D:\IDE\common\bin\IarBuild.exe"
# 使用 .ewp 项目文件（不是 .eww 工作区文件）
IAR_PROJECT_PATH = r"D:\IDE\E0Y\600-CICD\02_genHex\M7\CYT4BF_M7.ewp"
BUILD_CONFIG = "Debug"

def test_iar_compilation():
    """测试 IAR 编译"""
    print("=" * 60)
    print("IAR 编译测试")
    print("=" * 60)

    # 检查 IarBuild.exe 是否存在
    if not Path(IAR_BUILD_EXE).exists():
        print(f"[X] IarBuild.exe 不存在: {IAR_BUILD_EXE}")
        return
    print(f"[OK] IarBuild.exe 存在: {IAR_BUILD_EXE}")

    # 检查项目文件是否存在
    if not Path(IAR_PROJECT_PATH).exists():
        print(f"[X] 项目文件不存在: {IAR_PROJECT_PATH}")
        return
    print(f"[OK] 项目文件存在: {IAR_PROJECT_PATH}")

    # 构建 IAR 编译命令
    # 格式: IarBuild.exe project.ewp -build ConfigName
    cmd = f'"{IAR_BUILD_EXE}" "{IAR_PROJECT_PATH}" -build {BUILD_CONFIG}'
    print(f"\n命令: {cmd}")

    try:
        print("\n开始编译...")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600,
            encoding='utf-8',
            errors='replace'
        )

        print(f"\n退出码: {result.returncode}")

        # 显示输出
        if result.stdout:
            print(f"\n标准输出 (最后 3000 字符):")
            print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)

        if result.stderr:
            print(f"\n标准错误:")
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)

        # 解释返回码
        error_codes = {
            0: "编译成功",
            1: "编译警告（有警告但编译成功）",
            2: "编译错误（存在编译错误）",
            3: "致命错误（无法继续编译）",
            4: "用户中止",
            5: "内部错误（IAR工具内部错误）",
        }
        print(f"\n返回码含义: {error_codes.get(result.returncode, f'未知错误: {result.returncode}')}")

        # 检查 ELF 文件
        project_dir = Path(IAR_PROJECT_PATH).parent
        elf_files = list(project_dir.rglob("*.elf"))
        if elf_files:
            print(f"\n找到 ELF 文件:")
            for elf in elf_files[:5]:
                size = elf.stat().st_size
                print(f"  {elf} ({size:,} bytes)")

    except subprocess.TimeoutExpired:
        print("[X] 编译超时（10分钟）")
    except FileNotFoundError as e:
        print(f"[X] 找不到文件: {e}")
    except Exception as e:
        print(f"[X] 编译异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_iar_compilation()
