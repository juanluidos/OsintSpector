import asyncio
import os
import sys
from time import sleep
from flask import Flask, redirect, url_for, render_template, request
from utils.Intelx.intelexapi import intelx
from searchScripts.buscarPersona.darknet.darkScraping import AhmiaScraping
from searchScripts.buscarPersona.username.usernameScraping import usernameScrapping
from searchScripts.buscarPersona.emailPhone.hibpApi import HIBPApi
from searchScripts.buscarPersona.emailPhone.emailPhoneIHBP import HIBPScraping
from searchScripts.buscarPersona.person.personScraping import GoogleScrapingPerson, INEScrapingName, INEScrapingSurName
from subprocess import Popen, PIPE

from utils.Proxies.getProxies import runProxyScript, set_interval

p = Popen([sys.executable, "-m", "playwright", "install"], stdin=PIPE, stdout=PIPE, stderr=PIPE)

App = Flask(__name__)

#Error que tiene la libreria de async_io para las versiones de python por debajo de la 3.9, a tener en cuenta para los requisitos recomendados del sistema.
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

@App.route("/buscar_Persona")
def buscarPersona():
    return render_template("buscarPersona.html")    

@App.route("/buscar_Persona_Twitter")
def buscarPersonaTwitter():
    return render_template("buscarPersonaTwitter.html")    

@App.route("/resultTwitter", methods=["POST", "GET"])
def resultTwitter():
    return render_template("index.html")    

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
                                    # resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    # resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    intel = intelx()
                                    # resultadosIntelxEmail = intel.emailOrPhoneSearch(email)
                                    # return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail)
                                    #"nonombre noapellido nickname email city darknet phone" TODO FALTA CITY
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    # resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    # resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    intel = intelx()
                                    # resultadosIntelxEmail = intel.emailOrPhoneSearch(email)
                                    # return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail)
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
                                    #IntelX
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #HIBPwned Scraping
                                    hp = HIBPScraping()
                                    resultadosPwnedPhone = asyncio.run(hp.parseHTML(phone))
                                    resultadosPwnedEmail = asyncio.run(hp.parseHTML(email))
                                    
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    uriUrlAhmia = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    resultadoDarknet = hp.parseHTML(baseUrlAhmia+uriUrlAhmia)

                                    return render_template("resultadosBusqueda.html",email=email, phone=phone, darknet=darknet, resultadosPwnedPhone = resultadosPwnedPhone ,resultadosIntelxEmail = resultadosIntelxEmail, resultadosIntelxPhone = resultadosIntelxPhone, resultadosPwnedEmail = resultadosPwnedEmail, resultadoDarknet=resultadoDarknet)
                                    #"nonombre noapellido nonickname email nocity darknet phone"
                            else:
                                if city:
                                    return "nonombre noapellido nonickname noemail city"
                                else:
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)
                                    return render_template("resultadosBusqueda.html",phone=phone, resultadosIntelxPhone = resultadosIntelxPhone)
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
                                    # return "nombre apellido nonickname noemail city nodarknet nophone"
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(nombre, apellidos)

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    uriUrlAhmia = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    resultadoDarknet = hp.parseHTML(baseUrlAhmia+uriUrlAhmia)
                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadoDarknet = resultadoDarknet, darknet = darknet, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch)

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
                                    # resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    # resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))

                                    # return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail)
                                    #"nonombre noapellido nickname email city darknet nophone" TODO FALTA CITY
                                else:
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    # resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    # resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))

                                    # return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail)
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
                                    pass
                                    # resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    # resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))

                                    # return render_template("resultadosBusqueda.html",email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail)
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
            if phone:
                if nombre:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(nombre, apellidos, city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre apellido nickname email city nodarknet phone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, surname=apellidos)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre apellido nickname email nocity nodarknet phone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(nombre, apellidos, city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre apellido nickname noemail city nodarknet phone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, surname=apellidos)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre apellido nickname noemail nocity nodarknet phone"
                                    
                        else:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(nombre, apellidos, city)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre apellido nonickname email city nodarknet phone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, surname=apellidos)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre apellido nonickname email nocity nodarknet phone"
                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name = nombre, surname= apellidos, city=city)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre apellido nonickname noemail city nodarknet phone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name= nombre,surname=apellidos)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre apellido nonickname noemail nocity nodarknet phone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre,city = city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nickname email city nodarknet phone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nickname email nocity nodarknet phone"
                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, city=city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nickname noemail city nodarknet phone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nickname noemail nocity nodarknet phone"
                        else:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, city=city)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nonickname email city nodarknet phone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nonickname email nocity nodarknet phone"
                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, city=city)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nonickname noemail city nodarknet phone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nonickname noemail nocity nodarknet phone"
                else:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData( surname=apellidos, city=city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nickname email city nodarknet phone"
                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData( surname=apellidos)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nickname email nocity nodarknet phone"
                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos, city=city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nickname noemail city nodarknet phone"
                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nickname noemail nocity nodarknet phone"
                        else:
                            if email:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos, city=city)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nonickname email city nodarknet phone"
                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nonickname email nocity nodarknet phone"
                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos, city=city)

                                    #Phone intelx
                                    intel=intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)                        
                                    #return "nonombre apellido nonickname noemail city nodarknet phone"
                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos)

                                    #Phone intelx
                                    intel=intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nonickname noemail nocity nodarknet phone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nickname email city nodarknet phone"
                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nickname email nocity nodarknet phone"
                            else:
                                if city:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre noapellido nickname noemail city nodarknet phone"
                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #nonombre noapellido nickname noemail nocity nodarknet phone
                        else:
                            if email:
                                if city:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)
                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre noapellido nonickname email city nodarknet phone"
                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)
                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nonickname email nocity nodarknet phone"
                            else:
                                if city:

                                    #Phone intelx
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre noapellido nonickname noemail city nodarknet phone"
                                else:

                                    #Phone intelx
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nonickname noemail nocity nodarknet phone"
            else:
                if nombre:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(nombre, apellidos, city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre apellido nickname email city nodarknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, surname=apellidos)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre apellido nickname email nocity nodarknet nophone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(nombre, apellidos, city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')


                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname)
                                    #return "nombre apellido nickname noemail city nodarknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, surname=apellidos)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')


                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname)
                                    #return "nombre apellido nickname noemail nocity nodarknet nophone"
                                    
                        else:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(nombre, apellidos, city)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre apellido nonickname email city nodarknet nophone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, surname=apellidos)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre apellido nonickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name = nombre, surname= apellidos, city=city)


                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch)
                                    #return "nombre apellido nonickname noemail city nodarknet nophone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name= nombre,surname=apellidos)


                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch)
                                    #return "nombre apellido nonickname noemail nocity nodarknet nophone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre,city = city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre noapellido nickname email city nodarknet nophone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre noapellido nickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, city=city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')


                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname)
                                    #return "nombre noapellido nickname noemail city nodarknet nophone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')


                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname)
                                    #return "nombre noapellido nickname noemail nocity nodarknet nophone"
                        else:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, city=city)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre noapellido nonickname email city nodarknet nophone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre noapellido nonickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, city=city)


                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch)
                                    #return "nombre noapellido nonickname noemail city nodarknet nophone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)


                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch)
                                    #return "nombre noapellido nonickname noemail nocity nodarknet nophone"
                else:
                    if apellidos:
                        if nickname:
                            if email:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData( surname=apellidos, city=city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nonombre apellido nickname email city nodarknet nophone"
                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData( surname=apellidos)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nonombre apellido nickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos, city=city)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')


                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname)
                                    #return "nonombre apellido nickname noemail city nodarknet nophone"
                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')


                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname)
                                    #return "nonombre apellido nickname noemail nocity nodarknet nophone"
                        else:
                            if email:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos, city=city)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nonombre apellido nonickname email city nodarknet nophone"
                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos)

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nonombre apellido nonickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos, city=city)

                                    #Phone intelx
                                    intel=intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch)                        
                                    #return "nonombre apellido nonickname noemail city nodarknet nophone"
                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos)

                                    #Phone intelx
                                    intel=intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch)
                                    #return "nonombre apellido nonickname noemail nocity nodarknet nophone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #"nonombre noapellido nickname email city nodarknet nophone"
                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #"nonombre noapellido nickname email nocity nodarknet nophone"
                            else:
                                if city:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')


                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname)
                                    #return "nonombre noapellido nickname noemail city nodarknet nophone"
                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname)
                                    #nonombre noapellido nickname noemail nocity nodarknet phone
                        else:
                            if email:
                                if city:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    return render_template("resultadosBusqueda.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre noapellido nonickname email city nodarknet nophone"
                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    return render_template("resultadosBusqueda.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nonickname email nocity nodarknet nophone"
                            else:
                                if city:

                                    #Phone intelx
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre noapellido nonickname noemail city nodarknet nophone"
                                else:

                                    #Phone intelx
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusqueda.html", phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nonickname noemail nocity nodarknet nophone"
            

        # elif nickname:
        #     resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
        #     return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname)

        # elif email:
        #     resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
        #     resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
        #     return render_template("resultadosBusqueda.html", email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail)
    
                                    # resultadosBreachedEmail = emailBreachedExpanded(email, os.getenv("API_KEY_IHBP"))
                                    # resultadosPastedEmail = emailPasted(email, os.getenv("API_KEY_IHBP"))
                                    # resultadosIntelx = emailOrPhoneSearch(email)
                                    # return render_template("resultadosBusqueda.html",email=email, resultadosBreached = resultadosBreachedEmail, resultadosPasted = resultadosPastedEmail, resultadosIntelx = resultadosIntelx)

        # elif city:
        #     return "he"
        # else:
        #     return redirect("buscarPersona")

    else:
        #si es metodo GET
        #quizás añadir 404.html en lugar de redirect
        return redirect("index.html")
        

#Subprocess to refresh the working free proxies available
set_interval(runProxyScript,1800)

# @app.route("/<name>")
# def user(name):
#     return f"Hello {name}!"

# @app.route("/admin/")
# def admin():
#     return redirect(url_for("user", name="Admin!"))

if __name__ == "__main__":
    App.run(debug=True)
    # App.run()

