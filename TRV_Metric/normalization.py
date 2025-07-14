#Normalize the data
import pandas as pd

def zscore_normalize(series: pd.Series) -> pd.Series:
    return (series - series.mean()) / series.std()

def normalize_player_vectors(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["offense"] = zscore_normalize(df["wRC+"])
    df["power"] = zscore_normalize(df["ISO"])
    df["plate_discipline"] = zscore_normalize(df["BB%"] / df["K%"])
    return df[["Name", "Team", "offense", "power", "plate_discipline"]]

def normalize_team_vectors(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["offense"] = zscore_normalize(df["wRC+"])
    df["power"] = zscore_normalize(df["ISO"])
    df["plate_discipline"] = zscore_normalize(df["BB%"] / df["K%"])
    return df[["Team", "offense", "power", "plate_discipline"]]