import pygame
from cores import *
#inicialização
pygame.init()

tela = pygame.display.set_mode((800,600))
pygame.display.set_caption('sem nome')
time =pygame.time.Clock()
#jogador
x = 100
y = 100
velocidade = 5
#colisão
parede_x = 800
parede_y = 600
parede_largura = 100
parede_altura = 50
#loop 
rodando = True
while rodando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
    #teclas (w,a,s,d)
    tecla = pygame.key.get_pressed()

    if tecla[pygame.K_d]:
        x+= velocidade

    if tecla[pygame.K_a]:
        x-= velocidade

    if tecla[pygame.K_s]:
        y += velocidade

    if tecla[pygame.K_w]:
        y -= velocidade
    tela.fill(AMARELO_CLARO)
    pygame.draw.circle(tela, VERMELHO, (x,y),25)
    parede = pygame.Rect(parede_x,parede_y, parede_altura, parede_largura)
    pygame.display.flip()
    tempo = time.tick(60) / 1000
pygame.quit()