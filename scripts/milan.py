#!/usr/bin/env python3
"""
Milan (Italy) rental market: scraping, cleaning and analysis.

Data source : immobiliare.it
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
DATA_FILE = "milano_rental.csv"


# ======================================================================
# 3. HELPER FUNCTIONS
# ======================================================================
def getAndParseURL(url):
    result = requests.get(url, headers={"User-Agent": "Chrome/ 111.0.5563.111"})
    soup = bts(result.text, "html.parser")
    return soup


# ======================================================================
# 4. DATA COLLECTION (web scraping)
# ======================================================================
def scrape_listings():
    """Scrape the Milan listings from immobiliare.it and save them to a CSV file."""
    pages = ["https://www.immobiliare.it/en/affitto-case/milano/"]

    for page in range(2, 81):
        pages.append("https://www.immobiliare.it/en/affitto-case/milano/?pag=" + str(page))

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("a", {"class": "in-card__title"}):
            links.append(resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            ad_info = html.find("h1", {"class": "in-titleBlock__title"}).text.strip()
        except:
            ad_info = np.nan
        try:
            rent = (
                html.find(
                    "li",
                    {
                        "class": "nd-list__item in-feat__item in-feat__item--main in-detail__mainFeaturesPrice"
                    },
                )
                .text.replace("€ ", "")
                .replace(",", "")
                .replace("/month", "")
            )
        except:
            rent = np.nan
        try:
            room = (
                html.find("dl", {"class": "in-realEstateFeatures__list"})
                .find(text=re.compile("rooms"))
                .findNext()
                .text[0:2]
                .strip()
            )
        except:
            room = np.nan
        try:
            bathroom = html.findAll("div", {"class": "in-feat__data"})[2].text
        except:
            bathroom = np.nan
        try:
            net_area = (
                html.find("dl", {"class": "in-realEstateFeatures__list"})
                .find(text=re.compile("surface"))
                .findNext()
                .text[0:3]
                .strip()
            )
        except:
            net_area = np.nan
        try:
            floor = html.findAll("div", {"class": "in-feat__data"})[3].text.strip()
        except:
            floor = np.nan
        try:
            expenses = (
                html.find("section", {"class": "in-wrapper is-detailView in-landingDetail"})
                .find(text=re.compile("fees"))
                .findNext()
                .text.replace("€ ", "")
                .replace(",", "")
                .replace("/month", "")
                .strip()
            )
        except:
            expenses = np.nan
        try:
            deposit = (
                html.find("section", {"class": "in-wrapper is-detailView in-landingDetail"})
                .find(text=re.compile("Expenses"))
                .findNext()
                .text[60:]
                .replace("€", "")
                .replace(",", "")
                .strip()
            )
        except:
            deposit = np.nan
        time.sleep(2)

        result.append([ad_info, rent, room, bathroom, net_area, floor, expenses, deposit])

    columns = ["Ad_Info", "Rent", "Bedroom", "Bathroom", "Net Area", "Floor", "Expenses", "Deposit"]

    df = pd.DataFrame.from_records(result, columns=columns)

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df["Rent"] = df["Rent"].apply(lambda x: "2000" if x == "Price on application" else x)

    df["Rent"] = df["Rent"].apply(lambda x: "2000" if x == "nan" else x)

    df["Rent"] = df["Rent"].astype(float)

    df["Bathroom"] = df["Bathroom"].apply(lambda x: "3" if x == "3+" else x)

    df["Bathroom"] = df["Bathroom"].apply(lambda x: "1" if x == "G" else x)

    df["Bathroom"] = df["Bathroom"].apply(lambda x: "1" if x == "M" else x)

    df["Bathroom"] = df["Bathroom"].astype(float)

    df["Bathroom"] = df["Bathroom"].fillna(1)

    df["Bathroom"] = df["Bathroom"].astype(int)

    df["Bedroom"] = df["Bedroom"].fillna(22)

    df["Bedroom"] = df["Bedroom"].str.replace("+", "")

    df["Bedroom"] = df["Bedroom"].str.strip()

    df["Bedroom"] = df["Bedroom"].fillna(1)

    df["Bedroom"] = df["Bedroom"].astype(int)

    df["Deposit"] = df["Deposit"].str.strip()

    df["Deposit"] = df["Deposit"].fillna(2000)

    df["Deposit"] = df["Deposit"].astype(int)

    df = df.loc[(df["Deposit"] >= 1000) & (df["Deposit"] <= 45000), :]

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Bedroom"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Milano", weight="bold")

    # display the chart
    plt.show()

    # get the value counts of the 'Bedroom' column
    room_counts = df["Bathroom"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bathroom_counts = room_counts[room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bathroom_counts, labels=filtered_bathroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bathroom Number Flats of Milano", weight="bold")

    # display the chart
    plt.show()

    # Calculate mean rent for each group
    one_bed_mean_rent = df[df["Bedroom"] == 1]["Rent"].mean()

    two_bed_mean_rent = df[df["Bedroom"] == 2]["Rent"].mean()

    three_bed_mean_rent = df[df["Bedroom"] == 3]["Rent"].mean()

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
    ax.set_title("Mean Rent by Number of Bedrooms(Milano)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
