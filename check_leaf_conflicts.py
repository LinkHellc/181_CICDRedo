#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查叶子节点名称冲突."""

import sys
import io
from pathlib import Path
from collections import defaultdict

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser

def check_leaf_conflicts():
    """检查叶子节点冲突"""
    elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"

    parser = ELFParser()
    symbols = parser.extract_symbols(Path(elf_path))

    # 统计叶子节点出现次数
    leaf_counts = defaultdict(list)
    for symbol_name in symbols.keys():
        if "." in symbol_name:
            leaf = symbol_name.split(".")[-1]
            leaf_counts[leaf].append(symbol_name)

    # 找出有冲突的叶子节点
    conflicts = {leaf: names for leaf, names in leaf_counts.items() if len(names) > 1}

    print(f"ELF符号总数: {len(symbols)}")
    print(f"带点号的符号数: {sum(len(names) for names in leaf_counts.values())}")
    print(f"唯一叶子节点数: {len(leaf_counts)}")
    print(f"有冲突的叶子节点数: {len(conflicts)}\n")

    if conflicts:
        print("叶子节点冲突示例 (前10个):")
        print("="*70)
        for i, (leaf, names) in enumerate(list(conflicts.items())[:10]):
            print(f"\n叶子节点: {leaf} ({len(names)}个不同前缀)")
            for name in names[:5]:
                print(f"  - {name} -> 0x{symbols[name]:08X}")

    # 检查特定问题变量
    print("\n" + "="*70)
    print("检查问题变量的叶子匹配:")
    print("="*70)

    problem_vars = [
        "TmsApp_ARID_DEF.IDP_o3.gCAN_ACU_1_SecRowRBeltWarning_uint8",
        "TmsApp_ARID_DEF.IDP_o3.gCAN_BMS_SOCLight_uint8",
    ]

    for var in problem_vars:
        leaf = var.split(".")[-1]
        if leaf in leaf_counts:
            print(f"\n{var}")
            print(f"  叶子节点: {leaf}")
            print(f"  ELF中的匹配:")
            for name in leaf_counts[leaf]:
                print(f"    - {name} -> 0x{symbols[name]:08X}")
        else:
            print(f"\n{var}")
            print(f"  叶子节点: {leaf} 未在ELF中找到")

if __name__ == "__main__":
    check_leaf_conflicts()
