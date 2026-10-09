
import pygame

from cores import *
from Personagem import Personagem
from banco import (
    criar_banco,
    salvar_partida,
    carregar_partida,
    carregar_posicao,
)
from inventario import Inventario


# =========================================================
# INICIALIZAÇÃO
# =========================================================

pygame.init()

LARGURA_TELA = 800
ALTURA_TELA = 600

tela = pygame.display.set_mode(
    (LARGURA_TELA, ALTURA_TELA)
)

pygame.display.set_caption("Sem nome")

clock = pygame.time.Clock()

criar_banco()


# =========================================================
# MAPA E CÂMERA
# =========================================================

camera_x = 0
camera_y = 0

mapa_largura = 30000
mapa_altura = 20000

mapa_atual = "mapa_inicial"


# =========================================================
# JOGADOR
# =========================================================

jogador = Personagem(
    "Jogador",
    "frame_70000",
    6
)

# Compatibilidade com o salvamento antigo de posição.
posicao = carregar_posicao()

if posicao is not None:
    jogador.x = posicao[0]
    jogador.y = posicao[1]

jogador.colisao.topleft = (
    round(jogador.x),
    round(jogador.y),
)


# =========================================================
# INVENTÁRIO
# =========================================================

inventario = Inventario()


# =========================================================
# COLISÕES INICIAIS
# =========================================================

parede = pygame.Rect(
    300,
    200,
    100,
    100
)

objetos_colisao = [
    parede
]


# =========================================================
# RESTAURAR PARTIDA
# =========================================================

dados_salvos = carregar_partida(
    jogador,
    inventario,
    mapa_atual,
)

if dados_salvos is not None:
    mapa_atual = dados_salvos["mapa_atual"]

    # Reconstrói as colisões salvas no banco.
    objetos_colisao = [
        pygame.Rect(
            round(colisao["x"]),
            round(colisao["y"]),
            round(colisao["largura"]),
            round(colisao["altura"]),
        )
        for colisao in dados_salvos["colisoes"]
    ]


# =========================================================
# SALVAMENTO AUTOMÁTICO
# =========================================================

INTERVALO_SALVAMENTO = 10000
tempo_desde_salvamento = 0


def salvar_jogo():
    """Salva o estado atual completo da partida."""
    salvar_partida(
        jogador,
        inventario,
        objetos_colisao,
        mapa_atual,
    )


# =========================================================
# LOOP PRINCIPAL
# =========================================================

rodando = True

while rodando:

    tempo = clock.tick(60)

    tempo_desde_salvamento += tempo

    # Salva a partida a cada 10 segundos.
    if tempo_desde_salvamento >= INTERVALO_SALVAMENTO:
        salvar_jogo()
        tempo_desde_salvamento = 0

    # -----------------------------------------------------
    # EVENTOS
    # -----------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            salvar_jogo()
            rodando = False

        else:
            inventario.tratar_evento(event)

    if not rodando:
        break

    # -----------------------------------------------------
    # MOVIMENTO DO JOGADOR
    # -----------------------------------------------------

    teclas = pygame.key.get_pressed()

    if not inventario.aberto:
        jogador.atualizar(
            teclas,
            tempo,
            objetos_colisao,
            mapa_largura,
            mapa_altura,
        )

    else:
        jogador.andando = False
        jogador.atualizar_animacao(tempo)

    # -----------------------------------------------------
    # CÂMERA
    # -----------------------------------------------------

    camera_x = jogador.x - LARGURA_TELA // 2
    camera_y = jogador.y - ALTURA_TELA // 2

    # -----------------------------------------------------
    # DESENHO DO MUNDO
    # -----------------------------------------------------

    tela.fill(AmareloClaro)

    # Desenha todas as paredes e colisões.
    for objeto in objetos_colisao:
        pygame.draw.rect(
            tela,
            Preto,
            (
                objeto.x - camera_x,
                objeto.y - camera_y,
                objeto.width,
                objeto.height,
            ),
        )

    jogador.desenhar(
        tela,
        camera_x,
        camera_y,
    )

    # -----------------------------------------------------
    # INVENTÁRIO
    # -----------------------------------------------------

    inventario.desenhar(tela)

    # -----------------------------------------------------
    # ATUALIZAÇÃO DA TELA
    # -----------------------------------------------------

    pygame.display.flip()


# =========================================================
# FINALIZAÇÃO
# =========================================================

pygame.quit()
