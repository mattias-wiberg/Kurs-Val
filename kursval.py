from mapper import Mapper
import parser as p
import scraper as s

""" Generates the report.csv file. Complete scrape """

mapper = Mapper()
mapper.update_map()
mapper.driver.quit()

s.update_courses(s.BP_URL, "./data/bp/")
s.update_courses(s.MP_URL, "./data/mp/")

p.update_searches()

s.update_reports("./data/bp/search/report_map.csv")
s.update_reports("./data/mp/search/report_map.csv")

p.parse_reports("./data/reports", save=True)