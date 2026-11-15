#!/usr/bin/env python3
"""
Europe-wide rental map: combines the per-city results into one comparison.

Input  : city-level averages (rent, deposit, living costs, salary, open jobs)
         that were collected in the per-city scripts and from Glassdoor / Numbeo.
Output : a summary table, a choropleth of mean rent, and an interactive folium map.
Snapshot: 2023 (legacy project, converted from a Jupyter notebook)

NOTE: This script has not been re-run after conversion. Note also that
`gpd.datasets` was removed in GeoPandas 1.0, so the choropleth step needs
GeoPandas < 1.0 (or a Natural Earth shapefile loaded another way).
"""

# ======================================================================
# 1. IMPORTS
# ======================================================================
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from folium.plugins import ScrollZoomToggler
from geopy.geocoders import Nominatim

# ======================================================================
# 2. CONFIGURATION
# ======================================================================
DATA_FILE = "rental_data_with_coords.csv"

# City-level averages (2023). Monthly values.
CITIES = [
    "Dublin",
    "London",
    "Berlin",
    "Amsterdam",
    "Copenhagen",
    "Barcelona",
    "Hamburg",
    "Milano",
    "Luxembourg",
    "Brussels",
    "Paris",
    "Stockholm",
    "Oslo",
    "Munich",
    "Zurich",
    "Istanbul",
]
AVG_RENT = [
    2876,
    3295,
    2340,
    2769,
    2215,
    1433,
    2074,
    1910,
    1587,
    1120,
    3294,
    1564,
    1390,
    2290,
    3186,
    1053,
]
AVG_DEPOSIT = [
    3217,
    3755,
    2675,
    4376,
    6051,
    1430,
    2383,
    2074,
    2606,
    2237,
    4291,
    1590,
    3690,
    2570,
    4407,
    1217,
]
LIVING_COSTS = [
    1016,
    1130,
    981,
    930,
    1044,
    764,
    973,
    965,
    944,
    912,
    1025,
    915,
    1041,
    1027,
    1686,
    515,
]
AVG_SALARY = [
    5916,
    6431,
    6000,
    6520,
    9943,
    3583,
    5416,
    2916,
    5604,
    5123,
    4500,
    7243,
    5102,
    6041,
    11125,
    1914,
]
OPEN_JOBS = [
    1237,
    4698,
    1758,
    747,
    336,
    1118,
    558,
    2340,
    542,
    2214,
    2206,
    737,
    212,
    1632,
    2476,
    306,
]

USER_AGENT = "Chrome/112.0.5615.138"

# Legend for the interactive map (marker colour by average rent)
LEGEND_HTML = """
<div style="position: fixed;
     bottom: 50px; left: 5px; width: 250px; height: 250px;
     border:2px solid black; z-index:9999; font-size:14px;
     background-color: white;">
  <h3 style="margin:2px; font-weight: bold; color: midnightblue;">Cost of Rent in Europe</h3>
  <p style="margin:10px; font-weight: bold;"><span style="color: deepskyblue;">&#9679;</span> Avg Rent &lt; 1800€ <span style="color: deepskyblue;">[Oslo, Stockholm, Istanbul, Barcelona, Brussels, Luxembourg]</span></p>
  <p style="margin:10px; font-weight: bold;"><span style="color: green;">&#9679;</span> 1800€ &le; Avg Rent &lt; 2800€ <span style="color: green;">[Copenhagen, Hamburg, Milano, Munich, Berlin]</span></p>
  <p style="margin:10px; font-weight: bold;"><span style="color: red;">&#9679;</span> Avg Rent &ge; 2800€ <span style="color: red;">[London, Dublin, Paris, Amsterdam, Zurich]</span></p>
</div>
"""


# ======================================================================
# 3. HELPER FUNCTIONS
# ======================================================================
def color_negative_red(val):
    """Style helper for the summary table."""
    if isinstance(val, str):
        return "background-color: lightblue; font-weight: bold"
    color = "red" if val < 0 else "black"
    return "color: %s; font-weight: bold" % color


def get_color(avg_rent):
    """Marker colour for a given average rent."""
    if avg_rent < 1800:
        return "blue"
    elif avg_rent < 2500:
        return "green"
    return "red"


def get_coords(geolocator, city):
    """Return (latitude, longitude) for a city name, or None if not found."""
    location = geolocator.geocode(city)
    if location:
        return location.latitude, location.longitude
    return None


# ======================================================================
# 4. DATA PREPARATION
# ======================================================================
def build_city_table():
    """Assemble the per-city averages into one DataFrame."""
    return pd.DataFrame(
        {
            "City": CITIES,
            "Average Rent": AVG_RENT,
            "Average Deposit": AVG_DEPOSIT,
            "Living Costs": LIVING_COSTS,
            "Average Salary": AVG_SALARY,
            "Open Jobs": OPEN_JOBS,
        }
    )


def style_city_table(table):
    """Return a styled version of the summary table (for notebooks / HTML export)."""
    return (
        table.style.format(
            {
                "Average Rent": "€{:,.0f}",
                "Average Deposit": "€{:,.0f}",
                "Living Costs": "€{:,.0f}",
                "Average Salary": "€{:,.0f}",
            }
        )
        .background_gradient(cmap=sns.light_palette("blue", as_cmap=True))
        .applymap(color_negative_red)
    )


def add_coordinates(table):
    """Geocode every city (Nominatim) and save the result to DATA_FILE."""
    geolocator = Nominatim(user_agent=USER_AGENT)
    coords = table["City"].apply(lambda city: get_coords(geolocator, city))
    table["Latitude"] = coords.apply(lambda x: x[0] if x else None)
    table["Longitude"] = coords.apply(lambda x: x[1] if x else None)
    table.to_csv(DATA_FILE, index=False)
    return table


# ======================================================================
# 5. VISUALISATION
# ======================================================================
def plot_choropleth(table):
    """Static map of the European countries coloured by mean rent."""
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

    # Merge the rental data with the country shapes (by name)
    merged = world.merge(table, left_on="name", right_on="City")
    city_means = table.groupby("City").mean()["Average Rent"]
    merged["Average Rent"] = merged["City"].map(city_means)

    europe = merged.query('continent == "Europe"')
    fig, ax = plt.subplots(figsize=(10, 10))
    europe.plot(
        column="Average Rent",
        cmap="YlOrRd",
        linewidth=0.8,
        edgecolor="gray",
        ax=ax,
        legend=True,
    )
    ax.set_title("Mean Rent by City in Europe", fontdict={"fontsize": "25", "fontweight": "3"})
    ax.set_xlabel("Longitude", fontdict={"fontsize": "20"})
    ax.set_ylabel("Latitude", fontdict={"fontsize": "20"})
    plt.show()


def build_interactive_map(table):
    """Interactive folium map with one coloured marker per city."""
    europe_map = folium.Map(location=[50, 10], zoom_start=4)

    for _, row in table.iterrows():
        if pd.isna(row["Latitude"]) or pd.isna(row["Longitude"]):
            continue
        popup_text = f"{row['City']}<br>Avg Rent: {row['Average Rent']:.2f}€"
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=popup_text,
            icon=folium.Icon(color=get_color(row["Average Rent"])),
        ).add_to(europe_map)

    europe_map.get_root().html.add_child(folium.Element(LEGEND_HTML))
    ScrollZoomToggler().add_to(europe_map)
    return europe_map


# ======================================================================
# 6. ENTRY POINT
# ======================================================================
def main():
    table = add_coordinates(build_city_table())
    # Equivalent to reloading the saved file: table = pd.read_csv(DATA_FILE)
    plot_choropleth(table)
    build_interactive_map(table)


if __name__ == "__main__":
    main()
