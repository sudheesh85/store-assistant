# 🔍 Debugging "NO_SQL" / "Unable to parse SQL from model output" Error

## What This Error Means

The `-- NO_SQL` error happens when the AI model **intentionally** returns this special marker because:
1. ❌ The question doesn't match the dataset (e.g., asking about inventory but querying sales data)
2. ❌ The question is too vague or ambiguous
3. ❌ The dataset doesn't have the required columns to answer the question
4. ❌ The question cannot be answered with SQL

## 🔧 Step-by-Step Fix

### Step 1: Restart Backend Server

The improved logging was just added, so restart the backend:

```bash
cd backend

# Stop current server (Ctrl+C)
# Then restart:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Verify OpenAI API Key

Check that your `.env` file has a valid API key:

```bash
cd backend
cat .env | grep OPENAI_API_KEY
```

Should show: `OPENAI_API_KEY=sk-proj-...` (not the placeholder)

### Step 3: Check Which Dataset You're Using

**In the Frontend:**
- Look at the header: "Querying: **{dataset_type}** data"
- Use the dropdown (sidebar or mobile header) to select the correct dataset

**Available Datasets:**
- **sales** - for revenue, transactions, products sold
- **inventory** - for stock levels, products, suppliers
- **staff** - for employees, roles, shifts

### Step 4: Match Your Question to the Dataset

| Question Type | Select Dataset |
|--------------|----------------|
| "How many products in stock?" | **Inventory** |
| "Show items below reorder level" | **Inventory** |
| "What is total revenue?" | **Sales** |
| "Top selling products?" | **Sales** |
| "How many staff members?" | **Staff** |
| "Who works night shift?" | **Staff** |

### Step 5: Test with Known Good Questions

Use these questions that are guaranteed to work:

**For Inventory Dataset:**
```
- "How many products are in the inventory?"
- "Show all products"
- "What products are low on stock?"
- "List products by category"
```

**For Sales Dataset:**
```
- "What is the total revenue?"
- "Show all sales"
- "Which products were sold?"
- "Total sales by date"
```

**For Staff Dataset:**
```
- "How many staff members do we have?"
- "List all employees"
- "Who are the store managers?"
- "Show staff by role"
```

### Step 6: Watch the Backend Logs

In a separate terminal, watch the logs in real-time:

```bash
cd backend
tail -f storage/logs/backend.log
```

Look for these lines:
```
Processing question: '<your question>' | Requested dataset_type: <type> | Resolved dataset: <type>
Generating SQL for question: '<your question>' | Dataset: <type> | Table: <table_name>
```

If you see "Failed to extract SQL from LLM output: -- NO_SQL", check:
1. Does the question match the dataset?
2. Is the dataset_type what you expect?

### Step 7: Test via API (Bypass Frontend)

Use the test script to verify the backend is working:

```bash
cd backend
./test_api.sh
```

This will test all three datasets with appropriate questions.

### Step 8: Clear Browser Cache

The frontend changes might not have loaded. Try:
1. Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)
2. Or clear browser cache
3. Or restart the frontend dev server

## 🐛 Common Issues

### Issue 1: Frontend Not Sending Dataset Type

**Symptom:** Logs show `Requested dataset_type: None` or wrong type

**Fix:**
1. Make sure frontend server is running with latest code
2. Refresh browser with hard reload
3. Check the dropdown actually changes when you select

### Issue 2: Wrong Dataset Being Selected

**Symptom:** You select "Inventory" but logs show "sales"

**Fix:**
1. The frontend defaults to the most recently uploaded dataset
2. Make sure you're selecting the dataset **before** asking the question
3. Check that the header shows the correct dataset name

### Issue 3: Question Is Too Vague

**Symptom:** OpenAI returns NO_SQL even with correct dataset

**Fix:**
- Be more specific: Instead of "show inventory", try "how many products are in the inventory?"
- Use column names: "show all products with qty_in_stock"
- Add context: "list products where qty_in_stock is below reorder_level"

### Issue 4: OpenAI API Issues

**Symptom:** Timeout or API errors in logs

**Fix:**
1. Check your OpenAI API key is valid
2. Check you have credits on your OpenAI account
3. Try a different model in `.env`: `OPENAI_MODEL=gpt-3.5-turbo`

## 📊 Verify Your Data

Check what tables exist and their structure:

```bash
cd backend
./inspect_database.sh

# Or for specific table:
./inspect_database.sh inventory_raw
```

## 🧪 Test from Command Line

Test a specific question directly:

```bash
curl -X POST "http://localhost:8000/api/v1/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many products in inventory?",
    "dataset_type": "inventory",
    "store_id": "demo-store"
  }' | python3 -m json.tool
```

Watch the backend logs to see what happens.

## 📞 Still Not Working?

1. Share the **exact question** you're asking
2. Share which **dataset** you selected in the dropdown
3. Share the **relevant backend log lines** showing:
   - "Processing question: ..."
   - "Generating SQL for question: ..."
   - "Failed to extract SQL from LLM output: ..."

This will help pinpoint the exact issue!

