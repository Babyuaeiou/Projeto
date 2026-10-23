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
from npc import NPC


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
        hpmaximo=1,
        dano=6,
        defesa=2,
        x=760,
        y=520,
        xp_recompensa=180000,
        moedas_recompensa=100000,
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
atributos_abertos = False
atributo_cursor = 0
mensagem_atributos = ""

itens_loja = [
    ("pocao_pequena", 10),
    ("pocao_grande", 35),
    ("elixir_servo", 75),
    ("pedra_afiacao", 20),
    ("espada_enferrujada", 25),
    ("armadura_couro", 30),
    ("espada_ferro", 80),
    ("armadura_ferro", 90),
    ("antidoto", 15),
    ("sais_revigorantes", 20),
    ("tonico_aceleracao", 30),
    ("lamina_cacador", 120),
    ("colete_escamas", 65),
    ("manto_explorador", 100),
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
    inventario.sincronizar_do_personagem(jogador)

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
# MINIMAPA AMPLIADO AO REDOR DO JOGADOR
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

    # Área do mundo exibida no minimapa.
    regiao_largura = min(
        LARGURA_TELA * 1.5,
        mapa_largura
    )

    regiao_altura = min(
        ALTURA_TELA * 1.5,
        mapa_altura
    )

    # Centraliza a região no jogador.
    origem_x = jogador.x - regiao_largura / 2
    origem_y = jogador.y - regiao_altura / 2

    # Mantém a região dentro dos limites do mapa.
    origem_x = max(
        0,
        min(mapa_largura - regiao_largura, origem_x)
    )

    origem_y = max(
        0,
        min(mapa_altura - regiao_altura, origem_y)
    )

    # Superfície que recebe os desenhos da região selecionada.
    superficie_minimapa = pygame.Surface(
        (
            max(1, round(regiao_largura)),
            max(1, round(regiao_altura))
        )
    )

    superficie_minimapa.fill(VerdeMar)

    # Desenha os inimigos nessa superfície.
    for inimigo in inimigos:
        if getattr(inimigo, "derrotado", False):
            continue

        inimigo.desenhar(
            superficie_minimapa,
            origem_x,
            origem_y
        )

    # Desenha os NPCs nessa superfície.
    for npc in npcs:
        npc.desenhar(
            superficie_minimapa,
            origem_x,
            origem_y,
            jogador
        )

    # Desenha o personagem normalmente.
    # Não desenha a bolinha azul adicional.
    jogador.desenhar(
        superficie_minimapa,
        origem_x,
        origem_y
    )

    # Redimensiona a região para caber no minimapa.
    imagem_minimapa = pygame.transform.scale(
        superficie_minimapa,
        (area.width, area.height)
    )

    tela.blit(
        imagem_minimapa,
        area.topleft
    )

    # Borda do minimapa.
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
        if not getattr(inimigo, "derrotado", False):
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
        f"Nível {jogador.nivel}  HP {jogador.hp}/{jogador.hpmaximo}  [P] Atributos",
        18,
        ALTURA_TELA - 57
    )

    desenhar_texto(
        f"Dano {jogador.danototal}  "
        f"Defesa {jogador.defesatotal}  "
        f"Moedas {jogador.moedas}  Pontos {jogador.pontos_atributo}",
        18,
        ALTURA_TELA - 32,
        Dourado
    )

    desenhar_minimapa()

    if mostrar_coordenadas:
        desenhar_coordenadas()


# =========================================================
# DISTRIBUIÇÃO DE ATRIBUTOS
# =========================================================

def desenhar_tela_atributos():
    painel = pygame.Rect(130, 90, 540, 420)

    pygame.draw.rect(
        tela,
        AzulMeiaNoite,
        painel,
        border_radius=10
    )

    pygame.draw.rect(
        tela,
        Dourado,
        painel,
        2,
        border_radius=10
    )

    desenhar_texto(
        "ATRIBUTOS DO PERSONAGEM",
        160,
        112,
        Dourado,
        fonte_grande
    )

    desenhar_texto(
        f"Pontos disponíveis: {jogador.pontos_atributo}",
        160,
        155
    )

    atributos = [
        (
            "vitalidade",
            "Vitalidade",
            f"HP máximo: {jogador.hpmaximo}",
            "+5 HP por ponto"
        ),
        (
            "forca",
            "Força",
            f"Ataque: {jogador.danototal}",
            "+2 ataque por ponto"
        ),
        (
            "defesa",
            "Defesa",
            f"Defesa: {jogador.defesatotal}",
            "+1 defesa por ponto"
        ),
        (
            "agilidade",
            "Agilidade",
            f"Velocidade ATB: {int((jogador.velocidade - 1) * 100)}% bônus",
            "+1,5% por ponto; máximo +30%"
        ),
    ]

    for indice, (chave, nome, valor, descricao) in enumerate(atributos):
        y = 195 + indice * 52
        selecionado = indice == atributo_cursor
        cor = Dourado if selecionado else Branco
        prefixo = "> " if selecionado else "  "
        pontos = jogador.atributos_distribuidos.get(chave, 0)

        desenhar_texto(
            f"{prefixo}{nome}: {pontos}/{jogador.limite_atributo}",
            165,
            y,
            cor
        )

        desenhar_texto(
            valor,
            385,
            y
        )

        desenhar_texto(
            descricao,
            185,
            y + 22,
            CinzaClaro
        )

    desenhar_texto(
        "Setas: escolher | Z/Enter: investir ponto | P/Esc: fechar",
        160,
        445,
        CinzaClaro
    )

    if mensagem_atributos:
        desenhar_texto(
            mensagem_atributos,
            160,
            475,
            Dourado
        )


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

    inventario.sincronizar_do_personagem(jogador)

    if not inventario.adicionar(item_id, 1):
        return

    inventario.sincronizar_para_personagem(jogador)
    jogador.moedas -= preco

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
                    # A batalha já concede XP e moedas.
                    batalha.inimigo.derrotado = True

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

        elif atributos_abertos:
            if evento.type == pygame.KEYDOWN:

                if evento.key in (
                    pygame.K_ESCAPE,
                    pygame.K_p
                ):
                    atributos_abertos = False

                elif evento.key in (
                    pygame.K_UP,
                    pygame.K_w
                ):
                    atributo_cursor = (
                        atributo_cursor - 1
                    ) % 4

                elif evento.key in (
                    pygame.K_DOWN,
                    pygame.K_s
                ):
                    atributo_cursor = (
                        atributo_cursor + 1
                    ) % 4

                elif evento.key in (
                    pygame.K_z,
                    pygame.K_RETURN
                ):
                    nomes_atributos = (
                        "vitalidade",
                        "forca",
                        "defesa",
                        "agilidade"
                    )

                    nome_atributo = nomes_atributos[atributo_cursor]

                    if jogador.distribuir_ponto(nome_atributo):
                        mensagem_atributos = (
                            f"Ponto aplicado em {nome_atributo.capitalize()}!"
                        )
                        salvar_jogo()
                    else:
                        mensagem_atributos = (
                            "Sem pontos disponíveis ou atributo no limite."
                        )

        elif inventario.aberto:
            inventario.tratar_evento(
                evento,
                jogador
            )

        elif evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_ESCAPE:
                rodando = False

            elif evento.key == pygame.K_F5:
                salvar_jogo()

            elif evento.key == pygame.K_c:
                mostrar_coordenadas = not mostrar_coordenadas

            elif evento.key == pygame.K_p:
                atributos_abertos = True
                atributo_cursor = 0
                mensagem_atributos = ""

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
    # ATUALIZAÇÃO DA BATALHA
    # =====================================================

    if batalha is not None:
        batalha.atualizar(dt)

        if batalha.terminada:
            if batalha.vitoria:
                batalha.inimigo.derrotado = True

            elif batalha.derrota:
                jogador.hp = jogador.hpmaximo
                jogador.x, jogador.y = 650, 150

                jogador.colisao.topleft = (
                    round(jogador.x),
                    round(jogador.y)
                )

            batalha = None
            salvar_jogo()

    # =====================================================
    # ATUALIZAÇÃO DO MUNDO
    # =====================================================

    if (
        rodando
        and batalha is None
        and not loja_aberta
        and not inventario.aberto
        and not atributos_abertos
        and npc_dialogo_atual is None
    ):
        retangulos_inimigos = [
            inimigo.colisao
            for inimigo in inimigos
            if not getattr(inimigo, "derrotado", False)
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
            if getattr(inimigo, "derrotado", False):
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
                not getattr(inimigo, "derrotado", False)
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

        if atributos_abertos:
            desenhar_tela_atributos()

        elif loja_aberta:
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
