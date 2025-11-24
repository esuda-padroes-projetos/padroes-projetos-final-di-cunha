from flask import Blueprint, request, jsonify
from models.usuario import Usuario
from database.db import Database
from validators.validadores import montar_chain_usuario

usuarios_bp = Blueprint('usuarios', __name__)
db = Database.get_instance()

@usuarios_bp.route('/', methods=['POST'])
def criar_usuario():
    data = request.json
    
    validador = montar_chain_usuario()
    erro = validador.handle(data)
    
    if erro:
        return jsonify({'error': erro}), 400

    novo_usuario = Usuario(data['nome'], data['email'], data['cpf'])
    
    db.insert('usuarios', novo_usuario.to_dict())
    
    return jsonify({'message': 'Usuário criado com sucesso!'}), 201

@usuarios_bp.route('/', methods=['GET'])
def listar_usuarios():
    usuarios = db.get_all('usuarios')
    return jsonify(usuarios)