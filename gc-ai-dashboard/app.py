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
from src.analysis.insights import generate_insights
from src.viz.charts import create_batting_trend_chart, create_player_leaderboard
from src.viz.spray_chart import generate_mock_spray_data, create_spray_chart, get_player_spray_summary, MOCK_MARINERS_PLAYERS
from src.viz.coach_summary import render_coach_summary, generate_coach_summary
from src.viz.scouting_report import render_scouting_report, generate_scouting_report
from src.ai.grok_client import ask_quick_question

# Page config
st.set_page_config(
    page_title="GC AI Dashboard",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SHARP, CLEAN, PROFESSIONAL COLOR SYSTEM + LAYOUT
# ============================================================
st.markdown("""
<style>
    /* === Base Layout === */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }

    /* === Typography === */
    h1 { 
        font-size: 2.0rem !important; 
        font-weight: 700 !important; 
        letter-spacing: -0.025em;
        color: #0f172a;
    }
    .dark h1 { color: #f1f5f9; }

    h2 { 
        font-size: 1.35rem !important; 
        font-weight: 700 !important; 
        margin-top: 0.6rem;
        color: #1e293b;
    }
    .dark h2 { color: #e2e8f0; }

    h3 { 
        font-size: 1.05rem !important; 
        font-weight: 600 !important; 
        color: #334155;
        margin-bottom: 0.35rem;
    }
    .dark h3 { color: #cbd5e1; }

    /* === Main Color Palette - Clean & Sharp === */
    :root {
        --accent: #2563eb;
        --accent-dark: #1e40af;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --bg-app: #f8fafc;           /* Very clean light gray */
        --bg-card: #ffffff;          /* Pure clean white */
        --border: #e2e8f0;
    }

    .dark {
        --accent: #3b82f6;
        --accent-dark: #1e40af;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --bg-app: #0b1120;           /* Deep, clean dark navy (less gray) */
        --bg-card: #1e293b;          /* Rich dark card */
        --border: #334155;
    }

    /* Force clean backgrounds */
    .stApp {
        background-color: var(--bg-app) !important;
    }

    /* === Premium Coach Tools Header === */
    .coach-tools-header {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white;
        padding: 13px 22px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-weight: 600;
        font-size: 1.02rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .dark .coach-tools-header {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
    }

    /* === Clean Cards === */
    .coach-card {
        background-color: var(--bg-card);
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid var(--border);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        margin-bottom: 10px;
    }

    /* === Metrics - Cleaner look === */
    .stMetric {
        background-color: var(--bg-card);
        border-radius: 8px;
        padding: 6px 12px;
        border: 1px solid var(--border);
    }
    .stMetric label { 
        font-size: 0.78rem !important; 
        color: var(--text-secondary) !important; 
        font-weight: 500;
    }
    .stMetric value { 
        font-size: 1.25rem !important; 
        font-weight: 700;
        color: var(--text-primary);
    }

    /* === Tabs - Cleaner === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        border-bottom: 2px solid var(--border);
        padding-bottom: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 7px 15px;
        font-weight: 500;
        color: var(--text-secondary);
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent);
        border-bottom: 2px solid var(--accent);
    }

    /* === Buttons === */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.15s ease;
    }
    .stButton > button[kind="primary"] {
        background: var(--accent);
        border: none;
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--accent-dark);
        transform: translateY(-1px);
    }

    /* === Insight / Info boxes === */
    .insight-box {
        background-color: var(--bg-card);
        border-left: 5px solid var(--accent);
        padding: 13px 17px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid var(--border);
    }

    /* === Captions & small text === */
    .stCaption { 
        color: var(--text-secondary); 
        font-size: 0.8rem; 
    }

    /* === Dividers === */
    hr { 
        border-color: var(--border); 
        margin: 0.8rem 0; 
    }

    /* === General clean feel === */
    .stMarkdown p, .stMarkdown li {
        color: var(--text-primary);
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
    if "plan" not in st.session_state:
        st.session_state.plan = "free"   # "free" or "pro" for now
    if "show_pricing" not in st.session_state:
        st.session_state.show_pricing = False
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"


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
        st.header("⚾ GC AI Dashboard")

        # AI Section
        st.subheader("AI Insights")
        grok_key = st.text_input(
            "Grok API Key",
            type="password",
            placeholder="xai-...",
            help="Get your key at https://x.ai/api"
        )
        if grok_key:
            os.environ["GROK_API_KEY"] = grok_key.strip()
        else:
            os.environ.pop("GROK_API_KEY", None)

        if not grok_key:
            st.caption("Add your Grok key for real AI-powered trend analysis.")

        st.divider()

        # Data Section
        st.subheader("Data")
        if st.button("🔄 Load Demo Season", use_container_width=True):
            load_demo_data()

        if st.session_state.data is not None:
            if st.button("🗑️ Clear Current Data", use_container_width=True, type="secondary"):
                st.session_state.data = None
                st.session_state.data_source = None
                st.rerun()

        st.divider()

        # Simple tier / upgrade section
        st.subheader("Your Plan")
        if st.session_state.plan == "pro":
            st.success("**Pro** — Unlimited AI + Advanced Tools")
        else:
            st.markdown("**Free** — Limited AI")
            used = st.session_state.get("quick_q_count", 0)
            st.caption(f"Quick Q's used this session: {used}/5")

        if st.button("Upgrade to Pro", use_container_width=True):
            st.session_state.show_pricing = True
            st.rerun()

        st.divider()

        # Dark / Light mode toggle
        theme = st.radio(
            "Theme",
            ["Light", "Dark"],
            horizontal=True,
            index=1 if st.session_state.get("theme", "Dark") == "Dark" else 0,
            key="theme_toggle"
        )
        st.session_state.theme = theme

        if theme == "Dark":
            st.markdown("""
            <style>
                .stApp {
                    background-color: #0e1117;
                    color: #fafafa;
                }
                .stMarkdown, .stCaption, .stMetric, .stSelectbox, .stRadio {
                    color: #fafafa !important;
                }
            </style>
            """, unsafe_allow_html=True)

        st.caption("Built with Grok • Python + Streamlit")


def render_header():
    """Render the main page header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚾ GC AI Dashboard")
        st.caption("Clear answers for coaches and scouts. Built for decisions, not just data.")
    with col2:
        if st.session_state.data is not None:
            source = "Demo Data" if st.session_state.data_source == "demo" else "Your Uploads"
            st.success(f"{source} • {st.session_state.games_count} games")
        else:
            st.info("No data loaded")


def render_upload_section():
    """Show a clear explanation of the tool + upload options when no data is loaded."""
    st.markdown("## Turn Your GameChanger Numbers Into Real Answers")

    st.markdown("""
    Most coaches and scouts are flying blind. GameChanger gives you the raw stats — 
    but it doesn't tell you what actually matters: **trends, problems, and what to do next**.
    """)

    st.markdown("### This tool exists for two types of people:")

    col_player, col_coach = st.columns(2)

    with col_player:
        st.markdown("**Players who want to stop guessing**")
        st.markdown("""
        - Know if you're truly improving or just getting lucky
        - See your real strengths and weaknesses with data
        - Ask direct questions and get honest feedback
        """)

    with col_coach:
        st.markdown("**Coaches & Scouts who need an edge**")
        st.markdown("""
        - Quickly understand why your team is winning or losing
        - Evaluate players and opponents objectively instead of by memory
        - Spot issues early (strikeouts, trends, matchups) before they become problems
        - Make lineup, practice, and scouting decisions with actual evidence
        """)

    st.divider()

    st.markdown("### Get Started")

    # Plan status
    if st.session_state.plan == "pro":
        st.caption("**Pro** plan — Full AI access enabled")
    else:
        st.caption("**Free** plan — Limited AI questions (5 Quick Q's per session)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Try it with demo data**")
        st.write("A realistic 12-game high school season so you can see exactly how it works.")
        if st.button("Load Demo Season", type="primary", use_container_width=True):
            load_demo_data()

    with col2:
        st.markdown("**Upload your real GameChanger data**")
        st.write("Export CSVs from GameChanger (multiple games at once works best).")

        uploaded_files = st.file_uploader(
            "Drop your CSV(s) here",
            type=["csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_files:
            handle_file_upload(uploaded_files)

    st.info(
        "Tip: GameChanger → Team → Stats → Export. The more games you upload, the better the trends become."
    )

    st.markdown("---")
    st.markdown("**Ready for unlimited AI questions and real scouting power?**")
    if st.button("See Pro Plan", use_container_width=False):
        st.session_state.show_pricing = True
        st.rerun()


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

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🏆 Leaderboards", "📊 Distributions", "🎯 Spray Charts"])

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

    with tab4:
        st.markdown('<div style="font-weight:600; font-size:1.0rem; margin-bottom:4px;">Spray Charts — Hit Location</div>', unsafe_allow_html=True)
        st.caption("Mock 2026 Seattle Mariners data — useful for shift and defensive alignment decisions.")

        view_mode = st.radio(
            "View",
            ["Individual Player", "Team by Handedness"],
            horizontal=True,
            key="spray_view_mode"
        )

        if view_mode == "Individual Player":
            player_list = list(MOCK_MARINERS_PLAYERS.keys())
            selected_player = st.selectbox("Select Player", player_list, index=0, key="spray_player")

            spray_df = generate_mock_spray_data(selected_player, num_at_bats=75)
            fig = create_spray_chart(spray_df, player_name=selected_player)
            st.plotly_chart(fig, use_container_width=True)

            summary = get_player_spray_summary(selected_player)
            st.markdown(f"**{selected_player} Spray Tendency**")
            st.markdown(f"Pull: **{summary['pull_pct']}%** | Center: **{summary['center_pct']}%** | Opposite: **{summary['opposite_pct']}%**")
            st.caption("Mock data for demonstration")

        else:
            # Team view by handedness
            handedness = st.radio(
                "Show",
                ["All Hitters", "Right-handers only", "Left-handers only"],
                horizontal=True,
                key="team_handedness"
            )

            filter_map = {
                "All Hitters": "All",
                "Right-handers only": "Right",
                "Left-handers only": "Left"
            }

            team_df = generate_team_spray_data(handedness=filter_map[handedness], num_at_bats_per_player=35)
            fig = create_team_spray_chart(team_df, title=f"Team Spray Chart — {handedness}")
            st.plotly_chart(fig, use_container_width=True)

            st.caption("Team-level view colored by handedness. Useful for shift decisions and pitching strategy.")


def render_insights(df: pd.DataFrame):
    """Generate and display insights (AI via Grok or rule-based fallback)."""
    grok_key = os.environ.get("GROK_API_KEY")

    # Header row with Regenerate button
    header_col, btn_col = st.columns([5, 2])
    with header_col:
        st.markdown("### 🧠 Smart Insights")
    with btn_col:
        if grok_key:
            if st.button("🔄 Regenerate", use_container_width=True, help="Re-analyze with Grok"):
                st.rerun()

    # Loading state
    if grok_key:
        spinner_text = "Grok is analyzing trends and recent performance..."
    else:
        spinner_text = "Analyzing the numbers..."

    with st.spinner(spinner_text):
        insights, mode = generate_insights(df, grok_api_key=grok_key)

    # Display
    if mode == "grok":
        # Better Grok badge
        st.markdown(
            '<span style="background-color:#4f46e5;color:white;padding:3px 10px;border-radius:6px;font-size:0.75em;font-weight:600;">POWERED BY GROK</span>',
            unsafe_allow_html=True
        )
        st.markdown(insights)

        # Copy button (light implementation)
        st.download_button(
            label="📋 Copy Insights",
            data=insights,
            file_name="grok_insights.md",
            mime="text/markdown",
            help="Download the insights as a Markdown file (easy to copy)",
            use_container_width=False
        )
        st.caption("Generated by Grok (xAI)")

    else:
        for insight in insights:
            st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
        st.caption("Rule-based insights (add your Grok API key in the sidebar for richer AI analysis).")


def render_quick_questions(df: pd.DataFrame):
    """Quick Q's - Ask short, direct questions about the data (role-aware)."""
    st.markdown("### Quick Q's")
    st.caption("Ask anything. Get straight answers about your players or team — tailored for coaches and scouts.")

    # Initialize session state
    if "quick_q_role" not in st.session_state:
        st.session_state.quick_q_role = "Player"
    if "quick_q_answer" not in st.session_state:
        st.session_state.quick_q_answer = ""
    if "quick_q_last_question" not in st.session_state:
        st.session_state.quick_q_last_question = ""

    # Role selector - clearer labeling
    role = st.radio(
        "I am a",
        options=["Player", "Coach"],
        horizontal=True,
        index=0 if st.session_state.quick_q_role == "Player" else 1,
    )
    st.session_state.quick_q_role = role

    # Question input
    question = st.text_input(
        "Your question",
        placeholder="Type a short question here...",
        key="quick_q_input"
    )

    ask_button = st.button("Ask Grok", type="primary")

    if ask_button and question.strip():
        if st.session_state.plan == "free":
            # Simple free tier limit for now
            if "quick_q_count" not in st.session_state:
                st.session_state.quick_q_count = 0

            if st.session_state.quick_q_count >= 5:
                st.warning("You've reached the Free plan limit for Quick Q's (5 questions). Upgrade to Pro for unlimited access.")
            else:
                with st.spinner("Thinking..."):
                    answer = ask_quick_question(df, question.strip(), role)
                    st.session_state.quick_q_answer = answer
                    st.session_state.quick_q_last_question = question.strip()
                    st.session_state.quick_q_count += 1
        else:
            # Pro = unlimited
            with st.spinner("Thinking..."):
                answer = ask_quick_question(df, question.strip(), role)
                st.session_state.quick_q_answer = answer
                st.session_state.quick_q_last_question = question.strip()

    # Show previous question + answer
    if st.session_state.quick_q_answer:
        st.markdown("---")
        if st.session_state.quick_q_last_question:
            st.markdown(f"**You asked:** {st.session_state.quick_q_last_question}")

        st.markdown("**Answer:**")
        st.markdown(st.session_state.quick_q_answer)

        if st.button("Clear", key="clear_quick_q"):
            st.session_state.quick_q_answer = ""
            st.session_state.quick_q_last_question = ""
            st.rerun()


def main():
    init_session_state()
    render_sidebar()
    render_header()

    st.divider()

    if st.session_state.data is None:
        render_upload_section()
        return

    df = st.session_state.data

    # ============================================
    # COACH / SCOUT TOOLS (High-value area)
    # ============================================
    st.markdown('<div class="coach-tools-header">Coach & Scout Tools</div>', unsafe_allow_html=True)
    st.caption("High-signal insights built for coaches and scouts who make real decisions.")

    st.markdown("#### Team Summary")
    render_coach_summary(df)

    st.markdown("#### Scouting Angles")
    render_scouting_report(df)

    st.divider()

    # ============================================
    # DETAILED ANALYSIS
    # ============================================
    st.markdown('<div style="margin-top: 12px; margin-bottom: 6px; font-weight: 600; color: #475569; font-size: 1.0rem;">Detailed Analysis</div>', unsafe_allow_html=True)

    # Remove the temporary banner for cleaner UX
    # (We can keep it only during heavy development if needed)

    render_kpi_cards(df)
    st.divider()

    # Hide the raw data table behind an expander by default (less clutter)
    with st.expander("📋 View Raw Data Table", expanded=False):
        render_data_table(df)

    st.divider()

    render_visualizations(df)
    st.divider()

    render_insights(df)

    st.divider()

    if st.session_state.data is not None:
        render_quick_questions(df)

    # Future expansion hint (keep collapsed)
    with st.expander("Roadmap & Ideas", expanded=False):
        st.markdown("""
        - Player deep-dive pages with spray charts
        - Pitching analysis section
        - Opponent scouting reports
        - "What if" lineup optimizer
        - Export beautiful PDF reports
        - Natural language chat ("Show me players who improved vs righties")
        """)


def render_pricing():
    """Pricing page for Free vs Pro, targeted at coaches and scouts."""
    st.markdown("## Stop Guessing. Start Knowing.")

    st.markdown(
        "GameChanger gives you the numbers. This tool turns them into **clear decisions** — "
        "for coaches who need to improve their team, and scouts who need to evaluate players and opponents quickly."
    )

    st.markdown("### The Real Difference")

    col_free, col_pro = st.columns(2)

    # Free Plan
    with col_free:
        st.markdown("### Free")
        st.markdown("**$0** — Forever")
        st.markdown("See what the tool can do")

        st.markdown("""
        - Upload your GameChanger data
        - Basic team and player stats
        - Charts and season overview
        - Limited AI (only 5 Quick Q's)
        - Rule-based insights only
        """)

        st.caption("Good for: Getting a feel for the tool")

    # Pro Plan
    with col_pro:
        st.markdown("### Pro — For Coaches & Scouts Who Need Answers")
        st.markdown("**$15 / month** or **$144 / year** (20% off)")

        st.markdown("""
        **What actually changes when you go Pro:**

        - Ask **unlimited** questions about your team or players in plain English
        - Get AI that understands context (not just generic stats)
        - Spot real trends and problems before they cost you games
        - Scout opponents faster and more objectively
        - Export clean reports you can actually use or share
        - Track how players and teams are trending over time
        """)

        st.caption("Best for: Coaches who want an edge and scouts who evaluate seriously")

    st.divider()

    st.markdown("### Pricing")

    price_col1, price_col2 = st.columns(2)

    with price_col1:
        st.markdown("**Monthly**")
        st.markdown("### $15 / month")
        if st.button("Subscribe Monthly", key="sub_monthly", type="primary", use_container_width=True):
            st.success("Thanks! In a real version this would open Stripe checkout.")
            st.info("For now, you can manually switch to Pro mode below for testing.")

    with price_col2:
        st.markdown("**Yearly** — Save 20%")
        st.markdown("### $144 / year")
        st.caption("≈ $12 per month")
        if st.button("Subscribe Yearly", key="sub_yearly", type="primary", use_container_width=True):
            st.success("Thanks! In a real version this would open Stripe checkout.")
            st.info("For now, you can manually switch to Pro mode below for testing.")

    st.divider()

    # Testing helper
    st.markdown("**For testing right now:**")
    if st.session_state.plan == "free":
        if st.button("Switch to Pro mode (testing only)", type="secondary"):
            st.session_state.plan = "pro"
            st.session_state.show_pricing = False
            st.rerun()
    else:
        if st.button("Switch back to Free mode (testing only)", type="secondary"):
            st.session_state.plan = "free"
            st.rerun()

    if st.button("Back to Dashboard"):
        st.session_state.show_pricing = False
        st.rerun()


if __name__ == "__main__":
    main()
