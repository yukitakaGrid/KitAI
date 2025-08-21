# KitAI システムの詳細解説

## 概要
KitAIは、ChatGPT（GPT-4）を活用してDiscord botの機能を自動的に実装できるシステムです。ユーザーが自然言語で機能を要求すると、AIが適切なコードを生成し、動的にbotに機能を追加します。

## システム構成

### 主要ファイル

#### 1. `main.py` - メインオーケストレーター
- **役割**: コマンドモードと編集モードを切り替えるメイン制御システム
- **動作**: マルチプロセシングを使用して2つのモード間を切り替え
- **詳細**:
  - `task1()`: execute.pyまたはexecute_combined.pyを実行（コマンドモード）
  - `task2()`: edit.pyを実行（編集モード）
  - イベントを使用してプロセス間の同期を制御

#### 2. `execute.py` - コマンドモード
- **役割**: 基本的なDiscord botの実行環境
- **機能**:
  - 初回メンション時の挨拶メッセージ
  - `!edit`コマンドでの編集モードへの切り替え
  - "お前"という単語を含むメッセージの自動削除
- **特徴**: シンプルな基本機能のみを提供

#### 3. `edit.py` - 編集モード（AI機能実装）
- **役割**: AIを使用した新機能の実装
- **主要機能**:
  - ユーザーの自然言語要求をGPT-4に送信
  - 生成されたコードの表示と承認確認
  - 承認されたコードを`register_bot_func.txt`に追加
  - `!display`コマンドで実装済み機能の一覧表示
  - `!command`コマンドでコマンドモードへの切り替え

#### 4. `openai_bot.py` - AI インターフェース
- **役割**: OpenAI GPT-4 APIとの連携
- **機能**:
  - Discord bot用のコード生成に特化したプロンプト設定
  - GPT-4との通信処理
  - 生成されたコードの形式チェック

#### 5. `syntax_make.py` - コード結合ユーティリティ
- **役割**: 複数のファイルを1つのPythonスクリプトに結合
- **機能**:
  - `init.txt`, `register_bot_func.txt`, `finish.txt`を結合
  - `execute_combined.py`の生成
  - 既存ファイルの安全な削除・作成

#### 6. `prefix.py` - テキスト装飾ユーティリティ
- **機能**:
  - テキストのインデント処理
  - Discord用の差分表示形式（```diff）でのメッセージ装飾

### サポートファイル

#### `syntax_source/` ディレクトリ
- **`init.txt`**: 基本的なDiscord bot設定とテンプレート
- **`register_bot_func.txt`**: AIが生成した機能が追加されるファイル
- **`finish.txt`**: bot実行とクリーンアップのコード

## 動作フロー

### 1. システム起動
```
main.py起動 → execute.py実行（コマンドモード）
```

### 2. 編集モードへの切り替え
```
ユーザー: @KitAI !edit
→ execute.py終了 → edit.py起動（編集モード）
```

### 3. 新機能の実装プロセス
```
1. ユーザーが自然言語で機能を要求
   例: "@KitAI 猫語で返事をする機能をお願いします"

2. edit.pyがGPT-4にリクエスト送信

3. GPT-4がDiscord bot用のコードを生成

4. 生成されたコードをユーザーに表示

5. ユーザーが"Yes"で承認

6. コードがregister_bot_func.txtに追加

7. init.txt + register_bot_func.txt + finish.txt を結合
   → execute_combined.py生成
```

### 4. コマンドモードへの復帰
```
edit.py終了 → execute_combined.py実行（新機能付きコマンドモード）
```

## 重要なポイント

### セキュリティ機能
- 生成されたコードは実行前にユーザーの明示的な承認が必要
- "Yes/No"以外の回答は受け付けない

### AI生成コードの形式
GPT-4は以下の形式でコードを生成：
```python
@bot.event
async def function_name_12345678():
    # 機能の説明コメント
    # 実装コード
    return
```

### エラーハンドリング
- コンパイルエラー時は緊急モードで基本的なexecute.pyを実行
- 不正な要求に対する適切なエラーメッセージ

### 拡張性
- 新しい機能は`register_bot_func.txt`に蓄積される
- システムを再起動しても追加された機能は保持される

## 設定方法

### 必要な設定
1. **Discord Bot Token**: 
   - `execute.py`, `edit.py`, `init.txt`の`TOKEN`変数
2. **OpenAI API Key**: 
   - `openai_bot.py`の`api_key`変数

### 実行方法
```bash
cd src
python main.py
```

## 制限事項
- データ永続化が必要な複雑な機能の実装は困難
- 生成されるコードの品質はGPT-4の能力に依存
- Discord APIの制限内での動作

このシステムにより、プログラミング知識がないユーザーでも、自然言語でDiscord botに新機能を追加できます。