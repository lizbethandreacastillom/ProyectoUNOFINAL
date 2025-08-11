from ui.login_ui import run_login
from ui.lobby_ui import run_lobby
from ui.juego_ui import run_game
from utils.database import init_db
from network.servidor import PeerNode
import pygame

DB_PATH = "unoverse.db"


def main():
    pygame.init()
    pygame.display.set_caption("UNOverse - UNO P2P")
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    init_db(DB_PATH)

    username = run_login(screen, clock, DB_PATH)
    if not username:
        pygame.quit()
        return

    peer = PeerNode(username)
    lobby_result = run_lobby(screen, clock, peer, username)
    if not lobby_result:
        pygame.quit()
        return

    run_game(screen, clock, peer, username)
    pygame.quit()


if __name__ == "__main__":
    main()
