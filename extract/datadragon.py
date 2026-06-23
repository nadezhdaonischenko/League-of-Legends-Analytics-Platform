import requests
import pandas as pd

# ==================================================== 
# 2. РАБОТА С RIOT DATA DRAGON 
# ==================================================== 
def generate_champions_dictionary(): 
    """ Скачиваем актуальный патч, создаем файл champions.csv и возвращаем словарь: 
        {int(ID): {"name": Имя, "tags": Теги, "title": Титул}} 
    """ 
    print("Загрузка статических данных из Riot Data Dragon...") 
    
    headers = { 
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/120.0.0.0 Safari/537.36"
        ) 
    }
    
    try: 
    # Получаем список актуальных версий игры 
        version_res = requests.get(
            "https://ddragon.leagueoflegends.com/api/versions.json", 
            headers=headers, 
            timeout=10) 
        version_res.raise_for_status() 
        latest_version = version_res.json()[0] 
        print(f"Актуальный патч Data Dragon: {latest_version}") 
    
        # Загружаем справочник чемпионов 
        champions_url = (
            f"https://ddragon.leagueoflegends.com/cdn/" 
            f"{latest_version}/data/en_US/champion.json") 
    
        response = requests.get(champions_url, headers=headers, timeout=10) 
        response.raise_for_status() 
        champions_data = response.json().get("data", {}) 
        champions_rows = [] 
        champion_map = {} 
    
        for champ_name, champ_info in champions_data.items(): 
            champ_id = int(champ_info["key"]) 
            tags_str = ",".join(champ_info["tags"]) 
            champions_rows.append({
                "champion_id": champ_id, 
                "champion_name": champ_name, 
                "title": champ_info["title"], 
                "tags": tags_str 
                }) 
            champion_map[champ_id] = {
                "name": champ_name, 
                "tags": tags_str, 
                "title": champ_info["title"]
                } 
        champions_df = pd.DataFrame(champions_rows) 

        print(
            f"Успешно сохранен справочник: champions.csv " 
            f"(Размер: {champions_df.shape})" 
            ) 
        return champion_map
         
    except Exception as e: 
        print(f"Ошибка обработки Data Dragon ({e}), используем числовые ID.") 
    return {}