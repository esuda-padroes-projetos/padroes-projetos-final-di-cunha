class Servico:
    def __init__(self, descricao, preco):
        self.descricao = descricao
        self.preco = preco

    def to_dict(self):
        return {
            'descricao': self.descricao,
            'preco': self.preco
        }