import sqlite3


def criar_banco():
    conexao = sqlite3.connect("jogo.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personagem (
            id INTEGER PRIMARY KEY,
            x REAL NOT NULL,
            y REAL NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


def salvar_posicao(x, y):
    conexao = sqlite3.connect("jogo.db")
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO personagem (id, x, y)
        VALUES (1, ?, ?)
    """, (x, y))

    conexao.commit()
    conexao.close()


def carregar_posicao():
    conexao = sqlite3.connect("jogo.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT x, y
        FROM personagem
        WHERE id = 1
    """)

    resultado = cursor.fetchone()

    conexao.close()

    if resultado:
        return resultado

    return None
