# coding:utf-8
"""MapleFox 对话窗口（本地 LLM）

外观沿用 MemoWindow：无框 + 半透明 + 投影白卡 + 自绘标题栏 + 拖拽移动。
交互：流式逐字显示，Enter 发送 / Shift+Enter 换行，生成中可打断。
"""
import os
from sys import platform

from PySide6.QtCore import Qt, QTimer, Signal, QThread, QSize, QPointF
from PySide6.QtGui import QColor, QIcon, QCursor, QPainter, QPixmap, QPainterPath, QFont, QFontMetrics
from PySide6.QtWidgets import (QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
                               QScrollArea, QTextEdit, QPushButton, QSizePolicy,
                               QGraphicsDropShadowEffect, QApplication)

from qfluentwidgets import isDarkTheme

import DyberPet.settings as settings
from DyberPet.style.theme import active_palette, UI_FONT
from DyberPet.llm_client import LLMClient, LLMWorker

try:
    import qtawesome as qta
except ImportError:
    qta = None

basedir = settings.BASEDIR


def _chat_qss(dark=None):
    """对话窗口样式：米黄底；气泡背景改在每个气泡上内联设置（更可靠）"""
    p = active_palette(dark)
    accent = p['primary']
    # 浅色模式用米黄色做背景，深色模式保持原来的卡片色
    frame_bg = '#F9F1E4' if not dark else p['card']
    return f"""
#chatFrame {{
    background: {frame_bg};
    border-radius: 12px;
    border: 1px solid {p['border']};
}}
#chatFrame QLabel#chatTitle {{
    font-family: {UI_FONT};
    font-size: 15px;
    font-weight: 600;
    color: {p['text']};
}}
#chatFrame QTextEdit {{
    border: 1px solid {p['border']};
    border-radius: 12px;
    background: {p['card']};
    padding: 6px 8px;
    font-family: {UI_FONT};
    font-size: 13px;
    color: {p['text']};
    selection-background-color: {accent};
}}
#chatFrame QTextEdit:focus {{
    border: 1px solid {accent};
}}
#chatFrame QTextEdit:disabled {{
    color: {p['textDisabled']};
}}
"""


def _screen_dpr():
    screen = QApplication.primaryScreen()
    return screen.devicePixelRatio() if screen is not None else 1.0


def _rect_pixmap(source, size=40):
    """不裁切、整体缩放（保留完整内容），并支持 Hi-DPI"""
    dpr = _screen_dpr()
    px = int(size * dpr)
    pm = source.scaled(px, px, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    pm.setDevicePixelRatio(dpr)
    return pm


def _circle_pixmap(source, size=40):
    """把头像裁成圆形（抗锯齿 + Hi-DPI），用于用户头像的圆形容器"""
    dpr = _screen_dpr()
    px = int(size * dpr)
    scaled = source.scaled(px, px, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = (scaled.width() - px) // 2
    y = (scaled.height() - px) // 2
    scaled = scaled.copy(x, y, px, px)
    pm = QPixmap(px, px)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing, True)
    path = QPainterPath()
    path.addEllipse(0, 0, px, px)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, scaled)
    painter.end()
    pm.setDevicePixelRatio(dpr)
    return pm


def _default_user_pixmap(size=40):
    """默认用户头像：圆形容器；优先用用户提供的图片，缺失时回落为圆形剪影"""
    path = os.path.join(basedir, 'res', 'icons', 'default_avatar.jpeg')
    pm = QPixmap()
    if os.path.exists(path) and pm.load(path):
        return _circle_pixmap(pm, size)

    # fallback：圆形卡片背景上的用户剪影
    dpr = _screen_dpr()
    px = int(size * dpr)
    p = active_palette()
    pm = QPixmap(px, px)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(p['border']))
    painter.drawEllipse(0, 0, px, px)
    painter.setBrush(QColor(p['textSecondary']))
    painter.drawEllipse(QPointF(px * 0.5, px * 0.38), px * 0.15, px * 0.15)
    painter.drawEllipse(QPointF(px * 0.5, px * 0.95), px * 0.26, px * 0.23)
    painter.end()
    pm.setDevicePixelRatio(dpr)
    return pm


def _pet_pixmap(size=40):
    """MapleFox 头像：用 avatar.png(256px) 整体缩放、不裁切；缺失时回落为待机帧。

    注意不再加载 000.ico：Qt 读多帧 ICO 默认只取第一帧（通常是最小的 16~48px），
    放大到 Hi-DPI 像素尺寸会比 256px 的 avatar.png 更糊，是之前头像变虚的元凶。
    """
    for path in (
        os.path.join(basedir, 'res', 'role', 'MapleFox', 'avatar.png'),
        os.path.join(basedir, 'res', 'role', 'MapleFox', 'action', 'stand_0.png'),
    ):
        if os.path.exists(path):
            pm = QPixmap()
            if pm.load(path):
                return _rect_pixmap(pm, size)
    return _default_user_pixmap(size)


class _InputBox(QTextEdit):
    """输入框：Enter 发送，Shift+Enter 换行"""

    sendTriggered = Signal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            self.sendTriggered.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class ChatWindow(QWidget):
    """与 MapleFox 聊天的独立窗口"""

    close_chat = Signal(name='close_chat')
    send_request = Signal(str)
    warmup_request = Signal(name='warmup_request')

    MAX_BUBBLE_WIDTH = 260
    AVATAR_SIZE = 40
    BUBBLE_NAMES = ('bubblePet', 'bubbleUser', 'bubbleSys')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_follow_mouse = False
        self._generating = False
        self._checked = False
        self._stream_label = None
        self._waiting = False
        self._dots_timer = None
        self._thread_cleaned = False

        self._client = LLMClient()
        self._pet_avatar = _pet_pixmap(self.AVATAR_SIZE)
        self._user_avatar = _default_user_pixmap(self.AVATAR_SIZE)

        self.centralwidget = QFrame()
        self.centralwidget.setObjectName('chatFrame')
        self.centralwidget.setStyleSheet(_chat_qss())

        vbox = QVBoxLayout(self.centralwidget)
        vbox.setContentsMargins(12, 10, 12, 12)
        vbox.setSpacing(10)

        vbox.addLayout(self._build_title())
        vbox.addWidget(self._build_message_area(), 1)
        vbox.addLayout(self._build_input_area())

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.addWidget(self.centralwidget)
        self.setFixedSize(420, 560)

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

        self._setup_worker()

    # ------------------------------------------------------------------
    # 界面构建
    # ------------------------------------------------------------------
    def _build_title(self):
        hbox = QHBoxLayout()
        hbox.setSpacing(6)

        icon = QLabel()
        icon.setFixedSize(22, 22)
        icon.setScaledContents(True)
        if qta is not None:
            c = '#FFFFFF' if isDarkTheme() else '#000000'
            icon.setPixmap(qta.icon('fa5s.comment', color=c).pixmap(22, 22))
        else:
            image_path = os.path.join(basedir, 'res/icons/Dialogue_icon.png')
            if os.path.exists(image_path):
                icon.setPixmap(QIcon(image_path).pixmap(22, 22))

        self.title_label = QLabel(self.tr('Chat'))
        self.title_label.setObjectName('chatTitle')

        self.close_button = QPushButton()
        self.close_button.setFixedSize(20, 20)
        dark = isDarkTheme()
        c = '#FFFFFF' if dark else '#000000'
        if qta is not None:
            self.close_button.setIcon(qta.icon('fa5s.times', color=c))
        else:
            close_path = os.path.join(basedir, 'res/icons/close_icon.png')
            if os.path.exists(close_path):
                self.close_button.setIcon(QIcon(close_path))
        self.close_button.setIconSize(QSize(12, 12))
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet(
            'QPushButton { border: none; background: transparent; }')
        self.close_button.clicked.connect(self.close_chat)

        hbox.addWidget(icon)
        hbox.addWidget(self.title_label)
        hbox.addStretch(1)
        hbox.addWidget(self.close_button)
        return hbox

    def _build_message_area(self):
        self._msg_widget = QWidget()
        self._msg_widget.setStyleSheet('background: transparent;')
        self._msg_layout = QVBoxLayout(self._msg_widget)
        self._msg_layout.setContentsMargins(2, 2, 2, 2)
        self._msg_layout.setSpacing(10)
        self._msg_layout.addStretch(1)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.viewport().setAutoFillBackground(False)
        self._scroll.setStyleSheet(
            'QScrollArea { border: none; background: transparent; }'
            'QScrollArea::viewport { background: transparent; border: none; }')
        self._scroll.setWidget(self._msg_widget)
        return self._scroll

    def _build_input_area(self):
        hbox = QHBoxLayout()
        hbox.setSpacing(8)

        self.text_edit = _InputBox()
        self.text_edit.setPlaceholderText(self.tr('Say something to MapleFox...'))
        self.text_edit.setFixedHeight(60)
        self.text_edit.sendTriggered.connect(self._send)

        self.send_button = QPushButton(self.tr('Send'))
        p = active_palette()
        self.send_button.setFixedHeight(60)
        self.send_button.setFixedWidth(64)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setStyleSheet(
            f'QPushButton {{ border: none; border-radius: 8px;'
            f' background: {p["primary"]}; color: {p["onPrimary"]};'
            f' font: 13px {UI_FONT}; }}'
            f'QPushButton:hover {{ background: {p["primaryHover"]}; }}'
            f'QPushButton:pressed {{ background: {p["primaryPressed"]}; }}'
            f'QPushButton:disabled {{ background: {p["border"]}; color: {p["textSecondary"]}; }}')
        self.send_button.clicked.connect(self._on_send_clicked)

        hbox.addWidget(self.text_edit, 1)
        hbox.addWidget(self.send_button)
        return hbox

    # ------------------------------------------------------------------
    # 线程
    # ------------------------------------------------------------------
    def _setup_worker(self):
        # 注意：QThread 不挂父对象。若挂在 self 上，父销毁时线程若仍在跑，
        # Qt 会打印 'QThread: Destroyed while thread is still running'；
        # 这里改为线程结束后自删，生命周期完全由我们控制。
        self._thread = QThread()
        self._worker = LLMWorker()
        self._worker.moveToThread(self._thread)

        self._worker.token.connect(self._on_token)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self.send_request.connect(self._worker.request)
        self.warmup_request.connect(self._worker.warmup)

        # 线程结束后自动清理线程与 worker 对象，避免悬空引用
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

        # 程序退出时无论窗口是否显式关闭，都保证停掉阻塞的 worker 线程
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self._cleanup_thread)

    def closeEvent(self, event):
        self._cleanup_thread()
        super().closeEvent(event)

    def _cleanup_thread(self):
        """停掉 worker 线程。

        worker 里的网络请求是阻塞 I/O，quit() 无法打断它，因此给宽限时间，
        超时则强制 terminate。所有 wait() 都带超时，绝不允许主线程被永久阻塞
        （之前无超时的 wait() 会在 terminate 未生效时死等，导致程序卡死）。
        """
        if getattr(self, '_thread_cleaned', False):
            return
        self._thread_cleaned = True
        try:
            self._worker.stop()
        except Exception:
            pass
        self._thread.quit()
        if not self._thread.wait(3000):
            self._thread.terminate()
            self._thread.wait(1500)

    # ------------------------------------------------------------------
    # 消息
    # ------------------------------------------------------------------
    def _add_message(self, text, role='pet'):
        """role: pet / user / system"""
        name = {'pet': 'bubblePet', 'user': 'bubbleUser', 'system': 'bubbleSys'}.get(role, 'bubblePet')

        p = active_palette(isDarkTheme())
        styles = {
            'pet': (f'background:#FFFFFF; color:#000000; border:1px solid {p["border"]}; '
                    f'border-radius:12px; padding:8px 10px;'),
            'user': (f'background:{p["primary"]}; color:#FFFFFF; border:none; '
                     f'border-radius:12px; padding:8px 10px;'),
            'system': (f'background:transparent; color:{p["textSecondary"]}; '
                       f'border:1px solid {p["border"]}; border-radius:12px; '
                       f'padding:8px 10px;'),
        }

        bubble = QLabel(text)
        bubble.setObjectName(name)
        bubble.setStyleSheet(styles.get(role, styles['pet']))
        # 显式设置 QFont，使 QFontMetrics 计算出的宽度与实际渲染一致，避免短文字被错误换行
        font = QFont()
        font.setFamilies(["Segoe UI", "Microsoft YaHei UI", "PingFang SC"])
        font.setPointSize(13 if role != 'system' else 12)
        bubble.setFont(font)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble.setMaximumWidth(self.MAX_BUBBLE_WIDTH)
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._resize_bubble(bubble, text)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        if role == 'user':
            row.addStretch(1)
            row.addWidget(bubble)
            row.addWidget(self._avatar_label(self._user_avatar))
        elif role == 'pet':
            row.addWidget(self._avatar_label(self._pet_avatar))
            row.addWidget(bubble)
            row.addStretch(1)
        else:
            row.addStretch(1)
            row.addWidget(bubble)
            row.addStretch(1)

        # stretch 始终保持在最后一项
        self._msg_layout.insertLayout(self._msg_layout.count() - 1, row)
        self._scroll_to_bottom()
        return bubble

    def _avatar_label(self, pixmap):
        # 无容器样式：头像形状由 pixmap 决定——用户头像圆形裁切、MapleFox 保留完整画面
        label = QLabel()
        label.setFixedSize(self.AVATAR_SIZE, self.AVATAR_SIZE)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignTop)
        label.setScaledContents(False)
        return label

    def _scroll_to_bottom(self):
        QTimer.singleShot(0, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()))

    def _set_input_enabled(self, enabled):
        self.text_edit.setEnabled(enabled)
        if enabled:
            self.send_button.setText(self.tr('Send'))
        else:
            self.send_button.setText(self.tr('Stop') if self._generating else self.tr('Send'))
        if not self._generating:
            self.send_button.setEnabled(enabled)

    # ------------------------------------------------------------------
    # 发送 / 接收
    # ------------------------------------------------------------------
    def _on_send_clicked(self):
        if self._generating:
            self._worker.stop()
            self.send_button.setEnabled(False)
            self.send_button.setText(self.tr('Send'))
            return
        self._send()

    def _send(self):
        if self._generating:
            return
        text = self.text_edit.toPlainText().strip()
        if not text:
            return

        self.text_edit.clear()
        self._add_message(text, 'user')

        self._generating = True
        self.text_edit.setEnabled(False)
        self.send_button.setEnabled(True)
        self.send_button.setText(self.tr('Stop'))

        self._stream_label = self._add_message('', 'pet')
        self._start_waiting()
        self.send_request.emit(text)

    # ---- 等待动画（模型加载 / 首个 token 未到之前显示跳动的三点）----
    def _start_waiting(self):
        self._waiting = True
        self._dots = 0
        self._stop_dots_timer()
        self._dots_timer = QTimer(self)
        self._dots_timer.setInterval(400)
        self._dots_timer.timeout.connect(self._tick_dots)
        self._dots_timer.start()
        self._tick_dots()

    def _stop_waiting(self):
        self._waiting = False
        self._stop_dots_timer()

    def _stop_dots_timer(self):
        if self._dots_timer is not None:
            self._dots_timer.stop()
            self._dots_timer.deleteLater()
            self._dots_timer = None

    def _tick_dots(self):
        if self._stream_label is None:
            return
        self._dots = self._dots % 3 + 1
        self._stream_label.setText('·' * self._dots)
        self._resize_bubble(self._stream_label, self._stream_label.text())
        self._msg_layout.update()
        self._scroll_to_bottom()

    def _on_token(self, piece):
        if self._stream_label is None:
            return
        if self._waiting:
            self._stop_waiting()
            self._stream_label.setText('')
        self._stream_label.setText(self._stream_label.text() + piece)
        self._resize_bubble(self._stream_label, self._stream_label.text())
        self._msg_layout.update()
        self._scroll_to_bottom()

    def _on_finished(self, reply):
        self._stop_waiting()
        self._generating = False
        self._stream_label = None
        self._set_input_enabled(True)
        self.text_edit.setFocus()
        # 用清洗后的完整文本覆盖流式内容（动作描写过滤可能有微小差异）
        if reply:
            self._replace_last(reply)
        self._scroll_to_bottom()

    def _on_failed(self, kind):
        self._stop_waiting()
        self._generating = False
        self._stream_label = None
        self._set_input_enabled(True)
        self._remove_last_if_empty()

        messages = {
            'connection': self.tr('Cannot reach the model service. Please start Ollama and try again.'),
            'timeout': self.tr('The model service did not respond in time. Please try again.'),
            'http': self.tr('The model service returned an error. Check the model name in Settings.'),
        }
        self._add_message(messages.get(kind, self.tr('Something went wrong while generating a reply.')), 'system')
        self._scroll_to_bottom()

    def _last_row(self):
        idx = self._msg_layout.count() - 2  # 最后一项是 stretch
        if idx < 0:
            return None
        item = self._msg_layout.itemAt(idx)
        if item is None:
            return None
        return item.layout()

    def _last_bubble(self):
        row = self._last_row()
        if row is None:
            return None
        for j in range(row.count()):
            w = row.itemAt(j).widget()
            if isinstance(w, QLabel) and w.objectName() in self.BUBBLE_NAMES:
                return w
        return None

    def _replace_last(self, text):
        """把最后一条气泡替换成给定文本"""
        label = self._last_bubble()
        if label is not None:
            label.setText(text)
            self._resize_bubble(label, text)
            self._msg_layout.update()

    def _resize_bubble(self, bubble, text):
        """按实际文字宽度计算气泡宽度：短则单行贴边，超出最大宽度则限制后换行。

        宽度需留 ~8px 余量：QLabel 的断行判断和 QFontMetrics 存在舍入/衬线差异，
        若宽度刚好等于文字宽，最后一个字符常被挤到第二行。
        """
        fm = QFontMetrics(bubble.font())
        padding = 22   # 水平 padding 10+10 + border 1+1
        w = fm.horizontalAdvance(text) + padding + 8
        if w > self.MAX_BUBBLE_WIDTH:
            w = self.MAX_BUBBLE_WIDTH
        elif w < 40:
            w = 40
        bubble.setFixedWidth(w)
        bubble.setMaximumWidth(self.MAX_BUBBLE_WIDTH)

    def _remove_last_if_empty(self):
        label = self._last_bubble()
        row = self._last_row()
        if label is None or row is None or label.text().strip():
            return
        self._msg_layout.removeItem(row)
        self._clear_layout(row)

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            w = child.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
            else:
                sub = child.layout()
                if sub is not None:
                    ChatWindow._clear_layout(sub)
        layout.setParent(None)

    # ------------------------------------------------------------------
    # 服务探测
    # ------------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)
        if self._checked:
            return
        self._checked = True

        if not getattr(settings, 'llm_enabled', True):
            self._add_message(self.tr('Chat is turned off. You can enable it in Settings.'), 'system')
            self._set_input_enabled(False)
            return

        if not self._client.is_available():
            self._add_message(
                self.tr('Cannot reach the model service at %1. Start Ollama, then reopen this window.')
                .replace('%1', self._client._base_url()), 'system')
            self._set_input_enabled(False)
            return

        # 后台预热模型，避免第一条消息卡在模型加载上
        self.warmup_request.emit()
        self.text_edit.setFocus()

    # ------------------------------------------------------------------
    # 窗口拖拽（与 MemoWindow 一致）
    # ------------------------------------------------------------------
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
