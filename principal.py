import pygame
from cores import *
from personagem import *


# =========================
# INICIALIZAÇÃO
# =========================

pygame.init()

tela = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sem nome")

clock = pygame.time.Clock()


# =========================
# JOGADOR
# =========================

x = 100
y = 100

velocidade = 5
tamanho_jogador = 25

# =========================
# RETÂNGULO DO JOGADOR
# =========================

jogador = pygame.Rect(
    x - tamanho_jogador,
    y - tamanho_jogador,
    tamanho_jogador * 2,
    tamanho_jogador * 2
)


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
# LOOP PRINCIPAL
# =========================

rodando = True

while rodando:

    # =========================
    # EVENTOS
    # =========================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            rodando = False

    else:
        frame_atual = 0
        andando = 0


    # =========================
    # DESENHO
    # =========================

    tela.fill(AMARELO)

    # Parede
    pygame.draw.rect(
        tela,
        PRETO,
        parede
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

