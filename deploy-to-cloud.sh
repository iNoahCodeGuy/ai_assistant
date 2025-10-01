#!/bin/bash

# Google Cloud deployment script for Noah's AI Assistant
# This script sets up the complete cloud infrastructure

set -e

# Configuration
PROJECT_ID="noah-ai-assistant"
REGION="us-central1"
SERVICE_NAME="noah-ai-assistant"
DB_INSTANCE_NAME="noah-analytics-db"
REDIS_INSTANCE_NAME="noah-cache"

echo "🚀 Starting Google Cloud deployment for Noah's AI Assistant"

# Set project
echo "📋 Setting Google Cloud project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudsql.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    pubsub.googleapis.com \
    redis.googleapis.com \
    aiplatform.googleapis.com \
    storage.googleapis.com

# Create Cloud SQL instance
echo "🗄️ Creating Cloud SQL PostgreSQL instance..."
gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --database-flags=log_statement=all || echo "Database instance may already exist"

# Create database
echo "📊 Creating analytics database..."
gcloud sql databases create noah_analytics --instance=$DB_INSTANCE_NAME || echo "Database may already exist"

# Create database user
echo "👤 Creating database user..."
gcloud sql users create analytics_user \
    --instance=$DB_INSTANCE_NAME \
    --password=$(openssl rand -base64 32) || echo "User may already exist"

# Create Redis instance (Memorystore)
echo "🔄 Creating Redis Memorystore instance..."
gcloud redis instances create $REDIS_INSTANCE_NAME \
    --size=1 \
    --region=$REGION \
    --redis-version=redis_6_x \
    --tier=basic || echo "Redis instance may already exist"

# Create Pub/Sub topic
echo "📡 Creating Pub/Sub topic for analytics events..."
gcloud pubsub topics create analytics-events || echo "Topic may already exist"

# Create service account
echo "🔐 Creating service account..."
gcloud iam service-accounts create noah-ai-service-account \
    --display-name="Noah AI Assistant Service Account" || echo "Service account may already exist"

# Grant necessary permissions
echo "🔑 Granting permissions to service account..."
SERVICE_ACCOUNT_EMAIL="noah-ai-service-account@$PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.objectViewer"

# Create secrets in Secret Manager
echo "🔒 Creating secrets in Secret Manager..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Please set OPENAI_API_KEY environment variable"
    exit 1
fi

echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=- || echo "Secret may already exist"

# Generate and store database password
DB_PASSWORD=$(openssl rand -base64 32)
echo -n "$DB_PASSWORD" | gcloud secrets create db-password --data-file=- || echo "Secret may already exist"

# Set database user password
gcloud sql users set-password analytics_user \
    --instance=$DB_INSTANCE_NAME \
    --password="$DB_PASSWORD"

# Create Artifact Registry repository
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create noah-ai-repo \
    --repository-format=docker \
    --location=$REGION || echo "Repository may already exist"

# Build and push Docker image
echo "🐳 Building and pushing Docker image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."

# Get Cloud SQL connection name
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)")

# Get Redis IP
REDIS_IP=$(gcloud redis instances describe $REDIS_INSTANCE_NAME --region=$REGION --format="value(host)")

gcloud run deploy $SERVICE_NAME \
    --image=gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --platform=managed \
    --region=$REGION \
    --service-account=$SERVICE_ACCOUNT_EMAIL \
    --set-cloudsql-instances=$CONNECTION_NAME \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,DATABASE_NAME=noah_analytics,DB_USER=analytics_user,REDIS_HOST=$REDIS_IP" \
    --allow-unauthenticated \
    --memory=4Gi \
    --cpu=2 \
    --concurrency=100 \
    --max-instances=10 \
    --min-instances=1

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "🎉 Deployment complete!"
echo ""
echo "📊 Cloud Resources Created:"
echo "  • Cloud SQL Instance: $DB_INSTANCE_NAME"
echo "  • Redis Instance: $REDIS_INSTANCE_NAME"
echo "  • Cloud Run Service: $SERVICE_NAME"
echo "  • Pub/Sub Topic: analytics-events"
echo ""
echo "🌐 Application URL: $SERVICE_URL"
echo ""
echo "🔧 Next steps:"
echo "  1. Test the application at $SERVICE_URL"
echo "  2. Set up monitoring and alerting"
echo "  3. Configure custom domain (optional)"
echo "  4. Set up CI/CD pipeline"
echo ""
echo "💾 Important:"
echo "  • Database password stored in Secret Manager as 'db-password'"
echo "  • OpenAI API key stored in Secret Manager as 'openai-api-key'"
echo "  • Monitor costs in the Google Cloud Console"