import os
from flask import Flask, redirect, url_for, render_template, request
from searchScripts.buscarPersona.phone.phoneSearch import phonebooksearch
from searchScripts.buscarPersona.username.usernameScraping import usernameScrapping
from searchScripts.buscarPersona.emailPwned.emailScraping import emailBreached, emailBreachedExpanded, emailPasted, pruebaIntel
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
def result():

    if request.method == 'POST':
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        nickname = request.form["nickname"]
        email = request.form["email"]
        city = request.form["city"]
        phone = request.form["phone"]

        if nombre:
            if apellidos:
                if nickname:
                    if email:
                        if city:
                            return "nombre apellido nickname email city"
                        else:
                            return "nombre apellido nickname email nocity"
                    else:
                        if city:
                            return "nombre apellido nickname noemail city"
                        else:
                            return "nombre apellido nickname noemail nocity"
                else:
                    if email:
                        if city:
                            return "nombre apellido nonickname email city"
                        else:
                            return "nombre apellido nonickname email nocity"
                    else:
                        if city:
                            return "nombre apellido nonickname noemail city"
                        else:
                            return "nombre apellido nonickname noemail nocity"
            else:
                if nickname:
                    if email:
                        if city:
                            return "nombre noapellido nickname email city"
                        else:
                            return "nombre noapellido nickname email nocity"
                    else:
                        if city:
                            return "nombre noapellido nickname noemail city"
                        else:
                            return "nombre noapellido nickname noemail nocity"
                else:
                    if email:
                        if city:
                            return "nombre noapellido nonickname email city"
                        else:
                            return "nombre noapellido nonickname email nocity"
                    else:
                        if city:
                            return "nombre noapellido nonickname noemail city"
                        else:
                            return "nombre noapellido nonickname noemail nocity"
        else:
            if apellidos:
                if nickname:
                    if email:
                        if city:
                            return "nonombre apellido nickname email city"
                        else:
                            return "nonombre apellido nickname email nocity"
                    else:
                        if city:
                            return "nonombre apellido nickname noemail city"
                        else:
                            return "nonombre apellido nickname noemail nocity"
                else:
                    if email:
                        if city:
                            return "nonombre apellido nonickname email city"
                        else:
                            return "nonombre apellido nonickname email nocity"
                    else:
                        if city:
                            return "nonombre apellido nonickname noemail city"
                        else:
                            return "nonombre apellido nonickname noemail nocity"
            else:
                if nickname:
                    if email:
                        if city:
                            resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                            resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                            resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                            resultadosIntelx = pruebaIntel(email)
                            return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                            #"nonombre noapellido nickname email city" TODO FALTA CITY
                        else:
                            resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                            resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                            resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                            resultadosIntelx = pruebaIntel(email)
                            return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                            #"nonombre noapellido nickname email nocity"
                    else:
                        if city:
                            return "nonombre noapellido nickname noemail city"
                        else:
                            resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                            return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname) 
                            #nonombre noapellido nickname noemail nocity
                else:
                    if email:
                        if city:
                            return "nonombre noapellido nonickname email city"
                        else:
                            resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                            resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                            resultadosIntelx = pruebaIntel(email)
                            return render_template("resultadosBusqueda.html",email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                            #"nonombre noapellido nonickname email nocity"
                    else:
                        if city:
                            return "nonombre noapellido nonickname noemail city"
                        else:
                            resultadosIntelx = phonebooksearch(phone)
                            return render_template("resultadosBusqueda.html",phone=phone, resultadosIntelx = resultadosIntelx)
                            #return redirect('buscarPersona') TODO
                            #"nonombre noapellido nonickname noemail nocity"

            

        # elif nickname:
        #     resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
        #     return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname)

        # elif email:
        #     resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
        #     resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
        #     return render_template("resultadosBusqueda.html", email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail)

        # elif city:
        #     return "he"
        # else:
        #     return redirect("buscarPersona")

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