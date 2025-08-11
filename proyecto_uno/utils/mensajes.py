from datetime import datetime


def build_msg(tipo: str, remitente: str, datos: dict) -> dict:
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo,
        "remitente": remitente,
        "datos": datos or {},
    }
