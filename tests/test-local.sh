#!/bin/bash

# Test the application locally before deployment
# Usage: ./test-local.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing FastAPI Video Narratives App Locally${NC}"
echo ""

# Test 1: Check if Docker build works
echo -e "${YELLOW}🐳 Testing Docker build...${NC}"
if docker build -t video-narratives-test . > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker build successful${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Test 2: Run Docker container locally
echo -e "${YELLOW}🚀 Starting Docker container...${NC}"
CONTAINER_ID=$(docker run -d -p 8080:8080 -e PORT=8080 -e ENVIRONMENT=test video-narratives-test)

# Wait for container to start
sleep 5

# Test 3: Health check
echo -e "${YELLOW}❤️  Testing health endpoint...${NC}"
if curl -s http://localhost:8080/health > /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    docker stop $CONTAINER_ID > /dev/null
    docker rm $CONTAINER_ID > /dev/null
    exit 1
fi

# Test 4: Test main UI endpoint
echo -e "${YELLOW}🎯 Testing main UI endpoint...${NC}"
if curl -s http://localhost:8080/ > /dev/null; then
    echo -e "${GREEN}✅ Main UI endpoint accessible${NC}"
else
    echo -e "${RED}❌ Main UI endpoint failed${NC}"
    docker stop $CONTAINER_ID > /dev/null
    docker rm $CONTAINER_ID > /dev/null
    exit 1
fi

# Test 5: Test API endpoint
echo -e "${YELLOW}📊 Testing API endpoint...${NC}"
RESPONSE=$(curl -s -w "%{http_code}" http://localhost:8080/random-narrative-for-user/testuser)
HTTP_CODE=${RESPONSE: -3}
if [[ $HTTP_CODE == "200" || $HTTP_CODE == "404" ]]; then
    echo -e "${GREEN}✅ API endpoint responding correctly${NC}"
else
    echo -e "${RED}❌ API endpoint failed (HTTP $HTTP_CODE)${NC}"
    docker stop $CONTAINER_ID > /dev/null
    docker rm $CONTAINER_ID > /dev/null
    exit 1
fi

# Cleanup
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null
docker rmi video-narratives-test > /dev/null

echo ""
echo -e "${GREEN}🎉 All tests passed! Your app is ready for Cloud Run deployment.${NC}"
echo ""
echo -e "${BLUE}📝 To deploy to Cloud Run:${NC}"
echo -e "${BLUE}1. Set your GCP project: export PROJECT_ID=your-project-id${NC}"
echo -e "${BLUE}2. Run deployment: ./deploy.sh \$PROJECT_ID${NC}"
echo ""
echo -e "${BLUE}🔗 Your app will be accessible via HTTPS on Cloud Run${NC}"
echo -e "${BLUE}✨ JavaScript API calls are already configured for HTTPS${NC}"
