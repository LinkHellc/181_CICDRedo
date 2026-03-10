#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终验证：手动处理与当前ELF的一致性."""

import sys
import io
import re
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser

def verify_manual_against_current_elf():
    """验证手动处理与当前ELF的一致性"""
    elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")
    manual_file = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_Mana.a2l")

    # 获取ELF符号
    parser = ELFParser()
    symbols = parser.extract_symbols(elf_path)

    # 提取手动处理的地址
    addr_pattern = re.compile(r'(?:ECU_ADDRESS|/\*\s*ECU\s+Address\s*\*/)\s+(0x[0-9A-Fa-f]+)')
    manual_addrs = {}

    content = manual_file.read_text(encoding='utf-8')
    lines = content.splitlines()

    for i, line in enumerate(lines):
        if '/* Name */' in line or '/* Name                   */' in line:
            var_match = re.search(r'Name\s*\*/\s*(\S+)', line)
            if var_match:
                var_name = var_match.group(1)
                for j in range(i, min(i+20, len(lines))):
                    addr_match = addr_pattern.search(lines[j])
                    if addr_match:
                        addr_str = addr_match.group(1)
                        if addr_str != '0x0000':
                            manual_addrs[var_name] = int(addr_str, 16)
                        break

    print("="*70)
    print("验证手动处理A2L与当前ELF的一致性")
    print("="*70)
    print(f"当前ELF符号数: {len(symbols)}")
    print(f"手动处理更新数: {len(manual_addrs)}")

    # 检查手动更新的变量是否在当前ELF中
    exact_match = 0
    leaf_match = 0
    not_found = 0
    addr_mismatch = 0
    addr_mismatch_list = []

    for var, manual_addr in manual_addrs.items():
        elf_addr = None
        match_type = None

        # 精确匹配
        if var in symbols:
            elf_addr = symbols[var]
            match_type = "exact"
        # 叶子匹配
        elif "." in var:
            leaf = var.split(".")[-1]
            if leaf in symbols:
                elf_addr = symbols[leaf]
                match_type = "leaf"

        if elf_addr is not None:
            if elf_addr == manual_addr:
                if match_type == "exact":
                    exact_match += 1
                else:
                    leaf_match += 1
            else:
                addr_mismatch += 1
                if len(addr_mismatch_list) < 10:
                    addr_mismatch_list.append((var, elf_addr, manual_addr, match_type))
        else:
            not_found += 1

    print(f"\n匹配统计:")
    print(f"  ✅ 精确匹配(地址一致): {exact_match}")
    print(f"  ✅ 叶子匹配(地址一致): {leaf_match}")
    print(f"  ❌ 当前ELF中未找到: {not_found}")
    print(f"  ❌ 地址不一致: {addr_mismatch}")

    total_matched = exact_match + leaf_match
    consistency = total_matched / len(manual_addrs) * 100 if manual_addrs else 0
    print(f"\n与当前ELF的一致性: {consistency:.2f}%")

    if addr_mismatch_list:
        print(f"\n地址不一致的变量示例:")
        for var, elf_addr, manual_addr, mt in addr_mismatch_list:
            print(f"  {var}")
            print(f"    当前ELF: 0x{elf_addr:08X}")
            print(f"    手动处理: 0x{manual_addr:08X}")
            print(f"    匹配类型: {mt}")

    if not_found > 0:
        print(f"\n当前ELF中未找到的变量示例:")
        count = 0
        for var, manual_addr in manual_addrs.items():
            elf_addr = None
            if var not in symbols:
                if "." in var:
                    leaf = var.split(".")[-1]
                    if leaf not in symbols:
                        print(f"  {var}: 0x{manual_addr:08X}")
                        count += 1
                        if count >= 10:
                            break
                else:
                    print(f"  {var}: 0x{manual_addr:08X}")
                    count += 1
                    if count >= 10:
                        break

    print("\n" + "="*70)
    print("结论:")
    if consistency < 80:
        print("手动处理A2L使用的不是当前ELF文件，或者使用了额外信息源。")
    elif not_found > 0:
        print("手动处理A2L包含当前ELF中不存在的变量，可能使用了DWARF调试信息。")
    else:
        print("手动处理A2L与当前ELF高度一致。")

if __name__ == "__main__":
    verify_manual_against_current_elf()
