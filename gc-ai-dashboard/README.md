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

### 3. Using Real AI Insights (Optional)

The dashboard works great with rule-based insights out of the box.

For LLM-powered insights:

1. Get an API key from [xAI (Grok)](https://x.ai/api) or OpenAI
2. Set it in the sidebar or create a `.env` file:

```env
AI_PROVIDER=xai          # or "openai"
AI_API_KEY=your-key-here
```

## GameChanger Export Tips

- Preferred: Player Game Log or Team Batting/Pitching Stats CSV
- The parser is flexible — it will try to auto-detect common column names
- You can upload multiple CSVs for tournament / "all games one day" analysis

There's a sample file at `sample_data/sample_gamechanger_export.csv` you can use to test immediately.

## Roadmap

- [ ] Robust GameChanger parser for hitting + pitching
- [ ] Multi-file upload + date filtering
- [ ] Player comparison tools
- [ ] Real LLM insights (Grok / OpenAI)
- [ ] Exportable reports
- [ ] Pitching / Fielding analysis sections

---

Let's build this together. What's the first thing you'd like to add or improve?
