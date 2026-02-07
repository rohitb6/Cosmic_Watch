# Cosmic Watch - DigitalOcean Deployment Guide

**Status**: Ready to deploy  
**Platform**: DigitalOcean ($5-7/month droplet)  
**Database**: SQLite (works for small traffic)  
**Domain**: Auto-generated subdomain  

---

## Step 1: Create DigitalOcean Droplet

### 1.1 Sign Up / Login
- Go to https://www.digitalocean.com
- Create account or login
- Add payment method

### 1.2 Create New Droplet
1. Click **Create** → **Droplets**
2. **Choose Image**: Ubuntu 22.04 LTS (latest)
3. **Choose Size**: **$5/month** (1GB RAM, 1 vCPU, 25GB SSD)
4. **Region**: Choose closest to your location
5. **Authentication**: SSH key (more secure than password)
   - If no SSH key, select **Password** for now
6. **Hostname**: `cosmic-watch`
7. Click **Create Droplet**

**Note**: Droplet IP address will appear in 2-3 minutes

---

## Step 2: SSH into Droplet

### Windows (PowerShell):
```powershell
ssh root@YOUR_DROPLET_IP
```

### Mac/Linux:
```bash
ssh root@YOUR_DROPLET_IP
```

Replace `YOUR_DROPLET_IP` with the actual IP shown in DigitalOcean dashboard.

---

## Step 3: Install Dependencies

Once SSH'd in, run:

```bash
# Update system
apt update && apt upgrade -y

# Install Python, Node.js, Git
apt install -y python3 python3-pip python3-venv nodejs npm git

# Install Nginx (reverse proxy)
apt install -y nginx

# Install Supervisor (process manager)
apt install -y supervisor

# Verify installations
python3 --version  # Should show Python 3.10+
node --version     # Should show v18+
npm --version      # Should show v9+
```

---

## Step 4: Clone Repository

```bash
# Clone Cosmic Watch
git clone https://github.com/rohitb6/Cosmic_Watch.git /opt/cosmic-watch
cd /opt/cosmic-watch

# Set permissions
chmod -R 755 /opt/cosmic-watch
```

---

## Step 5: Setup Backend (FastAPI)

```bash
# Navigate to backend
cd /opt/cosmic-watch/backend

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test backend
python3 main.py
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Press `Ctrl+C` to stop. Keep running it will be managed by Supervisor.

---

## Step 6: Setup Frontend (React/Vite)

```bash
# Navigate to frontend
cd /opt/cosmic-watch/frontend

# Install dependencies
npm install

# Build for production
npm run build

# This creates 'dist' folder with optimized files
```

---

## Step 7: Configure Backend Service (Supervisor)

Create Supervisor config:

```bash
sudo nano /etc/supervisor/conf.d/cosmic-watch-backend.conf
```

Paste this (change `YOUR_USERNAME` to your server user):

```ini
[program:cosmic-watch-backend]
directory=/opt/cosmic-watch/backend
command=/opt/cosmic-watch/backend/venv/bin/python3 main.py
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/cosmic-watch-backend.log
environment=PATH="/opt/cosmic-watch/backend/venv/bin"
```

Save: `Ctrl+X` → `Y` → `Enter`

Enable Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start cosmic-watch-backend

# Check status
sudo supervisorctl status cosmic-watch-backend
```

---

## Step 8: Configure Nginx (Web Server)

Create Nginx config:

```bash
sudo nano /etc/nginx/sites-available/cosmic-watch
```

Paste this:

```nginx
upstream cosmic_watch_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name localhost;
    client_max_body_size 10M;

    # Serve frontend static files
    location / {
        root /opt/cosmic-watch/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API proxy to backend
    location /api {
        proxy_pass http://cosmic_watch_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # Auth endpoints (non-/api prefix)
    location /auth {
        proxy_pass http://cosmic_watch_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://cosmic_watch_backend;
    }
}
```

Save and enable:

```bash
sudo ln -s /etc/nginx/sites-available/cosmic-watch /etc/nginx/sites-enabled/cosmic-watch

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx  # Auto-start on reboot
```

---

## Step 9: Update Backend CORS

The backend needs to allow requests from your DigitalOcean IP.

Edit backend config:

```bash
nano /opt/cosmic-watch/backend/app/core/config.py
```

Find this line:
```python
cors_origins: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:3001", "http://localhost:3002"]
```

Replace with your droplet's IP (find it in DigitalOcean dashboard):
```python
cors_origins: list = [
    "http://YOUR_DROPLET_IP",
    "http://YOUR_DROPLET_IP:80",
    "http://your-domain.com",  # Add if you get a domain later
]
```

Restart backend:
```bash
sudo supervisorctl restart cosmic-watch-backend
```

---

## Step 10: Verify Deployment

Check if everything is running:

```bash
# Check backend
sudo supervisorctl status cosmic-watch-backend

# Check Nginx
sudo systemctl status nginx

# Check ports
sudo netstat -tulpn | grep -E ':(80|8000)'
```

---

## Step 11: Access Your App

Open browser and go to:
```
http://YOUR_DROPLET_IP
```

Replace `YOUR_DROPLET_IP` with your actual DigitalOcean IP

**Demo Login:**
- Email: `demo@cosmicwatch.io`
- Password: `Demo@12345`

---

## Step 12: (Optional) Setup Domain

If you want a custom domain:

### 1. Register Domain
- Go to **GoDaddy**, **Namecheap**, or **Route53**
- Register: `cosmicwatch.com` or your choice
- Cost: $10-15/year

### 2. Update DNS Records
In your domain registrar, add these DNS records:

| Type | Name | Value |
|------|------|-------|
| A | @ | YOUR_DROPLET_IP |
| A | www | YOUR_DROPLET_IP |

Wait 5-10 minutes for DNS to propagate.

### 3. Get SSL Certificate (HTTPS)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

Update Nginx config to redirect HTTP → HTTPS:

```bash
sudo nano /etc/nginx/sites-available/cosmic-watch
```

Add at top of server block:
```nginx
if ($scheme != "https") {
    return 301 https://$server_name$request_uri;
}
```

---

## Troubleshooting

### Backend not responding
```bash
# Check logs
sudo tail -f /var/log/cosmic-watch-backend.log

# Restart
sudo supervisorctl restart cosmic-watch-backend
```

### Nginx errors
```bash
# Check syntax
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
```

### CORS errors
- Make sure CORS origins in `config.py` includes your IP/domain
- Restart backend after changes

### Database locked
```bash
# Clear database
rm /opt/cosmic-watch/backend/cosmic_watch.db

# Restart backend
sudo supervisorctl restart cosmic-watch-backend
```

---

## Monitoring

### Check Disk Space
```bash
df -h
```

### Check Memory Usage
```bash
free -h
```

### Check Backend Logs
```bash
sudo tail -f /var/log/cosmic-watch-backend.log
```

### Check Nginx Logs
```bash
sudo tail -f /var/log/nginx/access.log
```

---

## Next Steps

- ✅ Droplet created and running
- ✅ Backend & Frontend deployed
- ✅ Nginx serving app
- ⏳ (Optional) Add custom domain
- ⏳ (Optional) Enable SSL/HTTPS
- ⏳ (Optional) Upgrade to PostgreSQL for better performance

---

## Cost Breakdown

| Service | Cost |
|---------|------|
| DigitalOcean Droplet ($5/mo) | $5 |
| Bandwidth (included) | Free |
| Domain (optional) | $10-15/year |
| SSL Certificate | Free (Let's Encrypt) |
| **Total/Month** | **$5-7** |

---

## Support

**Cosmic Watch GitHub**: https://github.com/rohitb6/Cosmic_Watch  
**DigitalOcean Docs**: https://docs.digitalocean.com  
**FastAPI Docs**: https://fastapi.tiangolo.com  

---

**Made with ❤️ by Rohit**  
© 2026 Cosmic Watch - All rights reserved

