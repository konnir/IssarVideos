# 🚀 GCP Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud SDK** installed and configured

   ```bash
   # Install gcloud CLI (if not already installed)
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   ```

2. **Docker** installed for local testing
3. **GCP Project** with billing enabled

## Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# 1. Set your project ID
export PROJECT_ID="your-gcp-project-id"

# 2. Test locally first (optional but recommended)
./test-local.sh

# 3. Deploy to Cloud Run
./deploy.sh $PROJECT_ID
```

### Option 2: Manual Deployment

```bash
# 1. Set project and enable APIs
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com

# 2. Build and deploy
gcloud builds submit --config cloudbuild.yaml

# 3. Get service URL
gcloud run services describe video-narratives --region=us-central1 --format="value(status.url)"
```

## 🔧 Configuration

### Environment Variables

The app uses these environment variables in production:

- `PORT`: Cloud Run sets this automatically (8080)
- `ENVIRONMENT`: Set to "production" for Cloud Run
- `NARRATIVES_DB_PATH`: Database file path
- `DATABASE_URL`: SQLite database URL (fallback)

### Resource Limits

Current Cloud Run configuration:

- **CPU**: 1 vCPU
- **Memory**: 512 MB
- **Timeout**: 300 seconds
- **Concurrency**: 80 requests per instance
- **Scaling**: 0-10 instances

## 🌐 HTTPS Compatibility

✅ **Your JavaScript is already HTTPS-ready!**

The `tagger.js` file uses:

- `window.location.origin` for protocol-agnostic URLs
- `apiCall()` utility function for consistent API calls
- Automatic HTTPS support when deployed to Cloud Run

## 📊 Monitoring & Health Checks

### Health Endpoint

- **URL**: `https://your-service-url/health`
- **Response**: `{"status": "healthy", "service": "video-narratives"}`

### Cloud Run Health Checks

- **Startup Probe**: `/health` endpoint
- **Liveness Probe**: `/health` endpoint
- **Readiness**: Automatic based on container startup

## 🎯 Application URLs

After deployment, your app will be available at:

- **Main UI**: `https://your-service-url/`
- **Tagger Interface**: `https://your-service-url/tagger`
- **Health Check**: `https://your-service-url/health`
- **API Docs**: `https://your-service-url/docs`

## 🔐 Security

### HTTPS

- ✅ Automatic HTTPS termination by Cloud Run
- ✅ JavaScript API calls work with both HTTP and HTTPS
- ✅ Secure headers and CORS configured

### Authentication

- Currently allows unauthenticated access
- To add authentication, modify `cloudbuild.yaml` and remove `--allow-unauthenticated`

## 📈 Scaling

### Automatic Scaling

- **Min instances**: 0 (scales to zero)
- **Max instances**: 10
- **CPU throttling**: Enabled for cost optimization

### Manual Scaling Adjustments

```bash
# Update scaling settings
gcloud run services update video-narratives \
  --region=us-central1 \
  --min-instances=1 \
  --max-instances=20
```

## 🐛 Troubleshooting

### Common Issues

1. **Build Fails**

   ```bash
   # Check build logs
   gcloud builds list --limit=5
   gcloud builds log BUILD_ID
   ```

2. **Service Won't Start**

   ```bash
   # Check service logs
   gcloud run services logs read video-narratives --region=us-central1
   ```

3. **Database Issues**
   - The app uses SQLite stored in the container
   - Data persists only during container lifetime
   - For persistent data, consider Cloud SQL or Cloud Storage

### Local Testing

```bash
# Test Docker build
docker build -t video-narratives .

# Test locally
docker run -p 8080:8080 -e PORT=8080 video-narratives

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/
```

## 💰 Cost Optimization

### Current Configuration

- **CPU allocation**: Only during request processing
- **Memory**: 512 MB (adjust based on usage)
- **Scale to zero**: Enabled (no charges when idle)

### Monitoring Costs

```bash
# View service details
gcloud run services describe video-narratives --region=us-central1

# Monitor usage
gcloud run services list
```

## 🔄 Updates & CI/CD

### Manual Updates

```bash
# Redeploy after changes
./deploy.sh $PROJECT_ID
```

### Automated CI/CD

The `cloudbuild.yaml` is ready for:

- GitHub integration
- Automatic deployments on push
- Multiple environment support

## 📞 Support

### Useful Commands

```bash
# Service status
gcloud run services list

# Service logs
gcloud run services logs read video-narratives --region=us-central1

# Service details
gcloud run services describe video-narratives --region=us-central1

# Delete service
gcloud run services delete video-narratives --region=us-central1
```

---

🎉 **Your FastAPI Video Narratives app is now ready for production deployment on Google Cloud Run with full HTTPS support!**
