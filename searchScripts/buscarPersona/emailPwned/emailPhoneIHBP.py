import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
# from utils.commonFunctions import randomUserAgent
def randomUserAgent(filename):
    with open(filename) as f:
        lines = f.readlines()
    return random.choice(lines).replace("\n","")
    
class HIBPScraping:
    
    def run(self,p):
        browser = p.chromium.launch(headless=False, slow_mo=50)
        userAgent = randomUserAgent("utils/userAgentsList.txt")
        context = browser.new_context(
            user_agent = userAgent
        )
        return context

    def getHIBPHtml(self, input):
        with async_playwright() as p:
            context = self.run(p)
            page = context.new_page()
            page.goto("https://haveibeenpwned.com/")
            page.fill("input[type=email]", input)
            page.click("button[type=submit]")
            page.is_visible("div.pwnedSites")
            html = page.inner_html("#pwnedWebsitesContainer")
            print(html)
        return html

    def parseHTML(self,**args):
        return "Hi"

Hp = HIBPScraping()
Hp.getHIBPHtml("a")