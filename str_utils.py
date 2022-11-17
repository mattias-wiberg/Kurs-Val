def parse_course_text(course_text: str):
    """
        Parses the given course text and returns a tuple containing the course 
        tag, name, period and reading period.
    """
    course_text = course_text.strip()
    words = course_text.split(' ')
    course_tag = words[0]
    course_name = ' '.join(words[1:-2])
    period = words[-2]
    reading_period = words[-1]
    return course_tag, course_name, period, reading_period

assert parse_course_text(" ATH100 Arkitektur och stadsbyggande: En kulturhistorisk orientering 2013/2014 LP3-LP4  ") == ('ATH100', 'Arkitektur och stadsbyggande: En kulturhistorisk orientering', '2013/2014', 'LP3-LP4')