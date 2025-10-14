from models.veiculo import Veiculo

class VeiculoFactory:
    @staticmethod
    def create(tipo, modelo, placa):
        if tipo.lower() in ['carro', 'moto', 'caminhao']:
            return Veiculo(tipo, modelo, placa)
        else:
            raise ValueError(f"Tipo de veículo inválido: {tipo}. Use 'carro', 'moto' ou 'caminhao'.")