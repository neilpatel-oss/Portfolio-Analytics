# Complete Setup Instructions

## Overview

This document provides step-by-step instructions for:
1. Linking Vercel to GitHub repo
2. Setting up GitHub Actions workflow
3. Configuring cron schedule

---

## PART 1: Link Vercel to GitHub Repo

### Step 1.1: Prepare and Push Code

1. **Commit all changes:**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Verify files are pushed:**
   - Check GitHub repo: `https://github.com/skp1008/Portfolio-Analytics`
   - Ensure these files exist:
     - `public/index.html`
     - `public/app.js`
     - `vercel.json`
     - `package.json`
     - `.github/workflows/daily_model_run.yml`

### Step 1.2: Connect Vercel

1. **Go to Vercel:**
   - Visit [vercel.com](https://vercel.com)
   - Sign in with GitHub

2. **Import Project:**
   - Click **"Add New Project"** or **"Import Project"**
   - Select **"Import Git Repository"**
   - Find and select: `skp1008/Portfolio-Analytics`
   - Click **"Import"**

3. **Configure Project Settings:**
   - **Framework Preset**: Select **"Other"** (or leave as default)
   - **Root Directory**: `./` (leave as root)
   - **Build Command**: Leave **empty** (or type: `echo "No build needed"`)
   - **Output Directory**: `public`
   - **Install Command**: Leave **empty**

4. **Environment Variables (if needed):**
   - For now, skip (we'll add FRED_API_KEY to GitHub Secrets, not Vercel)

5. **Deploy:**
   - Click **"Deploy"**
   - Wait for deployment to complete (~1-2 minutes)

6. **Verify Deployment:**
   - Visit your Vercel URL (e.g., `portfolio-analytics-xxx.vercel.app`)
   - You should see "Loading data..." (this is expected - no JSON file yet)

### Step 1.3: Update Vercel Settings (if needed)

After first deployment:
1. Go to **Project Settings** → **General**
2. Verify:
   - **Root Directory**: `./`
   - **Output Directory**: `public`
   - **Build Command**: Empty or `echo "No build needed"`

**Note:** The frontend is now **HTML/JS** (not Streamlit). It fetches `/cached_results.json` from the public directory. The `vercel.json` file handles routing.

---

## PART 2: Setup GitHub Actions Workflow

### Step 2.1: Add FRED API Key to GitHub Secrets

1. **Go to your GitHub repo:**
   - Visit: `https://github.com/skp1008/Portfolio-Analytics`

2. **Navigate to Secrets:**
   - Click **"Settings"** tab (top menu)
   - Click **"Secrets and variables"** → **"Actions"** (left sidebar)

3. **Add Secret:**
   - Click **"New repository secret"**
   - **Name**: `FRED_API_KEY`
   - **Value**: Your FRED API key (get it from `config.py` or [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html))
   - Click **"Add secret"**

4. **Verify:**
   - You should see `FRED_API_KEY` listed in secrets

### Step 2.2: Verify Workflow File Exists

The workflow file is already created at:
```
.github/workflows/daily_model_run.yml
```

**Verify it exists:**
- Check GitHub repo → `.github/workflows/daily_model_run.yml`
- Or check locally: `ls -la .github/workflows/`

### Step 2.3: Test Workflow Manually

1. **Go to Actions tab:**
   - In your GitHub repo, click **"Actions"** tab

2. **Find the workflow:**
   - Click **"Daily Model Run"** in the left sidebar
   - If you don't see it, wait a moment or refresh

3. **Run manually:**
   - Click **"Run workflow"** dropdown (top right)
   - Click **"Run workflow"** button
   - Select branch: `main`
   - Click green **"Run workflow"** button

4. **Monitor the run:**
   - Click on the running workflow
   - Watch the logs in real-time
   - It will take **~5-6 minutes** to complete

5. **Check results:**
   - After completion, check the **"run-model"** job logs
   - Verify it says: `Results saved to: public/cached_results.json`
   - Check that the commit step succeeded

6. **Verify file was created:**
   - Go back to repo main page
   - Navigate to `public/cached_results.json`
   - File should exist and contain JSON data

### Step 2.4: Verify Workflow is Connected

**The workflow is already configured to:**
- Run daily at 6 AM UTC (via cron)
- Install Python dependencies
- Run `run_model_github_actions.py`
- Save results to `public/cached_results.json`
- Commit and push the updated file

**You don't need to do anything else** - the cron is already set up in the workflow file.

---

## PART 3: Cron Setup (Already Configured)

### Step 3.1: Verify Cron Schedule

The cron is **already configured** in `.github/workflows/daily_model_run.yml`:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
```

**This means:**
- The workflow runs **automatically every day at 6 AM UTC**
- No external cron service needed
- GitHub Actions handles the scheduling

### Step 3.2: How It Works

**Daily Flow:**
1. **6 AM UTC**: GitHub Actions triggers the workflow
2. **Model runs**: Takes ~5-6 minutes to complete
3. **Results saved**: `public/cached_results.json` is updated
4. **Auto-commit**: Workflow commits and pushes the file
5. **Vercel detects push**: Automatically redeploys
6. **Users see latest**: Frontend loads the new JSON instantly

**No user waits**: The model runs in the background. Users always see cached results instantly.

### Step 3.3: Change Schedule (Optional)

To change when the model runs:

1. **Edit workflow file:**
   - Edit `.github/workflows/daily_model_run.yml`
   - Change the cron expression

2. **Common schedules:**
   - `'0 0 * * *'` = Midnight UTC daily
   - `'0 12 * * *'` = Noon UTC daily
   - `'0 6 * * 1'` = 6 AM UTC every Monday
   - `'0 */6 * * *'` = Every 6 hours

3. **Use crontab.guru:**
   - Visit [crontab.guru](https://crontab.guru) to build cron expressions
   - Copy the expression to the workflow file

4. **Commit and push:**
   ```bash
   git add .github/workflows/daily_model_run.yml
   git commit -m "Update cron schedule"
   git push
   ```

---

## Complete Flow Summary

### Initial Setup (One-time)
1. ✅ Code is restructured (HTML/JS frontend, separate model script)
2. ✅ Push code to GitHub
3. ✅ Connect Vercel to repo
4. ✅ Add FRED_API_KEY to GitHub Secrets
5. ✅ Test workflow manually

### Daily Operation (Automatic)
1. **6 AM UTC**: GitHub Actions runs workflow
2. **~5-6 min**: Model executes and generates results
3. **Auto-save**: Results saved to `public/cached_results.json`
4. **Auto-commit**: Workflow commits and pushes file
5. **Auto-deploy**: Vercel detects push and redeploys
6. **Users**: See latest results instantly (no wait)

---

## Troubleshooting

### Vercel shows "Loading..." forever
- **Check**: Visit `your-site.vercel.app/cached_results.json` directly
- **Fix**: Run GitHub Actions workflow manually to create the file
- **Verify**: JSON file exists and is valid

### GitHub Actions fails
- **Check**: Actions tab → Latest run → Error logs
- **Common issues**:
  - Missing `FRED_API_KEY` secret → Add it in Settings → Secrets
  - Missing dependencies → Check `requirements.txt`
  - Script errors → Check `run_model_github_actions.py` syntax

### Workflow doesn't run automatically
- **Check**: Actions tab → Workflow schedules
- **Note**: First run might take up to 24 hours
- **Test**: Use "Run workflow" button to test manually

### Frontend doesn't update after model run
- **Check**: Vercel deployment logs
- **Verify**: `public/cached_results.json` was updated in GitHub
- **Wait**: Vercel auto-deploy takes ~1-2 minutes after push

---

## Next Steps

1. **Test locally first** (optional):
   ```bash
   python run_model_github_actions.py
   # Check that public/cached_results.json was created
   ```

2. **Deploy to Vercel** (follow Part 1)

3. **Test GitHub Actions** (follow Part 2.3)

4. **Monitor first daily run** (check Actions tab next day at 6 AM UTC)

5. **Verify site works** (visit Vercel URL, check data loads)

---

## Files Changed for Deployment

**New files:**
- `public/index.html` - Web frontend (replaces Streamlit)
- `public/app.js` - Frontend JavaScript logic
- `run_model_github_actions.py` - Model runner for GitHub Actions
- `.github/workflows/daily_model_run.yml` - GitHub Actions workflow
- `vercel.json` - Vercel configuration
- `package.json` - For Vercel build

**Kept files:**
- `model.py` - Model code (unchanged)
- `frontend.py` - Streamlit version (for local dev)
- `launcher.py` - Local launcher (for local dev)
- `config.py` - Configuration (unchanged)

**Result:**
- **Local dev**: Use `launcher.py` (Streamlit)
- **Production**: GitHub Actions runs model → Vercel serves HTML/JS
