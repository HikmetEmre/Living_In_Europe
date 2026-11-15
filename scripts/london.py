#!/usr/bin/env python3
"""
London (United Kingdom) rental market: scraping, cleaning and analysis.

Data source : primelocation.com & openrent.co.uk
Snapshot    : 2023 (legacy project, converted from a Jupyter notebook)

NOTE: The scraping selectors target the website markup as it was in 2023 and
will most likely no longer work. This script is kept as a readable record of
the original analysis and has not been re-run after conversion.
"""

# ======================================================================
# 1. IMPORTS
# ======================================================================
from urllib.request import urlopen
import os
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
DATA_FILE = "londonn_rental.csv"


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
    """Scrape the London listings from primelocation.com & openrent.co.uk and save them to a CSV file."""
    pages = ["https://www.primelocation.com/to-rent/property/london/?page_size=50"]

    for page in range(2, 201):
        pages.append(
            "https://www.primelocation.com/to-rent/property/london/?identifier=london&page_size=50&q=London&results_sort=newest_listings&radius=0&pn="
            + str(page)
        )

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("a", {"class": "listing-results-price text-price"}):
            links.append("https://www.primelocation.com" + resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            location = html.find("h1", {"class": "listing-details-h1"}).text[15:].strip()
        except:
            location = np.nan
        try:
            rent = (
                html.find("span", {"class": "price"})
                .text.strip()[0:7]
                .replace("£", "")
                .replace(",", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            deposit = (
                html.find("div", {"class": "nts_value"})
                .text.strip()
                .replace("£", "")
                .replace(",", "")
            )
        except:
            deposit = np.nan
        try:
            bedrooms = html.find("span", {"class": "num-icon num-beds"}).text.strip()
        except:
            bedrooms = np.nan
        try:
            bathroom = html.find("span", {"class": "num-icon num-baths"}).text.strip()
        except:
            bathroom = np.nan
        try:
            reception_room = html.find("span", {"class": "num-icon num-reception"}).text.strip()
        except:
            reception_room = np.nan
        time.sleep(2)

        result.append([location, rent, deposit, bedrooms, bathroom, reception_room])

    columns = ["Location", "Rent", "Deposit", "Rooms", "Bathroom", "Reception Room"]

    df = pd.DataFrame.from_records(result, columns=columns)

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df["Rent"] = df["Rent"].apply(lambda x: x.replace("pc", ""))

    df["Rent"] = df["Rent"].apply(lambda x: x.replace("POA", "2500"))

    df["Rent"] = df["Rent"].astype(float)

    df = df.loc[(df["Rent"] >= 800) & (df["Rent"] <= 12000), :]

    ### 1 Pound equal 1.14 Euro###
    df["Rent"] = df["Rent"].apply(lambda x: float(x) * 1.14)

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("nan", "3295"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("992 years", "6590"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("0.14", "3295"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("169 years", "3295"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("982 years", "3295"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("982 years", "3295"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("176 years", "3295"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("985 years", "3295"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("965", "6590"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("989", "6590"))

    df["Deposit"] = df["Deposit"].apply(lambda x: str(x).replace("6590 years", "6590"))

    df["Deposit"] = df["Deposit"].astype(float)

    df = df.loc[(df["Deposit"] >= 800) & (df["Rent"] <= 16000), :]

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace(".", ""))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("nan", "1"))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("10", "1"))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("20", "2"))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("50", "5"))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("60", "6"))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("30", "3"))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("40", "4"))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("100", "10"))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("70", "7"))

    df["Bathroom"] = df["Bathroom"].apply(lambda x: str(x).replace("90", "9"))

    df["Bathroom"] = df["Bathroom"].astype(int)

    # get the value counts of the 'Bedroom' column
    room_counts = df["Bathroom"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bathroom_counts = room_counts[room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bathroom_counts, labels=filtered_bathroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bathroom Number Flats of London ")

    # display the chart
    plt.show()

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace(".", ""))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("nan", "1"))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("10", "1"))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("20", "2"))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("50", "5"))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("60", "6"))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("30", "3"))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("40", "4"))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("100", "10"))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("70", "7"))

    df["Rooms"] = df["Rooms"].apply(lambda x: str(x).replace("80", "9"))

    df["Rooms"] = df["Rooms"].astype(int)

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Rooms"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of London ")

    # display the chart
    plt.show()

    # Calculate mean rent for each group and multiply with 1.14
    one_bed_mean_rent = df[df["Rooms"] == 1]["Rent"].mean() * 1.14

    two_bed_mean_rent = df[df["Rooms"] == 2]["Rent"].mean() * 1.14

    three_bed_mean_rent = df[df["Rooms"] == 3]["Rent"].mean() * 1.14

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

    ax.set_yticklabels(["€0", "€2,000", "€4,000", "€6,000"], weight="bold")

    # Format the x and y-axis labels
    ax.set_xlabel("Number of Bedrooms", weight="bold")

    ax.set_ylabel("Mean Rent (€)", weight="bold")

    # Set the plot title
    ax.set_title("Mean Rent by Number of Bedrooms(London)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
