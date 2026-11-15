#!/usr/bin/env python3
"""
Brussels (Belgium) rental market: scraping, cleaning and analysis.

Data source : spotahome.com
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
DATA_FILE = "brussels.csv"


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
    """Scrape the Brussels listings from spotahome.com and save them to a CSV file."""
    pages = ["https://www.spotahome.com/s/brussels/for-rent:apartments/for-rent:studios"]

    for page in range(2, 103):
        pages.append(
            "https://www.spotahome.com/s/brussels/for-rent:apartments/for-rent:studios/page:"
            + str(page)
        )

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("a", {"class": "home-card__HomecardWrapper___OmV4c"}):
            links.append("https://www.spotahome.com" + resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            ad_info = html.find(
                "h1",
                {
                    "class": "root__Heading___OmV4c dark__Heading___OmV4c large__Heading___OmV4c left__Heading___OmV4c inline__Heading___OmV4c property-title__heading"
                },
            ).text.strip()
        except:
            ad_info = np.nan
        try:
            rent = (
                html.find("p", {"class": "listing-pricing-structured__rent"})
                .text.replace("€", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            bedroom = (
                html.find("div", {"class": "property-title__details"})
                .find(text=re.compile("Apartment"))
                .findNext()
                .text.replace("bedrooms", "")
                .strip()
            )
        except:
            bedroom = np.nan
        try:
            bathroom = (
                html.find("div", {"class": "property-title__details"})
                .find(text=re.compile("rooms"))
                .findNext()
                .text.replace("bathrooms", "")
                .strip()
            )
        except:
            bathroom = np.nan
        try:
            net_area = (
                html.find("div", {"class": "property-title__details"})
                .find(text=re.compile("bathrooms"))
                .findNext()
                .text.replace("m2", "")
                .strip()
            )
        except:
            net_area = np.nan
        time.sleep(2)

        result.append([ad_info, rent, bedroom, bathroom, net_area])

    columns = ["Ad_Info", "Rent", "Bedroom", "Bathroom", "Net Area"]

    df = pd.DataFrame.from_records(result, columns=columns)

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df["Rent"] = df["Rent"].astype(str)

    df["Rent"] = df["Rent"].apply(lambda x: x[0:4])

    df["Rent"] = df["Rent"].apply(lambda x: 1200 if x == "nan" else x)

    df["Rent"] = df["Rent"].astype(int)

    df["Bedroom"] = df["Bedroom"].fillna("Studio")

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Bedroom"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Brussels", weight="bold")

    # display the chart
    plt.show()

    ### Calculate mean rent for each group + add expenses ###
    studio_mean_rent = df[df["Bedroom"] == "Studio"]["Rent"].mean()

    one_bed_mean_rent = df[df["Bedroom"] == 1]["Rent"].mean()

    two_bed_mean_rent = df[df["Bedroom"] == 2]["Rent"].mean()

    three_bed_mean_rent = df[df["Bedroom"] == 3]["Rent"].mean()

    ### Create a bar plot ###
    sns.set_style("whitegrid")

    ax = sns.barplot(
        x=["Studio", "1 Bedroom", "2 Bedrooms", "3 Bedrooms"],
        y=[studio_mean_rent, one_bed_mean_rent, two_bed_mean_rent, three_bed_mean_rent],
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
    ax.set_xticklabels(
        [
            "Studio",
            "1 Bedroom",
            "2 Bedrooms",
            "3 Bedrooms",
        ],
        weight="bold",
    )

    ax.set_yticklabels(["€0", "€2,000", "€3,000"], weight="bold")

    # Format the x and y-axis labels
    ax.set_xlabel("Number of Bedrooms", weight="bold")

    ax.set_ylabel("Mean Rent (€)", weight="bold")

    # Set the plot title
    ax.set_title("Mean Rent by Number of Bedrooms(Brussels)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
