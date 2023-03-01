import asyncio
import os
import sys
from time import sleep
from flask import Flask, flash, redirect, url_for, render_template, request
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone,darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre apellido nickname email city darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre apellido nickname email nocity darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre apellido nickname noemail city darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre apellido nickname noemail nocity darknet phone"
                                    
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre apellido nonickname email city darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre apellido nonickname email nocity darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre apellido nonickname noemail city darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre apellido nonickname noemail nocity darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    print(resultadoDarknetNombre)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nickname email city darknet phone"
                                    
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
                                    #return "nombre noapellido nickname email nocity darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nickname noemail city darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nickname noemail nocity darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nonickname email city darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nonickname email nocity darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nonickname noemail city darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nonickname noemail nocity darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nickname email city darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nickname email nocity darknet phone"
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
                                
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nickname noemail city darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nickname noemail nocity darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nonickname email city darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nonickname email nocity darknet phone

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetPhone=resultadoDarknetPhone)                        
                                    #return "nonombre apellido nonickname noemail city darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nonickname noemail nocity darknet phone"
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #"nonombre noapellido nickname email city darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #"nonombre noapellido nickname email nocity darknet phone"

                            else:
                                if city:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre noapellido nickname noemail city darknet phone"

                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Phone intelx
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #nonombre noapellido nickname noemail nocity darknet phone

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre noapellido nonickname email city darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #"nonombre noapellido nonickname email nocity darknet phone"
                            else:
                                if city:

                                    #Phone intelx
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre noapellido nonickname noemail city darknet phone"

                                else:

                                    #Phone intelx
                                    intel = intelx()
                                    resultadosIntelxPhone = intel.emailOrPhoneSearch(phone)

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusqueda.html", phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #"nonombre noapellido nonickname noemail nocity darknet phone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)


                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre apellido nickname email city darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre apellido nickname email nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    uriUrlAhmia = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    resultadoDarknet = hp.parseHTML(baseUrlAhmia+uriUrlAhmia)

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nombre apellido nickname noemail city darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nombre apellido nickname noemail nocity darknet nophone"
                                    
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre apellido nonickname email city darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre apellido nonickname email nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
                                    #return "nombre apellido nonickname noemail city darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
                                    #return "nombre apellido nonickname noemail nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre noapellido nickname email city darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre noapellido nickname email nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nombre noapellido nickname noemail city darknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nombre noapellido nickname noemail nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre noapellido nonickname email city darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre noapellido nonickname email nocity darknet nophone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre, city=city)

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
                                    #return "nombre noapellido nonickname noemail city darknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(name=nombre)

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
                                    #return "nombre noapellido nonickname noemail nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre apellido nickname email city darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre apellido nickname email nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nonombre apellido nickname noemail city darknet nophone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultadosGoogleSearch = hp.parseData(surname=apellidos)

                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nonombre apellido nickname noemail nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre apellido nonickname email city darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre apellido nonickname email nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)                        
                                    #return "nonombre apellido nonickname noemail city darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusqueda.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
                                    #return "nonombre apellido nonickname noemail nocity darknet nophone"

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #"nonombre noapellido nickname email city darknet nophone"

                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #"nonombre noapellido nickname email nocity darknet nophone"

                            else:
                                if city:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, darknet=darknet, resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nonombre noapellido nickname noemail city darknet nophone"

                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname, darknet=darknet, resultadoDarknetNickname=resultadoDarknetNickname)
                                    #nonombre noapellido nickname noemail nocity darknet nophone

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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre noapellido nonickname email city darknet nophone"

                                else:
                                    #Nickname
                                    resultadosNickname = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')

                                    #Email intelx
                                    intel = intelx()
                                    resultadosIntelxEmail = intel.emailOrPhoneSearch(email)

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusqueda.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetEmail=resultadoDarknetEmail)
                                    #"nonombre noapellido nonickname email nocity darknet nophone"

                            else:
                                if city:
                                    flash("Añade más información al formulario")
                                    return redirect(url_for("buscarPersona"))
                                    #return "nonombre noapellido nonickname noemail city darknet nophone"

                                else:
                                    flash("Añade más información al formulario")
                                    return redirect(url_for("buscarPersona"))
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

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    uriUrlAhmia = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    resultadoDarknet = hp.parseHTML(baseUrlAhmia+uriUrlAhmia)

                                    return render_template("resultadosBusqueda.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname, darknet=darknet, resultadoDarknet=resultadoDarknet)
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

                                    return render_template("resultadosBusqueda.html", nickname=nickname, resultadoNickname = resultadosNickname)
                                    #nonombre noapellido nickname noemail nocity nodarknetnophone
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
                                    flash("Añade más información al formulario")
                                    return redirect(url_for("buscarPersona"))
                                    #return "nonombre noapellido nonickname noemail city nodarknet nophone"
                                else:
                                    flash("Añade más información al formulario")
                                    return redirect(url_for("buscarPersona"))
                                    #"nonombre noapellido nonickname noemail nocity nodarknet nophone"

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
    App.secret_key = os.getenv('APP_KEY')
    App.run(debug=True)
    #App.run()