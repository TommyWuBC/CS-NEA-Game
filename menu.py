import pygame
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Menu")
clock = pygame.time.Clock()

# Game State variables
username = ""
current_state = "main_menu"
selected_level = 0

class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        font = pygame.font.Font(None, 36)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

def draw_text(text, size, color, surface, x, y):
    font = pygame.font.Font(None, size)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    surface.blit(text_surf, text_rect)

def main_menu():
    global current_state
    buttons = [
        Button("Start Game", 300, 200, 200, 50, lambda: globals().update(current_state="username_input")),
        Button("Settings", 300, 260, 200, 50, lambda: print("Settings")),
        Button("Leaderboard", 300, 320, 200, 50, lambda: print("Leaderboard")),
        Button("Exit", 300, 380, 200, 50, lambda: [pygame.quit(), sys.exit()])
    ]

    return buttons

def username_input():
    global username, current_state
    input_box = pygame.Rect(250, 250, 300, 50)
    active = True
    cursor_visible = True
    last_cursor_toggle = pygame.time.get_ticks()
    cursor_blink_interval = 500  # Milliseconds between cursor blinks

    while active:
        current_time = pygame.time.get_ticks()
        
        if current_time - last_cursor_toggle > cursor_blink_interval:
            cursor_visible = not cursor_visible
            last_cursor_toggle = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                cursor_visible = True
                last_cursor_toggle = current_time
                
                if event.key == pygame.K_RETURN:
                    active = False
                    current_state = "level_select"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode

        screen.fill(WHITE)
        draw_text("Enter Username:", 40, BLACK, screen, SCREEN_WIDTH//2, 200)
        
        pygame.draw.rect(screen, GRAY, input_box)
        
        font = pygame.font.Font(None, 32)
        txt_surface = font.render(username, True, BLACK)
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 15))
        
        if cursor_visible:
            cursor_x = input_box.x + 14 + txt_surface.get_width()
            cursor_y = input_box.y + 15
            cursor_height = txt_surface.get_height()
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + cursor_height), 2)

        pygame.display.flip()
        clock.tick(FPS)

def level_select():
    global selected_level, current_state
    buttons = [
        Button("Level 1", 100, 200, 120, 50, lambda: globals().update(selected_level=1)),
        Button("Level 2", 250, 200, 120, 50, lambda: globals().update(selected_level=2)),
        Button("Level 3", 400, 200, 120, 50, lambda: globals().update(selected_level=3)),
        Button("Level 4", 550, 200, 120, 50, lambda: globals().update(selected_level=4)),
        Button("Level 5", 700, 200, 120, 50, lambda: globals().update(selected_level=5)),
    ]

    while True:
        screen.fill(WHITE)
        draw_text(f"Welcome {username}! Choose Level:", 40, BLACK, screen, SCREEN_WIDTH//2, 150)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.rect.collidepoint(pos):
                        button.callback()
                        print(f"Starting Level {selected_level}")  # Replace with actual game start
                        current_state = "main_menu"
                        return

        clock.tick(FPS)

# Main game loop
while True:
    screen.fill(WHITE)

    if current_state == "main_menu":
        buttons = main_menu()
    elif current_state == "username_input":
        username_input()
    elif current_state == "level_select":
        level_select()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and current_state == "main_menu":
            pos = pygame.mouse.get_pos()
            for button in buttons:
                if button.rect.collidepoint(pos):
                    button.callback()

    if current_state == "main_menu":
        for button in buttons:
            button.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)