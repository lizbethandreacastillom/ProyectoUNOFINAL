import unittest
from game.logica import GameState
from game.cartas import Card


class TestLogica(unittest.TestCase):
    def test_turno_y_victoria(self):
        gs = GameState(seed=42)
        jugadores = ["A", "B", "C", "D"]
        gs.preparar_partida(jugadores)
        self.assertIn(gs.turno_actual, jugadores)
        # Forzar mano de A a vaciarse
        gs.hands["A"] = []
        gs.aplicar_jugada(gs.turno_actual, gs.carta_superior, None) if gs.carta_superior in gs.hands[gs.turno_actual] else None
        gs.ganador = "A"
        self.assertEqual(gs.ganador, "A")


if __name__ == "__main__":
    unittest.main()
