# coding:utf-8
"""简约自绘面板体系：窗口框架 + 左侧导航 + 设置行 + 基础控件

完全脱离 qfluentwidgets 组件，纯 PySide6 + QSS 自绘。
"""
from PySide6.QtCore import (Qt, Signal, QPoint, QSize, QPointF, QRectF,
                            QPropertyAnimation, QEasingCurve, QAbstractAnimation)
from PySide6.QtGui import QIcon, QColor, QPainter, QPen
from PySide6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                               QStackedWidget, QPushButton, QCheckBox, QSlider,
                               QComboBox, QLineEdit, QListWidget, QListWidgetItem,
                               QScrollBar, QScrollArea, QApplication,
                               QGraphicsDropShadowEffect)

from qfluentwidgets import isDarkTheme

from DyberPet.style import palette
from DyberPet.style.theme import active_palette, UI_FONT

try:
    import qtawesome as qta
except ImportError:
    qta = None

_SHADOW = 16          # 窗口阴影留白
_PANEL_RADIUS = 12    # 窗口圆角
_NAV_WIDTH = 200      # 导航栏宽度
_NAV_ITEM_H = 40      # 导航项高度


# ============================================================
#    样式构建
# ============================================================

def _icon(name, dark=None, color=None):
    """Font Awesome 图标，颜色随主题"""
    if qta is None:
        return QIcon()
    if color is None:
        dark = isDarkTheme() if dark is None else dark
        color = '#FFFFFF' if dark else '#000000'
    return qta.icon(name, color=color)


def _panel_qss(dark=None):
    """窗口框架 + 导航 QSS"""
    p = active_palette(dark)
    return f'''
QFrame#panelContainer {{
    background-color: {p['bg']};
    border: 1px solid {p['border']};
    border-radius: {_PANEL_RADIUS}px;
}}
QLabel#panelTitle {{
    color: {p['text']};
    font: 600 15px {UI_FONT};
    background: transparent;
}}
QFrame#navPanel {{
    background-color: transparent;
    border-right: 1px solid {p['border']};
}}
QFrame#navItem {{
    border: none;
    background-color: transparent;
}}
QFrame#navIconBox {{
    border: none;
    border-radius: 10px;
    background-color: transparent;
}}
QFrame#navItem:hover QFrame#navIconBox {{ background-color: {p['hover']}; }}
QFrame#navItem[selected="true"] QFrame#navIconBox {{ background-color: rgba(232, 135, 74, 0.15); }}
QFrame#navItem[selected="true"]:hover QFrame#navIconBox {{ background-color: rgba(232, 135, 74, 0.22); }}
QLabel#navItemText {{ background: transparent; font: 14px {UI_FONT}; }}
QLabel#navItemText[selected="true"] {{ color: {p['primary']}; font-weight: 600; }}
QLabel#navItemText[selected="false"] {{ color: {p['text']}; }}
QPushButton#titleButton {{
    border: none; border-radius: 6px;
    background-color: transparent;
}}
QPushButton#titleButton:hover {{ background-color: {p['hover']}; }}
QPushButton#titleButton:pressed {{ background-color: {p['active']}; }}
'''


def _setting_row_qss(dark=None):
    """设置行 QSS"""
    p = active_palette(dark)
    return f'''
QFrame#settingRow {{
    background-color: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 10px;
}}
QLabel#settingRowTitle {{
    color: {p['text']};
    font: 600 14px {UI_FONT};
    background: transparent;
}}
QLabel#settingRowContent {{
    color: {p['textSecondary']};
    font: 12px {UI_FONT};
    background: transparent;
}}
'''


def scrollbar_qss(dark=None):
    """简约滚动条 QSS（各页面统一使用）"""
    p = active_palette(dark)
    return f'''
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {p['textDisabled']};
    border-radius: 4px;
    min-height: 24px;
    margin: 6px 0;
}}
QScrollBar::handle:vertical:hover {{ background: {p['textSecondary']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; width: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {p['textDisabled']};
    border-radius: 4px;
    min-width: 24px;
    margin: 0 6px;
}}
QScrollBar::handle:horizontal:hover {{ background: {p['textSecondary']}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ height: 0; width: 0; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}
'''


def _controls_qss(dark=None):
    """基础控件 QSS（开关/滑块/下拉/输入框）"""
    p = active_palette(dark)
    return f'''
QCheckBox#sSwitch {{ background: transparent; spacing: 10px; min-height: 24px; }}
QCheckBox#sSwitch::indicator {{
    width: 22px; height: 22px;
    border-radius: 6px;
    border: 1.5px solid {p['border']};
    background-color: {p['card']};
    subcontrol-origin: content;
    subcontrol-position: center;
}}
QCheckBox#sSwitch::indicator:checked {{
    background-color: {p['primary']};
    border-color: {p['primary']};
}}
QCheckBox#sSwitch::indicator:disabled {{
    background-color: {p['hover']};
    border-color: {p['border']};
}}
/* 正方形开关：基于 QPushButton checkable，整个 widget 是软角方块 */
QPushButton#sSwitch {{
    border: 1.5px solid {p['border']};
    border-radius: 6px;
    background-color: {p['card']};
    padding: 0px;
    min-width: 24px; max-width: 24px;
    min-height: 24px; max-height: 24px;
}}
QPushButton#sSwitch:hover {{ border-color: {p['textSecondary']}; }}
QPushButton#sSwitch:checked {{
    background-color: {p['primary']};
    border-color: {p['primary']};
}}
QPushButton#sSwitch:disabled {{
    background-color: {p['hover']};
    border-color: {p['border']};
}}

QSlider::groove:horizontal {{
    height: 4px; border-radius: 2px;
    background-color: {p['active']};
}}
QSlider::sub-page:horizontal {{
    background: {p['primary']}; border-radius: 2px;
}}
QSlider::handle:horizontal {{
    width: 16px; height: 16px; margin: -6px 0;
    border-radius: 8px;
    background: {p['card']};
    border: 1px solid {p['primary']};
}}
QSlider::handle:horizontal:hover {{ background-color: {p['primaryHover']}; }}

QComboBox#sCombo, QLineEdit#sLineEdit {{
    border: 1px solid {p['border']};
    border-radius: 6px;
    background-color: {p['card']};
    padding: 4px 10px;
    color: {p['text']};
    font: 13px {UI_FONT};
    min-height: 26px;
}}
QComboBox#sCombo:focus, QLineEdit#sLineEdit:focus {{ border-color: {p['primary']}; }}
QComboBox#sCombo::drop-down {{ border: none; width: 24px; }}

QScrollArea, QScrollArea > QWidget > QWidget {{ border: none; background: transparent; }}
''' + scrollbar_qss(dark)


# ============================================================
#    窗口框架
# ============================================================

class _TitleBar(QWidget):
    """可拖拽标题栏"""

    def __init__(self, title='', parent=None):
        super().__init__(parent)
        self._drag = False
        self._dragPos = QPoint()
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 10, 0)
        layout.setSpacing(4)

        self.titleLabel = QLabel(title, self)
        self.titleLabel.setObjectName('panelTitle')
        self.minButton = QPushButton(self)
        self.closeButton = QPushButton(self)
        for b in (self.minButton, self.closeButton):
            b.setObjectName('titleButton')
            b.setFixedSize(28, 28)
            b.setCursor(Qt.PointingHandCursor)
            b.setIconSize(QSize(13, 13))
        self.minButton.clicked.connect(self.window().showMinimized)
        self.closeButton.clicked.connect(self.window().close)

        layout.addWidget(self.titleLabel)
        layout.addStretch(1)
        layout.addWidget(self.minButton)
        layout.addWidget(self.closeButton)

        self._applyStyle()

    def _applyStyle(self):
        dark = isDarkTheme()
        c = '#FFFFFF' if dark else '#000000'
        self.minButton.setIcon(_icon('fa5s.minus', dark))
        self.closeButton.setIcon(_icon('fa5s.times', dark))
        _ = c

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = True
            self._dragPos = e.globalPos() - self.window().frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if self._drag:
            self.window().move(e.globalPos() - self._dragPos)
            e.accept()

    def mouseReleaseEvent(self, e):
        self._drag = False
        e.accept()


class SimpleWindow(QWidget):
    """简约自绘窗口：无边框 + 圆角 + 阴影 + 可拖拽标题栏"""

    def __init__(self, title='', width=900, height=680, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(width, height)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(_SHADOW, _SHADOW, _SHADOW, _SHADOW)

        self._container = QFrame(self)
        self._container.setObjectName('panelContainer')
        self._container.setStyleSheet(_panel_qss())
        outer.addWidget(self._container)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.titleBar = _TitleBar(title, self._container)
        layout.addWidget(self.titleBar)

        self._content = QWidget(self._container)
        layout.addWidget(self._content, 1)

        shadow = QGraphicsDropShadowEffect(self._container)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 60))
        self._container.setGraphicsEffect(shadow)

    def contentWidget(self):
        return self._content

    def setWindowTitle(self, title):
        super().setWindowTitle(title)
        self.titleBar.titleLabel.setText(title)

    def _applyStyle(self):
        self._container.setStyleSheet(_panel_qss())
        self.titleBar._applyStyle()


class NavItem(QFrame):
    """简约导航项：图标 + 文字 + hover / 选中态"""
    clicked = Signal()

    def __init__(self, icon_name, text, parent=None):
        super().__init__(parent)
        self.setObjectName('navItem')
        self.setFixedHeight(_NAV_ITEM_H)
        self.setCursor(Qt.PointingHandCursor)

        self._iconName = icon_name
        self._text = text
        self._selected = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 12, 0)
        layout.setSpacing(10)

        # 正方形软角图标块：hover/选中的背景框
        self._iconBox = QFrame(self)
        self._iconBox.setObjectName('navIconBox')
        self._iconBox.setFixedSize(34, 34)
        iconLayout = QHBoxLayout(self._iconBox)
        iconLayout.setContentsMargins(0, 0, 0, 0)
        self._iconLabel = QLabel(self._iconBox)
        self._iconLabel.setFixedSize(18, 18)
        self._iconLabel.setAlignment(Qt.AlignCenter)
        iconLayout.addWidget(self._iconLabel)

        self._textLabel = QLabel(text, self)
        self._textLabel.setObjectName('navItemText')
        layout.addWidget(self._iconBox)
        layout.addWidget(self._textLabel, 1)

        self._applyStyle()

    def _applyStyle(self):
        dark = isDarkTheme()
        p = palette.DARK if dark else palette.LIGHT
        self.setStyleSheet(_panel_qss(dark))
        if qta is not None:
            color = p['primary'] if self._selected else ('#FFFFFF' if dark else '#000000')
            self._iconLabel.setPixmap(_icon(self._iconName, dark, color).pixmap(18, 18))
        self._textLabel.setProperty('selected', 'true' if self._selected else 'false')
        self._textLabel.style().unpolish(self._textLabel)
        self._textLabel.style().polish(self._textLabel)
        # 重新触发属性选择器
        self.style().unpolish(self)
        self.style().polish(self)

    def setSelected(self, selected):
        self._selected = selected
        self.setProperty('selected', 'true' if selected else 'false')
        self._applyStyle()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()
            e.accept()


class SideNavWindow(SimpleWindow):
    """带左侧简约导航的自绘窗口"""

    def __init__(self, title='', width=900, height=680, parent=None):
        super().__init__(title, width, height, parent)
        self._navItems = []
        self._pageItems = {}

        body = QHBoxLayout(self.contentWidget())
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._navPanel = QFrame(self.contentWidget())
        self._navPanel.setObjectName('navPanel')
        self._navPanel.setFixedWidth(_NAV_WIDTH)
        self._navLayout = QVBoxLayout(self._navPanel)
        self._navLayout.setContentsMargins(8, 8, 8, 8)
        self._navLayout.setSpacing(2)
        self._navLayout.addStretch(1)

        self._stack = QStackedWidget(self.contentWidget())

        body.addWidget(self._navPanel)
        body.addWidget(self._stack, 1)

    def addSubInterface(self, widget, icon_name, text):
        """添加导航页"""
        item = NavItem(icon_name, text, self._navPanel)
        self._navItems.append(item)
        self._pageItems[widget] = item
        self._navLayout.insertWidget(self._navLayout.count() - 1, item)
        self._stack.addWidget(widget)
        item.clicked.connect(lambda: self._selectPage(widget, item))
        if len(self._navItems) == 1:
            item.setSelected(True)
            self._stack.setCurrentWidget(widget)
        return widget

    def _selectPage(self, widget, item):
        self._stack.setCurrentWidget(widget)
        for it in self._navItems:
            it.setSelected(it is item)

    def switchTo(self, widget):
        """切换到指定页面（widget 必须是已注册的页面）"""
        item = self._pageItems.get(widget)
        if item is not None:
            self._selectPage(widget, item)

    def switch_to(self, page_name):
        pass  # 子类可重写

    def closeEvent(self, e):
        e.ignore()
        self.hide()


# ============================================================
#    设置行与基础控件
# ============================================================

class SettingRow(QFrame):
    """简约设置行：图标 + 标题 + 描述 + 右侧控件"""

    def __init__(self, icon_name, title, content=None, parent=None):
        super().__init__(parent)
        self.setObjectName('settingRow')
        self.setStyleSheet(_setting_row_qss())

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self._iconLabel = QLabel(self)
        self._iconLabel.setFixedSize(18, 18)
        dark = isDarkTheme()
        self._iconLabel.setPixmap(_icon(icon_name, dark).pixmap(18, 18))
        layout.addWidget(self._iconLabel)

        textBox = QVBoxLayout()
        textBox.setSpacing(2)
        self.titleLabel = QLabel(title, self)
        self.titleLabel.setObjectName('settingRowTitle')
        textBox.addWidget(self.titleLabel)
        self.contentLabel = None
        if content:
            self.contentLabel = QLabel(content, self)
            self.contentLabel.setObjectName('settingRowContent')
            textBox.addWidget(self.contentLabel)
        layout.addLayout(textBox, 1)

        self._widgetLayout = QHBoxLayout()
        self._widgetLayout.setSpacing(8)
        layout.addLayout(self._widgetLayout)

    def addWidget(self, widget):
        """在行右侧加入控件"""
        self._widgetLayout.addWidget(widget)

    def addWidgets(self, widgets):
        for w in widgets:
            self.addWidget(w)

    def setTitle(self, title):
        self.titleLabel.setText(title)

    def setContent(self, content):
        if self.contentLabel is not None:
            self.contentLabel.setText(content)


class SSwitch(QPushButton):
    """简约正方形开关（QPushButton checkable，22×22 软角方块，checked 暖橙）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('sSwitch')
        self.setCheckable(True)
        self.setFixedSize(22, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(_controls_qss())


class SSlider(QSlider):
    """简约滑块"""

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet(_controls_qss())


class _ComboPopup(QFrame):
    """简约下拉弹窗：自绘列表（不用 QListWidget / 阴影，避免 Windows layered-window 报错）"""
    itemSelected = Signal(str)

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._items = list(items)
        self._itemWidgets = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)
        for i, t in enumerate(self._items):
            item = QFrame(self)
            item.setObjectName('comboItem')
            item.setFixedHeight(32)
            item.setCursor(Qt.PointingHandCursor)
            lbl = QLabel(t, item)
            lbl.setObjectName('comboItemText')
            il = QHBoxLayout(item)
            il.setContentsMargins(12, 0, 12, 0)
            il.addWidget(lbl)
            item.mousePressEvent = lambda e, idx=i: self._select(idx)
            layout.addWidget(item)
            self._itemWidgets.append(item)
        self._applyStyle()
        self._setCurrent(0)

    def _applyStyle(self):
        dark = isDarkTheme()
        p = palette.DARK if dark else palette.LIGHT
        # 背景/边框由 paintEvent 直接绘制（顶级 popup 的 QSS background 不生效）
        self._card = p['card']
        self._border = p['border']
        self.setStyleSheet(f'''
            QFrame#comboItem {{ background-color: transparent; border-radius: 6px; }}
            QFrame#comboItem:hover {{ background-color: {p['hover']}; }}
            QFrame#comboItem[selected="true"] {{
                background-color: rgba(232, 135, 74, 0.15);
            }}
            QLabel#comboItemText {{
                color: {p['text']};
                font: 13px {UI_FONT};
                background: transparent;
            }}
            QLabel#comboItemText[selected="true"] {{ color: {p['primary']}; }}
        ''')

    def paintEvent(self, e):
        """自绘不透明圆角背景（顶级 popup 的 QSS background 在 translucent 下不生效）"""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        p.setPen(QPen(QColor(self._border), 1))
        p.setBrush(QColor(self._card))
        p.drawRoundedRect(rect, 8, 8)
        p.end()

    def _setCurrent(self, i):
        for idx, w in enumerate(self._itemWidgets):
            selected = (idx == i)
            w.setProperty('selected', 'true' if selected else 'false')
            w.style().unpolish(w)
            w.style().polish(w)

    def setCurrent(self, i):
        if 0 <= i < len(self._items):
            self._setCurrent(i)

    def _select(self, idx):
        self.itemSelected.emit(self._items[idx])
        self.close()

    def showAt(self, pos, width):
        self.adjustSize()
        self.setFixedWidth(max(width, self.width()))
        screen = QApplication.screenAt(pos) or QApplication.primaryScreen()
        if screen is not None:
            rect = screen.availableGeometry()
            x = min(pos.x(), rect.right() - self.width())
            y = min(pos.y(), rect.bottom() - self.height())
            self.move(max(x, rect.left()), max(y, rect.top()))
        else:
            self.move(pos)
        self.show()
        self.raise_()


class SComboBox(QWidget):
    """自绘简约下拉框：显示框 + 弹出简约列表"""
    currentTextChanged = Signal(str)
    activated = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current = -1
        self._popup = None

        self._button = QFrame(self)
        self._button.setObjectName('sCombo')
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.mousePressEvent = lambda e: self._togglePopup()
        btnLayout = QHBoxLayout(self._button)
        btnLayout.setContentsMargins(10, 0, 8, 0)
        btnLayout.setSpacing(8)
        self._textLabel = QLabel('', self._button)
        self._textLabel.setObjectName('sComboText')
        self._arrowLabel = QLabel('', self._button)
        self._arrowLabel.setFixedSize(12, 12)
        btnLayout.addWidget(self._textLabel)
        btnLayout.addStretch(1)
        btnLayout.addWidget(self._arrowLabel)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._button)
        self.setFixedHeight(34)

        self._applyStyle()

    def _applyStyle(self):
        dark = isDarkTheme()
        p = palette.DARK if dark else palette.LIGHT
        self._button.setStyleSheet(f'''
            QFrame#sCombo {{
                border: 1px solid {p['border']};
                border-radius: 6px;
                background-color: {p['card']};
            }}
            QFrame#sCombo:hover {{ border-color: {p['textSecondary']}; }}
            QFrame#sCombo:pressed {{ background-color: {p['hover']}; }}
            QLabel#sComboText {{
                color: {p['text']};
                font: 13px {UI_FONT};
                background: transparent;
            }}
        ''')
        if qta is not None:
            c = '#FFFFFF' if dark else '#000000'
            self._arrowLabel.setPixmap(qta.icon('fa5s.caret-down', color=c).pixmap(12, 12))

    # ---------- API（兼容 QComboBox） ----------
    def addItems(self, items):
        self._items = list(items)
        if self._current < 0 and self._items:
            self.setCurrentIndex(0)

    def addItem(self, text, userData=None):
        self._items.append(text)
        if self._current < 0:
            self.setCurrentIndex(0)

    def clear(self):
        self._items.clear()
        self._current = -1
        self._textLabel.setText('')

    def setCurrentIndex(self, i):
        if 0 <= i < len(self._items):
            self._current = i
            self._textLabel.setText(self._items[i])

    def setCurrentText(self, text):
        if text in self._items:
            self.setCurrentIndex(self._items.index(text))

    def currentIndex(self):
        return self._current

    def currentText(self):
        return self._items[self._current] if 0 <= self._current < len(self._items) else ''

    def _togglePopup(self):
        if not self._items:
            return
        if self._popup is None:
            self._popup = _ComboPopup(self._items, self)
            self._popup.itemSelected.connect(self._onItemSelected)
        self._popup.setCurrent(self._current)
        self._popup.showAt(self.mapToGlobal(QPoint(0, self.height() + 4)), self.width())

    def _onItemSelected(self, text):
        idx = self._items.index(text)
        if idx != self._current:
            self._current = idx
            self._textLabel.setText(text)
            self.currentTextChanged.emit(text)
            self.activated.emit(idx)


class SLineEdit(QLineEdit):
    """简约输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('sLineEdit')
        self.setStyleSheet(_controls_qss())


# ============================================================
#    自绘圆形滚动条
# ============================================================

class SScrollBar(QScrollBar):
    """自绘滚动条：胶囊滑块按内容比例伸缩，轨道透明，两端留白，永不裁切"""

    def __init__(self, orientation=Qt.Vertical, parent=None):
        super().__init__(orientation, parent)
        self._hover = False
        self.setObjectName('sScrollBar')
        if orientation == Qt.Vertical:
            self.setFixedWidth(8)
        else:
            self.setFixedHeight(8)

    def enterEvent(self, e):
        self._hover = True
        self.update()
        return super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self.update()
        return super().leaveEvent(e)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        dark = isDarkTheme()
        pal = palette.DARK if dark else palette.LIGHT
        color = QColor(pal['textSecondary'] if self._hover else pal['textDisabled'])
        rng = self.maximum() - self.minimum()
        if rng <= 0:
            return
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        # 滑块长度 = 视口/内容比例，内容少时接近满轨；两端 pad 留白不贴边
        w, pad, min_h = 6, 6, 28
        r = w / 2
        if self.orientation() == Qt.Vertical:
            track = self.height() - pad * 2
            total = rng + self.pageStep()
            fh = max(min_h, track * min(1.0, self.pageStep() / total))
            avail = track - fh
            frac = (self.sliderPosition() - self.minimum()) / rng
            y = pad + frac * avail
            p.drawRoundedRect(QRectF(self.width() / 2 - w / 2, y, w, fh), r, r)
        else:
            track = self.width() - pad * 2
            total = rng + self.pageStep()
            fw = max(min_h, track * min(1.0, self.pageStep() / total))
            avail = track - fw
            frac = (self.sliderPosition() - self.minimum()) / rng
            x = pad + frac * avail
            p.drawRoundedRect(QRectF(x, self.height() / 2 - w / 2, fw, w), r, r)
        p.end()


class SScrollArea(QScrollArea):
    """自带自绘滚动条 + 平滑滚轮动画的滚动区"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBar(SScrollBar(Qt.Vertical, self))
        self.setHorizontalScrollBar(SScrollBar(Qt.Horizontal, self))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._vAni = QPropertyAnimation(self.verticalScrollBar(), b'value', self)
        self._vAni.setDuration(220)
        self._vAni.setEasingCurve(QEasingCurve.OutCubic)

    def wheelEvent(self, e):
        bar = self.verticalScrollBar()
        dy = e.angleDelta().y()
        if dy == 0 or bar.maximum() <= 0:
            super().wheelEvent(e)
            return
        if self._vAni.state() == QAbstractAnimation.Running:
            self._vAni.stop()
        # 平滑步长：一档滚轮滚 ~40% 页高，动画过渡消除跳变
        step = max(40.0, bar.pageStep() * 0.4)
        target = bar.value() - (dy / 120) * step
        target = max(bar.minimum(), min(bar.maximum(), target))
        self._vAni.setStartValue(bar.value())
        self._vAni.setEndValue(target)
        self._vAni.start()
        e.accept()
