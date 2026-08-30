# coding:utf-8
"""简约设置页：SettingRow 体系（完全脱离 Fluent SettingCard）"""
import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea,
                               QPushButton, QColorDialog)

from qfluentwidgets import isDarkTheme, setThemeColor

import DyberPet.settings as settings
from DyberPet.style import palette
from DyberPet.style.theme import active_palette, UI_FONT
from DyberPet.style.panel import SettingRow, SSwitch, SSlider, SComboBox, SScrollArea

basedir = settings.BASEDIR


class SettingInterface(QWidget):
    """简约设置页（QWidget + 滚动区 + SettingRow）"""

    ontop_changed = Signal(name='ontop_changed')
    scale_changed = Signal(name='scale_changed')
    lang_changed = Signal(name='lang_changed')

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('SettingInterface')

        # 当前 UI 实际显示的语言（启动时快照；切换语言后 UI 不即时重绘，提示始终用它）
        self._ui_lang = self._current_lang()

        # 桌宠大小三档
        self.pet_size_scales = [0.5, 0.75, 1.0]
        self.pet_size_texts = self._get_pet_size_texts()

        self._scroll = SScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.viewport().setAutoFillBackground(False)
        self._scroll.setStyleSheet(
            'QScrollArea { border: none; background: transparent; }'
            'QScrollArea::viewport { background: transparent; border: none; }'
            'QScrollArea > QWidget > QWidget { background: transparent; }')

        self._body = QWidget()
        self._layout = QVBoxLayout(self._body)
        self._layout.setContentsMargins(24, 16, 24, 24)
        self._layout.setSpacing(10)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)
        self._scroll.setWidget(self._body)

        self._buildSections()

    # ---------- 构建 ----------
    def _addSectionTitle(self, text):
        p = active_palette()
        label = QLabel(text, self._body)
        label.setStyleSheet(
            f'QLabel {{ color: {p["textSecondary"]}; font: 600 13px {UI_FONT};'
            f' padding: 12px 4px 4px 4px; background: transparent; }}')
        self._layout.addWidget(label)
        return label

    def _makeSwitch(self, icon, title, content, checked, slot):
        row = SettingRow(icon, title, content, self._body)
        switch = SSwitch()
        switch.setMinimumSize(34, 24)
        switch.setChecked(checked)
        switch.toggled.connect(slot)
        row.addWidget(switch)
        self._layout.addWidget(row)
        return row

    def _makeSlider(self, icon, title, content, vmin, vmax, value, slot, sstep=1):
        row = SettingRow(icon, title, content, self._body)
        slider = SSlider()
        slider.setRange(vmin, vmax)
        slider.setValue(value)
        valueLabel = QLabel(f'{value * sstep:g}', self._body)
        p = active_palette()
        valueLabel.setStyleSheet(f'QLabel {{ color: {p["text"]}; font: 13px {UI_FONT}; }}')
        valueLabel.setFixedWidth(46)
        valueLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        slider.setFixedWidth(160)
        slider.valueChanged.connect(
            lambda v: (valueLabel.setText(f'{v * sstep:g}'), slot(v)))
        row.addWidgets([valueLabel, slider])
        self._layout.addWidget(row)
        return row

    def _makeCombo(self, icon, title, content, items, index, slot):
        row = SettingRow(icon, title, content, self._body)
        combo = SComboBox()
        combo.addItems(items)
        combo.setCurrentIndex(index)
        combo.setFixedWidth(180)
        combo.currentTextChanged.connect(slot)
        row.comboBox = combo
        row.addWidget(combo)
        self._layout.addWidget(row)
        return row

    def _makeColorRow(self):
        row = SettingRow('fa5s.palette', self.tr('Theme color'),
                         self.tr('Change the theme color of you application'), self._body)
        btn = QPushButton(self.tr('Choose color'), self._body)
        p = active_palette()
        btn.setStyleSheet(
            f'QPushButton {{ border: 1px solid {p["border"]}; border-radius: 6px;'
            f' background: {p["card"]}; padding: 4px 14px; color: {p["text"]};'
            f' font: 13px {UI_FONT}; }}'
            f'QPushButton:hover {{ background: {p["hover"]}; }}')
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._showColorDialog)
        row.addWidget(btn)
        self._layout.addWidget(row)
        return row

    def _buildSections(self):
        # Mode
        self._addSectionTitle(self.tr('Mode'))
        self.AlwaysOnTopCard = self._makeSwitch(
            'fa5s.thumbtack', self.tr('Always-On-Top'),
            self.tr('Pet will be displayed on top of the other Apps'),
            settings.on_top_hint, self._AlwaysOnTopChanged)
        self.AllowDropCard = self._makeSwitch(
            'fa5s.arrow-down', self.tr('Allow Drop'),
            self.tr('When mouse released, pet falls to the ground (on) / stays at the site (off)'),
            settings.set_fall, self._AllowDropChanged)
        self.AutoLockCard = self._makeSwitch(
            'fa5s.lock', self.tr('Auto-Lock'),
            self.tr('When screen is locked, HP and FV will be locked too (currently only works in Windows)'),
            settings.auto_lock, self._AutoLockChanged)
        if os.name != 'nt':
            self.AutoLockCard.findChild(SSwitch).setEnabled(False)

        # Interaction
        self._addSectionTitle(self.tr('Interaction'))
        self.GravityCard = self._makeSlider(
            'fa5s.arrow-circle-down', self.tr('Gravity'),
            self.tr('Pet falling down acceleration'),
            1, 200, int(settings.gravity * 100), self._GravityChanged, sstep=0.01)
        self.DragCard = self._makeSlider(
            'fa5s.mouse-pointer', self.tr('Drag Speed'),
            self.tr('Mouse speed factor'),
            0, 200, int(settings.fixdragspeedx * 100), self._DragChanged, sstep=0.01)

        # Notification
        self._addSectionTitle(self.tr('Notification'))
        self.AllowToasterCard = self._makeSwitch(
            'fa5s.bell', self.tr('Pop-up Toaster'),
            self.tr('When turned on, notification will pop-up at the bottom right corner'),
            settings.toaster_on, self._AllowToasterChanged)
        self.AllowBubbleCard = self._makeSwitch(
            'fa5s.comment', self.tr('Dialogue Bubble'),
            self.tr('When turned on, various kinds of bubbles will pop-up above the pet'),
            settings.bubble_on, self._AllowBubbleChanged)

        # Personalization
        self._addSectionTitle(self.tr('Personalization'))
        self.PetSizeCard = self._makeCombo(
            'fa5s.expand-arrows-alt', self._get_pet_size_title(),
            self._get_pet_size_subtitle(),
            self.pet_size_texts, self._scale_to_index(settings.tunable_scale),
            self._PetSizeChanged)
        self.languageCard = self._makeCombo(
            'fa5s.globe', self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            self._lang_choices(), 0, self._LanguageChanged)
        self.themeColorCard = self._makeColorRow()

    def _lang_choices(self):
        lang_choices = list(settings.lang_dict.keys())
        lang_now = lang_choices[list(settings.lang_dict.values()).index(settings.language_code)]
        lang_choices.remove(lang_now)
        return [lang_now] + lang_choices

    # ---------- 设置变更逻辑 ----------
    def _AlwaysOnTopChanged(self, isChecked):
        settings.on_top_hint = isChecked
        settings.save_settings()
        self.ontop_changed.emit()

    def _AllowDropChanged(self, isChecked):
        settings.set_fall = isChecked
        settings.save_settings()

    def _AutoLockChanged(self, isChecked):
        settings.auto_lock = isChecked
        settings.save_settings()

    def _GravityChanged(self, value):
        settings.gravity = value * 0.01
        settings.save_settings()

    def _DragChanged(self, value):
        settings.fixdragspeedx, settings.fixdragspeedy = value * 0.01, value * 0.01
        settings.save_settings()

    def _PetSizeChanged(self, text):
        idx = self.pet_size_texts.index(text)
        settings.tunable_scale = self.pet_size_scales[idx]
        settings.scale_dict[settings.petname] = settings.tunable_scale
        settings.save_settings()
        self.scale_changed.emit()

    def _LanguageChanged(self, value):
        settings.language_code = settings.lang_dict[value]
        settings.save_settings()
        settings.change_translator(settings.lang_dict[value])
        self.lang_changed.emit()
        self._showRestartNotice()

    def _showRestartNotice(self, lang=None):
        """语言切换后提示重启才能完全生效
        提示始终用当前 UI 实际显示的语言（启动时快照，UI 不即时重绘）"""
        from qfluentwidgets import InfoBar, InfoBarPosition
        lang = lang or self._ui_lang
        if lang == 'zh':
            title, content = '需要重启', '语言更改将在重启应用后完全生效'
        elif lang == 'ja':
            title, content = '再起動が必要です', '言語の変更はアプリの再起動後に完全に反映されます'
        else:
            title, content = 'Restart required', 'Language changes take effect fully after restarting the app'
        InfoBar.info(title, content, duration=4000,
                     position=InfoBarPosition.TOP, parent=self.window())

    def _AllowToasterChanged(self, isChecked):
        settings.toaster_on = isChecked
        settings.save_settings()

    def _AllowBubbleChanged(self, isChecked):
        settings.bubble_on = isChecked
        settings.save_settings()

    def _showColorDialog(self):
        color = QColorDialog.getColor(
            QColor(settings.themeColor or settings.DEFAULT_THEME_COL), self)
        if color.isValid():
            self.colorChanged(color.name())

    def colorChanged(self, color_str):
        setThemeColor(color_str)
        settings.themeColor = color_str
        settings.save_settings()

    # ---------- 语言相关的显示 ----------
    @staticmethod
    def _current_lang():
        lang = settings.language_code or ''
        return lang.split('_')[0]

    def _get_pet_size_texts(self):
        lang = self._current_lang()
        if lang == 'zh':
            return ['小 (200px)', '中 (300px)', '大 (400px)']
        if lang == 'ja':
            return ['小 (200px)', '中 (300px)', '大 (400px)']
        return ['Small (200px)', 'Medium (300px)', 'Large (400px)']

    def _get_pet_size_title(self):
        lang = self._current_lang()
        if lang == 'zh':
            return '桌宠大小'
        if lang == 'ja':
            return 'ペットサイズ'
        return 'Pet Size'

    def _get_pet_size_subtitle(self):
        lang = self._current_lang()
        if lang == 'zh':
            return '选择桌宠的显示大小'
        if lang == 'ja':
            return 'ペットの表示サイズを選択'
        return 'Select the display size of the pet'

    def _scale_to_index(self, scale_value):
        closest = min(range(len(self.pet_size_scales)),
                      key=lambda i: abs(self.pet_size_scales[i] - scale_value))
        return closest

    def _update_scale(self):
        # 语言切换后同步刷新三档下拉的显示文本、卡片标题与说明
        new_texts = self._get_pet_size_texts()
        if new_texts != self.pet_size_texts:
            self.pet_size_texts = new_texts
            combo = self.PetSizeCard.comboBox
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(self.pet_size_texts)
            combo.blockSignals(False)
        self.PetSizeCard.setTitle(self._get_pet_size_title())
        self.PetSizeCard.setContent(self._get_pet_size_subtitle())
        self.PetSizeCard.comboBox.setCurrentIndex(self._scale_to_index(settings.tunable_scale))
