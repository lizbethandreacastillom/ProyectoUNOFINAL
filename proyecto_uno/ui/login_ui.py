import pygame
from utils.database import register_user, login_user

FONT_NAME = pygame.font.get_default_font()


def draw_text(surface, text, pos, size=28, color=(240, 240, 240)):
    font = pygame.font.SysFont(FONT_NAME, size)
    surface.blit(font.render(text, True, color), pos)


class TextInput:
    def __init__(self, rect, placeholder="", password=False):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.placeholder = placeholder
        self.password = password
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
        shown = ("*" * len(self.text)) if self.password else self.text
        if not shown:
            draw_text(surface, self.placeholder, (self.rect.x + 10, self.rect.y + 8), 22, (160, 160, 160))
        else:
            draw_text(surface, shown, (self.rect.x + 10, self.rect.y + 8), 22)


def run_login(screen, clock, db_path):
    username_input = TextInput((490, 260, 300, 44), "Usuario")
    password_input = TextInput((490, 320, 300, 44), "Contraseña", password=True)
    message = ""

    buttons = {
        "login": pygame.Rect(490, 380, 140, 44),
        "register": pygame.Rect(650, 380, 140, 44),
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            username_input.handle_event(event)
            password_input.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["login"].collidepoint(event.pos):
                    ok, err = login_user(db_path, username_input.text.strip(), password_input.text)
                    if ok:
                        return username_input.text.strip()
                    message = err or "Credenciales inválidas"
                if buttons["register"].collidepoint(event.pos):
                    ok, err = register_user(db_path, username_input.text.strip(), password_input.text)
                    message = "Registro exitoso" if ok else (err or "Error de registro")

        screen.fill((24, 24, 28))
        draw_text(screen, "UNOverse - Login", (500, 180), 36)
        username_input.draw(screen)
        password_input.draw(screen)

        for name, rect in buttons.items():
            pygame.draw.rect(screen, (90, 120, 255), rect, border_radius=8)
            draw_text(screen, "Login" if name == "login" else "Registro", (rect.x + 24, rect.y + 10), 24)

        if message:
            draw_text(screen, message, (490, 440), 20, (255, 180, 180))

        pygame.display.flip()
        clock.tick(60)

    return None
