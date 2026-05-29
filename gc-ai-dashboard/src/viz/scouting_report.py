"""
Opponent Scouting Report / Angles

This is high-value content for coaches and scouts.
It turns raw stats into actionable game-planning information.
"""

import pandas as pd
import streamlit as st
from src.viz.spray_chart import MOCK_MARINERS_PLAYERS, generate_mock_spray_data


def generate_scouting_report(df: pd.DataFrame) -> dict:
    """
    Create a structured scouting report from the dataset.
    Designed for coaches and scouts to use when preparing for an opponent.
    """
    if df is None or df.empty:
        return {}

    report = {}

    total_ab = int(df.get("AB", pd.Series([0])).sum())
    total_so = int(df.get("SO", pd.Series([0])).sum())
    total_hr = int(df.get("HR", pd.Series([0])).sum())
    total_bb = int(df.get("BB", pd.Series([0])).sum())

    k_rate = (total_so / total_ab * 100) if total_ab > 0 else 0
    bb_rate = (total_bb / total_ab * 100) if total_ab > 0 else 0

    # Team-level tendencies
    tendencies = []

    if k_rate > 26:
        tendencies.append("High strikeout rate overall — attack the zone early in counts.")
    elif k_rate < 18:
        tendencies.append("Very contact-oriented team. They put the ball in play a lot.")

    if bb_rate > 11:
        tendencies.append("Patient at the plate. Expect long at-bats and deep counts.")
    elif bb_rate < 7:
        tendencies.append("Very aggressive early — look for first-pitch strikes.")

    if total_hr >= 8:
        tendencies.append("Legitimate power threat. Respect pull-side power from the middle of the order.")

    report["team_tendencies"] = tendencies if tendencies else ["No extreme tendencies in this sample."]

    # Player-specific scouting notes (using mock spray tendencies where available)
    player_notes = []

    if "player_name" in df.columns:
        player_stats = (
            df.groupby("player_name")
            .agg({"AB": "sum", "H": "sum", "HR": "sum", "SO": "sum"})
            .reset_index()
        )
        player_stats["AVG"] = player_stats.apply(lambda r: r["H"] / r["AB"] if r["AB"] > 0 else 0, axis=1)

        # Find interesting players
        qualified = player_stats[player_stats["AB"] >= 12]

        if not qualified.empty:
            # Power threat
            power = qualified.nlargest(1, "HR").iloc[0]
            if power["HR"] >= 3:
                player_notes.append(
                    f"**{power['player_name']}** — Major power threat. {int(power['HR'])} HR in sample. "
                    "Attack him up in the zone."
                )

            # High K guy
            high_k = qualified.nlargest(1, "SO").iloc[0]
            if high_k["SO"] / high_k["AB"] > 0.30:
                player_notes.append(
                    f"**{high_k['player_name']}** — Swing-and-miss guy ({int(high_k['SO'])} K's). "
                    "Expand the zone and attack with breaking balls."
                )

            # Contact machine
            contact = qualified.nsmallest(1, "SO").iloc[0]
            if contact["SO"] / contact["AB"] < 0.15 and contact["AB"] >= 15:
                player_notes.append(
                    f"**{contact['player_name']}** — Tough out. Low strikeouts. "
                    "Make him earn it — don't give him anything to drive."
                )

    # Blend in spray chart insights for players who have mock data
    for player in MOCK_MARINERS_PLAYERS:
        if player in df["player_name"].values:
            profile = MOCK_MARINERS_PLAYERS[player]
            if profile["pull"] > 0.48:
                player_notes.append(
                    f"**{player}** is very pull-heavy. Shift him and attack away."
                )
            elif profile["opposite"] > 0.30:
                player_notes.append(
                    f"**{player}** has a strong opposite-field approach. Don't leave anything over the plate."
                )

    report["player_notes"] = player_notes if player_notes else ["No major individual scouting flags in this sample."]

    # Suggested game plan
    game_plan = []

    if k_rate > 25:
        game_plan.append("Attack early in the count. Don't nibble.")
    if total_hr >= 6:
        game_plan.append("Be careful with the middle of the order — they have real power.")
    if bb_rate > 10:
        game_plan.append("Work ahead. This team will make you throw a lot of pitches.")

    report["game_plan"] = game_plan if game_plan else ["No major adjustments needed based on this sample."]

    return report


def render_scouting_report(df: pd.DataFrame):
    """Render a high-value opponent scouting report."""
    st.markdown('<div style="font-weight:600; font-size:1.05rem; margin-bottom:2px;">Scouting Angles</div>', unsafe_allow_html=True)
    st.caption("Game-planning intelligence. What you actually do with the data.")

    report = generate_scouting_report(df)

    # Team Tendencies
    st.markdown("**Team Tendencies**")
    for t in report.get("team_tendencies", []):
        st.markdown(f"- {t}")

    st.divider()

    # Player-Specific Notes
    st.markdown("**Key Player Notes**")
    for note in report.get("player_notes", []):
        st.markdown(f"- {note}")

    st.divider()

    # Suggested Game Plan (highest value section)
    st.markdown("**🎯 Suggested Game Plan / Adjustments**")
    for item in report.get("game_plan", []):
        st.markdown(f"- {item}")

    st.caption(
        "Pro unlocks the ability to generate these reports for any opponent and export them."
    )