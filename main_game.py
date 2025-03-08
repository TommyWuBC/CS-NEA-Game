import pygame
from constants import *
from character import *
from player import *

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("shooter platformer game")



run = True
while run:
    
    player.image = pygame.image.load("NEA_game/Assets/player_idle1.png")
    screen.blit(player.image, player.rect)
    
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
            
    pygame.display.update()
           
pygame.quit()
        