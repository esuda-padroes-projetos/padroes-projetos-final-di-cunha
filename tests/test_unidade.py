import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validators.validadores import ValidadorCPF, ValidadorCamposObrigatorios
from factories.veiculo_factory import VeiculoFactory
from models.usuario import Usuario

class TestePadroesProjeto(unittest.TestCase):

    def test_cpf_com_tamanho_errado(self):
        validador = ValidadorCPF()
        dados = {'cpf': '123'} 
        
        resultado = validador.handle(dados)
        self.assertEqual(resultado, "Erro: O CPF deve conter exatamente 11 números.")

    def test_cpf_correto_limpeza(self):
        validador = ValidadorCPF()
        dados = {'cpf': '123.456.789-00'} 
        
        validador.handle(dados)
        
        self.assertEqual(dados['cpf'], '12345678900')

    def test_veiculo_factory_sucesso(self):
        veiculo = VeiculoFactory.create("Carro", "Fusca", "ABC-1234", 1)
        
        self.assertEqual(veiculo.modelo, "Fusca")
        self.assertEqual(veiculo.cliente_id, 1)

    def test_veiculo_factory_erro(self):
        with self.assertRaises(ValueError):
            VeiculoFactory.create("Carro", "Fusca", "ABC-1234", None)

    def test_modelo_usuario(self):
        user = Usuario("Diego", "diego@email.com", "12345678900")
        dict_user = user.to_dict()
        
        self.assertEqual(dict_user['nome'], "Diego")
        self.assertEqual(dict_user['email'], "diego@email.com")

if __name__ == '__main__':
    unittest.main()