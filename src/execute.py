import discord
from discord.ext import commands

# ボットのトークンをセット
TOKEN = 'MTE0MTY0ODQ2NjczNzYzNTM4OA.GsPWoV.DDtudM0sdfNe-JlUOa5eaEm_zDE1DNRdKL1OjQ'

isStand = 0

def run(e):
    # ボットの接続準備
    intents = discord.Intents.default()
    intents.voice_states = True  # ボイスチャンネルの情報を取得するために必要

    bot = commands.Bot(command_prefix='!', intents=intents)

    # discordと接続した時に呼ばれる
    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user} : execute')
        return

    @bot.event
    async def on_message(message):
        global isStand
        if(isStand==0 and bot.user.mentioned_in(message)):
            await message.channel.send('Hello! My name is KitAI. Support your Discord life☺')
            isStand = 1
        elif(e==-1):
            await message.channel.send('Some error occurred, so I switched to emergency command mode. Check the console for details.')
        print(f"{message.author} mended {bot.user} : execute")
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
    bot = None

    return