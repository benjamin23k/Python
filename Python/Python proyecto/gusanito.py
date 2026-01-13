import pygame
import sys

pygame.init()

ancho = 640
alto = 480
pantalla = pygame.display.set_mode((ancho, alto))

blanco = (255, 255, 255)
rojo = (255, 0, 0)
verde = (0, 255, 0)

class Gusanito:
    def __init__(self):
        self.x = ancho // 2
        self.y = alto // 2
        self.ancho = 50
        self.alto = 50

    def dibujar(self):
        pygame.draw.rect(pantalla, verde, (self.x, self.y, self.ancho, self.alto))

class Manzana:
    def __init__(self):
        self.x = ancho // 2 + 100
        self.y = alto // 2
        self.ancho = 30
        self.alto = 30

    def dibujar(self):
        pygame.draw.rect(pantalla, rojo, (self.x, self.y, self.ancho, self.alto))

# Instancias
gusanito = Gusanito()
manzana = Manzana()

clock = pygame.time.Clock()

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            sys.exit()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                manzana.x = 100
                manzana.y = -100
                print("Gusanito se comió la manzana")

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        gusanito.x -= 5
    if keys[pygame.K_RIGHT]:
        gusanito.x += 5
    if keys[pygame.K_UP]:
        gusanito.y -= 5
    if keys[pygame.K_DOWN]:
        gusanito.y += 5

    pantalla.fill(blanco)
    gusanito.dibujar()
    manzana.dibujar()

    pygame.display.flip()
    clock.tick(60)