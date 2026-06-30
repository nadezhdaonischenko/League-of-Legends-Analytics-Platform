import time
from datetime import datetime, timezone
import requests
from ratelimit import sleep_and_retry, limits
from utils.config import TIERS

REGION_MAPPING = {
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

# ====================================================
# Сессия
# ====================================================

session = requests.Session()


def set_api_key(api_key):
    session.headers.update({
        "X-Riot-Token": api_key
    })

# ====================================================
# 2. ЗАЩИТА ОТ RATE LIMITS
# ====================================================

@sleep_and_retry
@limits(calls=90, period=120)

def rate_limited_get(url, params=None, max_retries=5):

    for attempt in range(max_retries):

        time.sleep(0.07)

        try:

            response = session.get(
                url,
                params=params,
                timeout=15
            )

            if response.status_code == 429:

                retry_after = int(
                    response.headers.get("Retry-After", 10)
                )

                print(
                    f"\n[Riot API] Лимит исчерпан. "
                    f"Ожидание {retry_after} сек..."
                )

                time.sleep(retry_after)
                continue

            if response.status_code in (500, 502, 503, 504):

                wait_time = 2 ** attempt

                print(
                    f"\n[Riot API] Ошибка {response.status_code}. "
                    f"Повтор через {wait_time} сек..."
                )

                time.sleep(wait_time)
                continue

            return response

        except requests.exceptions.Timeout:
            print("\n[Ошибка] Таймаут запроса")

        except requests.exceptions.ConnectionError:
            print("\n[Ошибка] Нет соединения")

        except Exception as e:
            print(f"\n[Ошибка сети]: {e}")

        time.sleep(2)

    return None


# ====================================================
# 3. ВРЕМЕННОЙ ДИАПАЗОН
# ====================================================

def get_current_month_timestamps():

    now = datetime.now(timezone.utc)

    start_of_month = datetime(
        now.year,
        now.month,
        1,
        tzinfo=timezone.utc
    )

    if now.month == 12:
        end_of_month = datetime(
            now.year + 1,
            1,
            1,
            tzinfo=timezone.utc
        )
    else:
        end_of_month = datetime(
            now.year,
            now.month + 1,
            1,
            tzinfo=timezone.utc
        )

    return (
        int(start_of_month.timestamp()),
        int(end_of_month.timestamp())
    )

# ====================================================
#  4. КЛАСС СБОРЩИКА ДАННЫХ
# ====================================================

class RiotDataPipeline:

    def __init__(
            self,
            platform_id,
            cluster_override=None):

        self.platform_id = platform_id
        self.cluster_id = cluster_override or REGION_MAPPING.get(platform_id)
        
        if not self.cluster_id:
            raise ValueError(f"Неизвестный регион: {platform_id}")

        self.platform_url = f"https://{platform_id}.api.riotgames.com"
        self.cluster_url = f"https://{self.cluster_id}.api.riotgames.com"

    def fetch_puuid_by_riot_id(self, game_name, tag_line):

        url = (
            f"{self.cluster_url}"
            f"/riot/account/v1/accounts/by-riot-id/"
            f"{game_name}/{tag_line}"
        )

        res = rate_limited_get(url)

        if res is None:
            print("Ответ не получен")
            return None

        if res.status_code != 200:
            print(
                f"Игрок {game_name}#{tag_line} "
                f"не найден на кластере {self.cluster_id}"
            )
            return None

        return res.json().get("puuid")
    
    def fetch_leagues_entries(self, tier):

        url = f"{self.platform_url}/lol/league/v4/{tier}leagues/by-queue/RANKED_SOLO_5x5"
        
        res = rate_limited_get(url)
        
        if not res or res.status_code != 200:
            return []
        
        return res.json().get("entries", [])

    def fetch_summoner_by_puuid(self, puuid):

        url = f"{self.platform_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        
        res = rate_limited_get(url)
        
        return res.json() if res and res.status_code == 200 else None

    def fetch_player_matches(
        self,
        puuid,
        start_time,
        end_time,
        count=100):

        url = (
            f"{self.cluster_url}"
            f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        )

        all_matches = []
        start = 0

        while True:

            params = {
                "startTime": start_time,
                "endTime": end_time,
                "queue": 420,
                "start": start,
                "count": count
            }

            res = rate_limited_get(url, params=params)

            if res is None or res.status_code != 200:
                break

            batch = res.json()

            if not batch:
                break

            all_matches.extend(batch)

            if len(batch) < count:
                break

            start += count

        return all_matches

    def fetch_match_details(self, match_id):

        url = f"{self.cluster_url}/lol/match/v5/matches/{match_id}"

        res = rate_limited_get(url)

        return res.json() if res and res.status_code == 200 else None
