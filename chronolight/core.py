import threading
import time
import asyncio
import inspect

from packaging.utils import canonicalize_name

def delayed(seconds):
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay(seconds, func, *args, **kwargs)
        return wrapper
    return decorator

def delay(seconds, func, *args, **kwargs):
    cancelled = False
    if inspect.iscoroutinefunction(func):
        async def async_wrapper():
            await asyncio.sleep(seconds)
            if not cancelled:
                await func(*args, **kwargs)
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(async_wrapper())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            threading.Thread(target=lambda: loop.run_until_complete(async_wrapper())).start()
    else:
        def sync_wrapper():
            time.sleep(seconds)
            if not cancelled:
                func(*args, **kwargs)

        threading.Thread(target=sync_wrapper).start()
    class Delayfunc:
        def __init__(self):
            pass
        def cancel(self):
            nonlocal cancelled
            cancelled = True
            return self
    return Delayfunc()
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

def on_error(func=None, callback=None, *args, **kwargs):
    if func:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if callback:
                try:
                    callback(e)
                except:
                    pass
    else:
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if callback:
                        try:
                            callback(e)
                        except:
                            pass
            return wrapper
        return decorator
    return None


class EventEmitter:
    def __init__(self):
        self.events = {}

    def on(self, name: str, func):
        if name not in self.events:
            self.events[name] = []
        self.events[name].append(func)
        return self

    def emit(self, name: str, *args, **kwargs):
        if name in self.events:
            split = name.split(";")
            for func in self.events[split[0]]:
                func(*args, **kwargs)
                if len(split) > 1:
                    if split[1] == "once":
                        self.events[split[0]] = []
        return self
    def once(self, name:str, func):
        if name not in self.events:
            self.events[name + ";once"] = []
        self.events[name].append(func)
        return self
    def off(self,name:str,func):
        if self.events[name]:
            self.events[name].remove(func)


class Chain:
    def __init__(self, seconds:float,function,logging:bool = False,*args,**kwargs):
        self.logging = logging
        self.current_delay = seconds
        result = after_delay(self.current_delay,function,*args,**kwargs)
        self.last = ["then",result]
        if self.logging:
            print(f"activated: {str(function)}")
            print(f"new last:{self.last}")
    def then(self,seconds:float, function, *args, **kwargs):
        if self.last[0] == "then" or self.last[0] == "then_true":
            self.current_delay += seconds
            result = after_delay(self.current_delay, function, *args, **kwargs)
            self.last = ["then",result]
            if self.logging:
                print(f"activated: {str(function)}")
                print(f"new last:{self.last}")
        return self
    def then_if(self,seconds:float, function, result, *args, **kwargs):
        if self.last[1] == result and self.last[0] == "then":
            self.current_delay += seconds
            newreslt = after_delay(self.current_delay,function,*args,**kwargs)
            self.last = ["then_true",newreslt]
            if self.logging:
                print(f"activated: {str(function)}")
                print(f"new last:{self.last}")
        else:
            self.last = ["then_false", result]
            if self.logging:
                print(f"activated: {str(function)}")
                print(f"new last:{self.last}")
        return self
    def then_else(self,seconds:float, function, *args, **kwargs):
        if self.last[0] == "then_false":
            self.current_delay += seconds
            result = after_delay(self.current_delay, function, *args, **kwargs)
            self.last = ["then",result]
            if self.logging:
                print(f"activated: {str(function)}")
                print(f"new last:{self.last}")
        return self




class Timeline:
    def __init__(self, logging:bool = False):
        self.eventemitter = None
        self.actions = []
        self.logging = logging
        self.paused = False
        self.last = ""
    def call(self,function,*args,**kwargs):
        self.actions.append(["call",function,args,kwargs])
        if self.logging:
            print(f"added action: [call,{str(function)},{str(args)},{str(kwargs)}]")
        if self.eventemitter:
            self.eventemitter.emit("call",function,*args,**kwargs)
    def wait(self,seconds:float):
        self.actions.append(["wait",seconds])
        if self.logging:
            print(f"added action: [wait,{str(seconds)}] ")
        if self.eventemitter:
            self.eventemitter.emit("wait",seconds)
    def run(self,threaded:bool=False):
        if self.eventemitter:
            self.eventemitter.emit("run",threaded)
        current_delay = 0
        everyflag = True
        def trueeveryflag():
            nonlocal everyflag
            everyflag = True
        for act in self.actions:
            while self.paused:
                time.sleep(0.1)
            if act[0] == "call":
                if threaded:
                    delay(current_delay, act[1], *act[2], **act[3])
                    if self.logging:
                        print(f"called threaded: {str(act[1])}")
                else:
                    time.sleep(current_delay)
                    act[1](*act[2], **act[3])
                    if self.logging:
                        print(f"called: {str(act[1])}")
            elif act[0] == "wait":
                if threaded:
                    current_delay += act[1]
                    if self.logging:
                        print(f"waited threaded: {str(act[1])}")
                else:
                    time.sleep(act[1])
                    if self.logging:
                        print(f"waited: {str(act[1])}")
            elif act[0] == "every":
                if not act[5]:
                    act[5] = 1
                while True:
                    if act[1]():
                        break
                    if threaded:
                        if everyflag:
                            everyflag = False
                            current_delay += 1
                            delay(act[5],trueeveryflag)
                            if act[2]:
                                delay(1, act[2], *act[3], **act[4])
                    else:
                        if act[2]:
                            act[2](*act[3],**act[4])
                        time.sleep(act[5])

    def repeat(self,times:int=2,threaded:bool=False):
        for i in range(times):
            self.run(threaded)
    def reverse(self):
        self.actions.reverse()
    def pause(self):
        self.paused = True
    def resume(self):
        self.paused = False
    def visualise(self):
        current_delay = 0
        print("Timeline visualise:")
        for act in self.actions:
            if act[0] == "wait":
                text = f"{str(current_delay)} {str(act[0])}: {str(act[1])}"
                if len(act) > 2:
                    text += f", {str(act[2])} ({str(act[3])})"
                print(text)
                current_delay += act[1]
            else:
                text = f"{str(current_delay)} {str(act[0])}: {str(act[1])}"
                if len(act) > 2:
                    text += f", {str(act[2])} ({str(act[3])})"
                print(text)
        print("Visualise end")
    def copy(self):
        newTimeline = Timeline()
        newTimeline.logging = self.logging
        newTimeline.actions = self.actions
        return newTimeline
    def add_eventemitter(self,eventemitter):
        self.eventemitter = eventemitter
    def every(self,seconds:float,func=None,times:int=1,until=None,*args,**kwargs):
        if not until:
            for _ in range(times):
                if func:
                    self.call(func, *args, **kwargs)
                self.wait(seconds)
        else:
            self.actions.append(["every",until,func,args,kwargs,seconds])
        return self

    def clear(self):
        self.actions.clear()
        return self
    def length(self):
        return len(self.actions)


class AsyncTimeline:
    def __init__(self, logging: bool = False):
        self.eventemitter = None
        self.actions = []
        self.logging = logging
        self.paused = False
        self.last = ""

    async def call(self, function, *args, **kwargs):
        self.actions.append(["call", function, args, kwargs])
        if self.logging:
            print(f"added action: [call,{str(function)},{str(args)},{str(kwargs)}]")
        if self.eventemitter:
            self.eventemitter.emit("call", function, *args, **kwargs)

    async def wait(self, seconds: float):
        self.actions.append(["wait", seconds])
        if self.logging:
            print(f"added action: [wait,{str(seconds)}] ")
        if self.eventemitter:
            self.eventemitter.emit("wait", seconds)

    async def run(self, threaded: bool = False):
        if self.eventemitter:
            self.eventemitter.emit("run", threaded)
        current_delay = 0
        everyflag = True

        def trueeveryflag():
            nonlocal everyflag
            everyflag = True

        for act in self.actions:
            while self.paused:
                time.sleep(0.1)
            if act[0] == "call":
                if threaded:
                    delay(current_delay, act[1], *act[2], **act[3])
                    if self.logging:
                        print(f"called threaded: {str(act[1])}")
                else:
                    time.sleep(current_delay)
                    act[1](*act[2], **act[3])
                    if self.logging:
                        print(f"called: {str(act[1])}")
            elif act[0] == "wait":
                if threaded:
                    current_delay += act[1]
                    if self.logging:
                        print(f"waited threaded: {str(act[1])}")
                else:
                    time.sleep(act[1])
                    if self.logging:
                        print(f"waited: {str(act[1])}")
            elif act[0] == "every":
                if not act[5]:
                    act[5] = 1
                while True:
                    if act[1]():
                        break
                    if threaded:
                        if everyflag:
                            everyflag = False
                            current_delay += 1
                            delay(act[5], trueeveryflag)
                            if act[2]:
                                delay(1, act[2], *act[3], **act[4])
                    else:
                        if act[2]:
                            act[2](*act[3], **act[4])
                        time.sleep(act[5])

    async def repeat(self, times: int = 2, threaded: bool = False):
        for i in range(times):
            await self.run(threaded)

    async def reverse(self):
        self.actions.reverse()

    async def pause(self):
        self.paused = True

    async def resume(self):
        self.paused = False

    async def visualise(self):
        current_delay = 0
        print("Timeline visualise:")
        for act in self.actions:
            if act[0] == "wait":
                text = f"{str(current_delay)} {str(act[0])}: {str(act[1])}"
                if len(act) > 2:
                    text += f", {str(act[2])} ({str(act[3])})"
                print(text)
                current_delay += act[1]
            else:
                text = f"{str(current_delay)} {str(act[0])}: {str(act[1])}"
                if len(act) > 2:
                    text += f", {str(act[2])} ({str(act[3])})"
                print(text)
        print("Visualise end")

    async def copy(self):
        newTimeline = Timeline()
        newTimeline.logging = self.logging
        newTimeline.actions = self.actions
        return newTimeline

    async def add_eventemitter(self, eventemitter):
        self.eventemitter = eventemitter

    async def every(self, seconds: float, func=None, times: int = 1, until=None, *args, **kwargs):
        if not until:
            for _ in range(times):
                if func:
                    await self.call(func, *args, **kwargs)
                await self.wait(seconds)
        else:
            self.actions.append(["every", until, func, args, kwargs, seconds])
        return self

    async def clear(self):
        self.actions.clear()
        return self
    async def length(self):
        return len(self.actions)

