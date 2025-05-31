#!/bin/bash

# Deploy FastAPI Video Narratives App to Google Cloud Run
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="video-narratives"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying FastAPI Video Narratives App to Cloud Run${NC}"
echo -e "${BLUE}Project: $PROJECT_ID${NC}"
echo -e "${BLUE}Region: $REGION${NC}"
echo -e "${BLUE}Service: $SERVICE_NAME${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI not found. Please install Google Cloud SDK.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Not authenticated with gcloud. Running authentication...${NC}"
    gcloud auth login
fi

# Set the project
echo -e "${YELLOW}📋 Setting project to $PROJECT_ID...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy using Cloud Build
echo -e "${YELLOW}🏗️  Building and deploying with Cloud Build...${NC}"
gcloud builds submit --config cloudbuild.yaml \
    --substitutions _DATABASE_URL="sqlite:///./narratives.db"

# Get the service URL
echo -e "${GREEN}✅ Deployment completed!${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo -e "${GREEN}🎉 Your FastAPI Video Narratives App is now live!${NC}"
echo -e "${GREEN}📱 Service URL: $SERVICE_URL${NC}"
echo -e "${GREEN}🔗 Tagger UI: $SERVICE_URL/tagger${NC}"
echo -e "${GREEN}📊 Health Check: $SERVICE_URL/health${NC}"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo -e "${BLUE}1. Test the application: curl $SERVICE_URL/health${NC}"
echo -e "${BLUE}2. Open the UI in your browser: $SERVICE_URL${NC}"
echo -e "${BLUE}3. Set up custom domain (optional)${NC}"
echo -e "${BLUE}4. Configure monitoring and alerts${NC}"
