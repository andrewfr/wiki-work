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

from extract import get_submission_wikicode_link
from extract import get_submission_wikicode

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


comment = '^\<\!\-\-(.*)\-\-\>'
p = "\[\[(.*)\]\]"
s = "'''(.*)'''"
events = '^\|.*class\s*="(presentation|unconference|workshop|keynote|posters|logistics)"'
l = "\{\{TNT\|(.*)\}\}"
b = "(\w*[Bb]reakout\w*)"

data =  s + "|" + p + "|" + l + "|" + b

event_pattern = re.compile(events)
data_pattern = re.compile(data)
comment_pattern = re.compile(comment)
#section_pattern = re.compile('\|\- style\="vertical\-align: top\;"')
section_pattern = re.compile('\|\-')

def traverse_schedule(schedule):
    for line in schedule:
        yield line
    raise StopIteration()

def get_url(url):
    response = requests.get(url)
    return response.content


def get_schedule(html_doc):
    soup = BeautifulSoup(html_doc,"lxml")
    schedule = soup.find("textarea")
    return schedule.get_text().splitlines()


def get_programme(url):
    html_doc = get_url(url)
    schedule = get_schedule(html_doc)

    program = traverse_schedule(schedule)

    for line in program:
        print line
        
def get_program():
    programs = ["https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Friday&action=edit",
               "https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Saturday&action=edit",
               "https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Sunday&action=edit"]


    programs = {"friday": "https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Friday&action=edit",
                "saturday" : "https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Saturday&action=edit",
                "sunday" : "https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Sunday&action=edit"}

    if len(sys.argv) != 2:
        print "usage: python get_program day"
        sys.exit(0)
    else:
        get_programme(programs[sys.argv[1].lower()])


def main():
    get_program()
   

if __name__ == "__main__":
    main()
