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
workingListIHBP = []
#get the list of free proxies
def getProxies():
    r = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('tbody')
    proxies = []
    for row in table:
#        if row.find_all('td')[4].text =='elite proxy':
        proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
        proxies.append(proxy)
        # else:
        #     pass
    return proxies

def extractINE(proxy):
    headers = {'User-Agent': randomUserAgent("utils/userAgentsList.txt")}
    try:
        requests.get("https://www.ine.es/widgets/nombApell/nombApell.shtml?L=&w=1189px&h=918px&borc=000000", headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=1)
        workingListINE.append(proxy)
    except requests.ConnectionError as err:
        pass
    return proxy

def extractIHBP(proxy):
    headers = {'User-Agent': randomUserAgent("utils/userAgentsList.txt")}
    try:
        requests.get("https://haveibeenpwned.com/", headers=headers, proxies={'http' : proxy,'https': proxy}, timeout=1)
        workingListIHBP.append(proxy)
    except requests.ConnectionError as err:
        pass
    return proxy
proxylist = getProxies()

with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(extractINE, proxylist)
        executor.map(extractIHBP, proxylist)

with open("utils\Proxies\workingproxylistIHBP.txt", "w") as file:
    for proxy in workingListIHBP:
        file.write(proxy + "\n")
    file.close()

with open("utils\Proxies\workingproxylistIHBP.txt", "w") as file:
    for proxy in workingListINE:
        file.write(proxy + "\n")
    file.close()