import pygame
from cores import *
from personagem import *
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
# JOGADOR
# =========================

jogador = Personagem(
    "Jogador",
    "jogador",
    4
)

# Carrega a posição salva
posicao = carregar_posicao()

if posicao:
    jogador.x = posicao[0]
    jogador.y = posicao[1]

    jogador.colisao.x = jogador.x
    jogador.colisao.y = jogador.y


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
        objetos_colisao
    )


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

    # Jogador
    jogador.desenhar(tela)


    # =========================
    # ATUALIZAÇÃO DA TELA
    # =========================

    pygame.display.flip()

    clock.tick(60)


# =========================
# FINALIZAÇÃO
# =========================

pygame.quit()
O que foi mantido do seu código
criar_banco()
salvar_posicao()
carregar_posicao()
Carregamento da posição ao iniciar
Salvamento ao fechar
Sua parede
Sua resolução 800x600
Seu clock
Suas cores
Sua estrutura de comentários
O que foi acrescentado
O jogador agora é:

jogador = Personagem(
    "Jogador",
    "jogador",
    4
)
E a parede é passada para o sistema de colisão:

objetos_colisao = [
    parede
]
Depois:

jogador.atualizar(
    teclas,
    clock.get_time(),
    objetos_colisao
)
