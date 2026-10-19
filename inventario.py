
import pygame
from item import catalogo


class Inventario:
    COLUNAS = 9
    ESPACOS_MOCHILA = 27
    TOTAL_ESPACOS = 36

    def __init__(self):
        self.espacos = [None] * self.TOTAL_ESPACOS
        self.aberto = False
        self.cursor = 0
        self.espaco_selecionado = None

        self.fonte = pygame.font.Font(None, 28)
        self.fonte_menor = pygame.font.Font(None, 21)

        self.tamanho_espaco = 48
        self.intervalo = 5
        self.mensagem = ""

    # =====================================================
    # SINCRONIZAÇÃO COM PERSONAGEM
    # =====================================================

    def sincronizar_do_personagem(self, jogador):
        """Copia os itens do personagem para os espaços do inventário."""
        self.espacos = [None] * self.TOTAL_ESPACOS

        for item_id, quantidade in jogador.inventario.items():
            restante = int(quantidade)

            item = catalogo.obter(item_id)
            limite_pilha = (
                max(1, int(item.max_pilha))
                if item else 1
            )

            while restante > 0:
                try:
                    indice = self.espacos.index(None)
                except ValueError:
                    self.mensagem = "Inventário cheio."
                    return

                quantidade_pilha = min(restante, limite_pilha)

                self.espacos[indice] = {
                    "item_id": item_id,
                    "quantidade": quantidade_pilha
                }

                restante -= quantidade_pilha

    def sincronizar_para_personagem(self, jogador):
        """Copia os espaços do inventário para o personagem."""
        novo_inventario = {}

        for slot in self.espacos:
            if not slot:
                continue

            item_id = slot.get("item_id")
            quantidade = int(slot.get("quantidade", 1))

            if catalogo.obter(item_id) and quantidade > 0:
                novo_inventario[item_id] = (
                    novo_inventario.get(item_id, 0)
                    + quantidade
                )

        jogador.inventario = novo_inventario

    # =====================================================
    # ADICIONAR ITENS
    # =====================================================

    def adicionar(self, item_id, quantidade=1):
        item = catalogo.obter(item_id)

        if item is None or quantidade <= 0:
            return False

        restante = quantidade
        limite_pilha = max(1, int(item.max_pilha))

        # Primeiro, tenta completar pilhas existentes.
        if limite_pilha > 1:
            for slot in self.espacos:
                if (
                    slot
                    and slot.get("item_id") == item_id
                    and slot.get("quantidade", 1) < limite_pilha
                ):
                    espaco_livre = (
                        limite_pilha - slot["quantidade"]
                    )
                    adicionar_agora = min(restante, espaco_livre)

                    slot["quantidade"] += adicionar_agora
                    restante -= adicionar_agora

                    if restante <= 0:
                        return True

        # Depois, usa espaços vazios.
        while restante > 0:
            try:
                indice = self.espacos.index(None)
            except ValueError:
                self.mensagem = "Inventário cheio."
                return False

            quantidade_pilha = min(restante, limite_pilha)

            self.espacos[indice] = {
                "item_id": item_id,
                "quantidade": quantidade_pilha
            }

            restante -= quantidade_pilha

        return True

    # =====================================================
    # EVENTOS E CONTROLES
    # =====================================================

    def tratar_evento(self, evento, jogador=None):
        if evento.type != pygame.KEYDOWN:
            return False

        # Abre o inventário.
        if evento.key == pygame.K_e and not self.aberto:
            self.aberto = True
            self.espaco_selecionado = None

            if jogador is not None:
                self.sincronizar_do_personagem(jogador)

            return True

        if not self.aberto:
            return False

        # Fecha o inventário.
        if evento.key in (pygame.K_ESCAPE, pygame.K_e):
            self.aberto = False
            self.espaco_selecionado = None
            return True

        # Navegação pelas setas.
        if evento.key == pygame.K_LEFT:
            if self.cursor % self.COLUNAS > 0:
                self.cursor -= 1

        elif evento.key == pygame.K_RIGHT:
            if self.cursor % self.COLUNAS < self.COLUNAS - 1:
                self.cursor += 1

        elif evento.key == pygame.K_UP:
            if self.cursor >= self.COLUNAS:
                self.cursor -= self.COLUNAS

        elif evento.key == pygame.K_DOWN:
            if self.cursor + self.COLUNAS < self.TOTAL_ESPACOS:
                self.cursor += self.COLUNAS

        # Seleciona ou desmarca um espaço.
        elif evento.key == pygame.K_z:
            if self.espaco_selecionado == self.cursor:
                self.espaco_selecionado = None
            else:
                self.espaco_selecionado = self.cursor

        # Usa ou equipa o item selecionado pelo cursor.
        elif evento.key == pygame.K_x:
            if jogador is not None:
                self._acao_item(jogador)

        return True

    # =====================================================
    # USAR, EQUIPAR E DESEQUIPAR
    # =====================================================

    def _acao_item(self, jogador):
        slot = self.espacos[self.cursor]

        if not slot:
            self.mensagem = "Espaço vazio."
            return

        item_id = slot.get("item_id")
        item = catalogo.obter(item_id)

        if item is None:
            self.mensagem = "Item não encontrado no catálogo."
            return

        categoria = str(item.categoria).lower()

        # Armas e armaduras.
        if categoria in ("arma", "armadura", "armas", "armaduras"):
            sucesso = jogador.equipar(item_id)

            if sucesso:
                self.sincronizar_do_personagem(jogador)
                self.mensagem = f"{item.nome} equipado."
            else:
                self.mensagem = "Não foi possível equipar este item."

            return

        # Poções e consumíveis.
        if categoria in ("pocao", "poção", "consumivel", "consumível"):
            efeitos = getattr(item, "efeitos", {}) or {}
            usou_item = False

            # Cura.
            cura = int(efeitos.get("cura", 0))
            cura_total = efeitos.get("cura_total", False)

            if cura > 0 or cura_total:
                if jogador.hp >= jogador.hpmaximo:
                    self.mensagem = "Seu HP já está cheio."
                    return

                if cura_total:
                    jogador.hp = jogador.hpmaximo
                else:
                    jogador.hp = min(
                        jogador.hpmaximo,
                        jogador.hp + cura
                    )

                usou_item = True

            # Bônus para o próximo ataque.
            bonus = efeitos.get("buff_proximo_ataque", 0)

            if bonus:
                jogador.buff_proximo_ataque = (
                    getattr(jogador, "buff_proximo_ataque", 0)
                    + bonus
                )
                usou_item = True

            if not usou_item:
                self.mensagem = "Este item não tem efeito utilizável."
                return

            slot["quantidade"] -= 1

            if slot["quantidade"] <= 0:
                self.espacos[self.cursor] = None

            self.sincronizar_para_personagem(jogador)
            self.mensagem = f"Você usou {item.nome}."
            return

        self.mensagem = "Este item não pode ser usado agora."

    # =====================================================
    # DESENHAR INVENTÁRIO
    # =====================================================

    def desenhar(self, tela, jogador=None):
        if not self.aberto:
            return

        largura = tela.get_width()
        altura = tela.get_height()

        painel = pygame.Rect(
            40, 35, largura - 80, altura - 70
        )

        pygame.draw.rect(
            tela, (24, 25, 32), painel, border_radius=10
        )
        pygame.draw.rect(
            tela, (90, 90, 105), painel, 3, border_radius=10
        )

        titulo = self.fonte.render(
            "INVENTÁRIO", True, (245, 225, 160)
        )
        tela.blit(titulo, (60, 48))

        inicio_x = 60
        inicio_y = 95
        passo = self.tamanho_espaco + self.intervalo

        for indice in range(self.TOTAL_ESPACOS):
            linha = indice // self.COLUNAS
            coluna = indice % self.COLUNAS

            x = inicio_x + coluna * passo
            y = inicio_y + linha * passo

            if indice >= self.ESPACOS_MOCHILA:
                y += 15

            retangulo = pygame.Rect(
                x, y, self.tamanho_espaco, self.tamanho_espaco
            )

            cor = (
                (75, 78, 91)
                if indice < self.ESPACOS_MOCHILA
                else (60, 83, 72)
            )

            pygame.draw.rect(
                tela, cor, retangulo, border_radius=4
            )
            pygame.draw.rect(
                tela, (130, 130, 145),
                retangulo, 1, border_radius=4
            )

            slot = self.espacos[indice]

            if slot:
                item = catalogo.obter(slot.get("item_id"))

                if item:
                    nome = self.fonte_menor.render(
                        item.nome[:7], True, (245, 245, 245)
                    )
                    tela.blit(nome, (x + 3, y + 5))

                    quantidade = slot.get("quantidade", 1)

                    if quantidade > 1:
                        texto_qtd = self.fonte_menor.render(
                            str(quantidade),
                            True,
                            (255, 240, 100)
                        )
                        tela.blit(texto_qtd, (x + 34, y + 29))

            # Cursor atual.
            if indice == self.cursor:
                pygame.draw.rect(
                    tela, (255, 220, 70),
                    retangulo, 3, border_radius=4
                )

            # Espaço selecionado com Z.
            if indice == self.espaco_selecionado:
                pygame.draw.rect(
                    tela, (80, 240, 120),
                    retangulo, 3, border_radius=4
                )

        # Equipamentos atuais.
        if jogador is not None:
            arma = catalogo.obter(
                jogador.equipamentos.get("arma")
            )
            armadura = catalogo.obter(
                jogador.equipamentos.get("armadura")
            )

            nome_arma = arma.nome if arma else "Nenhuma"
            nome_armadura = armadura.nome if armadura else "Nenhuma"

            equipamento = (
                f"Arma: {nome_arma} | Armadura: {nome_armadura}"
            )

            tela.blit(
                self.fonte_menor.render(
                    equipamento, True, (255, 220, 140)
                ),
                (60, altura - 100)
            )

        ajuda = self.fonte_menor.render(
            "Setas: mover | Z: selecionar | X: usar/equipar | E/ESC: fechar",
            True,
            (230, 230, 230)
        )
        tela.blit(ajuda, (60, altura - 72))

        if self.mensagem:
            tela.blit(
                self.fonte_menor.render(
                    self.mensagem[:75],
                    True,
                    (255, 235, 140)
                ),
                (60, altura - 48)
            )
