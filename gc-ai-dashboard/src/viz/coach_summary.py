"""
Coach / Scout Summary View

This is the "money view" — the section that should make a coach or scout think:
"I would actually pay for this every month."
"""

import pandas as pd
import streamlit as st


def generate_coach_summary(df: pd.DataFrame) -> dict:
    """
    Generate a high-signal, actionable summary for coaches and scouts.
    Designed to feel like something a good advance scout would hand you.
    """
    if df is None or df.empty:
        return {}

    summary = {}

    total_games = df["date"].nunique() if "date" in df.columns else 1
    total_ab = int(df.get("AB", pd.Series([0])).sum())
    total_hits = int(df.get("H", pd.Series([0])).sum())
    team_avg = total_hits / total_ab if total_ab > 0 else 0.0

    total_hr = int(df.get("HR", pd.Series([0])).sum())
    total_so = int(df.get("SO", pd.Series([0])).sum())
    total_bb = int(df.get("BB", pd.Series([0])).sum())
    total_rbi = int(df.get("RBI", pd.Series([0])).sum())

    summary["games"] = total_games
    summary["team_avg"] = round(team_avg, 3)
    summary["total_hr"] = total_hr
    summary["k_rate"] = round((total_so / total_ab) * 100, 1) if total_ab > 0 else 0
    summary["bb_rate"] = round((total_bb / total_ab) * 100, 1) if total_ab > 0 else 0
    summary["rbi_per_game"] = round(total_rbi / total_games, 2) if total_games > 0 else 0

    # === Key Problems (what a coach needs to fix) ===
    problems = []
    if summary["k_rate"] > 27:
        problems.append(f"**Strikeouts are killing you** — {summary['k_rate']}% K-rate. This is the #1 issue right now.")
    if team_avg < 0.235:
        problems.append("**Contact is poor.** The offense is not putting the ball in play enough.")
    if summary["bb_rate"] < 8.5:
        problems.append("**Way too aggressive early.** Very low walk rate — hitters are not working counts.")

    summary["problems"] = problems if problems else ["No glaring team-wide issues in this sample."]

    # === Strengths ===
    strengths = []
    if summary["k_rate"] < 19:
        strengths.append("Excellent plate discipline as a unit.")
    if total_hr >= max(6, total_games // 2):
        strengths.append("Power is a legitimate weapon right now.")
    if summary["bb_rate"] > 11:
        strengths.append("Very patient approach — working deep counts and getting on base.")

    summary["strengths"] = strengths if strengths else ["No dominant strengths showing in this window."]

    # === Actionable Recommendations (this is what people pay for) ===
    recommendations = []
    if summary["k_rate"] > 26:
        recommendations.append("Shorten swings with two strikes. Consider a more aggressive approach in hitter's counts.")
    if summary["bb_rate"] < 8:
        recommendations.append("Work on plate discipline in practice — too many first-pitch swings.")
    if total_hr > 0 and summary["k_rate"] > 25:
        recommendations.append("You're giving up too many easy outs. Prioritize contact over launch angle in big situations.")

    summary["recommendations"] = recommendations if recommendations else [
        "Continue current approach — no major adjustments recommended based on this sample."
    ]

    # === Individual Scouting Notes (very high value for scouts) ===
    scouting_notes = []
    if "player_name" in df.columns:
        player_stats = (
            df.groupby("player_name")
            .agg({"AB": "sum", "H": "sum", "HR": "sum", "SO": "sum", "RBI": "sum"})
            .reset_index()
        )
        player_stats["AVG"] = player_stats.apply(lambda r: r["H"] / r["AB"] if r["AB"] > 0 else 0, axis=1)

        # Top performer
        qualified = player_stats[player_stats["AB"] >= 12]
        if not qualified.empty:
            hot = qualified.nlargest(1, "AVG").iloc[0]
            scouting_notes.append(
                f"**{hot['player_name']}** is a real problem right now — {hot['AVG']:.3f} AVG with {int(hot['HR'])} HR in the sample."
            )

            # Cold / struggling
            cold = qualified.nsmallest(1, "AVG").iloc[0]
            if cold["AVG"] < 0.200 and cold["AB"] >= 15:
                scouting_notes.append(
                    f"**{cold['player_name']}** is ice cold — only {int(cold['H'])} hits in {int(cold['AB'])} at-bats. Exploit him."
                )

    summary["scouting_notes"] = scouting_notes if scouting_notes else ["No major individual red flags or standouts in this sample."]

    return summary


def render_coach_summary(df: pd.DataFrame):
    """Render the premium Coach/Scout Summary view."""
    st.markdown('<div style="font-weight:600; font-size:1.05rem; margin-bottom:2px;">Team Summary</div>', unsafe_allow_html=True)
    st.caption("The view a serious coach checks first. Actionable, not just data.")

    summary = generate_coach_summary(df)

    # Key Numbers
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Team AVG", f"{summary.get('team_avg', 0):.3f}")
    c2.metric("K-Rate", f"{summary.get('k_rate', 0)}%")
    c3.metric("Walk Rate", f"{summary.get('bb_rate', 0)}%")
    c4.metric("RBI / Game", f"{summary.get('rbi_per_game', 0):.2f}")

    st.divider()

    # Problems vs Strengths
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🚨 Biggest Problems Right Now**")
        for item in summary.get("problems", []):
            st.markdown(f"- {item}")

    with col2:
        st.markdown("**✅ What’s Working**")
        for item in summary.get("strengths", []):
            st.markdown(f"- {item}")

    st.divider()

    # Actionable Recommendations (this is the money section)
    st.markdown("**🎯 What You Should Do**")
    for rec in summary.get("recommendations", []):
        st.markdown(f"- {rec}")

    st.divider()

    # Scouting Notes
    st.markdown("**🔍 Scouting Notes (For Opponents & Your Own Team)**")
    for note in summary.get("scouting_notes", []):
        st.markdown(f"- {note}")

    st.caption(
        "This view is designed to replace 30–90 minutes of manual stat work. "
        "Pro unlocks unlimited access + the ability to save/export these reports."
    )