# MapleFox 功能入口重构方案

> 状态：方案已定，待开工
> 日期：2026-08-30（首版） / 2026-08-30（修订）
> 所属：P1-4 UI 重做的前置架构设计（先定入口，再动表现层）

---

## 1. 目标与原则

1. **右键菜单极简**：基础信息（MapleFox、等级、好感度、饱食度）+ 3 个大类 + 退出。
2. **设置与互动分离**：入口命名清晰直白，去掉「系统」「角色面板」等模糊叫法。
3. **为 LLM 对话预留位置**（P1-1 尚未接入，先置灰）。
4. **备忘录与提醒拆分为两个独立功能**，均归入互动类。
5. **只有 MapleFox 一个角色，不做「更换角色」**。
6. **所有现有功能保持不变**，只调整入口、命名与层级；提醒为重新实现。

---

## 2. 现状分析

### 2.1 当前右键菜单（`DyberPet.py` → `PetWidget._set_Statusmenu`）

```
MapleFox（Fed for X days）   ← 宠物名 + 喂养天数
Level ★                      ← 等级徽章
Satiety █████                ← 饱食度条
Favor ██████                 ← 好感度条
────────────────────────────
Dashboard                    ← 仪表盘（状态/背包/商店/动画）
System                       ← 系统设置（设置/存档管理）
Memo                         ← 备忘录（含失效的提醒设置区）
────────────────────────────
Exit
```

### 2.2 现有功能窗口清单

| 窗口 | 导航页面 | 功能 | 文件 |
|:---|:---|:---|:---|
| **仪表盘 Dashboard** | 状态 Status | 角色数值、Buff、用户昵称、状态日志 | `Dashboard/statusUI.py` |
| | 背包 Backpack | 物品使用/佩戴/卖出（食物/收藏品） | `Dashboard/inventoryUI.py` |
| | 商店 Shop | 买/卖物品、搜索、筛选 | `Dashboard/shopUI.py` |
| | 动画 Animation | 动作播放列表、自定义动作、动作设计器 | `Dashboard/animationUI.py` |
| **控制面板 System** | 设置 Settings | 置顶/下落/重力/拖拽/音量/气泡/自动锁定/宠物大小/语言/主题色 | `DyberSettings/BasicSettingUI.py` |
| | 存档管理 Game Save | 存档槽位读写/回溯/删除、导出导入 | `DyberSettings/GameSaveUI.py` |
| **备忘录 Memo** | — | 见 2.3 | `extra_windows.py → Remindme` |

> 其他功能入口：配件对话 `DPDialogue`、对话气泡 `bubbleManager`、通知 `QToaster` 均为**被动触发**，无需菜单入口。

### 2.3 备忘录窗口现状（`Remindme`，`extra_windows.py:688`）

当前是一个**左右合并窗口**：
- **左侧**：提醒设置区（延时提醒 / 定时提醒 / 间隔重复提醒 三个单选 + 文本输入 + 确认），确认后把「时间 - 文本」追加进右侧文本。
- **右侧**：备忘录文本框 `e2`（`QTextEdit`），内容自动保存到 `data/remindme.txt`，下次打开自动加载。

**⚠️ 关键事实：提醒调度代码已全部失效**
- `modules.py` 的 `add_remind` / `run_remind` 被注释（v0.3.7 起删除）；
- `DyberPet.py` 的 `run_remind`、`remind_window.initial_task()` 被注释；
- `confirm_remind` 信号**无任何连接**。

结论：当前「提醒」只往备忘录里追加文字，**到点不会真正弹提醒**。本次拆分后「提醒」实为**重新实现**的新功能。

### 2.4 现状问题

- 「System」语义模糊；仪表盘与「角色面板」概念重叠。
- 备忘录与设置、仪表盘平级，层级不合理。
- **LLM 对话无入口**；「更换角色」确定不做。
- 备忘录窗口塞入了失效的提醒设置区，职责混杂。
- 「更换角色」「选择动作」子菜单已构建但被注释（`_set_menu`），重构时可一并清理（P2-1）。

---

## 3. 新菜单结构（已确认：养成 - 互动 + 设置单按钮）

```
MapleFox · 等级 ★ · 饱食度 ███ · 好感度 ███   ← 基础信息（只读）
────────────────────────────────────────────
▶ 养成
    ├─ 状态
    ├─ 背包
    └─ 商店
▶ 互动
    ├─ 对话            ← LLM，预留（置灰）
    ├─ 备忘录          ← 纯文本框
    └─ 提醒            ← 多实例（事项 + 日期时间）
────────────────────────────────────────────
设置                            ← 单按钮，打开设置窗口
────────────────────────────────────────────
退出
```

- **养成 / 互动** 两个大类用 `RoundMenu` 子菜单实现，功能项点击直达对应窗口/页面。
- **设置是单按钮**（非大类）：点击打开设置窗口，窗口内含「设置 / 存档管理 / 动画」三个页面，通过左侧导航访问。
- 对话项**置灰**（`Action.setEnabled(False)`），P1-1 接入后直接挂接，不动菜单结构。
- 变更记录（2026-08-30）：「动画」从养成移入设置窗口（属桌宠行为配置）；「设置」由大类改为单按钮。

---

## 4. 功能映射

| 新大类 | 功能项 | 来源/实现 | 说明 |
|:---|:---|:---|:---|
| **养成** | 状态 | 仪表盘 Status 页 | 打开仪表盘并切换状态页 |
| | 背包 | 仪表盘 Backpack 页 | 打开仪表盘并切换背包页 |
| | 商店 | 仪表盘 Shop 页 | 打开仪表盘并切换商店页 |
| | 动画 | 仪表盘 Animation 页 | 打开仪表盘并切换动画页 |
| **互动** | 对话 | 预留 | 置灰，P1-1 后挂接 |
| | 备忘录 | 新独立窗口（拆分自 Remindme 右侧） | 纯文本框 + 自动保存 |
| | 提醒 | 新窗口（重新实现） | 多实例：事项 + 日期时间，到点通知 |
| **设置** | 设置 | 控制面板 Settings 页 | 原样保留 |
| | 存档管理 | 控制面板 Game Save 页 | 原样保留 |

---

## 5. 命名对照

| 位置 | 旧 | 新 | 说明 |
|:---|:---|:---|:---|
| 右键菜单项 | Dashboard | 删除，改为「养成」子菜单 | — |
| 右键菜单项 | System | 删除，改为「设置」子菜单 | — |
| 右键菜单项 | Memo | 删除，改为「互动」子菜单下的「备忘录」「提醒」 | — |
| 控制面板窗口标题 | System | **设置** | `ControlMainWindow.initWindow` |
| 仪表盘窗口标题 | Dashboard | **养成** | `DashboardMainWindow.initWindow` |
| 右键菜单大类 | — | 养成 / 互动 / 设置 | 新增 |

---

## 6. LLM 对话预留

- 位置：互动类第一项，文案「对话」，图标沿用 `Dialogue_icon.png`。
- 实现：置灰（`Action.setEnabled(False)`）。
- P1-1 完成后把该 Action 的 `triggered` 挂接到对话窗口，菜单结构不变。

---

## 7. 备忘录与提醒拆分设计

### 7.1 备忘录（Memo）

- **形态**：独立小窗口，一个多行文本框（`QTextEdit`）+ 关闭按钮。
- **行为**：纯文本自动保存，打开自动加载（沿用现有 `data/remindme.txt` 读写逻辑）。
- **改动**：从 `Remindme` 右侧拆出，去掉左侧提醒设置区；改名为独立类（如 `MemoWindow`）。

### 7.2 提醒（Reminder）

- **形态**：独立窗口，竖向列表展示多个提醒实例；每个实例 = **事项文本框** + **日期时间选择器**（`QDateTimeEdit`）+ 删除按钮；窗口顶部「新增」按钮可无限添加。
- **数据**：存储为 `data/reminders.json`（数组：`[{id, text, datetime}]`），增删改即时保存。
- **调度**：到点触发通知。
  - 推荐：复用现有 `Scheduler_worker` 的 QtScheduler，为每个提醒注册 `date.DateTrigger`；或启动一个常驻 `QTimer` 每秒轮询最近到期提醒。二选一，实现时定。
  - 触发表现：复用 `QToaster` 弹窗通知（比旧 `show_dialogue` 更符合当前通知体系）。
- **历史提醒**：到点后可保留在列表并标记「已触发」，或自动移除（实现时定，倾向保留直至用户删除）。
- **改动**：新建 `ReminderWindow` 类；`Remindme` 删除；新增调度注册/轮询逻辑。

---

## 8. 实现要点

1. **切页能力**：`DashboardMainWindow` 增加 `switch_to(page_name)`（`navigationInterface.setCurrentWidget(...)`），控制面板同理，使菜单项能直达指定页。
2. **子菜单构建**：复用 `_build_act` 为每个大类建 `RoundMenu`，`StatMenu.addMenu(...)` 挂接。
3. **菜单精简**：`_set_Statusmenu` 三大类 + 退出，移除 Dashboard/System/Memo 平级项。
4. **窗口标题**：按第 5 节命名对照表修改。
5. **多语言**：新文案全部走英文源串 `self.tr(...)`，补三语言翻译（遵循 P2-2 约定）。
6. **死代码清理**：`_set_menu` 被注释的 `act_menu`/`change_menu`、`DyberPet.py` 被注释的 `run_remind`、`initial_task` 调用、`confirm_remind` 信号定义随重构移除（P2-1 部分）。

---

## 9. 实施步骤

1. **入口重构**：
   - 右键菜单三大类子菜单
   - 窗口标题改名
   - 仪表盘/控制面板 `switch_to`
   - 清理死代码
2. **备忘录拆分**：独立纯文本框窗口。
3. **提醒重做**：多实例窗口 + 数据存储 + 到点调度 + 通知触发。
4. **表现层重做**（P1-4 主体）：定设计规范（色板/字体/圆角/阴影 token），逐界面重做。
5. **LLM 接入**（P1-1，独立任务）：挂接「对话」入口。

---

## 10. 已确认决策记录

| # | 决策 | 确认时间 |
|:---|:---|:---|
| 1 | 三大类，顺序：养成 → 互动 → 设置 | 2026-08-30 |
| 2 | 「养成」命名可用 | 2026-08-30 |
| 3 | 单一角色 MapleFox，不做更换角色 | 2026-08-30 |
| 4 | 对话预留态：置灰 | 2026-08-30 |
| 5 | 备忘录=纯文本框；提醒=多实例（事项+日期时间） | 2026-08-30 |
| 6 | 备忘录图标沿用 `Dialogue_icon.png` | 2026-08-30 |

---

## 11. 设计规范（简洁风格，2026-08-30 定稿）

| Token | 值 | 说明 |
|:---|:---|:---|
| 主色 | 跟随 `settings.themeColor`（默认 `#009faa`） | 选中态 / 焦点 / 进度 / 强调 |
| 主文本 | `#333333` | 标题、正文 |
| 次文本 | `#8a8a8a` | 辅助说明 |
| 页面背景 | qfluentwidgets 默认浅色 | 窗口背景由 Fluent 主题控制 |
| 卡片 | 纯白（`rgba(255,255,255,235)` 级）+ `1px rgba(0,0,0,25)` 边框 | 备忘录/提醒/通知/气泡 |
| 卡片圆角 | **8px** | `SimpleCardWidget`、通知、气泡 |
| 弹窗圆角 | 12px | 备忘录/提醒窗口 |
| 按钮/输入框圆角 | 6px | — |
| 标题字号 | **28px semibold** | 设置页 / 仪表盘各页 `panelLabel` |
| 页面内边距 | 左右 60px（qfluentwidgets 默认） | — |
| 分组间距 | 28px（qfluentwidgets 默认） | — |
| 字体 | `'Segoe UI', 'Microsoft YaHei UI', 'PingFang SC'` | 全局统一 |

**落地清单**：
- `res/icons/system/qss/light/setting_interface.qss`：设置页标题 28px semibold
- `res/icons/Dashboard/qss/light/status_interface.qss`：仪表盘 4 页共用标题 28px semibold
- `Dashboard/dashboard_widgets.py`：`StatusCard` / `ShopItemWidget` / `filterView` / `ActionCard` 圆角 5→8px
- `Notification.py`：`DyberToaster` / `BubbleText` 边框柔化 `rgba(0,0,0,25)`、背景不透明度 245
- `extra_windows.py`：`MemoWindow` / `ReminderWindow` 简洁白卡 + 中性关闭按钮（新增 `CloseButtonStyle`）
