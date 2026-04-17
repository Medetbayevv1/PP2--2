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

#Other Variables for use in the program
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 3
COIN_SPEED = 2  # Static, always slower than enemy
SCORE = 0
COIN_COUNT = 0

#Setting up Fonts
font = pygame.font.SysFont("Verdana", 60, bold = True)
font_small = pygame.font.SysFont("Verdana", 20, bold = True)
game_over = font.render("Game Over", True, BLACK)

background = pygame.image.load("AnimatedStreet.png")

#Create a white screen 
DISPLAYSURF = pygame.display.set_mode((400,600))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")


class Coin(pygame.sprite.Sprite):
    def __init__(self, enemies_group):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (7, 7), 7)
        pygame.draw.circle(self.image, (200, 160, 0), (7, 7), 7, 2)  # Darker border
        self.rect = self.image.get_rect()

        # Keep trying random positions until it doesn't overlap any enemy
        max_attempts = 20
        for _ in range(max_attempts):
            self.rect.center = (random.randint(20, SCREEN_WIDTH - 20), 0)
            if not pygame.sprite.spritecollideany(self, enemies_group):
                break  # Found a safe spot

    def move(self):
        self.rect.move_ip(0, COIN_SPEED)  # Uses static COIN_SPEED, not SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
      def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40,SCREEN_WIDTH-40), 0)

      def move(self):
        global SCORE
        self.rect.move_ip(0,SPEED)
        if (self.rect.bottom > 600):
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

#Creating Sprites Groups
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
pygame.time.set_timer(SPAWN_COIN, 1500)  # Spawn a new coin every 1.5 seconds

#Game Loop
while True:
      
    #Cycles through all events occuring  
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            if SPEED < 6:
                SPEED += 0.2     # Only enemy speeds up, COIN_SPEED stays the same
        if event.type == SPAWN_COIN:
            new_coin = Coin(enemies)  # Pass enemies group to avoid overlap
            coins.add(new_coin)
            all_sprites.add(new_coin)
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.blit(background, (0,0))

    # Score on top-left
    scores = font_small.render("Score: " + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10, 10))

    # Coin count on top-right
    coin_text = font_small.render("Coins: " + str(COIN_COUNT), True, GOLD)
    coin_rect = coin_text.get_rect()
    coin_rect.topright = (SCREEN_WIDTH - 10, 10)
    DISPLAYSURF.blit(coin_text, coin_rect)

    #Moves and Re-draws all Sprites
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # Check if player collects any coins
    collected = pygame.sprite.spritecollide(P1, coins, True)
    if collected:
        coin_sound.play()
    COIN_COUNT += len(collected)

    #To be run if collision occurs between Player and Enemy
    if pygame.sprite.spritecollideany(P1, enemies):
          pygame.mixer.Sound('crash.wav').play()
          time.sleep(1)
                   
          DISPLAYSURF.fill(RED)
          DISPLAYSURF.blit(game_over, (30,250))

          # Show final coin count on game over screen
          final_coins = font_small.render("Coins collected: " + str(COIN_COUNT), True, BLACK)
          DISPLAYSURF.blit(final_coins, (130, 320))
          
          pygame.display.update()
          for entity in all_sprites:
                entity.kill() 
          time.sleep(2)
          pygame.quit()
          sys.exit()        
        
    pygame.display.update()
    FramePerSec.tick(FPS)