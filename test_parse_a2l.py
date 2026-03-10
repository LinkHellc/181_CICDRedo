#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test A2L parser to see if it extracts all variables."""

import sys
import io
from pathlib import Path

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.a2l_parser import A2LParser

def test_a2l_parser():
    """测试A2L解析器"""
    a2l_file = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\TmsApp.a2l"

    parser = A2LParser()
    variables = parser.parse(Path(a2l_file))

    print(f"总共解析了 {len(variables)} 个变量")

    # 查找特定的未匹配变量
    test_vars = [
        "cCbnEMA_DuctAirFlowRateVent_x",
        "cCbnBlw_BlowerAirFlow2Level_Front_x",
        "ctCbnTemp_SecLeDVTEpsKi_y",
        "Lo_Temp"  # 这个应该能匹配
    ]

    print("\n查找特定变量:")
    for var_name in test_vars:
        var = parser.get_variable(var_name)
        if var:
            print(f"  ✅ {var_name}: 地址=0x{var.address:08X}, 行={var.address_line}")
        else:
            print(f"  ❌ {var_name}: 未找到")

    # 查找所有带 _x 和 _y 后缀的变量
    x_vars = [v for v in variables.keys() if v.endswith('_x')]
    y_vars = [v for v in variables.keys() if v.endswith('_y')]

    print(f"\n带 _x 后缀的变量: {len(x_vars)}")
    print(f"带 _y 后缀的变量: {len(y_vars)}")

    if x_vars:
        print("示例 _x 变量:")
        for v in x_vars[:10]:
            print(f"  {v}")

if __name__ == "__main__":
    test_a2l_parser()
