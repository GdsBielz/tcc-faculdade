from flask import Blueprint, redirect, render_template

page = Blueprint('page', __name__)

@page.route("/")
def raiz():
    return redirect("/login")