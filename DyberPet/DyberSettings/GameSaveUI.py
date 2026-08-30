# coding:utf-8
"""简约存档管理页：自绘存档卡 + 保存/导入"""
import os
import json
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths, QSize
from PySide6.QtGui import QIcon, QImage, QPixmap, QAction
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea,
                               QPushButton, QFileDialog, QApplication, QFrame)

from qfluentwidgets import isDarkTheme

from DyberPet.style import palette
from DyberPet.style.theme import active_palette, UI_FONT
from DyberPet.style.panel import SettingRow, SScrollArea
from DyberPet.custom_roundmenu import RoundMenu

from .fileOp_utils import CopySave, DeleteQuickSave
import DyberPet.settings as settings
basedir = settings.BASEDIR

try:
    import qtawesome as qta
except ImportError:
    qta = None

from sys import platform


class SaveCard(QFrame):
    """自绘简约存档卡（头像 + 名称 + HP/FV + 操作菜单）"""
    saveClicked = Signal(int, name='saveClicked')
    loadinClicked = Signal(int, name='loadinClicked')
    rewriteClicked = Signal(int, name='rewriteClicked')
    deleteClicked = Signal(int, name='deleteClicked')
    backtraceClicked = Signal(int, name='backtraceClicked')

    def __init__(self, cardIndex, jsonPath=None, parent=None):
        super().__init__(parent)
        self.setObjectName('saveCard')
        self.setFixedHeight(96)
        self.cardIndex = cardIndex
        self.jsonPath = jsonPath
        self.cardTitle = None

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(14, 8, 14, 8)
        self._layout.setSpacing(14)

        self._applyStyle()

        if jsonPath is None:
            self._buildEmpty()
        else:
            self._buildInfo()

    def _applyStyle(self):
        p = active_palette()
        self.setStyleSheet(f'''
            QFrame#saveCard {{
                background-color: {p['card']};
                border: 1px solid {p['border']};
                border-radius: 10px;
            }}
            QFrame#saveCard:hover {{ border-color: {p['textSecondary']}; }}
            QLabel {{ background: transparent; }}
            QLabel#saveCardTitle {{
                color: {p['text']};
                font: 600 14px {UI_FONT};
            }}
            QLabel#saveCardName {{
                color: {p['textSecondary']};
                font: 12px {UI_FONT};
            }}
            QLabel#saveCardStat {{
                color: {p['text']};
                font: 13px {UI_FONT};
            }}
        ''')

    def _buildEmpty(self):
        btn = QPushButton(self)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._saveClicked)
        c = '#FFFFFF' if isDarkTheme() else '#000000'
        if qta is not None:
            btn.setIcon(qta.icon('fa5s.plus', color=c))
        btn.setIconSize(QSize(28, 28))
        btn.setFixedSize(48, 48)
        p = active_palette()
        btn.setStyleSheet(
            f'QPushButton {{ border: 1px dashed {p["border"]}; border-radius: 24px;'
            f' background: transparent; }}'
            f'QPushButton:hover {{ border-color: {p["primary"]}; }}')
        self._layout.addWidget(btn, 0, Qt.AlignCenter)

    def _buildInfo(self):
        # 读取存档信息
        info = open(os.path.join(self.jsonPath, 'info.txt'), 'r', encoding='UTF-8').readlines()
        info = [i.strip() for i in info if i.strip()]
        petname = info[0] if info else '?'
        self.cardTitle = info[1] if len(info) > 1 else ''

        # 头像
        pfp_file = os.path.join(basedir, 'res/icons/unknown.svg')
        infoJson = os.path.join(basedir, 'res/role', petname, 'info', 'info.json')
        if os.path.exists(infoJson):
            infoConfig = json.load(open(infoJson, 'r', encoding='UTF-8'))
            pfp = infoConfig.get('pfp', None)
            if pfp:
                pfp_file = os.path.join(basedir, 'res/role', petname, 'info', pfp)
        image = QImage(pfp_file)
        avatar = QLabel(self)
        avatar.setFixedSize(56, 56)
        avatar.setScaledContents(True)
        avatar.setPixmap(QPixmap.fromImage(image))
        avatar.setStyleSheet('border-radius: 28px;')

        # 名称/标题
        textBox = QVBoxLayout()
        textBox.setSpacing(2)
        titleLabel = QLabel(self.cardTitle, self)
        titleLabel.setObjectName('saveCardTitle')
        nameLabel = QLabel(petname, self)
        nameLabel.setObjectName('saveCardName')
        textBox.addWidget(titleLabel)
        textBox.addWidget(nameLabel)

        # HP / FV
        statBox = QVBoxLayout()
        statBox.setSpacing(2)
        saveData = {}
        try:
            data = json.load(open(os.path.join(self.jsonPath, 'pet_data.json'), 'r', encoding='UTF-8'))
            saveData = data.get(petname, {})
        except Exception:
            pass
        hp = saveData.get('HP', 0)
        if hp != 'null':
            hp = max(0, int(hp) // settings.HP_INTERVAL)
        fv = saveData.get('FV', 0)
        fv_lvl = saveData.get('FV_lvl', 0)
        hpLabel = QLabel(f'{self.tr("Satiety")}: {hp}/100', self)
        hpLabel.setObjectName('saveCardStat')
        fvLabel = QLabel(f'Lv.{fv_lvl}   {self.tr("Favor")}: {fv}', self)
        fvLabel.setObjectName('saveCardStat')
        statBox.addWidget(hpLabel)
        statBox.addWidget(fvLabel)

        # 操作菜单
        menu = RoundMenu(parent=self)
        menu.addAction(self._mkAct('fa5s.download', self.tr('Load In'), self._loadinClicked))
        menu.addAction(self._mkAct('fa5s.pen', self.tr('Rewrite'), self._rewriteClicked))
        menu.addAction(self._mkAct('fa5s.trash-alt', self.tr('Delete'), self._deleteClicked))
        menu.addAction(self._mkAct('fa5s.undo', self.tr('Backtrace'), self._backtraceClicked))
        menuButton = QPushButton(self)
        menuButton.setFixedSize(30, 30)
        menuButton.setCursor(Qt.PointingHandCursor)
        c = '#FFFFFF' if isDarkTheme() else '#000000'
        if qta is not None:
            menuButton.setIcon(qta.icon('fa5s.ellipsis-v', color=c))
        menuButton.setIconSize(QSize(14, 14))
        p = active_palette()
        menuButton.setStyleSheet(
            f'QPushButton {{ border: none; border-radius: 6px; background: transparent; }}'
            f'QPushButton:hover {{ background: {p["hover"]}; }}')
        menuButton.clicked.connect(
            lambda: menu.exec(menuButton.mapToGlobal(QPoint(0, 0))))

        self._layout.addWidget(avatar, 0, Qt.AlignVCenter)
        self._layout.addLayout(textBox, 1)
        self._layout.addLayout(statBox, 2)
        self._layout.addWidget(menuButton, 0, Qt.AlignTop)

    def _mkAct(self, icon, text, slot):
        act = QAction(text, self)
        if qta is not None:
            c = '#FFFFFF' if isDarkTheme() else '#000000'
            act.setIcon(qta.icon(icon, color=c))
        act.triggered.connect(lambda: slot(self.cardIndex))
        return act

    # ---------- 状态更新 ----------
    def _registerSave(self, jsonPath):
        self.jsonPath = jsonPath
        self._clear()
        self._buildInfo()

    def _deleteSave(self):
        self.jsonPath = None
        self.cardTitle = None
        self._clear()
        self._buildEmpty()

    def _clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _saveClicked(self):
        self.saveClicked.emit(self.cardIndex)

    def _loadinClicked(self, cardIndex):
        self.loadinClicked.emit(cardIndex)

    def _rewriteClicked(self, cardIndex):
        self.rewriteClicked.emit(cardIndex)

    def _deleteClicked(self, cardIndex):
        self.deleteClicked.emit(cardIndex)

    def _backtraceClicked(self, cardIndex):
        self.backtraceClicked.emit(cardIndex)


class SaveCardGroup(QWidget):
    """存档卡组：纵向排列"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(10)
        self._addTitle(title)

    def _addTitle(self, title):
        p = active_palette()
        label = QLabel(title, self)
        label.setStyleSheet(
            f'QLabel {{ color: {p["textSecondary"]}; font: 600 13px {UI_FONT};'
            f' padding: 4px; background: transparent; }}')
        self._layout.addWidget(label)

    def addSaveCard(self, card):
        self._layout.addWidget(card)

    def addSaveCards(self, cards):
        for c in cards:
            self.addSaveCard(c)


class SaveInterface(QWidget):
    """简约存档管理页"""
    freeze_pet = Signal(name='freeze_pet')
    refresh_pet = Signal(name='refresh_pet')

    def __init__(self, sizeHintDyber, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('SaveInterface')
        self.sizeHintDyber = (sizeHintDyber[0] - 100, sizeHintDyber[1])
        self.saveCardList = []

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
        self._connectSlots()

    # ---------- 构建 ----------
    def _buildSections(self):
        p = active_palette()

        # 页面标题
        title = QLabel(self.tr('Save'), self._body)
        title.setStyleSheet(
            f'QLabel {{ color: {p["text"]}; font: 600 20px {UI_FONT};'
            f' padding: 4px; background: transparent; }}')
        self._layout.addWidget(title)

        # Save Transfer
        self._addSectionTitle(self.tr('Save Transfer'))
        docPath = QStandardPaths.locate(QStandardPaths.DocumentsLocation, '',
                                        QStandardPaths.LocateDirectory)
        exportDir = os.path.normpath(docPath + '/DyberPet/Exports')
        os.makedirs(exportDir, exist_ok=True)
        saveDir = '/DyberPet/Saves'
        self.quickSaveDir = os.path.normpath(docPath + saveDir)
        os.makedirs(self.quickSaveDir, exist_ok=True)

        self.ExportSaveCard = SettingRow('fa5s.folder-open', self.tr('Export to'),
                                         exportDir, self._body)
        exportBtn = QPushButton(self.tr('Choose folder'), self._body)
        exportBtn.setCursor(Qt.PointingHandCursor)
        exportBtn.setStyleSheet(f'''
            QPushButton {{
                border: 1px solid {p['border']}; border-radius: 6px;
                background: {p['card']}; padding: 4px 14px;
                color: {p['text']}; font: 13px {UI_FONT};
            }}
            QPushButton:hover {{ background: {p['hover']}; }}
        ''')
        exportBtn.clicked.connect(self.__onExportSaveCardClicked)
        self.ExportSaveCard.addWidget(exportBtn)
        self._layout.addWidget(self.ExportSaveCard)

        # Quick Save
        self.QuickSaveGroup = SaveCardGroup(self.tr('Quick Save'), self._body)
        for iCard in range(6):
            folder = os.path.join(self.quickSaveDir, str(iCard))
            folder = os.path.normpath(folder)
            card = None
            if os.path.exists(folder):
                allSaves = get_child_folder(folder, relative=True)
                good_saves = []
                for save in allSaves:
                    if save.startswith('broken'):
                        continue
                    if check_quicksave_folder(folder, save):
                        good_saves.append(save)
                good_saves = sorted(good_saves, key=int)
                if good_saves:
                    latest = good_saves[-1]
                    card = SaveCard(iCard, jsonPath=os.path.join(folder, latest),
                                    parent=self.QuickSaveGroup)
            if card is None:
                card = SaveCard(iCard, parent=self.QuickSaveGroup)
            self.QuickSaveGroup.addSaveCard(card)
            self.saveCardList.append(card)
        self._layout.addWidget(self.QuickSaveGroup)
        self._layout.addStretch(1)

    def _addSectionTitle(self, text):
        p = active_palette()
        label = QLabel(text, self._body)
        label.setStyleSheet(
            f'QLabel {{ color: {p["textSecondary"]}; font: 600 13px {UI_FONT};'
            f' padding: 12px 4px 4px 4px; background: transparent; }}')
        self._layout.addWidget(label)
        return label

    def _connectSlots(self):
        for i in range(len(self.saveCardList)):
            card = self.saveCardList[i]
            card.saveClicked.connect(self.__onCardSaveClicked)
            card.loadinClicked.connect(self.__onCardLoadinClicked)
            card.rewriteClicked.connect(self.__onCardSaveClicked)
            card.deleteClicked.connect(self.__onCardDeleteClicked)
            card.backtraceClicked.connect(self.__onCardBackClicked)

    # ---------- 业务逻辑（保留原有） ----------
    def __onExportSaveCardClicked(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr('Choose Export folder'),
                                                  self.ExportSaveCard.contentLabel.text())
        if not folder:
            return
        save_folder = os.path.join(folder, get_foler_name())
        os.makedirs(save_folder, exist_ok=True)
        source_folder = os.path.join(basedir, 'data')
        status_code = CopySave(source_folder, save_folder)
        status_mssg = [self.tr('Export Succeed!'),
                       self.tr('Export Failed! Please try again.'),
                       self.tr('Export Failed! Please try again.')]
        status_meth = [0, 2, 2]
        self.__showSystemNote(status_mssg[status_code], status_meth[status_code])
        self.ExportSaveCard.setContent(folder)

    def _loadin_petData(self, folder, petname):
        if not os.path.exists(os.path.join(folder, 'pet_data.json')):
            self.__showSystemNote(self.tr('File: pet_data.json not found in selected folder!'), 2)
            return
        save_dict = json.load(open(os.path.join(folder, 'pet_data.json'), 'r', encoding='UTF-8'))
        if petname == self.tr('All pets'):
            petname = 'all'
        CheckStatus = settings.pet_data.check_save_integrity(save_dict, petname)
        if not CheckStatus:
            self.__showSystemNote(self.tr('File: pet_data.json is not in compatible format!'), 2)
            return
        settings.pet_data.frozen()
        save_dict = json.load(open(os.path.join(folder, 'pet_data.json'), 'r', encoding='UTF-8'))
        TransferStatus = settings.pet_data.transfer_save(save_dict, petname)
        self.__showSystemNote(self.tr('Save imported successfully!') if TransferStatus
                              else self.tr('Failed to import save!'),
                              0 if TransferStatus else 2)
        self.refresh_pet.emit()

    def __onCardSaveClicked(self, cardIndex):
        title = self.tr('Name of the Save')
        if self.saveCardList[cardIndex].jsonPath is None:
            self.saveName = get_foler_name(filename=False)
        else:
            oldTitle = self.saveCardList[cardIndex].cardTitle
            self.saveName = (get_foler_name(filename=False)
                             if is_default_time_format(oldTitle) else oldTitle)
        from .custom_base import LineEditDialog
        w = LineEditDialog(title, self.saveName, self)
        if not w.exec():
            return
        self.saveName = w.nameLineEdit.text()

        parentFolder = os.path.join(self.quickSaveDir, str(cardIndex))
        os.makedirs(parentFolder, exist_ok=True)
        good_saves = [int(s) for s in get_child_folder(parentFolder, relative=True)
                      if s.isdigit()]
        finalFolder = os.path.join(parentFolder, str(len(good_saves)))
        os.makedirs(finalFolder)
        with open(os.path.join(finalFolder, 'info.txt'), 'w', encoding='UTF-8') as f:
            f.write(f"{settings.petname}\n{self.saveName}")
        source_folder = os.path.join(basedir, 'data')
        status_code = CopySave(source_folder, finalFolder)
        status_mssg = [self.tr('Save Succeed!'),
                       self.tr('Save Failed! Please try again.'),
                       self.tr('Save Failed! Please try again.')]
        if status_code == 0:
            try:
                self.saveCardList[cardIndex]._registerSave(finalFolder)
            except Exception:
                self.__showSystemNote(self.tr('Updating Save card failed!'), 2)
        else:
            DeleteQuickSave(finalFolder)
        self.__showSystemNote(status_mssg[status_code], [0, 2, 2][status_code])

    def __onCardLoadinClicked(self, cardIndex):
        if not self.__showMessageBox(self.tr('Load in the save?'),
                                     self.tr('Pet save data will be overwritten.')):
            return
        folder = os.path.join(self.quickSaveDir, str(cardIndex))
        folder = os.path.normpath(folder)
        savePath = None
        if os.path.exists(folder):
            allSaves = get_child_folder(folder, relative=True)
            savePath = get_latest_save(allSaves)
        if not savePath:
            self.__showSystemNote(self.tr('Error: Save folder in bad format!'), 2)
            return
        jsonPath = os.path.join(folder, savePath)
        info = open(os.path.join(jsonPath, 'info.txt'), 'r', encoding='UTF-8').readlines()
        info = [i.strip() for i in info]
        petname = info[0] if info else '?'
        self._loadin_petData(jsonPath, petname)

    def __onCardDeleteClicked(self, cardIndex):
        if not self.__showMessageBox(self.tr('Are you sure you want to delete the save?'),
                                     self.tr('All history saves in this slot will be deleted, use carefully')):
            return
        folder = os.path.join(self.quickSaveDir, str(cardIndex))
        folder = os.path.normpath(folder)
        if DeleteQuickSave(folder):
            self.__showSystemNote(self.tr('Deletion Succeed!'), 0)
        else:
            self.__showSystemNote(self.tr('Error: Deletion Failed!'), 2)
            return
        try:
            self.saveCardList[cardIndex]._deleteSave()
        except Exception:
            self.__showSystemNote(self.tr('Updating Save card failed!'), 2)

    def __onCardBackClicked(self, cardIndex):
        if not self.__showMessageBox(self.tr('Are you sure you want to backtrace the save slot?'),
                                     self.tr('It will delete the current save, and backtrace to the last one in this slot.')):
            return
        folder = os.path.join(self.quickSaveDir, str(cardIndex))
        folder = os.path.normpath(folder)
        allSaves = get_child_folder(folder, relative=True) if os.path.exists(folder) else []
        savePath = get_latest_save(allSaves)
        if not savePath:
            self.__showSystemNote(self.tr('Error: Save folder in bad format!'), 2)
            return
        jsonPath = os.path.join(folder, savePath)
        if not DeleteQuickSave(jsonPath, keep=False):
            self.__showSystemNote(self.tr('Error: Deleting current save Failed!'), 2)
            return
        self.__showSystemNote(self.tr('Save backtraced successfully!'), 0)
        try:
            remaining = get_child_folder(folder, relative=True)
            latest = get_latest_save(remaining)
            if latest:
                self.saveCardList[cardIndex]._registerSave(os.path.join(folder, latest))
            else:
                self.saveCardList[cardIndex]._deleteSave()
        except Exception:
            self.__showSystemNote(self.tr('Updating Save card failed!'), 2)

    def __showMessageBox(self, title, content):
        from qfluentwidgets import MessageBox
        msg = MessageBox(title, content, self)
        msg.yesButton.setText(self.tr('OK'))
        msg.cancelButton.setText(self.tr('Cancel'))
        return bool(msg.exec())

    def __showSystemNote(self, content, type_code):
        from qfluentwidgets import InfoBar, InfoBarPosition
        methods = [InfoBar.success, InfoBar.warning, InfoBar.error]
        methods[type_code]('', content, duration=3000,
                           position=InfoBarPosition.BOTTOM, parent=self.window())


# ============================================================
#    工具函数（保留原有）
# ============================================================

def get_foler_name(filename=True):
    current_time = datetime.now()
    return current_time.strftime('%Y-%m-%d-%H-%M-%S' if filename else '%Y-%m-%d %H:%M:%S')


def get_child_folder(parentFolder, relative=False):
    all_files_and_dirs = os.listdir(parentFolder)
    if relative:
        return [os.path.basename(d) for d in all_files_and_dirs
                if os.path.isdir(os.path.join(parentFolder, d))]
    return [d for d in all_files_and_dirs if os.path.isdir(os.path.join(parentFolder, d))]


def is_default_time_format(s):
    try:
        datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False


def check_quicksave_folder(folder, subfolder):
    try:
        int(subfolder)
    except ValueError:
        return False
    info_file = os.path.join(folder, subfolder, 'info.txt')
    data_file = os.path.join(folder, subfolder, 'pet_data.json')
    info_check, petname = check_info_file(info_file) if os.path.exists(info_file) else (False, False)
    data_check = check_data_file(data_file, petname) if (os.path.exists(data_file) and info_check) else False
    return bool(info_check and data_check)


def check_info_file(file):
    info = open(file, 'r', encoding='UTF-8').readlines()
    info = [i.strip() for i in info if i.strip()]
    return (True, info[0]) if len(info) == 2 else (False, False)


def check_data_file(file, petname):
    try:
        allData_params = json.load(open(file, 'r', encoding='UTF-8'))
        pet_data = allData_params.get(petname, {})
    except Exception:
        return False
    return all(k in pet_data for k in ('HP', 'HP_tier', 'FV', 'FV_lvl'))


def get_latest_save(allSaves):
    possible_names = {str(i) for i in range(len(allSaves))}
    good_saves = [int(save) for save in allSaves if save in possible_names]
    return str(max(good_saves)) if good_saves else None
