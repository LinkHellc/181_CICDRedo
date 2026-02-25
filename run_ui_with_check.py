#!/usr/bin/env python3
"""
MBD_CICDKits 启动器（带环境检查）

在启动主程序前检查必要的环境依赖：
- PyQt6
- psutil（可选）

注意：MATLAB Engine 检测已移除（ADR-005）
MATLAB 代码生成功能已改为预留接口，不再需要 MATLAB Engine API。
"""

import sys
import subprocess
from pathlib import Path


def check_pyqt6() -> bool:
    """检查 PyQt6 是否可用"""
    try:
        from PyQt6.QtWidgets import QApplication
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

    # 检查 PyQt6（必需）
    print("[1/2] 检查 PyQt6...")
    if check_pyqt6():
        print("      [OK] PyQt6 可用")
    else:
        print("      [FAIL] PyQt6 未安装")
        errors.append({
            "title": "PyQt6 未安装",
            "message": "未检测到 PyQt6。\n\n本程序需要 PyQt6 才能正常运行。",
            "details": """安装方法：

  pip install PyQt6

或使用 requirements.txt 安装所有依赖：
  pip install -r requirements.txt"""
        })

    # 检查 psutil（可选）
    print("[2/2] 检查 psutil...")
    if check_psutil():
        print("      [OK] psutil 可用")
    else:
        print("      [WARN] psutil 未安装（可选，进程检测功能受限）")

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
