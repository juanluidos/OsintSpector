import os
import random
import time
import requests
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googleapiclient.discovery import build
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
        # print(self.params)
        # print(json.dumps(api_result.json()))
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
        if results["organic_results"]:
            return results["organic_results"]
        else:
            return []

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
        searchResultsNameSurname = []
        searchResultsSurnameName = []
        rawDataNameSurname = self.getDataNameSurname(name,surname,city)
        rawDataSurnameName = self.getDataSurnameName(name,surname,city)

        for element in rawDataNameSurname:
                searchResultsNameSurname.append([element["domain"], element["link"] ,element["title"], element["snippet"]])
        for element in rawDataSurnameName:
                searchResultsSurnameName.append([element["domain"], element["link"] ,element["title"], element["snippet"]])
        #merge 2 list removing duplicates values
        searchResultsNameSurname.extend(x for x in searchResultsSurnameName if x not in searchResultsNameSurname)
        print("Found {data1} and google search results".format(data1 = len(searchResultsNameSurname)))
        return searchResultsNameSurname



# params = {
# 'api_key': os.getenv('API_SERP'),
#   'q': '"Eric Andrés Obaya"',
#   'nfpr': 1,
#   'filter': 0,
#    'location': 'Asturias,Spain'
# }

# # make the http GET request to Scale SERP
# api_result = requests.get('https://api.scaleserp.com/search', params)

# # print the JSON response from Scale SERP
# print(json.dumps(api_result.json()))