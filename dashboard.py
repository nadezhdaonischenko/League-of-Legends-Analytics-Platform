import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import sys
from datetime import datetime, timedelta
from load.db import engine
from utils.config import MIN_MATCHES_FOR_ANALYTICS

# Инициализируем Dash-приложение с темной темой
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

CARD_STYLE = {
    "borderRadius": "12px",
    "border": "1px solid #495057",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.25)"
    }
KPI_VALUE_CLASS = "display-6 text-center fw-bold"
KPI_LABEL_CLASS = "text-center text-secondary mb-0"

def create_kpi_card(title, value_id, color, icon):
    return dbc.Card(
        dbc.CardBody([
            html.H3(
                id=value_id,
                className=f"{KPI_VALUE_CLASS} {color}"
            ),
            html.P(
                f"{icon} {title}",
                className=KPI_LABEL_CLASS
            )
        ]),
        style=CARD_STYLE
    )

def create_graph_card(graph_id):
    return dbc.Card(
        dbc.CardBody(
            dcc.Loading(
                type="circle",
                children=dcc.Graph(id=graph_id)
            )
        ),
        style=CARD_STYLE
    )

def style_figure(fig):
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text="",
        template="plotly_dark"
    )

    fig.update_xaxes(
        title_font_size=15,
        tickfont_size=12
    )

    fig.update_yaxes(
        title_font_size=15,
        tickfont_size=12
    )

    return fig

app.layout = dbc.Container([

    # Заголовок
    dbc.Row([
        dbc.Col(
            [
                html.H1(
                    "Аналитический дашборд League of Legends",
                    className="text-center text-info fw-bold my-4"
                ),
                html.P(
                    "Статистика игроков, матчей и чемпионов на основе Riot Games API",
                    className="text-center text-secondary mb-4"
                )
            ],     
            width=12
        )
    ]),

    # KPI карточки
    
    dbc.Row([

    dbc.Col(create_kpi_card("Игроков", "total-players", "text-info", "👥"), md=3),
    dbc.Col(create_kpi_card("Матчей", "total-matches", "text-success", "🎮"), md=3),
    dbc.Col(create_kpi_card("Средний Win Rate", "avg-winrate", "text-warning", "🏆"), md=3),
    dbc.Col(create_kpi_card("Средняя длительность", "avg-duration", "text-danger", "⏱"), md=3),

    ], className="mb-4"),

    # Фильтры
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        
                        dbc.Col([
                            html.Label(
                                "🌍 Регион",
                                className="text-info fw-bold mb-2"
                            ),
                            dcc.Dropdown(
                                id="region-dropdown",
                                options=[
                                    {"label": "Все регионы", "value": "both"},
                                    {"label": "Europe West (EUW1)", "value": "euw1"},
                                    {"label": "North America (NA1)", "value": "na1"}
                                ],
                                value="both", clearable=False, style={"color": "#000"}
                            )
                        ], md=4),

                        dbc.Col([
                            html.Label(
                                "📅 Период",
                                className="text-info fw-bold mb-2"
                            ),

                            dcc.Dropdown(
                                id="period-dropdown",
                                options=[
                                    {"label": "Последний снимок", "value": "latest"},
                                    {"label": "Текущий месяц", "value": "current_month"},
                                    {"label": "Последние 30 дней", "value": "last_30_days"},
                                    {"label": "Все время", "value": "all"}
                                ],
                                value="latest", clearable=False, style={"color": "#000"}
                            )
                        ], md=4),

                        dbc.Col([
                            html.Label(
                                "🛡 Чемпион",
                                className="text-info fw-bold mb-2"
                            ),
                            dcc.Dropdown(
                                id="champion-dropdown",
                                options=[
                                    {"label": "Все чемпионы", "value": "all"}
                                ],
                                value="all", clearable=False, searchable=True, style={"color": "#000"}
                            ),
                            html.Small(
                                "Используется только для Scatter-графика",
                                className="text-secondary"
                            )       
                        ], md=4)
                    ])
                ]),
                style=CARD_STYLE
            ),
            width=12
        )
    ], className="mb-4"),

    # Графики
    dbc.Row([

        dbc.Col(
            create_graph_card("top-champions-chart"),
            lg=6,
            md=12
        ),

        dbc.Col(
            create_graph_card("lp-distribution-chart"),
            lg=6,
            md=12
        )], 
    className="mb-4"
    ),

    dbc.Row([

        dbc.Col(
            create_graph_card("match-duration-chart"),
            lg=6,
            md=12
        ),

        dbc.Col(
            create_graph_card("kd-scatter-chart"),
            lg=6,
            md=12
        )], 
    className="mb-4"),

    # Подпись 
    html.Hr(),

    html.P(
        "Разработано с использованием Riot Games API • Dash • PostgreSQL",
        className="text-center text-secondary small mb-3"
    )

], fluid=True)

@app.callback(
    Output("champion-dropdown", "options"),
    Input("region-dropdown", "value")
)
def update_champion_list(selected_region):

    query = """
        SELECT DISTINCT champion_name
        FROM dashboard_champions_by_region
    """

    if selected_region != "both":
        query += f" WHERE region = '{selected_region}'"

    query += " ORDER BY champion_name"

    df = pd.read_sql(query, engine)

    options = [
        {
            "label": "Все чемпионы",
            "value": "all"
        }
    ]

    options.extend(
        {
            "label": champion,
            "value": champion
        }
        for champion in df["champion_name"]
    )

    return options

@app.callback(
    [
        Output('top-champions-chart', 'figure'),
        Output('lp-distribution-chart', 'figure'),
        Output('match-duration-chart', 'figure'),
        Output('kd-scatter-chart', 'figure'),

        Output('total-players', 'children'),
        Output('total-matches', 'children'),
        Output('avg-winrate', 'children'),
        Output('avg-duration', 'children')
    ],
    [
    Input('region-dropdown', 'value'),
    Input('period-dropdown', 'value'),
    Input("champion-dropdown", "value")
    ]
)

def update_dashboard(selected_region, selected_period, selected_champion):

    # Пустые графики по умолчанию
    empty_fig = go.Figure()
    empty_fig.update_layout(
        title="Нет данных",
        template="plotly_dark"
    )

    fig1 = empty_fig
    fig2 = empty_fig
    fig3 = empty_fig
    fig4 = empty_fig

    # KPI по умолчанию
    total_players = "0"
    total_matches = "0"
    avg_winrate = "0%"
    avg_duration = "0 мин"

    # Чтение файлов
    try:
        df_lp = pd.read_sql("SELECT * FROM dashboard_lp_distribution", engine)
        df_champions = pd.read_sql("SELECT * FROM dashboard_champions_by_region", engine)
        df_matches = pd.read_sql("SELECT * FROM dashboard_matches_durations", engine)
        df_players = pd.read_sql("""SELECT * FROM players_daily""", engine)

    except Exception as e:
        print(
            f"\n[КРИТИЧЕСКАЯ ОШИБКА ДАШБОРДА]: {e}",
            file=sys.stderr
        )

        return (
            fig1,
            fig2,
            fig3,
            fig4,
            total_players,
            total_matches,
            avg_winrate,
            avg_duration
        )
    
    df_players["snapshot_date"] = pd.to_datetime(
        df_players["snapshot_date"],
        errors="coerce"
    )

    df_champions["snapshot_date"] = pd.to_datetime(
        df_champions["snapshot_date"],
        errors="coerce"
    )

    df_lp["snapshot_date"] = pd.to_datetime(
        df_lp["snapshot_date"],
        errors="coerce"
    )

    df_matches["game_date"] = pd.to_datetime(
        df_matches["game_date"],
        errors="coerce"
    )

    # Удаляем записи с некорректными датами
    df_players = df_players.dropna(subset=["snapshot_date"])
    df_champions = df_champions.dropna(subset=["snapshot_date"])
    df_lp = df_lp.dropna(subset=["snapshot_date"])
    df_matches = df_matches.dropna(subset=["game_date"])

    # Фильтрация периода

    today = pd.Timestamp.today().normalize()

    if selected_period == "latest":

        latest_snapshot = df_players["snapshot_date"].max()

        df_players = (
            df_players[
                df_players["snapshot_date"] == latest_snapshot
            ]
        )

        df_champions = (
            df_champions[
                df_champions["snapshot_date"] == latest_snapshot
            ]
        )

        df_lp = (
            df_lp[
                df_lp["snapshot_date"] == latest_snapshot
            ]
        )

        # Таблица по матчам накопительная, за последний снимок будем принимать последнюю дату матчей
        latest_match_date = df_matches["game_date"].dt.normalize().max()

        df_matches = df_matches[
        df_matches["game_date"].dt.normalize() == latest_match_date
        ]

    elif selected_period == "current_month":

        start_month = pd.Timestamp(
            year=today.year,
            month=today.month,
            day=1
        )

        df_players = (
            df_players[
                df_players["snapshot_date"] >= start_month
            ]
        )

        df_champions = (
            df_champions[
                df_champions["snapshot_date"] >= start_month
            ]
        )

        df_lp = (
            df_lp[
                df_lp["snapshot_date"] >= start_month
            ]
        )

        df_matches = (
            df_matches[
            df_matches["game_date"] >= start_month
            ]
        )

    elif selected_period == "last_30_days":

        start_date = today - pd.Timedelta(days=30)

        df_players = (
            df_players[
                df_players["snapshot_date"] >= start_date
            ]
        )

        df_champions = (
            df_champions[
                df_champions["snapshot_date"] >= start_date
            ]
        )

        df_lp = (
            df_lp[
                df_lp["snapshot_date"] >= start_date
            ]
        )

        df_matches = (
            df_matches[
                df_matches["game_date"] >= start_date
            ]
        )

    # Фильтрация региона
    if selected_region != "both":

        if "region" in df_lp.columns:
            df_lp = df_lp[
                df_lp["region"] == selected_region
            ]

        if "region" in df_matches.columns:
            df_matches = df_matches[
                df_matches["region"] == selected_region
            ]

        if "region" in df_champions.columns:
            df_champions = df_champions[
                df_champions["region"] == selected_region
            ]

        if "region" in df_players.columns:
            df_players = df_players[
                df_players["region"] == selected_region
            ]

    # KPI карточки
    total_players = str(len(df_players))

    total_matches = str(df_matches["match_id"].nunique())

    # Для расчета винрейта учитываем только игроков, сыгравших минимальное количество матчей для анализа
    
    df_players_wr = df_players[
        df_players["matches_played_month"] >= MIN_MATCHES_FOR_ANALYTICS
    ]

    if not df_players_wr.empty:

        total_wins = df_players_wr["wins"].sum()
        total_losses = df_players_wr["losses"].sum()

        total_games = total_wins + total_losses

        avg_winrate = (
            f"{(total_wins / total_games) * 100:.1f}%"
            if total_games > 0
            else "0%"
        )

    else:
        avg_winrate = "0%"

    avg_duration = (
        f"{df_matches['game_duration_min'].mean():.1f} мин"
        if not df_matches.empty
        else "0 мин"
    )

    # --- [График 1] Топ-15 чемпионов ---
    try:
        if (
            not df_champions.empty
            and "matches_count" in df_champions.columns):

            if selected_region == "both":
                top_15 = (
                    df_champions
                    .groupby("champion_name")
                    .agg(
                        matches_count=("matches_count", "sum"),
                        wins=("wins", "sum")
                    )
                    .reset_index()
                )

                top_15["winrate"] = round(
                    top_15["wins"] / top_15["matches_count"] * 100,
                    2
                )

            else:
                top_15 = df_champions.copy()

            top_15 = top_15[
                top_15["matches_count"] >= MIN_MATCHES_FOR_ANALYTICS
            ]

            top_15 = (
                top_15
                .sort_values(by="matches_count", ascending=False)
                .head(15)
                .sort_values(by="winrate", ascending=True)
            )

            fig1 = style_figure(
                px.bar(
                    top_15,
                    x="winrate",
                    y="champion_name",
                    orientation="h",
                    color="matches_count",
                    title="🏆 Лучшие чемпионы по Win Rate",
                    labels={
                        "winrate": "Винрейт (%)",
                        "champion_name": "Чемпион",
                        "matches_count": "Сыграно матчей"
                    },
                    template="plotly_dark"
                )
            )

            min_wr = top_15["winrate"].min()
            max_wr = top_15["winrate"].max()

            fig1.update_xaxes(
                range=[
                    max(0, min_wr - 2),
                    min(100, max_wr + 2)
                ]
            )

    except Exception as e:
        print(
            f"Ошибка построения Графика 1 (Топ чемпионов): {e}",
            file=sys.stderr
        )

    # --- [График 2] Гистограмма LP ---
    try:
        if not df_lp.empty and 'league_points' in df_lp.columns:
            
            fig2 = px.histogram(
                df_lp, 
                x='league_points', 
                color='tier',
                nbins=10, 
                barmode='group',
                title="📊 Распределение League Points",
                labels={
                    'league_points': 'Текущие LP', 
                    'count': 'Количество игроков', 
                    'tier': 'Ранг'},
                template='plotly_dark'
            )
            style_figure(fig2)

    except Exception as e:
        print(f"Ошибка построения Графика 2 (Гистограмма LP): {e}", file=sys.stderr) 

    # --- [График 3] Диаграмма размаха матчей ---
    try:
        if not df_matches.empty and 'game_duration_min' in df_matches.columns:
            x_col = None

            if selected_region == "both" and "region" in df_matches.columns:
                x_col = "region"
            elif "tier" in df_matches.columns:
                x_col = "tier"

            if x_col is not None:

                fig3 = px.box(
                    df_matches,
                    x=x_col,
                    y="game_duration_min",
                    points="outliers",
                    title="⏱ Длительность матчей",
                    labels={
                        "game_duration_min": "Время игры (мин)",
                        "region": "Регион",
                        "tier": "Ранг"
                    },
                    color=x_col,
                    template="plotly_dark"
                )
                style_figure(fig3)

    except Exception as e:
        print(f"Ошибка построения Графика 3 (Box-plot длительности): {e}", file=sys.stderr)

    # Подготовка данных для Scatter 
    df_scatter = df_champions.copy()

    # Отбираем только чемпионов с достаточным количеством матчей
    df_scatter = df_scatter[
        df_scatter["matches_count"] >= MIN_MATCHES_FOR_ANALYTICS
    ]

    if selected_champion != "all":
        df_scatter = df_scatter[
            df_scatter["champion_name"] == selected_champion
        ]

    # --- [График 4] Карта стилей чемпионов (Scatter) ---
    try:
        if not df_champions.empty and 'avg_deaths' in df_champions.columns and 'avg_kills' in df_champions.columns:

            if not df_scatter.empty:
            
                fig4 = px.scatter(
                    df_scatter, 
                    x='avg_deaths', 
                    y='avg_kills',
                    size='matches_count',
                    color='winrate',
                    size_max=18,
                    hover_name="champion_name",
                    hover_data={
                        "region": True,
                        "matches_count": True,
                        "winrate": ":.2f",
                        "avg_kills": ":.2f",
                        "avg_deaths": ":.2f",
                        "champion_name": False
                    },
                    title="⚔ Соотношение убийств и смертей",
                    labels={
                        'avg_deaths': 'Смерти', 
                        'avg_kills': 'Убийства',
                        "winrate": "WR (%)"
                        },
                    template='plotly_dark',
                    color_continuous_scale='Viridis'
                )
                style_figure(fig4)
            
                fig4.update_layout(
                    legend=dict(
                    orientation="h",
                    y=-0.25
                    )
                )
            
                max_val = max(df_champions['avg_deaths'].max(), df_champions['avg_kills'].max())
                fig4.add_trace(
                    go.Scatter(
                        x=[0, max_val], 
                        y=[0, max_val], 
                        mode='lines', 
                        name='Линия KDA 1.0', 
                        line=dict(dash='dash', color='orange'))
                )
    except Exception as e:
        print(f"Ошибка построения Графика 4 (Scatter-plot): {e}", file=sys.stderr)

    return (
    fig1,
    fig2,
    fig3,
    fig4,
    str(total_players),
    str(total_matches),
    str(avg_winrate),
    str(avg_duration)
    )

if __name__ == "__main__":
    app.run(
        debug=os.getenv("DEBUG", "False").lower() == "true",
        port=8050
    )
