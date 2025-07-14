#Scrape static playoff odds from fangraphs
import requests
from bs4 import BeautifulSoup
import logging

def fetch_fangraphs_playoff_odds():
    url = "https://www.fangraphs.com/standings/playoff-odds"
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="full-table")

        if not table:
            logging.error("Playoff odds table not found on FanGraphs page.")
            return None

        headers = [th.text.strip() for th in table.find("thead").find_all("th")]
        rows = table.find("tbody").find_all("tr")

        if "Team" not in headers or "Playoff %" not in headers:
            logging.error("Playoff odds table missing expected columns.")
            return None

        team_col = headers.index("Team")
        playoff_col = headers.index("Playoff %")

        odds = {}
        for row in rows:
            cols = row.find_all("td")
            if len(cols) <= max(team_col, playoff_col):
                continue
            team = cols[team_col].text.strip()
            playoff_str = cols[playoff_col].text.strip().replace("%", "")
            try:
                playoff_prob = float(playoff_str) / 100.0
                odds[team] = playoff_prob
            except ValueError:
                continue

        return odds

    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
    except Exception as e:
        logging.error(f"General error fetching playoff odds: {e}")

    logging.error("Failed to fetch playoff odds — falling back to base_weights.")
    return None