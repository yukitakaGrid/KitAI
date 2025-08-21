import multiprocessing
import execute
import edit
import subprocess
import syntax_make

# KitAIシステムのメイン制御プログラム
# コマンドモード（execute系）と編集モード（edit）を切り替えて実行

# 実行状態管理: 0=初回実行（execute.py）, 1=機能追加後実行（execute_combined.py）
counter = [0]

def task1(event1, event2):
    """
    コマンドモードを実行するタスク
    初回はexecute.py、2回目以降はAI生成機能を含むexecute_combined.pyを実行
    """
    while True:
        event1.wait()  # 実行可能になるまで待機
        if counter[0] == 0:
            print('executeを実行します')
            execute.run(0) # execute.pyの実行（基本機能のみ）
            counter[0] += 1;
        else:
            try:
                print('execute_combinedをコンパイルし、実行します')
                # AI生成機能を含む統合botを実行
                result = subprocess.run(['python', 'execute_combined.py'], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f'コンパイルに失敗しました: {e.stderr}')
                execute.run(-1) # 緊急時は基本execute.pyを実行

        event1.clear()
        event2.set()  # editモードを実行可能にする

def task2(event1, event2):
    """
    編集モードを実行するタスク
    AIによる新機能実装とコード生成を担当
    """
    while True:
        event2.wait()  # 実行可能になるまで待機
        print('editを実行します')
        edit.run()  # AI機能実装モードを実行
        event2.clear()
        event1.set()  # executeモードを実行可能にする

if __name__ == '__main__':
    # マルチプロセシング用のイベント作成
    event1 = multiprocessing.Event()  # executeモード制御用
    event2 = multiprocessing.Event()  # editモード制御用
    
    # 初期状態: executeモードから開始
    event1.set()  # 最初はexecuteから開始
    event2.clear()

    # 2つのプロセスを作成
    p1 = multiprocessing.Process(target=task1, args=(event1, event2))  # コマンドモード
    p2 = multiprocessing.Process(target=task2, args=(event1, event2))  # 編集モード

    print("編集プログラムと実行プログラムの非同期処理を開始します")
    p1.start()
    p2.start()

    # プロセス終了まで待機
    p1.join()
    p2.join()