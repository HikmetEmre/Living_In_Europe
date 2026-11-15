#!/usr/bin/env python3
"""
Istanbul (Turkey) rental market: scraping, cleaning and analysis.

Data source : hepsiemlak.com
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
# 2. CONFIGURATION
# ======================================================================
DATA_FILE_1 = "./hepsirent_df.csv"
DATA_FILE_2 = "./LATEST_VERSION.csv"


# ======================================================================
# 3. HELPER FUNCTIONS
# ======================================================================
def getAndParseURL(url):
    result = requests.get(url, headers={"User-Agent": "Chrome/110.0.5481.78"})
    soup = bts(result.text, "html.parser")
    return soup


# ======================================================================
# 4. DATA COLLECTION (web scraping)
# ======================================================================
def scrape_listings():
    """Scrape the Istanbul listings from hepsiemlak.com and save them to a CSV file."""
    pages = ["https://www.hepsiemlak.com/istanbul-kiralik"]

    for page in range(2, 466):
        pages.append("https://www.hepsiemlak.com/istanbul-kiralik?page=" + str(page))

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for sonuc in html.findAll("a", {"class": "card-link"}):
            links.append("https://www.hepsiemlak.com" + sonuc.get("href"))

    result = []

    for sonuc in links:
        html = getAndParseURL(sonuc)

        try:
            disctrict = (
                html.find("div", {"class": "det-title-bottom"})
                .find(text=re.compile("İstanbul"))
                .findNext()
                .text.strip()
            )
        except:
            disctrict = np.nan
        try:
            rent = (
                html.find("p", {"class": "fontRB fz24 price"})
                .text.replace("TL", "")
                .replace(".", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            net_area = (
                html.find("div", {"class": "container det-container"})
                .find(text=re.compile("Brüt / Net M2"))
                .findNext()
                .text.replace("m2", "")
                .strip()
            )
        except:
            net_area = np.nan
        try:
            rooms = (
                html.find("ul", {"class": "short-info-list"})
                .find(text=re.compile("Daire"))
                .findNext()
                .text.replace(" ", "")
                .replace("\n", "")
            )
        except:
            rooms = np.nan
        try:
            bath = (
                html.find("div", {"class": "container det-container"})
                .find(text=re.compile("Banyo Sayısı"))
                .findNext()
                .text.strip()
            )
        except:
            bath = np.nan
        try:
            number_of_floors = (
                html.find("div", {"class": "container det-container"})
                .find(text=re.compile("Kat Sayısı"))
                .findNext()
                .text.strip()
            )
        except:
            number_of_floors = np.nan
        try:
            floor = (
                html.find("div", {"class": "container det-container"})
                .find(text=re.compile("Bulunduğu Kat"))
                .findNext()
                .text.strip()
            )
        except:
            floor = np.nan
        try:
            heat_type = (
                html.find("div", {"class": "container det-container"})
                .find(text=re.compile("Yakıt Tipi"))
                .findNext()
                .text.strip()
            )
        except:
            heat_type = np.nan
        try:
            age_of_flat = (
                html.find("div", {"class": "container det-container"})
                .find(text=re.compile("Bina Yaşı"))
                .findNext()
                .text.strip()
            )
        except:
            age_of_flat = np.nan
        try:
            dues = (
                html.find("div", {"class": "container det-container"})
                .find(text=re.compile("Aidat"))
                .findNext()
                .text.replace("TL", "")
                .replace(".", "")
                .strip()
            )
        except:
            dues = np.nan
        try:
            deposit = (
                html.find("div", {"class": "container det-container"})
                .find(text=re.compile("Depozito"))
                .findNext()
                .text.replace("TL", "")
                .replace(".", "")
                .strip()
            )
        except:
            deposit = np.nan
        time.sleep(2)

        result.append(
            [
                disctrict,
                rent,
                net_area,
                rooms,
                bath,
                number_of_floors,
                floor,
                heat_type,
                age_of_flat,
                dues,
                deposit,
            ]
        )

    columns = [
        "District",
        "Rent",
        "Net Area",
        "Rooms",
        "Bath",
        "NOF",
        "FLOOR",
        "Heat Type",
        "Age",
        "Dues",
        "Deposit",
    ]

    df = pd.DataFrame.from_records(result, columns=columns)
    return df


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()


if __name__ == "__main__":
    main()
