from dotenv import load_dotenv
import os
import pandas as pd

from extract.riot_client import set_api_key
from extract.extractor import extract_data

from utils.config import API_KEY

from utils.file_storage import (
    save_raw_data,
    save_players_registry
)

load_dotenv()

set_api_key(API_KEY)

if not API_KEY:
    raise ValueError(
        "Добавьте RIOT_API_KEY в .env"
    )

def main():

    # ---------------- EXTRACT ----------------
    raw_matches_list, raw_participants_list, players_registry = extract_data()

    save_raw_data(
        raw_matches_list,
        raw_participants_list
    )

    save_players_registry(
    players_registry
    )

    if not raw_matches_list:
        print("Данные не собраны.")
        return

if __name__ == "__main__":
    main()