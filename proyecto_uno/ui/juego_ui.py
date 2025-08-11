import pygame
from game.logica import GameState
from game.cartas import Card

FONT_NAME = pygame.font.get_default_font()


def draw_text(surface, text, pos, size=22, color=(240, 240, 240)):
    font = pygame.font.SysFont(FONT_NAME, size)
    surface.blit(font.render(text, True, color), pos)


class ChatInput:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                txt = self.text.strip()
                self.text = ""
                return txt
            else:
                if len(self.text) < 140 and event.unicode.isprintable():
                    self.text += event.unicode
        return None

    def draw(self, surface):
        pygame.draw.rect(surface, (60, 60, 60), self.rect, border_radius=8)
        pygame.draw.rect(surface, (120, 120, 120), self.rect, 2, border_radius=8)
        shown = self.text if self.text else "Escribe mensaje..."
        color = (220, 220, 220) if self.text else (150, 150, 150)
        draw_text(surface, shown, (self.rect.x + 8, self.rect.y + 8), 20, color)


def card_rect(i, total):
    x_start = 60
    spacing = 80
    return pygame.Rect(x_start + i * spacing, 550, 70, 110)


def draw_card(surface, rect, card: Card, highlight=False):
    color_map = {
        "rojo": (200, 70, 70),
        "amarillo": (200, 180, 70),
        "verde": (70, 170, 90),
        "azul": (70, 100, 200),
        "negro": (40, 40, 40),
    }
    c = color_map.get(card.color, (90, 90, 90))
    pygame.draw.rect(surface, c, rect, border_radius=10)
    if highlight:
        pygame.draw.rect(surface, (255, 255, 255), rect, 3, border_radius=10)
    draw_text(surface, str(card.valor), (rect.x + 10, rect.y + 10), 26)


def run_game(screen, clock, peer, username):
    # Esperar estado inicial del Host si no lo somos
    if not peer.is_host:
        peer.await_initial_state()
    state = peer.game_state or GameState(seed=None)

    chat_in = ChatInput((980, 660, 280, 36))
    selected = None
    message = ""

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            sent = chat_in.handle_event(event)
            if sent:
                peer.send_chat(sent)
            if event.type == pygame.MOUSEBUTTONDOWN:
                # seleccionar carta
                hand = state.hands.get(username, [])
                for i, card in enumerate(hand):
                    if card_rect(i, len(hand)).collidepoint(event.pos):
                        selected = i if selected != i else None
                # botones
                if pygame.Rect(60, 500, 140, 36).collidepoint(event.pos):
                    peer.request_draw()
                if pygame.Rect(220, 500, 140, 36).collidepoint(event.pos):
                    if selected is not None:
                        c = hand[selected]
                        chosen_color = None
                        if c.color == "negro":
                            # elegir color simple (rojo, amarillo, verde, azul)
                            chosen_color = "rojo"
                        ok, err = peer.request_play(c, chosen_color)
                        message = "" if ok else (err or "Jugada inválida")
                        selected = None

        # procesar red
        peer.pump_messages()
        state = peer.game_state or state

        screen.fill((20, 24, 28))
        draw_text(screen, f"Turno: {state.turno_actual}", (60, 40), 28)
        draw_text(screen, f"Color actual: {state.color_actual}", (280, 40), 24)

        # carta superior
        pygame.draw.rect(screen, (35, 35, 45), (500, 140, 200, 260), border_radius=12)
        if state.carta_superior:
            draw_card(screen, pygame.Rect(530, 170, 140, 200), state.carta_superior)
        draw_text(screen, "Mazo", (760, 220), 22)

        # mano del jugador
        hand = state.hands.get(username, [])
        for i, card in enumerate(hand):
            r = card_rect(i, len(hand))
            draw_card(screen, r, card, highlight=(i == selected))

        # jugadores y contadores
        y = 120
        for p in state.players:
            if p == username:
                continue
            cnt = len(state.hands.get(p, []))
            draw_text(screen, f"{p}: {cnt} cartas", (60, y), 22)
            y += 28

        # chat panel
        pygame.draw.rect(screen, (35, 35, 45), (960, 60, 300, 620), border_radius=10)
        draw_text(screen, "Chat", (970, 70), 22)
        y = 100
        for msg in peer.chat_tail(18):
            draw_text(screen, msg, (970, y), 18, (220, 220, 220))
            y += 20
        chat_in.draw(screen)

        # botones
        pygame.draw.rect(screen, (90, 120, 255), (60, 500, 140, 36), border_radius=8)
        draw_text(screen, "Robar", (100, 508), 22)
        pygame.draw.rect(screen, (90, 120, 255), (220, 500, 140, 36), border_radius=8)
        draw_text(screen, "Jugar", (260, 508), 22)

        if state.ganador:
            draw_text(screen, f"Ganador: {state.ganador}", (500, 420), 28, (255, 220, 180))

        if message:
            draw_text(screen, message, (60, 460), 20, (255, 200, 180))

        pygame.display.flip()
        clock.tick(60)
