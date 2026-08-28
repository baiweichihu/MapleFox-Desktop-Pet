# MapleFox 桌宠定制指南

> 本指南基于 DyberPet（呆啵宠物）v0.10.3 fork 版，说明当前项目已具备的功能，以及如何用你自己的形象替换桌宠。

## 目录
- [一、项目现状](#一项目现状)
- [二、定制决策与裁剪规划](#二定制决策与裁剪规划)
- [三、项目已有功能清单](#三项目已有功能清单)
- [四、如何更换成你自己的桌宠形象](#四如何更换成你自己的桌宠形象)
  - [4.1 你需要准备什么](#41-你需要准备什么)
  - [4.2 角色文件夹结构](#42-角色文件夹结构)
  - [4.3 分步制作流程](#43-分步制作流程)
  - [4.4 动画帧图片规范（重要）](#44-动画帧图片规范重要)
  - [4.5 桌宠参数文件 pet_conf.json](#45-桌宠参数文件-pet_confjson)
  - [4.6 动作参数文件 act_conf.json](#46-动作参数文件-act_confjson)
  - [4.7 可选增强：通知 / 气泡 / 信息 / 自带物品 / 对话](#47-可选增强通知--气泡--信息--自带物品--对话)
  - [4.8 如何测试你的形象](#48-如何测试你的形象)
- [五、增删功能时改哪里](#五增删功能时改哪里)
- [六、相关参考文档](#六相关参考文档)

---

## 一、项目现状

- 上游项目：**DyberPet（呆啵宠物）** v0.10.3，作者 ChaozhongLiu
- 技术栈：Python 3.9+ / PySide6 / PySide6-Fluent-Widgets / apscheduler / pynput
- 本仓库 fork 后尚未做定制，保留上游全部能力：
  - 桌面宠物：动画、交互、养成、任务、商店、迷你宠物
  - AI 助手（LLM 模块，上游未完全开源）
  - 模组生态：角色 / 物品 / 音效 / 迷你宠物均可自由扩展
- 当前仓库内置素材：
  - `res/role/Kitty`（默认桌宠，小猫）
  - `res/role/ChrisKitty`（圣诞限定小猫）
  - `res/role/sys`（系统角色：心形组件动画示例）
  - `res/pet/派蒙`（迷你宠物示例）
  - `res/items/Default`（默认物品模组：薯条、汉堡等）
- 运行方式：安装依赖后运行根目录 `run_DyberPet.py`（依赖安装见 `README.md` 快速体验章节）

---

## 二、定制决策与裁剪规划

> 本项目的产品定位：**面向消费者的成品桌宠，而非开发者框架**。因此移除开发者向的功能，并把个性化功能在代码层写死，打包成单一成品交付给用户。下方为定制决策总表，标注了裁剪范围与主要涉及代码位置。

### 2.0 定制决策总表

| 模块 | 决策 | 说明 |
|:---|:---:|:---|
| 2.1 召唤同伴 | 🗑️ 删除 | 产品只有一个角色，无需多宠物同屏 |
| 2.2 核心桌宠 | ✅ 保留 | 动画/交互/养成核心全部保留 |
| 2.3 迷你宠物 | 🗑️ 删除 | 删除物品系统中的迷你宠物类型及其管理系统 |
| 2.4 番茄钟 | 🗑️ 删除 | 保留"日常任务"（不在此范围） |
| 2.4 专注时间 | 🗑️ 删除 | 连带删除专注动画入口 |
| 2.4 专注状态反馈 | 🗑️ 删除 | 专注内拍拍气泡、频繁点击气泡 |
| 2.5 个性化通知 | 🗑️ 删除 | 产品仅一个角色，开发完成后无需每角色自定义 |
| 2.5 语音系统 | 🗑️ 删除 | 产品只用对话框，不要声音 |
| 2.6 角色与模组管理 | 🗑️ 删除 | 用户是消费者，无需导入/管理模组 |
| 2.7 设置与存档 | ✅ 保留 | 含每角色独立存档（产品只有一个角色，不受影响） |
| 2.8 AI 助手（大模型入口） | ✅ 保留 | 其余功能也全部保留 |

### 2.1 裁剪的联动依赖

以下功能之间存在耦合，裁剪时必须一起处理，否则会报错或残留逻辑：

1. **番茄钟 + 专注时间强耦合**：二者共用 `FocusPanel`（`DyberPet/Dashboard/dashboard_widgets.py` 第 2419 行起）、旧版独立窗口 `Focus`/`Tomato`（`DyberPet/extra_windows.py`）、状态栏图标（`DyberPet/DyberPet.py` 第 680-710 行）、`_change_time()`（第 1436-1490 行）。**必须一起删除**。
2. **专注/频繁气泡依赖 `focus_timer_on`**：`settings.focus_timer_on`（`DyberPet/settings.py`）被专注功能、专注动画（`modules.py` 第 163 行）、`pat_focus` 气泡三方共用，裁剪需同步。
3. **语音 + 个性化通知共用 `DPNote`**：两者都依赖 `DyberPet/Notification.py` 的 `DPNote` / `play_audio` / `init_note` / `sound_dict`。删除语音时，**必须保留 `DPNote` 的基础文字气泡/通知能力**（HP/FV 变化、普通提示仍需显示），只去掉声音与每角色个性化。
4. **迷你宠物 + 召唤同伴共用 `SubPet` 类**：`DyberPet/Accessory.py` 的 `SubPet` 同时服务召唤同伴（`isSubpet=False`）和迷你宠物（`isSubpet=True`），`SubPet_Manager` 仅被迷你宠物使用。删除两者后可一并精简 `SubPet` 的 `isSubpet` 分支。
5. **系统面板**：删除"角色/模组管理"时，`ControlMainWindow`（`DyberPet/DyberSettings/DyberControlPanel.py` 第 23-76 行）仍需保留 "Settings"/"Game Save" 界面，只需移除 "Characters"/"Item MOD"/"Mini-Pets" 三个子界面注册（第 45-53 行）。

### 2.2 各待删除功能的代码定位

| 待删除功能 | 主要文件与位置 |
|:---|:---|
| 召唤同伴 | `DyberPet/DyberPet.py` 第 817-821、1020、1042-1046 行（右键菜单"Call Partner"）；`DyberPet/Accessory.py` 第 95-101 行 |
| 迷你宠物 | `DyberPet/Accessory.py` 第 56、78、103-125、201-217、840-1240 行；`DyberPet/utils.py` 第 198-269 行（`SubPet_Manager`）；`DyberPet/conf.py` 第 273 行起；`DyberPet/DyberPet.py` 第 1525-1530 行（背包 subpet 物品）；`res/pet/` 目录 |
| 番茄钟 | `DyberPet/modules.py` 第 846-851、978-1132 行；`DyberPet/extra_windows.py` 第 687-950 行（`Tomato`）；`DyberPet/Dashboard/dashboard_widgets.py` 第 2419-2660 行（`FocusPanel`）；`DyberPet/DyberPet.py` 第 680-698、1444-1464、1705-1734 行 |
| 专注时间 | `DyberPet/modules.py` 第 847-849、1134-1306 行；`DyberPet/extra_windows.py` 第 952-1231 行（`Focus`）；`DyberPet/DyberPet.py` 第 700-710、1466-1490、1737-1769 行；`DyberPet/settings.py` 第 185-187 行 |
| 专注/频繁点击气泡 | `DyberPet/DyberPet.py` 第 1567-1578 行（`patpat()` 内）；`res/icons/bubble_conf.json` 第 44-57 行；`res/icons/note_icon.json` 第 80-85 行 |
| 个性化通知 | `DyberPet/Notification.py` 第 74-79、101-186 行（角色 note 合并逻辑）；`res/role/{角色}/note/` |
| 语音系统 | `DyberPet/Notification.py` 第 254-276 行（`play_audio`）、第 876-881 行（`_load_item_sound`）；`DyberPet/modules.py` 第 925-947 行（问候语音）；`DyberPet/DyberPet.py` 第 1501、1567-1577 行；`res/sounds/` |
| 角色与模组管理 | `DyberPet/DyberSettings/DyberControlPanel.py` 第 31-53 行；`DyberPet/DyberSettings/CharCardUI.py`（`CharInterface`）；`DyberPet/DyberSettings/PetCardUI.py`（`PetInterface`）；`DyberPet/DyberSettings/ItemCardUI.py`（`ItemInterface`） |

> 完整定位报告与调用链详情已确认，实际裁剪时以此为据逐项执行。

---

## 三、项目已有功能清单

### 2.1 核心桌面宠物
| 功能 | 说明 |
|:---|:---|
| 动画播放系统 | 双模块（动画模块 + 交互模块）播放 PNG 序列帧，实现 GIF 效果 |
| 自由拖拽 | 鼠标拖拽宠物，带重力下落、落地动作、反弹机制、预下落动作 `prefall` |
| 随机动作 | 按饱食度等级分级随机播放动作组（`random_act`） |
| 附件组件动作 | 额外特效图层（`accessory_act`），如技能、光环、可跟随鼠标的组件 |
| 可穿戴物品 Equip | 翅膀、披风等持续显示在角色身上的组件，随角色移动 |
| 昼夜作息系统 | 白天/夜晚切换动画池，含入睡/起床/被吵醒过渡动画 |
| 多屏支持 | 桌宠可在多个屏幕之间移动 |
| 召唤同伴 | 禁止多开进程，但可同屏召唤多个宠物 |
| 客制化光标 | 进入桌宠范围 / 拍拍 / 拖拽显示不同鼠标光标 |
| 右键菜单 | 状态栏、常驻动作选择、动作列表、召唤、设置等 |
| 落地动画 | 角色落地瞬间播放 `onfloor` 动作 |

### 2.2 养成与数值
| 功能 | 说明 |
|:---|:---|
| 饱食度 HP | 随时间下降，等级影响动作播放概率 |
| 好感度 FV | 200 级上限（每级 120 点），解锁动作与物品 |
| 等级徽章 | 星星(1级)/月亮(4级)/太阳(16级)/皇冠(64级) |
| 啵币系统 | 喂食、任务、好感升级获取；金币名称与图标可按角色自定义 |
| 摸摸/拍拍 | 点击触发拍拍动画（可按饱食度等级定义不同动作）、浮动心心、随机语音、概率掉落物品 |
| 物品喜爱度 | 角色对物品有 特别喜欢/一般/讨厌 分级，喂食触发不同动作与语音 |

### 2.3 物品与经济
| 功能 | 说明 |
|:---|:---|
| 物品系统 | 4 种类型：消耗品 / 收藏品 / 对话物品 / 迷你宠物 |
| 背包 | 可拖动交换格子的背包，分食物/收藏品栏 |
| 商店 | 购买/出售，按好感度等级解锁，支持搜索与标签筛选 |
| 物品掉落 | 单击桌宠随机掉落物品（抛物线掉落在任务栏） |
| 好感度奖励 | 升级时奖励指定物品 |
| Buff 增益系统 | 5 种增益：饱食度/好感度/啵币恢复、停止 HP/FV 下降 |
| 自动喂食 | 自动使用背包食物 |
| 对话物品 | 收藏品触发带选项的分支对话（文字游戏式） |

### 2.4 任务与生产力
| 功能 | 说明 |
|:---|:---|
| 番茄钟 | 自定义时长，倒计时、通知 |
| 专注时间 | 绑定角色 `focus` 专注动画，可暂停 |
| 提醒事项/备忘录 | 到时提醒、间隔提醒，关闭宠物后保留 |
| 日常任务 | 每日进度功能 |
| 专注状态反馈 | 专注时点击宠物出现提示气泡，过于频繁点击有警告气泡 |

### 2.5 通知与对话气泡
| 功能 | 说明 |
|:---|:---|
| 通知系统 | 弹窗通知，带图标/语音/优先级，同类通知自动合并 |
| 个性化通知 | 每个角色可自定义通知图标、语音（`note/note.json`） |
| 语音系统 | 问候语音（早安/午安/下午/晚安/深夜）、喂食语音、随机点击语音、优先级机制 |
| 对话气泡 | 9 类气泡：好感升级/好感下降/饱食度低/饱食度归零/喂食/索要食物/专注/频繁点击/随机 |
| 用户昵称系统 | 气泡文字中用 `USERTAG` 替换为用户设置的昵称 |
| 启动问候 | 启动角色时问候语迁移至对话气泡 |

### 2.6 角色与模组管理
| 功能 | 说明 |
|:---|:---|
| 角色管理面板 | 角色列表、启动按钮、角色信息卡片（封面/标签/介绍/作者信息） |
| 模组添加 | 通过系统面板自动导入角色/物品/迷你宠物模组，自动检查并提示错误 |
| 动作管理 | 动作列表播放、自定义动作、动作设计 UI |
| 迷你宠物管理 | 召唤/收回、跟随开关、大小调节（独立于主宠物） |
| 作者信息 | 角色/物品模组的作者头像、主页链接（B站/微博/抖音/GitHub/爱发电等） |

### 2.7 系统设置与存档
| 功能 | 说明 |
|:---|:---|
| 设置面板 | 语言切换（中英）、主题色、置顶、缩放、音量、静音、重力、拖拽速度 |
| 自动锁定 | 屏幕锁定状态下 HP/FV 停止变化 |
| 存档系统 | 每角色独立存档、导出/导入、快速存档、新旧存档自动转换、损坏容错 |
| 多语言 | 基于 Qt 翻译（`langs.pro`），UI 全量中英翻译 |
| 进程单开 | 防止多开导致存档混乱 |
| 更新提醒 | 软件更新检查与通知 |
| 陪伴天数 | 统计陪伴天数并显示铭牌 |

### 2.8 其他
| 功能 | 说明 |
|:---|:---|
| AI 助手 | 接入大模型陪伴聊天、待办管理（LLM 模块未完全开源） |
| 桌面收纳功能 | 隐藏到屏幕边缘 |
| 通知开关 | 可分别关闭弹窗通知、对话气泡 |

---

## 四、如何更换成你自己的桌宠形象

### 4.1 你需要准备什么

- 一套**透明背景 PNG 动作帧图**（角色各动作的逐帧图片）
- 一个文本编辑器（改 JSON）
- 无需改任何 Python 代码 —— 角色是纯"素材 + JSON 配置"驱动的

> 只要你不改变 `default / drag / fall` 等程序约定的动作名，就完全不需要碰代码。

### 4.2 角色文件夹结构

在 `res/role/` 下新建一个**英文命名**的文件夹（程序会扫描 `res/role/` 下所有文件夹作为角色列表）。参考内置 `Kitty`：

```
res/role/你的角色名/            # 英文命名，避免中文乱码
│
├── pet_conf.json               # 【必须】桌宠参数文件
├── act_conf.json               # 【必须】动作参数文件
├── action/                     # 【必须】存放所有动作帧 PNG
│   ├── stand_0.png, stand_1.png, ...
│   ├── leftwalk_0.png, ...
│   └── ...
│
├── note/                       # 【可选】个性化通知/语音/气泡
│   ├── note.json
│   ├── bubble_conf.json
│   ├── note_icon.json
│   └── *.wav / *.png
│
├── info/                       # 【可选】角色与作者信息（角色面板展示）
│   ├── info.json
│   ├── pfp.png
│   └── ...
│
├── items/                      # 【可选】角色自带物品
│   └── items_config.json
│
└── msg_conf.json               # 【可选】对话物品的分支对话内容
```

### 4.3 分步制作流程

1. **建文件夹**：在 `res/role/` 下创建英文名角色文件夹，例如 `res/role/MyFox/`。
2. **画动作帧**：把每个动作的逐帧 PNG 放进 `action/`，命名规则见 4.4。
3. **写 `act_conf.json`**：为每个动作声明图片前缀、帧数、单帧时长、是否移动、锚点等（见 4.6）。
4. **写 `pet_conf.json`**：声明画布尺寸、默认动作映射、随机动作组等（见 4.5）。
5. **（可选）补充** `note/`、`info/`、`items/`、`msg_conf.json` 个性化内容。
6. **测试**：运行 `run_DyberPet.py`，在「系统 → 角色管理」中启动新角色；或用系统的模组添加功能自动检查配置错误。
7. **（可选）替换默认角色**：若想启动就是你的角色，在「设置 → 启动默认角色」中选择它。

### 4.4 动画帧图片规范（重要）

- 每帧为**透明背景 PNG**。
- 文件名格式：`相同前缀_序号.png`，序号从 `0` 开始，如 `stand_0.png`、`stand_1.png`。
- 所有图片中**宠物的绝对大小（像素）必须一致**。
- 站立/在地面的图片，**地面必须对齐图片底部**，这样桌宠才能正确"踩"在任务栏上。
- 若某动作帧需要整体平移（例如睡觉时悬浮），用 `act_conf.json` 里的 `anchor` 参数修正，而不是改图片。

### 4.5 桌宠参数文件 pet_conf.json

参考内置 `res/role/Kitty/pet_conf.json` 与 `docs/art_dev.md` 第 99 行起的完整注释：

```jsonc
{
  "width": 98,            // 所有 PNG 的最大宽度
  "height": 98,           // 所有 PNG 的最大高度
  "scale": 1.0,           // 显示比例，影响宠物大小和移动距离

  "default": "default",   // 静息动作
  "up": "up",             // 以下为方向/事件动作映射
  "down": "down",         //   → 值必须与 act_conf.json 中的动作名一致
  "left": "left",
  "right": "right",
  "drag": "drag",         // 拖拽动作
  "prefall": "prefall",   // 鼠标松开时的下落预备动作
  "fall": "fall",         // 下落动作
  "focus": "focus",       // 专注动画（专注时间开始后播放）

  "patpat": {"0":"patpat0","1":"patpat1","2":"patpat2","3":"patpat3"},  // 拍拍动作，可按键值 0~3（饱食度等级）分别定义

  // 随机动作组：组合多个动作形成完整动画，按饱食度等级加权随机播放
  "random_act": [
    {"name": "站立", "act_list": ["default"], "act_prob": 1.0, "act_type": [2, 0]},
    {"name": "左右行走", "act_list": ["left_walk", "right_walk", "default"], "act_prob": 0.1, "act_type": [3, 1]},
    {"name": "睡觉", "act_list": ["fall_asleep", "sleep"], "act_prob": 0.05, "act_type": [0, 0]},
    // 内部保留的特殊动作名（勿占用）：
    {"name": "feed_1", "act_list": ["feed_1"], "act_prob": 0, "act_type": [0, 10000]},
    {"name": "check_item", "act_list": ["checkitem_start", "checkitem", "checkitem_end"], "act_prob": 0, "act_type": [0, 10000]},
    {"name": "onfloor", "act_list": ["onfloor"], "act_prob": 0, "act_type": [0, 10000]}
  ]
}
```

要点：
- **最少必须有 `default`、`drag`、`fall` 三个动作**；缺失的动作程序会自动用 `default` 填补（`prefall` 用 `fall` 填补）。
- `act_type` 是 `[饱食度分级, 好感度解锁等级]`；饱食度 3=活跃(hp>80)、2=正常(hp>50)、1=饥饿(hp>0)、0=饿昏(hp=0)。
- `patpat` 可按饱食度等级定义不同拍拍动作；`accessory_act` 定义特效/可穿戴组件；`item_favorite/item_dislike` 定义物品喜爱度；`coin_config` 自定义金币名称与图标。
- 完整字段表见 `docs/art_dev.md`「各项参数详情」。

### 3.6 动作参数文件 act_conf.json

参考内置 `res/role/Kitty/act_conf.json`：

```jsonc
{
  "default": {           // 动作名（对应 pet_conf.json 里的映射）
    "images": "stand",   // 帧图片前缀 → 读取 stand_0.png, stand_1.png, ...
    "act_num": 1         // 整组帧循环播放次数
  },
  "left_walk": {
    "images": "leftwalk",
    "act_num": 5,
    "need_move": true,   // 是否带动移动
    "direction": "left", // 移动方向
    "frame_move": 0.5,   // 每帧移动距离
    "frame_refresh": 0.2 // 单帧刷新间隔（秒）
  },
  "sleep": {
    "images": "sleep",
    "act_num": 5,
    "frame_refresh": 0.06,
    "anchor": [0, 36]    // 画面整体平移偏移，保证动作连贯不悬空
  }
}
```

- 其他默认参数：`frame_refresh` 默认 0.5 秒，`frame_move` 默认 10.0。
- 强烈建议所有动作的单帧时长一致，可避免自定义动作出错。
- 完整的参数表（images / act_num / need_move / direction / frame_move / frame_refresh / anchor）见 `docs/art_dev.md`。

### 4.7 可选增强：通知 / 气泡 / 信息 / 自带物品 / 对话

| 想实现 | 配置位置 | 参考文档 |
|:---|:---|:---|
| 角色专属通知图标/语音 | `note/note.json` | `docs/art_dev.md`「个性化通知系统」 |
| 自定义对话气泡 | `note/bubble_conf.json` + `note/note_icon.json` | `docs/art_dev.md`「对话气泡系统」 |
| 角色信息卡（封面/标签/作者） | `info/info.json` | `docs/art_dev.md`「桌宠及作者信息」 |
| 角色自带物品 | `items/items_config.json` | `docs/art_dev.md`「物品开发」 |
| 分支对话（对话物品） | `msg_conf.json` + `pet_conf.json` 的 `msg_dict` | `docs/art_dev.md`「对话类物品」 |
| 可穿戴外观 Equip | 物品配置 + `pet_conf.json` 的 `accessory_act`（`acc_type:"equip"`） | `docs/art_dev.md`「可穿戴物品（Equip）」 |
| 昼夜作息 | `pet_conf.json` 的 `day_night` + 夜间动画 `phase:"night"` | `docs/art_dev.md`「昼夜作息系统」 |

### 3.8 如何测试你的形象

1. 安装依赖后运行 `run_DyberPet.py`。
2. 右键桌宠 → 打开系统面板 → 「角色管理」→ 选择你的角色并启动。
3. 或使用系统内「模组添加」功能，程序会检查角色文件夹并给出潜在错误提示。
4. 逐项检查：待机 / 行走 / 拖拽 / 下落 / 落地 / 拍拍 / 睡觉 / 喂食等动作是否正常、是否错位或悬空。
5. 注意：开发过程中任何素材变更，需要重新加载角色（切换角色或重启程序）才会生效。

---

## 五、增删功能时改哪里

| 想改的功能 | 主要文件 |
|:---|:---|
| 桌宠本体（动画/交互/数值） | `DyberPet/DyberPet.py` |
| 通知系统 | `DyberPet/Notification.py` |
| 附件/组件动画 | `DyberPet/Accessory.py` |
| 系统面板（设置/角色/存档） | `DyberPet/DyberSettings/` |
| 仪表盘（状态/背包/商店/任务/动画面板） | `DyberPet/Dashboard/` |
| 全局设置与常量 | `DyberPet/settings.py`、`DyberPet/conf.py` |
| 工具函数（读 JSON 等） | `DyberPet/utils.py` |
| 程序入口 / 各模块信号连接 | `run_DyberPet.py` |
| 迷你宠物 | `res/pet/` |
| 物品/商店内容 | `res/items/` |
| 语言翻译 | `langs.pro` + `res/language`（需 `pylupdate5` / `lrelease` 重新编译） |
| 桌面图标 / 打包 | `run_DyberPet.py` 头部注释中的 pyinstaller 命令 |

> 提示：先用 Git 新建分支再动手改代码；只换形象完全不需要碰这些文件。

---

## 六、相关参考文档

- 素材开发文档（角色/物品/对话/Equip/昼夜，最详细）：[docs/art_dev.md](../docs/art_dev.md)
- 角色与模组集合：docs/collection.md
- 上游 README（功能、依赖安装、打包）：[README.md](../README.md)

---

## 七、裁剪执行进度记录

| 日期 | 内容 | 状态 |
|:---|:---|:---:|
| 2026-08-28 | 删除「召唤同伴」功能（右键菜单 Call Partner 入口 + `Accessory.py` 的 `name=='pet'` 分支） | ✅ 完成 |
| 2026-08-28 | 删除「迷你宠物」系统（`SubPet` 类、`SubPet_Manager`、背包 subpet 物品类型、`res/pet/`、`PetCardUI.py`） | ✅ 完成 |
| 2026-08-28 | 删除「番茄钟 + 专注时间 + 专注状态反馈」（`FocusPanel`、`Focus`/`Tomato` 窗口、状态栏图标、`focus_timer_on`、专注动画入口、`pat_focus`/`pat_frequent` 气泡） | ✅ 完成 |
| 2026-08-28 | 删除「日常任务」系统（`TaskPanel`/`ProgressPanel`/`TaskCard`/`EmptyTaskCard`、`taskUI.py`、`TaskData`、任务奖励常量） | ✅ 完成 |
| 2026-08-28 | 隐藏系统面板左上角返回按钮（`navigationInterface.setReturnButtonVisible(False)`） | ✅ 完成 |
| 2026-08-28 | **修复并启用「备忘录」记事本功能**：修复 `Remindme` 类引用不存在的 `RemindStyle`（改回 `TomatoStyle`），在 `PetWidget._init_ui` 实例化 `remind_window`、连接关闭信号、右键菜单加入口。只启用记事/自动保存（`data/remindme.txt`），不启用定时提醒 | ✅ 完成 |
| 2026-08-28 | 删除「个性化通知」机制：`Notification.py` 的 `init_note` 改为只读全局 `res/icons/note_icon.json`，不再加载 `res/role/<角色>/note/` 配置，`icon_dict` 去掉 `sound` 字段。保留 `DPNote` 基础文字通知/气泡 | ✅ 完成 |
| 2026-08-28 | 删除「语音系统」：删除 `play_audio`、`sound_dict`/`sound_playing`、`_load_item_sound`、`QSoundEffect`/`QMediaPlayer`/`QAudioOutput`、`BubbleText` 的 `end_audio`、`setup_bubbleText` 的 `start_audio` 处理；`res/sounds/` 目录已无代码引用。气泡/通知只显示文字 | ✅ 完成 |
| 2026-08-28 | 删除「角色与模组管理」：删除 `CharCardUI.py`/`ItemCardUI.py` 两个文件，`DyberControlPanel` 的 Characters/Item MOD 界面注册，`run_DyberPet.py` 对 `charCardInterface` 的 2 处信号连接，`langs.pro` 相关 SOURCES。系统面板只剩 **Settings / Game Save**。保留右键菜单「更换角色」 | ✅ 完成 |

| 2026-08-28 | 精简右键菜单：移除「选择动作」和「更换角色」两个菜单项（动画面板功能不受影响，独立信号链路） | ✅ 完成 |
| 2026-08-28 | 接入 MapleFox 角色：创建 `res/role/MapleFox/`（`act_conf.json` 所有动作指向单帧 `stand_0.png` + `pet_conf.json`），固定 `default_pet='MapleFox'` | ✅ 完成 |
| 2026-08-28 | 清理角色：删除 `res/role/Kitty/` 和 `res/role/ChrisKitty/`，产品只剩 MapleFox 一个角色（+ 系统组件 `sys/`，勿删） | ✅ 完成 |
| 2026-08-28 | MapleFox 尺寸治理：`stand_0.png` 压缩 2048×2048→400×400（2.1MB→103KB），`pet_conf.json` width/height 改为 400 | ✅ 完成 |
| 2026-08-28 | 新增「桌宠大小」三档设置：`BasicSettingUI.py` 用 `PetSizeCard`（下拉）替换 `ScaleCard`（滑块）。小=0.5/200px、中=0.75/300px、大=1.0/400px，切换写入 `tunable_scale`+`scale_dict` 并 emit `scale_changed` 触发实时 resize | ✅ 完成 |
| 2026-08-28 | 清理设置面板：删除「音量」「默认宠物」「帮助&问题」「二次开发」设置项；PetSize 三档选项支持中英文（`_get_pet_size_texts` 按 `language_code` 返回 小/中/大 或 Small/Medium/Large） | ✅ 完成 |
| 2026-08-28 | 游戏存档：删除「从...导入」（`ImportSaveCard`/`__onImportSaveCardClicked`），保留导出和快速存档的 Load In（共用 `_loadin_petData`，勿删） | ✅ 完成 |
| 2026-08-28 | 修复大尺寸时系统面板被桌宠盖住：`ControlMainWindow` 加 `Qt.WindowStaysOnTopHint` 置顶，`show_window` 显示时 `raise_()`+`activateWindow()` | ✅ 完成 |
| 2026-08-28 | libpng iCCP 警告已消除：压缩 stand_0.png 时 QImage 重编码 PNG 自动清除错误 iCCP；扫描 `res/` 全目录确认无 iCCP 问题 | ✅ 完成 |
| 2026-08-28 | 删除「软件更新可用」提醒：移除 `DyberPet.py` 启动更新通知、`BasicSettingUI.py` 的 `_checkUpdate`/`get_latest_version`/`compare_versions` 与 `aboutCard`、`settings.py` 的 `RELEASE_API`/`RELEASE_URL`/`UPDATE_NEEDED` | ✅ 完成 |
| 2026-08-28 | 抑制 apscheduler misfire 警告：`Scheduler_worker` 设 `apscheduler` 日志级别为 ERROR，`change_hp`/`change_fv` 加 `misfire_grace_time=None` | ✅ 完成 |
| 2026-08-28 | 修复系统面板初始尺寸过小：`ControlMainWindow.__init__` 加 `resize(800,800)`，避免首次弹出时窗口很小 | ✅ 完成 |

> 全部裁剪任务已完成。后续：重做 UI（用户计划）、补充 MapleFox 多帧动画素材。

---

*最后更新：2026-08-28 · 基于 DyberPet v0.10.3 fork 仓库整理 · 含定制决策与裁剪规划*
