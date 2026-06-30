import pandas as pd
from load.db import engine

def load_analysis_data():

    try:
        df_players = pd.read_sql("""
                                 SELECT *
                                 FROM players_daily
                                 WHERE snapshot_date = (
                                 SELECT MAX(snapshot_date)
                                 FROM players_daily
                                 )
                                 """, con=engine)
        df_matches = pd.read_sql("""
                                 SELECT * 
                                 FROM matches
                                 """, con=engine)
        df_champions = pd.read_sql("""
                                 SELECT *
                                 FROM champions_daily
                                 WHERE snapshot_date = (
                                 SELECT MAX(snapshot_date)
                                 FROM champions_daily
                                 )
                                 """, con=engine)
        df_parts = pd.read_sql("""
                               SELECT * 
                               FROM participants
                               """, con=engine)

        return (
            df_players,
            df_matches,
            df_champions,
            df_parts
        )

    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return None