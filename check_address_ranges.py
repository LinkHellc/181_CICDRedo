#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查ELF地址范围和手动处理变量的地址分布."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile

elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")

print("="*70)
print("检查ELF地址范围")
print("="*70)

with open(elf_path, 'rb') as f:
    elf = ELFFile(f)

    # 检查所有可加载的段
    print("\n可加载段 (PT_LOAD):")
    load_segments = []
    for segment in elf.iter_segments():
        if segment.header.p_type == 'PT_LOAD':
            vaddr = segment.header.p_vaddr
            memsz = segment.header.p_memsz
            filesz = segment.header.p_filesz
            load_segments.append((vaddr, vaddr + memsz))
            print(f"  虚拟地址: 0x{vaddr:08X} - 0x{vaddr + memsz:08X} (大小: {memsz})")

    # 检查符号的地址范围
    symtab = elf.get_section_by_name('.symtab')
    if symtab:
        addrs = []
        for symbol in symtab.iter_symbols():
            if symbol['st_value'] > 0:
                addrs.append(symbol['st_value'])

        if addrs:
            addrs.sort()
            print(f"\n符号地址范围:")
            print(f"  最小: 0x{addrs[0]:08X}")
            print(f"  最大: 0x{addrs[-1]:08X}")

            # 统计0x2804xxxx范围的符号
            range_2804 = [a for a in addrs if 0x28040000 <= a < 0x28050000]
            print(f"  0x28040000-0x2804FFFF范围: {len(range_2804)} 个符号")

print("\n" + "="*70)

# 检查手动处理独有变量的地址分布
import re

manual_file = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_Mana.a2l")
addr_pattern = re.compile(r'(?:ECU_ADDRESS|/\*\s*ECU\s+Address\s*\*/)\s+(0x[0-9A-Fa-f]+)')

manual_addrs = []
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
                    addr = int(addr_str, 16)
                    manual_addrs.append((var_name, addr))
                    break

print("\n手动处理变量的地址分布:")
manual_addrs_sorted = sorted(manual_addrs, key=lambda x: x[1])

print(f"  总数: {len(manual_addrs)}")
if manual_addrs_sorted:
    print(f"  最小: 0x{manual_addrs_sorted[0][1]:08X}")
    print(f"  最大: 0x{manual_addrs_sorted[-1][1]:08X}")

    # 统计各地址段
    ranges = {
        "0x2803xxxx": sum(1 for _, a in manual_addrs if 0x28030000 <= a < 0x28040000),
        "0x2804xxxx": sum(1 for _, a in manual_addrs if 0x28040000 <= a < 0x28050000),
        "0x2805xxxx": sum(1 for _, a in manual_addrs if 0x28050000 <= a < 0x28060000),
    }

    print(f"\n地址段分布:")
    for range_name, count in ranges.items():
        print(f"  {range_name}: {count}")
