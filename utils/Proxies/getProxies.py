import json
from subprocess import PIPE, Popen
import sys
import threading
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import random
def randomUserAgent(filename):
    with open(filename) as f:
        lines = f.readlines()

    return random.choice(lines).replace("\n","")

def runProxyScript():
    print("Running proxy updating script")
    Popen([sys.executable,"utils/Proxies/getProxies.py"], stdin=PIPE, stdout=PIPE, stderr=PIPE)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

workingListINE = []
workingListHIBP = []
workingListAhmia = []

#get the list of free proxies
def getProxies():
    r = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('tbody')
    proxies = []
    for row in table:
        # if row.find_all('td')[4].text =='elite proxy' or row.find_all('td')[4].text =='transparent':
        proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
        proxies.append(proxy)
    return proxies

def extractINE(proxy):
    headers = {'User-Agent': randomUserAgent("utils/userAgentsList.txt")}
    try:
        requests.get("https://www.ine.es/widgets/nombApell/nombApell.shtml?L=&w=1189px&h=918px&borc=000000", headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=1)
        workingListINE.append(proxy)
    except requests.exceptions.Timeout as err:
        pass
    except requests.exceptions.RequestException as err:
        pass
    except json.decoder.JSONDecodeError as err:
        pass
    return workingListINE

def extractIHBP(proxy):
    headers = {'User-Agent': randomUserAgent("utils/userAgentsList.txt")}
    try:
        r = requests.get("https://haveibeenpwned.com/", headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=1)
        soup = BeautifulSoup(r.content, 'html.parser')
        #Si el titulo contiene Just a moment significa que han pillado q es un posible bot usando el proxy
        #TODO aún el INE no ha detectado que fuera un bot entonces aun no se como actua ante estos casos y html es por eso aun esta copiado del ScrapingHIBP
        if(soup.title.string == "Just a moment..."):
            raise Exception("Err")
        workingListHIBP.append(proxy)
    except requests.exceptions.RequestException as err:
        pass
    return workingListHIBP

def extractAhmia(proxy):
    headers = {'User-Agent': randomUserAgent("utils/userAgentsList.txt")}
    try:
        r = requests.get("https://ahmia.fi/search/", headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=1)
        soup = BeautifulSoup(r.content, 'html.parser')
        #Si el titulo contiene Just a moment significa que han pillado q es un posible bot usando el proxy
        #TODO aún el INE no ha detectado que fuera un bot entonces aun no se como actua ante estos casos y html es por eso aun esta copiado del ScrapingHIBP
        if(soup.title.string == "Just a moment..."):
            raise Exception("Err")
        workingListAhmia.append(proxy)
    except requests.exceptions.RequestException as err:
        pass
    return workingListAhmia

proxylist = getProxies()

with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(extractINE, proxylist)
        executor.map(extractIHBP, proxylist)
        executor.map(extractAhmia, proxylist)

with open("utils\Proxies\workingproxylistHIBP.txt", "w") as file:
    for proxy in workingListHIBP:
        file.write(proxy + "\n")
    file.close()

with open("utils\Proxies\workingproxylistINE.txt", "w") as file:
    for proxy in workingListINE:
        file.write(proxy + "\n")
    file.close()

with open("utils\Proxies\workingproxylistAhmia.txt", "w") as file:
    for proxy in workingListAhmia:
        file.write(proxy + "\n")
    file.close()