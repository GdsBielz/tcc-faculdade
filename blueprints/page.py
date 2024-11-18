from functools import wraps
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from libs.sql import sqlExecute, sqlSelectDict

page = Blueprint('page', __name__)

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get('loggedin'):
            return redirect(url_for('auth.login'))  # Redireciona para a página de login
        return func(*args, **kwargs)
    return decorated_function

def getUsername(completo=False):
    nomeUsuario = session['user_nome']
    if nomeUsuario is not None:
        if completo:
            return nomeUsuario
        else:
            partesNome = nomeUsuario.split(" ")

            if len(partesNome) >= 2:
                nomeUsuario = partesNome[0]
                return nomeUsuario
            else:
                # Se não houver sobrenome, retorna o nome completo
                return nomeUsuario
    else:
        return "Usuário"

@page.route("/")
def raiz():
    logado = session.get("loggedin")
    return redirect("/home") if logado else redirect("/landing-page")
        

@page.route("/home")
@login_required
def home():
    nomeUsuario = getUsername()
    return render_template("home.html", nomeUsuario=nomeUsuario)

@page.route("/caixa")
@login_required
def caixa():
    nomeUsuario = getUsername()
    return render_template("caixa.html", nomeUsuario=nomeUsuario)

@page.route("/metas")
@login_required
def metas():
    nomeUsuario = getUsername()
    usuario_id = session.get('user_id')
    metas = sqlSelectDict("SELECT * FROM metas WHERE usuario_id = %s", (usuario_id,))
    
    total_metas = len(metas)
    metas_concluidas = sum(1 for meta in metas if meta['concluida'])
    porcentagem_concluidas = round((metas_concluidas / total_metas * 100), 2) if total_metas > 0 else 0


    return render_template('metas.html', metas=metas, porcentagem=porcentagem_concluidas, nomeUsuario=nomeUsuario)

@page.route('/add-meta', methods=['POST'])
@login_required
def add_meta():
    descricao = request.form.get('descricao')
    usuario_id = session.get('user_id')
    
    if descricao:
        sqlExecute("INSERT INTO metas (descricao, usuario_id, concluida) VALUES (%s, %s, %s)", (descricao, usuario_id, 0))
    return redirect(url_for('page.metas'))

@page.route('/update-meta/<int:id>', methods=['POST'])
@login_required
def update_meta(id):
    usuario_id = session.get('user_id')
    meta = sqlSelectDict("SELECT * FROM metas WHERE idmeta = %s AND usuario_id = %s", (id, usuario_id))
    
    if meta:
        concluida = meta[0]['concluida']
        if concluida == 0:
            concluida = 1
        else:
            concluida = 0
        sqlExecute("UPDATE metas SET concluida = %s WHERE idmeta = %s AND usuario_id = %s", (concluida, id, usuario_id))
    return redirect(url_for('page.metas'))

@page.route('/delete-meta/<int:id>', methods=['POST'])
@login_required
def delete_meta(id):
    usuario_id = session.get('user_id')
    sqlExecute("DELETE FROM metas WHERE idmeta = %s AND usuario_id = %s", (id, usuario_id))
    return redirect(url_for('page.metas'))

@page.route("/dashboard")
@login_required
def dashboard():
    nomeUsuario = getUsername()
    return render_template("dashboard.html", nomeUsuario=nomeUsuario)

@page.route("/insercao")
@login_required
def insercao():
    nomeUsuario = getUsername()
    return render_template("insercao.html", nomeUsuario=nomeUsuario)

@page.route("/api/insercao", methods=["POST"])
@login_required
def api_insercao():
    try:
        # Obtém os dados enviados pelo front-end
        data = request.get_json()

        tipo = data["tipo"]
        km = None
        litros = None
        nome = None
        valor = None

        if tipo == 'corrida':
            valor = data['valor']
            km = data['km']
        elif tipo == 'abastecimento':
            valor = data['valorTotal']
            litros = data['litros']
        elif tipo == 'manutencao':
            valor = data['valor']
            nome = data['nome']
    
        if km is not None:
            #Inserir
            print(km, valor)

        elif litros is not None:
            #Inserir
            print(litros, valor)

        elif nome is not None:
            #Inserir
            print(nome, valor)

        # Retorna uma resposta de sucesso
        return jsonify({"message": "Registro inserido com sucesso!"}), 200
    except Exception as e:
        print("Erro ao processar os dados:", e)
        return jsonify({"error": "Ocorreu um erro ao processar os dados."}), 500
    
@page.route("/conta")
@login_required
def conta():
    nomeUsuario = getUsername(completo=True)
    emailUsuario = session.get("user_email")
    return render_template("conta.html", nomeUsuario=nomeUsuario, emailUsuario = emailUsuario)

@page.route("/configuracoes")
@login_required
def configuracoes():
    nomeUsuario = getUsername(completo=True)
    return render_template("configuracoes.html", nomeUsuario=nomeUsuario)

@page.route("/landing-page")
def landingPage():
    return render_template("landingPage.html")