# Potrzebne importy
import random
import pygame
from pygame.constants import *
from pygame.locals import *
from pygame import mixer

pygame.init()

# Tworzenie obrazków
playerImg = pygame.image.load("imgs/Dora.png")
platformImg = pygame.image.load("imgs/platform.png")
wallImg = pygame.image.load("imgs/wall.png")
rabusImg = pygame.image.load("imgs/rabus.png")

jumpSound = mixer.Sound("audio/jump.mp3")
someRelaxingMusic = mixer.music.load("audio/The Only Thing They Fear Is You ( DOOM Eternal OST High Quality 2021 MICK GORDON).mp3")

class DrawableObject:
    # Korekta kontruktorów, żeby przyjmowały one obrazki
    def __init__(self, x, y, width, height, img):
        self.x = x
        self.y = y

        self.width = width
        self.height = height

        # Wgrywanie obrazka i skalowanie obrazka przy okazji
        self.img = pygame.transform.scale(img, (self.width, self.height))

        self.rect = Rect(self.x, self.y, self.width, self.height)

    def update_rect(self):
        self.rect = Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        x = self.x - offsetX
        y = self.y - offsetY

        # Rysowanie obrazka screen.blit(obrazek, (pozycjaX, pozycjaY)
        screen.blit(self.img, (x, y))


class Player(DrawableObject):
    def __init__(self, x, y):
        # Wgrywamy obrazki
        super().__init__(x, y, 70, 70, playerImg)
        self.velX = self.velY = 0
        self.canJump = False

    def update_rect(self):
        global wallList
        self.velY += 0.5

        self.velX *= 0.98

        self.y += self.velY
        for wall in wallList:
            self.check_collision_with_wall(wall, "VERTICAL")

        self.x += self.velX
        for wall in wallList:
            self.check_collision_with_wall(wall, "HORIZONTAL")

        if self.y < 0:
            self.y = 0
            self.velY = 0

        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.velY = 0
            self.canJump = True

        print(self.y)
        super().update_rect()

    # Skakanko
    def jump(self):
        if self.canJump:
            mixer.Sound.play(jumpSound)
            self.velY = -20
            self.canJump = False

    def check_collision_with_platform(self, platform):
        if self.rect.colliderect(platform.rect) and self.velY > 0:
            self.y = platform.y - self.height
            self.velY = 0
            super().update_rect()
            self.canJump = True

    # UPDATE
    # ZMIANA MECHANIZMU KOLIZJI:
    # Rozłożenie kolizji na dwie składowe
    def check_collision_with_wall(self, wall, side):
        if self.rect.colliderect(wall.rect):
            if side == "HORIZONTAL":
                if self.velX >= 0 and self.x + self.width >= wall.x >= self.x:
                    self.x = wall.x - self.width
                    self.velX = 0

                elif self.velX <= 0 and wall.x + wall.width >= self.x >= wall.x:
                    self.x = wall.x + wall.width
                    self.velX = 0

            elif side == "VERTICAL":
                if self.velY >= 0 and self.y + self.height >= wall.y >= self.y:
                    self.y = wall.y - self.height
                    self.velY = 0
                    self.canJump = True

                elif self.velY <= 0 and wall.y + wall.height >= self.y >= wall.y:
                    self.y = wall.y + wall.height
                    self.velY = 0

            super().update_rect()
    # /UPDATE


class Platform(DrawableObject):
    def __init__(self, x, y):
        # The same thing with image
        super().__init__(x, y, 250, 50, platformImg)


class Wall(DrawableObject):
    def __init__(self, x, y):
        # The same thing with image
        super().__init__(x, y, 100, 250, wallImg)


# UPDATE
# Tworzenie rabusia:
class Enemy(DrawableObject):
    def __init__(self, x, y):
        super().__init__(x, y, 50, 50, rabusImg)

    # Rysowanie rabusia tak, żeby pojawiał się znacznik informujący o nadejściu Rabusia.
    def draw(self):
        x = self.x - offsetX
        y = self.y - offsetY
        if 4000 > x > SCREEN_WIDTH:
            pygame.draw.rect(screen,
                             (255, 0, 0),
                             Rect(SCREEN_WIDTH - self.width - 50, y, self.width, self.height))
        else:
            super().draw()


# /UPDATE

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

offsetX = 0
offsetY = 0
offsetAcceleration = 1

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

wallList = []


def main():

    global offsetX
    global offsetY

    clock = pygame.time.Clock()
    player = Player(100, 100)

    platformList = []
    pygame.mixer.music.play()
    for i in range(50):
        x = 200 + 400 * i
        y = 200 + random.randint(-100, 500)
        platformList.append(Platform(x, y))

    for i in range(100):
        x = 100 + 250 * i
        y = 200 + random.randint(-100, 500)
        wallList.append(Wall(x, y))

    # UPDATE
    rabusList = []

    for i in range(100):
        x = 4000 + 2000 * i
        y = 200 + random.randint(-100, 500)
        rabusList.append(Enemy(x, y))
    # /UPDATE

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        keys = pygame.key.get_pressed()
        if keys[K_w] or keys[K_SPACE]:
            player.jump()
        if keys[K_a]:
            player.velX -= 0.5
        if keys[K_d]:
            player.velX += 0.5

        player.update_rect()

        offsetX += offsetAcceleration

        if player.x - offsetX > SCREEN_WIDTH / 2:
            offsetX += (player.x - offsetX - (SCREEN_WIDTH / 2)) / 10

        if player.x - offsetX < 0:
            running = False

        for platform in platformList:
            player.check_collision_with_platform(platform)

        # UPDATE
        # Sprawdzamy najpierw kolizje horyzontalne, a dopiero potem wertykalne.
        # for wall in wallList:
        #     player.check_collision_with_wall(wall, "VERTICAL")
        #
        # for wall in wallList:
        #     player.check_collision_with_wall(wall, "HORIZONTAL")
        # # /UPDATE

        for rabus in rabusList:
            if player.rect.colliderect(rabus.rect):
                running = False

        # GRAFIKA:
        screen.fill((0, 0, 0))
        player.draw()
        for platform in platformList:
            platform.draw()

        for wall in wallList:
            wall.draw()

        # UPDATE
        for rabus in rabusList:
            rabus.draw()

        # /UPDATE
        # Aktualizacja gry
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


main()
