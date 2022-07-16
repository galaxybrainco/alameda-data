from PyPDF2 import PdfReader
import re

def main():
    item_regex = re.compile("^\(\d\d\-\d\d\d\)$")
    reader = PdfReader("Minutes.pdf")

    text = "\n".join([page.extract_text() for page in reader.pages])
    mucked = text.replace("\n \n", "NEWLINE")
    mucked = mucked.replace("\n\n", "NEWLINE")
    mucked = mucked.replace("\n", "")
    mucked = mucked.replace("  ", " ")
    mucked = mucked.replace("NEWLINE", "\n")
    # print(mucked)
    lines = mucked.split("\n")
    current_item = None
    in_closed_session = False
    for line in lines:
        if "Closed Session" in line:
            print("In Closed Session")
            in_closed_session = True
        if in_closed_session and "adjourned" in line:
            print("Out of Closed Session")
            in_closed_session = False
        if match :=  re.match("^\(\d\d\-\d\d\d\)", line):
            current_item = match.group()
        if line.startswith("CONSENT CALENDAR"):
            current_item = "Consent Calendar"
        if "roll call" in line and line.count("roll call") < 2:
            if not in_closed_session:
                print(f"Item: {current_item}")
                # print(line.split("roll call vote: Councilmembers ")[1].split(". ")[0].split("; "))
                votes_raw = line.split("roll call vote: Councilmembers ")[1].split(". ")[0].split("; ")
                votes = []
                for vote in votes_raw:
                    vote = vote.split(": ")
                    name = vote[0]
                    name = name.strip().lstrip("and Mayor ")
                    choice = vote[1]
                    choice = choice.lower()
                    if choice.startswith("no"):
                        choice = "no"
                    if choice.startswith("aye"):
                        choice = "aye"
                    votes.append((name, choice))
                print(votes)


    # vote_lines = [line for line in lines if "roll call" in line]
    # for line in vote_lines[1:]:
    #     print(line.split("roll call vote: Councilmembers ")[1].split(". ")[0].split("; "))

if __name__ == "__main__":
    main()