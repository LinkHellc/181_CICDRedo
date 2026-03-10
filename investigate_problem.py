#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调查问题变量的真实情况."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser
from a2l.a2l_parser import A2LParser

def investigate():
    """调查问题变量"""
    elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"
    a2l_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp.a2l"

    elf_parser = ELFParser()
    a2l_parser = A2LParser()

    symbols = elf_parser.extract_symbols(Path(elf_path))
    a2l_vars = a2l_parser.parse(Path(a2l_path))

    # 问题变量
    var_name = "TmsApp_ARID_DEF.IDP_o3.gCAN_ACU_1_SecRowRBeltWarning_uint8"
    expected_addr = 0x280359C7

    print(f"调查变量: {var_name}")
    print(f"期望地址: 0x{expected_addr:08X}\n")

    # 检查ELF中是否有精确匹配
    if var_name in symbols:
        print(f"✅ 精确匹配: 0x{symbols[var_name]:08X}")
    else:
        print("❌ ELF中无精确匹配")

        # 搜索部分匹配
        parts = var_name.split(".")
        print(f"\n搜索部分匹配:")
        for i in range(len(parts)):
            partial = ".".join(parts[-i-1:]) if i > 0 else parts[-1]
            if partial in symbols:
                print(f"  ✅ '{partial}' -> 0x{symbols[partial]:08X}")
            else:
                print(f"  ❌ '{partial}' 未找到")

    # 搜索包含关键字段的符号
    keywords = ["gCAN_ACU", "SecRowRBeltWarning", "uint8"]
    print(f"\n搜索包含关键词的符号:")
    for keyword in keywords:
        matches = [s for s in symbols.keys() if keyword in s]
        if matches:
            print(f"\n  包含 '{keyword}' ({len(matches)}个):")
            for m in matches[:5]:
                print(f"    - {m} -> 0x{symbols[m]:08X}")

    # 检查期望地址对应的符号
    print(f"\n检查期望地址 0x{expected_addr:08X} 对应的符号:")
    addr_matches = [name for name, addr in symbols.items() if addr == expected_addr]
    if addr_matches:
        for name in addr_matches[:10]:
            print(f"  - {name}")
    else:
        print("  未找到任何符号使用此地址")

if __name__ == "__main__":
    investigate()
