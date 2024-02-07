import discord
from discord.ext import commands

# ボットのトークンをセット
TOKEN = 'あなたのトークンを入力してください'

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
        channel = bot.get_channel(message.channel.id)
        message = await channel.fetch_message(message.id)
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
    ##########


    
    

        #on_message
        if "お前" in message.content:
            await message.delete()
            warning_msg = f"{message.author.mention} その言葉遣いは適切ではありません。"
            await message.channel.send(warning_msg)
        return
    

    bot.run(TOKEN)

    # botインスタンスへの参照を削除
    del bot

    return

run()

