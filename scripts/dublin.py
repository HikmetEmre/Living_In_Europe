#!/usr/bin/env python3
"""
Dublin (Ireland) rental market: scraping, cleaning and analysis.

Data source : daft.ie
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
DATA_FILE = "ireland_rental.csv"


# ======================================================================
# 3. HELPER FUNCTIONS
# ======================================================================
def getAndParseURL(url):
    result = requests.get(url, headers={"User-Agent": "Chrome/110.0.5481.104"})
    soup = bts(result.text, "html.parser")
    return soup


# ======================================================================
# 4. DATA COLLECTION (web scraping)
# ======================================================================
def scrape_listings():
    """Scrape the Dublin listings from daft.ie and save them to a CSV file."""
    pages = ["https://www.daft.ie/property-for-rent/ireland"]

    for page in range(20, 1141, 20):
        pages.append("https://www.daft.ie/property-for-rent/ireland?from=20&pageSize=" + str(page))

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("a", {"class": "SubUnit__Wrapper-sc-10x486s-0 knvdcE"}):
            links.append("https://www.daft.ie/" + resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            ad_info = html.find(
                "h1", {"class": "TitleBlock__Address-sc-1avkvav-8 dzihxK"}
            ).text.strip()
        except:
            ad_info = np.nan
        try:
            rent = (
                html.find("h2", {"class": "TitleBlock__StyledCustomHeading-sc-1avkvav-5 blbeVq"})
                .text.replace("€", "")
                .replace(",", "")
                .replace(" ", "")
                .replace("permonth", "")
            )
        except:
            rent = np.nan
        try:
            single_bedroom = (
                html.find("ul", {"class": "styles__InfoSection-sc-15fxapi-7 ikMOXo"})
                .text[0:17]
                .replace("Single Bedroom: ", "")
                .strip()
            )
        except:
            single_bedroom = np.nan
        try:
            double_bedroom = (
                html.find("ul", {"class": "styles__InfoSection-sc-15fxapi-7 ikMOXo"})
                .text[0:17]
                .replace("Double Bedroom: ", "")
                .strip()
            )
        except:
            double_bedroom = np.nan
        try:
            bathroom_number1 = (
                html.find("ul", {"class": "styles__InfoSection-sc-15fxapi-7 ikMOXo"})
                .find(text=re.compile("Single Bedroom"))
                .findNext()
                .text.replace("Bathroom:", "")
                .strip()
            )
        except:
            bathroom_number1 = np.nan
        try:
            bathroom_number2 = (
                html.find("ul", {"class": "styles__InfoSection-sc-15fxapi-7 ikMOXo"})
                .find(text=re.compile("Double Bedroom"))
                .findNext()
                .text.replace("Bathroom:", "")
                .strip()
            )
        except:
            bathroom_number2 = np.nan
        time.sleep(2)

        result.append(
            [ad_info, rent, single_bedroom, double_bedroom, bathroom_number1, bathroom_number2]
        )

    columns = ["Ad_Info", "Rent", "Single Bedroom", "Double Bedroom", "Bathroom1", "Bathroom2"]

    df = pd.DataFrame.from_records(result, columns=columns)

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df["Rent"] = pd.to_numeric(df["Rent"], errors="coerce")

    df.drop(columns=["Bathroom1", "Single Bedroom"], inplace=True, axis=1)

    df_new = df.set_index("Ad_Info").filter(like="Dublin", axis=0)

    df_new.columns = df_new.columns.str.strip()

    df_new.drop(columns="Unnamed: 0", axis=0, inplace=True)

    df_new["Rent"] = df_new["Rent"].apply(lambda x: "2520" if x == "630perweek" else x)

    df_new["Rent"] = df_new["Rent"].astype(float)

    df_new["Double Bedroom"] = df_new["Double Bedroom"].apply(
        lambda x: "1" if x == "Single Bedroom: 1" else x
    )

    df_new["Double Bedroom"] = df_new["Double Bedroom"].apply(
        lambda x: "2" if x == "Twin Bedroom: 2Ba" else x
    )

    df_new["Double Bedroom"] = df_new["Double Bedroom"].apply(
        lambda x: "1" if x == "Available From: I" else x
    )

    df_new["Double Bedroom"] = df_new["Double Bedroom"].apply(
        lambda x: "1" if x == "Available From: M" else x
    )

    df_new["Double Bedroom"] = df_new["Double Bedroom"].astype(float)

    df_new["Bathroom2"] = df_new["Bathroom2"].fillna(df_new["Double Bedroom"])

    df_new.rename(columns={"Double Bedroom": "Bedroom", "Bathroom2": "Bathroom"}, inplace=True)

    df_new = df_new.loc[(df_new["Rent"] >= 800) & (df_new["Rent"] <= 10000), :]

    # get the value counts of the 'Bedroom' column
    room_counts = df_new["Bedroom"].value_counts()

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(room_counts, labels=room_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Dublin ")

    # display the chart
    plt.show()

    # get the value counts of the 'Bathroom' column
    room_counts = df_new["Bathroom"].value_counts()

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(room_counts, labels=room_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bathroom Number Flats of Dublin ")

    # display the chart
    plt.show()

    # Calculate mean rent for each group
    one_bed_mean_rent = df_new[df_new["Bedroom"] == 1]["Rent"].mean()

    two_bed_mean_rent = df_new[df_new["Bedroom"] == 2]["Rent"].mean()

    three_bed_mean_rent = df_new[df_new["Bedroom"] == 3]["Rent"].mean()

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
    ax.set_title("Mean Rent by Number of Bedrooms(Dublin)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
