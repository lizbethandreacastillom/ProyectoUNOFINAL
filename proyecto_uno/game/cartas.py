from dataclasses import dataclass
import random
from typing import List

COLORES = ["rojo", "amarillo", "verde", "azul"]
VALORES = [str(i) for i in range(10)] + ["salta", "reversa", "+2"]

@dataclass(frozen=True)
class Card:
    color: str  # rojo, amarillo, verde, azul, negro (comodines)
    valor: str  # 0-9, salta, reversa, +2, comodin, +4

    @property
    def es_comodin(self):
        return self.color == "negro"

    def compatible_con(self, otra: "Card", color_actual: str | None):
        if self.es_comodin:
            return True
        if otra.es_comodin:
            return self.color == color_actual
        return self.color == otra.color or self.valor == otra.valor


def crear_mazo() -> List[Card]:
    mazo: List[Card] = []
    # numeradas: 0 una vez por color, 1-9 dos veces por color
    for c in COLORES:
        mazo.append(Card(c, "0"))
        for v in [str(i) for i in range(1, 10)] + ["salta", "reversa", "+2"]:
            mazo.append(Card(c, v))
            mazo.append(Card(c, v))
    # comodines
    for _ in range(4):
        mazo.append(Card("negro", "comodin"))
        mazo.append(Card("negro", "+4"))
    random.shuffle(mazo)
    return mazo
