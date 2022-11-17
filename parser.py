import os
import re
import pandas as pd

from bs4 import BeautifulSoup

def search_parse(search_path: str, save: bool = False):
    """
        Parses the search htmls in the given path and returns a list of
        tuples containing the course info and the report id.
    """
    full_data = pd.DataFrame(columns=['name', 'ans_freq', 'report_id'])
    path = search_path

    print("Parsing search path")
    print(f"Found {len(os.listdir(search_path))} directories")
    # loop through all the directories in the path
    for directory in os.listdir(search_path):
        data = pd.DataFrame(columns=['name', 'ans_freq', 'report_id']) # Reset for each program
        path = search_path+"/"+directory

        # check if the file is a directory
        if not os.path.isdir(path):
            continue # skip if not a directory
    
        print(f"  Found directory {directory}.")
        # loop through all the files in the program directory
        for f in os.listdir(path):
            if f.endswith(".html"):
                with open(path + "/" + f, 'r') as html:
                    print(f"    Parsing {f}...")
                    soup = BeautifulSoup(html.read(), 'html.parser')
                    rows = soup.find_all("tr", {"class": "srtbl-row"})

                    print(f"      Found {len(rows)} courses")
                    for row in rows:
                        name = row.find('th').text
                        ans_freq = row.find('td').text
                        # regex get the id from the on click argument. Ex: 'showReport('3284|-');return false;'
                        report_link = row.find('a')
                        if report_link is not None:
                            report_id = int(re.search(r"(\d+)", report_link['onclick']).group(1))
                        else:
                            report_id = None
                            print(f"      Course {name} has no report")
                        data = pd.concat([data, pd.DataFrame([[name, ans_freq, report_id]], columns=['name', 'ans_freq', 'report_id'])])
        
        print(f"  Done parsing directory {directory}")
        if save:
            data.to_csv(path+"/report_parse.csv", index=False, sep=";")
        full_data = pd.concat([full_data, data])

    if save:
        full_data.to_csv(search_path+"/report_parse.csv", index=False, sep=";")
    print("Done parsing search path")
    return full_data

def parse_and_update_search():
    search_parse("./data/bp/search", save=True)
    search_parse("./data/mp/search", save=True)

parse_and_update_search()