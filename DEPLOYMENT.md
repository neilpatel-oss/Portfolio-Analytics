# Deployment Instructions

This guide walks you through deploying the Stock Analysis Platform to Vercel with GitHub Actions for daily model updates.

**Before you redeploy:** complete [Step 2 (GitHub Secrets)](#step-2-github-secrets-do-this-before-first-deploy) and, if you want a fixed-time daily run, [Step 4 Option B (external cron)](#option-b-external-cron-site-eg-cron-joborg). Then push and redeploy.

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

## Step 2: GitHub Secrets (do this before first deploy)

The workflow needs a FRED API key. Add it as a repository secret so Actions can run the model.

### 2.1 Get a FRED API key (if you don’t have one)
1. Go to [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Sign in or create an account
3. Request an API key and copy it

### 2.2 Add the secret in GitHub
1. Open your repo on GitHub (e.g. `https://github.com/skp1008/Portfolio-Analytics`)
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. **Name:** `FRED_API_KEY` (exactly this)
5. **Value:** paste your FRED API key
6. Click **"Add secret"**

You should see `FRED_API_KEY` listed under Repository secrets. The workflow will use it; you never commit it.

---

## Step 3: Setup GitHub Actions Workflow

### 3.1 Enable GitHub Actions
The workflow file is already at `.github/workflows/daily_model_run.yml`.

**The workflow will:**
- Run on schedule (and/or via external cron — see Step 4)
- Install Python dependencies
- Run `run_model_github_actions.py`
- Save results to `public/cached_results.json`
- Commit and push the updated JSON file

### 3.2 Test the workflow manually
1. Go to the **Actions** tab in your GitHub repo
2. Click **"Daily Model Run"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait ~5–6 minutes, then confirm `public/cached_results.json` was updated

### 3.3 Verify
- **Actions** tab shows workflow runs
- The first successful run creates/updates `public/cached_results.json`

---

## Step 4: Cron — GitHub schedule and/or external cron site

You can use **only** the built-in schedule, **only** an external cron site, or **both**.

### Option A: Built-in schedule (in the workflow)

The workflow already has a schedule in `.github/workflows/daily_model_run.yml`:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:     # allows manual + external cron trigger
```

**To change the time:** edit the `cron` line (e.g. [crontab.guru](https://crontab.guru)):
- `'0 0 * * *'` = midnight UTC daily
- `'0 12 * * *'` = noon UTC daily
- `'0 6 * * 1'` = 6 AM UTC every Monday

Note: GitHub may run scheduled workflows a few minutes late; for exact timing, use Option B.

### Option B: External cron site (e.g. cron-job.org)

Use a free cron website to call GitHub’s API at a fixed time and trigger the workflow. That way the run happens when the cron site fires, not when GitHub’s scheduler runs.

**1. Create a Personal Access Token (PAT) on GitHub**
1. GitHub → **Settings** (your profile, not the repo) → **Developer settings** → **Personal access tokens** → **Tokens (classic)** or **Fine-grained tokens**
2. **New token**
   - **Classic:** enable scope **`repo`**
   - **Fine-grained:** select this repo, permissions **Contents: Read and write** and **Actions: Read and write** (or **Workflows: Read and write**)
3. Generate and **copy the token** (you won’t see it again)

**2. Create the cron job on cron-job.org**
1. Go to [cron-job.org](https://cron-job.org) and sign up / log in
2. **Create cronjob**
3. **URL:**  
   `https://api.github.com/repos/OWNER/REPO/actions/workflows/daily_model_run.yml/dispatches`  
   Replace `OWNER` and `REPO` with your GitHub username and repo name (e.g. `skp1008` and `Portfolio-Analytics`).
4. **Request method:** `POST`
5. **Request headers:** add these two:
   - `Authorization`: `token YOUR_GITHUB_PAT`
   - `Accept`: `application/vnd.github.v3+json`
6. **Request body:**  
   - Choose “Raw” or “JSON” and enter:  
     `{"ref":"main"}`  
   (Use `master` if your default branch is `master`.)
7. **Schedule:** set the time (e.g. daily at 6:00 UTC)
8. Save the cron job

**3. Test**
- Use “Run now” on the cron job, then check the repo **Actions** tab for a new “Daily Model Run” run.

**Other cron sites (e.g. EasyCron, cron-job.com):** use the same URL, method, headers, and body as above.

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
├── config.py                      # Local only (gitignored); use GitHub Secret for Actions
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
