"""
Smart Insights Engine for GC AI Dashboard

Currently rule-based + statistical analysis.
Designed to be easily upgraded to call real LLMs later.
"""

import pandas as pd
import numpy as np
from typing import List


def _safe_div(n: float, d: float) -> float:
    return n / d if d > 0 else 0.0


def generate_smart_insights(df: pd.DataFrame) -> List[str]:
    """
    Analyze the loaded baseball data and return a list of insightful bullet points.
    These are written in natural, coach-friendly language.
    """
    if df is None or df.empty:
        return ["No data available to analyze yet."]

    insights: List[str] = []

    # === Basic aggregates ===
    total_games = df["date"].nunique() if "date" in df.columns else 1
    total_ab = int(df["AB"].sum())
    total_hits = int(df["H"].sum())
    team_avg = _safe_div(total_hits, total_ab)

    total_hr = int(df.get("HR", pd.Series([0])).sum())
    total_rbi = int(df.get("RBI", pd.Series([0])).sum())
    total_walks = int(df.get("BB", pd.Series([0])).sum())

    # === Team-level insights ===
    if team_avg >= 0.320:
        insights.append(f"🔥 The team is absolutely raking — collective batting average of <b>{team_avg:.3f}</b> across {total_games} games.")
    elif team_avg >= 0.280:
        insights.append(f"✅ Solid team offense: <b>{team_avg:.3f}</b> AVG with {total_hr} home runs and {total_rbi} RBIs.")
    elif team_avg >= 0.240:
        insights.append(f"📊 Team is hitting <b>{team_avg:.3f}</b>. Contact is decent but there's room to drive the ball more ({total_hr} HR total).")
    else:
        insights.append(f"⚠️ Offense struggling at <b>{team_avg:.3f}</b> AVG. Walk rate ({total_walks} BB) is a bright spot worth building on.")

    # === Power & extra-base analysis ===
    extra_base_hits = int(df.get("2B", 0).sum()) + int(df.get("3B", 0).sum()) + total_hr
    if total_ab > 80:
        xbh_rate = extra_base_hits / total_ab
        if xbh_rate > 0.085:
            insights.append(f"💪 Power production is strong — extra-base hit rate of {xbh_rate:.1%}.")

    # === Top performers ===
    if "player_name" in df.columns:
        player_stats = (
            df.groupby("player_name")
            .agg({"AB": "sum", "H": "sum", "HR": "sum", "RBI": "sum", "BB": "sum"})
            .reset_index()
        )
        player_stats["AVG"] = player_stats.apply(lambda r: _safe_div(r["H"], r["AB"]), axis=1)

        # Best hitter (min 12 AB)
        qualified = player_stats[player_stats["AB"] >= 12]
        if not qualified.empty:
            best_hitter = qualified.loc[qualified["AVG"].idxmax()]
            insights.append(
                f"⭐ <b>{best_hitter['player_name']}</b> is the hottest bat right now: "
                f"{best_hitter['AVG']:.3f} AVG over {int(best_hitter['AB'])} at-bats."
            )

            # Home run leader
            hr_leader = player_stats.loc[player_stats["HR"].idxmax()]
            if hr_leader["HR"] >= 2:
                insights.append(
                    f"🏠 Power leader: <b>{hr_leader['player_name']}</b> with {int(hr_leader['HR'])} home runs."
                )

            # On-base machine
            obp_leader = player_stats.loc[(player_stats["H"] + player_stats["BB"]).idxmax()]
            if obp_leader["BB"] >= 5:
                insights.append(
                    f"👀 <b>{obp_leader['player_name']}</b> is getting on base a ton "
                    f"({int(obp_leader['H'] + obp_leader['BB'])} times via hit or walk)."
                )

    # === Strikeout vs walk observations ===
    total_so = int(df.get("SO", pd.Series([0])).sum())
    if total_ab > 60:
        so_rate = total_so / total_ab
        bb_rate = total_walks / total_ab
        if so_rate > 0.32:
            insights.append(f"📉 High strikeout rate ({so_rate:.0%}). Chasing or missing too many pitches?")
        elif bb_rate > 0.14:
            insights.append(f"🎯 Excellent plate discipline — {bb_rate:.0%} walk rate.")

    # === Multi-game / "all games one day" context ===
    if total_games >= 3:
        # Simple hot/cold detection
        if "date" in df.columns:
            recent = df[df["date"] >= df["date"].max() - pd.Timedelta(days=10)]
            if not recent.empty and len(recent) > 15:
                recent_avg = _safe_div(recent["H"].sum(), recent["AB"].sum())
                if recent_avg > team_avg + 0.045:
                    insights.append(f"🚀 The bats have heated up lately — {recent_avg:.3f} AVG in the most recent games.")

    # === Final encouragement / next step ===
    if len(insights) < 3:
        insights.append(
            "📌 Tip: Upload more complete game logs (including multiple dates) for deeper streak and matchup analysis."
        )

    return insights[:6]  # Keep it focused
