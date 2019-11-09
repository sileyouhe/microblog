import threading

global_Data = threading.local()

def show():
    print(threading.current_thread().getName(), global_Data.num)

def thread_cal():
    global_Data.num = 0
    for _ in range(100):
        global_Data.num += 1
    show()

threads = []
for i in range(10):
    threads.append(threading.Thread(target=thread_cal))
    threads[i].start()






