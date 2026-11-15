#!/usr/bin/env python3
"""
Luxembourg (Luxembourg) rental market: scraping, cleaning and analysis.

Data source : athome.lu
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
DATA_FILE = "lxmbrg.csv"


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
    """Scrape the Luxembourg listings from athome.lu and save them to a CSV file."""
    pages = ["https://www.athome.lu/en/rent/apartment/luxembourg"]

    for page in range(2, 66):
        pages.append("https://www.athome.lu/en/rent/apartment/luxembourg?page=" + str(page))

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("link", {"itemprop": "url"}):
            links.append("https://www.athome.lu" + resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            location = html.find(
                "h1", {"class": "KeyInfoBlockStyle__PdpTitle-sc-1o1h56e-2 ilPGib"}
            ).text.strip()
        except:
            location = np.nan
        try:
            rent = (
                html.find("div", {"class": "KeyInfoBlockStyle__Price-sc-1o1h56e-5 fpNLMn"})
                .text.replace(",", "")
                .replace("€", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            add_expenses = (
                html.find("div", {"class": "feature-bloc"})
                .find(text=re.compile("charges"))
                .findNext()
                .text.replace(",", "")
                .replace("€", "")
                .strip()
            )
        except:
            add_expenses = np.nan
        try:
            deposit = (
                html.find("div", {"class": "feature-bloc"})
                .find(text=re.compile("deposit"))
                .findNext()
                .text.replace(",", "")
                .replace("€", "")
                .strip()
            )
        except:
            deposit = np.nan
        try:
            commission = (
                html.find("div", {"class": "feature-bloc"})
                .find(text=re.compile("commission"))
                .findNext()
                .text[0:5]
                .replace(",", "")
                .replace("€", "")
                .replace(".", "")
                .strip()
            )
        except:
            comission = np.nan
        try:
            bedroom = html.find("i", {"class": "icon-bed"}).findNext().text.strip()
        except:
            bedroom = np.nan
        try:
            bathroom = html.find("i", {"class": "icon-bath"}).findNext().text.strip()
        except:
            bathroom = np.nan
        try:
            net_area = (
                html.find("i", {"class": "icon-surface"}).findNext().text.replace(" m²", "").strip()
            )
        except:
            net_area = np.nan
        try:
            car_park = html.find("i", {"class": "icon-car"}).findNext().text.strip()
        except:
            car_park = np.nan
        time.sleep(2)

        result.append(
            [
                location,
                rent,
                add_expenses,
                deposit,
                commission,
                bedroom,
                bathroom,
                net_area,
                car_park,
            ]
        )

    columns = [
        "Location",
        "Rent",
        "Add Expenses",
        "Deposit",
        "Commission",
        "Bedroom",
        "Bathroom",
        "Net Area",
        "Car Park",
    ]

    df = pd.DataFrame.from_records(result, columns=columns)

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df = df.loc[(df["Rent"] >= 800) & (df["Rent"] <= 20000), :]

    df["Bedroom"] = df["Bedroom"].fillna("Studio")

    df["Deposit"] = df["Deposit"].apply(lambda x: 3500 if x == "NC" else x)

    df["Deposit"] = df["Deposit"].astype(int)

    df["Bathroom"] = df["Bathroom"].fillna(1)

    df["Bathroom"] = df["Bathroom"].astype(int)

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Bedroom"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Luxemburg", weight="bold")

    # display the chart
    plt.show()

    # get the value counts of the 'Bedroom' column
    room_counts = df["Bathroom"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bathroom_counts = room_counts[room_counts / len(df) > 0.02]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bathroom_counts, labels=filtered_bathroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bathroom Number Flats of Luxemburg", weight="bold")

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
    ax.set_title("Mean Rent by Number of Bedrooms(Luxemburg)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
