#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试叶子节点匹配逻辑."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser
from a2l.a2l_parser import A2LParser

def test_leaf_matching():
    """测试叶子节点匹配"""
    elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"
    a2l_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp.a2l"

    elf_parser = ELFParser()
    a2l_parser = A2LParser()

    symbols = elf_parser.extract_symbols(Path(elf_path))
    a2l_vars = a2l_parser.parse(Path(a2l_path))

    print(f"ELF符号数: {len(symbols)}")
    print(f"A2L变量数: {len(a2l_vars)}\n")

    # 测试不匹配的变量
    test_vars = [
        "TmsApp_ARID_DEF.IDP_o1.gCDD_TMSMDVFRLF_I_uint8",
        "TmsApp_ARID_DEF.ODP_o194",
        "CbnHMI_DW.is_TempSet",
    ]

    print("测试叶子节点匹配逻辑:")
    print("="*70)

    for var in test_vars:
        if var not in a2l_vars:
            continue

        # 1. 精确匹配
        if var in symbols:
            print(f"✅ {var}")
            print(f"   精确匹配: 0x{symbols[var]:08X}")
            continue

        # 2. 叶子节点匹配
        leaf_name = var.split(".")[-1]
        if leaf_name in symbols:
            print(f"✅ {var}")
            print(f"   叶子匹配: {leaf_name} -> 0x{symbols[leaf_name]:08X}")
            continue

        # 3. 未匹配
        print(f"❌ {var}")
        print(f"   未找到")

    # 统计所有带点号变量的匹配情况
    print("\n" + "="*70)
    print("统计带点号变量的匹配情况:")
    print("="*70)

    dot_vars = [v for v in a2l_vars.keys() if "." in v]
    print(f"A2L中带点号变量数: {len(dot_vars)}")

    exact_match = 0
    leaf_match = 0
    no_match = 0

    for var in dot_vars:
        if var in symbols:
            exact_match += 1
        else:
            leaf_name = var.split(".")[-1]
            if leaf_name in symbols:
                leaf_match += 1
            else:
                no_match += 1

    print(f"  精确匹配: {exact_match}")
    print(f"  叶子匹配: {leaf_match}")
    print(f"  未匹配: {no_match}")
    print(f"  总匹配率: {(exact_match + leaf_match) / len(dot_vars) * 100:.1f}%")

if __name__ == "__main__":
    test_leaf_matching()
