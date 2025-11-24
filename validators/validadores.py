from abc import ABC, abstractmethod
import re

class Handler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request):
        if self._next_handler:
            return self._next_handler.handle(request)
        return None

class ValidadorCamposObrigatorios(Handler):
    def handle(self, request):
        if not request.get('nome') or not request.get('email') or not request.get('cpf'):
            return "Erro: Todos os campos (nome, email, cpf) são obrigatórios."
        return super().handle(request)

class ValidadorCPF(Handler):
    def handle(self, request):
        cpf = str(request.get('cpf'))
        
        cpf_limpo = re.sub(r'\D', '', cpf)

        if len(cpf_limpo) != 11:
            return "Erro: O CPF deve conter exatamente 11 números."
        
        request['cpf'] = cpf_limpo
        
        return super().handle(request)

def montar_chain_usuario():
    validador_campos = ValidadorCamposObrigatorios()
    validador_cpf = ValidadorCPF()
    
    validador_campos.set_next(validador_cpf)
    return validador_campos