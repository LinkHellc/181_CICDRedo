#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查ELF文件中的DWARF调试信息."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile

elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"

print("检查ELF文件中的调试信息:")
print("="*70)

with open(elf_path, 'rb') as f:
    elf = ELFFile(f)

    print(f"ELF类型: {elf.header.e_type}")
    print(f"ELF架构: {elf.header.e_machine}")
    print()

    # 检查所有section
    debug_sections = []
    for section in elf.iter_sections():
        name = section.name
        if any(x in name for x in ['debug', '.dwo', '.zdebug', 'dwo', 'dwarf']):
            debug_sections.append((name, section.header.sh_type, section.header.sh_size))

    if debug_sections:
        print("调试相关sections:")
        for name, sh_type, size in debug_sections:
            print(f"  {name:30s} 类型: {sh_type:20s} 大小: {size:10d}")
    else:
        print("未找到调试sections")

    # 检查.symtab
    print()
    symtab = elf.get_section_by_name('.symtab')
    if symtab:
        sym_symbols = list(symtab.iter_symbols())
        print(f".symtab section:")
        print(f"  符号数量: {len(sym_symbols)}")

        # 统计有效符号
        valid_syms = [s for s in sym_symbols if s.name and s['st_value'] > 0]
        print(f"  有效符号(有地址): {len(valid_syms)}")

        # 统计带点号的符号
        dot_syms = [s for s in valid_syms if '.' in s.name]
        print(f"  带点号的符号: {len(dot_syms)}")

    # 检查.dynsym
    print()
    dynsym = elf.get_section_by_name('.dynsym')
    if dynsym:
        dyn_symbols = list(dynsym.iter_symbols())
        print(f".dynsym section:")
        print(f"  符号数量: {len(dyn_symbols)}")

        valid_dyn = [s for s in dyn_symbols if s.name and s['st_value'] > 0]
        print(f"  有效符号(有地址): {len(valid_dyn)}")

    # 检查是否有调试信息
    print()
    has_debug_info = elf.has_dwarf_info()
    print(f"包含DWARF调试信息: {has_debug_info}")

    if has_debug_info:
        try:
            dwarf_info = elf.get_dwarf_info()
            print(f"DWARF版本: {dwarf_info.version if hasattr(dwarf_info, 'version') else '未知'}")

            # 尝试获取编译单元
            if hasattr(dwarf_info, 'iter_CUs'):
                cu_count = sum(1 for _ in dwarf_info.iter_CUs())
                print(f"编译单元数量: {cu_count}")
        except Exception as e:
            print(f"读取DWARF信息出错: {e}")

print()
print("="*70)
