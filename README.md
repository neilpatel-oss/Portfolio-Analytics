# Stock Analysis Platform

A stock analysis system that uses gradient boosting models to predict stock price movements and displays results through a static web dashboard.

## Architecture

**Two separate systems:**

1. **Model Execution (GitHub Actions)**
   - Runs daily at midnight (cron) or manually via workflow_dispatch
   - Executes `run_model_github_actions.py` which calls `model.py`
   - Saves results to `public/cached_results.json`
   - Commits and pushes the updated JSON file

2. **Frontend (Vercel)**
   - Static HTML/JS site served from `public/` directory
   - **Only reads** `public/cached_results.json` - never runs the model
   - Displays predictions, charts, and metrics
   - Updates automatically when GitHub Actions commits new data

**No server needed** - everything is static or runs on GitHub Actions.

## Project Structure

```
├── public/                          # Frontend (deployed to Vercel)
│   ├── index.html                  # Web frontend
│   ├── app.js                      # Frontend JavaScript (reads JSON only)
│   └── cached_results.json         # Model results (auto-updated by GitHub Actions)
├── .github/
│   └── workflows/
│       └── daily_model_run.yml     # GitHub Actions workflow (runs model daily)
├── model.py                        # Model code (used by GitHub Actions)
├── run_model_github_actions.py     # Script for GitHub Actions (runs model, saves JSON)
├── config.example.py               # Template for config (copy to config.py locally)
├── requirements.txt                # Python dependencies (for GitHub Actions)
├── vercel.json                     # Vercel configuration
├── package.json                    # Minimal package.json for Vercel
└── DEPLOYMENT.md                   # Complete deployment guide
```

## Local Development

### Run Model Locally

```bash
# Copy config template
cp config.example.py config.py
# Edit config.py and add your FRED_API_KEY

# Install dependencies
pip install -r requirements.txt

# Run model (saves to public/cached_results.json)
python run_model_github_actions.py
```

### View Frontend Locally

```bash
# Serve the public/ directory with any static server
cd public
python -m http.server 8000
# Open http://localhost:8000
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions.

**Quick Summary:**
1. Push code to GitHub
2. Connect Vercel to the repo (serves `public/` directory)
3. Add `FRED_API_KEY` to GitHub Secrets
4. GitHub Actions runs daily and updates `public/cached_results.json`
5. Vercel auto-deploys when the JSON file is updated

## Default Stocks

The system analyzes these stocks:
- NVDA, ORCL, THAR, SOFI, RR, RGTI

## Model Variables

The model uses four main categories:
1. **Stock History**: Historical price movements, returns, momentum, volatility
2. **Market Conditions**: S&P 500 (^GSPC) performance and volatility
3. **Industry Conditions**: Sector ETF performance
4. **Economic Variables**: Interest rates, inflation (YoY), unemployment rate

## Notes

- Model runs take 5-6 minutes
- Results are cached in `public/cached_results.json`
- Frontend loads instantly by reading the cached JSON file
- Model runs automatically daily via GitHub Actions cron
- Frontend never executes Python or runs the model - it only displays the JSON data
