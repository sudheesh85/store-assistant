# Final Deployment Guide

Follow these steps to deploy the Frontend using Local Git.

## 1. Prepare Azure for Pre-built Deployment
Since we are building locally, we need to tell Azure NOT to build again.

```bash
# 1. Disable Remote Build
az webapp config appsettings set --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --settings SCM_DO_BUILD_DURING_DEPLOYMENT=false

# 2. Set Startup Command
az webapp config set --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --startup-file "node server.js"
```

## 2. Deploy the Pre-built Artifact
I have already prepared a `frontend-deploy.zip` for you which contains the standalone build.

```bash
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $FRONTEND_APP_NAME --src frontend-deploy.zip
```

## 3. Verify
After the command finishes, open your website URL. It should load immediately.
