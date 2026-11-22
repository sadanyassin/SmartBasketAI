# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

The MVP is built (Streamlit app, calculations, validation, scenarios, AI explanation component, tests). It is not yet pushed to GitHub, and has not been user-tested.

### Commands (Windows, PowerShell; Python 3.12 in `.venv`)
- Setup once: `python -m venv .venv` then `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
- Run the app: `.\.venv\Scripts\python.exe -m streamlit run app.py` (opens http://localhost:8501)
- Run tests: `.\.venv\Scripts\python.exe -m pytest -q`
- AI key: `ANTHROPIC_API_KEY` in `.streamlit/secrets.toml` (git-ignored; copy from `secrets.toml.example`) or as an environment variable. Never commit a key.

### Layout
`core/` business logic with no Streamlit (models, calculations in Decimal, validation, scenarios, basket_io, catalog) · `ai/` (payload, prompt, llm_client, fallback) · `ui/` (one module per tab) · `data/demo_catalog.csv` · `tests/`. The AI provider in `ai/llm_client.py` is provisional (Anthropic SDK, model overridable by `SMARTBASKET_LLM_MODEL`) until the lecturer approves a service.

The source of truth is the product spec (Hebrew, v2.0) that the team supplied. This file condenses the parts that constrain the code.

## Who you are working with

The team is three students with little programming background, working on a course project. Act as technical PM, systems analyst and development mentor:
- Work in small, incremental steps. Present decisions, alternatives and risks. Explain code simply. Propose tests for every calculation.
- **Do not build the whole app before the team brings the lecturer's weekly task.** Do not expand the MVP without explicit approval.
- When a critical decision is missing, ask **one focused question at a time** and challenge unfounded assumptions ("grill me").
- At the end of each stage, summarize: what was decided, what was actually done, what is still open.
- Never fabricate test results, business data or usage/user-testing results.
- Speak Hebrew with the team.

## Product in one paragraph

A Hebrew-language desktop web app for owners of small Israeli neighborhood groceries. It simulates the **contribution margin of a single customer purchase (one basket)**. Inputs are buy price, sell price, quantity, spoilage (פחת) and credit card fees. The app compares a base scenario with an alternative one and adds a short AI-generated Hebrew explanation of the results that Python has already computed.

## UI/UX design (Stitch)

The UI mockups live in a Google Stitch project: **"SmartBasket AI", id `3544294369882181384`**. Use the Stitch MCP to access it. It holds a design system (Rubik, green primary, RTL, with semantic profit/break-even/loss colors and data-certainty chips) and 4 desktop screens that map to the app's tabs:
- Home `0b66375cc57441628554b9f77f865083`
- Build basket `df778ffdb4e343478a9795701bc6ac19` (the other two "בניית סל" screens are discarded drafts)
- Results & simulation `a7c8b104179e45f69cef25399b126918`
- AI explanation `192b88748ece48479111c1115915807f`

Fixes were applied as Stitch edits. Files downloaded via `download_file` may still show the pre-edit version, so check them against the rules in this file before reusing any text. All mockups use the same demo basket: bread 4.20→6.00 ×1 at 5% spoilage; milk 5.10→6.50 ×2 at 0%; tomatoes 6.00→9.00 ×2 at 20%; credit fee 1.5% + 0.50. That gives R = 37.00, K = 29.62, fee = 1.06, P = 6.32 and R* = 30.58. The alternative scenario (tomato spoilage cut to 10%) gives K = 27.95, P = 7.99 and R* = 28.89. Use the same numbers as a second test case.

## Planned stack (final choice subject to the lecturer)

Python · Streamlit (UI, screens as tabs in one app) · Pandas · Plotly · local CSV/JSON for demo data · Git/GitHub · an LLM through a course-approved connection. There is no database, no user accounts and no public deployment in the MVP.

## Domain model and invariants (must hold in code)

- **Basket = one customer transaction at the register.** It is not a day's or a week's sales. A basket has one payment method (cash or credit).
- All prices and fees are **excluding VAT**. Rent, wages, taxes and other opex are out of scope.
- **Spoilage** is a periodic estimate built into the cost of the units sold. Never charge it again as a separate line, because that double-counts it.
- The **fixed credit fee F is charged once per basket**, never per item.
- Label the result **"רווח תרומתי משוער" (estimated contribution margin)**, never net profit.

### Formulas
- Revenue: `R = Σ sell_price_i × qty_i`
- Effective unit cost: `C_i / (1 − d_i)`, where `0 ≤ d_i < 1`; basket cost `K = Σ C_i/(1−d_i) × qty_i`
- Fee: credit → `R × r + F`; cash → `0`
- Contribution: `P = R − K − fee`
- Break-even revenue (fixed mix and quantity): credit → `R* = (K + F) / (1 − r)` (requires `r < 1`); cash → `R* = K`

### Reference test case (must pass, rounded to 2 decimals)
Fresh product: buy 6 ₪, sell 9 ₪, qty 2, spoilage 20%, credit fee 1.5% + 0.50 ₪.
→ R = 18.00, K = 15.00, fee = 0.77, P = 2.23, R* ≈ 15.74.

The target is ≥ 12 test cases, including invalid input and edge cases, all passing.

## Data provenance and validation

- Every input value carries a certainty tag: **"הוזן" (entered) / "הערכה" (estimate) / "הדגמה" (demo)**. Show it next to the value. Never present an estimate as fact.
- A missing buy price means **no profit is computed for that item**. Show the gap instead of making up a number. Only demo mode may show a simulated price, and it must be marked as demo.
- A missing sell price must be filled in before the calculation runs. Quantity must be positive. Spoilage must be in `[0, 1)`. Invalid or missing values must never pass silently into a calculation.
- The example spoilage defaults by category (fresh 10%, shelf 0%) are **illustrative only**. They are not verified industry data, so label them that way.
- The demo catalog holds 10–15 mock products.

## AI explanation component (required in the MVP)

- The model receives **only values Python has already computed**: revenue, costs, fee, profit, the delta between scenarios, and the list of fields that are estimates. Send no personal or customer data.
- The model must not recompute profit, invent market prices, forecast demand or promise profit.
- Output is 2–3 Hebrew sentences. It names the main driver of the result and suggests **one** change to test (not claimed to be good in every case), and it states the limits of the estimate.
- If the model is unavailable, show a clear message, or a rule-based explanation **visibly labeled as not AI**. Never pass rule-based text off as AI output.

## MVP scope

**In:** demo catalog and editing of prices and quantities; cash/credit with a per-basket fee; known or estimated spoilage; profit/loss, break-even, input validation, a before/after chart and a loss/break-even/profit indicator; sliders for price and spoilage; the AI explanation.

**Out (needs approval):** saving baskets over time, multi-basket comparison, report export, advanced sensitivity analysis, smart recommendations, POS/real-time sales, inventory, payments processing, suppliers/customers, accounting, demand forecasting, "optimal pricing". In the MVP, "optimization" means comparing scenarios only.

**Open decisions:** which AI service to use and how to connect to it, persistence between runs, export, public hosting, extra cost types.
