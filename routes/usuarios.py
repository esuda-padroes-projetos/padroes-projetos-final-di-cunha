from flask import Blueprint, request, jsonify
from models.usuario import Usuario
from database.db import Database

usuarios_bp = Blueprint('usuarios', __name__)
db = Database.get_instance()

@usuarios_bp.route('/', methods=['POST'])
def create_usuario():
    data = request.json
    usuario = Usuario(data['nome'], data['email'], data['cpf'])
    id = db.insert('usuarios', usuario.to_dict())
    return jsonify({'id': id, 'message': 'Usuário criado'}), 201

@usuarios_bp.route('/', methods=['GET'])
def list_usuarios():
    usuarios = db.get_all('usuarios')
    return jsonify(usuarios)

@usuarios_bp.route('/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    db.update('usuarios', id, data)
    return jsonify({'message': 'Usuário atualizado'})

@usuarios_bp.route('/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    db.delete('usuarios', id)
    return jsonify({'message': 'Usuário deletado'})
