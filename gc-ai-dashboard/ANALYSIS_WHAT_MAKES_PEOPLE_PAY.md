# What’s Missing to Make Coaches & Scouts Pay?

## Current State (as of late May 2026)

The app has good bones:
- Clean UI
- Real Grok integration with good role-aware prompting
- Spray charts (mock)
- Basic Free/Pro gating
- Decent value messaging on landing

But it is still missing several things that would make a coach or scout actually pull out their credit card.

## What Would Make Someone Pay ($15/mo or $144/yr)

### 1. Clear Time Savings & Workflow Value (Highest Leverage)
Coaches and scouts are busy. They will pay for tools that save them 1–2 hours per week or per opponent.

**Missing right now:**
- A "Coach/Scout Summary" view that gives them the 5 things they actually care about in under 30 seconds (we just added a first version of this).
- Pre-built "Opponent Scouting Report" one-click output.
- "What should I do against this team?" recommendations.

### 2. Scouting-Specific Features
Your target audience includes people who scout opponents and players.

**High-value missing features:**
- Opponent spray charts + tendencies vs RHP/LHP
- Player comparison tools (side-by-side)
- "Watchlist" functionality
- Ability to upload multiple opponents and compare them

### 3. Longitudinal Value (Trends Over Time)
One of the biggest reasons people pay for tools is **tracking change**.

Current demo data is too short and flat. Real value comes from:
- "This player has raised his OBP 80 points over the last 6 weeks."
- Season-long trends
- Ability to save/upload multiple date ranges

### 4. Output That Can Be Shared
Coaches need to communicate with staff, parents, or players.

**Missing:**
- One-click nice PDF or Markdown export of the Coach Summary + key charts
- Ability to annotate insights

### 5. Trust & Credibility in the Demo
Right now the demo uses generic synthetic high school data + mock spray charts.

To convert better, the demo should feel like:
- "This is exactly what I would see if I uploaded my real team"
- Or use real public MLB data (as you suggested with the Mariners) so it feels credible.

### 6. "I Would Look Stupid Without This" Factor
The strongest conversion usually comes from FOMO + status.

Examples:
- "Other coaches in your league are already using this."
- "See what a scout wrote about your team last week."

---

## Recommendation on "Overall or Trends Tab in the Demo Spot"

**Yes — you need something like this urgently.**

The current flow after loading demo data is:
KPIs → Data Table → Visualizations (Trends, Leaderboards, etc.)

This is too low-level for a first-time coach/scout.

**What you should have instead (or in addition):**

A prominent **"Coach / Scout Summary"** or **"Quick Takeaways"** section that appears *first* after loading data.

It should answer:
- What is the biggest problem with this team/opponent right now?
- Who are the 2-3 players I need to pay attention to?
- What should I do differently in my next series?

We just added a first version of this (see `src/viz/coach_summary.py`). It is a big step in the right direction.

### Suggested Next Priorities (in rough order)

1. **Polish the new Coach Summary view** — make it the hero of the demo experience.
2. Add 1-2 more high-signal "scout" views (e.g. simple opponent comparison or hot/cold players).
3. Make the demo data feel more real (use real Mariners 2026 stats + generated tendencies instead of pure synthetic).
4. Add fake but nice **Export Report** button on the Coach Summary (even if it just downloads a markdown file for now).
5. Improve the "Why Pro?" messaging with concrete time savings ("Save 45-90 minutes per opponent").

---

## Bottom Line

People will pay when they feel:
- "This saves me real time"
- "This helps me make better decisions than my competitors"
- "I can see the value in the first 60 seconds of using it"

Right now the tool has potential, but the demo experience still requires the user to do too much work to discover the value. Adding a strong, opinionated **Coach/Scout Summary** view (which we started) is probably the single highest-leverage thing we can do next.

The pricing page and value messaging are already much better than they were two weeks ago. The gap is now mostly in the *demo experience itself* showing immediate, undeniable value.