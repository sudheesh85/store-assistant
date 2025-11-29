# Quick Redeployment Guide

## Backend Deployment

When you make changes to the backend code:

```bash
cd backend

az webapp up \
  --name store-backend-ai \
  --resource-group store-assistant-rg \
  --runtime "PYTHON:3.11"

cd ..
```

**Note**: This will automatically install dependencies and restart the app.

---

## Frontend Deployment

When you make changes to the frontend code:

```bash
cd frontend

# Set the backend URL
export NEXT_PUBLIC_API_URL="https://store-backend-ai.azurewebsites.net/api/v1"

# Build
npm run build

# Prepare standalone package
cp -r .next/static .next/standalone/.next/
cp -r public .next/standalone/

# Zip it
cd .next/standalone
zip -r ../../../frontend-deploy.zip .
cd ../../..

# Deploy
az webapp deployment source config-zip \
  --resource-group store-assistant-rg \
  --name store-frontend-ai \
  --src frontend-deploy.zip
```

---

## Useful Commands

### View Backend Logs
```bash
az webapp log tail --name store-backend-ai --resource-group store-assistant-rg
```

### View Frontend Logs
```bash
az webapp log tail --name store-frontend-ai --resource-group store-assistant-rg
```

### Restart Backend
```bash
az webapp restart --name store-backend-ai --resource-group store-assistant-rg
```

### Restart Frontend
```bash
az webapp restart --name store-frontend-ai --resource-group store-assistant-rg
```

### Check App Status
```bash
az webapp list --resource-group store-assistant-rg --query "[].{Name:name, State:state, URL:defaultHostName}" -o table
```

### Update Environment Variables

**Backend:**
```bash
az webapp config appsettings set \
  --name store-backend-ai \
  --resource-group store-assistant-rg \
  --settings KEY="value"
```

**Frontend:**
```bash
# Note: Frontend env vars are baked into the build, so you need to rebuild and redeploy
export NEXT_PUBLIC_API_URL="https://store-backend-ai.azurewebsites.net/api/v1"
# Then follow frontend deployment steps above
```

---

## Live URLs

- **Frontend**: https://store-frontend-ai.azurewebsites.net
- **Backend API**: https://store-backend-ai.azurewebsites.net/api/v1
- **API Docs**: https://store-backend-ai.azurewebsites.net/docs
- **Backend Health**: https://store-backend-ai.azurewebsites.net/api/v1/health

---

## Resource Group Info

- **Resource Group**: `store-assistant-rg`
- **Region**: `Central India`
- **Plan**: `store-plan` (B1 tier)
