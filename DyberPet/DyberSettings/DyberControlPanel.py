# coding:utf-8
import sys
import os
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, FluentWindow,
                            NavigationAvatarWidget,  SplitFluentWindow, FluentTranslator)
from qfluentwidgets import FluentIcon as FIF

from .BasicSettingUI import SettingInterface
from .GameSaveUI import SaveInterface
from ..Dashboard.animationUI import animationInterface
from sys import platform
import DyberPet.settings as settings
basedir = settings.BASEDIR

module_path = os.path.join(basedir, 'DyberPet/DyberSettings/')


class ControlMainWindow(FluentWindow):

    def __init__(self, minWidth=1000, minHeight=800):
        super().__init__()
        # 置顶显示：确保系统面板能盖住置顶的桌宠（尤其大尺寸时）
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        # create sub interface
        self.settingInterface = SettingInterface(self)
        self.gamesaveInterface = SaveInterface(sizeHintDyber=(minWidth, minHeight), parent=self)
        self.animInterface = animationInterface(sizeHintdb=(minWidth, minHeight), parent=self)

        self.initNavigation()
        self.setMinimumSize(minWidth, minHeight)
        self.initWindow()

    def initNavigation(self):
        # add sub interface
        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('Settings'))
        self.addSubInterface(self.gamesaveInterface,
                             FIF.SAVE, #QIcon(os.path.join(module_path, 'resource/saveIcon.svg')), 
                             self.tr('Game Save'))
        self.addSubInterface(self.animInterface,
                             QIcon(os.path.join(basedir, 'res/icons/Dashboard/videoEdit.svg')),
                             self.tr('Animation'))

        self.navigationInterface.setExpandWidth(200)
        # 隐藏导航栏左上角的返回按钮（本产品无多级子页面返回需求）
        self.navigationInterface.setReturnButtonVisible(False)

    def initWindow(self):
        #self.setMinimumSize(minWidth, minHeight)
        #self.resize(1000, 800)
        self.setWindowIcon(QIcon(os.path.join(basedir, "res/icons/SystemPanel.png")))
        self.setWindowTitle(self.tr('Settings'))

        desktop = QApplication.primaryScreen().availableGeometry() #QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def switch_to(self, page_name: str) -> None:
        """
        从右键菜单直达指定页面
        :param page_name: settings / gamesave
        """
        mapping = {
            'settings': self.settingInterface,
            'gamesave': self.gamesaveInterface,
            'animation': self.animInterface,
        }
        widget = mapping.get(page_name)
        if widget is not None:
            self.stackedWidget.setCurrentWidget(widget, popOut=False)
            self.navigationInterface.setCurrentItem(widget.objectName())

    def show_window(self, page_name=None):
        if page_name is not None:
            self.switch_to(page_name)
        if not self.isVisible():
            # 确保初始尺寸不小于最小尺寸（FluentWindow 布局在 show 前可能挤压窗口）
            if self.width() < self.minimumWidth() or self.height() < self.minimumHeight():
                self.resize(self.minimumWidth(), self.minimumHeight())
            self.show()
            self.raise_()
            self.activateWindow()

    def closeEvent(self, event):
        event.ignore()  # Ignore the close event
        self.hide()

    #def _onCharChange(self, char):
    #    self.hide()


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)

    # install translator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = ControlMainWindow()
    w.show()
    app.exec_()



















