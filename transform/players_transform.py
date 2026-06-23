from datetime import date

import pandas as pd


def transform_players(df_raw_parts, players_registry):

    snapshot_date = date.today()

    player_monthly_stats = (
        df_raw_parts[
            df_raw_parts["puuid"].isin(players_registry.keys())
        ]
        .groupby("puuid")
        .agg(
            matches_this_month=("match_id", "count")
        )
        .reset_index()
    )

    players_rows = []

    for puuid, meta in players_registry.items():

        monthly_m = player_monthly_stats[
            player_monthly_stats["puuid"] == puuid
        ]

        matches_count = (
            int(monthly_m["matches_this_month"].iloc[0])
            if not monthly_m.empty
            else 0
        )

        total_games = (
            meta["wins_total"] +
            meta["losses_total"]
        )

        winrate = (
            round(
                meta["wins_total"] / total_games * 100,
                2
            )
            if total_games > 0
            else 0.0
        )

        players_rows.append({
            "puuid": puuid,
            "summoner_name": meta["summoner_name"],
            "region": meta["region"],
            "tier": meta["tier"],
            "league_points": meta["league_points"],
            "wins": meta["wins_total"],
            "losses": meta["losses_total"],
            "winrate": winrate,
            "matches_played_month": matches_count,
            "is_veteran": meta["veteran"],
            "is_inactive": meta["inactive"],
            "is_fresh_blood": meta["fresh_blood"],
            "is_hot_streak": meta["hot_streak"]
        })

    df_players = pd.DataFrame(players_rows)
    df_players["snapshot_date"] = snapshot_date

    return df_players