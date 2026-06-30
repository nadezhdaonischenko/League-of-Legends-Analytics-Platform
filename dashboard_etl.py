# ====================================================
# ПОДГОТОВКА ДАННЫХ ДЛЯ DASHBOARD
# ====================================================

import pandas as pd
import numpy as np
from sqlalchemy import text
from load.db import engine

def build_dashboard_tables(engine):

    df_players = pd.read_sql("""
                             SELECT *
                             FROM players_daily
                             WHERE snapshot_date = (
                                 SELECT MAX(snapshot_date)
                                 FROM players_daily
                             )
                             """, engine)
    
    df_champions = pd.read_sql("""
                                 SELECT *
                                 FROM champions_daily
                                 WHERE snapshot_date = (
                                     SELECT MAX(snapshot_date)
                                     FROM champions_daily
                                 )
                               """, engine)
    
    df_matches = pd.read_sql("""
                             SELECT *
                             FROM matches
                             """, engine)
    
    df_parts = pd.read_sql("""
                           SELECT *
                           FROM participants
                           """, engine)
    
    region_summary = (
        df_players
        .groupby("region")
        .agg(
            total_tracked_players=("puuid", "count"),
            avg_player_winrate=("winrate", "mean"),
            avg_lp=("league_points", "mean")
        )
        .reset_index()
    )

    lp_dist = df_players[
        [
            "snapshot_date",
            "puuid",
            "region",
            "tier",
            "league_points"
        ]
    ]

    match_durations = df_matches[
        [
            "match_id",
            "region",
            "tier",
            "game_duration_min"
        ]
    ].copy()

    match_durations["game_date"] = pd.to_datetime(
        df_matches["game_creation"],
        unit="ms"
    )

    region_summary["avg_player_winrate"] = (
        region_summary["avg_player_winrate"].round(2)
        )

    region_summary["avg_lp"] = (
        region_summary["avg_lp"].round(2)
        )
    
    df_champions_dashboard = df_champions[
        [
            "snapshot_date",
            "champion_id",
            "champion_name",
            "matches_count",
            "wins",
            "losses",
            "winrate",
            "avg_kda"
        ]
    ]

    df_parts["kda"] = (
        df_parts["kills"] + df_parts["assists"]
        ) / np.maximum(df_parts["deaths"], 1)
    
    champions_by_region = (
        df_parts
        .groupby(["region", "champion_name"])
        .agg(
            matches_count=("match_id", "count"),
            wins=("win", "sum"),
            avg_kills=("kills", "mean"),
            avg_deaths=("deaths", "mean"),
            avg_kda=("kda", "mean")
            )
            .reset_index()
            )
    champions_by_region["winrate"] = round(
        champions_by_region["wins"]
        / champions_by_region["matches_count"] * 100, 2
        )
    
    snapshot_date = df_players["snapshot_date"].max()

    champions_by_region["snapshot_date"] = snapshot_date

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE dashboard_region_summary"))
        conn.execute(text("TRUNCATE dashboard_lp_distribution"))
        conn.execute(text("TRUNCATE dashboard_champions_cleaned"))
        conn.execute(text("TRUNCATE dashboard_matches_durations"))
        conn.execute(text("TRUNCATE dashboard_champions_by_region"))

    region_summary.to_sql(
        "dashboard_region_summary",
        engine,
        if_exists="append",
        index=False
        )
    
    lp_dist.to_sql(
        "dashboard_lp_distribution",
        engine,
        if_exists="append",
        index=False
        )
    
    df_champions_dashboard.to_sql(
        "dashboard_champions_cleaned",
        engine,
        if_exists="append",
        index=False
        )
    
    match_durations.to_sql(
        "dashboard_matches_durations",
        engine,
        if_exists="append",
        index=False
        )
    
    champions_by_region.to_sql(
        "dashboard_champions_by_region",
        engine,
        if_exists="append",
        index=False
        )
    
    print("Dashboard tables успешно обновлены.")

def run_dashboard_etl():
    build_dashboard_tables(engine)

if __name__ == "__main__":
    print("Запуск dashboard_etl...")

    run_dashboard_etl()

    print("Dashboard ETL завершен.")
