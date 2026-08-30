# coding:utf-8
"""简约 UI 样式构建工具

用法：
- menu_qss()         -> 右键菜单简约样式（配 qfluentwidgets.setCustomStyleSheet 追加覆盖）
- bubble_frame_qss() -> 对话 / 通知气泡卡片样式
- soft_button_qss()  -> 简约按钮样式（secondary / primary）
"""
from qfluentwidgets import isDarkTheme

from . import palette

# 圆角规范
MENU_RADIUS = 8      # 菜单圆角
CARD_RADIUS = 12     # 卡片圆角
CONTROL_RADIUS = 8   # 控件圆角
SMALL_RADIUS = 6     # 小控件圆角

# 统一字体
UI_FONT = '"Segoe UI", "Microsoft YaHei", "PingFang SC"'


def active_palette(dark=None):
    """返回当前主题的设计令牌

    Parameters
    ----------
    dark: bool | None
        指定深/浅色；为 None 时跟随系统（isDarkTheme）
    """
    if dark is None:
        dark = isDarkTheme()
    return palette.DARK if dark else palette.LIGHT


def qss_color(c):
    """将设计令牌颜色转为 QSS 颜色字符串"""
    if isinstance(c, tuple):
        r, g, b, a = c
        return 'rgba(%d, %d, %d, %d)' % (r, g, b, a)
    return c


def menu_qss(dark=None):
    """右键菜单简约样式

    通过 qfluentwidgets 的 setCustomStyleSheet 追加到控件样式表末尾，
    从而覆盖 Fluent 原生的菜单 QSS。
    """
    p = active_palette(dark)
    return f'''
RoundMenu {{
    background-color: transparent;
    border: none;
}}

MenuActionListWidget {{
    border: 1px solid {p['menuBorder']};
    border-radius: {MENU_RADIUS}px;
    background-color: {p['menuBg']};
    outline: none;
    font: 14px {UI_FONT};
}}

MenuActionListWidget[transparent=true] {{
    background-color: transparent;
}}

MenuActionListWidget::item {{
    padding-left: 12px;
    padding-right: 12px;
    border-radius: {SMALL_RADIUS}px;
    margin-left: 6px;
    margin-right: 6px;
    border: none;
    color: {p['text']};
}}

MenuActionListWidget::item:disabled {{
    color: {p['textDisabled']};
}}

MenuActionListWidget::item:hover {{
    background-color: {p['itemHover']};
}}

MenuActionListWidget::item:selected {{
    background-color: {p['itemSelected']};
    color: {p['text']};
}}

MenuActionListWidget::item:selected:active {{
    background-color: {p['itemSelected']};
    color: {p['textSecondary']};
}}
'''


def bubble_frame_qss(dark=None, radius=CARD_RADIUS):
    """对话 / 通知气泡卡片样式"""
    p = active_palette(dark)
    return f'''
QFrame {{
    border: 1px solid {p['border']};
    border-radius: {radius}px;
    background: {p['card']};
}}

QLabel {{
    border: 0px;
    background-color: transparent;
    color: {p['text']};
}}
'''


def soft_button_qss(dark=None, primary=False):
    """简约按钮样式

    Parameters
    ----------
    primary: bool
        是否为主按钮（暖橙实底）；默认次级按钮（白底描边）
    """
    p = active_palette(dark)
    if primary:
        return f'''
QPushButton {{
    background-color: {p['primary']};
    border: none;
    border-radius: {CONTROL_RADIUS}px;
    padding: 6px 14px;
    color: {p['onPrimary']};
    font: 14px {UI_FONT};
}}
QPushButton:hover {{
    background-color: {p['primaryHover']};
}}
QPushButton:pressed {{
    background-color: {p['primaryPressed']};
}}
QPushButton:disabled {{
    background-color: {p['active']};
    color: {p['textDisabled']};
}}
'''
    return f'''
QPushButton {{
    background-color: {p['card']};
    border: 1px solid {p['border']};
    border-radius: {CONTROL_RADIUS}px;
    padding: 6px 14px;
    color: {p['text']};
    font: 14px {UI_FONT};
}}
QPushButton:hover {{
    background-color: {p['hover']};
    border-color: {p['textSecondary']};
}}
QPushButton:pressed {{
    background-color: {p['active']};
}}
QPushButton:disabled {{
    color: {p['textDisabled']};
    background-color: {p['hover']};
}}
'''
