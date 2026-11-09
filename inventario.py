
import pygame
from item import catalogo
from cores import *


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
        restantes = {
            str(item_id): max(0, int(quantidade))
            for item_id, quantidade in jogador.inventario.items()
            if int(quantidade) > 0
        }
        novos_espacos = [None] * self.TOTAL_ESPACOS

        for indice, slot in enumerate(self.espacos):
            if not slot:
                continue
            item_id = slot.get("item_id")
            item = catalogo.obter(item_id)
            if item is None or restantes.get(item_id, 0) <= 0:
                continue
            limite_pilha = max(1, int(item.max_pilha))
            quantidade = min(
                int(slot.get("quantidade", 1)),
                limite_pilha,
                restantes[item_id],
            )
            if quantidade > 0:
                novos_espacos[indice] = {
                    "item_id": item_id,
                    "quantidade": quantidade,
                }
                restantes[item_id] -= quantidade

        for item_id, quantidade_total in restantes.items():
            item = catalogo.obter(item_id)
            if item is None:
                continue
            limite_pilha = max(1, int(item.max_pilha))
            restante = quantidade_total
            while restante > 0:
                try:
                    indice = novos_espacos.index(None)
                except ValueError:
                    self.mensagem = "Inventário cheio."
                    break
                quantidade_pilha = min(restante, limite_pilha)
                novos_espacos[indice] = {
                    "item_id": item_id,
                    "quantidade": quantidade_pilha,
                }
                restante -= quantidade_pilha

        self.espacos = novos_espacos

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

        restante = int(quantidade)
        limite_pilha = max(1, int(item.max_pilha))

        # Verifica a capacidade antes de alterar o inventário, evitando perdas parciais.
        capacidade = 0
        for slot in self.espacos:
            if slot is None:
                capacidade += limite_pilha
            elif limite_pilha > 1 and slot.get("item_id") == item_id:
                capacidade += max(0, limite_pilha - int(slot.get("quantidade", 1)))
        if capacidade < restante:
            self.mensagem = "Inventário cheio."
            return False

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

        elif evento.key == pygame.K_z:
            if self.espaco_selecionado is None:
                self.espaco_selecionado = self.cursor
            else:
                primeiro = self.espaco_selecionado
                segundo = self.cursor
                self.espacos[primeiro], self.espacos[segundo] = self.espacos[segundo], self.espacos[primeiro]
                self.espaco_selecionado = None
                self.mensagem = "Itens trocados de lugar."
                if jogador is not None:
                    self.sincronizar_para_personagem(jogador)

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

        largura, altura = tela.get_size()
        painel = pygame.Rect(35, 25, largura - 70, altura - 50)
        pygame.draw.rect(tela, AzulMeiaNoite, painel, border_radius=10)
        pygame.draw.rect(tela, Dourado, painel, 2, border_radius=10)

        tela.blit(self.fonte.render("INVENTÁRIO", True, Dourado), (55, 38))
        tela.blit(self.fonte_menor.render("Mochila", True, Branco), (58, 83))

        inicio_x = 58
        inicio_y = 108
        passo = self.tamanho_espaco + self.intervalo

        for indice in range(self.TOTAL_ESPACOS):
            if indice < self.ESPACOS_MOCHILA:
                linha = indice // self.COLUNAS
                coluna = indice % self.COLUNAS
                x = inicio_x + coluna * passo
                y = inicio_y + linha * passo
            else:
                coluna = indice - self.ESPACOS_MOCHILA
                x = inicio_x + coluna * passo
                y = 310

            retangulo = pygame.Rect(x, y, self.tamanho_espaco, self.tamanho_espaco)
            cor_fundo = CinzaArdósiaEscuro if indice < self.ESPACOS_MOCHILA else AzulArdósiaEscuro
            pygame.draw.rect(tela, cor_fundo, retangulo, border_radius=5)
            pygame.draw.rect(tela, CinzaArdósiaClaro, retangulo, 1, border_radius=5)

            slot = self.espacos[indice]
            if slot:
                item = catalogo.obter(slot.get("item_id"))
                if item:
                    nome = self.fonte_menor.render(item.nome[:8], True, BrancoAntigo)
                    tela.blit(nome, (x + 3, y + 7))
                    quantidade = int(slot.get("quantidade", 1))
                    if quantidade > 1:
                        texto_qtd = self.fonte_menor.render(str(quantidade), True, AmareloClaro)
                        tela.blit(texto_qtd, (x + 34, y + 29))

            if indice == self.cursor:
                pygame.draw.rect(tela, Dourado, retangulo, 3, border_radius=5)
            if indice == self.espaco_selecionado:
                pygame.draw.rect(tela, VerdePrimavera, retangulo, 3, border_radius=5)

        painel_equipamentos = pygame.Rect(555, 80, 185, 270)
        pygame.draw.rect(tela, AzulArdósiaEscuro, painel_equipamentos, border_radius=7)
        pygame.draw.rect(tela, CinzaArdósiaClaro, painel_equipamentos, 1, border_radius=7)
        tela.blit(self.fonte_menor.render("EQUIPAMENTOS", True, Dourado), (568, 94))

        if jogador is not None:
            for indice, (chave, titulo) in enumerate((("arma", "Arma"), ("armadura", "Armadura"))):
                y = 132 + indice * 105
                caixa = pygame.Rect(570, y, 150, 76)
                pygame.draw.rect(tela, CinzaArdósiaEscuro, caixa, border_radius=5)
                pygame.draw.rect(tela, Dourado, caixa, 1, border_radius=5)
                equipado = catalogo.obter(jogador.equipamentos.get(chave))
                tela.blit(self.fonte_menor.render(titulo, True, Branco), (580, y + 7))
                nome = equipado.nome if equipado else "Vazio"
                tela.blit(self.fonte_menor.render(nome[:15], True, AmareloClaro), (580, y + 34))

        tela.blit(self.fonte_menor.render("Barra rápida", True, Branco), (58, 286))
        tela.blit(self.fonte_menor.render("Setas: mover | Z: selecionar/trocar | X: usar/equipar | E/ESC: fechar", True, CinzaPrataClaro), (58, altura - 67))
        if self.mensagem:
            tela.blit(self.fonte_menor.render(self.mensagem[:75], True, AmareloDouradoClaro), (58, altura - 43))
