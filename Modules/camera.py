from Objects.player import Player

import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("First Person Bike Racing Game")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
GRAY = (70, 70, 70)
DARK_GRAY = (35, 35, 35)
GREEN = (40, 160, 60)
SKY = (90, 190, 255)
RED = (220, 30, 30)
YELLOW = (255, 220, 30)
BLUE = (40, 160, 255)
NAVY = (18, 28, 52)
ROAD_GLOW = (255, 150, 60)
MINT = (88, 235, 195)
SAND = (242, 210, 132)
PANEL = (16, 22, 38)
PANEL_ALT = (28, 37, 60)
PANEL_EDGE = (255, 255, 255)

font_big = pygame.font.SysFont("verdana", 62, bold=True)
font_med = pygame.font.SysFont("verdana", 34, bold=True)
font_small = pygame.font.SysFont("verdana", 22, bold=True)
font_tiny = pygame.font.SysFont("verdana", 18, bold=True)

game_state = "menu"

speed = 0
score = 0
distance = 0
boost = 100
player_x = 0
road_offset = 0
enemies = []
spawn_timer = 0


def draw_text(text, font, color, x, y, center=True):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(img, rect)


def draw_panel(x, y, w, h, accent=BLUE, alpha=230):
    panel_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, (*PANEL, alpha), (0, 0, w, h), border_radius=24)
    pygame.draw.rect(panel_surface, (*accent, 65), (8, 8, w - 16, h - 16), 2, border_radius=18)
    pygame.draw.rect(panel_surface, (*PANEL_EDGE, 230), (0, 0, w, h), 3, border_radius=24)
    screen.blit(panel_surface, (x, y))


def draw_progress_bar(x, y, w, h, value, maximum, fill_color, label):
    pygame.draw.rect(screen, WHITE, (x, y, w, h), 2, border_radius=10)
    fill_width = int((max(0, min(value, maximum)) / maximum) * (w - 4))
    pygame.draw.rect(screen, fill_color, (x + 2, y + 2, fill_width, h - 4), border_radius=8)
    draw_text(label, font_tiny, WHITE, x, y - 24, center=False)


def button(text, x, y, w, h, accent=ROAD_GLOW):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    rect = pygame.Rect(x, y, w, h)
    hovered = rect.collidepoint(mouse)

    if hovered:
        pygame.draw.rect(screen, accent, rect, border_radius=20)
        pygame.draw.rect(screen, WHITE, rect, 4, border_radius=20)
        if click:
            pygame.time.delay(150)
            return True
    else:
        pygame.draw.rect(screen, PANEL_ALT, rect, border_radius=20)
        pygame.draw.rect(screen, WHITE, rect, 3, border_radius=20)

    text_color = BLACK if hovered else WHITE
    draw_text(text, font_small, text_color, x + w // 2, y + h // 2)
    return False


def reset_game():
    global speed, score, distance, boost, player_x, road_offset, enemies, spawn_timer
    speed = 60
    score = 0
    distance = 0
    boost = 100
    player_x = 0
    road_offset = 0
    enemies = []
    spawn_timer = 0


def draw_background():
    for y in range(HEIGHT):
        blend = y / HEIGHT
        color = (
            int(18 + (90 - 18) * blend),
            int(28 + (190 - 28) * blend),
            int(52 + (255 - 52) * blend),
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    pygame.draw.circle(screen, (255, 240, 120), (1050, 100), 52)
    pygame.draw.circle(screen, (255, 250, 210), (1050, 100), 70, 2)

    for i in range(8):
        x = i * 180 - 80
        pygame.draw.polygon(screen, (80, 130, 170), [
            (x, 260), (x + 140, 120), (x + 300, 260)
        ])

    pygame.draw.rect(screen, GREEN, (0, 260, WIDTH, HEIGHT - 260))
    pygame.draw.rect(screen, (32, 110, 55), (0, 260, WIDTH, 18))


def draw_road():
    global road_offset

    horizon_y = 260
    bottom_y = HEIGHT
    road_top_w = 160
    road_bottom_w = 900

    center = WIDTH // 2 + player_x

    road_poly = [
        (center - road_top_w // 2, horizon_y),
        (center + road_top_w // 2, horizon_y),
        (center + road_bottom_w // 2, bottom_y),
        (center - road_bottom_w // 2, bottom_y)
    ]

    pygame.draw.polygon(screen, DARK_GRAY, road_poly)
    pygame.draw.polygon(screen, ROAD_GLOW, road_poly, 3)

    pygame.draw.line(screen, WHITE, road_poly[0], road_poly[3], 6)
    pygame.draw.line(screen, WHITE, road_poly[1], road_poly[2], 6)

    road_offset += speed * 0.08
    if road_offset > 80:
        road_offset = 0

    for i in range(18):
        y = horizon_y + i * 45 + road_offset
        scale = (y - horizon_y) / (bottom_y - horizon_y)
        if scale <= 0:
            continue

        line_w = int(8 + scale * 10)
        line_h = int(20 + scale * 45)
        x = center
        pygame.draw.rect(screen, SAND, (x - line_w // 2, y, line_w, line_h), border_radius=5)


def draw_trees():
    for i in range(14):
        x_left = i * 95
        x_right = WIDTH - i * 95
        y = 280 + (i % 4) * 45
        size = 30 + (i % 5) * 12

        pygame.draw.rect(screen, (95, 56, 24), (x_left - 6, y + size * 2 - 10, 12, 34), border_radius=4)
        pygame.draw.polygon(screen, (20, 100, 35), [
            (x_left, y),
            (x_left - size, y + size * 2),
            (x_left + size, y + size * 2)
        ])

        pygame.draw.rect(screen, (95, 56, 24), (x_right - 6, y + size * 2 - 10, 12, 34), border_radius=4)
        pygame.draw.polygon(screen, (20, 100, 35), [
            (x_right, y),
            (x_right - size, y + size * 2),
            (x_right + size, y + size * 2)
        ])


def draw_dashboard():
    pygame.draw.polygon(screen, RED, [
        (400, 720), (500, 582), (780, 582), (880, 720)
    ])
    pygame.draw.polygon(screen, ROAD_GLOW, [
        (430, 720), (520, 605), (760, 605), (850, 720)
    ], 4)

    draw_panel(530, 505, 220, 120, accent=MINT)
    draw_text(str(int(speed)), font_big, WHITE, 640, 550)
    draw_text("KM/H", font_tiny, MINT, 640, 595)

    pygame.draw.line(screen, BLACK, (355, 645), (530, 592), 18)
    pygame.draw.line(screen, BLACK, (925, 645), (750, 592), 18)

    pygame.draw.circle(screen, BLACK, (338, 652), 58)
    pygame.draw.circle(screen, WHITE, (338, 652), 58, 4)
    pygame.draw.circle(screen, BLACK, (942, 652), 58)
    pygame.draw.circle(screen, WHITE, (942, 652), 58, 4)

    pygame.draw.ellipse(screen, (25, 25, 25), (220, 472, 210, 98))
    pygame.draw.ellipse(screen, (25, 25, 25), (850, 472, 210, 98))
    pygame.draw.ellipse(screen, (120, 200, 255), (245, 497, 160, 46))
    pygame.draw.ellipse(screen, (120, 200, 255), (875, 497, 160, 46))


def draw_hud():
    draw_panel(20, 20, 290, 165, accent=MINT)
    draw_text("RACE STATUS", font_tiny, MINT, 40, 38, False)
    draw_text(f"SCORE  {int(score)}", font_small, WHITE, 40, 68, False)
    draw_text(f"DIST   {distance:.1f} KM", font_small, WHITE, 40, 103, False)
    draw_text(f"BOOST  {int(boost)}%", font_small, YELLOW, 40, 138, False)
    draw_progress_bar(40, 155, 220, 16, boost, 100, BLUE, "Nitro")


def draw_bike(center_x, y, scale, bike_color, rider_primary=(38, 42, 88), rider_secondary=(120, 255, 90)):
    side_shift = int(10 * scale)
    rear_wheel = (center_x - side_shift, y + int(60 * scale))
    front_wheel = (center_x + side_shift, y + int(24 * scale))
    rear_r = max(4, int(11 * scale))
    front_r = max(3, int(9 * scale))

    shadow = pygame.Rect(
        center_x - int(26 * scale),
        y + int(54 * scale),
        max(18, int(52 * scale)),
        max(8, int(14 * scale)),
    )
    pygame.draw.ellipse(screen, (0, 0, 0, 120), shadow)

    pygame.draw.circle(screen, (18, 18, 18), rear_wheel, rear_r)
    pygame.draw.circle(screen, (18, 18, 18), front_wheel, front_r)
    pygame.draw.circle(screen, (120, 120, 120), rear_wheel, max(2, int(rear_r * 0.42)))
    pygame.draw.circle(screen, (140, 140, 140), front_wheel, max(2, int(front_r * 0.42)))

    frame_color = tuple(max(0, c - 55) for c in bike_color)
    highlight_color = tuple(min(255, c + 35) for c in bike_color)

    lower_fairing = [
        (center_x - int(12 * scale), y + int(38 * scale)),
        (center_x + int(4 * scale), y + int(25 * scale)),
        (center_x + int(18 * scale), y + int(29 * scale)),
        (center_x + int(10 * scale), y + int(44 * scale)),
        (center_x - int(6 * scale), y + int(48 * scale)),
    ]
    upper_fairing = [
        (center_x - int(8 * scale), y + int(30 * scale)),
        (center_x + int(4 * scale), y + int(16 * scale)),
        (center_x + int(14 * scale), y + int(20 * scale)),
        (center_x + int(7 * scale), y + int(33 * scale)),
    ]
    tail_section = [
        (center_x - int(18 * scale), y + int(47 * scale)),
        (center_x - int(10 * scale), y + int(35 * scale)),
        (center_x + int(1 * scale), y + int(38 * scale)),
        (center_x - int(3 * scale), y + int(54 * scale)),
        (center_x - int(14 * scale), y + int(56 * scale)),
    ]

    pygame.draw.line(screen, GRAY, rear_wheel, (center_x - int(4 * scale), y + int(44 * scale)), max(2, int(3 * scale)))
    pygame.draw.line(screen, GRAY, front_wheel, (center_x + int(8 * scale), y + int(31 * scale)), max(2, int(3 * scale)))
    pygame.draw.line(screen, GRAY, (center_x - int(4 * scale), y + int(44 * scale)), (center_x + int(8 * scale), y + int(31 * scale)), max(2, int(3 * scale)))
    pygame.draw.line(screen, GRAY, (center_x + int(8 * scale), y + int(31 * scale)), (center_x + int(19 * scale), y + int(16 * scale)), max(2, int(2 * scale)))

    pygame.draw.polygon(screen, frame_color, lower_fairing)
    pygame.draw.polygon(screen, bike_color, upper_fairing)
    pygame.draw.polygon(screen, highlight_color, [
        (center_x - int(4 * scale), y + int(31 * scale)),
        (center_x + int(4 * scale), y + int(22 * scale)),
        (center_x + int(11 * scale), y + int(24 * scale)),
        (center_x + int(6 * scale), y + int(31 * scale)),
    ])
    pygame.draw.polygon(screen, bike_color, tail_section)

    seat = pygame.Rect(center_x - int(8 * scale), y + int(31 * scale), max(8, int(13 * scale)), max(4, int(7 * scale)))
    pygame.draw.rect(screen, (24, 24, 24), seat, border_radius=max(2, int(3 * scale)))
    pygame.draw.rect(screen, (255, 90, 74), (center_x - int(16 * scale), y + int(49 * scale), max(4, int(6 * scale)), max(5, int(8 * scale))), border_radius=3)

    pygame.draw.line(screen, GRAY, (center_x + int(14 * scale), y + int(20 * scale)), (center_x + int(22 * scale), y + int(10 * scale)), max(1, int(2 * scale)))
    pygame.draw.line(screen, GRAY, (center_x + int(16 * scale), y + int(22 * scale)), (center_x + int(26 * scale), y + int(16 * scale)), max(1, int(2 * scale)))

    helmet_x = center_x + int(2 * scale)
    helmet_y = y + int(8 * scale)
    head_r = max(4, int(5 * scale))
    torso = [
        (center_x - int(8 * scale), y + int(17 * scale)),
        (center_x + int(1 * scale), y + int(11 * scale)),
        (center_x + int(12 * scale), y + int(16 * scale)),
        (center_x + int(6 * scale), y + int(31 * scale)),
        (center_x - int(5 * scale), y + int(28 * scale)),
    ]
    arm_color = tuple(max(0, c - 15) for c in rider_primary)

    pygame.draw.polygon(screen, rider_primary, torso)
    pygame.draw.circle(screen, SAND, (helmet_x, helmet_y + 2), max(3, int(head_r * 0.72)))
    pygame.draw.circle(screen, rider_primary, (helmet_x, helmet_y), head_r)
    pygame.draw.arc(
        screen,
        rider_secondary,
        (helmet_x - int(6 * scale), helmet_y - int(2 * scale), max(8, int(15 * scale)), max(6, int(10 * scale))),
        math.radians(200),
        math.radians(342),
        max(2, int(3 * scale)),
    )
    pygame.draw.line(screen, arm_color, (center_x + int(5 * scale), y + int(19 * scale)), (center_x + int(18 * scale), y + int(16 * scale)), max(2, int(2 * scale)))
    pygame.draw.line(screen, arm_color, (center_x - int(2 * scale), y + int(27 * scale)), (center_x - int(8 * scale), y + int(41 * scale)), max(2, int(3 * scale)))
    pygame.draw.line(screen, arm_color, (center_x + int(3 * scale), y + int(28 * scale)), (center_x + int(2 * scale), y + int(41 * scale)), max(2, int(3 * scale)))


def create_enemy():
    lane = random.choice([-180, 0, 180])
    return {
        "x": lane,
        "y": 260,
        "scale": 0.15,
        "color": random.choice([(255, 88, 50), (220, 30, 30), (40, 80, 220), (240, 180, 40)]),
        "rider_primary": random.choice([(45, 48, 96), (30, 30, 30), (72, 30, 110)]),
        "rider_secondary": random.choice([(120, 255, 90), (255, 210, 80), (70, 220, 255)]),
    }


def draw_enemy(enemy):
    return


def draw_player_bike():
    center_x = WIDTH // 2 + player_x
    draw_bike(center_x, 490, 1.58, (255, 88, 50), (55, 60, 120), (120, 255, 90))


def update_enemies():
    global game_state, score

    player_rect = pygame.Rect(WIDTH // 2 - 62 + player_x, 525, 124, 118)

    for enemy in enemies[:]:
        enemy["y"] += speed * 0.07
        enemy["scale"] += 0.008

        draw_enemy(enemy)

        center_x = WIDTH // 2 + enemy["x"] + player_x
        w = int(80 * enemy["scale"])
        h = int(120 * enemy["scale"])
        enemy_rect = pygame.Rect(center_x - w // 2, enemy["y"], w, h)

        if enemy_rect.colliderect(player_rect):
            game_state = "gameover"

        if enemy["y"] > HEIGHT:
            enemies.remove(enemy)
            score += 50


def menu():
    draw_background()
    draw_trees()
    draw_road()
    draw_player_bike()
    draw_dashboard()

    draw_panel(360, 70, 560, 240, accent=ROAD_GLOW)
    draw_text("BIKE RACING", font_big, YELLOW, WIDTH // 2, 145)
    draw_text("Arcade highway sprint in first-person view", font_small, WHITE, WIDTH // 2, 205)
    draw_text("Thread traffic, manage boost, stay alive.", font_tiny, MINT, WIDTH // 2, 248)

    if button("START RIDE", WIDTH // 2 - 160, 338, 320, 66, accent=ROAD_GLOW):
        reset_game()
        return "play"

    if button("HOW TO RIDE", WIDTH // 2 - 160, 420, 320, 66, accent=MINT):
        return "instructions"

    if button("EXIT", WIDTH // 2 - 160, 502, 320, 66, accent=RED):
        pygame.quit()
        sys.exit()

    return "menu"


def instructions():
    draw_background()
    draw_trees()
    draw_road()
    draw_player_bike()
    draw_panel(260, 60, 760, 540, accent=MINT)
    draw_text("HOW TO RIDE", font_big, YELLOW, WIDTH // 2, 122)
    draw_text("LEFT / RIGHT", font_med, WHITE, 390, 225, False)
    draw_text("Shift lanes across the road", font_small, MINT, 670, 225)
    draw_text("UP ARROW", font_med, WHITE, 390, 295, False)
    draw_text("Build speed on straight sections", font_small, MINT, 690, 295)
    draw_text("DOWN ARROW", font_med, WHITE, 390, 365, False)
    draw_text("Brake before traffic closes in", font_small, MINT, 680, 365)
    draw_text("SPACE", font_med, WHITE, 390, 435, False)
    draw_text("Spend boost for short bursts", font_small, MINT, 665, 435)
    draw_text("Avoid rival bikes and stretch the run.", font_small, YELLOW, WIDTH // 2, 505)

    if button("BACK", WIDTH // 2 - 120, 550, 240, 60, accent=ROAD_GLOW):
        return "menu"

    return "instructions"


def play():
    global speed, score, distance, boost, player_x, spawn_timer, game_state

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player_x += 8
    if keys[pygame.K_RIGHT]:
        player_x -= 8
    if keys[pygame.K_UP]:
        speed += 0.5
    if keys[pygame.K_DOWN]:
        speed -= 0.8
    if keys[pygame.K_SPACE] and boost > 0:
        speed += 1.2
        boost -= 0.8
    else:
        boost += 0.2

    speed = max(30, min(speed, 260))
    boost = max(0, min(boost, 100))
    player_x = max(-180, min(player_x, 180))

    score += speed * 0.01
    distance += speed * 0.0002

    spawn_timer += 1
    if spawn_timer > max(30, 100 - speed // 3):
        enemies.append(create_enemy())
        spawn_timer = 0

    draw_background()
    draw_trees()
    draw_road()
    update_enemies()
    draw_player_bike()
    draw_dashboard()
    draw_hud()

    return "play"


def gameover():
    draw_background()
    draw_trees()
    draw_road()
    draw_player_bike()
    draw_dashboard()
    draw_panel(350, 150, 580, 390, accent=RED)
    draw_text("GAME OVER", font_big, RED, WIDTH // 2, 230)
    draw_text(f"Final Score: {int(score)}", font_med, WHITE, WIDTH // 2, 310)
    draw_text(f"Distance: {distance:.2f} KM", font_med, WHITE, WIDTH // 2, 360)

    if button("RIDE AGAIN", WIDTH // 2 - 150, 420, 300, 62, accent=ROAD_GLOW):
        reset_game()
        return "play"

    if button("EXIT", WIDTH // 2 - 150, 495, 300, 62, accent=RED):
        pygame.quit()
        sys.exit()

    return "gameover"


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if game_state == "menu":
        game_state = menu()
    elif game_state == "instructions":
        game_state = instructions()
    elif game_state == "play":
        game_state = play()
    elif game_state == "gameover":
        game_state = gameover()

    pygame.display.update()
    clock.tick(60)
