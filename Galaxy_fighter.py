import pygame
import os
pygame.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40
pygame.display.set_caption("Galaxy Fighter")

YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('galaxy fighter assets', 'spaceship_yellow.png'))
RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('galaxy fighter assets', 'spaceship_red.png'))

YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), -90)
def draw_window():
    WIN.fill((255, 255, 255))
    WIN.blit(YELLOW_SPACESHIP, (200, 100))  
    WIN.blit(RED_SPACESHIP, (700, 100))
    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        draw_window()

    pygame.quit()

if __name__ == "__main__":
    main()
