"""
GameChanger CSV Parser + Synthetic Data Generator

Handles real GameChanger exports and creates realistic demo data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import io


# Common column name mappings from various GameChanger exports
COLUMN_MAPPINGS = {
    "player_name": ["player", "player name", "name", "athlete", "batter"],
    "date": ["date", "game date", "gamedate"],
    "opponent": ["opponent", "vs", "opponent team", "team"],
    "AB": ["ab", "at bats", "at-bats", "atbats"],
    "H": ["h", "hits", "hit"],
    "2B": ["2b", "2b", "doubles", "double", "2b"],
    "3B": ["3b", "3b", "triples", "triple", "3b"],
    "HR": ["hr", "home runs", "homeruns", "home run"],
    "RBI": ["rbi", "runs batted in"],
    "BB": ["bb", "walks", "base on balls"],
    "SO": ["so", "strikeouts", "k", "strike outs"],
    "HBP": ["hbp", "hit by pitch"],
    "SF": ["sf", "sacrifice flies"],
    "SH": ["sh", "sacrifice hits", "bunts"],
    "R": ["r", "runs", "run"],
    "SB": ["sb", "stolen bases"],
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map whatever column names GameChanger gave us to our standard set."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    rename_map = {}
    for standard, variants in COLUMN_MAPPINGS.items():
        for col in df.columns:
            if col in variants:
                rename_map[col] = standard
                break

    df = df.rename(columns=rename_map)
    return df


def parse_gamechanger_csv(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Parse a GameChanger CSV export.
    Works with player game logs and many team stat exports.
    """
    try:
        # Read the file (handles both file-like and path)
        if hasattr(uploaded_file, "read"):
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="ignore")
            df = pd.read_csv(io.StringIO(content))
        else:
            df = pd.read_csv(uploaded_file)

        df = _normalize_columns(df)

        # Extra friendly renames for common export variations
        extra_renames = {"doubles": "2B", "triples": "3B", "double": "2B", "triple": "3B"}
        df = df.rename(columns={k: v for k, v in extra_renames.items() if k in df.columns})

        # Keep only rows that look like player stat rows
        required = ["player_name"]
        if not all(col in df.columns for col in required):
            # Try to find a reasonable player column
            possible_player_cols = [c for c in df.columns if "player" in c or "name" in c]
            if possible_player_cols:
                df = df.rename(columns={possible_player_cols[0]: "player_name"})
            else:
                return None

        # Convert numeric columns
        numeric_cols = ["AB", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "HBP", "SF", "R", "SB"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            else:
                df[col] = 0

        # Parse dates if present
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])
        else:
            # Synthesize dates if missing (assume sequential games)
            df["date"] = pd.date_range(end=datetime.now().date(), periods=len(df), freq="3D")

        # Clean player names
        df["player_name"] = df["player_name"].astype(str).str.strip()

        # Fill opponent if missing
        if "opponent" not in df.columns or df["opponent"].isna().all():
            opponents = ["Eagles", "Titans", "Warriors", "Knights", "Raptors", "Falcons"]
            df["opponent"] = np.random.choice(opponents, size=len(df))

        # Only keep rows with meaningful at-bats or clear player data
        df = df[df["AB"] + df["BB"] + df["SO"] > 0]

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"Parser error: {e}")
        return None


def generate_synthetic_baseball_data(num_games: int = 12, num_players: int = 14) -> pd.DataFrame:
    """
    Generate a realistic high school varsity baseball season dataset.
    Good for demoing the dashboard without real uploads.
    """
    np.random.seed(42)

    players = [
        "Alex Rivera", "Jordan Hale", "Tyler Brooks", "Marcus Chen",
        "Dylan Torres", "Ethan Park", "Liam Santos", "Noah Kim",
        "Caleb Wright", "Mason Reed", "Logan Hayes", "Jacob Cruz",
        "Lucas Bennett", "Ryan Morales"
    ][:num_players]

    # Positions / archetypes for more realistic stat distribution
    archetypes = {
        "power": {"avg": 0.265, "hr_rate": 0.048, "k_rate": 0.28},
        "contact": {"avg": 0.312, "hr_rate": 0.012, "k_rate": 0.14},
        "patient": {"avg": 0.278, "hr_rate": 0.022, "k_rate": 0.18},
        "speed": {"avg": 0.291, "hr_rate": 0.008, "k_rate": 0.19},
    }

    player_archetypes = {p: list(archetypes.keys())[i % 4] for i, p in enumerate(players)}

    rows = []
    start_date = datetime(2025, 3, 1)

    for game_num in range(num_games):
        game_date = start_date + timedelta(days=game_num * 3 + (1 if game_num % 4 == 0 else 0))
        opponent = ["Eagles", "Titans", "Warriors", "Knights", "Raptors", "Falcons", "Bulldogs"][game_num % 7]

        for player in players:
            arch = player_archetypes[player]
            params = archetypes[arch]

            # Simulate game performance
            ab = np.random.choice([2, 3, 4, 5], p=[0.1, 0.35, 0.4, 0.15])
            hits = np.random.binomial(ab, params["avg"] + np.random.uniform(-0.04, 0.05))

            # Extra base hits
            hr = 1 if np.random.random() < params["hr_rate"] * ab else 0
            doubles = np.random.binomial(max(0, hits - hr), 0.28)
            triples = 1 if (np.random.random() < 0.018 and hits - hr - doubles > 0) else 0

            singles = max(0, hits - doubles - triples - hr)
            rbi = max(0, min(hits + (1 if hr else 0), np.random.randint(0, 5)))
            bb = 1 if np.random.random() < 0.12 else 0
            so = np.random.binomial(ab, params["k_rate"])

            # Occasional big games
            if np.random.random() < 0.06:
                hits = min(ab, hits + np.random.randint(2, 4))
                hr = max(hr, 1 if np.random.random() < 0.6 else hr)

            rows.append({
                "player_name": player,
                "date": game_date,
                "opponent": opponent,
                "AB": int(ab),
                "H": int(hits),
                "2B": int(doubles),
                "3B": int(triples),
                "HR": int(hr),
                "RBI": int(rbi),
                "BB": int(bb),
                "SO": int(so),
                "HBP": 0,
                "SF": 0,
                "R": int(max(0, hits - 1 + np.random.randint(0, 2))),
                "SB": 1 if (arch == "speed" and np.random.random() < 0.35) else 0,
            })

    df = pd.DataFrame(rows)
    return df
