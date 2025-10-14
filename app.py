# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from routes.usuarios import usuarios_bp
from routes.veiculos import veiculos_bp
from routes.ordens import ordens_bp
from database.db import Database
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_oficina'

# Inicializa o banco
db = Database.get_instance()

# Registra as rotas API (para uso futuro com JS/fetch)
app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(veiculos_bp, url_prefix="/api/veiculos")
app.register_blueprint(ordens_bp, url_prefix="/api/ordens")

# Rotas para páginas HTML
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/cadastroUsuario")
def cadastro_usuario():
    return render_template("cadastroUsuario.html")

@app.route("/cadastroVeiculo")
def cadastro_veiculo():
    return render_template("cadastroVeiculo.html")

@app.route("/cadastroServico")
def cadastro_servico():
    clientes = db.get_all("usuarios")
    veiculos = db.get_all("veiculos")
    servicos = db.get_all("servicos")
    
    # Debug no terminal para verificar se dados estão chegando
    print(f"Debug - Clientes encontrados: {len(clientes)}")
    print(f"Debug - Veículos encontrados: {len(veiculos)}")
    print(f"Debug - Serviços encontrados: {len(servicos)}")
    if servicos:
        print(f"Debug - Serviços: {[s[1] for s in servicos]}")  # Mostra descrições
    
    return render_template("cadastroServico.html", clientes=clientes, veiculos=veiculos, servicos=servicos)

@app.route("/ordensDeServico")
def ordens_servico():
    ordens = db.get_all("ordens")
    # Para cada ordem, busca itens e serviços associados
    ordens_com_detalhes = []
    for ordem in ordens:
        ordem_id = ordem[0]
        itens = db.cursor.execute("SELECT servico_id FROM itens_ordem WHERE ordem_id = ?", (ordem_id,)).fetchall()
        servicos_ids = [item[0] for item in itens]
        servicos_desc = []
        orcamento = ordem[4]  # Coluna orcamento (índice 4)
        for sid in servicos_ids:
            servico = db.get_by_id("servicos", sid)
            if servico:
                servicos_desc.append(f"{servico[1]} (R${servico[2]})")
        ordens_com_detalhes.append({
            'id': ordem_id,
            'cliente_id': ordem[1],
            'veiculo_id': ordem[2],
            'status': ordem[3],
            'orcamento': orcamento,
            'servicos': ', '.join(servicos_desc) if servicos_desc else 'Nenhum'
        })
    return render_template("ordensDeServico.html", ordens=ordens_com_detalhes)

# Rota POST para cadastro de usuário
@app.route("/cadastroUsuario", methods=["POST"])
def processar_cadastro_usuario():
    nome = request.form.get("nome")
    email = request.form.get("email")
    cpf = request.form.get("cpf")
    
    if not all([nome, email, cpf]):
        flash("Todos os campos são obrigatórios!", "error")
        return redirect(url_for("cadastro_usuario"))
    
    from models.usuario import Usuario
    usuario = Usuario(nome, email, cpf)
    try:
        user_id = db.insert("usuarios", usuario.to_dict())
        flash(f"Usuário '{nome}' cadastrado com ID {user_id}!", "success")
    except Exception as e:
        flash(f"Erro ao cadastrar: {str(e)}", "error")
    
    return redirect(url_for("landing"))

# Rota POST para cadastro de veículo
@app.route("/cadastroVeiculo", methods=["POST"])
def processar_cadastro_veiculo():
    tipo = request.form.get("tipo")
    modelo = request.form.get("modelo")
    placa = request.form.get("placa")
    
    if not all([tipo, modelo, placa]):
        flash("Todos os campos são obrigatórios!", "error")
        return redirect(url_for("cadastro_veiculo"))
    
    from factories.veiculo_factory import VeiculoFactory
    try:
        veiculo = VeiculoFactory.create(tipo, modelo, placa)
        veiculo_id = db.insert("veiculos", veiculo.to_dict())
        flash(f"Veículo '{modelo}' cadastrado com ID {veiculo_id}!", "success")
    except ValueError as e:
        flash(f"Erro: {str(e)}", "error")
    except Exception as e:
        flash(f"Erro ao cadastrar: {str(e)}", "error")
    
    return redirect(url_for("landing"))

# Rota POST para ordem de serviço (com serviços e orçamento)
@app.route("/cadastroServico", methods=["POST"])
def processar_cadastro_ordem():
    cliente_id = request.form.get("cliente_id")
    veiculo_id = request.form.get("veiculo_id")
    servicos_selecionados = request.form.getlist("servicos_ids")  # Múltiplos IDs

    if not all([cliente_id, veiculo_id]):
        flash("Selecione cliente e veículo!", "error")
        return redirect(url_for("cadastro_servico"))
    
    if not servicos_selecionados:
        flash("Selecione pelo menos um serviço!", "error")
        return redirect(url_for("cadastro_servico"))
    
    # Converte para int
    cliente_id = int(cliente_id)
    veiculo_id = int(veiculo_id)
    servicos_ids = [int(sid) for sid in servicos_selecionados]
    
    # Calcula orçamento
    orcamento = db.get_servicos_by_ids(servicos_ids)
    print(f"Orçamento calculado: R${orcamento}")  # Debug
    
    from models.ordem_servico import OrdemServico
    ordem = OrdemServico(cliente_id, veiculo_id, servicos_ids, orcamento=orcamento)
    try:
        ordem_id = db.insert("ordens", ordem.to_dict())
        # Insere itens associados
        db.insert_itens_ordem(ordem_id, servicos_ids)
        flash(f"Ordem de serviço criada com ID {ordem_id} e orçamento R${orcamento}!", "success")
    except Exception as e:
        flash(f"Erro ao criar ordem: {str(e)}", "error")
        print(f"Erro detalhado: {e}")  # Debug
    
    return redirect(url_for("ordens_servico"))

# Rota para login simples
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if username and password:
        return redirect(url_for("landing"))
    flash("Login inválido!", "error")
    return redirect(url_for("index"))


# Rota para finalizar ordem de serviço (atualiza status)
@app.route("/finalizar_ordem/<int:ordem_id>", methods=["POST"])
def finalizar_ordem(ordem_id):
    try:
        # Busca a ordem atual para verificar status
        ordem_atual = db.get_by_id("ordens", ordem_id)
        if not ordem_atual:
            flash("Ordem não encontrada!", "error")
            return redirect(url_for("ordens_servico"))
        
        status_atual = ordem_atual[3]  # Índice do status
        if status_atual == "Finalizado":
            flash("Esta ordem já está finalizada!", "error")
            return redirect(url_for("ordens_servico"))
        
        # Atualiza status via Adapter
        db.update("ordens", ordem_id, {'status': 'Finalizado'})
        flash(f"Ordem {ordem_id} finalizada com sucesso! Orçamento total: R${ordem_atual[4]:.2f}", "success")
        print(f"Debug: Ordem {ordem_id} atualizada para 'Finalizado'.")
    except Exception as e:
        flash(f"Erro ao finalizar ordem: {str(e)}", "error")
        print(f"Erro detalhado: {e}")
    
    return redirect(url_for("ordens_servico"))


if __name__ == "__main__":
    app.run(debug=True)