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
#colisão/jogador
parede_x = 300
parede_y = 200
parede_largura = 100
parede_altura = 50

jogador =pygame.Rect(x - 25,y - 25,50,50)
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
    parede = pygame.Rect(parede_x,parede_y, parede_largura, parede_altura)
    pygame.draw.rect(tela,PRETO,parede)
    if jogador.colliderect(parede):
        print('COLIDIU')
    pygame.display.flip()
    tempo = time.tick(60) / 1000
pygame.quit()