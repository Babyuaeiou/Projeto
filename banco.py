
import json
import sqlite3
from pathlib import Path

from item import Item, catalogo


# =========================================================
# CONFIGURAÇÃO DO BANCO
# =========================================================

CAMINHO_BANCO = Path(__file__).resolve().parent / "jogo.db"


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_banco():
    """Cria as tabelas sem apagar os dados existentes."""

    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS personagem (
                id INTEGER PRIMARY KEY,
                x REAL NOT NULL,
                y REAL NOT NULL
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS estado_personagem (
                id INTEGER PRIMARY KEY,
                dados TEXT NOT NULL
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY,
                dados TEXT NOT NULL
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS estado_jogo (
                id INTEGER PRIMARY KEY,
                mapa_atual TEXT NOT NULL
            )
        """)

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
    """Converte os dados para formatos que podem ser salvos em JSON."""

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
    """Reconstrói itens e estruturas salvas em JSON."""

    if isinstance(valor, list):
        return [_desserializar(item) for item in valor]

    if isinstance(valor, dict):
        if valor.get("__tipo__") == "Item":
            dados = _desserializar(valor["dados"])
            item_id = dados.get("id")

            item_cadastrado = catalogo.obter(item_id)

            if item_cadastrado is not None:
                return item_cadastrado

            dados.pop("id", None)

            return Item(id=item_id, **dados)

        return {
            chave: _desserializar(item)
            for chave, item in valor.items()
        }

    return valor


# =========================================================
# SALVAMENTO SIMPLES DA POSIÇÃO
# =========================================================

def salvar_posicao(x, y):
    """Mantém compatibilidade com o sistema antigo de posição."""

    with conectar() as conexao:
        conexao.execute("""
            INSERT INTO personagem (id, x, y)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                x = excluded.x,
                y = excluded.y
        """, (x, y))


def carregar_posicao():
    """Retorna (x, y) ou None caso não exista posição salva."""

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
    """Salva personagem, progressão, inventário, mapa e colisões."""

    nomes_atributos = (
        "nome",
        "hp",
        "hpmaximo",
        "nivel",
        "xp",
        "xp_proximo",
        "moedas",
        "dano_base",
        "defesa_base",
        "dano",
        "danototal",
        "defesa",
        "defesatotal",
        "velocidade",
        "velocidade_movimento",
        "cooldown",
        "restante",
        "buff_proximo_ataque",
        "hp_base",
        "pontos_atributo",
        "limite_atributo",
        "x",
        "y",
    )

    dados_personagem = {}

    for nome in nomes_atributos:
        if hasattr(jogador, nome):
            valor = getattr(jogador, nome)

            if isinstance(
                valor, (str, int, float, bool)
            ) or valor is None:
                dados_personagem[nome] = valor

    if hasattr(jogador, "atributos_distribuidos"):
        dados_personagem["atributos_distribuidos"] = dict(jogador.atributos_distribuidos)

    # Guarda também os equipamentos do personagem.
    if hasattr(jogador, "equipamentos"):
        dados_personagem["equipamentos"] = (
            jogador.equipamentos.copy()
        )

    # Guarda o inventário de itens do personagem, se existir.
    if hasattr(jogador, "inventario"):
        dados_personagem["inventario_personagem"] = (
            _serializar(jogador.inventario)
        )

    dados_inventario = {
        "espacos": _serializar(inventario.espacos),
        "cursor": inventario.cursor,
        "espaco_selecionado": inventario.espaco_selecionado,
        "aberto": inventario.aberto,
    }

    # Prepara os retângulos de colisão.
    colisoes = []

    for retangulo in objetos_colisao:
        if not all(
            hasattr(retangulo, atributo)
            for atributo in ("x", "y", "width", "height")
        ):
            raise TypeError(
                "Todos os objetos de colisão precisam ter "
                "x, y, width e height."
            )

        colisoes.append((
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

    # Salva tudo em uma única transação.
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

        # Substitui as colisões anteriormente salvas deste mapa.
        conexao.execute("""
            DELETE FROM colisoes
            WHERE mapa_atual = ?
        """, (mapa_atual,))

        conexao.executemany("""
            INSERT INTO colisoes (
                mapa_atual,
                x,
                y,
                largura,
                altura
            )
            VALUES (?, ?, ?, ?, ?)
        """, colisoes)


# =========================================================
# CARREGAR PARTIDA COMPLETA
# =========================================================

def carregar_partida(
    jogador,
    inventario,
    mapa_padrao="mapa_inicial",
):
    """
    Carrega a partida salva.

    Retorna None caso não exista uma partida completa.
    Caso exista, retorna o mapa e suas colisões.
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
            linha_mapa[0] if linha_mapa else mapa_padrao
        )

        linhas_colisoes = conexao.execute("""
            SELECT x, y, largura, altura
            FROM colisoes
            WHERE mapa_atual = ?
            ORDER BY id
        """, (mapa_atual,)).fetchall()

    # Restaura os atributos do personagem.
    for nome, valor in dados_personagem.items():
        if nome in (
            "equipamentos",
            "inventario_personagem",
            "atributos_distribuidos",
        ):
            continue

        if hasattr(jogador, nome):
            setattr(jogador, nome, valor)

    if "atributos_distribuidos" in dados_personagem:
        jogador.atributos_distribuidos = {
            chave: max(0, int(valor))
            for chave, valor in dados_personagem["atributos_distribuidos"].items()
            if chave in ("vitalidade", "forca", "defesa", "agilidade")
        }

    # Restaura os equipamentos.
    if "equipamentos" in dados_personagem:
        if hasattr(jogador, "equipamentos"):
            jogador.equipamentos.update(
                dados_personagem["equipamentos"]
            )

    # Restaura o inventário interno do personagem.
    if "inventario_personagem" in dados_personagem:
        if hasattr(jogador, "inventario"):
            jogador.inventario = _desserializar(
                dados_personagem["inventario_personagem"]
            )

    if hasattr(jogador, "recalcular_atributos"):
        jogador.recalcular_atributos()

    # Atualiza a caixa de colisão para a posição carregada.
    if hasattr(jogador, "colisao"):
        jogador.colisao.topleft = (
            round(jogador.x),
            round(jogador.y),
        )

    # Restaura os espaços do inventário visual.
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

    if (
        isinstance(selecionado, int)
        and 0 <= selecionado < total_espacos
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
