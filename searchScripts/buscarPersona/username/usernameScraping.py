import json
import random
import string

import requests
import urllib3
import threading
import logging

from utils.commonFunctions import randomUserAgent


def usernameScrapping(username, inputfile):
    #todos los sitios encontrados con username demandado
    all_found_sites = []

    #Sistema de logs
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
                'User-Agent': randomUserAgent("utils/userAgentsList.txt")
            }

    def web_call(location):
        try:
            # Make web request for that URL, timeout in X secs and don't verify SSL/TLS certs
            resp = requests.get(location, headers=headers, timeout=30, verify=False)
        except requests.exceptions.Timeout:
            return f' !  ERROR: {location} CONNECTION TIME OUT. Try increasing the timeout delay.'
        except requests.exceptions.TooManyRedirects:
            return f' !  ERROR: {location} TOO MANY REDIRECTS. Try changing the URL.'
        except requests.exceptions.RequestException as e:
            return f' !  ERROR: CRITICAL ERROR. {e}'
        else:
            return resp


    def random_string(length):
        return ''.join(
            random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(length))

    # Suppress HTTPS warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



    with open(inputfile, 'r', errors='ignore') as data_file:
        data = json.load(data_file)

    def check_site(site, username):
        # Examine the current validity of the entry
        if not site['valid']:
            return logging.info(f" *  Skipping {site['name']} - Marked as not valid.")

        if not site['known_accounts'][0]:
            return logging.info(f" *  Skipping {site['name']} - No valid user names to test.")

        # Set the username
        if username:
            uname = username
        else:
            # if no username specified Pull the first user from known_accounts and replace the {account} with it
            known_account = site['known_accounts'][0]
            uname = known_account

        url = site['check_uri'].replace("{account}", uname)

        # Perform initial lookup
        logging.info(f" >  Looking up {url}")
        r = web_call(url)
        if isinstance(r, str):
            # We got an error on the web call
            return logging.error(r)
        else:
            # Analyze the responses against what they should be
            code_match = r.status_code == int(site['account_existence_code'])
            if site['account_existence_string']:
                string_match = r.text.find(site['account_existence_string']) >= 0
            else:
                string_match = 0

            if username:
                if code_match and string_match:
                    if 'pretty_uri' in site:
                        url = site['pretty_uri'].replace("{account}", uname)
                    all_found_sites.append((site["name"], site["category"], url))
                    return
            else:
                if code_match and string_match:
                    # logging.info('     [+] Response code and Search Strings match expected.')
                    # Generate a random string to use in place of known_accounts
                    url_fp = site['check_uri'].replace("{account}", random_string(20))
                    r_fp = web_call(url_fp)
                    if isinstance(r_fp, str):
                        # If this is a string then web got an error
                        return logging.error(r_fp)

                    code_match = r_fp.status_code == int(site['account_existence_code'])
                    string_match = r_fp.text.find(site['account_existence_string']) > 0

    # Start threads
    threads = []

    for site_ in data['sites']:
        x = threading.Thread(target=check_site, args=(site_, username), daemon=True)
        threads.append(x)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return all_found_sites

