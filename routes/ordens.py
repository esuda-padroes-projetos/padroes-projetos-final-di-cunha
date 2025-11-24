from flask import Blueprint, request, jsonify, render_template
from models.ordem_servico import OrdemServico
from database.db import Database

ordens_bp = Blueprint('ordens', __name__)
db = Database.get_instance()

@ordens_bp.route('/dashboard', methods=['GET'])
def view_dashboard():
    return render_template('dashboard.html')

@ordens_bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    todas_ordens = db.get_all('ordens')
    em_aberto = 0
    total_faturado = 0.0

    for ordem in todas_ordens:
        if isinstance(ordem, dict):
            status = ordem.get('status')
            orcamento = ordem.get('orcamento', 0)
        else:
            try:
                status = ordem[3]
                orcamento = ordem[4]
            except IndexError:
                status = ''
                orcamento = 0

        if status == 'Finalizado':
            total_faturado += float(orcamento) if orcamento else 0.0
        else:
            em_aberto += 1

    todos_clientes = db.get_all('usuarios')
    qtd_clientes = len(todos_clientes)

    todos_veiculos = db.get_all('veiculos')
    qtd_veiculos = len(todos_veiculos)

    return jsonify({
        'ordens_em_aberto': em_aberto,
        'total_faturado': total_faturado,
        'total_clientes': qtd_clientes,
        'total_veiculos': qtd_veiculos 
    })

@ordens_bp.route('/', methods=['POST'])
def create_ordem():
    data = request.json
    ordem = OrdemServico(data['cliente_id'], data['veiculo_id'])
    id_criado = db.insert('ordens', ordem.to_dict())
    return jsonify({'id': id_criado, 'message': 'Ordem criada'}), 201

@ordens_bp.route('/', methods=['GET'])
def list_ordens():
    filtro_status = request.args.get('status')
    todas_ordens = db.get_all('ordens')
    
    if filtro_status:
        ordens_filtradas = []
        for o in todas_ordens:
            status = o.get('status') if isinstance(o, dict) else o[3] 
            if status == filtro_status:
                ordens_filtradas.append(o)
        return jsonify(ordens_filtradas)
        
    return jsonify(todas_ordens)

@ordens_bp.route('/<int:id>', methods=['PUT'])
def update_ordem(id):
    data = request.json
    campos_permitidos = ['status', 'orcamento', 'servicos_ids']
    dados_para_atualizar = {}

    for campo in campos_permitidos:
        if campo in data:
            dados_para_atualizar[campo] = data[campo]

    if dados_para_atualizar:
        db.update('ordens', id, dados_para_atualizar)
        return jsonify({'message': 'Ordem atualizada', 'dados': dados_para_atualizar})
    
    return jsonify({'error': 'Nenhum dado válido para atualizar'}), 400