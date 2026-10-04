"""承認。固定の承認者だけが、依頼ごとに紐づいた保留を、完全一致の Yes/No で決める。"""
import json
import os
import tempfile
import time

import rules

YES = {"yes", "y", "はい"}
NO = {"no", "n", "いいえ"}
TTL_SECONDS = 300

def is_approver(user_id, role_ids, cfg):
    return user_id in cfg.approver_user_ids or bool(set(role_ids) & cfg.approver_role_ids)

class Pending:
    def __init__(self, clock=time.time, path=None):
        """path を渡すと保留をファイルに残し、再起動後も（期限内なら）引き継ぐ。"""
        self._clock = clock
        self._path = path
        self._items = {}  # channel_id -> (requester_id, rule, expires)
        self._load()

    def _load(self):
        if not self._path or not os.path.exists(self._path):
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                raw = json.load(f)
            now = self._clock()
            for ch, (req, rule, exp) in raw.items():
                if exp >= now:  # 保留中のルールも読み込み時に再検査する
                    self._items[int(ch)] = (int(req), rules.validate_rule(rule), float(exp))
        except (OSError, ValueError, TypeError):
            self._items = {}  # 壊れていたら保留は全部捨てる（承認は取り直せる）

    def _save(self):
        if not self._path:
            return
        data = {str(ch): [req, rule, exp] for ch, (req, rule, exp) in self._items.items()}
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(self._path)))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, self._path)

    def put(self, channel_id, requester_id, rule):
        self._items[channel_id] = (requester_id, rule, self._clock() + TTL_SECONDS)
        self._save()

    def has(self, channel_id):
        it = self._items.get(channel_id)
        if it and it[2] < self._clock():
            del self._items[channel_id]
            self._save()
            return False
        return it is not None

    def decide(self, channel_id, text, user_id, role_ids, cfg):
        """('approved', rule) / ('rejected', None) / ('denied', None) / ('ignored', None)"""
        if not self.has(channel_id):
            return "ignored", None
        word = text.strip().lower()
        if word not in YES and word not in NO:
            return "ignored", None
        if not is_approver(user_id, role_ids, cfg):
            return "denied", None
        _, rule, _ = self._items.pop(channel_id)
        self._save()
        return ("approved", rule) if word in YES else ("rejected", None)
