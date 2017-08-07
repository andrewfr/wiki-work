from bs4 import BeautifulSoup
import codecs

def extract_information(submission):
    soup = BeautifulSoup(submission,"lxml")
    print soup
    l = soup.find_all("span")
    print l

    # look for the link

def main():
    with codecs.open("sample.html", encoding="utf-8") as fp:
        html_doc = fp.read()
    extract_information(html_doc)


if __name__ == "__main__":
    main()
