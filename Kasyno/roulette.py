def launch_roulette(players):
    import pygame
    import sys
    import random
    import time

    pygame.init()

    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ruletka – Tylko kręcenie")

    FONT = pygame.font.SysFont("arial", 24, bold=True)
    GREEN = (0, 100, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    BLUE = (0, 0, 255)

    clock = pygame.time.Clock()

    roulette_img = pygame.image.load("ruletka1.png").convert_alpha()
    arrow_img = pygame.image.load("strzalka.png").convert_alpha()

    RADIUS = 260
    roulette_img = pygame.transform.smoothscale(roulette_img, (RADIUS, RADIUS))
    arrow_img = pygame.transform.smoothscale(arrow_img, (40, 60))

    numbers = ["0", "28", "9", "26", "30", "11", "7", "20", "32", "17", "5", "22", "34", "15", "3",
               "24", "36", "13", "1", "00", "27", "10", "25", "29", "12", "8", "19", "31", "18",
               "6", "21", "33", "16", "4", "23", "35", "14", "2"]
    angle_per_number = 360 / len(numbers)

    current_angle = 0
    target_angle = 0
    spinning = False
    spin_speed = 0
    initial_speed = 0
    slowdown_distance = 0
    result_number = ""
    show_result_time = None

    inputs = [{"text": "", "active": False, "rect": None} for _ in players]

    def get_angle_for_number(number):
        index = numbers.index(number)
        return (index * angle_per_number) % 360

    def draw_ui():
        screen.fill(GREEN)

        back_rect = pygame.Rect(20, 20, 100, 35)
        pygame.draw.rect(screen, GRAY, back_rect)
        screen.blit(FONT.render("Wróć", True, BLACK), (30, 25))

        for i, player in enumerate(players):
            y = 80 + i * 40
            screen.blit(FONT.render(player["nick"], True, WHITE), (40, y))
            screen.blit(FONT.render(f"${player['balance']}", True, WHITE), (200, y))

            input_rect = pygame.Rect(360, y - 5, 100, 30)
            pygame.draw.rect(screen, WHITE, input_rect)
            pygame.draw.rect(screen, BLACK, input_rect, 2)
            input_text = FONT.render(inputs[i]["text"], True, BLACK)
            screen.blit(input_text, (input_rect.x + 5, input_rect.y + 5))
            inputs[i]["rect"] = input_rect

        angle = (current_angle + 180) % 360
        rotated = pygame.transform.rotozoom(roulette_img, angle, 1)
        rect = rotated.get_rect(center=(WIDTH - 330, HEIGHT // 2 - 40))
        screen.blit(rotated, rect)
        screen.blit(arrow_img, (WIDTH - 350, HEIGHT // 2 - RADIUS // 2 - 77))

        pygame.draw.rect(screen, GRAY, (WIDTH - 300, HEIGHT - 130, 200, 40))
        msg = FONT.render(f"Wypadło: {result_number}" if result_number else "Co wypadło", True, WHITE)
        screen.blit(msg, (WIDTH - 290, HEIGHT - 125))

        spin_btn = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 80, 120, 45)
        pygame.draw.rect(screen, BLUE, spin_btn)
        screen.blit(FONT.render("Kręć", True, WHITE), (spin_btn.x + 30, spin_btn.y + 10))

        return back_rect, spin_btn

    running = True
    while running:
        back_btn, spin_btn = draw_ui()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if back_btn.collidepoint(mx, my):
                    return

                input_active = False
                for inp in inputs:
                    if inp["rect"].collidepoint(mx, my):
                        inp["active"] = True
                        input_active = True
                    else:
                        inp["active"] = False

                if spin_btn.collidepoint(mx, my) and not spinning:
                    valid_inputs = [inp["text"] for inp in inputs if inp["text"] in numbers]
                    if valid_inputs:
                        result_number = random.choice(numbers)
                        win_angle = get_angle_for_number(result_number)
                        relative_angle = (360 - (current_angle % 360) + win_angle) % 360
                        total_rotation = 7 * 360 + relative_angle
                        target_angle = current_angle + total_rotation
                        spin_speed = 40
                        initial_speed = spin_speed
                        slowdown_distance = total_rotation
                        spinning = True
                        show_result_time = None

            elif event.type == pygame.KEYDOWN:
                for inp in inputs:
                    if inp["active"]:
                        if event.key == pygame.K_BACKSPACE:
                            inp["text"] = inp["text"][:-1]
                        elif len(inp["text"]) < 3 and (event.unicode.isdigit() or event.unicode == '0'):
                            inp["text"] += event.unicode

        if spinning:
            remaining = target_angle - current_angle
            if remaining > 0:
                slowdown_factor = remaining / slowdown_distance
                spin_speed = max(1, initial_speed * slowdown_factor)
                current_angle += spin_speed
            else:
                spinning = False
                current_angle = target_angle % 360
                show_result_time = time.time() + 1.5

        if show_result_time and time.time() >= show_result_time:
            show_result_time = None

            for inp in inputs:
                inp["text"] = ""

        pygame.display.flip()
        clock.tick(60)
