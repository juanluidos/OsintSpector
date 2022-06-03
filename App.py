import asyncio
import os
import sys
from flask import Flask, redirect, url_for, render_template, request
from searchScripts.buscarPersona.darknet.darkScraping import AhmiaScraping
from searchScripts.buscarPersona.phone.phoneSearch import phonebooksearch
from searchScripts.buscarPersona.username.usernameScraping import usernameScrapping
from searchScripts.buscarPersona.email.emailScraping import emailBreachedExpanded, emailPasted, pruebaIntel
from searchScripts.buscarPersona.email.emailPhoneIHBP import HIBPScraping

App = Flask(__name__)

#Error que tiene la libreria de async_io para las versiones de python por debajo de la 3.9
if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
@App.route("/")
@App.route("/index.html")
def home():
    return render_template("index.html")

@App.route("/about")
def about():
    return render_template("about.html")

@App.route("/info")
def info():
    return render_template("info.html")

@App.route("/buscarPerson")
def buscarPersona():
    return render_template("buscarPersona.html")    

@App.route("/result", methods=["POST", "GET"])
def result():

    if request.method == 'POST':
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        nickname = request.form["nickname"]
        email = request.form["email"]
        city = request.form["city"]
        phone = request.form["area_code"] + request.form["phone"]
        darknet = request.form["darknet"]
        baseUrlAhmia = "https://ahmia.fi/search/"


        if darknet:
            if phone:
                if nombre:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    return "nombre apellido nickname email city darknet phone"
                                else:
                                    return "nombre apellido nickname email nocity darknet phone"
                            else:
                                if city:
                                    return "nombre apellido nickname noemail city darknet phone"
                                else:
                                    return "nombre apellido nickname noemail nocity darknet phone"
                        else:
                            if email:
                                if city:
                                    return "nombre apellido nonickname email city darknet phone"
                                else:
                                    return "nombre apellido nonickname email nocity darknet phone"
                            else:
                                if city:
                                    return "nombre apellido nonickname noemail city darknet phone"
                                else:
                                    return "nombre apellido nonickname noemail nocity darknet phone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    return "nombre noapellido nickname email city darknet phone"
                                else:
                                    return "nombre noapellido nickname email nocity darknet phone"
                            else:
                                if city:
                                    return "nombre noapellido nickname noemail city darknet phone"
                                else:
                                    return "nombre noapellido nickname noemail nocity darknet phone"
                        else:
                            if email:
                                if city:
                                    return "nombre noapellido nonickname email city darknet phone"
                                else:
                                    return "nombre noapellido nonickname email nocity darknet phone"
                            else:
                                if city:
                                    return "nombre noapellido nonickname noemail city darknet phone"
                                else:
                                    return "nombre noapellido nonickname noemail nocity darknet phone"
                else:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    return "nonombre apellido nickname email city darknet phone"
                                else:
                                    return "nonombre apellido nickname email nocity darknet phone"
                            else:
                                if city:
                                    return "nonombre apellido nickname noemail city darknet phone"
                                else:
                                    return "nonombre apellido nickname noemail nocity darknet phone"
                        else:
                            if email:
                                if city:
                                    return "nonombre apellido nonickname email city darknet phone"
                                else:
                                    return "nonombre apellido nonickname email nocity darknet phone"
                            else:
                                if city:
                                    return "nonombre apellido nonickname noemail city darknet phone"
                                else:
                                    return "nonombre apellido nonickname noemail nocity darknet phone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nickname email city darknet phone" TODO FALTA CITY
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nickname email nocity darknet phone"
                            else:
                                if city:
                                    return "nonombre noapellido nickname noemail city darknet phone"
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname) 
                                    #nonombre noapellido nickname noemail nocity darknet phone
                        else:
                            if email:
                                if city:
                                    return "nonombre noapellido nonickname email city darknet phone"
                                else:
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html",email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nonickname email nocity darknet phone"
                            else:
                                if city:
                                    return "nonombre noapellido nonickname noemail city"
                                else:
                                    resultadosIntelx = phonebooksearch(phone)
                                    return render_template("resultadosBusqueda.html",phone=phone, resultadosIntelx = resultadosIntelx)
                                    #return redirect('buscarPersona') TODO
                                    #"nonombre noapellido nonickname noemail nocity darknet phone"
            else:
                if nombre:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    return "nombre apellido nickname email city darknet nophone"
                                else:
                                    return "nombre apellido nickname email nocity darknet nophone"
                            else:
                                if city:
                                    return "nombre apellido nickname noemail city darknet nophone"
                                else:
                                    return "nombre apellido nickname noemail nocity darknet nophone"
                        else:
                            if email:
                                if city:
                                    return "nombre apellido nonickname email city darknet nophone"
                                else:
                                    return "nombre apellido nonickname email nocity darknet nophone"
                            else:
                                if city:
                                    return "nombre apellido nonickname noemail city darknet nophone"
                                else:
                                    hp = AhmiaScraping()
                                    uriUrlAhmia = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    resultadoDarknet = hp.parseHTML(baseUrlAhmia+uriUrlAhmia)
                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadoDarknet = resultadoDarknet, darknet = darknet)

                                    #return "nombre apellido nonickname noemail nocity darknet nophone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    return "nombre noapellido nickname email city darknet nophone"
                                else:
                                    return "nombre noapellido nickname email nocity darknet nophone"
                            else:
                                if city:
                                    return "nombre noapellido nickname noemail city darknet nophone"
                                else:
                                    return "nombre noapellido nickname noemail nocity darknet nophone"
                        else:
                            if email:
                                if city:
                                    return "nombre noapellido nonickname email city darknet nophone"
                                else:
                                    return "nombre noapellido nonickname email nocity darknet nophone"
                            else:
                                if city:
                                    return "nombre noapellido nonickname noemail city darknet nophone"
                                else:
                                    return "nombre noapellido nonickname noemail nocity darknet nophone"
                else:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    return "nonombre apellido nickname email city darknet nophone"
                                else:
                                    return "nonombre apellido nickname email nocity darknet nophone"
                            else:
                                if city:
                                    return "nonombre apellido nickname noemail city darknet nophone"
                                else:
                                    return "nonombre apellido nickname noemail nocity darknet nophone"
                        else:
                            if email:
                                if city:
                                    return "nonombre apellido nonickname email city darknet nophone"
                                else:
                                    return "nonombre apellido nonickname email nocity darknet nophone"
                            else:
                                if city:
                                    return "nonombre apellido nonickname noemail city darknet nophone"
                                else:
                                    return "nonombre apellido nonickname noemail nocity darknet nophone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nickname email city darknet nophone" TODO FALTA CITY
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nickname email nocity darknet nophone"
                            else:
                                if city:
                                    return "nonombre noapellido nickname noemail city"
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname) 
                                    #nonombre noapellido nickname noemail nocity darknet nophone
                        else:
                            if email:
                                if city:
                                    return "nonombre noapellido nonickname email city"
                                else:
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html",email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nonickname email nocity darknet nophone"
                            else:
                                if city:
                                    return "nonombre noapellido nonickname noemail city"
                                else:
                                    # resultadosIntelx = phonebooksearch(phone)
                                    # return render_template("resultadosBusqueda.html",phone=phone, resultadosIntelx = resultadosIntelx)
                                    return redirect('buscarPersona')
                                    #"nonombre noapellido nonickname noemail nocity darknet nophone"

        else:
            print(darknet)
            if phone:
                if nombre:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    return "nombre apellido nickname email city nodarknet phone"
                                else:
                                    return "nombre apellido nickname email nocity nodarknet phone"
                            else:
                                if city:
                                    return "nombre apellido nickname noemail city nodarknet phone"
                                else:
                                    return "nombre apellido nickname noemail nocity nodarknet phone"
                        else:
                            if email:
                                if city:
                                    return "nombre apellido nonickname email city nodarknet phone"
                                else:
                                    return "nombre apellido nonickname email nocity nodarknet phone"
                            else:
                                if city:
                                    return "nombre apellido nonickname noemail city nodarknet phone"
                                else:
                                    return "nombre apellido nonickname noemail nocity nodarknet phone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    return "nombre noapellido nickname email city nodarknet phone"
                                else:
                                    return "nombre noapellido nickname email nocity nodarknet phone"
                            else:
                                if city:
                                    return "nombre noapellido nickname noemail city nodarknet phone"
                                else:
                                    return "nombre noapellido nickname noemail nocity nodarknet phone"
                        else:
                            if email:
                                if city:
                                    return "nombre noapellido nonickname email city nodarknet phone"
                                else:
                                    return "nombre noapellido nonickname email nocity nodarknet phone"
                            else:
                                if city:
                                    return "nombre noapellido nonickname noemail city nodarknet phone"
                                else:
                                    return "nombre noapellido nonickname noemail nocity nodarknet phone"
                else:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    return "nonombre apellido nickname email city nodarknet phone"
                                else:
                                    return "nonombre apellido nickname email nocity nodarknet phone"
                            else:
                                if city:
                                    return "nonombre apellido nickname noemail city nodarknet phone"
                                else:
                                    return "nonombre apellido nickname noemail nocity nodarknet phone"
                        else:
                            if email:
                                if city:
                                    return "nonombre apellido nonickname email city nodarknet phone"
                                else:
                                    return "nonombre apellido nonickname email nocity nodarknet phone"
                            else:
                                if city:
                                    return "nonombre apellido nonickname noemail city nodarknet phone"
                                else:
                                    return "nonombre apellido nonickname noemail nocity nodarknet phone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nickname email city nodarknet phone" TODO FALTA CITY
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    hp = HIBPScraping()
                                    resultadosPwnedPhone = asyncio.run(hp.parseHTML(phone))
                                    resultadosPwnedEmail = asyncio.run(hp.parseHTML(email))
                                    return render_template("resultadosBusqueda.html",nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosPwnedEmail = resultadosPwnedEmail, phone = phone,  resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nickname email nocity nodarknet phone"
                            else:
                                if city:
                                    return "nonombre noapellido nickname noemail city"
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname) 
                                    #nonombre noapellido nickname noemail nocity nodarknet phone
                        else:
                            if email:
                                if city:
                                    return "nonombre noapellido nonickname email city"
                                else:
                                    hp = HIBPScraping()
                                    resultadosPwnedPhone = asyncio.run(hp.parseHTML(phone))
                                    resultadosPwnedEmail = asyncio.run(hp.parseHTML(email))
                                    return render_template("resultadosBusqueda.html",email=email, resultadosPwnedEmail = resultadosPwnedEmail, phone = phone,  resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nonickname email nocity nodarknet phone"
                            else:
                                if city:
                                    return "nonombre noapellido nonickname noemail city"
                                else:
                                    resultadosIntelx = phonebooksearch(phone)
                                    return render_template("resultadosBusqueda.html",phone=phone, resultadosIntelx = resultadosIntelx)
                                    #return redirect('buscarPersona') TODO
                                    #"nonombre noapellido nonickname noemail nocity nodarknet phone"
            else:
                if nombre:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    return "nombre apellido nickname email city nodarknet nophone"
                                else:
                                    return "nombre apellido nickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    return "nombre apellido nickname noemail city nodarknet nophone"
                                else:
                                    return "nombre apellido nickname noemail nocity nodarknet nophone"
                        else:
                            if email:
                                if city:
                                    return "nombre apellido nonickname email city nodarknet nophone"
                                else:
                                    return "nombre apellido nonickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    return "nombre apellido nonickname noemail city nodarknet nophone"
                                else:
                                    return "nombre apellido nonickname noemail nocity nodarknet nophone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    return "nombre noapellido nickname email city nodarknet nophone"
                                else:
                                    return "nombre noapellido nickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    return "nombre noapellido nickname noemail city nodarknet nophone"
                                else:
                                    return "nombre noapellido nickname noemail nocity nodarknet nophone"
                        else:
                            if email:
                                if city:
                                    return "nombre noapellido nonickname email city nodarknet nophone"
                                else:
                                    return "nombre noapellido nonickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    return "nombre noapellido nonickname noemail city nodarknet nophone"
                                else:
                                    return "nombre noapellido nonickname noemail nocity nodarknet nophone"
                else:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    return "nonombre apellido nickname email city nodarknet nophone"
                                else:
                                    return "nonombre apellido nickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    return "nonombre apellido nickname noemail city nodarknet nophone"
                                else:
                                    return "nonombre apellido nickname noemail nocity nodarknet nophone"
                        else:
                            if email:
                                if city:
                                    return "nonombre apellido nonickname email city nodarknet nophone"
                                else:
                                    return "nonombre apellido nonickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    return "nonombre apellido nonickname noemail city nodarknet nophone"
                                else:
                                    return "nonombre apellido nonickname noemail nocity nodarknet nophone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nickname email city nodarknet nophone" TODO FALTA CITY
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    return "nonombre noapellido nickname noemail city nodarknet nophone"
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname) 
                                    #nonombre noapellido nickname noemail nocity nodarknet nophone
                        else:
                            if email:
                                if city:
                                    return "nonombre noapellido nonickname email city nodarknet nophone"
                                else:
                                    resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    resultadosIntelx = pruebaIntel(email)
                                    return render_template("resultadosBusqueda.html",email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
                                    #"nonombre noapellido nonickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    return "nonombre noapellido nonickname noemail city nodarknet nophone"
                                else:
                                    return redirect('buscarPersona')
                                    #nonombre noapellido nonickname noemail nocity nodarknet nophone
            

        # elif nickname:
        #     resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
        #     return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname)

        # elif email:
        #     resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
        #     resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
        #     return render_template("resultadosBusqueda.html", email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail)
    
                                    # resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    # resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    # resultadosIntelx = pruebaIntel(email)
                                    # return render_template("resultadosBusqueda.html",email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)

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
#    App.run(debug=True)
    App.run()





        # if phone:
        #     if nombre:
        #         if apellidos:
        #             if nickname:
        #                 if email:
        #                     if city:
        #                         return "nombre apellido nickname email city darknet phone"
        #                     else:
        #                         return "nombre apellido nickname email nocity darknet phone"
        #                 else:
        #                     if city:
        #                         return "nombre apellido nickname noemail city darknet phone"
        #                     else:
        #                         return "nombre apellido nickname noemail nocity darknet phone"
        #             else:
        #                 if email:
        #                     if city:
        #                         return "nombre apellido nonickname email city darknet phone"
        #                     else:
        #                         return "nombre apellido nonickname email nocity darknet phone"
        #                 else:
        #                     if city:
        #                         return "nombre apellido nonickname noemail city darknet phone"
        #                     else:
        #                         return "nombre apellido nonickname noemail nocity darknet phone"
        #         else:
        #             if nickname:
        #                 if email:
        #                     if city:
        #                         return "nombre noapellido nickname email city darknet phone"
        #                     else:
        #                         return "nombre noapellido nickname email nocity darknet phone"
        #                 else:
        #                     if city:
        #                         return "nombre noapellido nickname noemail city darknet phone"
        #                     else:
        #                         return "nombre noapellido nickname noemail nocity darknet phone"
        #             else:
        #                 if email:
        #                     if city:
        #                         return "nombre noapellido nonickname email city darknet phone"
        #                     else:
        #                         return "nombre noapellido nonickname email nocity darknet phone"
        #                 else:
        #                     if city:
        #                         return "nombre noapellido nonickname noemail city darknet phone"
        #                     else:
        #                         return "nombre noapellido nonickname noemail nocity darknet phone"
        #     else:
        #         if apellidos:
        #             if nickname:
        #                 if email:
        #                     if city:
        #                         return "nonombre apellido nickname email city darknet phone"
        #                     else:
        #                         return "nonombre apellido nickname email nocity darknet phone"
        #                 else:
        #                     if city:
        #                         return "nonombre apellido nickname noemail city darknet phone"
        #                     else:
        #                         return "nonombre apellido nickname noemail nocity darknet phone"
        #             else:
        #                 if email:
        #                     if city:
        #                         return "nonombre apellido nonickname email city darknet phone"
        #                     else:
        #                         return "nonombre apellido nonickname email nocity darknet phone"
        #                 else:
        #                     if city:
        #                         return "nonombre apellido nonickname noemail city darknet phone"
        #                     else:
        #                         return "nonombre apellido nonickname noemail nocity darknet phone"
        #         else:
        #             if nickname:
        #                 if email:
        #                     if city:
        #                         resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
        #                         resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosIntelx = pruebaIntel(email)
        #                         return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
        #                         #"nonombre noapellido nickname email city darknet phone" TODO FALTA CITY
        #                     else:
        #                         resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
        #                         resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosIntelx = pruebaIntel(email)
        #                         return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
        #                         #"nonombre noapellido nickname email nocity darknet phone"
        #                 else:
        #                     if city:
        #                         return "nonombre noapellido nickname noemail city darknet phone"
        #                     else:
        #                         resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
        #                         return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname) 
        #                         #nonombre noapellido nickname noemail nocity darknet phone
        #             else:
        #                 if email:
        #                     if city:
        #                         return "nonombre noapellido nonickname email city darknet phone"
        #                     else:
        #                         resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosIntelx = pruebaIntel(email)
        #                         return render_template("resultadosBusqueda.html",email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
        #                         #"nonombre noapellido nonickname email nocity darknet phone"
        #                 else:
        #                     if city:
        #                         return "nonombre noapellido nonickname noemail city"
        #                     else:
        #                         resultadosIntelx = phonebooksearch(phone)
        #                         return render_template("resultadosBusqueda.html",phone=phone, resultadosIntelx = resultadosIntelx)
        #                         #return redirect('buscarPersona') TODO
        #                         #"nonombre noapellido nonickname noemail nocity darknet phone"
        # else:
        #     if nombre:
        #         if apellidos:
        #             if nickname:
        #                 if email:
        #                     if city:
        #                         return "nombre apellido nickname email city darknet nophone"
        #                     else:
        #                         return "nombre apellido nickname email nocity darknet nophone"
        #                 else:
        #                     if city:
        #                         return "nombre apellido nickname noemail city darknet nophone"
        #                     else:
        #                         return "nombre apellido nickname noemail nocity darknet nophone"
        #             else:
        #                 if email:
        #                     if city:
        #                         return "nombre apellido nonickname email city darknet nophone"
        #                     else:
        #                         return "nombre apellido nonickname email nocity darknet nophone"
        #                 else:
        #                     if city:
        #                         return "nombre apellido nonickname noemail city darknet nophone"
        #                     else:
        #                         return "nombre apellido nonickname noemail nocity darknet nophone"
        #         else:
        #             if nickname:
        #                 if email:
        #                     if city:
        #                         return "nombre noapellido nickname email city darknet nophone"
        #                     else:
        #                         return "nombre noapellido nickname email nocity darknet nophone"
        #                 else:
        #                     if city:
        #                         return "nombre noapellido nickname noemail city darknet nophone"
        #                     else:
        #                         return "nombre noapellido nickname noemail nocity darknet nophone"
        #             else:
        #                 if email:
        #                     if city:
        #                         return "nombre noapellido nonickname email city darknet nophone"
        #                     else:
        #                         return "nombre noapellido nonickname email nocity darknet nophone"
        #                 else:
        #                     if city:
        #                         return "nombre noapellido nonickname noemail city darknet nophone"
        #                     else:
        #                         return "nombre noapellido nonickname noemail nocity darknet nophone"
        #     else:
        #         if apellidos:
        #             if nickname:
        #                 if email:
        #                     if city:
        #                         return "nonombre apellido nickname email city darknet nophone"
        #                     else:
        #                         return "nonombre apellido nickname email nocity darknet nophone"
        #                 else:
        #                     if city:
        #                         return "nonombre apellido nickname noemail city darknet nophone"
        #                     else:
        #                         return "nonombre apellido nickname noemail nocity darknet nophone"
        #             else:
        #                 if email:
        #                     if city:
        #                         return "nonombre apellido nonickname email city darknet nophone"
        #                     else:
        #                         return "nonombre apellido nonickname email nocity darknet nophone"
        #                 else:
        #                     if city:
        #                         return "nonombre apellido nonickname noemail city darknet nophone"
        #                     else:
        #                         return "nonombre apellido nonickname noemail nocity darknet nophone"
        #         else:
        #             if nickname:
        #                 if email:
        #                     if city:
        #                         resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
        #                         resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosIntelx = pruebaIntel(email)
        #                         return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
        #                         #"nonombre noapellido nickname email city darknet nophone" TODO FALTA CITY
        #                     else:
        #                         resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
        #                         resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosIntelx = pruebaIntel(email)
        #                         return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
        #                         #"nonombre noapellido nickname email nocity darknet nophone"
        #                 else:
        #                     if city:
        #                         return "nonombre noapellido nickname noemail city"
        #                     else:
        #                         resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
        #                         return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname) 
        #                         #nonombre noapellido nickname noemail nocity darknet nophone
        #             else:
        #                 if email:
        #                     if city:
        #                         return "nonombre noapellido nonickname email city"
        #                     else:
        #                         resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
        #                         resultadosIntelx = pruebaIntel(email)
        #                         return render_template("resultadosBusqueda.html",email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)
        #                         #"nonombre noapellido nonickname email nocity darknet nophone"
        #                 else:
        #                     if city:
        #                         return "nonombre noapellido nonickname noemail city"
        #                     else:
        #                         # resultadosIntelx = phonebooksearch(phone)
        #                         # return render_template("resultadosBusqueda.html",phone=phone, resultadosIntelx = resultadosIntelx)
        #                         return redirect('buscarPersona')
        #                         #"nonombre noapellido nonickname noemail nocity darknet nophone"

