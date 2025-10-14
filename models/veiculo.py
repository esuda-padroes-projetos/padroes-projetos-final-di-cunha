class Veiculo:
    def __init__(self, tipo, modelo, placa):
        self.tipo = tipo
        self.modelo = modelo
        self.placa = placa

    def to_dict(self):
        return {
            'tipo': self.tipo,
            'modelo': self.modelo,
            'placa': self.placa
        }