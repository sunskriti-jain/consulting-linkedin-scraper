# Getting Started: LinkedIn Scraper (Complete Beginner Guide)

Welcome! This guide is for people with **no coding experience**. You'll harvest LinkedIn contacts and send personalized emails.

---

## What This Project Does

1. **Finds real people** on LinkedIn from major companies
2. **Writes personalized emails** automatically using AI
3. **Sends emails** through your Gmail account
4. **Tracks responses** and helps you follow up

**Result:** Reach hundreds of business decision-makers with personalized messages.

---

## Before You Start: What You Need

### Required
- A computer (Windows, Mac, or Linux)
- Python (we'll install this)
- A Gmail account
- Internet connection

### Optional but Recommended
- Professional Gmail address
- API keys for:
  - Claude (Anthropic) - AI email writing
  - Perplexity - backup AI
  - Hunter.io - email finding (optional)

---

## Installation (Step-by-Step)

### Step 1: Install Python

**On Windows:**
1. Go to https://www.python.org/downloads/
2. Click "Download Python 3.12"
3. Run the installer
4. **CHECK:** "Add Python to PATH"
5. Click "Install Now"

**Verify:**
- Open Command Prompt (search "cmd")
- Type: `python --version`
- Should show: `Python 3.12.x`

### Step 2: Download This Project

**Option A: Using Git**
1. Open Command Prompt
2. Type: `git clone https://github.com/eleyn-xiong/linkedin-scraper.git`
3. Type: `cd linkedin-scraper`

**Option B: Download as ZIP**
1. Go to https://github.com/eleyn-xiong/linkedin-scraper
2. Click green "<> Code" button
3. Click "Download ZIP"
4. Extract the ZIP file
5. Open Command Prompt
6. Type: `cd C:\linkedin-scraper`

### Step 3: Install Dependencies

In Command Prompt:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Wait for completion (lots of text = normal).

### Step 4: Set Up Gmail

1. Go to https://myaccount.google.com/
2. Click "Security"
3. Find "App passwords"
4. Select "Mail" and "Windows Computer"
5. Google generates a 16-character password
6. **Save this password somewhere safe**

---

## Getting API Keys (Free Trials Available)

### Claude API

1. Go to https://console.anthropic.com/
2. Sign up free
3. Go to "API Keys"
4. Create new key
5. Copy and save

**Free tier:** $5/month

### Perplexity API

1. Go to https://www.perplexity.ai/
2. Sign up
3. Go to "API" settings
4. Create key
5. Save it

**Free tier:** Available

### Hunter.io (Optional)

1. Go to https://hunter.io/
2. Sign up
3. Go to "Integrations" > "API"
4. Copy API key

**Free tier:** 50 lookups/month

---

## Creating Your Configuration File

1. Find `.env.example` in the folder
2. Copy it and rename to `.env`
3. Right-click `.env` > "Edit with Notepad"
4. Fill in:

```
ANTHROPIC_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
HUNTER_API_KEY=your_key_here

SENDER_NAME=Your Name
SENDER_EMAIL=your@gmail.com
SENDER_TITLE=Your Title
SENDER_COMPANY=Your Company

DAILY_EMAIL_CAP=40
MIN_DELAY_SECONDS=60
MAX_DELAY_SECONDS=120
```

5. Save (Ctrl+S)
6. Close

---

## Running Your First Campaign

### Step 1: Create Company List

Create `my_companies.csv`:

```
name,domain,industry
Apple Inc,apple.com,Technology
Microsoft,microsoft.com,Technology
Google,google.com,Technology
Amazon,amazon.com,Technology
Meta,meta.com,Technology
```

### Step 2: Discover LinkedIn Contacts

In Command Prompt:
```bash
cd C:\linkedin-scraper
python campaign.py discover my_companies.csv
```

Takes 5-10 minutes per company.

### Step 3: Find Email Addresses

```bash
python campaign.py discover_emails
```

### Step 4: Create Campaign

```bash
python campaign.py create_campaign "My First Campaign"
```

Save the ID that appears! You'll need it.

Then personalize:
```bash
python personalize_once.py YOUR_CAMPAIGN_ID
```

Replace `YOUR_CAMPAIGN_ID` with the ID from above.

### Step 5: Send Emails

```bash
python fast_send.py YOUR_CAMPAIGN_ID
```

You'll see progress. Let it run in background.

### Step 6: Check Replies

After 1-2 hours:
```bash
python campaign.py check_replies YOUR_CAMPAIGN_ID
```

### Step 7: Send Follow-ups

```bash
python campaign.py queue_next_step YOUR_CAMPAIGN_ID 1
python fast_send.py YOUR_CAMPAIGN_ID
```

---

## Understanding Results

### campaign_final_tracker.csv
- Every email sent
- Contact details
- Send time
- Success/failure

### campaign_status_tracker.csv
- Summary by company
- Total contacts
- Sent count
- Reply count

Open with Excel!

---

## Troubleshooting

### "Python not found"
- Reinstall Python
- Check "Add to PATH"
- Restart Command Prompt

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Gmail API error"
- Check app password in .env
- Enable 2-factor auth
- Create new app password

### "Rate limit exceeded"
- Wait 1 hour
- Reduce DAILY_EMAIL_CAP in .env

### "No contacts found"
- Check CSV format
- Try 1 company first
- Verify domain is correct

---

## Tips for Success

### Before Campaign
1. Test with 1 company
2. Use professional email
3. Keep subject lines short
4. Start small (50-100 emails)

### During Campaign
1. Keep computer on
2. Check progress regularly
3. Monitor Gmail for errors

### After Campaign
1. Check replies within 24 hours
2. Reply quickly to interested people
3. Send follow-ups to non-responders

---

## Common Questions

### How much does it cost?
- Claude: ~$0.50 per 1,000 emails
- Gmail: Free
- Hunter: Free tier or $49/month
- **Total:** $5-20 per campaign

### How many emails per day?
- Gmail allows: ~500/day
- Default limit: 40/day
- Recommended: <100/day to avoid spam filters

### Are these legal?
- Yes, for business outreach
- Personalized, relevant emails
- Follow CAN-SPAM rules
- Good for B2B outreach

### Can I customize emails?
- Yes, edit personalize_once.py
- Or manually edit generated emails

### What if Gmail blocks me?
- Reduce send rate
- Increase delays
- Check Gmail security notifications

---

## Next Steps

1. Complete installation
2. Create .env file
3. Test with 1-3 companies
4. Check results
5. Run larger campaign

---

## Getting Help

If stuck:
1. Read error message carefully
2. Check Troubleshooting above
3. Check README.md
4. Check CAMPAIGN_GUIDE.md

---

## You're Ready!

You now have a professional email system:
- Finds real LinkedIn contacts
- Writes personalized emails
- Sends automatically
- Tracks replies

**Start small and expand!** Good luck! 🚀
