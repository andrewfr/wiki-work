from bs4 import BeautifulSoup
import requests
import codecs
import sys

from parse_submission import parse_submission

reload(sys)
sys.setdefaultencoding("utf-8")

def get_submission_wikicode_link(url_prefix, submission):
    soup = BeautifulSoup(submission,"lxml")
    link = soup.find(text="Edit source")
    if link:
        link = url_prefix + link.parent["href"]
    return link

def get_submission_wikicode(html_doc):
    soup = BeautifulSoup(html_doc,"lxml")
    submission = soup.find("textarea")
    if submission:
        wikicode = submission.get_text()
    else:
        wikicode = None
    return wikicode

def main():
    result = requests.get("https://wikimania2017.wikimedia.org/w/index.php?title=Submissions/Wikitext:_upcoming_changes,_available_tools,_what_you_can_do.&action=edit")
    prefix = "https://wikimania2017.wikimedia.org"
    wikicode_link = get_submission_wikicode_link(prefix, result.text)
    print wikicode_link
    result = requests.get(wikicode_link)
    wikicode = get_submission_wikicode(result.text)
    print wikicode
    #print parse_submission(wikicode)   
    


if __name__ == "__main__":
    main()
