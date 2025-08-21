import discord
from discord.ext import commands

# Discord botトークン（実際の使用時は有効なトークンに置き換える）
TOKEN = 'あなたのトークンを入力してください'

# 初回起動フラグ（挨拶メッセージの重複防止）
isStand = 0

def run(e):
    """
    コマンドモード（基本機能モード）のメイン実行関数
    
    Args:
        e (int): エラー状態フラグ (-1: 緊急モード, 0: 通常モード)
    """
    # Discord bot の基本設定
    intents = discord.Intents.default()
    intents.voice_states = True  # ボイスチャンネルの情報を取得するために必要

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        """Bot起動完了時の処理"""
        print(discord.__version__)
        print(f'We have logged in as {bot.user} : execute')
        return

    @bot.event
    async def on_message(message):
        """
        メッセージ受信時の処理
        - 初回メンション時の挨拶
        - 編集モードへの切り替え（!editコマンド）
        - 基本的な単語フィルター機能
        """
        global isStand
        
        # 初回メンション時の挨拶（1回のみ）
        if(isStand==0 and bot.user.mentioned_in(message)):
            await message.channel.send('Hello! My name is KitAI. Support your Discord life☺')
            isStand = 1
        # 緊急モード時のエラーメッセージ
        elif(e==-1):
            await message.channel.send('Some error occurred, so I switched to emergency command mode. Check the console for details.')
            
        print(f"{message.author} mended {bot.user} : execute\n{message.content}")
        
        # Bot自身のメッセージは無視
        if message.author == bot.user:
            return 

        # 編集モードに切り替え
        if "!edit" in message.content and bot.user.mentioned_in(message):
            await message.channel.send('''```diff
+change edit mode!!
```''')
            await bot.close()
            return
        
        # 基本的な単語フィルター機能（"お前"という単語を削除）
        if "お前" in message.content:
            await message.delete()
        return

    # Discord botを起動
    bot.run(TOKEN)

    # メモリクリーンアップ
    del bot

    return