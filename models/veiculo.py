class Veiculo:
    def __init__(self, tipo, modelo, placa, cliente_id):
        self.tipo = tipo
        self.modelo = modelo
        self.placa = placa
        self.cliente_id = cliente_id

    def to_dict(self):
        return {
            'tipo': self.tipo,
            'modelo': self.modelo,
            'placa': self.placa,
            'cliente_id': self.cliente_id
        }