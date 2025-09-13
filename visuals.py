import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import os
import matplotlib.pyplot as plt 
import seaborn as sns 

# from streamlit_option_menu import option_menu
from streamlit_option_menu import option_menu

# Page Congi 
st.set_page_config(page_title="Crickalytics ODI : 🏏 ",layout="wide")
st.title("Crickalytic ODI : 🏏")

st.title("🏏Batting ")
# @st.cache_data
# def load_dataset():
#     # fixed_path = "merged_odi_dataset_new.csv" 
#     # st.title("🏏Batting data ")
#     fixed_path="odi_batting_new.csv"
#     if os.path.exists(fixed_path):
#         df = pd.read_csv(fixed_path, low_memory=False)
#         return df
#     else:
#         uploaded = st.file_uploader("odi_batting_new.csv", type=["csv"])
#         if uploaded:
#             df = pd.read_csv(uploaded, low_memory=False)
#             return df
#         else:
#             return pd.DataFrame()
@st.cache_data
def load_dataset():
    # Replace with your dataset path
    df1 = pd.read_csv("cleaned_odi_team_summary.csv")
    return df1
        
@st.cache_data
def load_dataset():
    # Replace with your dataset path
    df2 = pd.read_csv("cleaned_odi_player_summary.csv")
    return df2

@st.cache_data
def load_dataset():
    # Replace with your dataset path
    df3 = pd.read_csv("cleaned_odi_match_summary.csv")
    return df3

# @st.cache_data
# def load_dataset():
#     # Replace with your dataset path
#     df4 = pd.read_csv("odi_Matches_new.csv")
#     return df4
# @st.cache_data
# def load_dataset():

    # fixed_path = "merged_odi_dataset_new.csv" 
#     fixed_path1="odi_Bowling_new.csv"
#     if os.path.exists(fixed_path1):
#         df1 = pd.read_csv(fixed_path1, low_memory=False)
#         return df
#     else:
#         uploaded = st.file_uploader("Upload odi_Bowling_new.csv", type=["csv"])
#         if uploaded:
#             df1 = pd.read_csv(uploaded, low_memory=False)
#             return df1
#         else:
#             return pd.DataFrame()
#         # 
# # load_dataset()

# Sidebar Navigation 
# selected = option_menu("Main Menu", options=['Home','Upload Data','Player Analysis','Team Analysis','Visualizations'],menu_icon="trophy",icons=['house','cloud-upload','person','people','bar-chart'],default_index=0,orientation="horizontal")
# selected

selected = option_menu("Main Menu", options=['Home','Player Analysis','Team Analysis','Visualizations'],menu_icon="trophy",icons=['house','person','people','bar-chart'],default_index=0,orientation="horizontal")
selected 

# Home Page
# ---------------------------


if selected == "Home":
    st.title("🏏 Crickalytics ODI Dashboard")
    st.title("🏠 Home — ODI Cricket Analysis")
    st.markdown("""Welcome to **Crickalytic ODI**, an interactive dashboard designed to explore and analyze the world of **One Day International (ODI) Cricket**.  
This platform provides powerful insights into team and player performances, match outcomes, and overall trends in ODI history.  

### 🎯 Purpose
- Discover which teams dominate ODIs.
- Compare batting and bowling performances.
- Analyze country-wise contributions of players.
- Visualize patterns across matches and tournaments.

### 📂 Dataset
- Contains match-level, player-level, and team-level ODI data.
- Includes details such as runs, wickets, strike rates, match winners, and more.
                
### 📊 Dataset Information
- Source: Official ODI match records & cricket statistics databases.
- Includes: Match results, player stats, team scores, venues, and more.
- Format: CSV/Excel datasets that can be uploaded directly into the app.
""")
    
    #  Batting data here 
    st.title("🏏 Team data ")
    df1 = load_dataset()     
    if not df1.empty:
        st.success("✅ Dataset loaded successfully!")
        st.dataframe(df1.head(50))  
    else:
        st.warning("⚠️ No dataset found. Please upload cleaned_odi_team_summary.csv.")

#   Bowling data 
    st.title("🏏 Player data ")
    df2 = load_dataset()     
    if not df2.empty:
        st.success("✅ Dataset loaded successfully!")
        st.dataframe(df2.head(50))  
    else:
        st.warning("⚠️ No dataset found. Please upload cleaned_odi_player_summary.csv.")

#    Fow dataset
    st.title("🏏 Match data ")
    df3 = load_dataset()     
    if not df3.empty:
        st.success("✅ Dataset loaded successfully!")
        st.dataframe(df3.head(50))  
    else:
        st.warning("⚠️ No dataset found. Please upload cleaned_odi_match_summary.csv.")


    # df1 = load_dataset()     
    # if not df1.empty:
    #     st.success("✅ Dataset loaded successfully!")
    #     st.dataframe(df1.head(50))  
    # else:
    #     st.warning("⚠️ No dataset found. Please upload merged_odi_dataset_new.csv.")

    st.markdown("""
### 📌 Navigation Guide
- **🏠 Home:** Introduction & dataset preview  
- **🎯 Player Analysis:** Compare player performances (runs, wickets, averages)  
- **🛡️ Team Analysis:** Analyze team stats (wins, losses, top players)  
- **📊 Visualizations:** Explore overall ODI trends & interactive charts  
-**🏆 Match Results:** Compare match names with winners & see team dominance  

---
Enjoy exploring the exciting world of ODI cricket with **Crickalytics ODI**! 🏏✨
""")


# # ---------------------------
# # Team Analysis
# # ---------------------------
elif selected == "Team Analysis":
    st.title("🛡️ Team Analysis")

    # df = load_dataset()
    df1=pd.read_csv("cleaned_odi_team_summary.csv")
    # if not df.empty:
    #     st.success("✅ Dataset loaded successfully!")
    #     st.dataframe(df.head(50))  
    # else:
    #     st.warning("⚠️ No dataset found. Please upload merged_odi_dataset_new.csv.")

#     if not df.empty:
#         st.success("✅ Dataset loaded successfully for Team Analysis")

#         # Dropdown for team selection
#         teams = df["Team"].dropna().unique()
#         selected_team = st.selectbox("Select a Team", sorted(teams))
#  # Filter data for the selected team
#         df = load_dataset[load_dataset["Team"] == selected_team]
# # Dropdown for team selection
#         teams = df["Team"].dropna().unique()
#         selected_team = st.selectbox("Select a Team", sorted(teams))

#         # Filter data for the selected team
#         df = df[df["Team"] == selected_team]
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "🏏 Batting", "🎯 Bowling"])

    # ---------------- Overview Tab ----------------#
    with tab1:
            st.subheader("📈 Overview")
            winner_counts = df1['Match Winner'].value_counts().reset_index()
            winner_counts.columns = ['Team', 'Wins']
            st.bar_chart(winner_counts.set_index('Team'))
            matches_played = df1["Match ID"].nunique()
            wins = df1[df1["Match Winner"] == "won"].shape[0]
            losses = df1[df1["Match Winner"] == "lost"].shape[0]
            win_percentage = round((wins / matches_played) * 100, 2) if matches_played > 0 else 0

            # col1, col2, col3, col4 = st.columns(4)
            # col1.metric("Matches Played", matches_played)
            # col2.metric("Wins", wins)
            # col3.metric("Losses", losses)
            # col4.metric("Win %", f"{win_percentage}%")
    with tab2:
            st. subheader(" Batting")
            # n=10
            top_scorers=df1.groupby('batsman')['Runs'].sum().nlargest(10)
            top_scorers.plot(kind='barh',color='skyblue')
            plt.title(f"Top 10 Run Scorers")
            plt.xlabel('Runs')
            plt.ylabel('Batsman')
            plt.show()



            # win_percent1 = df['Match Winner'].value_counts()
            # win_percent1.plot.pie(autopct='%1.1f%%')
            # plt.title('Team Win Percentages')
            # plt.xticks(rotation=45)
            # plt.show()


# # ---------------------------
# # Player Analysis
# # ---------------------------
elif selected == "Player Analysis":
    st.title("🎯 Player Analysis")
    
    # role_choice = st.selectbox("Select Role", [c for c in ["batsman", "bowler"] if c in df.columns])
    # metric_choice = st.selectbox("Select Metric", [col for col in df.columns if df[col].dtype in [np.int64, np.float64]])
    # agg = df.groupby(role_choice)[metric_choice].sum().reset_index().sort_values(metric_choice, ascending=False)
    # st.dataframe(agg.head(10))
    # fig = px.bar(agg.head(10), x=role_choice, y=metric_choice, title=f"Top {role_choice.title()}s by {metric_choice}")
    # st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# # Visualizations
# # ---------------------------
elif selected == "Visualizations":
    st.title("📊 Visualizations") 
    #  Load dataset
    df = pd.read_csv("cleaned_odi_match_summary.csv")
    @st.cache_data
    def load_match_data():
        df = pd.read_csv("cleaned_odi_match_summary.csv")
        df["Match Date"] = pd.to_datetime(df["Match Date"], errors="coerce")
        df["year"] = df["Match Date"].dt.year
        return df

    matches = load_match_data()
    # SIDEBAR FILTERS
# ==========================
    st.sidebar.header("🔍 Filters")

    years = sorted(matches["year"].dropna().unique())
    teams = sorted(pd.concat([matches["Team1 Name"], matches["Team2 Name"], matches["Match Winner"]]).dropna().unique())
    venues = sorted(matches["Match Venue (Stadium)"].dropna().unique())

    selected_years = st.sidebar.multiselect("Select Years", years, default=years)
    selected_teams = st.sidebar.multiselect("Select Teams", teams, default=teams)
    selected_venues = st.sidebar.multiselect("Select Venues", venues, default=venues[:10])  # top 10 for usability
    # Apply filters
    filtered = matches[(matches["year"].isin(selected_years)) &((matches["Team1 Name"].isin(selected_teams)) | (matches["Team2 Name"].isin(selected_teams)) | (matches["Match Winner"].isin(selected_teams))) &(matches["Match Venue (Stadium)"].isin(selected_venues))]
    st.write(f"### Showing {len(filtered)} matches after filtering")

    # 1. Matches per year
# ==========================
    st.subheader("📅 Matches per Year")
    matches_per_year = filtered.groupby("year")["Match ID"].nunique()

    fig, ax = plt.subplots()
    matches_per_year.plot(kind="bar", ax=ax)
    ax.set_ylabel("Number of Matches")
    ax.set_xlabel("Year")
    st.pyplot(fig)

# ==========================
# 2. Most Winning Teams
# ==========================
    st.subheader("🏆 Most Successful Teams")
    top_winners = filtered["Match Winner"].value_counts().head(10)

    fig, ax = plt.subplots()
    sns.barplot(x=top_winners.values, y=top_winners.index, ax=ax)
    ax.set_xlabel("Wins")
    ax.set_ylabel("Team")
    st.pyplot(fig)

# ==========================
# 3. Toss Decision Impact
# ==========================
    st.subheader("🎲 Toss Decision vs Match Result")
    fig, ax = plt.subplots()
    sns.countplot(data=filtered, x="Toss Winner Choice", hue="Match Result Text", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ==========================
# 4. Match Venues
# ==========================
    st.subheader("🌍 Top Match Venues")
    venue_counts = filtered["Match Venue (Stadium)"].value_counts().head(15)

    fig, ax = plt.subplots()
    sns.barplot(x=venue_counts.values, y=venue_counts.index, ax=ax)
    ax.set_xlabel("Matches Hosted")
    ax.set_ylabel("Stadium")
    st.pyplot(fig)
# st.title("🏏 ODI Matches Analysis Dashboard")


# # Convert 'Match Date' to datetime
#     df['Match Date'] = pd.to_datetime(df['Match Date'], errors='coerce')
#     df['Year'] = df['Match Date'].dt.year

#     st.title("ODI Team Analysis")

# Sidebar filters
#     teams = sorted(df['team'].unique())
#     selected_team = st.sidebar.selectbox("Select Team", ["All"] + teams)

#     years = sorted(df['Year'].dropna().unique())
#     selected_year = st.sidebar.selectbox("Select Year", ["All"] + list(years))

# # Apply filters
#     filtered_df = df.copy()
#     if selected_team != "All":
#         filtered_df = filtered_df[filtered_df['team'] == selected_team]
#     if selected_year != "All":
#         filtered_df = filtered_df[filtered_df['Year'] == selected_year]

# # Summary statistics
#     st.subheader("Team Summary Stats")
#     total_matches = filtered_df['Match ID'].nunique()
#     total_runs = filtered_df['Team_Total_Runs'].sum()
#     total_wickets = filtered_df['Team_Total_Wickets'].sum()
#     match_wins = filtered_df[filtered_df['Match Winner'] == selected_team]['Match ID'].nunique() if selected_team != "All" else "N/A"

#     st.markdown(f"**Total Matches Played:** {total_matches}")
#     st.markdown(f"**Total Runs Scored:** {total_runs}")
#     st.markdown(f"**Total Wickets Taken:** {total_wickets}")
#     if selected_team != "All":
#         st.markdown(f"**Total Matches Won:** {match_wins}")

# # Top scores per match
#     st.subheader("Top Team Scores")
#     top_scores = filtered_df[['Match Date','team','Team_Total_Runs']].sort_values(by='Team_Total_Runs', ascending=False).head(10)
#     st.dataframe(top_scores)

# # Visualization: Total Runs by Team
#     st.subheader("Total Runs by Team")
#     runs_by_team = df.groupby('team')['Team_Total_Runs'].sum().sort_values(ascending=False)
#     plt.figure(figsize=(12,6))
#     sns.barplot(x=runs_by_team.index, y=runs_by_team.values, palette="viridis")
#     plt.xticks(rotation=45)
#     plt.ylabel("Total Runs")
#     plt.title("Total Runs by Team in ODI History")
#     st.pyplot(plt)

# # Visualization: Matches Won by Team
#     st.subheader("Matches Won by Team")
#     wins_by_team = df.groupby('Match Winner')['Match ID'].nunique().sort_values(ascending=False)
#     plt.figure(figsize=(12,6))
#     sns.barplot(x=wins_by_team.index, y=wins_by_team.values, palette="magma")
#     plt.xticks(rotation=45)
#     plt.ylabel("Matches Won")
#     plt.title("Total Matches Won by Each Team")
#     st.pyplot(plt)
# pd.read_csv("C:\\Users\\manmo\\OneDrive\\Desktop\\final project of Crick analytic\\merged_odi_dataset_new.csv")
#     winner_counts   
#     = df1['Match Winner'].value_counts().reset_index()
#     winner_counts.columns = ['Team', 'Wins']

#     st.subheader("🏆 Total Wins by Team")
#     st.bar_chart(winner_counts.set_index('Team'))
# df1=


# import pandas as pd

# # === Load datasets ===
# batting = pd.read_csv("odi_batting_new.csv")
# bowling = pd.read_csv("odi_Bowling_new.csv")
# fow = pd.read_csv("odi_Fow_new.csv")
# matches = pd.read_csv("odi_Matches_new.csv")
# partnership = pd.read_csv("odi_Patnership_new.csv")
# players = pd.read_csv("odi_players_info_new.csv")

# # === Clean datasets ===
# # Drop unnecessary index column
# batting = batting.drop(columns=["Unnamed: 0"], errors="ignore")

# # === Merge Player Info (add player names) ===
# # For Batting (batsman column)
# batting = batting.merge(players[["player_id", "player_name"]],
#                         left_on="batsman", right_on="player_id", how="left") \
#                  .drop(columns=["player_id"]) \
#                  .rename(columns={"player_name": "batsman_name"})

# # For Bowling (bowler id column)
# bowling = bowling.merge(players[["player_id", "player_name"]],
#                         left_on="bowler id", right_on="player_id", how="left") \
#                  .drop(columns=["player_id"]) \
#                  .rename(columns={"player_name": "bowler_name"})

