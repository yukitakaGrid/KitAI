import discord
from discord.ext import commands

# ボットのトークンをセット
TOKEN = 'MTE0MTY0ODQ2NjczNzYzNTM4OA.G-edaX.XC19pqWBTv8jmWixbHnuBSlhH6yMB1Rh3Tte00'

def run():
    # ボットの接続準備
    intents = discord.Intents.default()
    intents.voice_states = True  # ボイスチャンネルの情報を取得するために必要

    bot = commands.Bot(command_prefix='!', intents=intents)

    # login
    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user} : execute_combined')
        return
    ##########

    # change_edit
    @bot.event
    async def on_message(message):
        print(f"{message.author} mended {bot.user} : execute_combined")
        if message.author == bot.user:
            return 

        # Check if "make" is in the message and if the bot is mentioned
        if "!edit" in message.content and bot.user.mentioned_in(message):
            await message.channel.send('''```diff
+change edit mode!!
```''')
            await bot.close()
            return

        # This is needed to process commands if you have any
        await bot.process_commands(message)
    ##########



    bot.run(TOKEN)

    # botインスタンスへの参照を削除
    del bot

    return

run()

