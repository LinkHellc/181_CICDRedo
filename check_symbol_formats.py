#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查符号名格式差异."""

import sys
import io
import re
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile

elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")
manual_file = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_Mana.a2l")

# 获取ELF符号
elf_symbols = {}
with open(elf_path, 'rb') as f:
    elf = ELFFile(f)
    symtab = elf.get_section_by_name('.symtab')
    if symtab:
        for symbol in symtab.iter_symbols():
            if symbol.name and symbol['st_value'] > 0:
                elf_symbols[symbol.name] = symbol['st_value']

# 获取手动处理的变量
manual_vars = {}
addr_pattern = re.compile(r'(?:ECU_ADDRESS|/\*\s*ECU\s+Address\s*\*/)\s+(0x[0-9A-Fa-f]+)')
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
                    addr = int(addr_match.group(1), 16)
                    manual_vars[var_name] = addr
                    break

print("="*70)
print("检查符号名格式差异")
print("="*70)
print(f"ELF符号数: {len(elf_symbols)}")
print(f"手动处理变量数: {len(manual_vars)}")

# 找出手动处理有但ELF没有的变量（检查是否有C mangling等问题）
manual_only_names = set(manual_vars.keys()) - set(elf_symbols.keys())
print(f"\n手动处理独有变量名: {len(manual_only_names)}")

# 检查这些变量名的特征
print("\n分析独有变量名特征:")
dot_count = sum(1 for name in manual_only_names if '.' in name)
double_underscore_count = sum(1 for name in manual_only_names if '__' in name)
underscore_suffix_count = sum(1 for name in manual_only_names if name.endswith('_'))

print(f"  包含点号: {dot_count}")
print(f"  包含双下划线: {double_underscore_count}")
print(f"  以下划线结尾: {underscore_suffix_count}")

# 检查ELF中是否有去掉后缀的版本
print("\n检查ELF中是否有去掉下划线后缀的版本:")
found_matches = 0
for name in list(manual_only_names)[:50]:
    if name.endswith('_'):
        stripped = name.rstrip('_')
        if stripped in elf_symbols:
            print(f"  {name} -> ELF中可能: {stripped}")
            found_matches += 1
            if found_matches >= 5:
                break

if found_matches == 0:
    print("  未找到匹配")

# 检查是否是C++ mangling导致的
# 许多编译器会生成带特殊后缀的符号名
cpp_suffixes = ['_', '.0', '.1', '.2', '.3', '.4']
print("\n检查C++/编译器生成的后缀:")
suffix_counts = {}
for name in list(manual_only_names)[:100]:
    for suffix in cpp_suffixes:
        if name.endswith(suffix):
            suffix_counts[suffix] = suffix_counts.get(suffix, 0) + 1
            break

for suffix, count in sorted(suffix_counts.items()):
    print(f"  '{suffix}' 后缀: {count}")

# 随机抽样检查几个独有变量
print("\n随机抽样独有变量:")
import random
sample = random.sample(list(manual_only_names), 10)
for name in sample:
    print(f"  {name}: 0x{manual_vars[name]:08X}")
