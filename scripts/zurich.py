#!/usr/bin/env python3
"""
Zurich (Switzerland) rental market: scraping, cleaning and analysis.

Data source : homegate.ch
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
DATA_FILE = "zrch_first.csv"


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
    """Scrape the Zurich listings from homegate.ch and save them to a CSV file."""
    pages = ["https://www.homegate.ch/rent/apartment/city-zurich/matching-list"]

    for page in range(2, 25):
        pages.append(
            "https://www.homegate.ch/rent/apartment/city-zurich/matching-list?ep=" + str(page)
        )

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("a", {"class": "ListItem_itemLink_30Did"}):
            links.append("https://www.homegate.ch" + resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            location = html.find("span", {"class": "AddressDetails_street_22a5p"}).text.strip()
        except:
            location = np.nan
        try:
            rent = (
                html.find("ul", {"class": "SpotlightAttributes_spotlight_37lw3"})
                .find(text=re.compile("CHF"))
                .findNext()
                .text.replace(",", "")
                .replace(".", "")
                .replace("–", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            add_expenses = (
                html.find("div", {"data-test": "costs"})
                .find(text=re.compile("expenses"))
                .findNext()
                .text.replace("CHF", "")
                .replace(".", "")
                .replace("–", "")
                .strip()
            )
        except:
            add_expenses = np.nan
        try:
            bedroom = (
                html.find("ul", {"class": "SpotlightAttributes_spotlight_37lw3"})
                .find(text=re.compile("Room"))
                .findNext()
                .text.strip()
            )
        except:
            bedroom = np.nan
        try:
            net_area = (
                html.find("ul", {"class": "SpotlightAttributes_spotlight_37lw3"})
                .find(text=re.compile("Living"))
                .findNext()
                .text.replace("m2", "")
                .strip()
            )
        except:
            net_area = np.nan
        try:
            flat_type = (
                html.find("div", {"class": "CoreAttributes_coreAttributes_2UrTf"})
                .find(text=re.compile("Type"))
                .findNext()
                .text.strip()
            )
        except:
            flat_type = np.nan
        time.sleep(2)

        result.append([location, rent, add_expenses, bedroom, net_area, flat_type])

    columns = ["Location", "Rent", "Additional Expenses", "Bedroom", "Net Area", "Type"]

    df = pd.DataFrame.from_records(result, columns=columns)

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df["Rent"] = df["Rent"].apply(lambda x: 2625 if x == "nan" else x)

    df["Rent"] = df["Rent"].astype(str)

    df["Rent"] = df["Rent"].str.replace(".", "")

    df["Rent"] = df["Rent"].astype(str)

    df["Rent"] = df["Rent"].str[:4]

    df["Rent"] = df["Rent"].apply(lambda x: 2625 if x == "nan" else x)

    df["Rent"] = df["Rent"].astype(int)

    df["Additional Expenses"] = df["Additional Expenses"].fillna(250)

    df["Additional Expenses"] = df["Additional Expenses"].astype(int)

    df["Bedroom"] = df["Bedroom"].astype(str)

    df["Bedroom"] = df["Bedroom"].str[:1]

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Bedroom"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Zurich ", weight="bold")

    # display the chart
    plt.show()

    df["Bedroom"] = df["Bedroom"].apply(lambda x: 0 if x == "n" else x)

    df["Bedroom"] = df["Bedroom"].loc[df["Bedroom"] != 0]

    df["Bedroom"] = df["Bedroom"].fillna(0)

    df["Bedroom"] = df["Bedroom"].astype(int)

    ### Calculate mean rent for each group + add expenses ###
    one_bed_mean_rent = df[df["Bedroom"] == 1]["Rent"].mean() + 248

    two_bed_mean_rent = df[df["Bedroom"] == 2]["Rent"].mean() + 248

    three_bed_mean_rent = df[df["Bedroom"] == 3]["Rent"].mean() + 248

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

    ax.set_yticklabels(["€0", "€2,000", "€3,000", "€4,000"], weight="bold")

    # Format the x and y-axis labels
    ax.set_xlabel("Number of Bedrooms", weight="bold")

    ax.set_ylabel("Mean Rent (€)", weight="bold")

    # Set the plot title
    ax.set_title("Mean Rent by Number of Bedrooms(Zurich)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
