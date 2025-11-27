# src/ranking.py
"""
Módulo de gerenciamento de ranking usando SQLite.
Responsável por persistir e recuperar as melhores pontuações.
"""
import sqlite3
import os
from datetime import datetime
from src.config import DB_PATH, MAX_RANKING_ENTRIES


class RankingDB:
    """
    Classe para gerenciar o banco de dados de ranking.
    Demonstra: Encapsulamento e Persistência de Dados.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self._db_path = db_path
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Cria e retorna uma conexão com o banco de dados."""
        return sqlite3.connect(self._db_path)
    
    def _init_db(self):
        """Cria a tabela de ranking se não existir."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rankings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL DEFAULT 'AAA',
                    score INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Índice para otimizar consultas por score
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_score ON rankings(score DESC)
            ''')
            conn.commit()
    
    def save_score(self, player_name: str, score: int) -> int:
        """
        Salva uma pontuação no ranking.
        
        Args:
            player_name: Nome do jogador (máx 10 caracteres)
            score: Pontuação obtida
            
        Returns:
            Posição no ranking (1-10) ou -1 se não entrou no top 10
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insere a nova pontuação
            cursor.execute(
                'INSERT INTO rankings (player_name, score) VALUES (?, ?)',
                (player_name[:10], score)  # Limita nome a 10 caracteres
            )
            conn.commit()
            
            # Calcula a posição no ranking
            cursor.execute(
                'SELECT COUNT(*) FROM rankings WHERE score > ?',
                (score,)
            )
            position = cursor.fetchone()[0] + 1
            
            # Limpa registros antigos além do top entries (mantém histórico limitado)
            self._cleanup_old_entries(cursor)
            conn.commit()
            
            return position if position <= MAX_RANKING_ENTRIES else -1
    
    def _cleanup_old_entries(self, cursor: sqlite3.Cursor, keep_entries: int = 100):
        """Remove entradas antigas mantendo apenas as melhores."""
        cursor.execute(f'''
            DELETE FROM rankings 
            WHERE id NOT IN (
                SELECT id FROM rankings ORDER BY score DESC LIMIT {keep_entries}
            )
        ''')
    
    def get_top_scores(self, limit: int = MAX_RANKING_ENTRIES) -> list:
        """
        Retorna as melhores pontuações.
        
        Args:
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de tuplas (posição, nome, score, data)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT player_name, score, created_at 
                FROM rankings 
                ORDER BY score DESC 
                LIMIT ?
            ''', (limit,))
            
            results = []
            for idx, row in enumerate(cursor.fetchall(), start=1):
                name, score, created_at = row
                # Formata a data para DD/MM/YY
                try:
                    dt = datetime.fromisoformat(created_at)
                    date_str = dt.strftime('%d/%m/%y')
                except:
                    date_str = '--/--/--'
                results.append((idx, name, score, date_str))
            
            return results
    
    def is_high_score(self, score: int) -> bool:
        """
        Verifica se a pontuação entra no top 10.
        
        Args:
            score: Pontuação a verificar
            
        Returns:
            True se a pontuação entra no ranking
        """
        if score <= 0:
            return False
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM rankings')
            total = cursor.fetchone()[0]
            
            # Se ainda não temos 10 scores, qualquer score positivo entra
            if total < MAX_RANKING_ENTRIES:
                return True
            
            # Verifica se o score é maior que o menor score do top 10
            cursor.execute('''
                SELECT MIN(score) FROM (
                    SELECT score FROM rankings ORDER BY score DESC LIMIT ?
                )
            ''', (MAX_RANKING_ENTRIES,))
            min_top_score = cursor.fetchone()[0]
            
            return score > min_top_score
    
    def get_rank_position(self, score: int) -> int:
        """
        Retorna a posição que o score ocuparia no ranking.
        
        Args:
            score: Pontuação a verificar
            
        Returns:
            Posição no ranking (1 = primeiro lugar)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT COUNT(*) FROM rankings WHERE score > ?',
                (score,)
            )
            return cursor.fetchone()[0] + 1
