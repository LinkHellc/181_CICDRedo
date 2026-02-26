#!/usr/bin/env python3
"""测试 A2L 工具路径显示修复

测试场景：
1. 创建包含所有路径（包括 a2l_tool_path）的项目配置
2. 保存配置
3. 加载配置
4. 验证所有路径（包括 a2l_tool_path）是否正确显示
"""

import sys
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.models import ProjectConfig
from core.config import save_config, load_config, delete_config
from ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication


def test_a2l_tool_path_display():
    """测试 A2L 工具路径显示"""
    print("=" * 60)
    print("测试 A2L 工具路径显示修复")
    print("=" * 60)

    # 创建测试配置
    test_config = ProjectConfig(
        name="测试项目_A2L路径显示",
        description="测试 A2L 工具路径显示功能",
        simulink_path="E:/test/simulink_project",
        matlab_code_path="E:/test/matlab_code",
        a2l_path="E:/test/test.a2l",
        target_path="E:/test/output",
        iar_project_path="E:/test/project.eww",
        iar_tool_path="C:/IAR/build/tools/IarBuild.exe",
        a2l_tool_path="E:/test/a2l_tools"  # 这是新增的测试字段
    )

    print("\n1. 创建测试配置:")
    print(f"   项目名称: {test_config.name}")
    print(f"   A2L 文件路径: {test_config.a2l_path}")
    print(f"   A2L 工具路径: {test_config.a2l_tool_path}")

    # 保存配置
    print("\n2. 保存配置...")
    success = save_config(test_config, test_config.name, overwrite=True)
    if not success:
        print("   [失败] 保存配置失败")
        return False
    print("   [成功] 配置保存成功")

    # 加载配置
    print("\n3. 加载配置...")
    try:
        loaded_config = load_config(test_config.name)
        print("   [成功] 配置加载成功")
    except Exception as e:
        print(f"   [失败] 配置加载失败: {e}")
        return False

    # 验证所有路径字段
    print("\n4. 验证路径字段:")

    all_paths = {
        "simulink_path": "Simulink 工程",
        "matlab_code_path": "IAR-MATLAB 代码",
        "a2l_path": "A2L 文件",
        "target_path": "目标文件夹",
        "iar_project_path": "IAR 工程",
        "iar_tool_path": "IAR 工具",
        "a2l_tool_path": "A2L 工具"
    }

    all_correct = True
    for field_key, field_name in all_paths.items():
        expected_value = getattr(test_config, field_key, "")
        loaded_value = getattr(loaded_config, field_key, "")
        is_correct = expected_value == loaded_value

        status = "[OK]" if is_correct else "[FAIL]"
        print(f"   {status} {field_name:20s}: {loaded_value}")

        if not is_correct:
            print(f"      预期: {expected_value}")
            all_correct = False

    # 特别检查 a2l_tool_path
    print("\n5. 重点检查 A2L 工具路径:")
    if loaded_config.a2l_tool_path == test_config.a2l_tool_path:
        print(f"   [成功] A2L 工具路径正确: {loaded_config.a2l_tool_path}")
    else:
        print(f"   [失败] A2L 工具路径错误:")
        print(f"      预期: {test_config.a2l_tool_path}")
        print(f"      实际: {loaded_config.a2l_tool_path}")
        all_correct = False

    # 清理测试配置
    print("\n6. 清理测试配置...")
    delete_config(test_config.name)
    print("   [成功] 测试配置已删除")

    print("\n" + "=" * 60)
    if all_correct:
        print("测试结果: [成功] 所有路径字段正确显示")
        print("=" * 60)
        return True
    else:
        print("测试结果: [失败] 部分路径字段显示错误")
        print("=" * 60)
        return False


def test_ui_path_labels():
    """测试 UI 中的 path_labels 字典"""
    print("\n" + "=" * 60)
    print("测试 UI 中的 path_labels 字典")
    print("=" * 60)

    app = QApplication(sys.argv)
    window = MainWindow()

    print("\n1. 检查 path_labels 字典:")
    expected_keys = [
        "simulink_path",
        "matlab_code_path",
        "a2l_path",
        "target_path",
        "iar_project_path",
        "iar_tool_path",
        "a2l_tool_path"
    ]

    all_exist = True
    for key in expected_keys:
        exists = key in window.path_labels
        status = "[OK]" if exists else "[FAIL]"
        print(f"   {status} {key:20s}: {'存在' if exists else '缺失'}")
        if not exists:
            all_exist = False

    print("\n" + "=" * 60)
    if all_exist:
        print("测试结果: [成功] 所有 path_labels 都存在")
        print("=" * 60)
        return True
    else:
        print("测试结果: [失败] 部分 path_labels 缺失")
        print("=" * 60)
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("A2L 工具路径显示修复测试")
    print("=" * 60 + "\n")

    # 测试 1: 配置加载测试
    test1_passed = test_a2l_tool_path_display()

    # 测试 2: UI 字典测试
    test2_passed = test_ui_path_labels()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"测试 1 (配置加载): {'[通过]' if test1_passed else '[失败]'}")
    print(f"测试 2 (UI 字典):  {'[通过]' if test2_passed else '[失败]'}")

    if test1_passed and test2_passed:
        print("\n[成功] 所有测试通过！A2L 工具路径显示修复成功！")
        sys.exit(0)
    else:
        print("\n[错误] 部分测试失败！需要进一步检查！")
        sys.exit(1)
