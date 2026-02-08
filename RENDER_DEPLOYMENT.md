# Render Deployment Guide (Free)

**Cost**: $0/month  
**Setup Time**: 10 minutes  
**Uptime**: 99.9% (free tier)

---

## 🎯 Overview

Deploy both frontend and backend completely free on [Render.com](https://render.com):

- **Backend** (FastAPI): Render Web Service
- **Frontend** (React): Render Static Site
- **Database** (PostgreSQL): ElephantSQL or Railway
- **Cache** (Redis): Upstash

---

## 📋 Prerequisites

- GitHub account (push code there)
- Render account (sign up with GitHub)
- Database URL (from ElephantSQL or Railway)
- Redis URL (from Upstash)

---

## Step 1: Create Free Database

### Option A: ElephantSQL (PostgreSQL)

1. Go to https://www.elephantsql.com
2. Sign up (free)
3. Create instance → Free tier
4. Copy **URL** (looks like `postgresql://user:pass@server:5432/db`)
5. Save for later

### Option B: Railway PostgreSQL

1. Go to https://railway.app
2. Sign up with GitHub
3. New project → Add PostgreSQL
4. Copy connection string
5. Save for later

---

## Step 2: Create Free Redis Cache

1. Go to https://upstash.com
2. Sign up (free tier)
3. Create database → Redis
4. Copy **UPSTASH URI** (looks like `redis://...@...`)
5. Save for later

---

## Step 3: Push Code to GitHub

```bash
cd d:\AstroSentinel\cosmic-watch

# Add Render config files
git add backend/render.yaml frontend/render.yaml
git commit -m "Add Render deployment config"
git push origin main
```

---

## Step 4: Deploy Backend

1. Go to https://render.com
2. **New +** → **Web Service**
3. Select your **cosmic-watch** GitHub repo
4. Configure:
   - **Name**: `cosmic-watch-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. **Environment Variables**:
   - `DATABASE_URL`: (paste from ElephantSQL/Railway)
   - `REDIS_URL`: (paste from Upstash)
   - `JWT_SECRET_KEY`: (generate: random 32 chars)
   - `CORS_ORIGINS`: `["https://yourdomain.onrender.com"]`
   - `ENVIRONMENT`: `production`
6. Click **Create Web Service**

**Wait 2-3 minutes for deployment** ✅

Note your backend URL: `https://cosmic-watch-backend.onrender.com`

---

## Step 5: Deploy Frontend

1. **New +** → **Static Site**
2. Select your **cosmic-watch** GitHub repo
3. Configure:
   - **Name**: `cosmic-watch-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. **Environment Variables**:
   - `VITE_API_BASE_URL`: `https://cosmic-watch-backend.onrender.com/api`
   - `VITE_APP_NAME`: `Cosmic Watch`
5. Click **Create Static Site**

**Wait 2-3 minutes for deployment** ✅

Note your frontend URL: `https://cosmic-watch-frontend.onrender.com`

---

## Step 6: Run Database Migrations

Once backend is deployed:

```bash
# SSH into backend (via Render dashboard)
# OR use the Shell tab to run:

cd backend
alembic upgrade head
```

---

## Step 7: Test Application

1. Open: `https://cosmic-watch-frontend.onrender.com`
2. See your app live! 🎉

---

## 📊 Performance & Limitations

| Feature | Free Tier | Notes |
|---------|-----------|-------|
| CPU | Shared | Sufficient for small traffic |
| Memory | 512 MB | Enough for Python app |
| Database | 20 MB (ElephantSQL) | Good for development |
| Deployment | Auto from GitHub | Pushes trigger redeploy |
| Uptime | ~99% | May hibernate if unused |
| Bandwidth | Unlimited | No overage charges |

---

## 🔄 Auto-Deploy on Every Push

Render automatically redeploys when you push to main:

```bash
# Make changes
git add .
git commit -m "Update API"
git push origin main

# Render detects push → Auto builds & deploys! ✅
```

---

## 💡 Pro Tips

### Keep Backend Awake
Render sleeps free services after inactivity. Keep it alive:

```bash
# Add to cronjob (every 10 min):
curl https://cosmic-watch-backend.onrender.com/health
```

Or use a free service like [Uptime Robot](https://uptimerobot.com):
- Monitor your backend URL
- Sends ping every 5 minutes
- Keeps it from sleeping

### Custom Domain

1. Buy domain (Namecheap, GoDaddy, etc.)
2. In Render dashboard → Settings → Custom Domain
3. Add CNAME record pointing to Render

### Environment-Specific Variables

Use `.env` files in Render dashboard:

```
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your-secret-key
REDIS_URL=redis://...
```

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check logs in Render dashboard
# Common issues:
# 1. Missing dependencies → Update requirements.txt
# 2. Port not set → Use $PORT env variable
# 3. DB connection failed → Check DATABASE_URL
```

### Frontend shows "Cannot find API"
```javascript
// Check frontend environment variables
console.log(import.meta.env.VITE_API_BASE_URL)
// Should be: https://cosmic-watch-backend.onrender.com/api
```

### Database connection timeout
- Check firewall rules
- Verify credentials
- ElephantSQL: Add your IP if needed

---

## 🚀 Scale to Paid (When Needed)

When free tier isn't enough:

1. **Backend**: Upgrade to Starter ($7/month)
   - Always running (no hibernation)
   - 1 GB RAM
   - Better performance

2. **Database**: Upgrade ElephantSQL ($35/month for more)
   - More storage & connections

3. **Redis**: Keep Upstash free or upgrade ($25+/month)

**Total cost when scaling: ~$50-80/month** (vs AWS $113+)

---

## 📚 Next Steps

1. ✅ Create free database (ElephantSQL)
2. ✅ Create free Redis (Upstash)
3. ✅ Push code to GitHub
4. ✅ Deploy backend to Render
5. ✅ Deploy frontend to Render
6. ✅ Run database migrations
7. ✅ Visit your live app!

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **ElephantSQL Help**: https://www.elephantsql.com/help
- **Upstash Support**: https://upstash.com/docs

---

**That's it! Free deployment in 15 minutes! 🚀**
