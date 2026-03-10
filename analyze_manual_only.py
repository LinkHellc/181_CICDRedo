#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查手动处理独有变量的详细情况."""

import sys
import io
import re
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser
from a2l.a2l_parser import A2LParser

elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")
manual_file = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_Mana.a2l")

print("="*70)
print("分析手动处理独有变量")
print("="*70)

# 获取ELF符号
elf_parser = ELFParser()
symbols = elf_parser.extract_symbols(elf_path)

# 解析手动处理
a2l_parser = A2LParser()
manual_vars = a2l_parser.parse(manual_file)

# 找出手动处理中已更新但当前ELF中找不到的变量
manual_only = []
for var_name, var_info in manual_vars.items():
    if var_info.address != 0:
        found = False
        if var_name in symbols:
            if symbols[var_name] == var_info.address:
                found = True
        elif "." in var_name:
            leaf = var_name.split(".")[-1]
            if leaf in symbols:
                if symbols[leaf] == var_info.address:
                    found = True
        if not found:
            manual_only.append((var_name, var_info.address, var_info.var_type, var_info.address_line))

print(f"手动处理中已更新但当前ELF中找不到的变量: {len(manual_only)}")

# 检查这些变量在ELF中是否有类似的符号
print(f"\n检查这些变量在ELF中是否有相似的符号:")

checked = 0
for var_name, addr, var_type, line in manual_only[:20]:
    print(f"\n  {var_name} (0x{addr:08X}) 行:{line}")

    # 检查精确匹配
    if var_name in symbols:
        print(f"    ELF中有此符号，但地址不同: 0x{symbols[var_name]:08X}")
        continue

    # 检查叶子节点
    if "." in var_name:
        leaf = var_name.split(".")[-1]
        if leaf in symbols:
            print(f"    ELF中有叶子 {leaf}，但地址不同: 0x{symbols[leaf]:08X}")
            continue

    # 搜索包含关键字段的符号
    parts = var_name.split("_")
    keywords = [p for p in parts if len(p) > 3][:3]  # 取前3个有意义的部分

    matches = []
    for symbol_name in symbols.keys():
        if all(kw.lower() in symbol_name.lower() for kw in keywords if len(kw) > 2):
            matches.append((symbol_name, symbols[symbol_name]))

    if matches:
        print(f"    ELF中相似的符号:")
        for sym, sym_addr in matches[:3]:
            print(f"      - {sym} -> 0x{sym_addr:08X}")
    else:
        print(f"    ELF中未找到相似符号")

    checked += 1
    if checked >= 10:
        break

# 统计不同类型的变量
type_count = {}
for var_name, addr, var_type, _ in manual_only:
    type_count[var_type] = type_count.get(var_type, 0) + 1

print(f"\n按变量类型统计:")
for var_type, count in sorted(type_count.items()):
    print(f"  {var_type}: {count}")
