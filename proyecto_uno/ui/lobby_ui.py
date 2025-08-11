import pygame
from network.protocolo import generate_room_code
import socket

FONT_NAME = pygame.font.get_default_font()


def draw_text(surface, text, pos, size=26, color=(240, 240, 240)):
    font = pygame.font.SysFont(FONT_NAME, size)
    surface.blit(font.render(text, True, color), pos)


class TextInput:
    def __init__(self, rect, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.placeholder = placeholder
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                if len(self.text) < 24 and event.unicode.isprintable():
                    self.text += event.unicode

    def draw(self, surface):
        color = (80, 80, 80) if self.active else (60, 60, 60)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (120, 120, 120), self.rect, 2, border_radius=8)
        if not self.text:
            draw_text(surface, self.placeholder, (self.rect.x + 10, self.rect.y + 8), 22, (160, 160, 160))
        else:
            draw_text(surface, self.text, (self.rect.x + 10, self.rect.y + 8), 22)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run_lobby(screen, clock, peer, username):
    code = None
    host_ip = get_local_ip()
    message = ""

    inputs = {
        "host": TextInput((80, 160, 260, 40), "IP del Host"),
        "code": TextInput((360, 160, 120, 40), "Código 6 dígitos"),
    }

    buttons = {
        "create": pygame.Rect(80, 220, 180, 44),
        "join": pygame.Rect(280, 220, 180, 44),
        "ready": pygame.Rect(80, 600, 160, 44),
        "start": pygame.Rect(260, 600, 160, 44),
    }

    ready = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            for ti in inputs.values():
                ti.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["create"].collidepoint(event.pos):
                    code = generate_room_code()
                    ok, err = peer.start_host(host_ip)
                    message = f"Host en {host_ip}:{peer.port}, código {code}" if ok else (err or "Error host")
                if buttons["join"].collidepoint(event.pos):
                    if len(inputs["code"].text) == 6 and inputs["host"].text:
                        ok, err = peer.join(inputs["host"].text, username, inputs["code"].text)
                        message = "Unido al lobby" if ok else (err or "No se pudo unir")
                    else:
                        message = "Ingresa IP y código válido"
                if buttons["ready"].collidepoint(event.pos):
                    ready = not ready
                    peer.set_ready(ready)
                if buttons["start"].collidepoint(event.pos):
                    peer.try_start_game()

        # procesar mensajes entrantes (actualiza jugadores, chat)
        peer.pump_messages()

        screen.fill((18, 18, 22))
        draw_text(screen, "Lobby", (80, 80), 34)

        # panel conexión
        draw_text(screen, "Crear/Unirse a partida", (80, 120), 22, (180, 200, 255))
        for ti in inputs.values():
            ti.draw(screen)
        for name, rect in buttons.items():
            pygame.draw.rect(screen, (90, 120, 255), rect, border_radius=8)
            label = {
                "create": "Crear Partida",
                "join": "Unirse",
                "ready": f"{'Listo' if ready else 'No Listo'}",
                "start": "Iniciar (Host)",
            }[name]
            draw_text(screen, label, (rect.x + 18, rect.y + 10), 22)

        # lista jugadores
        pygame.draw.rect(screen, (35, 35, 45), (600, 120, 560, 400), border_radius=8)
        draw_text(screen, "Jugadores:", (620, 130), 24)
        y = 170
        for p in peer.get_players_snapshot():
            draw_text(screen, f"- {p['nombre']} {'✅' if p['ready'] else '⏳'}", (640, y), 22)
            y += 30

        # chat (sólo display en lobby; input se maneja en juego)
        pygame.draw.rect(screen, (35, 35, 45), (80, 300, 460, 200), border_radius=8)
        draw_text(screen, "Chat (ver consola)", (90, 310), 20, (200, 200, 200))

        if message:
            draw_text(screen, message, (80, 270), 20, (255, 200, 180))

        if peer.game_started:
            return True

        pygame.display.flip()
        clock.tick(60)

    return False
