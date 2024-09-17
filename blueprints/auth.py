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

@auth.route("/login", methods=["POST","GET"])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get("email")
            user = sqlSelectDict("SELECT * FROM usuarios WHERE email = %s", (email,))

            if user is None or len(user) == 0:
                return render_template(pageError, message="Usuário não existe!")
            else:
                user = user[0]

            password = request.form.get("password")
            hash = hashlib.md5(password.encode())
            if user['senha'] != hash.hexdigest():
                return render_template(pageError, message="Usuário ou senha incorreta!")
            elif user['senha'] == password:
                session['loggedin'] = True
                session.permanent = True
                session['user_nome'] = user['nome']
                session['user_email'] = user['email']
                return redirect('/home')
            else:
                return render_template(pageError, message="Usuário inativo!")

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
            nome = request.form.get("nome")
            email = request.form.get("email")
            senha = request.form.get("senha")

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