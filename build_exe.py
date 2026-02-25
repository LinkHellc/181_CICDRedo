#!/usr/bin/env python3
"""
MBD_CICDKits 打包脚本

功能：
- 自动安装PyInstaller（如果未安装）
- 执行打包命令
- 输出打包结果信息

使用方法:
    python build_exe.py

打包结果:
    dist/MBD_CICDKits/ 目录包含可执行文件和所有依赖

分发方式:
    将整个 dist/MBD_CICDKits/ 目录打包成ZIP发送给用户
    用户解压后直接运行 MBD_CICDKits.exe 即可
"""

import subprocess
import sys
import shutil
from pathlib import Path


def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print(f"[OK] PyInstaller 已安装: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("[!] PyInstaller 未安装")
        return False


def install_pyinstaller():
    """安装PyInstaller"""
    print("[*] 正在安装 PyInstaller...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("[OK] PyInstaller 安装成功")
        return True
    else:
        print(f"[ERROR] PyInstaller 安装失败:\n{result.stderr}")
        return False


def clean_build_dirs():
    """清理之前的打包目录"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    project_root = Path(__file__).parent

    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"[*] 清理目录: {dir_name}")
            shutil.rmtree(dir_path)

    # 清理 .spec 文件生成的临时文件
    for spec_file in project_root.glob("*.spec"):
        warn_file = project_root / f"{spec_file.stem}.warn"
        if warn_file.exists():
            warn_file.unlink()


def build_exe():
    """执行打包"""
    print("\n" + "=" * 60)
    print("MBD_CICDKits 打包工具")
    print("=" * 60)

    # 检查并安装PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return False

    # 清理旧文件
    clean_build_dirs()

    # 执行打包命令
    print("\n[*] 开始打包...")
    print("-" * 60)

    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "MBD_CICDKits.spec", "--clean"],
        capture_output=False  # 直接显示输出
    )

    if result.returncode != 0:
        print("\n[ERROR] 打包失败！")
        return False

    # 检查输出
    dist_dir = Path(__file__).parent / "dist" / "MBD_CICDKits"
    exe_path = dist_dir / "MBD_CICDKits.exe"

    print("\n" + "=" * 60)
    if exe_path.exists():
        print("[OK] 打包成功！")
        print(f"\n输出目录: {dist_dir}")
        print(f"可执行文件: {exe_path}")

        # 计算目录大小
        total_size = sum(f.stat().st_size for f in dist_dir.rglob("*") if f.is_file())
        size_mb = total_size / (1024 * 1024)
        print(f"总大小: {size_mb:.1f} MB")

        print("\n分发说明:")
        print("1. 将整个 'dist/MBD_CICDKits' 文件夹打包成ZIP")
        print("2. 发送给用户后，用户解压运行 MBD_CICDKits.exe")
        print("3. 用户无需安装Python或其他依赖")
    else:
        print("[ERROR] 打包输出未找到！")
        return False

    print("=" * 60)
    return True


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
