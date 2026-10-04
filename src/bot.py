"""Discord との橋渡し。discord.py の型に依存せず（message と許可設定は渡される）、試験できる。"""
import logic
import rules
from approval import Pending
from ratelimit import RateLimiter

def build_state(cfg):
    return {"edit": False, "pending": Pending(path=cfg.pending_path),
            "ai_limiter": RateLimiter(3, 60),      # 1人あたり1分3回まで AI を呼ぶ
            "rule_limiter": RateLimiter(5, 60)}    # 1チャンネルあたり1分5回までルールが動く

def to_msg(message, bot_user):
    roles = [r.id for r in getattr(message.author, "roles", [])]
    return {"author_id": message.author.id, "role_ids": roles,
            "channel_id": message.channel.id, "content": message.content,
            "mentioned": bot_user.mentioned_in(message),
            "is_bot": message.author.bot}

async def process(message, bot_user, state, cfg, store, maker, no_mentions):
    for act in logic.handle(to_msg(message, bot_user), state, cfg, store, maker):
        try:
            if act[0] == "send":
                await message.channel.send(act[1], allowed_mentions=no_mentions)
            else:
                await message.delete()
        except Exception as e:  # 権限不足などで落とさない。詳細は型名だけ記録
            print("discord action failed:", type(e).__name__)
