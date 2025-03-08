import pygame
from constants import *

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.img = pygame.image.load("C:/Users/wgq19/Documents/python_code/NEA_game/player_idle1.png")
        self.img = pygame.transform.scale(self.img, (int(self.img.get_width()*SCALE), int(self.img.get_height()*SCALE)))
        self.rect = self.img.get_rect()
        self.rect.center = (x, y)