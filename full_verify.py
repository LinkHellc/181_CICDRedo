#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全面验证工具输出和手动处理的地址匹配情况."""

import sys
import io
import re
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 文件路径
tool_file = Path(r'D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_test_output.a2l')
mana_file = Path(r'D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_Mana.a2l')

# 提取地址的正则
addr_pattern = re.compile(r'(?:ECU_ADDRESS|/\*\s*ECU\s+Address\s*\*/)\s+(0x[0-9A-Fa-f]+)')

def extract_addresses(file_path):
    """从A2L文件中提取变量地址"""
    addresses = {}
    content = file_path.read_text(encoding='utf-8')
    lines = content.splitlines()

    for i, line in enumerate(lines):
        # 查找变量名（在地址行之前）
        if '/* Name */' in line or '/* Name                   */' in line:
            var_match = re.search(r'Name\s*\*/\s*(\S+)', line)
            if var_match:
                var_name = var_match.group(1)
                # 在接下来几行查找地址
                for j in range(i, min(i+20, len(lines))):
                    addr_match = addr_pattern.search(lines[j])
                    if addr_match:
                        addresses[var_name] = addr_match.group(1)
                        break

    return addresses

print("全面验证地址匹配情况...")
print("="*80)

tool_addrs = extract_addresses(tool_file)
mana_addrs = extract_addresses(mana_file)

print(f"工具输出变量数: {len(tool_addrs)}")
print(f"手动处理变量数: {len(mana_addrs)}")

# 找出所有共同变量
common_vars = set(tool_addrs.keys()) & set(mana_addrs.keys())
print(f"共同变量数: {len(common_vars)}")

# 统计匹配情况
matched = 0
mismatched = 0
mismatches = []

for var in common_vars:
    if tool_addrs[var] == mana_addrs[var]:
        matched += 1
    else:
        mismatched += 1
        mismatches.append((var, tool_addrs[var], mana_addrs[var]))

print(f"\n匹配统计:")
print(f"  ✅ 匹配: {matched} 个")
print(f"  ❌ 不匹配: {mismatched} 个")
print(f"  匹配率: {matched/len(common_vars)*100:.2f}%")

if mismatches:
    print(f"\n不匹配的变量 (最多显示20个):")
    for var, t, m in mismatches[:20]:
        print(f"  {var}")
        print(f"    工具: {t}, 手动: {m}")
else:
    print("\n✅ 所有共同变量地址完全匹配!")

# 检查只在某个文件中存在的变量
only_in_tool = set(tool_addrs.keys()) - set(mana_addrs.keys())
only_in_mana = set(mana_addrs.keys()) - set(tool_addrs.keys())

if only_in_tool:
    print(f"\n只在工具输出中: {len(only_in_tool)} 个")
if only_in_mana:
    print(f"\n只在手动处理中: {len(only_in_mana)} 个")

print("\n" + "="*80)
print("验证完成!")
