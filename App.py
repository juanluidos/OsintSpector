import os
from flask import Flask, redirect, url_for, render_template, request
from searchScripts.buscarPersona.username.usernameScraping import usernameScrapping
from searchScripts.buscarPersona.emailPwned.emailScraping import emailBreached, emailBreachedExpanded, emailPasted
app = Flask(__name__)

@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/info")
def info():
    return render_template("info.html")

@app.route("/buscarPersona")
def buscarPersona():
    return render_template("buscarPersona.html")    

@app.route("/result", methods=["POST", "GET"])
async def result():

    if request.method == 'POST':
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        nickname = request.form["nickname"]
        email = request.form["email"]
        city = request.form["city"]

        if nombre:
            if apellidos:
                if nickname:
                    if email:
                        if city:
                            return "nombre apellido nickname email city"
                        else:
                            return "nombre apellido nickname email nocity"
                    elif city:
                        return "nombre apellido nickname noemail city"
                elif email:
                    return "a"
                elif city:
                    return "a"
            elif nickname:
                return "he"
            elif email:
                return "he"
            elif city:
                return "he"
            else:
                return "nombre noapellido nonickname noemail nocity"
        elif apellidos:
            return "he"
            
        elif nickname:
            resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
            return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname)

        elif email:
            resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY"))
            resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY"))
            return render_template("resultadosBusqueda.html", email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail)

        elif city:
            return "he"
        else:
            return redirect("buscarPersona")

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