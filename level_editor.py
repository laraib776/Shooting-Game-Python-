import csv
import json
import os
import re
import sys

import pygame


pygame.init()

APP_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = getattr(sys, "_MEIPASS", APP_DIR)

def resource_path(relative_path):
    return os.path.join(RESOURCE_DIR, relative_path)

def writable_path(relative_path):
    return os.path.join(APP_DIR, relative_path)


OVERRIDE_LEVELS_FILE = writable_path("edited_levels.json")


def load_level_overrides():
    if not os.path.exists(OVERRIDE_LEVELS_FILE):
        return {}
    try:
        with open(OVERRIDE_LEVELS_FILE, "r") as jsonfile:
            return json.load(jsonfile)
    except (json.JSONDecodeError, OSError):
        return {}


def save_level_overrides(overrides):
    with open(OVERRIDE_LEVELS_FILE, "w") as jsonfile:
        json.dump(overrides, jsonfile)

SCREEN_WIDTH = 820
SCREEN_HEIGHT = 470
ROWS = 16
COLUMNS = 150
TILE_TYPES = 21
TILE_SIZE = 25
MAP_WIDTH = 600
PANEL_WIDTH = SCREEN_WIDTH - MAP_WIDTH
MAP_HEIGHT = ROWS * TILE_SIZE
FPS = 60

BG = (135, 206, 235)
PANEL_BG = (143, 203, 119)
GRID = (235, 245, 245)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 235, 89)
RED = (214, 72, 61)
GREEN = (78, 191, 93)
DARK = (34, 44, 48)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level Editor")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16, bold=True)
font_small = pygame.font.SysFont("Arial", 13, bold=True)


def load_image(path, alpha=True):
    image = pygame.image.load(resource_path(path))
    return image.convert_alpha() if alpha else image.convert()


def scale_to_screen_width(img):
    scale = MAP_WIDTH / img.get_width()
    return pygame.transform.smoothscale(img, (MAP_WIDTH, int(img.get_height() * scale)))


sky_img = pygame.transform.smoothscale(load_image("img/Background/sky_cloud.png"), (MAP_WIDTH, MAP_HEIGHT))
mountain_img = scale_to_screen_width(load_image("img/Background/mountain.png"))
pine1_img = scale_to_screen_width(load_image("img/Background/pine1.png"))
pine2_img = scale_to_screen_width(load_image("img/Background/pine2.png"))

tile_images = []
tile_thumbs = []
for tile_id in range(TILE_TYPES):
    img = load_image(f"img/Tile/{tile_id}.png")
    tile_images.append(pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)))
    tile_thumbs.append(pygame.transform.smoothscale(img, (32, 32)))


def make_empty_level():
    return [[-1 for _ in range(COLUMNS)] for _ in range(ROWS)]


def available_levels():
    levels = set()
    for folder in (APP_DIR, RESOURCE_DIR):
        if os.path.isdir(folder):
            for name in os.listdir(folder):
                match = re.fullmatch(r"level(\d+)_data\.csv", name)
                if match:
                    levels.add(int(match.group(1)))
    return sorted(levels)


def next_level_number():
    levels = available_levels()
    return (levels[-1] + 1) if levels else 1


def level_exists(level):
    return os.path.exists(writable_path(f"level{level}_data.csv")) or os.path.exists(resource_path(f"level{level}_data.csv"))


def load_level(level):
    data = make_empty_level()
    overrides = load_level_overrides()
    if str(level) in overrides:
        return overrides[str(level)]
    writable_file = writable_path(f"level{level}_data.csv")
    resource_file = resource_path(f"level{level}_data.csv")
    filename = writable_file if os.path.exists(writable_file) else resource_file
    if not os.path.exists(filename):
        return data
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row_index, row in enumerate(reader):
            if row_index >= ROWS:
                break
            for col_index, tile in enumerate(row[:COLUMNS]):
                data[row_index][col_index] = int(tile)
    return data


def save_level(data, level):
    overrides = load_level_overrides()
    overrides[str(level)] = data
    save_level_overrides(overrides)


def can_save_level(data):
    has_player = any(15 in row for row in data)
    has_exit = any(20 in row for row in data)
    return has_player and has_exit


def ensure_player_and_exit(data):
    added = []
    player_positions = [(row_index, col_index) for row_index, row in enumerate(data) for col_index, tile in enumerate(row) if tile == 15]
    invalid_player = player_positions and (
        player_positions[0][1] < 3
        or player_positions[0][1] > COLUMNS - 4
        or player_positions[0][0] < 2
        or player_positions[0][0] > ROWS - 2
    )
    if not player_positions or invalid_player:
        for row_index, col_index in player_positions:
            data[row_index][col_index] = -1
        data[14][6] = 15
        added.append("player")
    if not any(20 in row for row in data):
        data[14][145] = 20
        added.append("exit")
    return added


class TextButton:
    def __init__(self, rect, text, colour=RED):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.colour = colour
        self.clicked = False

    def draw(self):
        action = False
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        hover = self.rect.collidepoint(mouse_pos)
        colour = tuple(min(255, c + 24) for c in self.colour) if hover else self.colour

        pygame.draw.rect(screen, colour, self.rect, border_radius=3)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=3)
        label = font_small.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

        if hover and mouse_down and not self.clicked:
            action = True
            self.clicked = True
        if not mouse_down:
            self.clicked = False
        return action


def draw_layer(img, scroll, y):
    width = img.get_width()
    offset = int(scroll % width)
    for x in range(-1, (MAP_WIDTH // width) + 3):
        screen.blit(img, ((x * width) - offset, y))


def draw_background(scroll):
    screen.fill(BG, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    draw_layer(sky_img, scroll * 0.15, 0)
    draw_layer(mountain_img, scroll * 0.35, MAP_HEIGHT - mountain_img.get_height() - 110)
    draw_layer(pine1_img, scroll * 0.6, MAP_HEIGHT - pine1_img.get_height() - 55)
    draw_layer(pine2_img, scroll * 0.85, MAP_HEIGHT - pine2_img.get_height())


def draw_grid(scroll):
    start_col = scroll // TILE_SIZE
    x_offset = -(scroll % TILE_SIZE)
    for col in range(start_col, min(COLUMNS + 1, start_col + (MAP_WIDTH // TILE_SIZE) + 3)):
        x = ((col - start_col) * TILE_SIZE) + x_offset
        pygame.draw.line(screen, GRID, (x, 0), (x, MAP_HEIGHT), 1)
    for row in range(ROWS + 1):
        y = row * TILE_SIZE
        pygame.draw.line(screen, GRID, (0, y), (MAP_WIDTH, y), 1)


def draw_tiles(data, scroll):
    start_col = scroll // TILE_SIZE
    end_col = min(COLUMNS, start_col + (MAP_WIDTH // TILE_SIZE) + 3)
    for row in range(ROWS):
        for col in range(start_col, end_col):
            tile = data[row][col]
            if tile >= 0:
                screen.blit(tile_images[tile], (col * TILE_SIZE - scroll, row * TILE_SIZE))


def draw_palette(selected_tile):
    pygame.draw.rect(screen, PANEL_BG, (MAP_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT))
    title = font.render("TILES", True, DARK)
    screen.blit(title, (MAP_WIDTH + 18, 14))

    palette_rects = []
    x_start = MAP_WIDTH + 28
    y_start = 48
    gap = 14
    for tile_id, thumb in enumerate(tile_thumbs):
        col = tile_id % 3
        row = tile_id // 3
        rect = pygame.Rect(x_start + col * (32 + gap), y_start + row * (32 + gap), 32, 32)
        palette_rects.append(rect)
        if tile_id == selected_tile:
            pygame.draw.rect(screen, YELLOW, rect.inflate(8, 8), border_radius=3)
        screen.blit(thumb, rect)

    notes = [
        "Left click: place",
        "Right click: erase",
        "A/D or arrows: scroll",
        "Mouse wheel: scroll",
    ]
    for index, note in enumerate(notes):
        label = font_small.render(note, True, DARK)
        screen.blit(label, (MAP_WIDTH + 18, 382 + index * 18))
    return palette_rects


def make_load_dropdown_buttons(start_index):
    buttons = []
    levels = available_levels()
    visible_levels = levels[start_index:start_index + 5]
    for index, level_number in enumerate(visible_levels):
        x = 384
        y = MAP_HEIGHT - 126 + index * 24
        buttons.append((level_number, TextButton((x, y, 70, 22), f"Level {level_number}", colour=(69, 123, 157))))
    return buttons, levels


def draw_bottom_bar(current_level, scroll):
    pygame.draw.rect(screen, PANEL_BG, (0, MAP_HEIGHT, MAP_WIDTH, SCREEN_HEIGHT - MAP_HEIGHT))
    level_text = font.render(f"Editing level: {current_level}", True, WHITE)
    screen.blit(level_text, (12, MAP_HEIGHT + 10))
    scroll_text = font_small.render(f"Scroll: {scroll // TILE_SIZE}/{COLUMNS - (MAP_WIDTH // TILE_SIZE)}", True, WHITE)
    screen.blit(scroll_text, (12, MAP_HEIGHT + 34))


current_level = available_levels()[0] if available_levels() else 1
world_data = load_level(current_level)
selected_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
max_scroll = (COLUMNS * TILE_SIZE) - MAP_WIDTH
message = f"Editing level {current_level}"
message_timer = 180
last_map_click_time = 0
last_map_click_cell = None
DOUBLE_CLICK_TIME = 350
suppress_place_until_mouse_up = False
show_load_dropdown = False
load_dropdown_start = 0

save_button = TextButton((300, MAP_HEIGHT + 16, 70, 30), "SAVE")
load_button = TextButton((384, MAP_HEIGHT + 16, 70, 30), "LOAD")
clear_button = TextButton((468, MAP_HEIGHT + 16, 70, 30), "CLEAR", colour=(75, 133, 194))
done_button = TextButton((552, MAP_HEIGHT + 16, 56, 30), "DONE", colour=GREEN)

run = True
while run:
    clock.tick(FPS)

    if scroll_left:
        scroll = max(0, scroll - 12)
    if scroll_right:
        scroll = min(max_scroll, scroll + 12)

    draw_background(scroll)
    draw_tiles(world_data, scroll)
    draw_grid(scroll)
    draw_bottom_bar(current_level, scroll)
    palette_rects = draw_palette(selected_tile)

    if message_timer > 0:
        message_img = font_small.render(message, True, DARK)
        screen.blit(message_img, (150, MAP_HEIGHT + 36))
        message_timer -= 1

    if save_button.draw():
        added = ensure_player_and_exit(world_data)
        save_level(world_data, current_level)
        if added:
            message = f"Saved level {current_level} and added {'/'.join(added)}"
        else:
            message = f"Saved level {current_level}"
        message_timer = 180
    if load_button.draw():
        show_load_dropdown = not show_load_dropdown
    if clear_button.draw():
        world_data = make_empty_level()
        show_load_dropdown = False
        message = f"Cleared level {current_level}"
        message_timer = 180
    if done_button.draw():
        ensure_player_and_exit(world_data)
        save_level(world_data, current_level)
        run = False

    dropdown_buttons = []
    if show_load_dropdown:
        dropdown_buttons, dropdown_levels = make_load_dropdown_buttons(load_dropdown_start)
        dropdown_height = 5 * 24 + 8
        pygame.draw.rect(screen, (118, 174, 99), (378, MAP_HEIGHT - 130, 84, dropdown_height), border_radius=6)
        pygame.draw.rect(screen, WHITE, (378, MAP_HEIGHT - 130, 84, dropdown_height), 2, border_radius=6)
        if load_dropdown_start > 0:
            up_img = font_small.render("^", True, WHITE)
            screen.blit(up_img, (456, MAP_HEIGHT - 128))
        if load_dropdown_start + 5 < len(dropdown_levels):
            down_img = font_small.render("v", True, WHITE)
            screen.blit(down_img, (456, MAP_HEIGHT - 24))
        for level_number, level_button in dropdown_buttons:
            if level_button.draw():
                if level_exists(level_number):
                    world_data = load_level(level_number)
                    message = f"Loaded level {level_number}"
                else:
                    message = "Only existing levels can be edited"
                current_level = level_number
                scroll = 0
                show_load_dropdown = False
                message_timer = 180

    mouse_pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()
    if 0 <= mouse_pos[0] < MAP_WIDTH and 0 <= mouse_pos[1] < MAP_HEIGHT:
        col = (mouse_pos[0] + scroll) // TILE_SIZE
        row = mouse_pos[1] // TILE_SIZE
        if 0 <= row < ROWS and 0 <= col < COLUMNS:
            if mouse_buttons[0] and not suppress_place_until_mouse_up:
                world_data[row][col] = selected_tile
            elif mouse_buttons[2]:
                world_data[row][col] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                if show_load_dropdown and 378 <= event.pos[0] <= 462 and MAP_HEIGHT - 130 <= event.pos[1] <= MAP_HEIGHT - 2:
                    load_dropdown_start = max(0, load_dropdown_start - 1)
                else:
                    scroll = max(0, scroll - TILE_SIZE * 2)
            elif event.button == 5:
                if show_load_dropdown and 378 <= event.pos[0] <= 462 and MAP_HEIGHT - 130 <= event.pos[1] <= MAP_HEIGHT - 2:
                    max_start = max(0, len(available_levels()) - 4)
                    load_dropdown_start = min(max_start, load_dropdown_start + 1)
                else:
                    scroll = min(max_scroll, scroll + TILE_SIZE * 2)
            elif event.button == 1:
                clicked_palette = False
                for tile_id, rect in enumerate(palette_rects):
                    if rect.collidepoint(event.pos):
                        selected_tile = tile_id
                        clicked_palette = True
                if not clicked_palette and 0 <= event.pos[0] < MAP_WIDTH and 0 <= event.pos[1] < MAP_HEIGHT:
                    col = (event.pos[0] + scroll) // TILE_SIZE
                    row = event.pos[1] // TILE_SIZE
                    now = pygame.time.get_ticks()
                    clicked_cell = (row, col)
                    if clicked_cell == last_map_click_cell and now - last_map_click_time <= DOUBLE_CLICK_TIME:
                        world_data[row][col] = -1
                        last_map_click_cell = None
                        suppress_place_until_mouse_up = True
                    else:
                        last_map_click_cell = clicked_cell
                    last_map_click_time = now
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                suppress_place_until_mouse_up = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                scroll_left = True
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                scroll_right = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_s:
                added = ensure_player_and_exit(world_data)
                save_level(world_data, current_level)
                if added:
                    message = f"Saved level {current_level} and added {'/'.join(added)}"
                else:
                    message = f"Saved level {current_level}"
                message_timer = 180
            if event.key == pygame.K_l:
                levels = available_levels()
                if current_level in levels:
                    world_data = load_level(current_level)
                    message = f"Loaded level {current_level}"
                elif levels:
                    current_level = levels[-1]
                    world_data = load_level(current_level)
                    message = f"Loaded latest level {current_level}"
                message_timer = 180
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                scroll_left = False
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                scroll_right = False

    pygame.display.update()

pygame.quit()
