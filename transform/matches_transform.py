import pandas as pd


def transform_matches(raw_matches_list):

    df_matches = pd.DataFrame(raw_matches_list)

    if df_matches.empty:
        return df_matches

    df_matches = df_matches.drop_duplicates(
        subset=["match_id"]
    )

    df_matches["game_duration_min"] = round(
        df_matches["game_duration"] / 60,
        2
    )

    matches_cols = [
        "match_id",
        "region",
        "tier",
        "game_duration",
        "game_duration_min",
        "game_mode",
        "game_version",
        "game_creation"
    ]

    return df_matches[matches_cols]