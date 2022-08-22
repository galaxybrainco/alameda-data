import re
import os
from datetime import datetime

from parsedatetime import Calendar
from PyPDF2 import PdfReader
from sqlite_utils import Database
from pprint import pprint
import random

# ORDER MATTERS!
# Text is hard


def main(filename):
    print(filename)
    # Setup some utilities
    db = Database("city_council.db")
    reader = PdfReader(filename)
    calendar = Calendar()

    # Setup some placeholders
    current_item = None
    current_item_title = None
    in_closed_session = False
    current_meeting_title = None
    current_meeting_datetime = None
    item_id = None
    roll_call_line = None

    items_to_upsert = []
    votes_to_upsert = []
    meetings_to_upsert = []

    text = "\n".join([page.extract_text() for page in reader.pages])
    # breakpoint()

    # Newline misparse
    mucked = text.replace("\n\n\n", "NEWLINE")
    mucked = mucked.replace("\n \n \n", "NEWLINE")
    mucked = mucked.replace("\n \n", "NEWLINE")
    mucked = mucked.replace("\n\n", "NEWLINE")

    # # Remove line break in paragraph
    mucked = mucked.replace("\n", " ")

    # # Put back the real newlines
    mucked = mucked.replace("NEWLINE", "\n")

    lines = mucked.split("\n")
    for line in lines:
        if (
            "made a motion" in line
            or "roll call vote" in line
            or "motion passed" in line
        ):
            print(line)
        # if "Present:" in line or "ROLL CALL" in line:
        #     print(line)
    #     line = line.lstrip()
    #     if line.startswith("MINUTES OF THE"):
    #         current_meeting_title = line.replace("MINUTES OF THE ", "")
    #         time_string = " ".join(line.split("- -")[1:])
    #         time_struct, _ = calendar.parse(time_string)
    #         current_meeting_datetime = datetime(*time_struct[:6])
    #         meetings_to_upsert.append(
    #             {"name": current_meeting_title, "date": current_meeting_datetime}
    #         )
    #     if "Closed Session" in line and not in_closed_session:
    #         in_closed_session = True
    #     if in_closed_session and "adjourned" in line:
    #         in_closed_session = False
    #     if match := re.match("^\(\d\d\-\d\d\d\)", line):
    #         current_item = match.group()
    #         try:
    #             current_item_title = line.split(") ")[1]
    #             item_id = current_item.strip("()")
    #         except IndexError:
    #             # print(line)
    #             continue
    #     if line.startswith("CONSENT CALENDAR"):
    #         current_item = "Consent Calendar"

    #     if line.lower().startswith("roll call - "):
    #         roll_call_line = line
    #         working = line.split(" - ")[1]
    #         working = run_through_replacements(working)
    #         members = working.split(", ")
    #         members = [member.split(" – ")[0].strip() for member in members]

    #     if "unanimous voice vote" in line.lower():
    #         if (
    #             not in_closed_session
    #             and current_item
    #             and current_item_title
    #             and current_item != "Consent Calendar"
    #         ):
    #             try:
    #                 for voter in members:
    #                     if voter:
    #                         votes_to_upsert.append(
    #                             {
    #                                 "councilmember": voter.strip(","),
    #                                 "item": item_id,
    #                                 "vote": "aye",
    #                                 "id": f"{item_id}-{voter}",
    #                             }
    #                         )
    #                     items_to_upsert.append(
    #                         {
    #                             "id": item_id,
    #                             "name": current_item_title,
    #                             "ayes": 5,
    #                             "nays": 0,
    #                             "majority": "aye",
    #                         }
    #                     )
    #             except UnboundLocalError:
    #                 print(roll_call_line)

    #     if "roll call" in line and line.count("roll call") < 2:
    #         if (
    #             not in_closed_session
    #             and current_item
    #             and current_item_title
    #             and current_item != "Consent Calendar"
    #         ):
    #             item_id = current_item.strip("()")
    #             try:
    #                 votes_raw = (
    #                     line.split("roll call vote: ")[1]
    #                     .replace("Councilmembers ", "")
    #                     .replace("Councilmembers/Commissioners ", "")
    #                     .split(". ")[0]
    #                     .split("; ")
    #                 )

    #                 votes = []
    #                 votes_for = 0
    #                 votes_against = 0
    #                 majority = "no"
    #                 for vote in votes_raw:
    #                     vote = vote.split(": ")
    #                     name = vote[0]
    #                     name = run_through_replacements(name)
    #                     name = name.strip()
    #                     choice = vote[1]
    #                     choice = choice.lower()
    #                     if choice.startswith("no"):
    #                         choice = "no"
    #                         votes_against += 1
    #                     if choice.startswith("aye"):
    #                         choice = "aye"
    #                         votes_for += 1
    #                     # votes.append((name, choice))
    #                     # name = run_through_replacements(name)
    #                     if name:
    #                         votes_to_upsert.append(
    #                             {
    #                                 "councilmember": name.strip(","),
    #                                 "item": item_id,
    #                                 "vote": choice,
    #                                 "id": f"{item_id}-{name}",
    #                             }
    #                         )

    #                 if votes_for > votes_against:
    #                     majority = "aye"
    #                 items_to_upsert.append(
    #                     {
    #                         "id": item_id,
    #                         "name": current_item_title,
    #                         "ayes": votes_for,
    #                         "nays": votes_against,
    #                         "majority": majority,
    #                     }
    #                 )
    #             except IndexError as e:
    #                 print(line)
    #                 continue
    # db["meetings"].upsert_all(
    #     meetings_to_upsert, pk="date", column_order=["date", "name"]
    # )
    # db["items"].upsert_all(
    #     items_to_upsert,
    #     pk="id",
    #     column_order=["id", "name", "ayes", "nays", "majority"],
    # )
    # db["votes"].upsert_all(
    #     votes_to_upsert, pk="id", column_order=["id", "councilmember", "item", "vote"]
    # )


if __name__ == "__main__":
    path = "./data/PlanningBoard"
    files = sorted(os.listdir(path))
    files = [random.choice(files) for _ in range(10)]
    for minutes in files:
        if minutes.endswith(".pdf"):
            main(f"{path}/{minutes}")

    # main("Minutes.pdf")
