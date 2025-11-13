# Store Assistant Data Ingestion & Intent Architecture

## Goals
- Allow Kerala SMB stores to upload multiple CSVs (sales, inventory, staff, transactions) into **one** SQLite/DuckDB database per store.
- Capture column descriptions/semantics so the NL2SQL prompt is grounded in business meaning.
- Build and maintain a **consolidated analytics view** that NL2SQL queries against (no ad-hoc multi-table joins from the LLM).
- Classify user intent up-front to route questions to either straight NL2SQL, diagnostic insight workflows, or administrative responses.

## 1. Storage Model

### Database Layout
- **Single SQLite file** per store: `storage/stores/{store_id}.db`.
- When authentication is added, `store_id` will come from the authenticated session; for now use a default `demo` store.
- Shared metadata registry in `storage/datasets_registry.json` keyed by `store_id` and `dataset_type`.

### Tables
| Dataset Type | Table Name | Key Columns | Notes |
|--------------|-----------|-------------|-------|
| sales        | `sales_raw`        | `invoice_id`, `item_id`, `staff_id`, `sold_at` | One row per line item. |
| transactions | `transactions_raw` | `transaction_id`, `invoice_id`, `payment_mode` | One row per payment event. |
| inventory    | `inventory_raw`    | `item_id`, `stock_on_hand`, `reorder_point` | Snapshot from POS/ERP. |
| staff        | `staff_raw`        | `staff_id`, `staff_name`, `role`, `store_branch` | Personnel data. |

### Column Metadata
- `datasets_registry.json` stores column descriptions coming from:
  1. Hard-coded defaults per dataset type (maintain under `backend/app/metadata/columns.py`).
  2. Optional overrides supplied during upload (frontend will prompt for friendly name + description).
  3. Automatic heuristics (regex on column names) as a fallback.
- Registry entry sample:
```json
{
  "demo": {
    "sales": {
      "source_file": "nov_sales.csv",
      "uploaded_at": "2025-11-12T09:20:33Z",
      "row_count": 4821,
      "columns": {
        "invoice_id": "Unique invoice number from POS",
        "item_id": "SKU or product identifier",
        "net_sales": "Total line amount after discount (INR)",
        "quantity": "Units sold",
        "sold_at": "Sale timestamp (local time)",
        "staff_id": "Associate who handled the sale"
      }
    },
    "inventory": { ... }
  }
}
```

## 2. Ingestion Pipeline
1. Frontend collects: `{ dataset_type, file, optional column descriptions }`.
2. Backend validates dataset type against an allowlist (`sales`, `inventory`, `staff`, `transactions`).
3. CSV is loaded via Pandas:
   - Normalize headers (`normalize_column_name`).
   - Enforce required columns per dataset; warn if optional fields missing.
   - Persist table into SQLite using `to_sql(..., if_exists='replace')`.
4. Metadata registry updated (row count, column descriptions, original filename).
5. Trigger consolidated view refresh (see below).

## 3. Consolidated Analytics View

### View Name
- `store_analytics_view` scoped per store (either actual SQL VIEW or materialized table).

### View Definition (draft)
```sql
CREATE VIEW store_analytics_view AS
SELECT
  s.invoice_id,
  s.item_id,
  items.item_name,
  s.quantity,
  s.net_sales,
  s.sold_at,
  date(s.sold_at) AS sale_date,
  strftime('%Y-%m', s.sold_at) AS sale_month,
  staffs.staff_id,
  staffs.staff_name,
  staffs.role,
  inv.stock_on_hand,
  inv.reorder_point,
  txn.payment_mode,
  txn.amount AS payment_amount
FROM sales_raw s
LEFT JOIN inventory_raw inv USING (item_id)
LEFT JOIN staff_raw staffs USING (staff_id)
LEFT JOIN transactions_raw txn USING (invoice_id);
```
- Add derived metrics (discount %, gross margin) once required columns exist.
- For performance: if view becomes slow, materialize into `store_analytics_materialized` and rebuild after each upload.

### Prompt Schema
- `sql_generator` will receive a schema block summarizing only `store_analytics_view` plus column descriptions:
```
Table: store_analytics_view
- invoice_id (text) – Unique invoice number (from sales CSV)
- item_id (text) – Product identifier
- item_name (text) – Friendly name from inventory
- quantity (number) – Units sold in transaction line
- net_sales (number) – Line-level sales amount in INR after discount
...
```

## 4. Intent Classification

### Pipeline Steps
1. **Intent Detector** (`IntentClassifierService`):
   - Input: question text, optional conversation context.
   - Output: `{ intent: str, confidence: float }` from label set:
     - `metric_lookup`
     - `comparison`
     - `diagnostic_insight`
     - `dataset_admin`
     - `inventory_alert`
     - `staff_performance`
     - `fallback`
2. Route question based on intent:
   - `metric_lookup`, `comparison`, `inventory_alert`, `staff_performance` → NL2SQL on `store_analytics_view` (with specialized prompt templates per intent).
   - `diagnostic_insight` → run curated SQL bundle (trend, baskets, staff, stock) then call LLM with factual summaries.
   - `dataset_admin` → respond using registry info (latest upload, row counts).
   - `fallback` → polite guidance toward supported queries.

### Classifier Implementation Options
- Short term: use OpenAI function call prompt (zero-shot) with guardrails to keep cost low.
- Mid term: fine-tune a small model (e.g., Instructor embeddings + logistic regression).
- Persist past questions/intents in local store for continuous improvement.

## 5. Cost & Performance Considerations
- Keep view limited to necessary columns; allow aggregates to be computed via SQL rather than LLM.
- Limit LLM prompt tokens by sending only column list + descriptions (no raw rows) unless absolutely necessary.
- Use indices on high-cardinality columns (`invoice_id`, `item_id`, `sold_at`), and consider DuckDB if datasets grow beyond typical SQLite comfort zone.
- Implement asynchronous view refresh so uploads return quickly (refresh job enqueued post-response).

## 6. Next Implementation Steps
1. Refactor dataset manager to work with `store_id` + dataset types, writing into single SQLite file.
2. Build metadata registry loader/saver with column descriptions.
3. Implement view builder + refresh trigger.
4. Update `sql_generator` schema prompt.
5. Add `IntentClassifierService` and wire into `/ask` pipeline.
6. Extend frontend upload UI to capture dataset type and optional column descriptions.

