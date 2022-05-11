from time import sleep
import asyncio
import requests
import os
uri = ""
apiKeyPwned= os.getenv("API_KEY")

async def make_request(
        url,
        api_key,
        meth="GET",
        timeout=20,
        redirs=True,
        data=None,
        params=None,
        verify=True,
        auth=None,
    ):

        response = requests.request(
            url=url,
            headers =  {"hibp-api-key":api_key, 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36' },
            method=meth,
            timeout=timeout,
            allow_redirects=redirs,
            data=data,
            params=params,
            verify=verify,
            auth=auth,
            )
            # response = requests.request(url="http://127.0.0.1:8000", headers=self.headers, method=meth, timeout=timeout, allow_redirects=redirs, data=data, params=params)
        return response


async def emailScrapping(target, api_key):
        all_found_sites = []
        pwned = 0
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{target}"
        response = await make_request(url, api_key)
        if response.status_code not in [200, 404]:
            print("Could not contact HIBP v3 for " + target)
            print(response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                for d in data:  # Returned type is a dict of Name : Service
                    for _, ser in d.items():
                        all_found_sites.append(("HIBP3", ser))
                        pwned += 1

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
                print(
                    f"HIBP v3: got API response code {response.status_code} for {target}"
                )

        return all_found_sites



# def get_hibp3_pastes(self):
#         try:
#             c.info_news("[" + self.target + "]>[hibp-paste]")
#             sleep(1.3)
#             url = f"https://haveibeenpwned.com/api/v3/pasteaccount/{self.target}"

#             response = self.make_request(url)
#             if response.status_code not in [200, 404]:
#                 c.bad_news("Could not contact HIBP PASTE for " + self.target)
#                 print(response.status_code)
#                 print(response)
#                 return

#             if response.status_code == 200:

#                 data = response.json()
#                 for d in data:  # Returned type is a dict of Name : Service
#                     self.pwned += 1
#                     if "Pastebin" in d["Source"]:
#                         self.data.append(
#                             ("HIBP3_PASTE", "https://pastebin.com/" + d["Id"])
#                         )
#                     else:
#                         self.data.append(("HIBP3_PASTE", d["Id"]))

#                 c.good_news(
#                     "Found {num} pastes for {target} using HIBP v3 Pastes".format(
#                         num=len(data), target=self.target
#                     )
#                 )

#             elif response.status_code == 404:
#                 c.info_news(
#                     f"No pastes found for {self.target} using HIBP v3 PASTE"
#                 )
#             else:
#                 c.bad_news(
#                     f"HIBP v3 PASTE: got API response code {response.status_code} for {self.target}"
#                 )

#         except Exception as ex:
#             c.bad_news("HIBP v3 PASTE error: " + self.target)
#             print(ex)