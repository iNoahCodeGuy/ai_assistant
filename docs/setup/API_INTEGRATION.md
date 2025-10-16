# Next.js API Integration Setup

## Overview
Vercel serverless functions now connect the Next.js frontend to the LangGraph backend.

## API Endpoints Created

✅ **POST /api/chat** - Execute conversation flow
✅ **POST /api/email** - Send resume/LinkedIn via Resend
✅ **POST /api/feedback** - Log ratings and contact requests
✅ **POST /api/confess** - Handle confession submissions

## Quick Start

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Set Environment Variables
```bash
vercel env add OPENAI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_KEY
vercel env add RESEND_API_KEY
vercel env add TWILIO_ACCOUNT_SID
vercel env add TWILIO_AUTH_TOKEN
vercel env add TWILIO_FROM
vercel env add LANGCHAIN_API_KEY
```

### 3. Test Locally
```bash
# Start local dev server
vercel dev

# In another terminal, run tests
python scripts/test_api_endpoints.py
```

### 4. Deploy to Production
```bash
vercel --prod
```

## Frontend Integration

### Chat Component Example
```typescript
// components/Chat.tsx
async function sendMessage(query: string, role: string) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      role,
      session_id: sessionId,
      chat_history: chatHistory,
      user_email: userEmail,
      user_name: userName
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Display answer
    setMessages([...messages, {
      role: 'assistant',
      content: data.answer
    }]);
    
    // Handle actions
    if (data.actions_taken.includes('send_resume')) {
      showResumeConfirmation();
    }
  }
}
```

### Email Request Example
```typescript
// components/ResumeButton.tsx
async function requestResume() {
  const response = await fetch('/api/email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type: 'resume',
      to_email: userEmail,
      to_name: userName,
      message: 'Requested via chat'
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    alert('Resume sent! Check your email.');
  }
}
```

### Feedback Form Example
```typescript
// components/FeedbackForm.tsx
async function submitFeedback(rating: number, comment: string, contactRequested: boolean) {
  const response = await fetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message_id: lastMessageId,
      rating,
      comment,
      contact_requested: contactRequested,
      user_email: userEmail,
      user_name: userName,
      user_phone: userPhone
    })
  });
  
  const data = await response.json();
  alert(data.message);
}
```

### Confession Form Example
```typescript
// components/ConfessionForm.tsx
async function submitConfession(message: string, isAnonymous: boolean, contactInfo?: any) {
  const response = await fetch('/api/confess', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      is_anonymous: isAnonymous,
      ...(isAnonymous ? {} : contactInfo)
    })
  });
  
  const data = await response.json();
  alert(data.message);
}
```

## Error Handling

All endpoints return consistent error format:
```json
{
  "success": false,
  "error": "Error message"
}
```

Always check `data.success` before processing response.

## Rate Limiting

Consider implementing rate limiting for production:

```typescript
// middleware/rateLimit.ts
import rateLimit from 'express-rate-limit';

export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests, please try again later.'
});
```

## Security

1. **CORS**: Update CORS headers in production to restrict origins
2. **API Keys**: Never expose API keys client-side
3. **Input Validation**: All endpoints validate required fields
4. **Rate Limiting**: Implement for production
5. **Authentication**: Add JWT/session auth if needed

## Monitoring

- View Vercel function logs in dashboard
- LangSmith traces for conversation flow
- Supabase logs for database operations
- Set up alerts for errors

## Next Steps

1. ✅ API endpoints created
2. 🔲 Build Next.js frontend components
3. 🔲 Add authentication (optional)
4. 🔲 Implement rate limiting
5. 🔲 Add monitoring/alerting
6. 🔲 Deploy to production

---

**Status**: API integration complete! Ready for frontend development.
