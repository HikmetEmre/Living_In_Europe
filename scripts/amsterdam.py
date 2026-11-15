#!/usr/bin/env python3
"""
Amsterdam (Netherlands) rental market: scraping, cleaning and analysis.

Data source : funda.nl
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
DATA_FILE = "amsterdam_market.csv"


# ======================================================================
# 3. HELPER FUNCTIONS
# ======================================================================
def getAndParseURL(url):
    result = requests.get(url, headers={"User-Agent": "Chrome/110.0.5481.178"})
    soup = bts(result.text, "html.parser")
    return soup


def replace_bathroom_value(value):
    if pd.isna(value):
        return 0
    elif "1" in value:
        return 1
    elif "2" in value:
        return 2
    elif "3" in value:
        return 3
    else:
        return 0


# ======================================================================
# 4. DATA COLLECTION (web scraping)
# ======================================================================
def scrape_listings():
    """Scrape the Amsterdam listings from funda.nl and save them to a CSV file."""
    pages = ["https://www.funda.nl/en/huur/amsterdam/"]

    for page in range(2, 88):
        pages.append("https://www.funda.nl/en/huur/amsterdam/p" + str(page))

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("div", {"class": "search-result__header-title-col"}):
            links.append("https://www.funda.nl/" + resulthf.a.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            location = html.find(
                "span", {"class": "object-header__subtitle fd-color-dark-3"}
            ).text.strip()
        except:
            location = np.nan
        try:
            rent = (
                html.find("strong", {"class": "object-header__price"})
                .text.replace("€ ", "")
                .replace(" p/mo.", "")
                .replace(",", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            deposit = (
                html.find("dd", {"class": "object-kenmerken-group-list"})
                .find(text=re.compile("Deposit"))
                .findNext()
                .text[0:7]
                .replace("€ ", "")
                .replace(",", "")
                .strip()
            )
        except:
            deposit = np.nan
        try:
            rooms = (
                html.find("div", {"class": "object-kenmerken-body"})
                .text.split("Number of rooms")[1]
                .split("\n")[2][0:7]
                .replace(" rooms", "")
                .strip()
            )
        except:
            rooms = np.nan
        try:
            bathroom = (
                html.find("div", {"class": "object-kenmerken-body"})
                .text.split("Number of bath rooms")[1]
                .split("\n")[2]
                .replace(" bathroom", "")
                .strip()
            )
        except:
            bathroom = np.nan
        try:
            net_area = (
                html.find("span", {"class": "kenmerken-highlighted__value fd-text--nowrap"})
                .text.replace(" m²", "")
                .strip()
            )
        except:
            net_area = np.nan
        time.sleep(2)

        result.append([location, rent, deposit, rooms, bathroom, net_area])

    columns = ["Location", "Rent", "Deposit", "Rooms", "Bathroom", "Net Area"]

    df = pd.DataFrame.from_records(result, columns=columns)

    df["Rent"] = df["Rent"].astype(float)

    df = df.loc[(df["Rent"] >= 800) & (df["Rent"] <= 15000), :]

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df["Deposit"] = df["Deposit"].apply(lambda x: 3000 if x == "None" else x)

    df["Deposit"] = df["Deposit"].fillna(3000)

    df["Deposit"] = df["Deposit"].astype(int)

    df["Rooms"] = df["Rooms"].apply(lambda x: 1 if x == "1 room" else x)

    df["Rooms"] = df["Rooms"].apply(lambda x: 10 if x == "10 room" else x)

    df["Rooms"] = df["Rooms"].fillna(1)

    df["Bathroom"] = df["Bathroom"].apply(replace_bathroom_value)

    df["Bathroom"] = df["Bathroom"].apply(lambda x: 1 if x == 0 else x)

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Rooms"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Amsterdam ")

    # display the chart
    plt.show()

    # get the value counts of the 'Bathroom' column
    room_counts = df["Bathroom"].value_counts()

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(room_counts, labels=room_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bathroom Number Flats of Amsterdam ")

    # display the chart
    plt.show()

    # Calculate mean rent for each group
    one_bed_mean_rent = df[df["Rooms"] == 1]["Rent"].mean()

    two_bed_mean_rent = df[df["Rooms"] == 2]["Rent"].mean()

    three_bed_mean_rent = df[df["Rooms"] == 3]["Rent"].mean()

    # Create a bar plot
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

    ax.set_yticklabels(["€0", "€2,000", "€3,000"], weight="bold")

    # Format the x and y-axis labels
    ax.set_xlabel("Number of Bedrooms", weight="bold")

    ax.set_ylabel("Mean Rent (€)", weight="bold")

    # Set the plot title
    ax.set_title("Mean Rent by Number of Bedrooms(Amsterdam)", weight="bold")

    plt.show()

    two_bed_mean_rent = df[df["Rooms"] == 2]

    df["Rooms"] = df["Rooms"].astype(int)


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
