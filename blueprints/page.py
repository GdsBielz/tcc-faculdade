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
    if logado:
        return redirect("/home")
    else:
        return redirect("/login")

@page.route("/home")
@login_required
def home():
    return render_template("home.html")