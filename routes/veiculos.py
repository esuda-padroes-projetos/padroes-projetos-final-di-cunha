from flask import Blueprint, request, jsonify
from factories.veiculo_factory import VeiculoFactory
from database.db import Database

veiculos_bp = Blueprint('veiculos', __name__)
db = Database.get_instance()

@veiculos_bp.route('/', methods=['POST'])
def create_veiculo():
    data = request.json
    try:
        veiculo = VeiculoFactory.create(data['tipo'], data['modelo'], data['placa'])
        id = db.insert('veiculos', veiculo.to_dict())
        return jsonify({'id': id, 'message': 'Veículo criado'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@veiculos_bp.route('/', methods=['GET'])
def list_veiculos():
    veiculos = db.get_all('veiculos')
    return jsonify(veiculos)

@veiculos_bp.route('/<int:id>', methods=['PUT'])
def update_veiculo(id):
    data = request.json
    db.update('veiculos', id, data)
    return jsonify({'message': 'Veículo atualizado'})

@veiculos_bp.route('/<int:id>', methods=['DELETE'])
def delete_veiculo(id):
    db.delete('veiculos', id)
    return jsonify({'message': 'Veículo deletado'})