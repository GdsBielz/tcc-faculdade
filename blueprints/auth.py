from flask import Blueprint, render_template

from libs.sql import sqlSelect

auth = Blueprint('auth', __name__)

@auth.route("/login")
def login():
    result = sqlSelect("SELECT * FROM usuarios")
    return render_template("login.html", result=result)

@auth.route("/login", methods=["POST"])
def login():
    email = "gdscheijaewkoaw"
    senha = 1234
    result = sqlSelect("SELECT * FROM usuarios where email = %s", (email,))
    if len(result) > 0:
        if result[3] == senha:
            print("autenticado")
        else:
            return "Usuário ou senha incorretos"
                
    return render_template("login.html", result=result)