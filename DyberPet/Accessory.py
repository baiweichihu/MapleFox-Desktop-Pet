import sys
from sys import platform
import time
import math
import uuid
import types
import random
import inspect
from typing import List
import pynput.mouse as mouse
from datetime import datetime, timedelta


from apscheduler.schedulers.qt import QtScheduler
from apscheduler.triggers import interval, date, cron

from PySide6.QtCore import Qt, QTimer, QObject, QPoint, QUrl, QEvent, QRectF, QRect, QSize
from PySide6.QtGui import QImage, QPixmap, QIcon, QCursor,QPainter
from PySide6.QtGui import QFont, QTransform, QAction

from PySide6.QtWidgets import *
from PySide6.QtCore import QObject, QThread, Signal
#from PySide6.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent

from qfluentwidgets import RoundMenu, Action
from qfluentwidgets import FluentIcon as FIF

from DyberPet.utils import *
from DyberPet.conf import *
#from DyberPet.extra_windows import DPDialogue
from DyberPet.custom_widgets import DPDialogue, MenuSlider
import DyberPet.settings as settings
'''
try:
    size_factor = 1 #ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
except:
    size_factor = 1
'''


if platform == 'win32':
    #basedir = ''
    flags = Qt.FramelessWindowHint | Qt.SubWindow | Qt.NoDropShadowWindowHint
else:
    #basedir = os.path.dirname(__file__) #Path(os.path.dirname(__file__))
    #basedir = basedir.replace('\\','/')
    #basedir = '/'.join(basedir.split('/')[:-1])
    flags = Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint

basedir = settings.BASEDIR

##############################
#          组件模块
##############################

class DPAccessory(QWidget):
    send_main_movement = Signal(int, int, name="send_main_movement")
    ontop_changed = Signal(name='ontop_changed')
    reset_size_sig = Signal(name='reset_size_sig')
    acc_withdrawed = Signal(str, name='acc_withdrawed')

    def __init__(self, parent=None):
        """
        宠物组件
        """
        super(DPAccessory, self).__init__(parent) #, flags=Qt.WindowFlags())

        self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        self.acc_dict = {}
        self.heart_list = []
        self.bubble_frame = _load_item_img(os.path.join(basedir, 'res/role/sys/action/bubble.png'))
        self.follow_main_list = []

    def setup_accessory(self, acc_act, pos_x, pos_y):

        #if acc_act.get('name','') == 'compdays':
        #    self.setup_compdays(acc_act, pos_x, pos_y)
        #    return

        acc_index = str(uuid.uuid4())

        if acc_act.get('name','') == 'item_drop':
            acc_act['frame'] = self.bubble_frame
            self.acc_dict[acc_index] = QItemDrop(acc_index, acc_act,
                                                 pos_x, pos_y)

            #self.acc_dict[acc_index].closed_acc.connect(self.remove_accessory)

        elif acc_act.get('name','') == 'dialogue':
            # 对话框不可重复打开
            for qacc in self.acc_dict:
                try:
                    msg_title = self.acc_dict[qacc].message['title']
                except:
                    continue
                if msg_title == acc_act['msg_dict']['title']:
                    return

            self.acc_dict[acc_index] = DPDialogue(acc_index, acc_act['msg_dict'],
                                                  pos_x, pos_y)

        else:

            if acc_act.get('name','') == 'heart':
                if len(self.heart_list) < 5:
                    self.heart_list.append(acc_index)
                    pos_y -= acc_act['acc_list'][0].images[0].height()
                else:
                    return
            # 具有唯一性的物品，在场的情况下使用将收回
            if acc_act.get('unique', False):
                for qacc in self.acc_dict:
                    try:
                        cur_name = self.acc_dict[qacc].acc_act['name']
                    except:
                        continue
                    if cur_name == acc_act['name']:
                        self.acc_dict[qacc]._closeit()
                        return

            self.acc_dict[acc_index] = QAccessory(acc_index,
                                                  acc_act,
                                                  pos_x, pos_y
                                                  )

            if acc_act.get('follow_main', False):
                self.send_main_movement.connect(self.acc_dict[acc_index].update_main_pos)
            if acc_act.get('closable', False):
                self.acc_dict[acc_index].acc_withdrawed.connect(self.acc_withdrawed)

        self.acc_dict[acc_index].closed_acc.connect(self.remove_accessory)
        self.ontop_changed.connect(self.acc_dict[acc_index].ontop_update)

        ''' mouse decorator not implemented
        elif acc_act.get('name','') == 'mouseDecor':
            for qacc in self.acc_dict:
                if not isinstance(self.acc_dict[qacc], DPMouseDecor):
                    continue

                if self.acc_dict[qacc].decor_name == acc_act['config']['name']:
                    # 收回挂件
                    self.acc_dict[qacc]._closeit()
                    return
                else:
                    # 替换挂件
                    self.acc_withdrawed.emit(self.acc_dict[qacc].decor_name)
                    self.acc_dict[qacc]._closeit()
                    break
        

            # 激活挂件
            self.acc_dict[acc_index] = DPMouseDecor(acc_index, acc_act['config'])
            self.acc_dict[acc_index].acc_withdrawed.connect(self.acc_withdrawed)
        '''


    def remove_accessory(self, acc_index):
        self.acc_dict.pop(acc_index)
        try:
            self.heart_list.remove(acc_index)
        except:
            pass

    def closeAll(self):
        # close all accessory in situation when pet changed
        acc_idxs = list(self.acc_dict.keys())
        for idx in acc_idxs:
            self.acc_dict[idx]._closeit()


def _load_item_img(img_path):
    return _get_q_img(img_path)

def _get_q_img(img_file) -> QPixmap:

    #image = QImage()
    image = QPixmap()
    image.load(img_file)
    return image


HangLabelStyle = """
QLabel {
    background: rgba(255, 255, 255, 0);
    font-size: 16px;
    font-family: "黑体";
    border: 0px
}
"""
HangStyle = """
QFrame{
    background: rgba(255, 255, 255, 100);
    border: 3px solid #94b0c8;
    border-radius: 10px
}
"""

class QHangLabel(QWidget):
    closed_acc = Signal(str, name='closed_acc')

    def __init__(self, acc_index,
                 acc_act,
                 pos_x, pos_y,
                 parent=None):
        super(QHangLabel, self).__init__(parent)

        self.is_follow_mouse = False

        self.acc_index = acc_index
        self.message = acc_act['message']
        self.main_height = acc_act['height']

        self.setSizePolicy(QSizePolicy.Minimum, 
                           QSizePolicy.Minimum)

        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
            Qt.BypassWindowManagerHint | Qt.SubWindow | Qt.NoDropShadowWindowHint)

        # Text
        hbox_1 = QHBoxLayout()
        hbox_1.setContentsMargins(15,0,15,0)

        self.label = QLabel(self.message)
        self.label.setStyleSheet(HangLabelStyle)
        hbox_1.addWidget(self.label, Qt.AlignCenter)

        self.centralwidget = QFrame()
        self.centralwidget.setLayout(hbox_1)
        self.centralwidget.setStyleSheet(HangStyle)
        self.layout_window = QVBoxLayout()
        self.layout_window.addWidget(self.centralwidget, Qt.AlignCenter)
        self.setLayout(self.layout_window)

        self.adjustSize()

        self.move(pos_x-self.width()//2, pos_y-self.height())
        self.show()


    def _closeit(self):
        #self.closed_note.emit(self.note_index)
        self.close()

    def closeEvent(self, event):
        # we don't need the notification anymore, delete it!
        self.closed_acc.emit(self.acc_index)
        self.deleteLater()

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

    def ontop_update(self):
        if settings.on_top_hint:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()





class QAccessory(QWidget):
    closed_acc = Signal(str, name='closed_acc')
    acc_withdrawed = Signal(str, name='acc_withdrawed')

    def __init__(self, acc_index,
                 acc_act,
                 pos_x, pos_y,
                 parent=None):
        super(QAccessory, self).__init__(parent)

        self.acc_index = acc_index
        self.acc_act = acc_act
        #self.move(pos_x, pos_y)
        self.timeout = acc_act.get('timeout', True)
        self.closable = acc_act.get('closable', False)
        self.follow_main = acc_act.get('follow_main', False)
        self.delay_respond = 500 #ms
        self.delay_timer = 500 #ms
        self.speed_follow_main = acc_act.get('speed_follow_main', 5)
        self.at_destination = True
        self.move_right = False

        if settings.on_top_hint:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        #self.repaint()

        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.previous_img = None
        if isinstance(acc_act['acc_list'][0], list):
            self.current_img = None
        else:
            self.current_img = acc_act['acc_list'][0].images[0]
        
        self.anchor = acc_act['anchor']
        if not isinstance(self.anchor[0], list):
            self.anchor = [self.anchor] * len(acc_act['acc_list'])
        if acc_act.get('name','') == 'heart':
            self.previous_anchor = [int(i) for i in self.anchor[0]]
            self.current_anchor = [int(i) for i in self.anchor[0]]
        else:
            self.previous_anchor = [int(i * settings.tunable_scale) for i in self.anchor[0]]
            self.current_anchor = [int(i * settings.tunable_scale) for i in self.anchor[0]]
        self.set_img()

        self.current_act = None
        self.previous_act = None
        self.playid = 0
        self.act_id = 0
        self.finished = False
        #self.waitn = 0
        

        # 是否跟随鼠标
        self.is_follow_mouse = acc_act.get('follow_mouse', False)
        if self.is_follow_mouse:
            self.manager = MouseMoveManager()
            self.manager.moved.connect(self._move_to_mouse)
            #print('check')
            #self.setMouseTracking(True)
            #self.installEventFilter(self)
        #else:
        #self.move(pos_x+self.current_anchor[0]*settings.tunable_scale, pos_y+self.current_anchor[1]*settings.tunable_scale)
        self.move(pos_x+self.current_anchor[0], pos_y+self.current_anchor[1])

        #print(self.is_follow_mouse)
        self.mouse_drag_pos = self.pos()

        #self.destination = [pos_x+self.current_anchor[0]*settings.tunable_scale, pos_y+self.current_anchor[1]*settings.tunable_scale]
        self.destination = [pos_x+self.current_anchor[0], pos_y+self.current_anchor[1]]

        # 是否可关闭
        if self.closable:
            menu = RoundMenu(parent=self)
            self.quit_act = Action(FIF.CLOSE,
                                   self.tr('Withdraw'), menu)
            self.quit_act.triggered.connect(self._withdraw)
            menu.addAction(self.quit_act)
            self.menu = menu

        self.petlayout = QVBoxLayout()
        self.petlayout.addWidget(self.label)
        self.petlayout.setAlignment(Qt.AlignCenter)
        self.petlayout.setContentsMargins(0,0,0,0)

        self.setLayout(self.petlayout)
        self.show()

        # heart 专属:物理轨迹参数(随机方向斜抛 + 渐变消失)
        if acc_act.get('name', '') == 'heart':
            physics = acc_act.get('physics', {})
            self._phys_v_x_range = tuple(physics.get('v_x_range', [-4, 4]))
            self._phys_v_y_range = tuple(physics.get('v_y_range', [-10, -5]))
            self._phys_gravity = float(physics.get('gravity', 1.0))
            self._phys_lifetime_ms = int(physics.get('lifetime_ms', 1500))
            self._phys_fade_ratio = float(physics.get('fade_ratio', 0.4))
            self.v_x = random.uniform(*self._phys_v_x_range)
            self.v_y = random.uniform(*self._phys_v_y_range)
            self._phys_frame_count = 0
            self._phys_total_frames = max(1, int(self._phys_lifetime_ms / 20))
            self._phys_fade_start_frame = int(self._phys_total_frames * (1.0 - self._phys_fade_ratio))
        else:
            self._phys_total_frames = 0

        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.Action)
        #print(self.pet_conf.interact_speed)
        self.timer.start(20)
        # Due to Qt internal behavior, has to force the position back to assigned
        QTimer.singleShot(10, lambda: self.move(pos_x + self.current_anchor[0], pos_y + self.current_anchor[1]))

    def set_img(self):
        if self.previous_anchor != self.current_anchor:
            self.move(self.pos().x()-self.previous_anchor[0]+self.current_anchor[0],
                      self.pos().y()-self.previous_anchor[1]+self.current_anchor[1])
        
        if self.current_img:
            if self.acc_act.get('name','') == 'heart':
                width_tmp = self.current_img.width()
                height_tmp = self.current_img.height()
            else:
                width_tmp = self.current_img.width()*settings.tunable_scale
                height_tmp = self.current_img.height()*settings.tunable_scale
            # HighDPI-compatible scaling solution
            self.label.setFixedSize(width_tmp, height_tmp)
            self.label.setPixmap(self.current_img)
            if not self.isVisible():
                self.setVisible(True)
        else:
            self.setVisible(False)

    def _move_to_mouse(self,x,y):
        #print(self.label.width()//2)
        if self.is_follow_mouse == 'x':
            self.move(x-self.current_anchor[0], self.pos().y())
        elif self.is_follow_mouse == 'y':
            self.move(self.pos().x(), y-self.current_anchor[1])
        else:
            self.move(x-self.current_anchor[0],y-self.current_anchor[1])

    def _withdraw(self):
        self.acc_withdrawed.emit(self.acc_act['name'])
        self._closeit()

    def _closeit(self):
        #self.closed_note.emit(self.note_index)
        if self.is_follow_mouse:
            self.manager._listener.stop()

        self.close()

    def closeEvent(self, event):
        # we don't need the notification anymore, delete it!
        self.closed_acc.emit(self.acc_index)
        self.deleteLater()

    def ontop_update(self):
        if settings.on_top_hint:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()

    def mousePressEvent(self, event):
        """
        鼠标点击事件
        :param event: 事件
        :return:
        """
        if event.button() == Qt.RightButton and self.closable:
            # 打开右键菜单
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self._show_right_menu)

    def _show_right_menu(self):
        self.menu.popup(QCursor.pos()-QPoint(0, 75))

    def update_main_pos(self, pos_x, pos_y):
        if self.follow_main:
            x_new = pos_x+self.current_anchor[0] - self.pos().x()
            y_pos = pos_y+self.current_anchor[1] - self.pos().y()
            if self.speed_follow_main*5 <= ((x_new**2 + y_pos**2)**0.5):
                self.at_destination = False
                self.destination = [pos_x+self.current_anchor[0], pos_y+self.current_anchor[1]]
                #if self.delay_respond == self.delay_time:
                #self.move(pos_x-self.anchor[0]*settings.tunable_scale, pos_y-self.anchor[1]*settings.tunable_scale)

    def img_from_act(self, act):

        if self.current_act != act:
            self.previous_act = self.current_act
            self.current_act = act
            self.playid = 0
            
            if isinstance(act, list):
                n_repeat = math.ceil(act[0]/20) * act[1]
                self.img_list_expand = [None] * n_repeat
            else:
                fr_list = getattr(act, 'frame_refresh_list', None)
                if fr_list:
                    n_repeat_list = [max(1, math.ceil(fr / (20 / 1000))) for fr in fr_list]
                    self.img_list_expand = [item for item, rep in zip(act.images, n_repeat_list) for _ in range(rep)] * act.act_num
                else:
                    n_repeat = math.ceil(act.frame_refresh / (20 / 1000))
                    self.img_list_expand = [item for item in act.images for i in range(n_repeat)] * act.act_num

        img = self.img_list_expand[self.playid]

        if isinstance(act, list):
            n_repeat = math.ceil(act[0]/20) * act[1]
            self.playid += 1
            if self.playid >= n_repeat:
                self.playid = 0
        else:
            self.playid += 1
            if self.playid >= len(self.img_list_expand):
                self.playid = 0
            #img = act.images[0]
            self.previous_img = self.current_img
            self.current_img = img
            self.previous_anchor = self.current_anchor
            tunable_scale = 1 if self.acc_act.get('name','') == 'heart' else settings.tunable_scale
            self.current_anchor = [int(i * tunable_scale) for i in self.anchor[self.act_id]]

    def Action(self):

        if self.finished and self.timeout:
            self.timer.stop()
            self._closeit()
            return

        is_heart = (self.acc_act.get('name', '') == 'heart')

        acts = self.acc_act['acc_list']
        #print(settings.act_id, len(acts))
        if self.act_id >= len(acts):
            if self.timeout:
                if is_heart:
                    self.act_id = 0  # heart 帧动画循环播放,寿命由物理轨迹控制
                else:
                    self.finished = True
                    return
            else:
                self.act_id = 0

        #else:
        act = acts[self.act_id]
        if isinstance(act, list):
            n_repeat = math.ceil(act[0]/20) * act[1]
        else:
            fr_list = getattr(act, 'frame_refresh_list', None)
            if fr_list:
                n_repeat = sum(max(1, math.ceil(fr / (20 / 1000))) for fr in fr_list) * act.act_num
            else:
                n_repeat = math.ceil(act.frame_refresh / (20 / 1000))
                n_repeat *= len(act.images) * act.act_num
        self.img_from_act(act)
        if self.playid >= n_repeat-1:
            self.act_id += 1

        if self.move_right:
            self.previous_img = self.current_img
            transform = QTransform()
            transform.scale(-1, 1)
            self.current_img = self.current_img.transformed(transform)
            #self.current_img = self.current_img.mirrored(True, False)
        if self.previous_img != self.current_img or self.previous_anchor != self.current_anchor:
            self.set_img()
            if not is_heart:
                self._move(act)

        if self.follow_main and not self.at_destination:
            self.move_to_main()

        # heart 专属:物理轨迹(随机方向 + 重力斜抛 + 渐变消失)
        if is_heart:
            self._heart_physics_step()

    def _heart_physics_step(self):
        """heart 浮动爱心:随机初速 + 重力斜抛 + 渐变消失"""
        self._phys_frame_count += 1

        # 渐变消失(后 fade_ratio 阶段)
        if self._phys_frame_count >= self._phys_fade_start_frame:
            fade_frames = self._phys_total_frames - self._phys_fade_start_frame
            if fade_frames > 0:
                opacity = 1.0 - (self._phys_frame_count - self._phys_fade_start_frame) / fade_frames
                self.setWindowOpacity(max(0.0, opacity))

        # 物理运动
        self.v_y += self._phys_gravity
        self.move(self.pos().x() + self.v_x, self.pos().y() + self.v_y)

        # 寿命结束,下一帧关闭
        if self._phys_frame_count >= self._phys_total_frames:
            self.finished = True

    def _move(self, act: QAction) -> None: #pos: QPoint, act: QAction) -> None:
        """
        在 Thread 中发出移动Signal
        :param act: 动作
        :return
        """
        #print(act.direction, act.frame_move)
        plus_x = 0.
        plus_y = 0.
        direction = act.direction

        if direction is None:
            pass
        else:
            if direction == 'right':
                plus_x = act.frame_move

            if direction == 'left':
                plus_x = -act.frame_move

            if direction == 'up':
                plus_y = -act.frame_move

            if direction == 'down':
                plus_y = act.frame_move

        self.move(self.pos().x()+plus_x, self.pos().y()+plus_y)

    def move_to_main(self):

        # 延迟响应
        if self.delay_timer > 0:
            self.delay_timer += -20
            return

        movement_x = self.destination[0] - self.pos().x()
        movement_y = self.destination[1] - self.pos().y()
        if movement_y != 0:
            kb = abs(movement_x/movement_y)
            plus_x = int(self.speed_follow_main * kb / ((1+kb**2)**0.5) * (int(movement_x>0)*2-1))
            plus_y = int(self.speed_follow_main * 1  / ((1+kb**2)**0.5) * (int(movement_y>0)*2-1))
        else:
            plus_x = int(self.speed_follow_main * (int(movement_x>0)*2-1))
            plus_y = 0

        if plus_x > 0:
            self.move_right = True
        else:
            self.move_right = False

        if max(1,self.speed_follow_main*settings.tunable_scale) >= ((movement_x**2 + movement_y**2)**0.5):
            #plus_x = movement_x
            #plus_y = movement_y
            self.move_right = False
            self.at_destination = True
            self.delay_timer = self.delay_respond
            return

        self.move(self.pos().x()+plus_x, self.pos().y()+plus_y)





class MouseMoveManager(QObject):
    moved = Signal(int, int)
    clicked = Signal(bool)

    def __init__(self, movement=True, click=False, parent=None):
        super().__init__(parent)
        if movement and click:
            self._listener = mouse.Listener(on_move=self._handle_move,
                                            on_click=self._handle_click)
        elif movement:
            self._listener = mouse.Listener(on_move=self._handle_move)
        elif click:
            self._listener = mouse.Listener(on_click=self._handle_click)
        else:
            return

        self._listener.start()

    def _handle_move(self, x, y):
        #if not pressed:
        self.moved.emit(x, y)

    def _handle_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.clicked.emit(pressed)


class QItemLabel(QLabel):

    def __init__(self, frame):
        super(QItemLabel, self).__init__()
        self.frame = frame

    def paintEvent(self, event):
        super(QItemLabel, self).paintEvent(event)
        printer = QPainter(self)
        #printer.drawPixmap(QPoint(0,0), self.frame) #QPixmap.fromImage(self.frame))


class QItemDrop(QWidget):
    closed_acc = Signal(str, name='closed_acc')

    def __init__(self, acc_index,
                 acc_act,
                 pos_x, pos_y,
                 parent=None):
        super(QItemDrop, self).__init__(parent)

        self.acc_index = acc_index
        self.acc_act = acc_act
        #self.move(pos_x, pos_y)
        self.size_wh = int(32) # * settings.size_factor)
        self.label = QItemLabel(self.acc_act['frame'].scaled(self.size_wh,
                                                             self.size_wh,
                                                             aspectMode=Qt.KeepAspectRatio,
                                                             mode=Qt.SmoothTransformation)
                                )
        self.label.setFixedSize(self.size_wh,self.size_wh)
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.previous_img = None
        self.current_img = acc_act['item_image'][0]
        #self.anchor = acc_act['anchor']
        self.set_img()
        
        if settings.on_top_hint:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags)
        #self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()

        self.move(pos_x, pos_y)

        self.petlayout = QVBoxLayout()
        self.petlayout.addWidget(self.label)
        self.petlayout.setAlignment(Qt.AlignCenter)
        self.petlayout.setContentsMargins(0,0,0,0)

        self.setLayout(self.petlayout)
        self.show()

        screen_geo = settings.current_screen.availableGeometry()
        self.current_screen = settings.current_screen.geometry()
        self.screen_width = screen_geo.width()
        work_height = screen_geo.height()
        self.floor_pos = work_height-self.height()

        # 运动轨迹相关
        self.finished = False
        self.v_x = random.uniform(2,4) * random.choice([-1,1])
        self.v_y = -random.uniform(5,10)
        self.gravity = 1.0
        self.waitn = 0
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.Action)
        #print(self.pet_conf.interact_speed)
        self.timer.start(20)

    def set_img(self):
        self.label.setPixmap(self.current_img) #QPixmap.fromImage(self.current_img))

    def _closeit(self):
        #self.closed_note.emit(self.note_index)
        self.timer.stop()
        self.close()

    def closeEvent(self, event):
        # we don't need the notification anymore, delete it!
        self.closed_acc.emit(self.acc_index)
        self.deleteLater()

    def ontop_update(self):
        if settings.on_top_hint:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()

    def Action(self):

        if self.finished:
            self.waitn += 1
            if self.waitn >= 3000/20:
                self.timer.stop()
                self._closeit()
                return
            else:
                return
        
        plus_y = self.v_y
        plus_x = self.v_x
        self.v_y += self.gravity
        self._move(plus_x, plus_y)

    def _move(self, plus_x, plus_y):
        
        new_x = self.pos().x()+plus_x
        new_y = self.pos().y()+plus_y

        new_x, new_y = self.limit_in_screen(new_x, new_y)

        self.move(new_x, new_y)

    def limit_in_screen(self, new_x, new_y):
        # 超出当前屏幕左边界
        if new_x+self.width()//2 < self.current_screen.topLeft().x(): #self.border:
            #surpass_x = 'Left'
            new_x = self.current_screen.topLeft().x()-self.width()//2 #self.screen_width + self.border - self.width()

        # 超出当前屏幕右边界
        elif new_x+self.width()//2 > self.current_screen.topLeft().x() + self.screen_width: #self.current_screen.bottomRight().x(): # + self.border:
            #surpass_x = 'Right'
            new_x = self.current_screen.topLeft().x() + self.screen_width-self.width()//2 #self.border-self.width()

        # 超出当前屏幕上边界
        if new_y+self.height()-self.label.height()//2 < self.current_screen.topLeft().y(): #self.border:
            #surpass_y = 'Top'
            new_y = self.current_screen.topLeft().y() + self.label.height()//2 - self.height() #self.floor_pos

        # 超出当前屏幕下边界
        elif new_y > self.floor_pos:
            self.finished = True
            new_y = self.floor_pos

        return new_x, new_y


# Mini-Pet following main settings:
#   follow_x only: allow drop (can be turned off), allow drag
#   follow_y only: no drop, no drag
#   follow x and y: no drop, no drag


''' Cursor decorator not completed
class DPMouseDecor(QWidget):
    closed_acc = Signal(str, name='closed_acc')
    acc_withdrawed = Signal(str, name='acc_withdrawed')

    def __init__(self, acc_index,
                 config,
                 parent=None):
        super(DPMouseDecor, self).__init__(parent)

        self.acc_index = acc_index
        self.config = config
        self.decor_name = config['name']
        self.cursor_size = 48

        self.label = QLabel(self)
        self.label.setScaledContents(False)
        self.previous_img = None
        self.current_img = config['default'][0].images[0]
        self.anchor = [-24, -24] #config['anchor']
        self.set_img()

        self.petlayout = QVBoxLayout()
        self.petlayout.addWidget(self.label)
        self.petlayout.setAlignment(Qt.AlignCenter)
        self.petlayout.setContentsMargins(0,0,0,0)

        self.setLayout(self.petlayout)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow | Qt.NoDropShadowWindowHint | Qt.BypassWindowManagerHint)
        self.show()
        
        self.manager = MouseMoveManager(click=True)
        self.manager.moved.connect(self._move_to_mouse)
        self.manager.clicked.connect(self._handle_click)

        self.act_name = 'default'
        self.current_act = None
        self.previous_act = None
        self.playid = 0
        self.act_id = 0
        #self.finished = False
        #self.waitn = 0
        
        # 摆动相关
        self.mousepos9=[self.pos().x(), self.pos().y()]
        self.mousepos8=[self.pos().x(), self.pos().y()]
        self.mousepos7=[self.pos().x(), self.pos().y()]
        self.mousepos6=[self.pos().x(), self.pos().y()]
        self.mousepos5=[self.pos().x(), self.pos().y()]
        self.mousepos4=[self.pos().x(), self.pos().y()]
        self.mousepos3=[self.pos().x(), self.pos().y()]
        self.mousepos2=[self.pos().x(), self.pos().y()]
        self.mousepos1=[self.pos().x(), self.pos().y()]
        self.mousepos0=[self.pos().x(), self.pos().y()]

        self.angle_destination = 0
        self.angle_current = 0
        self.angle_delta = 0

        
        # 是否可关闭
        #if self.closable:
        menu = RoundMenu(parent=self)
        self.quit_act = Action(FIF.CLOSE,
                               self.tr('Withdraw'), menu)
        self.quit_act.triggered.connect(self._withdraw)
        menu.addAction(self.quit_act)
        self.menu = menu
        
        
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.Action)
        self.fresh_ms = 40
        self.timer.start(self.fresh_ms)
        

    def mousePressEvent(self, event):
        """
        鼠标点击事件
        :param event: 事件
        :return:
        """
        if event.button() == Qt.RightButton:
            # 打开右键菜单
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self._show_right_menu)

    def _show_right_menu(self):
        self.menu.popup(QCursor.pos()-QPoint(0, 50))

    def set_img(self):
        width_tmp = self.cursor_size #*settings.size_factor
        height_tmp = self.cursor_size #*settings.size_factor
        self.label.resize(width_tmp, height_tmp)
        self.label.setPixmap(QPixmap.fromImage(self.current_img.scaled(width_tmp, height_tmp, 
                                                                       aspectMode=Qt.KeepAspectRatio,
                                                                       mode=Qt.SmoothTransformation)))
        #print(self.size())

    def _move_to_mouse(self,x,y):
        #print(self.label.width()//2)
        self.move(x+self.anchor[0], y+self.anchor[1])

    def _handle_click(self, pressed):
        if pressed:
            self.act_name = 'click'
        else:
            self.act_name = 'default'

        self.playid = 0
        self.act_id = 0

    def _withdraw(self):
        self.acc_withdrawed.emit(self.decor_name)
        self._closeit()

    def _closeit(self):
        self.close()

    def closeEvent(self, event):
        self.closed_acc.emit(self.acc_index)
        self.deleteLater()

    def ontop_update(self):
        return

    def img_from_act(self, act, rotation=0):

        if self.current_act != act:
            self.previous_act = self.current_act
            self.current_act = act
            self.playid = 0

            n_repeat = math.ceil(act.frame_refresh / (self.fresh_ms / 1000))
            self.img_list_expand = [item for item in act.images for i in range(n_repeat)] * act.act_num

        img = self.img_list_expand[self.playid]

        self.playid += 1
        if self.playid >= len(self.img_list_expand):
            self.playid = 0
        #img = act.images[0]
        self.previous_img = self.current_img
        self.current_img = img.transformed(QTransform().rotate(rotation), Qt.SmoothTransformation)

    def Action(self):

        self.mousepos8=self.mousepos7
        self.mousepos7=self.mousepos6
        self.mousepos6=self.mousepos5
        self.mousepos5=self.mousepos4
        self.mousepos4=self.mousepos3
        self.mousepos3=self.mousepos2
        self.mousepos2=self.mousepos1
        self.mousepos1=self.mousepos0
        self.mousepos0=[self.pos().x(), self.pos().y()]

        rotation = self.cal_rotate()
        rotation = self.continuous_change(rotation)
        
        acts = self.config[self.act_name]
        #print(settings.act_id, len(acts))
        if self.act_id >= len(acts):
            self.act_id = 0

        #else:
        act = acts[self.act_id]
        n_repeat = math.ceil(act.frame_refresh / (self.fresh_ms / 1000))
        n_repeat *= len(act.images) * act.act_num
        self.img_from_act(act, rotation)
        if self.playid >= n_repeat-1:
            self.act_id += 1

        if self.previous_img != self.current_img:
            self.set_img()
            self._move(act)

    def cal_rotate(self):
        ax = (self.mousepos0[0]+self.mousepos8[0]-2*self.mousepos4[0])/40 * settings.fixdragspeedx
        ay = (self.mousepos0[1]+self.mousepos8[1]-2*self.mousepos4[1])/40 * settings.fixdragspeedy

        if ax==0 and ay==0:
            return 0
        elif ay == 0:
            return 360-90 if ax>0 else 90
        elif ax == 0:
            return 0 if ay<0 else 180

        theta = math.degrees(math.atan(ay/ax))
        g = settings.gravity * 2000
        a = math.sqrt(ax**2 + ay**2)

        if ay < 0:
            c = math.sqrt(a**2 + g**2 - 2*a*g*math.cos(math.radians(90+theta)))
        else:
            c = math.sqrt(a**2 + g**2 - 2*a*g*math.cos(math.radians(90-theta)))
        
        cos_gama = (c**2 + g**2 - a**2) / (2*c*g)
        gama = math.degrees(math.acos(cos_gama))

        return 360-gama if ax>0 else gama

    def continuous_change(self, rotation):

        if self.angle_destination != rotation:
            self.angle_destination = rotation
            angle_diff = rotation - self.angle_current
            self.angle_delta = max(1, abs(angle_diff) / 20) * (2*int(angle_diff>0)-1)

        if self.angle_destination - rotation < self.angle_delta:
            self.angle_current = self.angle_destination
        else:
            self.angle_current += self.angle_delta
        return self.angle_current



    def _move(self, act: QAction) -> None: #pos: QPoint, act: QAction) -> None:
        """
        在 Thread 中发出移动Signal
        :param act: 动作
        :return
        """
        #print(act.direction, act.frame_move)
        plus_x = 0.
        plus_y = 0.
        direction = act.direction

        if direction is None:
            pass
        else:
            if direction == 'right':
                plus_x = act.frame_move

            if direction == 'left':
                plus_x = -act.frame_move

            if direction == 'up':
                plus_y = -act.frame_move

            if direction == 'down':
                plus_y = act.frame_move

        self.move(self.pos().x()+plus_x, self.pos().y()+plus_y)

'''

