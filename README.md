# KitAI
個人でハッカソンで制作したChat GPTが自動的にコマンド実装してくれるDiscord bot

<img src=https://github.com/yukitakaGrid/KitAI/blob/main/img/KitAI_greed.png width="50%" />

This product's slide.  
https://www.canva.com/design/DAFsDdJhtgQ/8kH_baIP2xj3stJ0DI2JRA/view#9

# Version

OpenAI : gpt-4-turbo-preview  
Python : 3.12.1

# How to set
このリモートリポジトリをクローンします。
```
git clone https://github.com/yukitakaGrid/KitAI.git
```
事前に必要なライブラリをインストールしておきます。
```
pip install openai
pip install discord.py
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
cd src
python main.py
```
で起動すれば完了です。

# Reference
このbotはedit modeとcommand modeの2種類のモードが存在します。デフォルトはcommand modeです。

### command mode
このモードは実装された機能を使うことができるモードです。基本的にはこちらの状態でサーバに置いておきます。

機能をAIに実装させたい場合は
```
@KitAI !edit
```
とメンションし!editコマンドを与えることでモードが変更されます。
以下が返ってきたら成功です。  
<img src=https://github.com/yukitakaGrid/KitAI/blob/main/img/KitAI_change_edit.png width="50%" />

### edit mode
このモードはAIに依頼をすることで任意の機能を自動的に実装をしてくれるAI編集モードです。
KitAIをメンションし、実装したい機能内容を送ることでAIが最適なプログラムを考え実装します。
しかし、抽象的な内容だったり文章として成り立っていない場合実装できないことがあります。

実装した機能達を振り返りたい場合、以下のコマンドを送ることで追加された関数名が一覧となって返ってきます。
```
@KitAI !display
```

command modeに変更したい場合は
```
@KitAI !command
```
とメンションし!commandコマンドを与えることでモードが変更されます。

# AI Prompt Example
##### example 1
```
@KitAI 猫語で話しかけたら猫語で返すコマンドをお願いします
```
<img src=https://github.com/yukitakaGrid/KitAI/blob/main/img/KitAI_nyan_code.png width="50%" /> 

```
@KitAI Yes
```

<img src=https://github.com/yukitakaGrid/KitAI/blob/main/img/KItAI_nyan.png width="50%" />  

##### example 2
```
@KitAI "お前"という単語を含んでいたらそのメッセージを消去して警告を送るコマンドをお願いします
```
<img src=https://github.com/yukitakaGrid/KitAI/blob/main/img/KitAI_delete_code.png width="50%" />  

```
@KitAI Yes
```

<img src=https://github.com/yukitakaGrid/KitAI/blob/main/img/KitAI_delete.png width="50%" />  

## Note
システムの設計上データを保持する必要のあるコマンドの自動的な実装は難しいです。

botで使用した画像  
<img src=https://github.com/yukitakaGrid/KitAI/blob/main/img/KitAI.jpg
 width="50%" />  
 作 : DALL-E 3 
