# Scraping the data from Statcast, FanGraphs
print(">>> Loaded statcast_fetcher.py")

from pybaseball import batting_stats, team_batting
import pandas as pd
import os

# Output paths
PLAYER_PATH = "Data/Processed/player_vectors.csv"
TEAM_PATH = "Data/Processed/team_vectors.csv"

# === Player Fetching ===
def get_player_stats(year: int = 2024) -> pd.DataFrame:
    """
    Fetch advanced batting stats for all hitters with at least one PA,
    then filter by PA > 150.
    """
    df = batting_stats(year, qual=0)
    print("Initial player count (qual=0):", df.shape)
    df = df[df['PA'] > 150]
    print("After PA > 150 filter:", df.shape)
    return df

# === Team Fetching ===
def get_team_offense_stats(player_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute team-level averages from individual player stats.
    """
    numeric_cols = ['wRC+', 'BsR', 'Z-Contact%', 'ISO', 'Barrel%', 'O-Swing%', 'Def']
    team_df = player_df[["Team"] + numeric_cols].dropna()
    team_avg = team_df.groupby("Team").mean().reset_index()
    print("Team stats shape (computed):", team_avg.shape)
    return team_avg

# === Vectorization Helpers ===
def normalize_series(series):
    return (series - series.mean()) / series.std(ddof=0)

def vectorize_players(df):
    selected = df[[
        'Name', 'Team', 'PA', 'wRC+', 'BsR', 'Z-Contact%', 'ISO', 'Barrel%', 'O-Swing%', 'Def'
    ]].copy()
    selected = selected.dropna()

    selected["offense"] = normalize_series(selected["wRC+"])
    selected["defense"] = normalize_series(selected["Def"])
    selected["baserunning"] = normalize_series(selected["BsR"])
    selected["contact"] = normalize_series(selected["Z-Contact%"])
    selected["power"] = normalize_series((selected["ISO"] + selected["Barrel%"]) / 2)
    selected["plate_discipline"] = normalize_series(100 - selected["O-Swing%"])

    return selected[[
        "Name", "Team", "offense", "defense", "contact",
        "power", "plate_discipline", "baserunning"
    ]]

def vectorize_teams(df):
    df = df.dropna()

    df["offense"] = normalize_series(df["wRC+"])
    df["defense"] = normalize_series(df["Def"])
    df["baserunning"] = normalize_series(df["BsR"])
    df["contact"] = normalize_series(df["Z-Contact%"])
    df["power"] = normalize_series((df["ISO"] + df["Barrel%"]) / 2)
    df["plate_discipline"] = normalize_series(100 - df["O-Swing%"])

    return df[[
        "Team", "offense", "defense", "contact",
        "power", "plate_discipline", "baserunning"
    ]]

# === Main Process ===
def main():
    os.makedirs("Data/Processed", exist_ok=True)

    player_df = get_player_stats()
    team_df = get_team_offense_stats(player_df)

    player_vectors = vectorize_players(player_df)
    team_vectors = vectorize_teams(team_df)

    player_vectors.to_csv(PLAYER_PATH, index=False)
    print(f"Saved {len(player_vectors)} player vectors.")

    team_vectors.to_csv(TEAM_PATH, index=False)
    print("Saved team vectors.")

if __name__ == "__main__":
    main()