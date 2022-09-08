import os
import random
import socket
import time
import requests
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

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
            return socket.gethostbyname(socket.gethostname()) 
    return random.choice(lines).rstrip("\n")

class INEScrapingName:
    async def run(self,p):
        browser = await p.chromium.launch(slow_mo=100, headless=True, proxy={"server": randomProxyServer("utils\Proxies\workingproxylistINE.txt")})
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
            await page.goto("https://www.ine.es/widgets/nombApell/nombApell.shtml?L=&w=1189px&h=918px&borc=000000")
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
        print("Searching name frequency on INE")
        result = await self.getINEHtmlName(input)
        if(result[1]):
            datos = result[0].findAll("span",{"class":"widgetResultTotal"})
            return datos[1].getText(), datos[2].getText()
        else:
            return "menor de 5"

class INEScrapingSurName:
    async def run(self,p):
        browser = await p.chromium.launch(slow_mo=100, headless=True, proxy={"server": randomProxyServer("utils\Proxies\workingproxylistINE.txt")})
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
            await page.goto("https://www.ine.es/widgets/nombApell/nombApell.shtml?L=&w=1189px&h=918px&borc=000000")
            time.sleep(1)
            surnameList = input.split()
            resultList = []
            for apellido in surnameList:
                await page.fill("input[id = cajaW]", apellido)
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
        print("Searching surname frequency on INE")
        result = await self.getINEHtmlSurName(input)
        resultList = []
        for index, apellido in enumerate(result):
            if (index == 0):
                if(apellido[1]):
                    datos = apellido[0].findAll("span",{"class":"widgetResultTotal"})
                    resultList.append((datos[0].getText(), datos[1].getText(),"primer"))
                else:
                    resultList.append((datos[0].getText(),"menor de 5","primer"))
            else:
                if(apellido[1]):
                    datos = apellido[0].findAll("span",{"class":"widgetResultTotal"})
                    resultList.append((datos[0].getText(), datos[1].getText(),"segundo"))
                else:
                    resultList.append((datos[0].getText(),"menor de 5","segundo"))
        return resultList

my_api_key = ""
my_cse_id = ""
query = '""'
start=1

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

#https://www.scaleserp.com/?gclid=Cj0KCQjw39uYBhCLARIsAD_SzMTj1eRSwq3l24yIHh3_zCp3abFgY4T3a1Rn0KRtfPu5FVLd5CVXSNgaAihhEALw_wcB
#https://console.apify.com/actors/nFJndFXA5zjCTuudP/runs/ALjTUc4YM5LQffxVU#output