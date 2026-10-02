"""承認。固定の承認者だけが、依頼ごとに紐づいた保留を、完全一致の Yes/No で決める。"""
import time

YES = {"yes", "y", "はい"}
NO = {"no", "n", "いいえ"}
TTL_SECONDS = 300

def is_approver(user_id, role_ids, cfg):
    return user_id in cfg.approver_user_ids or bool(set(role_ids) & cfg.approver_role_ids)

class Pending:
    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self._items = {}  # channel_id -> (requester_id, rule, expires)

    def put(self, channel_id, requester_id, rule):
        self._items[channel_id] = (requester_id, rule, self._clock() + TTL_SECONDS)

    def has(self, channel_id):
        it = self._items.get(channel_id)
        if it and it[2] < self._clock():
            del self._items[channel_id]
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
        return ("approved", rule) if word in YES else ("rejected", None)
