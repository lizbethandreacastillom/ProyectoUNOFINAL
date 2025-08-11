import json
import time
import random

MESSAGE_TYPES = {"jugada", "chat", "estado", "conexion", "control"}


def now_str():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def generate_room_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def encode_message(tipo: str, remitente: str, datos: dict) -> str:
    if tipo not in MESSAGE_TYPES:
        raise ValueError("tipo de mensaje inválido")
    payload = {
        "timestamp": now_str(),
        "tipo": tipo,
        "remitente": remitente,
        "datos": datos or {},
    }
    return json.dumps(payload, ensure_ascii=False)


def decode_message(line: str) -> dict | None:
    try:
        obj = json.loads(line)
        if not {"timestamp", "tipo", "remitente", "datos"}.issubset(obj.keys()):
            return None
        return obj
    except Exception:
        return None
