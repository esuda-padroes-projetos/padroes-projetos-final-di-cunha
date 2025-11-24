from models.veiculo import Veiculo

class VeiculoFactory:
    @staticmethod
    def create(tipo, modelo, placa, cliente_id):
        if not tipo or not modelo or not placa or not cliente_id:
            raise ValueError("Todos os campos (incluindo dono) são obrigatórios.")
        
        return Veiculo(tipo, modelo, placa, cliente_id)