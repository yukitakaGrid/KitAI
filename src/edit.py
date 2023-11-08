import discord
from discord.ext import commands

import syntax_make
import openai_bot
import prefix

# ボットのトークンをセット
TOKEN = 'Discord botのAPI key'

func_N = 3
func_name_list = ['login','change_edit','voice_hello_user']

gpt3_5 = openai_bot.GPT3_5()

def run():
    # ボットの接続準備
    intents = discord.Intents.default()
    intents.voice_states = True  # ボイスチャンネルの情報を取得するために必要

    Kitbot = commands.Bot(command_prefix='!', intents=intents)

    # discordと接続した時に呼ばれる
    @Kitbot.event
    async def on_ready():
        print(f'We have logged in as {Kitbot.user}')

    @Kitbot.event
    async def on_message(message):
        if message.author == Kitbot.user:
            return 

        # Check if "make" is in the message and if the bot is mentioned
        if "!command" in message.content and Kitbot.user.mentioned_in(message):
            await message.channel.send('Command Mode に切り替わりました')
            await Kitbot.close()
            return

        elif "!func" in message.content and Kitbot.user.mentioned_in(message):
            # func_name_listの中身を表示
            func_name_list_str = ""
            for i in range(len(func_name_list)):
                func_name_list_str += str(i) + ": " + func_name_list[i] + "\n"
            func_name_list_str_color = prefix.green_lines_with_prefix(func_name_list_str,"+")
            await message.channel.send(func_name_list_str_color)
            return 

        elif Kitbot.user.mentioned_in(message):
            contents = gpt3_5.interaction(message.content)

            # 関数名を抽出
            # 文章を改行で分割し、各行の最初の#の後ろの単語を抽出する
            lines = contents.split('\n')
            keywords = [line.split('#', 1)[-1].strip().split()[0] for line in lines if line.strip().startswith('#')]
            # 関数名をリストの先頭に追加
            func_name_list.insert(0, keywords[0])
            global func_N
            func_N += 1

            keyword_color = prefix.green_lines_with_prefix(keywords[0] + "を実装しました","+")
            await message.channel.send(keyword_color)

            # GPTから取得したコードを字下げする
            contents = prefix.indent_text(contents)
            add_func = "\n\n"
            add_func += contents
            with open("syntax_source/register_bot_func.txt", 'a', encoding='utf-8') as f:
                f.write(add_func)

        # This is needed to process commands if you have any
        await Kitbot.process_commands(message)

    print("botを実行します")
    Kitbot.run(TOKEN)

    # botインスタンスへの参照を削除
    del Kitbot

    input_files = ["syntax_source/init.txt", "syntax_source/register_bot_func.txt", "syntax_source/finish.txt"]
    syntax_make.combine_files(input_files, "execute_combined.py")
    print("構文を結合し、ファイルを上書きしました")

    return
