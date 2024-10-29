from functools import wraps
from flask import Blueprint, redirect, render_template, session, url_for

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
    return render_template("metas.html", nomeUsuario=nomeUsuario)


@page.route("/dashboard")
@login_required
def dashboard():
    nomeUsuario = getUsername()
    return render_template("dashboard.html", nomeUsuario=nomeUsuario)


@page.route("/conta")
@login_required
def conta():
    nomeUsuario = getUsername()
    emailUsuario = session.get("user_email")
    return render_template("conta.html", nomeUsuario=nomeUsuario, emailUsuario = emailUsuario)

@page.route("/configuracoes")
@login_required
def configuracoes():
    nomeUsuario = getUsername()
    return render_template("configuracoes.html", nomeUsuario=nomeUsuario)

@page.route("/landing-page")
def landingPage():
    return render_template("landingPage.html")