#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证工具输出基于当前ELF的正确性."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser
from a2l.a2l_parser import A2LParser

def verify():
    """验证工具输出"""
    elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")
    tool_output = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_tool_output.a2l")

    elf_parser = ELFParser()
    a2l_parser = A2LParser()

    print("提取ELF符号...")
    symbols = elf_parser.extract_symbols(elf_path)

    print("解析工具输出...")
    a2l_vars = a2l_parser.parse(tool_output)

    print(f"\nELF符号数: {len(symbols)}")
    print(f"工具输出变量数: {len(a2l_vars)}")

    # 验证所有非零地址的变量
    correct = 0
    incorrect = 0
    errors = []

    for var_name, var_info in a2l_vars.items():
        if var_info.address != 0:
            expected = None
            match_type = None

            if var_name in symbols:
                expected = symbols[var_name]
                match_type = "exact"
            elif "." in var_name:
                leaf = var_name.split(".")[-1]
                if leaf in symbols:
                    expected = symbols[leaf]
                    match_type = "leaf"

            if expected and var_info.address == expected:
                correct += 1
            else:
                incorrect += 1
                if len(errors) < 10:
                    errors.append((var_name, var_info.address, expected, match_type))

    print(f"\n验证结果:")
    print(f"  ✅ 正确: {correct} 个")
    print(f"  ❌ 错误: {incorrect} 个")
    print(f"  准确率: {correct / (correct + incorrect) * 100:.2f}%")

    if errors:
        print(f"\n错误示例:")
        for var, actual, expected, mt in errors:
            print(f"  {var}")
            print(f"    工具: 0x{actual:08X}, ELF期望: 0x{expected:08X if expected else None}")

    # 检查手动处理独有的变量
    print("\n检查手动处理独有的1730个变量...")
    import re

    manual_file = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_Mana.a2l")
    addr_pattern = re.compile(r'(?:ECU_ADDRESS|/\*\s*ECU\s+Address\s*\*/)\s+(0x[0-9A-Fa-f]+)')

    manual_addrs = {}
    content = manual_file.read_text(encoding='utf-8')
    lines = content.splitlines()

    for i, line in enumerate(lines):
        if '/* Name */' in line or '/* Name                   */' in line:
            var_match = re.search(r'Name\s*\*/\s*(\S+)', line)
            if var_match:
                var_name = var_match.group(1)
                for j in range(i, min(i+20, len(lines))):
                    addr_match = addr_pattern.search(lines[j])
                    if addr_match:
                        addr_str = addr_match.group(1)
                        if addr_str != '0x0000':
                            manual_addrs[var_name] = addr_str
                        break

    # 检查这些手动独有的变量在当前ELF中是否存在
    manual_only_vars = set(manual_addrs.keys()) - set(a2l_vars.keys())
    # 实际上需要比较哪些在手动中更新但工具中没更新的
    tool_updated = set(v for v, a in a2l_vars.items() if a.address != 0)

    print(f"手动更新数: {len(manual_addrs)}")
    print(f"工具更新数: {len(tool_updated)}")

    # 取几个手动独有的变量检查
    sample_vars = list(set(manual_addrs.keys()) - tool_updated)[:5]
    print(f"\n检查手动独有的变量是否在当前ELF中:")
    for var in sample_vars:
        if var in symbols:
            print(f"  ✅ {var} -> 0x{symbols[var]:08X}")
        elif "." in var:
            leaf = var.split(".")[-1]
            if leaf in symbols:
                print(f"  ✅ {var} (叶子: {leaf}) -> 0x{symbols[leaf]:08X}")
            else:
                print(f"  ❌ {var} (叶子: {leaf}) 未在ELF中找到")
        else:
            print(f"  ❌ {var} 未在ELF中找到")

if __name__ == "__main__":
    verify()
