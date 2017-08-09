import codecs
import re

session_pattern = re.compile("\s*!\s*(Session\s*\d+)")
session_name_pattern = re.compile("(\'.\d+)\:(.*)\'")
time_pattern = re.compile("(\d\d\:\d\d)\-(\d\d\:\d\d)")

schedule_block_info = []

class ScheduleBlock(object):
    def __init__(self, start_time, end_time, block_name, sessions):
        self.start_time = start_time
        self.end_time = end_time
        self.block_name = block_name
        self.sessions = sessions

    def __repr__(self):
        (self.start_time, self.end_time, self.block_name) % "%s %s %s"

def traverse_schedule(schedule):
    for line in schedule:
        yield line
    raise StopIteration()

def get_session_info(session, line):
    block_name = None
    start_time = ""
    end_time = ""
    block_name = session.group(1)
    the_times = time_pattern.search(line)
    if the_times:
        start_time = the_times.group(1)
        end_time = the_times.group(2)
    return block_name, start_time, end_time
    
def generate_schedule_info(wiki):
    """
    args
       wiki: list of strings representing the wiki schedule
    """

    def get_them_sessions(session_block):
        them_sessions = []
        for line in session_block:
            if line[0] == "!":
                break
            if line.find("header") != -1:
                # okay we are a session
                result = session_name_pattern.search(line)
                if result:
                    data = (result.group(1), result.group(2))
                else:
                    data = line[2:].split("|")
                    data = ("bo", data[1])
                them_sessions.append(data)

        return them_sessions


    session_blocks = []

    schedule_gen = traverse_schedule(wiki)

    for line in schedule_gen:
        result = session_pattern.search(line)
        if result:
            block_name, start_time, end_time = get_session_info(result, line)
            sessions = get_them_sessions(schedule_gen)
            block = ScheduleBlock(start_time, end_time, block_name, sessions)
            print block.block_name
            print block.start_time
            print block.end_time
            print block.sessions
            schedule_block_info.append(block)
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


def print_schedule_block():
    """
    this is a test of the data structure
    """
    return

def main():
    wiki = open_schedule("data/friday.wiki")
    generate_schedule_info(wiki)


if __name__ == "__main__":
    main()
