import requests
from bs4 import BeautifulSoup

URL = 'https://course-eval.portal.chalmers.se/sr/ar/4257/sv'
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
    def __init__(self, programmes, years, lps=['1049','1050','1051','1052']):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.programmes = programmes # MAX 5
        self.years = years # MAX 5 (only in bachelor programmes page)
        self.lps = lps # LP1, LP2, LP3, LP4

    def get_data(self):
        if self.data is None:
            print("No data collected")
        return self.data

    def fetch(self):
        """
            Preforms a search on courses using the programmes, years and 
            lps as filters for the search through a POST request and 
            saves the resulting html in self.data. 
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
        self.data = self.session.post(URL, data=data)
        return self.data

    def export_html(self, filename):
        with open(filename, 'w') as f:
            f.write(self.data.text)

    def update_mp_courses(self):
        """
            Updates the courses in the master program page.
            The courses are saved in self.mp_courses
        """
        self.mp_courses = []
        soup = BeautifulSoup(self.data.text, 'html.parser')
        for course in soup.find_all('div', class_='course'):
            self.mp_courses.append(course.find('a').text)

collector = Collector()
collector.programmes = ['275','1477','147','224','162'] # MPALG
collector.years = ['49'] # 2013/2014
collector.fetch()
collector.export_html('data/test.html')