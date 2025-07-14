# Rewritten API for TRV to match CSV logic exactly
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from TRV_Metric.calculator import calculate_trv, zscore_trvs
from TRV_Metric.weights import get_weight_scheme
import pandas as pd
import numpy as np
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Load data ===
player_df = pd.read_csv("Data/Processed/player_vectors.csv")
team_df = pd.read_csv("Data/Processed/team_vectors.csv")
league_avg_vector = player_df.drop(columns=["Name", "Team"]).mean().to_dict()


# === Request model ===
class TRVRequest(BaseModel):
    team_name: str
    player_names: List[str]
    weight_scheme: Optional[str] = "Balanced"
    custom_weights: Optional[Dict[str, float]] = None
    average_of: Optional[List[str]] = None

@app.post("/compute_trv/")
def compute_trv(request: TRVRequest):
    try:
        weights = get_weight_scheme(
            scheme_name=request.weight_scheme,
            custom=request.custom_weights,
            average_of=request.average_of,
            team_name=request.team_name,
        )
        print("=== DEBUG: FINAL WEIGHTS USED ===")
        print(json.dumps(weights, indent=2))

        team_vector = team_df.drop(columns=["Team"]).mean().to_dict()

        # Step 1: Compute raw TRVs for ALL players for normalization
        raw_trvs = []
        name_list = []

        for _, row in player_df.iterrows():
            name = row["Name"]
            player_vector = row.drop(["Name", "Team"]).to_dict()
            raw_trv = calculate_trv(player_vector, team_vector, weights, league_avg_vector)
            raw_trvs.append(raw_trv)
            name_list.append(name)

        # Step 2: Normalize using z-score
        zscores = zscore_trvs(raw_trvs)
        trv_map = dict(zip(name_list, zscores))

        # Step 3: Extract requested players' TRVs and raw values
        player_results = []
        total_trv = 0.0
        for name in request.player_names:
            if name not in trv_map:
                player_results.append({"name": name, "error": "Player not found"})
            else:
                idx = name_list.index(name)
                player_results.append({
                    "name": name,
                    "trv": round(zscores[idx], 4),
                    "raw": round(raw_trvs[idx], 4)
                })
                total_trv += zscores[idx]

        return {
            "team": request.team_name,
            "weight_scheme": request.weight_scheme,
            "used_weights": {k: float(v) for k, v in weights.items()},
            "total_trv": round(total_trv, 4),
            "players": player_results,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/players_for_team/")
def get_players_for_team(team_name: str):
    matching_players = player_df[player_df["Team"] == team_name]["Name"].tolist()
    return {"players": matching_players}

# === New League-wide TRV Endpoint ===
@app.post("/league_trv/")
def league_trv(request: TRVRequest):
    try:
        weights = get_weight_scheme(
            scheme_name=request.weight_scheme,
            custom=request.custom_weights,
            average_of=request.average_of,
            team_name=request.team_name,
        )

        # --- Team TRVs (each team vs league avg) ---
        league_team_vectors = team_df.drop(columns=["Team"])
        raw_team_trvs = []
        team_names = []

        for _, row in team_df.iterrows():
            team_name = row["Team"]
            team_vector = row.drop("Team").to_dict()
            raw_trv = calculate_trv(team_vector, league_avg_vector, weights, league_avg_vector)
            raw_team_trvs.append(raw_trv)
            team_names.append(team_name)

        team_zscores = zscore_trvs(raw_team_trvs)
        team_trvs = [
            {"team": name, "trv": round(z, 4)}
            for name, z in zip(team_names, team_zscores)
        ]

        # --- Player TRVs (each player vs their own team) ---
        raw_player_trvs = []
        player_names = []

        for _, row in player_df.iterrows():
            name = row["Name"]
            team = row["Team"]
            player_vector = row.drop(["Name", "Team"]).to_dict()

            matching_team_row = team_df[team_df["Team"] == team]
            if matching_team_row.empty:
                continue
            team_vector = matching_team_row.iloc[0].drop("Team").to_dict()

            raw_trv = calculate_trv(player_vector, team_vector, weights, league_avg_vector)
            raw_player_trvs.append(raw_trv)
            player_names.append(name)

        player_zscores = zscore_trvs(raw_player_trvs)
        player_trvs = [
            {"name": name, "trv": round(z, 4)}
            for name, z in zip(player_names, player_zscores)
        ]

        return {
            "team_trvs": team_trvs,
            "player_trvs": player_trvs,
            "selected_team": request.team_name,
            "selected_players": request.player_names,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
# === Add this to your FastAPI backend (e.g., in api.py) ===
from fastapi import Request
from scipy.stats import norm

@app.post("/trv_distribution/")
async def trv_distribution(request: Request):
    try:
        body = await request.json()
        weights = get_weight_scheme(
            scheme_name=body.get("weight_scheme"),
            custom=body.get("custom_weights"),
            average_of=body.get("average_of"),
            team_name=body.get("team_name")
        )

        team_vector = team_df.drop(columns=["Team"]).mean().to_dict()
        # Compute raw TRVs
        raw_trvs = []
        for _, row in player_df.iterrows():
            player_vector = row.drop(["Name", "Team"]).to_dict()
            trv = calculate_trv(player_vector, team_vector, weights, league_avg_vector)
            raw_trvs.append(trv)

        # Normalize using z-score
        zscores = zscore_trvs(raw_trvs)
        mean = float(np.mean(zscores))  # will be 0
        std = float(np.std(zscores))    # will be 1

        # Bell curve using z-scores
        x_vals = np.linspace(-4, 4, 300)  # wide enough to include any player TRV
        y_vals = norm.pdf(x_vals, mean, std)

        return {
            "x": x_vals.tolist(),
            "y": y_vals.tolist(),
            "mean": mean,
            "std": std
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)
