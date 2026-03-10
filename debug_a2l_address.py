#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug script to analyze ELF symbol tables and A2L matching."""

import sys
import io
from pathlib import Path
from elftools.elf.elffile import ELFFile

# 设置 stdout 编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from a2l.elf_parser import ELFParser
from a2l.a2l_parser import A2LParser

def diagnose_elf_symbols(elf_path: str):
    """诊断 ELF 符号"""
    print(f"\n{'='*60}")
    print(f"诊断 ELF 文件: {elf_path}")
    print(f"{'='*60}")

    parser = ELFParser()
    try:
        symbols = parser.extract_symbols(Path(elf_path))
        print(f"✅ 成功提取 {len(symbols)} 个符号")
        print(f"   过滤掉 {parser.get_filtered_count()} 个符号")

        if symbols:
            # 显示前 20 个符号
            print(f"\n前 20 个符号:")
            for i, (name, addr) in enumerate(list(symbols.items())[:20]):
                print(f"   {name:40s} -> 0x{addr:08X}")

            # 检查特定符号
            test_names = ["Lo_Temp", "cCAN_ACExv_FltSt_0x45D_OvrdFlg"]
            print(f"\n检查特定符号:")
            for name in test_names:
                addr = symbols.get(name)
                if addr:
                    print(f"   ✅ {name} -> 0x{addr:08X}")
                else:
                    print(f"   ❌ {name} 未找到")
        else:
            print("⚠️  没有找到任何符号!")

    except Exception as e:
        print(f"❌ 错误: {e}")

def diagnose_a2l_parsing(a2l_path: str):
    """诊断 A2L 解析"""
    print(f"\n{'='*60}")
    print(f"诊断 A2L 文件: {a2l_path}")
    print(f"{'='*60}")

    parser = A2LParser()
    try:
        variables = parser.parse(Path(a2l_path))
        print(f"✅ 成功解析 {len(variables)} 个变量")

        if variables:
            # 显示前 20 个变量
            print(f"\n前 20 个变量:")
            for i, (name, var) in enumerate(list(variables.items())[:20]):
                addr_marker = "✅" if var.address != 0 else "❌"
                print(f"   {addr_marker} {name:40s} -> 0x{var.address:08X} (行 {var.address_line})")

            # 统计地址为 0 的变量
            zero_addr_vars = [name for name, var in variables.items() if var.address == 0]
            print(f"\n📊 统计:")
            print(f"   总变量数: {len(variables)}")
            print(f"   地址为 0x0: {len(zero_addr_vars)}")
            print(f"   地址非 0: {len(variables) - len(zero_addr_vars)}")

            if zero_addr_vars:
                print(f"\n前 10 个地址为 0x0 的变量:")
                for name in zero_addr_vars[:10]:
                    var = variables[name]
                    print(f"   {name:40s} -> 0x{var.address:08X} (行 {var.address_line})")
        else:
            print("⚠️  没有找到任何变量!")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def diagnose_matching(elf_path: str, a2l_path: str):
    """诊断匹配情况"""
    print(f"\n{'='*60}")
    print(f"诊断 ELF 和 A2L 匹配情况")
    print(f"{'='*60}")

    elf_parser = ELFParser()
    a2l_parser = A2LParser()

    try:
        symbols = elf_parser.extract_symbols(Path(elf_path))
        variables = a2l_parser.parse(Path(a2l_path))

        matched = []
        unmatched = []

        for var_name in variables:
            if var_name in symbols:
                matched.append(var_name)
            else:
                unmatched.append(var_name)

        print(f"✅ 匹配成功: {len(matched)}/{len(variables)} 个变量")
        print(f"❌ 未匹配: {len(unmatched)}/{len(variables)} 个变量")

        if unmatched:
            print(f"\n未匹配的变量 (前 20 个):")
            for name in unmatched[:20]:
                var = variables[name]
                print(f"   {name:40s} (地址: 0x{var.address:08X})")

    except Exception as e:
        print(f"❌ 错误: {e}")

def check_symbol_tables(elf_path: str, a2l_output: str):
    """检查ELF符号表和未匹配变量"""
    print(f"\n{'='*60}")
    print("检查ELF符号表和未匹配变量")
    print(f"{'='*60}")

    elf_path = Path(elf_path)
    a2l_output = Path(a2l_output)

    # Extract unmatched variables from A2L
    unmatched_vars = set()
    with open(a2l_output, 'r', encoding='utf-8') as f:
        for line in f:
            if 'ECU Address' in line and '0x0000' in line:
                # Extract variable name from comment
                if '@ECU_Address@' in line:
                    var_name = line.split('@ECU_Address@')[1].split('@')[0]
                    unmatched_vars.add(var_name)

    print(f"在A2L中找到 {len(unmatched_vars)} 个未匹配变量")
    print("示例未匹配变量:")
    for var in sorted(unmatched_vars)[:10]:
        print(f"  - {var}")

    # Check what symbol tables exist in ELF
    with open(elf_path, 'rb') as f:
        elf = ELFFile(f)

        print("\n=== ELF 符号表 ===")
        for section in elf.iter_sections():
            if section.header.sh_type in ['SHT_SYMTAB', 'SHT_DYNSYM']:
                print(f"\nSection: {section.name}")
                print(f"  Type: {section.header.sh_type}")
                print(f"  Size: {section.header.sh_size} bytes")

                # Count symbols
                num_symbols = 0
                sample_symbols = []
                for symbol in section.iter_symbols():
                    if symbol.name and symbol['st_value'] > 0:
                        num_symbols += 1
                        if len(sample_symbols) < 5:
                            sample_symbols.append(symbol.name)

                print(f"  有效符号数: {num_symbols}")
                print(f"  示例符号: {sample_symbols}")

    # Check if unmatched vars are in .dynsym
    print("\n=== 在.dynsym中检查未匹配变量 ===")
    with open(elf_path, 'rb') as f:
        elf = ELFFile(f)
        dynsym = elf.get_section_by_name('.dynsym')

        if dynsym:
            # Build symbol map
            dynsym_symbols = {}
            for symbol in dynsym.iter_symbols():
                if symbol.name and symbol['st_value'] > 0:
                    dynsym_symbols[symbol.name] = symbol['st_value']

            print(f".dynsym 有 {len(dynsym_symbols)} 个符号")

            # Check unmatched variables
            found_in_dynsym = []
            for var in unmatched_vars:
                if var in dynsym_symbols:
                    found_in_dynsym.append((var, f"0x{dynsym_symbols[var]:08X}"))

            if found_in_dynsym:
                print(f"\n在.dynsym中找到 {len(found_in_dynsym)} 个未匹配变量:")
                for var, addr in found_in_dynsym[:10]:
                    print(f"  {var} -> {addr}")
            else:
                print("\n在.dynsym中未找到未匹配变量")
        else:
            print("ELF中没有.dynsym section")

    # Check .symtab too
    print("\n=== 在.symtab中检查未匹配变量 ===")
    with open(elf_path, 'rb') as f:
        elf = ELFFile(f)
        symtab = elf.get_section_by_name('.symtab')

        if symtab:
            symtab_symbols = {}
            for symbol in symtab.iter_symbols():
                if symbol.name and symbol['st_value'] > 0:
                    symtab_symbols[symbol.name] = symbol['st_value']

            print(f".symtab 有 {len(symtab_symbols)} 个符号")

            # Check unmatched variables
            found_in_symtab = []
            for var in unmatched_vars:
                if var in symtab_symbols:
                    found_in_symtab.append((var, f"0x{symtab_symbols[var]:08X}"))

            if found_in_symtab:
                print(f"\n在.symtab中找到 {len(found_in_symtab)} 个未匹配变量:")
                for var, addr in found_in_symtab[:10]:
                    print(f"  {var} -> {addr}")
            else:
                print("\n在.symtab中未找到未匹配变量 (已确认!)")
        else:
            print("ELF中没有.symtab section")

    # Compare symbol tables
    print("\n=== 比较.symtab和.dynsym ===")
    with open(elf_path, 'rb') as f:
        elf = ELFFile(f)
        symtab = elf.get_section_by_name('.symtab')
        dynsym = elf.get_section_by_name('.dynsym')

        if symtab and dynsym:
            symtab_set = set()
            dynsym_set = set()

            for symbol in symtab.iter_symbols():
                if symbol.name and symbol['st_value'] > 0:
                    symtab_set.add(symbol.name)

            for symbol in dynsym.iter_symbols():
                if symbol.name and symbol['st_value'] > 0:
                    dynsym_set.add(symbol.name)

            only_in_dynsym = dynsym_set - symtab_set
            only_in_symtab = symtab_set - dynsym_set

            print(f"仅在.dynsym中的符号: {len(only_in_dynsym)}")
            print(f"仅在.symtab中的符号: {len(only_in_symtab)}")
            print(f"公共符号: {len(symtab_set & dynsym_set)}")

            # Check if unmatched vars are in only_in_dynsym
            overlap = unmatched_vars & only_in_dynsym
            if overlap:
                print(f"\n*** 关键发现: {len(overlap)} 个未匹配变量仅在.dynsym中! ***")
                print("示例:", sorted(overlap)[:5])


if __name__ == "__main__":
    # 使用实际文件路径
    elf_file = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\CYT4BF_M7_Master.elf"
    a2l_output = r"D:\BaiduSyncdisk\4-学习\100-项目\181_CICDRedo\00_用户输入需求与材料\MBD_CICD_Obj_2026_03_04_16_08\tmsAPP_upAdress_2026_03_04_22_01.a2l"

    import argparse
    parser_args = argparse.ArgumentParser(description="诊断A2L地址更新问题")
    parser_args.add_argument("--elf", default=elf_file, help="ELF文件路径")
    parser_args.add_argument("--a2l", default=a2l_output, help="A2L输出文件路径")
    args = parser_args.parse_args()

    print("="*60)
    print("A2L地址更新诊断工具 - 符号表分析")
    print("="*60)

    # 检查符号表
    check_symbol_tables(args.elf, args.a2l)
