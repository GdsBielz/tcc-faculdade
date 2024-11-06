from functools import wraps
import hashlib
from flask import Blueprint, abort, jsonify, make_response, redirect, render_template, request, session, url_for

from libs.sql import sqlExecute, sqlSelect, sqlSelectDict

auth = Blueprint('auth', __name__)
pageError = "pageError.html"

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get('loggedin'):
            return redirect(url_for('auth.login'))  # Redireciona para a página de login
        return func(*args, **kwargs)
    return decorated_function

@auth.route("/logout", methods=["GET"])
def logout():
    session['loggedin'] = False
    return redirect(url_for('auth.login'))

@auth.route("/login", methods=["POST","GET"])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get("email")
            user = sqlSelectDict("SELECT * FROM usuarios WHERE email = %s", (email,))

            if user is None or len(user) == 0:
                return make_response(jsonify(message="Usuário ou senha invalidos."), 400)
            else:
                user = user[0]

            password = request.form.get("password")
            hash = hashlib.md5(password.encode())
            if user['senha'] != hash.hexdigest():
                return make_response(jsonify(message="Usuário ou senha invalidos."), 400)
            elif user['senha'] == hash.hexdigest():
                session['loggedin'] = True
                session.permanent = True
                session['user_nome'] = user['nome']
                session['user_email'] = user['email']
                session['user_id'] = user['idusuarios']
                return make_response(jsonify(login=True), 200)
            else:
                return make_response(jsonify(message="Erro interno, contate o suporte."), 400)

        except Exception as ex:
            abort(500, str(ex))

    elif request.method == 'GET':
        logado = session.get("loggedin")
        if logado:
            return redirect("/home")
        else:
            return render_template('login.html')

@auth.route("/cadastro", methods=["POST","GET"])
def cadastro():
    if request.method == 'GET':
        try:
            return render_template('cadastro.html')
        except Exception as ex:
            return make_response(ex, 400)
    elif request.method == 'POST':
        try:
            nome = request.json["nome"]
            email = request.json["email"]
            senha = request.json["password"]

            hash = hashlib.md5(senha.encode())
            senha = hash.hexdigest()

            #VERIFICA SE NÃO TEM USUÁRIO CADASTRADO

            row = sqlSelectDict(""" SELECT email FROM usuarios WHERE email = %s """, (email,))

            #SE VIER RESULTADO, EXISTE USUÁRIO COM ALGUM DADO IGUAL
            if len(row) > 0:
                row = row[0]
                if row['email'] == email:
                    message = "Email já cadastrado."

                return make_response(jsonify(message=message), 400)
                
            else:

                sqlExecute(""" INSERT INTO usuarios (nome, email, senha, dataCadastro) VALUES(%s, %s, %s, NOW())
                        """, (nome, email, senha))
            
            return make_response(jsonify(message="Cadastrado com sucesso!"), 200)
        except Exception as ex:
            return make_response(ex, 400)

@auth.route("/alterar", methods=["PUT"])
@login_required
def alterar_usuario():
    try:
        nome = request.json["nome"]
        email = request.json["email"]
        senha = request.json["password"]
        usuario_id = session.get("user_id")  # Usar o ID do usuário logado na sessão
        
        # Verificar se o usuário existe no banco
        user = sqlSelectDict("SELECT * FROM usuarios WHERE idusuarios = %s", (usuario_id,))
        if not user:
            return make_response(jsonify(message="Usuário não encontrado."), 404)

        # Atualizar nome, email ou senha conforme necessário
        updates = []
        params = []

        if nome:
            updates.append("nome = %s")
            params.append(nome)
        
        if email:
            updates.append("email = %s")
            params.append(email)
        
        if senha:
            hash = hashlib.md5(senha.encode())
            updates.append("senha = %s")
            params.append(hash.hexdigest())
        
        # Verifica se há campos para atualizar
        if updates:
            params.append(usuario_id)
            sqlExecute(f"UPDATE usuarios SET {', '.join(updates)} WHERE idusuarios = %s", tuple(params))

            # Atualizar a sessão se o email ou nome foram alterados
            if nome:
                session["user_nome"] = nome
            if email:
                session["user_email"] = email

            return make_response(jsonify(message="Usuário atualizado com sucesso!"), 200)
        else:
            return make_response(jsonify(message="Nenhum dado para atualizar."), 400)
    
    except Exception as ex:
        return make_response(jsonify(message="Erro interno, contate o suporte."), 500)


@auth.route("/excluir", methods=["DELETE"])
@login_required
def excluir_usuario():
    try:
        senha = request.json["password"]
        usuario_id = session.get("user_id")  # Usar o ID do usuário logado na sessão
        
        # Buscar o usuário no banco
        user = sqlSelectDict("SELECT * FROM usuarios WHERE idusuarios = %s", (usuario_id,))
        if not user:
            return make_response(jsonify(message="Usuário não encontrado."), 404)
        
        # Validar senha
        hash = hashlib.md5(senha.encode())
        if user[0]["senha"] != hash.hexdigest():
            return make_response(jsonify(message="Senha incorreta."), 400)
        
        # Excluir usuário
        sqlExecute("DELETE FROM usuarios WHERE idusuarios = %s", (usuario_id,))
        
        # Limpar sessão e redirecionar para login
        session.clear()
        
        return make_response(jsonify(message="Usuário excluído com sucesso."), 200)
    
    except Exception as ex:
        return make_response(jsonify(message="Erro interno, contate o suporte."), 500)
