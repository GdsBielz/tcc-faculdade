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

@page.route("/")
def raiz():
    logado = session.get("loggedin")
    return redirect("/home") if logado else redirect("/landing-page")
        

@page.route("/home")
@login_required
def home():
    return render_template("home.html")

@page.route("/caixa")
@login_required
def caixa():
    return render_template("caixa.html")

@page.route("/metas")
@login_required
def metas():
    return render_template("metas.html")


@page.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@page.route("/conta")
@login_required
def conta():
    return render_template("conta.html")

@page.route("/configuracoes")
@login_required
def configuracoes():
    return render_template("configuracoes.html")

@page.route("/landing-page")
def landingPage():
    return render_template("landingPage.html")