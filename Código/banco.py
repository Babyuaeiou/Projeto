
import json
import sqlite3
from pathlib import Path

from item import Item, catalogo


# Salva o banco na mesma pasta deste arquivo.
CAMINHO_BANCO = Path(__file__).resolve().parent / "jogo.db"


# =========================================================
# CONEXÃO E CRIAÇÃO DO BANCO
# =========================================================

def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_banco():
    """Cria as tabelas sem apagar os dados existentes."""

    with conectar() as conexao:
        # Tabela antiga: mantida para compatibilidade.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS personagem (
                id INTEGER PRIMARY KEY,
                x REAL NOT NULL,
                y REAL NOT NULL
            )
        """)

        # Atributos completos do personagem.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS estado_personagem (
                id INTEGER PRIMARY KEY,
                dados TEXT NOT NULL
            )
        """)

        # Inventário e organização dos espaços.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY,
                dados TEXT NOT NULL
            )
        """)

        # Estado geral do mundo.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS estado_jogo (
                id INTEGER PRIMARY KEY,
                mapa_atual TEXT NOT NULL
            )
        """)

        # Paredes e demais retângulos de colisão.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS colisoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mapa_atual TEXT NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                largura REAL NOT NULL,
                altura REAL NOT NULL
            )
        """)


# =========================================================
# SERIALIZAÇÃO DE ITENS
# =========================================================

def _serializar(valor):
    """Converte valores e itens em dados que o SQLite pode guardar."""

    if valor is None or isinstance(valor, (str, int, float, bool)):
        return valor

    if isinstance(valor, Item):
        return {
            "__tipo__": "Item",
            "dados": valor.para_dict(),
        }

    if isinstance(valor, dict):
        return {
            str(chave): _serializar(item)
            for chave, item in valor.items()
        }

    if isinstance(valor, (list, tuple)):
        return [_serializar(item) for item in valor]

    if hasattr(valor, "para_dict"):
        return {
            "__tipo__": "Item",
            "dados": _serializar(valor.para_dict()),
        }

    raise TypeError(
        f"Não é possível salvar o tipo {type(valor).__name__}."
    )


def _desserializar(valor):
    """Reconstrói os itens salvos, quando possível."""

    if isinstance(valor, list):
        return [_desserializar(item) for item in valor]

    if isinstance(valor, dict):
        if valor.get("__tipo__") == "Item":
            dados = _desserializar(valor["dados"])
            item_id = dados.get("id")

            # Reutiliza o item cadastrado no catálogo.
            item_cadastrado = catalogo.obter(item_id)

            if item_cadastrado is not None:
                return item_cadastrado

            # Se não estiver cadastrado, recria a instância.
            dados.pop("id", None)

            return Item(
                id=item_id,
                **dados,
            )

        return {
            chave: _desserializar(item)
            for chave, item in valor.items()
        }

    return valor


# =========================================================
# POSIÇÃO ANTIGA — COMPATIBILIDADE
# =========================================================

def salvar_posicao(x, y):
    """Salva apenas a posição, para chamadas do código antigo."""

    with conectar() as conexao:
        conexao.execute("""
            INSERT INTO personagem (id, x, y)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                x = excluded.x,
                y = excluded.y
        """, (x, y))


def carregar_posicao():
    """Retorna (x, y), ou None se não houver posição salva."""

    with conectar() as conexao:
        resultado = conexao.execute("""
            SELECT x, y
            FROM personagem
            WHERE id = 1
        """).fetchone()

    return resultado if resultado else None


# =========================================================
# SALVAR PARTIDA COMPLETA
# =========================================================

def salvar_partida(
    jogador,
    inventario,
    objetos_colisao,
    mapa_atual="mapa_inicial",
):
    """
    Salva posição, atributos do personagem, inventário,
    mapa atual e todas as colisões da lista recebida.
    """

    # Atributos relevantes do personagem.
    nomes_atributos = (
        "nome",
        "hp",
        "hpmaximo",
        "dano",
        "danototal",
        "defesa",
        "defesatotal",
        "velocidade",
        "velocidade_movimento",
        "cooldown",
        "restante",
        "x",
        "y",
    )

    dados_personagem = {}

    for nome in nomes_atributos:
        if hasattr(jogador, nome):
            valor = getattr(jogador, nome)

            if isinstance(valor, (str, int, float, bool)) or valor is None:
                dados_personagem[nome] = valor

    dados_inventario = {
        "espacos": _serializar(inventario.espacos),
        "cursor": inventario.cursor,
        "espaco_selecionado": inventario.espaco_selecionado,
        "aberto": inventario.aberto,
    }

    # Captura as colisões antes de abrir a transação.
    colisões = []

    for retangulo in objetos_colisao:
        if not all(
            hasattr(retangulo, atributo)
            for atributo in ("x", "y", "width", "height")
        ):
            raise TypeError(
                "Todos os objetos de colisão devem ter "
                "x, y, width e height."
            )

        colisões.append((
            mapa_atual,
            retangulo.x,
            retangulo.y,
            retangulo.width,
            retangulo.height,
        ))

    dados_json = json.dumps(
        dados_personagem,
        ensure_ascii=False,
    )

    inventario_json = json.dumps(
        dados_inventario,
        ensure_ascii=False,
    )

    # Todas as alterações são salvas na mesma transação.
    with conectar() as conexao:
        conexao.execute("""
            INSERT INTO personagem (id, x, y)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                x = excluded.x,
                y = excluded.y
        """, (jogador.x, jogador.y))

        conexao.execute("""
            INSERT INTO estado_personagem (id, dados)
            VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET
                dados = excluded.dados
        """, (dados_json,))

        conexao.execute("""
            INSERT INTO inventario (id, dados)
            VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET
                dados = excluded.dados
        """, (inventario_json,))

        conexao.execute("""
            INSERT INTO estado_jogo (id, mapa_atual)
            VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET
                mapa_atual = excluded.mapa_atual
        """, (mapa_atual,))

        # Substitui as colisões salvas deste mapa.
        conexao.execute("""
            DELETE FROM colisoes
            WHERE mapa_atual = ?
        """, (mapa_atual,))

        conexao.executemany("""
            INSERT INTO colisoes (
                mapa_atual, x, y, largura, altura
            )
            VALUES (?, ?, ?, ?, ?)
        """, colisões)


# =========================================================
# CARREGAR PARTIDA COMPLETA
# =========================================================

def carregar_partida(
    jogador,
    inventario,
    mapa_padrao="mapa_inicial",
):
    """
    Restaura os dados do jogador e do inventário.

    Retorna:
        None, se não existir uma partida completa;
        ou um dicionário com o mapa e as colisões salvas.
    """

    with conectar() as conexao:
        linha_personagem = conexao.execute("""
            SELECT dados
            FROM estado_personagem
            WHERE id = 1
        """).fetchone()

        linha_inventario = conexao.execute("""
            SELECT dados
            FROM inventario
            WHERE id = 1
        """).fetchone()

        linha_mapa = conexao.execute("""
            SELECT mapa_atual
            FROM estado_jogo
            WHERE id = 1
        """).fetchone()

        if not linha_personagem or not linha_inventario:
            return None

        dados_personagem = json.loads(linha_personagem[0])
        dados_inventario = json.loads(linha_inventario[0])

        mapa_atual = (
            linha_mapa[0]
            if linha_mapa
            else mapa_padrao
        )

        linhas_colisoes = conexao.execute("""
            SELECT x, y, largura, altura
            FROM colisoes
            WHERE mapa_atual = ?
            ORDER BY id
        """, (mapa_atual,)).fetchall()

    # Restaura somente atributos existentes na classe.
    for nome, valor in dados_personagem.items():
        if hasattr(jogador, nome):
            setattr(jogador, nome, valor)

    # Sincroniza a caixa de colisão do personagem.
    if hasattr(jogador, "colisao"):
        jogador.colisao.topleft = (
            round(jogador.x),
            round(jogador.y),
        )

    # Restaura os espaços do inventário.
    espacos_salvos = _desserializar(
        dados_inventario.get("espacos", [])
    )

    total_espacos = inventario.TOTAL_ESPACOS

    inventario.espacos = list(
        espacos_salvos[:total_espacos]
    )

    inventario.espacos.extend(
        [None] * (
            total_espacos - len(inventario.espacos)
        )
    )

    inventario.cursor = max(
        0,
        min(
            int(dados_inventario.get("cursor", 0)),
            total_espacos - 1,
        ),
    )

    selecionado = dados_inventario.get(
        "espaco_selecionado"
    )

    if isinstance(selecionado, int) and (
        0 <= selecionado < total_espacos
    ):
        inventario.espaco_selecionado = selecionado
    else:
        inventario.espaco_selecionado = None

    inventario.aberto = bool(
        dados_inventario.get("aberto", False)
    )

    return {
        "mapa_atual": mapa_atual,
        "colisoes": [
            {
                "x": x,
                "y": y,
                "largura": largura,
                "altura": altura,
            }
            for x, y, largura, altura in linhas_colisoes
        ],
    }
