"""
Modern Theme - MBD_CICDKits

设计理念：现代化的 Glassmorphism + 渐变设计
- 柔和的渐变背景
- 玻璃拟态卡片效果
- 流畅的过渡动画
- 友好的色彩对比度
- Anthropic 品牌配色系统
- 智能字体管理 (Poppins/Lora + fallback + 嵌入字体)

版本: 3.1
更新日期: 2026-02-07
"""

import sys
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase
from typing import Optional


def get_resource_path(relative_path: str) -> Path:
    """获取资源文件路径，支持PyInstaller打包

    Args:
        relative_path: 相对于src/ui目录的路径

    Returns:
        资源文件的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的路径
        base_path = Path(sys._MEIPASS) / "src" / "ui"
    else:
        # 开发环境路径
        base_path = Path(__file__).parent

    return base_path / relative_path


# =============================================================================
# 字体管理器 - Anthropic品牌字体智能加载
# =============================================================================

class FontManager:
    """字体管理器 - 智能加载品牌字体

    支持 Poppins (标题) 和 Lora (正文)，自动 fallback 到系统字体。
    会自动从应用资源目录加载嵌入的字体文件。
    """

    # Anthropic 品牌字体配置
    HEADING_FONT = "Poppins"
    BODY_FONT = "Lora"
    HEADING_FALLBACK = "Arial"
    BODY_FALLBACK = "Georgia"
    CHINESE_FONT = "Microsoft YaHei"
    CODE_FONT = "Consolas"

    # 字体缓存（延迟加载）
    _available_fonts: Optional[set[str]] = None
    _embedded_fonts_loaded = False

    @classmethod
    def _load_embedded_fonts(cls) -> None:
        """加载应用嵌入的字体"""
        if cls._embedded_fonts_loaded:
            return

        # 字体目录 - 支持PyInstaller打包
        font_dir = get_resource_path("resources/fonts")

        # 要加载的字体文件
        font_files = [
            "Poppins-Regular.ttf",
            "Poppins-Bold.ttf",
            "Lora-Regular.ttf",
            "Lora-Bold.ttf",
        ]

        loaded_count = 0
        for font_file in font_files:
            font_path = font_dir / font_file
            if font_path.exists():
                try:
                    font_id = QFontDatabase.addApplicationFont(str(font_path))
                    if font_id >= 0:
                        families = QFontDatabase.applicationFontFamilies(font_id)
                        if families:
                            loaded_count += 1
                except Exception:
                    pass

        cls._embedded_fonts_loaded = True

        # 重置字体缓存，以便下次查询时包含新加载的字体
        cls._available_fonts = None

    @classmethod
    def _init_font_db(cls) -> None:
        """初始化字体数据库缓存"""
        if cls._available_fonts is None:
            # 首先加载嵌入字体
            cls._load_embedded_fonts()

            # PyQt6: families() 是静态方法，直接调用
            cls._available_fonts = set(QFontDatabase.families())

    @classmethod
    def is_font_available(cls, font_name: str) -> bool:
        """检测字体是否可用

        Args:
            font_name: 字体名称

        Returns:
            字体是否可用
        """
        cls._init_font_db()
        return font_name in cls._available_fonts

    @classmethod
    def get_heading_font(cls, size: int = 14, bold: bool = True) -> QFont:
        """获取标题字体 (Poppins → Arial fallback)

        Args:
            size: 字体大小
            bold: 是否加粗

        Returns:
            配置好的 QFont 对象
        """
        cls._init_font_db()
        font = QFont()

        # 优先使用 Poppins
        if cls.is_font_available(cls.HEADING_FONT):
            font.setFamily(cls.HEADING_FONT)
        else:
            # Fallback 到 Arial
            font.setFamily(cls.HEADING_FALLBACK)

        font.setPointSize(size)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        return font

    @classmethod
    def get_body_font(cls, size: int = 14) -> QFont:
        """获取正文字体 (Lora → Georgia fallback)

        Args:
            size: 字体大小

        Returns:
            配置好的 QFont 对象
        """
        cls._init_font_db()
        font = QFont()

        # 优先使用 Lora
        if cls.is_font_available(cls.BODY_FONT):
            font.setFamily(cls.BODY_FONT)
        else:
            # Fallback 到 Georgia
            font.setFamily(cls.BODY_FALLBACK)

        font.setPointSize(size)
        return font

    @classmethod
    def get_chinese_font(cls, size: int = 14) -> QFont:
        """获取中文字体 (Microsoft YaHei)

        Args:
            size: 字体大小

        Returns:
            配置好的 QFont 对象
        """
        font = QFont()
        font.setFamily(cls.CHINESE_FONT)
        font.setPointSize(size)
        return font

    @classmethod
    def get_code_font(cls, size: int = 12) -> QFont:
        """获取等宽字体 (Consolas)

        Args:
            size: 字体大小

        Returns:
            配置好的 QFont 对象
        """
        font = QFont()
        font.setFamily(cls.CODE_FONT)
        font.setPointSize(size)
        return font

    @classmethod
    def get_font_info(cls) -> dict[str, bool]:
        """获取字体可用性信息（用于调试）

        Returns:
            字体名称到可用性的映射
        """
        cls._init_font_db()
        return {
            cls.HEADING_FONT: cls.is_font_available(cls.HEADING_FONT),
            cls.BODY_FONT: cls.is_font_available(cls.BODY_FONT),
            cls.HEADING_FALLBACK: cls.is_font_available(cls.HEADING_FALLBACK),
            cls.BODY_FALLBACK: cls.is_font_available(cls.BODY_FALLBACK),
            cls.CHINESE_FONT: cls.is_font_available(cls.CHINESE_FONT),
            cls.CODE_FONT: cls.is_font_available(cls.CODE_FONT),
        }


# =============================================================================
# 配色系统
# =============================================================================


class BrandColors:
    """Anthropic 品牌配色 - 深色主题

    基于 Anthropic 官方品牌指南的配色系统。
    """

    # 主背景色
    BG_PRIMARY = "#141413"      # 深黑 - 主背景
    BG_SECONDARY = "#1a1a19"    # 深灰黑 - 次级背景
    BG_CARD = "rgba(250, 249, 245, 0.05)"  # 玻璃卡片
    BG_CARD_HOVER = "rgba(250, 249, 245, 0.08)"

    # Anthropic 品牌强调色
    ACCENT_PRIMARY = "#d97757"  # 橙色 - 主要操作按钮
    ACCENT_SECONDARY = "#6a9bcc"  # 蓝色 - 次要操作
    ACCENT_TERTIARY = "#788c5d"  # 绿色 - 辅助操作

    # 状态色（基于品牌色系）
    ACCENT_SUCCESS = "#788c5d"  # 绿色 - 成功状态
    ACCENT_WARNING = "#d97757"  # 橙色 - 警告
    ACCENT_DANGER = "#d97757"   # 橙色 - 危险
    ACCENT_INFO = "#6a9bcc"     # 蓝色 - 信息

    # 渐变色（橙色系主色调）
    GRADIENT_PRIMARY_1 = "#d97757"
    GRADIENT_PRIMARY_2 = "#e89b7f"
    GRADIENT_SUCCESS_1 = "#788c5d"
    GRADIENT_SUCCESS_2 = "#8ea375"
    GRADIENT_DANGER_1 = "#d97757"
    GRADIENT_DANGER_2 = "#e89b7f"

    # 中灰色系
    MID_GRAY = "#b0aea5"
    LIGHT_GRAY = "#e8e6dc"

    # 文字色
    TEXT_PRIMARY = "#faf9f5"     # Anthropic 浅色
    TEXT_SECONDARY = "#e8e6dc"   # 浅灰
    TEXT_TERTIARY = "#b0aea5"    # 中灰
    TEXT_MUTED = "#8a8880"       # 深灰禁用

    # 边框和分隔
    BORDER_SUBTLE = "rgba(250, 249, 245, 0.08)"
    BORDER_DEFAULT = "rgba(250, 249, 245, 0.12)"
    BORDER_FOCUS = "rgba(217, 119, 87, 0.6)"  # 橙色焦点
    BORDER_ERROR = "rgba(217, 119, 87, 0.5)"

    # 阴影
    SHADOW_SM = "0 1px 2px rgba(0, 0, 0, 0.3)"
    SHADOW_MD = "0 4px 6px rgba(0, 0, 0, 0.4)"
    SHADOW_LG = "0 10px 15px rgba(0, 0, 0, 0.5)"
    SHADOW_GLOW = "0 0 20px rgba(217, 119, 87, 0.3)"  # 橙色光晕


class BrandLightColors:
    """Anthropic 品牌配色 - 浅色主题

    基于 Anthropic 官方品牌指南的浅色主题变体。
    """

    # 背景色
    BG_PRIMARY = "#faf9f5"      # Anthropic 浅色背景
    BG_SECONDARY = "#ffffff"    # 纯白
    BG_CARD = "rgba(20, 20, 19, 0.02)"
    BG_CARD_HOVER = "rgba(20, 20, 19, 0.04)"

    # 强调色（与深色主题一致）
    ACCENT_PRIMARY = "#d97757"
    ACCENT_SECONDARY = "#6a9bcc"
    ACCENT_TERTIARY = "#788c5d"
    ACCENT_SUCCESS = "#788c5d"
    ACCENT_WARNING = "#d97757"
    ACCENT_DANGER = "#d97757"
    ACCENT_INFO = "#6a9bcc"

    # 渐变色
    GRADIENT_PRIMARY_1 = "#d97757"
    GRADIENT_PRIMARY_2 = "#e89b7f"
    GRADIENT_SUCCESS_1 = "#788c5d"
    GRADIENT_SUCCESS_2 = "#8ea375"
    GRADIENT_DANGER_1 = "#d97757"
    GRADIENT_DANGER_2 = "#e89b7f"

    # 中灰色系
    MID_GRAY = "#b0aea5"
    LIGHT_GRAY = "#e8e6dc"

    # 文字色
    TEXT_PRIMARY = "#141413"    # 深黑
    TEXT_SECONDARY = "#4a4a48"  # 深灰
    TEXT_TERTIARY = "#8a8880"   # 中灰
    TEXT_MUTED = "#b0aea5"      # 浅灰禁用

    # 边框
    BORDER_SUBTLE = "rgba(20, 20, 19, 0.06)"
    BORDER_DEFAULT = "rgba(20, 20, 19, 0.1)"
    BORDER_FOCUS = "rgba(217, 119, 87, 0.5)"
    BORDER_ERROR = "rgba(217, 119, 87, 0.4)"

    # 阴影
    SHADOW_SM = "0 1px 2px rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px rgba(0, 0, 0, 0.07)"
    SHADOW_LG = "0 10px 15px rgba(0, 0, 0, 0.1)"
    SHADOW_GLOW = "0 0 20px rgba(217, 119, 87, 0.2)"


# 保留原有的配色类作为向后兼容
class Colors:
    """现代化配色系统 - 深色主题"""

    # 背景色（深空紫蓝渐变基底）
    BG_PRIMARY = "#1a1a2e"        # 深紫黑 - 主背景
    BG_SECONDARY = "#16213e"      # 深蓝灰 - 次级背景
    BG_CARD = "rgba(255, 255, 255, 0.05)"  # 玻璃卡片
    BG_CARD_HOVER = "rgba(255, 255, 255, 0.08)"

    # 强调色（渐变效果）
    ACCENT_PRIMARY = "#6366f1"    # 靛蓝 - 主要操作
    ACCENT_SECONDARY = "#8b5cf6"  # 紫色 - 次要操作
    ACCENT_SUCCESS = "#10b981"    # 翠绿 - 成功状态
    ACCENT_WARNING = "#f59e0b"    # 琥珀 - 警告
    ACCENT_DANGER = "#ef4444"     # 绯红 - 危险操作
    ACCENT_INFO = "#3b82f6"       # 天蓝 - 信息

    # 渐变色
    GRADIENT_PRIMARY_1 = "#6366f1"
    GRADIENT_PRIMARY_2 = "#8b5cf6"
    GRADIENT_SUCCESS_1 = "#10b981"
    GRADIENT_SUCCESS_2 = "#34d399"
    GRADIENT_DANGER_1 = "#ef4444"
    GRADIENT_DANGER_2 = "#f87171"

    # 文字色（优化对比度）
    TEXT_PRIMARY = "#f1f5f9"      # 亮白 - 主要文字
    TEXT_SECONDARY = "#cbd5e1"    # 浅灰 - 次要文字
    TEXT_TERTIARY = "#94a3b8"     # 中灰 - 辅助文字
    TEXT_MUTED = "#64748b"        # 深灰 - 禁用文字

    # 边框和分隔
    BORDER_SUBTLE = "rgba(255, 255, 255, 0.08)"
    BORDER_DEFAULT = "rgba(255, 255, 255, 0.12)"
    BORDER_FOCUS = "rgba(99, 102, 241, 0.6)"
    BORDER_ERROR = "rgba(239, 68, 68, 0.5)"

    # 阴影
    SHADOW_SM = "0 1px 2px rgba(0, 0, 0, 0.3)"
    SHADOW_MD = "0 4px 6px rgba(0, 0, 0, 0.4)"
    SHADOW_LG = "0 10px 15px rgba(0, 0, 0, 0.5)"
    SHADOW_GLOW = "0 0 20px rgba(99, 102, 241, 0.3)"


class LightColors:
    """现代化配色系统 - 浅色主题"""

    # 背景色
    BG_PRIMARY = "#f8fafc"        # 浅灰白
    BG_SECONDARY = "#ffffff"      # 纯白
    BG_CARD = "rgba(0, 0, 0, 0.02)"
    BG_CARD_HOVER = "rgba(0, 0, 0, 0.04)"

    # 强调色
    ACCENT_PRIMARY = "#6366f1"
    ACCENT_SECONDARY = "#8b5cf6"
    ACCENT_SUCCESS = "#10b981"
    ACCENT_WARNING = "#f59e0b"
    ACCENT_DANGER = "#ef4444"
    ACCENT_INFO = "#3b82f6"

    # 渐变色
    GRADIENT_PRIMARY_1 = "#6366f1"
    GRADIENT_PRIMARY_2 = "#8b5cf6"
    GRADIENT_SUCCESS_1 = "#10b981"
    GRADIENT_SUCCESS_2 = "#34d399"
    GRADIENT_DANGER_1 = "#ef4444"
    GRADIENT_DANGER_2 = "#f87171"

    # 文字色
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    TEXT_TERTIARY = "#64748b"
    TEXT_MUTED = "#94a3b8"

    # 边框
    BORDER_SUBTLE = "rgba(0, 0, 0, 0.06)"
    BORDER_DEFAULT = "rgba(0, 0, 0, 0.1)"
    BORDER_FOCUS = "rgba(99, 102, 241, 0.5)"
    BORDER_ERROR = "rgba(239, 68, 68, 0.4)"

    # 阴影
    SHADOW_SM = "0 1px 2px rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px rgba(0, 0, 0, 0.07)"
    SHADOW_LG = "0 10px 15px rgba(0, 0, 0, 0.1)"
    SHADOW_GLOW = "0 0 20px rgba(99, 102, 241, 0.2)"


# 默认使用 Anthropic 品牌深色主题
_CurrentColors = BrandColors


def set_theme(theme: str = "dark", use_brand: bool = True):
    """设置主题

    Args:
        theme: "dark" 或 "light"
        use_brand: 是否使用 Anthropic 品牌配色（默认 True）
    """
    global _CurrentColors
    if theme == "light":
        _CurrentColors = BrandLightColors if use_brand else LightColors
    else:
        _CurrentColors = BrandColors if use_brand else Colors


def get_colors():
    """获取当前主题配色"""
    return _CurrentColors


# 深色主题样式表 - 现代化玻璃拟态风格
DARK_STYLESHEET = f"""
/* ========== 全局样式 ========== */
* {{
    outline: none;
}}

QWidget {{
    background-color: transparent;
    color: {Colors.TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Roboto', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
    border: none;
}}

/* ========== 主窗口背景 ========== */
QMainWindow {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0f0f1a,
        stop:0.5 {Colors.BG_PRIMARY},
        stop:1 {Colors.BG_SECONDARY}
    );
}}

/* ========== 卡片容器（玻璃拟态） ========== */
QFrame {{
    background-color: {Colors.BG_CARD};
    border-radius: 16px;
    border: 1px solid {Colors.BORDER_SUBTLE};
}}

QFrame[elevated="true"] {{
    background-color: {Colors.BG_CARD};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 16px;
}}

/* 卡片悬停效果 */
QFrame[elevated="true"]:hover {{
    background-color: {Colors.BG_CARD_HOVER};
    border: 1px solid {Colors.BORDER_FOCUS};
}}

/* ========== 标题样式 ========== */
QLabel[heading="true"] {{
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: {Colors.TEXT_PRIMARY};
    letter-spacing: -1px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {Colors.GRADIENT_PRIMARY_1},
        stop:1 {Colors.GRADIENT_PRIMARY_2}
    );
    -webkit-background-clip: text;
}}

QLabel[subheading="true"] {{
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: {Colors.ACCENT_PRIMARY};
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-bottom: 8px;
}}

QLabel[label="true"] {{
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 13px;
    color: {Colors.TEXT_SECONDARY};
    padding: 6px 0px;
}}

/* ========== 输入框（现代化设计） ========== */
QLineEdit {{
    background-color: rgba(255, 255, 255, 0.05);
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: {Colors.ACCENT_PRIMARY};
}}

QLineEdit:focus {{
    background-color: rgba(255, 255, 255, 0.08);
    border: 2px solid {Colors.BORDER_FOCUS};
}}

QLineEdit:hover {{
    border: 1px solid {Colors.BORDER_FOCUS};
}}

QLineEdit::placeholder {{
    color: {Colors.TEXT_MUTED};
}}

/* 自动检测的输入框（绿色高亮） */
QLineEdit[auto-detected="true"] {{
    background-color: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: {Colors.ACCENT_SUCCESS};
}}

QLineEdit[auto-detected="true"]:focus {{
    border: 2px solid {Colors.ACCENT_SUCCESS};
}}

/* ========== 下拉框 ========== */
QComboBox {{
    background-color: rgba(255, 255, 255, 0.05);
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
}}

QComboBox:hover {{
    border: 1px solid {Colors.BORDER_FOCUS};
}}

QComboBox:focus {{
    border: 2px solid {Colors.BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
    padding-right: 8px;
}}

QComboBox::down-arrow {{
    image: none;
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {Colors.BG_SECONDARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    selection-background-color: {Colors.ACCENT_PRIMARY};
    selection-color: {Colors.TEXT_PRIMARY};
    padding: 8px;
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    padding: 10px 16px;
    border-radius: 6px;
    margin: 2px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: rgba(99, 102, 241, 0.2);
}}

/* ========== 按钮（现代化设计） ========== */
QPushButton {{
    background-color: rgba(255, 255, 255, 0.05);
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid {Colors.BORDER_FOCUS};
}}

QPushButton:pressed {{
    background-color: rgba(255, 255, 255, 0.05);
    padding: 11px 23px 13px 25px;
}}

QPushButton:disabled {{
    background-color: rgba(255, 255, 255, 0.02);
    color: {Colors.TEXT_MUTED};
    border: 1px solid {Colors.BORDER_SUBTLE};
}}

/* 主要按钮（渐变效果） */
QPushButton[primary="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {Colors.GRADIENT_PRIMARY_1},
        stop:1 {Colors.GRADIENT_PRIMARY_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[primary="true"]:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c7ff5,
        stop:1 #9d76fa
    );
}}

QPushButton[primary="true"]:pressed {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {Colors.GRADIENT_PRIMARY_1},
        stop:1 {Colors.GRADIENT_PRIMARY_2}
    );
}}

/* 危险按钮（渐变效果） */
QPushButton[danger="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {Colors.GRADIENT_DANGER_1},
        stop:1 {Colors.GRADIENT_DANGER_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[danger="true"]:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #f87171,
        stop:1 #fca5a5
    );
}}

/* 成功按钮 */
QPushButton[success="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {Colors.GRADIENT_SUCCESS_1},
        stop:1 {Colors.GRADIENT_SUCCESS_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[success="true"]:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #34d399,
        stop:1 #6ee7b7
    );
}}

/* 图标按钮 */
QPushButton[icon-btn="true"] {{
    background-color: transparent;
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 10px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}}

QPushButton[icon-btn="true"]:hover {{
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid {Colors.BORDER_FOCUS};
}}

/* ========== 滚动条 ========== */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: rgba(255, 255, 255, 0.3);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    border-radius: 4px;
    margin: 4px;
}}

QScrollBar::handle:horizontal {{
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    min-width: 40px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: rgba(255, 255, 255, 0.3);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ========== 分隔线 ========== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {Colors.BORDER_DEFAULT};
    max-height: 1px;
}}

/* ========== 对话框 ========== */
QDialog {{
    background-color: {Colors.BG_SECONDARY};
    border-radius: 20px;
}}

QDialog QLabel {{
    color: {Colors.TEXT_PRIMARY};
}}

/* ========== 消息框 ========== */
QMessageBox {{
    background-color: {Colors.BG_SECONDARY};
    border-radius: 16px;
}}

QMessageBox QPushButton {{
    min-width: 80px;
    padding: 10px 20px;
}}

/* ========== 状态栏 ========== */
QStatusBar {{
    background-color: {Colors.BG_PRIMARY};
    color: {Colors.TEXT_SECONDARY};
    border: none;
    border-top: 1px solid {Colors.BORDER_SUBTLE};
    padding: 8px 16px;
}}

QStatusBar::item {{
    border: none;
}}

QStatusBar QLabel {{
    color: {Colors.TEXT_SECONDARY};
    padding: 0px;
}}

/* ========== 菜单栏 ========== */
QMenuBar {{
    background-color: {Colors.BG_PRIMARY};
    border: none;
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 6px;
}}

QMenuBar::item:selected {{
    background-color: rgba(255, 255, 255, 0.1);
}}

QMenuBar::item:pressed {{
    background-color: rgba(255, 255, 255, 0.05);
}}

QMenu {{
    background-color: {Colors.BG_SECONDARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 4px;
}}

QMenu::item {{
    padding: 10px 20px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: rgba(99, 102, 241, 0.2);
}}

/* ========== 进度条 ========== */
QProgressBar {{
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {Colors.GRADIENT_PRIMARY_1},
        stop:1 {Colors.GRADIENT_PRIMARY_2}
    );
    border-radius: 6px;
}}
"""


# 浅色主题样式表
LIGHT_STYLESHEET = f"""
/* ========== 全局样式 ========== */
* {{
    outline: none;
}}

QWidget {{
    background-color: transparent;
    color: {LightColors.TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Roboto', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
    border: none;
}}

/* ========== 主窗口背景 ========== */
QMainWindow {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #f1f5f9,
        stop:0.5 {LightColors.BG_PRIMARY},
        stop:1 #e2e8f0
    );
}}

/* ========== 卡片容器 ========== */
QFrame {{
    background-color: {LightColors.BG_CARD};
    border-radius: 16px;
    border: 1px solid {LightColors.BORDER_SUBTLE};
}}

QFrame[elevated="true"] {{
    background-color: {LightColors.BG_SECONDARY};
    border: 1px solid {LightColors.BORDER_DEFAULT};
    border-radius: 16px;
}}

QFrame[elevated="true"]:hover {{
    background-color: {LightColors.BG_CARD_HOVER};
    border: 1px solid {LightColors.BORDER_FOCUS};
}}

/* ========== 标题样式 ========== */
QLabel[heading="true"] {{
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: {LightColors.TEXT_PRIMARY};
    letter-spacing: -1px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {LightColors.GRADIENT_PRIMARY_1},
        stop:1 {LightColors.GRADIENT_PRIMARY_2}
    );
    -webkit-background-clip: text;
}}

QLabel[subheading="true"] {{
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: {LightColors.ACCENT_PRIMARY};
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-bottom: 8px;
}}

QLabel[label="true"] {{
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 13px;
    color: {LightColors.TEXT_SECONDARY};
    padding: 6px 0px;
}}

/* ========== 输入框 ========== */
QLineEdit {{
    background-color: {LightColors.BG_SECONDARY};
    color: {LightColors.TEXT_PRIMARY};
    border: 1px solid {LightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: {LightColors.ACCENT_PRIMARY};
}}

QLineEdit:focus {{
    background-color: {LightColors.BG_SECONDARY};
    border: 2px solid {LightColors.BORDER_FOCUS};
}}

QLineEdit:hover {{
    border: 1px solid {LightColors.BORDER_FOCUS};
}}

QLineEdit::placeholder {{
    color: {LightColors.TEXT_MUTED};
}}

QLineEdit[auto-detected="true"] {{
    background-color: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: {LightColors.ACCENT_SUCCESS};
}}

/* ========== 下拉框 ========== */
QComboBox {{
    background-color: {LightColors.BG_SECONDARY};
    color: {LightColors.TEXT_PRIMARY};
    border: 1px solid {LightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
}}

QComboBox:hover {{
    border: 1px solid {LightColors.BORDER_FOCUS};
}}

QComboBox:focus {{
    border: 2px solid {LightColors.BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
}}

QComboBox QAbstractItemView {{
    background-color: {LightColors.BG_SECONDARY};
    border: 1px solid {LightColors.BORDER_DEFAULT};
    border-radius: 10px;
    selection-background-color: {LightColors.ACCENT_PRIMARY};
    selection-color: #FFFFFF;
    padding: 8px;
}}

QComboBox QAbstractItemView::item {{
    padding: 10px 16px;
    border-radius: 6px;
    margin: 2px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: rgba(99, 102, 241, 0.1);
}}

/* ========== 按钮 ========== */
QPushButton {{
    background-color: {LightColors.BG_CARD};
    color: {LightColors.TEXT_PRIMARY};
    border: 1px solid {LightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {LightColors.BG_CARD_HOVER};
    border: 1px solid {LightColors.BORDER_FOCUS};
}}

QPushButton:pressed {{
    background-color: {LightColors.BG_CARD};
}}

QPushButton:disabled {{
    background-color: rgba(0, 0, 0, 0.02);
    color: {LightColors.TEXT_MUTED};
    border: 1px solid {LightColors.BORDER_SUBTLE};
}}

QPushButton[primary="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {LightColors.GRADIENT_PRIMARY_1},
        stop:1 {LightColors.GRADIENT_PRIMARY_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[primary="true"]:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c7ff5,
        stop:1 #9d76fa
    );
}}

QPushButton[danger="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {LightColors.GRADIENT_DANGER_1},
        stop:1 {LightColors.GRADIENT_DANGER_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[success="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {LightColors.GRADIENT_SUCCESS_1},
        stop:1 {LightColors.GRADIENT_SUCCESS_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[icon-btn="true"] {{
    background-color: transparent;
    border: 1px solid {LightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 10px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}}

QPushButton[icon-btn="true"]:hover {{
    background-color: {LightColors.BG_CARD};
}}

/* ========== 滚动条 ========== */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: rgba(0, 0, 0, 0.15);
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: rgba(0, 0, 0, 0.25);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    border-radius: 4px;
    margin: 4px;
}}

QScrollBar::handle:horizontal {{
    background-color: rgba(0, 0, 0, 0.15);
    border-radius: 4px;
    min-width: 40px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: rgba(0, 0, 0, 0.25);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ========== 分隔线 ========== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {LightColors.BORDER_DEFAULT};
    max-height: 1px;
}}

/* ========== 对话框 ========== */
QDialog {{
    background-color: {LightColors.BG_SECONDARY};
    border-radius: 20px;
}}

QDialog QLabel {{
    color: {LightColors.TEXT_PRIMARY};
}}

/* ========== 状态栏 ========== */
QStatusBar {{
    background-color: {LightColors.BG_PRIMARY};
    color: {LightColors.TEXT_SECONDARY};
    border: none;
    border-top: 1px solid {LightColors.BORDER_SUBTLE};
    padding: 8px 16px;
}}

QStatusBar::item {{
    border: none;
}}

/* ========== 菜单栏 ========== */
QMenuBar {{
    background-color: {LightColors.BG_PRIMARY};
    border: none;
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 6px;
}}

QMenuBar::item:selected {{
    background-color: rgba(0, 0, 0, 0.05);
}}

QMenu {{
    background-color: {LightColors.BG_SECONDARY};
    border: 1px solid {LightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 4px;
}}

QMenu::item {{
    padding: 10px 20px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: rgba(99, 102, 241, 0.1);
}}
"""


# =============================================================================
# Anthropic 品牌样式表 - 深色主题（橙色系）
# =============================================================================

BRAND_DARK_STYLESHEET = f"""
/* ========== 全局样式 ========== */
* {{
    outline: none;
}}

QWidget {{
    background-color: transparent;
    color: {BrandColors.TEXT_PRIMARY};
    font-family: 'Poppins', 'Lora', 'Segoe UI', 'Roboto', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
    border: none;
}}

/* ========== 主窗口背景 ========== */
QMainWindow {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0a0a09,
        stop:0.5 {BrandColors.BG_PRIMARY},
        stop:1 {BrandColors.BG_SECONDARY}
    );
}}

/* ========== 卡片容器（玻璃拟态） ========== */
QFrame {{
    background-color: {BrandColors.BG_CARD};
    border-radius: 16px;
    border: 1px solid {BrandColors.BORDER_SUBTLE};
}}

QFrame[elevated="true"] {{
    background-color: {BrandColors.BG_CARD};
    border: 1px solid {BrandColors.BORDER_DEFAULT};
    border-radius: 16px;
}}

/* 卡片悬停效果 */
QFrame[elevated="true"]:hover {{
    background-color: {BrandColors.BG_CARD_HOVER};
    border: 1px solid {BrandColors.BORDER_FOCUS};
}}

/* ========== 标题样式（Poppins 字体） ========== */
QLabel[heading="true"] {{
    font-family: 'Poppins', 'Arial', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: {BrandColors.TEXT_PRIMARY};
    letter-spacing: -1px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandColors.GRADIENT_PRIMARY_1},
        stop:1 {BrandColors.GRADIENT_PRIMARY_2}
    );
    -webkit-background-clip: text;
}}

QLabel[subheading="true"] {{
    font-family: 'Poppins', 'Arial', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: {BrandColors.ACCENT_PRIMARY};
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-bottom: 8px;
}}

QLabel[label="true"] {{
    font-family: 'Lora', 'Georgia', 'Segoe UI', sans-serif;
    font-size: 13px;
    color: {BrandColors.TEXT_SECONDARY};
    padding: 6px 0px;
}}

/* ========== 输入框（现代化设计） ========== */
QLineEdit {{
    background-color: rgba(250, 249, 245, 0.05);
    color: {BrandColors.TEXT_PRIMARY};
    border: 1px solid {BrandColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    font-family: 'Lora', 'Georgia', 'Segoe UI', sans-serif;
    selection-background-color: {BrandColors.ACCENT_PRIMARY};
}}

QLineEdit:focus {{
    background-color: rgba(250, 249, 245, 0.08);
    border: 2px solid {BrandColors.BORDER_FOCUS};
}}

QLineEdit:hover {{
    border: 1px solid {BrandColors.BORDER_FOCUS};
}}

QLineEdit::placeholder {{
    color: {BrandColors.TEXT_MUTED};
}}

/* 自动检测的输入框（绿色高亮） */
QLineEdit[auto-detected="true"] {{
    background-color: rgba(120, 140, 93, 0.1);
    border: 1px solid rgba(120, 140, 93, 0.4);
    color: {BrandColors.ACCENT_SUCCESS};
}}

QLineEdit[auto-detected="true"]:focus {{
    border: 2px solid {BrandColors.ACCENT_SUCCESS};
}}

/* ========== 下拉框 ========== */
QComboBox {{
    background-color: rgba(250, 249, 245, 0.05);
    color: {BrandColors.TEXT_PRIMARY};
    border: 1px solid {BrandColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    font-family: 'Lora', 'Georgia', 'Segoe UI', sans-serif;
}}

QComboBox:hover {{
    border: 1px solid {BrandColors.BORDER_FOCUS};
}}

QComboBox:focus {{
    border: 2px solid {BrandColors.BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
    padding-right: 8px;
}}

QComboBox::down-arrow {{
    image: none;
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {BrandColors.BG_SECONDARY};
    border: 1px solid {BrandColors.BORDER_DEFAULT};
    border-radius: 10px;
    selection-background-color: {BrandColors.ACCENT_PRIMARY};
    selection-color: {BrandColors.TEXT_PRIMARY};
    padding: 8px;
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    padding: 10px 16px;
    border-radius: 6px;
    margin: 2px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: rgba(217, 119, 87, 0.2);
}}

/* ========== 按钮（现代化设计） ========== */
QPushButton {{
    background-color: rgba(250, 249, 245, 0.05);
    color: {BrandColors.TEXT_PRIMARY};
    border: 1px solid {BrandColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    font-family: 'Poppins', 'Arial', sans-serif;
}}

QPushButton:hover {{
    background-color: rgba(250, 249, 245, 0.1);
    border: 1px solid {BrandColors.BORDER_FOCUS};
}}

QPushButton:pressed {{
    background-color: rgba(250, 249, 245, 0.05);
    padding: 11px 23px 13px 25px;
}}

QPushButton:disabled {{
    background-color: rgba(250, 249, 245, 0.02);
    color: {BrandColors.TEXT_MUTED};
    border: 1px solid {BrandColors.BORDER_SUBTLE};
}}

/* 主要按钮（橙色渐变效果） */
QPushButton[primary="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandColors.GRADIENT_PRIMARY_1},
        stop:1 {BrandColors.GRADIENT_PRIMARY_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[primary="true"]:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #e89b7f,
        stop:1 #f2b59c
    );
}}

QPushButton[primary="true"]:pressed {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandColors.GRADIENT_PRIMARY_1},
        stop:1 {BrandColors.GRADIENT_PRIMARY_2}
    );
}}

/* 危险按钮（橙色渐变效果） */
QPushButton[danger="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandColors.GRADIENT_DANGER_1},
        stop:1 {BrandColors.GRADIENT_DANGER_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[danger="true"]:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #e89b7f,
        stop:1 #f2b59c
    );
}}

/* 成功按钮（绿色渐变） */
QPushButton[success="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandColors.GRADIENT_SUCCESS_1},
        stop:1 {BrandColors.GRADIENT_SUCCESS_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[success="true"]:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #8ea375,
        stop:1 #a2b689
    );
}}

/* 图标按钮 */
QPushButton[icon-btn="true"] {{
    background-color: transparent;
    border: 1px solid {BrandColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 10px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}}

QPushButton[icon-btn="true"]:hover {{
    background-color: rgba(250, 249, 245, 0.1);
    border: 1px solid {BrandColors.BORDER_FOCUS};
}}

/* ========== 滚动条 ========== */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: rgba(250, 249, 245, 0.2);
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: rgba(250, 249, 245, 0.3);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    border-radius: 4px;
    margin: 4px;
}}

QScrollBar::handle:horizontal {{
    background-color: rgba(250, 249, 245, 0.2);
    border-radius: 4px;
    min-width: 40px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: rgba(250, 249, 245, 0.3);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ========== 分隔线 ========== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {BrandColors.BORDER_DEFAULT};
    max-height: 1px;
}}

/* ========== 对话框 ========== */
QDialog {{
    background-color: {BrandColors.BG_SECONDARY};
    border-radius: 20px;
}}

QDialog QLabel {{
    color: {BrandColors.TEXT_PRIMARY};
}}

/* ========== 消息框 ========== */
QMessageBox {{
    background-color: {BrandColors.BG_SECONDARY};
    border-radius: 16px;
}}

QMessageBox QPushButton {{
    min-width: 80px;
    padding: 10px 20px;
}}

/* ========== 状态栏 ========== */
QStatusBar {{
    background-color: {BrandColors.BG_PRIMARY};
    color: {BrandColors.TEXT_SECONDARY};
    border: none;
    border-top: 1px solid {BrandColors.BORDER_SUBTLE};
    padding: 8px 16px;
}}

QStatusBar::item {{
    border: none;
}}

QStatusBar QLabel {{
    color: {BrandColors.TEXT_SECONDARY};
    padding: 0px;
}}

/* ========== 菜单栏 ========== */
QMenuBar {{
    background-color: {BrandColors.BG_PRIMARY};
    border: none;
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 6px;
}}

QMenuBar::item:selected {{
    background-color: rgba(250, 249, 245, 0.1);
}}

QMenuBar::item:pressed {{
    background-color: rgba(250, 249, 245, 0.05);
}}

QMenu {{
    background-color: {BrandColors.BG_SECONDARY};
    border: 1px solid {BrandColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 4px;
}}

QMenu::item {{
    padding: 10px 20px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: rgba(217, 119, 87, 0.2);
}}

/* ========== 进度条 ========== */
QProgressBar {{
    background-color: rgba(250, 249, 245, 0.05);
    border: 1px solid {BrandColors.BORDER_DEFAULT};
    border-radius: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandColors.GRADIENT_PRIMARY_1},
        stop:1 {BrandColors.GRADIENT_PRIMARY_2}
    );
    border-radius: 6px;
}}
"""


# =============================================================================
# Anthropic 品牌样式表 - 浅色主题
# =============================================================================

BRAND_LIGHT_STYLESHEET = f"""
/* ========== 全局样式 ========== */
* {{
    outline: none;
}}

QWidget {{
    background-color: transparent;
    color: {BrandLightColors.TEXT_PRIMARY};
    font-family: 'Poppins', 'Lora', 'Segoe UI', 'Roboto', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
    border: none;
}}

/* ========== 主窗口背景 ========== */
QMainWindow {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #f5f3ef,
        stop:0.5 {BrandLightColors.BG_PRIMARY},
        stop:1 #e8e6dc
    );
}}

/* ========== 卡片容器 ========== */
QFrame {{
    background-color: {BrandLightColors.BG_CARD};
    border-radius: 16px;
    border: 1px solid {BrandLightColors.BORDER_SUBTLE};
}}

QFrame[elevated="true"] {{
    background-color: {BrandLightColors.BG_SECONDARY};
    border: 1px solid {BrandLightColors.BORDER_DEFAULT};
    border-radius: 16px;
}}

QFrame[elevated="true"]:hover {{
    background-color: {BrandLightColors.BG_CARD_HOVER};
    border: 1px solid {BrandLightColors.BORDER_FOCUS};
}}

/* ========== 标题样式（Poppins 字体） ========== */
QLabel[heading="true"] {{
    font-family: 'Poppins', 'Arial', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: {BrandLightColors.TEXT_PRIMARY};
    letter-spacing: -1px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandLightColors.GRADIENT_PRIMARY_1},
        stop:1 {BrandLightColors.GRADIENT_PRIMARY_2}
    );
    -webkit-background-clip: text;
}}

QLabel[subheading="true"] {{
    font-family: 'Poppins', 'Arial', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: {BrandLightColors.ACCENT_PRIMARY};
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-bottom: 8px;
}}

QLabel[label="true"] {{
    font-family: 'Lora', 'Georgia', 'Segoe UI', sans-serif;
    font-size: 13px;
    color: {BrandLightColors.TEXT_SECONDARY};
    padding: 6px 0px;
}}

/* ========== 输入框 ========== */
QLineEdit {{
    background-color: {BrandLightColors.BG_SECONDARY};
    color: {BrandLightColors.TEXT_PRIMARY};
    border: 1px solid {BrandLightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    font-family: 'Lora', 'Georgia', 'Segoe UI', sans-serif;
    selection-background-color: {BrandLightColors.ACCENT_PRIMARY};
}}

QLineEdit:focus {{
    background-color: {BrandLightColors.BG_SECONDARY};
    border: 2px solid {BrandLightColors.BORDER_FOCUS};
}}

QLineEdit:hover {{
    border: 1px solid {BrandLightColors.BORDER_FOCUS};
}}

QLineEdit::placeholder {{
    color: {BrandLightColors.TEXT_MUTED};
}}

QLineEdit[auto-detected="true"] {{
    background-color: rgba(120, 140, 93, 0.08);
    border: 1px solid rgba(120, 140, 93, 0.3);
    color: {BrandLightColors.ACCENT_SUCCESS};
}}

/* ========== 下拉框 ========== */
QComboBox {{
    background-color: {BrandLightColors.BG_SECONDARY};
    color: {BrandLightColors.TEXT_PRIMARY};
    border: 1px solid {BrandLightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    font-family: 'Lora', 'Georgia', 'Segoe UI', sans-serif;
}}

QComboBox:hover {{
    border: 1px solid {BrandLightColors.BORDER_FOCUS};
}}

QComboBox:focus {{
    border: 2px solid {BrandLightColors.BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
}}

QComboBox QAbstractItemView {{
    background-color: {BrandLightColors.BG_SECONDARY};
    border: 1px solid {BrandLightColors.BORDER_DEFAULT};
    border-radius: 10px;
    selection-background-color: {BrandLightColors.ACCENT_PRIMARY};
    selection-color: #FFFFFF;
    padding: 8px;
}}

QComboBox QAbstractItemView::item {{
    padding: 10px 16px;
    border-radius: 6px;
    margin: 2px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: rgba(217, 119, 87, 0.1);
}}

/* ========== 按钮 ========== */
QPushButton {{
    background-color: {BrandLightColors.BG_CARD};
    color: {BrandLightColors.TEXT_PRIMARY};
    border: 1px solid {BrandLightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    font-family: 'Poppins', 'Arial', sans-serif;
}}

QPushButton:hover {{
    background-color: {BrandLightColors.BG_CARD_HOVER};
    border: 1px solid {BrandLightColors.BORDER_FOCUS};
}}

QPushButton:pressed {{
    background-color: {BrandLightColors.BG_CARD};
}}

QPushButton:disabled {{
    background-color: rgba(20, 20, 19, 0.02);
    color: {BrandLightColors.TEXT_MUTED};
    border: 1px solid {BrandLightColors.BORDER_SUBTLE};
}}

QPushButton[primary="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandLightColors.GRADIENT_PRIMARY_1},
        stop:1 {BrandLightColors.GRADIENT_PRIMARY_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[primary="true"]:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #e89b7f,
        stop:1 #f2b59c
    );
}}

QPushButton[danger="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandLightColors.GRADIENT_DANGER_1},
        stop:1 {BrandLightColors.GRADIENT_DANGER_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[success="true"] {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BrandLightColors.GRADIENT_SUCCESS_1},
        stop:1 {BrandLightColors.GRADIENT_SUCCESS_2}
    );
    color: #FFFFFF;
    border: none;
    font-weight: 600;
    border-radius: 12px;
}}

QPushButton[icon-btn="true"] {{
    background-color: transparent;
    border: 1px solid {BrandLightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 10px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}}

QPushButton[icon-btn="true"]:hover {{
    background-color: {BrandLightColors.BG_CARD};
}}

/* ========== 滚动条 ========== */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: rgba(20, 20, 19, 0.15);
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: rgba(20, 20, 19, 0.25);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    border-radius: 4px;
    margin: 4px;
}}

QScrollBar::handle:horizontal {{
    background-color: rgba(20, 20, 19, 0.15);
    border-radius: 4px;
    min-width: 40px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: rgba(20, 20, 19, 0.25);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ========== 分隔线 ========== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {BrandLightColors.BORDER_DEFAULT};
    max-height: 1px;
}}

/* ========== 对话框 ========== */
QDialog {{
    background-color: {BrandLightColors.BG_SECONDARY};
    border-radius: 20px;
}}

QDialog QLabel {{
    color: {BrandLightColors.TEXT_PRIMARY};
}}

/* ========== 状态栏 ========== */
QStatusBar {{
    background-color: {BrandLightColors.BG_PRIMARY};
    color: {BrandLightColors.TEXT_SECONDARY};
    border: none;
    border-top: 1px solid {BrandLightColors.BORDER_SUBTLE};
    padding: 8px 16px;
}}

QStatusBar::item {{
    border: none;
}}

/* ========== 菜单栏 ========== */
QMenuBar {{
    background-color: {BrandLightColors.BG_PRIMARY};
    border: none;
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 6px;
}}

QMenuBar::item:selected {{
    background-color: rgba(20, 20, 19, 0.05);
}}

QMenu {{
    background-color: {BrandLightColors.BG_SECONDARY};
    border: 1px solid {BrandLightColors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 4px;
}}

QMenu::item {{
    padding: 10px 20px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: rgba(217, 119, 87, 0.1);
}}
"""


# =============================================================================
# 主题应用函数（更新版 - 支持品牌配色）
# =============================================================================

def apply_industrial_theme(widget, theme: str = "dark", use_brand: bool = True):
    """应用现代化主题到指定组件

    Args:
        widget: 要应用主题的组件
        theme: "dark" 或 "light"
        use_brand: 是否使用 Anthropic 品牌配色（默认 True）
    """
    set_theme(theme, use_brand=use_brand)

    if use_brand:
        # 使用 Anthropic 品牌配色
        if theme == "light":
            widget.setStyleSheet(BRAND_LIGHT_STYLESHEET)
        else:
            widget.setStyleSheet(BRAND_DARK_STYLESHEET)
    else:
        # 使用原有的配色方案
        if theme == "light":
            widget.setStyleSheet(LIGHT_STYLESHEET)
        else:
            widget.setStyleSheet(DARK_STYLESHEET)


# 导出便捷函数
def apply_brand_theme(widget, theme: str = "dark"):
    """应用 Anthropic 品牌主题

    Args:
        widget: 要应用主题的组件
        theme: "dark" 或 "light"
    """
    apply_industrial_theme(widget, theme, use_brand=True)

