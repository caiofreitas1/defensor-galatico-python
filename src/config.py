import os

# Diretório base dos assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# Configurações do Ranking
DB_PATH = os.path.join(os.path.dirname(__file__), 'ranking.db')
MAX_RANKING_ENTRIES = 10
MAX_NAME_LENGTH = 10

# Dimensões da Tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Cores (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Caminhos das Imagens
PLAYER_IMAGE = os.path.join(ASSETS_DIR, 'player.png')
ENEMY_IMAGE = os.path.join(ASSETS_DIR, 'enemy.png')
BULLET_IMAGE = os.path.join(ASSETS_DIR, 'bullet.png')
BACKGROUND_IMAGE = os.path.join(ASSETS_DIR, 'background.png')

# Configurações do Jogador
PLAYER_SPEED = 5
PLAYER_SIZE = (50, 40) # Largura, Altura
PLAYER_LIVES = 3  # Vidas iniciais

# Configurações do Inimigo
ENEMY_SPEED = 3
ENEMY_SIZE = (40, 40)
SPAWN_RATE = 60 # A cada 60 frames (1 seg), nasce um inimigo

# Configurações do Tiro
BULLET_SPEED = 7
BULLET_SIZE = (5, 10)