# 🚀 Render Deployment - Step by Step Guide

**Total Time**: 20 minutes | **Cost**: $0/month

---

## 📋 Complete Checklist

- [ ] Step 1: Create free database
- [ ] Step 2: Create free Redis cache
- [ ] Step 3: Push code to GitHub
- [ ] Step 4: Deploy backend to Render
- [ ] Step 5: Deploy frontend to Render
- [ ] Step 6: Configure environment variables
- [ ] Step 7: Test your app

---

## ✅ STEP 1: Create Free PostgreSQL Database (2 minutes)

### 1.1 Go to ElephantSQL
- Open: https://www.elephantsql.com
- Click **Sign Up** (top right)
- Choose **Sign up with GitHub** (easier)
- Click **Authorize elephantsql**

### 1.2 Create Free Instance
- Click **Create New Instance**
- **Name**: `cosmic-watch-db`
- **Plan**: Select **Tiny Turtle (Free)**
- **Tags**: (leave empty)
- Click **Select Region**
- Choose: **US-East (Dublin)** or closest to you
- Click **Review**
- Click **Create Instance**

### 1.3 Get Database URL
- Wait ~30 seconds for instance to start
- Click on your instance name
- Copy the full **URL** (looks like):
  ```
  postgresql://user:password@server.elephantsql.com:5432/dbname
  ```
- **Save this somewhere** - you'll need it soon! 📌

---

## ✅ STEP 2: Create Free Redis Cache (2 minutes)

### 2.1 Go to Upstash
- Open: https://upstash.com
- Click **Sign Up** (or **Sign In** if you have account)
- Click **Sign up with GitHub** (easier)

### 2.2 Create Free Redis Database
- Click **Create Database**
- **Database Name**: `cosmic-watch-redis`
- **Region**: Select **us-east-1** (closest to you)
- **Eviction**: `NoEviction`
- Click **Create**

### 2.3 Get Redis Connection String
- Wait for database to be ready
- Click on your database name
- Go to **Details** tab
- Copy **UPSTASH_REDIS_REST_URL** (looks like):
  ```
  redis://default:password@server.upstash.io:port
  ```
  Or copy from **Redis CLI** tab → first line
- **Save this somewhere** - you'll need it soon! 📌

---

## ✅ STEP 3: Push Code to GitHub (3 minutes)

### 3.1 Initialize Git (if not done)
```powershell
cd d:\AstroSentinel\cosmic-watch

# Check if git repo exists
git status

# If not, initialize:
git init
git add .
git commit -m "Initial commit"
```

### 3.2 Create GitHub Repository
- Go to: https://github.com/new
- **Repository Name**: `cosmic-watch`
- **Description**: `Real-time Asteroid Monitoring & AI Chatbot`
- **Visibility**: Public (required for free Render)
- Click **Create repository**

### 3.3 Connect Local Repo to GitHub
```powershell
cd d:\AstroSentinel\cosmic-watch

# Show current remote
git remote -v

# If no remote, add it:
git remote add origin https://github.com/YOUR_USERNAME/cosmic-watch.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

### 3.4 Verify on GitHub
- Go to: https://github.com/YOUR_USERNAME/cosmic-watch
- Should see your files ✅

---

## ✅ STEP 4: Deploy Backend to Render (5 minutes)

### 4.1 Go to Render
- Open: https://render.com
- Click **Sign Up**
- Choose **Sign up with GitHub**
- Click **Authorize render-oss**

### 4.2 Create New Web Service
- Click **New +** (top right)
- Select **Web Service**
- Under "Deploy existing code from a repository", click **Connect GitHub Account**
- Select your **cosmic-watch** repo
- Click **Connect**

### 4.3 Configure Backend Service
- **Name**: `cosmic-watch-backend`
- **Root Directory**: `backend`
- **Environment**: Python 3
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- **Instance Type**: **Free**

### 4.4 Add Environment Variables
Click **Add Environment Variable** and add each one:

1. **DATABASE_URL**
   - Value: (paste from Step 1.3)
   ```
   postgresql://user:password@server.elephantsql.com:5432/dbname
   ```

2. **REDIS_URL**
   - Value: (paste from Step 2.3)
   ```
   redis://default:password@server.upstash.io:port
   ```

3. **JWT_SECRET_KEY**
   - Value: (generate random 32 chars)
   ```
   SuperSecretJWTKeyMustBe32CharactersLongHere1234
   ```

4. **JWT_ALGORITHM**
   - Value: `HS256`

5. **ACCESS_TOKEN_EXPIRE_MINUTES**
   - Value: `30`

6. **CORS_ORIGINS**
   - Value: `["https://cosmic-watch-frontend.onrender.com"]`

7. **ENVIRONMENT**
   - Value: `production`

### 4.5 Deploy
- Scroll down
- Click **Create Web Service**
- ⏳ **Wait 2-3 minutes** for deployment
- See green checkmark → **Success!** ✅

### 4.6 Get Backend URL
- On the service page, copy **URL** at top
- Looks like: `https://cosmic-watch-backend.onrender.com`
- **Save this - you'll need it for frontend!** 📌

---

## ✅ STEP 5: Deploy Frontend to Render (5 minutes)

### 5.1 Create Static Site Service
- Click **New +** (top right)
- Select **Static Site**
- Under "Deploy existing code from a repository", click your **cosmic-watch** repo

### 5.2 Configure Frontend Service
- **Name**: `cosmic-watch-frontend`
- **Root Directory**: `frontend`
- **Build Command**: 
  ```
  npm install && npm run build
  ```
- **Publish Directory**: 
  ```
  dist
  ```
- **Instance Type**: **Free**

### 5.3 Add Environment Variables
Click **Add Environment Variable**:

1. **VITE_API_BASE_URL**
   - Value: (backend URL from Step 4.6)
   ```
   https://cosmic-watch-backend.onrender.com/api
   ```

2. **VITE_APP_NAME**
   - Value: `Cosmic Watch`

3. **VITE_APP_VERSION**
   - Value: `1.0.0`

### 5.4 Deploy
- Scroll down
- Click **Create Static Site**
- ⏳ **Wait 2-3 minutes** for deployment
- See green checkmark → **Success!** ✅

### 5.5 Get Frontend URL
- On the service page, copy **URL** at top
- Looks like: `https://cosmic-watch-frontend.onrender.com`
- **This is your app!** 🎉

---

## ✅ STEP 6: Run Database Migrations (2 minutes)

### 6.1 Connect to Backend Shell
- Go to backend service in Render dashboard
- Click **Shell** tab (top)
- Run these commands:

```bash
cd backend
alembic upgrade head
```

Wait for migration to complete. ✅

---

## ✅ STEP 7: Test Your App (2 minutes)

### 7.1 Visit Frontend
- Open: `https://cosmic-watch-frontend.onrender.com`
- Should see your Cosmic Watch app! 🚀

### 7.2 Test Backend
- Open: `https://cosmic-watch-backend.onrender.com/docs`
- Should see Swagger API documentation

### 7.3 Test API
```bash
# Test health endpoint
curl https://cosmic-watch-backend.onrender.com/health

# Should return: {"status":"ok"}
```

---

## 🔧 Make Updates & Auto-Deploy

### Push Code Changes
```powershell
cd d:\AstroSentinel\cosmic-watch

# Make changes to your code
# Example: edit a file

# Commit and push
git add .
git commit -m "Update feature X"
git push origin main
```

✅ **Render automatically detects the push and redeploys within 2-3 minutes!**

No manual action needed.

---

## 📊 What You Now Have

| Component | Status | URL | Cost |
|-----------|--------|-----|------|
| **Backend** | ✅ Running | https://cosmic-watch-backend.onrender.com | Free |
| **Frontend** | ✅ Running | https://cosmic-watch-frontend.onrender.com | Free |
| **Database** | ✅ Running | ElephantSQL | Free |
| **Cache** | ✅ Running | Upstash | Free |
| **Total** | | | **$0/month** |

---

## ⚠️ Important Notes

### Free Tier Limitations

1. **Hibernation**: Free services sleep after 15 mins of inactivity
   - First request wakes them up (takes 30 seconds)
   - Solution: Use [Uptime Robot](https://uptimerobot.com) to ping every 5 mins (keeps it awake)

2. **Database Size**: ElephantSQL free tier = 20 MB
   - Fine for development
   - Upgrade later if needed

3. **Bandwidth**: Unlimited (no overage)

---

## 🆘 Troubleshooting

### Backend shows error "health check failed"
```bash
# Check logs in Render dashboard
# Look for error messages
# Common issues:
# 1. DATABASE_URL wrong → Copy exactly from ElephantSQL
# 2. REDIS_URL wrong → Copy exactly from Upstash
# 3. Missing dependencies → Check requirements.txt
```

**Solution**: 
- Click service → Logs tab
- Scroll to see error message
- Copy error → Google it

### Frontend shows "Cannot reach API"
```javascript
// Check browser console (F12)
// Should see API requests going to:
// https://cosmic-watch-backend.onrender.com/api

// If getting CORS error:
// Backend CORS_ORIGINS is wrong
// Set to: ["https://cosmic-watch-frontend.onrender.com"]
```

### Database connection timeout
- Check DATABASE_URL is correct
- ElephantSQL free tier might sleep
- Click instance → Wake it up

---

## 🚀 Next Steps (Optional)

### 1. Keep Backend Awake (Recommended)
- Go to https://uptimerobot.com
- Sign up (free)
- Monitor: `https://cosmic-watch-backend.onrender.com/health`
- Set interval: 5 minutes
- ✅ Backend will never sleep

### 2. Use Custom Domain
- Buy domain (Namecheap, GoDaddy, ~$1/year)
- In Render dashboard → Settings → Custom Domain
- Add DNS records (Render will show instructions)
- ✅ Access at `yourdomain.com`

### 3. Setup GitHub Actions (CI/CD)
- Automatically test on every push
- Only deploy if tests pass
- (Optional - works fine without it)

---

## 📞 Getting Help

**If something fails:**

1. Check **Logs** in Render dashboard
2. Copy the error
3. Google the error message
4. Check [Render Docs](https://render.com/docs)
5. Ask in [Render Community](https://community.render.com)

---

## ✨ Summary

**You now have:**
- ✅ Production-deployed backend
- ✅ Production-deployed frontend
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Auto-deploy on every git push
- ✅ SSL/TLS (HTTPS) included
- ✅ All for FREE 🎉

**Total deployment time: 20 minutes**

**Congratulations! Your app is live! 🚀**

---

**Questions?** Check the logs in Render dashboard or refer back to the troubleshooting section.
