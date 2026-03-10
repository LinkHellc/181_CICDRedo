#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check if specific symbols exist in ELF."""

import sys
import io
from pathlib import Path
from elftools.elf.elffile import ELFFile

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser

def check_symbols():
    """检查特定符号是否在ELF中"""
    elf_path = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"

    parser = ELFParser()
    symbols = parser.extract_symbols(Path(elf_path))

    test_vars = [
        "HV_PTC_Emg_Off_Rq",
        "Lo_Temp",
        "cCbnEMA_DuctAirFlowRateVent_x",
        "TwmCtrl_tHeaterClntTrgtMax"
    ]

    print(f"ELF中总共有 {len(symbols)} 个符号\n")
    print("检查特定符号:")
    for var in test_vars:
        addr = symbols.get(var)
        if addr:
            print(f"  ✅ {var:40s} -> 0x{addr:08X}")
        else:
            print(f"  ❌ {var:40s} 未找到")

            # 尝试模糊搜索
            matches = [s for s in symbols.keys() if var.lower() in s.lower()]
            if matches:
                print(f"     相似匹配:")
                for m in matches[:5]:
                    print(f"       - {m} -> 0x{symbols[m]:08X}")

if __name__ == "__main__":
    check_symbols()
