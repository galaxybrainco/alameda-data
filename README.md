# alameda-data

## Searchable, queryable data for the City of Alameda.

This repo is the scripts and data for creating queryable databases for data from the City of Alameda, hosted at https://data.alameda.one.

Right now, this includes:
- `city_council.db`, all the available minutes of the Alameda City Council, broken down bu item and votes on each item for each councilmember.

This data is incomplete! You can help by improving `parse_minutes.py` to better parse the PDF data. We do not claim absolute correctness, yet, but where things are incorrect they are incorrect via not correctly counting absences or abstentions. For example, if a vote is marked as "unanimous voice vote", but members were absent or abstainnig from that vote, they might be listed as _still_ having voted.

You can help! Pull requests are very welcomed, and you can email phildini@phildini.net if you have questions.

