import pandas as pd
import json
import os

os.makedirs("data", exist_ok=True)

def save_raw_data(raw_matches_list, raw_participants_list):

    df_matches = pd.DataFrame(raw_matches_list)
    df_parts = pd.DataFrame(raw_participants_list)

    df_matches.to_csv(
        "data/raw_matches.csv",
        index=False
    )

    df_parts.to_csv(
        "data/raw_participants.csv",
        index=False
    )

    print("Raw data сохранены в папку data/")

def save_players_registry(players_registry):

    with open(
        "data/players_registry.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            players_registry,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("players_registry сохранён")

def load_raw_matches():

    return pd.read_csv(
        "data/raw_matches.csv"
    )


def load_raw_participants():

    return pd.read_csv(
        "data/raw_participants.csv"
    )

def load_players_registry():

    with open(
        "data/players_registry.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)