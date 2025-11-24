# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from routes.usuarios import usuarios_bp
from routes.veiculos import veiculos_bp
from routes.ordens import ordens_bp
from database.db import Database
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_oficina'

db = Database.get_instance()

app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(veiculos_bp, url_prefix="/api/veiculos")
app.register_blueprint(ordens_bp, url_prefix="/api/ordens")

@app.template_filter('moeda')
def format_moeda(valor):
    try:
        valor = float(valor)
    except:
        valor = 0.0
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/dashboard")
def dashboard():
    return render_template("landing.html")

@app.route("/cadastroUsuario")
def cadastro_usuario():
    return render_template("cadastroUsuario.html")

@app.route("/cadastroVeiculo")
def cadastro_veiculo():
    clientes = db.get_all("usuarios")
    return render_template("cadastroVeiculo.html", clientes=clientes)

@app.route("/novoServico")
def novo_servico():
    return render_template("novoServico.html")

@app.route("/cadastroServico")
def cadastro_servico():
    clientes = db.get_all("usuarios")
    veiculos = db.get_all("veiculos")
    servicos = db.get_all("servicos")
    return render_template("cadastroServico.html", clientes=clientes, veiculos=veiculos, servicos=servicos)

@app.route("/clientes")
def listar_clientes():
    raw_clientes = db.get_all("usuarios")
    lista_clientes = []

    for c in raw_clientes:
        if isinstance(c, dict):
            c_id, nome, email, cpf = c['id'], c['nome'], c['email'], c['cpf']
        else:
            c_id, nome, email, cpf = c[0], c[1], c[2], c[3]

        veiculos_desc = []
        if hasattr(db, 'cursor'):
            veiculos_raw = db.cursor.execute(
                "SELECT modelo, placa FROM veiculos WHERE cliente_id = ?", 
                (c_id,)
            ).fetchall()
            for v in veiculos_raw:
                veiculos_desc.append(f"{v[0]} ({v[1]})")
        
        lista_clientes.append({
            'id': c_id, 'nome': nome, 'email': email, 'cpf': cpf, 'veiculos': veiculos_desc
        })

    return render_template("clientes.html", clientes=lista_clientes)


@app.route("/veiculos")
def listar_veiculos():
    raw_veiculos = db.get_all("veiculos")
    lista_veiculos = []

    for v in raw_veiculos:
        if isinstance(v, dict):
            v_id, tipo, modelo, placa, cliente_id = v['id'], v['tipo'], v['modelo'], v['placa'], v['cliente_id']
        else:
            v_id, tipo, modelo, placa, cliente_id = v[0], v[1], v[2], v[3], v[4]

        dono_nome = "Desconhecido"
        dono = db.get_by_id("usuarios", cliente_id)
        if dono:
            dono_nome = dono['nome'] if isinstance(dono, dict) else dono[1]

        lista_veiculos.append({
            'id': v_id,
            'tipo': tipo,
            'modelo': modelo,
            'placa': placa,
            'dono': dono_nome
        })

    return render_template("veiculos.html", veiculos=lista_veiculos)

@app.route("/veiculo/<int:id>/excluir", methods=["POST"])
def excluir_veiculo(id):
    try:
        if hasattr(db, 'cursor'):
            count = db.cursor.execute("SELECT COUNT(*) FROM ordens WHERE veiculo_id = ?", (id,)).fetchone()[0]
            
            if count > 0:
                flash(f"Não é possível excluir! Este veículo possui {count} Ordem(ns) de Serviço no histórico.", "error")
                return redirect(url_for("listar_veiculos"))

        db.cursor.execute("DELETE FROM veiculos WHERE id = ?", (id,))
        db.conn.commit()
        flash("Veículo excluído com sucesso!", "success")
        
    except Exception as e:
        flash(f"Erro ao excluir: {str(e)}", "error")
    
    return redirect(url_for("listar_veiculos"))

@app.route("/veiculo/<int:id>/editar", methods=["GET"])
def editar_veiculo(id):
    raw_v = db.get_by_id("veiculos", id)
    if not raw_v:
        flash("Veículo não encontrado.", "error")
        return redirect(url_for("listar_veiculos"))

    veiculo = {}
    if isinstance(raw_v, dict):
        veiculo = raw_v
    else:
        veiculo = {'id': raw_v[0], 'tipo': raw_v[1], 'modelo': raw_v[2], 'placa': raw_v[3], 'cliente_id': raw_v[4]}
    
    clientes = db.get_all("usuarios")
    
    return render_template("editarVeiculo.html", veiculo=veiculo, clientes=clientes)

@app.route("/veiculo/<int:id>/editar", methods=["POST"])
def processar_edicao_veiculo(id):
    placa = request.form.get("placa")
    cliente_id = request.form.get("cliente_id")
    
    novo_modelo = request.form.get("modelo") 
    novo_tipo = request.form.get("tipo")

    
    dados_atualizar = {
        "placa": placa,
        "cliente_id": int(cliente_id)
    }

    if novo_tipo: dados_atualizar['tipo'] = novo_tipo
    if novo_modelo: dados_atualizar['modelo'] = novo_modelo

    try:
        db.update("veiculos", id, dados_atualizar)
        flash("Veículo atualizado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao atualizar: {str(e)}", "error")
        
    return redirect(url_for("listar_veiculos"))

@app.route("/cliente/<int:user_id>/editar", methods=["GET"])
def editar_usuario(user_id):
    raw_cliente = db.get_by_id("usuarios", user_id)
    if not raw_cliente:
        flash("Cliente não encontrado.", "error")
        return redirect(url_for("listar_clientes"))

    cliente = raw_cliente if isinstance(raw_cliente, dict) else {
        'id': raw_cliente[0], 'nome': raw_cliente[1], 'email': raw_cliente[2], 'cpf': raw_cliente[3]
    }
    return render_template("editarUsuario.html", cliente=cliente)

@app.route("/ordensDeServico")
def ordens_servico():
    ordens = db.get_all("ordens")
    ordens_com_detalhes = []
    
    for ordem in ordens:
        if isinstance(ordem, dict):
            ordem_id, cliente_id, veiculo_id = ordem['id'], ordem['cliente_id'], ordem['veiculo_id']
            status_os, orcamento = ordem['status'], ordem['orcamento']
        else:
            ordem_id, cliente_id, veiculo_id, status_os, orcamento = ordem[0], ordem[1], ordem[2], ordem[3], ordem[4]

        itens_raw = []
        if hasattr(db, 'cursor'):
            itens_raw = db.cursor.execute(
                "SELECT servico_id, status FROM itens_ordem WHERE ordem_id = ?", (ordem_id,)
            ).fetchall()
        
        lista_servicos = []
        for item in itens_raw:
            sid, status_item = item[0], item[1]
            dados_servico = db.get_by_id("servicos", sid)
            if dados_servico:
                desc = dados_servico['descricao'] if isinstance(dados_servico, dict) else dados_servico[1]
                preco = dados_servico['preco'] if isinstance(dados_servico, dict) else dados_servico[2]
                lista_servicos.append({'id': sid, 'descricao': desc, 'preco': preco, 'status': status_item})
        
        cliente = db.get_by_id("usuarios", cliente_id)
        nome_cliente = (cliente['nome'] if isinstance(cliente, dict) else cliente[1]) if cliente else "Desconhecido"
        
        veiculo = db.get_by_id("veiculos", veiculo_id)
        modelo_veiculo = (veiculo['modelo'] if isinstance(veiculo, dict) else veiculo[2]) if veiculo else "Desconhecido"

        ordens_com_detalhes.append({
            'id': ordem_id, 'cliente_nome': nome_cliente, 'veiculo_modelo': modelo_veiculo,
            'status': status_os, 'orcamento': orcamento, 'itens': lista_servicos
        })
        
    return render_template("ordensDeServico.html", ordens=ordens_com_detalhes)


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
        db.insert("usuarios", usuario.to_dict())
        flash(f"Usuário '{nome}' cadastrado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao cadastrar: {str(e)}", "error")
    return redirect(url_for("landing"))

@app.route("/cliente/<int:user_id>/editar", methods=["POST"])
def processar_edicao_usuario(user_id):
    nome = request.form.get("nome")
    email = request.form.get("email")
    cpf = request.form.get("cpf")
    
    try:
        db.update("usuarios", user_id, {"nome": nome, "email": email, "cpf": cpf})
        flash(f"Cliente '{nome}' atualizado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao atualizar: {str(e)}", "error")
    return redirect(url_for("listar_clientes"))

@app.route("/cadastroVeiculo", methods=["POST"])
def processar_cadastro_veiculo():
    tipo = request.form.get("tipo")
    modelo = request.form.get("modelo")
    placa = request.form.get("placa")
    cliente_id = request.form.get("cliente_id") 
    
    if not all([tipo, modelo, placa, cliente_id]):
        flash("Todos os campos são obrigatórios!", "error")
        return redirect(url_for("cadastro_veiculo"))
    
    from factories.veiculo_factory import VeiculoFactory
    try:
        veiculo = VeiculoFactory.create(tipo, modelo, placa, int(cliente_id))
        db.insert("veiculos", veiculo.to_dict())
        flash(f"Veículo '{modelo}' cadastrado com sucesso!", "success")
    except ValueError as e:
        flash(f"Erro de validação: {str(e)}", "error")
    except Exception as e:
        flash(f"Erro ao cadastrar: {str(e)}", "error")
    return redirect(url_for("landing"))

@app.route("/novoServico", methods=["POST"])
def processar_novo_servico():
    descricao = request.form.get("descricao")
    preco = request.form.get("preco")
    try:
        db.insert("servicos", {"descricao": descricao, "preco": float(preco)})
        flash(f"Serviço '{descricao}' cadastrado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao cadastrar: {str(e)}", "error")
    return redirect(url_for("landing"))

@app.route("/cadastroServico", methods=["POST"])
def processar_cadastro_ordem():
    cliente_id = request.form.get("cliente_id")
    veiculo_id = request.form.get("veiculo_id")
    servicos_selecionados = request.form.getlist("servicos_ids")

    if not all([cliente_id, veiculo_id]) or not servicos_selecionados:
        flash("Preencha todos os campos e selecione serviços!", "error")
        return redirect(url_for("cadastro_servico"))
    
    servicos_ids = [int(sid) for sid in servicos_selecionados]
    orcamento = db.get_servicos_by_ids(servicos_ids)
    
    from models.ordem_servico import OrdemServico
    ordem = OrdemServico(int(cliente_id), int(veiculo_id), servicos_ids, orcamento=orcamento)
    try:
        ordem_id = db.insert("ordens", ordem.to_dict())
        db.insert_itens_ordem(ordem_id, servicos_ids)
        flash(f"Ordem {ordem_id} criada com sucesso! Orçamento: R${orcamento}", "success")
    except Exception as e:
        flash(f"Erro ao criar ordem: {str(e)}", "error")
    return redirect(url_for("ordens_servico"))


@app.route("/api/ordens/dashboard-data", methods=['GET'])
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

    return jsonify({
        'ordens_em_aberto': em_aberto,
        'total_faturado': total_faturado,
        'total_clientes': qtd_clientes
    })

@app.route("/api/ordem/<int:ordem_id>/item/<int:servico_id>/status", methods=["POST"])
def update_item_status(ordem_id, servico_id):
    if not hasattr(db, 'cursor'):
        return jsonify({'success': False, 'error': 'Banco de dados incompatível.'}), 500

    data = request.json
    novo_status_item = data.get('status')
    
    if novo_status_item not in ['Pendente', 'Finalizado']:
        return jsonify({'success': False, 'error': 'Status inválido'}), 400

    try:
        db.cursor.execute(
            "UPDATE itens_ordem SET status = ? WHERE ordem_id = ? AND servico_id = ?",
            (novo_status_item, ordem_id, servico_id)
        )
        db.conn.commit()
        
        pendentes = db.cursor.execute(
            "SELECT count(*) FROM itens_ordem WHERE ordem_id = ? AND status = 'Pendente'",
            (ordem_id,)
        ).fetchone()[0]
        
        msg = ""
        if pendentes == 0:
            db.update("ordens", ordem_id, {'status': 'Finalizado'})
            msg = "Item finalizado. Ordem encerrada!"
        else:
            db.update("ordens", ordem_id, {'status': 'Em andamento'})
            msg = f"Item atualizado para {novo_status_item}."
            
        return jsonify({'success': True, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/ordem/<int:ordem_id>/finalizar-tudo", methods=["POST"])
def finalizar_ordem_inteira(ordem_id):
    if not hasattr(db, 'cursor'):
        return jsonify({'success': False, 'error': 'Banco de dados incompatível.'}), 500

    try:
        db.cursor.execute("UPDATE itens_ordem SET status = 'Finalizado' WHERE ordem_id = ?", (ordem_id,))
        db.update("ordens", ordem_id, {'status': 'Finalizado'})
        db.conn.commit()
        return jsonify({'success': True, 'message': 'Ordem e todos os itens finalizados com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
 
DADOS_VEICULOS = {
    'Carro': {
        'Chevrolet': ['Onix', 'Tracker', 'Cruze', 'S10', 'Spin'],
        'Fiat': ['Mobi', 'Argo', 'Cronos', 'Pulse', 'Toro', 'Strada', 'Fiorino'],
        'Ford': ['Ka', 'EcoSport', 'Ranger', 'Mustang', 'Territory'],
        'Hyundai': ['HB20', 'HB20S', 'Creta', 'Tucson'],
        'Toyota': ['Corolla', 'Hilux', 'Yaris', 'Corolla Cross', 'SW4'],
        'Volkswagen': ['Gol', 'Polo', 'Virtus', 'Nivus', 'T-Cross', 'Amarok'],
        'Honda': ['Civic', 'HR-V', 'City', 'Fit', 'WR-V'],
        'Jeep': ['Renegade', 'Compass', 'Commander']
    },
    'Moto': {
        'Honda': ['CG 160', 'Biz', 'NXR 160 Bros', 'CB 500', 'XRE 300'],
        'Yamaha': ['YBR 150', 'Fazer 250', 'NMAX', 'Lander', 'MT-03'],
        'BMW': ['G 310 GS', 'F 850 GS', 'R 1250 GS'],
        'Kawasaki': ['Ninja 400', 'Z400', 'Versys']
    },
    'Caminhão': {
        'Mercedes-Benz': ['Accelo', 'Atego', 'Actros'],
        'Volvo': ['FH 540', 'VM', 'FM'],
        'Scania': ['R 450', 'R 540', 'P 360'],
        'Volkswagen': ['Delivery', 'Constellation', 'Meteor']
    }
}

@app.route("/api/dados-veiculos", methods=['GET'])
def get_dados_veiculos():
    tipo = request.args.get('tipo')
    marca = request.args.get('marca')

    if tipo and not marca:
        if tipo in DADOS_VEICULOS:
            return jsonify(list(DADOS_VEICULOS[tipo].keys()))
        return jsonify([])

    if tipo and marca:
        if tipo in DADOS_VEICULOS and marca in DADOS_VEICULOS[tipo]:
            return jsonify(DADOS_VEICULOS[tipo][marca])
        return jsonify([])

    return jsonify([])

if __name__ == "__main__":
    app.run(debug=True, port=5001)