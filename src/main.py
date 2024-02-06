import multiprocessing
import execute
import edit
import subprocess
import syntax_make

# 0のときシンプルなdiscord botの起動
# 1のとき構文が結合されたdiscord botの起動
counter = [0]

def task1(event1, event2):
    while True:
        event1.wait()  # 実行可能になるまで待機
        if counter[0] == 0:
            print('executeを実行します')
            execute.run(0) # execute.pyの実行
            counter[0] += 1;
        else:
            try:
                print('execute_combinedをコンパイルし、実行します')
                result = subprocess.run(['python', 'execute_combined.py'], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f'コンパイルに失敗しました: {e.stderr}')
                execute.run(-1) # 緊急でexecute.py実行

        event1.clear()
        event2.set()  # editを実行可能にする

def task2(event1, event2):
    while True:
        event2.wait()  # 実行可能になるまで待機
        print('editを実行します')
        edit.run()
        event2.clear()
        event1.set()  # executeを実行可能にする

if __name__ == '__main__':
    event1 = multiprocessing.Event()
    event2 = multiprocessing.Event()
    
    event1.set()  # 最初はexecuteから開始
    event2.clear()

    p1 = multiprocessing.Process(target=task1, args=(event1, event2))
    p2 = multiprocessing.Process(target=task2, args=(event1, event2))

    print("編集プログラムと実行プログラムの非同期処理を開始します")
    p1.start()
    p2.start()

    p1.join()
    p2.join()