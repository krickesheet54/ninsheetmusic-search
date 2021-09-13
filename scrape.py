"""
Scrape sheet music data from www.ninsheetmusic.org
"""

import json
import os
import requests
from bs4 import BeautifulSoup

# the series page is the easiest to scrape
BASE_URL = "https://www.ninsheetmusic.org"
SERIES_URL = f"{BASE_URL}/browse/series"

def scrape():
    """
    Scrape all data and output as json to stdout
    """
    sheets = scrape_all_series()
    if not sheets:
        return

    print(json.dumps(sheets, indent=2))

def scrape_all_series() -> list:
    """
    Iterate through each series page
    """
    r = requests.get(SERIES_URL)
    if not r.ok:
        return []

    series_page = BeautifulSoup(r.text, "html.parser")
    categories = series_page.select(".browseCategoryList a")
    categories = [c.attrs["href"] for c in categories]

    # iterate over each series
    all_sheets = []
    for c in categories:
        sheets = scrape_series_page(f"{SERIES_URL}/{os.path.basename(c)}")
        all_sheets.extend(sheets)

    return all_sheets

def scrape_series_page(url: str) -> list:
    """
    Scrape data for each game in a series
    """
    r = requests.get(url)
    if not r.ok:
        return []

    page = BeautifulSoup(r.text, "html.parser")

    # get series title
    series_name = list(page.select_one("#mainTitle span").stripped_strings)[0]

    # iterate over each game in the series
    series_sheets = []
    games = page.select(".game")
    for game in games:
        game_title = game.select_one("heading h3").text.strip()
        platform = game.select_one(".consoleList a").text.strip()
        sheets = game.select(".tableList li")
        for sheet in sheets:
            series_sheets.append(scrape_sheet_data(series_name, game_title, platform, sheet))

    return series_sheets

def scrape_sheet_data(series_name: str, game_title: str, platform: str, sheet) -> dict:
    """
    Combine all data for a sheet into a single dict
    """
    title = sheet.select_one(".tableList-cell--sheetTitle").text.strip()
    arranger = sheet.select_one(".tableList-cell--sheetArranger").text.strip()
    pdf = sheet.select_one(".tableList-buttonCell--sheetPdf").attrs["href"].strip()
    midi = sheet.select_one(".tableList-buttonCell--sheetMid").attrs["href"].strip()
    finale = sheet.select_one(".tableList-buttonCell--sheetMus").attrs["href"].strip()

    pdf = f"{BASE_URL}{pdf}"
    midi = f"{BASE_URL}{midi}"
    finale = f"{BASE_URL}{finale}"

    return {
        "series": series_name,
        "game": game_title,
        "platform": platform,
        "title": title,
        "arranger": arranger,
        "pdf": pdf,
        "midi": midi,
        "finale": finale,
    }

if __name__ == "__main__":
    scrape()
