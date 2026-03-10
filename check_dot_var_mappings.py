#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查带点号变量在ELF中的对应符号."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile

elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")

# 获取ELF符号
elf_symbols = set()
with open(elf_path, 'rb') as f:
    elf = ELFFile(f)
    symtab = elf.get_section_by_name('.symtab')
    if symtab:
        for symbol in symtab.iter_symbols():
            if symbol.name and symbol['st_value'] > 0:
                elf_symbols.add(symbol.name)

# 手动处理独有变量（带点号）
manual_only_with_dot = [
    "CbnBlw_B.Out",
    "CbnBlw_DW.Delay2_DSTATE",
    "CbnEMA_B.Switch",
    "CbnEMA_B.Switch1",
    "CbnEMA_DW.DelayInput1_DSTATE",
    "CbnEMA_DW.Delay_DSTATE",
    "CbnEMA_DW.Filter.Delay_DSTATE",
    "CbnEMA_DW.Filter2.Delay_DSTATE",
    "CbnRec_DW.Delay_DSTATE_i",
    "CbnSpc_DW.Unit_Delay_DSTATE",
]

print("="*70)
print("检查带点号变量在ELF中的可能对应符号")
print("="*70)

for var in manual_only_with_dot:
    print(f"\n{var}:")

    # 方法1：去掉所有点号
    no_dot = var.replace(".", "")
    if no_dot in elf_symbols:
        print(f"  去掉点号: {no_dot}")

    # 方法2：点号替换为下划线
    underscore = var.replace(".", "_")
    if underscore in elf_symbols:
        print(f"  点号转下划线: {underscore}")

    # 方法3：只保留最后一个点后的部分
    parts = var.split(".")
    last_part = parts[-1]
    if last_part in elf_symbols:
        print(f"  叶子节点: {last_part}")

    # 方法4：搜索包含关键词的符号
    keywords = [p for p in parts if len(p) > 3][:2]
    matches = []
    for sym in elf_symbols:
        if all(kw.lower() in sym.lower() for kw in keywords):
            matches.append(sym)
            if len(matches) >= 3:
                break

    if matches:
        print(f"  包含关键词的匹配:")
        for m in matches[:3]:
            print(f"    - {m}")
