"""Scrapes the Premier League season page on Wikipedia.

This is the code from the premier-league-webscraper repo, reshaped into functions
that return plain Python data instead of writing CSV files.
"""
from io import StringIO
import re

from bs4 import BeautifulSoup
import pandas as pd
import requests

SEASON = "2026–27"  # en dash, to match Wikipedia's page names
HEADERS = {"User-Agent": "premier-league-stats-app/0.1 (personal learning project)"}

# Maps Wikipedia's full column names (from <abbr title="...">) to our database column names
TEAM_COLUMNS = {
    "Position": "position",
    "Team": "name",
    "Played": "played",
    "Won": "won",
    "Drawn": "drawn",
    "Lost": "lost",
    "Goals for": "goals_for",
    "Goals against": "goals_against",
    "Goal difference": "goal_difference",
    "Points": "points",
}


def get_headers(table):
    """Return the visible text of each header cell, e.g. ['Pos', 'Team', 'Pld', ...]."""
    first_row = table.find("tr")
    return [th.get_text(strip=True) for th in first_row.find_all("th")]


def get_full_headers(table):
    """Return each header's full name from <abbr title="...">, or its text if there's no abbr."""
    first_row = table.find("tr")
    full_names = []
    for th in first_row.find_all("th"):
        abbr = th.find("abbr")
        if abbr and abbr.get("title"):
            full_names.append(abbr.get("title"))
        else:
            full_names.append(th.get_text(strip=True))
    return full_names


def find_table_with_headers(soup, required):
    """Find the first wikitable whose header row contains every name in `required`."""
    for table in soup.find_all("table", class_="wikitable"):
        if all(name in get_headers(table) for name in required):
            return table
    return None


def remove_citations(text):
    """Turn 'Goals[107][108]' into 'Goals'."""
    return re.sub(r"\[\d+\]", "", text).strip()


def clean_team_name(text):
    """Turn 'Wolverhampton Wanderers(R)' into 'Wolverhampton Wanderers'.

    In finished seasons Wikipedia adds markers like (C) champions, (R) relegated,
    (Q) qualified, plus footnotes like [a]. Remove anything in () or [] at the end.
    """
    return re.sub(r"(\s*[\(\[][^\)\]]*[\)\]])+$", "", text).strip()


def to_int(text):
    """Convert text like '+11' or '−3' to a number.

    Wikipedia writes negatives with a Unicode minus sign (−), which int() doesn't
    understand, so swap it for a normal hyphen first.
    """
    return int(str(text).replace("−", "-"))


def scrape_season(season=SEASON):
    """Download the season page and return (teams, scorers) as lists of dictionaries."""
    url = f"https://en.wikipedia.org/wiki/{season}_Premier_League"
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return parse_standings(soup), parse_scorers(soup)


def parse_standings(soup):
    table = find_table_with_headers(soup, ["Pos", "Team", "Pts"])
    if table is None:
        raise ValueError("Couldn't find the league table on the page")

    columns = get_full_headers(table)[:10]
    teams = []
    for row in table.find_all("tr")[1:]:
        cells = row.find_all(["th", "td"])
        values = [cell.get_text(strip=True) for cell in cells[:10]]
        raw = dict(zip(columns, values))

        # Rename the columns and convert numbers from text to int
        team = {}
        for wiki_name, db_name in TEAM_COLUMNS.items():
            team[db_name] = clean_team_name(raw[wiki_name]) if db_name == "name" else to_int(raw[wiki_name])

        link = cells[1].find("a")
        team["wiki_url"] = link.get("href") if link else None
        teams.append(team)
    return teams


def parse_scorers(soup):
    table = find_table_with_headers(soup, ["Rank", "Player", "Club"])
    if table is None:
        return []  # early in a season this table might not exist yet

    df = pd.read_html(StringIO(str(table)))[0]
    df.columns = [remove_citations(col).lower() for col in df.columns]  # 'Goals[107]' -> 'goals'
    return [
        {
            "rank": to_int(row["rank"]),
            "player": str(row["player"]),
            "club": str(row["club"]),
            "goals": to_int(row["goals"]),
        }
        for row in df.to_dict("records")  # one dictionary per row
    ]
