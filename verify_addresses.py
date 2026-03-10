#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify addresses match between tool output and manual processing."""

import sys
import io
import re
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取工具输出和手动处理文件
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

print("提取变量地址...")
tool_addrs = extract_addresses(tool_file)
mana_addrs = extract_addresses(mana_file)

print(f"工具输出: {len(tool_addrs)} 个变量")
print(f"手动处理: {len(mana_addrs)} 个变量")

# 对比特定变量
test_vars = ['HV_PTC_Emg_Off_Rq', 'Lo_Temp', 'cCbnEMA_DuctAirFlowRateVent_x',
            'TwmCtrl_tHeaterClntTrgtMax', 'cCbnBlw_BlowerAirFlow2Level_Front_x']

print("\n" + "="*80)
print("变量地址对比:")
print("="*80)
print(f"{'变量名':45s} {'工具输出':12s} {'手动处理':12s} {'匹配':6s}")
print("="*80)

all_match = True
mismatches = []
for var in test_vars:
    tool_addr = tool_addrs.get(var, '未找到')
    mana_addr = mana_addrs.get(var, '未找到')
    match = '✅' if tool_addr == mana_addr else '❌'
    if match == '❌':
        all_match = False
        mismatches.append((var, tool_addr, mana_addr))
    print(f'{var:45s} {tool_addr:12s} {mana_addr:12s} {match:6s}')

print("="*80)
if all_match:
    print("✅ 全部匹配!")
else:
    print(f"❌ 存在 {len(mismatches)} 个差异:")
    for var, t, m in mismatches:
        print(f"   {var}: 工具={t}, 手动={m}")
