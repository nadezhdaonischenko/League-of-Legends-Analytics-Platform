# ====================================================
# АНАЛИЗ ОПРЕДЕЛЕННОГО ИГРОКА
# ====================================================

import pandas as pd
from datetime import datetime, timezone

from extract.riot_client import (
    RiotDataPipeline,
    get_current_month_timestamps
)

from utils.config import MATCHES_PER_PLAYER
from utils.config import API_KEY

from extract.riot_client import set_api_key

set_api_key(API_KEY)

if not API_KEY:
    raise ValueError("RIOT_API_KEY не найден")

REGIONS = {
    "euw1": "europe",
    "eun1": "europe",
    "ru": "europe",
    "tr1": "europe",
    "na1": "americas",
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "kr": "asia",
    "jp1": "asia",
    "tw2": "asia",
    "sg2": "asia"
}

TAG_TO_PLATFORM = {
    "KR": "kr",
    "EUW": "euw1",
    "EUNE": "eun1",
    "NA1": "na1",
    "RU": "ru",
    "TR1": "tr1",
    "JP1": "jp1"
}

POSSIBLE_TAGS = [
    "EUW",
    "EUNE",
    "KR",
    "NA1",
    "RU",
    "TR1",
    "JP1"
]

def find_player_tag(player_name):

    for tag in POSSIBLE_TAGS:

        platform = TAG_TO_PLATFORM.get(tag)

        cluster = REGIONS.get(platform)

        pipeline = RiotDataPipeline(
            platform_id=platform,
            cluster_override=cluster
        )

        puuid = pipeline.fetch_puuid_by_riot_id(
            player_name,
            tag
        )

        if puuid:
            print(f"Найден игрок: {player_name}#{tag}")
            return tag, puuid

    return None, None
    
def analyze_star_player(player_id: str) -> pd.DataFrame:

    """
    Анализ активности игрока Riot в его домашнем регионе.

    Пример:
        analyze_star_player("Hide on bush#KR")
    """

    if "#" not in player_id:
        raise ValueError(
            "Необходимо указать Riot ID"
            "в формате Name#Tag"
            "(например: Phanta#EUW)"
        )

    star_name, star_tag = player_id.split("#", 1)
    star_name = star_name.strip()
    star_tag = star_tag.strip()

    star_home_platform = TAG_TO_PLATFORM.get(
        star_tag.upper()
    )

    if not star_home_platform:
        raise ValueError(
            f"Неизвестный тег региона: {star_tag}"
        )

    star_home_cluster = REGIONS.get(
        star_home_platform,
        "europe"
    )

    print("\n=== Анализ звездного игрока ===")

    start_ts, end_ts = get_current_month_timestamps()

    print(
        f"Поиск игрока "
        f"{player_id} "
        f"({star_home_platform.upper()})"
    )

    star_pipeline = RiotDataPipeline(
        platform_id=star_home_platform,
        cluster_override=star_home_cluster
    )

    star_puuid = star_pipeline.fetch_puuid_by_riot_id(
        star_name,
        star_tag
    )

    if not star_puuid:
        print("Игрок не найден.")
        return pd.DataFrame()

    print(
        f"Найден PUUID игрока: "
        f"{star_puuid[:12]}..."
    )

    print("Сбор матчей игрока...")

    matches = star_pipeline.fetch_player_matches(
        star_puuid,
        start_ts,
        end_ts,
        count=MATCHES_PER_PLAYER
    )   

    total_games = len(matches)

    star_row = {
        "riot_id": player_id,
        "puuid": star_puuid,
        "home_platform": star_home_platform.upper(),
        "home_cluster": star_home_cluster.upper(),
        "total_games_this_month": total_games
    }

    df_star = pd.DataFrame([star_row])

    print("\n--- АНАЛИЗ АКТИВНОСТИ ЗА ТЕКУЩИЙ МЕСЯЦ ---")

    print(
        f"Игрок: {player_id} | "
        f"Домашний регион: "
        f"{star_home_platform.upper()} "
        f"({star_home_cluster.upper()})"
    )

    print(
        f"\nОбщая активность за текущий месяц: "
        f"{total_games} матчей."
    )

    return df_star


if __name__ == "__main__":

    PLAYER_NAME = "Phanta"

    tag, puuid = find_player_tag(PLAYER_NAME)

    if tag is None:
        print("Игрок не найден")
    else:
        df = analyze_star_player(f"{PLAYER_NAME}#{tag}")

    # if not df.empty:
    #     df.to_csv("star_player.csv", index=False, encoding="utf-8-sig")
    #     print("\nФайл star_player.csv успешно сохранен.")