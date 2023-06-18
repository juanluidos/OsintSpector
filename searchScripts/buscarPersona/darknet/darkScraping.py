import random
from bs4 import BeautifulSoup
import requests

def randomUserAgent(filename):
    with open(filename) as f:
        lines = f.readlines()
    return random.choice(lines).replace("\n","")

def randomProxyServer(filename):
    with open(filename) as f:
        lines = f.readlines()
        if(len(lines)>1):
            lines = lines[0:len(lines)-1]
        #Si no existe ningún proxy disponible tendríamos q usar nuestra IP (solo me ha ocurrido una vez durante todo el desarrollo, pero por si acaso)
        elif(len(lines)==0):
            return None
    return {"https:": random.choice(lines).rstrip("\n")}


class AhmiaScraping:
    def make_request(self, url):
        proxy = randomProxyServer("utils\Proxies\workingproxylistINE.txt")
        if proxy != None:
            print(f"Scraping Ahmia with proxy: {proxy} for {url}")
        else:
            print(f"Scraping HIBP with no proxy available for {url}")   
        payload= {}
        headers = {
        'timeout': '2.5',
        'User-Agent': randomUserAgent("utils/userAgentsList.txt")
        }
        return requests.request("GET", f"{url}", headers=headers, data=payload, proxies=proxy)

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