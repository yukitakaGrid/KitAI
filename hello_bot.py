import discord
from discord.ext import commands

# ボットのトークンをセット
TOKEN = 'MTE0MTY0ODQ2NjczNzYzNTM4OA.GJ1rIW.7IB6CQ20lf9YsdO_EdKZNsml62TrrumikF7g5w'

# ボットの接続準備
intents = discord.Intents.default()
intents.voice_states = True  # ボイスチャンネルの情報を取得するために必要

bot = commands.Bot(command_prefix='!', intents=intents)

# discordと接続した時に呼ばれる
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# ボイスチャンネルに入ったときのイベントハンドラ
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel:  # ボイスチャンネルに入った場合
        guild = member.guild  # メンバーが所属しているサーバー（ギルド）を取得

        # 送信先の一般チャンネルを取得（チャンネル名に応じて調整してください）
        channel_name = '一般'  # 送信先のチャンネル名
        general_channel = discord.utils.get(guild.text_channels, name=channel_name)

        if general_channel:
            await general_channel.send(f'Hello, {member.display_name}! {member.mention} joined a voice channel.')

# ボットの起動
bot.run(TOKEN)