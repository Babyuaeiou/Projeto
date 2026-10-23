
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

        # Atributos-base e pontos distribuíveis.
        self.hp_base = 20
        self.dano_base = 5
        self.defesa_base = 3
        self.atributos_distribuidos = {
            "vitalidade": 0,
            "forca": 0,
            "defesa": 0,
            "agilidade": 0,
        }
        self.pontos_atributo = 0
        self.limite_atributo = 20
        self.hpmaximo = self.hp_base
        self.hp = self.hpmaximo
        self.dano = self.dano_base
        self.defesa = self.defesa_base
        self.danototal = self.dano_base
        self.defesatotal = self.defesa_base
        self.velocidade = 1.0
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
                caminho = self._resolver_caminho_sprite(arquivo)
                imagem = pygame.image.load(caminho).convert_alpha()
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

    @staticmethod
    def _resolver_caminho_sprite(arquivo):
        """Localiza sprites tanto na raiz quanto na pasta de sprites do projeto."""
        from pathlib import Path
        base = Path(__file__).resolve().parent
        candidatos = [base / arquivo, base / "sprite principal" / arquivo]
        for candidato in candidatos:
            if candidato.is_file():
                return str(candidato)
            pasta = candidato.parent
            if pasta.is_dir():
                encontrado = next((p for p in pasta.iterdir() if p.name.casefold() == candidato.name.casefold()), None)
                if encontrado is not None:
                    return str(encontrado)
        raise FileNotFoundError(
            f"Sprite '{arquivo}' não encontrado. Procurado em: "
            + ", ".join(str(c) for c in candidatos)
        )

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
        """Recalcula atributos sem acumular bônus de equipamento repetidamente."""
        from item import catalogo

        distribuicao = getattr(self, "atributos_distribuidos", {}) or {}
        vitalidade = max(0, int(distribuicao.get("vitalidade", 0)))
        forca = max(0, int(distribuicao.get("forca", 0)))
        defesa_extra = max(0, int(distribuicao.get("defesa", 0)))
        agilidade = max(0, int(distribuicao.get("agilidade", 0)))

        self.hpmaximo = max(1, int(getattr(self, "hp_base", 20)) + vitalidade * 5)
        self.dano = int(getattr(self, "dano_base", 5)) + forca * 2
        self.defesa = int(getattr(self, "defesa_base", 3)) + defesa_extra

        for slot, atributo in (("arma", "dano"), ("armadura", "defesa")):
            item_id = self.equipamentos.get(slot)
            item = catalogo.obter(item_id) if item_id else None
            if item is not None:
                bonus = (getattr(item, "atributos", {}) or {}).get(atributo, 0)
                if isinstance(bonus, (int, float)):
                    if atributo == "dano":
                        self.dano += bonus
                    else:
                        self.defesa += bonus

        self.danototal = max(0, int(self.dano))
        self.defesatotal = max(0, int(self.defesa))
        # Agilidade reduz o intervalo de ação, com limite para evitar abuso.
        self.velocidade = min(1.30, 1.0 + agilidade * 0.015)
        self.cooldown = max(0.65, 1.0 / self.velocidade)
        self.hp = max(0, min(int(getattr(self, "hp", self.hpmaximo)), self.hpmaximo))

    def distribuir_ponto(self, atributo):
        """Investe um ponto disponível em um atributo válido."""
        if atributo not in self.atributos_distribuidos or self.pontos_atributo <= 0:
            return False
        if self.atributos_distribuidos[atributo] >= self.limite_atributo:
            return False

        hp_anterior = self.hpmaximo
        self.atributos_distribuidos[atributo] += 1
        self.pontos_atributo -= 1
        self.recalcular_atributos()
        if atributo == "vitalidade":
            self.hp = min(self.hpmaximo, self.hp + (self.hpmaximo - hp_anterior))
        return True

    def ganhar_xp(self, quantidade):
        if quantidade <= 0:
            return 0

        niveis_ganhos = 0
        self.xp += int(quantidade)
        while self.xp >= self.xp_proximo:
            self.xp -= self.xp_proximo
            self.nivel += 1
            niveis_ganhos += 1
            self.pontos_atributo += 3
            self.xp_proximo = max(self.xp_proximo + 1, int(self.xp_proximo * 1.35))

        if niveis_ganhos:
            hp_antigo = self.hpmaximo
            self.recalcular_atributos()
            self.hp = min(self.hpmaximo, self.hp + max(0, self.hpmaximo - hp_antigo))
        return niveis_ganhos

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
            dano = int(dano * (1 + float(self.buff_proximo_ataque)))
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

        base = os.path.dirname(os.path.abspath(__file__))
        candidatos = [os.path.abspath(sprite), os.path.join(base, sprite)]
        # Sprites dos inimigos podem estar organizados em pastas temáticas.
        candidatos.extend([
            os.path.join(base, "gatu esqueletu", os.path.basename(sprite)),
            os.path.join(base, "Frames arara", os.path.basename(sprite)),
        ])
        caminho = next((c for c in candidatos if os.path.isfile(c)), None)
        if caminho is None:
            nome = os.path.basename(sprite).casefold()
            for pasta_raiz, _, arquivos in os.walk(base):
                achado = next((a for a in arquivos if a.casefold() == nome), None)
                if achado:
                    caminho = os.path.join(pasta_raiz, achado)
                    break
        if caminho is None:
            return

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
    """Combate ATB: jogador e inimigo carregam suas barras independentemente."""

    ATB_MAXIMO = 100.0

    def __init__(self, jogador, inimigo):
        self.jogador = jogador
        self.inimigo = inimigo
        self.ativa = True
        self.terminada = False
        self.vitoria = False
        self.derrota = False
        self.resultado = None
        self.defendendo = False
        self.barra_jogador = 0.0
        self.barra_inimigo = 0.0
        self.jogador_pronto = False
        self.opcoes = ["Atacar", "Defender", "Usar item", "Fugir"]
        self.opcao_selecionada = 0
        self.mensagem = f"Um {inimigo.nome} apareceu!"
        self.fonte = pygame.font.Font(None, 27)
        self.fonte_titulo = pygame.font.Font(None, 42)
        self.tempo_mensagem = 0.0

    def atualizar(self, dt):
        if not self.ativa:
            return
        dt = max(0.0, min(float(dt), 0.1))
        if self.tempo_mensagem > 0:
            self.tempo_mensagem = max(0.0, self.tempo_mensagem - dt)

        velocidade_jogador = max(0.65, min(1.30, float(getattr(self.jogador, "velocidade", 1.0))))
        velocidade_inimigo = max(0.65, min(1.30, float(getattr(self.inimigo, "velocidade_atb", 1.0))))

        if not self.jogador_pronto:
            self.barra_jogador = min(self.ATB_MAXIMO, self.barra_jogador + dt * 32 * velocidade_jogador)
            if self.barra_jogador >= self.ATB_MAXIMO:
                self.jogador_pronto = True
                self.mensagem = "Sua ação está pronta. Escolha um comando."
                self.tempo_mensagem = 2.0

        self.barra_inimigo = min(self.ATB_MAXIMO, self.barra_inimigo + dt * 25 * velocidade_inimigo)
        if self.barra_inimigo >= self.ATB_MAXIMO and self.ativa:
            self._acao_inimigo()

    def calcular_dano(self, atacante, alvo):
        ataque = max(1, int(getattr(atacante, "danototal", getattr(atacante, "dano", 1))))
        defesa = max(0, int(getattr(alvo, "defesatotal", getattr(alvo, "defesa", 0))))
        dano = max(1, int(ataque * ataque / (ataque + defesa) * random.uniform(0.9, 1.1)))
        return dano

    def _mensagem(self, texto):
        self.mensagem = texto
        self.tempo_mensagem = 2.5

    def _gastar_acao_jogador(self):
        self.barra_jogador = 0.0
        self.jogador_pronto = False
        self.opcao_selecionada = 0

    def _verificar_fim(self):
        if self.inimigo.hp <= 0:
            self.inimigo.hp = 0
            self.inimigo.derrotado = True
            self.ativa = False
            self.terminada = True
            self.vitoria = True
            self.resultado = "vitoria"
            self.jogador.ganhar_xp(self.inimigo.xp_recompensa)
            self.jogador.moedas += self.inimigo.moedas_recompensa
            self._mensagem(f"Vitória! +{self.inimigo.xp_recompensa} XP e +{self.inimigo.moedas_recompensa} moedas.")
            return True
        if self.jogador.hp <= 0:
            self.jogador.hp = 0
            self.ativa = False
            self.terminada = True
            self.derrota = True
            self.resultado = "derrota"
            self._mensagem("Você foi derrotado!")
            return True
        return False

    def _acao_inimigo(self):
        self.barra_inimigo = 0.0
        dano = self.calcular_dano(self.inimigo, self.jogador)
        if self.defendendo:
            dano = max(1, dano // 2)
            self.defendendo = False
            self._mensagem(f"Você defendeu o golpe e recebeu {dano} de dano.")
        else:
            self._mensagem(f"{self.inimigo.nome} causou {dano} de dano!")
        self.jogador.hp = max(0, self.jogador.hp - dano)
        self._verificar_fim()

    def _usar_item(self):
        from item import catalogo
        for item_id, quantidade in list(self.jogador.inventario.items()):
            if quantidade <= 0:
                continue
            item = catalogo.obter(item_id)
            if item is None or item.categoria not in ("pocao", "consumivel"):
                continue
            efeitos = item.efeitos or {}
            cura = int(efeitos.get("cura", 0))
            cura_total = bool(efeitos.get("cura_total", False))
            if cura_total or cura > 0:
                if self.jogador.hp >= self.jogador.hpmaximo:
                    self._mensagem("Seu HP já está cheio.")
                    return False
                antes = self.jogador.hp
                self.jogador.hp = self.jogador.hpmaximo if cura_total else min(self.jogador.hpmaximo, self.jogador.hp + cura)
                self.jogador.remover_item(item_id, 1)
                self._mensagem(f"Você usou {item.nome} e recuperou {self.jogador.hp - antes} HP.")
                return True
            bonus = efeitos.get("buff_proximo_ataque", 0)
            if bonus:
                self.jogador.buff_proximo_ataque = getattr(self.jogador, "buff_proximo_ataque", 0) + bonus
                self.jogador.remover_item(item_id, 1)
                self._mensagem(f"Você usou {item.nome}.")
                return True
        self._mensagem("Você não possui um item utilizável.")
        return False

    def executar_comando(self):
        if not self.ativa or not self.jogador_pronto:
            return
        comando = self.opcoes[self.opcao_selecionada]
        if comando == "Atacar":
            dano = self.jogador.calcular_dano(self.inimigo)
            self.inimigo.hp = max(0, self.inimigo.hp - dano)
            self._mensagem(f"Você causou {dano} de dano!")
            self._gastar_acao_jogador()
            self._verificar_fim()
        elif comando == "Defender":
            self.defendendo = True
            self._mensagem("Você assumiu uma postura defensiva.")
            self._gastar_acao_jogador()
        elif comando == "Usar item":
            if self._usar_item():
                self._gastar_acao_jogador()
        elif comando == "Fugir":
            if getattr(self.inimigo, "chefe", False):
                self._mensagem("Não é possível fugir de um chefe!")
            elif random.random() < 0.65:
                self.ativa = False
                self.terminada = True
                self.resultado = "fuga"
                self._mensagem("Você conseguiu fugir!")
            else:
                self._mensagem("A fuga falhou!")
                self._gastar_acao_jogador()

    def processar_evento(self, evento):
        if not self.ativa or evento.type != pygame.KEYDOWN:
            return
        if not self.jogador_pronto:
            return
        if evento.key in (pygame.K_UP, pygame.K_w):
            self.opcao_selecionada = (self.opcao_selecionada - 1) % len(self.opcoes)
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.opcao_selecionada = (self.opcao_selecionada + 1) % len(self.opcoes)
        elif evento.key in (pygame.K_RETURN, pygame.K_z):
            self.executar_comando()

    def _desenhar_barra(self, tela, x, y, largura, altura, valor, maximo, cor):
        pygame.draw.rect(tela, CinzaArdósiaEscuro, (x, y, largura, altura), border_radius=4)
        proporcao = max(0.0, min(1.0, valor / maximo if maximo else 0.0))
        if proporcao:
            pygame.draw.rect(tela, cor, (x, y, int(largura * proporcao), altura), border_radius=4)
        pygame.draw.rect(tela, Branco, (x, y, largura, altura), 1, border_radius=4)

    def desenhar(self, tela):
        largura, altura = tela.get_size()
        tela.fill(AzulMeiaNoite)
        pygame.draw.rect(tela, AzulArdósiaEscuro, (0, altura // 2, largura, altura // 2))

        tela.blit(self.fonte_titulo.render(self.inimigo.nome, True, Branco), (40, 35))
        tela.blit(self.fonte.render(f"HP {max(0, self.inimigo.hp)}/{self.inimigo.hpmaximo}", True, Branco), (40, 82))
        self._desenhar_barra(tela, 40, 110, largura - 80, 18, self.inimigo.hp, self.inimigo.hpmaximo, VermelhoTijolo)
        tela.blit(self.fonte.render("ATB do inimigo", True, Branco), (40, 145))
        self._desenhar_barra(tela, 40, 172, largura - 80, 12, self.barra_inimigo, self.ATB_MAXIMO, Dourado)

        painel = pygame.Rect(30, altura - 225, largura - 60, 190)
        pygame.draw.rect(tela, AzulMeiaNoite, painel, border_radius=8)
        pygame.draw.rect(tela, Dourado, painel, 2, border_radius=8)
        tela.blit(self.fonte.render(f"{self.jogador.nome}  |  HP {self.jogador.hp}/{self.jogador.hpmaximo}", True, Branco), (48, altura - 210))
        tela.blit(self.fonte.render("ATB do jogador", True, Branco), (48, altura - 178))
        self._desenhar_barra(tela, 48, altura - 154, largura - 96, 14, self.barra_jogador, self.ATB_MAXIMO, VerdePrimavera)

        colunas = [48, largura // 2 + 10]
        for i, opcao in enumerate(self.opcoes):
            selecionada = i == self.opcao_selecionada and self.jogador_pronto
            cor = Dourado if selecionada else CinzaPrataClaro
            x = colunas[i % 2]
            y = altura - 125 + (i // 2) * 30
            marcador = "> " if selecionada else "  "
            tela.blit(self.fonte.render(marcador + opcao, True, cor), (x, y))

        cor_mensagem = Dourado if self.jogador_pronto else Branco
        tela.blit(self.fonte.render(self.mensagem[:95], True, cor_mensagem), (40, altura - 265))
        if self.terminada:
            resultado = "VITÓRIA!" if self.vitoria else ("DERROTA!" if self.derrota else "FUGA!")
            texto = self.fonte_titulo.render(resultado, True, Dourado)
            tela.blit(texto, texto.get_rect(center=(largura // 2, altura // 2)))
