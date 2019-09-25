import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    def __init__(self, ai_settings, screen, mode):
        super(Alien, self).__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # load image and set rect
        if not mode:
            self.image = pygame.image.load('images/alien.bmp')
        else:
            self.image = pygame.image.load('images/marthaStewart.bmp')
        self.rect = self.image.get_rect()

        # set initial place
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        self.x = float(self.rect.x)  # exact position
        self.explode = pygame.mixer.Sound('sounds/alien_alienHit.wav')
        self.shiftDown = pygame.mixer.Sound('sounds/alien_downRow.wav')

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def check_edges(self):
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right:
            self.shiftDown.play()
            return True
        elif self.rect.left <= 0:
            self.shiftDown.play()
            return True

    def update(self):
        self.x += (self.ai_settings.alien_speed_factor * self.ai_settings.fleet_direction)
        self.rect.x = self.x

    def __del__(self):  # destructor: Automatically called when instance is deleted
        self.explode.play()
