
import pygame
import random
import math
import re

from cores import *


# =========================================================
# PERSONAGEM
# =========================================================

class Personagem:
    def __init__(
        self,
        nome,
        nome_sprite,
        quantidade_sprites,
        sprites_andando=None
    ):
        self.nome = nome

        # Atributos de combate
        self.hpmaximo = 20
        self.hp = 20

        self.dano_base = 5
        self.defesa_base = 3

        self.dano = self.dano_base
        self.defesa = self.defesa_base
        self.danototal = self.dano_base
        self.defesatotal = self.defesa_base

        self.velocidade = 1
        self.cooldown = 1.0
        self.restante = 0.0
        self.buff_proximo_ataque = 0

        # Progressão
        self.nivel = 1
        self.xp = 0
        self.xp_proximo = 30
        self.moedas = 30

        # Inventário
        self.inventario = {}

        # Equipamentos
        self.equipamentos = {
            "arma": None,
            "armadura": None
        }

        # Movimento
        self.x = 100
        self.y = 100
        self.velocidade_movimento = 5
        self.andando = False

        self.colisao = pygame.Rect(self.x, self.y, 50, 50)

        # Sprites direcionais do jogador
        self.nome_sprite = nome_sprite
        self.quantidade_sprites = quantidade_sprites

        nomes_sprites = {
            "direita": ["D1.PNG", "D2.PNG", "D3.PNG", "D1.PNG"],
            "esquerda": ["S1.PNG", "S2.PNG", "S3.PNG", "S1.PNG"],
            "cima": ["T1.PNG", "T2.PNG", "T3.PNG", "T1.PNG"],
            "baixo": ["F1.PNG", "F2.PNG", "F3.PNG", "F1.PNG"]
        }

        if isinstance(sprites_andando, dict):
            for direcao in nomes_sprites:
                if direcao in sprites_andando:
                    nomes_sprites[direcao] = sprites_andando[direcao]

        self.sprites_parados = {}
        self.sprites_andando = {
            "direita": [],
            "esquerda": [],
            "cima": [],
            "baixo": []
        }

        for direcao, arquivos in nomes_sprites.items():
            arquivos = list(arquivos)

            if not arquivos:
                raise ValueError(
                    f"Nenhum sprite configurado para {direcao}."
                )

            imagens = []

            for arquivo in arquivos[:max(1, quantidade_sprites)]:
                imagem = pygame.image.load(arquivo).convert_alpha()
                imagens.append(imagem)

            self.sprites_parados[direcao] = imagens[0]
            self.sprites_andando[direcao] = imagens

        self.direcao = "baixo"
        self.sprite_atual = self.sprites_parados[self.direcao]

        self.frame_atual = 0
        self.tempo_animacao = 0
        self.velocidade_animacao = 100
        self.teclas_movimento_anterior = set()

        self.recalcular_atributos()

    # =====================================================
    # ITENS E INVENTÁRIO
    # =====================================================

    def adicionar_item(self, item_id, quantidade=1):
        if not isinstance(quantidade, int) or quantidade <= 0:
            return False

        if not isinstance(item_id, str) or not item_id:
            return False

        self.inventario[item_id] = (
            self.inventario.get(item_id, 0) + quantidade
        )
        return True

    def remover_item(self, item_id, quantidade=1):
        if not isinstance(quantidade, int) or quantidade <= 0:
            return False

        quantidade_atual = self.inventario.get(item_id, 0)

        if quantidade_atual < quantidade:
            return False

        restante = quantidade_atual - quantidade

        if restante > 0:
            self.inventario[item_id] = restante
        else:
            self.inventario.pop(item_id, None)

        return True

    def quantidade_item(self, item_id):
        return self.inventario.get(item_id, 0)

    # =====================================================
    # ARMAS E ARMADURAS
    # =====================================================

    def equipar(self, item_id):
        from item import catalogo

        item = catalogo.obter(item_id)

        if item is None:
            return False

        categoria = str(getattr(item, "categoria", "")).lower()

        if categoria in ("arma", "armas", "weapon"):
            slot = "arma"
        elif categoria in ("armadura", "armaduras", "armor"):
            slot = "armadura"
        else:
            return False

        if self.inventario.get(item_id, 0) <= 0:
            return False

        equipamento_anterior = self.equipamentos.get(slot)

        if not self.remover_item(item_id, 1):
            return False

        if equipamento_anterior:
            self.adicionar_item(equipamento_anterior, 1)

        self.equipamentos[slot] = item_id
        self.recalcular_atributos()
        return True

    def equipar_arma(self, item_id):
        from item import catalogo

        item = catalogo.obter(item_id)

        if item is None:
            return False

        categoria = str(getattr(item, "categoria", "")).lower()

        if categoria not in ("arma", "armas", "weapon"):
            return False

        return self.equipar(item_id)

    def equipar_armadura(self, item_id):
        from item import catalogo

        item = catalogo.obter(item_id)

        if item is None:
            return False

        categoria = str(getattr(item, "categoria", "")).lower()

        if categoria not in ("armadura", "armaduras", "armor"):
            return False

        return self.equipar(item_id)

    def desequipar(self, slot):
        if slot not in self.equipamentos:
            return False

        item_id = self.equipamentos.get(slot)

        if not item_id:
            return False

        self.adicionar_item(item_id, 1)
        self.equipamentos[slot] = None
        self.recalcular_atributos()
        return True

    def recalcular_atributos(self):
        from item import catalogo

        self.dano = getattr(self, "dano_base", 5)
        self.defesa = getattr(self, "defesa_base", 3)

        for slot, atributo in (
            ("arma", "dano"),
            ("armadura", "defesa")
        ):
            item_id = self.equipamentos.get(slot)

            if not item_id:
                continue

            item = catalogo.obter(item_id)

            if item is None:
                continue

            bonus = getattr(item, "atributos", {}) or {}
            valor = bonus.get(atributo, 0)

            if isinstance(valor, (int, float)):
                if atributo == "dano":
                    self.dano += valor
                else:
                    self.defesa += valor

        self.danototal = max(0, int(self.dano))
        self.defesatotal = max(0, int(self.defesa))

    # =====================================================
    # EXPERIÊNCIA E NÍVEIS
    # =====================================================

    def ganhar_xp(self, quantidade):
        if quantidade <= 0:
            return

        self.xp += int(quantidade)

        while self.xp >= self.xp_proximo:
            self.xp -= self.xp_proximo
            self.nivel += 1
            self.xp_proximo = int(self.xp_proximo * 1.5)

            self.hpmaximo += 5
            self.dano_base += 1
            self.defesa_base += 1

            self.hp = self.hpmaximo
            self.recalcular_atributos()

    # =====================================================
    # COOLDOWN E CÁLCULO DE DANO
    # =====================================================

    def esta_pronto(self, tempo):
        if self.restante > 0:
            self.restante = max(0, self.restante - tempo)
            return False

        return True

    def reiniciar_cooldown(self):
        self.restante = self.cooldown

    def calcular_dano(self, alvo):
        ataque = max(0, getattr(self, "danototal", self.dano))

        defesa_alvo = max(
            0,
            getattr(
                alvo,
                "defesatotal",
                getattr(alvo, "defesa", 0)
            )
        )

        if ataque <= 0:
            return 0

        dano = ataque * ataque / (ataque + defesa_alvo)
        dano = int(dano * random.uniform(0.9, 1.1))

        if self.buff_proximo_ataque > 0:
            dano += self.buff_proximo_ataque
            self.buff_proximo_ataque = 0

        return max(1, dano)

    # =====================================================
    # MOVIMENTO E COLISÕES
    # =====================================================

    def movimentar(
        self,
        teclas,
        objetos_colisao,
        mapa_largura,
        mapa_altura
    ):
        self.andando = False

        movimento_x = 0
        movimento_y = 0

        # Movimento horizontal: somente A e D.
        if teclas[pygame.K_a]:
            movimento_x = -self.velocidade_movimento
            self.direcao = "esquerda"
        elif teclas[pygame.K_d]:
            movimento_x = self.velocidade_movimento
            self.direcao = "direita"

        # Movimento vertical: somente W e S.
        if teclas[pygame.K_w]:
            movimento_y = -self.velocidade_movimento
            self.direcao = "cima"
        elif teclas[pygame.K_s]:
            movimento_y = self.velocidade_movimento
            self.direcao = "baixo"

        # Movimento horizontal e colisões.
        if movimento_x:
            nova_x = self.x + movimento_x
            self.colisao.x = round(nova_x)

            dentro_mapa = (
                self.colisao.left >= 0
                and self.colisao.right <= mapa_largura
            )

            colidiu = (
                self.colisao.collidelist(objetos_colisao) != -1
            )

            if dentro_mapa and not colidiu:
                self.x = nova_x

            self.colisao.x = round(self.x)

        # Movimento vertical e colisões.
        if movimento_y:
            nova_y = self.y + movimento_y
            self.colisao.y = round(nova_y)

            dentro_mapa = (
                self.colisao.top >= 0
                and self.colisao.bottom <= mapa_altura
            )

            colidiu = (
                self.colisao.collidelist(objetos_colisao) != -1
            )

            if dentro_mapa and not colidiu:
                self.y = nova_y

            self.colisao.y = round(self.y)

        self.colisao.topleft = (
            round(self.x),
            round(self.y)
        )

        self.andando = bool(movimento_x or movimento_y)

    # =====================================================
    # ANIMAÇÃO DOS SPRITES
    # =====================================================

    def atualizar_animacao(self, tempo):
        teclas = pygame.key.get_pressed()

        # As setinhas não controlam a direção do personagem.
        teclas_movimento = {
            pygame.K_a: "esquerda",
            pygame.K_d: "direita",
            pygame.K_w: "cima",
            pygame.K_s: "baixo"
        }

        teclas_atuais = {
            tecla for tecla in teclas_movimento
            if teclas[tecla]
        }

        novas_teclas = (
            teclas_atuais - self.teclas_movimento_anterior
        )

        if novas_teclas:
            tecla = next(iter(novas_teclas))
            self.direcao = teclas_movimento[tecla]

        self.teclas_movimento_anterior = teclas_atuais

        if self.andando:
            self.tempo_animacao += tempo * 1000

            if self.tempo_animacao >= self.velocidade_animacao:
                self.tempo_animacao -= self.velocidade_animacao
                sprites = self.sprites_andando[self.direcao]

                if sprites:
                    self.frame_atual = (
                        self.frame_atual + 1
                    ) % len(sprites)

                    self.sprite_atual = sprites[self.frame_atual]

        else:
            self.frame_atual = 0
            self.tempo_animacao = 0
            self.sprite_atual = self.sprites_parados[self.direcao]

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
                round(self.x - camera_x),
                round(self.y - camera_y)
            )
        )


# =========================================================
# INIMIGOS VISÍVEIS NO MAPA
# =========================================================

class Inimigo:
    """Inimigo visível no mapa, com sprite animado e movimento por patrulha."""

    def __init__(
        self,
        nome="Goblin",
        hpmaximo=15,
        dano=4,
        defesa=1,
        x=0,
        y=0,
        xp_recompensa=10,
        moedas_recompensa=5,
        chefe=False,
        cor=VermelhoTijolo,
        sprite="d1.png",
        tamanho_sprite=(64, 64),
        velocidade_movimento=45,
        distancia_maxima=140,
        pode_andar=True,
        colisao_tamanho=(38, 38),
    ):
        self.nome = nome
        self.hpmaximo = hpmaximo
        self.hp = hpmaximo
        self.dano = dano
        self.defesa = defesa

        self.x = float(x)
        self.y = float(y)

        self.largura_sprite, self.altura_sprite = tamanho_sprite
        self.largura_colisao, self.altura_colisao = colisao_tamanho

        self.colisao = pygame.Rect(
            round(self.x + (self.largura_sprite - self.largura_colisao) / 2),
            round(self.y + self.altura_sprite - self.altura_colisao),
            self.largura_colisao,
            self.altura_colisao,
        )

        self.xp_recompensa = xp_recompensa
        self.moedas_recompensa = moedas_recompensa
        self.chefe = chefe
        self.cor = cor
        self.derrotado = False

        self.velocidade_movimento = float(velocidade_movimento)
        self.distancia_maxima = float(distancia_maxima)
        self.pode_andar = pode_andar
        self.andando = False
        self.direcao = "baixo"
        self.quadro = 0
        self.tempo_animacao = 0.0
        self.intervalo_animacao = 160
        self.tempo_parado = 0.0
        self.tempo_espera = random.randint(700, 1700)
        self.destino_x = self.x
        self.destino_y = self.y

        self.sprites = {
            "direita": [],
            "esquerda": [],
            "cima": [],
            "baixo": [],
        }

        self.sprite_atual = None
        self._espelhar = False

        self.carregar_sprites(sprite)

    @property
    def colisao(self):
        return self._colisao

    @colisao.setter
    def colisao(self, retangulo):
        self._colisao = retangulo

    def carregar_sprites(self, sprite):
        """Carrega os sprites direcionais do inimigo."""
        import os

        if not sprite:
            return

        caminho = os.path.abspath(sprite)

        if not os.path.isfile(caminho) and not os.path.isabs(sprite):
            caminho = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                sprite,
            )

        pasta = os.path.dirname(caminho) or os.getcwd()
        extensao_base = os.path.splitext(caminho)[1]

        extensoes = [
            extensao_base,
            ".png",
            ".PNG",
            ".jpg",
            ".JPG",
            ".jpeg",
            ".JPEG"
        ]

        nomes_direcao = {
            "direita": ["gd", "GD"],
            "esquerda": ["ge", "GE"],
            "cima": ["gt", "GT"],
            "baixo": ["gf", "GF"]
        }

        def tentar_carregar(caminho_imagem):
            if not os.path.isfile(caminho_imagem):
                return None

            try:
                imagem = pygame.image.load(caminho_imagem).convert_alpha()

                imagem = pygame.transform.scale(
                    imagem,
                    (self.largura_sprite, self.altura_sprite)
                )

                return imagem

            except (pygame.error, OSError):
                return None

        sprites_carregados = {}

        for direcao, prefixos in nomes_direcao.items():
            quadros = []

            for prefixo in prefixos:
                for numero in range(1, 4):
                    encontrados = []

                    for extensao in extensoes:
                        nome_arquivo = f"{prefixo}{numero}{extensao}"
                        caminho_imagem = os.path.join(pasta, nome_arquivo)

                        if os.path.isfile(caminho_imagem):
                            encontrados.append(caminho_imagem)

                    if encontrados:
                        imagem = tentar_carregar(encontrados[0])

                        if imagem is not None:
                            quadros.append(imagem)

                if quadros:
                    break

            sprites_carregados[direcao] = quadros

        if not any(sprites_carregados.values()):
            imagem = tentar_carregar(caminho)

            if imagem is not None:
                sprites_carregados["baixo"] = [imagem]

        primeiro_grupo = next(
            (
                quadros
                for quadros in sprites_carregados.values()
                if quadros
            ),
            []
        )

        for direcao in self.sprites:
            quadros = sprites_carregados.get(direcao, [])

            if not quadros:
                quadros = list(primeiro_grupo)

            self.sprites[direcao] = quadros

        if self.sprites[self.direcao]:
            self.sprite_atual = self.sprites[self.direcao][0]

    def atualizar_colisao(self):
        self.colisao.topleft = (
            round(
                self.x
                + (self.largura_sprite - self.largura_colisao) / 2
            ),
            round(
                self.y
                + self.altura_sprite
                - self.altura_colisao
            ),
        )

    def pode_ocupar(
        self,
        novo_x,
        novo_y,
        obstaculos,
        outros_inimigos,
        limites_mundo
    ):
        retangulo = pygame.Rect(
            round(
                novo_x
                + (self.largura_sprite - self.largura_colisao) / 2
            ),
            round(
                novo_y
                + self.altura_sprite
                - self.altura_colisao
            ),
            self.largura_colisao,
            self.altura_colisao,
        )

        largura_mundo, altura_mundo = limites_mundo

        if (
            retangulo.left < 0
            or retangulo.top < 0
            or retangulo.right > largura_mundo
            or retangulo.bottom > altura_mundo
        ):
            return False

        for obstaculo in obstaculos:
            if retangulo.colliderect(obstaculo):
                return False

        for outro in outros_inimigos:
            if outro is self or outro.derrotado:
                continue

            if retangulo.colliderect(outro.colisao):
                return False

        return True

    # =====================================================
    # MÉTODO CORRIGIDO: MOVIMENTO DOS INIMIGOS
    # =====================================================

    def atualizar(
        self,
        delta_ms,
        obstaculos=None,
        outros_inimigos=None,
        limites_mundo=(30000, 20000),
        jogador=None
    ):
        if self.derrotado or not self.pode_andar:
            self.andando = False
            return

        obstaculos = list(obstaculos or [])
        outros_inimigos = list(outros_inimigos or [])

        # Espera antes de escolher uma direção.
        if not self.andando:
            self.tempo_parado += delta_ms

            if self.tempo_parado < self.tempo_espera:
                return

            self.tempo_parado = 0
            self.tempo_espera = random.randint(500, 1300)

            self.direcao = random.choice([
                "direita",
                "esquerda",
                "cima",
                "baixo"
            ])

            distancia = random.uniform(
                max(10, self.distancia_maxima * 0.3),
                max(11, self.distancia_maxima)
            )

            self.destino_x = self.x
            self.destino_y = self.y

            if self.direcao == "direita":
                self.destino_x += distancia
            elif self.direcao == "esquerda":
                self.destino_x -= distancia
            elif self.direcao == "baixo":
                self.destino_y += distancia
            else:
                self.destino_y -= distancia

            self.andando = True
            self.quadro = 0
            self.tempo_animacao = 0

        # Calcula a distância restante na direção escolhida.
        if self.direcao == "direita":
            distancia_restante = self.destino_x - self.x
        elif self.direcao == "esquerda":
            distancia_restante = self.x - self.destino_x
        elif self.direcao == "baixo":
            distancia_restante = self.destino_y - self.y
        else:
            distancia_restante = self.y - self.destino_y

        # Terminou o deslocamento.
        if distancia_restante <= 1:
            self.andando = False
            self.tempo_parado = 0
            self.tempo_espera = random.randint(500, 1300)
            self.quadro = 0
            self.atualizar_colisao()
            return

        # Move em apenas uma direção por vez.
        passo = min(
            self.velocidade_movimento * max(0, delta_ms) / 1000,
            distancia_restante
        )

        novo_x = self.x
        novo_y = self.y

        if self.direcao == "direita":
            novo_x += passo
        elif self.direcao == "esquerda":
            novo_x -= passo
        elif self.direcao == "baixo":
            novo_y += passo
        elif self.direcao == "cima":
            novo_y -= passo

        # Impede atravessar paredes, NPCs e outros inimigos.
        if self.pode_ocupar(
            novo_x,
            novo_y,
            obstaculos,
            outros_inimigos,
            limites_mundo
        ):
            self.x = novo_x
            self.y = novo_y
        else:
            self.andando = False
            self.tempo_parado = 0
            self.tempo_espera = random.randint(300, 700)

        self.atualizar_colisao()

        # Anima os quadros do sprite enquanto anda.
        if self.andando:
            self.tempo_animacao += max(0, delta_ms)

            if self.tempo_animacao >= self.intervalo_animacao:
                self.tempo_animacao %= self.intervalo_animacao

                quadros = self.sprites.get(self.direcao, [])

                if quadros:
                    self.quadro = (
                        self.quadro + 1
                    ) % len(quadros)

                    self.sprite_atual = quadros[self.quadro]
        else:
            self.quadro = 0
            self.tempo_animacao = 0

            quadros = self.sprites.get(self.direcao, [])

            if quadros:
                self.sprite_atual = quadros[0]

    def desenhar(self, tela, camera_x, camera_y):
        if self.derrotado:
            return

        pos_x = round(self.x - camera_x)
        pos_y = round(self.y - camera_y)

        quadros = self.sprites.get(self.direcao, [])

        if quadros:
            imagem = quadros[self.quadro % len(quadros)]
            tela.blit(imagem, (pos_x, pos_y))
        else:
            retangulo = pygame.Rect(
                pos_x,
                pos_y,
                self.colisao.width,
                self.colisao.height,
            )

            pygame.draw.rect(
                tela,
                self.cor,
                retangulo,
                border_radius=7
            )

            pygame.draw.rect(
                tela,
                Preto,
                retangulo,
                2,
                border_radius=7
            )

        fonte = pygame.font.Font(None, 20)
        nome = fonte.render(self.nome, True, Branco)

        fundo = nome.get_rect(
            midbottom=(
                pos_x + self.largura_sprite // 2,
                pos_y - 2
            )
        )

        fundo.inflate_ip(8, 4)

        pygame.draw.rect(
            tela,
            Preto,
            fundo,
            border_radius=4
        )

        tela.blit(nome, (fundo.x + 4, fundo.y + 2))


# =========================================================
# BATALHA POR TURNOS
# =========================================================

class Batalha:
    def __init__(self, jogador, inimigo):
        self.jogador = jogador
        self.inimigo = inimigo

        self.ativa = True
        self.terminada = False
        self.vitoria = False
        self.derrota = False
        self.resultado = None

        self.turno = "jogador"
        self.defendendo = False

        self.mensagem = f"Um {inimigo.nome} apareceu!"
        self.opcoes = ["Atacar", "Defender"]
        self.opcao_selecionada = 0

        self.fonte = pygame.font.Font(None, 30)
        self.fonte_titulo = pygame.font.Font(None, 44)

    def calcular_dano(self, atacante, alvo):
        ataque = max(
            0,
            getattr(
                atacante,
                "danototal",
                getattr(atacante, "dano", 0)
            )
        )

        defesa = max(
            0,
            getattr(
                alvo,
                "defesatotal",
                getattr(alvo, "defesa", 0)
            )
        )

        if ataque <= 0:
            return 0

        dano = ataque * ataque / (ataque + defesa)

        return max(1, int(dano * random.uniform(0.9, 1.1)))

    def verificar_fim(self):
        if self.inimigo.hp <= 0:
            self.inimigo.hp = 0
            self.inimigo.derrotado = True
            self.ativa = False
            self.terminada = True
            self.vitoria = True
            self.resultado = "vitoria"

            self.jogador.ganhar_xp(self.inimigo.xp_recompensa)
            self.jogador.moedas += self.inimigo.moedas_recompensa

            self.mensagem = (
                f"Você venceu! +{self.inimigo.xp_recompensa} XP "
                f"e +{self.inimigo.moedas_recompensa} moedas."
            )

            return True

        if self.jogador.hp <= 0:
            self.jogador.hp = 0
            self.ativa = False
            self.terminada = True
            self.derrota = True
            self.resultado = "derrota"
            self.mensagem = "Você foi derrotado!"

            return True

        return False

    def atacar(self):
        if not self.ativa or self.turno != "jogador":
            return

        dano = self.jogador.calcular_dano(self.inimigo)
        self.inimigo.hp -= dano

        self.mensagem = f"Você causou {dano} de dano!"

        if self.verificar_fim():
            return

        self.turno = "inimigo"
        self.turno_inimigo()

    def defender(self):
        if not self.ativa or self.turno != "jogador":
            return

        self.defendendo = True
        self.mensagem = "Você se preparou para defender!"

        self.turno = "inimigo"
        self.turno_inimigo()

    def turno_inimigo(self):
        if not self.ativa:
            return

        dano = self.calcular_dano(self.inimigo, self.jogador)

        if self.defendendo:
            dano = max(1, dano // 2)
            self.defendendo = False
            self.mensagem = (
                f"Você defendeu e recebeu {dano} de dano."
            )
        else:
            self.mensagem = (
                f"{self.inimigo.nome} causou {dano} de dano!"
            )

        self.jogador.hp -= dano

        if self.verificar_fim():
            return

        self.turno = "jogador"
        self.opcao_selecionada = 0

    def processar_evento(self, evento):
        if not self.ativa or evento.type != pygame.KEYDOWN:
            return

        if self.turno != "jogador":
            return

        if evento.key in (pygame.K_UP, pygame.K_w):
            self.opcao_selecionada = (
                self.opcao_selecionada - 1
            ) % len(self.opcoes)

        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.opcao_selecionada = (
                self.opcao_selecionada + 1
            ) % len(self.opcoes)

        elif evento.key in (pygame.K_RETURN, pygame.K_z):
            if self.opcao_selecionada == 0:
                self.atacar()
            else:
                self.defender()

    def desenhar_barra(
        self,
        tela,
        x,
        y,
        largura,
        altura,
        hp,
        hpmaximo,
        cor
    ):
        pygame.draw.rect(
            tela,
            CinzaFraco,
            (x, y, largura, altura)
        )

        proporcao = (
            max(0, min(1, hp / hpmaximo))
            if hpmaximo > 0
            else 0
        )

        pygame.draw.rect(
            tela,
            cor,
            (
                x,
                y,
                int(largura * proporcao),
                altura
            )
        )

        pygame.draw.rect(
            tela,
            Branco,
            (x, y, largura, altura),
            2
        )

    def desenhar(self, tela):
        largura = tela.get_width()
        altura = tela.get_height()

        tela.fill(AzulMeiaNoite)

        pygame.draw.rect(
            tela,
            AzulArdósiaEscuro,
            (0, altura // 2, largura, altura // 2)
        )

        # Painel do inimigo
        pygame.draw.rect(
            tela,
            AzulMeiaNoite,
            (largura - 310, 30, 280, 110)
        )

        tela.blit(
            self.fonte.render(self.inimigo.nome, True, Branco),
            (largura - 295, 40)
        )

        self.desenhar_barra(
            tela,
            largura - 295,
            80,
            250,
            20,
            self.inimigo.hp,
            self.inimigo.hpmaximo,
            VermelhoTijolo
        )

        tela.blit(
            self.fonte.render(
                f"HP: {self.inimigo.hp}/{self.inimigo.hpmaximo}",
                True,
                Branco
            ),
            (largura - 295, 105)
        )

        # Painel do jogador
        pygame.draw.rect(
            tela,
            AzulMeiaNoite,
            (30, altura - 190, 300, 150)
        )

        tela.blit(
            self.fonte.render(self.jogador.nome, True, Branco),
            (45, altura - 180)
        )

        self.desenhar_barra(
            tela,
            45,
            altura - 145,
            270,
            20,
            self.jogador.hp,
            self.jogador.hpmaximo,
            VerdePrimavera
        )

        tela.blit(
            self.fonte.render(
                f"HP: {self.jogador.hp}/{self.jogador.hpmaximo}",
                True,
                Branco
            ),
            (45, altura - 115)
        )

        # Painel de comandos
        painel_x = largura - 310
        painel_y = altura - 190

        pygame.draw.rect(
            tela,
            AzulMeiaNoite,
            (painel_x, painel_y, 280, 150)
        )

        tela.blit(
            self.fonte_titulo.render("COMANDOS", True, Dourado),
            (painel_x + 15, painel_y + 10)
        )

        for i, opcao in enumerate(self.opcoes):
            selecionada = (
                i == self.opcao_selecionada
                and self.turno == "jogador"
                and self.ativa
            )

            cor = Dourado if selecionada else CinzaPrataClaro
            marcador = "> " if selecionada else "  "

            tela.blit(
                self.fonte.render(marcador + opcao, True, cor),
                (painel_x + 20, painel_y + 60 + i * 35)
            )

        # Mensagem
        pygame.draw.rect(
            tela,
            AzulMeiaNoite,
            (30, 30, min(largura - 60, 500), 55)
        )

        tela.blit(
            self.fonte.render(self.mensagem, True, Branco),
            (45, 45)
        )

        if self.terminada:
            resultado = "VITÓRIA!" if self.vitoria else "DERROTA!"

            texto = self.fonte_titulo.render(
                resultado,
                True,
                Dourado
            )

            tela.blit(
                texto,
                texto.get_rect(
                    center=(largura // 2, altura // 2)
                )
            )
