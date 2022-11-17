import os
import requests
import pandas as pd

from collections import namedtuple
from bs4 import BeautifulSoup

BP_URL = 'https://course-eval.portal.chalmers.se/sr/ar/4257/sv'
MP_URL = 'https://course-eval.portal.chalmers.se/sr/ar/4248/sv'

# Headers to use when fetching the reports and doing the POST requests to bypass the login
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-GB,en;q=0.5",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "sec-ch-ua": "\"Brave\";v=\"107\", \"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "cookie": "AspxAutoDetectCookieSupport=1; .SRPUB_SessionId=tkdwqk5hios1rkdohz11w5pq",
    "Referer": "https://course-eval.portal.chalmers.se/sr/ar/4257/sv",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  }

class Collector:
    def __init__(self, programmes: list, years: list, lps=['1049','1050','1051','1052']):
        """
            programmes, years and lps has to be the correct id taken 
            from mapper.py
        """
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.programmes = list(map(lambda x: str(x), programmes)) # MAX 5
        self.years = list(map(lambda x: str(x), years)) # MAX 5 (only in bachelor programmes page)
        self.lps = list(map(lambda x: str(x), lps)) # LP1, LP2, LP3, LP4

    def fetch(self, search_page: str):
        """
            Preforms a search on courses using the programmes, years and 
            lps as filters for the search through a POST request and 
            returns the html in the response. 
        """
        if not self.programmes or not self.years:
            print("No programmes or years selected")
            return
        if len(self.programmes) > 5 or len(self.years) > 5:
            print("Too many programmes or years selected. The max is 5 each")
            return

        data = "&".join(["hfSelection=1",
            "hfCategory1="+"%2C".join(self.programmes),
            "hfCategory2="+"%2C".join(self.years),
            "hfCategory3="+"%2C".join(self.lps)])
        self.data = self.session.post(search_page, data=data)
        return self.data

    def export_html(self, filename):
        with open(filename, 'w') as f:
            f.write(self.data.text)
            
def get_report(report_id: int, save: bool = False):
    """
        Gets the report html from the given report id and returns the html
        as a string.
    """
    url = f"https://course-eval.portal.chalmers.se/SR/Report/Token/{report_id}/0/0"
    print(f"Getting report {report_id}")
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        print("  Success")
        if save:
            with open(f"./data/bp/reports/{report_id}.html", 'w') as f:
                f.write(r.text)
        return r.text
    else:
        print("  Failed")
        return None

def get_reports(report_ids: list, save: bool = False):
    """
        Gets the report html from the given report ids and returns a list of
        tuples containing the report id and the html.
    """
    reports = []
    for report_id in report_ids:
        report = get_report(report_id, save)
        if report is not None:
            reports.append((report_id, report))
    return reports

def update_courses(search_page: str, map_location: str):
    """
        Updates the mapping of course id to the program and the reports
        and then saves the mapping in a csv file.
    """
    lps = pd.read_csv(map_location+"LP_map.csv", sep=";")['sid'].tolist()
    programmes = pd.read_csv(map_location+"Programme_map.csv", sep=";")
    years = pd.read_csv(map_location+"Year_map.csv", sep=";")['sid'].tolist()

    for index, program in programmes.iterrows():
        i = 0
        print(f"Fetching {program['name']} ({i})... ({index+1}/{len(programmes)})")
        for j in range(0, len(years), 5):
            collector = Collector([program['sid']], years[j:j+5], lps)
            location = map_location+"search/"+program['tag']+"/"
            os.makedirs(location, exist_ok=True)
            
            collector.fetch(search_page)
            collector.export_html(location + str(i) + ".html")
            i += 1

# Load the csv data
update_courses(BP_URL, "./data/bp/")
update_courses(MP_URL, "./data/mp/")
#df = pd.read_csv(data_path+'data.csv')
#collector = Collector()
#collector.programmes = ['275','1477','147','224','162'] # MPALG
#collector.years = ['49'] # 2013/2014
#collector.fetch()
#collector.export_html('data/test.html')