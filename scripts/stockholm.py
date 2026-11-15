#!/usr/bin/env python3
"""
Stockholm (Sweden) rental market: scraping, cleaning and analysis.

Data source : housingtarget.com
Snapshot    : 2023 (legacy project, converted from a Jupyter notebook)

NOTE: The scraping selectors target the website markup as it was in 2023 and
will most likely no longer work. This script is kept as a readable record of
the original analysis and has not been re-run after conversion.
"""

# ======================================================================
# 1. IMPORTS
# ======================================================================
from urllib.request import urlopen
import re
import time

from bs4 import BeautifulSoup as bts
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns


# ======================================================================
# 3. HELPER FUNCTIONS
# ======================================================================
def getAndParseURL(url):
    result = requests.get(url, headers={"User-Agent": "Chrome/111.0.5563.65"})
    soup = bts(result.text, "html.parser")
    return soup


# ======================================================================
# 4. DATA COLLECTION (web scraping)
# ======================================================================
def scrape_listings():
    """Scrape the Stockholm listings from housingtarget.com and save them to a CSV file."""
    pages = ["https://www.housingtarget.com/sweden/housing-rentals/stockholm"]

    for page in range(2, 199):
        pages.append(
            "https://www.housingtarget.com/sweden/housing-rentals/stockholm/pageindex" + str(page)
        )

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("a", {"target": "_blank"}):
            links.append("https://www.housingtarget.com" + resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            location = html.find("h1", {"id": "ad_title"}).text.strip()
        except:
            location = np.nan
        try:
            rent = (
                html.find("div", {"class": "facts-list"})
                .find(text=re.compile("Price"))
                .findNext()
                .text.replace(",", "")
                .replace("SEK", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            rooms = (
                html.find("div", {"class": "facts-list"})
                .find(text=re.compile("Number"))
                .findNext()
                .text.strip()
            )
        except:
            rooms = np.nan
        try:
            net_area = (
                html.find("div", {"class": "facts-list"})
                .find(text=re.compile("Size"))
                .findNext()
                .text.replace("m2", "")
                .strip()
            )
        except:
            net_area = np.nan
        try:
            prop_type = (
                html.find("div", {"class": "facts-list"})
                .find(text=re.compile("Housing"))
                .findNext()
                .text.strip()
            )
        except:
            prop_type = np.nan
        time.sleep(2)

        result.append([location, rent, rooms, net_area, prop_type])

    columns = ["Location", "Rent", "Deposit", "Rooms", "Bathroom", "Net Area"]

    df = pd.DataFrame.from_records(result, columns=columns)
    return df


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()


if __name__ == "__main__":
    main()
