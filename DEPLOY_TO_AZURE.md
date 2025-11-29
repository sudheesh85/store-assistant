# Deploying Store Assistant to Azure

This guide explains how to deploy the Store Assistant application (Frontend + Backend) to **Azure Container Apps**.

## Prerequisites

1.  **Azure CLI**: [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
2.  **Docker**: Ensure Docker is running locally.
3.  **Azure Account**: You need an active Azure subscription.

## Step 1: Login to Azure

Open your terminal and run:

```bash
az login
```

## Step 2: Set Variables

Set some variables to make the commands easier to copy-paste.

```bash
RESOURCE_GROUP="store-assistant-rg"
LOCATION="eastus"
ACR_NAME="storeassistantacr$RANDOM" # Must be unique
BACKEND_APP_NAME="store-backend"
FRONTEND_APP_NAME="store-frontend"
ENV_NAME="store-env"
```

## Step 3: Create Resource Group

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

## Step 4: Create Azure Container Registry (ACR)

```bash
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
```

## Step 5: Build and Push Images

**Note:** You do NOT need Docker installed locally for this step. We will build the images directly in Azure.

### Backend

```bash
# Build and Push Backend to Azure ACR
az acr build --registry $ACR_NAME --image backend:latest ./backend
```

### Frontend

**Note:** For the frontend, we need to know the backend URL *before* building if we are baking it in, but Next.js `NEXT_PUBLIC_` variables are often baked at build time. However, with Azure Container Apps, we can use environment variables if we configure Next.js correctly or use server-side calls.

For simplicity, we will deploy the backend first, get its URL, and then rebuild/deploy the frontend.

## Step 6: Create Container Apps Environment

```bash
az containerapp env create --name $ENV_NAME --resource-group $RESOURCE_GROUP --location $LOCATION
```

## Step 7: Deploy Backend

```bash
az containerapp create \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $ACR_NAME.azurecr.io/backend:latest \
  --target-port 8000 \
  --ingress external \
  --query properties.configuration.ingress.fqdn
```

**Copy the output URL**. It will look like `https://store-backend.some-region.azurecontainerapps.io`.

## Step 8: Deploy Frontend

1.  Replace `<BACKEND_URL>` below with the URL you just copied (e.g., `https://store-backend...`).
2.  Build and push the frontend image.

```bash
# Build Frontend with the API URL
az acr build \
  --registry $ACR_NAME \
  --image frontend:latest \
  --build-arg NEXT_PUBLIC_API_URL=<BACKEND_URL>/api/v1 \
  ./frontend
```

3.  Deploy the Frontend Container App.

```bash
az containerapp create \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $ACR_NAME.azurecr.io/frontend:latest \
  --target-port 3000 \
  --ingress external \
  --env-vars NEXT_PUBLIC_API_URL=<BACKEND_URL>/api/v1
```

## Step 9: Configure Environment Variables

You need to set the `OPENAI_API_KEY` for the backend.

```bash
az containerapp update \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars OPENAI_API_KEY=your-key-here
```

## Step 10: Access the App

Run the following to get the frontend URL:

```bash
az containerapp show --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn --output tsv
```

Open that URL in your browser!
