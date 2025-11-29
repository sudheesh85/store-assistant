# Deploying Store Assistant to Azure App Service

Since `az acr build` is restricted on your subscription, we will use **Azure App Service**. This method deploys your code directly and builds it on Azure, without needing Docker or ACR Tasks.

## Prerequisites

1.  **Azure CLI**: You already have this.
2.  **Login**: Ensure you are logged in (`az login`).

## Step 1: Set Variables

Run these commands in your terminal to set up names for your services.

```bash
RESOURCE_GROUP="store-assistant-rg"
LOCATION="centralindia"
BACKEND_APP_NAME="store-backend-$RANDOM"
FRONTEND_APP_NAME="store-frontend-$RANDOM"
PLAN_NAME="store-plan"
```

## Step 2: Create a Resource Group

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

## Step 3: Create an App Service Plan

We will create a Linux plan. `B1` is a basic paid tier. If you want free, use `F1` (but it may be slow or limited).

```bash
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux
```

## Step 4: Deploy Backend (Python)

We will deploy the Python code from the `backend` folder.

1.  Create the Web App:

```bash
az webapp create \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --runtime "PYTHON:3.11"
```

2.  Configure the Startup Command:

```bash
az webapp config set \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port 8000"
```

3.  Deploy the code:

```bash
# 1. Enable build during deployment
az webapp config appsettings set --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

# 2. Zip and deploy the backend folder
cd backend
az webapp up --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --runtime "PYTHON:3.11"
cd ..
```
*Note: `az webapp up` might take a few minutes as it packages and builds your Python dependencies.*

4.  **Get the Backend URL**:
    The output will show a URL like `https://store-backend-1234.azurewebsites.net`. **Copy this URL.**

## Step 5: Deploy Frontend (Next.js)

1.  Create the Web App:

```bash
az webapp create \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --runtime "NODE:20-lts"
```

2.  Set the Backend URL Environment Variable:
    Replace `<BACKEND_URL>` with the URL you copied in Step 4 (e.g., `https://store-backend-1234.azurewebsites.net`). Add `/api/v1` to the end.

```bash
# Example: https://store-backend-1234.azurewebsites.net/api/v1
BACKEND_API_URL="<YOUR_BACKEND_URL>/api/v1"

az webapp config appsettings set \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings NEXT_PUBLIC_API_URL=$BACKEND_API_URL
```

3.  Deploy the code:

```bash
# 1. Enable build during deployment
az webapp config appsettings set --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

# 2. Deploy the code
cd frontend
az webapp up --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --runtime "NODE:20-lts"
cd ..
```
*Note: This will trigger a build on Azure. Since we set the App Setting beforehand, Next.js should pick up the API URL.*

## Step 6: Configure Backend API Key

Finally, give the backend your OpenAI API Key.

```bash
az webapp config appsettings set \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings OPENAI_API_KEY="your-openai-key-here"
```

## Step 7: Access the App

Open the Frontend URL in your browser!
