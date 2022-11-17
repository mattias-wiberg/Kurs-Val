import os
import re
import pandas as pd
import str_utils as str_utils

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
            data.to_csv(path+"/report_map.csv", index=False, sep=";")
        full_data = pd.concat([full_data, data])

    if save:
        full_data.to_csv(search_path+"/report_map.csv", index=False, sep=";")
    print("Done parsing search path")
    return full_data

def update_searches():
    parse_search("./data/bp/search", save=True)
    parse_search("./data/mp/search", save=True)

def parse_report(report_id: int, report: str):
    """
        Parses the given report html and returns a dict with the parsed data.
    """
    soup = BeautifulSoup(report, 'html.parser')
    cols = ['course_tag', 'course_name', 'period', 'reading_period', 'report_id', 'answers_count', 'respondents_count', 'category', 'question', 'mean', 'median']
    report = pd.DataFrame(columns=cols)
    course = soup.find('h1').text
    course_tag, course_name, period, reading_period = str_utils.parse_course_text(course)

    course_info = soup.find('p').text
    numbers = re.findall(r'\d+', course_info)
    answers_count = int(numbers[0])
    respondents_count = int(numbers[1])

    categories_divs = soup.find_all('div', {'class': 'artBaseTable'})
    for div in categories_divs[2:]:
        category = " ".join(div.find('h3').text.split(' ')[1:]) # remove the number from the category name
        questions_tables = div.find_all('table')
        for table in questions_tables: # Skips the categories without any tables/"numerics" (ex: "Vad i kursen bör bevaras till nästa kursomgång?")
            question_text = table.find('th', {'class': 'srtbl-rh'}).text
            stat_cells = table.find_all('td', {'class': 'srtbl-cell'})
            question_mean = stat_cells[0].text
            question_median = stat_cells[1].text
            report = pd.concat([report, 
                pd.DataFrame(
                    [[course_tag, course_name, period, reading_period, report_id, answers_count, respondents_count, category, question_text, question_mean, question_median]], columns=cols
                )
            ])

    return report

def parse_reports(reports_path: str, save: bool = False):
    """
        Parses the given reports and returns a list of data frames with the 
        parsed data.
    """
    print("Parsing reports")
    for file in os.listdir(reports_path):
        if file.endswith(".html"):
            with open(os.path.join(reports_path, file), 'r') as f:
                html = f.read()
                report_id = file.split('.')[0]
                print(f"  Parsing report {report_id}")
                report = parse_report(report_id, html)

                if save:
                    report.to_csv(f"{os.path.join(reports_path, report_id)}.csv", index=False, sep=";")
    print("Done parsing reports")

def update_reports():
    parse_reports("./data/bp/reports", save=True)
    parse_reports("./data/mp/reports", save=True)

update_searches()
update_reports()
