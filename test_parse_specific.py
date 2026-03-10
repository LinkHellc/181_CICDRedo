#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test if A2L parser can extract specific variables."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.a2l_parser import A2LParser

def test_parser():
    """测试A2L解析器"""
    a2l_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp.a2l"

    parser = A2LParser()
    variables = parser.parse(Path(a2l_path))

    test_vars = [
        "HV_PTC_Emg_Off_Rq",
        "Lo_Temp",
        "cCbnEMA_DuctAirFlowRateVent_x",
        "CbnBlw_B.Out",
        "ctCbnTemp_SecLeDVTEpsKi_y"
    ]

    print(f"A2L解析器提取了 {len(variables)} 个变量\n")
    print("检查特定变量:")
    for var in test_vars:
        v = parser.get_variable(var)
        if v:
            print(f"  ✅ {var}")
            print(f"     类型: {v.var_type}, 地址: 0x{v.address:08X}, 行: {v.address_line}")
        else:
            print(f"  ❌ {var} 未被解析器提取")

if __name__ == "__main__":
    test_parser()
