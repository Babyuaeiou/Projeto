from random import randint
class Personagem:
    def __init__(self, nome):
        self.inventario = {}
        self.nome = nome
        self.cooldown = 1
        self.restante = 0
        self.hpmaximo, self.hp = 20, 20
        self.dano, self.danototal = 5, 5
        self.defesa, self.defesatotal = 3, 3
        self.velocidade = 1
    def esta_pronto(self, tempo):
        if self.restante > 0:
            self.restante -= tempo
            return False
        return True
    def reiniciar_cooldown(self):
        self.restante = self.cooldown
    def calcular_dano(self, alvo):
        ataquetotal = self.dano + #Dano equipamento
        dano = ataquetotal * (ataquetotal / (ataquetotal + alvo.defesa))
        