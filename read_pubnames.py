#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从.debug_pubnames section读取变量."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile

elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")

# 手动处理独有的变量
manual_only_vars = [
    "CbnBlw_B.Out",
    "CbnBlw_DW.Delay2_DSTATE",
    "CbnEMA_B.Switch",
    "CbnEMA_DW.DelayInput1_DSTATE",
]

print("="*70)
print("从.debug_pubnames section读取变量")
print("="*70)

with open(elf_path, 'rb') as f:
    elf = ELFFile(f)

    pubnames_section = elf.get_section_by_name('.debug_pubnames')
    if not pubnames_section:
        print("未找到.debug_pubnames section")
        sys.exit(1)

    print(f"Found .debug_pubnames section")
    print(f"Size: {pubnames_section.header.sh_size} bytes")

    # .debug_pubnames格式：
    # - header (长度等)
    # - 一系列条目，每个包含：
    #   - length (u32)
    #   - offset (u32) - 在.debug_info中的偏移
    #   - name (null结尾字符串)

    data = pubnames_section.data()
    pos = 0

    # 跳过header
    # header格式: length(4) + version(2) + debug_info_offset(4) + debug_info_length(4)
    header_length = 14

    # 读取所有符号名
    pubnames = []
    pos = header_length

    while pos < len(data):
        # 读取长度
        length = int.from_bytes(data[pos:pos+4], byteorder='little')
        pos += 4

        if length == 0 or length == 0xFFFFFFFF:
            break

        # 读取偏移
        offset = int.from_bytes(data[pos:pos+4], byteorder='little')
        pos += 4

        # 读取名称（以null结尾）
        name_start = pos
        while pos < len(data) and data[pos] != 0:
            pos += 1
        name = data[name_start:pos].decode('utf-8', errors='ignore')
        pos += 1

        if name:
            pubnames.append((offset, name))

    print(f"\n从.debug_pubnames读取了 {len(pubnames)} 个符号")

    # 查找目标变量
    print(f"\n查找目标变量:")
    for target in manual_only_vars:
        found = False
        for offset, name in pubnames:
            if name == target:
                print(f"  ✅ {target}: offset=0x{offset:08X}")
                found = True
                break

        if not found:
            # 检查部分匹配
            for offset, name in pubnames:
                if target.endswith(name) or name.endswith(target):
                    print(f"  ⚠️ {target} -> pubname: {name}")
                    found = True
                    break

        if not found:
            # 检查叶子节点
            if "." in target:
                leaf = target.split(".")[-1]
                for offset, name in pubnames:
                    if name == leaf:
                        print(f"  ⚠️ {target} -> pubname叶子: {name}")
                        found = True
                        break

        if not found:
            print(f"  ❌ {target} 未找到")

print("\n" + "="*70)
