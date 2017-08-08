import codecs
import re
import pdb

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

title_pattern = re.compile("\s*;\s*Title")
author_pattern = re.compile("\s*;\s*Author")
abstract_pattern = re.compile("\s*;\s*Abstract")

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

def parse_submission(submission):

    submission_gen = traverse_submission(submission)

    title = None
    description = None
    facilitators = None

    for line in submission_gen:
        print '->', line
        result = title_pattern.search(line)
        if result:
            title= result.group(0)
            print '*title', result.group(0)
            continue
        result = author_pattern.search(line)
        if result:
            facilitators = result.group(0)
            print '*author', result.group(0)
            continue
        result = abstract_pattern.search(line)
        if result:
            description = result.group(0)
            print '*abstract', result.group(0)
            continue

    return title, description, facilitators


def main():
    with codecs.open("submission.wiki", encoding="utf-8") as fp:
        submission = fp.read()

    print parse_submission(submission)

if __name__ == "__main__":
    main()
