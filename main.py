import pygame
import random
import sys
import os

# --- RESOURCE PATH FIX (FOR PYINSTALLER) ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- INITIALIZATION ---
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Astro Shooter 2: Galaxy War 🚀")
clock = pygame.time.Clock()

# Colors & Fonts
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,50,50)
GREEN = (50,255,50)
BLUE = (50,150,255)
GOLD = (255, 215, 0)

font = pygame.font.SysFont("Impact", 30)
big_font = pygame.font.SysFont("Impact", 70)

# Game States
MENU, SELECT_SHIP, PLAYING, GAME_OVER = "menu", "select_ship", "playing", "game_over"
game_state = MENU

# --- SAFE IMAGE LOADER ---
def load_img(path, size=None):
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        print(f"Missing Image: {path} | {e}")
        fallback = pygame.Surface(size if size else (50, 50))
        fallback.fill(RED)
        return fallback

# --- LOAD ASSETS ---

# Backgrounds
bg_menu = load_img("bg/bg2.png", (WIDTH, HEIGHT))
bg_game = load_img("bg/bg1.jpg", (WIDTH, HEIGHT))
bg_y = 0

# Ships & Bullets
ship_images = [load_img(f"ships/ship{i}.png", (60, 60)) for i in range(1, 4)]
bullet_images = [load_img(f"projectiles/Pure_{i:02d}.png", (20, 40)) for i in [1, 6, 11]]

# Asteroids Animation
asteroid_frames = [load_img(f"Asteroids/Asteroid-A-09-{i:03d}.png", (60, 60)) for i in range(120)]

# Sounds
shoot_snd = pygame.mixer.Sound(resource_path("sound effect/lasergun.mp3"))
explod_snd = pygame.mixer.Sound(resource_path("sound effect/explod.mp3"))
shoot_snd.set_volume(0.3)
explod_snd.set_volume(0.5)

def play_bg_music(file_path):
    try:
        pygame.mixer.music.load(resource_path(file_path))
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
    except:
        print("Music error:", file_path)

# --- CLASSES ---

class Player:
    def __init__(self):
        self.reset(0)

    def reset(self, ship_index):
        self.index = ship_index
        self.image = ship_images[self.index]
        self.bullet_img = bullet_images[self.index]
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-80))
        self.speed = 8

    def move(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WIDTH:
            self.rect.x += self.speed

class Asteroid:
    def __init__(self):
        self.frames = asteroid_frames
        self.current_frame = random.randint(0, 119)
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH-50), -60))
        self.speed = random.randint(4, 8)

    def update(self):
        self.rect.y += self.speed
        self.current_frame = (self.current_frame + 1) % 120
        self.image = self.frames[self.current_frame]

# --- UI HELPERS ---

def draw_text(text, font, color, x, y, center=True):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y)) if center else surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)

def draw_button(text, x, y, w, h, color):
    btn_rect = pygame.Rect(x - w//2, y - h//2, w, h)
    mx, my = pygame.mouse.get_pos()
    final_color = WHITE if btn_rect.collidepoint(mx, my) else color

    pygame.draw.rect(screen, final_color, btn_rect, border_radius=12)
    pygame.draw.rect(screen, BLACK, btn_rect, 2, border_radius=12)
    draw_text(text, font, BLACK if final_color == WHITE else WHITE, x, y)
    return btn_rect

# --- GAME SETUP ---
player = Player()
bullets = []
enemies = []
score = 0
spawn_timer = 0
selected_ship = 0

play_bg_music("sound effect/bgsound.ogg")

# --- MAIN LOOP ---
while True:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == MENU:
                if start_btn.collidepoint(event.pos):
                    game_state = SELECT_SHIP

            elif game_state == SELECT_SHIP:
                for i, s_rect in enumerate(selection_rects):
                    if s_rect.collidepoint(event.pos):
                        selected_ship = i
                        player.reset(selected_ship)
                        enemies, bullets, score = [], [], 0
                        game_state = PLAYING
                        play_bg_music("sound effect/bgsound2.mp3")

            elif game_state == GAME_OVER:
                if retry_btn.collidepoint(event.pos):
                    game_state = PLAYING
                    enemies, bullets, score = [], [], 0
                    play_bg_music("sound effect/bgsound2.mp3")

                if menu_btn.collidepoint(event.pos):
                    game_state = MENU
                    play_bg_music("sound effect/bgsound.ogg")

        if event.type == pygame.KEYDOWN and game_state == PLAYING:
            if event.key == pygame.K_SPACE:
                new_bullet = player.bullet_img.get_rect(midbottom=player.rect.midtop)
                bullets.append(new_bullet)
                shoot_snd.play()

    # --- STATES ---

    if game_state == MENU:
        screen.blit(bg_menu, (0, 0))
        draw_text("ASTRO SHOOTER 2", big_font, GOLD, WIDTH//2, 200)
        start_btn = draw_button("START MISSION", WIDTH//2, 400, 250, 60, BLUE)

    elif game_state == SELECT_SHIP:
        screen.blit(bg_menu, (0, 0))
        draw_text("CHOOSE YOUR SHIP", font, WHITE, WIDTH//2, 120)
        selection_rects = []
        mx, my = pygame.mouse.get_pos()

        for i in range(3):
            x_pos = 120 + (i * 180)
            rect = pygame.Rect(x_pos - 65, 300, 130, 160)
            color = GOLD if rect.collidepoint(mx, my) else BLUE
            pygame.draw.rect(screen, color, rect, 3, border_radius=15)

            ship_rect = ship_images[i].get_rect(center=(x_pos, 380))
            screen.blit(ship_images[i], ship_rect)
            selection_rects.append(rect)

    elif game_state == PLAYING:
        bg_y += 3
        if bg_y >= HEIGHT:
            bg_y = 0

        screen.blit(bg_game, (0, bg_y))
        screen.blit(bg_game, (0, bg_y - HEIGHT))

        player.move()
        screen.blit(player.image, player.rect)

        for b in bullets[:]:
            b.y -= 12
            screen.blit(player.bullet_img, b)
            if b.bottom < 0:
                bullets.remove(b)

        spawn_timer += 1
        if spawn_timer > 25:
            enemies.append(Asteroid())
            spawn_timer = 0

        for e in enemies[:]:
            e.update()
            screen.blit(e.image, e.rect)

            for b in bullets[:]:
                if e.rect.colliderect(b):
                    explod_snd.play()
                    if e in enemies: enemies.remove(e)
                    if b in bullets: bullets.remove(b)
                    score += 10

            if e.rect.colliderect(player.rect):
                explod_snd.play()
                pygame.mixer.music.fadeout(500)
                game_state = GAME_OVER

            if e.rect.top > HEIGHT:
                enemies.remove(e)

        draw_text(f"SCORE: {score}", font, WHITE, 20, 30, center=False)

    elif game_state == GAME_OVER:
        draw_text("MISSION FAILED", big_font, RED, WIDTH//2, 220)
        draw_text(f"SCORE: {score}", font, WHITE, WIDTH//2, 300)
        retry_btn = draw_button("RETRY", WIDTH//2, 400, 200, 60, GREEN)
        menu_btn = draw_button("MENU", WIDTH//2, 480, 200, 60, BLUE)

    pygame.display.flip()
    clock.tick(60)