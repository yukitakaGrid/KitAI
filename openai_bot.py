import os
import openai

openai.organization = os.environ.get("org-aSq6cg3kqopgOyZ3WUZneVYj")
openai.api_key = "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"

# プロンプトの設定
prompt = "空の色を教えてください。"

# APIリクエストの設定
response = openai.Completion.create(
    model="text-davinci-002",  # GPTのエンジン名を指定します
    prompt=prompt,
    max_tokens=100,  # 生成するトークンの最大数
    n=5,  # 生成するレスポンスの数
    stop=None,  # 停止トークンの設定
    temperature=0.7,  # 生成時のランダム性の制御
    top_p=1,  # トークン選択時の確率閾値
)

# 生成されたテキストの取得
for i, choice in enumerate(response.choices):
    print(f"\nresult {i}:")
    print(choice.text.strip())