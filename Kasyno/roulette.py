import pygame
import sys
import random
import time

import tkinter as tk
from tkinter import messagebox
import pygame_gui

from pygame_gui.elements import UITextEntryLine, UIDropDownMenu
from db import update_balance

def show_message(title, message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()

def setup_inputs(players, manager):
    inputs = []
    for i, player in enumerate(players):
        y = 80 + i * 40
        input_box = UITextEntryLine(pygame.Rect(360, y - 5, 100, 30), manager)
        inputs.append({"player": player, "input": input_box})
    return inputs

def validate_inputs(inputs, numbers, selected_bet):
    for inp in inputs:
        player = inp["player"]
        if player["balance"] < 25:
            return False, f"{player['nick']} ma mniej niż 25 zł!"
        if player["balance"] < selected_bet:
            return False, f"{player['nick']} nie ma {selected_bet} zł!"
        if inp["input"].get_text() not in numbers:
            return False, f"{player['nick']} wpisał złą liczbę!"
    return True, ""

def start_spin(current_angle, result_number, get_angle_for_number):
    win_angle = get_angle_for_number(result_number)
    relative_angle = (360 - (current_angle % 360) + win_angle) % 360

    total_rotation = 7 * 360 + relative_angle
    target_angle = current_angle + total_rotation
    return target_angle, total_rotation

def handle_spin_result(inputs, result_number, bet_amount):
    winners = []
    for inp in inputs:
        player = inp["player"]
        chosen = player["chosen"]
        if chosen == result_number:
            win = bet_amount * 36
            player["balance"] += win
            winners.append((player["nick"], win))
        else:
            player["balance"] -= bet_amount
        update_balance(player["nick"], player["balance"])
        inp["input"].set_text("")
    return winners

def launch_roulette(players):
    pygame.init()
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ruletka – Tylko kręcenie")
    FONT = pygame.font.SysFont("arial", 24, bold=True)

    GREEN, WHITE, BLACK, GRAY, BLUE = (0,100,0), (255,255,255), (0,0,0), (200,200,200), (0,0,255)

    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
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

    def get_selected_bet():
        raw = bet_dropdown.selected_option
        return int(raw[0]) if isinstance(raw, tuple) else int(raw)

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

        angle = (current_angle + 180) % 360
        rotated = pygame.transform.rotozoom(roulette_img, angle, 1)
        rect = rotated.get_rect(center=(WIDTH - 330, HEIGHT // 2 - 40))
        screen.blit(rotated, rect)
        screen.blit(arrow_img, (WIDTH - 350, HEIGHT // 2 - RADIUS // 2 - 77))

        result_rect = pygame.Rect(WIDTH // 2 + 200, HEIGHT - 140, 200, 45)
        pygame.draw.rect(screen, GRAY, result_rect)
        text = f"Wypadło: {result_number}" if not spinning and result_number else "Co wypadło"
        msg = FONT.render(text, True, WHITE)
        screen.blit(msg, msg.get_rect(center=result_rect.center))

        spin_btn = pygame.Rect(WIDTH // 2 - 140, HEIGHT - 140, 120, 45)
        pygame.draw.rect(screen, BLUE, spin_btn)
        screen.blit(FONT.render("Kręć", True, WHITE), (spin_btn.x + 30, spin_btn.y + 10))

        return back_rect, spin_btn

    current_angle = 0
    target_angle = 0
    spinning = False
    initial_speed = 0
    slowdown_distance = 0
    result_number = ""
    show_result_time = None

    inputs = setup_inputs(players, manager)
    bet_dropdown = UIDropDownMenu(["500", "100", "50", "25"], "100",
                                  pygame.Rect(WIDTH // 2 + 80, HEIGHT - 140, 100, 45), manager)

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        back_btn, spin_btn = draw_ui()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if back_btn.collidepoint(mx, my):
                    return

                if spin_btn.collidepoint(mx, my) and not spinning:
                    selected_bet = get_selected_bet()
                    valid, msg = validate_inputs(inputs, numbers, selected_bet)

                    if valid:

                        for inp in inputs:
                            inp["player"]["chosen"] = inp["input"].get_text()
                        result_number = random.choice(numbers)
                        target_angle, slowdown_distance = start_spin(current_angle, result_number, get_angle_for_number)
                        spin_speed = 40

                        initial_speed = spin_speed
                        spinning = True
                        show_result_time = None

                    else:
                        show_message("Błąd", msg)
            manager.process_events(event)

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
            bet_amount = get_selected_bet()
            winners = handle_spin_result(inputs, result_number, bet_amount)

            if winners:
                msg = "\n".join([f"{nick} wygrał {amount} zł" for nick, amount in winners])

            else:
                msg = "Nikt nie wygrał"
            show_message("Wyniki rundy", msg)

        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()