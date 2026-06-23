# 🎮 League of Legends Analytics Platform

## 📖 О проекте

League of Legends Analytics Platform — аналитическая платформа для автоматизированного сбора, хранения, обработки и визуализации игровых данных League of Legends с использованием официального Riot Games API.

Проект реализует полный цикл работы с данными:

- получение данных из Riot API;
- хранение данных в PostgreSQL;
- формирование исторических снимков игроков и чемпионов;
- аналитическую обработку данных;
- построение аналитических витрин;
- визуализацию данных через интерактивный веб-дашборд;
- автоматическое ежедневное обновление данных.

---

## 🎯 Цель проекта

Разработка системы аналитики игровых данных, позволяющей исследовать:

- активность игроков высоких рангов;
- эффективность чемпионов;
- распределение рейтинговых очков (LP);
- различия между игровыми регионами;
- динамику показателей во времени.

---

## 🏗 Архитектура решения

```text
                    Riot API
                        │
                        ▼
                     main.py
                (EXTRACT layer)
                        │
                        ▼
              CSV/JSON files (raw data)
                        │
                        ▼
              run_transform_load.py
               (TRANSFORM + LOAD)
                        │
                        ▼
                   PostgreSQL
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
         EDA.py             dashboard_etl.py
            │                       │
            └───────────┬───────────┘
                        ▼
                  Dash Dashboard
```

---

## 📁 Структура проекта

📦 LeagueOfLegendsAnalytics<br>
│<br>
├── 📄 [main.py](./main.py/)<br>
├── 📄 [run_transform_load.py](./run_transform_load.py/)<br>
├── 📄 [EDA.py](./EDA.py/)<br>
├── 📄 [dashboard_etl.py](./dashboard_etl.py/)<br>
├── 📄 [dashboard.py](./dashboard.py/)<br>
├── 📄 [star_player_search.py](./star_player_search.py/)<br>
│<br>
├── 📄 [run_daily_pipeline.bat](./run_daily_pipeline.bat/)<br>
├── 📄 [lol_daily_pipeline.py](./lol_daily_pipeline.py/)<br>
│<br>
├── 📁 extract<br>
│   ├── 📄 [riot_client.py](./riot_client.py/)<br>
│   ├── 📄 [extractor.py](./extractor.py/)<br>
│   └── 📄 [datadragon.py](./datadragon.py/)<br>
│<br>
├── 📁 transform<br>
│   ├── 📄 [matches_transform.py](./matches_transform.py/)<br>
│   ├── 📄 [players_transform.py](./players_transform.py/)<br>
│   └── 📄 [champions_transform.py](./champions_transform.py/)<br>
│<br>
├── 📁 load<br>
│   ├── 📄 [db.py](./db.py/)<br>
│   └── 📄 [loaders.py](./loaders.py/)<br>
│<br>
├── 📁 utils<br>
│   ├── 📄 [config.py](./config.py/)<br>
│   └── 📄 [file_storage.py](./file_storage.py/)<br>
│<br>
├── 📁 data<br>
│   ├── 📄 raw_matches.csv<br>
│   ├── 📄 raw_participants.csv<br>
│   └── 📄 players_registry.json<br>
│<br>
├── 📄 [script_database.sql](./script_database.sql/)<br>
├── 📄 [requirements.txt](./requirements.txt/)<br>
├── 📄 .env<br>
├── 📄 pipeline.log<br>
│<br>
└── 📄 README.md
---

## 📊 Источники данных

### Riot Games API

Используется для получения:

- информации об игроках;
- рейтинговых таблиц;
- истории матчей;
- статистики участников матчей.

### Riot Data Dragon

Используется для получения:

- списка чемпионов;
- названий чемпионов;
- игровых тегов;
- дополнительной справочной информации.

---

## 🌍 Анализируемые регионы

- Europe West (EUW1)
- North America (NA1)

---

## 🏆 Анализируемые лиги

- Challenger
- Grandmaster
- Master

Для каждого ранга анализируются топ-20 игроков региона.

---

# 🗄 Структура базы данных

## Основные таблицы

### matches

Хранит информацию о матчах:

- Match ID;
- регион;
- ранг игрока;
- длительность матча;
- режим игры;
- версия игры;
- дата создания матча.

### participants

Содержит подробную статистику каждого участника матча:

- чемпион;
- команда;
- победа/поражение;
- убийства;
- смерти;
- помощи;
- заработанное золото;
- нанесённый урон;
- количество миньонов;
- обзор карты;
- игровая роль.

---

## Исторические таблицы

### players_daily

Ежедневные снимки игроков.

Используются для анализа:

- LP;
- Win Rate;
- активности игроков;
- изменений рейтинга во времени.

### champions_daily

Ежедневные снимки чемпионов.

Используются для анализа:

- популярности чемпионов;
- KDA;
- Win Rate;
- изменений игровой меты.

---

## Аналитические витрины

Для ускорения работы дашборда используются отдельные агрегированные таблицы:

- dashboard_region_summary
- dashboard_lp_distribution
- dashboard_matches_durations
- dashboard_champions_cleaned
- dashboard_champions_by_region

---

# 📈 [Dashboard](./screenshot_dashboard.jpg/)

Интерактивный веб-дашборд разработан с использованием Dash и Plotly.

---

## KPI-показатели

На главной странице отображаются:

- 👥 количество игроков;
- 🎮 количество матчей;
- 📈 средний Win Rate;
- ⏱ средняя длительность матчей.

---

## Фильтрация данных

### По региону

- Все регионы
- EUW1
- NA1

### По периоду

- Последний снимок
- Текущий месяц
- Последние 30 дней
- Всё время

---

## Визуализации

### 🏹 Топ чемпионов

Отображает:

- популярность чемпионов;
- количество матчей;
- Win Rate.

### 🏆 Распределение LP

Гистограмма распределения рейтинговых очков игроков.

### ⏱ Анализ длительности матчей

Box Plot позволяет сравнивать:

- длительность матчей;
- различия между регионами;
- наличие выбросов.

### ⚔ Анализ игрового стиля чемпионов

Scatter Plot показывает:

- среднее количество убийств;
- среднее количество смертей;
- количество матчей;
- Win Rate;
- эффективность чемпионов.

---

# ⭐ Анализ звездных игроков 

## [star_player_search.py](./star_player_search.py/)

Проект содержит отдельный модуль анализа известных игроков по Riot ID.

Поддерживаются:

- поиск игрока по нику(Name);
- получение PUUID;
- анализ игровой активности;
- кросс-региональный анализ матчей.

Используемые кластеры Riot:

- Asia
- Europe
- Americas

---

# 🔄 ETL-процесс

## [main.py](./main.py/)

**Модуль слоя Extract**

Выполняет:

- получение данных из Riot API;
- сбор информации об игроках и матчах;
- формирование реестра игроков;
- сохранение сырых данных в CSV/JSON файлы.

## [run_transform_load.py](./run_transform_load.py/)

**Модуль слоёв Transform и Load.***

Выполняет:

- загрузку сырых данных из CSV/JSON;
- преобразование матчей, игроков и чемпионов;
- очистку ежедневных таблиц;
- загрузку подготовленных данных в PostgreSQL;
- обновление аналитических таблиц проекта.

---

## [EDA.py](./EDA.py/)

Выполняет аналитическую обработку данных:

- расчёт агрегированных показателей;
- статистический анализ;
- формирование аналитических отчётов.

---

## [dashboard_etl.py](./dashboard_etl.py/)

Формирует специализированные витрины данных для дашборда.

---

# ⏰ Автоматизация

В проекте предусмотрено два варианта автоматизации.



---

## Вариант 1. Windows Task Scheduler

В текущей реализации используется Планировщик заданий Windows.

Ежедневный запуск выполняется через:

### [run_daily_pipeline.bat](./run_daily_pipeline.bat/)

Последовательность выполнения:

```text
run_daily_pipeline.bat
│
├── main.py
├── run_transform_load.py
├── EDA.py
└── dashboard_etl.py
```

Дополнительно ведётся журнал выполнения:

```text
pipeline.log
```

---

## Вариант 2. Apache Airflow

Для промышленного развертывания подготовлен DAG:

### [lol_daily_pipeline.py](./lol_daily_pipeline.py/)

Структура DAG:

```text
collect_riot_data
        │
        ▼
transform_and_load
        │
        ▼
run_eda_analysis
        │
        ▼
refresh_dashboard_tables
```

Преимущества:

- мониторинг выполнения задач;
- журналирование запусков;
- управление зависимостями задач;
- масштабируемость;
- повторные запуски при ошибках.

# 🛠 Используемые технологии

## Backend

- Python
- PostgreSQL
- SQLAlchemy

## Data Processing

- Pandas
- NumPy

## API

- Riot Games API
- Riot Data Dragon

## Visualization

- Dash
- Plotly
- Dash Bootstrap Components

## Automation

- Apache Airflow
- Windows Task Scheduler

---

# 📦 Установка

## 1. Получение проекта

Проект можно скачать командой:

```bash
git clone https://github.com/<ВАШ_ЛОГИН>/<League-of-Legends-Analytics-Platform>.git
cd <LLeague-of-Legends-Analytics-Platform>
```

Либо скачать архив проекта через интерфейс GitHub:

```text
Code → Download ZIP
```

и распаковать его в любую папку на компьютере.

---

## 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## 3. Настройка переменных окружения

Создать файл `.env`

```env
RIOT_API_KEY=YOUR_API_KEY
parole_postgresql=YOUR_PASSWORD
```

### 🔑 Важное примечание по `RIOT_API_KEY`

> ⚠️ **Внимание:** По умолчанию Riot Games предоставляет **Development API Key**, который автоматически сгорает каждые **24 часа**. 

Если ежедневные скрипты перестали собирать данные, выполните следующие шаги:

1. Перейдите на [Riot Developer Portal](https://riotgames.com).
2. Войдите в аккаунт и обновите/скопируйте ваш текущий ключ `RGAPI-...`.
3. Вставьте его в файл `.env` вместо старого значения `YOUR_API_KEY`.
4. **Важно:** После обновления ключа на сайте Riot, подождите **2–3 минуты** перед запуском скрипта. Серверам авторизации Riot требуется время, чтобы новый ключ активировался глобально.

*Для полной автоматизации пайплайна без ежедневной смены ключа рекомендуется подать заявку на **Personal Application** в личном кабинете разработчика Riot для получения бессрочного ключа.*

---

## 4. Создание базы данных

Выполнить SQL-скрипт:

```text
script_database.sql
```

---

## 5. Запуск ETL

```bash
python main.py
python run_transform_load.py
```

---

## 6. Аналитическая обработка

```bash
python EDA.py
```

---

## 7. Обновление витрин

```bash
python dashboard_etl.py
```

---

## 8. Запуск дашборда

```bash
python dashboard.py
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:8050
```

---

# 📚 Полезные ссылки

- Riot Developer Portal: https://developer.riotgames.com/
- Riot Data Dragon: https://developer.riotgames.com/docs/lol#data-dragon
- League of Legends: https://www.leagueoflegends.com/
