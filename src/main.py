import sys

import discord

import approval  # noqa: F401
import logic
import openai_bot
import rules
from approval import Pending
from config import Config

def main():
    cfg = Config()
    missing = cfg.missing()
    if missing:
        sys.exit("環境変数が足りません: " + ", ".join(missing))
    store = rules.RuleStore(cfg.rules_path)
    maker = openai_bot.RuleMaker(cfg)
    state = {"edit": False, "pending": Pending()}
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    no_mentions = discord.AllowedMentions.none()  # 返信で @everyone 等を飛ばさない

    @client.event
    async def on_message(message):
        roles = [r.id for r in getattr(message.author, "roles", [])]
        msg = {"author_id": message.author.id, "role_ids": roles,
               "channel_id": message.channel.id, "content": message.content,
               "mentioned": client.user.mentioned_in(message),
               "is_bot": message.author.bot}
        for act in logic.handle(msg, state, cfg, store, maker):
            if act[0] == "send":
                await message.channel.send(act[1], allowed_mentions=no_mentions)
            else:
                await message.delete()

    client.run(cfg.discord_token)

if __name__ == "__main__":
    main()
