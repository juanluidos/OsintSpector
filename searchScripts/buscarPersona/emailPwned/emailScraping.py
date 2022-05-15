import requests

from utils.commonFunctions import randomUserAgent

def make_request(target,api_key, url):

    payload={}
    headers = {
    'hibp-api-key': str(api_key),
    'format': 'application/json',
    'timeout': '2.5',
    'HIBP': str(api_key),
    'User-Agent': randomUserAgent("utils/userAgentsList.txt"),
    }
    return requests.request("GET", f"{url}{target}", headers=headers, data=payload)


def emailBreached(target, api_key):
    all_found_sites = []
    response = make_request(target,api_key,"https://haveibeenpwned.com/api/v3/breachedaccount/")

    if response.status_code == 200:
        data = response.json()
        for d in data:  # Returned type is a dict of Name : Service
            for _, ser in d.items():
                all_found_sites.append(ser)

        print(
            "Found {num} breaches for {target} using HIBP v3".format(
                num=len(data) - 1, target=target
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

def emailPasted(target, api_key):
    all_found_sites = []
    response = make_request(target,api_key, "https://haveibeenpwned.com/api/v3/pasteaccount/")
    if response.status_code == 200:
        data = response.json()
        all_found_sites = data

        print(
            "Found {num} times pasted for {target} account using HIBP v3".format(
                num=len(data) - 1, target=target
            )
        )
    elif response.status_code == 404:
        print(
            f"No pasted found for {target} account using HIBP v3"
        )
    else:
        print("Could not contact HIBP v3 for " + target)
        print(response.status_code)
    return all_found_sites

def emailBreachedExpanded(target, api_key):
    
    all_found_sites = emailBreached(target, api_key)
    extendedInfo_sites = []
    for site in all_found_sites:
        response = make_request(site, api_key,"https://haveibeenpwned.com/api/v3/breach/")
        if response.status_code == 200:
            data = response.json()
            extendedInfo_sites.append(data)

        elif response.status_code == 404:
            print(
                f"No breaches found for {target} using HIBP v3"
            )
        else:
            print("Could not contact HIBP v3 for " + target)
            print(response.status_code)
        
    print(f"Los sitios donde se leakearon el correo con información sensible fue:{all_found_sites}")
    return extendedInfo_sites

