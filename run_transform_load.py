from utils.file_storage import (
    load_raw_matches,
    load_raw_participants,
    load_players_registry
)
from load.db import engine
from transform.matches_transform import transform_matches
from transform.players_transform import transform_players
from transform.champions_transform import transform_champions

from load.loaders import (
    clear_daily_tables,
    load_matches,
    load_participants,
    load_players,
    load_champions
)


def main():

    # ---------------- LOAD RAW CSV ----------------
    df_raw_matches = load_raw_matches()
    df_raw_parts = load_raw_participants()
    players_registry = load_players_registry()

    # ---------------- TRANSFORM ----------------
    df_matches = transform_matches(
        df_raw_matches.to_dict(orient="records")
    )

    df_players = transform_players(
        df_raw_parts,
        players_registry
    )

    df_champions = transform_champions(
        df_raw_parts
    )

    # ---------------- LOAD ----------------
    with engine.begin() as conn:

        clear_daily_tables(conn)

        load_matches(conn, df_matches)

        load_participants(conn, df_raw_parts)

        load_players(conn, df_players)

        load_champions(conn, df_champions)
        
    print("\nTransform + Load завершены успешно!")


if __name__ == "__main__":
    main()
