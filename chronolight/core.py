import threading
import time


def delay(seconds, func, *args, **kwargs):

    def wrapper():
        time.sleep(seconds)
        func(*args, **kwargs)

    thread = threading.Thread(target=wrapper)
    thread.start()

class Timeline:
    def __init__(self):
        self.actions = []
    def call(self,function,*args,**kwargs):
        self.actions.append(["call",function,args,kwargs])
    def wait(self,seconds:float):
        self.actions.append(["wait",seconds])
    def run(self,threaded:bool=False):
        current_delay = 0
        for act in self.actions:
            if act[0] == "call":
                if threaded:
                    delay(current_delay, act[1], *act[2], **act[3])
                else:
                    time.sleep(current_delay)
                    act[1](*act[2], **act[3])
            elif act[0] == "wait":
                if threaded:
                    current_delay += act[1]
                else:
                    time.sleep(act[1])

