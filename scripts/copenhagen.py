#!/usr/bin/env python3
"""
Copenhagen (Denmark) rental market: scraping, cleaning and analysis.

Data source : boligzonen.dk
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
DATA_FILE = "copenhagen.csv"


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
    """Scrape the Copenhagen listings from boligzonen.dk and save them to a CSV file."""
    pages = [
        "https://boligzonen.dk/en/housing/kobenhavn?gclid=Cj0KCQjw2cWgBhDYARIsALggUhruGsy5jjcYWEmtMipbd1nKIdqOXy-T0nCsOl0p6HxfrYdJb-SasjYaAhbLEALw_wcB&property_search%5Barea_ids%5D%5B%5D=4&property_search%5Bproperty_type%5D%5B%5D=1&property_search%5Bproperty_type%5D%5B%5D=2&property_search%5Bproperty_type%5D%5B%5D=3&property_search%5Bproperty_type%5D%5B%5D=6&property_search%5Bzip_code_group_ids%5D%5B%5D=48&property_search%5Bzip_code_group_ids%5D%5B%5D=49&property_search%5Bzip_code_group_ids%5D%5B%5D=50&property_search%5Bzip_codes%5D%5B%5D=1000-1473&property_search%5Bzip_codes%5D%5B%5D=1500-1799&property_search%5Bzip_codes%5D%5B%5D=1800-1974&property_search%5Bzip_codes%5D%5B%5D=2000&property_search%5Bzip_codes%5D%5B%5D=2100&property_search%5Bzip_codes%5D%5B%5D=2200&property_search%5Bzip_codes%5D%5B%5D=2300&property_search%5Bzip_codes%5D%5B%5D=2400&property_search%5Bzip_codes%5D%5B%5D=2450&property_search%5Bzip_codes%5D%5B%5D=2500&property_search%5Bzip_codes%5D%5B%5D=2610&property_search%5Bzip_codes%5D%5B%5D=2700&property_search%5Bzip_codes%5D%5B%5D=2720&property_search%5Bzip_codes%5D%5B%5D=2770&property_search%5Bzip_codes%5D%5B%5D=2791&property_search%5Bzip_codes%5D%5B%5D=2860&property_search%5Bzip_codes%5D%5B%5D=2900&property_search%5Bzip_codes%5D%5B%5D=2150&property_type%5B%5D=1&property_type%5B%5D=2&property_type%5B%5D=3&property_type%5B%5D=6"
    ]

    for page in range(2, 114):
        pages.append(
            "https://boligzonen.dk/en/housing/kobenhavn?gclid=Cj0KCQjw2cWgBhDYARIsALggUhruGsy5jjcYWEmtMipbd1nKIdqOXy-T0nCsOl0p6HxfrYdJb-SasjYaAhbLEALw_wcB&page="
            + str(page)
        )

    links = []

    for page in pages:
        html = getAndParseURL(page)
        for resulthf in html.findAll("a", {"class": "property-partial"}):
            links.append("https://boligzonen.dk" + resulthf.get("href"))

    result = []

    for resulthf in links:
        html = getAndParseURL(resulthf)

        try:
            location = html.find("p", {"class": "address-line"}).text.strip()
        except:
            location = np.nan
        try:
            flat_type = (
                html.find("div", {"class": "section-bars section-bars-compact"})
                .find(text=re.compile("type"))
                .findNext()
                .text
            )
        except:
            flat_type = np.nan
        try:
            rent = (
                html.find("div", {"class": "section-bars section-bars-compact"})
                .find(text=re.compile("Monthly"))
                .findNext()
                .text.replace(",", "")
                .replace("-", "")
                .strip()
            )
        except:
            rent = np.nan
        try:
            pre_rent = (
                html.find("div", {"class": "section-bars section-bars-compact"})
                .find(text=re.compile("Prepaid"))
                .findNext()
                .text.replace(",", "")
                .replace("-", "")
                .strip()
            )
        except:
            pre_rent = np.nan
        try:
            deposit = (
                html.find("div", {"class": "section-bars section-bars-compact"})
                .find(text=re.compile("deposit"))
                .findNext()
                .text.replace(",", "")
                .replace("-", "")
                .strip()
            )
        except:
            deposit = np.nan
        try:
            add_exp = (
                html.find("div", {"class": "section-bars section-bars-compact"})
                .find(text=re.compile("Aconto"))
                .findNext()
                .text.replace(",", "")
                .replace("-", "")
                .strip()
            )
        except:
            add_exp = np.nan
        try:
            bedroom = (
                html.find("div", {"class": "section-bars section-bars-compact"})
                .find(text=re.compile("rooms"))
                .findNext()
                .text.strip()
            )
        except:
            bedroom = np.nan
        try:
            net_area = (
                html.find("div", {"class": "section-bars section-bars-compact"})
                .find(text=re.compile("Size"))
                .findNext()
                .text.replace("\xa0m2", "")
                .strip()
            )
        except:
            net_area = np.nan
        try:
            furnished = (
                html.find("div", {"class": "section-bars section-bars-compact"})
                .find(text=re.compile("Furnished"))
                .findNext()
                .text
            )
        except:
            furnished = np.nan
        time.sleep(2)

        result.append(
            [location, flat_type, rent, pre_rent, deposit, add_exp, bedroom, net_area, furnished]
        )

    columns = [
        "Location",
        "Flat Type",
        "Rent",
        "Pre Rent",
        "Deposit",
        "Add Expenses",
        "Bedroom",
        "Net Area",
        "Furnished",
    ]

    df = pd.DataFrame.from_records(result, columns=columns)

    df.to_csv(DATA_FILE)


# ======================================================================
# 5. CLEANING, ANALYSIS AND VISUALISATION
# ======================================================================
def analyse_listings():
    """Load the scraped data, clean it, and produce the summary statistics and plots."""
    df = pd.read_csv(DATA_FILE)

    df["Add Expenses"] = df["Add Expenses"].astype(int)

    df["Add Expenses"] = df["Add Expenses"].apply(lambda x: "1750" if x == "—" else x)

    df["Bedroom"] = df["Bedroom"].astype(int)

    df["Net Area"] = df["Net Area"].astype(int)

    df["Deposit"] = df["Deposit"].astype(int)

    df["Deposit"] = df["Deposit"].apply(lambda x: 15000 if x == "—" else x)

    df["Pre Rent"] = df["Pre Rent"].apply(lambda x: 15000 if x == "—" else x)

    df["Pre Rent"] = df["Pre Rent"].astype(int)

    # get the value counts of the 'Bedroom' column
    bed_room_counts = df["Bedroom"].value_counts()

    # filter the value counts to include only values bigger than 1%
    filtered_bedroom_counts = bed_room_counts[bed_room_counts / len(df) > 0.01]

    # create the pie chart
    plt.figure(figsize=(8, 8))

    plt.pie(filtered_bedroom_counts, labels=filtered_bedroom_counts.index, autopct="%1.1f%%")

    # set the title of the chart
    plt.title("Distrubition of the Bedroom Number Flats of Copenhagen ", weight="bold")

    # display the chart
    plt.show()

    ### Calculate mean rent for each group + add expenses ###
    one_bed_mean_rent = df[df["Bedroom"] == 1]["Rent"].mean() * 0.14 + 200

    two_bed_mean_rent = df[df["Bedroom"] == 2]["Rent"].mean() * 0.14 + 200

    three_bed_mean_rent = df[df["Bedroom"] == 3]["Rent"].mean() * 0.14 + 200

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

    ax.set_yticklabels(["€0", "€2,000", "€3,000"], weight="bold")

    # Format the x and y-axis labels
    ax.set_xlabel("Number of Bedrooms", weight="bold")

    ax.set_ylabel("Mean Rent (€)", weight="bold")

    # Set the plot title
    ax.set_title("Mean Rent by Number of Bedrooms(Copenhagen)", weight="bold")

    plt.show()


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    scrape_listings()
    analyse_listings()


if __name__ == "__main__":
    main()
