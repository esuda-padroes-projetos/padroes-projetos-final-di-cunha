class Usuario:
    def __init__(self, nome, email, cpf):
        self.nome = nome
        self.email = email
        self.cpf = cpf

    def to_dict(self):
        return {
            'nome': self.nome,
            'email': self.email,
            'cpf': self.cpf
        }