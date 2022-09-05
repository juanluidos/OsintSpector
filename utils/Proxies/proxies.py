import requests
import concurrent.futures
proxyList = []
workingProxys = []
with open("utils\Proxies\proxylist.txt", "r") as f:
    reader = f.readlines()
    for row in reader:
        proxyList.append(row.rstrip("\n"))
    f.close()

def extract(proxy):
    try:
        r = requests.get("https://haveibeenpwned.com", proxies ={"http":proxy, "https":proxy}, timeout=1)
        print(r.json(), "working", proxy)
        workingProxys.append(proxy)
    except:
        pass
    return workingProxys

with concurrent.futures.ThreadPoolExecutor() as exector:
    exector.map(extract,proxyList)