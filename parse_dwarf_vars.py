#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用DWARF调试信息解析变量."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile
from elftools.dwarf.die import DIE

elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")

# 手动处理独有的变量
manual_only_vars = [
    "CbnBlw_B.Out",
    "CbnBlw_DW.Delay2_DSTATE",
    "CbnEMA_B.Switch",
    "CbnEMA_DW.DelayInput1_DSTATE",
    "CbnRec_DW.Delay_DSTATE_i",
]

print("="*70)
print("使用DWARF调试信息查找变量")
print("="*70)

with open(elf_path, 'rb') as f:
    elf = ELFFile(f)

    if not elf.has_dwarf_info():
        print("ELF不包含DWARF信息")
        sys.exit(1)

    dwarf_info = elf.get_dwarf_info()

    # 遍历所有DIE（Debugging Information Entry）
    print("\n搜索目标变量...")

    found_vars = {}

    for cu in dwarf_info.iter_CUs():
        for die in cu.iter_DIEs():
            # 检查是否有名称和位置属性
            if 'DW_AT_name' in die.attributes:
                name_attr = die.attributes.get('DW_AT_name')
                if name_attr:
                    name = name_attr.value

                    # 处理bytes类型
                    if isinstance(name, bytes):
                        name = name.decode('utf-8', errors='ignore')

                    # 检查是否是目标变量
                    for target in manual_only_vars:
                        if name == target:
                            # 获取地址
                            addr = None
                            location = die.attributes.get('DW_AT_location')
                            if location:
                                loc_value = location.value
                                addr = str(loc_value)

                            found_vars[target] = (name, addr, die.tag)

                # 早期退出
                if len(found_vars) >= len(manual_only_vars):
                    break

        if len(found_vars) >= len(manual_only_vars):
            break

    print(f"\n找到 {len(found_vars)} 个变量:")
    for var, (name, addr, tag) in found_vars.items():
        print(f"  {var}:")
        print(f"    DIE名称: {name}")
        print(f"    地址: {addr}")
        print(f"    DIE标签: {tag}")

print("\n" + "="*70)
