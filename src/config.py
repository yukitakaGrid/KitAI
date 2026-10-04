"""設定は環境変数から読む。値そのものをソースやログに出さない。"""
import os

def _ids(name):
    raw = os.environ.get(name, "")
    return frozenset(int(x) for x in raw.replace(" ", "").split(",") if x.isdigit())

class Config:
    def __init__(self, env=None):
        if env is not None:  # 試験用
            old, os.environ = os.environ, env
        try:
            self.discord_token = os.environ.get("DISCORD_TOKEN", "")
            self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
            self.openai_org = os.environ.get("OPENAI_ORG_ID") or None
            self.openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            self.approver_user_ids = _ids("APPROVER_USER_IDS")
            self.approver_role_ids = _ids("APPROVER_ROLE_IDS")
            self.rules_path = os.environ.get("KITAI_RULES_PATH", "rules.json")
            self.pending_path = os.environ.get("KITAI_PENDING_PATH", "pending.json")
        finally:
            if env is not None:
                os.environ = old

    def missing(self):
        out = [n for n, v in (("DISCORD_TOKEN", self.discord_token),
                              ("OPENAI_API_KEY", self.openai_api_key)) if not v]
        if not (self.approver_user_ids or self.approver_role_ids):
            out.append("APPROVER_USER_IDS または APPROVER_ROLE_IDS")
        return out
