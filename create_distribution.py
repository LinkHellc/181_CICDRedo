#!/usr/bin/env python3
"""
创建 MBD_CICDKits 分发包

功能：
- 打包 dist/MBD_CICDKits 为 ZIP 文件
- 生成版本信息和校验文件
- 创建安装说明

使用方法:
    python create_distribution.py
"""

import subprocess
import sys
import hashlib
from pathlib import Path
from datetime import datetime


def calculate_sha256(file_path: Path) -> str:
    """计算文件的 SHA256 校验和"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def create_zip_package():
    """创建 ZIP 分发包"""
    print("\n" + "=" * 60)
    print("MBD_CICDKits 分发包创建工具")
    print("=" * 60)

    # 版本信息
    version = "0.1.0"
    date_str = datetime.now().strftime("%Y%m%d")
    zip_name = f"MBD_CICDKits_v{version}_{date_str}.zip"
    source_dir = Path(__file__).parent / "dist" / "MBD_CICDKits"
    output_zip = Path(__file__).parent / "dist" / zip_name

    # 检查源目录
    if not source_dir.exists():
        print(f"\n[错误] 源目录不存在: {source_dir}")
        print("请先运行 python build_exe.py 进行打包")
        return False

    # 删除旧的 ZIP 文件
    if output_zip.exists():
        print(f"\n[*] 删除旧文件: {output_zip.name}")
        output_zip.unlink()

    # 创建 ZIP 文件
    print(f"\n[*] 创建分发包: {zip_name}")
    print(f"    源目录: {source_dir}")
    print(f"    输出文件: {output_zip}")

    try:
        # 使用 PowerShell 的 Compress-Archive（Windows 内置）
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                f"Compress-Archive -Path '{source_dir}' -DestinationPath '{output_zip}' -Force"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"[错误] 创建 ZIP 失败:\n{result.stderr}")
            return False

    except Exception as e:
        print(f"[错误] {e}")
        return False

    # 计算文件大小和校验和
    file_size = output_zip.stat().st_size
    size_mb = file_size / (1024 * 1024)
    sha256 = calculate_sha256(output_zip)

    # 打印结果
    print("\n" + "=" * 60)
    print("[成功] 分发包创建完成！")
    print("=" * 60)
    print(f"\n文件名: {zip_name}")
    print(f"位置: {output_zip}")
    print(f"大小: {size_mb:.2f} MB")
    print(f"SHA256: {sha256}")

    # 创建版本信息文件
    info_file = output_zip.with_suffix(".txt")
    with open(info_file, "w", encoding="utf-8") as f:
        f.write("MBD_CICDKits 分发包信息\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"版本: {version}\n")
        f.write(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"文件名: {zip_name}\n")
        f.write(f"大小: {size_mb:.2f} MB\n")
        f.write(f"SHA256: {sha256}\n\n")
        f.write("安装说明:\n")
        f.write("1. 解压 ZIP 文件到任意位置\n")
        f.write("2. 双击运行 MBD_CICDKits.exe\n")
        f.write("3. 无需安装 Python 或其他依赖\n\n")
        f.write("系统要求:\n")
        f.write("- Windows 10/11 (64位)\n")
        f.write("- 无需安装 Python\n\n")
        f.write("注意事项:\n")
        f.write("- MATLAB 代码生成功能需单独安装 MATLAB Engine\n")
        f.write("- 详见应用内的安装指南文档\n")

    print(f"\n[*] 创建版本信息文件: {info_file.name}")

    # 创建 README
    readme_file = Path(__file__).parent / "dist" / "README_分发.txt"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write("MBD_CICDKits - Simulink 模型 CI/CD 自动化工具\n")
        f.write("=" * 50 + "\n\n")
        f.write("快速安装:\n")
        f.write("1. 下载最新版本的分发包 (ZIP 文件)\n")
        f.write("2. 解压到任意目录\n")
        f.write("3. 运行 MBD_CICDKits.exe\n\n")
        f.write("系统要求:\n")
        f.write("- Windows 10/11 (64位)\n")
        f.write("- 至少 200MB 可用磁盘空间\n\n")
        f.write("主要功能:\n")
        f.write("- 项目配置管理\n")
        f.write("- 文件处理和移动\n")
        f.write("- IAR 工程编译\n")
        f.write("- A2L 文件处理\n")
        f.write("- 自动化打包归档\n\n")
        f.write("获取帮助:\n")
        f.write("- 应用内置帮助文档\n")
        f.write("- GitHub Issues\n\n")
        f.write(f"版本: {version}\n")
        f.write(f"更新日期: {date_str}\n")

    print(f"[*] 创建 README 文件: {readme_file.name}")

    print("\n" + "=" * 60)
    print("分发文件清单:")
    print("=" * 60)
    print(f"1. {zip_name} ({size_mb:.2f} MB)")
    print(f"2. {info_file.name}")
    print(f"3. {readme_file.name}")

    print("\n分发说明:")
    print("- 将上述3个文件一起打包发送给用户")
    print("- 或者只发送 ZIP 文件（包含完整应用）")

    return True


if __name__ == "__main__":
    success = create_zip_package()
    sys.exit(0 if success else 1)
