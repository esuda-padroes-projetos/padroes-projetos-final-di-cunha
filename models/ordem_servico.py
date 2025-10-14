class OrdemServico:
    def __init__(self, cliente_id, veiculo_id, servicos_ids=None, status='Em andamento', orcamento=0.0):
        self.cliente_id = cliente_id
        self.veiculo_id = veiculo_id
        self.servicos_ids = servicos_ids or []  # Lista de IDs de serviços
        self.status = status
        self.orcamento = orcamento

    def to_dict(self):
        return {
            'cliente_id': self.cliente_id,
            'veiculo_id': self.veiculo_id,
            'status': self.status,
            'orcamento': self.orcamento
        }