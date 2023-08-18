import discord

# インテントの生成
intents = discord.Intents.default()
intents.message_content = True

# クライアントの生成
client = discord.Client(intents=intents)

# discordと接続した時に呼ばれる
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# メッセージを受信した時に呼ばれる
@client.event
async def on_message(message):
    # 自分のメッセージを無効
    if message.author == client.user:
        return

    # メッセージが"$hello"で始まっていたら"Hello!"と応答
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

# クライアントの実行
client.run('MTE0MTY0ODQ2NjczNzYzNTM4OA.GJ1rIW.7IB6CQ20lf9YsdO_EdKZNsml62TrrumikF7g5w')