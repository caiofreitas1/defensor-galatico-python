import pygame
import random
import os
from src.config import *
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.bullet import Bullet
from src.ranking import RankingDB


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

        # Carrega a imagem de background
        try:
            self.background = pygame.image.load(BACKGROUND_IMAGE).convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Erro ao carregar background: {e}")
            self.background = None

        # Inicializa o sistema de ranking
        try:
            self.ranking_db = RankingDB()
        except Exception as e:
            print(f"Erro ao inicializar ranking: {e}")
            self.ranking_db = None

        # Variáveis para entrada de nome
        self.player_name = ""
        self.is_new_high_score = False

        self.init_game_objects()

    def init_game_objects(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.score = 0
        self.lives = PLAYER_LIVES
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
                    elif event.key == pygame.K_r:
                        self.state = 'RANKING'

                elif self.state == 'PLAYING':
                    if event.key == pygame.K_SPACE:
                        if self.sfx_shoot: self.sfx_shoot.play()

                        new_bullet = Bullet(
                            self.player.rect.centerx - BULLET_SIZE[0] // 2,
                            self.player.rect.top
                        )
                        self.bullets.append(new_bullet)

                elif self.state == 'ENTER_NAME':
                    if event.key == pygame.K_RETURN and len(self.player_name) > 0:
                        # Salva o score e vai para GAME_OVER
                        if self.ranking_db:
                            self.ranking_db.save_score(self.player_name, self.score)
                        self.state = 'GAME_OVER'
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif len(self.player_name) < MAX_NAME_LENGTH:
                        # Aceita apenas caracteres alfanuméricos
                        if event.unicode.isalnum():
                            self.player_name += event.unicode.upper()

                elif self.state == 'GAME_OVER':
                    if event.key == pygame.K_r:
                        self.state = 'PLAYING'
                        self.init_game_objects()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'MENU'

                elif self.state == 'RANKING':
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = 'MENU'

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
            self.check_escaped_enemies()

            self.enemies = [e for e in self.enemies if e.is_active]
            self.bullets = [b for b in self.bullets if b.is_active]

    def check_collisions(self):
        for bullet in self.bullets:
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    if self.sfx_explosion: self.sfx_explosion.play()

                    bullet.destroy()
                    enemy.destroy()
                    self.score += 10

        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                # Colisão direta com player = Game Over instantâneo
                self.trigger_game_over()
                return

    def check_escaped_enemies(self):
        """Verifica inimigos que escaparam e reduz vidas."""
        for enemy in self.enemies:
            if enemy.escaped:
                self.lives -= 1
                if self.lives <= 0:
                    self.trigger_game_over()
                    return

    def trigger_game_over(self):
        """Dispara o game over, verificando se é high score."""
        self.is_new_high_score = self.ranking_db and self.ranking_db.is_high_score(self.score)
        if self.is_new_high_score:
            self.player_name = ""
            self.state = 'ENTER_NAME'
        else:
            self.state = 'GAME_OVER'

    def draw_text_centered(self, text, font, color, y_offset=0):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        self.screen.blit(surface, rect)

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)

        if self.state == 'MENU':
            self.draw_text_centered("DEFENSOR GALÁCTICO", self.font_big, GREEN, -50)
            self.draw_text_centered("Pressione ENTER para Iniciar", self.font, WHITE, 30)
            self.draw_text_centered("Pressione 'R' para ver Ranking", self.font, WHITE, 70)

        elif self.state == 'PLAYING':
            self.player.draw(self.screen)
            for enemy in self.enemies: enemy.draw(self.screen)
            for bullet in self.bullets: bullet.draw(self.screen)
            # HUD: Score e Vidas
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            lives_text = self.font.render(f"Vidas: {'| ' * self.lives}", True, RED)
            self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))

        elif self.state == 'ENTER_NAME':
            self.draw_text_centered("NOVO RECORDE!", self.font_big, GREEN, -100)
            self.draw_text_centered(f"Score: {self.score}", self.font, WHITE, -40)
            self.draw_text_centered("Digite seu nome:", self.font, WHITE, 10)
            # Desenha o nome com cursor piscante
            name_display = self.player_name + ("_" if pygame.time.get_ticks() % 1000 < 500 else " ")
            self.draw_text_centered(name_display, self.font_big, WHITE, 60)
            self.draw_text_centered("Pressione ENTER para confirmar", self.font, WHITE, 130)

        elif self.state == 'GAME_OVER':
            self.draw_text_centered("GAME OVER", self.font_big, RED, -50)
            self.draw_text_centered(f"Score Final: {self.score}", self.font, WHITE, 10)
            self.draw_text_centered("Pressione 'R' para Reiniciar ou ESC para Menu", self.font, WHITE, 60)

        elif self.state == 'RANKING':
            self.draw_ranking_screen()

        pygame.display.flip()

    def draw_ranking_screen(self):
        """Desenha a tela de ranking com top 10 scores."""
        self.draw_text_centered("RANKING - TOP 10", self.font_big, GREEN, -220)

        if not self.ranking_db:
            self.draw_text_centered("Ranking indisponível", self.font, RED, 0)
        else:
            scores = self.ranking_db.get_top_scores()
            if not scores:
                self.draw_text_centered("Nenhum score registrado", self.font, WHITE, 0)
            else:
                # Cabeçalho da tabela
                header_y = SCREEN_HEIGHT // 2 - 150
                header = self.font.render("POS   NOME         SCORE      DATA", True, GREEN)
                header_rect = header.get_rect(center=(SCREEN_WIDTH // 2, header_y))
                self.screen.blit(header, header_rect)

                # Linhas do ranking
                for i, (pos, name, score, date) in enumerate(scores):
                    y_pos = header_y + 35 + (i * 30)
                    # Formata a linha com espaçamento fixo
                    line = f"{pos:>2}º    {name:<10}   {score:>6}     {date}"
                    color = WHITE if i > 2 else [GREEN, WHITE, RED][i]  # Top 3 colorido
                    text = self.font.render(line, True, color)
                    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                    self.screen.blit(text, text_rect)

        self.draw_text_centered("Pressione ESC ou ENTER para voltar", self.font, WHITE, 220)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()