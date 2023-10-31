import multiprocessing
import execute
import edit
import subprocess

counter = [0]

def task1(event1, event2):
    while True:
        event1.wait()  # executeを実行可能にする
        if counter[0] == 0:
            print('executeを実行します')
            execute.run()
            counter[0] += 1;
        elif counter[0] == 1:
            print('subprocess.runを使ってexecute_combinedを実行します')
            subprocess.run(['python', 'execute_combined.py'])
        event1.clear()
        event2.set()  # editを実行可能にする

def task2(event1, event2):
    while True:
        event2.wait()  # editを実行可能にする
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

    p1.start()
    p2.start()

    p1.join()
    p2.join()