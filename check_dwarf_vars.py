#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用DWARF调试信息查找变量."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile

elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"

# 手动独有的变量
manual_only_vars = [
    "CbnEMA_DW.UnitDelay2_DSTATE_p",
    "TmsApp_ARID_DEF.ODP_o567",
    "CbnHMI_B.AND_n",
]

print("使用DWARF调试信息查找变量:")
print("="*70)

with open(elf_path, 'rb') as f:
    elf = ELFFile(f)

    if not elf.has_dwarf_info():
        print("ELF文件不包含DWARF信息")
        sys.exit(1)

    dwarf_info = elf.get_dwarf_info()

    # 方法1：遍历所有编译单元的DIE（Debugging Information Entry）
    print("\n方法1: 遍历所有DIE查找变量...")
    found_vars = set()

    cu_count = 0
    for cu in dwarf_info.iter_CUs():
        cu_count += 1
        # 显示进度
        if cu_count % 1000 == 0:
            print(f"  已处理 {cu_count} 个编译单元...")

        # 遍历CU中的所有DIE
        for die in cu.iter_DIEs():
            # 只关心有名称和地址的DIE
            if 'DW_AT_name' in die.attributes and 'DW_AT_location' in die.attributes:
                name = die.attributes.get('DW_AT_name').value

                # 检查是否是我们找的变量
                for target in manual_only_vars:
                    if target == name:
                        location = die.attributes.get('DW_AT_location').value
                        print(f"  ✅ 找到: {name}")
                        print(f"     Location: {location}")
                        found_vars.add(target)

                    # 检查叶子节点
                    elif "." in target:
                        leaf = target.split(".")[-1]
                        if name == leaf:
                            location = die.attributes.get('DW_AT_location').value
                            print(f"  ⚠️  {target} -> DIE名称: {name}")
                            print(f"     Location: {location}")

        # 如果找到了所有变量，提前退出
        if len(found_vars) >= len(manual_only_vars):
            break

    print(f"\n处理了 {cu_count} 个编译单元")

    # 方法2：使用.dwarf_aranges（地址范围）
    print("\n方法2: 使用.debug_aranges查找...")
    aranges = dwarf_info.aranges()
    if aranges:
        for arange in aranges.iter_entries():
            pass  # 需要进一步解析

print("\n" + "="*70)
