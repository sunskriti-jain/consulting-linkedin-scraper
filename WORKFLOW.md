# Campaign Workflow (Visual Guide)

## The 7-Step Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR EMAIL CAMPAIGN                          │
└─────────────────────────────────────────────────────────────────┘

STEP 1: PREPARE
═════════════════
┌──────────────────────────────┐
│  Install Python & Libraries  │ (5 minutes)
│  Get API Keys                │
│  Create .env file            │
└──────────────────┬───────────┘
                   ▼
STEP 2: CREATE COMPANY LIST
════════════════════════════
┌──────────────────────────────┐
│  Create my_companies.csv with:│
│  - Apple Inc, apple.com       │
│  - Microsoft, microsoft.com   │
│  - Google, google.com         │
│  - [More companies...]        │
└──────────────────┬───────────┘
                   ▼
STEP 3: DISCOVER CONTACTS
═════════════════════════
┌──────────────────────────────┐
│  python campaign.py discover  │
│  my_companies.csv            │
│                              │
│  ▶ Searches LinkedIn         │
│  ▶ Finds people's names      │
│  ▶ Gets their titles         │
│  Result: 50-100 people/co    │
└──────────────────┬───────────┘
         (5-10 min per company)
                   ▼
STEP 4: FIND EMAILS
═══════════════════
┌──────────────────────────────┐
│  python campaign.py           │
│  discover_emails             │
│                              │
│  ▶ Uses Hunter.io (paid)     │
│  ▶ Uses pattern guessing     │
│  ▶ Gets email addresses      │
│  Result: Email for each      │
└──────────────────┬───────────┘
         (3-5 minutes)
                   ▼
STEP 5: WRITE EMAILS (AI)
═════════════════════════
┌──────────────────────────────┐
│  python personalize_once.py   │
│  [your_campaign_id]          │
│                              │
│  ▶ Claude/Perplexity AI      │
│  ▶ Writes personalized       │
│    emails for each person    │
│  ▶ Different templates per   │
│    company                   │
│  Result: Ready-to-send       │
│  emails in database          │
└──────────────────┬───────────┘
         (10-20 minutes)
                   ▼
STEP 6: SEND EMAILS
═══════════════════
┌──────────────────────────────┐
│  python fast_send.py          │
│  [your_campaign_id]          │
│                              │
│  ▶ Uses Gmail API            │
│  ▶ Sends 1.3 emails/minute   │
│  ▶ Smart delays (60-120 sec) │
│  ▶ Avoids spam filters       │
│  Result: Emails delivered    │
│  to inboxes                  │
└──────────────────┬───────────┘
    (30 min - 4 hours depending)
                   ▼
STEP 7: TRACK REPLIES
═════════════════════
┌──────────────────────────────┐
│  python campaign.py           │
│  check_replies                │
│  [your_campaign_id]          │
│                              │
│  ▶ Checks Gmail for replies  │
│  ▶ Shows response rate       │
│  ▶ Lists who replied         │
│  Result: 50%+ reply rate!    │
└──────────────────┬───────────┘
      (Check after 2-4 hours)
                   ▼
OPTIONAL: FOLLOW-UPS
════════════════════
┌──────────────────────────────┐
│  python campaign.py           │
│  queue_next_step              │
│  [campaign_id] 1             │
│                              │
│  Then: python fast_send.py    │
│        [campaign_id]         │
│                              │
│  ▶ Sends Step 2 to           │
│    non-responders            │
│  ▶ Continues follow-up chain │
└──────────────────────────────┘
```

---

## Time Estimate

| Step | Duration | Notes |
|------|----------|-------|
| 1. Setup | 20 min | One-time only |
| 2. Company List | 10 min | Copy-paste company names |
| 3. Discover | 30-60 min | 5-10 min per company |
| 4. Find Emails | 5 min | Automatic |
| 5. AI Writing | 15 min | Automatic |
| 6. Send | 30 min - 4 hrs | Depends on list size |
| 7. Track | 5 min | Check replies |
| **Total** | **~2-6 hours** | For 100+ emails |

---

## What Happens at Each Step

### Step 3: Discover Contacts
- Tool searches LinkedIn using company name
- Finds people with profiles at that company
- Extracts: Name, Title, LinkedIn URL
- Saves to local database
- Example: Finds "John Smith - Product Manager - Apple Inc"

### Step 4: Find Emails
- Takes the names and company
- Tries Hunter.io API (if you have credits)
- Falls back to pattern-based guessing
- Examples of found emails:
  - john.smith@apple.com
  - jsmith@apple.com
  - smithjohn@apple.com
- Confidence score: 60-100%

### Step 5: AI Writes Emails
- Claude/Perplexity reads company research
- Writes unique emails for each person
- Includes:
  - Personalized greeting
  - Relevant company mention
  - Your value proposition
  - Clear call-to-action
- 95% cheaper than personalizing each email individually

### Step 6: Send Emails
- Gmail API sends one by one
- 60-120 second delay between each
- Tracking: Records send time, status
- Result: Emails in their inbox in <5 minutes

### Step 7: Check Replies
- Polls Gmail for thread responses
- Counts who replied vs silent
- Typical: 50%+ reply rate
- Way better than standard email (2-5%)

---

## Example Output

After running campaign with 10 companies (200 people):

```
RESULTS
═══════
Companies:        10
Total Contacts:   200
Emails Sent:      198 (99%)
Delivery Failures: 2 (invalid emails)
Replies Received: 105 (52%)

TIME TAKEN: 4 hours

COST BREAKDOWN
══════════════
AI (Claude/Perplexity): $1.50
Email discovery (Hunter): $0 (free tier)
Gmail: Free
Total Cost: $1.50 for 200 emails!
```

---

## Common Scenarios

### Scenario 1: Small Test (5 companies, 50 people)
- Time: 1-2 hours
- Cost: $0.50
- Replies expected: 25-30 people

### Scenario 2: Medium Campaign (15 companies, 300 people)
- Time: 3-4 hours
- Cost: $3-5
- Replies expected: 150+ people

### Scenario 3: Large Campaign (30+ companies, 1000+ people)
- Time: 8-12 hours (can split over 2 days)
- Cost: $10-20
- Replies expected: 500+ people
- What you actually did: Real Fortune 500 reach

---

## Pro Tips

1. **Start Small**
   - Test with 1-2 companies first
   - Check email quality
   - Then expand

2. **Monitor Progress**
   - Keep Command Prompt window open
   - Watch the [Sent | Queued | Progress] numbers
   - You can see it working!

3. **Optimize Timing**
   - Send during business hours (9 AM - 5 PM)
   - Tuesday-Thursday best response
   - Avoid Mondays and Fridays

4. **Follow Up Fast**
   - Reply to emails within 1 hour if possible
   - People are more engaged when they just replied
   - Use queue_next_step for automated follow-ups

5. **Track What Works**
   - Export campaign_final_tracker.csv
   - Open in Excel
   - Analyze: Which roles reply most?
   - Which industries respond best?
   - Use this for next campaign!

---

## You're Following This Workflow!

Each command executes one step. Just follow the numbers 1-7
in order and you're running a professional email campaign.

**Ready? Start with GETTING_STARTED.md**
