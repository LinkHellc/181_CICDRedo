#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证工具的正确性 - 基于当前ELF."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser
from a2l.a2l_parser import A2LParser

def verify_tool_correctness():
    """验证工具的正确性"""
    elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"
    tool_output = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_test_output.a2l"

    elf_parser = ELFParser()
    a2l_parser = A2LParser()

    symbols = elf_parser.extract_symbols(Path(elf_path))
    a2l_vars = a2l_parser.parse(Path(tool_output))

    print("验证工具正确性 (基于当前ELF):")
    print("="*70)
    print(f"ELF符号数: {len(symbols)}")
    print(f"工具输出变量数: {len(a2l_vars)}")

    # 检查所有已更新变量的地址是否正确
    correct = 0
    incorrect = 0
    errors = []

    for var_name, var_info in a2l_vars.items():
        if var_info.address != 0:
            # 变量已更新，验证地址是否正确
            expected_addr = None
            match_type = None

            # 1. 精确匹配
            if var_name in symbols:
                expected_addr = symbols[var_name]
                match_type = "exact"
            # 2. 叶子节点匹配
            elif "." in var_name:
                leaf = var_name.split(".")[-1]
                if leaf in symbols:
                    expected_addr = symbols[leaf]
                    match_type = "leaf"

            if expected_addr is not None and var_info.address == expected_addr:
                correct += 1
            else:
                incorrect += 1
                if len(errors) < 20:
                    errors.append((var_name, var_info.address, expected_addr, match_type))

    print(f"\n验证结果:")
    print(f"  ✅ 正确: {correct} 个")
    print(f"  ❌ 错误: {incorrect} 个")
    print(f"  准确率: {correct / (correct + incorrect) * 100:.2f}%")

    if errors:
        print(f"\n错误示例 (最多20个):")
        for var, actual, expected, match_type in errors:
            print(f"  {var}")
            print(f"    工具输出: 0x{actual:08X}")
            print(f"    ELF期望: 0x{expected:08X if expected else None}")
            print(f"    匹配类型: {match_type}")

if __name__ == "__main__":
    verify_tool_correctness()
