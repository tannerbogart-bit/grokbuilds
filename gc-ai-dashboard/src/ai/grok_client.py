"""
Grok (xAI) Client for GC AI Dashboard

Handles real LLM-powered insights using Grok via the OpenAI-compatible API.
"""

from openai import OpenAI
from typing import Optional
import pandas as pd
import os


GROK_BASE_URL = "https://api.x.ai/v1"
DEFAULT_MODEL = "grok-3"   # or "grok-3-mini" if you want faster/cheaper responses


def get_grok_client(api_key: str) -> Optional[OpenAI]:
    """Create and return a Grok client if the key looks valid."""
    if not api_key or len(api_key.strip()) < 10:
        return None

    try:
        client = OpenAI(
            api_key=api_key.strip(),
            base_url=GROK_BASE_URL,
        )
        return client
    except Exception:
        return None


def generate_grok_insights(
    df: pd.DataFrame,
    api_key: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 900
) -> Optional[str]:
    """
    Generate coach-style insights using Grok.

    Returns a markdown-formatted string of insights, or None if it fails.
    """
    client = get_grok_client(api_key)
    if client is None:
        return None

    # Build a compact but useful data summary for the prompt
    summary = _build_data_summary(df)

    system_prompt = """You are an experienced high school baseball coach who also understands advanced stats.

Tone & Style:
- Direct, honest, and practical — like a coach talking in the dugout.
- Use specific numbers. Call out real trends (hot streaks, cold streaks, improvement/decline).
- Be encouraging when earned, blunt when needed. No fluff.

Required Structure — use these exact headings:

## Team Trends
## Standout Players
## Concerns & Opportunities
## Recommendations

Keep every section short and tight. Focus heavily on trends.

Example of the style and structure I want:

## Team Trends
The top of the order has been carrying us. As a group we're hitting .312 over the last 5 games, up from .241 on the season. The bottom 4 hitters are still pressing — only 6 hits in their last 28 at-bats.

## Standout Players
**Tyler Brooks** has turned it around — 9 hits in his last 14 ABs with a .429 AVG over the past 4 games. **Marcus Chen** is ice cold right now, 1-for-19 in his last 5 games.

## Concerns & Opportunities
We're striking out 28% of the time as a team, and that number jumps to 41% with runners in scoring position. Walk rate is solid at 11%, but we're not doing enough damage on pitches in the zone.

## Recommendations
Get the bottom half of the lineup more aggressive early in counts. Tyler and Alex should see more pitches in RBI situations right now.

Use this exact style: short paragraphs, specific numbers, clear trends, coach voice."""

    user_prompt = f"""Here is a baseball dataset from GameChanger exports.

{summary}

Analyze the data and produce insights using the exact section structure I specified. 
Be specific with numbers and player names. Sound like a real coach who knows the game and the stats."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        raw_output = response.choices[0].message.content.strip()
        return post_process_grok_output(raw_output)

    except Exception as e:
        # Return None so the app can fall back gracefully
        print(f"Grok API error: {e}")
        return None


def ask_quick_question(df: pd.DataFrame, question: str, role: str) -> str:
    """
    Basic Quick Q's feature.
    Allows players and coaches to ask natural language questions about the data.
    """
    client = get_grok_client(os.environ.get("GROK_API_KEY", ""))
    if client is None:
        return "Please add a valid Grok API key in the sidebar to use Quick Q's."

    if not question or not question.strip():
        return "Please enter a question."

    # Build context
    data_summary = _build_data_summary(df)

    role = role.lower().strip()

    if role == "player":
        system_prompt = """You are a direct, honest baseball coach talking to a player.

Rules:
- Keep answers short and simple (2-5 sentences max).
- Be encouraging when the data supports it, but honest.
- Focus only on the individual player.
- Use actual numbers from the data.
- No long explanations or advice unless asked."""
    else:  # coach
        system_prompt = """You are a direct, analytical baseball coach talking to another coach.

Rules:
- Keep answers short and simple (2-5 sentences max).
- Be straightforward and analytical.
- Focus on team patterns, trends, and what the numbers actually show.
- Use specific data and percentages.
- Avoid fluff or motivational language."""

    user_prompt = f"""Dataset summary:
{data_summary}

Question from a {role}:
{question}

Answer in 2-5 short sentences using the actual data. Be direct."""

    try:
        response = client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=600,
            temperature=0.6,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Grok Quick Q error: {e}")
        return "Sorry, there was an error getting a response from Grok. Please try again."


def _build_data_summary(df: pd.DataFrame) -> str:
    """Create a data summary optimized for trend analysis (coaches & players)."""
    lines = []

    if "date" not in df.columns:
        df = df.copy()
        df["date"] = pd.date_range(end=pd.Timestamp.today(), periods=len(df), freq="D")

    games = df["date"].nunique()
    players = df["player_name"].nunique() if "player_name" in df.columns else "Unknown"

    total_ab = int(df.get("AB", pd.Series([0])).sum())
    total_hits = int(df.get("H", pd.Series([0])).sum())
    team_avg = total_hits / total_ab if total_ab > 0 else 0

    total_hr = int(df.get("HR", pd.Series([0])).sum())
    total_rbi = int(df.get("RBI", pd.Series([0])).sum())
    total_bb = int(df.get("BB", pd.Series([0])).sum())
    total_so = int(df.get("SO", pd.Series([0])).sum())

    lines.append(f"Games: {games} | Players: {players}")
    lines.append(f"Season: {total_hits}H / {total_ab}AB = {team_avg:.3f} AVG | {total_hr} HR | {total_rbi} RBI | {total_so} K | {total_bb} BB")

    if "player_name" not in df.columns:
        return "\n".join(lines)

    # Full season stats per player
    player_stats = (
        df.groupby("player_name")
        .agg({"AB": "sum", "H": "sum", "HR": "sum", "RBI": "sum", "BB": "sum", "SO": "sum"})
        .reset_index()
    )
    player_stats["AVG"] = player_stats.apply(lambda r: r["H"] / r["AB"] if r["AB"] > 0 else 0, axis=1)

    # === Recent form (last 3-5 games per player) ===
    recent_stats = []
    sorted_dates = sorted(df["date"].unique())

    for player in player_stats["player_name"].unique():
        player_games = df[df["player_name"] == player].sort_values("date")
        recent = player_games.tail(5)  # last 5 games

        if len(recent) >= 3:
            r_ab = recent["AB"].sum()
            r_h = recent["H"].sum()
            r_hr = recent.get("HR", pd.Series([0])).sum()
            r_avg = r_h / r_ab if r_ab > 0 else 0

            season_row = player_stats[player_stats["player_name"] == player].iloc[0]
            season_avg = season_row["AVG"]

            trend = ""
            if r_ab >= 6:
                diff = r_avg - season_avg
                if diff > 0.080:
                    trend = "HOT"
                elif diff < -0.080:
                    trend = "COLD"
                else:
                    trend = "steady"

            recent_stats.append({
                "player": player,
                "recent_ab": r_ab,
                "recent_avg": r_avg,
                "season_avg": season_avg,
                "trend": trend,
                "recent_hr": r_hr
            })

    if recent_stats:
        lines.append("\nRecent Form (last ~5 games vs season):")
        for r in sorted(recent_stats, key=lambda x: x["recent_avg"], reverse=True)[:8]:
            diff = r["recent_avg"] - r["season_avg"]
            diff_str = f"+{diff:.3f}" if diff > 0 else f"{diff:.3f}"
            trend_label = f" [{r['trend']}]" if r["trend"] in ["HOT", "COLD"] else ""
            lines.append(
                f"- {r['player']}: {r['recent_avg']:.3f} ({int(r['recent_ab'])} AB) vs season {r['season_avg']:.3f} ({diff_str}){trend_label}"
            )

    # Top / bottom performers (season)
    qualified = player_stats[player_stats["AB"] >= 8]
    if not qualified.empty:
        top = qualified.nlargest(3, "AVG")
        low = qualified.nsmallest(3, "AVG")

        lines.append("\nSeason Leaders (min 8 AB):")
        for _, row in top.iterrows():
            lines.append(f"+ {row['player_name']}: {row['AVG']:.3f} ({int(row['H'])}H, {int(row['HR'])}HR)")

        lines.append("Struggling:")
        for _, row in low.iterrows():
            lines.append(f"- {row['player_name']}: {row['AVG']:.3f} ({int(row['H'])}H)")

    # Raw recent game logs (most important for trend detection)
    lines.append("\nMost recent game logs (newest first):")
    recent_logs = df.sort_values("date", ascending=False).head(18)
    cols = ["player_name", "date", "AB", "H", "HR", "RBI", "BB", "SO"]
    available = [c for c in cols if c in recent_logs.columns]
    lines.append(recent_logs[available].to_string(index=False))

    return "\n".join(lines)


def post_process_grok_output(text: str) -> str:
    """
    Clean and standardize Grok's output for coaches and players.
    Focus: readability, consistency, and trend visibility.
    """
    if not text or not text.strip():
        return text

    lines = text.strip().split("\n")
    cleaned = []
    seen_sections = set()

    # Expected sections (in order)
    expected_sections = [
        "## Team Trends",
        "## Standout Players",
        "## Concerns & Opportunities",
        "## Recommendations"
    ]

    for line in lines:
        stripped = line.strip()

        # Normalize headings
        if stripped.lower().startswith("## team"):
            cleaned.append("## Team Trends")
            seen_sections.add("## Team Trends")
            continue
        if stripped.lower().startswith("## standout"):
            cleaned.append("## Standout Players")
            seen_sections.add("## Standout Players")
            continue
        if stripped.lower().startswith("## concern"):
            cleaned.append("## Concerns & Opportunities")
            seen_sections.add("## Concerns & Opportunities")
            continue
        if stripped.lower().startswith("## recommend"):
            cleaned.append("## Recommendations")
            seen_sections.add("## Recommendations")
            continue

        # Remove very repetitive or empty lines
        if stripped and not stripped.startswith("#"):
            cleaned.append(line.rstrip())

    # Add any missing sections (gracefully)
    for section in expected_sections:
        if section not in seen_sections:
            cleaned.append(f"\n{section}")
            cleaned.append("_No clear signal in this area._")

    # Final cleanup
    result = "\n".join(cleaned).strip()

    # Make sure we don't have too many blank lines
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")

    return result
