#Imports
from werkzeug.exceptions import HTTPException
from flask import Flask, redirect, render_template, request
from flask_session import Session
from flask_compress import Compress


#Iniciando o flask
app = Flask(__name__, static_url_path='', static_folder='static')
Session(app)
Compress(app)

#Rotas para tratativa de erros
@app.errorhandler(Exception)
def handle_exception(e):
    path = request.path
    message = "Erro interno na aplicação"
    if isinstance(e, HTTPException):
        message = f"{e.code} {path}: {e.name} {e.description}"
        if e.code != 404:
            print(message, "APP")
    else:
        message = str(e)

    return render_template('pageError.html', message=message)

@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')

#Para iniciar quando executar o arquivo
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
