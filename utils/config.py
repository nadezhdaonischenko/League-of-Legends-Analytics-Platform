import os
from dotenv import load_dotenv

load_dotenv()

# API
API_KEY = os.getenv("RIOT_API_KEY", "").strip()

# Регионы
PLATFORMS = [
    "euw1",
    "na1"
]

# Ранги
TIERS = [
    "challenger",
    "grandmaster",
    "master"
]

# Ограничение игроков на лигу
TOP_PLAYERS_PER_TIER = 20   # Количество игроков на лигу можно корректировать

# Количество матчей на игрока
MATCHES_PER_PLAYER = 100    # Количество матчей - базовое значение
