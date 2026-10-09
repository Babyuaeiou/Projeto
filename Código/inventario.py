
import pygame


class Inventario:
    COLUNAS = 9
    ESPACOS_MOCHILA = 27
    TOTAL_ESPACOS = 36

    def __init__(self):
        # Todos os espaços começam vazios.
        self.espacos = [None] * self.TOTAL_ESPACOS

        self.aberto = False
        self.cursor = 0
        self.espaco_selecionado = None

        self.fonte = pygame.font.Font(None, 28)
        self.fonte_menor = pygame.font.Font(None, 21)

        self.tamanho_espaco = 48
        self.intervalo = 5

    def tratar_evento(self, evento):
        """Processa os controles do inventário."""

        if evento.type != pygame.KEYDOWN:
            return False

        # Enter abre ou fecha o inventário.
        if evento.key == pygame.K_RETURN:
            self.aberto = not self.aberto
            self.espaco_selecionado = None
            return True

        # Com o inventário fechado, não consome outros controles.
        if not self.aberto:
            return False

        # Esc fecha o inventário.
        if evento.key == pygame.K_ESCAPE:
            self.aberto = False
            self.espaco_selecionado = None
            return True

        # Setas: navegar pela grade.
        if evento.key == pygame.K_LEFT:
            coluna = self.cursor % self.COLUNAS
            if coluna > 0:
                self.cursor -= 1

        elif evento.key == pygame.K_RIGHT:
            coluna = self.cursor % self.COLUNAS
            if coluna < self.COLUNAS - 1:
                self.cursor += 1

        elif evento.key == pygame.K_UP:
            if self.cursor >= self.COLUNAS:
                self.cursor -= self.COLUNAS

        elif evento.key == pygame.K_DOWN:
            if self.cursor + self.COLUNAS < self.TOTAL_ESPACOS:
                self.cursor += self.COLUNAS

        # Z confirma a seleção do espaço atual.
        elif evento.key == pygame.K_z:
            if self.espaco_selecionado == self.cursor:
                self.espaco_selecionado = None
            else:
                self.espaco_selecionado = self.cursor

        return True

    def desenhar(self, tela):
        """Desenha a interface do inventário."""

        if not self.aberto:
            return

        largura_tela, altura_tela = tela.get_size()

        tamanho = self.tamanho_espaco
        intervalo = self.intervalo

        largura_grade = (
            self.COLUNAS * tamanho
            + (self.COLUNAS - 1) * intervalo
        )

        largura_painel = largura_grade + 40
        altura_painel = 340

        painel = pygame.Rect(
            (largura_tela - largura_painel) // 2,
            (altura_tela - altura_painel) // 2,
            largura_painel,
            altura_painel,
        )

        # Fundo escuro, inspirado no inventário do Minecraft.
        pygame.draw.rect(
            tela, (35, 35, 39), painel
        )

        pygame.draw.rect(
            tela, (190, 190, 190), painel, 3
        )

        pygame.draw.rect(
            tela, (75, 75, 80),
            painel.inflate(-8, -8), 2
        )

        titulo = self.fonte.render(
            "Inventario", True, (245, 245, 245)
        )

        tela.blit(
            titulo,
            (painel.x + 20, painel.y + 14)
        )

        inicio_x = painel.x + 20
        inicio_y = painel.y + 55

        for indice in range(self.TOTAL_ESPACOS):
            coluna = indice % self.COLUNAS

            if indice < self.ESPACOS_MOCHILA:
                linha = indice // self.COLUNAS
                y = inicio_y + linha * (tamanho + intervalo)
            else:
                # Barra inferior, separada da mochila.
                linha = 3
                y = inicio_y + 3 * (tamanho + intervalo) + 15

            x = inicio_x + coluna * (tamanho + intervalo)

            retangulo = pygame.Rect(
                x, y, tamanho, tamanho
            )

            # Fundo de cada espaço.
            pygame.draw.rect(
                tela, (91, 91, 96), retangulo
            )

            pygame.draw.rect(
                tela, (25, 25, 28), retangulo, 3
            )

            # Espaço selecionado pelas setas.
            if indice == self.cursor:
                pygame.draw.rect(
                    tela, (255, 220, 80), retangulo, 3
                )

            # Espaço confirmado com Z.
            if indice == self.espaco_selecionado:
                pygame.draw.rect(
                    tela, (100, 230, 130),
                    retangulo.inflate(-8, -8), 3
                )

        if self.espaco_selecionado is None:
            mensagem = "Setas: navegar   Z: selecionar"
        else:
            mensagem = (
                f"Espaco selecionado: "
                f"{self.espaco_selecionado + 1}"
                "   Z: desmarcar"
            )

        texto = self.fonte_menor.render(
            mensagem, True, (240, 240, 240)
        )

        tela.blit(
            texto,
            (
                painel.centerx - texto.get_width() // 2,
                painel.bottom - 31,
            )
        )

        dica = self.fonte_menor.render(
            "ENTER: fechar   ESC: fechar",
            True, (185, 185, 185)
        )

        tela.blit(
            dica,
            (
                painel.centerx - dica.get_width() // 2,
                painel.bottom + 8,
            )
        )
