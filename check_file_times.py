#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查文件时间和大小."""

import sys
import io
from pathlib import Path
import os

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

folder = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08")

print("文件夹中的A2L和ELF文件:")
print("="*70)

files = sorted(folder.glob("*.a2l")) + sorted(folder.glob("*.elf"))

for f in files:
    stat = f.stat()
    mtime = stat.st_mtime
    size = stat.st_size
    print(f"{f.name:45s} 大小: {size:10d}  时间: {mtime}")

# 检查原始TmsApp.a2l的时间
original_a2l = folder / "TmsApp.a2l"
if original_a2l.exists():
    stat = original_a2l.stat()
    print(f"\n原始TmsApp.a2l:")
    print(f"  大小: {stat.st_size}")
    print(f"  时间: {stat.st_mtime}")
