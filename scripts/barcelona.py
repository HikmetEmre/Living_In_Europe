#!/usr/bin/env python3
"""
Barcelona (Spain) rental market: scraping, cleaning and analysis.

Data source : housinganywhere.com
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
DATA_FILE = "barcelona_rental.csv"


# ======================================================================
# 3. HELPER FUNCTIONS
# ======================================================================
def getAndParseURL(url):
    result = requests.get(url, headers={"User-Agent": "Chrome/110.0.5481.178"})
    soup = bts(result.text, "html.parser")
    return soup


def replace_bedroom_value(value):
    if pd.isna(value):
        return 1
    elif "housemates" in value:
        return "shared"
    elif "1 bedroom" in value:
        return 1
    elif "Studio" in value:
        return "1+0"
    elif "Space" in value:
        return "shared"
    elif "housemate" in value:
        return "shared"
    else:
        return value


# ======================================================================
# 4. DATA COLLECTION (web scraping)
# ======================================================================
def scrape_listings():
    """Scrape the Barcelona listings from housinganywhere.com and save them to a CSV file."""
    pages = ["https://housinganywhere.com/s/Barcelona--Spain"]

    for page in range(2, 146):
        pages.append("https://housinganywhere.com/s/Barcelona--Spain?page=" + str(page))

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("a", {"class": "css-16pwyb1-cardLink-link"}):
            links.append("https://housinganywhere.com" + resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            location = html.find(
                "h2",
                {
                    "class": "MuiTypography-root MuiTypography-h2 css-1njgbqb-h2-overflow-initial-color-default-address"
                },
            ).text.strip()
        except:
            location = np.nan
        try:
            rent = (
                html.find(
                    "div",
                    {
                        "class": "MuiGrid-root MuiGrid-container MuiGrid-item MuiGrid-grid-xs-6 css-174xb6y-costName"
                    },
                )
                .text[0:5]
                .replace("€", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            deposit = (
                html.find(
                    "div",
                    {
                        "class": "MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-10 MuiGrid-grid-lg-8 css-1ncwui0"
                    },
                )
                .find(text=re.compile("Deposits"))
                .findNext()
                .text.replace("€", "")
                .strip()
            )
        except:
            deposit = np.nan
        try:
            rooms = (
                html.findAll(
                    "p",
                    {
                        "class": "MuiTypography-root MuiTypography-body1 css-1agh6db-paragraph-overflow-initial-color-default"
                    },
                )[4]
                .text.replace("bedrooms", "")
                .strip()
            )
        except:
            rooms = np.nan
        try:
            capacity = html.findAll(
                "p",
                {
                    "class": "MuiTypography-root MuiTypography-body1 css-1agh6db-paragraph-overflow-initial-color-default"
                },
            )[3].text.strip()
        except:
            capacity = np.nan
        try:
            net_area = (
                html.findAll(
                    "p",
                    {
                        "class": "MuiTypography-root MuiTypography-body1 css-1agh6db-paragraph-overflow-initial-color-default"
                    },
                )[1]
                .text.replace("Property: ", "")
                .replace("m²", "")
                .strip()
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

    df["Rent"] = df["Rent"].astype(float)

    df["Deposit"] = df["Deposit"].astype(float)

    df["Rooms"] = df["Rooms"].apply(replace_bedroom_value)

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Rooms"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Barcelona", weight="bold")

    # display the chart
    plt.show()

    ### Calculate mean rent for each group + add expenses ###
    studio_mean_rent = df[df["Rooms"] == "1+0"]["Rent"].mean()

    one_bed_mean_rent = df[df["Rooms"] == 1]["Rent"].mean()

    two_bed_mean_rent = df[df["Rooms"] == "2"]["Rent"].mean()

    three_bed_mean_rent = df[df["Rooms"] == "3"]["Rent"].mean()

    shared_mean_rent = df[df["Rooms"] == "shared"]["Rent"].mean()

    ### Create a bar plot ###
    sns.set_style("whitegrid")

    ax = sns.barplot(
        x=["Studio", "1 Bedroom", "2 Bedrooms", "3 Bedrooms", "Shared"],
        y=[
            shared_mean_rent,
            studio_mean_rent,
            one_bed_mean_rent,
            two_bed_mean_rent,
            three_bed_mean_rent,
        ],
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
            "Shared",
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
    ax.set_title("Mean Rent by Number of Bedrooms(Barcelona)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
