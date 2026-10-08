import pygame
from cores import *
from personagem import  Personagem
from banco import criar_banco, salvar_posicao, carregar_posicao


# =========================
# INICIALIZAÇÃO
# =========================

pygame.init()

criar_banco()

tela = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sem nome")

clock = pygame.time.Clock()

#==========================
# CAMERA
#==========================

camera_x = 0
camera_y = 0

mapa_largura = 30000
mapa_altura = 20000

mapa = pygame.surface(
    (mapa_largura,mapa_altura)
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

    #==========================
    # ATUALIZAÇÃO DA CAMERA
    #==========================

    camera_x = jogador.x - 800 // 2
    camera_y = jogador.y - 600 // 2

    # =========================
    # DESENHO
    # =========================

    tela.fill(Amarelo)

    # Parede
    pygame.draw.rect(
        tela,
        Preto,
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

# =========================
# LIMITAÇÃO DO JOGADOR
# =========================

# A limitação do jogador serve para impedir que o personagem saia
# dos limites definidos pelo mapa.
#
# O mapa possui uma largura e uma altura determinadas pelas variáveis
# MAPA_LARGURA e MAPA_ALTURA.
#
# A posição X do jogador controla o movimento horizontal,
# ou seja, o movimento para a esquerda e para a direita.
#
# Se o jogador tentar ultrapassar o lado esquerdo do mapa,
# sua posição X será corrigida para 0.
#
# Se o jogador tentar ultrapassar o lado direito do mapa,
# sua posição X será corrigida para o valor máximo da largura do mapa.
#
# A posição Y do jogador controla o movimento vertical,
# ou seja, o movimento para cima e para baixo.
#
# Se o jogador tentar ultrapassar o topo do mapa,
# sua posição Y será corrigida para 0.
#
# Se o jogador tentar ultrapassar a parte inferior do mapa,
# sua posição Y será corrigida para o valor máximo da altura do mapa.
#
# Dessa forma, o personagem fica preso dentro da área do mapa
# e não consegue sair pelos cantos ou pelas laterais.


# =========================
# ATUALIZAÇÃO DA CÂMERA
# =========================

# A câmera é responsável por mostrar uma parte do mapa na tela.
#
# A tela possui 800 pixels de largura e 600 pixels de altura.
#
# A câmera acompanha a posição do jogador para mantê-lo
# aproximadamente no centro da tela.
#
# Para encontrar a posição horizontal da câmera,
# pegamos a posição X do jogador e diminuímos metade da largura da tela.
#
# Para encontrar a posição vertical da câmera,
# pegamos a posição Y do jogador e diminuímos metade da altura da tela.
#
# Dessa forma, quando o jogador se movimenta,
# a câmera também se movimenta junto com ele.
#
# Isso cria o efeito de que o personagem está sendo acompanhado
# pela câmera enquanto anda pelo mapa.


# =========================
# LIMITAÇÃO DA CÂMERA
# =========================

# A câmera também precisa possuir limites.
#
# Se a câmera não tivesse limites, quando o jogador chegasse
# perto das bordas do mapa, ela poderia tentar mostrar uma área
# que não existe.
#
# Primeiro, impedimos que a câmera ultrapasse o lado esquerdo.
#
# Se a posição X da câmera ficar menor que 0,
# ela será corrigida para 0.
#
# Depois, impedimos que a câmera ultrapasse o lado direito.
#
# Para isso, usamos a largura do mapa menos a largura da tela.
#
# Por exemplo, se o mapa possui 3000 pixels de largura
# e a tela possui 800 pixels de largura,
# a câmera pode chegar no máximo até a posição 2200.
#
# Isso acontece porque 3000 menos 800 é igual a 2200.
#
# Dessa forma, a câmera consegue mostrar os últimos 800 pixels
# do mapa sem mostrar uma área que esteja fora dele.
#
# O mesmo processo acontece no eixo vertical.
#
# A câmera não pode ficar com uma posição Y menor que 0,
# pois isso faria com que ela tentasse mostrar uma área acima do mapa.
#
# Também não pode ultrapassar a altura do mapa menos a altura da tela.
#
# Por exemplo, se o mapa possui 2000 pixels de altura
# e a tela possui 600 pixels de altura,
# a câmera pode chegar no máximo até a posição 1400.
#
# Isso acontece porque 2000 menos 600 é igual a 1400.
#
# Portanto, a limitação do jogador impede que o personagem
# saia do mapa.
#
# A limitação da câmera impede que a câmera mostre áreas
# que estão fora do mapa.
#
# A câmera funciona como uma janela que se movimenta pelo mapa,
# acompanhando o jogador.
#
# Quando o jogador está no centro do mapa, a câmera acompanha
# normalmente o seu movimento.
#
# Quando o jogador chega perto de uma borda,
# a câmera para naquela direção para não mostrar áreas vazias
# que estão fora dos limites do mapa.
