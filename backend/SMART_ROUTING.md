# 🤖 Smart Dataset Routing

## Overview

The Store Assistant now has **intelligent dataset routing** - users don't need to manually select which dataset to query. The AI automatically figures out which table contains the relevant data based on the question.

## How It Works

### User Experience (Non-Technical Store Owners)

1. **Upload CSVs**: Owner uploads `sales.csv`, `inventory.csv`, `staff.csv`, etc.
2. **Ask Questions**: Owner asks natural language questions like:
   - "How many products in stock?"
   - "What was yesterday's revenue?"
   - "Who works the night shift?"
3. **Smart Detection**: System automatically:
   - Analyzes the question
   - Determines which dataset is relevant
   - Queries the right table
   - Returns the answer

**No dataset selection required!** ✅

---

## Technical Implementation

### Two-Layer Routing Strategy

#### Layer 1: LLM-Based Routing (Preferred)
- Uses OpenAI to analyze the question
- Compares question intent against all available datasets
- Provides dataset descriptions and schemas to the LLM
- LLM returns the best matching dataset type
- **Most accurate** for complex or ambiguous questions

#### Layer 2: Keyword-Based Routing (Fallback)
- Used when OpenAI is unavailable or fails
- Keyword matching against predefined rules:
  - **Inventory keywords**: inventory, stock, product, item, reorder, supplier, qty, available
  - **Sales keywords**: sale, revenue, transaction, purchase, payment, customer, order, profit
  - **Staff keywords**: staff, employee, worker, team, manager, role, shift
- Also matches column names from datasets
- Scores each dataset and picks the highest match

### Code Architecture

```
User Question
     ↓
API Endpoint (/ask/question)
     ↓
Dataset Router Service
     ↓
   ┌─────────────────────┐
   │  Is dataset_type    │
   │  explicitly set?    │
   └─────────────────────┘
         │           │
      YES│           │NO
         │           │
         ↓           ↓
    Use that    Smart Routing
    dataset     (LLM or Keywords)
         │           │
         └─────┬─────┘
               ↓
         SQL Generator
               ↓
         Query Executor
               ↓
            Result
```

### Key Files

- **`backend/app/services/dataset_router.py`**: Core routing logic
- **`backend/app/api/routes/ask.py`**: Updated endpoint using the router
- **`frontend/components/ChatContainer.tsx`**: Updated UI with "Auto" option

---

## Usage Examples

### 1. Auto-Detection (Default Behavior)

**Frontend:**
```typescript
// User doesn't select dataset, or selects "Auto"
const request = {
  question: "How many products in stock?",
  store_id: "demo-store",
  // dataset_type is undefined - triggers smart routing
};
```

**Backend:**
```python
# dataset_router.route_question() is called
# Returns: inventory dataset (detected from "products", "stock")
```

**Result:** ✅ Queries `inventory_raw` table

### 2. Manual Override (Optional)

Power users can still manually select:

**Frontend:**
```typescript
const request = {
  question: "How many products in stock?",
  store_id: "demo-store",
  dataset_type: "sales", // Explicitly set
};
```

**Backend:**
```python
# Skips routing, uses specified dataset directly
```

**Result:** ⚠️ Queries `sales_raw` table (may return incorrect result)

---

## Configuration

### Environment Variables

No additional configuration needed! Works with existing settings:
- `OPENAI_API_KEY`: If set, uses LLM-based routing
- If not set, falls back to keyword-based routing

### Customizing Routing Rules

Edit `backend/app/services/dataset_router.py`:

```python
routing_rules = {
    "inventory": [
        "inventory", "stock", "product", "item", "reorder",
        # Add your custom keywords
    ],
    "sales": [
        "sale", "revenue", "transaction", "purchase",
        # Add your custom keywords
    ],
}
```

Add dataset descriptions:

```python
descriptions = {
    "sales": "Sales transactions, revenue, products sold",
    "inventory": "Product stock levels, suppliers, quantities",
    # Add your custom dataset descriptions
}
```

---

## Testing

### Test Smart Routing

```bash
cd backend
./test_smart_routing.sh
```

This runs 6 tests without specifying `dataset_type` to verify auto-detection.

### Watch Routing Decisions

```bash
cd backend
tail -f storage/logs/backend.log | grep "Auto-routed"
```

You'll see logs like:
```
Processing question: 'how many inventory is here' | Auto-routed: Yes | Resolved dataset: inventory
LLM routing for question '...': chose dataset 'inventory'
```

---

## Advantages Over Manual Selection

| Feature | Manual Selection | Smart Routing |
|---------|-----------------|---------------|
| **User Experience** | Technical, confusing | Natural, intuitive |
| **Error Rate** | High (users pick wrong dataset) | Low (AI understands context) |
| **Ease of Use** | Requires training | Zero training needed |
| **Multi-language** | Same complexity | Works in Malayalam/English/Manglish |
| **Scalability** | More datasets = more confusion | More datasets = AI adapts |

---

## Troubleshooting

### Issue: Wrong dataset selected

**Check logs:**
```bash
grep "Processing question" storage/logs/backend.log | tail -5
```

Look for: `Resolved dataset: <type>`

**Solutions:**
1. Add more keywords to `routing_rules` for better matching
2. Improve dataset descriptions for LLM
3. Use manual override temporarily while fixing rules

### Issue: No datasets found

**Error:** "No datasets available"

**Solution:** Upload CSVs first via the frontend upload feature

### Issue: LLM routing not working

**Check:**
- Is `OPENAI_API_KEY` set in `.env`?
- Are there API errors in logs?

**Fallback:** System automatically uses keyword-based routing

---

## Future Enhancements

### Potential Improvements:

1. **Multi-table queries**: Query across multiple datasets (JOINs)
2. **Learning**: Track which routings work best and improve over time
3. **Confidence scores**: Show users which dataset was selected and why
4. **Dataset suggestions**: "Did you mean to ask about inventory?"
5. **Custom datasets**: Support user-defined dataset types beyond sales/inventory/staff

---

## Summary

✅ **No manual dataset selection required**  
✅ **Works with any question in any language**  
✅ **Falls back gracefully when needed**  
✅ **Maintains backward compatibility** (manual selection still works)  
✅ **Non-technical friendly** (store owners can just ask questions)

This is how a modern AI assistant should work - intelligent and user-friendly! 🎉

