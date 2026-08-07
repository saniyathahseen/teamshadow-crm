# 📱 How to Get WhatsApp API Credentials

This guide shows you exactly how to get the three credentials needed for the Meta Ads → WhatsApp integration:

```
WHATSAPP_VERIFY_TOKEN=your-verify-token
WHATSAPP_API_TOKEN=your-api-token
WHATSAPP_PHONE_ID=your-phone-id
```

---

## Step 1: Create a Meta Developer Account (Free)

1. Go to **https://developers.facebook.com**
2. Click **"Get Started"**
3. Login with your Facebook account
4. Complete the developer registration (verify email/phone)

---

## Step 2: Create a Meta App

1. In the Developer Dashboard, click **"Create App"**
2. Select **"Business"** as the app type
3. Enter:
   - **App name**: `Team Shadow Weddings`
   - **Contact email**: your email
4. Click **"Create App"**

---

## Step 3: Add WhatsApp Product

1. In your app dashboard, click **"Add Product"**
2. Find **"WhatsApp"** and click **"Set Up"**
3. This creates your WhatsApp Business integration

---

## Step 4: Get Your Credentials

### 4a. Get `WHATSAPP_PHONE_ID`

1. In the WhatsApp section, click **"API Setup"**
2. You'll see a **"Temporary access token"** and **"Phone number ID"**
3. **Phone number ID** is your `WHATSAPP_PHONE_ID`
4. Copy it (looks like a number, e.g., `123456789012345`)

### 4b. Get `WHATSAPP_API_TOKEN`

**Option A: Use Temporary Token (for testing)**
- The temporary token shown in API Setup works for 24 hours
- Copy it as your `WHATSAPP_API_TOKEN`

**Option B: Create Permanent Token (recommended)**
1. Go to **https://business.facebook.com**
2. Click **"Settings"** → **"Business Settings"**
3. Click **"Users"** → **"System Users"**
4. Click **"Add"** → Create a system user
5. Click **"Add Assets"** → Select your app
6. Click **"Generate Token"** → Select your app
7. Copy the generated token as your `WHATSAPP_API_TOKEN`

### 4c. Create `WHATSAPP_VERIFY_TOKEN`

This is **any random string you create yourself** (not from Meta):
```bash
# Generate a random token
python3 -c "import secrets; print(secrets.token_hex(16))"
# Example output: 4f8a2b9c1d3e5f7a8b9c0d1e2f3a4b5c
```

Use this value for both:
- Your `WHATSAPP_VERIFY_TOKEN` environment variable
- The webhook verification token in Meta

---

## Step 5: Configure Webhook

1. In your app, go to **WhatsApp** → **Configuration**
2. Click **"Edit"** next to Webhook
3. Enter:
   - **Callback URL**: `https://your-domain.com/api/webhooks/whatsapp`
   - **Verify Token**: Your `WHATSAPP_VERIFY_TOKEN`
4. Click **"Verify and Save"**
5. Under **"Webhook Fields"**, subscribe to:
   - `messages`
   - `message_deliveries`
   - `message_reads`

---

## Step 6: Add Your WhatsApp Number

1. In **API Setup**, click **"Add Phone Number"**
2. Enter your business WhatsApp number
3. You'll receive a verification code on WhatsApp
4. Enter the code to verify

---

## Step 7: Configure Your Backend

Create a `.env` file in your project root:

```bash
# .env
WHATSAPP_VERIFY_TOKEN=4f8a2b9c1d3e5f7a8b9c0d1e2f3a4b5c
WHATSAPP_API_TOKEN=EAAG...your-long-token...
WHATSAPP_PHONE_ID=123456789012345
```

Or set them in docker-compose.yml:

```yaml
environment:
  - WHATSAPP_VERIFY_TOKEN=your-verify-token
  - WHATSAPP_API_TOKEN=your-api-token
  - WHATSAPP_PHONE_ID=your-phone-id
```

---

## Step 8: Test the Integration

```bash
# 1. Test webhook verification
curl "http://localhost:8000/api/webhooks/whatsapp?hub_mode=subscribe&hub_verify_token=your-verify-token&hub_challenge=12345"

# 2. Simulate a lead
curl -X POST http://localhost:8000/api/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"from":"919876543210","message":"Hi! I saw your ad","source":"facebook"}'
```

---

## 💰 Cost Information

| Item | Cost |
|------|------|
| Meta Developer Account | Free |
| Meta App Creation | Free |
| WhatsApp Business API | Free for first 1,000 conversations/month |
| After 1,000 conversations | ~₹0.5-1 per conversation (varies by country) |
| Facebook/Instagram Ads | Separate ad budget |

---

## 🔑 Quick Reference

| Credential | Where to Find | Example |
|------------|--------------|---------|
| `WHATSAPP_VERIFY_TOKEN` | You create it yourself | `4f8a2b9c1d3e5f7a` |
| `WHATSAPP_API_TOKEN` | Meta Developer → API Setup | `EAAG...` (long string) |
| `WHATSAPP_PHONE_ID` | Meta Developer → API Setup | `123456789012345` |

---

## 🚨 Common Issues

### "Webhook verification failed"
- Make sure `WHATSAPP_VERIFY_TOKEN` matches exactly in both places
- Your server must be publicly accessible (use ngrok for testing)

### "Message not received"
- Check webhook is subscribed to `messages` field
- Verify your phone number is added and verified

### "Can't send messages"
- WhatsApp requires the user to message you first (24-hour window)
- After 24 hours, use a pre-approved message template

### Testing locally with ngrok
```bash
# Expose your local server
ngrok http 8000

# Use the ngrok URL as your webhook callback
# https://your-ngrok-url.ngrok.io/api/webhooks/whatsapp