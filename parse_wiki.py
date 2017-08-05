from dateutil.parser import parse
import requests
import pdb
import json
import codecs
import re
from bs4 import BeautifulSoup

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

time_pattern = re.compile("(\d\d\:\d\d)")
presentation_pattern = re.compile("\[\[(.*)\]\]")
level_pattern = re.compile("\((.*)\)")
session_pattern = re.compile("'''(.*)'''")
event_pattern = re.compile("presentation|unconference|workshop|keynote|posters|logistics")
event_pattern = re.compile('class="(presentation|unconference|workshop|keynote|posters|logistics)"')
logistics_pattern = re.compile("\{\{TNT\|(.*)\}\}")

c = {"room ballroomwc" : "Ballroom West", 
        "room ballroome"  : "Ballroom Center", 
        "room drummondw"  : "Drummond West", 
        "room drummondc"  : "Drummond Center",
        "room drummonde"  : "Drummond East",
        "room salon45"    : "Salon 3", 
        "room salon6"     : "Salon 5",  
        "room salon7"     : "Joyce/Jarry",
        "room salon8"     : "Salon 1", 
        "room salon9"     : "Salon 4" } 

def traverse_schedule(schedule):
    for line in schedule:
        yield line
    raise StopIteration()

def get_time(line):
    answer = time_pattern.search(line)
    if answer:
       return answer.group(0)
    else:
       return None

def get_sessions(schedule):

    def get_session_dates(line):
        i = line.find(":")
        if i != -1:
            times = line[i + 1:].split("-")
        return times[0], times[1]

    def get_them_sessions(schedule, session_number):
        these_sessions = []
        for line in schedule:
            n = line.find("Session")
            if n >= 0:
                break
            if line.find('class="header"'):
                result = session_pattern.search(line)
                if result:
                    these_sessions.append(result.group(1))
        return these_sessions

    gen_schedule = traverse_schedule(schedule)
    sessions = {}
    session_number = 1

    for line in gen_schedule:
        if line.find("Session") != -1:
            start, finish = get_session_dates(line)
            the_sessions = get_them_sessions(gen_schedule, session_number)
            sessions[session_number] = (the_sessions, start, finish)
            session_number += 1

    return sessions        


def get_room(line):

    def get_short_name(line):
        i = line.find("=")
        if i != -1:
            start = line.find('"')
            finish = line.find('"', start + 1)
        return c[line[start + 1:finish]]

    def get_long_name(line):
        i = line.find("|")
        j = line.find("&lt")
        if j != -1:
           room = line[i+1:j-1]
        else:
           room = line[i+1:]
        return room

    def get_level(line):
        level = level_pattern.search(line)
        if level:
            return level.group(1)
        else:
            return None

    short_name = get_short_name(line)
    long_name = get_long_name(line)
    level = get_level(line)
    return short_name, long_name, level

def get_url(url):
    response = requests.get(url)
    return response.content

def get_file(file_name):
    lines = None
    with codecs.open(file_name, encoding="utf-8") as fp:
        lines = [line for line in fp]
    return lines

def get_rooms(schedule):

    def get_them(schedule):
        rooms = []
        for line in schedule:
            if line.find('class=\"time\"') != -1:
                break
            else:
                # okay lets process them
                the_room = get_room(line.strip())
                rooms.append(the_room)
        return rooms

    have_rooms = False
    gen_schedule = traverse_schedule(schedule)

    for line in gen_schedule:
        if have_rooms:
            break
        j = line.find('class="time"')
        if j != -1:
            rooms = get_them(gen_schedule)
            have_rooms = True

    return rooms

def get_presentations(schedule):
        event = {}
        events = []
        current_time = None
        for i in range(0, len(schedule)):
            time = get_time(schedule[i])
            if time:
                current_time = time
                continue

            p = get_presentation(schedule[i])
            if p:
                if len(p) == 2:
                    events.append((current_time, p[0], p[1]))
                else:
                    events.append((current_time, p[0]))
                continue
        return events

def get_time(line):
    result = time_pattern.search(line)
    if result:
        return result.group(0)
    else:
        return None


def get_details(event_type, line):

    details = None

    def get_presentation_details(line):
        answer = presentation_pattern.search(line)
        if answer:
            data = answer.group(1).split("|")
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
        global logistics_pattern
        answer = logistics_pattern.search(line)
        if answer:
            return answer.group(1)
        else:
            return None

    def get_poster_details(line):
        return get_keynote_details(line)

    def get_unconference_details(line):
        #check for break out
        if line.find("Breakout sessions"):
            return "Breakout sessions"
        details = get_presentation_details(line)
        if details:
            return details
        details = get_logistics_details(line)
        if details:
            return details

    def get_workshop_details(line):
        return get_presentation_details(line)

    if event_type == "presentation":
        details = get_presentation_details(line)
    elif event_type == "logistics":
        details = get_logistics_details(line)
    elif event_type == "keynote":
        details = get_keynote_details(line)
    elif event_type == "posters":
        details = get_poster_details(line)
    elif event_type == "unconference":
        details = get_unconference_details(line)
    elif event_type == "workshop":
        details = get_workshop_details(line)
        #print "->workshop", details

    return event_type, details

def get_events(schedule):

    def get_the_events(schedule):
        the_events = []
        line = schedule.next()
        the_time = get_time(line)

        #if next line is not time, we are not in an event block
        if not the_time:
            return []
       
        # check if this is an event
        line = schedule.next()
        result = event_pattern.search(line)

        if result:
            print "->", result.group(1), "<-"
            details = get_details(result.group(1), line)
            the_events.append((the_time, details))

            # now get the rest of the events
            for line in schedule:
                #if we see the time again, we are done for that block
                if get_time(line):
                    break
                result = event_pattern.search(line)
                if result:
                   details = get_details(result.group(1), line)
                   the_events.append((the_time, details))

        return the_events

    daily_events = []

    schedule_gen = traverse_schedule(schedule)

    for line in schedule_gen:
        if line.find("|-") != -1:
            events = get_the_events(schedule_gen)
            if len(events) == 0:
                continue
            daily_events = daily_events + events
               
    return daily_events


def get_schedule(html_doc):
    soup = BeautifulSoup(html_doc,"lxml")
    schedule = soup.find("textarea")
    return schedule.get_text().splitlines()
    
def add_rooms(information, presentations):
    i = 0
    modulus = len(information)
    for presentation in presentations:
        print "->", presentation, information[i % modulus]
        i = i + 1
    return


def main():
    html_doc = get_url("https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Friday&action=edit")
    schedule = get_schedule(html_doc)
    get_events(schedule)
    for event in get_events(schedule):
        print event
    #rooms = get_rooms(schedule)
    #presentations = get_presentations(schedule)
    #sessions = get_sessions(schedule)

    # now lets add the rooms to the presentations

    #add_rooms(rooms, presentations)



if __name__ == "__main__":
    main()
