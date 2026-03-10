#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度调查未匹配的变量."""

import sys
import io
from pathlib import Path
from elftools.elf.elffile import ELFFile

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"

# 未匹配的变量
unmatched = [
    "TmsApp_ARID_DEF.ODP_o194",
    "CbnHMI_DW.is_TempSet",
    "TmsApp_ARID_DEF.IDP_o1.gCDD_TMSMDVFRLF_I_uint8",
]

print("在ELF中查找未匹配变量的可能变体:\n")

with open(elf_path, 'rb') as f:
    elf = ELFFile(f)

    symtab = elf.get_section_by_name('.symtab')
    if symtab:
        all_symbols = {}
        for symbol in symtab.iter_symbols():
            if symbol.name and symbol['st_value'] > 0:
                all_symbols[symbol.name] = symbol['st_value']

        print(f"ELF符号总数: {len(all_symbols)}\n")

        for var in unmatched:
            print(f"查找: {var}")

            # 精确匹配
            if var in all_symbols:
                print(f"  ✅ 精确匹配: 0x{all_symbols[var]:08X}")
                continue

            # 尝试各种变体
            variants = {
                "点号变下划线": var.replace(".", "_"),
                "点号变双下划线": var.replace(".", "__"),
                "移除点号": var.replace(".", ""),
            }

            found = False
            for desc, variant in variants.items():
                if variant in all_symbols:
                    print(f"  ⚠️  {desc}: {variant} -> 0x{all_symbols[variant]:08X}")
                    found = True
                    break

            if not found:
                # 模糊搜索：包含主要部分
                parts = var.split(".")
                if len(parts) > 1:
                    last_part = parts[-1]
                    matches = [s for s in all_symbols.keys() if last_part in s]
                    if matches:
                        print(f"  ℹ️  可能的匹配 (包含 '{last_part}'):")
                        for m in matches[:3]:
                            print(f"     - {m} -> 0x{all_symbols[m]:08X}")
                    else:
                        print(f"  ❌ 未找到")
                else:
                    print(f"  ❌ 未找到")

# 检查MATLAB是否有特殊处理
print("\n" + "="*60)
print("检查A2L文件中的地址格式:")
print("="*60)

a2l_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp.a2l"
import re

with open(a2l_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有带点号的变量名
dot_var_pattern = re.compile(r'/\*\s*Name\s*\*/\s*([A-Za-z0-9_]+\.[A-Za-z0-9_.]+)')
dot_vars = dot_var_pattern.findall(content)

print(f"\nA2L中带点号的变量数: {len(dot_vars)}")

# 统计地址格式
ecu_address_count = content.count('ECU_ADDRESS')
comment_ecu_addr_count = content.count('/* ECU Address */')

print(f"ECU_ADDRESS格式: {ecu_address_count} 处")
print(f"/* ECU Address */格式: {comment_ecu_addr_count} 处")
