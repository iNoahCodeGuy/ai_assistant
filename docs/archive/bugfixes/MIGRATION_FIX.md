# 🚀 Quick Fix Guide: Run Migration 002

Your verification shows that **Migration 002 is needed** to fix the failing API endpoints.

## Current Status

✅ **Working**:
- `/api/chat` - Fully functional
- Database tables from Migration 001 (kb_chunks, messages, feedback, etc.)

❌ **Broken** (Missing tables):
- `/api/confess` - Needs `confessions` table
- `/api/feedback` - May need updated `feedback` columns
- `/api/email` - Needs `sms_logs` table

## How to Fix (5 minutes)

### Step 1: Open Supabase SQL Editor

1. Go to: https://app.supabase.com
2. Select your project: `tjnlusesinzzlwvlbnnm`
3. Click **"SQL Editor"** in left sidebar
4. Click **"New Query"** button

### Step 2: Run Migration 002

1. Open the file: `supabase/migrations/002_add_confessions_and_sms.sql`
2. **Copy all contents** (it's safe, uses `IF NOT EXISTS`)
3. **Paste** into Supabase SQL Editor
4. Click **"Run"** (or press Cmd/Ctrl + Enter)

You should see: `Success. No rows returned`

### Step 3: Verify Tables Created

Run this query in SQL Editor:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('confessions', 'sms_logs')
ORDER BY table_name;
```

Expected output:
```
confessions
sms_logs
```

### Step 4: Verify Locally

Run the verification script:

```bash
python3 scripts/verify_migration.py
```

You should now see:
```
✓ confessions exists (Migration 002)
✓ sms_logs exists (Migration 002)
```

### Step 5: Test Endpoints

```bash
# Test confess endpoint
curl -X POST https://noahsaiassistant.vercel.app/api/confess \
  -H "Content-Type: application/json" \
  -d '{"message": "Testing after migration", "is_anonymous": true}'

# Should return: {"success": true, ...}
```

## What Gets Created

Migration 002 creates:

1. **`confessions` table**
   - Stores anonymous/named crush confessions
   - Columns: id, message, is_anonymous, name, email, phone, created_at
   - RLS policies for privacy

2. **`sms_logs` table**
   - Tracks Twilio SMS notifications
   - Columns: id, event, from_name, from_email, message_preview, status, created_at

3. **Updates to `feedback` table**
   - Adds: user_name, user_phone, user_email columns
   - (If they don't already exist)

4. **Analytics views**
   - `recent_confessions` - Summary of recent confessions
   - `pending_contacts` - Feedback with contact requests

## Troubleshooting

### "relation already exists" error
**Solution**: Safe to ignore - means tables already exist

### "permission denied" error
**Solution**: Make sure you're using the **service_role** key, not anon key

### Still getting 404 errors after migration
**Solution**:
1. Clear Vercel cache: Go to Vercel dashboard → Deployments → Redeploy
2. Wait 30 seconds for deployment
3. Test again

## Need Help?

Run verification again anytime:
```bash
python3 scripts/verify_migration.py
```

Check the complete migration guide:
```bash
cat supabase/migrations/README.md
```

Check Vercel logs:
```bash
vercel logs --follow
```
