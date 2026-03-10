#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证工具输出和手动处理对于当前ELF的正确性."""

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
tool_output = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_tool_output.a2l")
manual_file = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_Mana.a2l")

print("="*70)
print("验证两种输出对于当前ELF的正确性")
print("="*70)

# 获取ELF符号
elf_parser = ELFParser()
symbols = elf_parser.extract_symbols(elf_path)
print(f"当前ELF符号数: {len(symbols)}")

# 解析A2L文件
a2l_parser = A2LParser()

print("\n解析工具输出...")
tool_vars = a2l_parser.parse(tool_output)

print("\n解析手动处理...")
manual_vars = a2l_parser.parse(manual_file)

# 验证工具输出
print("\n" + "="*70)
print("工具输出验证:")
print("="*70)

tool_correct = 0
tool_incorrect = 0
tool_errors = []

for var_name, var_info in tool_vars.items():
    if var_info.address != 0:
        expected = None
        if var_name in symbols:
            expected = symbols[var_name]
        elif "." in var_name:
            leaf = var_name.split(".")[-1]
            if leaf in symbols:
                expected = symbols[leaf]

        if expected and var_info.address == expected:
            tool_correct += 1
        else:
            tool_incorrect += 1
            if len(tool_errors) < 10:
                tool_errors.append((var_name, var_info.address, expected))

print(f"  ✅ 正确: {tool_correct} 个")
print(f"  ❌ 错误: {tool_incorrect} 个")
print(f"  准确率: {tool_correct/(tool_correct+tool_incorrect)*100:.2f}%" if tool_correct+tool_incorrect > 0 else "  无数据")

if tool_errors:
    print(f"\n  错误示例:")
    for var, actual, expected in tool_errors:
        print(f"    {var}: 工具=0x{actual:08X}, ELF=0x{expected:08X if expected else None}")

# 验证手动处理
print("\n" + "="*70)
print("手动处理验证:")
print("="*70)

manual_correct = 0
manual_incorrect = 0
manual_errors = []

for var_name, var_info in manual_vars.items():
    if var_info.address != 0:
        expected = None
        if var_name in symbols:
            expected = symbols[var_name]
        elif "." in var_name:
            leaf = var_name.split(".")[-1]
            if leaf in symbols:
                expected = symbols[leaf]

        if expected and var_info.address == expected:
            manual_correct += 1
        else:
            manual_incorrect += 1
            if len(manual_errors) < 10:
                manual_errors.append((var_name, var_info.address, expected))

print(f"  ✅ 正确: {manual_correct} 个")
print(f"  ❌ 错误: {manual_incorrect} 个")
print(f"  准确率: {manual_correct/(manual_correct+manual_incorrect)*100:.2f}%" if manual_correct+manual_incorrect > 0 else "  无数据")

if manual_errors:
    print(f"\n  错误示例:")
    for var, actual, expected in manual_errors:
        elf_str = f"0x{expected:08X}" if expected else "None"
        print(f"    {var}: 手动=0x{actual:08X}, ELF={elf_str}")

# 统计手动处理独有的变量
manual_only_vars = []
for var_name, var_info in manual_vars.items():
    if var_info.address != 0:
        found = False
        if var_name in symbols:
            found = True
        elif "." in var_name:
            leaf = var_name.split(".")[-1]
            if leaf in symbols:
                found = True
        if not found:
            manual_only_vars.append((var_name, var_info.address))

print(f"\n手动处理独有的变量(当前ELF中找不到): {len(manual_only_vars)}")
if manual_only_vars:
    print(f"  示例:")
    for var, addr in manual_only_vars[:20]:
        print(f"    {var}: 0x{addr:08X}")

print("\n" + "="*70)
print("总结:")
print("="*70)
print(f"工具输出对于当前ELF: {tool_correct/(tool_correct+tool_incorrect)*100:.1f}% 正确" if tool_correct+tool_incorrect > 0 else "工具输出: 无数据")
print(f"手动处理对于当前ELF: {manual_correct/(manual_correct+manual_incorrect)*100:.1f}% 正确" if manual_correct+manual_incorrect > 0 else "手动处理: 无数据")
print()
print("结论: ", end="")
if tool_correct/(tool_correct+tool_incorrect) > manual_correct/(manual_correct+manual_incorrect):
    print("工具输出对于当前ELF更准确。")
elif manual_correct > 0 and manual_incorrect > 0:
    ratio = manual_correct/(manual_correct+manual_incorrect)
    if ratio < 0.6:
        print("手动处理可能使用了不同的ELF文件或DWARF调试信息。")
    else:
        print(f"两者都基于当前ELF，但手动处理额外更新了{len(manual_only_vars)}个当前ELF中不存在的变量。")
else:
    print("无法比较。")
