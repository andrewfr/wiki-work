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

p = "\[\[(.*)\]\]"
s = "'''(.*)'''"
event_pattern = '^\|.*class\s*="presentation|unconference|workshop|keynote|posters|logistics"'
l = "\{\{TNT\|(.*)\}\}"
b = "(\w*[Bb]reakout\w*)"

data =  s + "|" + p + "|" + l + "|" + b

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

def get_data(line):
    columns = line.split("|")
    return columns[:-1]


def test_patterns():
    friday="https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Friday&action=edit"
    #saturday="https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Saturday&action=edit"
    #sunday="https://wikimania2017.wikimedia.org/w/index.php?title=Programme/Sunday&action=edit"
    html_doc = get_url(friday)
    schedule = get_schedule(html_doc)

    #pattern = re.compile(p)

    data_pattern = re.compile(data)
    for line in schedule:
        result = data_pattern.search(line)
        if result:
            print result.group(0) 

def main():
    test_patterns()
   

if __name__ == "__main__":
    main()
