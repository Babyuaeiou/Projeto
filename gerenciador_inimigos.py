import random
import sqlite3
import time
from pathlib import Path

from cores import MarromSela, VerdePrimavera, VermelhoTijolo, AzulDodger
from personagem import Inimigo

CAMINHO_BANCO = Path(__file__).resolve().parent / "jogo.db"

DEFINICOES_INIMIGOS = (
    {"id": "gato_esqueleto_01", "nome": "gato esqueleto", "hpmaximo": 1, "dano": 6, "defesa": 2, "x": 760, "y": 520, "xp_recompensa": 180000, "moedas_recompensa": 100000, "cor": MarromSela, "sprite": "gt1.png", "respawn": 75, "raio": 150},
    {"id": "lobo_sombrio_01", "nome": "Lobo Sombrio", "hpmaximo": 18, "dano": 5, "defesa": 1, "x": 1050, "y": 680, "xp_recompensa": 15, "moedas_recompensa": 8, "cor": VerdePrimavera, "sprite": "gt1.png", "respawn": 65, "raio": 130},
    {"id": "morcego_fantasma_01", "nome": "Morcego Fantasma", "hpmaximo": 16, "dano": 7, "defesa": 1, "x": 1370, "y": 850, "xp_recompensa": 20, "moedas_recompensa": 12, "cor": AzulDodger, "sprite": "gt1.png", "respawn": 90, "raio": 170},
    {"id": "goblin_floresta_01", "nome": "Goblin da Floresta", "hpmaximo": 25, "dano": 7, "defesa": 3, "x": 1750, "y": 1120, "xp_recompensa": 25, "moedas_recompensa": 15, "cor": VermelhoTijolo, "sprite": "gt1.png", "respawn": 100, "raio": 180},
    {"id": "gato_esqueleto_02", "nome": "Gato Esqueleto Errante", "hpmaximo": 28, "dano": 8, "defesa": 3, "x": 2050, "y": 1450, "xp_recompensa": 30, "moedas_recompensa": 18, "cor": MarromSela, "sprite": "gt1.png", "respawn": 110, "raio": 160},
)


class GerenciadorInimigos:
    def __init__(self, mapa_atual, largura_mapa, altura_mapa):
        self.mapa_atual = mapa_atual
        self.largura_mapa = largura_mapa
        self.altura_mapa = altura_mapa
        self.inimigos = []
        self.ultimo_salvamento = 0.0
        self._criar_tabela()
        self._registrar_definicoes()

    def _conectar(self):
        conexao = sqlite3.connect(CAMINHO_BANCO)
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    def _criar_tabela(self):
        with self._conectar() as conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS inimigos_mapa (
                    inimigo_id TEXT NOT NULL,
                    mapa_atual TEXT NOT NULL,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    derrotado_ate REAL NOT NULL DEFAULT 0,
                    PRIMARY KEY (inimigo_id, mapa_atual)
                )
            """)

    def _registrar_definicoes(self):
        with self._conectar() as conexao:
            for definicao in DEFINICOES_INIMIGOS:
                conexao.execute("""
                    INSERT OR IGNORE INTO inimigos_mapa
                    (inimigo_id, mapa_atual, x, y, derrotado_ate)
                    VALUES (?, ?, ?, ?, 0)
                """, (definicao["id"], self.mapa_atual, definicao["x"], definicao["y"]))

    def _instanciar(self, definicao, x, y):
        inimigo = Inimigo(
            nome=definicao["nome"],
            hpmaximo=definicao["hpmaximo"],
            dano=definicao["dano"],
            defesa=definicao["defesa"],
            x=x,
            y=y,
            xp_recompensa=definicao["xp_recompensa"],
            moedas_recompensa=definicao["moedas_recompensa"],
            chefe=False,
            cor=definicao["cor"],
            sprite=definicao["sprite"],
            tamanho_sprite=(64, 64),
            velocidade_movimento=45,
            distancia_maxima=definicao["raio"],
            pode_andar=True,
        )
        inimigo.spawn_id = definicao["id"]
        inimigo.respawn_segundos = definicao["respawn"]
        return inimigo

    def carregar(self, jogador, objetos_colisao=(), npcs=()):
        agora = time.time()
        with self._conectar() as conexao:
            registros = conexao.execute(
                "SELECT inimigo_id, x, y, derrotado_ate FROM inimigos_mapa WHERE mapa_atual = ?",
                (self.mapa_atual,),
            ).fetchall()
        definicoes = {item["id"]: item for item in DEFINICOES_INIMIGOS}
        self.inimigos.clear()
        for inimigo_id, x, y, derrotado_ate in registros:
            if derrotado_ate > agora:
                continue
            definicao = definicoes.get(inimigo_id)
            if definicao is None:
                continue
            posicao = self._localizar_posicao(x, y, jogador, objetos_colisao, npcs, self.inimigos)
            if posicao is not None:
                self.inimigos.append(self._instanciar(definicao, *posicao))
        return self.inimigos

    def _localizar_posicao(self, x, y, jogador, objetos_colisao, npcs, inimigos):
        candidatos = [(float(x), float(y))]
        for _ in range(45):
            candidatos.append((
                max(40, min(self.largura_mapa - 100, float(x) + random.uniform(-140, 140))),
                max(40, min(self.altura_mapa - 100, float(y) + random.uniform(-140, 140))),
            ))
        for px, py in candidatos:
            retangulo = __import__("pygame").Rect(round(px + 13), round(py + 26), 38, 38)
            if retangulo.colliderect(jogador.colisao.inflate(180, 180)):
                continue
            if any(retangulo.colliderect(obstaculo) for obstaculo in objetos_colisao):
                continue
            if any(retangulo.colliderect(npc.colisao) for npc in npcs):
                continue
            if any(retangulo.colliderect(outro.colisao.inflate(30, 30)) for outro in inimigos):
                continue
            return px, py
        return None

    def registrar_derrota(self, inimigo):
        if not getattr(inimigo, "spawn_id", None):
            return
        prazo = time.time() + float(getattr(inimigo, "respawn_segundos", 75))
        with self._conectar() as conexao:
            conexao.execute(
                "UPDATE inimigos_mapa SET x = ?, y = ?, derrotado_ate = ? WHERE inimigo_id = ? AND mapa_atual = ?",
                (inimigo.x, inimigo.y, prazo, inimigo.spawn_id, self.mapa_atual),
            )
        inimigo.derrotado = True
        if inimigo in self.inimigos:
            self.inimigos.remove(inimigo)

    def atualizar(self, jogador, objetos_colisao=(), npcs=()):
        agora = time.time()
        definicoes = {item["id"]: item for item in DEFINICOES_INIMIGOS}
        ativos = {getattr(item, "spawn_id", None) for item in self.inimigos}
        with self._conectar() as conexao:
            registros = conexao.execute(
                "SELECT inimigo_id, x, y, derrotado_ate FROM inimigos_mapa WHERE mapa_atual = ?",
                (self.mapa_atual,),
            ).fetchall()
            for inimigo_id, x, y, derrotado_ate in registros:
                if inimigo_id in ativos or derrotado_ate <= 0 or derrotado_ate > agora:
                    continue
                definicao = definicoes.get(inimigo_id)
                if definicao is None:
                    continue
                posicao = self._localizar_posicao(x, y, jogador, objetos_colisao, npcs, self.inimigos)
                if posicao is None:
                    continue
                self.inimigos.append(self._instanciar(definicao, *posicao))
                conexao.execute(
                    "UPDATE inimigos_mapa SET x = ?, y = ?, derrotado_ate = 0 WHERE inimigo_id = ? AND mapa_atual = ?",
                    (posicao[0], posicao[1], inimigo_id, self.mapa_atual),
                )
        if agora - self.ultimo_salvamento >= 10:
            with self._conectar() as conexao:
                conexao.executemany(
                    "UPDATE inimigos_mapa SET x = ?, y = ? WHERE inimigo_id = ? AND mapa_atual = ?",
                    [(item.x, item.y, item.spawn_id, self.mapa_atual) for item in self.inimigos],
                )
            self.ultimo_salvamento = agora
