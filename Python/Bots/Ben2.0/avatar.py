# avatar.py
import pygame, sys, os
import pyautogui

WIDTH, HEIGHT = 240, 240

class Avatar:
    def __init__(self, image_path="avatar.png"):
        pygame.init()
        # ventana sin borde y siempre arriba
        os.environ['SDL_VIDEO_WINDOW_POS'] = "50,50"
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("Ben")
        self.avatar = pygame.image.load(image_path).convert_alpha()
        self.x, self.y = WIDTH//2, HEIGHT//2
        self.clock = pygame.time.Clock()

    def update(self):
        mx, my = pyautogui.position()
        # calculamos posición relativa: convertir cursor del sistema a coords de la ventana (simple smoothing)
        # aquí solo movemos el avatar dentro de su ventana hacia una dirección simulada
        self.x += (mx - self.x) * 0.05
        self.y += (my - self.y) * 0.05

    def draw(self):
        self.screen.fill((0,0,0,0))  # si no soporta alpha, cambia color
        rect = self.avatar.get_rect(center=(self.x, self.y))
        self.screen.blit(self.avatar, rect)
        pygame.display.update()

    def loop_once(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        self.update()
        self.draw()
        self.clock.tick(30)