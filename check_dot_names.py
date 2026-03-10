#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查ELF中带点号的变量名."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser

def check_dot_symbols():
    """检查带点号的符号在ELF中的格式"""
    elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"

    parser = ELFParser()
    symbols = parser.extract_symbols(Path(elf_path))

    # 测试带点号的变量名
    test_names = [
        "TmsApp_ARID_DEF.IDP_o3.gCAN_SeatHeatLevelsFR_uint8",
        "TmsApp_ARID_DEF.ODP_o194",
        "CbnHMI_DW.is_TempSet",
        "TmsApp_ARID_DEF.IDP_o1.gCDD_TMSMDVFRLF_I_uint8",
    ]

    print("检查带点号的变量名:\n")
    for name in test_names:
        # 检查精确匹配
        if name in symbols:
            print(f"  ✅ {name}")
            print(f"     地址: 0x{symbols[name]:08X}")
            continue

        # 检查替换点号的变体
        variants = [
            name.replace(".", "_"),  # 点号变下划线
            name.replace(".", "__"),  # 点号变双下划线
        ]

        found = False
        for variant in variants:
            if variant in symbols:
                print(f"  ⚠️  {name} -> ELF中名为: {variant}")
                print(f"     地址: 0x{symbols[variant]:08X}")
                found = True
                break

        if not found:
            print(f"  ❌ {name} 未在ELF中找到")

    # 统计ELF中带点号的符号
    dot_symbols = [s for s in symbols.keys() if "." in s]
    print(f"\nELF中带点号的符号数: {len(dot_symbols)}")
    if dot_symbols:
        print("示例:")
        for s in dot_symbols[:10]:
            print(f"  - {s} -> 0x{symbols[s]:08X}")

if __name__ == "__main__":
    check_dot_symbols()
