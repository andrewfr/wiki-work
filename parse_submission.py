import codecs
import re
import pdb

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

title_pattern = re.compile("\s*;\s*Title")
author_pattern = re.compile("\s*;\s*Author")
abstract_pattern = re.compile("\s*;\s*Abstract")
start_pattern = re.compile("^\s*;")

def traverse_submission(submission):
    for line in submission.splitlines():
        yield line
    raise StopIteration()


def get_content(submission):
    content = ""
    for line in submission:
        print "->", line
        if line.find("<!--") >= 0 :
            continue
        if line.find(";") >= 0 :
            break
        content = content + line
    print "*", content, len(content)
    if content[0] == ":":
        content = content[1:]
    return content

def get_title(line, submission):

    # is there a title on the same line?
    i = line.find(':')
    if i != -1:
        title = line[i+1:]
        return title

    #assume on a separate line
    title = ""
    for line in submission:
        result = start_pattern.search(line)
        if result:
            break
        title = title + line
    return title

def get_author(line, submission):
    # is there a title on the same line?
    print '->', line
    i = line.find(':')
    if i != -1:
        author = line[i+1:]
    else:
        #assume on a separate line
        author = ""
        for line in submission:
            print '->', line
            result = start_pattern.search(line)
            if result:
                break
            author = author + line
    return author

def get_description(submission):
    return description

def parse_submission(submission):

    submission_gen = traverse_submission(submission)

    title = None
    description = None
    facilitators = None

    for line in submission_gen:
        result = title_pattern.search(line)
        if result:
            print '*title', result.group(0)
            title= get_title(line, submission_gen)
            continue
        result = author_pattern.search(line)
        if result:
            print '*author', result.group(0)
            facilitators = get_author(line, submission_gen)
            continue
        result = abstract_pattern.search(line)
        if result:
            description = get_description(line, submission_gen)
            #print '*abstract', result.group(0)
            continue

    return title, description, facilitators


def main():
    with codecs.open("submission.wiki", encoding="utf-8") as fp:
        submission = fp.read()

    print parse_submission(submission)

if __name__ == "__main__":
    main()
