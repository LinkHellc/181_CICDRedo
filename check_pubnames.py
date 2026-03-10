#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查.debug_pubnames section中的符号."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from elftools.elf.elffile import ELFFile

elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"

# 手动处理中独有的变量
manual_only_vars = [
    "CbnEMA_DW.UnitDelay2_DSTATE_p",
    "TmsApp_ARID_DEF.ODP_o567",
    "CbnHMI_B.AND_n",
    "TmsApp_ARID_DEF.ODP_o163",
    "CbnHMI_DW.UnitDelay7_DSTATE",
    "TmsApp_ARID_DEF.ODP_o735",
    "TmsApp_ARID_DEF.ODP_o113",
]

print("检查.debug_pubnames中的符号:")
print("="*70)

with open(elf_path, 'rb') as f:
    elf = ELFFile(f)

    # 获取.debug_pubnames section
    pubnames = elf.get_section_by_name('.debug_pubnames')

    if pubnames:
        print(f".debug_pubnames section找到")
        print(f"大小: {pubnames.header.sh_size} bytes")

        # 解析pubnames
        # .debug_pubnames格式：一系列条目，每个包含长度、偏移、名称
        pubnames_list = []
        data = pubnames.data()

        # 尝试解析
        pos = 0
        entry_count = 0
        sample_names = []

        # 简单的文本搜索
        content_str = data.decode('utf-8', errors='ignore')

        # 检查手动独有的变量是否在pubnames中
        print(f"\n检查手动独有的变量:")
        for var in manual_only_vars:
            if var.encode('utf-8') in data:
                print(f"  ✅ {var} 在.debug_pubnames中")
            else:
                # 检查叶子节点
                leaf = var.split(".")[-1]
                if leaf.encode('utf-8') in data:
                    print(f"  ⚠️  {var} 叶子 {leaf} 在.debug_pubnames中")
                else:
                    print(f"  ❌ {var} 未找到")

        # 统计包含点号的符号
        print(f"\n统计.debug_pubnames中的符号:")

        # 查找所有以点号分隔的符号（简单方式）
        # .debug_pubnames是二进制格式，但符号名以null结尾
        names = []
        current_name = b''
        for byte in data:
            if byte == 0:
                if current_name:
                    names.append(current_name.decode('utf-8', errors='ignore'))
                    current_name = b''
            elif 32 <= byte < 127:  # 可打印ASCII
                current_name += bytes([byte])

        print(f"  总符号数: {len(names)}")

        # 去重
        unique_names = list(set(names))
        print(f"  唯一符号数: {len(unique_names)}")

        # 统计带点号的符号
        dot_names = [n for n in unique_names if '.' in n]
        print(f"  带点号的符号: {len(dot_names)}")

        if dot_names:
            print(f"\n带点号符号示例:")
            for name in dot_names[:20]:
                print(f"  - {name}")

    else:
        print("未找到.debug_pubnames section")

print("\n" + "="*70)
