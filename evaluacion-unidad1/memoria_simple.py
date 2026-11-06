from collections import deque

class SimpleMemory:
    def __init__(self, max_messages:int=10):
        self.history = deque(maxlen=max_messages)
        self.rango = None

    def add(self, role:str, content:str):
        self.history.append({"role": role, "content": content})

    def messages(self):
        return list(self.history)

    def set_rango(self, time_ini:str, time_end:str):
        self.rango = (time_ini, time_end)
