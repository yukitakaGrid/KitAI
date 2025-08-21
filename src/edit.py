import discord
from discord.ext import commands

import syntax_make
import openai_bot
import prefix

# Discord botトークン（実際の使用時は有効なトークンに置き換える）
TOKEN = 'あなたのトークンを入力してください'

# グローバル変数
isPermissionRequested = 0  # コード承認待ち状態フラグ
keywords = []              # AI生成コードから抽出したキーワード
add_func = ""             # 追加する関数のコード
func_N = 3                # 関数番号カウンター
func_name_list = ['login','change_edit','voice_hello_user']  # 実装済み機能リスト

# GPT-4インスタンスを作成
gpt4_0 = openai_bot.GPT4_0()

def run():
    """
    編集モード（AI機能実装モード）のメイン実行関数
    ユーザーの要求をAIが解析し、Discord bot機能を自動生成する
    """
    # Discord bot の基本設定
    intents = discord.Intents.default()
    intents.voice_states = True  # ボイスチャンネルの情報を取得するために必要

    Kitbot = commands.Bot(command_prefix='!', intents=intents)

    @Kitbot.event
    async def on_ready():
        """Bot起動完了時の処理"""
        print(f'We have logged in as {Kitbot.user} : edit')

    @Kitbot.event
    async def on_message(message):
        """
        メッセージ受信時の処理
        - コマンド実行（!command, !display）
        - AI機能要求の受付と処理
        - 生成コードの承認処理
        """
        global isPermissionRequested
        global keywords
        global add_func
        print(f"{message.author} mended {Kitbot.user} : edit")
        
        # Bot自身のメッセージは無視
        if message.author == Kitbot.user:
            return 

        # メイン処理: コード承認待ちでない場合 & Botがメンションされている場合
        if(isPermissionRequested==0 and Kitbot.user.mentioned_in(message)):
            # コマンドモードに切り替え
            if "!command" in message.content and Kitbot.user.mentioned_in(message):
                await message.channel.send('''```diff
+change command mode!!
```''')
                await Kitbot.close()
                return

            # 実装済み機能一覧表示
            elif "!display" in message.content and Kitbot.user.mentioned_in(message):
                # func_name_listの中身を表示
                func_name_list_str = ""
                for i in range(len(func_name_list)):
                    func_name_list_str += str(i) + ": " + func_name_list[i] + "\n"
                func_name_list_str_color = prefix.green_lines_with_prefix(func_name_list_str,"+")
                await message.channel.send(func_name_list_str_color)
                return 

            # AI機能実装要求の処理
            else:
                await message.channel.send("Ok! Wait a moment, I'll think about it...")
                # GPT-4にユーザーの要求を送信
                contents = gpt4_0.interaction(message.content)

                # AI生成コードから関数名を抽出
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

                # AI生成コードからPythonコード部分を抽出
                on_etract = 0  # コード抽出フラグ
                contents_code = ""
                for line in lines:
                    # '#'マーカーでコード部分を識別
                    if(line.strip().startswith('#')):
                        on_etract = abs(on_etract-1)  # フラグの切り替え
                    if(on_etract==1):
                        contents_code += line + "\n"

                # GPTから取得したコードをインデント調整
                contents_code = prefix.indent_text(contents_code)
                add_func += contents_code

                # ユーザーにコード承認を求める
                await message.channel.send(f"以下のコードの実装を許可する？Yes/No")
                await message.channel.send(f"コード内容 :```{contents_code}```")

                isPermissionRequested = 1  # 承認待ち状態に変更
                return
                
        # コード承認処理: 承認待ち状態 & Botがメンションされている場合
        if(isPermissionRequested==1 and Kitbot.user.mentioned_in(message)):
            # コード実装承認
            if "Yes" in message.content:
                keyword_color = prefix.green_lines_with_prefix(keywords[0] + "を実装しました","+")
                await message.channel.send(keyword_color)

                # 承認されたコードをregister_bot_func.txtに追加
                with open("syntax_source/register_bot_func.txt", 'a', encoding='utf-8') as f:
                    f.write(add_func)
                isPermissionRequested = 0  # 承認待ち状態をリセット
                return 
            
            # コード実装拒否
            elif "No" in message.content:
                await message.channel.send("変更内容を破棄しました。")
                isPermissionRequested = 0  # 承認待ち状態をリセット
                return
            
            # 無効な回答
            else:
                await message.channel.send("can only accept Yes/No")

        # Discord.pyのコマンド処理（必須）
        await Kitbot.process_commands(message)

    # Discord botを起動
    Kitbot.run(TOKEN)

    # Bot終了後の後処理: AI生成コードを統合ファイルに結合
    input_files = ["syntax_source/init.txt", "syntax_source/register_bot_func.txt", "syntax_source/finish.txt"]
    syntax_make.combine_files(input_files, "execute_combined.py")
    print("構文を結合し、ファイルを上書きしました")

    # メモリクリーンアップ
    del Kitbot

    return
