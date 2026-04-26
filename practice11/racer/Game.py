#Imports
import pygame, sys
from pygame.locals import *
import random, time

#Initialzing 
pygame.init()
coin_sound = pygame.mixer.Sound("collsound.mp3")

#Setting up FPS 
FPS = 60
FramePerSec = pygame.time.Clock()

#Creating colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD  = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

#Other Variables for use in the program
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 3
COIN_SPEED = 2
SCORE = 0
COIN_POINTS = 0          # Total weighted coin score
COIN_MILESTONE = 10      # Speed boost every N coin points
LAST_MILESTONE = 0       # Tracks last triggered milestone
SPEED_FLASH_TIMER = 0    # Frames to show "Speed Up!" message


COIN_TYPES = [
    ("bronze", BRONZE,    (160, 90, 30),    7, 1, 55),
    ("silver", SILVER,    (140, 140, 140),  8, 2, 30),
    ("gold",   GOLD,      (200, 160, 0),    9, 3, 15),
]

#Setting up Fonts
font = pygame.font.SysFont("Verdana", 60, bold=True)
font_small = pygame.font.SysFont("Verdana", 20, bold=True)
font_flash = pygame.font.SysFont("Verdana", 28, bold=True)
game_over = font.render("Game Over", True, BLACK)

background = pygame.image.load("AnimatedStreet.png")

#Create a white screen 
DISPLAYSURF = pygame.display.set_mode((400, 600))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")


class Coin(pygame.sprite.Sprite):
    def __init__(self, enemies_group):
        super().__init__()
        # Pick a weighted random coin type
        labels     = [c[0] for c in COIN_TYPES]
        weights    = [c[5] for c in COIN_TYPES]
        chosen     = random.choices(COIN_TYPES, weights=weights, k=1)[0]

        _, color, border_color, radius, self.points, _ = chosen
        size = radius * 2 + 4

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)
        pygame.draw.circle(self.image, color, center, radius)
        pygame.draw.circle(self.image, border_color, center, radius, 2)

        # Draw point value inside coin
        coin_font = pygame.font.SysFont("Verdana", max(8, radius - 2), bold=True)
        label_surf = coin_font.render(str(self.points), True, border_color)
        label_rect = label_surf.get_rect(center=center)
        self.image.blit(label_surf, label_rect)

        self.rect = self.image.get_rect()

        max_attempts = 20
        for _ in range(max_attempts):
            self.rect.center = (random.randint(20, SCREEN_WIDTH - 20), 0)
            if not pygame.sprite.spritecollideany(self, enemies_group):
                break

    def move(self):
        self.rect.move_ip(0, COIN_SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.bottom > 600:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)


#Setting up Sprites        
P1 = Player()
E1 = Enemy()

#Creating Sprite Groups
coins = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemies.add(E1)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)

#Adding user events
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 1500)

#Game Loop
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            if SPEED < 6:
                SPEED += 0.2
        if event.type == SPAWN_COIN:
            new_coin = Coin(enemies)
            coins.add(new_coin)
            all_sprites.add(new_coin)
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.blit(background, (0, 0))

    # HUD: score top-left
    scores = font_small.render("Score: " + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10, 10))

    # HUD: coin points top-right
    coin_text = font_small.render("Coins: " + str(COIN_POINTS), True, GOLD)
    coin_rect = coin_text.get_rect()
    coin_rect.topright = (SCREEN_WIDTH - 10, 10)
    DISPLAYSURF.blit(coin_text, coin_rect)

    # "Speed Up!" flash
    if SPEED_FLASH_TIMER > 0:
        flash_surf = font_flash.render("Speed Up!", True, RED)
        flash_rect = flash_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        DISPLAYSURF.blit(flash_surf, flash_rect)
        SPEED_FLASH_TIMER -= 1

    # Move and draw all sprites
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # Check coin collection
    collected = pygame.sprite.spritecollide(P1, coins, True)
    if collected:
        coin_sound.play()
        for coin in collected:
            COIN_POINTS += coin.points

        # Check for milestone: speed boost every COIN_MILESTONE points
        new_milestone = (COIN_POINTS // COIN_MILESTONE)
        if new_milestone > LAST_MILESTONE:
            SPEED = min(SPEED + 0.5, 10)   
            LAST_MILESTONE = new_milestone
            SPEED_FLASH_TIMER = 90           

    # Collision with enemy → game over
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound('crash.wav').play()
        time.sleep(1)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))

        final_coins = font_small.render("Coins: " + str(COIN_POINTS) + " points", True, BLACK)
        DISPLAYSURF.blit(final_coins, (130, 320))

        pygame.display.update()
        for entity in all_sprites:
            entity.kill()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)