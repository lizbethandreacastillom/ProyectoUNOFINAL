import socket
import threading
from typing import Callable
from network.protocolo import encode_message


class ClientConnection:
    def __init__(self, sock: socket.socket, peer_id: str, on_receive: Callable[[dict, str], None]):
        self.sock = sock
        self.peer_id = peer_id
        self.on_receive = on_receive
        self.running = True
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()
        self.lock = threading.Lock()

    def _reader(self):
        file = self.sock.makefile("r", encoding="utf-8")
        while self.running:
            line = file.readline()
            if not line:
                break
            try:
                import json
                msg = json.loads(line)
                self.on_receive(msg, self.peer_id)
            except Exception:
                continue
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass

    def send(self, msg: dict):
        data = (encode_message(msg["tipo"], msg["remitente"], msg["datos"]) + "\n").encode("utf-8")
        with self.lock:
            try:
                self.sock.sendall(data)
            except Exception:
                self.running = False

    def close(self):
        self.running = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except Exception:
            pass
