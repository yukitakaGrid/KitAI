import os
import openai

class GPT4_0:
    """
    OpenAI GPT-4 APIを使用してDiscord bot機能を生成するクラス
    ユーザーの自然言語要求をDiscord.py用のコードに変換する
    """
    def __init__(self):
        """GPT-4 APIの初期化とプロンプト設定"""
        # OpenAI APIの認証情報設定
        openai.organization = os.environ.get("org-aSq6cg3kqopgOyZ3WUZneVYj")
        openai.api_key = "あなたのキーを入力してください"

        # Discord bot用のコード生成プロンプト
        # GPT-4に特化した指示とフォーマットを定義
        self.prompt_prefix = '''
        あなたはdiscord.pyのプログラマーです。求められた機能に対して、適するイベント関数を実装してください。なお説明はいらず、
        プログラムのみを出力してください。
        このプログラムはそのまま実行中のプログラムに組み込まれるのでなるべくコンパイルエラーの
        なくすために組んだコードは一度目視でコンパイルエラーチェックしてから再度組み直してください
        以下フォーマットです。なお、discord botの変数名はbotと定義するものとします。
        イベントのコマンドエクステンションとasync defの関数は事前に用意してあるので除外してプログラムを組んでください。
        
        <@イベントのコマンドエクステンションをここに記述>
        async def <関数名-識別できるように8桁の乱数を後ろにつける>():
            <あなたが実装する関数の名前をコメントとしてここに記してください 例:#on_message_delete>
            <以下プログラムの実装>
            return <returnを必ず含む>
        ########## <関数の区切りとして#を10個追加>
        
'''

    def interaction(self,request_text):
        """
        ユーザーの要求をGPT-4に送信してDiscord bot用のコードを生成
        
        Args:
            request_text (str): ユーザーからの機能要求テキスト
            
        Returns:
            str: GPT-4が生成したDiscord bot用のPythonコード
        """
        # GPT-4 APIリクエストの設定
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",  # GPT-4 Turboモデルを使用
            messages=[
                {"role":"system","content":self.prompt_prefix},  # システムプロンプト
                {"role":"user","content":request_text}           # ユーザーの要求
            ]
        )

        # 生成されたコードを取得
        text = response["choices"][0]["message"]["content"]

        # デバッグ用出力
        print(f"CHatGPT:\n\n{text}")

        return text