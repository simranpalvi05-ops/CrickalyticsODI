import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_echarts import st_echarts

# --- Page Configuration ---
st.set_page_config(
    page_title="ODI Analysis Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86C1;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .tab-header {
        font-size: 1.8rem;
        color: #17A589;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 8px;
        padding: 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E86C1;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading and Caching ---
@st.cache_data
def load_data():
    try:
        bowling_df = pd.read_csv('bowling_clean.csv')
        fow_df = pd.read_csv('fow_clean.csv')
        partnership_df = pd.read_csv('partnership_clean.csv')
        player_info_df = pd.read_csv('player_info_clean.csv')
        
        team_mask = pd.to_numeric(bowling_df['team'], errors='coerce').isna()
        opposition_mask = pd.to_numeric(bowling_df['opposition'], errors='coerce').isna()
        bowling_df = bowling_df[team_mask & opposition_mask]

        bowling_df = bowling_df.merge(player_info_df[['player_id', 'player_name']], left_on='bowler id', right_on='player_id', how='left')
        partnership_df = partnership_df.merge(player_info_df[['player_id', 'player_name']], left_on='player1', right_on='player_id', how='left')
        partnership_df.rename(columns={'player_name': 'player1_name'}, inplace=True)
        partnership_df = partnership_df.merge(player_info_df[['player_id', 'player_name']], left_on='player2', right_on='player_id', how='left')
        partnership_df.rename(columns={'player_name': 'player2_name'}, inplace=True)
        fow_df_named = fow_df.merge(player_info_df[['player_id', 'player_name']], left_on='player', right_on='player_id', how='left')
        
        return bowling_df, fow_df_named, partnership_df
        
    except FileNotFoundError:
        st.error("Data files not found. Please ensure your CSV files are in the same directory.")
        return None, None, None

# --- Main App ---
def main():
    st.markdown('<h1 class="main-header">🏏 ODI Cricket Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    bowling_df, fow_df_named, partnership_df = load_data()

    if bowling_df is None:
        return

    st.sidebar.title("📊 Dashboard Controls")
    st.sidebar.markdown("---")
    
    st.sidebar.header("Dataset Overview")
    total_matches = bowling_df['Match ID'].nunique()
    total_players = pd.concat([partnership_df['player1_name'], partnership_df['player2_name']]).nunique()
    total_wickets = bowling_df['wickets'].sum()
    
    st.sidebar.metric("Total Matches Analyzed", f"{total_matches}")
    st.sidebar.metric("Total Players Found", f"{total_players}")
    st.sidebar.metric("Total Wickets Taken", f"{int(total_wickets)}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Player Analysis", "🌍 Team Analysis", "📊 Match Analysis", "🤝 Partnership Analysis"])

    with tab1:
        player_analysis_tab(bowling_df, fow_df_named, partnership_df)
    with tab2:
        team_analysis_tab(bowling_df, fow_df_named, partnership_df)
    with tab3:
        match_analysis_tab(bowling_df, fow_df_named, partnership_df)
    with tab4:
        partnership_analysis_tab(partnership_df)

def create_death_overs_analysis(bowling_df):
    """Analyze death overs (40-50) performance"""
    death_overs = bowling_df[bowling_df['overs'].between(40, 50)].copy()
    powerplay = bowling_df[bowling_df['overs'].between(1, 10)].copy()
    middle_overs = bowling_df[bowling_df['overs'].between(11, 40)].copy()
    
    # Team performance by phase
    phase_data = []
    for phase_name, phase_df in [('Powerplay (1-10)', powerplay), 
                                ('Middle (11-40)', middle_overs), 
                                ('Death (40-50)', death_overs)]:
        phase_stats = phase_df.groupby('team').agg({
            'wickets': 'sum',
            'economy': 'mean',
            'conceded': 'sum'
        }).reset_index()
        phase_stats['phase'] = phase_name
        phase_data.append(phase_stats)
    
    phase_comparison = pd.concat(phase_data, ignore_index=True)
    
    # Create the visualization
    fig = px.bar(
        phase_comparison,
        x='team',
        y='economy',
        color='phase',
        barmode='group',
        title='Team Economy Rate by Match Phase',
        hover_data=['wickets', 'conceded'],
        labels={'economy': 'Economy Rate', 'team': 'Team'}
    )
    fig.update_layout(
        xaxis_tickangle=45,
        height=500,
        showlegend=True
    )
    return fig


def player_analysis_tab(bowling_df, fow_df_named, partnership_df):
    st.markdown('<h2 class="tab-header">👤 Player Performance Deep Dive</h2>', unsafe_allow_html=True)
    
    st.subheader("Bowling Performance")
    total_wickets_per_bowler = bowling_df.groupby('player_name')['wickets'].sum()
    wicket_takers_list = total_wickets_per_bowler[total_wickets_per_bowler > 0].index.tolist()
    bowler_list = sorted(wicket_takers_list)
    selected_bowler = st.selectbox("Select a Bowler", bowler_list)
    player_bowling_stats = bowling_df[bowling_df['player_name'] == selected_bowler]
    
    # Chart 1: Wickets vs Opposition
    player_vs_opposition = player_bowling_stats.groupby('opposition')['wickets'].sum().reset_index()
    fig_vs_opposition = px.bar(player_vs_opposition, x='opposition', y='wickets', title=f"{selected_bowler}'s Wickets vs Opposition", color_discrete_sequence=px.colors.sequential.Aggrnyl)
    st.plotly_chart(fig_vs_opposition, use_container_width=True)

    # Chart 2: Bowler Economy Rate Distribution (NEW)
    fig_economy_box = px.box(player_bowling_stats, y='economy', title=f"Economy Rate Consistency for {selected_bowler}", points="all")
    fig_economy_box.update_traces(marker=dict(color='#17A589'))
    st.plotly_chart(fig_economy_box, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Batting & Dismissal")
    partner_players_1 = partnership_df['player1_name'].dropna().unique()
    partner_players_2 = partnership_df['player2_name'].dropna().unique()
    dismissed_players = fow_df_named['player_name'].dropna().unique()
    all_batting_players = set(partner_players_1) | set(partner_players_2) | set(dismissed_players)
    batsman_list = sorted(list(all_batting_players))
    selected_batsman = st.selectbox("Select a Batsman", batsman_list)
    
    # --- DISMISSAL ANALYSIS CHART WITH DETAILED HOVER LABELS ---
    st.markdown("#### Dismissal Analysis")
    player_dismissals = fow_df_named[fow_df_named['player_name'] == selected_batsman]
    dismissal_counts = player_dismissals['wicket'].value_counts().reset_index()
    dismissal_counts.columns = ['wicket', 'count']

    # Function to create descriptive labels
    def get_wicket_label(w_num):
        w_num = int(w_num)
        if w_num == 1: return "1st Wicket"
        if w_num == 2: return "2nd Wicket"
        if w_num == 3: return "3rd Wicket"
        return f"{w_num}th Wicket"

    dismissal_counts['wicket_label'] = dismissal_counts['wicket'].apply(get_wicket_label)

    # Prepare data for ECharts
    dismissal_data = []
    total_dismissals = dismissal_counts['count'].sum()

    for _, row in dismissal_counts.iterrows():
        percentage = (row['count'] / total_dismissals) * 100
        dismissal_data.append({
            'value': int(row['count']),
            'name': row['wicket_label'],
            'percentage': round(percentage, 1)
        })

    # Create ECharts donut chart
    donut_chart = {
        "title": {
            "text": f"Dismissal Position for {selected_batsman}",
            "left": "center",
            "textStyle": {
                "fontSize": 16,
                "fontWeight": "bold"
            }
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "<b>Wicket Position:</b> {b}<br><b>Times Dismissed:</b> {c}<br><b>Percentage:</b> {d}%"
        },
        "legend": {
            "orient": "vertical",
            "left": "left",
            "top": "middle"
        },
        "series": [
            {
                "name": "Dismissal Position",
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "formatter": "{b}: {c} ({d}%)"
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": "16",
                        "fontWeight": "bold"
                    }
                },
                "labelLine": {
                    "show": True
                },
                "data": dismissal_data
            }
        ],
        "color": [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
        ]
    }

    # Display the donut chart
    st_echarts(
        options=donut_chart,
        height="500px",
        key="dismissal_donut_chart"
    )
        
    # Chart 4: Top Partners
    st.subheader(f"Top 10 Partners for {selected_batsman}")
    player_partnerships = partnership_df[(partnership_df['player1_name'] == selected_batsman) | (partnership_df['player2_name'] == selected_batsman)].copy()
    player_partnerships['partner_name'] = player_partnerships.apply(lambda row: row['player2_name'] if row['player1_name'] == selected_batsman else row['player1_name'], axis=1)
    top_partners = player_partnerships.groupby('partner_name')['partnership runs'].sum().sort_values(ascending=False).reset_index()
    fig_partners = px.bar(top_partners.head(10), x='partner_name', y='partnership runs', title=f"Total Partnership Runs with {selected_batsman}", color_discrete_sequence=px.colors.sequential.ice)
    st.plotly_chart(fig_partners, use_container_width=True)

def team_analysis_tab(bowling_df, fow_df, partnership_df):
    st.markdown('<h2 class="tab-header">🌍 Comparative Team Analysis</h2>', unsafe_allow_html=True)
    
    # --- ENHANCED MAP CHART ---
    st.subheader("Global Wicket Takers Distribution")

    # Aggregate wickets for ALL teams for the map
    total_wickets_map = bowling_df.groupby('team')['wickets'].sum().reset_index()

    fig_map = px.choropleth(
        total_wickets_map,
        locations='team',
        locationmode='country names',
        color='wickets',
        hover_name='team',
        color_continuous_scale=px.colors.sequential.Plasma,
        title='Total Wickets Taken by Country'
    )

    # Increase the size and enhance the appearance
    fig_map.update_layout(
        height=600,  # Increased height
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        title_font_size=20,
        title_x=0.5  # Center the title
    )

    # Improve the color scale with better formatting
    fig_map.update_coloraxes(
        colorbar=dict(
            title="Wickets",
            thickness=15,
            len=0.75,
            x=0.02,
            y=0.5
        )
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")

    # --- Comparison Section ---
    team_list = sorted(bowling_df['team'].unique())
    st.subheader("Team Performance Comparison")
    default_teams = team_list[:3] if len(team_list) >= 3 else team_list
    selected_teams = st.multiselect("Select Teams to Compare", team_list, default=default_teams)

    if selected_teams:
        comparison_bowling_df = bowling_df[bowling_df['team'].isin(selected_teams)]
        comparison_partnership_df = partnership_df[partnership_df['team'].isin(selected_teams)]
        
        # Chart 1: Total Wickets Taken
        total_wickets = comparison_bowling_df.groupby('team')['wickets'].sum().reset_index()
        
        # Generate colors for teams
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        team_colors = {}
        for i, team in enumerate(total_wickets['team']):
            team_colors[team] = colors[i % len(colors)]
        
        wickets_chart = {
            "title": {
                "text": "Total Wickets Taken (Selected Teams)",
                "left": "center",
                "textStyle": {
                    "fontSize": 16,
                    "fontWeight": "bold"
                }
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "shadow"
                }
            },
            "xAxis": {
                "type": "category",
                "data": total_wickets['team'].tolist(),
                "axisLabel": {
                    "rotate": 45
                }
            },
            "yAxis": {
                "type": "value",
                "name": "Wickets"
            },
            "series": [
                {
                    "name": "Wickets",
                    "type": "bar",
                    "data": [{"value": row['wickets'], "itemStyle": {"color": team_colors[row['team']]}} 
                            for _, row in total_wickets.iterrows()],
                    "label": {
                        "show": True,
                        "position": "top",
                        "formatter": "{c}"
                    }
                }
            ],
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            }
        }
        
        # UNIQUE KEY: Include team names and chart type
        wickets_key = f"wickets_{'_'.join(selected_teams)}"
        st_echarts(wickets_chart, height="400px", key=wickets_key)
        
        # Chart 2: Average Partnership Runs
        avg_partnership = comparison_partnership_df.groupby('team')['partnership runs'].mean().reset_index()
        avg_partnership['partnership runs'] = avg_partnership['partnership runs'].round(2)
        
        partnership_chart = {
            "title": {
                "text": "Average Partnership Runs by Team",
                "left": "center",
                "textStyle": {
                    "fontSize": 16,
                    "fontWeight": "bold"
                }
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "shadow"
                }
            },
            "xAxis": {
                "type": "category",
                "data": avg_partnership['team'].tolist(),
                "axisLabel": {
                    "rotate": 45
                }
            },
            "yAxis": {
                "type": "value",
                "name": "Average Runs"
            },
            "series": [
                {
                    "name": "Average Partnership Runs",
                    "type": "bar",
                    "data": [{"value": row['partnership runs'], "itemStyle": {"color": team_colors.get(row['team'], '#1f77b4')}} 
                            for _, row in avg_partnership.iterrows()],
                    "label": {
                        "show": True,
                        "position": "top",
                        "formatter": "{c}"
                    }
                }
            ],
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            }
        }
        
        # UNIQUE KEY: Different from wickets key
        partnership_key = f"partnership_{'_'.join(selected_teams)}"
        st_echarts(partnership_chart, height="400px", key=partnership_key)

    st.markdown("---")

    # Phase-wise Performance
    st.subheader("⏱️ Match Phase Performance")
    fig_death_overs = create_death_overs_analysis(bowling_df)
    st.plotly_chart(fig_death_overs, use_container_width=True)
    
    # You can also add additional phase analysis charts:
    
    # Wickets by phase comparison
    st.subheader("🎯 Wickets by Match Phase")
    
    # Calculate wickets by phase for each team
    phases = {
        'Powerplay (1-10)': (1, 10),
        'Middle Overs (11-40)': (11, 40),
        'Death Overs (41-50)': (41, 50)
    }
    
    phase_wickets_data = []
    for phase_name, (start, end) in phases.items():
        phase_df = bowling_df[bowling_df['overs'].between(start, end)]
        wickets_by_team = phase_df.groupby('team')['wickets'].sum().reset_index()
        wickets_by_team['phase'] = phase_name
        phase_wickets_data.append(wickets_by_team)
    
    if phase_wickets_data:
        phase_wickets_df = pd.concat(phase_wickets_data, ignore_index=True)
        
        fig_wickets_phase = px.bar(
            phase_wickets_df,
            x='team',
            y='wickets',
            color='phase',
            barmode='group',
            title='Wickets Taken by Team in Different Match Phases',
            labels={'wickets': 'Total Wickets', 'team': 'Team'}
        )
        fig_wickets_phase.update_layout(xaxis_tickangle=45, height=500)
        st.plotly_chart(fig_wickets_phase, use_container_width=True)
    
    # Team-specific phase performance selector
    st.subheader("🔍 Detailed Team Phase Analysis")
    
    team_list = sorted(bowling_df['team'].unique())
    selected_team = st.selectbox("Select Team for Detailed Phase Analysis", team_list)
    
    if selected_team:
        team_bowling = bowling_df[bowling_df['team'] == selected_team].copy()
        
        # Define phases
        team_bowling['phase'] = pd.cut(
            team_bowling['overs'],
            bins=[0, 10, 40, 50],
            labels=['Powerplay (1-10)', 'Middle Overs (11-40)', 'Death Overs (41-50)']
        )
        
        team_phase_stats = team_bowling.groupby('phase').agg({
            'wickets': 'sum',
            'economy': 'mean',
            'conceded': 'sum',
            'overs': 'count'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Wickets by phase for selected team
            fig_team_wickets = px.pie(
                team_phase_stats,
                values='wickets',
                names='phase',
                title=f'{selected_team} - Wickets Distribution by Phase',
                hole=0.4
            )
            st.plotly_chart(fig_team_wickets, use_container_width=True)
        
        with col2:
            # Economy by phase for selected team
            fig_team_economy = px.bar(
                team_phase_stats,
                x='phase',
                y='economy',
                title=f'{selected_team} - Economy Rate by Phase',
                color='economy',
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_team_economy, use_container_width=True)
    

    # --- Head-to-Head Section ---
    st.subheader("Head-to-Head Analysis")
    team1 = st.selectbox("Select Team 1", team_list, index=0, key='team1_h2h')
    opponents1 = bowling_df[bowling_df['team'] == team1]['opposition'].unique()
    opponents2 = bowling_df[bowling_df['opposition'] == team1]['team'].unique()
    h2h_team_list = sorted(list(set(opponents1) | set(opponents2)))

    if h2h_team_list:
        team2 = st.selectbox("Select Team 2", h2h_team_list, index=0, key='team2_h2h')
        if team1 and team2:
            h2h_bowling = bowling_df[((bowling_df['team'] == team1) & (bowling_df['opposition'] == team2)) | ((bowling_df['team'] == team2) & (bowling_df['opposition'] == team1))]
            h2h_wickets = h2h_bowling.groupby('team')['wickets'].sum().reset_index()
            
            # Prepare data for head-to-head chart
            team1_wickets = h2h_wickets[h2h_wickets['team'] == team1]['wickets'].iloc[0] if not h2h_wickets[h2h_wickets['team'] == team1].empty else 0
            team2_wickets = h2h_wickets[h2h_wickets['team'] == team2]['wickets'].iloc[0] if not h2h_wickets[h2h_wickets['team'] == team2].empty else 0
            
            h2h_chart = {
                "title": {
                    "text": f"Head-to-Head: {team1} vs {team2}",
                    "left": "center",
                    "textStyle": {
                        "fontSize": 16,
                        "fontWeight": "bold"
                    }
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {
                        "type": "shadow"
                    }
                },
                "legend": {
                    "data": [team1, team2],
                    "top": "bottom"
                },
                "xAxis": {
                    "type": "category",
                    "data": ["Wickets"]
                },
                "yAxis": {
                    "type": "value",
                    "name": "Wickets"
                },
                "series": [
                    {
                        "name": team1,
                        "type": "bar",
                        "data": [team1_wickets],
                        "itemStyle": {
                            "color": "#1f77b4"
                        },
                        "label": {
                            "show": True,
                            "position": "top",
                            "formatter": "{c}"
                        }
                    },
                    {
                        "name": team2,
                        "type": "bar",
                        "data": [team2_wickets],
                        "itemStyle": {
                            "color": "#ff7f0e"
                        },
                        "label": {
                            "show": True,
                            "position": "top",
                            "formatter": "{c}"
                        }
                    }
                ],
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "15%",
                    "containLabel": True
                }
            }
            
            # UNIQUE KEY: Include both team names
            h2h_key = f"h2h_{team1}_{team2}"
            st_echarts(h2h_chart, height="400px", key=h2h_key)
    else:
        st.warning(f"No head-to-head match data found for {team1} in this dataset.")

def match_analysis_tab(bowling_df, fow_df_named, partnership_df):
    st.markdown('<h2 class="tab-header">📊 Detailed Match Breakdown</h2>', unsafe_allow_html=True)
    
    valid_bowling_matches = set(bowling_df[bowling_df['overs'] <= 50]['Match ID'].unique())
    valid_fow_matches = set(fow_df_named[fow_df_named['over'] <= 50]['Match ID'].unique())
    match_ids = sorted(list(valid_bowling_matches.intersection(valid_fow_matches)))
    selected_match_id = st.selectbox("Select a Match to Analyze", match_ids)
    
    if not selected_match_id:
        return
    
    match_bowling = bowling_df[bowling_df['Match ID'] == selected_match_id]
    match_fow = fow_df_named[fow_df_named['Match ID'] == selected_match_id]
    match_partnership = partnership_df[partnership_df['Match ID'] == selected_match_id]
    
    # --- Chart 1: Innings Progression with Wickets ---
    st.markdown("#### Innings Progression")
    
    # --- Prepare Innings Data for Area Chart ---
    match_bowling_match = match_bowling.copy()

    # Sum conceded runs per team per over
    match_bowling_match['over_number'] = match_bowling_match['overs'].astype(int) + 1
    innings_data = (
        match_bowling_match.groupby(['opposition', 'over_number'])['conceded']
        .sum()
        .reset_index()
        .rename(columns={'opposition': 'batting_team', 'conceded': 'runs'})
    )

    # Ensure overs 1–50 exist for each team
    teams_in_match = innings_data['batting_team'].unique()
    full_overs_df = pd.DataFrame({'over_number': range(1, 51)})

    all_teams_data = []
    for team in teams_in_match:
        team_data = innings_data[innings_data['batting_team'] == team]
        team_data = full_overs_df.merge(team_data, on='over_number', how='left').fillna(0)
        team_data['batting_team'] = team
        team_data['runs'] = team_data['runs'].astype(int)  # convert to integer
        team_data['cumulative_score'] = team_data['runs'].cumsum()
        all_teams_data.append(team_data)

    final_innings_data = pd.concat(all_teams_data)

    # --- Plot Area Chart ---
    fig_combined = go.Figure()
    colors = px.colors.qualitative.Plotly

    for i, team in enumerate(teams_in_match):
        team_data = final_innings_data[final_innings_data['batting_team'] == team]
        fig_combined.add_trace(go.Scatter(
            x=team_data['over_number'],
            y=team_data['cumulative_score'],
            mode='lines',
            fill='tozeroy',
            name=team,
            line=dict(color=colors[i])
        ))

        # Add wicket markers
        team_fow_data = match_fow[match_fow['team'] == team].copy()
        if not team_fow_data.empty:
            team_fow_data['over_int'] = team_fow_data['over'].astype(float).astype(int) + 1
            fig_combined.add_trace(go.Scatter(
                x=team_fow_data['over_int'],
                y=team_fow_data['runs'],
                mode='markers',
                marker=dict(color=colors[i], size=10, line=dict(width=1, color='DarkSlateGrey')),
                name=f"{team} Wickets",
                text=team_fow_data['player_name'],
                hovertemplate='<b>Player Dismissed:</b> %{text}<br><b>Over:</b> %{x}<br><b>Score:</b> %{y}<extra></extra>',
                showlegend=False
            ))

    fig_combined.update_layout(
        title="Innings Progression with Wicket Markers",
        xaxis_title="Overs",
        yaxis_title="Cumulative Score",
        xaxis=dict(range=[1, 50], showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        plot_bgcolor='white'
    )

    st.plotly_chart(fig_combined, use_container_width=True)

    
    # --- Chart 3: Partnership Breakdown ---
    st.markdown("#### Partnership Breakdown")
    if not match_partnership.empty:
        fig_partnership_breakdown = px.bar(
            match_partnership.sort_values(by='for wicket'), 
            x='partnership runs', 
            y='team', 
            color='for wicket', 
            orientation='h', 
            title="Partnerships by Wicket"
        )
        st.plotly_chart(fig_partnership_breakdown, use_container_width=True)
    
    # --- Chart 4: Bowler Performance Summary ---
    st.markdown("#### Bowler Performance Summary")
    bowler_summary = match_bowling.groupby(['team', 'player_name']).agg(
        Overs=('overs', 'max'),
        Wickets=('wickets', 'sum'),
        Conceded=('conceded', 'sum'),
        Economy=('economy', 'first')
    ).reset_index()
    
    fig_bowler_perf = px.bar(
        bowler_summary.sort_values('Wickets', ascending=False),
        x='player_name', 
        y='Wickets', 
        color='team',
        hover_data=['Overs', 'Conceded', 'Economy'], 
        title="Wickets Taken by Bowlers in the Match"
    )
    st.plotly_chart(fig_bowler_perf, use_container_width=True)


def partnership_analysis_tab(partnership_df):
    st.markdown('<h2 class="tab-header">🤝 Partnership Deep Dive</h2>', unsafe_allow_html=True)
    
    # --- Top N Charts Section ---
    num_to_display = st.number_input("Select number of top partnerships to display:", min_value=5, max_value=50, value=10, step=5)
    
    st.subheader(f"Top {num_to_display} Highest Partnerships")
    top_partnerships_df = partnership_df.nlargest(num_to_display, 'partnership runs').copy()
    top_partnerships_df.dropna(subset=['player1_name', 'player2_name'], inplace=True)
    top_partnerships_df['pair'] = top_partnerships_df['player1_name'] + " & " + top_partnerships_df['player2_name']
    fig_top_partnerships = px.bar(top_partnerships_df, x='partnership runs', y='pair', orientation='h', title=f"Top {num_to_display} Highest Individual Partnerships", color='partnership runs', color_continuous_scale='OrRd')
    fig_top_partnerships.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_partnerships, use_container_width=True)

    st.subheader(f"Top {num_to_display} Most Successful Pairs")
    partnership_analysis_df = partnership_df.copy()
    partnership_analysis_df.dropna(subset=['player1_name', 'player2_name'], inplace=True)
    partnership_analysis_df['pair_key'] = partnership_analysis_df.apply(lambda row: tuple(sorted((row['player1_name'], row['player2_name']))), axis=1)
    prolific_pairs = partnership_analysis_df.groupby('pair_key')['partnership runs'].sum().nlargest(num_to_display).reset_index()
    prolific_pairs['pair'] = prolific_pairs['pair_key'].apply(lambda x: f"{x[0]} & {x[1]}")
    fig_prolific_pairs = px.bar(prolific_pairs, x='partnership runs', y='pair', orientation='h', title=f"Top {num_to_display} Most Prolific Batting Pairs", color='partnership runs', color_continuous_scale='Cividis')
    fig_prolific_pairs.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_prolific_pairs, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Scatter Plot Section with NEW Filter ---
    st.subheader("Partnership Run Rate Analysis")

    team_list_partnership = sorted(partnership_df['team'].dropna().unique())
    default_teams_scatter = team_list_partnership[:2] if len(team_list_partnership) >= 2 else team_list_partnership
    selected_teams_scatter = st.multiselect(
        "Select teams to display on the scatter plot:",
        team_list_partnership,
        default=default_teams_scatter,
        key='scatter_team_select'
    )
    
    scatter_df = partnership_df[partnership_df['partnership balls'] > 0].copy()
    scatter_df['run_rate'] = (scatter_df['partnership runs'] / scatter_df['partnership balls']) * 100

    if selected_teams_scatter:
        filtered_scatter_df = scatter_df[scatter_df['team'].isin(selected_teams_scatter)]
        
        fig_scatter_pr = px.scatter(filtered_scatter_df, x='partnership balls', y='partnership runs',
                                    title="Partnership Pace (Runs vs. Balls)",
                                    color='team',  # Color by team for clear comparison
                                    hover_data=['player1_name', 'player2_name', 'for wicket', 'run_rate'],
                                    labels={'partnership balls': 'Balls Faced', 'partnership runs': 'Runs Scored'})
        st.plotly_chart(fig_scatter_pr, use_container_width=True)
    else:
        st.warning("Please select at least one team to display the scatter plot.")

if __name__ == "__main__":
    main()