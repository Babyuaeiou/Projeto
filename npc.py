
import os
import random
import pygame


class NPC:
    def __init__(
        self,
        nome,
        x,
        y,
        dialogos=None,
        sprite=None,
        tamanho_sprite=(64, 64),
        tem_loja=False,
        velocidade=45,
        distancia_maxima=120,
        pode_andar=True,
        cor=(80, 180, 100),
        colisao_tamanho=(40, 40),
    ):
        self.nome = nome
        self.x = float(x)
        self.y = float(y)

        self.dialogos = dialogos or ["Olá!"]
        self.tem_loja = tem_loja

        self.velocidade = float(velocidade)
        self.distancia_maxima = float(distancia_maxima)
        self.pode_andar = pode_andar

        self.cor = cor
        self.largura_sprite, self.altura_sprite = tamanho_sprite
        self.largura_colisao, self.altura_colisao = colisao_tamanho

        self.sprite_base = sprite
        self.sprites = {
            "baixo": [],
            "cima": [],
            "esquerda": [],
            "direita": [],
        }

        self.direcao = "baixo"
        self.quadro = 0
        self.tempo_animacao = 0
        self.intervalo_animacao = 180

        self.dialogo_aberto = False
        self.indice_dialogo = 0

        self.tempo_movimento = 0
        self.tempo_espera = random.randint(800, 2200)
        self.andando = False
        self.destino_x = self.x
        self.destino_y = self.y

        self.carregar_sprites(sprite)

    # =====================================================
    # SPRITES
    # =====================================================

    def carregar_sprites(self, sprite):
        if not sprite:
            return

        caminho = os.path.abspath(sprite)

        if not os.path.isfile(caminho):
            print(
                f"[NPC] Sprite não encontrado: {caminho}. "
                "O NPC será desenhado automaticamente."
            )
            return

        pasta = os.path.dirname(caminho)
        nome_arquivo = os.path.basename(caminho)

        # Exemplo: F1.png -> prefixo F, quadro 1
        nome_sem_extensao = os.path.splitext(nome_arquivo)[0]
        prefixo = nome_sem_extensao[0].upper()

        prefixos = {
            "F": "baixo",
            "T": "cima",
            "S": "esquerda",
            "D": "direita",
        }

        if prefixo not in prefixos:
            print(
                f"[NPC] Nome de sprite inválido: {nome_arquivo}. "
                "Use F1.png, T1.png, S1.png ou D1.png."
            )
            return

        for letra, direcao in prefixos.items():
            for numero in range(1, 10):
                caminho_quadro = os.path.join(
                    pasta, f"{letra}{numero}.png"
                )

                # Aceita também extensões em maiúsculas.
                if not os.path.isfile(caminho_quadro):
                    caminho_alternativo = os.path.join(
                        pasta, f"{letra}{numero}.PNG"
                    )
                    if os.path.isfile(caminho_alternativo):
                        caminho_quadro = caminho_alternativo
                    else:
                        continue

                try:
                    imagem = pygame.image.load(
                        caminho_quadro
                    ).convert_alpha()

                    imagem = pygame.transform.scale(
                        imagem,
                        (
                            self.largura_sprite,
                            self.altura_sprite,
                        ),
                    )

                    self.sprites[direcao].append(imagem)

                except pygame.error as erro:
                    print(
                        f"[NPC] Erro ao carregar "
                        f"{caminho_quadro}: {erro}"
                    )

        if not any(self.sprites.values()):
            print("[NPC] Nenhum sprite direcional foi carregado.")

    # =====================================================
    # COLISÃO
    # =====================================================

    @property
    def colisao(self):
        return pygame.Rect(
            round(self.x + (self.largura_sprite - self.largura_colisao) / 2),
            round(self.y + self.altura_sprite - self.altura_colisao),
            self.largura_colisao,
            self.altura_colisao,
        )

    def pode_ocupar(self, novo_x, novo_y, obstaculos=None,
                    outros_npcs=None, limites_mundo=None):

        rect = pygame.Rect(
            round(novo_x + (self.largura_sprite - self.largura_colisao) / 2),
            round(novo_y + self.altura_sprite - self.altura_colisao),
            self.largura_colisao,
            self.altura_colisao,
        )

        if obstaculos:
            for obstaculo in obstaculos:
                if rect.colliderect(obstaculo):
                    return False

        if outros_npcs:
            for outro in outros_npcs:
                if outro is self:
                    continue

                if rect.colliderect(outro.colisao):
                    return False

        if limites_mundo:
            largura_mundo, altura_mundo = limites_mundo

            if (
                rect.left < 0
                or rect.top < 0
                or rect.right > largura_mundo
                or rect.bottom > altura_mundo
            ):
                return False

        return True

    # =====================================================
    # MOVIMENTAÇÃO
    # =====================================================

    def escolher_destino(self):
        distancia = random.uniform(
            self.distancia_maxima * 0.3,
            self.distancia_maxima,
        )

        angulo = random.uniform(0, 6.283185307)

        self.destino_x = self.x + (
            pygame.math.Vector2(1, 0).rotate_rad(angulo).x * distancia
        )
        self.destino_y = self.y + (
            pygame.math.Vector2(1, 0).rotate_rad(angulo).y * distancia
        )

        self.andando = True

    def atualizar(
        self,
        delta_ms,
        obstaculos=None,
        outros_npcs=None,
        limites_mundo=None,
    ):
        if not self.pode_andar or self.dialogo_aberto:
            self.andando = False
            return

        self.tempo_movimento += delta_ms

        if not self.andando:
            if self.tempo_movimento >= self.tempo_espera:
                self.tempo_movimento = 0
                self.escolher_destino()
            return

        dx = self.destino_x - self.x
        dy = self.destino_y - self.y
        distancia = (dx * dx + dy * dy) ** 0.5

        if distancia < 3:
            self.andando = False
            self.tempo_movimento = 0
            self.tempo_espera = random.randint(800, 2200)
            return

        direcao_x = dx / distancia
        direcao_y = dy / distancia

        if abs(dx) > abs(dy):
            self.direcao = "direita" if dx > 0 else "esquerda"
        else:
            self.direcao = "baixo" if dy > 0 else "cima"

        passo = self.velocidade * (delta_ms / 1000)
        passo = min(passo, distancia)

        novo_x = self.x + direcao_x * passo
        novo_y = self.y + direcao_y * passo

        # Tenta mover nos dois eixos.
        if self.pode_ocupar(
            novo_x,
            novo_y,
            obstaculos,
            outros_npcs,
            limites_mundo,
        ):
            self.x = novo_x
            self.y = novo_y
        else:
            # Se diagonal estiver bloqueada, tenta um eixo de cada vez.
            moveu = False

            if self.pode_ocupar(
                novo_x,
                self.y,
                obstaculos,
                outros_npcs,
                limites_mundo,
            ):
                self.x = novo_x
                moveu = True

            if self.pode_ocupar(
                self.x,
                novo_y,
                obstaculos,
                outros_npcs,
                limites_mundo,
            ):
                self.y = novo_y
                moveu = True

            if not moveu:
                self.andando = False
                self.tempo_movimento = 0
                self.tempo_espera = random.randint(800, 1800)

        if self.andando:
            self.tempo_animacao += delta_ms

            if self.tempo_animacao >= self.intervalo_animacao:
                self.tempo_animacao = 0

                frames = self.sprites.get(self.direcao, [])
                if frames:
                    self.quadro = (self.quadro + 1) % len(frames)

    # =====================================================
    # DESENHO
    # =====================================================

    def desenhar(self, tela, camera_x=0, camera_y=0, jogador=None):
        pos_x = round(self.x - camera_x)
        pos_y = round(self.y - camera_y)

        frames = self.sprites.get(self.direcao, [])

        if frames:
            if self.andando:
                imagem = frames[self.quadro % len(frames)]
            else:
                imagem = frames[0]

            tela.blit(imagem, (pos_x, pos_y))

        else:
            # Desenho simples caso não tenha sprites.
            pygame.draw.rect(
                tela,
                self.cor,
                (
                    pos_x + 12,
                    pos_y + 12,
                    self.largura_sprite - 24,
                    self.altura_sprite - 12,
                ),
                border_radius=6,
            )

            pygame.draw.circle(
                tela,
                (240, 200, 160),
                (
                    pos_x + self.largura_sprite // 2,
                    pos_y + 12,
                ),
                12,
            )

        fonte = pygame.font.SysFont(None, 20)
        texto_nome = fonte.render(self.nome, True, (255, 255, 255))
        fundo_nome = texto_nome.get_rect(
            midbottom=(pos_x + self.largura_sprite // 2, pos_y - 3)
        )
        fundo_nome.inflate_ip(8, 4)

        pygame.draw.rect(
            tela,
            (30, 30, 30),
            fundo_nome,
            border_radius=4,
        )

        tela.blit(
            texto_nome,
            (
                fundo_nome.x + 4,
                fundo_nome.y + 2,
            ),
        )

        if jogador is not None:
            if self.perto_do_jogador(jogador):
                self.desenhar_prompt(
                    tela,
                    pos_x,
                    pos_y,
                )

    def desenhar_prompt(self, tela, pos_x, pos_y):
        fonte = pygame.font.SysFont(None, 22)
        texto = fonte.render(
            "APERTE ESPAÇO PARA INTERAGIR",
            True,
            (255, 255, 255),
        )

        caixa = texto.get_rect(
            midbottom=(
                pos_x + self.largura_sprite // 2,
                pos_y - 12,
            )
        )
        caixa.inflate_ip(14, 10)

        pygame.draw.rect(
            tela,
            (25, 25, 35),
            caixa,
            border_radius=5,
        )
        pygame.draw.rect(
            tela,
            (230, 230, 230),
            caixa,
            width=1,
            border_radius=5,
        )

        tela.blit(
            texto,
            (
                caixa.centerx - texto.get_width() // 2,
                caixa.centery - texto.get_height() // 2,
            ),
        )

    # =====================================================
    # INTERAÇÃO
    # =====================================================

    def perto_do_jogador(self, jogador, distancia_maxima=70):
        jogador_rect = getattr(jogador, "colisao", None)

        if jogador_rect is None:
            jogador_rect = pygame.Rect(
                int(getattr(jogador, "x", 0)),
                int(getattr(jogador, "y", 0)),
                50,
                50,
            )

        centro_npc = pygame.Vector2(self.colisao.center)
        centro_jogador = pygame.Vector2(jogador_rect.center)

        return centro_npc.distance_to(centro_jogador) <= distancia_maxima

    def interagir(self, jogador):
        if not self.perto_do_jogador(jogador):
            return False

        self.dialogo_aberto = True
        self.indice_dialogo = 0
        return True

    def processar_evento(self, evento):
        if not self.dialogo_aberto:
            return False

        if evento.type == pygame.KEYDOWN:
            if evento.key in (
                pygame.K_SPACE,
                pygame.K_RETURN,
                pygame.K_z,
            ):
                self.indice_dialogo += 1

                if self.indice_dialogo >= len(self.dialogos):
                    self.dialogo_aberto = False
                    self.indice_dialogo = 0

                return True

            if evento.key == pygame.K_ESCAPE:
                self.dialogo_aberto = False
                self.indice_dialogo = 0
                return True

        return False

    def desenhar_dialogo(self, tela):
        if not self.dialogo_aberto:
            return

        largura_tela, altura_tela = tela.get_size()

        caixa = pygame.Rect(
            30,
            altura_tela - 145,
            largura_tela - 60,
            115,
        )

        pygame.draw.rect(
            tela,
            (20, 20, 30),
            caixa,
            border_radius=8,
        )
        pygame.draw.rect(
            tela,
            (240, 240, 240),
            caixa,
            width=2,
            border_radius=8,
        )

        fonte_nome = pygame.font.SysFont(None, 26, bold=True)
        fonte_dialogo = pygame.font.SysFont(None, 24)
        fonte_dica = pygame.font.SysFont(None, 18)

        nome = fonte_nome.render(
            self.nome,
            True,
            (255, 220, 100),
        )
        tela.blit(nome, (caixa.x + 16, caixa.y + 12))

        if self.dialogos:
            indice = min(
                self.indice_dialogo,
                len(self.dialogos) - 1,
            )
            linha = fonte_dialogo.render(
                str(self.dialogos[indice]),
                True,
                (255, 255, 255),
            )
            tela.blit(linha, (caixa.x + 16, caixa.y + 45))

        dica = fonte_dica.render(
            "ESPAÇO: continuar    ESC: fechar",
            True,
            (190, 190, 190),
        )
        tela.blit(
            dica,
            (
                caixa.right - dica.get_width() - 14,
                caixa.bottom - dica.get_height() - 10,
            ),
        )
