# ZaloKit Bot Deployment Guide

Complete guide to deploy your ZaloKit bot to production using Railway or Heroku.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Zalo Official Account (OA)** - Created at [developers.zalo.me](https://developers.zalo.me)
2. **Zalo App Credentials**:
   - App ID
   - Secret Key
   - Official Account ID
3. **GitHub Account** - To clone this repository
4. **Railway or Heroku Account** - For hosting

## 🔧 Step 1: Configure Zalo Developer Portal

### 1.1 Create Zalo Application

1. Visit [https://developers.zalo.me](https://developers.zalo.me)
2. Click **"Tạo ứng dụng mới"** (Create new application)
3. Fill in application details:
   - **Tên ứng dụng**: Your bot name
   - **Mô tả**: Bot description
   - **Loại ứng dụng**: Official Account API

### 1.2 Enable Required APIs

1. Go to **"Đăng ký API"** (Register API)
2. Enable the following permissions:
   - ✅ **Gửi tin nhắn** (Send messages)
   - ✅ **Nhận tin nhắn** (Receive messages)
   - ✅ **Quản lý người dùng** (Manage users)
   - ✅ **Quản lý nhóm** (Manage groups)

### 1.3 Configure Webhook

1. Navigate to **"Cài đặt"** → **"Webhook"**
2. Enter your webhook URL (you'll get this after deployment):
   ```
   https://your-app-name.railway.app/webhook
   ```
3. Select events to subscribe:
   - ✅ `user_send_text`
   - ✅ `user_received_message`
   - ✅ `user_seen_message`

## 🚀 Step 2: Deploy to Railway

### 2.1 Create Railway Account

1. Go to [https://railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"**

### 2.2 Deploy from GitHub

1. Click **"Deploy from GitHub repo"**
2. Select `ZaloKit` repository
3. Railway will automatically detect the `Procfile`

### 2.3 Set Environment Variables

1. Go to **Variables** tab
2. Add the following environment variables:

```bash
ZALO_APP_ID=your_app_id_here
ZALO_SECRET_KEY=your_secret_key_here
ZALO_OA_ID=your_official_account_id_here
PORT=5000
```

### 2.4 Deploy

1. Click **"Deploy"**
2. Wait for deployment to complete (2-3 minutes)
3. Railway will provide your app URL:
   ```
   https://your-app-name.railway.app
   ```

## 🌐 Step 3: Alternative - Deploy to Heroku

### 3.1 Install Heroku CLI

```bash
# macOS
brew install heroku/brew/heroku

# Windows
choco install heroku-cli

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
```

### 3.2 Login and Create App

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-zalo-bot-name

# Set environment variables
heroku config:set ZALO_APP_ID=your_app_id_here
heroku config:set ZALO_SECRET_KEY=your_secret_key_here
heroku config:set ZALO_OA_ID=your_official_account_id_here
```

### 3.3 Deploy

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Add Heroku remote
heroku git:remote -a your-zalo-bot-name

# Push to Heroku
git push heroku main
```

## ✅ Step 4: Verify Deployment

### 4.1 Check Server Health

Visit your deployment URL:
```
https://your-app-name.railway.app/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "zalo-bot-webhook",
  "bot_ready": true
}
```

### 4.2 Test Webhook Endpoint

Visit:
```
https://your-app-name.railway.app/webhook
```

You should see:
```json
{
  "status": "ok",
  "message": "Webhook is active"
}
```

## 🔗 Step 5: Connect Webhook to Zalo

1. Go back to **Zalo Developer Portal**
2. Navigate to **"Cài đặt"** → **"Webhook"**
3. Update webhook URL:
   ```
   https://your-app-name.railway.app/webhook
   ```
4. Click **"Xác nhận"** (Confirm)
5. Zalo will send a verification request

## 🧪 Step 6: Test Your Bot

### 6.1 Find Your Official Account

1. Open **Zalo App** on your phone
2. Search for your **Official Account** name
3. Follow the OA

### 6.2 Test Commands

Send these messages to test:

```
/help          # Show available commands
/ping          # Check bot response
/info          # Get bot information
/echo Hello!   # Echo your message
/time          # Get current time
```

## 📊 Step 7: Monitor Your Bot

### Railway Logs

1. Go to Railway dashboard
2. Click on your project
3. Go to **"Logs"** tab
4. Monitor real-time logs

### Heroku Logs

```bash
# View real-time logs
heroku logs --tail

# View last 100 lines
heroku logs -n 100
```

## 🔧 Troubleshooting

### Bot Not Responding

1. **Check logs** for errors
2. **Verify environment variables** are set correctly
3. **Test webhook endpoint** manually
4. **Ensure Zalo webhook** is configured correctly

### Webhook Not Receiving Events

1. **Verify webhook URL** in Zalo Developer Portal
2. **Check webhook events** are subscribed
3. **Test with webhook.site** first to see raw events

### Environment Variable Issues

```bash
# Railway: Check variables
# Go to Variables tab in Railway dashboard

# Heroku: Check variables
heroku config

# Heroku: Update variable
heroku config:set ZALO_APP_ID=new_value
```

## 🔐 Security Best Practices

1. **Never commit credentials** to Git
2. **Use environment variables** for sensitive data
3. **Enable HTTPS only** (Railway/Heroku do this by default)
4. **Rotate API keys** regularly
5. **Monitor logs** for suspicious activity

## 📈 Scaling Your Bot

### Railway Scaling

1. Go to **Settings** → **Resources**
2. Increase memory/CPU as needed
3. Railway scales automatically based on traffic

### Heroku Scaling

```bash
# Scale to 2 dynos
heroku ps:scale web=2

# Upgrade dyno type
heroku ps:type standard-1x
```

## 🎯 Next Steps

1. **Customize bot commands** in `examples/zalo_bot_demo.py`
2. **Add database integration** for user data
3. **Implement analytics** tracking
4. **Set up monitoring** alerts
5. **Create admin dashboard** for management

## 📚 Additional Resources

- [Zalo API Documentation](https://developers.zalo.me/docs)
- [Railway Documentation](https://docs.railway.app)
- [Heroku Documentation](https://devcenter.heroku.com)
- [ZaloKit GitHub](https://github.com/jvunder/ZaloKit)

## 🤝 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review **Railway/Heroku logs**
3. Open an issue on [GitHub](https://github.com/jvunder/ZaloKit/issues)

---

**Happy Bot Building! 🚀**
