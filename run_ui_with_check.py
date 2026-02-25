#!/usr/bin/env python3
"""
MBD_CICDKits 启动器（带环境检查）

在启动主程序前检查必要的环境依赖：
- MATLAB Engine for Python
- psutil（可选）
"""

import sys
import subprocess
from pathlib import Path


def check_matlab_engine() -> bool:
    """检查 MATLAB Engine 是否可用"""
    try:
        import matlab.engine
        return True
    except ImportError:
        return False


def check_psutil() -> bool:
    """检查 psutil 是否可用"""
    try:
        import psutil
        return True
    except ImportError:
        return False


def show_error_dialog(title: str, message: str, details: str = ""):
    """显示错误对话框"""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        if details:
            msg.setDetailedText(details)
        msg.exec()
    except Exception:
        # 如果 PyQt6 不可用，使用控制台输出
        print(f"\n{'='*60}")
        print(f"错误: {title}")
        print(f"{'='*60}")
        print(message)
        if details:
            print(f"\n详细信息:\n{details}")
        print(f"{'='*60}\n")
        input("按回车键退出...")


def main():
    """主函数"""
    print("MBD_CICDKits 环境检查...")
    print("-" * 40)

    errors = []

    # 检查 MATLAB Engine
    print("[1/2] 检查 MATLAB Engine for Python...")
    if check_matlab_engine():
        print("      ✓ MATLAB Engine 可用")
    else:
        print("      ✗ MATLAB Engine 未安装")
        errors.append({
            "title": "MATLAB Engine 未安装",
            "message": "未检测到 MATLAB Engine for Python。\n\n本程序需要 MATLAB Engine 才能正常运行。",
            "details": """安装方法：

方法一（在 MATLAB 中执行）：
  cd(fullfile(matlabroot, 'extern', 'engines', 'python'))
  system('python setup.py install')

方法二（命令行）：
  cd "MATLAB安装路径\\extern\\engines\\python"
  python setup.py install

详细说明请查看：docs/MATLAB_ENGINE_安装指南.md"""
        })

    # 检查 psutil（可选）
    print("[2/2] 检查 psutil...")
    if check_psutil():
        print("      ✓ psutil 可用")
    else:
        print("      ⚠ psutil 未安装（可选，部分功能受限）")

    print("-" * 40)

    # 如果有错误，显示对话框并退出
    if errors:
        error = errors[0]
        show_error_dialog(error["title"], error["message"], error["details"])
        return 1

    print("环境检查通过，启动主程序...\n")

    # 启动主程序
    from PyQt6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)

    # 解析主题参数
    theme = "dark"
    if "--light" in sys.argv:
        theme = "light"

    window = MainWindow(theme=theme)
    window.show()

    print(f"MBD_CICDKits 启动 (主题: {theme})")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
