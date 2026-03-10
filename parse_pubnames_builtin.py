#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用pyelftools解析pubnames."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile

elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")

print("="*70)
print("使用pyelftools解析.debug_pubnames")
print("="*70)

with open(elf_path, 'rb') as f:
    elf = ELFFile(f)

    pubnames = elf.get_section_by_name('.debug_pubnames')
    if not pubnames:
        print("未找到.debug_pubnames section")
        sys.exit(1)

    print(f"Section size: {pubnames.header.sh_size}")

    # 使用pyelftools内置的pubnames解析
    try:
        pubnames_list = list(pubnames.iter_pubnames())
        print(f"读取到 {len(pubnames_list)} 个pubnames")

        if len(pubnames_list) > 0:
            print(f"\n前20个pubnames:")
            for i, (offset, die_offset, name) in enumerate(pubnames_list[:20]):
                print(f"  {i+1}. offset=0x{offset:08X}, die_offset=0x{die_offset:08X}, name={name}")

        # 查找目标变量
        manual_only_vars = ["CbnBlw_B.Out", "CbnEMA_B.Switch"]
        print(f"\n查找目标变量:")
        for target in manual_only_vars:
            for offset, die_offset, name in pubnames_list:
                if name == target:
                    print(f"  ✅ {target}: offset=0x{offset:08X}")
                    break

    except Exception as e:
        print(f"解析失败: {e}")
        import traceback
        traceback.print_exc()
