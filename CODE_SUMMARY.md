# このコードについて - KitAIシステムの詳細解説

## 概要
このリポジトリのコードは、**KitAI**という革新的なDiscord botシステムです。最大の特徴は、**ユーザーが自然言語で要求した機能をGPT-4が自動的にプログラムコードに変換し、リアルタイムでbotに実装する**ことができる点です。

## コードの構成と各ファイルの役割

### 🎯 メインシステム (`src/main.py`)
**役割**: システム全体のオーケストレーター

```python
# マルチプロセシングで2つのモードを管理
task1() # コマンドモード（実装済み機能の実行）
task2() # 編集モード（新機能の実装）
```

**動作原理**:
- プロセス間通信でモード切り替えを制御
- 初回は基本bot（execute.py）を起動
- 機能追加後は統合bot（execute_combined.py）を起動

### 🤖 基本実行モード (`src/execute.py`)
**役割**: 基本的なDiscord bot機能を提供

```python
def run(e):
    # 基本機能のみのシンプルなbot
    # - 初回メンション時の挨拶
    # - !editコマンドで編集モードに切り替え
    # - 単語フィルター機能（"お前"を削除）
```

**特徴**:
- 軽量で安定した基本機能
- 緊急時のフォールバック機能
- 編集モードへのゲートウェイ

### 🧠 AI編集モード (`src/edit.py`)  
**役割**: AIを使った新機能の自動実装

**主要処理フロー**:
1. ユーザーの自然言語要求を受信
2. GPT-4に送信してコード生成を依頼
3. 生成されたコードをユーザーに表示
4. ユーザーの承認後、機能をファイルに追加
5. テンプレートファイルを統合して新botを生成

```python
@Kitbot.event
async def on_message(message):
    # ユーザー要求 → AI生成 → 承認 → 実装
    contents = gpt4_0.interaction(message.content)  # AI生成
    # コード抽出とファイル追加処理
```

### 🚀 AI エンジン (`src/openai_bot.py`)
**役割**: GPT-4との連携とコード生成

```python
class GPT4_0:
    def __init__(self):
        # Discord bot専用のプロンプト設定
        self.prompt_prefix = '''Discord.py専用のコード生成指示'''
    
    def interaction(self, request_text):
        # GPT-4 APIでコード生成
        return generated_code
```

**特徴**:
- Discord.py専用にプロンプトを最適化
- エラー回避のための詳細な指示
- 一貫したコード形式の保証

### 🔧 コード統合システム (`src/syntax_make.py`)
**役割**: 複数ファイルを1つのbotスクリプトに統合

```python
def combine_files(input_files, output_filename):
    # init.txt + register_bot_func.txt + finish.txt
    # ↓
    # execute_combined.py (完全なbotスクリプト)
```

**統合プロセス**:
1. `init.txt`: Discord botの基本設定
2. `register_bot_func.txt`: AI生成機能を蓄積
3. `finish.txt`: bot起動とクリーンアップ

### 🎨 テキスト装飾 (`src/prefix.py`)
**役割**: Discord表示用のテキストフォーマット

```python
def green_lines_with_prefix(text, prefix):
    # Discord差分表示形式（```diff）でメッセージ装飾
    return formatted_discord_message
```

## 🔄 システムの動作フロー

### 1. 起動プロセス
```
main.py起動
    ↓
execute.py実行（基本機能のみ）
    ↓
ユーザーが機能を使用
```

### 2. 新機能実装プロセス
```
ユーザー: "@KitAI 猫語で返事する機能をお願いします"
    ↓
edit.py: GPT-4にリクエスト送信
    ↓
GPT-4: Discord bot用コードを生成
    ↓
edit.py: 生成コードをユーザーに提示
    ↓
ユーザー: "Yes" で承認
    ↓
edit.py: register_bot_func.txtにコード追加
    ↓
syntax_make: 3つのファイルを統合
    ↓
execute_combined.py生成（新機能付きbot）
```

### 3. 機能拡張の継続
```
新機能付きbotが起動
    ↓
さらなる機能要求があれば上記プロセス繰り返し
    ↓
機能は蓄積され続ける
```

## 💡 システムの革新性

### 1. **動的機能追加**
- プログラム再起動なしで新機能追加
- ユーザーが直接プログラミング不要

### 2. **AI駆動開発**
- 自然言語→コード変換
- Discord.py専用最適化

### 3. **セキュリティ機能** 
- 生成コードの事前表示
- ユーザー明示承認必須

### 4. **永続化システム**
- 機能は自動保存
- システム再起動後も維持

## 🔒 安全性の仕組み

```python
# 生成コードの承認プロセス
await message.channel.send("以下のコードの実装を許可する？Yes/No")
await message.channel.send(f"コード内容 :```{contents_code}```")
```

- **二段階承認**: コード表示→ユーザー承認
- **透明性**: 実行前にコード内容を完全表示
- **制御可能**: Yes/No以外は受け付けない

## 🚧 技術的制約

### 現在の制限
- データ永続化機能は実装困難
- 複雑な状態管理が必要な機能は制限される
- OpenAI APIの利用制限に依存

### 設定要件
- Discord Bot Token の設定必要
- OpenAI API Key の設定必要
- Python 3.12.1 + discord.py + openai ライブラリ

## 🎯 使用例

### 基本的な機能要求例
```
@KitAI 猫語で話しかけたら猫語で返すコマンドをお願いします
→ 猫語変換機能が自動実装される

@KitAI "お前"という単語を含んでいたらそのメッセージを消去して警告を送るコマンドをお願いします  
→ メッセージフィルター機能が自動実装される
```

## 🔮 このシステムの意義

KitAIは、**プログラミング知識を持たないユーザーでも、自然言語でbotに新機能を追加できる**画期的なシステムです。これにより：

- **民主化**: プログラミングの民主化
- **効率化**: 開発時間の大幅短縮  
- **カスタマイゼーション**: ユーザーニーズに完全対応
- **学習機会**: AI生成コードから学習可能

このコードは、AI時代のソフトウェア開発の新しい可能性を示すプロトタイプといえます。