# coding:utf-8
import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .statusUI import statusInterface
from .inventoryUI import backpackInterface
from .shopUI import shopInterface

import DyberPet.settings as settings
from DyberPet.style.panel import SideNavWindow

basedir = settings.BASEDIR
module_path = os.path.join(basedir, 'DyberPet/Dashboard/')


class DashboardMainWindow(SideNavWindow):
    """简约化 Growth 面板：左侧简约导航 + Status / Backpack / Shop"""

    def __init__(self, minWidth=700, minHeight=560):
        super().__init__(title=self.tr('Growth'), width=minWidth, height=minHeight)

        # 三页 sizeHintdb 传「stack 实际可用宽」（窗口 - 160 nav - 32 outer - 余量）
        stack_w = minWidth - 210
        self.statusInterface = statusInterface(sizeHintdb=(stack_w, minHeight), parent=self)
        self.backpackInterface = backpackInterface(sizeHintdb=(stack_w, minHeight), parent=self)
        self.shopInterface = shopInterface(sizeHintdb=(stack_w, minHeight), parent=self)

        self.initNavigation()
        self.setMinimumSize(minWidth, minHeight)
        self.initWindow()
        self.__connectSignalToSlot()

    def initNavigation(self):
        # add sub interface（简约导航：fa5s 图标 + 文本）
        self.addSubInterface(self.statusInterface, 'fa5s.heartbeat', self.tr('Status'))
        self.addSubInterface(self.backpackInterface, 'fa5s.box-open', self.tr('Backpack'))
        self.addSubInterface(self.shopInterface, 'fa5s.store', self.tr('Shop'))

    def initWindow(self):
        self.setWindowIcon(QIcon(os.path.join(basedir, "res/icons/dashboard.svg")))
        self.setWindowTitle(self.tr('Growth'))

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def switch_to(self, page_name: str) -> None:
        """
        从右键菜单直达指定页面
        :param page_name: status / backpack / shop
        """
        mapping = {
            'status': self.statusInterface,
            'backpack': self.backpackInterface,
            'shop': self.shopInterface,
        }
        widget = mapping.get(page_name)
        if widget is not None:
            self.switchTo(widget)

    def __connectSignalToSlot(self):
        self.backpackInterface.addBuff.connect(self.statusInterface._addBuff)
        self.statusInterface.addCoins.connect(self.backpackInterface.addCoins)
        self.backpackInterface.rmBuff.connect(self.statusInterface._rmBuff)
        self.backpackInterface.coinWidget.coinUpdated.connect(self.shopInterface.coinWidget._update2data)
        self.backpackInterface.item_num_changed.connect(self.shopInterface._updateItemNum)
        # buy&sell
        self.shopInterface.buyItem.connect(self.backpackInterface.add_item)
        self.shopInterface.sellItem.connect(self.backpackInterface.add_item)
        self.shopInterface.updateCoin.connect(self.backpackInterface.addCoins)

    def show_window(self, page_name=None):
        if page_name is not None:
            self.switch_to(page_name)
        if not self.isVisible():
            if self.width() < self.minimumWidth() or self.height() < self.minimumHeight():
                self.resize(self.minimumWidth(), self.minimumHeight())
            self.show()


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    from qfluentwidgets import FluentTranslator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = DashboardMainWindow()
    w.show()
    app.exec_()
