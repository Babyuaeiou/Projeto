import pygame


class Personagem:
    def __init__(
        self,
        nome,
        nome_sprite,
        quantidade_sprites,
        sprites_andando=None
    ):
        self.inventario = {}
        self.nome = nome

        # Combate
        self.cooldown = 1
        self.restante = 0

        self.hpmaximo = 20
        self.hp = 20

        self.dano = 5
        self.danototal = 5

        self.defesa = 3
        self.defesatotal = 3

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

        # Configuração dos sprites
        self.nome_sprite = nome_sprite
        self.quantidade_sprites = quantidade_sprites

        # Sprites parados para cada direção
        self.sprites_parados = {
            "direita": pygame.image.load(
                "D1.PNG"
            ).convert_alpha(),

            "esquerda": pygame.image.load(
                "S1.PNG"
            ).convert_alpha(),

            "cima": pygame.image.load(
                "T1.PNG"
            ).convert_alpha(),

            "baixo": pygame.image.load(
                "F1.PNG"
            ).convert_alpha()
        }

        # Sprites de caminhada na ordem original
        nomes_sprites = {
            "direita": ["D1.PNG", "D2.PNG", "D3.PNG", "D1.PNG"],
            "esquerda": ["S1.PNG", "S2.PNG", "S3.PNG", "S1.PNG"],
            "cima": ["T1.PNG", "T2.PNG", "T3.PNG", "T1.PNG"],
            "baixo": ["F1.PNG", "F2.PNG", "F3.PNG", "F1.PNG"]
        }

        self.sprites_andando = {
            "direita": [],
            "esquerda": [],
            "cima": [],
            "baixo": []
        }

        # Carrega os sprites na ordem definida acima
        for direcao, arquivos in nomes_sprites.items():
            for arquivo in arquivos[:quantidade_sprites]:
                sprite = pygame.image.load(
                    arquivo
                ).convert_alpha()

                self.sprites_andando[direcao].append(sprite)

        # Estado da animação
        self.direcao = "baixo"
        self.sprite_atual = self.sprites_parados[self.direcao]

        self.frame_atual = 0
        self.tempo_animacao = 0
        self.velocidade_animacao = 100

    # =====================================================
    # COOLDOWN
    # =====================================================

    def esta_pronto(self, tempo):
        if self.restante > 0:
            self.restante -= tempo
            return False

        return True

    def reiniciar_cooldown(self):
        self.restante = self.cooldown

    # =====================================================
    # COMBATE
    # =====================================================

    def calcular_dano(self, alvo):
        dano_equipamento = 0

        ataque_total = self.dano + dano_equipamento

        dano = ataque_total * (
            ataque_total / (ataque_total + alvo.defesa)
        )

        return dano

    # =====================================================
    # MOVIMENTO ORIGINAL
    # Permite coordenadas negativas
    # =====================================================

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
            self.direcao = "esquerda"

        elif teclas[pygame.K_d]:
            movimento_x = self.velocidade_movimento
            self.direcao = "direita"

        if movimento_x != 0:
            nova_x = self.x + movimento_x

            self.colisao.x = nova_x

            # Verifica apenas as colisões com objetos
            if self.colisao.collidelist(objetos_colisao) == -1:
                self.x = nova_x
            else:
                self.colisao.x = self.x

            self.andando = True

        # Movimento vertical
        movimento_y = 0

        if teclas[pygame.K_w]:
            movimento_y = -self.velocidade_movimento
            self.direcao = "cima"

        elif teclas[pygame.K_s]:
            movimento_y = self.velocidade_movimento
            self.direcao = "baixo"

        if movimento_y != 0:
            nova_y = self.y + movimento_y

            self.colisao.y = nova_y

            # Verifica apenas as colisões com objetos
            if self.colisao.collidelist(objetos_colisao) == -1:
                self.y = nova_y
            else:
                self.colisao.y = self.y

            self.andando = True

        # Sincroniza a caixa de colisão
        self.colisao.topleft = (self.x, self.y)

    # =====================================================
    # ANIMAÇÃO
    # =====================================================

    def atualizar_animacao(self, tempo):
        # Sprite parado correspondente à última direção
        if not self.andando:
            self.frame_atual = 0
            self.tempo_animacao = 0
            self.sprite_atual = self.sprites_parados[self.direcao]
            return

        # Seleciona os sprites da direção atual
        sprites = self.sprites_andando[self.direcao]

        if not sprites:
            self.sprite_atual = self.sprites_parados[self.direcao]
            return

        # Atualiza a animação
        self.tempo_animacao += tempo

        if self.tempo_animacao >= self.velocidade_animacao:
            self.tempo_animacao -= self.velocidade_animacao

            self.frame_atual += 1

            if self.frame_atual >= len(sprites):
                self.frame_atual = 0

        self.sprite_atual = sprites[self.frame_atual]

    # =====================================================
    # ATUALIZAÇÃO DO PERSONAGEM
    # =====================================================

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

    # =====================================================
    # DESENHO
    # =====================================================

    def desenhar(self, tela, camera_x, camera_y):
        tela.blit(
            self.sprite_atual,
            (
                self.x - camera_x,
                self.y - camera_y
            )
        )
