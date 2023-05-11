from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import random

class getProxies:
    def __init__(self):
        print("Inicializando script de actualización de Proxies")

    def randomUserAgent(self,filename):
        with open(filename) as f:
            lines = f.readlines()
        return random.choice(lines).replace("\n", "")

    # get the list of free proxies
    def getRawProxies(self):
        r = requests.get('https://free-proxy-list.net/')
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('tbody')
        proxies = []
        for row in table:
            if row.find_all('td')[4].text == 'elite proxy' or row.find_all('td')[4].text == 'transparent':
                proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
                proxies.append(proxy)
        return proxies

    def extractINE(self, proxy):
        workingListINE = []
        headers = {'User-Agent': self.randomUserAgent("utils/userAgentsList.txt")}
        try:
            r = requests.get("https://www.ine.es/widgets/nombApell/nombApell.shtml?L=&w=1189px&h=918px&borc=000000", headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=1)
            soup = BeautifulSoup(r.content, 'html.parser')
            if soup.find_all('form', {"class": 'widgetForm'}):
                workingListINE.append(proxy)
        except:
            pass
        return workingListINE

    def extractAhmia(self, proxy):
        workingListAhmia = []
        headers = {'User-Agent': self.randomUserAgent("utils/userAgentsList.txt")}
        try:
            r = requests.get("https://ahmia.fi", headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=1)
            soup = BeautifulSoup(r.content, 'html.parser')
            if soup.title.string != "Just a moment...":
                workingListAhmia.append(proxy)
        except:
            pass
        return workingListAhmia

    def extractINEFiltrado(self, playwright, proxylist):
        lista = []
        for proxy in proxylist:
            try:
                browser = playwright.chromium.launch(slow_mo=100, headless=False, proxy={"server": proxy})
                headers = self.randomUserAgent("utils/userAgentsList.txt")
                context = browser.new_context(user_agent=headers)
                page = context.new_page()
                page.goto("https://www.ine.es/widgets/nombApell/nombApell.shtml?L=&w=1189px&h=918px&borc=000000")
            except:
                pass
            else:
                lista.append(proxy)
            browser.close()

        return lista

    def obtenerProxiesFiltrados(self):
        proxyRawList = self.getRawProxies()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            workingListINE = list(executor.map(self.extractINE, proxyRawList))
            workingListAhmia = executor.map(self.extractAhmia, proxyRawList)
        workingListINE = [item for sublist in workingListINE for item in sublist]
        workingListAhmia = [item for sublist in workingListAhmia for item in sublist]

        with sync_playwright() as playwright:
            listaFinal = self.extractINEFiltrado(playwright, workingListINE)

        print("Escribiendo proxies disponibles para la página del INE")
        with open("utils/Proxies/workingproxylistINE.txt", "w") as file:
            for proxy in listaFinal:
                file.write(proxy + "\n")

        print("Escribiendo proxies disponibles para la página de Ahmia")
        with open("utils/Proxies/workingproxylistAhmia.txt", "w") as file:
            for proxy in workingListAhmia:
                file.write(proxy + "\n")

