import random
from time import sleep

import pygame
from pygame.locals import *

WINDOW_WIDTH = 480      # horizontal
WINDOW_HEIGHT = 640     # vertical

BLACK = (0, 0, 0)  # RGB color
RED = (250, 50, 50)
YELLOW = (250, 250, 50)
WHITE = (255, 255, 255)

FPS = 60


class SpaceShip(pygame.sprite.Sprite):
    def __init__(self):
        super(SpaceShip, self).__init__()
        self.image = pygame.image.load('spaceship.png')
        self.rect = self.image.get_rect()
        self.rect.x = int(WINDOW_WIDTH / 2)  # align center
        self.rect.y = WINDOW_HEIGHT - self.rect.height
        self.dx = 0
        self.dy = 0

    def update(self):  # spaceship move
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.x < 0 or self.rect.x + self.rect.width > WINDOW_WIDTH:
            self.rect.x -= self.dx

        if self.rect.y < 0 or self.rect.y + self.rect.height > WINDOW_HEIGHT:
            self.rect.y -= self.dy

    def draw(self, window):
        window.blit(self.image, self.rect)

    def collide(self, sprites):   # spaceship crash
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                return sprite


class Missile(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed):
        super(Missile, self).__init__()
        self.image = pygame.image.load('missile.png')
        self.rect = self.image.get_rect()
        self.rect.x = xpos   # missile from spaceship
        self.rect.y = ypos
        self.speed = speed
        self.sound = pygame.mixer.Sound('missile.wav')


    def update(self):
        self.rect.y -= self.speed
        if self.rect.y + self.rect.height < 0:
            self.kill()  # disappears after shooting

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                return sprite

    def launch(self):
        self.sound.play()


class Meteo(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, speed):
        super(Meteo, self).__init__()
        meteo_images = ('meteo01.png', 'meteo02.png', 'meteo03.png', 'meteo04.png', 'meteo05.png', \
                       'meteo06.png', 'meteo07.png', 'meteo08.png', 'meteo09.png', 'meteo10.png', \
                       'meteo11.png', 'meteo12.png', 'meteo13.png', 'meteo14.png', 'meteo15.png', \
                       'meteo16.png', 'meteo17.png', 'meteo18.png', 'meteo19.png', 'meteo20.png', \
                       'meteo21.png', 'meteo22.png', 'meteo23.png', 'meteo24.png', 'meteo25.png', \
                       'meteo26.png', 'meteo27.png', 'meteo28.png', 'meteo29.png', 'meteo30.png')
        self.image = pygame.image.load(random.choice(meteo_images))
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.speed = speed

    def outter(self):       # out of screen
        if self.rect.y > WINDOW_HEIGHT:
            return True

    def update(self):
        self.rect.y += self.speed


def occur_explosion(surface, x, y):
    explosion_image = pygame.image.load('explosion.png')
    explosion_rect = explosion_image.get_rect()
    explosion_rect.x = x
    explosion_rect.y = y
    surface.blit(explosion_image, explosion_rect)

    explosion_sounds = ('explosion01.wav', 'explosion02.wav', 'explosion03.wav')
    explosion_sounds = pygame.mixer.Sound(random.choice(explosion_sounds))
    explosion_sounds.play()


def draw_text(text, font, surface, x, y, m_color):
    text_obj = font.render(text, True, m_color)
    text_rect = text_obj.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surface.blit(text_obj, text_rect)


def game_loop():
    default_font = pygame.font.Font('NanumGothic.ttf', 28)
    background_image = pygame.image.load('background.png')
    gameover_sound = pygame.mixer.Sound('gameover.wav')
    pygame.mixer.music.load('music.wav')
    pygame.mixer.music.play(-1)  # -1 ---> means loop
    fps_clock = pygame.time.Clock()

    spaceship = SpaceShip()
    missiles = pygame.sprite.Group()  # Group() --> multiple
    meteorites = pygame.sprite.Group()

    occur_prob = 40
    count_missiles = 0
    missed = 0

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    spaceship.dx -= 3
                elif event.key == pygame.K_RIGHT:
                    spaceship.dx += 3
                elif event.key == pygame.K_UP:
                    spaceship.dy -= 3
                elif event.key == pygame.K_DOWN:
                    spaceship.dy += 3
                elif event.key == pygame.K_SPACE:
                    missile = Missile(spaceship.rect.centerx, spaceship.rect.y, 10)
                    missile.launch()
                    missiles.add(missile)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    spaceship.dx = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    spaceship.dy = 0

        window.blit(background_image, background_image.get_rect())

        occur_of_meteorites = 1 + int(count_missiles / 300)
        min_meteo_speed = 1 + int(count_missiles / 200)          # make difficult
        max_meteo_speed = 1 + int(count_missiles / 100)

        if random.randint(1, occur_prob) == 1:
            for i in range(occur_of_meteorites):
                speed = random.randint(min_meteo_speed, max_meteo_speed)
                meteo = Meteo(random.randint(0, WINDOW_WIDTH - 30), 0, speed)
                meteorites.add(meteo)

        draw_text('Destroyed: {}'.format(count_missiles), default_font, window, 100, 20, YELLOW)
        draw_text('Missed: {}'.format(missed), default_font, window, 400, 20, RED)

        for missile in missiles:
            meteo = missile.collide(meteorites)
            if meteo:
                missile.kill()
                meteo.kill()
                occur_explosion(window, meteo.rect.x, meteo.rect.y)
                count_missiles += 1

        for meteo in meteorites:
            if meteo.outter():
                meteo.kill()
                missed += 1

        meteorites.update()
        meteorites.draw(window)
        missiles.update()
        missiles.draw(window)
        spaceship.update()
        spaceship.draw(window)
        pygame.display.flip()

        if spaceship.collide(meteorites) or missed >= 3:
            pygame.mixer_music.stop()
            occur_explosion(window, spaceship.rect.x, spaceship.rect.y)
            pygame.display.update()
            gameover_sound.play()
            sleep(1)
            done = True

        fps_clock.tick(FPS)

    return 'game_menu'


def game_menu():
    start_image = pygame.image.load('background.png')
    window.blit(start_image, [0, 0])

    draw_x = int(WINDOW_WIDTH / 2)
    draw_y = int(WINDOW_HEIGHT / 4)

    font_40 = pygame.font.Font('NanumGothic.ttf', 40)
    font_30 = pygame.font.Font('NanumGothic.ttf', 30)

    draw_text('INVADER : METEOR V1', font_40, window, draw_x, draw_y, YELLOW)
    draw_text('Press [ENTER] to start', font_30, window, draw_x, draw_y + 250, WHITE)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return 'play'
        if event.type == QUIT:
            return 'quit'

    return 'game_menu'


def main():
    global window

    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('INVADER : METEOR V1')

    action = 'game_menu'
    while action != 'quit':
        if action == 'game_menu':
            action = game_menu()
        elif action == 'play':
            action = game_loop()

    pygame.quit()



if __name__ == "__main__":
    main()

