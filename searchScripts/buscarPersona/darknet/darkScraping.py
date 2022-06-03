import asyncio
import random
import time
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
import requests
# from utils.commonFunctions import randomUserAgent

def randomUserAgent(filename):
    with open(filename) as f:
        lines = f.readlines()
    return random.choice(lines).replace("\n","")


class AhmiaScraping:
    def make_request(self, url):

        payload={}
        headers = {
        'timeout': '2.5',
        'User-Agent': randomUserAgent("utils/userAgentsList.txt")
        }
        return requests.request("GET", f"{url}", headers=headers, data=payload)

    def getAhmiaHtml(self, url):
#es muy diferente aqui lo tengo copiado de como seria con la api de IHBP mirar videos del tio asi cojo solo el html y listo combinado con request
        response = self.make_request(url)

        if response.status_code == 200:
            htmlData = response.text
            soup = BeautifulSoup(htmlData, "html.parser")

        elif response.status_code == 404:
            print(
                f"No Darknet sites found for {url} using Ahmia"
            )
            soup = ""
        else:
            print("Could not contact Ahmia for " + url)
            print(response.status_code)
            soup = ""

        return soup

    def parseHTML(self, url):
        soup = self.getAhmiaHtml(url)
        
        if(soup.find(id="noResults")):
            return []
        else:
            resultsArray = []
            results = soup.findAll("li",{"class": "result"})
            for result in results:
                title = result.find("a").text.replace(" ", "").replace("\n","")
                link = result.find("a")["href"].partition("url=")[2]
                description = result.find("p").text
                lastSeen = result.find("span", {"class": "lastSeen"})["data-timestamp"]
                resultsArray.append([title, link, description, lastSeen])
            return resultsArray