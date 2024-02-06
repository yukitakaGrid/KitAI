import os
import openai

class GPT4_0:
    def __init__(self):
        openai.organization = os.environ.get("org-aSq6cg3kqopgOyZ3WUZneVYj")
        openai.api_key = "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"

        self.prompt_prefix = '''
        あなたはdiscord.pyのプログラマーです。求められた機能に対して、適するイベント関数を実装してください。なお説明はいらず、
        プログラムのみを出力してください。
        このプログラムはそのまま実行中のプログラムに組み込まれるのでなるべくコンパイルエラーの
        なくすために組んだコードは一度目視でコンパイルエラーチェックしてから再度組み直してください
        以下フォーマットです。なお、discord botの変数名はbotと定義するものとします。
        
        # <あなたが実装する関数の名前をここに代入してください>
        <@イベントのコマンドエクステンションをここに記述>
        async def <関数名>():
            <以下プログラムの実装>
            return <returnを必ず含む>
        ########## <関数の区切りとして#を10個追加>
        
'''

    def interaction(self,request_text):
        # APIリクエストの設定
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",  # GPTのエンジン名を指定します
            messages=[
                {"role":"system","content":self.prompt_prefix},
                {"role":"user","content":request_text}
            ]
        )

        text = response["choices"][0]["message"]["content"]

        print(f"CHatGPT:\n\n{text}")

        return text