#!/usr/bin/env python3
"""
Oslo (Norway) rental market: scraping, cleaning and analysis.

Data source : finn.no
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
DATA_FILE = "osloo.csv"


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
    """Scrape the Oslo listings from finn.no and save them to a CSV file."""
    pages = ["https://www.finn.no/realestate/lettings/search.html?q=oslo&sort=PUBLISHED_DESC"]

    for page in range(2, 51):
        pages.append(
            "https://www.finn.no/realestate/lettings/search.html?page="
            + str(page)
            + "&q=oslo&sort=PUBLISHED_DESC"
        )

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll(
            "a", {"class": "link link--dark sf-ad-link sf-realestate-heading"}
        ):
            links.append(resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            location = html.find("span", {"class": "pl-4"}).text.strip()
        except:
            location = np.nan
        try:
            flat_type = (
                html.find("dl", {"class": "grid md:grid-cols-3 grid-cols-2 pb-8 gap-16 m-0"})
                .find(text=re.compile("Boligtype"))
                .findNext()
                .text.strip()
            )
        except:
            flat_type = np.nan
        try:
            rent = (
                html.find("dd", {"class": "m-0 font-bold text-28"})
                .text.replace("kr", "")
                .strip()
                .replace("\xa0", "")
            )
        except:
            rent = np.nan
        try:
            deposit = (
                html.findAll("dd", {"class": "m-0 font-bold text-28"})[1]
                .text.replace("kr", "")
                .strip()
                .replace("\xa0", "")
            )
        except:
            deposit = np.nan
        try:
            bedroom = (
                html.find("dl", {"class": "grid md:grid-cols-3 grid-cols-2 pb-8 gap-16 m-0"})
                .find(text=re.compile("Soverom"))
                .findNext()
                .text.strip()
            )
        except:
            bedroom = np.nan
        try:
            floor = (
                html.find("dl", {"class": "grid md:grid-cols-3 grid-cols-2 pb-8 gap-16 m-0"})
                .find(text=re.compile("Etasje"))
                .findNext()
                .text.replace(".", "")
                .strip()
            )
        except:
            floor = np.nan
        try:
            net_area = html.find("dd", {"class": "m-0 font-bold"}).text.replace("m²", "").strip()
        except:
            net_area = np.nan
        time.sleep(2)

        result.append([location, flat_type, rent, deposit, bedroom, floor, net_area])

    columns = ["Location", "Flat Type", "Rent", "Deposit", "Bedroom", "Floor", "Net Area"]

    df = pd.DataFrame.from_records(result, columns=columns)

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df["Bedroom"] = df["Bedroom"].fillna(1)

    df["Bedroom"] = df["Bedroom"].astype(int)

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Bedroom"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.05]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Oslo", weight="bold")

    # display the chart
    plt.show()

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "mnd" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "husleie" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "måneders" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "Husleie" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "3 Mnd/Garanti" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "månedsleie" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "Etter avtale" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "nan" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "3 måneder/Garanti" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "/ garanti" in x else x)

    df["Deposit"] = df["Deposit"].apply(lambda x: "48000" if "ja" in x else x)

    df = df.loc[(df["Deposit"] >= 8000) & (df["Deposit"] <= 96000), :]

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace(",", ""))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("–", ""))

    df["Deposit"] = df["Deposit"].astype(int)

    df["Rent"] = df["Rent"].apply(lambda x: str(x).replace(",", ""))

    df["Rent"] = df["Rent"].apply(lambda x: str(x).replace("–", ""))

    df["Rent"] = df["Rent"].apply(lambda x: 12000 if x == "nan" else x)

    df["Rent"] = df["Rent"].astype(int)

    df = df.loc[(df["Rent"] >= 8000) & (df["Rent"] <= 46000), :]

    df["Deposit"] = df["Deposit"].astype(int)

    ### Calculate mean rent for each group + add expenses ###
    one_bed_mean_rent = df[df["Bedroom"] == 1]["Rent"].mean() * 0.087

    two_bed_mean_rent = df[df["Bedroom"] == 2]["Rent"].mean() * 0.087

    three_bed_mean_rent = df[df["Bedroom"] == 3]["Rent"].mean() * 0.087

    ### Create a bar plot ###
    sns.set_style("whitegrid")

    ax = sns.barplot(
        x=["1 Bedroom", "2 Bedrooms", "3 Bedrooms"],
        y=[one_bed_mean_rent, two_bed_mean_rent, three_bed_mean_rent],
        palette="Set1",
    )

    # Add labels to the bars
    for p in ax.patches:
        height = p.get_height()
        ax.text(
            p.get_x() + p.get_width() / 2.0,
            height + 50,
            "€{:.0f}".format(height),
            ha="center",
            weight="bold",
        )

    # Format the x and y-axis tick labels
    ax.set_xticklabels(["1 Bedroom", "2 Bedrooms", "3 Bedrooms"], weight="bold")

    ax.set_yticklabels(["€0", "€2,000"], weight="bold")

    # Format the x and y-axis labels
    ax.set_xlabel("Number of Bedrooms", weight="bold")

    ax.set_ylabel("Mean Rent (€)", weight="bold")

    # Set the plot title
    ax.set_title("Mean Rent by Number of Bedrooms(Oslo)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
