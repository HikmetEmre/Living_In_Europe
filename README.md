# Living in Europe

A data-mining project on the European rental market: **50,805 rental listings** scraped from local property websites in **16 cities**, compared against average salaries, open jobs and everyday living costs.

> **Heads-up: this is a 2023 snapshot.** All data was collected in 2023 and the scripts are kept as a record of that work. The websites' markup has most likely changed since, so the scrapers will probably no longer work as-is. The code was converted from notebooks to scripts afterwards and **has not been re-run**.

![Mean rent by city in Europe](images/banner.svg)

## Project aim

Moving to another European city raises one practical question: *what will it actually cost me, and does my salary cover it?* Rental prices are published only on scattered local portals, so this project collects them directly from public listings and puts them side by side with income and cost-of-living figures to answer:

1. How much does an average rental flat cost in each city, and how does that change with the number of bedrooms?
2. Which cities are the most and least expensive once deposits and monthly living costs are included?
3. How do salaries and the number of job openings compare to the rent in each city?

## Approach (the data-mining steps)

1. **Collect**: for each city, request the listing pages of a local rental portal, follow every listing link, and extract price, size, rooms, bathrooms, location, deposit and similar fields with `requests` + `BeautifulSoup` (with `time.sleep` delays between requests). Public ads only; no private or sensitive data.
2. **Store**: save the raw table per city to CSV.
3. **Clean**: convert text prices to numbers, strip currency symbols and units, fill or drop missing values, and harmonise room counts.
4. **Analyse**: average rent by number of bedrooms and distribution of flat types (for Istanbul also a breakdown by district, heating type and net area).
5. **Enrich**: add average salaries and job openings (Glassdoor) and living costs excluding rent (Numbeo).
6. **Visualise**: per-city bar and pie charts, then a Europe-wide choropleth and interactive folium map built from the city averages.

## Results at a glance

City-level averages as recorded in the aggregation script ([`scripts/map.py`](scripts/map.py)), sorted by average rent. Values are monthly and shown in euros, as in the original map notebook; "Open jobs" is the number of job openings found.

| City | Avg. rent | Avg. deposit | Living costs (excl. rent) | Avg. salary | Open jobs |
| --- | ---: | ---: | ---: | ---: | ---: |
| London | €3,295 | €3,755 | €1,130 | €6,431 | 4,698 |
| Paris | €3,294 | €4,291 | €1,025 | €4,500 | 2,206 |
| Zurich | €3,186 | €4,407 | €1,686 | €11,125 | 2,476 |
| Dublin | €2,876 | €3,217 | €1,016 | €5,916 | 1,237 |
| Amsterdam | €2,769 | €4,376 | €930 | €6,520 | 747 |
| Berlin | €2,340 | €2,675 | €981 | €6,000 | 1,758 |
| Munich | €2,290 | €2,570 | €1,027 | €6,041 | 1,632 |
| Copenhagen | €2,215 | €6,051 | €1,044 | €9,943 | 336 |
| Hamburg | €2,074 | €2,383 | €973 | €5,416 | 558 |
| Milano | €1,910 | €2,074 | €965 | €2,916 | 2,340 |
| Luxembourg | €1,587 | €2,606 | €944 | €5,604 | 542 |
| Stockholm | €1,564 | €1,590 | €915 | €7,243 | 737 |
| Barcelona | €1,433 | €1,430 | €764 | €3,583 | 1,118 |
| Oslo | €1,390 | €3,690 | €1,041 | €5,102 | 212 |
| Brussels | €1,120 | €2,237 | €912 | €5,123 | 2,214 |
| Istanbul | €1,053 | €1,217 | €515 | €1,914 | 306 |

See the [output gallery](images/README.md) for the per-city charts.

## Data sources and coverage

"Listings scraped" is the row count of the first scraped table (before cleaning), taken from the notebooks' saved output. It was not recorded for Milan and Stockholm; the project total is 50,805.

| City | Country | Source | Listings scraped | Script |
| --- | --- | --- | ---: | --- |
| Amsterdam | Netherlands | funda.nl | 1,273 | [`scripts/amsterdam.py`](scripts/amsterdam.py) |
| Barcelona | Spain | housinganywhere.com | 3,480 | [`scripts/barcelona.py`](scripts/barcelona.py) |
| Berlin | Germany | wunderflats.com | 2,105 | [`scripts/berlin.py`](scripts/berlin.py) |
| Brussels | Belgium | spotahome.com | 6,120 | [`scripts/brussels.py`](scripts/brussels.py) |
| Copenhagen | Denmark | boligzonen.dk | 2,020 | [`scripts/copenhagen.py`](scripts/copenhagen.py) |
| Dublin | Ireland | daft.ie | 1,297 | [`scripts/dublin.py`](scripts/dublin.py) |
| Hamburg | Germany | wunderflats.com | 493 | [`scripts/hamburg.py`](scripts/hamburg.py) |
| Istanbul | Turkey | hepsiemlak.com | 9,884 | [`scripts/istanbul.py`](scripts/istanbul.py) |
| London | United Kingdom | primelocation.com & openrent.co.uk | 8,688 | [`scripts/london.py`](scripts/london.py) |
| Luxembourg | Luxembourg | athome.lu | 1,300 | [`scripts/luxembourg.py`](scripts/luxembourg.py) |
| Milano | Italy | immobiliare.it | – | [`scripts/milan.py`](scripts/milan.py) |
| Munich | Germany | wunderflats.com | 382 | [`scripts/munich.py`](scripts/munich.py) |
| Oslo | Norway | finn.no | 2,550 | [`scripts/oslo.py`](scripts/oslo.py) |
| Paris | France | wunderflats.com | 520 | [`scripts/paris.py`](scripts/paris.py) |
| Stockholm | Sweden | housingtarget.com | – | [`scripts/stockholm.py`](scripts/stockholm.py) |
| Zurich | Switzerland | homegate.ch | 420 | [`scripts/zurich.py`](scripts/zurich.py) |

Additional sources: average salaries and job openings from **glassdoor.com**, living costs except rent from **numbeo.com**.

## Repository structure

```
Living_In_Europe/
├── scripts/          one script per city + map.py (converted from the notebooks)
├── images/           chart outputs, one folder per city (+ README.md gallery)
├── *.ipynb           the original 2023 notebooks, left unchanged
├── requirements.txt
└── README.md
```

Every city script has the same layout: imports, configuration, helper functions, `scrape_listings()`, `analyse_listings()` and `main()`.

## Setup

```bash
pip install -r requirements.txt
```

The scripts are provided for reference. To adapt one, first update the selectors in `scrape_listings()` to the site's current markup, then run e.g. `python scripts/zurich.py`. `scripts/map.py` uses `geopandas.datasets`, which requires GeoPandas < 1.0.
