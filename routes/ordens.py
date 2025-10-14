from flask import Blueprint, request, jsonify
from models.ordem_servico import OrdemServico
from database.db import Database

ordens_bp = Blueprint('ordens', __name__)
db = Database.get_instance()

@ordens_bp.route('/', methods=['POST'])
def create_ordem():
    data = request.json
    ordem = OrdemServico(data['cliente_id'], data['veiculo_id'])
    id = db.insert('ordens', ordem.to_dict())
    return jsonify({'id': id, 'message': 'Ordem criada'}), 201

@ordens_bp.route('/', methods=['GET'])
def list_ordens():
    filtro = request.args.get('status', None)
    if filtro:
        cursor = db.conn.cursor() if hasattr(db, 'conn') else None
        if cursor:
            cursor.execute("SELECT * FROM ordens WHERE status = ?", (filtro,))
            ordens = cursor.fetchall()
        else:
            ordens = [o for o in db.get_all('ordens') if o[3] == filtro] 
    else:
        ordens = db.get_all('ordens')
    return jsonify(ordens)

@ordens_bp.route('/<int:id>/finalizar', methods=['POST'])
def finalizar_ordem(id):
    db.update('ordens', id, {'status': 'Finalizado'})
    return jsonify({'message': 'Ordem finalizada'})

@ordens_bp.route('/<int:id>', methods=['PUT'])
def update_ordem(id):
    data = request.json
    db.update('ordens',)