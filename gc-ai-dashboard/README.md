# GC AI Dashboard

An AI-powered analytics dashboard for GameChanger baseball/softball stats.

## Features (MVP)

- Upload GameChanger CSV exports (team stats, player game logs)
- Automatic parsing and standardization of baseball metrics
- Interactive visualizations (trends, distributions, leaderboards)
- Smart AI-generated insights and summaries
- Support for multi-game / tournament analysis ("all games one day")

## Getting Started

### 1. Setup

```powershell
cd gc-ai-dashboard

# Create virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Dashboard

```powershell
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### If the app fails to load ("Failed to load")

1. Run the diagnostic script:
   ```powershell
   .\diagnose.bat
   ```

2. Make sure you're using the easier launcher:
   ```powershell
   .\start-app.bat
   ```

3. Common fixes:
   - Close any other Streamlit windows first
   - Try a different port: `streamlit run app.py --server.port 8502`
   - Restart your terminal completely
   - Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## How to See the Latest Changes (Testing Guide)

1. Run the app:
   ```powershell
   .\start-app.bat
   ```

2. Click **"Load Demo Season"**.

3. Look for these new sections (they appear right at the top after the demo loads):
   - **Coach / Scout Summary** — High-level takeaways and recommendations
   - **Opponent Scouting Report** — Team tendencies + suggested game plan

4. Scroll down to **Visualizations → 🎯 Spray Charts** tab to see the new hit location visuals (using mock 2026 Mariners data).

A blue info banner will appear at the top when using demo data to highlight what's new.

### 3. Using Real AI Insights (Recommended)

The dashboard works with smart rule-based insights by default.

For much richer, coach-style analysis powered by **Grok**:

1. Get a Grok API key at [https://x.ai/api](https://x.ai/api)
2. Paste it into the **"Grok API Key (xAI)"** field in the sidebar.

When a valid key is present, the Smart Insights section will automatically use Grok instead of the rule-based system. The tone is designed to sound like a real coach with data awareness.

## GameChanger Export Tips

- Preferred: Player Game Log or Team Batting/Pitching Stats CSV
- The parser is flexible — it will try to auto-detect common column names
- You can upload multiple CSVs for tournament / "all games one day" analysis

There's a sample file at `sample_data/sample_gamechanger_export.csv` you can use to test immediately.

## Roadmap

- [x] Real LLM insights using Grok (xAI)
- [x] Spray Charts (hit location visualization) - currently uses mock MLB data
- [x] Strong Coach / Scout Summary (high-value "money view")
- [x] Opponent Scouting Report with game-planning angles
- [ ] Pitching analysis section
- [ ] Player deep-dive profiles
- [ ] Robust support for real GameChanger export formats
- [ ] Natural language questions ("How has our cleanup hitter done lately?")
- [ ] Exportable PDF reports
- [ ] Multi-season support

---

Let's build this together. What's the first thing you'd like to add or improve?
