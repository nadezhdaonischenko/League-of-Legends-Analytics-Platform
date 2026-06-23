from extract.datadragon import generate_champions_dictionary
from extract.riot_client import (
    RiotDataPipeline,
    TIERS,
    get_current_month_timestamps
)

from utils.config import (
    PLATFORMS,
    TOP_PLAYERS_PER_TIER,
    MATCHES_PER_PLAYER
)

# ====================================================
# 5. ГЛАВНЫЙ ЦИКЛ СБОРА И СВЯЗЫВАНИЯ ТАБЛИЦ
# ====================================================

def extract_data():

    champion_map = generate_champions_dictionary()
    start_ts, end_ts = get_current_month_timestamps()

    raw_matches_list = []
    raw_participants_list = []
    players_registry = {}

    team_id_to_name = {
        100: "Blue",
        200: "Red"
    }

    print("\n=== Сбор данных ===")

    for platform in PLATFORMS:
        pipeline = RiotDataPipeline(platform)
        for tier in TIERS:
            entries = pipeline.fetch_leagues_entries(tier)
            print(f"[{platform.upper()}] Найдено {len(entries)} игроков in лиге {tier.upper()}")
            
            for entry in entries[:TOP_PLAYERS_PER_TIER]:  # Топ-20 
                puuid = entry.get("puuid")
                if not puuid:
                    continue
                
                summoner_data = pipeline.fetch_summoner_by_puuid(puuid)
                # ДЛЯ УБОРКИ UNKNOWN: 
                # Если сервер Riot отдал имя — берем его. 
                # Если сервер занят или лимит ключа исчерпан — генерируем красивый уникальный никнейм по ТЗ
                if summoner_data and summoner_data.get("name"):
                    real_name = summoner_data.get("name")
                else:
                    real_name = f"Summoner_{platform.upper()}_{puuid[:6]}"
                
                players_registry[puuid] = {
                    "puuid": puuid, 
                    "summoner_name": real_name, 
                    "region": platform, 
                    "tier": tier,
                    "league_points": entry.get("leaguePoints", 0), 
                    "wins_total": entry.get("wins", 0), 
                    "losses_total": entry.get("losses", 0),
                    "veteran": entry.get("veteran", False), 
                    "inactive": entry.get("inactive", False),
                    "fresh_blood": entry.get("freshBlood", False), 
                    "hot_streak": entry.get("hotStreak", False)
                }
                
                match_ids = pipeline.fetch_player_matches(
                    puuid,
                    start_ts,
                    end_ts,
                    count=MATCHES_PER_PLAYER
                    )
                    
                print(f"Игрок {real_name} сыграл {len(match_ids)} матчей за месяц")
                
                for m_id in match_ids:
                    match_data = pipeline.fetch_match_details(m_id)
                    if not match_data:
                        continue
                        
                    info = match_data.get("info", {})
                    game_duration = info.get("gameDuration", 0)
                    
                    raw_matches_list.append({
                        "match_id": m_id, 
                        "region": platform, 
                        "tier": tier, 
                        "game_duration": game_duration,
                        "game_mode": info.get("gameMode"), 
                        "game_version": info.get("gameVersion"), 
                        "game_creation": info.get("gameCreation")
                    })
                    
                    winning_team_name = "Unknown"
                    for team in info.get("teams", []):
                        if team.get("win") == True:
                            winning_team_name = team_id_to_name.get(team.get("teamId"), "Unknown")
                    
                    for p in info.get("participants", []):
                        player_team_name = team_id_to_name.get(p.get("teamId"), "Unknown")
                        c_id = p.get("championId")
                        champ_info = champion_map.get(c_id, {"name": f"Unknown_{c_id}", "tags": "Unknown", "title": "Unknown"})

                        raw_participants_list.append({
                            "match_id": m_id,
                            "region": platform, 
                            "puuid": p.get("puuid"), 
                            "champion_name": champ_info["name"], 
                            "champion_id": c_id,
                            "champion_title": champ_info["title"], 
                            "champion_tags": champ_info["tags"], 
                            "team": player_team_name,
                            "winning_team": winning_team_name, 
                            "kills": p.get("kills", 0), 
                            "deaths": p.get("deaths", 0), 
                            "assists": p.get("assists", 0),
                            "gold_earned": p.get("goldEarned", 0), 
                            "damage_to_champions": p.get("totalDamageDealtToChampions", 0),
                            "minions_killed": p.get("totalMinionsKilled", 0), 
                            "vision_score": p.get("visionScore", 0), 
                            "win": p.get("win", False),
                            "role": p.get("role"), 
                            "team_position": p.get("teamPosition"), 
                            "game_duration_sec": game_duration
                        })
    return (
        raw_matches_list,
        raw_participants_list,
        players_registry
        )

