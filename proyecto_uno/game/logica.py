from __future__ import annotations
from typing import Dict, List, Optional
import random
from game.cartas import Card, crear_mazo, COLORES


class GameState:
    def __init__(self, seed: Optional[int]):
        if seed is not None:
            random.seed(seed)
        self.players: List[str] = []
        self.hands: Dict[str, List[Card]] = {}
        self.mazo: List[Card] = crear_mazo()
        self.descartes: List[Card] = []
        self.turno_idx: int = 0
        self.direccion: int = 1
        self.color_actual: Optional[str] = None
        self.ganador: Optional[str] = None

    @property
    def carta_superior(self) -> Optional[Card]:
        return self.descartes[-1] if self.descartes else None

    @property
    def turno_actual(self) -> Optional[str]:
        if not self.players:
            return None
        return self.players[self.turno_idx % len(self.players)]

    def preparar_partida(self, jugadores: List[str], cartas_iniciales: int = 7):
        self.players = jugadores[:]
        for j in self.players:
            self.hands[j] = [self.mazo.pop() for _ in range(cartas_iniciales)]
        # sacar primera carta que no sea comodín
        top = self.mazo.pop()
        while top.es_comodin:
            self.mazo.insert(random.randint(0, len(self.mazo)), top)
            top = self.mazo.pop()
        self.descartes.append(top)
        self.color_actual = top.color

    def robar(self, jugador: str, n: int = 1):
        for _ in range(n):
            if not self.mazo:
                # reciclar descartes sin la última
                to_mix = self.descartes[:-1]
                random.shuffle(to_mix)
                self.mazo = to_mix
                self.descartes = [self.descartes[-1]]
            self.hands[jugador].append(self.mazo.pop())

    def validar_jugada(self, jugador: str, carta: Card, color_elegido: Optional[str]):
        if self.ganador:
            return False, "La partida terminó"
        if jugador != self.turno_actual:
            return False, "No es tu turno"
        if carta not in self.hands[jugador]:
            return False, "No tienes esa carta"
        if carta.es_comodin:
            if carta.valor == "+4":
                # +4 permitido siempre en esta implementación base
                return True, None
            if carta.valor == "comodin":
                return True, None
        ok = carta.compatible_con(self.carta_superior, self.color_actual)
        return (True, None) if ok else (False, "No compatible")

    def aplicar_jugada(self, jugador: str, carta: Card, color_elegido: Optional[str]):
        self.hands[jugador].remove(carta)
        self.descartes.append(carta)
        # actualizar color actual
        if carta.es_comodin:
            if color_elegido not in COLORES:
                color_elegido = random.choice(COLORES)
            self.color_actual = color_elegido
        else:
            self.color_actual = carta.color
        # efectos especiales
        salto = False
        avance = 1
        if carta.valor == "salta":
            salto = True
        elif carta.valor == "reversa":
            self.direccion *= -1
        elif carta.valor == "+2":
            idx_obj = (self.turno_idx + self.direccion) % len(self.players)
            self.robar(self.players[idx_obj], 2)
            salto = True
        elif carta.valor == "+4":
            idx_obj = (self.turno_idx + self.direccion) % len(self.players)
            self.robar(self.players[idx_obj], 4)
            salto = True
        # comprobar victoria
        if len(self.hands[jugador]) == 0:
            self.ganador = jugador
        # avanzar turno
        self._avanzar_turno(2 if salto else 1)

    def _avanzar_turno(self, pasos: int = 1):
        for _ in range(pasos):
            self.turno_idx = (self.turno_idx + self.direccion) % len(self.players)

    def estado_publico(self, para_jugador: str):
        return {
            "players": self.players,
            "turno_actual": self.turno_actual,
            "carta_superior": None if not self.carta_superior else {"color": self.carta_superior.color, "valor": self.carta_superior.valor},
            "color_actual": self.color_actual,
            "mano": len(self.hands.get(para_jugador, [])),
            "conteos": {j: len(self.hands[j]) for j in self.players},
            "ganador": self.ganador,
        }

    @staticmethod
    def from_wire(data: dict) -> "GameState":
        gs = GameState(seed=None)
        gs.players = data["players"]
        gs.hands = {
            j: [Card(c["color"], c["valor"]) for c in data["hands"][j]] for j in data["hands"]
        }
        gs.mazo = [Card(c["color"], c["valor"]) for c in data["mazo"]]
        gs.descartes = [Card(c["color"], c["valor"]) for c in data["descartes"]]
        gs.turno_idx = data["turno_idx"]
        gs.direccion = data["direccion"]
        gs.color_actual = data["color_actual"]
        gs.ganador = data["ganador"]
        return gs

    def to_wire(self) -> dict:
        return {
            "players": self.players,
            "hands": {j: [{"color": c.color, "valor": c.valor} for c in self.hands[j]] for j in self.hands},
            "mazo": [{"color": c.color, "valor": c.valor} for c in self.mazo],
            "descartes": [{"color": c.color, "valor": c.valor} for c in self.descartes],
            "turno_idx": self.turno_idx,
            "direccion": self.direccion,
            "color_actual": self.color_actual,
            "ganador": self.ganador,
        }
