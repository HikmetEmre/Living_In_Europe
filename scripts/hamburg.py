#!/usr/bin/env python3
"""
Hamburg (Germany) rental market: scraping, cleaning and analysis.

Data source : wunderflats.com
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
DATA_FILE = "hamburg_rental.csv"


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
    """Scrape the Hamburg listings from wunderflats.com and save them to a CSV file."""
    pages = ["https://wunderflats.com/en/furnished-apartments/hamburg"]

    for page in range(2, 18):
        pages.append("https://wunderflats.com/en/furnished-apartments/hamburg/" + str(page))

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("a", {"class": "Listing-link"}):
            links.append("https://wunderflats.com" + resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            location = html.find("span", {"class": "txt-light"}).text.strip()
        except:
            location = np.nan
        try:
            rent = (
                html.find("strong", {"class": "ListingPriceText-value"})
                .text.replace("€", "")
                .replace(",", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            deposit = (
                html.findAll("div", {"class": "CostOverview-itemRow"})[1]
                .text.replace("Security deposit€", "")
                .replace(",", "")
                .strip()
            )
        except:
            deposit = np.nan
        try:
            rooms = (
                html.find("span", {"class": "ListingDetails-statsElt rooms"})
                .text.replace("Rooms", "")
                .strip()
            )
        except:
            rooms = np.nan
        try:
            capacity = html.find("span", {"class": "ListingDetails-statsElt guests"}).text.strip()
        except:
            capacity = np.nan
        try:
            net_area = (
                html.find("span", {"class": "ListingDetails-statsElt floor"}).text[0:3].strip()
            )
        except:
            net_area = np.nan
        time.sleep(2)

        result.append([location, rent, deposit, rooms, capacity, net_area])

    columns = ["Location", "Rent", "Deposit", "Rooms", "Capacity", "Net Area"]

    df = pd.DataFrame.from_records(result, columns=columns)

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df["Rooms"] = df["Rooms"].apply(lambda x: "1" if x == "1 Room" else x)

    df["Rooms"] = df["Rooms"].astype(int)

    df["Net Area"] = df["Net Area"].apply(lambda x: "80" if x == "8 m" else x)

    df["Net Area"] = df["Net Area"].apply(lambda x: "90" if x == "9 m" else x)

    df["Net Area"] = df["Net Area"].str.replace(".", "")

    df["Net Area"] = df["Net Area"].astype(int)

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Rooms"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Hamburg", weight="bold")

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
    ax.set_title("Mean Rent by Number of Bedrooms(Hamburg)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
