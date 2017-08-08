import codecs
import csv

def make_csv(file_name, events):
    with codecs.open(file_name, "wb", encoding="utf-8") as fp:
        writer = csv.writer(fp, delimiter='', quotechar='"', quoting=csv.QUOTE_ALL)

    return

def main():
    make_csv()

if  __name__ == "__main__":
    main()
