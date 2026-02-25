#!/usr/bin/env python3
"""MBD_CICDKits UI 启动入口

支持主题选择：
- 默认深色主题（工业精密风格）
- 可通过命令行参数切换到浅色主题

使用方法：
    python run_ui.py          # 默认深色主题
    python run_ui.py --light  # 浅色主题
    python run_ui.py --dark   # 深色主题
"""

import sys
import traceback
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def exception_hook(exc_type, exc_value, exc_tb):
    """全局异常处理器 - 防止未捕获的异常导致应用崩溃"""
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"\n未捕获的异常:\n{error_msg}")

    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        # 确保有 QApplication 实例
        app = QApplication.instance()
        if app:
            QMessageBox.critical(
                None,
                "程序错误",
                f"发生未预期的错误:\n\n{str(exc_value)}\n\n程序将继续运行。"
            )
    except Exception:
        pass


# 安装全局异常处理器
sys.excepthook = exception_hook


def check_environment() -> bool:
    """检查运行环境

    Returns:
        bool: 环境检查通过返回 True，否则返回 False
    """
    errors = []
    warnings = []

    # 检查 PyQt6（必需）
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        errors.append("PyQt6 未安装")

    # 检查 MATLAB Engine（可选，仅在使用 MATLAB 功能时需要）
    try:
        import matlab.engine
    except ImportError:
        warnings.append("MATLAB Engine for Python 未安装（MATLAB 相关功能将不可用）")

    # 显示警告（不阻止启动）
    if warnings:
        print("\n" + "-" * 60)
        print("环境警告")
        print("-" * 60)
        for warning in warnings:
            print(f"  ⚠ {warning}")
        print("-" * 60 + "\n")

    # 只有必需依赖缺失才阻止启动
    if errors:
        print("\n" + "=" * 60)
        print("环境检查失败")
        print("=" * 60)
        for error in errors:
            print(f"  ✗ {error}")
        print("\n请安装缺少的依赖后重试。")
        print("=" * 60 + "\n")

        # 尝试显示图形界面错误提示
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("环境检查失败")
            msg.setText("缺少必要的依赖组件：\n\n" + "\n".join(f"• {e}" for e in errors))
            msg.exec()
        except Exception:
            pass

        return False

    return True


def main():
    """启动应用"""
    # 环境检查
    if not check_environment():
        sys.exit(1)

    from PyQt6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)

    # 解析命令行参数
    theme = "dark"  # 默认主题
    if "--light" in sys.argv:
        theme = "light"
    elif "--dark" in sys.argv:
        theme = "dark"

    # 创建主窗口并应用主题
    window = MainWindow(theme=theme)
    window.show()

    print(f"MBD_CICDKits 启动 (主题: {theme})")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
