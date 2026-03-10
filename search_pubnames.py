#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在.debug_pubnames中搜索变量名."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile

elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")

# 目标变量
target_vars = [
    "CbnBlw_B.Out",
    "CbnEMA_B.Switch",
    "CbnBlw_DW.Delay2_DSTATE",
]

print("="*70)
print("在.debug_pubnames中搜索变量名")
print("="*70)

with open(elf_path, 'rb') as f:
    elf = ELFFile(f)

    pubnames = elf.get_section_by_name('.debug_pubnames')
    if not pubnames:
        print("未找到.debug_pubnames section")
        sys.exit(1)

    data = pubnames.data()

    print(f".debug_pubnames大小: {len(data)} bytes")

    # 直接搜索变量名
    for target in target_vars:
        target_bytes = target.encode('utf-8')

        # 搜索精确匹配
        if target_bytes in data:
            print(f"\n✅ '{target}' 在.debug_pubnames中")

            # 找到所有出现位置
            pos = 0
            occurrences = []
            while True:
                pos = data.find(target_bytes, pos)
                if pos == -1:
                    break
                occurrences.append(pos)
                pos += 1

            print(f"  出现 {len(occurrences)} 次，位置: {occurrences[:3]}")
        else:
            print(f"\n❌ '{target}' 未在.debug_pubnames中")

            # 检查叶子节点
            if "." in target:
                leaf = target.split(".")[-1]
                leaf_bytes = leaf.encode('utf-8')
                if leaf_bytes in data:
                    print(f"  但叶子节点 '{leaf}' 在.debug_pubnames中")

                    # 找到所有出现位置
                    pos = 0
                    occurrences = []
                    while True:
                        pos = data.find(leaf_bytes, pos)
                        if pos == -1:
                            break
                        occurrences.append(pos)
                        pos += 1

                    print(f"  叶子出现 {len(occurrences)} 次，位置: {occurrences[:3]}")

print("\n" + "="*70)
