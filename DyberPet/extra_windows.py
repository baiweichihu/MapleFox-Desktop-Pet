import os
import sys
from sys import platform
import time
import math
import json
import types
import random
import ctypes
import inspect
import textwrap as tr
from typing import List
from datetime import datetime, timedelta

from PySide6.QtWidgets import *
from PySide6.QtCore import QObject, QThread, Signal, QRectF
from PySide6.QtCore import Qt, QTimer, QObject, QPoint, QEvent, QRect, QSize, QDateTime, QPropertyAnimation, QAbstractAnimation
from PySide6.QtGui import QImage, QPixmap, QIcon, QCursor, QPainter, QFont, QFontDatabase, QColor, QPainterPath, QRegion, QIntValidator, QDoubleValidator

from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import TransparentToolButton, ToolTipFilter, isDarkTheme
from DyberPet.style import palette
from DyberPet.style.theme import active_palette

try:
    import qtawesome as qta
except ImportError:
    qta = None

'''
try:
    size_factor = 1 #ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
except:
    size_factor = 1
    all_font_size = 10 #int(10/screen_scale)
'''
import DyberPet.settings as settings
from DyberPet.utils import text_wrap
#from pathlib import Path
#basedir = Path(os.path.dirname(__file__))
#basedir = str(basedir.parent).replace('\\', '/')

basedir = settings.BASEDIR
configdir = settings.CONFIGDIR

if platform == 'win32':
    #basedir = ''
    check_icon_path = 'res/icons/check_icon.png'
    arrow_icon_path = 'res/icons/arrow-204-32.ico'
else:
    #basedir = os.path.dirname(__file__) #Path(os.path.dirname(__file__))
    #basedir = basedir.replace('\\','/')
    #basedir = '/'.join(basedir.split('/')[:-1])

    check_icon_path = basedir + '/res/icons/check_icon.png'
    arrow_icon_path = basedir + '/res/icons/arrow-204-32.ico'


##############################
#          General
##############################
checkStyle = f"""
QCheckBox {{
    padding: 2px;
    font-size: 15px;
    font-family: "黑体";
    height: 25px
}}

/*CHECKBOX*/
QCheckBox:hover {{
    border-radius:4px;
    border-style:solid;
    border-width:1px;
    padding-left: 1px;
    padding-right: 1px;
    padding-bottom: 1px;
    padding-top: 1px;
    border-color: #64b4c4;
    background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 #cfe8ed, stop:1 #deeff2);
}}
QCheckBox::indicator:checked {{
    width: 15px;
    height: 15px;
    border-radius:4px;
    border-style:solid;
    border-width:1px;
    border-color: #64b4c4;
    image: url({check_icon_path})
}}
QCheckBox::indicator:unchecked {{
    width: 15px;
    height: 15px;
    border-radius:4px;
    border-style:solid;
    border-width:1px;
    border-color:#64b4c4;
    background-color:qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0,stop: 0 #f3d5f7, stop: 0.5 #fbf6e7,stop: 1 #e6fcf5);
}}
"""


pushbuttonStyle = """
QPushButton {
    background-color: #ffbdad;
    color: #000000;
    border-style: solid;
    padding: 7px;
    font: 16px;
    font-family: "黑体";
    border-width: 3px;
    border-radius: 10px;
    border-color: #B39C86;
}
QPushButton:hover:!pressed {
    background-color: #ffb19e;
}
QPushButton:pressed {
    background-color: #ffa48f;
}
QPushButton:disabled {
    background-color: #e0e1e0;
}
"""

LineStyle = """
QHLine{
    background-color: #9f7a6a;
    border: 0.5px solid #9f7a6a;
    border-style: solid;
}

QVLine{
    background-color: #9f7a6a;
    border: 0.5px solid #9f7a6a;
    border-style: solid;
}
"""

##############################
#          Settings
##############################
sliderStyle = """
QSlider::groove:horizontal {
border: 1px solid #bbb;
background: white;
height: 7px;
border-radius: 3px;
}

QSlider::sub-page:horizontal {
background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
    stop: 0 #8fccff, stop: 1 #bbdbf7);
background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
    stop: 0 #bbdbf7, stop: 1 #66baff);
border: 1px solid #777;
height: 7px;
border-radius: 3px;
}

QSlider::add-page:horizontal {
background: #fff;
border: 1px solid #777;
height: 7px;
border-radius: 3px;
}

QSlider::handle:horizontal {
background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0,stop: 0 #f3d5f7, stop: 0.5 #fbf6e7,stop: 1 #e6fcf5);
border: 1px solid #777;
width: 12px;
margin-top: -2px;
margin-bottom: -2px;
border-radius: 4px;
}

QSlider::handle:horizontal:hover {
background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0,stop: 0 #f3d5f7, stop: 0.5 #f6eac6,stop: 1 #c4f8e7);
border: 1px solid #444;
border-radius: 4px;
}

QSlider::sub-page:horizontal:disabled {
background: #bbb;
border-color: #999;
}

QSlider::add-page:horizontal:disabled {
background: #eee;
border-color: #999;
}

QSlider::handle:horizontal:disabled {
background: #eee;
border: 1px solid #aaa;
border-radius: 4px;
}
"""

ComboBoxStyle = f"""
QComboBox {{
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 4px;
    padding-left: 10px;
    font-family: "黑体";
    font-size: 16px;
}}

QComboBox::drop-down {{
    border: 0px;
}}

QComboBox::down-arrow {{
    image: url({arrow_icon_path});
    width: 12px;
    height: 12px;
    margin-right: 15px;
}}

QComboBox::on {{
    border: 3px solid #c2dbfe
}}

QComboBox QAbstractItemView {{
    font-size: 12px;
    border: 1px solid rgba(0,0,0,25);
    padding: 5px;
    padding-left: 10px;
    background-color: #fff;
    outline: 0px;
}}

"""


SettingStyle = f"""
QFrame {{
    background:#F5F4EF;
    border: 3px solid #F5F4EF;
    border-radius: 10px;
}}

QLabel {{
    font-size: 16px;
    font-family: "黑体";
}}

{sliderStyle}

QCheckBox {{
    padding: 2px;
    font-size: 16px;
    font-family: "黑体";
    height: 25px
}}

/*CHECKBOX*/
QCheckBox:hover {{
    border-radius:4px;
    border-style:solid;
    border-width:1px;
    padding-left: 1px;
    padding-right: 1px;
    padding-bottom: 1px;
    padding-top: 1px;
    border-color: #64b4c4;
    background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 #cfe8ed, stop:1 #deeff2);
}}
QCheckBox::indicator:checked {{
    width: 15px;
    height: 15px;
    border-radius: 4px;
    border-style:solid;
    border-width:1px;
    border-color: #64b4c4;
    image: url({check_icon_path})
}}
QCheckBox::indicator:unchecked {{
    width: 15px;
    height: 15px;
    border-radius: 4px;
    border-style:solid;
    border-width:1px;
    border-color:#64b4c4;
    background-color:qlineargradient(x1: 0, y1: 1, x2: 1, y2: 0,stop: 0 #f3d5f7, stop: 0.5 #fbf6e7,stop: 1 #e6fcf5);
}}

{pushbuttonStyle}
"""
'''
class SettingUI(QWidget):
    close_setting = Signal(name='close_setting')
    scale_changed = Signal(name='scale_changed')
    ontop_changed = Signal(name='ontop_changed')

    def __init__(self, parent=None):
        super(SettingUI, self).__init__(parent)
        self.is_follow_mouse = False

        # SettingUI window
        self.centralwidget = QFrame()
        self.centralwidget.setStyleSheet(SettingStyle)
        vbox_s = QVBoxLayout()

        hbox_t0 = QHBoxLayout()
        self.title = QLabel("设置")
        self.title.setStyleSheet(TomatoTitle)
        icon = QLabel()
        #icon.setStyleSheet(TomatoTitle)
        image = QImage()
        image.load(os.path.join(basedir,'res/icons/Setting_icon.png'))
        icon.setScaledContents(True)
        icon.setPixmap(QPixmap.fromImage(image)) #.scaled(20,20)))
        icon.setFixedSize(int(25*size_factor), int(25*size_factor))
        hbox_t0.addWidget(icon, Qt.AlignBottom | Qt.AlignLeft)
        hbox_t0.addWidget(self.title, Qt.AlignVCenter | Qt.AlignLeft)
        hbox_t0.addStretch(1)

        # 缩放
        self.button_close = QPushButton()
        self.button_close.setStyleSheet(TomatoClose)
        self.button_close.setFixedSize(int(20*size_factor), int(20*size_factor))
        self.button_close.setIcon(QIcon(os.path.join(basedir,'res/icons/close_icon.png')))
        self.button_close.setIconSize(QSize(int(20*size_factor),int(20*size_factor)))
        self.button_close.clicked.connect(self.close_setting)
        hbox_t0.addWidget(self.button_close, Qt.AlignTop | Qt.AlignRight)

        self.slider_scale = QSlider(Qt.Horizontal)
        self.slider_scale.setMinimum(1)
        self.slider_scale.setMaximum(500)
        self.slider_scale.setValue(settings.tunable_scale*100)
        self.slider_scale.setTickInterval(5)
        self.slider_scale.setTickPosition(QSlider.TicksAbove)
        self.scale_label = QLabel("宠物缩放: ") # %s"%(self.slider_scale.value()/100))

        self.scale_text = QLineEdit()
        qfltv = QDoubleValidator()
        qfltv.setRange(0,5,2)
        qfltv.setNotation(QDoubleValidator.StandardNotation)
        #qfltv.setDecimals(2)
        self.scale_text.setValidator(qfltv)
        self.scale_text.setMaxLength(4)
        self.scale_text.setAlignment(Qt.AlignCenter)
        self.scale_text.setFont(QFont("Arial",12))
        self.scale_text.setFixedSize(int(3*15*size_factor), int(20*size_factor))
        self.scale_text.setText(str(settings.tunable_scale))
        self.scale_text.textChanged.connect(self.scale_text_update)

        hbox_s1 = QHBoxLayout()
        hbox_s1.addWidget(self.scale_label)
        hbox_s1.addWidget(self.scale_text) #, Qt.AlignVCenter | Qt.AlignRight)

        self.slider_scale.valueChanged.connect(self.valuechange_scale)
        vbox_s1 = QVBoxLayout()
        vbox_s1.addLayout(hbox_s1)
        vbox_s1.addWidget(self.slider_scale)


        # 重力
        self.slider_gravity = QSlider(Qt.Horizontal)
        self.slider_gravity.setMinimum(1)
        self.slider_gravity.setMaximum(20)
        self.slider_gravity.setValue(settings.gravity*10)
        self.slider_gravity.setTickInterval(1)
        self.slider_gravity.setTickPosition(QSlider.TicksAbove)
        self.slider_gravity.valueChanged.connect(self.valuechange_gravity)

        self.gravity_label = QLabel("重力加速度: ") #%s"%(self.slider_gravity.value()/10))
        self.gravity_text = QLineEdit()
        qfltv = QDoubleValidator()
        qfltv.setRange(0,10,2)
        qfltv.setNotation(QDoubleValidator.StandardNotation)
        #qfltv.setDecimals(2)
        self.gravity_text.setValidator(qfltv)
        self.gravity_text.setMaxLength(4)
        self.gravity_text.setAlignment(Qt.AlignCenter)
        self.gravity_text.setFont(QFont("Arial",12))
        self.gravity_text.setFixedSize(int(3*15*size_factor), int(20*size_factor))
        self.gravity_text.setText(str(settings.gravity))
        self.gravity_text.textChanged.connect(self.gravity_text_update)
        hbox_s2 = QHBoxLayout()
        hbox_s2.addWidget(self.gravity_label)
        hbox_s2.addWidget(self.gravity_text)

        vbox_s2 = QVBoxLayout()
        vbox_s2.addLayout(hbox_s2)
        vbox_s2.addWidget(self.slider_gravity)

        self.slider_mouse = QSlider(Qt.Horizontal)
        self.slider_mouse.setMinimum(1)
        self.slider_mouse.setMaximum(20)
        self.slider_mouse.setValue(settings.fixdragspeedx*10)
        self.slider_mouse.setTickInterval(1)
        self.slider_mouse.setTickPosition(QSlider.TicksAbove)
        self.slider_mouse.valueChanged.connect(self.valuechange_mouse)

        self.mouse_label = QLabel("拖拽速度倍率: ") #%s"%(self.slider_mouse.value()/10))
        self.mouse_text = QLineEdit()
        qfltv = QDoubleValidator()
        qfltv.setRange(0,5,2)
        qfltv.setNotation(QDoubleValidator.StandardNotation)
        #qfltv.setDecimals(2)
        self.mouse_text.setValidator(qfltv)
        self.mouse_text.setMaxLength(4)
        self.mouse_text.setAlignment(Qt.AlignCenter)
        self.mouse_text.setFont(QFont("Arial",12))
        self.mouse_text.setFixedSize(int(3*15*size_factor), int(20*size_factor))
        self.mouse_text.setText(str(settings.fixdragspeedx))
        self.mouse_text.textChanged.connect(self.mouse_text_update)
        hbox_s3 = QHBoxLayout()
        hbox_s3.addWidget(self.mouse_label)
        hbox_s3.addWidget(self.mouse_text)

        vbox_s3 = QVBoxLayout()
        vbox_s3.addLayout(hbox_s3)
        vbox_s3.addWidget(self.slider_mouse)

        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setMinimum(0)
        self.slider_volume.setMaximum(10)
        self.slider_volume.setValue(settings.volume*10)
        self.slider_volume.setTickInterval(1)
        self.slider_volume.setTickPosition(QSlider.TicksAbove)
        self.volume_label = QLabel("音量: %s"%(self.slider_volume.value()/10))
        self.slider_volume.valueChanged.connect(self.valuechange_volume)
        vbox_s4 = QVBoxLayout()
        vbox_s4.addWidget(self.volume_label)
        vbox_s4.addWidget(self.slider_volume)

        self.checkA = QCheckBox("置顶宠物", self)
        if settings.on_top_hint:
            self.checkA.setChecked(True)
        self.checkA.stateChanged.connect(self.checks_update)
        vbox_s5 = QVBoxLayout()
        vbox_s5.addWidget(self.checkA)

        self.firstpet_label = QLabel("默认启动角色")
        self.first_pet = QComboBox()
        self.first_pet.setStyleSheet(ComboBoxStyle)
        pet_list = settings.pets #json.load(open(os.path.join(basedir,'res/role/pets.json'), 'r', encoding='UTF-8'))
        #pet_list.remove(settings.default_pet)
        #pet_list = [settings.default_pet] + pet_list
        self.first_pet.addItems(pet_list)
        self.first_pet.currentTextChanged.connect(self.change_firstpet)
        vbox_s6 = QVBoxLayout()
        vbox_s6.addWidget(self.firstpet_label)
        vbox_s6.addWidget(self.first_pet)

        # 开机自启

        #self.checkAutoStart = QCheckBox("开机自启", self)
        #vbox_s7 = QHBoxLayout()
        #vbox_s7.addWidget(self.checkAutoStart)


        vbox_s.addLayout(hbox_t0)
        vbox_s.addWidget(QHLine())
        vbox_s.addLayout(vbox_s5)
        #vbox_s.addLayout(vbox_s7)
        vbox_s.addLayout(vbox_s1)
        vbox_s.addLayout(vbox_s2)
        vbox_s.addLayout(vbox_s3)
        vbox_s.addLayout(vbox_s4)
        vbox_s.addLayout(vbox_s6)
        
        self.centralwidget.setLayout(vbox_s)
        self.layout_window = QVBoxLayout()
        self.layout_window.addWidget(self.centralwidget)
        self.setLayout(self.layout_window)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        if settings.platform == 'win32':
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)

    def mousePressEvent(self, event):
        """
        鼠标点击事件
        :param event: 事件
        :return:
        """
        if event.button() == Qt.LeftButton:
            # 左键绑定拖拽
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件, 左键且绑定跟随, 移动窗体
        :param event:
        :return:
        """
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        松开鼠标操作
        :param event:
        :return:
        """
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def valuechange_scale(self):
        #print(self.slider_scale.value())
        if settings.tunable_scale >=5 and self.slider_scale.value()==500:
            self.scale_changed.emit()
        else:
            settings.tunable_scale = self.slider_scale.value()/100
            settings.save_settings()
            #self.scale_label.setText("宠物缩放: %s"%(self.slider_scale.value()/100))
            self.scale_text.setText(str(settings.tunable_scale))
            self.scale_changed.emit()

    def scale_text_update(self):
        try:
            scale = float(self.scale_text.text())
        except:
            return
        if scale == 0:
            return
        elif scale == settings.tunable_scale:
            return

        settings.tunable_scale = scale
        settings.save_settings()
        self.slider_scale.setValue(min(5,scale)*100)


    def valuechange_gravity(self):
        if settings.gravity >=2 and self.slider_gravity.value()==20:
            return
        else:
            settings.gravity = self.slider_gravity.value()/10
            settings.save_settings()
            #self.gravity_label.setText("重力加速度: %s"%(self.slider_gravity.value()/10))
            self.gravity_text.setText(str(settings.gravity))
        #self.gravity_changed.emit()

    def gravity_text_update(self):
        try:
            g = float(self.gravity_text.text())
        except:
            return
        if g == 0:
            return
        elif g == settings.gravity:
            return

        settings.gravity = g
        settings.save_settings()
        self.slider_gravity.setValue(min(2,g)*10)


    def valuechange_mouse(self):
        if settings.fixdragspeedx >=2 and self.slider_mouse.value()==20:
            return
        else:
            settings.fixdragspeedx, settings.fixdragspeedy = self.slider_mouse.value()/10, self.slider_mouse.value()/10
            #self.mouse_label.setText("鼠标拖拽速度: %s"%(self.slider_mouse.value()/10))
            settings.save_settings()
            self.mouse_text.setText(str(settings.fixdragspeedx))

        #print(self.slider_mouse.value(), settings.fixdragspeedx)

    def mouse_text_update(self):
        try:
            mouse = float(self.mouse_text.text())
        except:
            return
        if mouse == 0:
            return
        elif mouse == settings.fixdragspeedx:
            return

        settings.fixdragspeedx, settings.fixdragspeedy = mouse, mouse
        settings.save_settings()
        self.slider_mouse.setValue(min(2,mouse)*10)


    def valuechange_volume(self):
        settings.volume = self.slider_volume.value()/10
        self.volume_label.setText("音量: %s"%(self.slider_volume.value()/10))
        settings.save_settings()

    def checks_update(self, state):
        # checking if state is checked
        if state == Qt.Checked:
            # if first check box is selected
            if self.sender() == self.checkA:
                settings.on_top_hint = True
                settings.save_settings()
                self.ontop_changed.emit()
            else:
                return
        elif state == Qt.Unchecked:
            if self.sender() == self.checkA:
                settings.on_top_hint = False
                settings.save_settings()
                self.ontop_changed.emit()
            else:
                return
        else:
            return

    def change_firstpet(self, pet_name):
        settings.default_pet = pet_name
        settings.save_settings()
        """
        pet_list = json.load(open(os.path.join(basedir,'res/role/pets.json'), 'r', encoding='UTF-8'))
        pet_list.remove(pet_name)
        pet_list = [pet_name] + pet_list
        with open(os.path.join(basedir,'res/role/pets.json'), 'w', encoding='utf-8') as f:
            json.dump(pet_list, f, ensure_ascii=False, indent=4)
        """
'''



class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        #self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet(LineStyle)

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        #self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet(LineStyle)


##############################
#           番茄钟
##############################

TomatoTitle = """
QLabel {
    border: 0;
    background-color: #F5F4EF;
    font-size: 15px;
    font-family: "黑体";
    width: 10px;
    height: 20px
}
"""

TomatoClose = """
QPushButton {
    background-color: #ffbdad;
    padding: 0px;
    border-style: solid;
    border-width: 2px;
    border-radius: 10px;
    border-color: transparent;
    text-align:middle;
}

QPushButton:hover:!pressed {
    background-color: #ffb19e;
}
QPushButton:pressed {
    background-color: #ffa48f;
}
QPushButton:disabled {
    background-color: #e0e1e0;
}
"""

TomatoStyle = f"""
QFrame {{
    background:#F5F4EF;
    border: 3px solid #F5F4EF;
    border-radius: 10px;
}}

QLabel {{
    font-size: 16px;
    font-family: "黑体";
}}

{pushbuttonStyle}
"""


##############################
#          备忘录 & 提醒
##############################

CloseButtonStyle = """
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 10px;
}
QPushButton:hover:!pressed {
    background-color: rgba(0, 0, 0, 25);
}
QPushButton:pressed {
    background-color: rgba(0, 0, 0, 40);
}
"""


def _memo_qss(dark=None):
    """备忘录简约卡片样式（暖橙主色 + 深浅双主题）"""
    p = active_palette(dark)
    accent = p['primary']
    return f"""
#memoFrame {{
    background: {p['card']};
    border-radius: 12px;
    border: 1px solid {p['border']};
}}
#memoFrame QLabel#memoTitle {{
    font-size: 15px;
    font-weight: 600;
    color: {p['text']};
}}
#memoFrame QTextEdit {{
    border: 1px solid {p['border']};
    border-radius: 8px;
    background: {p['card']};
    padding: 8px;
    font-size: 13px;
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI";
    color: {p['text']};
    selection-background-color: {accent};
}}
#memoFrame QTextEdit:focus {{
    border: 1px solid {accent};
}}
"""

class MemoWindow(QWidget):
    """备忘录：单一文本框，自动保存自动加载"""
    close_memo = Signal(name='close_memo')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_follow_mouse = False
        self.memo_path = os.path.join(configdir, 'data/remindme.txt')

        self.centralwidget = QFrame()
        self.centralwidget.setObjectName('memoFrame')
        self.centralwidget.setStyleSheet(_memo_qss())

        vbox = QVBoxLayout(self.centralwidget)
        vbox.setContentsMargins(12, 10, 12, 12)
        vbox.setSpacing(10)

        # 标题栏
        hbox_title = QHBoxLayout()
        hbox_title.setSpacing(6)
        icon = QLabel()
        icon.setFixedSize(22, 22)
        icon.setScaledContents(True)
        if qta is not None:
            c = '#FFFFFF' if isDarkTheme() else '#000000'
            icon.setPixmap(qta.icon('fa5s.sticky-note', color=c).pixmap(22, 22))
        else:
            image = QImage()
            image.load(os.path.join(basedir, 'res/icons/Dialogue_icon.png'))
            icon.setPixmap(QPixmap.fromImage(image))
        self.title_label = QLabel(self.tr('Memo'))
        self.title_label.setObjectName('memoTitle')
        self.close_button = QPushButton()
        self.close_button.setStyleSheet(CloseButtonStyle)
        self.close_button.setFixedSize(20, 20)
        if qta is not None:
            c = '#FFFFFF' if isDarkTheme() else '#000000'
            self.close_button.setIcon(qta.icon('fa5s.times', color=c))
        else:
            self.close_button.setIcon(QIcon(os.path.join(basedir, 'res/icons/close_icon.png')))
        self.close_button.setIconSize(QSize(12, 12))
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.close_memo)
        hbox_title.addWidget(icon)
        hbox_title.addWidget(self.title_label)
        hbox_title.addStretch(1)
        hbox_title.addWidget(self.close_button)

        # 文本编辑区
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(self.tr('Write down anything here...'))
        self.text_edit.textChanged.connect(self._save)

        vbox.addLayout(hbox_title)
        vbox.addWidget(self.text_edit, 1)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.addWidget(self.centralwidget)
        self.setFixedSize(380, 460)
        shadow = QGraphicsDropShadowEffect(self.centralwidget)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 45))
        self.centralwidget.setGraphicsEffect(shadow)

        self._load()

        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        if platform == 'win32':
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)

    def _load(self):
        try:
            if os.path.isfile(self.memo_path):
                with open(self.memo_path, 'r', encoding='UTF-8') as f:
                    self.text_edit.setPlainText(f.read())
        except Exception:
            pass

    def _save(self):
        try:
            with open(self.memo_path, 'w', encoding='UTF-8') as f:
                f.write(self.text_edit.toPlainText())
        except Exception:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))


def _reminder_qss(dark=None):
    """提醒窗口简约卡片样式（暖橙主色 + 深浅双主题）"""
    p = active_palette(dark)
    accent = p['primary']
    return f"""
#reminderFrame {{
    background: {p['card']};
    border-radius: 12px;
    border: 1px solid {p['border']};
}}
#reminderFrame QLabel#reminderTitle {{
    font-size: 15px;
    font-weight: 600;
    color: {p['text']};
}}
#reminderFrame QPushButton#confirmButton {{
    border: 1px solid {accent};
    border-radius: 6px;
    background: transparent;
    color: {accent};
    font-size: 13px;
    padding: 4px 14px;
}}
#reminderFrame QPushButton#confirmButton:hover {{
    background: rgba(232, 135, 74, 15);
}}
#reminderFrame QPushButton#confirmButton:disabled {{
    border: 1px solid {p['border']};
    color: {p['textDisabled']};
    background: transparent;
}}
QScrollArea#reminderScroll, QScrollArea#reminderScroll > QWidget > QWidget {{
    border: none;
    background: transparent;
}}
#reminderList {{
    background: transparent;
}}
ReminderItem {{
    background: {p['card']};
    border-radius: 8px;
    border: 1px solid {p['border']};
}}
ReminderItem QLineEdit {{
    border: none;
    border-bottom: 1px solid {p['border']};
    background: transparent;
    padding: 4px 2px;
    font-size: 13px;
    color: {p['text']};
}}
ReminderItem QLineEdit:focus {{
    border-bottom: 2px solid {accent};
}}
ReminderItem QDateTimeEdit {{
    border: 1px solid {p['border']};
    border-radius: 6px;
    background: {p['card']};
    padding: 2px 6px;
    font-size: 12px;
    color: {p['text']};
}}
ReminderItem QPushButton#deleteButton {{
    border: none;
    border-radius: 6px;
    background: transparent;
    color: #d93025;
    font-size: 12px;
    padding: 4px 8px;
}}
ReminderItem QPushButton#deleteButton:hover {{
    background: rgba(217, 48, 37, 15);
}}
ReminderItem[completed="true"] QLineEdit {{
    color: {p['textDisabled']};
    border-bottom: 1px solid {p['border']};
}}
ReminderItem[completed="true"] QDateTimeEdit {{
    color: {p['textDisabled']};
    background: {p['hover']};
}}
"""

class ReminderItem(QWidget):
    """单条提醒：事项文本框 + 日期时间选择"""
    removed = Signal(QWidget, name='removed')

    def __init__(self, text='', dt_str=None, completed=False, parent=None):
        super().__init__(parent)
        self.completed = False

        self.text_edit = QLineEdit(text)
        self.text_edit.setPlaceholderText(self.tr('What to remind?'))
        self.text_edit.setClearButtonEnabled(True)

        dt = self._parse_dt(dt_str) if dt_str else (datetime.now() + timedelta(hours=1))
        self.dt_edit = QDateTimeEdit(QDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))
        self.dt_edit.setDisplayFormat('yyyy-MM-dd HH:mm')
        self.dt_edit.setCalendarPopup(True)
        self.dt_edit.setMinimumWidth(150)

        self.delete_button = QPushButton(self.tr('Delete'))
        self.delete_button.setObjectName('deleteButton')
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.clicked.connect(lambda: self.removed.emit(self))

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(10, 8, 10, 8)
        hbox.setSpacing(8)
        hbox.addWidget(self.text_edit, 1)
        hbox.addWidget(self.dt_edit)
        hbox.addWidget(self.delete_button)

        if completed:
            self.set_completed(True)

    def set_completed(self, completed):
        """标记为已完成：锁定内容并置灰显示（保留在列表中）"""
        self.completed = completed
        self.setProperty('completed', completed)
        self.style().unpolish(self)
        self.style().polish(self)
        self.text_edit.setReadOnly(completed)
        self.dt_edit.setEnabled(not completed)

    def get_text(self):
        return self.text_edit.text().strip()

    def get_datetime(self):
        qdt = self.dt_edit.dateTime()
        return datetime(qdt.date().year(), qdt.date().month(), qdt.date().day(),
                        qdt.time().hour(), qdt.time().minute())

    def _parse_dt(self, s):
        try:
            return datetime.strptime(s, '%Y-%m-%d %H:%M')
        except Exception:
            return datetime.now() + timedelta(hours=1)


class ReminderWindow(QWidget):
    """提醒：多实例（事项 + 日期时间），到点触发通知"""
    close_reminder = Signal(name='close_reminder')
    remind_trigger = Signal(str, name='remind_trigger')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_follow_mouse = False
        self.reminder_path = os.path.join(configdir, 'data/reminders.json')
        self._items = []

        self.centralwidget = QFrame()
        self.centralwidget.setObjectName('reminderFrame')
        self.centralwidget.setStyleSheet(_reminder_qss())

        vbox = QVBoxLayout(self.centralwidget)
        vbox.setContentsMargins(12, 10, 12, 12)
        vbox.setSpacing(10)

        # 标题栏
        hbox_title = QHBoxLayout()
        hbox_title.setSpacing(6)
        icon = QLabel()
        icon.setFixedSize(22, 22)
        icon.setScaledContents(True)
        if qta is not None:
            c = '#FFFFFF' if isDarkTheme() else '#000000'
            icon.setPixmap(qta.icon('fa5s.bell', color=c).pixmap(22, 22))
        else:
            image = QImage()
            image.load(os.path.join(basedir, 'res/icons/remind_icon.png'))
            icon.setPixmap(QPixmap.fromImage(image))
        self.title_label = QLabel(self.tr('Reminders'))
        self.title_label.setObjectName('reminderTitle')
        self.close_button = QPushButton()
        self.close_button.setStyleSheet(CloseButtonStyle)
        self.close_button.setFixedSize(20, 20)
        if qta is not None:
            c = '#FFFFFF' if isDarkTheme() else '#000000'
            self.close_button.setIcon(qta.icon('fa5s.times', color=c))
        else:
            self.close_button.setIcon(QIcon(os.path.join(basedir, 'res/icons/close_icon.png')))
        self.close_button.setIconSize(QSize(12, 12))
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.close_reminder)
        hbox_title.addWidget(icon)
        hbox_title.addWidget(self.title_label)
        hbox_title.addStretch(1)
        hbox_title.addWidget(self.close_button)

        # 草稿输入行（文本框 + 日期时间 + 确认按钮）
        self.draft_text = QLineEdit()
        self.draft_text.setPlaceholderText(self.tr('What to remind?'))
        self.draft_text.setClearButtonEnabled(True)
        self.draft_text.textChanged.connect(self._update_confirm_btn)

        now_dt = datetime.now() + timedelta(hours=1)
        self.draft_dt = QDateTimeEdit(QDateTime(now_dt.year, now_dt.month, now_dt.day,
                                                now_dt.hour, now_dt.minute, now_dt.second))
        self.draft_dt.setDisplayFormat('yyyy-MM-dd HH:mm')
        self.draft_dt.setCalendarPopup(True)
        self.draft_dt.setMinimumWidth(150)

        self.confirm_button = QPushButton(self.tr('Confirm'))
        self.confirm_button.setObjectName('confirmButton')
        self.confirm_button.setCursor(Qt.PointingHandCursor)
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self._confirm_draft)

        hbox_draft = QHBoxLayout()
        hbox_draft.setContentsMargins(0, 0, 0, 0)
        hbox_draft.setSpacing(8)
        hbox_draft.addWidget(self.draft_text, 1)
        hbox_draft.addWidget(self.draft_dt)
        hbox_draft.addWidget(self.confirm_button)

        # 列表
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName('reminderScroll')
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.viewport().setAutoFillBackground(False)
        self.list_widget = QWidget()
        self.list_widget.setObjectName('reminderList')
        self.list_widget.setAutoFillBackground(False)
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch(1)
        self.scroll_area.setWidget(self.list_widget)

        vbox.addLayout(hbox_title)
        vbox.addLayout(hbox_draft)
        vbox.addWidget(self.scroll_area, 1)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.addWidget(self.centralwidget)
        self.setFixedSize(520, 480)
        shadow = QGraphicsDropShadowEffect(self.centralwidget)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 45))
        self.centralwidget.setGraphicsEffect(shadow)

        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        if platform == 'win32':
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)

        self._load()

        # 到期检查（20s 轮询）
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self._check_reminders)
        self.check_timer.start(20000)

    def _update_confirm_btn(self, text=''):
        """只有事项非空时才允许确认"""
        self.confirm_button.setEnabled(bool(self.draft_text.text().strip()))

    def _confirm_draft(self):
        text = self.draft_text.text().strip()
        if not text:
            return
        qdt = self.draft_dt.dateTime()
        dt_str = datetime(qdt.date().year(), qdt.date().month(), qdt.date().day(),
                          qdt.time().hour(), qdt.time().minute()).strftime('%Y-%m-%d %H:%M')
        self._add_item(text, dt_str)
        # 清空草稿并重置时间
        self.draft_text.clear()
        new_dt = datetime.now() + timedelta(hours=1)
        self.draft_dt.setDateTime(QDateTime(new_dt.year, new_dt.month, new_dt.day,
                                            new_dt.hour, new_dt.minute, new_dt.second))

    def _add_item(self, text='', dt_str=None, completed=False):
        item = ReminderItem(text, dt_str, completed)
        item.removed.connect(self._remove_item)
        self.list_layout.insertWidget(self.list_layout.count() - 1, item)
        self._items.append(item)
        self._save()
        return item

    def _remove_item(self, item):
        if item in self._items:
            self._items.remove(item)
            self.list_layout.removeWidget(item)
            item.deleteLater()
            self._save()

    def _clear_items(self):
        for item in self._items[:]:
            self._remove_item(item)

    def _save(self):
        try:
            data = [{'text': it.get_text(), 'datetime': it.get_datetime().strftime('%Y-%m-%d %H:%M'),
                     'completed': it.completed}
                    for it in self._items]
            with open(self.reminder_path, 'w', encoding='UTF-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load(self):
        self._clear_items()
        try:
            if os.path.isfile(self.reminder_path):
                with open(self.reminder_path, 'r', encoding='UTF-8') as f:
                    data = json.load(f)
                for d in data:
                    self._add_item(d.get('text', ''), d.get('datetime'), d.get('completed', False))
        except Exception:
            pass

    def _check_reminders(self):
        now = datetime.now()
        for item in self._items[:]:
            if not item.completed and item.get_datetime() <= now:
                text = item.get_text()
                if text:
                    self.remind_trigger.emit(text)
                # 完成后保留在列表，标记为已完成
                item.set_completed(True)
                self._save()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))


##############################
#          背包系统
##############################

ItemStyle = """
QLabel{
    border : 2px solid #EFEBDF;
    border-radius: 5px;
    background-color: #EFEBDF
}
"""

CollectStyle = """
QLabel{
    border : 2px solid #e1eaf4;
    border-radius: 5px;
    background-color: #e1eaf4
}
"""

ItemClick = """
QLabel{
    border : 2px solid #B1C790;
    border-radius: 5px;
    background-color: #EFEBDF
}
"""

CollectClick = """
QLabel{
    border : 2px solid #B1C790;
    border-radius: 5px;
    background-color: #e1eaf4
}
"""

EmptyStyle = """
QLabel{
    border : 2px solid #EFEBDF;
    border-radius: 5px;
    background-color: #EFEBDF
}
"""

class Inventory_item(QLabel):
    clicked = Signal()
    Ii_selected = Signal(tuple, bool, name="Ii_selected")
    Ii_removed = Signal(tuple, name="Ii_removed")

    '''特性
    
    - 固定大小的正方形
    - 主界面是物品UI
    - 右下角是物品个数
    - 鼠标点击时更改背景颜色
    - 鼠标停留时显示物品信息

    - 可更改个数
    - 可更改图片
    - 可更改背景

    '''
    def __init__(self, cell_index, item_config=None, item_num=0):
        '''item_config
        
        name: str
        img: Pixmap object
        number: int
        effect_HP: int
        effect_FV: int
        drop_rate: float
        description: str

        '''
        super(Inventory_item, self).__init__()
        self.cell_index = cell_index

        self.item_config = item_config
        self.item_name = 'None'
        self.image = None
        self.item_num = item_num
        self.selected = False
        self.size_wh = int(56) #*size_factor)

        self.setFixedSize(self.size_wh,self.size_wh)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        #self.installEventFilter(self)
        #self.setPixmap(QPixmap.fromImage())
        self.font = QFont()
        self.font.setPointSize(self.size_wh/8)
        self.font.setBold(True)
        self.clct_inuse = False

        if item_config is not None:
            self.item_name = item_config['name']
            self.image = item_config['image']
            self.image = self.image.scaled(self.size_wh,self.size_wh, mode=Qt.SmoothTransformation)
            self.setPixmap(QPixmap.fromImage(self.image))
            self.installEventFilter(ToolTipFilter(self, showDelay=500))
            self.setToolTip(item_config['hint'])
            if self.item_config.get('item_type', 'consumable') in ['collection', 'dialogue']:
                self.setStyleSheet(CollectStyle)
            else:
                self.setStyleSheet(ItemStyle) #"QLabel{border : 3px solid #4c9bf7; border-radius: 5px}")
        else:
            self.setStyleSheet(EmptyStyle) #"QLabel{border : 3px solid #6d6f6d; border-radius: 5px}")

    def mousePressEvent(self, ev):
        self.clicked.emit()

    def mouseReleaseEvent(self, event):
        if self.item_config is not None:
            if self.selected:
                self.Ii_selected.emit(self.cell_index, self.clct_inuse)
                if self.item_config.get('item_type', 'consumable') in ['collection', 'dialogue']:
                    self.setStyleSheet(CollectStyle)
                else:
                    self.setStyleSheet(ItemStyle)
                #self.setStyleSheet(ItemStyle) #"QLabel{border : 3px solid #4c9bf7; border-radius: 5px}")
                self.selected = False
            else:
                if self.item_config.get('item_type', 'consumable') in ['collection', 'dialogue']:
                    self.setStyleSheet(CollectClick)
                else:
                    self.setStyleSheet(ItemClick)
                #self.setStyleSheet(ItemClick) #"QLabel{border : 3px solid #ee171d; border-radius: 5px}")
                self.Ii_selected.emit(self.cell_index, self.clct_inuse)
                self.selected = True
        #pass # change background, enable Feed bottom

    def paintEvent(self, event):
        super(Inventory_item, self).paintEvent(event)
        if self.item_num > 1:
            text_printer = QPainter(self)
            text_printer.setFont(self.font)
            text_printer.drawText(QRect(0, 0, int(self.size_wh-3), int(self.size_wh-3)), Qt.AlignBottom | Qt.AlignRight, str(self.item_num))
            #text_printer.drawText(QRect(0, 0, int(self.size_wh-3*size_factor), int(self.size_wh-3*size_factor)), Qt.AlignBottom | Qt.AlignRight, str(self.item_num))



    def unselected(self):
        self.selected = False
        if self.item_config.get('item_type', 'consumable') in ['collection', 'dialogue']:
            self.setStyleSheet(CollectStyle)
        else:
            self.setStyleSheet(ItemStyle)
        #self.setStyleSheet(ItemStyle) #"QLabel{border : 3px solid #4c9bf7; border-radius: 5px}")

    def registItem(self, item_config, n_items):
        self.item_config = item_config
        self.item_num = n_items
        self.item_name = item_config['name']
        self.image = item_config['image']
        self.image = self.image.scaled(self.size_wh,self.size_wh, mode=Qt.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.image))
        self.setToolTip(item_config['hint'])
        if self.item_config.get('item_type', 'consumable') in ['collection', 'dialogue']:
            self.setStyleSheet(CollectStyle)
        else:
            self.setStyleSheet(ItemStyle)
        #self.setStyleSheet(ItemStyle) #"QLabel{border : 3px solid #4c9bf7; border-radius: 5px}")

    def addItem(self, add_n):
        self.item_num += add_n
        self.setPixmap(QPixmap.fromImage(self.image))

    def consumeItem(self):
        if self.item_config.get('item_type', 'consumable') in ['collection', 'dialogue']:
            self.clct_inuse = not self.clct_inuse
        else:
            self.item_num += -1
            if self.item_num == 0:
                self.removeItem()
            else:
                self.setPixmap(QPixmap.fromImage(self.image))
    '''
    def changeNum(self):
        self.setPixmap(QPixmap.fromImage(self.image))
    '''

    def removeItem(self):
        # 告知Inventory item被移除
        self.Ii_removed.emit(self.cell_index)

        self.item_config = None
        self.item_name = 'None'
        self.image = None
        self.item_num = 0
        self.selected = False

        self.clear()
        self.setToolTip('')
        self.setStyleSheet(EmptyStyle) #"QLabel{border : 3px solid #6d6f6d; border-radius: 5px}")
        

    def changeBackground(self):
        pass


ItemGroupStyle = """
QGroupBox {
    border: 1px solid transparent;
    background-color: #F5F4EF;
    border-radius: 10px
}
"""

IvenTitle = """
QLabel {
    border: 0;
    background-color: #F5F4EF;
    font-size: 15px;
    font-family: "黑体";
    width: 10px;
    height: 10px
}
"""

InvenStyle = """
QFrame{
    background:#F5F4EF;
    border: 3px solid #F5F4EF;
    border-radius: 10px
}

QScrollArea {
    padding: 2px;
    border: 0px solid #9f7a6a;
    background-color: #F5F4EF;
    border-radius: 10px
}

QPushButton {
    width: 60px;
    background-color: #ffbdad;
    color: #000000;
    border-style: solid;
    padding: 7px;
    font: 16px;
    font-family: "黑体";
    border-width: 3px;
    border-radius: 15px;
    border-color: #B39C86;
}
QPushButton:hover:!pressed {
    background-color: #ffb19e;
}
QPushButton:pressed {
    background-color: #ffa48f;
}
QPushButton:disabled {
    background-color: #e0e1e0;
}
QScrollBar:vertical {
    background-color: #F5F4EF;
    width: 15px;
    margin: 5px 1px 5px 1px;
    border: 1px #F5F4EF;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    width: 15px;
    background-color: #FFC8BB;         /* #f184ae; */
    min-height: 5px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical {
height: 0px;
}

QScrollBar::sub-line:vertical {
height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
height: 0px;
}
"""

TabStyle = """
QTabWidget::pane {
    border: 3px solid #9f7a6a;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    border-bottom-left-radius: 10px;
    background-color: #F5F4EF;
}

QTabWidget::tab-bar:top {
    top: 3px;
}
QTabWidget::tab-bar:bottom {
    bottom: 3px;
}

QTabWidget::tab-bar:left {
    right: 3px;
}

QTabWidget::tab-bar:right {
    left: 3px;
}

QTabBar::tab {
    border: 3px solid #9f7a6a;
    border-top-right-radius: 8px;
    border-top-left-radius: 8px;
    width: 30px;
}

QTabBar::tab:selected {
    background: #F5F4EF;
}

QTabBar::tab:!selected {
    background: #ffdad1;
}

QTabBar::tab:!selected:hover {
    background: #FFC8BB;
}

QTabBar::tab:top:!selected {
    margin-top: 3px;
}

QTabBar::tab:bottom:!selected {
    margin-bottom: 3px;
}


QTabBar::tab:top, QTabBar::tab:bottom {
    min-width: 8ex;
    margin-right: -1px;
    padding: 5px 10px 5px 10px;
}

QTabBar::tab:top:selected {
    border-bottom: 5px;
    border-bottom-color: none;
}

QTabBar::tab:bottom:selected {
    border-top-color: none;
}

QTabBar::tab:top:last, QTabBar::tab:bottom:last,
QTabBar::tab:top:only-one, QTabBar::tab:bottom:only-one {
    margin-right: 0;
}

QTabBar::tab:left:!selected {
    margin-right: 3px;
}

QTabBar::tab:right:!selected {
    margin-left: 3px;
}

QTabBar::tab:left, QTabBar::tab:right {
    min-height: 8ex;
    margin-bottom: -1px;
    padding: 10px 5px 10px 5px;
}

QTabBar::tab:left:selected {
    border-left-color: none;
}

QTabBar::tab:right:selected {
    border-right-color: none;
}

QTabBar::tab:left:last, QTabBar::tab:right:last,
QTabBar::tab:left:only-one, QTabBar::tab:right:only-one {
    margin-bottom: 0;
}
"""

class Inventory(QWidget):
    close_inventory = Signal(name='close_inventory')
    use_item_inven = Signal(str, name='use_item_inven')
    item_note = Signal(str, str, name='item_note')
    item_anim = Signal(str, name='item_anim')
    #confirm_inventory = Signal(str, int, int, str, name='confirm_inventory')

    def __init__(self, items_data, parent=None):
        super(Inventory, self).__init__(parent)

        self.is_follow_mouse = False
        self.items_data = items_data
        self.calculate_droprate()
        self.selected_cell = None
        self.inven_shape = (5,3)
        self.items_numb = {}
        self.cells_dict = {}
        self.empty_cell = {}
        self.tab_dict = {'consumable':0, 'collection':1, 'dialogue':1}

        # 界面设计
        self.centralwidget = QFrame()

        self.FoodGroupBox = QGroupBox()
        self.FoodGroupBox.setStyleSheet(ItemGroupStyle)
        self.FoodGridLayout = self.construct_item_tab(['consumable'], 0)
        self.FoodGroupBox.setLayout(self.FoodGridLayout)
        self.FoodScrollArea = QScrollArea(self)
        self.FoodScrollArea.setFrameShape(QFrame.NoFrame)
        self.FoodScrollArea.setWidgetResizable(True)
        self.FoodScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.FoodScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.FoodScrollArea.setWidget(self.FoodGroupBox)

        self.ClctGroupBox = QGroupBox()
        self.ClctGroupBox.setStyleSheet(ItemGroupStyle)
        self.ClctGridLayout = self.construct_item_tab(['collection', 'dialogue'], 1)
        self.ClctGroupBox.setLayout(self.ClctGridLayout)
        self.ClctScrollArea = QScrollArea(self)
        self.ClctScrollArea.setFrameShape(QFrame.NoFrame)
        self.ClctScrollArea.setWidgetResizable(True)
        self.ClctScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ClctScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ClctScrollArea.setWidget(self.ClctGroupBox)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(TabStyle)

        self.tab_widget.addTab(self.FoodScrollArea, QIcon(os.path.join(basedir,'res/icons/tab_1.svg')), '')
        self.tab_widget.addTab(self.ClctScrollArea, QIcon(os.path.join(basedir,'res/icons/tab_2.svg')), '')
        self.tab_widget.setIconSize(QSize(int(30), int(20)))
        #self.tab_widget.setIconSize(QSize(int(30*size_factor), int(20*size_factor)))

        self.layer_dict = {'consumable':self.FoodGridLayout,
                           'collection':self.ClctGridLayout, 
                           'dialogue':self.ClctGridLayout}


        hbox = QHBoxLayout()
        self.button_confirm = QPushButton(self.tr("Use")) #, objectName='InvenButton')
        #self.button_confirm.setFont(QFont('黑体', all_font_size))
        self.button_confirm.clicked.connect(self.confirm)
        self.button_confirm.setDisabled(True)
        #self.button_confirm.setStyleSheet(InventQSS)
        '''
        self.button_confirm.setStyleSheet("QPushButton {\
                                                background-color: #bcbdbc;\
                                                color: #000000;\
                                                border-style: outset;\
                                                padding: 3px;\
                                                font: bold 15px;\
                                                border-width: 2px;\
                                                border-radius: 10px;\
                                                border-color: #facccc;\
                                            }\
                                            QPushButton:pressed {\
                                                background-color: lightgreen;\
                                            }")
        '''
        self.button_cancel = QPushButton(self.tr("Close")) #, objectName='InvenButton')
        #self.button_cancel.setStyleSheet(objectName='InvenButton')

        #self.button_cancel.setFont(QFont('黑体', all_font_size))
        self.button_cancel.clicked.connect(self.close_inventory)
        hbox.addStretch()
        hbox.addWidget(self.button_confirm)
        hbox.addStretch()
        hbox.addWidget(self.button_cancel)
        hbox.addStretch()

        hbox_0 = QHBoxLayout()
        self.title = QLabel(self.tr("Pet Backpack"))
        self.title.setStyleSheet(IvenTitle)
        icon = QLabel()
        icon.setStyleSheet(IvenTitle)
        inven_image = QImage()
        inven_image.load(os.path.join(basedir,'res/icons/Inven_icon.png'))
        icon.setScaledContents(True)
        icon.setPixmap(QPixmap.fromImage(inven_image.scaled(int(20), int(20))))
        #icon.setPixmap(QPixmap.fromImage(inven_image.scaled(int(20*size_factor), int(20*size_factor))))
        hbox_0.addWidget(icon)
        hbox_0.addWidget(self.title)
        hbox_0.addStretch()
        hbox_0.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        windowLayout = QVBoxLayout()
        #windowLayout.addWidget(QLabel(" "))
        windowLayout.addLayout(hbox_0)
        #windowLayout.addWidget(QLabel(" "))
        windowLayout.addWidget(self.tab_widget) #ItemGroupBox)
        windowLayout.addLayout(hbox)

        #radius = 10
        self.centralwidget.setLayout(windowLayout)
        self.centralwidget.setStyleSheet(InvenStyle)
        self.layout_window = QVBoxLayout()
        self.layout_window.addWidget(self.centralwidget)
        self.setLayout(self.layout_window)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        if settings.platform == 'win32':
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)


        #self.setLayout(windowLayout)
        #self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        #self.setFixedSize(235,379)
        #self.setStyleSheet(InvenStyle)
        '''
        radius = 10.0
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)
        '''

    def construct_item_tab(self, item_types, tab_index):

        layout = QGridLayout()
        layout.setVerticalSpacing(9)
        self.empty_cell[tab_index] = []
        index_item = 0

        keys = settings.pet_data.items.keys()
        keys = [i for i in keys if i in self.items_data.item_dict.keys()]
        keys = [i for i in keys if self.items_data.item_dict[i]['item_type'] in item_types]
        if tab_index == 0:
            keys_lvl = [self.items_data.item_dict[i]['fv_lock'] for i in keys]
            keys = [x for _, x in sorted(zip(keys_lvl, keys))]
        else:
            keys = sorted(keys)

        for item in keys:
            if self.items_data.item_dict[item]['item_type'] not in item_types:
                continue
            if settings.pet_data.items[item] <= 0:
                continue

            n_row = index_item // self.inven_shape[1]
            n_col = (index_item - (n_row-1)*self.inven_shape[1]) % self.inven_shape[1]

            self.items_numb[(tab_index, index_item)] = int(settings.pet_data.items[item])
            self.cells_dict[(tab_index, index_item)] = Inventory_item((tab_index, index_item), self.items_data.item_dict[item], self.items_numb[(tab_index, index_item)])
            self.cells_dict[(tab_index, index_item)].Ii_selected.connect(self.change_selected)
            self.cells_dict[(tab_index, index_item)].Ii_removed.connect(self.item_removed)
            layout.addWidget(self.cells_dict[(tab_index, index_item)], n_row, n_col)
            index_item += 1

        if index_item < self.inven_shape[0]*self.inven_shape[1]:

            for j in range(index_item, (self.inven_shape[0]*self.inven_shape[1])):
                n_row = j // self.inven_shape[1]
                n_col = (j - (n_row-1)*self.inven_shape[1]) % self.inven_shape[1]

                self.items_numb[(tab_index,j)] = 0
                self.cells_dict[(tab_index,j)] = Inventory_item((tab_index,j))
                self.cells_dict[(tab_index,j)].Ii_selected.connect(self.change_selected)
                self.cells_dict[(tab_index,j)].Ii_removed.connect(self.item_removed)
                layout.addWidget(self.cells_dict[(tab_index,j)], n_row, n_col)

                self.empty_cell[tab_index].append(j)

        return layout
        
    def mousePressEvent(self, event):
        """
        鼠标点击事件
        :param event: 事件
        :return:
        """
        if event.button() == Qt.LeftButton:
            # 左键绑定拖拽
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件, 左键且绑定跟随, 移动窗体
        :param event:
        :return:
        """
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        松开鼠标操作
        :param event:
        :return:
        """
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def change_selected(self, selected_index, clct_inuse):

        if self.selected_cell == selected_index:
            self.selected_cell = None
            self.changeButton(clct_inuse)
        elif self.selected_cell is not None:
            self.cells_dict[self.selected_cell].unselected()
            self.selected_cell = selected_index
            self.changeButton(clct_inuse)
        else:
            self.selected_cell = selected_index
            self.changeButton(clct_inuse)

    def item_removed(self, rm_index):
        self.items_numb[rm_index] = 0
        self.empty_cell[rm_index[0]].append(rm_index[1])
        self.empty_cell[rm_index[0]].sort()

    def changeButton(self, clct_inuse=False):
        if self.selected_cell is None:
            self.button_confirm.setText(self.tr('Use'))
            self.button_confirm.setDisabled(True)
    
        else:
            if clct_inuse:
                self.button_confirm.setText(self.tr('Withdraw'))
            else:
                self.button_confirm.setText(self.tr('Use'))
            self.button_confirm.setDisabled(False)

    def acc_withdrawed(self, item_name):
        cell_index = [i for i in self.cells_dict.keys() if self.cells_dict[i].item_name==item_name]
        cell_index = cell_index[0]
        self.cells_dict[cell_index].consumeItem()


    def confirm(self):
        
        if self.selected_cell is None: #无选择
            return

        item_name_selected = self.cells_dict[self.selected_cell].item_name

        # 判断是否为个别宠物的专属物品
        if len(self.items_data.item_dict[item_name_selected]['pet_limit']) != 0:
            pet_list = self.items_data.item_dict[item_name_selected]['pet_limit']
            if settings.petname not in pet_list:
                self.item_note.emit('system', self.tr('Only available after switching to %s') % '、'.join(pet_list))
                return

        if self.items_data.item_dict[item_name_selected]['item_type'] == 'consumable':
            #数值已满 且物品为正向效果
            if (settings.pet_data.hp == (settings.HP_TIERS[-1]*settings.HP_INTERVAL) and self.items_data.item_dict[item_name_selected]['effect_HP'] >= 0):
                if self.items_data.item_dict[item_name_selected]['effect_FV'] == 0:
                    return
                elif ((settings.pet_data.fv_lvl == (len(settings.LVL_BAR)-1)) and (settings.pet_data.fv==settings.LVL_BAR[settings.pet_data.fv_lvl]) and self.items_data.item_dict[item_name_selected]['effect_FV'] > 0):
                    return


            # 使用物品所消耗的数值不足 （当有负向效果时）
            if (settings.pet_data.hp + self.items_data.item_dict[item_name_selected]['effect_HP']) < 0: # or\
                #(settings.pet_data.em + self.items_data.item_dict[item_name_selected]['effect_FV']) < 0:
                return

            #elif self.items_data.item_dict[item_name_selected]['item_type'] == 'consumable': #成功使用物品
            self.items_numb[self.selected_cell] -= 1

            # change pet_data
            settings.pet_data.change_item(item_name_selected, item_change=-1)

            # signal to item label
            self.cells_dict[self.selected_cell].unselected()
            self.cells_dict[self.selected_cell].consumeItem()

            # signal to act feed animation
            self.use_item_inven.emit(item_name_selected)
            self.item_note.emit(item_name_selected, '[%s] -1'%item_name_selected)

            # change button
            self.selected_cell = None
            self.changeButton()

        elif self.items_data.item_dict[item_name_selected]['item_type'] == 'collection':
            #print('collection used')
            self.cells_dict[self.selected_cell].unselected()
            self.cells_dict[self.selected_cell].consumeItem()
            if self.cells_dict[self.selected_cell].clct_inuse:
                self.use_item_inven.emit(item_name_selected)
            else:
                #print('收回')
                self.use_item_inven.emit(item_name_selected)
            self.selected_cell = None
            self.changeButton()

        elif self.items_data.item_dict[item_name_selected]['item_type'] == 'dialogue':
            #print('collection used')
            self.cells_dict[self.selected_cell].unselected()
            #self.cells_dict[self.selected_cell].consumeItem()
            self.use_item_inven.emit(item_name_selected)
            self.selected_cell = None
            self.changeButton()

        return

    def add_items(self, n_items, item_names=[]):
        # 没有可掉落物品 返回
        if sum(self.all_probs) <= 0:
            return

        # 随机物品
        item_names_pendding = []
        for i in range(n_items):
            item = random.choices(self.all_items, weights=self.all_probs, k=1)[0]
            if self.items_data.item_dict[item]['item_type'] == 'collection':
                self.add_item(item, 1)
                self.calculate_droprate()
            else:
                item_names_pendding.append(item)

        #print(n_items, item_names)
        # 物品添加列表
        items_toadd = {}
        for i in range(len(item_names_pendding)):
            item_name = item_names_pendding[int(i%len(item_names_pendding))]
            if item_name in items_toadd.keys():
                items_toadd[item_name] += 1
            else:
                items_toadd[item_name] = 1

        # 依次添加物品
        for item in items_toadd.keys():
            #while self.items_data.item_dict[item]['item_type'] == 'collection' and 
            self.add_item(item, items_toadd[item])


    def add_item(self, item_name, n_items):
        item_exist = False
        item_type = self.items_data.item_dict[item_name]['item_type']
        tab_index = self.tab_dict[item_type]

        for i in self.cells_dict.keys():
            if i[0] == tab_index:
                if self.cells_dict[i].item_name == item_name:
                    item_index = i
                    item_exist = True
                    break
                else:
                    continue
            else:
                continue

        if item_exist:
            self.items_numb[item_index] += n_items
            # signal to item label
            self.cells_dict[item_index].addItem(n_items)

        elif self.empty_cell[tab_index]:
            item_index = (tab_index, self.empty_cell[tab_index][0])
            self.empty_cell[tab_index] = self.empty_cell[tab_index][1:]
            self.cells_dict[item_index].registItem(self.items_data.item_dict[item_name], n_items)

        else:
            item_index = len([i for i in self.cells_dict.keys() if i[0]==tab_index])

            n_row = item_index // self.inven_shape[1]
            n_col = (item_index - (n_row-1)*self.inven_shape[1]) % self.inven_shape[1]

            item_index = (tab_index, item_index)

            self.items_numb[item_index] = int(n_items)
            self.cells_dict[item_index] = Inventory_item(item_index, self.items_data.item_dict[item_name], n_items)
            self.cells_dict[item_index].Ii_selected.connect(self.change_selected)
            self.cells_dict[item_index].Ii_removed.connect(self.item_removed)

            self.layer_dict[item_type].addWidget(self.cells_dict[item_index], n_row, n_col)

        self.item_note.emit(item_name, '[%s] +%s'%(item_name, n_items))
        self.item_anim.emit(item_name)
        # change pet_data
        settings.pet_data.change_item(item_name, item_change=n_items)

    def fvchange(self, fv_lvl):

        if fv_lvl in self.items_data.reward_dict:
            for item_i in self.items_data.reward_dict[fv_lvl]:
                if settings.petname in self.items_data.item_dict[item_i]['pet_limit'] \
                   or self.items_data.item_dict[item_i]['pet_limit']==[]:
                    self.add_item(item_i, 1)

        self.calculate_droprate()

    def calculate_droprate(self):

        all_items = []
        all_probs = []
        #确定物品掉落概率
        for item in self.items_data.item_dict.keys():
            all_items.append(item)
            #排除已经获得的收藏品
            if self.items_data.item_dict[item]['item_type'] != 'consumable' and settings.pet_data.items.get(item, 0)>0:
                all_probs.append(0)
            else:
                all_probs.append((self.items_data.item_dict[item]['drop_rate'])*int(self.items_data.item_dict[item]['fv_lock']<=settings.pet_data.fv_lvl))
        
        if sum(all_probs) != 0:
            all_probs = [i/sum(all_probs) for i in all_probs]

        self.all_items = all_items
        self.all_probs = all_probs

    def compensate_rewards(self):
        for fv_lvl in range(settings.pet_data.fv_lvl+1):
            for item_i in self.items_data.reward_dict.get(fv_lvl, []):

                if self.items_data.item_dict[item_i]['item_type'] != 'consumable'\
                   and settings.pet_data.items.get(item_i, 0)<=0:

                   if settings.petname in self.items_data.item_dict[item_i]['pet_limit'] \
                      or self.items_data.item_dict[item_i]['pet_limit']==[]:
                      
                        self.add_item(item_i, 1)

        self.calculate_droprate()







##############################
#           通知栏
##############################
NoteClose = """
QPushButton {
    background-color: palette(window);
    padding: 0px;
    border-style: solid;
    border-width: 2px;
    border-radius: 10px;
    border-color: transparent;
    text-align:middle;
}

QPushButton:hover:!pressed {
    background-color: #ffb19e;
}
QPushButton:pressed {
    background-color: #ffa48f;
}
QPushButton:disabled {
    background-color: #e0e1e0;
}
"""

class QToaster(QFrame):
    closed_note = Signal(str, str, name='closed_note')

    def __init__(self, note_index,
                 message='', #parent
                 icon=QStyle.SP_MessageBoxInformation,
                 corner=Qt.BottomRightCorner,
                 height_margin=10,
                 closable=True,
                 timeout=5000,
                 parent=None):
        super(QToaster, self).__init__(parent)

        #def __init__(self, *args, **kwargs):
        #    super(QToaster, self).__init__(*args, **kwargs)
        self.note_index = note_index
        #QHBoxLayout(self)

        self.setSizePolicy(QSizePolicy.Maximum, 
                           QSizePolicy.Maximum)
        
        #self.setStyleSheet(f'''
        #    QToaster {{
        #        border: {int(max(1, int(1*size_factor)))}px solid black;
        #        border-radius: {int(4*size_factor)}px; 
        #        background: palette(window);
        #    }}
        #''')
        
        # alternatively:
        # self.setAutoFillBackground(True)
        # self.setFrameShape(self.Box)

        self.timer = QTimer(singleShot=True, timeout=self.hide)

        '''
        if self.parent():
            self.opacityEffect = QtWidgets.QGraphicsOpacityEffect(opacity=0)
            self.setGraphicsEffect(self.opacityEffect)
            self.opacityAni = QtCore.QPropertyAnimation(self.opacityEffect, b'opacity')
            # we have a parent, install an eventFilter so that when it's resized
            # the notification will be correctly moved to the right corner
            self.parent().installEventFilter(self)
        else:
            # there's no parent, use the window opacity property, assuming that
            # the window manager supports it; if it doesn't, this won'd do
            # anything (besides making the hiding a bit longer by half a second)
        '''
        self.opacityAni = QPropertyAnimation(self, b'windowOpacity')
        self.opacityAni.setStartValue(0.)
        self.opacityAni.setEndValue(1.)
        self.opacityAni.setDuration(100)
        self.opacityAni.finished.connect(self.checkClosed)

        #self.corner = Qt.TopLeftCorner
        self.margin = int(10) #*size_factor)

        self.close_type = 'faded'

        self.setupMessage(message, icon, corner, height_margin, closable, timeout)

    def _closeit(self, close_type='button'):
        if not close_type:
            close_type = 'button'
        self.close_type = close_type
        #self.closed_note.emit(self.note_index)
        self.close()

    def checkClosed(self):
        # if we have been fading out, we're closing the notification
        if self.opacityAni.direction() == QAbstractAnimation.Backward: #self.opacityAni.Backward:
            self._closeit('faded')

    def restore(self):
        # this is a "helper function", that can be called from mouseEnterEvent
        # and when the parent widget is resized. We will not close the
        # notification if the mouse is in or the parent is resized
        self.timer.stop()
        # also, stop the animation if it's fading out...
        self.opacityAni.stop()
        # ...and restore the opacity
        '''
        if self.parent():
            self.opacityEffect.setOpacity(1)
        else:
        '''
        self.setWindowOpacity(1)

    def hide(self):
        # start hiding
        self.opacityAni.setDirection(QAbstractAnimation.Backward)
        self.opacityAni.setDuration(500)
        self.opacityAni.start()

    '''
    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Resize:
            self.opacityAni.stop()
            parentRect = self.parent().rect()
            geo = self.geometry()
            if self.corner == QtCore.Qt.TopLeftCorner:
                geo.moveTopLeft(
                    parentRect.topLeft() + QtCore.QPoint(self.margin, self.margin))
            elif self.corner == QtCore.Qt.TopRightCorner:
                geo.moveTopRight(
                    parentRect.topRight() + QtCore.QPoint(-self.margin, self.margin))
            elif self.corner == QtCore.Qt.BottomRightCorner:
                geo.moveBottomRight(
                    parentRect.bottomRight() + QtCore.QPoint(-self.margin, -self.margin))
            else:
                geo.moveBottomLeft(
                    parentRect.bottomLeft() + QtCore.QPoint(self.margin, -self.margin))
            self.setGeometry(geo)
            self.restore()
            self.timer.start()
        return super(QToaster, self).eventFilter(source, event)
    '''

    def enterEvent(self, event):
        self.restore()

    def leaveEvent(self, event):
        self.timer.start()

    def closeEvent(self, event):
        # we don't need the notification anymore, delete it!
        self.closed_note.emit(self.note_index, self.close_type)
        self.deleteLater()

    '''
    def resizeEvent(self, event):
        super(QToaster, self).resizeEvent(event)
        # if you don't set a stylesheet, you don't need any of the following!
        if not self.parent():
            # there's no parent, so we need to update the mask
            path = QtGui.QPainterPath()
            path.addRoundedRect(QtCore.QRectF(self.rect()).translated(-.5, -.5), 4, 4)
            self.setMask(QtGui.QRegion(path.toFillPolygon(QtGui.QTransform()).toPolygon()))
        else:
            self.clearMask()
    '''

    #@staticmethod
    def setupMessage(self,
                    message='', #parent
                    icon=QStyle.SP_MessageBoxInformation, 
                    corner=Qt.BottomRightCorner,
                    height_margin=10,
                    closable=True, 
                    timeout=5000): #, desktop=False, parentWindow=True):

        

        #if not parent or desktop:
        #self = QToaster(None)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        if platform == 'win32':
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
            Qt.BypassWindowManagerHint | Qt.SubWindow | Qt.NoDropShadowWindowHint)
        else:
            # SubWindow not work in MacOS
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
            Qt.BypassWindowManagerHint | Qt.NoDropShadowWindowHint)
        
        # This is a dirty hack!
        # parentless objects are garbage collected, so the widget will be
        # deleted as soon as the function that calls it returns, but if an
        # object is referenced to *any* other object it will not, at least
        # for PyQt (I didn't test it to a deeper level)
        #self.__self = self

        currentScreen = QApplication.primaryScreen()
        '''
            if parent and parent.window().geometry().size().isValid():
                # the notification is to be shown on the desktop, but there is a
                # parent that is (theoretically) visible and mapped, we'll try to
                # use its geometry as a reference to guess which desktop shows
                # most of its area; if the parent is not a top level window, use
                # that as a reference
                reference = parent.window().geometry()
            else:
        '''
        # the parent has not been mapped yet, let's use the cursor as a
        # reference for the screen
        reference = QRect(QCursor.pos() - QPoint(1, 1), 
                          QSize(3, 3))
        maxArea = 0
        for screen in QApplication.screens():
            intersected = screen.geometry().intersected(reference)
            area = intersected.width() * intersected.height()
            if area > maxArea:
                maxArea = area
                currentScreen = screen
        parentRect = currentScreen.availableGeometry()
        '''
        else:
            self = QToaster(parent)
            parentRect = parent.rect()
        '''

        self.timer.setInterval(timeout)

        # use Qt standard icon pixmaps; see:
        # https://doc.qt.io/qt-5/qstyle.html#StandardPixmap-enum
        #if isinstance(icon, QStyle.StandardPixmap):
        labelIcon = QLabel()
        #size = self.style().pixelMetric(QStyle.PM_SmallIconSize)
        labelIcon.setFixedSize(int(24), int(24))
        #labelIcon.setFixedSize(int(24*size_factor), int(24*size_factor))
        labelIcon.setScaledContents(True)
        labelIcon.setPixmap(icon) #QPixmap.fromImage(icon)) #.scaled(24,24)))

        frame = QFrame()
        frame.setStyleSheet('''
            QFrame {
                border: 1px solid black;
                border-radius: 4px; 
                background: palette(window);
            }
            QLabel{
                border: 0px
            }
        ''')
        hbox = QHBoxLayout()
        #hbox.setContentsMargins(10*size_factor,10*size_factor,10*size_factor,10*size_factor)
        hbox.setContentsMargins(10,10,10,10)
        hbox.setSpacing(0)

        #self.layout()
        hbox1 = QHBoxLayout()
        hbox1.setContentsMargins(0,0,10,0)
        hbox1.addWidget(labelIcon)
        hbox.addLayout(hbox1)
        #icon = self.style().standardIcon(icon)
        #labelIcon.setPixmap(icon.pixmap(size))

        self.label = QLabel(message)
        font = QFont(self.tr('Segoe UI'))
        #print(settings.font_factor)
        font.setPointSize(10)
        self.label.setFont(font) #QFont('黑体', int(10/screen_scale)))
        self.label.setWordWrap(True)
        #self.layout()
        hbox2 = QHBoxLayout()
        hbox2.setContentsMargins(0,0,5,0)
        hbox2.addWidget(self.label, Qt.AlignLeft)
        hbox.addLayout(hbox2)
        #hbox.addWidget(self.label, Qt.AlignLeft) # | Qt.AlignVCenter)

        if closable:
            self.closeButton = TransparentToolButton(FIF.CLOSE)
            self.closeButton.clicked.connect(self._closeit)
            #self.closeButton.setFixedSize(int(20*size_factor), int(20*size_factor))
            #self.closeButton.setIconSize(QSize(int(12*size_factor), int(12*size_factor)))
            self.closeButton.setFixedSize(int(20), int(20))
            self.closeButton.setIconSize(QSize(int(12), int(12)))
            '''
            self.closeButton = QPushButton()
            self.closeButton.setStyleSheet(NoteClose)
            self.closeButton.setFixedSize(int(20*size_factor), int(20*size_factor))
            self.closeButton.setIcon(QIcon(os.path.join(basedir,'res/icons/close_icon.png')))
            self.closeButton.setIconSize(QSize(int(20*size_factor), int(20*size_factor)))
            self.closeButton.clicked.connect(self._closeit)
            '''
            hbox.addWidget(self.closeButton)

            '''
            self.closeButton = QToolButton()
            #self.layout().
            hbox.addWidget(self.closeButton)
            closeIcon = self.style().standardIcon(QStyle.SP_TitleBarCloseButton)
            self.closeButton.setIcon(closeIcon)
            iw = int(self.closeButton.iconSize().width() * size_factor)
            self.closeButton.setIconSize(QSize(iw,iw))
            self.closeButton.setAutoRaise(True)
            self.closeButton.clicked.connect(self._closeit)
            '''

        frame.setLayout(hbox)
        wholebox = QHBoxLayout()
        wholebox.setContentsMargins(0,0,0,0)
        wholebox.addWidget(frame)
        self.setLayout(wholebox)

        self.timer.start()

        # raise the widget and adjust its size to the minimum
        self.raise_()
        self.setFixedWidth(int(200)) #*size_factor))
        self.adjustSize()
        self.setFixedHeight(self.height()*1.3)


        #self.corner = corner
        self.height_margin = int(height_margin) #*size_factor)

        geo = self.geometry()
        # now the widget should have the correct size hints, let's move it to the
        # right place
        if corner == Qt.TopLeftCorner:
            geo.moveTopLeft(
                parentRect.topLeft() + QPoint(self.margin, self.margin+self.height_margin))
        elif corner == Qt.TopRightCorner:
            geo.moveTopRight(
                parentRect.topRight() + QPoint(-self.margin, self.margin+self.height_margin))
        elif corner == Qt.BottomRightCorner:
            geo.moveBottomRight(
                parentRect.bottomRight() + QPoint(-self.margin, -(self.margin+self.height_margin)))
        else:
            geo.moveBottomLeft(
                parentRect.bottomLeft() + QPoint(self.margin, -(self.margin+self.height_margin)))

        self.setGeometry(geo)
        self.show()
        self.opacityAni.start()
        #return self.height()





###################
#  对话框
###################
OptionbuttonStyle = """
QPushButton {
    background-color: #ffbdad;
    color: #000000;
    border-style: solid;
    padding: 7px;
    font: 16px;
    font-family: "黑体";
    text-align: left;
    border-width: 3px;
    border-radius: 10px;
    border-color: #B39C86;
}
QPushButton:hover:!pressed {
    background-color: #ffb19e;
}
QPushButton:pressed {
    background-color: #ffa48f;
}
QPushButton:disabled {
    background-color: #e0e1e0;
}
"""


DialogueClose = """
QPushButton {
    background-color: #ffbdad;
    padding: 0px;
    border-style: solid;
    border-width: 2px;
    border-radius: 10px;
    border-color: transparent;
    text-align:middle;
}

QPushButton:hover:!pressed {
    background-color: #ffb19e;
}
QPushButton:pressed {
    background-color: #ffa48f;
}
QPushButton:disabled {
    background-color: #e0e1e0;
}
"""

DialogueTitle = """
QLabel {
    border: 0;
    background-color: #F5F4EF;
    font-size: 15px;
    font-family: "黑体";
    width: 10px;
    height: 20px
}
"""
OptionGroupStyle = """
QGroupBox {
    border: 1px solid transparent;
    background-color: #F5F4EF;
    border-radius: 10px
}
"""

DialogueClose = """
QPushButton {
    background-color: #ffbdad;
    padding: 0px;
    border-style: solid;
    border-width: 2px;
    border-radius: 10px;
    border-color: transparent;
    text-align:middle;
}

QPushButton:hover:!pressed {
    background-color: #ffb19e;
}
QPushButton:pressed {
    background-color: #ffa48f;
}
QPushButton:disabled {
    background-color: #e0e1e0;
}
"""

DialogueStyle = """
QLabel {
    font-size: 16px;
    font-family: "黑体";
    border: 0px
}

QFrame{
    background:#F5F4EF;
    border: 3px solid #F5F4EF;
    border-radius: 10px
}

QScrollArea {
    padding: 2px;
    border: 3px solid #F5F4EF;
    background-color: #F5F4EF;
    border-radius: 10px
}

QScrollBar:vertical
{
    background-color: #F5F4EF;
    width: 15px;
    margin: 5px 1px 5px 1px;
    border: 1px #F5F4EF;
    border-radius: 6px;
}

QScrollBar::handle:vertical
{
    width: 15px;
    background-color: #FFC8BB;         /* #f184ae; */
    min-height: 5px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical {
height: 0px;
}

QScrollBar::sub-line:vertical {
height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
height: 0px;
}

"""

OptionScrollStyle = """
QScrollArea {
    padding: 2px;
    border: 3px solid #9f7a6a;
    background-color: #F5F4EF;
    border-radius: 10px
}

QScrollBar:vertical
{
    background-color: #F5F4EF;
    width: 15px;
    margin: 5px 1px 5px 1px;
    border: 1px #F5F4EF;
    border-radius: 6px;
}

QScrollBar::handle:vertical
{
    width: 15px;
    background-color: #FFC8BB;         /* #f184ae; */
    min-height: 5px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical {
height: 0px;
}

QScrollBar::sub-line:vertical {
height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
height: 0px;
}
"""


class DPDialogue(QWidget):
    closed_acc = Signal(str, name='closed_acc')

    def __init__(self, acc_index,
                 message={},
                 pos_x=0,
                 pos_y=0,
                 closable=True,
                 timeout=5000,
                 parent=None):
        super(DPDialogue, self).__init__(parent)

        self.is_follow_mouse = False

        self.acc_index = acc_index
        self.message = message

        self.setSizePolicy(QSizePolicy.Minimum, 
                           QSizePolicy.Minimum)

        '''
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
            Qt.BypassWindowManagerHint | Qt.SubWindow | Qt.NoDropShadowWindowHint)
        '''


        # 界面设计
        frame = QFrame()
        frame.setStyleSheet(f'''
            QFrame {{
                border: 1px solid black;
                border-radius: 4px; 
                background: palette(window);
            }}
            QLabel{{
                border: 0px
            }}
        ''')

        # 标题栏
        hbox_0 = QHBoxLayout()
        self.title = QLabel(message.get('title',''))
        self.title.setStyleSheet(DialogueTitle)
        icon = QLabel()
        image = QImage()
        image.load(os.path.join(basedir,'res/icons/Dialogue_icon.png'))
        icon.setScaledContents(True)
        icon.setPixmap(QPixmap.fromImage(image)) #.scaled(20,20)))
        icon.setFixedSize(int(25), int(25))
        #icon.setFixedSize(int(25*size_factor), int(25*size_factor))
        hbox_0.addWidget(icon, Qt.AlignBottom | Qt.AlignLeft)
        hbox_0.addWidget(self.title, Qt.AlignVCenter | Qt.AlignLeft)
        hbox_0.addStretch(1)
        self.button_close = QPushButton()
        self.button_close.setStyleSheet(DialogueClose)
        #self.button_close.setFixedSize(int(20*size_factor), int(20*size_factor))
        self.button_close.setFixedSize(int(20), int(20))
        self.button_close.setIcon(QIcon(os.path.join(basedir,'res/icons/close_icon.png')))
        self.button_close.setIconSize(QSize(int(20), int(20)))
        #self.button_close.setIconSize(QSize(int(20*size_factor), int(20*size_factor)))
        self.button_close.clicked.connect(self._closeit)
        hbox_0.addWidget(self.button_close, Qt.AlignTop | Qt.AlignRight)

        # 对话文本
        hbox_1 = QHBoxLayout()
        hbox_1.setContentsMargins(5,5,5,5)
        self.text_now = message['start']
        self.label = QLabel(message[message['start']])
        #self.label.setFixedWidth(int(250*size_factor))
        #self.label.setMinimumSize(int(250*size_factor),int(20*size_factor))
        self.label.setFixedWidth(int(250))
        self.label.setMinimumSize(int(250),int(20))
        font = QFont(self.tr('Segoe UI'))
        #print(settings.font_factor)
        font.setPointSize(10)
        self.label.setFont(font) #QFont('黑体', int(10/screen_scale)))
        self.label.setWordWrap(True)
        #self.layout()

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidget(self.label)
        self.scrollArea.setMinimumHeight(int(100)) #*size_factor))
        hbox_1.addWidget(self.scrollArea, Qt.AlignHCenter | Qt.AlignTop)


        # 选项
        self.n_col = 1
        self.OptionGroupBox = QGroupBox()
        self.OptionGroupBox.setStyleSheet(OptionGroupStyle)
        self.OptionLayout = QGridLayout()
        self.OptionLayout.setVerticalSpacing(9)
        self.OptionGenerator(message['start'])

        # Layout
        self.windowLayout = QVBoxLayout()
        self.windowLayout.addLayout(hbox_0, Qt.AlignHCenter | Qt.AlignTop)
        self.windowLayout.addLayout(hbox_1, Qt.AlignHCenter | Qt.AlignTop)
        if self.opts_dict != {}:
            #self.windowLayout.addWidget(QHLine())
            self.scrollArea2 = QScrollArea(self)
            self.scrollArea2.setFrameShape(QFrame.NoFrame)
            self.scrollArea2.setWidgetResizable(True)
            self.scrollArea2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.scrollArea2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scrollArea2.setWidget(self.OptionGroupBox)
            self.scrollArea2.setMinimumHeight(int(200)) #*size_factor))
            self.scrollArea2.setMinimumHeight(int(200)) #*size_factor))
            self.scrollArea2.setStyleSheet(OptionScrollStyle)
            #hbox_1.addWidget(self.scrollArea, Qt.AlignHCenter | Qt.AlignTop)
            self.windowLayout.addWidget(self.scrollArea2) #ItemGroupBox)

        self.centralwidget = QFrame()
        self.centralwidget.setLayout(self.windowLayout)
        self.centralwidget.setStyleSheet(DialogueStyle)
        self.layout_window = QVBoxLayout()
        self.layout_window.addWidget(self.centralwidget, Qt.AlignHCenter | Qt.AlignTop)
        self.setLayout(self.layout_window)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        if settings.platform == 'win32':
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)

        self.setFixedWidth(int(350)) #*size_factor))
        #self.adjustSize()
        #self.setFixedHeight(self.height()*1.1)

        self.move(pos_x-self.width()//2, pos_y-self.height())
        self.show()

    def mousePressEvent(self, event):
        """
        鼠标点击事件
        :param event: 事件
        :return:
        """
        if event.button() == Qt.LeftButton:
            # 左键绑定拖拽
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件, 左键且绑定跟随, 移动窗体
        :param event:
        :return:
        """
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        松开鼠标操作
        :param event:
        :return:
        """
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def _closeit(self):
        self.close()

    def closeEvent(self, event):
        # we don't need the notification anymore, delete it!
        self.closed_acc.emit(self.acc_index)
        self.deleteLater()

    def ontop_update(self):
        if settings.on_top_hint:
            #self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow | Qt.NoDropShadowWindowHint)
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)

        else:
            #self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow | Qt.NoDropShadowWindowHint)
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)

        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()

    def OptionGenerator(self, text_key=None, prev_text=None, reverse=False):
        for item in [self.OptionLayout.itemAt(i) for i in range(self.OptionLayout.count())]:
            #item.deleteLater()
            widget = item.widget()
            widget.deleteLater()
        
        self.opts_dict = {}
        option_index = 0

        # 添加上一步
        if prev_text is not None and not reverse:
            if text_key is not None:
                self.message['relationship']['option_prev_%s'%text_key] = [prev_text]
                if 'option_prev_%s'%text_key not in self.message['relationship'].get(text_key, []):
                    self.message['option_prev_%s'%text_key] = self.tr('Back')
                    self.message['relationship'][text_key] = self.message['relationship'].get(text_key, []) + ['option_prev_%s'%text_key]
            else:
                self.message['relationship']['option_prev_end'] = [prev_text]
                n_row = option_index // self.n_col
                n_col = (option_index - (n_row-1)*self.n_col) % self.n_col

                self.opts_dict[option_index] = DialogueButtom(self.tr('Back'), 'option_prev_end') ##################
                self.opts_dict[option_index].clicked.connect(self.confirm)
                self.OptionLayout.addWidget(self.opts_dict[option_index], n_row, n_col)
                option_index += 1


        if text_key is not None:
            for option in self.message.get('relationship', {}).get(text_key, []):
                n_row = option_index // self.n_col
                n_col = (option_index - (n_row-1)*self.n_col) % self.n_col

                self.opts_dict[option_index] = DialogueButtom(self.message[option], option) ##################
                self.opts_dict[option_index].clicked.connect(self.confirm)

                self.OptionLayout.addWidget(self.opts_dict[option_index], n_row, n_col)
                option_index += 1


        self.OptionGroupBox.setLayout(self.OptionLayout)

        if option_index == 0:
            pass
            '''
            try:
                item = self.windowLayout.itemAt(self.windowLayout.count()-1)
                widget = item.widget()
                widget.deleteLater()
            except:
                pass
            '''


    def confirm(self):
        opt_key = self.sender().msg_key
        new_key = self.message['relationship'].get(opt_key,[])
        if new_key == []:
            self.label.setText('')
            self.OptionGenerator(prev_text=self.text_now, reverse=self.sender().msg==self.tr('Back'))
            self.text_now = ''
        else:
            new_key = new_key[0]
            self.label.setText(self.message[new_key])
            self.OptionGenerator(new_key, self.text_now, reverse=self.sender().msg==self.tr('Back'))
            self.text_now = new_key

        self.adjustSize()
        

class DialogueButtom(QPushButton):
    def __init__(self, msg, msg_key):

        super(DialogueButtom, self).__init__()
        self.msg = msg
        self.msg_key = msg_key
        #n_sp_symbol = math.ceil((msg.count('，') + msg.count('。') + msg.count('（') + msg.count('）')) / math.ceil(len(msg)/15))
        #print(n_sp_symbol)
        self.setText(text_wrap(msg,15)) #-n_sp_symbol))

        self.setStyleSheet(OptionbuttonStyle)
        #self.adjustSize()
        self.setFixedWidth(int(250)) #*settings.size_factor))
        self.adjustSize()

'''
def text_wrap(texts, width):
    text_list = tr.wrap(texts, width=width)
    texts_wrapped = '\n'.join(text_list)

    return texts_wrapped
'''


