import asyncio
import random
import time
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
# from utils.commonFunctions import randomUserAgent
def randomUserAgent(filename):
    with open(filename) as f:
        lines = f.readlines()
    return random.choice(lines).replace("\n","")
    
class HIBPScraping:

    async def run(self,p):
        browser = await p.chromium.launch(slow_mo=100)
        userAgent = randomUserAgent("utils/userAgentsList.txt")
        context = await browser.new_context(
            user_agent = userAgent
        )
        return context

    async def getHIBPHtml(self, input):
        breaches = True
        pastes = True
        soupSites = ""
        soupPastes = ""
        async with async_playwright() as p:
            context = await self.run(p)
            page = await context.new_page()
            await stealth_async(page) #stealth
            await page.goto("https://haveibeenpwned.com/")
            time.sleep(1)
            await page.fill("input[type=email]", input)
            await page.click("button[type=submit]")
            await page.is_visible("div.pwnedRow")

            try:
                await page.click("#pwnedSites", timeout=5000)
            except:
                breaches = False
            else:
                htmlSites = await page.inner_html("#pwnedSites")
                soupSites = BeautifulSoup(htmlSites, "html.parser")

            try:
                await page.click("#pastes", timeout=5000)
            except:
                pastes = False
            else:
                htmlPastes = await page.inner_html("#pastes")
                soupPastes = BeautifulSoup(htmlPastes, "html.parser")


        return soupSites, breaches, soupPastes , pastes

    async def parseHTML(self, input):
        result = await self.getHIBPHtml(input)
        breachesArray = []
        pastesArray = []
        if result[1] == True:
            resultsBreaches = result[0].findAll("div", {"class": "pwnedSearchResult pwnedWebsite panel-collapse collapse in"})
            for breach in resultsBreaches:
                titleBr = breach.find("span", {"class": "pwnedCompanyTitle"}).text

                linkBr = breach.find("a")["href"]
                descriptionBr = breach.find("p").text

                compromisedDataBr = breach.find("p", {"class": "dataClasses"}).text
                breachesArray.append([titleBr, linkBr, descriptionBr, compromisedDataBr])

        if result[3] == True:
            resultsPastes = result[2].find("table", {"class": "table-striped"}).find("tbody").findAll("tr")
            for paste in resultsPastes:
                tittlePasted = paste.find("a").text
                linkPasted = paste.find("a")["href"]
                datePasted = paste.find("td", {"class": "pasteDate"}).text
                emailsPasted = paste.find("td", {"class": "text-right"}).text

                pastesArray.append([tittlePasted,linkPasted, datePasted, emailsPasted])

        return breachesArray, pastesArray