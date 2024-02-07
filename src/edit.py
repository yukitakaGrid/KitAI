import discord
from discord.ext import commands

import syntax_make
import openai_bot
import prefix

# ボットのトークンをセット
TOKEN = 'MTE0MTY0ODQ2NjczNzYzNTM4OA.G0Y_md.-YHA0DA98ezQu4Czy_rRHidMh3-hYBvr5HhRJA'

isPermissionRequested = 0
keywords = []
add_func = ""
func_N = 3
func_name_list = ['login','change_edit','voice_hello_user']

gpt4_0 = openai_bot.GPT4_0()

def run():
    # ボットの接続準備
    intents = discord.Intents.default()
    intents.voice_states = True  # ボイスチャンネルの情報を取得するために必要

    Kitbot = commands.Bot(command_prefix='!', intents=intents)

    # discordと接続した時に呼ばれる
    @Kitbot.event
    async def on_ready():
        print(f'We have logged in as {Kitbot.user} : edit')

    @Kitbot.event
    async def on_message(message):
        global isPermissionRequested
        global keywords
        global add_func
        print(f"{message.author} mended {Kitbot.user} : edit")
        if message.author == Kitbot.user:
            return 

        # Check if "make" is in the message and if the bot is mentioned
        if(isPermissionRequested==0 and Kitbot.user.mentioned_in(message)):
            if "!command" in message.content and Kitbot.user.mentioned_in(message):
                await message.channel.send('''```diff
+change command mode!!
```''')
                await Kitbot.close()
                return

            elif "!display" in message.content and Kitbot.user.mentioned_in(message):
                # func_name_listの中身を表示
                func_name_list_str = ""
                for i in range(len(func_name_list)):
                    func_name_list_str += str(i) + ": " + func_name_list[i] + "\n"
                func_name_list_str_color = prefix.green_lines_with_prefix(func_name_list_str,"+")
                await message.channel.send(func_name_list_str_color)
                return 

            else:
                await message.channel.send("Ok! Wait a moment, I'll think about it...")
                contents = gpt4_0.interaction(message.content)

                # 関数名を抽出
                # 文章を改行で分割し、各行の最初の#の後ろの単語を抽出する
                lines = contents.split('\n')
                keywords = [line.split('#', 1)[-1].strip().split()[0] for line in lines if line.strip().startswith('#')]
                # 関数名をリストの先頭に追加
                if keywords:
                    func_name_list.insert(0, keywords[0])
                else:
                    await message.channel.send("具体的なコマンド要求を満たしていません。プログラムの構築には明確な要求（機能の説明や目的など）が必要です。詳細を提供していただければ、適切なコードを作成いたします。")
                    return
                global func_N
                func_N += 1

                add_func = "\n\n"

                # コードの切り抜き
                on_etract = 0
                contents_code = ""
                for line in lines:
                    # '#'が来たらコードの切り抜き開始
                    # 再度'#'が来たらコードの切り抜き終了
                    if(line.strip().startswith('#')):
                        on_etract = abs(on_etract-1)
                    if(on_etract==1):
                        contents_code += line + "\n"

                # GPTから取得したコードを字下げする
                contents_code = prefix.indent_text(contents_code)
                add_func += contents_code

                await message.channel.send(f"以下のコードの実装を許可する？Yes/No")
                await message.channel.send(f"コード内容 :```{contents_code}```")

                isPermissionRequested = 1
                return
                
        
        if(isPermissionRequested==1 and Kitbot.user.mentioned_in(message)):
            if "Yes" in message.content:
                keyword_color = prefix.green_lines_with_prefix(keywords[0] + "を実装しました","+")
                await message.channel.send(keyword_color)

                with open("syntax_source/register_bot_func.txt", 'a', encoding='utf-8') as f:
                    f.write(add_func)
                isPermissionRequested = 0
                return 
            
            elif "No" in message.content:
                await message.channel.send("変更内容を破棄しました。")
                isPermissionRequested = 0
                return
            
            else:
                await message.channel.send("can only accept Yes/No")

        # This is needed to process commands if you have any
        await Kitbot.process_commands(message)

    Kitbot.run(TOKEN)

    input_files = ["syntax_source/init.txt", "syntax_source/register_bot_func.txt", "syntax_source/finish.txt"]
    syntax_make.combine_files(input_files, "execute_combined.py")
    print("構文を結合し、ファイルを上書きしました")

    # botインスタンスへの参照を削除
    del Kitbot

    return
