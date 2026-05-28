"""
Visualization helpers for the GC AI Dashboard.
All charts use Plotly for rich interactivity.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional


def create_batting_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Show team or player hitting performance over time.
    Aggregates by date.
    """
    if "date" not in df.columns or "H" not in df.columns or "AB" not in df.columns:
        return go.Figure()

    daily = (
        df.groupby("date")
        .agg({"H": "sum", "AB": "sum"})
        .reset_index()
    )
    daily["AVG"] = daily.apply(
        lambda r: r["H"] / r["AB"] if r["AB"] > 0 else 0, axis=1
    )
    daily = daily.sort_values("date")

    fig = go.Figure()

    # Batting average line
    fig.add_trace(
        go.Scatter(
            x=daily["date"],
            y=daily["AVG"],
            mode="lines+markers",
            name="Team AVG",
            line=dict(color="#4f46e5", width=3),
            marker=dict(size=8),
        )
    )

    # Add a subtle hits bar on secondary axis
    fig.add_trace(
        go.Bar(
            x=daily["date"],
            y=daily["H"],
            name="Total Hits",
            yaxis="y2",
            marker_color="rgba(79, 70, 229, 0.25)",
        )
    )

    fig.update_layout(
        title="Team Batting Performance Over Time",
        xaxis_title="Game Date",
        yaxis=dict(title="Batting Average", tickformat=".3f", range=[0, 0.55]),
        yaxis2=dict(title="Hits", overlaying="y", side="right", showgrid=False),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
    )
    return fig


def create_player_leaderboard(df: pd.DataFrame, metric: str = "OPS", top_n: int = 10) -> go.Figure:
    """
    Horizontal bar chart of top players by a key metric.
    """
    if "player_name" not in df.columns:
        return go.Figure()

    # Calculate per-player stats
    player_stats = (
        df.groupby("player_name")
        .agg({
            "AB": "sum",
            "H": "sum",
            "2B": "sum",
            "3B": "sum",
            "HR": "sum",
            "BB": "sum",
            "HBP": "sum",
            "SF": "sum",
        })
        .reset_index()
    )

    # Compute advanced metrics
    player_stats["AVG"] = player_stats.apply(
        lambda r: r["H"] / r["AB"] if r["AB"] > 0 else 0, axis=1
    )
    player_stats["OBP"] = player_stats.apply(
        lambda r: (r["H"] + r["BB"] + r["HBP"]) / (r["AB"] + r["BB"] + r["HBP"] + r["SF"])
        if (r["AB"] + r["BB"] + r["HBP"] + r["SF"]) > 0 else 0,
        axis=1,
    )
    player_stats["SLG"] = player_stats.apply(
        lambda r: (r["H"] + 2 * r["2B"] + 3 * r["3B"] + 4 * r["HR"]) / r["AB"]
        if r["AB"] > 0 else 0,
        axis=1,
    )
    player_stats["OPS"] = player_stats["OBP"] + player_stats["SLG"]

    # Filter players with enough at-bats
    qualified = player_stats[player_stats["AB"] >= 8].copy()
    if qualified.empty:
        qualified = player_stats.copy()

    qualified = qualified.sort_values(metric, ascending=True).tail(top_n)

    color_map = {
        "OPS": "#4f46e5",
        "AVG": "#10b981",
        "HR": "#ef4444",
        "RBI": "#f59e0b",
    }
    color = color_map.get(metric, "#4f46e5")

    fig = px.bar(
        qualified,
        x=metric,
        y="player_name",
        orientation="h",
        title=f"Top {top_n} Players by {metric}",
        labels={metric: metric, "player_name": ""},
        color_discrete_sequence=[color],
    )
    fig.update_layout(height=420, yaxis={"categoryorder": "total ascending"})
    return fig
