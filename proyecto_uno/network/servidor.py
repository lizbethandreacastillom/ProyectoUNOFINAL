import socket
import threading
import queue
from typing import Dict, List, Tuple, Optional
from network.cliente import ClientConnection
from network.protocolo import encode_message, decode_message
from utils.mensajes import build_msg
from game.chat import ChatLog
from game.logica import GameState
from game.cartas import Card

DEFAULT_PORT = 5007


class PeerNode:
    def __init__(self, username: str, port: int = DEFAULT_PORT):
        self.username = username
        self.port = port
        self.is_host = False
        self.server_sock: Optional[socket.socket] = None
        self.accept_thread: Optional[threading.Thread] = None
        self.running = False

        self.connections: Dict[str, ClientConnection] = {}
        self.msg_queue: "queue.Queue[Tuple[dict, str]]" = queue.Queue()
        self.players: Dict[str, dict] = {}  # nombre -> {ready: bool}
        self.chat = ChatLog()
        self.game_state: Optional[GameState] = None
        self.game_started = False

        self.lock = threading.Lock()

    # --- Hosting y unión ---
    def start_host(self, host_ip: str) -> Tuple[bool, Optional[str]]:
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind((host_ip, self.port))
            self.server_sock.listen()
            self.running = True
            self.is_host = True
            self.players[self.username] = {"ready": False}
            self.accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self.accept_thread.start()
            return True, None
        except Exception as e:
            return False, str(e)

    def join(self, host_ip: str, username: str, code: str) -> Tuple[bool, Optional[str]]:
        try:
            sock = socket.create_connection((host_ip, self.port), timeout=5)
            self._wrap_socket(sock, f"{host_ip}:{self.port}")
            hello = build_msg("conexion", self.username, {"accion": "join", "code": code, "nombre": self.username})
            self._broadcast_one(hello, f"{host_ip}:{self.port}")
            return True, None
        except Exception as e:
            return False, str(e)

    def _accept_loop(self):
        while self.running:
            try:
                conn, addr = self.server_sock.accept()
                peer_id = f"{addr[0]}:{addr[1]}"
                self._wrap_socket(conn, peer_id)
            except Exception:
                break

    def _wrap_socket(self, sock: socket.socket, peer_id: str):
        def on_receive(msg: dict, from_peer: str):
            self.msg_queue.put((msg, from_peer))
        self.connections[peer_id] = ClientConnection(sock, peer_id, on_receive)

    # --- Mensajería ---
    def _broadcast_all(self, msg: dict):
        for pid, c in list(self.connections.items()):
            c.send(msg)

    def _broadcast_one(self, msg: dict, peer_id: str):
        c = self.connections.get(peer_id)
        if c:
            c.send(msg)

    def send_chat(self, text: str):
        msg = build_msg("chat", self.username, {"text": text})
        self.chat.add(self.username, text)
        self._broadcast_all(msg)

    def set_ready(self, ready: bool):
        self.players.setdefault(self.username, {"ready": False})
        self.players[self.username]["ready"] = ready
        msg = build_msg("conexion", self.username, {"accion": "ready", "estado": ready})
        self._broadcast_all(msg)

    def try_start_game(self):
        if not self.is_host:
            return
        if len(self.players) < 4:
            return
        if not all(p["ready"] for p in self.players.values()):
            return
        # crear estado y repartir
        import random
        seed = random.randint(0, 2**31 - 1)
        gs = GameState(seed)
        jugadores = list(self.players.keys())
        gs.preparar_partida(jugadores)
        self.game_state = gs
        self.game_started = True
        start_msg = build_msg("estado", self.username, {"accion": "start", "seed": seed, "state": gs.to_wire()})
        self._broadcast_all(start_msg)

    def await_initial_state(self):
        # esperar a recibir estado inicial desde host
        import time
        t0 = time.time()
        while self.game_state is None and time.time() - t0 < 15:
            self.pump_messages()
            time.sleep(0.05)

    def request_draw(self):
        msg = build_msg("jugada", self.username, {"accion": "robar"})
        self._broadcast_all(msg)

    def request_play(self, card: Card, chosen_color: str | None):
        msg = build_msg("jugada", self.username, {"accion": "jugar", "carta": {"color": card.color, "valor": card.valor}, "color": chosen_color})
        self._broadcast_all(msg)
        # validación local optimista; real se actualiza por estado
        return True, None

    # --- Procesamiento ---
    def pump_messages(self):
        # drenar cola
        while True:
            try:
                msg, src = self.msg_queue.get_nowait()
            except queue.Empty:
                break
            self._handle_message(msg, src)

    def _handle_message(self, msg: dict, src: str):
        tipo = msg.get("tipo")
        datos = msg.get("datos", {})
        remitente = msg.get("remitente")

        if tipo == "chat":
            txt = datos.get("text", "")
            self.chat.add(remitente, txt)
        elif tipo == "conexion":
            accion = datos.get("accion")
            if accion == "join":
                # registrar jugador
                nombre = datos.get("nombre") or remitente
                self.players[nombre] = {"ready": False}
                # enviar snapshot de jugadores y estado ready
                snap = build_msg("conexion", self.username, {"accion": "snapshot", "players": self.players})
                self._broadcast_all(snap)
            elif accion == "ready":
                self.players[remitente] = self.players.get(remitente, {"ready": False})
                self.players[remitente]["ready"] = bool(datos.get("estado"))
            elif accion == "snapshot":
                self.players = datos.get("players", {})
        elif tipo == "estado":
            if datos.get("accion") == "start":
                st = datos.get("state")
                if st:
                    self.game_state = GameState.from_wire(st)
                    self.game_started = True
            elif datos.get("accion") == "sync" and self.game_state:
                st = datos.get("state")
                if st:
                    self.game_state = GameState.from_wire(st)
        elif tipo == "jugada" and self.game_state:
            accion = datos.get("accion")
            jugador = remitente
            if accion == "robar":
                if self.game_state.turno_actual == jugador:
                    self.game_state.robar(jugador, 1)
                    self._sync_state()
            elif accion == "jugar":
                c = datos.get("carta")
                carta = Card(c["color"], c["valor"]) if c else None
                color = datos.get("color")
                ok, err = self.game_state.validar_jugada(jugador, carta, color)
                if ok:
                    self.game_state.aplicar_jugada(jugador, carta, color)
                    self._sync_state()

    def _sync_state(self):
        msg = build_msg("estado", self.username, {"accion": "sync", "state": self.game_state.to_wire()})
        self._broadcast_all(msg)

    # --- Utilidades UI ---
    def get_players_snapshot(self) -> List[dict]:
        return [{"nombre": n, **info} for n, info in self.players.items()]

    def chat_tail(self, n: int):
        return self.chat.tail(n)
