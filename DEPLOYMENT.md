# Deployment Instructions

This guide walks you through deploying the Stock Analysis Platform to Vercel with GitHub Actions for daily model updates.

## Architecture Overview

- **GitHub Actions**: Runs model daily (cron) and saves results to `public/cached_results.json`
- **Vercel**: Hosts the static frontend (HTML/JS) that reads the JSON file
- **No server needed**: Everything is static or runs on GitHub Actions

---

## Step 1: Link Vercel to GitHub Repo

### 1.1 Push code to GitHub
Make sure all files are committed and pushed to `skp1008/Portfolio-Analytics`:
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 1.2 Connect Vercel to GitHub
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository: `skp1008/Portfolio-Analytics`
4. Configure project:
   - **Framework Preset**: Other (or leave default)
   - **Root Directory**: `./` (root)
   - **Build Command**: Leave empty (or `echo "No build needed"`)
   - **Output Directory**: `public`
   - **Install Command**: Leave empty
5. Click **"Deploy"**

### 1.3 Configure Vercel settings
After deployment, go to **Project Settings** → **General**:
- Ensure **Root Directory** is set correctly
- The `vercel.json` file will handle routing

**Note**: The frontend is now HTML/JS (not Streamlit). It fetches `/cached_results.json` from the public directory.

---

## Step 2: Setup GitHub Actions Workflow

### 2.1 Add FRED API Key to GitHub Secrets
1. Go to your GitHub repo: `https://github.com/skp1008/Portfolio-Analytics`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: `FRED_API_KEY`
5. Value: Your FRED API key (from `config.py`)
6. Click **"Add secret"**

### 2.2 Enable GitHub Actions
The workflow file is already created at `.github/workflows/daily_model_run.yml`

**The workflow will:**
- Run daily at 6 AM UTC (configurable in the cron)
- Install Python dependencies
- Run `run_model_github_actions.py`
- Save results to `public/cached_results.json`
- Commit and push the updated JSON file

### 2.3 Test the workflow manually
1. Go to **Actions** tab in your GitHub repo
2. Click on **"Daily Model Run"** workflow
3. Click **"Run workflow"** → **"Run workflow"** (manual trigger)
4. Wait ~5-6 minutes for it to complete
5. Check that `public/cached_results.json` was updated

### 2.4 Verify the workflow
- Check the **Actions** tab to see workflow runs
- The first run will create `public/cached_results.json`
- Subsequent runs will update it daily

---

## Step 3: Cron Setup (Already Configured)

The cron is **already set up** in the GitHub Actions workflow file:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
```

**To change the schedule:**
- Edit `.github/workflows/daily_model_run.yml`
- Modify the cron expression (use [crontab.guru](https://crontab.guru) for help)
- Examples:
  - `'0 0 * * *'` = Midnight UTC daily
  - `'0 12 * * *'` = Noon UTC daily
  - `'0 6 * * 1'` = 6 AM UTC every Monday

**The workflow automatically:**
1. Runs the model (takes ~5-6 minutes)
2. Saves results to `public/cached_results.json`
3. Commits and pushes the file
4. Vercel auto-deploys when it detects the push

---

## File Structure for Deployment

```
Portfolio-Analytics/
├── .github/
│   └── workflows/
│       └── daily_model_run.yml    # GitHub Actions workflow
├── public/
│   ├── index.html                 # Frontend HTML
│   ├── app.js                     # Frontend JavaScript
│   └── cached_results.json       # Model results (auto-generated)
├── model.py                       # Model code
├── run_model_github_actions.py    # Script for GitHub Actions
├── config.py                      # API keys (not committed)
├── requirements.txt               # Python dependencies
├── vercel.json                    # Vercel configuration
├── package.json                   # For Vercel build
└── README.md
```

---

## How It Works

1. **Daily at 6 AM UTC**: GitHub Actions runs the workflow
2. **Model Execution**: `run_model_github_actions.py` runs the model (~5-6 min)
3. **Save Results**: Results saved to `public/cached_results.json`
4. **Auto-commit**: Workflow commits and pushes the updated JSON
5. **Vercel Auto-deploy**: Vercel detects the push and redeploys
6. **Users See Latest**: Frontend fetches `/cached_results.json` and displays it

**No user waits**: The model runs in the background. Users always see the latest cached results instantly.

---

## Troubleshooting

### GitHub Actions fails
- Check **Actions** tab for error logs
- Verify `FRED_API_KEY` secret is set correctly
- Ensure `requirements.txt` has all dependencies
- Check that `run_model_github_actions.py` exists and is executable

### Vercel deployment fails
- Check Vercel build logs
- Ensure `vercel.json` is in the root
- Verify `public/index.html` exists
- Check that `package.json` exists (even if minimal)

### Frontend shows "Loading..." forever
- Check browser console for errors
- Verify `/cached_results.json` is accessible (visit `your-site.vercel.app/cached_results.json`)
- Ensure JSON file exists and is valid
- Check CORS headers in `vercel.json`

### Model results not updating
- Check GitHub Actions workflow ran successfully
- Verify `public/cached_results.json` was updated in the repo
- Check Vercel deployment logs for the latest deploy

---

## Next Steps

Once deployed:
1. Test the site: Visit your Vercel URL
2. Verify data loads: Check that charts and predictions appear
3. Wait for first daily run: Check GitHub Actions after 6 AM UTC
4. Monitor: Check Actions tab periodically to ensure runs succeed

---

## Integration with Main Portfolio Site

When ready to integrate into your main portfolio website:
1. Copy this folder into your main website directory
2. Update routing in your main site to point to `/portfolio-analytics` or similar
3. The `public/` folder contents can be served from a subdirectory
4. Update `app.js` fetch path if needed: `fetch('/portfolio-analytics/cached_results.json')`
