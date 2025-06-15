import pygame
import tkinter as tk
import threading
import re
from tkinter import messagebox
from db import register_user, authenticate_user
import sys
from roulette import launch_roulette

pygame.init()

WIDTH, HEIGHT = 1000, 700
FONT = pygame.font.SysFont("arial", 24, bold=True)
WHITE = (255, 255, 255)
GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ruletka Kasyno - Menu i Gracze")

players = []
delete_buttons = []
add_button_rect = None
add_funds_rect = None

def draw_ui():
    global back_button_rect, add_button_rect, delete_buttons, add_funds_rect, play_button_rect

    screen.fill(GREEN)


    back_button_rect = pygame.Rect(20, 10, 100, 35)
    pygame.draw.rect(screen, GRAY, back_button_rect)
    back_text = FONT.render("Wróć", True, BLACK)
    screen.blit(back_text, (back_button_rect.x + 20, back_button_rect.y + 5))

    delete_buttons.clear()
    box_height = 45
    box_margin = 12

    for i, player in enumerate(players):
        y = 60 + i * (box_height + box_margin)


        pygame.draw.rect(screen, WHITE, (0, y, WIDTH, box_height))


        player_text = pygame.font.SysFont("arial", 26, bold=True).render(
            f"{player['nick']} - ${player['balance']}", True, BLACK
        )
        screen.blit(player_text, (20, y + (box_height - player_text.get_height()) // 2))


        usun_rect = pygame.Rect(WIDTH - 90, y + 7, 70, 30)
        pygame.draw.rect(screen, RED, usun_rect)
        usun_text = pygame.font.SysFont("arial", 18).render("usuń", True, WHITE)
        screen.blit(usun_text, (usun_rect.x + 10, usun_rect.y + 6))
        delete_buttons.append((usun_rect, player['nick']))


    if len(players) < 4:
        add_text = FONT.render("+ Dodaj nowego użytkownika", True, BLACK)
        text_width = add_text.get_width() + 20
        add_x = 20
        add_y = 60 + len(players) * (box_height + box_margin)
        add_button_rect = pygame.Rect(add_x, add_y, text_width, box_height)
        pygame.draw.rect(screen, GRAY, add_button_rect)
        screen.blit(add_text, (add_x + 10, add_y + (box_height - add_text.get_height()) // 2))
    else:
        add_button_rect = None


    add_funds_rect = pygame.Rect(40, HEIGHT - 70, 200, 50)
    pygame.draw.rect(screen, GRAY, add_funds_rect)
    add_funds_text = FONT.render("Dodaj pieniędzy", True, BLACK)
    screen.blit(add_funds_text, (add_funds_rect.x + 10, add_funds_rect.y + 10))


    play_button_rect = pygame.Rect(WIDTH - 190, HEIGHT - 70, 150, 50)
    pygame.draw.rect(screen, BLUE, play_button_rect)
    play_text = FONT.render("Gramy!", True, WHITE)
    screen.blit(play_text, (play_button_rect.x + 20, play_button_rect.y + 10))

    pygame.display.flip()


def show_add_funds_message():
    def run():
        win = tk.Tk()
        win.title("Dodaj pieniędzy")
        win.geometry("420x140")
        msg = (
            "Aby dodać pieniądze do portfela,\n"
            "zrób przelew na konto: 12 3456 7890 1234 5678 9012 3456\n"
            "W tytule przelewu wpisz swój NICK."
        )
        tk.Label(win, text=msg, justify="left").pack(padx=20, pady=20)
        tk.Button(win, text="OK", command=win.destroy).pack()
        win.mainloop()
    threading.Thread(target=run).start()

def open_user_action_window():
    def run():
        win = tk.Tk()
        win.title("Wybierz akcję")
        win.geometry("300x150")

        def open_login():
            win.destroy()
            open_login_window()

        def open_register():
            win.destroy()
            open_registration_window()

        tk.Label(win, text="Wybierz:").pack(pady=10)
        tk.Button(win, text="Zaloguj się", command=open_login).pack(pady=5)
        tk.Button(win, text="Zarejestruj się", command=open_register).pack(pady=5)
        win.mainloop()

    threading.Thread(target=run).start()

def open_login_window():
    def run():
        win = tk.Tk()
        win.title("Logowanie")
        win.geometry("300x200")

        def submit():
            global players
            nick = entry_nick.get().strip()
            password = entry_password.get().strip()

            if not nick or not password:
                messagebox.showerror("Błąd", "Wszystkie pola są wymagane.")
                return

            if any(p.get('nick') == nick for p in players):
                messagebox.showerror("Błąd", "Ten użytkownik jest już dodany.")
                return

            result = authenticate_user(nick, password)
            if result:
                players.append({'nick': result[0], 'balance': result[1]})
                win.destroy()
            else:
                messagebox.showerror("Błąd", "Nieprawidłowy nick lub hasło.")

        tk.Label(win, text="Nick:").pack()
        entry_nick = tk.Entry(win)
        entry_nick.pack()

        tk.Label(win, text="Hasło:").pack()
        entry_password = tk.Entry(win, show="*")
        entry_password.pack()

        tk.Button(win, text="Zaloguj", command=submit).pack(pady=10)
        win.mainloop()

    threading.Thread(target=run).start()


def open_registration_window():
    def run():
        win = tk.Tk()
        win.title("Rejestracja")
        win.geometry("300x350")

        def submit():
            global players
            nick = entry_nick.get().strip()
            if any(p.get('nick') == nick for p in players):
                messagebox.showerror("Błąd", "Ten użytkownik jest już dodany.")
                return
            imie = entry_imie.get().strip()
            nazwisko = entry_nazwisko.get().strip()
            pesel = entry_pesel.get().strip()
            password = entry_haslo.get().strip()

            if not all([nick, imie, nazwisko, pesel, password]):
                messagebox.showerror("Błąd", "Wszystkie pola są wymagane.")
                return

            if not re.match(r'^[A-Za-z0-9]+$', nick) or len(nick) > 12 or len(nick) < 5:
                messagebox.showerror("Błąd", "Nick musi mieć od 5 do 12 znaków i zawierać tylko litery i cyfry.")
                return

            if len(imie) > 15 or len(nazwisko) > 15:
                messagebox.showerror("Błąd", "Imię i nazwisko max 15 znaków.")
                return

            if re.search(r'\d', imie) or re.search(r'\d', nazwisko):
                messagebox.showerror("Błąd", "Imię i nazwisko nie mogą zawierać cyfr.")
                return

            if not pesel.isdigit() or len(pesel) != 11:
                messagebox.showerror("Błąd", "PESEL musi mieć dokładnie 11 cyfr.")
                return

            success, error = register_user(nick, imie, nazwisko, pesel, password)

            if success:
                if any(p['nick'] == nick for p in players):
                    messagebox.showerror("Błąd", "Ten użytkownik jest już dodany na listę.")
                    return

                players.append({'nick': nick, 'balance': 2000})
                win.destroy()

            else:
                messagebox.showerror("Błąd", error)

        tk.Label(win, text="Nick:").pack()
        entry_nick = tk.Entry(win)
        entry_nick.pack()

        tk.Label(win, text="Imię:").pack()
        entry_imie = tk.Entry(win)
        entry_imie.pack()

        tk.Label(win, text="Nazwisko:").pack()
        entry_nazwisko = tk.Entry(win)
        entry_nazwisko.pack()

        tk.Label(win, text="PESEL:").pack()
        entry_pesel = tk.Entry(win)
        entry_pesel.pack()

        tk.Label(win, text="Hasło:").pack()
        entry_haslo = tk.Entry(win, show="*")
        entry_haslo.pack()

        tk.Button(win, text="Zarejestruj", command=submit).pack(pady=10)
        win.mainloop()

    threading.Thread(target=run).start()

def main_loop():

    global players

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if add_button_rect and add_button_rect.collidepoint(mx, my):
                    if len(players) < 4:
                        open_user_action_window()

                elif add_funds_rect and add_funds_rect.collidepoint(mx, my):
                    show_add_funds_message()

                elif back_button_rect and back_button_rect.collidepoint(mx, my):
                    return

                elif play_button_rect and play_button_rect.collidepoint(mx, my):

                    removed = [p['nick'] for p in players if p['balance'] < 25]
                    players = [p for p in players if p['balance'] >= 25]

                    if removed:
                        msg = "Usunięto graczy z małą ilością pieniędzy:\n" + ", ".join(removed)
                        messagebox.showinfo("Usunięci gracze", msg)

                    if players:
                        launch_roulette(players)
                    else:
                        messagebox.showwarning("Brak graczy",
                                               "Wszyscy gracze mieli mniej niż 25 pieniędzy. Dodaj nowych.")

                for rect, nick in delete_buttons:

                    if rect.collidepoint(mx, my):
                        players[:] = [p for p in players if p['nick'] != nick]

        draw_ui()
    pygame.quit()