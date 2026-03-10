#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用原始文件执行最终的A2L地址更新."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.address_updater import A2LAddressUpdater

# 使用原始文件
elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")
a2l_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp.a2l")
# 输出到新文件，便于对比
output_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_tool_output.a2l")
# 手动处理文件（用于对比）
manual_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_Mana.a2l")

print("="*70)
print("A2L地址更新 - 使用修复后的代码")
print("="*70)
print(f"ELF文件: {elf_path.name}")
print(f"A2L输入: {a2l_path.name}")
print(f"A2L输出: {output_path.name}")
print(f"手动处理: {manual_path.name}")
print("="*70)

updater = A2LAddressUpdater()

def log_callback(msg):
    print(f"[{msg}]")

updater.set_log_callback(log_callback)

result = updater.update(elf_path, a2l_path, output_path, backup=False)

print("\n" + "="*70)
print("更新完成")
print("="*70)
print(f"成功: {result.success}")
print(f"消息: {result.message}")
print(f"匹配变量: {result.matched_count} / {result.total_variables}")
print(f"未匹配变量: {result.unmatched_count}")
print(f"输出文件: {result.output_path}")

# 验证输出文件
if result.success and output_path.exists():
    print(f"\n输出文件大小: {output_path.stat().st_size} 字节")
