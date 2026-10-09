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

        # Caixa de colisão
        self.colisao = pygame.Rect(
            self.x,
            self.y,
            50,
            50
        )

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

    def movimentar(
        self,
        teclas,
        objetos_colisao,
        mapa_largura,
        mapa_altura
    ):
        self.andando = False

        # Movimento horizontal
        movimento_x = 0

        if teclas[pygame.K_a]:
            movimento_x = -self.velocidade_movimento
        elif teclas[pygame.K_d]:
            movimento_x = self.velocidade_movimento

        if movimento_x != 0:
            nova_x = self.x + movimento_x

            self.colisao.x = nova_x

            # Verifica colisões sem limitar a coordenada a zero
            if self.colisao.collidelist(objetos_colisao) == -1:
                self.x = nova_x
            else:
                self.colisao.x = self.x

            self.andando = True

        # Movimento vertical
        movimento_y = 0

        if teclas[pygame.K_w]:
            movimento_y = -self.velocidade_movimento
        elif teclas[pygame.K_s]:
            movimento_y = self.velocidade_movimento

        if movimento_y != 0:
            nova_y = self.y + movimento_y

            self.colisao.y = nova_y

            # Verifica colisões sem limitar a coordenada a zero
            if self.colisao.collidelist(objetos_colisao) == -1:
                self.y = nova_y
            else:
                self.colisao.y = self.y

            self.andando = True

        # Mantém a caixa de colisão sincronizada
        self.colisao.topleft = (self.x, self.y)

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

    def atualizar(
        self,
        teclas,
        tempo,
        objetos_colisao,
        mapa_largura,
        mapa_altura
    ):
        self.movimentar(
            teclas,
            objetos_colisao,
            mapa_largura,
            mapa_altura
        )

        self.atualizar_animacao(tempo)

    def desenhar(self, tela, camera_x, camera_y):
        tela.blit(
            self.sprite_atual,
            (
                self.x - camera_x,
                self.y - camera_y
            )
        )
