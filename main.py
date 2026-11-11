import pygame
from pygame import mixer
from pygame.locals import *
import random


#fps
clock = pygame.time.Clock()
fps = 60


screenW = 600
screenH = 800

screen = pygame.display.set_mode((screenW, screenH))
pygame.display.set_caption('Space Invaders')

#define game variables
rows = 5
columns = 5
alien_cooldown = 1000
last_alien_shot = pygame.time.get_ticks()

#define colors
red = (255, 0, 0)
green = (0, 255, 0)


#load images
bg = pygame.image.load('assets/background.png')

def draw_bg():
    screen.blit(bg, (0, 0))


#create space ship class
class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, x, y, health=3):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/spaceship.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.healthStart = health
        self.healthRemaining = health
        self.lastShot = pygame.time.get_ticks()

    def update(self):
        #movement
        speed = 8
        cooldown = 500
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screenW:
            self.rect.x += speed

        #shoot cooldown
        timeNow = pygame.time.get_ticks()
        #shoot bullets
        if key[pygame.K_SPACE] and timeNow - self.lastShot > cooldown:
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.lastShot = timeNow

        #draw player health
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.healthRemaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.healthRemaining / self.healthStart)), 15))
        elif self.healthRemaining <= 0:
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            
        self.mask = pygame.mask.from_surface(self.image)



#create bullet class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, health=3):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()

        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)



#create aliens class
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/alien' + str(random.randint(1, 5)) + '.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.moveCounter = 0
        self.moveDirection = 1

    def update(self):
        self.rect.x += self.moveDirection
        self.moveCounter += 1
        if abs(self.moveCounter) > 75:
            self.moveDirection *= -1
            self.moveCounter *= self.moveDirection


class AlienBullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/alien_bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screenH:
            self.kill()

        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            player.healthRemaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

#create explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):   
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'assets/exp{num}.png')
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        #update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


#create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_aliens():
    for row in range(rows):
        for item in range(columns):
            alien = Aliens(item * 100 + 100, row * 70 + 100)
            alien_group.add(alien)

create_aliens()

#create player
player = SpaceShip(int(screenW / 2), int(screenH - 100), 3)
spaceship_group.add(player)


run = True
while run:

    clock.tick(fps)

    #draw background
    draw_bg()

    timeNow = pygame.time.get_ticks()

    #create random alien bullets
    if timeNow - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
        attacking_alien = random.choice(alien_group.sprites())
        alien_bullet = AlienBullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
        alien_bullet_group.add(alien_bullet)
        last_alien_shot = timeNow

    #event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False



    #update spaceship
    spaceship_group.update()

    #update group
    bullet_group.update()
    alien_group.update()
    alien_bullet_group.update()
    explosion_group.update()

    #draw sprite groups
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    pygame.display.update()

pygame.quit()