# coding:utf-8
import math
from enum import Enum
from typing import List, Union

from qframelesswindow import WindowEffect
from PySide6.QtCore import (QEasingCurve, QEvent, QPropertyAnimation, QObject, QModelIndex,
                          Qt, QSize, QRectF, QPointF, Signal, QPoint, QTimer, QObject, QParallelAnimationGroup)
from PySide6.QtGui import (QAction, QIcon, QColor, QPainter, QPainterPath, QPen, QPixmap, QRegion, QCursor,
                           QTextCursor, QHoverEvent, QFontMetrics, QKeySequence)
from PySide6.QtWidgets import (QApplication, QMenu, QProxyStyle, QStyle,
                               QGraphicsDropShadowEffect, QListWidget, QWidget, QHBoxLayout,
                               QListWidgetItem, QLineEdit, QTextEdit, QStyledItemDelegate, QStyleOptionViewItem,
                               QFrame, QLabel, QVBoxLayout)

from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.common.icon import FluentIconEngine, Action, FluentIconBase, Icon
from qfluentwidgets.common.style_sheet import FluentStyleSheet, themeColor, setCustomStyleSheet
from qfluentwidgets.common.font import getFont
from qfluentwidgets.common.config import isDarkTheme
from qfluentwidgets.components.widgets.scroll_bar import SmoothScrollDelegate
from qfluentwidgets.common.screen import getCurrentScreenGeometry

from DyberPet.style import palette
from DyberPet.style.theme import menu_qss, UI_FONT

try:
    import qtawesome as qta
except ImportError:
    qta = None

class CustomMenuStyle(QProxyStyle):
    """ Custom menu style """

    def __init__(self, iconSize=14):
        """
        Parameters
        ----------
        iconSizeL int
            the size of icon
        """
        super().__init__()
        self.iconSize = iconSize

    def pixelMetric(self, metric, option, widget):
        if metric == QStyle.PM_SmallIconSize:
            return self.iconSize

        return super().pixelMetric(metric, option, widget)


class DWMMenu(QMenu):
    """ A menu with DWM shadow """

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.windowEffect = WindowEffect(self)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyle(CustomMenuStyle())
        FluentStyleSheet.MENU.apply(self)
        setCustomStyleSheet(self, menu_qss(dark=False), menu_qss(dark=True))

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.windowEffect.addMenuShadowEffect(self.winId())
        return QMenu.event(self, e)


class MenuAnimationType(Enum):
    """ Menu animation type """

    NONE = 0
    DROP_DOWN = 1
    PULL_UP = 2
    FADE_IN_DROP_DOWN = 3
    FADE_IN_PULL_UP = 4



class SubMenuItemWidget(QWidget):
    """ Sub menu item """

    showMenuSig = Signal(QListWidgetItem)

    def __init__(self, menu, item, parent=None):
        """
        Parameters
        ----------
        menu: QMenu | FluentRoundMenu
            sub menu

        item: QListWidgetItem
            menu item

        parent: QWidget
            parent widget
        """
        super().__init__(parent)
        self.menu = menu
        self.item = item

    def enterEvent(self, e):
        super().enterEvent(e)
        self.showMenuSig.emit(self.item)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        # draw right arrow
        FIF.CHEVRON_RIGHT.render(painter, QRectF(
            self.width()-10, self.height()/2-9/2, 9, 9))


class MenuItemDelegate(QStyledItemDelegate):
    """ Menu item delegate """

    def _isSeparator(self, index: QModelIndex):
        return index.model().data(index, Qt.DecorationRole) == "seperator"

    def paint(self, painter, option, index):
        if not self._isSeparator(index):
            return super().paint(painter, option, index)

        # draw seperator
        painter.save()

        sep = palette.DARK['separator'] if isDarkTheme() else palette.LIGHT['separator']
        pen = QPen(QColor(*sep), 1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        rect = option.rect
        painter.drawLine(0, rect.y() + 4, rect.width() + 12, rect.y() + 4)

        painter.restore()


class ShortcutMenuItemDelegate(MenuItemDelegate):
    """ Shortcut key menu item delegate """

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        super().paint(painter, option, index)
        if self._isSeparator(index):
            return

        # draw shortcut key
        action = index.data(Qt.UserRole)  # type: QAction
        if not isinstance(action, QAction) or action.shortcut().isEmpty():
            return

        painter.save()

        if not option.state & QStyle.State_Enabled:
            painter.setOpacity(0.5 if isDarkTheme() else 0.6)

        font = getFont(12)
        painter.setFont(font)
        sc = palette.DARK['shortcut'] if isDarkTheme() else palette.LIGHT['shortcut']
        painter.setPen(QColor(sc))

        fm = QFontMetrics(font)
        shortcut = action.shortcut().toString(QKeySequence.NativeText)

        sw = fm.boundingRect(shortcut).width()
        painter.translate(option.rect.width()-sw-20, 0)

        rect = QRectF(0, option.rect.y(), sw, option.rect.height())
        painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, shortcut)

        painter.restore()


class MenuActionListWidget(QListWidget):
    """ Menu action list widget """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._itemHeight = 28
        self._maxVisibleItems = -1  # adjust visible items according to the size of screen

        self.setViewportMargins(0, 6, 0, 6)
        self.setTextElideMode(Qt.ElideNone)
        self.setDragEnabled(False)
        self.setMouseTracking(True)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)
        self.setIconSize(QSize(14, 14))
        self.setItemDelegate(ShortcutMenuItemDelegate(self))

        self.scrollDelegate = SmoothScrollDelegate(self)
        self.setStyleSheet(
            'MenuActionListWidget{font: 14px "Segoe UI", "Microsoft YaHei", "PingFang SC"}')

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def insertItem(self, row, item):
        """ inserts menu item at the position in the list given by row """
        super().insertItem(row, item)
        self.adjustSize()

    def addItem(self, item):
        """ add menu item at the end """
        super().addItem(item)
        self.adjustSize()

    def takeItem(self, row):
        """ delete item from list """
        item = super().takeItem(row)
        self.adjustSize()
        return item

    def adjustSize(self, pos=None, aniType=MenuAnimationType.NONE):
        size = QSize()
        for i in range(self.count()):
            s = self.item(i).sizeHint()
            size.setWidth(max(s.width(), size.width(), 1))
            size.setHeight(max(1, size.height() + s.height()))

        # adjust the height of viewport
        w, h = MenuAnimationManager.make(self, aniType).availableViewSize(pos)
        self.viewport().adjustSize()

        # adjust the height of list widget
        m = self.viewportMargins()
        size += QSize(m.left()+m.right()+2, m.top()+m.bottom())
        size.setHeight(min(h, size.height()+3))
        size.setWidth(max(min(w, size.width()), self.minimumWidth()))

        if self.maxVisibleItems() > 0:
            size.setHeight(min(
                size.height(), self.maxVisibleItems() * self._itemHeight + m.top()+m.bottom() + 3))

        self.setFixedSize(size)

    def setItemHeight(self, height: int):
        """ set the height of item """
        if height == self._itemHeight:
            return

        for i in range(self.count()):
            item = self.item(i)
            if not self.itemWidget(item):
                item.setSizeHint(QSize(item.sizeHint().width(), height))

        self._itemHeight = height
        self.adjustSize()

    def setMaxVisibleItems(self, num: int):
        """ set the maximum visible items """
        self._maxVisibleItems = num
        self.adjustSize()

    def maxVisibleItems(self):
        return self._maxVisibleItems

    def heightForAnimation(self, pos: QPoint, aniType: MenuAnimationType):
        """ height for animation """
        ih = self.itemsHeight()
        _, sh = MenuAnimationManager.make(self, aniType).availableViewSize(pos)
        return min(ih, sh)

    def itemsHeight(self):
        """ Return the height of all items """
        N = self.count() if self.maxVisibleItems() < 0 else min(self.maxVisibleItems(), self.count())
        h = sum(self.item(i).sizeHint().height() for i in range(N))
        m = self.viewportMargins()
        return h + m.top() + m.bottom()


class FluentRoundMenu(QMenu):
    """ Round corner menu """

    closedSignal = Signal()

    def __init__(self, title="", parent=None):
        super().__init__(parent=parent)
        self._title = title
        self._icon = QIcon()
        self._actions = []  # type: List[QAction]
        self._subMenus = []

        self.isSubMenu = False
        self.parentMenu = None
        self.menuItem = None
        self.lastHoverItem = None
        self.lastHoverSubMenuItem = None
        self.isHideBySystem = True
        self.itemHeight = 28

        self.hBoxLayout = QHBoxLayout(self)
        self.view = MenuActionListWidget(self)

        self.aniManager = None
        self.timer = QTimer(self)

        self.__initWidgets()

    def __initWidgets(self):
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint |
                            Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.timer.setSingleShot(True)
        self.timer.setInterval(400)
        self.timer.timeout.connect(self._onShowMenuTimeOut)

        self.setShadowEffect()
        self.hBoxLayout.addWidget(self.view, 1, Qt.AlignCenter)

        self.hBoxLayout.setContentsMargins(12, 8, 12, 20)
        FluentStyleSheet.MENU.apply(self)
        setCustomStyleSheet(self, menu_qss(dark=False), menu_qss(dark=True))

        self.view.itemClicked.connect(self._onItemClicked)
        self.view.itemEntered.connect(self._onItemEntered)

    def setMaxVisibleItems(self, num: int):
        """ set the maximum visible items """
        self.view.setMaxVisibleItems(num)
        self.adjustSize()

    def setItemHeight(self, height):
        """ set the height of menu item """
        if height == self.itemHeight:
            return

        self.itemHeight = height
        self.view.setItemHeight(height)

    def setShadowEffect(self, blurRadius=30, offset=(0, 8), color=QColor(0, 0, 0, 30)):
        """ add shadow to dialog """
        self.shadowEffect = QGraphicsDropShadowEffect(self.view)
        self.shadowEffect.setBlurRadius(blurRadius)
        self.shadowEffect.setOffset(*offset)
        self.shadowEffect.setColor(color)
        self.view.setGraphicsEffect(None)
        self.view.setGraphicsEffect(self.shadowEffect)

    def _setParentMenu(self, parent, item):
        self.parentMenu = parent
        self.menuItem = item
        self.isSubMenu = True if parent else False

    def adjustSize(self):
        m = self.layout().contentsMargins()
        w = self.view.width() + m.left() + m.right()
        h = self.view.height() + m.top() + m.bottom()
        self.setFixedSize(w, h)

    def icon(self):
        return self._icon

    def title(self):
        return self._title

    def clear(self):
        """ clear all actions """
        for i in range(len(self._actions)-1, -1, -1):
            self.removeAction(self._actions[i])

    def setIcon(self, icon: Union[QIcon, FluentIconBase]):
        """ set the icon of menu """
        if isinstance(icon, FluentIconBase):
            icon = Icon(icon)

        self._icon = icon

    def addAction(self, action: Union[QAction, Action]):
        """ add action to menu

        Parameters
        ----------
        action: QAction
            menu action
        """
        item = self._createActionItem(action)
        self.view.addItem(item)
        self.adjustSize()

    def addWidget(self, widget: QWidget, selectable=True, onClick=None):
        """ add custom widget

        Parameters
        ----------
        widget: QWidget
            custom widget

        selectable: bool
            whether the menu item is selectable

        onClick: callable
            the slot connected to item clicked signal
        """
        action = QAction()
        action.setProperty('selectable', selectable)

        item = self._createActionItem(action)
        item.setSizeHint(widget.size())

        self.view.addItem(item)
        self.view.setItemWidget(item, widget)

        if not selectable:
            item.setFlags(Qt.NoItemFlags)

        if onClick:
            action.triggered.connect(onClick)

        self.adjustSize()

    def _createActionItem(self, action: QAction, before=None):
        """ create menu action item  """
        if not before:
            self._actions.append(action)
            super().addAction(action)
        elif before in self._actions:
            index = self._actions.index(before)
            self._actions.insert(index, action)
            super().insertAction(before, action)
        else:
            raise ValueError('`before` is not in the action list')

        item = QListWidgetItem(self._createItemIcon(action), action.text())
        self._adjustItemText(item, action)

        # disable item if the action is not enabled
        if not action.isEnabled():
            item.setFlags(Qt.NoItemFlags)

        item.setData(Qt.UserRole, action)
        action.setProperty('item', item)
        action.changed.connect(self._onActionChanged)
        return item

    def _hasItemIcon(self):
        return any(not i.icon().isNull() for i in self._actions+self._subMenus)

    def _adjustItemText(self, item: QListWidgetItem, action: QAction):
        """ adjust the text of item """
        # leave some space for shortcut key
        if isinstance(self.view.itemDelegate(), ShortcutMenuItemDelegate):
            sw = self._longestShortcutWidth()
            if sw:
                sw += 22
        else:
            sw = 0

        # adjust the width of item
        if not self._hasItemIcon():
            item.setText(action.text())
            w = 40 + self.view.fontMetrics().boundingRect(action.text()).width() + sw
        else:
            # add a blank character to increase space between icon and text
            item.setText(" " + action.text())
            space = 4 - self.view.fontMetrics().boundingRect(" ").width()
            w = 60 + self.view.fontMetrics().boundingRect(item.text()).width() + sw + space

        item.setSizeHint(QSize(w, self.itemHeight))
        return w

    def _longestShortcutWidth(self):
        """ longest shortcut key """
        fm = QFontMetrics(getFont(12))
        return max(fm.boundingRect(a.shortcut().toString()).width() for a in self.menuActions())

    def _createItemIcon(self, w):
        """ create the icon of menu item """
        hasIcon = self._hasItemIcon()
        icon = QIcon(FluentIconEngine(w.icon()))

        if hasIcon and w.icon().isNull():
            pixmap = QPixmap(self.view.iconSize())
            pixmap.fill(Qt.transparent)
            icon = QIcon(pixmap)
        elif not hasIcon:
            icon = QIcon()

        return icon

    def insertAction(self, before: Union[QAction, Action], action: Union[QAction, Action]):
        """ inserts action to menu, before the action before """
        if before not in self._actions:
            return

        beforeItem = before.property('item')
        if not beforeItem:
            return

        index = self.view.row(beforeItem)
        item = self._createActionItem(action, before)
        self.view.insertItem(index, item)
        self.adjustSize()

    def addActions(self, actions: List[Union[QAction, Action]]):
        """ add actions to menu

        Parameters
        ----------
        actions: Iterable[QAction]
            menu actions
        """
        for action in actions:
            self.addAction(action)

    def insertActions(self, before: Union[QAction, Action], actions: List[Union[QAction, Action]]):
        """ inserts the actions actions to menu, before the action before """
        for action in actions:
            self.insertAction(before, action)

    def removeAction(self, action: Union[QAction, Action]):
        """ remove action from menu """
        if action not in self._actions:
            return

        # remove action
        item = action.property("item")
        self._actions.remove(action)
        action.setProperty('item', None)

        if not item:
            return

        # remove item
        self.view.takeItem(self.view.row(item))
        item.setData(Qt.UserRole, None)
        super().removeAction(action)

        # delete widget
        widget = self.view.itemWidget(item)
        if widget:
            widget.deleteLater()

    def setDefaultAction(self, action: Union[QAction, Action]):
        """ set the default action """
        if action not in self._actions:
            return

        item = action.property("item")
        if item:
            self.view.setCurrentItem(item)

    def addMenu(self, menu):
        """ add sub menu

        Parameters
        ----------
        menu: FluentRoundMenu
            sub round menu
        """
        if not isinstance(menu, FluentRoundMenu):
            raise ValueError('`menu` should be an instance of `FluentRoundMenu`.')

        item, w = self._createSubMenuItem(menu)
        self.view.addItem(item)
        self.view.setItemWidget(item, w)
        self.adjustSize()

    def insertMenu(self, before: Union[QAction, Action], menu):
        """ insert menu before action `before` """
        if not isinstance(menu, FluentRoundMenu):
            raise ValueError('`menu` should be an instance of `FluentRoundMenu`.')

        if before not in self._actions:
            raise ValueError('`before` should be in menu action list')

        item, w = self._createSubMenuItem(menu)
        self.view.insertItem(self.view.row(before.property('item')), item)
        self.view.setItemWidget(item, w)
        self.adjustSize()

    def _createSubMenuItem(self, menu):
        self._subMenus.append(menu)

        item = QListWidgetItem(self._createItemIcon(menu), menu.title())
        if not self._hasItemIcon():
            w = 60 + self.view.fontMetrics().boundingRect(menu.title()).width()
        else:
            # add a blank character to increase space between icon and text
            item.setText(" " + item.text())
            w = 72 + self.view.fontMetrics().boundingRect(item.text()).width()

        # add submenu item
        menu._setParentMenu(self, item)
        item.setSizeHint(QSize(w, self.itemHeight))
        item.setData(Qt.UserRole, menu)
        w = SubMenuItemWidget(menu, item, self)
        w.showMenuSig.connect(self._showSubMenu)
        w.resize(item.sizeHint())

        return item, w

    def _showSubMenu(self, item):
        """ show sub menu """
        self.lastHoverItem = item
        self.lastHoverSubMenuItem = item
        # delay 400 ms to anti-shake
        self.timer.stop()
        self.timer.start()

    def _onShowMenuTimeOut(self):
        if self.lastHoverSubMenuItem is None or not self.lastHoverItem is self.lastHoverSubMenuItem:
            return

        w = self.view.itemWidget(self.lastHoverSubMenuItem)

        if w.menu.parentMenu.isHidden():
            return

        pos = w.mapToGlobal(QPoint(w.width()+5, -5))
        w.menu.exec(pos)

    def addSeparator(self):
        """ add seperator to menu """
        m = self.view.viewportMargins()
        w = self.view.width()-m.left()-m.right()

        # add separator to list widget
        item = QListWidgetItem()
        item.setFlags(Qt.NoItemFlags)
        item.setSizeHint(QSize(w, 9))
        self.view.addItem(item)
        item.setData(Qt.DecorationRole, "seperator")
        self.adjustSize()

    def _onItemClicked(self, item):
        action = item.data(Qt.UserRole)  # type: QAction
        if action not in self._actions or not action.isEnabled():
            return

        if self.view.itemWidget(item) and not action.property('selectable'):
            return

        self._hideMenu(False)

        if not self.isSubMenu:
            action.trigger()
            return

        # close parent menu
        self._closeParentMenu()
        action.trigger()

    def _closeParentMenu(self):
        menu = self
        while menu:
            menu.close()
            menu = menu.parentMenu

    def _onItemEntered(self, item):
        self.lastHoverItem = item
        if not isinstance(item.data(Qt.UserRole), FluentRoundMenu):
            return

        self._showSubMenu(item)

    def _hideMenu(self, isHideBySystem=False):
        self.isHideBySystem = isHideBySystem
        self.view.clearSelection()
        if self.isSubMenu:
            self.hide()
        else:
            self.close()

    def hideEvent(self, e):
        #if self.isHideBySystem and self.isSubMenu:
        #    self._closeParentMenu()

        self.isHideBySystem = True
        e.accept()

    def closeEvent(self, e):
        e.accept()
        self.closedSignal.emit()
        self.view.clearSelection()

    def menuActions(self):
        return self._actions

    def mousePressEvent(self, e):
        w = self.childAt(e.pos())
        if (w is not self.view) and (not self.view.isAncestorOf(w)):
            self._hideMenu(True)

    def mouseMoveEvent(self, e):
        if not self.isSubMenu:
            return

        # hide submenu when mouse moves out of submenu item
        pos = e.globalPos()
        view = self.parentMenu.view

        # get the rect of menu item
        margin = view.viewportMargins()
        rect = view.visualItemRect(self.menuItem).translated(view.mapToGlobal(QPoint()))
        rect = rect.translated(margin.left(), margin.top()+2)
        if self.parentMenu.geometry().contains(pos) and not rect.contains(pos) and \
                not self.geometry().contains(pos):
            view.clearSelection()
            self._hideMenu(False)

    def _onActionChanged(self):
        """ action changed slot """
        action = self.sender()  # type: QAction
        item = action.property('item')  # type: QListWidgetItem
        item.setIcon(self._createItemIcon(action))

        self._adjustItemText(item, action)

        if action.isEnabled():
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        else:
            item.setFlags(Qt.NoItemFlags)

        self.view.adjustSize()
        self.adjustSize()

    def exec(self, pos, ani=True, aniType=MenuAnimationType.DROP_DOWN):
        """ show menu

        Parameters
        ----------
        pos: QPoint
            pop-up position

        ani: bool
            Whether to show pop-up animation

        aniType: MenuAnimationType
            menu animation type
        """
        #if self.isVisible():
        #    aniType = MenuAnimationType.NONE

        self.aniManager = MenuAnimationManager.make(self, aniType)
        self.aniManager.exec(pos)

        self.show()

        if self.isSubMenu:
            self.menuItem.setSelected(True)

    def exec_(self, pos: QPoint, ani=True, aniType=MenuAnimationType.DROP_DOWN):
        """ show menu

        Parameters
        ----------
        pos: QPoint
            pop-up position

        ani: bool
            Whether to show pop-up animation

        aniType: MenuAnimationType
            menu animation type
        """
        self.exec(pos, ani, aniType)

    def adjustPosition(self):
        m = self.layout().contentsMargins()
        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        w, h = self.layout().sizeHint().width() + 5, self.layout().sizeHint().height()

        x = min(self.x() - m.left(), rect.right() - w)
        y = self.y()
        if y > rect.bottom() - h:
            y = self.y() - h + m.bottom()

        self.move(x, y)

    def paintEvent(self, e):
        pass


class MenuAnimationManager(QObject):
    """ Menu animation manager """

    managers = {}

    def __init__(self, menu: FluentRoundMenu):
        super().__init__()
        self.menu = menu
        self.ani = QPropertyAnimation(menu, b'pos', menu)

        self.ani.setDuration(250)
        self.ani.setEasingCurve(QEasingCurve.OutQuad)
        self.ani.valueChanged.connect(self._onValueChanged)
        self.ani.valueChanged.connect(self._updateMenuViewport)

    def _onValueChanged(self):
        pass

    def availableViewSize(self, pos: QPoint):
        """ Return the available size of view """
        ss = getCurrentScreenGeometry() #QApplication.screenAt(QCursor.pos()).availableGeometry()
        w, h = ss.width() - 100, ss.height() - 100
        return w, h

    def _updateMenuViewport(self):
        self.menu.view.viewport().update()
        self.menu.view.setAttribute(Qt.WA_UnderMouse, True)
        e = QHoverEvent(QEvent.HoverEnter, QPoint(), QPoint(1, 1))
        QApplication.sendEvent(self.menu.view, e)

    def _endPosition(self, pos):
        m = self.menu
        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        w, h = m.width() + 5, m.height()
        x = min(pos.x() - m.layout().contentsMargins().left(), rect.right() - w)
        y = min(pos.y() - 4, rect.bottom() - h + 10)

        return QPoint(x, y)

    def _menuSize(self):
        m = self.menu.layout().contentsMargins()
        w = self.menu.view.width() + m.left() + m.right() + 120
        h = self.menu.view.height() + m.top() + m.bottom() + 20
        return w, h

    def exec(self, pos: QPoint):
        pass

    @classmethod
    def register(cls, name):
        """ register menu animation manager

        Parameters
        ----------
        name: Any
            the name of manager, it should be unique
        """
        def wrapper(Manager):
            if name not in cls.managers:
                cls.managers[name] = Manager

            return Manager

        return wrapper

    @classmethod
    def make(cls, menu: FluentRoundMenu, aniType: MenuAnimationType):
        if aniType not in cls.managers:
            raise ValueError(f'`{aniType}` is an invalid menu animation type.')

        return cls.managers[aniType](menu)


@MenuAnimationManager.register(MenuAnimationType.NONE)
class DummyMenuAnimationManager(MenuAnimationManager):
    """ Dummy menu animation manager """

    def exec(self, pos: QPoint):
        self.menu.move(self._endPosition(pos))


@MenuAnimationManager.register(MenuAnimationType.DROP_DOWN)
class DropDownMenuAnimationManager(MenuAnimationManager):
    """ Drop down menu animation manager """

    def exec(self, pos):
        pos = self._endPosition(pos)
        h = self.menu.height() + 5

        self.ani.setStartValue(pos-QPoint(0, int(h/2)))
        self.ani.setEndValue(pos)
        self.ani.start()

    def availableViewSize(self, pos: QPoint):
        ss = QApplication.screenAt(QCursor.pos()).availableGeometry()
        return ss.width() - 100, max(ss.bottom() - pos.y() - 10, 1)

    def _onValueChanged(self):
        w, h = self._menuSize()
        y = self.ani.endValue().y() - self.ani.currentValue().y()
        self.menu.setMask(QRegion(0, y, w, h))


@MenuAnimationManager.register(MenuAnimationType.PULL_UP)
class PullUpMenuAnimationManager(MenuAnimationManager):
    """ Pull up menu animation manager """

    def _endPosition(self, pos):
        m = self.menu
        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        w, h = m.width() + 5, m.height()
        x = min(pos.x() - m.layout().contentsMargins().left(), rect.right() - w)
        y = max(pos.y() - h + 10, 4)
        return QPoint(x, y)

    def exec(self, pos):
        pos = self._endPosition(pos)
        h = self.menu.height() + 5

        self.ani.setStartValue(pos+QPoint(0, int(h/2)))
        self.ani.setEndValue(pos)
        self.ani.start()

    def availableViewSize(self, pos: QPoint):
        ss = QApplication.screenAt(QCursor.pos()).availableGeometry()
        return ss.width() - 100, max(pos.y() - 28, 1)

    def _onValueChanged(self):
        w, h = self._menuSize()
        y = self.ani.endValue().y() - self.ani.currentValue().y()
        self.menu.setMask(QRegion(0, y, w, h - 28))


@MenuAnimationManager.register(MenuAnimationType.FADE_IN_DROP_DOWN)
class FadeInDropDownMenuAnimationManager(MenuAnimationManager):
    """ Fade in drop down menu animation manager """

    def __init__(self, menu: FluentRoundMenu):
        super().__init__(menu)
        self.opacityAni = QPropertyAnimation(menu, b'windowOpacity', self)
        self.aniGroup = QParallelAnimationGroup(self)
        self.aniGroup.addAnimation(self.ani)
        self.aniGroup.addAnimation(self.opacityAni)

    def exec(self, pos):
        pos = self._endPosition(pos)

        self.opacityAni.setStartValue(0)
        self.opacityAni.setEndValue(1)
        self.opacityAni.setDuration(150)
        self.opacityAni.setEasingCurve(QEasingCurve.OutQuad)

        self.ani.setStartValue(pos-QPoint(0, 8))
        self.ani.setEndValue(pos)
        self.ani.setDuration(150)
        self.ani.setEasingCurve(QEasingCurve.OutQuad)

        self.aniGroup.start()

    def availableViewSize(self, pos: QPoint):
        ss = QApplication.screenAt(QCursor.pos()).availableGeometry()
        return ss.width() - 100, max(ss.bottom() - pos.y() - 10, 1)


@MenuAnimationManager.register(MenuAnimationType.FADE_IN_PULL_UP)
class FadeInPullUpMenuAnimationManager(MenuAnimationManager):
    """ Fade in pull up menu animation manager """

    def __init__(self, menu: FluentRoundMenu):
        super().__init__(menu)
        self.opacityAni = QPropertyAnimation(menu, b'windowOpacity', self)
        self.aniGroup = QParallelAnimationGroup(self)
        self.aniGroup.addAnimation(self.ani)
        self.aniGroup.addAnimation(self.opacityAni)

    def _endPosition(self, pos):
        m = self.menu
        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        w, h = m.width() + 5, m.height()
        x = min(pos.x() - m.layout().contentsMargins().left(), rect.right() - w)
        y = max(pos.y() - h + 15, 4)
        return QPoint(x, y)

    def exec(self, pos):
        pos = self._endPosition(pos)

        self.opacityAni.setStartValue(0)
        self.opacityAni.setEndValue(1)
        self.opacityAni.setDuration(150)
        self.opacityAni.setEasingCurve(QEasingCurve.OutQuad)

        self.ani.setStartValue(pos+QPoint(0, 8))
        self.ani.setEndValue(pos)
        self.ani.setDuration(200)
        self.ani.setEasingCurve(QEasingCurve.OutQuad)
        self.aniGroup.start()

    def availableViewSize(self, pos: QPoint):
        ss = QApplication.screenAt(QCursor.pos()).availableGeometry()
        return ss.width() - 100, pos.y() - 28


class EditMenu(FluentRoundMenu):
    """ Edit menu """

    def createActions(self):
        self.cutAct = QAction(
            FIF.CUT.icon(),
            self.tr("Cut"),
            self,
            shortcut="Ctrl+X",
            triggered=self.parent().cut,
        )
        self.copyAct = QAction(
            FIF.COPY.icon(),
            self.tr("Copy"),
            self,
            shortcut="Ctrl+C",
            triggered=self.parent().copy,
        )
        self.pasteAct = QAction(
            FIF.PASTE.icon(),
            self.tr("Paste"),
            self,
            shortcut="Ctrl+V",
            triggered=self.parent().paste,
        )
        self.cancelAct = QAction(
            FIF.CANCEL.icon(),
            self.tr("Cancel"),
            self,
            shortcut="Ctrl+Z",
            triggered=self.parent().undo,
        )
        self.selectAllAct = QAction(
            self.tr("Select all"),
            self,
            shortcut="Ctrl+A",
            triggered=self.parent().selectAll
        )
        self.action_list = [
            self.cutAct, self.copyAct,
            self.pasteAct, self.cancelAct, self.selectAllAct
        ]

    def _parentText(self):
        raise NotImplementedError

    def _parentSelectedText(self):
        raise NotImplementedError

    def exec(self, pos, ani=True, aniType=MenuAnimationType.DROP_DOWN):
        self.clear()
        self.createActions()

        if QApplication.clipboard().mimeData().hasText():
            if self._parentText():
                if self._parentSelectedText():
                    if self.parent().isReadOnly():
                        self.addActions([self.copyAct, self.selectAllAct])
                    else:
                        self.addActions(self.action_list)
                else:
                    if self.parent().isReadOnly():
                        self.addAction(self.selectAllAct)
                    else:
                        self.addActions(self.action_list[2:])
            elif not self.parent().isReadOnly():
                self.addAction(self.pasteAct)
            else:
                return
        else:
            if not self._parentText():
                return

            if self._parentSelectedText():
                if self.parent().isReadOnly():
                    self.addActions([self.copyAct, self.selectAllAct])
                else:
                    self.addActions(
                        self.action_list[:2] + self.action_list[3:])
            else:
                if self.parent().isReadOnly():
                    self.addAction(self.selectAllAct)
                else:
                    self.addActions(self.action_list[3:])

        super().exec(pos, ani, aniType)


class LineEditMenu(EditMenu):
    """ Line edit menu """

    def __init__(self, parent: QLineEdit):
        super().__init__("", parent)
        self.selectionStart = parent.selectionStart()
        self.selectionLength = parent.selectionLength()

    def _onItemClicked(self, item):
        if self.selectionStart >= 0:
            self.parent().setSelection(self.selectionStart, self.selectionLength)

        super()._onItemClicked(item)

    def _parentText(self):
        return self.parent().text()

    def _parentSelectedText(self):
        return self.parent().selectedText()

    def exec(self, pos, ani=True, aniType=MenuAnimationType.DROP_DOWN):
        return super().exec(pos, ani, aniType)


class TextEditMenu(EditMenu):
    """ Text edit menu """

    def __init__(self, parent: QTextEdit):
        super().__init__("", parent)
        cursor = parent.textCursor()
        self.selectionStart = cursor.selectionStart()
        self.selectionLength = cursor.selectionEnd() - self.selectionStart + 1

    def _parentText(self):
        return self.parent().toPlainText()

    def _parentSelectedText(self):
        return self.parent().textCursor().selectedText()

    def _onItemClicked(self, item):
        if self.selectionStart >= 0:
            cursor = self.parent().textCursor()
            cursor.setPosition(self.selectionStart)
            cursor.movePosition(
                QTextCursor.Right, QTextCursor.KeepAnchor, self.selectionLength)

        super()._onItemClicked(item)

    def exec(self, pos, ani=True, aniType=MenuAnimationType.DROP_DOWN):
        return super().exec(pos, ani, aniType)


class IndicatorMenuItemDelegate(MenuItemDelegate):
    """ Menu item delegate with indicator """

    def paint(self, painter: QPainter, option, index):
        super().paint(painter, option, index)
        if not option.state & QStyle.State_Selected:
            return

        painter.save()
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)

        painter.setPen(Qt.NoPen)
        painter.setBrush(themeColor())
        painter.drawRoundedRect(6, 11+option.rect.y(), 3, 15, 1.5, 1.5)

        painter.restore()


class CheckableMenuItemDelegate(ShortcutMenuItemDelegate):
    """ Checkable menu item delegate """

    def _drawIndicator(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        raise NotImplementedError

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        super().paint(painter, option, index)

        # draw indicator
        action = index.data(Qt.UserRole)  # type: QAction
        if not (isinstance(action, QAction) and action.isChecked()):
            return

        painter.save()
        self._drawIndicator(painter, option, index)
        painter.restore()


class RadioIndicatorMenuItemDelegate(CheckableMenuItemDelegate):
    """ Checkable menu item delegate with radio indicator """

    def _drawIndicator(self, painter, option, index):
        rect = option.rect
        r = 5
        x = rect.x() + 22
        y = rect.center().y() - r / 2

        painter.setRenderHints(QPainter.Antialiasing)
        if not option.state & QStyle.State_MouseOver:
            painter.setOpacity(0.75 if isDarkTheme() else 0.65)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.white if isDarkTheme() else Qt.black)
        painter.drawEllipse(QRectF(x, y, r, r))


class CheckIndicatorMenuItemDelegate(CheckableMenuItemDelegate):
    """ Checkable menu item delegate with check indicator """

    def _drawIndicator(self, painter, option, index):
        rect = option.rect
        s = 11
        x = rect.x() + 19
        y = rect.center().y() - s / 2

        painter.setRenderHints(QPainter.Antialiasing)
        if not option.state & QStyle.State_MouseOver:
            painter.setOpacity(0.75)

        FIF.ACCEPT.render(painter, QRectF(x, y, s, s))


class MenuIndicatorType(Enum):
    """ Menu indicator type """
    CHECK = 0
    RADIO = 1


def createCheckableMenuItemDelegate(style: MenuIndicatorType):
    """ create checkable menu item delegate """
    if style == MenuIndicatorType.RADIO:
        return RadioIndicatorMenuItemDelegate()
    if style == MenuIndicatorType.CHECK:
        return CheckIndicatorMenuItemDelegate()

    raise ValueError(f'`{style}` is not a valid menu indicator type.')


class CheckableMenu(FluentRoundMenu):
    """ Checkable menu """

    def __init__(self, title="", parent=None, indicatorType=MenuIndicatorType.CHECK):
        super().__init__(title, parent)
        self.view.setItemDelegate(createCheckableMenuItemDelegate(indicatorType))
        self.view.setObjectName('checkableListWidget')

    def _adjustItemText(self, item: QListWidgetItem, action: QAction):
        w = super()._adjustItemText(item, action)
        item.setSizeHint(QSize(w + 26, self.itemHeight))

    def exec(self, pos, ani=True, aniType=MenuAnimationType.DROP_DOWN):
        return super().exec(pos, ani, aniType)


class SystemTrayMenu(FluentRoundMenu):
    """ System tray menu """

    def showEvent(self, e):
        super().showEvent(e)
        self.adjustPosition()


class CheckableSystemTrayMenu(CheckableMenu):
    """ Checkable system tray menu """

    def showEvent(self, e):
        super().showEvent(e)
        self.adjustPosition()


# ============================================================
#    简约自绘菜单（纯 PySide6，脱离 Fluent 风格）
# ============================================================

_MENU_RADIUS = 10      # 菜单圆角
_MENU_ITEM_H = 36      # 菜单项高度
_MENU_PAD = 6          # 面板内边距
_SHADOW_PAD = 16       # 阴影留白


# 菜单项图标：使用 Font Awesome（qtawesome）现成图标体系
_ICON_KIND_MAP = {
    'folder': 'fa5s.folder',
    'settings': 'fa5s.cog',
    'exit': 'fa5s.power-off',
    'status': 'fa5s.heart',
    'backpack': 'fa5s.briefcase',
    'shop': 'fa5s.shopping-cart',
    'memo': 'fa5s.sticky-note',
    'remind': 'fa5s.bell',
    'growth': 'fa5s.arrow-up',
    'interact': 'fa5s.comments',
    'chat': 'fa5s.comment',
}

# qtawesome 缺失时的 FluentIcon 兜底
_ICON_FALLBACK = {
    'folder': FIF.FOLDER,
    'settings': FIF.SETTING,
    'exit': FIF.POWER_BUTTON,
    'status': FIF.HEART,
    'backpack': FIF.SAVE,
    'shop': FIF.SHOPPING_CART,
    'memo': FIF.QUICK_NOTE,
    'remind': FIF.RINGER,
    'growth': FIF.UP,
    'interact': FIF.MESSAGE,
    'chat': FIF.CHAT,
}


def _kind_for_text(text):
    """根据菜单文本映射到图标类型；找不到返回 None"""
    if not text:
        return None
    t = text.lower()
    for keys, kind in [
        (('exit', 'quit', 'close', 'logout', '退出', '关闭'), 'exit'),
        (('settings', 'option', 'preference', 'config', '设置', '选项', '配置'), 'settings'),
        (('status', 'health', 'favor', '状态', '健康', '好感'), 'status'),
        (('backpack', 'inventory', 'bag', 'item', '背包', '物品', '道具'), 'backpack'),
        (('shop', 'store', 'market', 'buy', '商店', '商城', '购买'), 'shop'),
        (('memo', 'note', '备忘', '笔记', '日志'), 'memo'),
        (('remind', 'reminder', 'alarm', '提醒', '闹钟'), 'remind'),
        (('growth', 'grow', '成长', '养成', '发展'), 'growth'),
        (('chat', 'talk', '对话', '聊天', '交谈'), 'chat'),
        (('interact', '互动', '交流'), 'interact'),
    ]:
        if any(k in t for k in keys):
            return kind
    return None


def _fluent_icon_for(kind):
    """返回菜单项图标（优先 Font Awesome，qtawesome 缺失时回退 FluentIcon）"""
    name = _ICON_KIND_MAP.get(kind)
    if qta is not None and name:
        dark = isDarkTheme()
        return qta.icon(name, color='#FFFFFF' if dark else '#000000')
    fif = _ICON_FALLBACK.get(kind)
    return fif.icon() if fif is not None else QIcon()


def _item_text_style(enabled):
    """菜单项文本内联样式（黑色正文 / 灰色禁用）

    不使用 QSS 组合选择器 `QFrame#x:disabled QLabel#y`（Qt 会误匹配 enabled 项），
    改为在构建时内联设置颜色。
    """
    dark = isDarkTheme()
    fg = '#FFFFFF' if dark else '#000000'
    fg_disabled = '#6B7178' if dark else '#B4BAC4'
    color = fg if enabled else fg_disabled
    return f'color: {color}; background: transparent; font: 14px {UI_FONT};'


def _set_item_hover(widget, on):
    """手动控制菜单项 hover 背景（鼠标移走即清除，避免 QSS :hover 残留）"""
    if getattr(widget, '_hoverState', None) == on:
        return
    widget._hoverState = on
    dark = isDarkTheme()
    bg = '#2F3238' if dark else '#F2F3F5'
    color = bg if on else 'transparent'
    widget.setStyleSheet(
        f'QFrame#simpleMenuItem {{ background-color: {color}; border: none; border-radius: 6px; }}')


class SimpleMenuItem(QFrame):
    """简约菜单项（系统图标 + 文本 + 快捷键）"""

    def __init__(self, menu, action, parent=None):
        super().__init__(parent)
        self._menu = menu
        self._action = action
        self.setObjectName('simpleMenuItem')
        self.setCursor(Qt.PointingHandCursor)

        self.hBox = QHBoxLayout(self)
        self.hBox.setContentsMargins(10, 10, 10, 10)
        self.hBox.setSpacing(10)

        icon = _fluent_icon_for(_kind_for_text(action.text()))
        if not icon.isNull():
            self.iconLabel = QLabel(self)
            self.iconLabel.setFixedSize(18, 18)
            self.iconLabel.setAlignment(Qt.AlignCenter)
            self.iconLabel.setPixmap(icon.pixmap(18, 18))
            self.hBox.addWidget(self.iconLabel)
        else:
            self.iconLabel = None

        self.textLabel = QLabel(action.text(), self)
        self.textLabel.setObjectName('simpleMenuItemText')
        self.hBox.addWidget(self.textLabel, 1)

        if action.shortcut().isEmpty():
            self.shortcutLabel = None
        else:
            self.shortcutLabel = QLabel(action.shortcut().toString(), self)
            self.shortcutLabel.setObjectName('simpleMenuHint')
            self.hBox.addWidget(self.shortcutLabel, 0, Qt.AlignRight)

        self.setEnabled(action.isEnabled())
        # 文本颜色内联设置（黑色正文 / 灰色禁用），避开 Qt QSS 组合 :disabled 的解析问题
        style = _item_text_style(action.isEnabled())
        self.textLabel.setStyleSheet(style)
        if self.shortcutLabel is not None:
            self.shortcutLabel.setStyleSheet(style)
        # 内部 QLabel 不拦截鼠标事件，确保整块区域的 hover/点击都由 QFrame 处理
        for lbl in (self.iconLabel, self.textLabel, self.shortcutLabel):
            if lbl is not None:
                lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self._action.isEnabled():
            self._menu._triggerAction(self._action)


class SimpleSubMenuItem(QFrame):
    """简约子菜单项（系统文件夹图标 + 文本 + 右箭头）"""

    def __init__(self, menu, subMenu, parent=None):
        super().__init__(parent)
        self._menu = menu
        self.subMenu = subMenu
        self.setObjectName('simpleMenuItem')
        self.setCursor(Qt.PointingHandCursor)

        self.hBox = QHBoxLayout(self)
        self.hBox.setContentsMargins(10, 10, 10, 10)
        self.hBox.setSpacing(10)

        # 子菜单图标按标题语义映射（养成=上箭头、互动=chat…），未匹配则用文件夹
        icon = _fluent_icon_for(_kind_for_text(subMenu.title()))
        if icon.isNull():
            icon = FIF.FOLDER.icon()
        if not icon.isNull():
            self.iconLabel = QLabel(self)
            self.iconLabel.setFixedSize(18, 18)
            self.iconLabel.setAlignment(Qt.AlignCenter)
            self.iconLabel.setPixmap(icon.pixmap(18, 18))
            self.hBox.addWidget(self.iconLabel)

        self.textLabel = QLabel(subMenu.title(), self)
        self.textLabel.setObjectName('simpleMenuItemText')
        self.hBox.addWidget(self.textLabel, 1)

        self.arrowLabel = QLabel('›', self)
        self.arrowLabel.setObjectName('simpleMenuHint')
        self.hBox.addWidget(self.arrowLabel, 0, Qt.AlignRight)

        style = _item_text_style(True)
        self.textLabel.setStyleSheet(style)
        self.arrowLabel.setStyleSheet(style)
        # 内部 QLabel 不拦截鼠标事件，确保整块区域的 hover 都由 QFrame 处理
        for lbl in (self.iconLabel, self.textLabel, self.arrowLabel):
            if lbl is not None:
                lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)

class SimpleMenuSeparator(QFrame):
    """简约分隔线"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('simpleMenuSeparator')
        self.setFixedHeight(9)


class RoundMenu(QWidget):
    """简约自绘菜单（纯 PySide6，脱离 Fluent 风格）

    兼容原 FluentRoundMenu 的常用 API：
    addAction / addActions / addSeparator / addMenu / addWidget /
    popup / exec / exec_ / setIcon / icon / title / menuActions /
    clear / setItemHeight / closedSignal
    """

    closedSignal = Signal()

    def __init__(self, title='', parent=None):
        super().__init__(parent)
        self._title = title
        self._icon = QIcon()
        self._actions = []
        self._subMenus = []
        self._items = []          # 菜单项 widget（用于鼠标位置轮询）
        self.itemHeight = _MENU_ITEM_H

        self._parentMenu = None
        self._hoverSubItem = None
        self._titleLabel = None
        self._hoverTimer = None

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._buildWidgets()
        self._applyStyle()

    # ---------- 构建 ----------
    def _buildWidgets(self):
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(_SHADOW_PAD, _SHADOW_PAD, _SHADOW_PAD, _SHADOW_PAD)

        self._panel = QFrame(self)
        self._panel.setObjectName('simpleMenuPanel')
        self._layout = QVBoxLayout(self._panel)
        self._layout.setContentsMargins(_MENU_PAD, _MENU_PAD, _MENU_PAD, _MENU_PAD)
        self._layout.setSpacing(2)

        if self._title:
            self._titleLabel = QLabel(self._title, self._panel)
            self._titleLabel.setObjectName('simpleMenuTitle')
            self._layout.addWidget(self._titleLabel)

        self._outer.addWidget(self._panel)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 45))
        self._panel.setGraphicsEffect(shadow)

    def _applyStyle(self):
        dark = isDarkTheme()
        p = palette.DARK if dark else palette.LIGHT
        # 正文使用纯黑/纯白；禁用项颜色由 _item_text_style 内联控制
        fg = '#000000' if not dark else '#FFFFFF'
        self._panel.setStyleSheet(f'''
            QFrame#simpleMenuPanel {{
                background-color: {p['menuBg']};
                border: 1px solid {p['menuBorder']};
                border-radius: {_MENU_RADIUS}px;
            }}
            QFrame#simpleMenuItem {{
                border: none;
                border-radius: 6px;
                background-color: transparent;
            }}
            QLabel#simpleMenuTitle {{
                color: {fg};
                font: 600 12px {UI_FONT};
                padding: 4px 10px 4px 10px;
            }}
            QFrame#simpleMenuSeparator {{
                border: none;
                border-top: 1px solid {p['menuBorder']};
                margin: 5px 10px;
            }}
        ''')

    # ---------- 内容 ----------
    def addAction(self, action):
        if isinstance(action, str):
            action = QAction(action, self)
        elif not isinstance(action, QAction):
            action = QAction(action, self)
        self._actions.append(action)
        item = SimpleMenuItem(self, action, self._panel)
        self._items.append(item)
        self._layout.addWidget(item)
        return action

    def addActions(self, actions):
        for action in actions:
            self.addAction(action)

    def addSeparator(self):
        self._layout.addWidget(SimpleMenuSeparator(self._panel))

    def addMenu(self, menu):
        if not isinstance(menu, RoundMenu):
            raise ValueError('`menu` should be an instance of `RoundMenu`.')
        menu._parentMenu = self
        self._subMenus.append(menu)
        item = SimpleSubMenuItem(self, menu, self._panel)
        self._items.append(item)
        self._layout.addWidget(item)
        return menu

    def addWidget(self, widget, selectable=True, onClick=None):
        """嵌入自定义 widget，四周补上与菜单项一致的侧边距，内容左对齐"""
        wrap = QWidget(self._panel)
        box = QHBoxLayout(wrap)
        box.setContentsMargins(10, 10, 10, 10)
        box.addWidget(widget, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self._layout.addWidget(wrap)
        return widget

    def setIcon(self, icon):
        self._icon = QIcon(icon) if not isinstance(icon, QIcon) else icon

    def icon(self):
        return self._icon

    def title(self):
        return self._title

    def menuActions(self):
        return self._actions

    def clear(self):
        self._actions.clear()
        self._subMenus.clear()
        self._items.clear()
        for i in range(self._layout.count() - 1, -1, -1):
            item = self._layout.itemAt(i)
            w = item.widget()
            if w is not None and w is not self._titleLabel:
                self._layout.removeItem(item)
                w.deleteLater()

    def setItemHeight(self, height):
        self.itemHeight = height

    def setMaxVisibleItems(self, num):
        pass

    def setDefaultAction(self, action):
        pass

    # ---------- 弹出 ----------
    def popup(self, pos, ani=True, aniType=None):
        self.adjustSize()
        self._moveWithinScreen(pos)
        self.show()
        self.raise_()
        self.activateWindow()
        self._startHoverTracking()

    def exec(self, pos, ani=True, aniType=None):
        self.popup(pos, ani, aniType)
        return True

    def exec_(self, pos, ani=True, aniType=None):
        return self.exec(pos, ani, aniType)

    def _moveWithinScreen(self, pos):
        screen = QApplication.screenAt(pos)
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is None:
            self.move(pos)
            return
        rect = screen.availableGeometry()
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        if x + w > rect.right():
            x = rect.right() - w
        if y + h > rect.bottom():
            y = rect.bottom() - h
        self.move(max(x, rect.left()), max(y, rect.top()))

    # ---------- 交互 ----------
    def _triggerAction(self, action):
        self._closeAllMenus()
        action.trigger()

    def _closeAllMenus(self):
        menu = self
        while menu is not None:
            menu.close()
            menu = menu._parentMenu

    # ---------- 鼠标位置轮询（hover 与子菜单开合完全以鼠标位置为基准）----------
    def _startHoverTracking(self):
        """启动 hover 轮询（仅根菜单）"""
        if self._parentMenu is not None:
            return
        if self._hoverTimer is None:
            self._hoverTimer = QTimer(self)
            self._hoverTimer.setInterval(50)
            self._hoverTimer.timeout.connect(self._tickHover)
        self._hoverTimer.start()

    def _stopHoverTracking(self):
        if self._hoverTimer is not None:
            self._hoverTimer.stop()

    def _tickHover(self):
        pos = QCursor.pos()
        w = QApplication.widgetAt(pos)
        menu_of_w = self._menuOf(w)

        # 找到鼠标命中的菜单项
        hover_item = None
        if menu_of_w is not None:
            for item in menu_of_w._items:
                if item.rect().contains(item.mapFromGlobal(pos)):
                    hover_item = item
                    break

        # 以鼠标位置为基准更新所有可见菜单项的 hover 态
        for menu in self._collectVisibleMenus():
            for item in menu._items:
                _set_item_hover(item, item is hover_item)

        # 子菜单开合
        if menu_of_w is self:
            if isinstance(hover_item, SimpleSubMenuItem):
                sub = hover_item.subMenu
                # 关闭同级的其它已打开子菜单
                for it in self._items:
                    if (isinstance(it, SimpleSubMenuItem) and it is not hover_item
                            and it.subMenu.isVisible()):
                        it.subMenu.close()
                if not sub.isVisible():
                    p = hover_item.mapToGlobal(QPoint(hover_item.width() + 2, 0))
                    sub.popup(p)
            elif hover_item is not None:
                # 根菜单普通项：收起所有子菜单
                self._closeAllSubMenus()
            else:
                # 鼠标在根菜单空白/自定义区域：收起所有子菜单
                self._closeAllSubMenus()
        elif menu_of_w is None:
            # 鼠标不在任何菜单上：hover 已清除，收起所有子菜单
            self._closeAllSubMenus()
        # 鼠标在子菜单内部时保持打开

    def _menuOf(self, w):
        """返回 widget 所属的 RoundMenu（沿父链向上）"""
        m = w
        while m is not None:
            if isinstance(m, RoundMenu):
                return m
            m = m.parentWidget()
        return None

    def _collectVisibleMenus(self):
        """收集当前可见的整条菜单链（自身 + 已打开的子菜单）"""
        menus = [self]
        stack = list(self._subMenus)
        while stack:
            m = stack.pop(0)
            if m.isVisible():
                menus.append(m)
                stack.extend(m._subMenus)
        return menus

    def _closeAllSubMenus(self):
        """递归收起所有已打开的子菜单"""
        for m in self._subMenus:
            m._closeAllSubMenus()
            if m.isVisible():
                m.close()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self._closeAllMenus()
        else:
            super().keyPressEvent(e)

    # ---------- 事件 ----------
    def showEvent(self, e):
        super().showEvent(e)
        # 仅根菜单安装全局过滤器，负责点击外部关闭整条菜单链
        if self._parentMenu is None:
            QApplication.instance().installEventFilter(self)

    def closeEvent(self, e):
        self._stopHoverTracking()
        if self._parentMenu is None:
            QApplication.instance().removeEventFilter(self)
        e.accept()
        self.closedSignal.emit()

    def eventFilter(self, obj, e):
        if e.type() == QEvent.MouseButtonPress:
            w = QApplication.widgetAt(e.globalPos())
            if w is None or not self._isInMenuChain(w):
                self._closeAllMenus()
        return super().eventFilter(obj, e)

    def _isInMenuChain(self, w):
        if self is w or self.isAncestorOf(w):
            return True
        for m in self._subMenus:
            if m._isInMenuChain(w):
                return True
        return False