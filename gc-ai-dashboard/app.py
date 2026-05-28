"""
GC AI Dashboard
AI-powered analytics for GameChanger baseball stats.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from pathlib import Path

from src.data.parser import parse_gamechanger_csv, generate_synthetic_baseball_data
from src.analysis.insights import generate_smart_insights
from src.viz.charts import create_batting_trend_chart, create_player_leaderboard

# Page config
st.set_page_config(
    page_title="GC AI Dashboard",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a clean, modern feel
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #e9ecef;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .insight-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9f0ff 100%);
        border-left: 5px solid #4f46e5;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "data" not in st.session_state:
        st.session_state.data = None
    if "data_source" not in st.session_state:
        st.session_state.data_source = None
    if "games_count" not in st.session_state:
        st.session_state.games_count = 0


def load_demo_data():
    """Generate and load a realistic synthetic baseball season."""
    with st.spinner("Generating realistic demo season..."):
        df = generate_synthetic_baseball_data(num_games=12, num_players=14)
        st.session_state.data = df
        st.session_state.data_source = "demo"
        st.session_state.games_count = df["date"].nunique()
        st.success("Demo season loaded! 12 games, 14 players.")


def handle_file_upload(uploaded_files):
    """Process uploaded GameChanger CSV files."""
    if not uploaded_files:
        return

    all_dfs = []
    for uploaded_file in uploaded_files:
        try:
            df = parse_gamechanger_csv(uploaded_file)
            if df is not None and not df.empty:
                df["source_file"] = uploaded_file.name
                all_dfs.append(df)
        except Exception as e:
            st.error(f"Failed to parse {uploaded_file.name}: {str(e)}")

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        st.session_state.data = combined
        st.session_state.data_source = "upload"
        st.session_state.games_count = combined["date"].nunique() if "date" in combined.columns else 1
        st.success(f"Loaded {len(all_dfs)} file(s) with {len(combined)} stat rows across {st.session_state.games_count} game(s).")
    else:
        st.warning("No valid data found in the uploaded files.")


def render_sidebar():
    """Render the configuration sidebar."""
    with st.sidebar:
        st.header("⚙️ Settings")

        st.subheader("AI Provider")
        ai_provider = st.selectbox(
            "Choose AI backend",
            ["Rule-based (no API key)", "Grok (xAI)", "OpenAI"],
            help="Rule-based mode works offline and is very good for baseball insights."
        )

        if ai_provider != "Rule-based (no API key)":
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="sk-..." if ai_provider == "OpenAI" else "xai-...",
                help="Your key is only used locally in this session."
            )
            if api_key:
                os.environ["AI_API_KEY"] = api_key
                os.environ["AI_PROVIDER"] = "xai" if ai_provider == "Grok (xAI)" else "openai"
        else:
            os.environ.pop("AI_API_KEY", None)

        st.divider()

        st.subheader("Data")
        if st.button("🔄 Load Demo Season", use_container_width=True):
            load_demo_data()

        if st.session_state.data is not None:
            if st.button("🗑️ Clear Data", use_container_width=True, type="secondary"):
                st.session_state.data = None
                st.session_state.data_source = None
                st.rerun()

        st.divider()

        st.caption("Built together with Grok • Python + Streamlit")
        st.caption("Baseball-first • Ready for all sports")


def render_header():
    """Render the main page header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚾ GC AI Dashboard")
        st.caption("Upload GameChanger stats → Get real insights powered by data + AI")
    with col2:
        if st.session_state.data is not None:
            source = "Demo Data" if st.session_state.data_source == "demo" else "Your Uploads"
            st.success(f"{source} • {st.session_state.games_count} games")
        else:
            st.info("No data loaded")


def render_upload_section():
    """Show upload area when no data is loaded."""
    st.markdown("### Get Started")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Option 1: Try with demo data**")
        st.write("A realistic 12-game high school baseball season with 14 players.")
        if st.button("Load Demo Season", type="primary", use_container_width=True):
            load_demo_data()

    with col2:
        st.markdown("**Option 2: Upload GameChanger exports**")
        st.write("CSV files from GameChanger (player game logs or team stats work best).")

        uploaded_files = st.file_uploader(
            "Drop your CSV(s) here",
            type=["csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_files:
            handle_file_upload(uploaded_files)

    st.info(
        "💡 Tip: GameChanger → Team → Stats → Export as CSV. "
        "You can upload multiple files for tournaments or 'all games one day' analysis."
    )


def render_kpi_cards(df: pd.DataFrame):
    """Display key performance indicators."""
    st.markdown("### Season Overview")

    # Basic calculations (hitting focused for now)
    if "AB" in df.columns and "H" in df.columns:
        total_ab = int(df["AB"].sum())
        total_hits = int(df["H"].sum())
        team_avg = total_hits / total_ab if total_ab > 0 else 0

        total_hr = int(df.get("HR", pd.Series([0])).sum())
        total_rbi = int(df.get("RBI", pd.Series([0])).sum())
        total_bb = int(df.get("BB", pd.Series([0])).sum())

        games = df["date"].nunique() if "date" in df.columns else 1
        players = df["player_name"].nunique() if "player_name" in df.columns else 1

        cols = st.columns(6)
        metrics = [
            ("Games", f"{games}"),
            ("Players", f"{players}"),
            ("Team AVG", f"{team_avg:.3f}"),
            ("Total HR", f"{total_hr}"),
            ("Total RBI", f"{total_rbi}"),
            ("Walks", f"{total_bb}"),
        ]
        for col, (label, value) in zip(cols, metrics):
            with col:
                st.metric(label, value)
    else:
        st.write(df.head())


def render_data_table(df: pd.DataFrame):
    """Show the processed data with filters."""
    with st.expander("📋 View & Filter Raw Data", expanded=False):
        # Simple player filter
        if "player_name" in df.columns:
            players = ["All"] + sorted(df["player_name"].unique().tolist())
            selected = st.selectbox("Filter by player", players, index=0)
            if selected != "All":
                df = df[df["player_name"] == selected]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=320,
        )


def render_visualizations(df: pd.DataFrame):
    """Render interactive charts."""
    st.markdown("### Visualizations")

    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🏆 Leaderboards", "📊 Distributions"])

    with tab1:
        if "date" in df.columns and "H" in df.columns:
            fig = create_batting_trend_chart(df)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Need date + hitting columns for trend analysis.")

    with tab2:
        if "player_name" in df.columns:
            fig = create_player_leaderboard(df)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if "AB" in df.columns and "H" in df.columns:
            df = df.copy()
            df["AVG"] = df.apply(
                lambda r: r["H"] / r["AB"] if r["AB"] > 0 else 0, axis=1
            )
            fig = px.histogram(
                df,
                x="AVG",
                nbins=15,
                title="Distribution of At-Bat Averages",
                labels={"AVG": "Batting Average"},
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)


def render_insights(df: pd.DataFrame):
    """Generate and display smart insights."""
    st.markdown("### 🧠 Smart Insights")

    with st.spinner("Analyzing the numbers..."):
        insights = generate_smart_insights(df)

    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

    st.caption(
        "These insights are currently generated with smart heuristics. "
        "Connect an AI provider in the sidebar for even richer analysis."
    )


def main():
    init_session_state()
    render_sidebar()
    render_header()

    st.divider()

    if st.session_state.data is None:
        render_upload_section()
        return

    df = st.session_state.data

    # Main dashboard sections
    render_kpi_cards(df)
    st.divider()

    render_data_table(df)
    st.divider()

    render_visualizations(df)
    st.divider()

    render_insights(df)

    # Future expansion hint
    with st.expander("What's next? (Ideas for us to build together)"):
        st.markdown("""
        - Player deep-dive pages with spray charts
        - Pitching analysis section
        - Opponent scouting reports
        - "What if" lineup optimizer
        - Export beautiful PDF reports
        - Natural language chat ("Show me players who improved vs righties")
        """)


if __name__ == "__main__":
    main()
