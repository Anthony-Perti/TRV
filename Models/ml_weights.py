# ml_weights.py
import pandas as pd
from collections import defaultdict
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import PolynomialFeatures

def get_ml_weights(team_vector_path="Data/processed/team_vectors.csv") -> dict:
    """
    Fit a polynomial regression model with interactions, then return blended weights.
    """
    df = pd.read_csv(team_vector_path)

    # Actual 2024 win percentages
    win_pct_2024 = {
        "LAD": 0.605, "PHI": 0.586, "NYY": 0.580, "MIL": 0.574, "SDP": 0.574,
        "CLE": 0.571, "BAL": 0.565, "ARI": 0.549, "HOU": 0.547, "ATL": 0.550,
        "NYM": 0.550, "KCR": 0.531, "DET": 0.531, "CHC": 0.512, "CIN": 0.506,
        "SEA": 0.525, "BOS": 0.500, "SFG": 0.494, "MIN": 0.506, "TOR": 0.457,
        "TEX": 0.481, "STL": 0.512, "MIA": 0.457, "PIT": 0.469, "LAA": 0.389,
        "COL": 0.377, "CHW": 0.253, "OAK": 0.426, "WSN": 0.438, "TBR": 0.494,
    }

    df["win_pct"] = df["Team"].map(win_pct_2024)
    df = df.dropna(subset=["win_pct"])

    X = df.drop(columns=["Team", "win_pct"])
    y = df["win_pct"]

    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    X_poly = poly.fit_transform(X)
    feature_names = poly.get_feature_names_out(X.columns)

    model = RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0])
    model.fit(X_poly, y)

    raw_weights = dict(zip(feature_names, model.coef_))

    # Blend interaction weights into base features
    blended_weights = defaultdict(float)
    for name, coef in raw_weights.items():
        parts = name.split(" ")
        if len(parts) == 1:
            blended_weights[parts[0]] += coef
        elif len(parts) == 2:
            blended_weights[parts[0]] += coef / 2
            blended_weights[parts[1]] += coef / 2

    print("R² score:", model.score(X_poly, y))
    return dict(blended_weights)
if __name__ == "__main__":
    weights = get_ml_weights()
    print(weights)