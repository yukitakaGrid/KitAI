# KitAI
ハッカソンで制作したChat GPTが自動的にコマンド実装してくれるDiscord bot

<img src=https://github.com/yukitakaGrid/KitAI/blob/main/img/KitAI_greed.png width="50%" />

This product's slide.
https://www.canva.com/design/DAFsDdJhtgQ/8kH_baIP2xj3stJ0DI2JRA/view#9

## Version

OpenAI : gpt-4-turbo-preview
Python : 3.12.1

## How to set
事前に必要なライブラリをインストールしておきます。
```
pip install openai
pip install discord.py
```

このリモートリポジトリをクローンします。
```
git clone https://github.com/yukitakaGrid/KitAI.git
```

次に、DiscordのDeveloperのwebページでbotの作成をし、トークンを発行します。
https://discord.com/developers/applications

同時に、OpenAIのサイトでAPI Keyを発行します。
https://platform.openai.com/docs/overview

終わったらトークンを適切なプログラムに埋め込んでいきます。
**discord token -> src/execute.py,src/edit.py,src/init.txt**
**openai key -> src/openai_bot.py**

最後に任意のチャンネルに作成したbotを招待し、
```
python main.py
```
で起動すれば完了です。

## Reference
このbotはedit modeとcommand modeの2種類のモードが存在します。デフォルトはcommand modeです。

### Example

## Note
システムの設計上データを保持する必要のあるコマンドの自動的な実装は難しいです。
