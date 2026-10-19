
import pygame

from cores import *
from personagem import Personagem, Inimigo, Batalha
from banco import (
    criar_banco,
    salvar_posicao,
    carregar_posicao,
    salvar_partida,
    carregar_partida,
)
from inventario import Inventario
from item import catalogo
from floresta import Floresta


# =========================================================
# INICIALIZAÇÃO
# =========================================================

pygame.init()

LARGURA_TELA = 800
ALTURA_TELA = 600

tela = pygame.display.set_mode(
    (LARGURA_TELA, ALTURA_TELA)
)
pygame.display.set_caption("Hunt Bird")

clock = pygame.time.Clock()
fonte = pygame.font.Font(None, 24)
fonte_grande = pygame.font.Font(None, 34)

criar_banco()


# =========================================================
# MAPA E FLORESTA
# =========================================================

mapa_largura = 2400
mapa_altura = 1800
mapa_atual = "mapa_inicial"

floresta = Floresta(
    largura=600,
    altura=mapa_altura
)


# =========================================================
# JOGADOR E INVENTÁRIO
# =========================================================

jogador = Personagem(
    "Servo do Rei Demônio",
    "F1.png",
    3
)

jogador.equipamentos["arma"] = "punhos"
jogador.equipamentos["armadura"] = None
jogador.recalcular_atributos()

jogador.adicionar_item("pocao_pequena", 2)
jogador.adicionar_item("pedra_afiacao", 1)

inventario = Inventario()
inventario.sincronizar_do_personagem(jogador)


# =========================================================
# COLISÕES
# =========================================================

objetos_colisao = list(floresta.colisoes)

objetos_colisao.extend([
    pygame.Rect(650, 380, 120, 170),
    pygame.Rect(1000, 250, 180, 90),
])


# =========================================================
# CARREGAR PARTIDA
# =========================================================

dados = carregar_partida(
    jogador,
    inventario,
    mapa_atual
)

if dados:
    mapa_atual = dados["mapa_atual"]

    colisoes_salvas = [
        pygame.Rect(
            int(c["x"]),
            int(c["y"]),
            int(c["largura"]),
            int(c["altura"])
        )
        for c in dados.get("colisoes", [])
    ]

    existentes = {
        (r.x, r.y, r.width, r.height)
        for r in objetos_colisao
    }

    for retangulo in colisoes_salvas:
        chave = (
            retangulo.x,
            retangulo.y,
            retangulo.width,
            retangulo.height
        )

        if chave not in existentes:
            objetos_colisao.append(retangulo)
            existentes.add(chave)

else:
    posicao = carregar_posicao()

    if posicao:
        jogador.x, jogador.y = posicao
        jogador.colisao.topleft = (
            round(jogador.x),
            round(jogador.y)
        )


# =========================================================
# INIMIGO ÚNICO
# =========================================================
# Por enquanto, o inimigo aparece como um retângulo colorido.
# Você poderá colocar o sprite dele depois.
# =========================================================

inimigos = [
    Inimigo(
        nome="Lobo Selvagem",
        hpmaximo=22,
        dano=6,
        defesa=2,
        x=760,
        y=520,
        xp_recompensa=18,
        moedas_recompensa=10,
        chefe=False,
        cor=(130, 110, 80)
    )
]


# =========================================================
# ESTADO DO JOGO
# =========================================================

batalha = None

mensagem = "Explore a floresta e encontre o caminho para o vilarejo."
mensagem_tempo = 7.0

loja_aberta = False
loja_cursor = 0

# C alterna a exibição das coordenadas.
mostrar_coordenadas = False

itens_loja = [
    ("pocao_pequena", 10),
    ("pocao_grande", 35),
    ("elixir_servo", 75),
    ("pedra_afiacao", 20),
    ("espada_enferrujada", 25),
    ("armadura_couro", 30),
    ("espada_ferro", 80),
    ("armadura_ferro", 90),
]


# =========================================================
# SALVAMENTO
# =========================================================

def salvar_jogo():
    inventario.sincronizar_para_personagem(jogador)

    salvar_partida(
        jogador,
        inventario,
        objetos_colisao,
        mapa_atual
    )

    salvar_posicao(jogador.x, jogador.y)


# =========================================================
# MENSAGENS E TEXTO
# =========================================================

def mostrar_msg(texto, duracao=3):
    global mensagem, mensagem_tempo

    mensagem = texto
    mensagem_tempo = duracao


def desenhar_texto(
    texto,
    x,
    y,
    cor=(255, 255, 255),
    fonte_usada=None
):
    if fonte_usada is None:
        fonte_usada = fonte

    imagem = fonte_usada.render(
        str(texto),
        True,
        cor
    )

    tela.blit(imagem, (x, y))


# =========================================================
# COORDENADAS EM TEMPO REAL
# =========================================================

def desenhar_coordenadas():
    """
    Mostra a posição atual do jogador no mundo.
    Os valores são atualizados continuamente enquanto
    o jogador se movimenta.
    """

    x = int(jogador.x)
    y = int(jogador.y)

    texto_x = f"X: {x}"
    texto_y = f"Y: {y}"

    largura_painel = 150
    altura_painel = 66

    painel_x = LARGURA_TELA - largura_painel - 10
    painel_y = 10

    pygame.draw.rect(
        tela,
        (20, 25, 25),
        (
            painel_x,
            painel_y,
            largura_painel,
            altura_painel
        ),
        border_radius=6
    )

    pygame.draw.rect(
        tela,
        (220, 220, 220),
        (
            painel_x,
            painel_y,
            largura_painel,
            altura_painel
        ),
        1,
        border_radius=6
    )

    desenhar_texto(
        "COORDENADAS",
        painel_x + 10,
        painel_y + 7,
        (255, 220, 100)
    )

    desenhar_texto(
        texto_x,
        painel_x + 10,
        painel_y + 28
    )

    desenhar_texto(
        texto_y,
        painel_x + 78,
        painel_y + 28
    )


# =========================================================
# DESENHAR O MUNDO
# =========================================================

def desenhar_mundo(camera_x, camera_y):
    tela.fill((80, 135, 75))

    # Regiões do mundo.
    pygame.draw.rect(
        tela, (173, 145, 92),
        pygame.Rect(600 - camera_x, -camera_y, 600, mapa_altura)
    )

    pygame.draw.rect(
        tela, (45, 90, 52),
        pygame.Rect(1200 - camera_x, -camera_y, 600, mapa_altura)
    )

    pygame.draw.rect(
        tela, (105, 100, 110),
        pygame.Rect(1800 - camera_x, -camera_y, 600, mapa_altura)
    )

    # Caminhos.
    pygame.draw.rect(
        tela, (160, 130, 85),
        pygame.Rect(600 - camera_x, 820 - camera_y, 600, 150)
    )

    pygame.draw.rect(
        tela, (160, 130, 85),
        pygame.Rect(900 - camera_x, 820 - camera_y, 100, 700)
    )

    pygame.draw.rect(
        tela, (135, 112, 81),
        pygame.Rect(1200 - camera_x, 820 - camera_y, 600, 150)
    )

    pygame.draw.rect(
        tela, (120, 105, 85),
        pygame.Rect(1800 - camera_x, 820 - camera_y, 600, 150)
    )

    # Floresta.
    floresta.desenhar(tela, camera_x, camera_y)

    # Único inimigo.
    for inimigo in inimigos:
        if not inimigo.derrotado:
            inimigo.desenhar(tela, camera_x, camera_y)

    # Jogador.
    jogador.desenhar(tela, camera_x, camera_y)

    # HUD: atributos do jogador.
    pygame.draw.rect(
        tela, (20, 25, 25),
        (8, ALTURA_TELA - 63, 300, 54),
        border_radius=6
    )

    desenhar_texto(
        f"Nv. {jogador.nivel}  HP {jogador.hp}/{jogador.hpmaximo}",
        18, ALTURA_TELA - 56
    )

    desenhar_texto(
        f"Dano {jogador.danototal}  "
        f"Defesa {jogador.defesatotal}  "
        f"Moedas {jogador.moedas}",
        18, ALTURA_TELA - 32
    )

    # Coordenadas aparecem somente quando C estiver ativado.
    if mostrar_coordenadas:
        desenhar_coordenadas()

    # Mensagens temporárias, como compras e salvamentos.
    if mensagem_tempo > 0:
        pygame.draw.rect(
            tela, (20, 20, 20),
            (70, 50, 660, 38),
            border_radius=5
        )

        desenhar_texto(
            mensagem, 82, 59, (255, 240, 180)
        )


# =========================================================
# LOJA
# =========================================================

def desenhar_loja():
    pygame.draw.rect(
        tela,
        (20, 22, 28),
        (90, 55, 620, 490),
        border_radius=10
    )

    pygame.draw.rect(
        tela,
        (190, 170, 100),
        (90, 55, 620, 490),
        3,
        border_radius=10
    )

    desenhar_texto(
        "LOJA DO VILAREJO",
        120,
        75,
        (255, 225, 145),
        fonte_grande
    )

    desenhar_texto(
        f"Suas moedas: {jogador.moedas}",
        120,
        115
    )

    for i, (item_id, preco) in enumerate(itens_loja):
        item = catalogo.obter(item_id)

        if item is None:
            continue

        cor = (
            (255, 225, 100)
            if i == loja_cursor
            else (240, 240, 240)
        )

        prefixo = "> " if i == loja_cursor else "  "

        desenhar_texto(
            f"{prefixo}{item.nome} - {preco} moedas",
            130,
            160 + i * 35,
            cor
        )

    desenhar_texto(
        "ENTER/Z comprar | ESC fechar",
        120,
        500,
        (210, 210, 210)
    )


# =========================================================
# LOOP PRINCIPAL
# =========================================================

rodando = True

while rodando:
    dt = min(clock.tick(60) / 1000, 0.05)
    mensagem_tempo = max(0, mensagem_tempo - dt)

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            salvar_jogo()
            rodando = False

        elif batalha is not None:
            batalha.processar_evento(evento)

            if batalha.terminada:
                if batalha.vitoria:
                    batalha.inimigo.derrotado = True

                    mostrar_msg(
                        f"Você venceu! +"
                        f"{batalha.inimigo.xp_recompensa} XP "
                        f"e +{batalha.inimigo.moedas_recompensa} moedas.",
                        5
                    )

                elif batalha.derrota:
                    jogador.hp = jogador.hpmaximo
                    jogador.x = 650
                    jogador.y = 150

                    jogador.colisao.topleft = (
                        round(jogador.x),
                        round(jogador.y)
                    )

                    mostrar_msg(
                        "Você voltou ao vilarejo e recuperou o HP.",
                        5
                    )

                batalha = None
                salvar_jogo()

        elif loja_aberta:
            if evento.type == pygame.KEYDOWN:

                if evento.key in (pygame.K_ESCAPE, pygame.K_l):
                    loja_aberta = False

                elif evento.key in (pygame.K_UP, pygame.K_w):
                    loja_cursor = (
                        loja_cursor - 1
                    ) % len(itens_loja)

                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    loja_cursor = (
                        loja_cursor + 1
                    ) % len(itens_loja)

                elif evento.key in (pygame.K_RETURN, pygame.K_z):
                    item_id, preco = itens_loja[loja_cursor]

                    if jogador.moedas < preco:
                        mostrar_msg(
                            "Você não tem moedas suficientes."
                        )

                    else:
                        item = catalogo.obter(item_id)

                        if item is None:
                            mostrar_msg(
                                "Esse item não existe no catálogo."
                            )
                        else:
                            jogador.moedas -= preco
                            jogador.adicionar_item(item_id, 1)

                            inventario.sincronizar_do_personagem(
                                jogador
                            )

                            mostrar_msg(
                                f"Comprou {item.nome}."
                            )

                            salvar_jogo()

        elif inventario.aberto:
            if inventario.tratar_evento(evento, jogador):
                inventario.sincronizar_para_personagem(
                    jogador
                )

        elif evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_ESCAPE:
                salvar_jogo()
                rodando = False

            elif evento.key == pygame.K_F5:
                salvar_jogo()
                mostrar_msg("Jogo salvo.")

            elif evento.key == pygame.K_c:
                # Alterna as coordenadas sem abrir uma mensagem temporária.
                mostrar_coordenadas = not mostrar_coordenadas

            elif evento.key == pygame.K_e:
                inventario.tratar_evento(
                    evento,
                    jogador
                )

            elif evento.key == pygame.K_l:
                if (
                    600 <= jogador.x <= 1200
                    and 80 <= jogador.y <= 260
                ):
                    loja_aberta = True
                else:
                    mostrar_msg("A loja fica no vilarejo.")

    # =====================================================
    # ATUALIZAR JOGADOR E ENCONTRO
    # =====================================================

    if (
        rodando
        and batalha is None
        and not loja_aberta
        and not inventario.aberto
    ):
        jogador.atualizar(
            pygame.key.get_pressed(),
            dt,
            objetos_colisao,
            mapa_largura,
            mapa_altura
        )

        # Inicia a batalha ao encostar no único inimigo.
        for inimigo in inimigos:
            if (
                not inimigo.derrotado
                and jogador.colisao.colliderect(inimigo.colisao)
            ):
                batalha = Batalha(jogador, inimigo)
                break

        # Cura ao entrar na praça do vilarejo.
        if (
            650 < jogador.x < 900
            and 100 < jogador.y < 230
            and jogador.hp < jogador.hpmaximo
        ):
            jogador.hp = jogador.hpmaximo

    # =====================================================
    # CÂMERA
    # =====================================================

    camera_x = max(
        0,
        min(
            mapa_largura - LARGURA_TELA,
            jogador.x - LARGURA_TELA // 2
        )
    )

    camera_y = max(
        0,
        min(
            mapa_altura - ALTURA_TELA,
            jogador.y - ALTURA_TELA // 2
        )
    )

    # =====================================================
    # DESENHO
    # =====================================================

    if batalha is not None:
        batalha.desenhar(tela)

    else:
        desenhar_mundo(camera_x, camera_y)

        if loja_aberta:
            desenhar_loja()
        else:
            inventario.desenhar(tela, jogador)

    pygame.display.flip()


# =========================================================
# ENCERRAMENTO
# =========================================================

salvar_jogo()
pygame.quit()
