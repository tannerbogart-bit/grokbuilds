"""
Spray Chart Visualization for GC AI Dashboard

Generates mock hit location data and renders interactive spray charts.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Mock Seattle Mariners 2026 roster with realistic spray tendencies
# Based on typical MLB player profiles (pull-heavy power hitters, opposite-field contact hitters, etc.)
MOCK_MARINERS_PLAYERS = {
    "Julio Rodriguez": {"hand": "R", "pull": 0.42, "center": 0.35, "opposite": 0.23, "hr_pull": 0.65},
    "Josh Naylor":     {"hand": "L", "pull": 0.38, "center": 0.37, "opposite": 0.25, "hr_pull": 0.55},
    "Randy Arozarena": {"hand": "R", "pull": 0.48, "center": 0.32, "opposite": 0.20, "hr_pull": 0.72},
    "Cole Young":      {"hand": "L", "pull": 0.30, "center": 0.42, "opposite": 0.28, "hr_pull": 0.40},
    "J.P. Crawford":   {"hand": "L", "pull": 0.28, "center": 0.38, "opposite": 0.34, "hr_pull": 0.35},
    "Cal Raleigh":     {"hand": "R", "pull": 0.55, "center": 0.30, "opposite": 0.15, "hr_pull": 0.80},
    "Luke Raley":      {"hand": "L", "pull": 0.45, "center": 0.33, "opposite": 0.22, "hr_pull": 0.68},
    "Dominic Canzone": {"hand": "L", "pull": 0.35, "center": 0.40, "opposite": 0.25, "hr_pull": 0.50},
}


def generate_mock_spray_data(player_name: str, num_at_bats: int = 80) -> pd.DataFrame:
    """
    Generate synthetic batted ball locations for a player.
    Returns a DataFrame with x, y coordinates on a baseball field.
    """
    if player_name not in MOCK_MARINERS_PLAYERS:
        player_name = "Julio Rodriguez"  # fallback

    profile = MOCK_MARINERS_PLAYERS[player_name]
    hand = profile["hand"]

    # Generate hit locations based on tendencies
    locations = []
    for _ in range(num_at_bats):
        r = np.random.random()

        if r < profile["pull"]:
            direction = "pull"
            angle = np.random.normal(30 if hand == "R" else -30, 18)  # degrees from center
        elif r < profile["pull"] + profile["center"]:
            direction = "center"
            angle = np.random.normal(0, 12)
        else:
            direction = "opposite"
            angle = np.random.normal(-30 if hand == "R" else 30, 18)

        # Distance (roughly 100-400 feet)
        distance = np.random.beta(2, 1.8) * 320 + 80

        # Convert to x/y (home plate at (0,0), left field negative x for righties)
        rad = np.radians(90 - angle)  # rotate so 0° is straight up (center field)
        x = distance * np.cos(rad)
        y = distance * np.sin(rad)

        # Add some noise
        x += np.random.normal(0, 8)
        y += np.random.normal(0, 8)

        is_hr = np.random.random() < 0.12  # ~12% HR rate in mock

        locations.append({
            "player": player_name,
            "x": x,
            "y": y,
            "direction": direction,
            "distance": distance,
            "is_home_run": is_hr
        })

    return pd.DataFrame(locations)


def create_spray_chart(df: pd.DataFrame, player_name: str = None, title: str = None) -> go.Figure:
    """
    Create an interactive spray chart using Plotly.
    """
    if player_name:
        plot_df = df[df["player"] == player_name].copy()
    else:
        plot_df = df.copy()

    if plot_df.empty:
        plot_df = generate_mock_spray_data("Julio Rodriguez")

    fig = go.Figure()

    # Draw simple baseball field (grass + foul lines)
    # Infield diamond
    fig.add_shape(type="path",
                  path="M 0,0 L -90,90 L 0,180 L 90,90 Z",
                  fillcolor="rgba(144, 238, 144, 0.3)",
                  line=dict(color="#2E8B57", width=2))

    # Outfield arc (approximate)
    fig.add_shape(type="circle",
                  x0=-220, y0=-20, x1=220, y1=420,
                  fillcolor="rgba(144, 238, 144, 0.15)",
                  line=dict(color="#228B22", width=2))

    # Foul lines
    fig.add_trace(go.Scatter(x=[0, -220], y=[0, 400],
                             mode='lines', line=dict(color="white", width=2),
                             showlegend=False))
    fig.add_trace(go.Scatter(x=[0, 220], y=[0, 400],
                             mode='lines', line=dict(color="white", width=2),
                             showlegend=False))

    # Home plate marker
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers',
                             marker=dict(size=12, color="white", symbol="diamond"),
                             showlegend=False))

    # Plot hits
    colors = {"pull": "#FF6B6B", "center": "#4ECDC4", "opposite": "#45B7D1"}

    for direction in ["pull", "center", "opposite"]:
        dir_df = plot_df[plot_df["direction"] == direction]
        if not dir_df.empty:
            fig.add_trace(go.Scatter(
                x=dir_df["x"],
                y=dir_df["y"],
                mode='markers',
                name=direction.capitalize(),
                marker=dict(
                    size=7,
                    color=colors[direction],
                    opacity=0.75,
                    line=dict(width=0.5, color="white")
                ),
                hovertemplate=f"<b>{direction.capitalize()}</b><br>Distance: %{{customdata[0]:.0f}} ft<extra></extra>",
                customdata=dir_df[["distance"]].values
            ))

    # Home runs as bigger markers
    hr_df = plot_df[plot_df["is_home_run"]]
    if not hr_df.empty:
        fig.add_trace(go.Scatter(
            x=hr_df["x"],
            y=hr_df["y"],
            mode='markers',
            name="Home Runs",
            marker=dict(size=11, color="gold", symbol="star", line=dict(width=1, color="black")),
            hovertemplate="HOME RUN<br>Distance: %{customdata[0]:.0f} ft<extra></extra>",
            customdata=hr_df[["distance"]].values
        ))

    fig.update_layout(
        title=title or f"Spray Chart - {player_name or 'Team'} (Mock Data)",
        xaxis=dict(range=[-250, 250], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-30, 420], showgrid=False, zeroline=False, showticklabels=False),
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor="#1a3a1a",   # dark green grass feel
        paper_bgcolor="#0f2a0f"
    )

    # Add field labels
    fig.add_annotation(x=-180, y=380, text="Left Field", showarrow=False, font=dict(color="white", size=11))
    fig.add_annotation(x=180, y=380, text="Right Field", showarrow=False, font=dict(color="white", size=11))
    fig.add_annotation(x=0, y=400, text="Center", showarrow=False, font=dict(color="white", size=11))

    return fig


def get_player_spray_summary(player_name: str) -> dict:
    """Return summary stats for a player's spray tendencies."""
    if player_name not in MOCK_MARINERS_PLAYERS:
        player_name = list(MOCK_MARINERS_PLAYERS.keys())[0]

    p = MOCK_MARINERS_PLAYERS[player_name]
    return {
        "player": player_name,
        "pull_pct": round(p["pull"] * 100),
        "center_pct": round(p["center"] * 100),
        "opposite_pct": round(p["opposite"] * 100),
        "pull_hr_tendency": round(p["hr_pull"] * 100),
    }


def generate_team_spray_data(handedness: str = "All", num_at_bats_per_player: int = 40) -> pd.DataFrame:
    """
    Generate team-level spray data, optionally filtered by handedness.
    handedness can be: "All", "Right", "Left"
    """
    all_data = []

    for player, profile in MOCK_MARINERS_PLAYERS.items():
        if handedness == "Right" and profile["hand"] != "R":
            continue
        if handedness == "Left" and profile["hand"] != "L":
            continue

        player_data = generate_mock_spray_data(player, num_at_bats=num_at_bats_per_player)
        all_data.append(player_data)

    if not all_data:
        return generate_mock_spray_data("Julio Rodriguez", num_at_bats=60)

    return pd.concat(all_data, ignore_index=True)


def create_team_spray_chart(df: pd.DataFrame, title: str = "Team Spray Chart") -> go.Figure:
    """Create a team spray chart, colored by handedness."""
    fig = go.Figure()

    # Draw baseball field background
    fig.add_shape(type="path",
                  path="M 0,0 L -90,90 L 0,180 L 90,90 Z",
                  fillcolor="rgba(144, 238, 144, 0.25)",
                  line=dict(color="#2E8B57", width=2))

    fig.add_shape(type="circle",
                  x0=-220, y0=-20, x1=220, y1=420,
                  fillcolor="rgba(144, 238, 144, 0.12)",
                  line=dict(color="#228B22", width=2))

    # Foul lines
    fig.add_trace(go.Scatter(x=[0, -220], y=[0, 400], mode='lines',
                             line=dict(color="#444", width=1.5), showlegend=False))
    fig.add_trace(go.Scatter(x=[0, 220], y=[0, 400], mode='lines',
                             line=dict(color="#444", width=1.5), showlegend=False))

    # Plot by handedness
    for hand, color in [("R", "#FF6B6B"), ("L", "#4ECDC4")]:
        hand_df = df[df["player"].map(lambda p: MOCK_MARINERS_PLAYERS.get(p, {}).get("hand") == hand)]
        if not hand_df.empty:
            fig.add_trace(go.Scatter(
                x=hand_df["x"],
                y=hand_df["y"],
                mode='markers',
                name=f"{'Right' if hand == 'R' else 'Left'}-handed",
                marker=dict(size=6, color=color, opacity=0.7),
                hovertemplate="%{text}<extra></extra>",
                text=hand_df["player"]
            ))

    fig.update_layout(
        title=title,
        xaxis=dict(range=[-250, 250], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-30, 420], showgrid=False, zeroline=False, showticklabels=False),
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="#1a3a1a",
        paper_bgcolor="#0f2a0f"
    )

    fig.add_annotation(x=-180, y=380, text="Left Field", showarrow=False, font=dict(color="white", size=10))
    fig.add_annotation(x=180, y=380, text="Right Field", showarrow=False, font=dict(color="white", size=10))

    return fig