# Kurs-Val (Stock-Whale)
Stock-Whale will help you with your kursval and help you find courses that are actually worth the högskolepoäng that they say they are or compare courses if you merit something else form the course surveys to be the most important.

## Data gathering
A database of the reports is to be gathered to allow for a more comprehensive format. A [scraper](scraper.py) was developed to keep the database updated with the newest of data and a [parser](parser.py) to parse the course-eval pages.
### Course Surveys
The course surveys can be found on on the links below for:
- [Bachelor level programmes](https://student.portal.chalmers.se/sv/chalmersstudier/minkursinformation/kursvardering/Sidor/kursenkatermaster.aspx)
- [Master level programmes](https://student.portal.chalmers.se/sv/chalmersstudier/minkursinformation/kursvardering/Sidor/kursenkatermaster.aspx)

As seen there is a page embedded in a frame in the student portal the link to the actual course-eval website are:
- [Bachelor level programmes](https://course-eval.portal.chalmers.se/sr/ar/4257/sv)
- [Master level programmes](https://course-eval.portal.chalmers.se/sr/ar/4248/sv)

### Search
In each of these a search can be made using a POST request. With the following payload and a big header (see [parser script](parser.py))
>hfSelection: 1<br>
>SessionKey: 990f0331-9906-43d5-a3fb-96f1897e8660<br>
>hfCategory1: {programme_id}<br>
>hfCategory2: {years} ex: 49,1329,1476,1601<br>
>hfCategory3: {reading_periods (LPs)} ex: 1049,1050,1051,1052<br>
>calDate_Year: <br>
>calDate_Month: <br>
>calDate_Day:

Although `SessionKey`, `calDate_Year`, `calDate_Month` and `calDate_Day` can be omitted.
#### Search Mapping
The GET request using the requests lib do not work since the page is generated using javascript. A workaround was made using selenium-wire to allow for a intercept to change the headers of the request which is not possible in selenium. Requires a path specified in the [mapper](mapper.py) to a chromium driver supporting the currently installed version of chrome on the system.

Since this is something done quite yearly I will allow it to be scuffed. Tried requests-html but it was not able to access the site using the headers.
### Report
The usual report url looks something like `https://course-eval.portal.chalmers.se/SR/Report/Token/2418/0/7adc3d81-2f29-4c0c-a3de-5cb8aeff74d8`
the path consisting of `{course_id}/0/{session_id}` although the `session_id` seems to only be required to be a non null string. Leading to the following syntax given a course id `https://course-eval.portal.chalmers.se/SR/Report/Token/{course_id}/0/0`
## Data Parsing
Parsing is done using BeautifulSoup 4.