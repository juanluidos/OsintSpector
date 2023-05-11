import asyncio
import base64
import os
import multiprocessing
import time
import sys
from time import sleep
from flask import Flask, flash, redirect, url_for, render_template, request
from searchScripts.twitter.busquedaTwitter import busquedaTwitter
from searchScripts.buscarPersona.emailPhone.intelexapi import intelx
from searchScripts.buscarPersona.darknet.darkScraping import AhmiaScraping
from searchScripts.buscarPersona.username.usernameScraping import usernameScrapping
from searchScripts.buscarPersona.emailPhone.hibpApi import HIBPApi
from searchScripts.buscarPersona.person.personScraping import GoogleScrapingPerson, INEScrapingName, INEScrapingSurName
from subprocess import Popen, PIPE

from utils.Proxies.getProxies import getProxies

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
    if request.method == 'POST':
        userForm = request.form["usuario"]
        usuario = userForm.replace("@","")

        #Llamada a la clase Padre
        busqueda = busquedaTwitter(usuario, 3200)
        resultado = busqueda.resultadoBusqueda()

        #WORDCLOUD
        # Generar la wordcloud
        img_path = resultado["wordcloud"]
        # Codificar la imagen en base64
        with open(img_path, 'rb') as f:
            img_data = f.read()
        img_data_b64 = base64.b64encode(img_data).decode('utf-8')
        # Eliminar imagen temporal
        os.remove(img_path)

        #GRAFO TOP
        listaTuplasTop = resultado["grafoTop"]

        #GRAFO COMUNIDAD
        grafoComunidad = resultado["grafoComunidad"]
        datosComunidad = resultado["datosComunidad"]

        #SENTIMENTAL ANALYSIS
        tupla_analisis = resultado["sentimentalAnalysis"]
        emotions = tupla_analisis[0]
        topTweets = tupla_analisis[1]
        listaTopTweets = []
        for emotion, data in topTweets.items():
            score = data['score']
            tweet = data['tweet']
            link = data['link']
            listaTopTweets.append((emotion, score, tweet, link))
        # Eliminar datos de la memoria dedicada de la GPU para liberar espacio
        del tupla_analisis

        #LOCATIONS
        localizaciones = resultado["locations"]

        # Enviar respuesta al cliente
        return render_template("resultadosBusquedaTwitter.html", usuario=usuario, img_data=img_data_b64, listaTuplasTop = listaTuplasTop, listaTopTweets = listaTopTweets, emotions = emotions, localizaciones = localizaciones,grafoComunidad = grafoComunidad,  datosComunidad=datosComunidad)
    
    else:
        #si es metodo GET
        #quizás añadir 404.html en lugar de redirect
        return redirect("index.html")

@App.route("/result", methods=["POST", "GET"])
def result():

    if request.method == 'POST':
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        nickname = request.form["nickname"]
        email = request.form["email"]
        city = request.form["city"]
        phone = request.form["area_code"].replace("+","") + request.form["phone"]
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, 
                                                           resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, 
                                                           graficaGoogleSearch=graficaGoogleSearch, nickname=nickname, resultadoNickname = resultadosNickname,
                                                           graficaNickname=graficaNickname, email=email, resultadosIntelxEmail=resultadosIntelxEmail, 
                                                           diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, 
                                                           diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, 
                                                           resultadosIntelxPhone=resultadosIntelxPhone, diccionarioTipoPhone= diccionarioTipoPhone, 
                                                           diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, 
                                                           resultadosPwnedPhone = resultadosPwnedPhone,darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, 
                                                           resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, 
                                                           resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch,imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData(name = nombre, surname= apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData(name= nombre,surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData(name=nombre,city = city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone, resultadosIntelxPhone=resultadosIntelxPhone, diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nickname email city darknet phone"
                                    
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nickname email nocity darknet phone"
                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nickname noemail city darknet phone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nickname noemail nocity darknet phone"

                        else:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nonickname email city darknet phone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nonickname email nocity darknet phone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nombre noapellido nonickname noemail city darknet phone"
                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData( surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nickname email city darknet phone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData( surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nickname email nocity darknet phone"
                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nickname noemail city darknet phone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nickname noemail nocity darknet phone"

                        else:
                            if email:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nonickname email city darknet phone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nonickname email nocity darknet phone

                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

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

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetPhone=resultadoDarknetPhone)                        
                                    #return "nonombre apellido nonickname noemail city darknet phone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre apellido nonickname noemail nocity darknet phone"
                    else:
                        if nickname:
                            if email:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #"nonombre noapellido nickname email city darknet phone"

                                else:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #"nonombre noapellido nickname email nocity darknet phone"

                            else:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre noapellido nickname noemail city darknet phone"

                                else:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #nonombre noapellido nickname noemail nocity darknet phone

                        else:
                            if email:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre noapellido nonickname email city darknet phone"

                                else:                
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)
                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet,resultadoDarknetEmail=resultadoDarknetEmail, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #"nonombre noapellido nonickname email nocity darknet phone"
                            else:
                                if city:

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetPhone=resultadoDarknetPhone)
                                    #return "nonombre noapellido nonickname noemail city darknet phone"

                                else:

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaPhoneUri = f"?q={phone}".replace(" ", "+")

                                    resultadoDarknetPhone = hp.parseHTML(baseUrlAhmia + AhmiaPhoneUri)

                                    return render_template("resultadosBusquedaPersona.html", phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetPhone=resultadoDarknetPhone)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

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


                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
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
                                    resultado = hp.parseData(name = nombre, surname= apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
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
                                    resultado = hp.parseData(name= nombre,surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
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
                                    resultado = hp.parseData(name=nombre,city = city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre noapellido nickname email city darknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre noapellido nickname email nocity darknet nophone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nombre noapellido nickname noemail city darknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nombre noapellido nickname noemail nocity darknet nophone"

                        else:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre, resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre noapellido nonickname email city darknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nombre noapellido nonickname email nocity darknet nophone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
                                    #return "nombre noapellido nonickname noemail city darknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
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
                                    resultado = hp.parseData( surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre apellido nickname email city darknet nophone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData( surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

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

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre apellido nickname email nocity darknet nophone"

                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nonombre apellido nickname noemail city darknet nophone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nonombre apellido nickname noemail nocity darknet nophone"

                        else:
                            if email:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre apellido nonickname email city darknet nophone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre apellido nonickname email nocity darknet nophone"

                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)                        
                                    #return "nonombre apellido nonickname noemail city darknet nophone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNombreUri = f"?q={nombre}+{apellidos}".replace(" ", "+")

                                    resultadoDarknetNombre = hp.parseHTML(baseUrlAhmia+AhmiaNombreUri)

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, darknet=darknet, resultadoDarknetNombre=resultadoDarknetNombre)
                                    #return "nonombre apellido nonickname noemail nocity darknet nophone"

                    else:
                        if nickname:
                            if email:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #"nonombre noapellido nickname email city darknet nophone"

                                else:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)
                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet,resultadoDarknetNickname=resultadoDarknetNickname,resultadoDarknetEmail=resultadoDarknetEmail)
                                    #"nonombre noapellido nickname email nocity darknet nophone"

                            else:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname, darknet=darknet, resultadoDarknetNickname=resultadoDarknetNickname)
                                    #return "nonombre noapellido nickname noemail city darknet nophone"

                                else:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaNicknameUri = f"?q={nickname}".replace(" ", "+")

                                    resultadoDarknetNickname = hp.parseHTML(baseUrlAhmia + AhmiaNicknameUri)

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname, darknet=darknet, resultadoDarknetNickname=resultadoDarknetNickname)
                                    #nonombre noapellido nickname noemail nocity darknet nophone

                        else:
                            if email:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone, darknet=darknet, resultadoDarknetEmail=resultadoDarknetEmail)
                                    #return "nonombre noapellido nonickname email city darknet nophone"

                                else:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    #Darknet Scraping
                                    hp = AhmiaScraping()
                                    AhmiaEmailUri =f"?q={email}".replace(" ", "+")

                                    resultadoDarknetEmail= hp.parseHTML(baseUrlAhmia + AhmiaEmailUri)

                                    return render_template("resultadosBusquedaPersona.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, darknet=darknet, resultadoDarknetEmail=resultadoDarknetEmail)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData(name = nombre, surname= apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData(name= nombre,surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData(name=nombre,city = city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nickname email city nodarknet phone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nickname email nocity nodarknet phone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nickname noemail city nodarknet phone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nickname noemail nocity nodarknet phone"

                        else:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nonickname email city nodarknet phone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nonickname email nocity nodarknet phone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nombre noapellido nonickname noemail city nodarknet phone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData( surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nickname email city nodarknet phone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData( surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nickname email nocity nodarknet phone"

                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nickname noemail city nodarknet phone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nickname noemail nocity nodarknet phone"

                        else:
                            if email:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nonickname email city nodarknet phone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nonickname email nocity nodarknet phone"

                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)                        
                                    #return "nonombre apellido nonickname noemail city nodarknet phone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre apellido nonickname noemail nocity nodarknet phone"

                    else:
                        if nickname:
                            if email:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nickname email city nodarknet phone"

                                else:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nickname email nocity nodarknet phone"

                            else:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre noapellido nickname noemail city nodarknet phone"

                                else:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #nonombre noapellido nickname noemail nocity nodarknet phone

                        else:
                            if email:
                                if city:

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre noapellido nonickname email city nodarknet phone"

                                else:

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))
                                    sleep(7)

                                    #Phone intelx
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail, phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #"nonombre noapellido nonickname email nocity nodarknet phone"

                            else:
                                if city:
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
                                    #return "nonombre noapellido nonickname noemail city nodarknet phone"

                                else:
                                    #Phone intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(phone)
                                    resultadosIntelxPhone = resultado[0]
                                    #DashBoard
                                    diccionarioTipoPhone = resultado[1]
                                    diccionarioTamanyoPhone = resultado[2]
                                    diccionarioFechasPhone = resultado[3]

                                    #Phone HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedPhone =asyncio.run(hp.getPwnedData(phone))

                                    return render_template("resultadosBusquedaPersona.html", phone=phone,  resultadosIntelxPhone=resultadosIntelxPhone,diccionarioTipoPhone= diccionarioTipoPhone, diccionarioTamanyoPhone = diccionarioTamanyoPhone, diccionarioFechasPhone = diccionarioFechasPhone, resultadosPwnedPhone = resultadosPwnedPhone)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname)
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
                                    resultado = hp.parseData(nombre, apellidos, city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
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
                                    resultado = hp.parseData(name=nombre, surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
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
                                    resultado = hp.parseData(name = nombre, surname= apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch)
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
                                    resultado = hp.parseData(name= nombre,surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch)
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
                                    resultado = hp.parseData(name=nombre,city = city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre noapellido nickname email city nodarknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre noapellido nickname email nocity nodarknet nophone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname)
                                    #return "nombre noapellido nickname noemail city nodarknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname)
                                    #return "nombre noapellido nickname noemail nocity nodarknet nophone"

                        else:
                            if email:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre noapellido nonickname email city nodarknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nombre noapellido nonickname email nocity nodarknet nophone"

                            else:
                                if city:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch)
                                    #return "nombre noapellido nonickname noemail city nodarknet nophone"

                                else:
                                    #INE nombre
                                    ine = INEScrapingName()
                                    resultadosINEName = asyncio.run(ine.parseHTML(nombre))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(name=nombre)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    return render_template("resultadosBusquedaPersona.html", nombre=nombre, resultadosINEName = resultadosINEName, resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch)
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
                                    resultado = hp.parseData( surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nonombre apellido nickname email city nodarknet nophone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData( surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nonombre apellido nickname email nocity nodarknet nophone"

                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname)
                                    #return "nonombre apellido nickname noemail city nodarknet nophone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname)
                                    #return "nonombre apellido nickname noemail nocity nodarknet nophone"

                        else:
                            if email:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nonombre apellido nonickname email city nodarknet nophone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname,  resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch, email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nonombre apellido nonickname email nocity nodarknet nophone"

                            else:
                                if city:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos, city=city)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch)                        
                                    #return "nonombre apellido nonickname noemail city nodarknet nophone"

                                else:
                                    #INE apellido
                                    apellid = INEScrapingSurName()
                                    resultadosINESurname = asyncio.run(apellid.parseHTML(apellidos))

                                    #Google Custom Search
                                    hp = GoogleScrapingPerson()
                                    resultado = hp.parseData(surname=apellidos)
                                    resultadosGoogleSearch = resultado[0]
                                    wordcloudGoogleSearch = resultado[1]
                                    graficaGoogleSearch = resultado[2]
                                    #WORDCLOUD
                                    # Generar la wordcloud
                                    if wordcloudGoogleSearch != "":
                                        img_path = wordcloudGoogleSearch
                                        # Codificar la imagen en base64
                                        with open(img_path, 'rb') as f:
                                            img_data = f.read()
                                        imgWordcloud = base64.b64encode(img_data).decode('utf-8')
                                        # Eliminar imagen temporal
                                        os.remove(img_path)
                                    else:
                                        imgWordcloud = ""

                                    return render_template("resultadosBusquedaPersona.html", apellidos = apellidos, resultadosINESurname = resultadosINESurname, resultadosGoogleSearch = resultadosGoogleSearch, imgWordcloud= imgWordcloud, graficaGoogleSearch=graficaGoogleSearch)
                                    #return "nonombre apellido nonickname noemail nocity nodarknet nophone"

                    else:
                        if nickname:
                            if email:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #"nonombre noapellido nickname email city nodarknet nophone"

                                else:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))


                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname,email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #"nonombre noapellido nickname email nocity nodarknet nophone"

                            else:
                                if city:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname)
                                    #return "nonombre noapellido nickname noemail city nodarknet nophone"

                                else:
                                    #Nickname
                                    resultado = usernameScrapping(nickname, './searchScripts/buscarPersona/username/web_accounts_list.json')
                                    resultadosNickname = resultado[0]
                                    graficaNickname = resultado[1]
                                    
                                    return render_template("resultadosBusquedaPersona.html", nickname=nickname,resultadoNickname = resultadosNickname,graficaNickname=graficaNickname)
                                    #nonombre noapellido nickname noemail nocity nodarknet nophone

                        else:
                            if email:
                                if city:
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
                                    #return "nonombre noapellido nonickname email city nodarknet nophone"
                                else:
                                    #Email intelx
                                    intel = intelx()
                                    resultado = intel.emailOrPhoneSearch(email)
                                    resultadosIntelxEmail = resultado[0]
                                    #DashBoard
                                    diccionarioTipoEmail = resultado[1]
                                    diccionarioTamanyoEmail = resultado[2]
                                    diccionarioFechasEmail = resultado[3]

                                    #Email HIBPwned API
                                    hp = HIBPApi(os.getenv('API_KEY_IHBP'))
                                    resultadosPwnedEmail =asyncio.run(hp.getPwnedData(email))

                                    return render_template("resultadosBusquedaPersona.html",email=email, resultadosIntelxEmail=resultadosIntelxEmail, diccionarioTipoEmail = diccionarioTipoEmail, diccionarioTamanyoEmail = diccionarioTamanyoEmail, diccionarioFechasEmail = diccionarioFechasEmail, resultadosPwnedEmail = resultadosPwnedEmail)
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

# Subprocess to refresh the working free proxies available usando multiprocessing, para no ralentizar el rendimiento de la aplicación de Flask, ya que éste requiere recursos de la CPU
def actualizar_proxies():
    while True:
        gp = getProxies()
        gp.obtenerProxiesFiltrados()
        time.sleep(1800)

if __name__ == "__main__":
    App.secret_key = os.getenv('APP_KEY')
    
    # Iniciar el proceso de actualización de proxies
    p = multiprocessing.Process(target=actualizar_proxies)
    p.start()
    
    # Iniciar la aplicación de Flask
    App.run(debug=True)
    
    # Esperar a que el proceso de actualización de proxies termine
    p.join()