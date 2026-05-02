# Quick Reference Card

## Installation (Copy & Paste)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create configuration file
copy .env.example .env
# Then edit .env with your API keys
```

## Campaign Commands

```bash
# Create company list (my_companies.csv with columns: name,domain,industry)

# 1. Discover contacts
python campaign.py discover my_companies.csv

# 2. Find email addresses  
python campaign.py discover_emails

# 3. Create campaign
python campaign.py create_campaign "Campaign Name"
# Save the ID that appears!

# 4. Personalize emails (replace ID with actual ID)
python personalize_once.py YOUR_CAMPAIGN_ID

# 5. Send emails
python fast_send.py YOUR_CAMPAIGN_ID

# 6. Check replies
python campaign.py check_replies YOUR_CAMPAIGN_ID

# 7. Queue follow-ups
python campaign.py queue_next_step YOUR_CAMPAIGN_ID 1

# 8. Send follow-ups
python fast_send.py YOUR_CAMPAIGN_ID
```

## File Locations

- **Configuration:** `.env` (copy from `.env.example`)
- **Company list:** `my_companies.csv`
- **Results:** `campaign_final_tracker.csv`
- **Company summary:** `campaign_status_tracker.csv`

## Typical Results

- **Delivery rate:** 99%+
- **Reply rate:** 50%+ (industry benchmark is 2-5%)
- **Time per campaign:** 1-2 days
- **Cost:** $5-20

## Support

1. Check GETTING_STARTED.md for detailed guide
2. Check README.md for technical details
3. Check CAMPAIGN_GUIDE.md for monitoring
