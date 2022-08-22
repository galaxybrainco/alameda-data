#!/bin/bash

datasette publish fly city_council.db alameda_minutes.db --metadata metadata.json --plugins-dir=plugins --app="alameda-datasette"