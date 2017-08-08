import codecs
import csv

headers = ['title', 'description', 'faciliator_array', 'faciliators',
        'location', 'pathways', 'schedule-block', 'space', 'start', 'end']

def make_csv(file_name, events):
    with codecs.open(file_name, "wb", encoding="utf-8") as fp:
        writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(headers)

    return

def main():
    make_csv("test.csv",[])

if  __name__ == "__main__":
    main()
