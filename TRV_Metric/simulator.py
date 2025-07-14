# This simulates when we replace a player
import pandas as pd
from .calculator import calculate_trv

def simulate_substitution(
    team_name: str,
    team_df: pd.DataFrame,
    player_df: pd.DataFrame,
    player_out: str,
    player_in: str,
    weights: dict
) -> pd.DataFrame:
    """
    Simulate replacing one player on a team with another, and recalculate TRVs.
    Prints before/after team vectors and total TRV change for the team.
    """

    # Step 1: Filter current team roster
    current_team = player_df[player_df["Team"] == team_name].copy()
    attribute_cols = [col for col in weights.keys() if col in current_team.columns]
    filtered_weights = {k: weights[k] for k in attribute_cols}

    # Compute baseline team vector and TRVs
    team_vector_before = current_team[attribute_cols].mean()
    def row_to_vector(row): return {attr: row[attr] for attr in attribute_cols}
    current_team["TRV_before"] = current_team.apply(
        lambda row: calculate_trv(row_to_vector(row), team_vector_before.to_dict(), filtered_weights),
        axis=1
    )
    total_trv_before = current_team["TRV_before"].sum()

    # Step 2: Replace player_out with player_in
    current_team = current_team[current_team["Name"] != player_out]
    incoming = player_df[player_df["Name"] == player_in].copy()
    if incoming.empty:
        raise ValueError(f"Replacement player '{player_in}' not found in dataset.")
    # Update their team field to match the target team in player_df in-place
    player_df.loc[player_df["Name"] == player_in, "Team"] = team_name
    if incoming.empty:
        raise ValueError(f"Replacement player '{player_in}' not found in dataset.")
    current_team = pd.concat([current_team, incoming], ignore_index=True)

    # Step 3: Compute new team vector
    team_vector_after = current_team[attribute_cols].mean()

    # Print attribute deltas
    print("\n🧠 Team Vector Comparison (Before vs After Substitution):")
    for attr in attribute_cols:
        before = team_vector_before[attr]
        after = team_vector_after[attr]
        delta = after - before
        print(f"  {attr:<18} | Before: {before:+.3f} | After: {after:+.3f} | Δ: {delta:+.3f}")

    # Step 4: Compute new team TRV
    current_team["TRV_after"] = current_team.apply(
        lambda row: calculate_trv(row_to_vector(row), team_vector_after.to_dict(), filtered_weights),
        axis=1
    )
    total_trv_after = current_team["TRV_after"].sum()

    print(f"\n📊 Total TRV of {team_name} roster:")
    print(f"  Before: {total_trv_before:.3f}")
    print(f"  After : {total_trv_after:.3f}")
    print(f"  Δ TRV : {total_trv_after - total_trv_before:+.3f}")

    # Step 5: Recalculate global TRVs using new team profile
    player_df["TRV"] = player_df.apply(
        lambda row: calculate_trv(row_to_vector(row), team_vector_after.to_dict(), filtered_weights),
        axis=1
    )

    return player_df.sort_values("TRV", ascending=False)
# Now, handle multiple substitutions at once
def simulate_multi_substitution(
    team_name: str,
    team_df: pd.DataFrame,
    player_df: pd.DataFrame,
    substitutions: list[tuple[str, str]],  # List of (out, in) pairs
    weights: dict
) -> pd.DataFrame:
    """
    Simulate multiple player substitutions on a team and print full TRV delta impact.
    """

    # Step 1: Filter team
    current_team = player_df[player_df["Team"] == team_name].copy()
    attribute_cols = [col for col in weights if col in current_team.columns]
    filtered_weights = {k: weights[k] for k in attribute_cols}

    # Step 2: Compute baseline TRV
    team_vector_before = current_team[attribute_cols].mean()
    def row_to_vector(row): return {attr: row[attr] for attr in attribute_cols}
    current_team["TRV_before"] = current_team.apply(
        lambda row: calculate_trv(row_to_vector(row), team_vector_before.to_dict(), filtered_weights),
        axis=1
    )
    total_trv_before = current_team["TRV_before"].sum()

    # Step 3: Apply all substitutions
    for out_name, in_name in substitutions:
        current_team = current_team[current_team["Name"] != out_name]
        incoming = player_df[player_df["Name"] == in_name].copy()
        if incoming.empty:
            raise ValueError(f"Incoming player '{in_name}' not found in dataset.")
        # Set their team to the new team in player_df in-place
        player_df.loc[player_df["Name"] == in_name, "Team"] = team_name
        if incoming.empty:
            raise ValueError(f"Incoming player '{in_name}' not found in dataset.")
        current_team = pd.concat([current_team, incoming], ignore_index=True)

    # Step 4: Compute new vector and TRV
    team_vector_after = current_team[attribute_cols].mean()

    print("\n🧠 Team Vector Comparison (Before vs After Multi-Substitution):")
    for attr in attribute_cols:
        before = team_vector_before[attr]
        after = team_vector_after[attr]
        print(f"  {attr:<18} | Before: {before:+.3f} | After: {after:+.3f} | Δ: {after - before:+.3f}")

    current_team["TRV_after"] = current_team.apply(
        lambda row: calculate_trv(row_to_vector(row), team_vector_after.to_dict(), filtered_weights),
        axis=1
    )
    total_trv_after = current_team["TRV_after"].sum()

    print(f"\n📊 Total TRV of {team_name} roster after {len(substitutions)} substitutions:")
    print(f"  Before: {total_trv_before:.3f}")
    print(f"  After : {total_trv_after:.3f}")
    print(f"  Δ TRV : {total_trv_after - total_trv_before:+.3f}")

    # Final global TRV recalculation
    player_df["TRV"] = player_df.apply(
        lambda row: calculate_trv(row_to_vector(row), team_vector_after.to_dict(), filtered_weights),
        axis=1
    )

    return player_df.sort_values("TRV", ascending=False)
def get_substitution_delta_trv(
    team_name: str,
    player_df: pd.DataFrame,
    player_out: str,
    player_in: str,
    weights: dict
) -> float:
    """
    API-style helper function to get only the delta TRV value for a player substitution.
    Useful for recommendation systems or endpoint responses.
    """
    current_team = player_df[player_df["Team"] == team_name].copy()
    attribute_cols = [col for col in weights.keys() if col in current_team.columns]
    filtered_weights = {k: weights[k] for k in attribute_cols}

    # Baseline TRV
    team_vector_before = current_team[attribute_cols].mean()
    def row_to_vector(row): return {attr: row[attr] for attr in attribute_cols}
    current_team["TRV_before"] = current_team.apply(
        lambda row: calculate_trv(row_to_vector(row), team_vector_before.to_dict(), filtered_weights),
        axis=1
    )
    total_trv_before = current_team["TRV_before"].sum()

    # Apply substitution
    current_team = current_team[current_team["Name"] != player_out]
    incoming = player_df[player_df["Name"] == player_in].copy()
    if incoming.empty:
        raise ValueError(f"Replacement player '{player_in}' not found.")
    player_df.loc[player_df["Name"] == player_in, "Team"] = team_name
    current_team = pd.concat([current_team, incoming], ignore_index=True)

    # New TRV
    team_vector_after = current_team[attribute_cols].mean()
    current_team["TRV_after"] = current_team.apply(
        lambda row: calculate_trv(row_to_vector(row), team_vector_after.to_dict(), filtered_weights),
        axis=1
    )
    total_trv_after = current_team["TRV_after"].sum()

    return total_trv_after - total_trv_before
def recommend_trades(
    team_name: str,
    player_df: pd.DataFrame,
    weights: dict,
    top_n: int = 5
) -> list[tuple[str, str, float]]:
    """
    Recommend top_n player substitutions that would improve the team's TRV the most.
    Returns a list of tuples: (player_out, player_in, delta_trv).
    """
    current_team = player_df[player_df["Team"] == team_name]
    all_other_players = player_df[player_df["Team"] != team_name]
    recommendations = []

    for _, player_out_row in current_team.iterrows():
        for _, player_in_row in all_other_players.iterrows():
            try:
                delta = get_substitution_delta_trv(
                    team_name,
                    player_df.copy(),
                    player_out=player_out_row["Name"],
                    player_in=player_in_row["Name"],
                    weights=weights
                )
                if delta > 0:
                    recommendations.append((
                        player_out_row["Name"],
                        player_in_row["Name"],
                        delta
                    ))
            except Exception:
                continue

    recommendations.sort(key=lambda x: x[2], reverse=True)
    top_recommendations = recommendations[:top_n]
    if not top_recommendations:
        print(f"\n⚠️  No trade recommendations available for {team_name}.")
    else:
        print(f"\nTop trade recommendations for {team_name}:")
        for out_player, in_player, delta in top_recommendations:
            print(f"  Replace {out_player} with {in_player} (Δ TRV: {delta:+.3f})")
    return top_recommendations