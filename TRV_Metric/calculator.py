# Calculator for the TRV Metric
import numpy as np
import pandas as pd

def calculate_trv(player_vector: dict, team_vector: dict, weights: dict, league_avg_vector: dict) -> float:
    """
    Compute raw TRV for one player against one team profile, with redundancy penalty and league average adjustment.
    """
    trv = 0.0
    for attr in weights:
        team_val = team_vector.get(attr, 0.5)
        player_val = player_vector.get(attr, 0.5)
        league_val = league_avg_vector.get(attr, 0.0)

        redundancy_penalty = 1.0 - team_val
        delta = player_val - league_val
        trv += weights[attr] * redundancy_penalty * delta
    return trv

def zscore_trvs(trv_values: list) -> list:
    """
    Normalize a list of TRV values using z-score normalization.
    """
    mean = np.mean(trv_values)
    std = np.std(trv_values, ddof=0)
    return [(val - mean) / std if std > 0 else 0.0 for val in trv_values]