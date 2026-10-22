
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
# MAPA
# =========================================================

mapa_largura = 2400
mapa_altura = 1800
mapa_atual = "mapa_inicial"

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

objetos_colisao = []

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

else:
    posicao = carregar_posicao()

    if posicao:
        jogador.x, jogador.y = posicao
        jogador.colisao.topleft = (
            round(jogador.x),
            round(jogador.y)
        )

# =========================================================
# INIMIGOS
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

loja_aberta = False
loja_cursor = 0

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
# TEXTO
# =========================================================

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
# COORDENADAS E FPS
# =========================================================

def desenhar_coordenadas():
    x = int(jogador.x)
    y = int(jogador.y)
    fps = int(clock.get_fps())

    largura_painel = 170
    altura_painel = 90

    # Canto superior esquerdo, separado do minimapa.
    painel_x = 10
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
        f"X: {x}  Y: {y}",
        painel_x + 10,
        painel_y + 32
    )

    desenhar_texto(
        f"FPS: {fps}",
        painel_x + 10,
        painel_y + 57,
        (120, 255, 120)
    )

# =========================================================
# MINIMAPA
# =========================================================

def desenhar_minimapa():
    largura_minimapa = 180
    altura_minimapa = 135
    margem = 10

    x_minimapa = LARGURA_TELA - largura_minimapa - margem
    y_minimapa = margem

    pygame.draw.rect(
        tela,
        (20, 25, 25),
        (
            x_minimapa,
            y_minimapa,
            largura_minimapa,
            altura_minimapa
        ),
        border_radius=5
    )

    area = pygame.Rect(
        x_minimapa + 3,
        y_minimapa + 3,
        largura_minimapa - 6,
        altura_minimapa - 6
    )

    escala_x = area.width / mapa_largura
    escala_y = area.height / mapa_altura

    def converter_x(valor):
        return area.x + round(valor * escala_x)

    def converter_y(valor):
        return area.y + round(valor * escala_y)

    # Representação neutra do mapa.
    pygame.draw.rect(
        tela,
        (85, 85, 90),
        area
    )

    # Jogador.
    pygame.draw.circle(
        tela,
        (60, 160, 255),
        (
            converter_x(jogador.x),
            converter_y(jogador.y)
        ),
        4
    )

    # Inimigos.
    for inimigo in inimigos:
        if not inimigo.derrotado:
            pygame.draw.circle(
                tela,
                (235, 55, 55),
                (
                    converter_x(inimigo.x),
                    converter_y(inimigo.y)
                ),
                3
            )

    pygame.draw.rect(
        tela,
        (230, 230, 230),
        (
            x_minimapa,
            y_minimapa,
            largura_minimapa,
            altura_minimapa
        ),
        2,
        border_radius=5
    )

# =========================================================
# DESENHAR O MUNDO
# =========================================================

def desenhar_mundo(camera_x, camera_y):
    tela.fill((85, 85, 90))

    # Inimigos.
    for inimigo in inimigos:
        if not inimigo.derrotado:
            inimigo.desenhar(tela, camera_x, camera_y)

    # Jogador.
    jogador.desenhar(tela, camera_x, camera_y)

    # HUD.
    pygame.draw.rect(
        tela,
        (20, 25, 25),
        (8, ALTURA_TELA - 63, 340, 54),
        border_radius=6
    )

    desenhar_texto(
        f"Nv. {jogador.nivel}  HP {jogador.hp}/{jogador.hpmaximo}",
        18,
        ALTURA_TELA - 56
    )

    desenhar_texto(
        f"Dano {jogador.danototal}  "
        f"Defesa {jogador.defesatotal}  "
        f"Moedas {jogador.moedas}",
        18,
        ALTURA_TELA - 32
    )

    # Primeiro desenha o minimapa.
    desenhar_minimapa()

    # Depois desenha o painel por cima do cenário.
    if mostrar_coordenadas:
        desenhar_coordenadas()

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
        "LOJA",
        120,
        75,
        (255, 225, 145),
        fonte_grande
    )

    desenhar_texto(
        f"Moedas: {jogador.moedas}",
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

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        elif batalha is not None:
            batalha.processar_evento(evento)

            if batalha.terminada:
                if batalha.vitoria:
                    batalha.inimigo.derrotado = True

                elif batalha.derrota:
                    jogador.hp = jogador.hpmaximo
                    jogador.x = 650
                    jogador.y = 150

                    jogador.colisao.topleft = (
                        round(jogador.x),
                        round(jogador.y)
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

                    if jogador.moedas >= preco:
                        item = catalogo.obter(item_id)

                        if item is not None:
                            jogador.moedas -= preco
                            jogador.adicionar_item(item_id, 1)

                            inventario.sincronizar_para_personagem(
                                jogador
                            )

                            salvar_jogo()

        elif inventario.aberto:
            if inventario.tratar_evento(evento, jogador):
                inventario.sincronizar_para_personagem(
                    jogador
                )

        elif evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_ESCAPE:
                rodando = False

            elif evento.key == pygame.K_F5:
                salvar_jogo()

            elif evento.key == pygame.K_c:
                mostrar_coordenadas = not mostrar_coordenadas

            elif evento.key == pygame.K_e:
                inventario.tratar_evento(
                    evento,
                    jogador
                )

            elif evento.key == pygame.K_l:
                loja_aberta = True

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

        # Inicia a batalha ao encostar no inimigo.
        for inimigo in inimigos:
            if (
                not inimigo.derrotado
                and jogador.colisao.colliderect(inimigo.colisao)
            ):
                batalha = Batalha(jogador, inimigo)
                break

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
