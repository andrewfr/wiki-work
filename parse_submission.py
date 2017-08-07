import codecs
import pdb


def traverse_submission(submission):
    for line in submission.splitlines():
        yield line
    raise StopIteration()


def get_content(submission):
    content = ""
    for line in submission:
        if line.find("<!--") >= 0 :
            continue
        if line.find(";") >= 0 :
            break
        content = content + line

    if content[0] == ":":
        content = content[1:]
    return content

def parse_submission(submission):

    submission_gen = traverse_submission(submission)

    title = None
    description = None
    facilitators = None

    for line in submission_gen:
        if line.find("Title of the submission") != -1:
            title = get_content(submission_gen)
            continue
        if line.find("; Author of the submission") != -1:
            facilitators = get_content(submission_gen)
        if line.find("; Abstract") != -1:
            description = get_content(submission_gen)

    return title, description, facilitators


def main():
    with codecs.open("submission.wiki", encoding="utf-8") as fp:
        submission = fp.read()

    print parse_submission(submission)

if __name__ == "__main__":
    main()
