import re
from datetime import datetime
from pathlib import Path

from parsedatetime import Calendar
from PyPDF2 import PdfReader
from sqlite_utils import Database


def main(filename):
    print(filename)
    # Setup some utilities
    db = Database("ausd.db")
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
    members = []

    items_to_upsert = []
    votes_to_upsert = []
    meetings_to_upsert = []

    text = "\n".join([page.extract_text() for page in reader.pages])
    # breakpoint()
    mucked = text.replace("\n \n", "NEWLINE")
    mucked = mucked.replace("\n\n", "NEWLINE")
    mucked = mucked.replace("\n", "")
    mucked = mucked.replace("  ", " ")
    mucked = mucked.replace("NEWLINE", "\n")
    mucked = mucked.replace("***", "")
    lines = mucked.split("\n")
    for line in lines:
        print(line)


if __name__ == "__main__":
    main(
        "/Users/phildini/Downloads/alameda/ausd_minutes/Minutes_2014_6_24_Meeting(48).pdf"
    )
