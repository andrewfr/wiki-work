import traceback
from urllib import quote
from dateutil.parser import parse
from datetime import timedelta
import requests
import pdb
import json
import codecs
import re
import csv

from bs4 import BeautifulSoup

from wikiSessions import generate_session_info, get_session_info
from wikiSessions import get_session_info
from wikiSessions import print_session_block

from extract import get_submission_wikicode_link
from extract import get_submission_wikicode

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# for getting link/title info
LINK = 0 
TITLE = 1

start_time = "^\! (\d\d\:\d\d)"
comment = '^\<\!\-\-(.*)\-\-\>'
p = "\[\[(.*)\]\]"
s = "'''(.*)'''"
#events = '^\|.*class\s*="(presentation|unconference|workshop|keynote|posters|logistics)"'
events = '.*class\s*="(presentation|unconference|workshop|keynote|posters|logistics)"'
l = "\{\{TNT\|(.*)\}\}"
b = "(\w*[Bb]reakout\w*)"
data =  s + "|" + p + "|" + l + "|" + b

event_pattern = re.compile(events)
data_pattern = re.compile(data)
comment_pattern = re.compile(comment)
section_pattern = re.compile('\|\-')
time_pattern = re.compile(start_time)

# more patterns
presentation_pattern = re.compile(p)
logistics_pattern = re.compile(l)


# we need to hardwire room names for now
rooms = ["Ballroom West (level 4)", "Ballroom Center (level 4)", "Drummond West (level 3)", "Drummond Center (level 3)",\
         "Drummond East (level 3)", "Salon 3 (level 2)", "Salon 5 (level 2)", "Joyce/Jarry (level A)", "Salon 1 (level 2)",\
         "Salon 4 (level 2)", "Salon 6 (level 3)"]

class ProgramEvent(object):
    def __init__(self,  event_type = None, start_time = None):
        self.event_type = event_type
        self.start_time = start_time

    def __repr__(self):
        return '%s %s %s %s %s %s %s' %\
               (self.title, self.start_time, self.room, self.session_name, 
                self.session_id, self.session_title, self.link) 

def traverse_schedule(schedule):
    for line in schedule:
        yield line
    raise StopIteration()

def get_url(url):
    response = requests.get(url)
    return response.content

def get_link(prefix, url):
    link = url
    link = link.replace(" ","_")
    return prefix + quote(link.encode('utf-8'))

def get_schedule(html_doc):
    soup = BeautifulSoup(html_doc,"lxml")
    schedule = soup.find("textarea")
    return schedule.get_text().splitlines()

def get_presentation_details(line):
    print "in presentation"
    answer = presentation_pattern.search(line)
    if answer:
        data = answer.group(1).split("|")
        if len(data) == 1:
            data = [data[0],data[0]]
        return data
    else:
        return None

def get_keynote_details(line):
    detail = None
    i = line.find("|", 1)
    if i != -1:
        detail = line[i + 1:]
        detail = detail.replace("<br/>","")
        detail = detail.replace("<small>","")
        detail = detail.replace("</small>","")
    return detail

def get_logistics_details(line):
    print "*in logistics"
    global logistics_pattern
    answer = logistics_pattern.search(line)
    if answer:
        return answer.group(1)
    answer = get_presentation_details(line)
    if answer:
       return answer
    else:
        return None

def get_poster_details(line):
    return get_keynote_details(line)

def get_unconference_details(line):
    print "* in unconference"
    #check for break out
    #answer = breakout_pattern.search(line)
    #if answer:
    #    return answer.group(0)
    details = get_presentation_details(line)
    if details:
        return details
    details = get_logistics_details(line)
    if details:
        return details
    else:
        i = line.find("|",5)
        if i != -1:
            return line[i + 1:].strip()

def get_workshop_details(line):
    print "* in workshop"
    answer = get_presentation_details(line)
    if answer:
        return answer
    answer = get_logistics_details(line)
    if answer:
        return answer
    return None


def get_details(event_type, line):
    details = None
    if event_type == "presentation":
        details = get_presentation_details(line)
    elif event_type == "workshop":
        details = get_workshop_details(line)
    elif event_type == "unconference":
        details = get_unconference_details(line)
    else:
        print "some weird detail stuff"
        details = line
    return details

"""
extract program events from the wiki
"""
def get_events(program, book_end, start_time_string):

    the_events = []

    column = 0

    start_time = parse(start_time_string)
    for line in program:
        if line == book_end:
            break
        comment_result = comment_pattern.search(line)
        if comment_result:
            continue
        else:
            event_result = event_pattern.search(line)
            if event_result:
                """
                we are ready to add an event
                """
                event_type = event_result.group(1) 
                if event_type in ["presentation","workshop","unconference"]:
                    try:
                        details = get_details(event_type, line)
                        if not details:
                            details = ["",""]

                        session_name, session_id, session_title = get_session_info(start_time, column)

                        print start_time.strftime("%H:%M"), event_type, rooms[column], session_name,\
                                session_id, session_title, details[TITLE]

                        event = ProgramEvent()

                        # start of this is bad 
                        event.session_name = session_name
                        event.session_id = session_id
                        event.session_title = session_title
                        event.start_time = start_time
                        event.room = rooms[column]
                        event.title = details[TITLE]
                        event.link = details[LINK]
                        # end of this is bad

                        the_events.append(event)
                    except:
                        print '->', line
                        traceback.print_exc()
                    column = column + 1
                else:
                    print "SOMETHING ELSE", line
    print "----"        
    return the_events

def get_section(program):
    """
    we are in a wikicode section
    we don't care about all sections - just activities
    """
    book_end = program.next()
    talks_result = time_pattern.search(book_end)
    if talks_result:
       return get_events(program, book_end, talks_result.group(1))
    # this may be an error
    return []

def process_programme(url):

    program_events = []
    html_doc = get_url(url)
    schedule = get_schedule(html_doc)

    generate_session_info(schedule)

    program = traverse_schedule(schedule)

    for line in program:

        # ignore comments
        comment_result = comment_pattern.search(line)
        if comment_result:
            continue

        section_result = section_pattern.search(line)
        if section_result:
            program_events = program_events + get_section(program)
            
    return program_events

def make_csv(file_name, events):
    with codecs.open(file_name, "wb", encoding="utf-8") as fp:
        writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for event in events:
            row = [event.title, event.start_time.strftime("%H:%M"), event.room, event.session_name, 
                   event.session_id, event.session_title, event.link] 
            writer.writerow(row)

def test_patterns():
    program = ["https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Friday&action=edit",
               "https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Saturday&action=edit",
               "https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Sunday&action=edit"]
    events = process_programme(program[0])
    #make_csv("test.csv", events)

def test_sessions():
    program = ["https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Friday&action=edit",
               "https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Saturday&action=edit",
               "https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Sunday&action=edit"]

    html_doc = get_url(program[0])
    schedule = get_schedule(html_doc)

    generate_session_info(schedule)

    print_session_block()

    # should be community bias
    print get_session_info(parse("11:00"), 2)

    # should be breakout
    print get_session_info(parse("11:30"), 9)

    #doesn't exist
    print get_session_info(parse("12:30"), 0)


def main():
    test_patterns()
   

if __name__ == "__main__":
    main()
