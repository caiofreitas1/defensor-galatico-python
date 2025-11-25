import pygame
import random
import os  # Novo! Necessário para achar os arquivos
from src.config import *
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.bullet import Bullet


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        pygame.display.set_caption("Defensor Galáctico")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_big = pygame.font.SysFont("Arial", 48)

        self.state = 'MENU'
        # Caminho para os arquivos de som
        base_path = os.path.dirname(__file__)
        assets_path = os.path.join(base_path, 'assets')

        try:
            # Efeitos Sonoros (SFX)
            self.sfx_shoot = pygame.mixer.Sound(os.path.join(assets_path, 'shoot.mp3'))
            self.sfx_explosion = pygame.mixer.Sound(os.path.join(assets_path, 'explosion.mp3'))

            # Ajuste de volume (0.0 a 1.0)
            self.sfx_shoot.set_volume(0.3)
            self.sfx_explosion.set_volume(0.5)

            # Música de Fundo
            pygame.mixer.music.load(os.path.join(assets_path, 'background.mp3'))
            pygame.mixer.music.set_volume(0.2)  # Música mais baixa para não atrapalhar
            pygame.mixer.music.play(-1)  # O '-1' faz a música repetir para sempre (loop)

        except Exception as e:
            print(f"Erro ao carregar sons: {e}")
            print("O jogo continuará sem som.")
            # Cria sons vazios para o jogo não travar se o arquivo faltar
            self.sfx_shoot = None
            self.sfx_explosion = None

        self.init_game_objects()

    def init_game_objects(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.score = 0
        self.frame_count = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.state == 'MENU':
                    if event.key == pygame.K_RETURN:
                        self.state = 'PLAYING'
                        self.init_game_objects()

                elif self.state == 'PLAYING':
                    if event.key == pygame.K_SPACE:
                        # Toca o som de tiro (Novo!)
                        if self.sfx_shoot: self.sfx_shoot.play()

                        new_bullet = Bullet(
                            self.player.rect.centerx - BULLET_SIZE[0] // 2,
                            self.player.rect.top
                        )
                        self.bullets.append(new_bullet)

                elif self.state == 'GAME_OVER':
                    if event.key == pygame.K_r:
                        self.state = 'PLAYING'
                        self.init_game_objects()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

    def update(self):
        if self.state == 'PLAYING':
            self.player.update()

            self.frame_count += 1
            if self.frame_count >= SPAWN_RATE:
                rand_x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE[0])
                self.enemies.append(Enemy(rand_x, -40))
                self.frame_count = 0

            for enemy in self.enemies: enemy.update()
            for bullet in self.bullets: bullet.update()

            self.check_collisions()

            self.enemies = [e for e in self.enemies if e.is_active]
            self.bullets = [b for b in self.bullets if b.is_active]

    def check_collisions(self):
        for bullet in self.bullets:
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    # Toca som de explosão (Novo!)
                    if self.sfx_explosion: self.sfx_explosion.play()

                    bullet.destroy()
                    enemy.destroy()
                    self.score += 10

        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                self.state = 'GAME_OVER'

    # (O resto dos métodos draw e draw_text_centered continuam iguais...)
    def draw_text_centered(self, text, font, color, y_offset=0):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        self.screen.blit(surface, rect)

    def draw(self):
        self.screen.fill(BLACK)
        if self.state == 'MENU':
            self.draw_text_centered("DEFENSOR GALÁCTICO", self.font_big, GREEN, -50)
            self.draw_text_centered("Pressione ENTER para Iniciar", self.font, WHITE, 50)
        elif self.state == 'PLAYING':
            self.player.draw(self.screen)
            for enemy in self.enemies: enemy.draw(self.screen)
            for bullet in self.bullets: bullet.draw(self.screen)
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
        elif self.state == 'GAME_OVER':
            self.draw_text_centered("GAME OVER", self.font_big, RED, -50)
            self.draw_text_centered(f"Score Final: {self.score}", self.font, WHITE, 10)
            self.draw_text_centered("Pressione 'R' para Reiniciar ou ESC para Sair", self.font, WHITE, 60)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()