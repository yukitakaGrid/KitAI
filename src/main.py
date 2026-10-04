import sys

import discord

import bot
import openai_bot
import rules
from config import Config

def main():
    cfg = Config()
    missing = cfg.missing()
    if missing:
        sys.exit("環境変数が足りません: " + ", ".join(missing))
    store = rules.RuleStore(cfg.rules_path)
    maker = openai_bot.RuleMaker(cfg)
    state = bot.build_state(cfg)
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    no_mentions = discord.AllowedMentions.none()  # 返信で @everyone 等を飛ばさない

    @client.event
    async def on_message(message):
        await bot.process(message, client.user, state, cfg, store, maker, no_mentions)

    client.run(cfg.discord_token)

if __name__ == "__main__":
    main()
