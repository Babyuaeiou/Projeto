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
# ANIMAÇÃO
# =========================

frames = [
    pygame.image.load("frame_70000.png").convert_alpha(),
    pygame.image.load("frame_70000 (1).png").convert_alpha(),
    pygame.image.load("frame_70000 (2).png").convert_alpha(),
    pygame.image.load("frame_70000 (3).png").convert_alpha(),
    pygame.image.load("frame_70000 (4).png").convert_alpha(),
    pygame.image.load("frame_70000 (5).png").convert_alpha(),
    pygame.image.load("frame_70000 (6).png").convert_alpha()
]

for i in range(len(frames)):
    frames[i] = pygame.transform.scale(
        frames[i],
        (tamanho_jogador * 2, tamanho_jogador * 2)
    )

frame_atual = 0
contador = 0


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

    # -------------------------
    # EVENTOS
    # -------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            rodando = False


    # -------------------------
    # CONTADOR DA ANIMAÇÃO
    # -------------------------

    contador += 1

    if contador >= 10:

        frame_atual += 1
        contador = 0

        if frame_atual >= len(frames):
            frame_atual = 0


    # -------------------------
    # TECLAS (W, A, S, D)
    # -------------------------

    teclas = pygame.key.get_pressed()


    # DIREITA
    if teclas[pygame.K_d]:

        x += velocidade

        jogador.x = x - tamanho_jogador

        if jogador.colliderect(parede):
            x -= velocidade


    # ESQUERDA
    if teclas[pygame.K_a]:

        x -= velocidade

        jogador.x = x - tamanho_jogador

        if jogador.colliderect(parede):
            x += velocidade


    # BAIXO
    if teclas[pygame.K_s]:

        y += velocidade

        jogador.y = y - tamanho_jogador

        if jogador.colliderect(parede):
            y -= velocidade


    # CIMA
    if teclas[pygame.K_w]:

        y -= velocidade

        jogador.y = y - tamanho_jogador

        if jogador.colliderect(parede):
            y += velocidade


    # =========================
    # DESENHO
    # =========================

    tela.fill(AmareloClaro)


    # Jogador
    tela.blit(
        frames[frame_atual],
        (x - tamanho_jogador, y - tamanho_jogador)
    )


    # Parede
    pygame.draw.rect(
        tela,
        Preto,
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
