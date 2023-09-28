import os
from pathlib import Path
from pprint import pprint
from automateda11y.pw.settings import Settings
from playwright.sync_api import sync_playwright
from automateda11y.pw.htmlcsrunner import HtmlCsRunner
from automateda11y.pw.modal.params import Params
from automateda11y.pw.a11y.engine import Engine
from automateda11y.pw.util.a11y import A11y

def root_dir():
    return Path(__file__).parent.parent.__str__()

class MyA11y:

    def __init__(self, page):
        self.page = page

    def execute(self, engine, params=None):
        # js_text = Path(root_dir() + "/resources/js/", engine.name.lower() + ".js").read_text()
        js_text = Path(os.path.join(Setting.Package_directoty, "/automateda11y/pw") + "/resources/js/", engine.name.lower() + ".js").read_text()
        self.page.evaluate("async (js)=> await window.eval(js)", js_text)
        data = self.page.evaluate("async (param) => await axeData(param)", params.to_json()) if engine.value == 2 else \
            self.page.evaluate("async (param) => await getData(param)", params.to_json())
        return data

class MyHtmlCsRunner(HtmlCsRunner):

    def __init__(self, page):
        self.a11y = MyA11y(page)
        self.params = Params()

    def execute(self):
        data = self.a11y.execute(Engine.HTMLCS, self.params)
        return data

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.class2learn.com")
    data = MyHtmlCsRunner(page)
    data.set_standard('WCAG2AA') # Need to mentioned WCAG standard level types here
    json_data = data.execute()
    res=''
    if json_data:
        res = json_data.get('results')
    errors=[]
    warnings=[]
    notices=[]
    if res:
        for i in res:
            if i['type'] == 1:
                errors.append(i)
            elif i['type'] == 2:
                warnings.append(i)
            else:
                notices.append(i)
        data={'errors':errors,'warnings':warnings,'notices':notices}
    else:
        data = {}
        raise Exception("Unable to fetch the page accessbility data")
    pprint(data)
    browser.close()
    