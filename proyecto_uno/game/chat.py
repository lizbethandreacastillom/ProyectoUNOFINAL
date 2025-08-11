from collections import deque
from typing import List


class ChatLog:
    def __init__(self, maxlen: int = 200):
        self.buffer = deque(maxlen=maxlen)

    def add(self, author: str, text: str):
        self.buffer.append(f"{author}: {text}")

    def tail(self, n: int) -> List[str]:
        return list(self.buffer)[-n:]
