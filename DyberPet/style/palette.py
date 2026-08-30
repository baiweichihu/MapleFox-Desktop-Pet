# coding:utf-8
"""MapleFox 简约 UI 设计令牌（Design Tokens）

风格：现代卡片式简约
- 浅灰底 + 白色圆角卡片 + 细分割线 + 柔和阴影（类 Notion/Arc）
- 暖橙主色，呼应 MapleFox 狐狸
- 保留浅/深双主题

颜色值约定：
- 十六进制字符串（#RRGGBB）：直接用于 QSS 与 QColor
- 元组 (r, g, b, a)：带透明度的颜色，QSS 中由 theme.qss_color 转 rgba()，
  代码中可直接 QColor(*color)
"""

# 浅色主题
LIGHT = {
    'bg': '#F7F8FA',             # 窗口背景
    'card': '#FFFFFF',           # 卡片背景
    'border': '#E8EAED',         # 分割线 / 边框
    'text': '#1F2329',           # 正文
    'textSecondary': '#8A919F',  # 次要文本
    'textDisabled': '#B4BAC4',   # 禁用文本
    'hover': '#F2F3F5',          # 悬停背景
    'active': '#E9EBEF',         # 按压 / 选中背景
    'primary': '#E8874A',        # 主色（暖橙）
    'primaryHover': '#F2A068',   # 主色悬停
    'primaryPressed': '#D97B3A',  # 主色按压
    'onPrimary': '#FFFFFF',      # 主色上的文本
    'menuBg': '#FFFFFF',         # 菜单背景
    'menuBorder': '#E8EAED',     # 菜单边框
    'itemHover': '#F2F3F5',      # 菜单项悬停
    'itemSelected': '#F2F3F5',   # 菜单项选中
    'separator': (31, 35, 41, 20),   # 分隔线
    'shortcut': '#8A919F',       # 快捷键文本
    'shadow': (0, 0, 0, 15),     # 卡片阴影
}

# 深色主题
DARK = {
    'bg': '#1E2024',
    'card': '#26282D',
    'border': '#34373D',
    'text': '#E8EAED',
    'textSecondary': '#9DA3AD',
    'textDisabled': '#6B7178',
    'hover': '#2F3238',
    'active': '#383C42',
    'primary': '#E8874A',
    'primaryHover': '#F2A068',
    'primaryPressed': '#D97B3A',
    'onPrimary': '#FFFFFF',
    'menuBg': '#26282D',
    'menuBorder': '#34373D',
    'itemHover': '#2F3238',
    'itemSelected': '#2F3238',
    'separator': (232, 234, 237, 20),
    'shortcut': '#9DA3AD',
    'shadow': (0, 0, 0, 60),
}
