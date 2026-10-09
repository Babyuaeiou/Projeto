
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
        self.id = id
        self.nome = nome
        self.categoria = categoria
        self.descricao = descricao
        self.valor = valor
        self.max_pilha = max_pilha
        self.raridade = raridade
        self.efeitos = efeitos or {}
        self.atributos = atributos or {}
        self.icone = icone

    def para_dict(self):
        """Converte o item para um dicionario."""
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
        """Cria e cadastra um item."""

        if not isinstance(id, str) or not id.strip():
            raise ValueError("O ID do item nao pode estar vazio.")

        id = id.strip().lower().replace(" ", "_")

        if id in self.itens:
            raise ValueError(f"Ja existe um item com ID '{id}'.")

        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("O nome do item nao pode estar vazio.")

        if categoria not in self.CATEGORIAS:
            raise ValueError(
                f"Categoria invalida: {categoria}. "
                f"Categorias disponiveis: {', '.join(sorted(self.CATEGORIAS))}"
            )

        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("O valor deve ser um numero nao negativo.")

        if not isinstance(max_pilha, int) or max_pilha < 1:
            raise ValueError("max_pilha deve ser um inteiro positivo.")

        if categoria in {
            "arma",
            "armadura",
            "acessorio",
            "chave",
            "missao",
        }:
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
        """Retorna um item pelo ID ou None."""
        return self.itens.get(id)

    def remover(self, id):
        """Remove um item do catalogo."""
        return self.itens.pop(id, None) is not None

    def listar(self, categoria=None):
        """Lista todos os itens ou filtra por categoria."""
        itens = list(self.itens.values())

        if categoria is not None:
            itens = [
                item for item in itens
                if item.categoria == categoria
            ]

        return itens

    def ids(self):
        """Retorna os IDs cadastrados."""
        return list(self.itens.keys())


# Catalogo inicialmente vazio.
catalogo = CatalogoItens()
