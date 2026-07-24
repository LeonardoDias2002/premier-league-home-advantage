# ⚽ The Home Advantage in the Premier League: Crowd Impact on Performance

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/Altair-125078?style=for-the-badge&logo=altair&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white"/>
</p>

## 📌 Project Overview

This **Data Analysis and Data Storytelling** project quantitatively investigates the "Home Advantage" phenomenon in elite football.

Through a comparative analysis of the English Premier League, the study contrasts a regular season with full stadiums (2018/2019) against an atypical season played behind closed doors due to the COVID-19 pandemic (2020/2021). The goal is to isolate and measure the direct impact of crowd presence on teams' offensive behavior and referee disciplinary strictness.

### 🚀 Interactive Dashboard (Streamlit)
The data exploration results were encapsulated into an interactive dashboard, allowing for direct comparison of clubs' tactical and disciplinary profiles.

> **[Access the Premier League Dashboard here](#)** *(Substitua a # pelo link após o deploy)*

---

## 📊 Key Insights and Conclusions

Through data modeling and interactive visualizations using `Altair` and `Plotly`, the project revealed non-obvious conclusions about sports dynamics:

1. **The Decline of Offensive Drive:** In the absence of a crowd (20/21), the home team's offensive volume dropped drastically, evidenced by a significant reduction in average shots.
2. **Disciplinary Behavior Inversion:** With fans present (18/19), the home team committed fewer fouls and received fewer cards than the visitors. Behind closed doors, this advantage vanished. The home team began committing more fouls (jumping from 10.15 to 11.22 per game), suggesting that the crowd inhibits the home team's infractions and exerts psychological pressure on the referee.
3. **Statistical Convergence:** Scatter plots revealed that clubs with strong offensive disparity (scoring much more at home than away) had their goal averages converge to the equilibrium line during the pandemic season, mathematically neutralizing the home-field advantage.

---

## 🗄️ Data Source and Reproducibility

The data used in this study covers 760 official matches and comes from the **Datahub (English Premier League)** open database. The consolidated `.csv` files are available in the `data/` folder of this repository to facilitate code reproduction.

---

## 🛠️ How to Run Locally

1. **Clone the repository:**
```bash
git clone [https://github.com/LeonardoDias2002/premier-league-home-advantage.git](https://github.com/LeonardoDias2002/premier-league-home-advantage.git)
cd premier-league-home-advantage
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Explore Notebooks or run the App:**
```bash
# To view the analysis code
jupyter notebook notebooks/plot.ipynb

# To run the interactive dashboard
streamlit run app/app.py
```