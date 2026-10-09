
import pygame

from cores import *
from Personagem import Personagem
from banco import criar_banco, salvar_posicao, carregar_posicao
from inventario import Inventario


# =========================
# INICIALIZACAO
# =========================

pygame.init()

LARGURA_TELA = 800
ALTURA_TELA = 600

tela = pygame.display.set_mode(
    (LARGURA_TELA, ALTURA_TELA)
)

pygame.display.set_caption("Sem nome")

clock = pygame.time.Clock()

criar_banco()


# =========================
# MAPA E CAMERA
# =========================

camera_x = 0
camera_y = 0

mapa_largura = 30000
mapa_altura = 20000


# =========================
# JOGADOR
# =========================

jogador = Personagem(
    "Jogador",
    "frame_70000",
    6
)

posicao = carregar_posicao()

if posicao:
    jogador.x = posicao[0]
    jogador.y = posicao[1]

jogador.colisao.topleft = (
    jogador.x,
    jogador.y
)


# =========================
# INVENTARIO
# =========================

inventario = Inventario()


# =========================
# PAREDE
# =========================

parede = pygame.Rect(
    300,
    200,
    100,
    100
)


# =========================
# OBJETOS COM COLISAO
# =========================

objetos_colisao = [
    parede
]


# =========================
# LOOP PRINCIPAL
# =========================

rodando = True

while rodando:

    tempo = clock.tick(60)

    # =========================
    # EVENTOS
    # =========================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            salvar_posicao(
                jogador.x,
                jogador.y
            )

            rodando = False

        else:
            inventario.tratar_evento(event)

    if not rodando:
        break

    # =========================
    # MOVIMENTO DO JOGADOR
    # =========================

    teclas = pygame.key.get_pressed()

    if not inventario.aberto:
        jogador.atualizar(
            teclas,
            tempo,
            objetos_colisao,
            mapa_largura,
            mapa_altura
        )

    else:
        # Mantem o jogador parado com o inventario aberto.
        jogador.andando = False
        jogador.atualizar_animacao(tempo)

    # =========================
    # CAMERA
    # =========================

    camera_x = jogador.x - LARGURA_TELA // 2
    camera_y = jogador.y - ALTURA_TELA // 2

    # =========================
    # DESENHO DO MUNDO
    # =========================

    tela.fill(AmareloClaro)

    pygame.draw.rect(
        tela,
        Preto,
        (
            parede.x - camera_x,
            parede.y - camera_y,
            parede.width,
            parede.height
        )
    )

    jogador.desenhar(
        tela,
        camera_x,
        camera_y
    )

    # =========================
    # INTERFACE DO INVENTARIO
    # =========================

    inventario.desenhar(tela)

    # =========================
    # ATUALIZACAO DA TELA
    # =========================

    pygame.display.flip()


# =========================
# FINALIZACAO
# =========================

pygame.quit()
