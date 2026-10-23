import pygame

from cores import *
from personagem import Personagem, Inimigo, Batalha
from banco import (
    criar_banco,
    salvar_posicao,
    carregar_posicao,
    salvar_partida,
    carregar_partida,
)
from inventario import Inventario
from item import catalogo
from npcs import NPC


# =========================================================
# INICIALIZAÇÃO
# =========================================================

pygame.init()

LARGURA_TELA = 800
ALTURA_TELA = 600

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Hunt Bird")

relogio = pygame.time.Clock()
fonte = pygame.font.Font(None, 24)
fonte_grande = pygame.font.Font(None, 34)

criar_banco()


# =========================================================
# MAPA
# =========================================================

mapa_largura = 2400
mapa_altura = 1800
mapa_atual = "mapa_inicial"

objetos_colisao = []

# =========================================================
# JOGADOR
# =========================================================

jogador = Personagem(
    "Servo do Rei Demônio",
    "F1.png",
    3
)

jogador.equipamentos["arma"] = "punhos"
jogador.equipamentos["armadura"] = None
jogador.recalcular_atributos()

inventario = Inventario()

dados_salvos = carregar_partida(
    jogador,
    inventario,
    mapa_atual
)

if dados_salvos:
    mapa_atual = dados_salvos["mapa_atual"]
else:
    jogador.adicionar_item("pocao_pequena", 2)
    jogador.adicionar_item("pedra_afiacao", 1)

    posicao_salva = carregar_posicao()

    if posicao_salva:
        jogador.x, jogador.y = posicao_salva

    jogador.colisao.topleft = (
        round(jogador.x),
        round(jogador.y)
    )

inventario.sincronizar_do_personagem(jogador)


# =========================================================
# INIMIGOS
# =========================================================

inimigos = [
    Inimigo(
        nome="gato esqueleto",
        hpmaximo=22,
        dano=6,
        defesa=2,
        x=760,
        y=520,
        xp_recompensa=18,
        moedas_recompensa=10,
        chefe=False,
        cor=MarromSela,
        sprite="gt1.png",
        tamanho_sprite=(64, 64),
        velocidade_movimento=45,
        distancia_maxima=150,
        pode_andar=True
    ),
]

# =========================================================
# NPCs
# =========================================================

npcs = [
    NPC(
        nome="Morador",
        x=300,
        y=300,
        dialogos=[
            "Que bom encontrar alguém por aqui!",
            "Tenho visto lobos rondando a estrada.",
            "Tome cuidado quando entrar na floresta.",
            "Boa sorte na sua jornada!"
        ],
        sprite=None,
        tem_loja=False,
        pode_andar=True,
        velocidade=35,
        distancia_maxima=100,
        cor=VerdePrimavera
    ),

    NPC(
        nome="Vendedor",
        x=450,
        y=300,
        dialogos=[
            "Bem-vindo à minha loja!",
            "Tenho poções e equipamentos para vender.",
            "Use as setas para escolher uma mercadoria."
        ],
        sprite=None,
        tem_loja=True,
        pode_andar=False,
        cor=Dourado
    ),
]


# =========================================================
# ESTADO DO JOGO
# =========================================================

batalha = None
npc_dialogo_atual = None

loja_aberta = False
loja_cursor = 0
mostrar_coordenadas = False

itens_loja = [
    ("pocao_pequena", 10),
    ("pocao_grande", 35),
    ("elixir_servo", 75),
    ("pedra_afiacao", 20),
    ("espada_enferrujada", 25),
    ("armadura_couro", 30),
    ("espada_ferro", 80),
    ("armadura_ferro", 90),
]


# =========================================================
# TEXTO
# =========================================================

def desenhar_texto(texto, x, y, cor=Branco, fonte_usada=None):
    if fonte_usada is None:
        fonte_usada = fonte

    imagem = fonte_usada.render(
        str(texto),
        True,
        cor
    )

    tela.blit(imagem, (x, y))


# =========================================================
# SALVAMENTO
# =========================================================

def salvar_jogo():
    inventario.sincronizar_para_personagem(jogador)

    salvar_partida(
        jogador,
        inventario,
        objetos_colisao,
        mapa_atual
    )

    salvar_posicao(jogador.x, jogador.y)


# =========================================================
# COORDENADAS
# =========================================================

def desenhar_coordenadas():
    pygame.draw.rect(
        tela,
        AzulMeiaNoite,
        (10, 10, 175, 85),
        border_radius=6
    )

    desenhar_texto(
        "COORDENADAS",
        20,
        17,
        Dourado
    )

    desenhar_texto(
        f"X: {int(jogador.x)}",
        20,
        42
    )

    desenhar_texto(
        f"Y: {int(jogador.y)}",
        20,
        64
    )


# =========================================================
# MINIMAPA
# =========================================================

def desenhar_minimapa():
    largura = 180
    altura = 135
    margem = 10

    x = LARGURA_TELA - largura - margem
    y = margem

    area = pygame.Rect(
        x + 3,
        y + 3,
        largura - 6,
        altura - 6
    )

    pygame.draw.rect(
        tela,
        AzulMeiaNoite,
        (x, y, largura, altura),
        border_radius=5
    )

    pygame.draw.rect(
        tela,
        CinzaArdósiaEscuro,
        area
    )

    escala_x = area.width / mapa_largura
    escala_y = area.height / mapa_altura

    def posicao_minimapa(px, py):
        return (
            area.x + round(px * escala_x),
            area.y + round(py * escala_y)
        )

    for inimigo in inimigos:
        if not inimigo.derrotado:
            pygame.draw.circle(
                tela,
                VermelhoTijolo,
                posicao_minimapa(inimigo.x, inimigo.y),
                3
            )

    for npc in npcs:
        pygame.draw.circle(
            tela,
            VerdePrimavera,
            posicao_minimapa(npc.x, npc.y),
            3
        )

    pygame.draw.circle(
        tela,
        AzulDodger,
        posicao_minimapa(jogador.x, jogador.y),
        4
    )

    pygame.draw.rect(
        tela,
        CinzaPrataClaro,
        (x, y, largura, altura),
        2,
        border_radius=5
    )


# =========================================================
# DESENHAR O MAPA
# =========================================================

def desenhar_mundo(camera_x, camera_y):
    tela.fill(VerdeMar)

    for inimigo in inimigos:
        if not inimigo.derrotado:
            inimigo.desenhar(
                tela,
                camera_x,
                camera_y
            )

    for npc in npcs:
        npc.desenhar(
            tela,
            camera_x,
            camera_y,
            jogador
        )

    jogador.desenhar(
        tela,
        camera_x,
        camera_y
    )

    pygame.draw.rect(
        tela,
        AzulMeiaNoite,
        (8, ALTURA_TELA - 65, 360, 57),
        border_radius=6
    )

    desenhar_texto(
        f"Nível {jogador.nivel}  HP {jogador.hp}/{jogador.hpmaximo}",
        18,
        ALTURA_TELA - 57
    )

    desenhar_texto(
        f"Dano {jogador.danototal}  "
        f"Defesa {jogador.defesatotal}  "
        f"Moedas {jogador.moedas}",
        18,
        ALTURA_TELA - 32,
        Dourado
    )

    desenhar_minimapa()

    if mostrar_coordenadas:
        desenhar_coordenadas()


# =========================================================
# LOJA
# =========================================================

def desenhar_loja():
    pygame.draw.rect(
        tela,
        AzulMeiaNoite,
        (90, 55, 620, 490),
        border_radius=10
    )

    pygame.draw.rect(
        tela,
        Dourado,
        (90, 55, 620, 490),
        3,
        border_radius=10
    )

    desenhar_texto(
        "LOJA",
        120,
        75,
        Dourado,
        fonte_grande
    )

    desenhar_texto(
        f"Moedas: {jogador.moedas}",
        120,
        115
    )

    for indice, (item_id, preco) in enumerate(itens_loja):
        item = catalogo.obter(item_id)

        if item is None:
            continue

        cor_texto = Branco

        if indice == loja_cursor:
            cor_texto = Dourado

        prefixo = "> " if indice == loja_cursor else "  "

        desenhar_texto(
            f"{prefixo}{item.nome} - {preco} moedas",
            130,
            155 + indice * 35,
            cor_texto
        )

    desenhar_texto(
        "ENTER ou Z: comprar | ESC: fechar",
        120,
        500,
        CinzaClaro
    )


def comprar_item():
    item_id, preco = itens_loja[loja_cursor]
    item = catalogo.obter(item_id)

    if item is None:
        return

    if jogador.moedas < preco:
        return

    jogador.moedas -= preco
    jogador.adicionar_item(item_id, 1)

    inventario.sincronizar_do_personagem(jogador)
    salvar_jogo()


# =========================================================
# CÂMERA
# =========================================================

def calcular_camera():
    camera_x = max(
        0,
        min(
            mapa_largura - LARGURA_TELA,
            jogador.x - LARGURA_TELA // 2
        )
    )

    camera_y = max(
        0,
        min(
            mapa_altura - ALTURA_TELA,
            jogador.y - ALTURA_TELA // 2
        )
    )

    return camera_x, camera_y


# =========================================================
# EVENTOS
# =========================================================

rodando = True

while rodando:
    dt = min(relogio.tick(60) / 1000, 0.05)

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        elif batalha is not None:
            batalha.processar_evento(evento)

            if batalha.terminada:
                if batalha.vitoria:
                    batalha.inimigo.derrotado = True

                    jogador.ganhar_xp(
                        batalha.inimigo.xp_recompensa
                    )

                    jogador.moedas += (
                        batalha.inimigo.moedas_recompensa
                    )

                elif batalha.derrota:
                    jogador.hp = jogador.hpmaximo
                    jogador.x = 650
                    jogador.y = 150

                    jogador.colisao.topleft = (
                        round(jogador.x),
                        round(jogador.y)
                    )

                batalha = None
                salvar_jogo()

        elif (
            npc_dialogo_atual is not None
            and npc_dialogo_atual.dialogo_aberto
        ):
            npc_dialogo_atual.processar_evento(evento)

            if not npc_dialogo_atual.dialogo_aberto:
                if npc_dialogo_atual.tem_loja:
                    loja_aberta = True

                npc_dialogo_atual = None

        elif loja_aberta:
            if evento.type == pygame.KEYDOWN:

                if evento.key in (
                    pygame.K_ESCAPE,
                    pygame.K_l
                ):
                    loja_aberta = False

                elif evento.key in (
                    pygame.K_UP,
                    pygame.K_w
                ):
                    loja_cursor = (
                        loja_cursor - 1
                    ) % len(itens_loja)

                elif evento.key in (
                    pygame.K_DOWN,
                    pygame.K_s
                ):
                    loja_cursor = (
                        loja_cursor + 1
                    ) % len(itens_loja)

                elif evento.key in (
                    pygame.K_RETURN,
                    pygame.K_z
                ):
                    comprar_item()

        elif inventario.aberto:
            if inventario.tratar_evento(evento, jogador):
                inventario.sincronizar_para_personagem(
                    jogador
                )

        elif evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_ESCAPE:
                rodando = False

            elif evento.key == pygame.K_F5:
                salvar_jogo()

            elif evento.key == pygame.K_c:
                mostrar_coordenadas = not mostrar_coordenadas

            elif evento.key == pygame.K_e:
                inventario.tratar_evento(
                    evento,
                    jogador
                )

            elif evento.key == pygame.K_l:
                loja_aberta = True

            elif evento.key == pygame.K_SPACE:
                for npc in npcs:
                    if npc.perto_do_jogador(jogador):
                        if npc.interagir(jogador):
                            npc_dialogo_atual = npc
                            break

    # =====================================================
    # ATUALIZAÇÃO DO MUNDO
    # =====================================================

    if (
        rodando
        and batalha is None
        and not loja_aberta
        and not inventario.aberto
        and npc_dialogo_atual is None
    ):
        retangulos_inimigos = [
            inimigo.colisao
            for inimigo in inimigos
            if not inimigo.derrotado
        ]

        obstaculos_npc = (
            list(objetos_colisao)
            + [jogador.colisao]
            + retangulos_inimigos
        )

        for npc in npcs:
            npc.atualizar(
                dt * 1000,
                obstaculos=obstaculos_npc,
                outros_npcs=npcs,
                limites_mundo=(mapa_largura, mapa_altura)
            )

        retangulos_npc = [
            npc.colisao
            for npc in npcs
        ]

        for inimigo in inimigos:
            if inimigo.derrotado:
                continue

            inimigo.atualizar(
                dt * 1000,
                obstaculos=(
                    list(objetos_colisao)
                    + retangulos_npc
                ),
                outros_inimigos=inimigos,
                limites_mundo=(mapa_largura, mapa_altura),
                jogador=jogador
            )

        obstaculos_jogador = (
            list(objetos_colisao)
            + [npc.colisao for npc in npcs]
        )

        jogador.atualizar(
            pygame.key.get_pressed(),
            dt,
            obstaculos_jogador,
            mapa_largura,
            mapa_altura
        )

        for inimigo in inimigos:
            if (
                not inimigo.derrotado
                and jogador.colisao.colliderect(
                    inimigo.colisao
                )
            ):
                batalha = Batalha(
                    jogador,
                    inimigo
                )
                break

    # =====================================================
    # DESENHO
    # =====================================================

    camera_x, camera_y = calcular_camera()

    if batalha is not None:
        batalha.desenhar(tela)

    else:
        desenhar_mundo(
            camera_x,
            camera_y
        )

        if loja_aberta:
            desenhar_loja()

        elif inventario.aberto:
            inventario.desenhar(
                tela,
                jogador
            )

        if (
            npc_dialogo_atual is not None
            and npc_dialogo_atual.dialogo_aberto
        ):
            npc_dialogo_atual.desenhar_dialogo(tela)

    pygame.display.flip()


# =========================================================
# ENCERRAMENTO
# =========================================================

salvar_jogo()
pygame.quit()
