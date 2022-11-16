"""
mapper.py - mapping the input fields in the search page to their ids
"""
import os
import pandas as pd

from datetime import date
from bs4 import BeautifulSoup
from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class Mapper:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')

        # Create a new instance of the Chrome driver using the manager to download the latest version
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        # Create a request interceptor
        def interceptor(request):
            # Set custom request headers
            del request.headers['Referer']  # Delete the ref header first
            request.headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
            request.headers["accept-language"] = "en-GB,en;q=0.5"
            request.headers["cache-control"] = "max-age=0",
            request.headers["content-type"] = "application/x-www-form-urlencoded"
            request.headers["sec-ch-ua"] = "\"Brave\";v=\"107\", \"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\""
            request.headers["sec-ch-ua-mobile"] = "?0"
            request.headers["sec-ch-ua-platform"] = "\"Windows\""
            request.headers["sec-fetch-dest"] = "document"
            request.headers["sec-fetch-mode"] = "navigate"
            request.headers["sec-fetch-site"] = "same-origin"
            request.headers["sec-fetch-user"] = "?1"
            request.headers["sec-gpc"] = "1"
            request.headers["upgrade-insecure-requests"] = "1"
            request.headers["cookie"] = "AspxAutoDetectCookieSupport=1; .SRPUB_SessionId=tkdwqk5hios1rkdohz11w5pq"
            request.headers["Referer"] = "https://course-eval.portal.chalmers.se/sr/ar/4257/sv"
            request.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Set the interceptor on the driver
        self.driver.request_interceptor = interceptor

        # Create data folder if it doesn't exist
        today = date.today()
        self.data_location = today.strftime("data_%Y%m%d")
        os.makedirs(self.data_location, exist_ok=True)
        os.makedirs(self.data_location+"/mp", exist_ok=True)
        os.makedirs(self.data_location+"/bp", exist_ok=True)

    def get_data(self):
        if self.driver.page_source is None:
            print("No data collected")
        return self.driver.page_source

    def fetch(self, master=False):
        """
            Fetches the search page for either master programme or 
            bachelor programme and saves the resulting html in 
            self.data.
        """
        if master:
            url = "https://course-eval.portal.chalmers.se/sr/ar/4248/sv" # Search page for master programmes
        else:
            url = "https://course-eval.portal.chalmers.se/sr/ar/4257/sv" # Search page for bachelor programmes
        self.driver.get(url)
        return self.driver.page_source

    def save_html(self, filename):
        """
            Saves the data fetched to a file
        """
        with open(filename, 'w') as f:
            f.write(self.driver.page_source)

    def parse(self, text):
        """
            Parses the html and returns a dictionary of the input fields
            and their ids and returns a list of data frames with the 
            columns ['tag', 'name', 'sid'].
        """
        soup = BeautifulSoup(text, 'html.parser')
        categories = {
            "Programme": soup.find("div", {"id": "treeCategories1"}),
            "Year": soup.find("div", {"id": "treeCategories2"}),
            "LP": soup.find("div", {"id": "treeCategories3"})
          }
        fields = {}

        for category, div in categories.items():
            lis = div.find_all('li')
            field = pd.DataFrame(columns=['tag', 'name', 'sid'])

            for li in lis:
                if li.text != "Markera alla":
                    # Has to handle ZBASS- Tekniskt basår, TSLOG - Sjöfart och logistik, 2013/2014 or Läsperiod 1
                    tag = li.text
                    name = ""

                    if "-" in li.text: 
                        keys = li.text.split("-")
                        tag = keys[0].strip()
                        name = keys[1].strip()
                    
                    sid = li.find('input')['tag']
                    # use concat to add a new row to the dataframe
                    field = pd.concat([field, pd.DataFrame([[tag, name, sid]], columns=['tag', 'name', 'sid'])], ignore_index=True)
            fields[category] = field

        return fields

    def parse_file(self, filename):
        """
            Parses the html file and returns a dictionary of the input fields
            and their ids.
        """
        with open(filename, 'r') as f:
            text = f.read()
        return self.parse(text)

    def update_map(self):
        """
            Updates the map files with the new data
        """

        # Fetch the data
        self.fetch(master=True)
        self.save_html(self.data_location+"/mp/search.html")
        print("Saved master search page")
        self.fetch(master=False)
        self.save_html(self.data_location+"/bp/search.html")
        print("Saved bachelor search page")

        # Parse the data
        mp_fields = self.parse_file(self.data_location+"/mp/search.html")
        print("Parsed master search page")
        bp_fields = self.parse_file(self.data_location+"/bp/search.html")
        print("Parsed bachelor search page")

        # Save the data
        for category, field in mp_fields.items():
            field.to_csv(self.data_location+"/mp/"+category+"_map.csv", index=False, sep=';')
        print("Saved master map")

        for category, field in bp_fields.items():
            field.to_csv(self.data_location+"/bp/"+category+"_map.csv", index=False, sep=';')
        print("Saved bachelor map")

mapper = Mapper()
mapper.update_map()
mapper.driver.quit()

#mapper.fetch(master=True)
#mapper.save_html("data/mp_search.html")
#mapper.fetch(master=False)
#mapper.save_html("data/bp_search.html")
#parse = mapper.parse_file("./data_20221116/bp_search.html")
#for category, field in parse.items():
#    field.to_csv(category+"_map.csv", index=False, sep=';')
#print(parse.to_string(index=False))
