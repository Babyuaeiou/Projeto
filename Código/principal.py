import pygame
from cores import *
from personagem import Personagem
from banco import criar_banco, salvar_posicao, carregar_posicao


# =========================
# INICIALIZAÇÃO
# =========================

pygame.init()

criar_banco()

tela = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sem nome")

clock = pygame.time.Clock()


# =========================
# CAMERA
# =========================

camera_x = 0
camera_y = 0

mapa_largura = 30000
mapa_altura = 20000

mapa = pygame.Surface(
    (mapa_largura, mapa_altura)
)


# =========================
# JOGADOR
# =========================

jogador = Personagem(
    "Jogador",
    "frame_70000",
    6
)

# Carrega a posição salva
posicao = carregar_posicao()

if posicao:
    jogador.x = posicao[0]
    jogador.y = posicao[1]

# Sincroniza a caixa de colisão com o jogador
jogador.colisao.topleft = (jogador.x, jogador.y)


# =========================
# PAREDE
# =========================

parede_x = 300
parede_y = 200

parede_largura = 100
parede_altura = 100

parede = pygame.Rect(
    parede_x,
    parede_y,
    parede_largura,
    parede_altura
)


# =========================
# OBJETOS COM COLISÃO
# =========================

objetos_colisao = [
    parede
]


# =========================
# LOOP PRINCIPAL
# =========================

rodando = True

while rodando:

    # =========================
    # EVENTOS
    # =========================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            # Salva a posição antes de fechar
            salvar_posicao(
                jogador.x,
                jogador.y
            )

            rodando = False


    # =========================
    # MOVIMENTO
    # =========================

    teclas = pygame.key.get_pressed()

    jogador.atualizar(
        teclas,
        clock.get_time(),
        objetos_colisao,
        mapa_largura,
        mapa_altura
    )


    # ==========================
    # ATUALIZAÇÃO DA CÂMERA
    # ==========================

    # A câmera acompanha o jogador em X e Y
    # sem limitar as coordenadas a zero.

    camera_x = jogador.x - 800 // 2
    camera_y = jogador.y - 600 // 2


    # =========================
    # DESENHO
    # =========================

    tela.fill(AmareloClaro)

    # Parede
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

    # Jogador
    jogador.desenhar(
        tela,
        camera_x,
        camera_y
    )


    # =========================
    # ATUALIZAÇÃO DA TELA
    # =========================

    pygame.display.flip()

    clock.tick(60)


# =========================
# FINALIZAÇÃO
# =========================

pygame.quit()
