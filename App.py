from django.shortcuts import render
from flask import Flask, redirect, url_for, render_template, request
import subprocess
from username import scraping
app = Flask(__name__)

@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

@app.route("/buscarPersona")
def buscarPersona():
    return render_template("buscarPersona.html")    

@app.route("/result", methods=["POST", "GET"])
def result():

    if request.method == 'POST':
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        nickname = request.form["nickname"]
        email = request.form["email"]
        city = request.form["city"]

        if nickname:
            resultadoscript = scraping.usernameScrapping(nickname, './username/web_accounts_list.json')
            return render_template("resultadosBusqueda.html", nickname=nickname, resultado = resultadoscript)
        else:
            return render_template("resultadosBusqueda.html", nombre = nombre, nickname = nickname)
    else:
        #quizás añadir 404.html en lugar de redirect
        return redirect("index.html")
        

# @app.route("/<name>")
# def user(name):
#     return f"Hello {name}!"

# @app.route("/admin/")
# def admin():
#     return redirect(url_for("user", name="Admin!"))

if __name__ == "__main__":
    app.run(debug=True)