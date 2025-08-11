# UNOverse (Proyecto UNO P2P)

Proyecto académico: Videojuego UNO multijugador en arquitectura P2P con Python 3.11, sockets TCP, threading, JSON, Pygame y SQLite.

Requisitos cubiertos:
- Autenticación local con SQLite (usuarios únicos, contraseñas hasheadas con PBKDF2).
- Lobby: crear/unirse con código de 6 dígitos, lista de jugadores, listo/no listo.
- Chat en tiempo real (lobby y juego).
- Lógica UNO completa (108 cartas, reglas clásicas y especiales).
- Sincronización P2P: estado compartido, turnos, jugadas, manejo básico de desconexiones.
- Protocolos en JSON, manejo de concurrencia con threads + Queue + Locks.

Ejecución rápida:
1) Requisitos
   - Python 3.11
   - pip install -r requirements.txt (o: pip install pygame)

2) Iniciar
   - cd proyecto_uno
   - python main.py

Notas de red y código de acceso:
- Un jugador debe actuar como Host. Generará un código de 6 dígitos y mostrará su IP local.
- Los demás ingresan IP del Host + código.
- Tras unirse, los peers intentan conectarse entre sí para formar malla completa.

Estructura:
proyecto_uno/
├── main.py
├── README.md (este archivo)
├── requirements.txt
├── ui/
│   ├── __init__.py
│   ├── login_ui.py
│   ├── lobby_ui.py
│   └── juego_ui.py
├── game/
│   ├── __init__.py
│   ├── cartas.py
│   ├── logica.py
│   └── chat.py
├── network/
│   ├── __init__.py
│   ├── servidor.py
│   ├── cliente.py
│   └── protocolo.py
├── utils/
│   ├── __init__.py
│   ├── mensajes.py
│   └── database.py
├── tests/
│   └── test_logica.py
└── assets/
    └── .gitkeep

Diagramas

Flujo alto nivel:

```mermaid
flowchart LR
  A[Login (SQLite)] --> B[Lobby]
  B -->|Crear Partida| H[Host]
  B -->|Unirse con código| P[Peer]
  H <--> P
  H <--> P2[Peer 2]
  P <--> P2
  B --> C[Chat Lobby]
  B --> D[Listo/No listo]
  D -->|Min 4| E[Iniciar Juego]
  E --> F[Juego UNO]
  F --> G[Sincronización P2P: jugadas/estado]
```

Protocolo de mensajes (JSON):
{
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "tipo": "jugada|chat|estado|conexion",
  "remitente": "nombre_jugador",
  "datos": { ... }
}

Estado compartido (resumen):
{
  "tipo_mensaje": "estado_juego",
  "nombre_jugador": "...",
  "cartas_en_mano": 7,
  "carta_superior": {"color":"rojo","valor":"5"},
  "cartas_jugadas": [ ... ],
  "turno_actual": "...",
  "acciones_especiales": "saltar|reversa|+2|+4|cambio_color",
  "ganador": null,
  "mensajes_chat": [ ... ],
  "eventos_red": "entrada|salida|errores"
}

Instrucciones de ejecución y pruebas
- Inicia como Host en el Lobby (botón Crear Partida) y comparte IP + código.
- Otros se unen con Unirse a Partida.
- Usa el chat para verificar conectividad.
- Requiere 4–6 jugadores para iniciar.
- Pruebas: python -m unittest tests/test_logica.py

Limitaciones prácticas
- Conectividad P2P real depende de la red (NAT/Firewall). Ideal en la misma LAN.
- UI minimalista (sin assets de cartas); renderiza rectángulos con texto.

Licencia: Uso académico.
