#USANDO LA KEY DE IHBP
import time
import requests
from utils.commonFunctions import randomUserAgent

class HIBPApi:
    def __init__(self, api_key):
        self.api_key = api_key

    def make_request(self, target, url):
        payload={}
        headers = {
        'hibp-api-key': str(self.api_key),
        'format': 'application/json',
        'timeout': '5',
        'User-Agent': randomUserAgent("utils/userAgentsList.txt"),
        }
        #truncateResponse=false para que nos de los datos completos de cada breach
        return requests.request("GET", f"{url}{target}?truncateResponse=false"	, headers=headers, data=payload)

    def getBreached(self, target):
        all_found_sites = []
        response = self.make_request(target,"https://haveibeenpwned.com/api/v3/breachedaccount/")

        if response.status_code == 200:
            data = response.json()
            for d in data:
                found_site = []
                for key,value in d.items():
                    if key == "Title":
                        found_site.append(value)
                    if key == "Domain":
                        found_site.append(value)
                    if key == "Description":
                        found_site.append(value)
                    if key == "DataClasses":
                        found_site.append(value)
                all_found_sites.append(found_site)

            print(
                "Found {num} breaches for {target} using HIBP v3".format(
                    num=len(data), target=target
                )
            )
        elif response.status_code == 404:
            print(
                f"No breaches found for {target} using HIBP v3"
            )
        else:
            print("Could not contact HIBP v3 for " + target)
            print(response.status_code)

        return all_found_sites

    def getPasted(self, target):
        all_found_sites = []
        response = self.make_request(target, "https://haveibeenpwned.com/api/v3/pasteaccount/")
        if response.status_code == 200:
            data = response.json()
            for d in data:
                found_site = []
                for key,value in d.items():
                    if key == "Title":
                        found_site.append(value)
                    if key == "Id":
                        found_site.append(value)
                    if key == "Date":
                        found_site.append(value)
                        print(value)
                    if key == "EmailCount":
                        found_site.append(value)
                    print(found_site)
                all_found_sites.append(found_site)

            print(
                "Found {num} times pasted for {target} account using HIBP v3".format(
                    num=len(data), target=target
                )
            )
        elif response.status_code == 404:
            print(
                f"No pasted found for {target} account using HIBP v3"
            )
        else:
            print("Could not contact HIBP v3 for " + target + " error: "+ response.status_code)
        return all_found_sites

    async def getPwnedData(self, target):
        breached = self.getBreached(target)
        if not target.isnumeric():
            time.sleep(7)
            pasted = self.getPasted(target)
            return breached, pasted
        return breached
