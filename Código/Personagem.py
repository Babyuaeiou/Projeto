from random import randint
import pygame


class Personagem:
    def __init__(self, nome, nome_sprite, quantidade_sprites):
        self.inventario = {}
        self.nome = nome
        self.cooldown = 1
        self.restante = 0
        self.hpmaximo, self.hp = 20, 20
        self.dano, self.danototal = 5, 5
        self.defesa, self.defesatotal = 3, 3
        self.velocidade = 1

        # Movimento
        self.x = 100
        self.y = 100
        self.velocidade_movimento = 5
        self.andando = False

        # Sprites
        self.nome_sprite = nome_sprite
        self.quantidade_sprites = quantidade_sprites

        # Sprite parado
        self.sprite_base = pygame.image.load(
            f"{self.nome_sprite}.png"
        ).convert_alpha()

        # Sprites andando
        self.sprites_andando = []

        for i in range(1, self.quantidade_sprites + 1):
            sprite = pygame.image.load(
                f"{self.nome_sprite}-{i}.png"
            ).convert_alpha()

            self.sprites_andando.append(sprite)

        self.sprite_atual = self.sprite_base

        # Animação
        self.frame_atual = 0
        self.tempo_animacao = 0
        self.velocidade_animacao = 100

    def esta_pronto(self, tempo):
        if self.restante > 0:
            self.restante -= tempo
            return False
        return True

    def reiniciar_cooldown(self):
        self.restante = self.cooldown

    def calcular_dano(self, alvo):
        dano_equipamento = 0

        ataquetotal = self.dano + dano_equipamento
        dano = ataquetotal * (
            ataquetotal / (ataquetotal + alvo.defesa)
        )

        return dano

    def movimentar(self, teclas):
        self.andando = False

        if teclas[pygame.K_w]:
            self.y -= self.velocidade_movimento
            self.andando = True

        if teclas[pygame.K_s]:
            self.y += self.velocidade_movimento
            self.andando = True

        if teclas[pygame.K_a]:
            self.x -= self.velocidade_movimento
            self.andando = True

        if teclas[pygame.K_d]:
            self.x += self.velocidade_movimento
            self.andando = True

    def atualizar_animacao(self, tempo):
        # Parado
        if not self.andando:
            self.frame_atual = 0
            self.tempo_animacao = 0
            self.sprite_atual = self.sprite_base
            return

        # Andando
        self.tempo_animacao += tempo

        if self.tempo_animacao >= self.velocidade_animacao:
            self.tempo_animacao = 0

            self.frame_atual += 1

            if self.frame_atual >= len(self.sprites_andando):
                self.frame_atual = 0

            self.sprite_atual = self.sprites_andando[
                self.frame_atual
            ]

    def atualizar(self, teclas, tempo):
        self.movimentar(teclas)
        self.atualizar_animacao(tempo)

    def desenhar(self, tela):
        tela.blit(
            self.sprite_atual,
            (self.x, self.y)
        )
