#!/bin/bash
# scripts/verify_deployment.sh
# Post-deployment smoke tests for Vercel production environment
# Usage: ./scripts/verify_deployment.sh [VERCEL_URL]

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEPLOYMENT_URL="${1:-https://your-app.vercel.app}"
SESSION_ID="smoke-test-$(date +%s)"

echo -e "${BLUE}🔍 Vercel Deployment Verification${NC}"
echo -e "${BLUE}URL: ${YELLOW}${DEPLOYMENT_URL}${NC}"
echo ""

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check Endpoint${NC}"
HEALTH_RESPONSE=$(curl -s "${DEPLOYMENT_URL}/api/health" || echo "FAILED")

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "$HEALTH_RESPONSE"
    exit 1
fi
echo ""

# Test 2: Chat Endpoint (Software Developer Role)
echo -e "${BLUE}Test 2: Chat Endpoint - Software Developer${NC}"
CHAT_RESPONSE=$(curl -s -X POST "${DEPLOYMENT_URL}/api/chat" \
    -H "Content-Type: application/json" \
    -d "{
        \"role\": \"Software Developer\",
        \"query\": \"What Python frameworks have you used?\",
        \"session_id\": \"${SESSION_ID}-dev\"
    }" || echo "FAILED")

if echo "$CHAT_RESPONSE" | grep -q "answer"; then
    echo -e "${GREEN}✅ Chat endpoint passed${NC}"
    echo "$CHAT_RESPONSE" | jq '.answer' 2>/dev/null || echo "$CHAT_RESPONSE"
else
    echo -e "${RED}❌ Chat endpoint failed${NC}"
    echo "$CHAT_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Chat Endpoint (Hiring Manager Role)
echo -e "${BLUE}Test 3: Chat Endpoint - Hiring Manager${NC}"
CHAT_RESPONSE_HM=$(curl -s -X POST "${DEPLOYMENT_URL}/api/chat" \
    -H "Content-Type: application/json" \
    -d "{
        \"role\": \"Hiring Manager (nontechnical)\",
        \"query\": \"Tell me about your career background\",
        \"session_id\": \"${SESSION_ID}-hm\"
    }" || echo "FAILED")

if echo "$CHAT_RESPONSE_HM" | grep -q "answer"; then
    echo -e "${GREEN}✅ Hiring Manager role passed${NC}"
    echo "$CHAT_RESPONSE_HM" | jq '.answer' 2>/dev/null || echo "$CHAT_RESPONSE_HM"
else
    echo -e "${RED}❌ Hiring Manager role failed${NC}"
    echo "$CHAT_RESPONSE_HM"
    exit 1
fi
echo ""

# Test 4: Feedback Endpoint
echo -e "${BLUE}Test 4: Feedback Endpoint${NC}"
FEEDBACK_RESPONSE=$(curl -s -X POST "${DEPLOYMENT_URL}/api/feedback" \
    -H "Content-Type: application/json" \
    -d "{
        \"session_id\": \"${SESSION_ID}\",
        \"rating\": 5,
        \"comment\": \"Smoke test - deployment verification\",
        \"helpful\": true
    }" || echo "FAILED")

if echo "$FEEDBACK_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ Feedback endpoint passed${NC}"
    echo "$FEEDBACK_RESPONSE" | jq '.' 2>/dev/null || echo "$FEEDBACK_RESPONSE"
else
    echo -e "${RED}❌ Feedback endpoint failed${NC}"
    echo "$FEEDBACK_RESPONSE"
    exit 1
fi
echo ""

# Test 5: Email Endpoint (if configured)
echo -e "${BLUE}Test 5: Email Endpoint (Optional)${NC}"
EMAIL_RESPONSE=$(curl -s -X POST "${DEPLOYMENT_URL}/api/email" \
    -H "Content-Type: application/json" \
    -d "{
        \"session_id\": \"${SESSION_ID}\",
        \"recipient_email\": \"test@example.com\",
        \"subject\": \"Smoke Test\",
        \"message\": \"Deployment verification\"
    }" || echo "FAILED")

if echo "$EMAIL_RESPONSE" | grep -q "success\|unavailable"; then
    echo -e "${GREEN}✅ Email endpoint passed (or gracefully degraded)${NC}"
    echo "$EMAIL_RESPONSE" | jq '.' 2>/dev/null || echo "$EMAIL_RESPONSE"
else
    echo -e "${YELLOW}⚠️  Email endpoint warning (non-critical)${NC}"
    echo "$EMAIL_RESPONSE"
fi
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All critical smoke tests passed!${NC}"
echo ""
echo -e "${BLUE}Deployment URL:${NC} ${YELLOW}${DEPLOYMENT_URL}${NC}"
echo -e "${BLUE}Session ID:${NC} ${SESSION_ID}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Verify custom domain DNS propagation"
echo "2. Test frontend UI manually"
echo "3. Check Vercel logs: vercel logs --prod"
echo "4. Monitor LangSmith for traces"
echo "5. Review Supabase analytics: SELECT * FROM messages LIMIT 10;"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

exit 0
