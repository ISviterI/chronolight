import threading
import time


def delay(seconds, func):
    def wrapper():
        time.sleep(seconds)
        func()

    thread = threading.Thread(target=wrapper)
    thread.start()

class Timeline:
    def __init__(self):
        self.actions = []
    def call(self,function):
        self.actions.append(["call",function])
    def wait(self,seconds:float):
        self.actions.append(["wait",seconds])
    def run(self,threaded:bool=False):
        current_delay = 0
        for act in self.actions:
            if act[0] == "call":
                if threaded:
                    delay(current_delay,act[1])
                else:
                    act[1]()
            elif act[0] == "wait":
                if threaded:
                    current_delay += act[1]
                else:
                    time.sleep(act[1])

