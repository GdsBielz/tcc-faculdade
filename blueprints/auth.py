from functools import wraps
from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from libs.sql import sqlSelect, sqlSelectDict

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
            # hash = hashlib.md5(password.encode())
            # if user[3] != hash.hexdigest():
            if user['senha'] != password:
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