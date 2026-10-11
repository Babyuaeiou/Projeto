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

        # Controle dos toques nas teclas
        self.teclas_movimento_anterior = set()

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
    # Primeiro passo -> parado -> segundo passo -> parado
    # =====================================================

    def atualizar_animacao(self, tempo):
        teclas = pygame.key.get_pressed()

        teclas_movimento = {
            pygame.K_a: "esquerda",
            pygame.K_d: "direita",
            pygame.K_w: "cima",
            pygame.K_s: "baixo"
        }

        teclas_atuais = {
            tecla
            for tecla in teclas_movimento
            if teclas[tecla]
        }

        # Detecta um novo toque
        novas_teclas = (
            teclas_atuais - self.teclas_movimento_anterior
        )

        if novas_teclas:
            tecla = next(iter(novas_teclas))
            self.direcao = teclas_movimento[tecla]

            # Avança para o próximo estado
            self.frame_atual = (self.frame_atual + 1) % 4
            self.tempo_animacao = 0

        self.teclas_movimento_anterior = teclas_atuais

        # Enquanto anda, alterna entre:
        # primeiro passo -> parado -> segundo passo -> parado
        if self.andando:
            self.tempo_animacao += tempo

            if self.tempo_animacao >= self.velocidade_animacao:
                self.tempo_animacao -= self.velocidade_animacao
                self.frame_atual = (self.frame_atual + 1) % 4

            if self.frame_atual == 1:
                indice_sprite = 1

            elif self.frame_atual == 3:
                indice_sprite = 2

            else:
                self.sprite_atual = (
                    self.sprites_parados[self.direcao]
                )
                return

            sprites = self.sprites_andando[self.direcao]

            if len(sprites) > indice_sprite:
                self.sprite_atual = sprites[indice_sprite]
            else:
                self.sprite_atual = (
                    self.sprites_parados[self.direcao]
                )

        elif novas_teclas:
            # Mostra o estado correspondente ao toque
            if self.frame_atual == 1:
                self.sprite_atual = (
                    self.sprites_andando[self.direcao][1]
                )

            elif self.frame_atual == 3:
                self.sprite_atual = (
                    self.sprites_andando[self.direcao][2]
                )

            else:
                self.sprite_atual = (
                    self.sprites_parados[self.direcao]
                )

        else:
            # Sprite parado correspondente à última direção
            self.frame_atual = 0
            self.tempo_animacao = 0
            self.sprite_atual = (
                self.sprites_parados[self.direcao]
            )

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
