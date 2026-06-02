# ====================================================
# АНАЛИЗ ОПРЕДЕЛЕННОГО ИГРОКА
# ====================================================

import pandas as pd

from riot_pipeline import (
    RiotDataPipeline,
    get_current_month_timestamps
)

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


def analyze_star_player(player_id: str) -> pd.DataFrame:
    """
    Анализ активности игрока Riot по всем глобальным кластерам.

    Пример:
        analyze_star_player("Hide on bush#KR")
    """

    if "#" not in player_id:
        raise ValueError(
            "Необходимо указать Riot ID "
            "в формате Name#Tag "
            "(например: Hide on bush#KR)."
        )

    star_name, star_tag = player_id.split("#", 1)

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
        f"Игрок найден. "
        f"PUUID: {star_puuid[:12]}..."
    )

    pipeline_asia = RiotDataPipeline(
        platform_id="kr",
        cluster_override="asia"
    )

    pipeline_europe = RiotDataPipeline(
        platform_id="euw1",
        cluster_override="europe"
    )

    pipeline_americas = RiotDataPipeline(
        platform_id="na1",
        cluster_override="americas"
    )

    print("Сбор матчей по кластерам...")

    matches_asia = pipeline_asia.fetch_player_matches(
        star_puuid,
        start_ts,
        end_ts,
        count=100
    )

    matches_europe = pipeline_europe.fetch_player_matches(
        star_puuid,
        start_ts,
        end_ts,
        count=100
    )

    matches_americas = pipeline_americas.fetch_player_matches(
        star_puuid,
        start_ts,
        end_ts,
        count=100
    )

    count_asia = len(matches_asia)
    count_europe = len(matches_europe)
    count_americas = len(matches_americas)

    total_games = (
        count_asia +
        count_europe +
        count_americas
    )

    star_row = {
        "riot_id": player_id,
        "puuid": star_puuid,
        "home_platform": star_home_platform.upper(),
        "home_cluster": star_home_cluster.upper(),
        "games_in_asia_cluster": count_asia,
        "games_in_europe_cluster": count_europe,
        "games_in_americas_cluster": count_americas,
        "total_games_this_month": total_games
    }

    df_star = pd.DataFrame([star_row])

    print(
        "\n--- АНАЛИЗ АКТИВНОСТИ "
        "ЗВЕЗДНОГО ИГРОКА ПО КЛАСТЕРАМ RIOT ---"
    )

    print(
        f"Игрок: {player_id} | "
        f"Домашний регион: "
        f"{star_home_platform.upper()} "
        f"({star_home_cluster.upper()})"
    )

    print(
        f" ├─ Матчей в Азии (ASIA):        "
        f"{count_asia}"
    )

    print(
        f" ├─ Матчей в Европе (EUROPE):    "
        f"{count_europe}"
    )

    print(
        f" └─ Матчей в Америке (AMERICAS): "
        f"{count_americas}"
    )

    print(
        f"\nОбщая активность за текущий месяц: "
        f"{total_games} матчей."
    )

    return df_star


if __name__ == "__main__":

    df = analyze_star_player(
        "Hide on bush#KR"               # Пример звездного игрока. Замените на нужного вам игрока.
    )

    # if not df.empty:
    #     df.to_csv("star_player.csv", index=False, encoding="utf-8-sig")
    #
    #     print("\nФайл star_player.csv успешно сохранен.")
