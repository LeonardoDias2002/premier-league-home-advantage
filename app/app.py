import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. Page Configuration & Aesthetics
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Premier League: O Fator Casa",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# High-quality transparent PNGs from a reliable sports CDN
TEAM_LOGOS = {
    "Arsenal": "https://a.espncdn.com/i/teamlogos/soccer/500/359.png",
    "Aston Villa": "https://a.espncdn.com/i/teamlogos/soccer/500/362.png",
    "Bournemouth": "https://a.espncdn.com/i/teamlogos/soccer/500/349.png",
    "Brighton": "https://a.espncdn.com/i/teamlogos/soccer/500/331.png",
    "Burnley": "https://a.espncdn.com/i/teamlogos/soccer/500/379.png",
    "Cardiff": "https://a.espncdn.com/i/teamlogos/soccer/500/347.png",
    "Chelsea": "https://a.espncdn.com/i/teamlogos/soccer/500/363.png",
    "Crystal Palace": "https://a.espncdn.com/i/teamlogos/soccer/500/384.png",
    "Everton": "https://a.espncdn.com/i/teamlogos/soccer/500/368.png",
    "Fulham": "https://a.espncdn.com/i/teamlogos/soccer/500/370.png",
    "Huddersfield": "https://a.espncdn.com/i/teamlogos/soccer/500/335.png",
    "Leeds": "https://a.espncdn.com/i/teamlogos/soccer/500/357.png",
    "Leicester": "https://a.espncdn.com/i/teamlogos/soccer/500/375.png",
    "Liverpool": "https://a.espncdn.com/i/teamlogos/soccer/500/364.png",
    "Man City": "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
    "Man United": "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
    "Newcastle": "https://a.espncdn.com/i/teamlogos/soccer/500/361.png",
    "Sheffield United": "https://a.espncdn.com/i/teamlogos/soccer/500/398.png",
    "Southampton": "https://a.espncdn.com/i/teamlogos/soccer/500/376.png",
    "Tottenham": "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
    "Watford": "https://a.espncdn.com/i/teamlogos/soccer/500/395.png",
    "West Brom": "https://a.espncdn.com/i/teamlogos/soccer/500/383.png",
    "West Ham": "https://a.espncdn.com/i/teamlogos/soccer/500/371.png",
    "Wolves": "https://a.espncdn.com/i/teamlogos/soccer/500/380.png",
}


# -----------------------------------------------------------------------------
# 2. Data Loading & Processing
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df_1819 = pd.read_csv("data/season-1819.csv")
        df_2021 = pd.read_csv("data/season-2021.csv")

        df_1819["Temporada"] = "18/19 (Com Torcida)"
        df_2021["Temporada"] = "20/21 (Sem Torcida)"

        return pd.concat([df_1819, df_2021], ignore_index=True)
    except FileNotFoundError:
        st.error(
            "Erro: Arquivos CSV não encontrados. Certifique-se de que 'season-1819.csv' e 'season-2021.csv' estão no mesmo diretório."
        )
        st.stop()


df = load_data()

# Process data for aggregated metrics and radar chart
records = []
for idx, row in df.iterrows():
    temp = row["Temporada"]
    records.extend(
        [
            {
                "Temporada": temp,
                "Time": row["HomeTeam"],
                "Mando": "Casa",
                "Gols": row["FTHG"],
                "Finalizações": row["HS"],
                "Faltas": row["HF"],
                "Cartões": row["HY"],
            },
            {
                "Temporada": temp,
                "Time": row["AwayTeam"],
                "Mando": "Fora",
                "Gols": row["FTAG"],
                "Finalizações": row["AS"],
                "Faltas": row["AF"],
                "Cartões": row["AY"],
            },
        ]
    )

df_granular = pd.DataFrame(records)
df_agrupado = (
    df_granular.groupby(["Temporada", "Mando"])[
        ["Gols", "Finalizações", "Faltas", "Cartões"]
    ]
    .mean()
    .reset_index()
)

# Process data for Scatter Plot
home_avg = df.groupby(["Temporada", "HomeTeam"])["FTHG"].mean().reset_index()
home_avg.columns = ["Temporada", "Time", "Media_Gols_Casa"]

away_avg = df.groupby(["Temporada", "AwayTeam"])["FTAG"].mean().reset_index()
away_avg.columns = ["Temporada", "Time", "Media_Gols_Fora"]

df_times = pd.merge(home_avg, away_avg, on=["Temporada", "Time"])
df_times["Logo_URL"] = df_times["Time"].map(TEAM_LOGOS)

# -----------------------------------------------------------------------------
# 3. Sidebar UI: Central do Clube (Interactive & Comparative)
# -----------------------------------------------------------------------------
st.sidebar.title("⚽ Central do Clube")
st.sidebar.markdown("Compare o perfil tático e disciplinar das equipes.")

all_teams = sorted(df_times["Time"].unique())

col_t1, col_t2 = st.sidebar.columns(2)
with col_t1:
    team_1 = st.selectbox(
        "Clube Principal:", all_teams, index=all_teams.index("Arsenal")
    )
    if team_1 in TEAM_LOGOS:
        st.image(TEAM_LOGOS[team_1], width=80)

with col_t2:
    team_2 = st.selectbox(
        "Comparar com:", ["Nenhum"] + all_teams, index=all_teams.index("Everton") + 1
    )
    if team_2 != "Nenhum" and team_2 in TEAM_LOGOS:
        st.image(TEAM_LOGOS[team_2], width=80)

temporada_radar = st.sidebar.radio(
    "Selecione a Temporada para Análise:",
    ["18/19 (Com Torcida)", "20/21 (Sem Torcida)"],
)


# Radar Chart Builder
def plot_radar(t1, t2, season):
    categories = ["Gols", "Finalizações", "Faltas", "Cartões"]
    fig = go.Figure()

    def add_team_trace(team_name, color):
        stats = df_granular[
            (df_granular["Time"] == team_name) & (df_granular["Temporada"] == season)
        ][categories].mean()
        # Normalize data slightly for better radar shape
        max_vals = df_granular[df_granular["Temporada"] == season][categories].max()
        normalized_stats = stats / max_vals * 100

        fig.add_trace(
            go.Scatterpolar(
                r=normalized_stats.values.tolist()
                + [normalized_stats.values.tolist()[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name=team_name,
                line=dict(color=color),
                hovertemplate="%{theta}: %{customdata:.2f}<extra></extra>",
                customdata=stats.values.tolist() + [stats.values.tolist()[0]],
            )
        )

    add_team_trace(t1, "#00ff85")  # PL Green
    if t2 != "Nenhum":
        add_team_trace(t2, "#38003c")  # PL Purple

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
    )
    return fig


st.sidebar.markdown(f"**Análise de Desempenho Relativo ({temporada_radar})**")
st.sidebar.plotly_chart(
    plot_radar(team_1, team_2, temporada_radar), use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("**INF01047 - Lab 3**\n\nCriado por Leonardo Dias")

# -----------------------------------------------------------------------------
# 4. Main Dashboard Area
# -----------------------------------------------------------------------------
st.title("O Fator Casa na Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿")
st.markdown(
    "Investigando o impacto da presença de público através da comparação entre as temporadas **18/19 (Estádios Cheios)** e **20/21 (Portões Fechados)**."
)
st.divider()

# --- Section 1: Scatter Plots with Plotly (Real Logos) ---
st.subheader("1. A Convergência Ofensiva: Desempenho Granular")
st.markdown(
    "A linha tracejada representa a bissetriz ($y = x$). Times abaixo da linha marcam mais em casa; times acima marcam mais fora."
)


def criar_scatter_plotly(temporada):
    df_temp = df_times[df_times["Temporada"] == temporada]
    fig = go.Figure()

    # Add the diagonal reference line
    fig.add_trace(
        go.Scatter(
            x=[0, 3.5],
            y=[0, 3.5],
            mode="lines",
            line=dict(color="gray", dash="dash"),
            name="Linha de Equilíbrio (Casa = Fora)",
            hoverinfo="skip",
        )
    )

    # Add hidden scatter points for hover text
    fig.add_trace(
        go.Scatter(
            x=df_temp["Media_Gols_Casa"],
            y=df_temp["Media_Gols_Fora"],
            mode="markers",
            marker=dict(size=1, color="rgba(0,0,0,0)"),  # Invisible markers
            text=df_temp["Time"],
            hovertemplate="<b>%{text}</b><br>Casa: %{x:.2f}<br>Fora: %{y:.2f}<extra></extra>",
        )
    )

    # Iterate through data to place logo images
    for idx, row in df_temp.iterrows():
        # Highlight logic: if a team is selected in sidebar, fade the others
        opacity = 1.0
        size = 0.35
        if team_1 != "Nenhum" or team_2 != "Nenhum":
            if row["Time"] not in [team_1, team_2]:
                opacity = 0.2
                size = 0.25
            else:
                size = 0.5  # Make selected teams slightly larger

        fig.add_layout_image(
            dict(
                source=row["Logo_URL"],
                xref="x",
                yref="y",
                x=row["Media_Gols_Casa"],
                y=row["Media_Gols_Fora"],
                sizex=size,
                sizey=size,
                xanchor="center",
                yanchor="middle",
                opacity=opacity,
            )
        )

    fig.update_layout(
        title=temporada,
        xaxis_title="Média de Gols em Casa",
        yaxis_title="Média de Gols Fora",
        xaxis=dict(range=[0, 3.5], fixedrange=False),
        yaxis=dict(range=[0, 3.5], fixedrange=False),
        height=500,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
    )

    # Add light gridlines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")

    return fig


sc1, sc2 = st.columns(2)
with sc1:
    st.plotly_chart(
        criar_scatter_plotly("18/19 (Com Torcida)"), use_container_width=True
    )
with sc2:
    st.plotly_chart(
        criar_scatter_plotly("20/21 (Sem Torcida)"), use_container_width=True
    )

st.divider()

# --- Section 2: Aggregated Metrics ---
st.subheader("2. Análise Global de Agressividade e Disciplina")


def criar_grafico_metrica_altair(metrica_nome):
    df_filtrado = df_agrupado.melt(
        id_vars=["Temporada", "Mando"],
        value_vars=["Gols", "Finalizações", "Faltas", "Cartões"],
        var_name="Métrica",
        value_name="Valor",
    )
    df_filtrado = df_filtrado[df_filtrado["Métrica"] == metrica_nome]

    barras = (
        alt.Chart(df_filtrado)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(
                "Temporada:N", title=None, axis=alt.Axis(labelAngle=0, labelFontSize=12)
            ),
            xOffset="Mando:N",
            y=alt.Y("Valor:Q", title=None),
            color=alt.Color(
                "Mando:N",
                legend=alt.Legend(title="Mando", orient="bottom"),
                scale=alt.Scale(domain=["Casa", "Fora"], range=["#00ff85", "#38003c"]),
            ),
            tooltip=[
                alt.Tooltip("Mando:N", title="Mando"),
                alt.Tooltip("Valor:Q", title="Média", format=".2f"),
            ],
        )
    )

    textos = (
        alt.Chart(df_filtrado)
        .mark_text(
            align="center", baseline="bottom", dy=-3, fontSize=14, fontWeight="bold"
        )
        .encode(
            x=alt.X("Temporada:N"),
            xOffset="Mando:N",
            y=alt.Y("Valor:Q"),
            text=alt.Text("Valor:Q", format=".2f"),
            color=alt.value("white"),
        )
    )

    return (barras + textos).properties(
        height=250, title=alt.TitleParams(f"Média de {metrica_nome}", fontSize=16)
    )


c1, c2, c3, c4 = st.columns(4)
with c1:
    st.altair_chart(criar_grafico_metrica_altair("Gols"), use_container_width=True)
with c2:
    st.altair_chart(
        criar_grafico_metrica_altair("Finalizações"), use_container_width=True
    )
with c3:
    st.altair_chart(criar_grafico_metrica_altair("Faltas"), use_container_width=True)
with c4:
    st.altair_chart(criar_grafico_metrica_altair("Cartões"), use_container_width=True)
