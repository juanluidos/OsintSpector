import os
import random
import tempfile
import time
from matplotlib.pyplot import show
import requests
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import unicodedata
from unidecode import unidecode
from wordcloud import WordCloud, STOPWORDS
import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
#from utils.commonFunctions import randomUserAgent

def randomUserAgent(filename):
    with open(filename) as f:
        lines = f.readlines()
    return random.choice(lines).replace("\n","")

def randomProxyServer(filename):
    with open(filename) as f:
        lines = f.readlines()
        if(len(lines)>1):
            lines = lines[0:len(lines)-1]
        #Si no existe ningún proxy disponible por desgracia tendríamos q usar nuestra IP (solo me ha ocurrido una vez durante todo el desarrollo, pero por si acaso)
        elif(len(lines)==0):
            return None
    return random.choice(lines).rstrip("\n")

class INEScrapingName:
    async def run(self,p):
        proxy = randomProxyServer("utils\Proxies\workingproxylistINE.txt")
        if(proxy) != None:
            browser = await p.chromium.launch(slow_mo=100, headless=False, proxy={"server": proxy })
            print(f"Scraping INE name with proxy: {proxy}")
        else:
            browser = await p.chromium.launch(slow_mo=100, headless=False)
            print(f"Scraping INE name with no proxy available")
        userAgent = randomUserAgent("utils/userAgentsList.txt")
        context = await browser.new_context(
            user_agent = userAgent
        )
        return context

    async def getINEHtmlName(self, input):
        #un try catch para comprobar si hay numero o si es nulo el valor
        async with async_playwright() as p:
            context = await self.run(p)
            page = await context.new_page()
            await stealth_async(page) #stealth
            await page.goto("https://www.ine.es/widgets/nombApell/nombApell.shtml?L=&w=1189px&h=918px&borc=000000", timeout=0)
            time.sleep(1)
            await page.fill("input[id = cajaW]", input)
            await page.keyboard.press('Enter')
            time.sleep(1)
            await page.is_visible("div.resultado")
            htmlNameNumber = await page.inner_html("div.resultado")
            soupNameNumber = BeautifulSoup(htmlNameNumber, "html.parser")
            if (soupNameNumber.find("div",{"class":"resultado"}) is None):
                return soupNameNumber, True
            else:
                return soupNameNumber, False
    
    async def parseHTML(self, input):
        result = await self.getINEHtmlName(input)
        if(result[1]):
            datos = result[0].findAll("span",{"class":"widgetResultTotal"})
            return datos[1].getText(), datos[2].getText()
        else:
            return "menor de 5"

class INEScrapingSurName:
    async def run(self,p):
        proxy = randomProxyServer("utils\Proxies\workingproxylistINE.txt")
        if(proxy) != None:
            browser = await p.chromium.launch(slow_mo=100, headless=False, proxy={"server": proxy })
            print(f"Scraping INE surname with proxy: {proxy}")
        else:
            browser = await p.chromium.launch(slow_mo=100, headless=False)
            print(f"Scraping INE surname with no proxy available")        
        userAgent = randomUserAgent("utils/userAgentsList.txt")
        context = await browser.new_context(
            user_agent = userAgent
        )
        return context

    async def getINEHtmlSurName(self, input):
        #un try catch para comprobar si hay numero o si es nulo el valor
        async with async_playwright() as p:
            context = await self.run(p)
            page = await context.new_page()
            await stealth_async(page) #stealth
            await page.goto("https://www.ine.es/widgets/nombApell/nombApell.shtml?L=&w=1189px&h=918px&borc=000000", timeout=0)
            time.sleep(1)
            surnameList = input.split()
            resultList = []
            for apellido in surnameList:
                await page.fill("input[id = cajaW]", apellido)
                time.sleep(2)
                await page.click("input#btnApell")
                time.sleep(1)
                await page.is_visible("div.resultado")
                htmlNameNumber = await page.inner_html("div.resultado")
                soupNameNumber = BeautifulSoup(htmlNameNumber, "html.parser")
                if (soupNameNumber.find("div",{"class":"resultado"}) is None):
                    resultList.append((soupNameNumber, True))
                else:
                    resultList.append((soupNameNumber, False))
            return resultList

    async def parseHTML(self, input):
        result = await self.getINEHtmlSurName(input)
        resultList = []
        for index, apellido in enumerate(result):
            if (index == 0):
                if(apellido[1]):
                    datos = apellido[0].findAll("span",{"class":"widgetResultTotal"})
                    resultList.append((datos[0].getText(), datos[1].getText(),"primer"))
                else:
                    resultList.append((input.split()[0],"menor de 5","primer"))
            else:
                if(apellido[1]):
                    datos = apellido[0].findAll("span",{"class":"widgetResultTotal"})
                    resultList.append((datos[0].getText(), datos[1].getText(),"segundo"))
                else:
                    datos = apellido[0].findAll("span",{"class":"widgetResultTotal"})
                    resultList.append((input.split()[1],"menor de 5","segundo"))
        return resultList

# my_api_key = os.getenv("API_KEY_GOOGLE")
# my_cse_id = ""
# query = '""'
# start=1

# def google_search(search_term, api_key, cse_id, **kwargs):
#     service = build("customsearch", "v1", developerKey=api_key)
#     res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
#     return res

# print(google_search(query,my_api_key,my_cse_id))

# url = f'https://www.googleapis.com/customsearch/v1?key={my_api_key}&cx={my_cse_id}&q={query}'

# print(requests.get(url).json())

#http://jsonviewer.stack.hu/

#Issue de google searchs api comparado con las busquedas reales desde 2008
#https://code.google.com/archive/p/google-ajax-apis/issues/43

#lo mismo le pasa a duckduckgo
#https://duckduckgo.com/api

#posibles salvavidas
#No me gusta mucho los resultados que pone
#https://console.apify.com/actors/nFJndFXA5zjCTuudP/runs/ALjTUc4YM5LQffxVU#output
#Prefiero mucho más la puesta en escena de los resultados que da esta API, buena estructura que puede anidarse bien.
#https://www.scaleserp.com/?gclid=Cj0KCQjw39uYBhCLARIsAD_SzMTj1eRSwq3l24yIHh3_zCp3abFgY4T3a1Rn0KRtfPu5FVLd5CVXSNgaAihhEALw_wcB https://app.scaleserp.com/playground

# set up the request parameters

class GoogleScrapingPerson():
    def __init__(self, key = os.getenv("API_SERP"), ua = randomUserAgent("utils/userAgentsList.txt")):
        self.api = key
        self.user_agent = ua
        self.params = {
            'api_key': os.getenv('API_SERP'),
            'nfpr': 1,
            'q':'',
            'max_page': '2',
            'location': ''
            }
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
                'User-Agent': self.user_agent
            }
    def getDataNameSurname(self, name="",surname="", city=""):
        if(name != "" and surname != ""):
            self.params["q"] = f'"{name} {surname}"'

        elif(name != ""):
            self.params["q"] = f'"{name}"'

        elif(surname != ""):
            self.params["q"] = f'"{surname}"'

        if(city != ""):
            self.params["location"] = f'"{city}"'

        api_result = requests.get('https://api.scaleserp.com/search', self.params, headers=self.headers)
        results = api_result.json()
        
        try:
            results["organic_results"]
        except:
            return []
        else:
            return results["organic_results"]

    def getDataSurnameName(self, name="",surname="", city=""):
        if(name != "" and surname != ""):
            self.params["q"] = f'"{surname} {name}"'

        elif(name != ""):
            self.params["q"] = f'"{name}"'

        elif(surname != ""):
            self.params["q"] = f'"{surname}"'

        if(city != ""):
            self.params["location"] = f'"{city}"'

        api_result = requests.get('https://api.scaleserp.com/search', self.params, headers=self.headers)
        results = api_result.json()
        #Comprobamos si exsiten o no resultados
        try:
            results["organic_results"]
        except:
            return []
        else:
            return results["organic_results"]

    def parseData(self, name="", surname="", city=""):
        #Estructura de los datos:
        #organicresults
        #[[dominio, link, titulo],....]
        print("Searching for " + name +" "+ surname +" "+ city)
        searchResultsNameSurname = []
        searchResultsSurnameName = []
        textoBrutoWordcloud = ""
        dominiosBruto = []
        rawDataNameSurname = self.getDataNameSurname(name,surname,city)
        rawDataSurnameName = self.getDataSurnameName(name,surname,city)
        
        for element in rawDataNameSurname:
            #A veces el parametro snippet da error porq no existe en el diccionario de respuesta
            try:
                searchResultsNameSurname.append([element["domain"], element["link"] ,element["title"], element["snippet"]])
                textoBrutoWordcloud += element["title"] + " " + element["snippet"]
                dominiosBruto.append(element["domain"])
            except:
                searchResultsNameSurname.append([element["domain"], element["link"] ,element["title"], ""])
                textoBrutoWordcloud += element["title"]
                dominiosBruto.append(element["domain"])
        for element in rawDataSurnameName:
            try:
                searchResultsNameSurname.append([element["domain"], element["link"] ,element["title"], element["snippet"]])
                textoBrutoWordcloud += element["title"] + " " + element["snippet"]
                dominiosBruto.append(element["domain"])
            except:
                searchResultsNameSurname.append([element["domain"], element["link"] ,element["title"], ""])
                textoBrutoWordcloud += element["title"]
                dominiosBruto.append(element["domain"])
        print(dominiosBruto)
        #merge 2 list removing duplicates values
        searchResultsNameSurname.extend(x for x in searchResultsSurnameName if x not in searchResultsNameSurname)
        print("Found {data1} and google search results".format(data1 = len(searchResultsNameSurname)))

        #PARTE PARA LA GRÁFICA Y WORDCLOUD
        if(textoBrutoWordcloud != "" and dominiosBruto != []):
                    
            #Gráfica
            print("Generando Datos Gráfica Persona...")
            diccionarioGrafica = {}

            for dominio in dominiosBruto:
                extension = "." + dominio.split('.')[-1]
                if extension in diccionarioGrafica:
                    diccionarioGrafica[extension] += 1
                else:
                    diccionarioGrafica[extension] = 1
            datosGrafica = [list(diccionarioGrafica.keys()),list(diccionarioGrafica.values())]
            print(datosGrafica)
            print("Datos para la gráfica generados")

            #Wordcloud
            print("Generando Wordcloud Persona...")
            # Eliminar menciones
            textoBrutoWordcloud = re.sub(r'@([A-Za-z0-9_]+)', r'\1', textoBrutoWordcloud)

            # Eliminar urls
            textoBrutoWordcloud = re.sub(r'https?://[A-Za-z0-9./]+', '', textoBrutoWordcloud)

            # Eliminar hashtags (solo el simbolo #)
            textoBrutoWordcloud = re.sub(r'#([^\s]+)', r'\1', textoBrutoWordcloud)

            # Eliminar signos de puntuación y números
            textoBrutoWordcloud = re.sub('[^a-zA-ZáéíóúüÁÉÍÓÚÜñÑ]', ' ', textoBrutoWordcloud)

            # Eliminar espacios extra y saltos de línea
            textoBrutoWordcloud = re.sub(' +', ' ', textoBrutoWordcloud).strip()

            # Eliminar stopwords en español y en inglés
            spanish_stopwords = set(stopwords.words('spanish'))
            english_stopwords = set(stopwords.words('english'))
            all_stopwords = spanish_stopwords.union(english_stopwords)
            
            # Agregar versiones normalizadas de stopwords originales
            for stopword in spanish_stopwords:
                all_stopwords.add(unidecode(stopword))
            for stopword in english_stopwords:
                all_stopwords.add(unidecode(stopword))
            
            # Eliminar stopwords y palabras de una sola letra
            texto_limpio = [word.lower() for word in nltk.word_tokenize(textoBrutoWordcloud) if word.lower() not in all_stopwords and len(word) > 1]

            #Convertir a minúsculas y normalizar letras con acentos y diéresis
            texto_limpio = " ".join(texto_limpio)
            texto_limpio = unicodedata.normalize('NFKD', texto_limpio.lower()).encode('ASCII', 'ignore').decode('utf-8')

            # Eliminar los propios nombres y apellidos, lo del split es por si fuera nombre compuesto
            palabras_a_eliminar = name.split(sep=' ')
            palabras_a_eliminar.extend(surname.split(sep=' '))

                # Eliminar las palabras de la cadena de texto
            for palabra in palabras_a_eliminar:
                texto_limpio = re.sub(palabra.lower(), '', texto_limpio)

            #Generar wordcloud
            # Crear la instancia de la clase WordCloud
            wordcloud = WordCloud(background_color="white", max_words=200, stopwords=set(STOPWORDS), contour_color='steelblue', scale=2, height=400, collocations=False)

            wordcloud.generate(texto_limpio)
            # Crear un archivo temporal para guardar la imagen
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                output_path = tmp.name

                # Guardar la imagen en el archivo temporal
                wordcloud.to_file(output_path)

                # Devolver la ruta de la imagen
                print("Wordcloud Generado")
                return (searchResultsNameSurname, output_path, datosGrafica)
        
        return searchResultsNameSurname, "",[]
    
# hp = GoogleScrapingPerson()
# resultadosGoogleSearch = hp.parseData(name="ángel jesús",surname="varela vaca",city= "sevilla")