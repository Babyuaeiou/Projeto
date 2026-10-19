
"""Sistema de itens do Hunt Bird."""

class Item:
    def __init__(
        self,
        id,
        nome,
        categoria,
        descricao="",
        valor=0,
        max_pilha=1,
        raridade="Comum",
        efeitos=None,
        atributos=None,
        icone=None,
    ):
        self.id = str(id).strip().lower().replace(" ", "_")
        self.nome = nome
        self.categoria = categoria
        self.descricao = descricao
        self.valor = valor
        self.max_pilha = max(1, int(max_pilha))
        self.raridade = raridade
        self.efeitos = dict(efeitos or {})
        self.atributos = dict(atributos or {})
        self.icone = icone

    def para_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "valor": self.valor,
            "max_pilha": self.max_pilha,
            "raridade": self.raridade,
            "efeitos": self.efeitos.copy(),
            "atributos": self.atributos.copy(),
            "icone": self.icone,
        }


class CatalogoItens:
    CATEGORIAS = {
        "arma",
        "armadura",
        "pocao",
        "consumivel",
        "acessorio",
        "material",
        "chave",
        "missao",
        "outro",
    }

    def __init__(self):
        self.itens = {}

    def criar_item(
        self,
        id,
        nome,
        categoria,
        descricao="",
        valor=0,
        max_pilha=1,
        raridade="Comum",
        efeitos=None,
        atributos=None,
        icone=None,
    ):
        if not isinstance(id, str) or not id.strip():
            raise ValueError("O ID do item não pode estar vazio.")

        id = id.strip().lower().replace(" ", "_")

        if id in self.itens:
            raise ValueError(f"Já existe um item com ID '{id}'.")

        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("O nome do item não pode estar vazio.")

        if categoria not in self.CATEGORIAS:
            raise ValueError(f"Categoria inválida: {categoria}")

        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("O valor deve ser não negativo.")

        if not isinstance(max_pilha, int) or max_pilha < 1:
            raise ValueError("max_pilha deve ser um inteiro positivo.")

        if categoria in {"arma", "armadura", "acessorio", "chave", "missao"}:
            max_pilha = 1

        item = Item(
            id=id,
            nome=nome.strip(),
            categoria=categoria,
            descricao=descricao,
            valor=valor,
            max_pilha=max_pilha,
            raridade=raridade,
            efeitos=efeitos,
            atributos=atributos,
            icone=icone,
        )

        self.itens[id] = item
        return item

    def obter(self, id):
        return self.itens.get(id)

    def remover(self, id):
        return self.itens.pop(id, None) is not None

    def listar(self, categoria=None):
        itens = list(self.itens.values())

        if categoria is not None:
            itens = [
                item for item in itens
                if item.categoria == categoria
            ]

        return itens

    def ids(self):
        return list(self.itens.keys())


catalogo = CatalogoItens()


# =========================================================
# ARMAS
# =========================================================

catalogo.criar_item(
    "punhos",
    "Punhos do Servo",
    "arma",
    "Arma inicial do Servo do Rei Demônio.",
    valor=0,
    atributos={"dano": 0},
)

catalogo.criar_item(
    "espada_enferrujada",
    "Espada Enferrujada",
    "arma",
    "Uma espada velha que aumenta o dano.",
    valor=25,
    atributos={"dano": 3},
)

catalogo.criar_item(
    "espada_ferro",
    "Espada de Ferro",
    "arma",
    "Uma espada resistente.",
    valor=80,
    raridade="Incomum",
    atributos={"dano": 7},
)


# =========================================================
# ARMADURAS
# =========================================================

catalogo.criar_item(
    "sem_armadura",
    "Roupa do Servo",
    "armadura",
    "A roupa inicial do personagem.",
    valor=0,
    atributos={"defesa": 0},
)

catalogo.criar_item(
    "armadura_couro",
    "Armadura de Couro",
    "armadura",
    "Uma proteção leve.",
    valor=30,
    atributos={"defesa": 2},
)


catalogo.criar_item(
    "armadura_ferro",
    "Armadura de Ferro",
    "armadura",
    "Uma proteção resistente.",
    valor=90,
    raridade="Incomum",
    atributos={"defesa": 5},
)


# =========================================================
# POÇÕES E CONSUMÍVEIS DO GDD
# =========================================================

catalogo.criar_item(
    "pocao_pequena",
    "Poção Pequena",
    "pocao",
    "Recupera 15 pontos de HP.",
    valor=15,
    max_pilha=9,
    efeitos={"cura": 15},
)

catalogo.criar_item(
    "pocao_grande",
    "Poção Grande",
    "pocao",
    "Recupera 50 pontos de HP.",
    valor=35,
    max_pilha=9,
    efeitos={"cura": 50},
)

catalogo.criar_item(
    "elixir_servo",
    "Elixir do Servo",
    "pocao",
    "Recupera todo o HP do personagem.",
    valor=75,
    max_pilha=5,
    raridade="Raro",
    efeitos={"cura_total": True},
)

catalogo.criar_item(
    "pedra_afiacao",
    "Pedra de Afiar",
    "consumivel",
    "Aumenta em 30% o dano do próximo ataque.",
    valor=20,
    max_pilha=9,
    efeitos={"buff_proximo_ataque": 0.30},
)
