import pygame
import sys
from player_screen import main_loop
from db import init_db
init_db()
pygame.init()


WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ruletka Kasyno - Menu")


font = pygame.font.SysFont(None, 48)


WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 100, 0)


running = True
while running:
    screen.fill(GREEN)


    title_text = font.render("Witamy w Ruletce Kasyno", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))


    start_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 60)
    pygame.draw.rect(screen, BLUE, start_btn)

    start_text = font.render("START", True, WHITE)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - 15))

    # tu zdarzenia
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn.collidepoint(event.pos):
                main_loop()

    pygame.display.flip()

pygame.quit()
sys.exit()