import discord
from discord.ext import commands

# ボットのトークンをセット
TOKEN = 'MTE0MTY0ODQ2NjczNzYzNTM4OA.G-edaX.XC19pqWBTv8jmWixbHnuBSlhH6yMB1Rh3Tte00'

isStand = 0

def run():
    # ボットの接続準備
    intents = discord.Intents.default()
    intents.voice_states = True  # ボイスチャンネルの情報を取得するために必要

    bot = commands.Bot(command_prefix='!', intents=intents)

    # discordと接続した時に呼ばれる
    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')
        return

    @bot.event
    async def on_message(message):
        global isStand
        if(isStand==0 and bot.user.mentioned_in(message)):
            await message.channel.send('Hello! My name is KitAI. Support your Discord life☺')
            isStand = 1
        print(f"{message.author} mended {bot.user}")
        if message.author == bot.user:
            return 

        if "!edit" in message.content and bot.user.mentioned_in(message):
            await message.channel.send('''```diff
+change edit mode!!
```''')
            await bot.close()
            return

    bot.run(TOKEN)

    # botインスタンスへの参照を削除
    del bot

    return