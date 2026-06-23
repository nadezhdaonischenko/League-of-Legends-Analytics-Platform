from datetime import date

import numpy as np
import pandas as pd


def transform_champions(df_raw_parts):

    snapshot_date = date.today()

    # KDA
    safe_deaths = np.maximum(df_raw_parts["deaths"], 1)

    df_raw_parts = df_raw_parts.copy()

    df_raw_parts["kda"] = (
        (df_raw_parts["kills"] + df_raw_parts["assists"])
        / safe_deaths
    )

    df_champions = (
        df_raw_parts
        .groupby("champion_name")
        .agg(
            champion_id=("champion_id", "first"),
            champion_title=("champion_title", "first"),
            champion_tags=("champion_tags", "first"),
            matches_count=("match_id", "count"),
            wins=("win", "sum"),
            avg_kills=("kills", "mean"),
            avg_deaths=("deaths", "mean"),
            avg_assists=("assists", "mean"),
            avg_kda=("kda", "mean"),
            avg_gold_earned=("gold_earned", "mean"),
            avg_damage=("damage_to_champions", "mean"),
            avg_minions_killed=("minions_killed", "mean"),
            avg_vision_score=("vision_score", "mean")
        )
        .reset_index()
    )

    df_champions["losses"] = (
        df_champions["matches_count"]
        - df_champions["wins"]
    )

    df_champions["winrate"] = round(
        (
            df_champions["wins"]
            / df_champions["matches_count"]
        ) * 100,
        2
    )

    avg_cols = [
        col
        for col in df_champions.columns
        if col.startswith("avg_") or col == "winrate"
    ]

    df_champions[avg_cols] = (
        df_champions[avg_cols]
        .round(2)
    )

    final_cols = [
        "champion_id",
        "champion_name",
        "champion_title",
        "champion_tags",
        "matches_count",
        "wins",
        "losses",
        "winrate",
        "avg_kills",
        "avg_deaths",
        "avg_assists",
        "avg_kda",
        "avg_gold_earned",
        "avg_damage",
        "avg_minions_killed",
        "avg_vision_score"
    ]

    df_champions = df_champions[final_cols]

    df_champions["snapshot_date"] = snapshot_date

    return df_champions