import pygame
from cores import *


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
# PAREDE
# =========================

parede_x = 300
parede_y = 200

parede_largura = 100
parede_altura = 100


# =========================
# LOOP PRINCIPAL
# =========================

rodando = True

while rodando:

    # -------------------------
    # EVENTOS
    # -------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            rodando = False


    # -------------------------
    # TECLAS (W, A, S, D)
    # -------------------------

    teclas = pygame.key.get_pressed()
    #direita
    if teclas[pygame.K_d]:
        x += velocidade

        jogador.x = x - tamanho_jogador

        if jogador.colliderecta(parede):
            x -= velocidade
    #esquerda
    if teclas[pygame.K_a]:
        x -= velocidade

        jogador.x = x - tamanho_jogador

        if jogador.colliderect(parede):
            x += velocidade
    #baixo
    if teclas[pygame.K_s]:
        y += velocidade

        jogador.y = y - tamanho_jogador

        if jogador.colliderect(parede):
            y -= velocidade
    #cima
    if teclas[pygame.K_w]:
        y -= velocidade

        jogador.y = y - tamanho_jogador

        if jogador.colliderect(parede):
            y += velocidade


    # -------------------------
    # RETÂNGULOS DE COLISÃO
    # -------------------------

    jogador = pygame.Rect(
        x - tamanho_jogador,
        y - tamanho_jogador,
        tamanho_jogador * 2,
        tamanho_jogador * 2
    )

    parede = pygame.Rect(
        parede_x,
        parede_y,
        parede_largura,
        parede_altura
    )


    # -------------------------
    # DESENHO
    # -------------------------

    tela.fill(AmareloClaro)

    # Jogador
    pygame.draw.circle(
        tela,
        Vermelho,
        (x, y),
        tamanho_jogador
    )

    # Parede
    pygame.draw.rect(
        tela,
        Preto,
        parede
    )

    # -------------------------
    # ATUALIZAÇÃO DA TELA
    # -------------------------

    pygame.display.flip()
    clock.tick(60)


# =========================
# FINALIZAÇÃO
# =========================

pygame.quit()
