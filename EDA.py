# ====================================================
# ИССЛЕДОВАТЕЛЬСКИЙ АНАЛИЗ ДАННЫХ
# ====================================================

import os
import pandas as pd
import numpy as np

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_USER = "postgres"
DB_PASSWORD = os.getenv("parole_postgresql", "")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "lol_db"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

def run_exploratory_data_analysis():
    try:
        df_players = pd.read_sql("""
                                 SELECT *
                                 FROM players_daily
                                 WHERE snapshot_date = (
                                 SELECT MAX(snapshot_date)
                                 FROM players_daily
                                 )
                                 """, con=engine)
        df_matches = pd.read_sql("matches", con=engine)
        df_champions = pd.read_sql("""
                                 SELECT *
                                 FROM champions_daily
                                 WHERE snapshot_date = (
                                 SELECT MAX(snapshot_date)
                                 FROM champions_daily
                                 )
                                 """, con=engine)
        df_parts = pd.read_sql("participants", con=engine)

    except FileNotFoundError as e:
        print(f"Ошибка: Не найден файл {e.filename}.")
        return

# ====================================================
# 1: Распределение игроков по очкам лиги (LP)
# ====================================================

    print("\n[1] АНАЛИЗ РАСПРЕДЕЛЕНИЯ ИГРОКОВ ПО ОЧКАМ ЛИГИ (LP)")
    for tier in df_players['tier'].unique():
        tier_data = df_players[df_players['tier'] == tier]['league_points']
        if not tier_data.empty:
            print(f"Лига {tier.upper()}:")
            print(f"  ├─ Количество игроков: {len(tier_data)}")
            print(f"  ├─ Среднее кол-во LP:  {round(tier_data.mean(), 1)}")
            print(f"  ├─ Медиана LP:         {round(tier_data.median(), 1)}")
            print(f"  └─ Разброс (Мин/Макс): {tier_data.min()} / {tier_data.max()} LP")

# ====================================================
# 2: Топ-15 чемпионов по винрейту и популярности
# ====================================================

    print("\n[2] ТОП-15 ЧЕМПИОНОВ ПО ПОПУЛЯРНОСТИ И ИХ ВИНРЕЙТ")
    # Берем топ-15 по количеству сыгранных матчей
    top_15_popular = df_champions.sort_values(by="matches_count", ascending=False).head(15)
    print(top_15_popular[["champion_name", "matches_count", "winrate", "avg_kda"]].to_string(index=False))

    print("\n АБСОЛЮТНЫЙ ТОП-15 ПО ВИНРЕЙТУ (среди чемпионов, сыгравших хотя бы 5 матчей):")
    # Берем топ-15 по проценту побед
    viable_champs = df_champions[df_champions["matches_count"] >= 5]
    top_15_winrate = viable_champs.sort_values(by="winrate", ascending=False).head(15)
    print(top_15_winrate[["champion_name", "matches_count", "winrate", "avg_damage"]].to_string(index=False))

# ====================================================
# 3: Корреляция между длительностью матча и исходом
# ====================================================

    print("\nКОРРЕЛЯЦИЯ МЕЖДУ ДЛИТЕЛЬНОСТЬЮ МАТЧА И ИСХОДОМ:")
    
    # Считаем корреляцию между средней длительностью матчей в регионе и винрейтом игроков
    avg_duration = df_matches["game_duration_min"].mean()
    correlation_outcome = df_players["winrate"].corr(df_players["matches_played_month"])
    
    print(f" ├─ Средняя длительность всех матчей в выборке: {round(avg_duration, 2)} мин.")
    print(f" └─ Коэффициент корреляции между активностью и винрейтом: {round(correlation_outcome, 4)}")
    
    print(" Интерпретация исходов:")
    if abs(correlation_outcome) < 0.2:
        print("  └─ Прямая линейная связь между временем и исходом слабая. Игры сбалансированы.")
    else:
        print("  └─ Длительность сессий имеет выраженное влияние на итоговый винрейт.")

# ====================================================
# 4: Сравнение метрик между регионами
# ====================================================

    print("\n[4] СРАВНЕНИЕ КЛЮЧЕВЫХ МЕТРИК МЕЖДУ РЕГИОНАМИ (EUW1 vs NA1)")
    
    # Сравнение игроков
    regions = df_players['region'].unique()
    print(" Статистика игроков по регионам:")
    for r in regions:
        r_players = df_players[df_players['region'] == r]
        print(f" Регион {r.upper()}:")
        print(f"  ├─ Средний винрейт игроков: {round(r_players['winrate'].mean(), 2)}%")
        print(f"  └─ Среднее кол-во LP:       {round(r_players['league_points'].mean(), 1)} LP")

    # Сравнение матчей
    print("\n Динамика матчей по регионам:")
    for r in df_matches['region'].unique():
        r_matches = df_matches[df_matches['region'] == r]
        print(f" Регион {r.upper()}:")
        print(f"  └─ Средняя длительность игры: {round(r_matches['game_duration_min'].mean(), 2)} минут")

if __name__ == "__main__":
    run_exploratory_data_analysis()