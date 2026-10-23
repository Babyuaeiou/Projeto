import os
import random
import pygame
from cores import *


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
        cor=VerdePrimavera,
        colisao_tamanho=(40, 40),
    ):
        self.nome = nome
        self.x = float(x)
        self.y = float(y)

        self.dialogos = dialogos or [
            "Olá! Como vai?",
            "É bom encontrar alguém por aqui.",
        ]
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

    # -----------------------------------------------------
    # CARREGAR SPRITES
    # -----------------------------------------------------

    def carregar_sprites(self, sprite):
        if not sprite:
            return

        base = os.path.dirname(os.path.abspath(__file__))
        candidatos = [os.path.abspath(sprite), os.path.join(base, sprite), os.path.join(base, "sprite principal", os.path.basename(sprite))]
        caminho = next((c for c in candidatos if os.path.isfile(c)), None)
        if caminho is None:
            nome = os.path.basename(sprite).casefold()
            for pasta_raiz, _, arquivos in os.walk(base):
                achado = next((a for a in arquivos if a.casefold() == nome), None)
                if achado:
                    caminho = os.path.join(pasta_raiz, achado)
                    break
        if caminho is None:
            print(f"[NPC] Sprite não encontrado: {sprite}")
            return

        pasta = os.path.dirname(caminho)

        nomes_direcoes = {
            "F": "baixo",
            "T": "cima",
            "S": "esquerda",
            "D": "direita",
        }

        nome_arquivo = os.path.basename(caminho)
        prefixo = os.path.splitext(nome_arquivo)[0][:1].upper()

        if prefixo not in nomes_direcoes:
            print(
                "[NPC] Use um sprite direcional como "
                "F1.png, T1.png, S1.png ou D1.png."
            )
            return

        for letra, direcao in nomes_direcoes.items():
            for numero in range(1, 10):
                caminho_quadro = os.path.join(
                    pasta,
                    f"{letra}{numero}.png",
                )

                if not os.path.isfile(caminho_quadro):
                    alvo = f"{letra}{numero}.png".casefold()
                    encontrado = next((os.path.join(pasta, nome) for nome in os.listdir(pasta) if nome.casefold() == alvo), None)
                    if encontrado:
                        caminho_quadro = encontrado
                    else:
                        continue

                try:
                    imagem = pygame.image.load(caminho_quadro)

                    if pygame.display.get_surface():
                        imagem = imagem.convert_alpha()

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
                        f"[NPC] Não foi possível carregar "
                        f"{caminho_quadro}: {erro}"
                    )

        if not any(self.sprites.values()):
            print(f"[NPC] Nenhum sprite foi carregado para {self.nome}.")

    # -----------------------------------------------------
    # CAIXA DE COLISÃO
    # -----------------------------------------------------

    @property
    def colisao(self):
        return pygame.Rect(
            round(
                self.x
                + (self.largura_sprite - self.largura_colisao) / 2
            ),
            round(self.y + self.altura_sprite - self.altura_colisao),
            self.largura_colisao,
            self.altura_colisao,
        )

    def pode_ocupar(
        self,
        novo_x,
        novo_y,
        obstaculos=None,
        outros_npcs=None,
        outros_inimigos=None,
        limites_mundo=None,
    ):
        rect = pygame.Rect(
            round(
                novo_x
                + (self.largura_sprite - self.largura_colisao) / 2
            ),
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

        if outros_inimigos:
            for inimigo in outros_inimigos:
                colisao_inimigo = getattr(inimigo, "colisao", None)

                if colisao_inimigo is None:
                    colisao_inimigo = getattr(inimigo, "rect", None)

                if colisao_inimigo and rect.colliderect(colisao_inimigo):
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

    # -----------------------------------------------------
    # MOVIMENTAÇÃO ALEATÓRIA
    # -----------------------------------------------------

    def escolher_destino(self):
        distancia = random.uniform(
            max(10, self.distancia_maxima * 0.3),
            max(11, self.distancia_maxima),
        )

        angulo = random.uniform(0, 2 * 3.141592653589793)

        self.destino_x = self.x + pygame.math.Vector2(
            distancia, 0
        ).rotate_rad(angulo).x

        self.destino_y = self.y + pygame.math.Vector2(
            distancia, 0
        ).rotate_rad(angulo).y

        self.andando = True

    def atualizar(
        self,
        delta_ms,
        obstaculos=None,
        outros_npcs=None,
        limites_mundo=None,
        outros_inimigos=None,
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

        if abs(dx) > abs(dy):
            self.direcao = "direita" if dx > 0 else "esquerda"
        else:
            self.direcao = "baixo" if dy > 0 else "cima"

        passo = self.velocidade * (delta_ms / 1000)
        passo = min(passo, distancia)

        direcao_x = dx / distancia
        direcao_y = dy / distancia

        novo_x = self.x + direcao_x * passo
        novo_y = self.y + direcao_y * passo

        argumentos = (
            obstaculos,
            outros_npcs,
            outros_inimigos,
            limites_mundo,
        )

        if self.pode_ocupar(
            novo_x,
            novo_y,
            obstaculos=argumentos[0],
            outros_npcs=argumentos[1],
            outros_inimigos=argumentos[2],
            limites_mundo=argumentos[3],
        ):
            self.x = novo_x
            self.y = novo_y
        else:
            moveu = False

            if self.pode_ocupar(
                novo_x,
                self.y,
                obstaculos=obstaculos,
                outros_npcs=outros_npcs,
                outros_inimigos=outros_inimigos,
                limites_mundo=limites_mundo,
            ):
                self.x = novo_x
                moveu = True

            if self.pode_ocupar(
                self.x,
                novo_y,
                obstaculos=obstaculos,
                outros_npcs=outros_npcs,
                outros_inimigos=outros_inimigos,
                limites_mundo=limites_mundo,
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

    # -----------------------------------------------------
    # DESENHAR NPC
    # -----------------------------------------------------

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
                AmêndoaClara,
                (
                    pos_x + self.largura_sprite // 2,
                    pos_y + 12,
                ),
                12,
            )

        fonte = pygame.font.SysFont(None, 20)
        texto_nome = fonte.render(
            self.nome,
            True,
            Branco,
        )

        caixa_nome = texto_nome.get_rect(
            midbottom=(
                pos_x + self.largura_sprite // 2,
                pos_y - 3,
            )
        )
        caixa_nome.inflate_ip(8, 4)

        pygame.draw.rect(
            tela,
            Preto,
            caixa_nome,
            border_radius=4,
        )

        tela.blit(
            texto_nome,
            (caixa_nome.x + 4, caixa_nome.y + 2),
        )

        if jogador is not None and self.perto_do_jogador(jogador):
            self.desenhar_prompt(tela, pos_x, pos_y)

    def desenhar_prompt(self, tela, pos_x, pos_y):
        fonte = pygame.font.SysFont(None, 22)

        texto = fonte.render(
            "APERTE ESPAÇO PARA INTERAGIR",
            True,
            Branco,
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
            AzulMeiaNoite,
            caixa,
            border_radius=5,
        )

        pygame.draw.rect(
            tela,
            CinzaPrataClaro,
            caixa,
            width=1,
            border_radius=5,
        )

        tela.blit(texto, texto.get_rect(center=caixa.center))

    # -----------------------------------------------------
    # INTERAÇÃO COM O JOGADOR
    # -----------------------------------------------------

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
        self.andando = False
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

    # -----------------------------------------------------
    # CAIXA DE DIÁLOGO
    # -----------------------------------------------------

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
            AzulMeiaNoite,
            caixa,
            border_radius=8,
        )

        pygame.draw.rect(
            tela,
            BrancoAntigo,
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
            AmareloClaro,
        )
        tela.blit(nome, (caixa.x + 16, caixa.y + 12))

        if self.dialogos:
            indice = min(
                self.indice_dialogo,
                len(self.dialogos) - 1,
            )

            texto_dialogo = str(self.dialogos[indice])
            linhas = self.quebrar_texto(
                texto_dialogo,
                fonte_dialogo,
                caixa.width - 32,
            )

            y = caixa.y + 45

            for linha in linhas[:2]:
                imagem_linha = fonte_dialogo.render(
                    linha,
                    True,
                    Branco,
                )
                tela.blit(imagem_linha, (caixa.x + 16, y))
                y += 25

        dica = fonte_dica.render(
            "ESPAÇO: continuar    ESC: fechar",
            True,
            CinzaClaro,
        )

        tela.blit(
            dica,
            (
                caixa.right - dica.get_width() - 14,
                caixa.bottom - dica.get_height() - 10,
            ),
        )

    @staticmethod
    def quebrar_texto(texto, fonte, largura_maxima):
        palavras = str(texto).split()
        linhas = []
        linha_atual = ""

        for palavra in palavras:
            teste = palavra if not linha_atual else linha_atual + " " + palavra

            if fonte.size(teste)[0] <= largura_maxima:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)

                linha_atual = palavra

        if linha_atual:
            linhas.append(linha_atual)

        return linhas
