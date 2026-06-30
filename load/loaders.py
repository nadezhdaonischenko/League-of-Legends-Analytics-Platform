from sqlalchemy import MetaData, Table, text
from sqlalchemy.dialects.postgresql import insert

from load.db import engine

def upsert_dataframe(
        conn,
        df,
        table_name,
        conflict_columns):

    metadata = MetaData()

    table = Table(
        table_name,
        metadata,
        autoload_with=engine
    )

    records = df.to_dict(orient="records")

    if not records:
        return

    stmt = insert(table).values(records)

    stmt = stmt.on_conflict_do_nothing(
        index_elements=conflict_columns
    )

    conn.execute(stmt)

def clear_daily_tables(conn):

    conn.execute(
        text(
            "DELETE FROM players_daily "
            "WHERE snapshot_date = CURRENT_DATE"
        )
    )

    conn.execute(
        text(
            "DELETE FROM champions_daily "
            "WHERE snapshot_date = CURRENT_DATE"
        )
    )

def load_matches(conn, df_matches):

    upsert_dataframe(
        conn,
        df_matches,
        "matches",
        ["match_id"]
    )

    print("Таблица matches успешно загружена")

def load_participants(conn, df_parts):

    upsert_dataframe(
        conn,
        df_parts,
        "participants",
        ["match_id", "puuid"]
    )

    print("Таблица participants успешно загружена")

def load_players(conn,df_players):

    df_players.to_sql(
        "players_daily",
        con=conn,
        if_exists="append",
        index=False
    )

    print("Таблица players успешно загружена")

def load_champions(conn,df_champions):

    df_champions.to_sql(
        "champions_daily",
        con=conn,
        if_exists="append",
        index=False
    )

    print("Таблица champions успешно загружена")
