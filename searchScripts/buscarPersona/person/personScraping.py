import asyncio
import random
import time
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup

#from utils.commonFunctions import randomUserAgent

def randomUserAgent(filename):
    with open(filename) as f:
        lines = f.readlines()
    return random.choice(lines).replace("\n","")

class INEScrapingName:
    async def run(self,p):
        browser = await p.chromium.launch(slow_mo=100, headless=True)
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
        result = await self.getINEHtmlName(input)
        print("Searching name frequency on INE")
        if(result[1]):
            datos = result[0].findAll("span",{"class":"widgetResultTotal"})
            return datos[1].getText(), datos[2].getText()
        else:
            return "menor de 5"

class INEScrapingSurName:
    async def run(self,p):
        browser = await p.chromium.launch(slow_mo=100, headless=True)
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
        result = await self.getINEHtmlSurName(input)
        resultList = []
        print("Searching surname frequency on INE")
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