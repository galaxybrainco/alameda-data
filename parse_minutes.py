import re
import os
from datetime import datetime

from parsedatetime import Calendar
from PyPDF2 import PdfReader
from sqlite_utils import Database


def main(filename):
    print(filename)
    # Setup some utilities
    db = Database("alameda_data.db")
    reader = PdfReader(filename)
    calendar = Calendar()

    # Setup some placeholders
    current_item = None
    current_item_title = None
    in_closed_session = False
    current_meeting_title = None
    current_meeting_datetime = None

    items_to_upsert = []
    votes_to_upsert = []
    meetings_to_upsert = []

    text = "\n".join([page.extract_text() for page in reader.pages])
    mucked = text.replace("\n \n", "NEWLINE")
    mucked = mucked.replace("\n\n", "NEWLINE")
    mucked = mucked.replace("\n", "")
    mucked = mucked.replace("  ", " ")
    mucked = mucked.replace("NEWLINE", "\n")
    # print(mucked)
    lines = mucked.split("\n")

    for line in lines:
        if line.startswith("MINUTES OF THE"):
            current_meeting_title = line.replace("MINUTES OF THE ", "")
            time_string = " ".join(line.split("- -")[1:])
            time_struct, _ = calendar.parse(time_string)
            current_meeting_datetime = datetime(*time_struct[:6])
            print(current_meeting_title)
            print(current_meeting_datetime)
            meetings_to_upsert.append(
                {"name": current_meeting_title, "date": current_meeting_datetime}
            )
        if "Closed Session" in line and not in_closed_session:
            print("In Closed Session")
            in_closed_session = True
        if in_closed_session and "adjourned" in line:
            print("Out of Closed Session")
            in_closed_session = False
        if match := re.match("^\(\d\d\-\d\d\d\)", line):
            current_item = match.group()
            try:
                current_item_title = line.split(") ")[1]
            except IndexError:
                print(line)
                continue
        if line.startswith("CONSENT CALENDAR"):
            current_item = "Consent Calendar"
        if "roll call" in line and line.count("roll call") < 2:
            if (
                not in_closed_session
                and current_item
                and current_item_title
                and current_item != "Consent Calendar"
            ):
                print(f"Item: {current_item}")
                item_id = current_item.strip("()")
                # print(line.split("roll call vote: Councilmembers ")[1].split(". ")[0].split("; "))
                try:
                    votes_raw = (
                        line.split("roll call vote: ")[1]
                        .replace("Councilmembers ", "")
                        .replace("Councilmembers/Commissioners ", "")
                        .split(". ")[0]
                        .split("; ")
                    )

                    votes = []
                    votes_for = 0
                    votes_against = 0
                    majority = "no"
                    for vote in votes_raw:
                        vote = vote.split(": ")
                        name = (
                            vote[0]
                            # Text parsing is hard
                            .replace("Councilmember s ", "")
                            .replace("Councilmember ", "")
                            .replace("Vice Mayor ", "")
                            .replace("Acting Mayor ", "")
                            .replace("and May or ", "")
                            .replace("and Ma yor ", "")
                            .replace("and Mayor ", "")
                            .replace("Mayor ", "")
                            # What's in a name? Spaces, according to PDFs
                            .replace("As hcraft", "Ashcraft")
                            .replace("Ash-craft", "Ashcraft")
                            .replace("Kn ox White", "Knox White")
                            # These next two are getting for getting her name consistently right
                            .replace("Herrera Spencer", "Spencer")
                            .replace("Spencer", "Herrera Spencer")
                        )
                        name = name.strip()
                        choice = vote[1]
                        choice = choice.lower()
                        if choice.startswith("no"):
                            choice = "no"
                            votes_against += 1
                        if choice.startswith("aye"):
                            choice = "aye"
                            votes_for += 1
                        votes.append((name, choice))
                        votes_to_upsert.append(
                            {
                                "councilmember": name,
                                "item": item_id,
                                "vote": choice,
                                "id": f"{item_id}-{name}",
                            }
                        )
                    # print(votes)
                    if votes_for > votes_against:
                        majority = "aye"
                    items_to_upsert.append(
                        {
                            "id": item_id,
                            "name": current_item_title,
                            "ayes": votes_for,
                            "nays": votes_against,
                            "majority": majority,
                        }
                    )
                except IndexError as e:
                    print(line)
                    continue
    db["meetings"].upsert_all(
        meetings_to_upsert, pk="date", column_order=["date", "name"]
    )
    db["items"].upsert_all(
        items_to_upsert,
        pk="id",
        column_order=["id", "name", "ayes", "nays", "majority"],
    )
    db["votes"].upsert_all(
        votes_to_upsert, pk="id", column_order=["id", "councilmember", "item", "vote"]
    )

    # vote_lines = [line for line in lines if "roll call" in line]
    # for line in vote_lines[1:]:
    #     print(line.split("roll call vote: Councilmembers ")[1].split(". ")[0].split("; "))


if __name__ == "__main__":
    path = "/Users/phildini/Downloads/alameda/city_council_minutes"
    for minutes in sorted(os.listdir(path)):
        main(f"{path}/{minutes}")
