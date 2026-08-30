# coding:utf-8
"""简约自绘控制面板（设置 / 存档管理）"""
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .BasicSettingUI import SettingInterface
from .GameSaveUI import SaveInterface
from DyberPet.style.panel import SideNavWindow

import DyberPet.settings as settings
basedir = settings.BASEDIR


class ControlMainWindow(SideNavWindow):

    def __init__(self, minWidth=1000, minHeight=800):
        super().__init__(title=self.tr('Settings'), width=minWidth, height=minHeight)
        # 置顶显示：确保系统面板能盖住置顶的桌宠（尤其大尺寸时）
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        # create sub interface
        self.settingInterface = SettingInterface(self)
        self.gamesaveInterface = SaveInterface(sizeHintDyber=(minWidth, minHeight), parent=self)

        self.addSubInterface(self.settingInterface, 'fa5s.cog', self.tr('Settings'))
        self.addSubInterface(self.gamesaveInterface, 'fa5s.save', self.tr('Save'))

        self.setMinimumSize(minWidth, minHeight)
        self.setWindowIcon(QIcon(os.path.join(basedir, 'res/icons/SystemPanel.png')))

        desktop = QApplication.primaryScreen().availableGeometry()
        self.move(desktop.width() // 2 - self.width() // 2,
                  desktop.height() // 2 - self.height() // 2)

    def switch_to(self, page_name: str) -> None:
        """
        从右键菜单直达指定页面
        :param page_name: settings / gamesave
        """
        mapping = {
            'settings': self.settingInterface,
            'gamesave': self.gamesaveInterface,
        }
        widget = mapping.get(page_name)
        if widget is not None:
            self.switchTo(widget)

    def show_window(self, page_name=None):
        if page_name is not None:
            self.switch_to(page_name)
        if not self.isVisible():
            if self.width() < self.minimumWidth() or self.height() < self.minimumHeight():
                self.resize(self.minimumWidth(), self.minimumHeight())
            self.show()
            self.raise_()
            self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
