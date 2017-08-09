import codecs
import re

session_pattern = re.compile("\s*!\s*(Session\s*\d)")
schedule_block_info = []

def traverse_schedule(schedule):
    for line in schedule:
        yield line
    raise StopIteration()


def generate_schedule_info(wiki):
    """
    args
       wiki: list of strings representing the wiki schedule
    """

    session_blocks = []

    schedule_gen = traverse_schedule(wiki)

    for line in schedule_gen:
        result = session_pattern.search(line)
        if result:
            print result.group(1), line

    return


def get_schedule_info(event):
    """
    get schedule information associated with event

    args:
        event : data structure representing an event

    return:
        tuple : (name, session_id, session_name)

        name - string
        session_id - string
        session_name - string
    """

    return name, session_id, session_name

def open_schedule(file_name):
    with codecs.open(file_name,encoding="utf-8") as fp:
        wiki_schedule = [line.strip() for line in fp]
    return wiki_schedule

def main():
    wiki = open_schedule("data/friday.wiki")
    generate_schedule_info(wiki)


if __name__ == "__main__":
    main()
