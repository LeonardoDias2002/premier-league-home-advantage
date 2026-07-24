import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. Page Configuration & Aesthetics
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Premier League: Home Advantage",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

        df_1819["Season"] = "18/19 (With Crowd)"
        df_2021["Season"] = "20/21 (Closed Doors)"

        return pd.concat([df_1819, df_2021], ignore_index=True)
    except FileNotFoundError:
        st.error(
            "Error: CSV files not found. Ensure 'season-1819.csv' and 'season-2021.csv' are in the data/ directory."
        )
        st.stop()


df = load_data()

# Process data for aggregated metrics and radar chart
records = []
for idx, row in df.iterrows():
    temp = row["Season"]
    records.extend(
        [
            {
                "Season": temp,
                "Team": row["HomeTeam"],
                "Venue": "Home",
                "Goals": row["FTHG"],
                "Shots": row["HS"],
                "Fouls": row["HF"],
                "Yellow Cards": row["HY"],
            },
            {
                "Season": temp,
                "Team": row["AwayTeam"],
                "Venue": "Away",
                "Goals": row["FTAG"],
                "Shots": row["AS"],
                "Fouls": row["AF"],
                "Yellow Cards": row["AY"],
            },
        ]
    )

df_granular = pd.DataFrame(records)
df_agrupado = (
    df_granular.groupby(["Season", "Venue"])[
        ["Goals", "Shots", "Fouls", "Yellow Cards"]
    ]
    .mean()
    .reset_index()
)

# Process data for Scatter Plot
home_avg = df.groupby(["Season", "HomeTeam"])["FTHG"].mean().reset_index()
home_avg.columns = ["Season", "Team", "Avg_Home_Goals"]

away_avg = df.groupby(["Season", "AwayTeam"])["FTAG"].mean().reset_index()
away_avg.columns = ["Season", "Team", "Avg_Away_Goals"]

df_times = pd.merge(home_avg, away_avg, on=["Season", "Team"])
df_times["Logo_URL"] = df_times["Team"].map(TEAM_LOGOS)

# -----------------------------------------------------------------------------
# 3. Sidebar UI: Team Hub
# -----------------------------------------------------------------------------
st.sidebar.title("⚽ Team Hub")
st.sidebar.markdown("Compare the tactical and disciplinary profiles of the teams.")

all_teams = sorted(df_times["Team"].unique())

col_t1, col_t2 = st.sidebar.columns(2)
with col_t1:
    team_1 = st.selectbox("Main Team:", all_teams, index=all_teams.index("Arsenal"))
    if team_1 in TEAM_LOGOS:
        st.image(TEAM_LOGOS[team_1], width=80)

with col_t2:
    team_2 = st.selectbox(
        "Compare with:", ["None"] + all_teams, index=all_teams.index("Everton") + 1
    )
    if team_2 != "None" and team_2 in TEAM_LOGOS:
        st.image(TEAM_LOGOS[team_2], width=80)

temporada_radar = st.sidebar.radio(
    "Select Season for Analysis:",
    ["18/19 (With Crowd)", "20/21 (Closed Doors)"],
)


# Radar Chart Builder
def plot_radar(t1, t2, season):
    categories = ["Goals", "Shots", "Fouls", "Yellow Cards"]
    fig = go.Figure()

    def add_team_trace(team_name, color):
        stats = df_granular[
            (df_granular["Team"] == team_name) & (df_granular["Season"] == season)
        ][categories].mean()
        max_vals = df_granular[df_granular["Season"] == season][categories].max()
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

    add_team_trace(t1, "#00ff85")
    if t2 != "None":
        add_team_trace(t2, "#38003c")

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
    )
    return fig


st.sidebar.markdown(f"**Relative Performance Analysis**")
st.sidebar.plotly_chart(
    plot_radar(team_1, team_2, temporada_radar), use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Portfolio Project**\n\nDeveloped by Leonardo Dias")

# -----------------------------------------------------------------------------
# 4. Main Dashboard Area
# -----------------------------------------------------------------------------
st.title("Home Advantage in the Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿")
st.markdown(
    "Investigating the impact of crowd presence by comparing the **18/19 (Full Stadiums)** and **20/21 (Closed Doors)** seasons."
)
st.divider()

# --- Section 1: Scatter Plots ---
st.subheader("1. Offensive Convergence: Granular Performance")
st.markdown(
    "The dashed line represents the equilibrium ($y = x$). Teams below the line score more at home; teams above score more away."
)


def criar_scatter_plotly(temporada):
    df_temp = df_times[df_times["Season"] == temporada]
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=[0, 3.5],
            y=[0, 3.5],
            mode="lines",
            line=dict(color="gray", dash="dash"),
            name="Equilibrium Line (Home = Away)",
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_temp["Avg_Home_Goals"],
            y=df_temp["Avg_Away_Goals"],
            mode="markers",
            marker=dict(size=1, color="rgba(0,0,0,0)"),
            text=df_temp["Team"],
            hovertemplate="<b>%{text}</b><br>Home: %{x:.2f}<br>Away: %{y:.2f}<extra></extra>",
        )
    )

    for idx, row in df_temp.iterrows():
        opacity, size = 1.0, 0.35
        if team_1 != "None" or team_2 != "None":
            if row["Team"] not in [team_1, team_2]:
                opacity, size = 0.2, 0.25
            else:
                size = 0.5

        fig.add_layout_image(
            dict(
                source=row["Logo_URL"],
                xref="x",
                yref="y",
                x=row["Avg_Home_Goals"],
                y=row["Avg_Away_Goals"],
                sizex=size,
                sizey=size,
                xanchor="center",
                yanchor="middle",
                opacity=opacity,
            )
        )

    fig.update_layout(
        title=temporada,
        xaxis_title="Average Home Goals",
        yaxis_title="Average Away Goals",
        xaxis=dict(range=[0, 3.5], fixedrange=False),
        yaxis=dict(range=[0, 3.5], fixedrange=False),
        height=500,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")

    return fig


sc1, sc2 = st.columns(2)
with sc1:
    st.plotly_chart(
        criar_scatter_plotly("18/19 (With Crowd)"), use_container_width=True
    )
with sc2:
    st.plotly_chart(
        criar_scatter_plotly("20/21 (Closed Doors)"), use_container_width=True
    )

st.divider()

# --- Section 2: Aggregated Metrics ---
st.subheader("2. Global Analysis of Aggressiveness and Discipline")


def criar_grafico_metrica_altair(metrica_nome):
    df_filtrado = df_agrupado.melt(
        id_vars=["Season", "Venue"],
        value_vars=["Goals", "Shots", "Fouls", "Yellow Cards"],
        var_name="Metric",
        value_name="Value",
    )
    df_filtrado = df_filtrado[df_filtrado["Metric"] == metrica_nome]

    barras = (
        alt.Chart(df_filtrado)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(
                "Season:N", title=None, axis=alt.Axis(labelAngle=0, labelFontSize=12)
            ),
            xOffset="Venue:N",
            y=alt.Y("Value:Q", title=None),
            color=alt.Color(
                "Venue:N",
                legend=alt.Legend(title="Venue", orient="bottom"),
                scale=alt.Scale(domain=["Home", "Away"], range=["#00ff85", "#38003c"]),
            ),
            tooltip=[
                alt.Tooltip("Venue:N", title="Venue"),
                alt.Tooltip("Value:Q", title="Average", format=".2f"),
            ],
        )
    )

    textos = (
        alt.Chart(df_filtrado)
        .mark_text(
            align="center", baseline="bottom", dy=-3, fontSize=14, fontWeight="bold"
        )
        .encode(
            x=alt.X("Season:N"),
            xOffset="Venue:N",
            y=alt.Y("Value:Q"),
            text=alt.Text("Value:Q", format=".2f"),
            color=alt.value("white"),
        )
    )

    return (barras + textos).properties(
        height=250, title=alt.TitleParams(f"Average {metrica_nome}", fontSize=16)
    )


c1, c2, c3, c4 = st.columns(4)
with c1:
    st.altair_chart(criar_grafico_metrica_altair("Goals"), use_container_width=True)
with c2:
    st.altair_chart(criar_grafico_metrica_altair("Shots"), use_container_width=True)
with c3:
    st.altair_chart(criar_grafico_metrica_altair("Fouls"), use_container_width=True)
with c4:
    st.altair_chart(
        criar_grafico_metrica_altair("Yellow Cards"), use_container_width=True
    )
