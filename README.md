# Stock Analysis Platform

A single-stock analysis system that uses gradient boosting models to predict stock price movements and displays results through a web dashboard.

## Features

- **Stock Prediction Model**: Gradient boosting model that predicts whether a stock will Rise, Fall, or remain Neutral
- **Interactive Dashboard**: Web-based dashboard with:
  - Movement history charts (1 day, 15 days, 1 month, 5 years, max)
  - Prediction pie chart (Rise/Fall/Neutral probabilities)
  - Action recommendation (BUY/HOLD/SHORT)
  - Model variables explanation
  - Economic conditions display
  - Market performance (S&P 500) chart
  - Backtest statistics and stock information

## Architecture

- **Frontend**: Static HTML/JS (served by Vercel)
- **Model**: Python/XGBoost (runs daily via GitHub Actions)
- **Data**: JSON file (`public/cached_results.json`) updated daily

## Local Development

### Run Locally (Streamlit version)

```bash
# Copy config and add your FRED API key
cp config.example.py config.py
# Edit config.py and set FRED_API_KEY

# Install dependencies
pip install -r requirements.txt

# Run launcher (uses cache if recent, otherwise runs model)
python launcher.py
```

### Run Model Only

```bash
python run_model_github_actions.py
```

Saves results to `public/cached_results.json`. For local runs, `config.py` with `FRED_API_KEY` is required (or set env var `FRED_API_KEY`).

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

**Quick Summary:**
1. Push code to GitHub (`skp1008/Portfolio-Analytics`)
2. Connect Vercel to the repo
3. Add `FRED_API_KEY` to GitHub Secrets
4. GitHub Actions runs daily and updates results
5. Vercel serves the static frontend

## Project Structure

```
├── public/
│   ├── index.html              # Web frontend
│   ├── app.js                  # Frontend JavaScript
│   └── cached_results.json     # Model results (auto-generated)
├── .github/
│   └── workflows/
│       └── daily_model_run.yml # GitHub Actions workflow
├── model.py                    # Model code
├── run_model_github_actions.py # Script for GitHub Actions
├── frontend.py                 # Streamlit frontend (local dev)
├── launcher.py                 # Local launcher
├── config.example.py           # Template for config (copy to config.py)
├── config.py                   # Local only, gitignored (FRED API key)
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel configuration
└── DEPLOYMENT.md              # Deployment guide
```

## Default Stocks

The system analyzes these stocks by default:
- NVDA, ORCL, THAR, SOFI, RR, RGTI

## Model Variables

The model uses four main categories of variables:

1. **Stock's Own History (AR1-like)**: Historical price movements, returns, momentum, volatility
2. **Overall Market Conditions**: S&P 500 (^GSPC) performance and volatility
3. **Industry Conditions**: Sector ETF performance (via market indicators)
4. **Economic Variables**: Interest rates, inflation (YoY), unemployment rate

## Notes

- Model runs take 5-6 minutes
- Results are cached and updated daily via GitHub Actions
- Frontend loads instantly by reading cached JSON
- For production, model runs once daily automatically
