# Quick Deployment Guide

## Deploy to Heroku (Recommended)

1. **Prerequisites:**
   - Heroku account at https://heroku.com
   - Heroku CLI installed

2. **Deploy:**
   ```bash
   heroku login
   heroku create attendance-maker-app-mannangoel
   git push heroku main
   heroku open
   ```

3. **Update README with live URL after deployment**

## Deploy to Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `mannangoel/attendance-maker-app`
5. Railway will auto-deploy
6. Copy the generated URL and update README

## Deploy to Render

1. Go to https://render.com
2. Connect GitHub account
3. Create "New Web Service"
4. Select the repository
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python app.py`
7. Deploy and copy the URL

## Post-Deployment

After getting your live URL, update the README.md:
```markdown
🌐 **[View Live Application](YOUR_LIVE_URL_HERE)**
```

Then commit and push:
```bash
git add README.md
git commit -m "Update live demo URL"
git push origin main
```