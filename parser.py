import os
import re
import pandas as pd
import str_utils as str_utils
from tqdm import tqdm

from bs4 import BeautifulSoup

def parse_search(search_path: str, save: bool = False):
    """
        Parses the search htmls in the given path and returns a data
        frame containing the programme, course_tag and report_id.
    """
    cols = ['programme', 'course_tag', 'report_id']
    full_data = pd.DataFrame(columns=cols)
    path = search_path

    print("Parsing search path")
    print(f"Found {len(os.listdir(search_path))} directories")
    # loop through all the directories in the path
    for programme_dir in os.listdir(search_path):
        data = pd.DataFrame(columns=cols) # Reset for each program
        path = search_path+"/"+programme_dir

        # check if the file is a directory
        if not os.path.isdir(path):
            continue # skip if not a directory
    
        print(f"  Found directory {programme_dir}.")
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
                        course_tag = str_utils.parse_course_text(name)[0]
                        # regex get the id from the on click argument. Ex: 'showReport('3284|-');return false;'
                        report_link = row.find('a')
                        if report_link is not None:
                            report_id = int(re.search(r"(\d+)", report_link['onclick']).group(1))
                        else:
                            report_id = None
                            print(f"      Course {name} has no report")
                        data = pd.concat([data, pd.DataFrame([[programme_dir, course_tag, report_id]], columns=cols)])
        
        print(f"  Done parsing directory {programme_dir}")
        if save:
            data.to_csv(path+"/report_map.csv", index=False, sep=";") # Not really needed, but nice for debugging
        full_data = pd.concat([full_data, data])

    if save:
        full_data.to_csv(search_path+"/report_map.csv", index=False, sep=";")
    print("Done parsing search path")
    return full_data

def update_searches():
    parse_search("./data/bp/search", save=True)
    parse_search("./data/mp/search", save=True)

report_cols = ['course_tag', 'course_name', 'period', 'reading_period', 'report_id', 'answers_count', 'respondents_count', 'category', 'question', 'mean', 'median']

def parse_report(report_id: int, report: str):
    """
        Parses the given report html and returns a dict with the parsed data.
    """
    soup = BeautifulSoup(report, 'html.parser')
    report_cols = ['course_tag', 'course_name', 'period', 'reading_period', 'report_id', 'answers_count', 'respondents_count', 'category', 'question', 'mean', 'median']
    df = pd.DataFrame(columns=report_cols)

    # Check if the report is empty
    if len(soup.find_all('div', {'class': 'artBaseTable'})) < 3:
        print(f"Report {report_id} is empty")
        return df

    course = soup.find('h1').text
    course_tag, course_name, period, reading_period = str_utils.parse_course_text(course)
    course_info = soup.find('p').text
    numbers = re.findall(r'\d+', course_info)
    answers_count = int(numbers[1])
    respondents_count = int(numbers[0])

    categories_divs = soup.find_all('div', {'class': 'artBaseTable'})
    for div in categories_divs:
        if div.find('table') is None: # Category div no tables
            continue

        h3 = div.find('h3')
        if h3 is not None:
            category = h3.text.strip()
        else:
            category = div.find('div', {'class': 'srTextWrapper'}).text.strip()

        category_start_index = re.search(r'[a-zA-ZåäöÅÄÖ]', category).start() # Find the first letter in the category
        category = category[category_start_index:] # remove the number from the category name

        questions_tables = div.find_all('table')
        for table in questions_tables: # Skips the categories without any tables/"numerics" (ex: "Vad i kursen bör bevaras till nästa kursomgång?")
            table_h1 = table.find('tr', {'class': 'srtbl-h1'})
            if table_h1 is None: # Skip the table if it has no header
                continue
            table_title = table_h1.text
            if table_title != "\xa0MeanMedian" and table_title != "\xa0MedelvärdeMedian": # Skip the table if it has no mean/median
                continue
            question_text = table.find('th', {'class': 'srtbl-rh'}).text.strip()
            stat_cells = table.find_all('td', {'class': 'srtbl-cell'})
            question_mean = stat_cells[0].text.strip()
            question_median = stat_cells[1].text.strip()
            df = pd.concat([df, 
                pd.DataFrame(
                    [[course_tag, course_name, period, reading_period, report_id, answers_count, respondents_count, category, question_text, question_mean, question_median]], columns=report_cols
                )
            ])
        
        end_categories = ["Overall impression", "Sammanfattande intryck", "Vad är Ditt sammanfattande intryck av kursen?", "What is your overall impression of the course?"]
        if category in end_categories:
            # Stop parsing after the overall impression category since after that it is just very detailed questions
            break

    return df

def parse_reports(reports_path: str, save: bool = False):
    """
        Parses the given reports and returns a list of data frames with the 
        parsed data.
    """
    print("Parsing reports")
    print(f"Found {len(os.listdir(reports_path))} directories")
    reports = pd.DataFrame(columns=report_cols)
    skipped = []
    for file in tqdm(os.listdir(reports_path)):
        if file.endswith(".html"):
            try:
                with open(os.path.join(reports_path, file), 'r') as f:
                    html = f.read()
                    report_id = file.split('.')[0]
                    report = parse_report(report_id, html)
                    reports = pd.concat([reports, report])
            except UnicodeDecodeError as e:
                print(f"Error parsing {file}: {e}")
                skipped.append(file)
    if save:
        reports.to_csv(f"./data/report.csv", index=False, sep=";")
    print("Done parsing reports")

def parse_form(data_path: str):
    """
        Parses the html and returns a dictionary of the input fields
        and their ids and returns a list of data frames with the 
        columns ['tag', 'name', 'sid'].
    """
    with open(os.path.join(data_path, "search.html"), 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
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

def update_form_mapping():
    fields = parse_form("./data/bp")
    for category, field in fields.items():
        field.to_csv(f"./data/bp/{category}.csv", index=False, sep=";")
    fields = parse_form("./data/mp")
    for category, field in fields.items():
        field.to_csv(f"./data/mp/{category}.csv", index=False, sep=";")

#update_searches()
parse_reports("./data/reports", save=True)