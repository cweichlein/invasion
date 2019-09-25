import pygame
from pygame.sprite import Sprite


class Ship(Sprite):

    def __init__(self, ai_settings, screen):
        super(Ship, self).__init__()  # research this
        self.screen = screen  # save passed screen object as local variable "screen"
        self.ai_settings = ai_settings
        self.image = pygame.image.load('images/ship.bmp')  # finds ship image
        self.rect = self.image.get_rect()  # gets the image's rectangle
        self.screen_rect = screen.get_rect()  # gets the passed screen object's rectangle
        # place ships in center and at bottom
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom
        self.center = float(self.rect.centerx)
        self.moving_right = False
        self.moving_left = False
        self.explode = pygame.mixer.Sound('sounds/alien_alert.wav')

    # Reads the movement flags and updates the ship's position accordingly
    def update(self):
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.center += self.ai_settings.ship_speed_factor
        if self.moving_left and self.rect.left > 0:
            self.center -= self.ai_settings.ship_speed_factor
        self.rect.centerx = self.center  # rect will round to int, but "center" still holds a decimal for calculations

    # draws ship image at the current position of self.rect
    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        self.center = self.screen_rect.centerx
