import pygame
from network import Network

pygame.init()

WIDTH =500
HEIGHT =500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")

clientNumber =0



class Player:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x,y,width,height)
        self.vel =3

    def draw(self, w):
        pygame.draw.rect(w, self.color, self.rect)

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.vel
        if keys[pygame.K_RIGHT]:
            self.x += self.vel
        if keys[pygame.K_UP]:
            self.y -= self.vel
        if keys[pygame.K_DOWN]:
            self.y += self.vel

        self.rect = (self.x, self.y, self.width, self.height)

def read_pos(str):
    str = str.split(",")
    return int(str[0]), int(str[1])

def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])


def redrawWindow(w, player):

    win.fill((255,255,255))
    player.draw(w)
    pygame.display.update()


def main():
    run = True
    n = Network()
    startPos = read_pos(n.getPos())
    p = Player(startPos[0],startPos[1],100,100,"green")
    p2  = Player(0,0,100,100,"green")
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        p2Pos = n.send(make_pos(p.x, p.y))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        p.move()
        redrawWindow(win , p)


    pygame.quit()


main()