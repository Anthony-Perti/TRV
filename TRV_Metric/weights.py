# Create the weights
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
team_df = pd.read_csv("Data/Processed/team_vectors.csv")

# === 1. Static Weights ===
def get_static_weights(scheme: str) -> dict:
    weights = {
        "Balanced": {
            "offense": 1.0,
            "defense": 1.0,
            "baserunning": 1.0,
            "contact": 1.0,
            "power": 1.0,
            "plate_discipline": 1.0
        },
        "Offense Focused": {
            "offense": 1.5,
            "defense": 0.75,
            "baserunning": 1.0,
            "contact": 1.25,
            "power": 1.5,
            "plate_discipline": 1.25
        },
        "Run Prevention Focused": {
            "offense": 0.75,
            "defense": 1.5,
            "baserunning": 1.25,
            "contact": 1.0,
            "power": 0.8,
            "plate_discipline": 1.0
        }
    }
    return weights.get(scheme, weights["Balanced"])


# === 2. Custom Weights ===
def get_custom_weights(user_input: dict) -> dict:
    return user_input

# === 3. Average Weights ===
def get_average_weights(scheme_names: list[str], custom: dict = None) -> dict:
    from Models.ml_weights import get_ml_weights

    all_weights = []
    for name in scheme_names:
        if name == "Custom" and custom:
            all_weights.append(get_custom_weights(custom))
        elif name == "ML":
            all_weights.append(get_ml_weights())
        else:
            all_weights.append(get_static_weights(name))

    shared_keys = set(all_weights[0].keys())
    for w in all_weights[1:]:
        shared_keys &= set(w.keys())

    avg_weights = {
        k: sum(w[k] for w in all_weights) / len(all_weights)
        for k in shared_keys
    }

    return avg_weights

# === 4. Main Weight Selector ===
def get_weight_scheme(
    scheme_name: str,
    custom: dict = None,
    average_of: list = None,
    team_name: str = None,
    base_scheme: str = "Balanced"  # NEW ARGUMENT
) -> dict:
    from Models.ml_weights import get_ml_weights

    if scheme_name == "Balanced":
        return get_static_weights("Balanced")
    elif scheme_name == "Offense":
        return get_static_weights("Offense Focused")
    elif scheme_name == "Prevention":
        return get_static_weights("Run Prevention Focused")
    elif scheme_name.lower() == "ml":
        return get_ml_weights()
    elif scheme_name == "Custom" and custom:
        return get_custom_weights(custom)
    elif scheme_name == "AverageOf" and average_of:
        return get_average_weights(average_of, custom=custom)
    else:
        raise ValueError(f"Unknown weight scheme: {scheme_name}")
