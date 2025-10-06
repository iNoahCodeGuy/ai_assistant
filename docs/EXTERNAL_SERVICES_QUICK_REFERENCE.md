# External Services Quick Reference Card

## 🚀 Quick Start

```bash
# Install dependencies
pip install resend twilio

# Configure environment variables
cat >> .env << EOF
# Resend (Email)
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=noah@yourdomain.com
ADMIN_EMAIL=noah@personal-email.com

# Twilio (SMS)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1-555-0123
ADMIN_PHONE_NUMBER=+1-555-0456
EOF

# Run setup
python scripts/setup_external_services.py
```

---

## 📦 Storage Service

```python
from services import get_storage_service

storage = get_storage_service()

# Upload files
resume_path = storage.upload_resume('data/resume.pdf')
headshot_url = storage.upload_headshot('data/headshot.jpg')

# Get signed URL (temporary access)
signed_url = storage.get_signed_url(resume_path, expires_in=86400)

# List files
files = storage.list_files('resumes')

# Delete file
storage.delete_file('resumes/old_resume.pdf')

# Health check
status = storage.health_check()
```

---

## 📧 Email Service (Resend)

```python
from services import get_resend_service

resend = get_resend_service()

# Contact notification
resend.send_contact_notification(
    from_name="Jane Doe",
    from_email="jane@company.com",
    message="Interested in role",
    user_role="Hiring Manager (technical)",
    phone="+1-555-0123"
)

# Resume delivery
resend.send_resume_email(
    to_email="recruiter@company.com",
    to_name="Jane Doe",
    resume_url="https://supabase.co/storage/...",
    message="Thank you for your interest!"
)

# Welcome email
resend.send_welcome_email(
    to_email="jane@company.com",
    to_name="Jane"
)

# Health check
status = resend.health_check()
```

---

## 📱 SMS Service (Twilio)

```python
from services import get_twilio_service

twilio = get_twilio_service()

# Contact alert
twilio.send_contact_alert(
    from_name="Jane Doe",
    from_email="jane@company.com",
    message_preview="Interested in senior role...",
    is_urgent=True
)

# Hiring manager alert
twilio.send_hiring_manager_alert(
    company_name="Google",
    contact_name="Jane Smith",
    interest_level="high"
)

# System alert
twilio.send_system_alert(
    alert_type="database_error",
    message="Vector search failing",
    severity="critical"
)

# Check delivery status
status = twilio.get_message_status(message_sid)

# Health check
status = twilio.health_check()
```

---

## 🔧 Common Patterns

### Complete Contact Flow

```python
from services import get_storage_service, get_resend_service, get_twilio_service

def handle_contact_form(name, email, message, role, request_resume=False):
    """Process contact form submission."""
    
    # 1. Send email notification
    resend = get_resend_service()
    resend.send_contact_notification(
        from_name=name,
        from_email=email,
        message=message,
        user_role=role
    )
    
    # 2. Send SMS for urgent contacts
    if "Hiring Manager" in role:
        twilio = get_twilio_service()
        twilio.send_contact_alert(
            from_name=name,
            from_email=email,
            message_preview=message[:100],
            is_urgent=True
        )
    
    # 3. Send welcome email
    resend.send_welcome_email(to_email=email, to_name=name)
    
    # 4. Send resume if requested
    if request_resume:
        storage = get_storage_service()
        resume_path = 'resumes/noah_resume_latest.pdf'
        signed_url = storage.get_signed_url(resume_path, expires_in=86400)
        
        resend.send_resume_email(
            to_email=email,
            to_name=name,
            resume_url=signed_url
        )
```

### Service Health Check

```python
def check_all_services():
    """Check health of all external services."""
    from services import StorageService, ResendService, TwilioService
    
    services = {
        'storage': StorageService().health_check(),
        'email': ResendService().health_check(),
        'sms': TwilioService().health_check()
    }
    
    all_healthy = all(
        s['status'] == 'healthy' 
        for s in services.values()
    )
    
    return {'all_healthy': all_healthy, 'services': services}
```

---

## 🐛 Troubleshooting

### Storage Issues

```python
# Check bucket access
storage = get_storage_service()
print(storage.health_check())

# List files to verify upload
files = storage.list_files()
print(f"Files: {len(files)}")

# Test upload
path = storage.upload_file(
    'test.txt',
    bucket='private',
    destination_path='test/test.txt'
)
print(f"Uploaded: {path}")
```

### Email Issues

```bash
# Check Resend dashboard
# https://resend.com/emails

# Verify domain
# https://resend.com/domains

# Test API key
python -c "
import os
print('API Key:', os.getenv('RESEND_API_KEY')[:10] + '...')
"
```

### SMS Issues

```bash
# Check Twilio console
# https://console.twilio.com

# Verify phone numbers
python -c "
import os
print('From:', os.getenv('TWILIO_PHONE_NUMBER'))
print('To:', os.getenv('ADMIN_PHONE_NUMBER'))
"

# Check account balance
# Free trial credit should show in console
```

---

## 💰 Cost Tracking

### Free Tier Limits

| Service | Free Tier | Overage Cost |
|---------|-----------|--------------|
| Supabase Storage | 1 GB | $0.021/GB |
| Resend | 3,000 emails/month | $20/50k emails |
| Twilio SMS | $15 trial credit | $0.0079/SMS (US) |

### Monthly Budget Estimates

| Usage Level | Storage | Email | SMS | Total |
|-------------|---------|-------|-----|-------|
| MVP | $0 | $0 | $2 | $2 |
| Light | $0 | $0 | $8 | $8 |
| Medium | $2 | $20 | $20 | $42 |
| Heavy | $10 | $40 | $50 | $100 |

---

## 📚 Resources

### Documentation
- Storage: https://supabase.com/docs/guides/storage
- Resend: https://resend.com/docs
- Twilio: https://www.twilio.com/docs/sms

### Dashboards
- Supabase: https://supabase.com/dashboard
- Resend: https://resend.com/emails
- Twilio: https://console.twilio.com

### Support
- Supabase: https://supabase.com/support
- Resend: support@resend.com
- Twilio: https://support.twilio.com

---

## ✅ Checklist

- [ ] Supabase storage buckets created
- [ ] Resume and headshot uploaded
- [ ] Resend account setup and domain verified
- [ ] Twilio account setup and phone number purchased
- [ ] Environment variables configured
- [ ] Setup script run successfully
- [ ] Test email sent and received
- [ ] Test SMS sent and received
- [ ] Health checks passing
- [ ] Integration tested in app

---

**Quick Help**: Run `python scripts/setup_external_services.py` to verify all services
