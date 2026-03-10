#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test full A2L address update with detailed logging."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.address_updater import A2LAddressUpdater

def test_update():
    """测试完整的地址更新"""
    elf_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf")
    a2l_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp.a2l")
    output_path = Path(r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp_test_output.a2l")

    updater = A2LAddressUpdater()

    # 设置日志回调以显示详细信息
    def log_callback(msg):
        print(f"[LOG] {msg}")

    updater.set_log_callback(log_callback)

    print("="*60)
    print("执行A2L地址更新")
    print("="*60)

    result = updater.update(elf_path, a2l_path, output_path, backup=False)

    print("\n"+"="*60)
    print("更新结果")
    print("="*60)
    print(f"成功: {result.success}")
    print(f"消息: {result.message}")
    print(f"总变量数: {result.total_variables}")
    print(f"总符号数: {result.total_symbols}")
    print(f"匹配数: {result.matched_count}")
    print(f"未匹配数: {result.unmatched_count}")

    # 检查特定变量
    test_vars = ["HV_PTC_Emg_Off_Rq", "Lo_Temp", "cCbnEMA_DuctAirFlowRateVent_x"]
    print("\n检查特定变量:")
    for var in test_vars:
        if var in result.updated_variables:
            print(f"  ✅ {var} 已更新")
        else:
            print(f"  ❌ {var} 未更新")

    # 显示部分未匹配变量
    if result.unmatched_variables:
        print(f"\n前20个未匹配变量:")
        for var in result.unmatched_variables[:20]:
            print(f"  - {var}")

if __name__ == "__main__":
    test_update()
