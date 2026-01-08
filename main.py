import pygame
import sys
import os
from maze_loader import load_next_level
from monsters import extract_monsters, move_monsters_random, player_hit_monster
from screens import Button, draw_menu, draw_rules, draw_game_over, draw_congrats


pygame.init()
pygame.mixer.init()

font = pygame.font.SysFont(None, 28)

TILE_SIZE = 16
HUD_HEIGHT = 40
FPS = 60

FLOOR_COLOR = (0, 0, 0)

MENU_WIDTH = 420
MENU_HEIGHT = 360

MOVE_DELAY = 150
MONSTER_MOVE_DELAY = 400

MENU_MUSIC = "assets/menu.mp3"
GAME_MUSIC = "assets/game.mp3"
GAME_OVER_SOUND = pygame.mixer.Sound("assets/bam.mp3")
WIN_SOUND = pygame.mixer.Sound("assets/win.mp3")

GAME_OVER_SOUND.set_volume(0.8)
WIN_SOUND.set_volume(0.8)

MENU, RULES, GAME, GAME_OVER, CONGRATS = "menu", "rules", "game", "game_over", "congrats"
state = MENU

player_anim_index = 0
player_anim_timer = 0
PLAYER_ANIM_DELAY = 120

monster_anim_index = 0
monster_anim_timer = 0
MONSTER_ANIM_DELAY = 180

maze, (player_row, player_col) = load_next_level()
ROWS = len(maze)
COLS = len(maze[0])

coins_left = sum(row.count(".") for row in maze)
monsters = extract_monsters(maze)

level = 1
VISIBLE_TILES = 11


def get_window_size():
    width = VISIBLE_TILES * TILE_SIZE
    height = VISIBLE_TILES * TILE_SIZE + HUD_HEIGHT
    return width, height

def resize_window():
    global WIDTH, HEIGHT, screen
    WIDTH, HEIGHT = get_window_size()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))


os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
WIDTH, HEIGHT = get_window_size()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")

wall_image = pygame.image.load("assets/sprite_0.png").convert_alpha()
wall_image = pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE))
clock = pygame.time.Clock()
last_move_time = 0
last_monster_move = 0

def load_animation(path_list, tile_size):
    frames = []
    for path in path_list:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (tile_size, tile_size))
        frames.append(img)
    return frames


def resize_menu_window():
    global screen, WIDTH, HEIGHT
    WIDTH, HEIGHT = MENU_WIDTH, MENU_HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))


def create_menu_buttons():
    cx = WIDTH // 2
    cy = HEIGHT // 2

    return [
        Button("Play",  (cx - 80, cy - 60, 160, 40)),
        Button("Rules", (cx - 80, cy,      160, 40)),
        Button("Exit",  (cx - 80, cy + 60, 160, 40)),
    ]

player_frames_right = load_animation(
    [f"assets/sprite_{i:02d}.png" for i in range(10)],
    TILE_SIZE
)

player_frames_left = [
    pygame.transform.flip(frame, True, False)
    for frame in player_frames_right
]

player_frames_up = [
    pygame.transform.rotate(frame, 90)
    for frame in player_frames_right
]

player_frames_down = [
    pygame.transform.rotate(frame, -90)
    for frame in player_frames_right
]

player_frames = {
    "left": player_frames_left,
    "right": player_frames_right,
    "up": player_frames_up,
    "down": player_frames_down,
}

monster_frames = load_animation(
    [f"assets/sprite{i}.png" for i in range(100, 116)],
    TILE_SIZE - 4
)

current_music = None

def play_music(path, volume=0.5):
    global current_music
    if current_music != path:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        current_music = path

game_over_played = False
win_played = False

def load_next_maze():
    global maze, player_row, player_col, coins_left
    global monsters, level, VISIBLE_TILES
    global WIDTH, HEIGHT, screen
    global last_move_time, last_monster_move
    global ROWS, COLS
    global state, game_over_played, win_played

    maze, start = load_next_level()

    if maze is None:
        if not win_played:
            pygame.mixer.music.stop()
            WIN_SOUND.play()
            win_played = True
        state = CONGRATS
        return

    level += 10

    ROWS = len(maze)
    COLS = len(maze[0])

    VISIBLE_TILES = min(9 + level * 2, min(ROWS, COLS))
    if VISIBLE_TILES % 2 == 0:
        VISIBLE_TILES -= 1

    player_row, player_col = start

    coins_left = sum(row.count(".") for row in maze)
    monsters = extract_monsters(maze)

    WIDTH = VISIBLE_TILES * TILE_SIZE
    HEIGHT = VISIBLE_TILES * TILE_SIZE + HUD_HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    now = pygame.time.get_ticks()
    last_move_time = now
    last_monster_move = now


def reset_game():
    global maze, player_row, player_col
    global coins_left, monsters
    global level, VISIBLE_TILES
    global last_move_time, last_monster_move
    global state
    global ROWS, COLS
    global game_over_played, win_played
    game_over_played = False
    win_played = False

    import maze_loader
    maze_loader.current_maze_index = 0

    level = 1
    VISIBLE_TILES = 11

    maze, (player_row, player_col) = load_next_level()

    ROWS = len(maze)
    COLS = len(maze[0])

    monsters = extract_monsters(maze)
    coins_left = sum(row.count(".") for row in maze)

    last_move_time = pygame.time.get_ticks()
    last_monster_move = pygame.time.get_ticks()

    resize_window()
    state = GAME


def get_view_window():
    center_r = ROWS // 2
    center_c = COLS // 2
    half = VISIBLE_TILES // 2
    return center_r - half, center_c - half


def draw_maze():
    r_start, c_start = get_view_window()

    for r in range(r_start, r_start + VISIBLE_TILES):
        for c in range(c_start, c_start + VISIBLE_TILES):
            if not (0 <= r < ROWS and 0 <= c < COLS):
                continue

            x = (c - c_start) * TILE_SIZE
            y = (r - r_start) * TILE_SIZE + HUD_HEIGHT

            if maze[r][c] == "#":
                screen.blit(wall_image, (x, y))
            else:
                pygame.draw.rect(screen, FLOOR_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
                if maze[r][c] == ".":
                    pygame.draw.circle(
                        screen,
                        (255, 200, 0),
                        (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                        TILE_SIZE // 5
                    )

def draw_player():
    r_start, c_start = get_view_window()
    if r_start <= player_row < r_start + VISIBLE_TILES and \
       c_start <= player_col < c_start + VISIBLE_TILES:

        x = (player_col - c_start) * TILE_SIZE
        y = (player_row - r_start) * TILE_SIZE + HUD_HEIGHT
        frames = player_frames[player_dir]
        frame = frames[player_anim_index % len(frames)]
        screen.blit(frame, (x, y))


def draw_monsters():
    r_start, c_start = get_view_window()
    for m in monsters:
        if r_start <= m["row"] < r_start + VISIBLE_TILES and \
           c_start <= m["col"] < c_start + VISIBLE_TILES:

            x = (m["col"] - c_start) * TILE_SIZE
            y = (m["row"] - r_start) * TILE_SIZE + HUD_HEIGHT
            screen.blit(monster_frames[monster_anim_index], (x + 2, y + 2))


def draw_hud():
    text = font.render(f"Coins left: {coins_left}", True, (0, 0, 0))
    screen.blit(text, (10, 10))


def run_game_tick():
    global player_row, player_col, coins_left
    global last_move_time, last_monster_move
    global pdr, pdc, player_dir
    global player_anim_index, player_anim_timer
    global monster_anim_index, monster_anim_timer
    global game_over_played
    global maze, state

    keys = pygame.key.get_pressed()
    now = pygame.time.get_ticks()

    if maze is None:
        return

    if now - player_anim_timer > PLAYER_ANIM_DELAY:
        frames = player_frames[player_dir]
        player_anim_index = (player_anim_index + 1) % len(frames)
        player_anim_timer = now

    if now - monster_anim_timer > MONSTER_ANIM_DELAY:
        monster_anim_index = (monster_anim_index + 1) % len(monster_frames)
        monster_anim_timer = now

    if keys[pygame.K_UP] and maze[player_row - 1][player_col] != "#":
        pdr, pdc = -1, 0
        player_dir = "up"
    elif keys[pygame.K_DOWN] and maze[player_row + 1][player_col] != "#":
        pdr, pdc = 1, 0
        player_dir = "down"
    elif keys[pygame.K_LEFT] and maze[player_row][player_col - 1] != "#":
        pdr, pdc = 0, -1
        player_dir = "left"
    elif keys[pygame.K_RIGHT] and maze[player_row][player_col + 1] != "#":
        pdr, pdc = 0, 1
        player_dir = "right"

    if now - last_monster_move > MONSTER_MOVE_DELAY:
        move_monsters_random(maze, monsters)
        last_monster_move = now
        if player_hit_monster(player_row, player_col, monsters):
            if not game_over_played:
                pygame.mixer.music.stop()
                GAME_OVER_SOUND.play()
                game_over_played = True
            state = GAME_OVER
            return

    if now - last_move_time > MOVE_DELAY:
        nr = player_row + pdr
        nc = player_col + pdc
        if maze[nr][nc] != "#":
            player_row, player_col = nr, nc

            if player_hit_monster(player_row, player_col, monsters):
                if not game_over_played:
                    pygame.mixer.music.stop()
                    GAME_OVER_SOUND.play()
                    game_over_played = True
                state = GAME_OVER
                return

            if maze[nr][nc] == ".":
                maze[nr][nc] = " "
                coins_left -= 1
                if coins_left == 0:
                    load_next_maze()

        last_move_time = now



pdr, pdc = 0, 1
player_dir = "left"
buttons = create_menu_buttons()
prev_state = None


while True:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    next_state = state

    for e in events:
        if state == MENU:
            result = draw_menu(screen, font, e, buttons)
            if result == GAME:
                reset_game()
                next_state = GAME
            else:
                next_state = result

        elif state == RULES:
            next_state = draw_rules(screen, font, e)

        elif state == GAME_OVER:
            next_state = draw_game_over(screen, font, e)

        elif state == CONGRATS:
            next_state = draw_congrats(screen, font, e)

        elif state == GAME:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                load_next_maze()
                next_state = state

    state = next_state

    if state == CONGRATS and prev_state != CONGRATS:
        resize_menu_window()

    if state != prev_state:
        if state in (MENU, RULES):
            play_music(MENU_MUSIC, volume=0.4)

        elif state == GAME:
            play_music(GAME_MUSIC, volume=0.6)

        elif state in (GAME_OVER, CONGRATS):
            pygame.mixer.music.stop()
            current_music = None

    if state == GAME:
        run_game_tick()

    if state != prev_state:
        if state in (MENU, RULES, GAME_OVER):
            resize_menu_window()
            buttons = create_menu_buttons()

    prev_state = state

    if state == GAME:
        screen.fill(FLOOR_COLOR)
        pygame.draw.rect(screen, (220, 220, 220), (0, 0, WIDTH, HUD_HEIGHT))
        draw_maze()
        draw_monsters()
        draw_player()
        draw_hud()

    elif state == MENU:
        draw_menu(screen, font, None, buttons)

    elif state == RULES:
        draw_rules(screen, font, None)

    elif state == GAME_OVER:
        draw_game_over(screen, font, None)

    elif state == CONGRATS:
        draw_congrats(screen, font, None)

    pygame.display.update()
    clock.tick(FPS)
