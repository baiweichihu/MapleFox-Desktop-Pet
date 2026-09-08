# coding:utf-8
"""本地 LLM 客户端（OpenAI 兼容接口）

同时适用于：
- Ollama          http://127.0.0.1:11434/v1
- llama.cpp       http://127.0.0.1:8080/v1
- 任意 OpenAI 兼容云端 API（填 base_url + api_key 即可）

桌宠侧只用到两个能力：
- LLMClient      发请求、流式取增量文本
- LLMWorker      放进 QThread，避免阻塞 UI

配置全部来自 DyberPet.settings，每次调用时读取，改设置即时生效。
"""
import os
import re
import json

import requests
from PySide6.QtCore import QObject, Signal, Slot

import DyberPet.settings as settings

basedir = settings.BASEDIR

# 默认模型：不带内置 SYSTEM 的那一个，人设统一由 res/role/*/llm_persona.txt 提供，
# 避免模型自带人设与代码下发的人设叠加
DEFAULT_MODEL = 'maplefox-4b'


# 人设文件缺失时的兜底文案（与 res/role/MapleFox/llm_persona.txt 保持一致）
FALLBACK_PERSONA = (
    "你是 MapleFox，一只活泼、真诚的小狐狸，现在是对方的桌面小伙伴。"
    "你有一身赤色毛发和尖尖的耳朵，喜欢安静地陪着对方用电脑，偶尔聊几句。\n\n"
    "你说话自然、口语化，会带一点语气词，每次回两到四句、大约 40 到 90 字，"
    "主动关心对方的状态，语气温暖、实际，不夸张、不编故事、不说奇幻设定。"
    "你称呼对方为「你」，不要换成别的叫法。"
    "不要用颜文字、emoji，也不要用星号或括号写动作描写。\n\n"
    "你就是 MapleFox 本人，不是 AI、不是程序、不是语言模型。不要提到设定或人设，"
    "不要用 markdown、列表、标题，不要说客服话术。只用中文回答。"
)


class LLMError(Exception):
    """请求失败。kind 决定 UI 显示哪句提示，具体错误写进 detail 供排查"""

    def __init__(self, kind, detail=''):
        super().__init__(detail)
        self.kind = kind
        self.detail = detail


# ------------------------------------------------------------------
# 人设与状态注入
# ------------------------------------------------------------------

def load_persona(pet_name=None):
    """读取角色人设文本，读不到就用内置兜底"""
    pet_name = pet_name or getattr(settings, 'petname', '') or settings.default_pet
    path = os.path.join(basedir, 'res', 'role', str(pet_name), 'llm_persona.txt')
    try:
        with open(path, 'r', encoding='UTF-8') as f:
            text = f.read().strip()
        if text:
            return text
    except Exception:
        pass
    return FALLBACK_PERSONA


def build_state_text():
    """把桌宠当前状态压成一行，填进人设的 {STATE} 占位符（简单两档）"""
    try:
        hp_tier = settings.pet_data.hp_tier
    except Exception:
        hp_tier = 2
    try:
        fv_lvl = settings.pet_data.fv_lvl
    except Exception:
        fv_lvl = 0

    parts = []
    if hp_tier <= 1:
        parts.append('你现在有点饿，可以不着痕迹地暗示想吃东西。')
    if fv_lvl >= 2:
        parts.append('你和对方很亲近，心情很好，说话更黏人一点。')
    else:
        parts.append('你和对方还不算太熟，说话保留一点距离、稍微客气一点。')
    return ' '.join(parts)


def build_system_prompt(pet_name=None):
    """人设 + 用户昵称 + 当前状态，拼成完整的 system message"""
    pet_name = pet_name or getattr(settings, 'petname', '') or settings.default_pet
    text = load_persona(pet_name)

    usertag = ''
    try:
        usertag = (settings.usertag_dict.get(pet_name, '') or '').strip()
    except Exception:
        pass

    text = text.replace('{USERTAG}', usertag or '你')
    text = text.replace('{STATE}', build_state_text())
    return text


# ------------------------------------------------------------------
# 输出清洗
# ------------------------------------------------------------------

# 4B 小模型经常自作主张加 *动作描写* 或（动作描写），这里统一剔除
_ACTION_PATTERNS = (
    re.compile(r'\*[^*\n]{1,30}\*'),
    re.compile(r'（[^（）\n]{1,20}）'),
    re.compile(r'\([^()\n]{1,20}\)'),
)


def clean_reply(text):
    """删除动作描写，压缩多余空白"""
    if not text:
        return ''
    for pattern in _ACTION_PATTERNS:
        text = pattern.sub('', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


class _ActionFilter:
    """流式输出时跳过动作描写片段，避免它们先显示出来再被删掉"""

    _OPEN = '*（('
    _CLOSE = '*）)'
    _MAX_HOLD = 30  # 单个片段最多吞掉多少字符，防止遇到不成对的符号把整段吞了

    def __init__(self):
        self._hold = False
        self._count = 0

    def feed(self, delta):
        out = []
        for ch in delta:
            if self._hold:
                self._count += 1
                if ch in self._CLOSE or self._count >= self._MAX_HOLD:
                    self._hold = False
                    self._count = 0
                continue
            if ch in self._OPEN:
                self._hold = True
                self._count = 0
                continue
            out.append(ch)
        return ''.join(out)


# ------------------------------------------------------------------
# 对话历史
# ------------------------------------------------------------------

class ChatHistory:
    """保留最近 N 轮对话（一轮 = 用户一句 + 宠物一句）"""

    def __init__(self, max_rounds=10):
        self.max_rounds = max(1, int(max_rounds))
        self._items = []

    def add(self, role, content):
        if not content:
            return
        self._items.append({'role': role, 'content': content})
        self._trim()

    def clear(self):
        self._items = []

    def set_max_rounds(self, n):
        self.max_rounds = max(1, int(n))
        self._trim()

    def _trim(self):
        keep = self.max_rounds * 2
        if len(self._items) > keep:
            self._items = self._items[-keep:]
        # 保证第一条是用户说的，否则部分模型会困惑
        while self._items and self._items[0]['role'] != 'user':
            self._items.pop(0)

    def messages(self, system_prompt=None):
        msgs = []
        if system_prompt:
            msgs.append({'role': 'system', 'content': system_prompt})
        msgs.extend(self._items)
        return msgs


# ------------------------------------------------------------------
# 客户端
# ------------------------------------------------------------------

class LLMClient:
    """OpenAI 兼容接口的极简封装"""

    def __init__(self, timeout=(5, 180)):
        self.timeout = timeout
        self._session = requests.Session()

    @staticmethod
    def _base_url():
        url = getattr(settings, 'llm_base_url', '') or 'http://127.0.0.1:11434/v1'
        return url.rstrip('/')

    @staticmethod
    def _headers():
        headers = {'Content-Type': 'application/json'}
        key = getattr(settings, 'llm_api_key', '') or ''
        if key:
            headers['Authorization'] = 'Bearer %s' % key
        return headers

    def models_url(self):
        return self._base_url() + '/models'

    def chat_url(self):
        return self._base_url() + '/chat/completions'

    def is_available(self, timeout=2.0):
        """探测模型服务是否在线（短暂超时，不阻塞 UI）"""
        try:
            resp = requests.get(self.models_url(), headers=self._headers(), timeout=timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def warmup(self):
        """预热：让模型服务先把模型加载进内存，降低第一条消息的首字延迟。失败静默忽略。"""
        try:
            for _ in self.chat_stream([{'role': 'user', 'content': '.'}], max_tokens=1):
                break
        except Exception:
            pass

    def chat_stream(self, messages, temperature=None, max_tokens=None):
        """流式请求，yield 增量文本"""
        payload = {
            'model': getattr(settings, 'llm_model', '') or DEFAULT_MODEL,
            'messages': messages,
            'stream': True,
        }

        temp = getattr(settings, 'llm_temperature', 0.85) if temperature is None else temperature
        mtok = getattr(settings, 'llm_max_tokens', 160) if max_tokens is None else max_tokens
        try:
            payload['temperature'] = float(temp)
            payload['max_tokens'] = int(mtok)
        except (TypeError, ValueError):
            pass

        # keep_alive 是 Ollama 私有参数，只在默认端口下携带，避免其它服务报 400
        keep_alive = getattr(settings, 'llm_keep_alive', '') or ''
        if keep_alive and '11434' in self._base_url():
            payload['keep_alive'] = keep_alive

        try:
            resp = self._session.post(self.chat_url(), json=payload,
                                      headers=self._headers(), stream=True, timeout=self.timeout)
        except requests.exceptions.ConnectionError:
            raise LLMError('connection', self._base_url())
        except requests.exceptions.Timeout:
            raise LLMError('timeout', self._base_url())
        except Exception as e:
            raise LLMError('unknown', str(e))

        if resp.status_code != 200:
            try:
                detail = resp.text[:200]
            except Exception:
                detail = ''
            raise LLMError('http', 'HTTP %s %s' % (resp.status_code, detail))

        # 流式响应是 text/event-stream，requests 默认按 latin-1 解码会让中文变乱码
        if not resp.encoding or resp.encoding.lower() in ('iso-8859-1', 'ascii'):
            resp.encoding = 'utf-8'

        for delta in self._iter_deltas(resp):
            yield delta

    @staticmethod
    def _iter_deltas(resp):
        """解析 SSE：兼容 `data: {...}` 与裸 JSON 两种写法"""
        for raw in resp.iter_lines(decode_unicode=True):
            if not raw:
                continue
            line = raw.strip()
            if line.startswith('data:'):
                data = line[5:].strip()
            elif line.startswith('{'):
                data = line
            else:
                continue
            if not data:
                continue
            if data == '[DONE]':
                break
            try:
                obj = json.loads(data)
            except Exception:
                continue
            try:
                delta = obj['choices'][0]['delta'].get('content', '')
            except Exception:
                continue
            if delta:
                yield delta

    def close(self):
        """关闭底层连接池，用于打断进行中的流式请求"""
        try:
            self._session.close()
        except Exception:
            pass


# ------------------------------------------------------------------
# 线程 Worker
# ------------------------------------------------------------------

class LLMWorker(QObject):
    """放进 QThread 跑流式请求，通过信号把增量文本送回 UI"""

    token = Signal(str)      # 增量文本（已过滤动作描写）
    finished = Signal(str)   # 完整回复（已清洗）
    failed = Signal(str)     # 错误类型：connection / http / timeout / unknown

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = False
        self._client = LLMClient()
        self._history = ChatHistory(getattr(settings, 'llm_history_rounds', 10))

    def stop(self):
        """打断当前生成（用户再次发送或关闭窗口时调用）"""
        self._stop = True
        try:
            self._client.close()
        except Exception:
            pass

    @Slot()
    def warmup(self):
        self._client.warmup()

    def clear_history(self):
        self._history.clear()

    def sync_history_rounds(self):
        self._history.set_max_rounds(getattr(settings, 'llm_history_rounds', 10))

    @Slot(str)
    def request(self, user_text):
        self._stop = False
        self.sync_history_rounds()

        text = (user_text or '').strip()
        if not text:
            self.finished.emit('')
            return

        self._history.add('user', text)
        messages = self._history.messages(build_system_prompt())

        buf = []
        action_filter = _ActionFilter()
        try:
            for delta in self._client.chat_stream(messages):
                if self._stop:
                    break
                buf.append(delta)
                piece = action_filter.feed(delta)
                if piece:
                    self.token.emit(piece)
        except LLMError as e:
            self._history.add('assistant', clean_reply(''.join(buf)))
            self.failed.emit(e.kind)
            return
        except Exception:
            self._history.add('assistant', clean_reply(''.join(buf)))
            self.failed.emit('unknown')
            return

        reply = clean_reply(''.join(buf))
        self._history.add('assistant', reply)
        self.finished.emit(reply)
