import threading
import time


def delay(seconds, func, *args, **kwargs):
    def wrapper():
        time.sleep(seconds)
        result = func(*args, **kwargs)
    thread = threading.Thread(target=wrapper)
    thread.start()
def after_delay(seconds, func, *args, **kwargs):
    res_container = []
    def wrapper():
        time.sleep(seconds)
        result = func(*args, **kwargs)
        res_container.append(result)

    thread = threading.Thread(target=wrapper)
    thread.start()
    thread.join()
    res = -1
    if len(res_container) > 0:
        res = res_container[0]
    return res


class Chain:
    def __init__(self, seconds:float,function,*args,**kwargs):
        self.current_delay = seconds
        result = after_delay(self.current_delay,function,*args,**kwargs)
        self.last = ["then",result]
    def then(self,seconds:float, function, *args, **kwargs):
        if self.last[0] == "then" or self.last[0] == "then_true":
            self.current_delay += seconds
            result = after_delay(self.current_delay, function, *args, **kwargs)
            self.last = ["then",result]
        return self
    def then_if(self,seconds:float, function, result, *args, **kwargs):
        if self.last[1] == result and self.last[0] == "then":
            self.current_delay += seconds
            newreslt = after_delay(self.current_delay,function,*args,**kwargs)
            self.last = ["then_true",newreslt]
        else:
            self.last = ["then_false", result]
        return self
    def then_else(self,seconds:float, function, *args, **kwargs):
        if self.last[0] == "then_false":
            self.current_delay += seconds
            result = after_delay(self.current_delay, function, *args, **kwargs)
            self.last = ["then",result]
        return self


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

