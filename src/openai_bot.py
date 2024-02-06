import os
import openai

class GPT3_5:
    def __init__(self):
        openai.organization = os.environ.get("org-aSq6cg3kqopgOyZ3WUZneVYj")
        openai.api_key = "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"

        self.prompt_prefix = '''
        求められた機能に対して、適するイベント関数を実装してください。なお説明はいらず、
        ただプログラムだけを出力してください。
        以下フォーマットです。
        ```
        # <function name(英語のみ)(関数内のプログラムの単語を含めて一様なfunction nameにする)>
        <@イベントのコマンドエクステンションをここに記述>
        async def <関数名>():
            <以下プログラムの実装>
            return <returnを必ず含む>
        ########## <関数の区切りとして#を10個追加>
        ```
'''

    def interaction(self,request_text):
        # APIリクエストの設定
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # GPTのエンジン名を指定します
            messages=[
                {"role":"system","content":self.prompt_prefix},
                {"role":"user","content":request_text}
            ]
        )

        return response["choices"][0]["message"]["content"]