
import pygame
import random


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

        # Inventário: {id_do_item: quantidade}
        self.inventario = {}

        # IDs dos itens equipados
        self.equipamentos = {
            "arma": None,
            "armadura": None
        }

        # Movimento
        self.x = 100
        self.y = 100
        self.velocidade_movimento = 5
        self.andando = False

        self.colisao = pygame.Rect(
            self.x, self.y, 50, 50
        )

        # Sprites direcionais
        self.nome_sprite = nome_sprite
        self.quantidade_sprites = quantidade_sprites

        nomes_sprites = {
            "direita": ["D1.PNG", "D2.PNG", "D3.PNG", "D1.PNG"],
            "esquerda": ["S1.PNG", "S2.PNG", "S3.PNG", "S1.PNG"],
            "cima": ["T1.PNG", "T2.PNG", "T3.PNG", "T1.PNG"],
            "baixo": ["F1.PNG", "F2.PNG", "F3.PNG", "F1.PNG"]
        }

        # Permite informar uma lista de sprites própria.
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
                imagem = pygame.image.load(
                    arquivo
                ).convert_alpha()
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
        """Adiciona uma quantidade de um item ao inventário."""
        if not isinstance(quantidade, int) or quantidade <= 0:
            return False

        if not isinstance(item_id, str) or not item_id:
            return False

        self.inventario[item_id] = (
            self.inventario.get(item_id, 0) + quantidade
        )
        return True

    def remover_item(self, item_id, quantidade=1):
        """Remove itens, desde que haja quantidade suficiente."""
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
        """
        Equipa uma arma ou armadura do catálogo.
        O equipamento anterior volta para o inventário.
        """
        from item import catalogo

        item = catalogo.obter(item_id)

        if item is None:
            return False

        categoria = str(
            getattr(item, "categoria", "")
        ).lower()

        if categoria in ("arma", "armas", "weapon"):
            slot = "arma"
        elif categoria in ("armadura", "armaduras", "armor"):
            slot = "armadura"
        else:
            return False

        if self.inventario.get(item_id, 0) <= 0:
            return False

        equipamento_anterior = self.equipamentos.get(slot)

        # Retira do inventário o item que será equipado.
        if not self.remover_item(item_id, 1):
            return False

        # Devolve o equipamento antigo ao inventário.
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

        categoria = str(
            getattr(item, "categoria", "")
        ).lower()

        if categoria not in ("arma", "armas", "weapon"):
            return False

        return self.equipar(item_id)

    def equipar_armadura(self, item_id):
        from item import catalogo

        item = catalogo.obter(item_id)
        if item is None:
            return False

        categoria = str(
            getattr(item, "categoria", "")
        ).lower()

        if categoria not in ("armadura", "armaduras", "armor"):
            return False

        return self.equipar(item_id)

    def desequipar(self, slot):
        """Desequipa arma ou armadura e devolve ao inventário."""
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
        """Recalcula dano e defesa usando os equipamentos atuais."""
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
        ataque = max(
            0,
            getattr(self, "danototal", self.dano)
        )

        defesa_alvo = max(
            0,
            getattr(alvo, "defesatotal", getattr(alvo, "defesa", 0))
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

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            movimento_x = -self.velocidade_movimento
            self.direcao = "esquerda"
        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            movimento_x = self.velocidade_movimento
            self.direcao = "direita"

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            movimento_y = -self.velocidade_movimento
            self.direcao = "cima"
        elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            movimento_y = self.velocidade_movimento
            self.direcao = "baixo"

        # Movimento horizontal
        if movimento_x:
            nova_x = self.x + movimento_x
            self.colisao.x = round(nova_x)

            dentro_mapa = (
                self.colisao.left >= 0
                and self.colisao.right <= mapa_largura
            )

            colidiu = self.colisao.collidelist(objetos_colisao) != -1

            if dentro_mapa and not colidiu:
                self.x = nova_x

            self.colisao.x = round(self.x)

        # Movimento vertical
        if movimento_y:
            nova_y = self.y + movimento_y
            self.colisao.y = round(nova_y)

            dentro_mapa = (
                self.colisao.top >= 0
                and self.colisao.bottom <= mapa_altura
            )

            colidiu = self.colisao.collidelist(objetos_colisao) != -1

            if dentro_mapa and not colidiu:
                self.y = nova_y

            self.colisao.y = round(self.y)

        self.colisao.topleft = (round(self.x), round(self.y))
        self.andando = bool(movimento_x or movimento_y)

    # =====================================================
    # ANIMAÇÃO DOS SPRITES
    # =====================================================

    def atualizar_animacao(self, tempo):
        teclas = pygame.key.get_pressed()

        teclas_movimento = {
            pygame.K_a: "esquerda",
            pygame.K_d: "direita",
            pygame.K_w: "cima",
            pygame.K_s: "baixo",
            pygame.K_LEFT: "esquerda",
            pygame.K_RIGHT: "direita",
            pygame.K_UP: "cima",
            pygame.K_DOWN: "baixo"
        }

        teclas_atuais = {
            tecla for tecla in teclas_movimento
            if teclas[tecla]
        }

        novas_teclas = teclas_atuais - self.teclas_movimento_anterior

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
        cor=(170, 55, 55)
    ):
        self.nome = nome
        self.hpmaximo = hpmaximo
        self.hp = hpmaximo
        self.dano = dano
        self.defesa = defesa

        self.x = x
        self.y = y
        self.colisao = pygame.Rect(x, y, 40, 40)

        self.xp_recompensa = xp_recompensa
        self.moedas_recompensa = moedas_recompensa
        self.chefe = chefe
        self.cor = cor
        self.derrotado = False

    def desenhar(self, tela, camera_x, camera_y):
        if self.derrotado:
            return

        retangulo = pygame.Rect(
            round(self.x - camera_x),
            round(self.y - camera_y),
            self.colisao.width,
            self.colisao.height
        )

        pygame.draw.rect(
            tela, self.cor, retangulo, border_radius=7
        )
        pygame.draw.rect(
            tela, (25, 25, 25), retangulo, 2, border_radius=7
        )

        fonte = pygame.font.Font(None, 20)
        nome = fonte.render(self.nome, True, (255, 255, 255))
        tela.blit(
            nome,
            (retangulo.x - 10, retangulo.y - 20)
        )


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
        ataque = max(0, getattr(atacante, "danototal",
                                getattr(atacante, "dano", 0)))
        defesa = max(0, getattr(alvo, "defesatotal",
                                getattr(alvo, "defesa", 0)))

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

            self.jogador.ganhar_xp(
                self.inimigo.xp_recompensa
            )
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
            self.mensagem = f"Você defendeu e recebeu {dano} de dano."
        else:
            self.mensagem = f"{self.inimigo.nome} causou {dano} de dano!"

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
        self, tela, x, y, largura, altura,
        hp, hpmaximo, cor
    ):
        pygame.draw.rect(
            tela, (60, 60, 60),
            (x, y, largura, altura)
        )

        proporcao = (
            max(0, min(1, hp / hpmaximo))
            if hpmaximo > 0 else 0
        )

        pygame.draw.rect(
            tela, cor,
            (x, y, int(largura * proporcao), altura)
        )
        pygame.draw.rect(
            tela, (255, 255, 255),
            (x, y, largura, altura), 2
        )

    def desenhar(self, tela):
        largura = tela.get_width()
        altura = tela.get_height()

        tela.fill((30, 45, 65))
        pygame.draw.rect(
            tela, (45, 65, 85),
            (0, altura // 2, largura, altura // 2)
        )

        # Painel do inimigo
        pygame.draw.rect(
            tela, (20, 25, 35),
            (largura - 310, 30, 280, 110)
        )

        tela.blit(
            self.fonte.render(
                self.inimigo.nome, True, (255, 255, 255)
            ),
            (largura - 295, 40)
        )

        self.desenhar_barra(
            tela, largura - 295, 80, 250, 20,
            self.inimigo.hp, self.inimigo.hpmaximo,
            (210, 55, 55)
        )

        tela.blit(
            self.fonte.render(
                f"HP: {self.inimigo.hp}/{self.inimigo.hpmaximo}",
                True, (255, 255, 255)
            ),
            (largura - 295, 105)
        )

        # Painel do jogador
        pygame.draw.rect(
            tela, (20, 25, 35),
            (30, altura - 190, 300, 150)
        )

        tela.blit(
            self.fonte.render(
                self.jogador.nome, True, (255, 255, 255)
            ),
            (45, altura - 180)
        )

        self.desenhar_barra(
            tela, 45, altura - 145, 270, 20,
            self.jogador.hp, self.jogador.hpmaximo,
            (50, 200, 90)
        )

        tela.blit(
            self.fonte.render(
                f"HP: {self.jogador.hp}/{self.jogador.hpmaximo}",
                True, (255, 255, 255)
            ),
            (45, altura - 115)
        )

        # Painel de comandos
        painel_x = largura - 310
        painel_y = altura - 190

        pygame.draw.rect(
            tela, (20, 25, 35),
            (painel_x, painel_y, 280, 150)
        )

        tela.blit(
            self.fonte_titulo.render(
                "COMANDOS", True, (255, 220, 100)
            ),
            (painel_x + 15, painel_y + 10)
        )

        for i, opcao in enumerate(self.opcoes):
            selecionada = (
                i == self.opcao_selecionada
                and self.turno == "jogador"
                and self.ativa
            )

            cor = (
                (255, 220, 100)
                if selecionada else (220, 220, 220)
            )

            marcador = "> " if selecionada else "  "

            tela.blit(
                self.fonte.render(
                    marcador + opcao, True, cor
                ),
                (painel_x + 20, painel_y + 60 + i * 35)
            )

        # Mensagem
        pygame.draw.rect(
            tela, (20, 25, 35),
            (30, 30, min(largura - 60, 500), 55)
        )

        tela.blit(
            self.fonte.render(
                self.mensagem, True, (255, 255, 255)
            ),
            (45, 45)
        )

        if self.terminada:
            resultado = (
                "VITÓRIA!"
                if self.vitoria else "DERROTA!"
            )

            texto = self.fonte_titulo.render(
                resultado, True, (255, 220, 100)
            )

            tela.blit(
                texto,
                texto.get_rect(
                    center=(largura // 2, altura // 2)
                )
            )
