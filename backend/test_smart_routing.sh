#!/bin/bash
# Test Smart Dataset Routing
# This tests the intelligent auto-detection feature

API_URL="http://localhost:8000/api/v1"

echo "🤖 Testing SMART Dataset Routing"
echo "=================================="
echo "These tests do NOT specify dataset_type - the system should auto-detect!"
echo ""

# Test 1: Inventory question (should auto-route to inventory)
echo "📦 Test 1: Auto-detect INVENTORY dataset"
echo "Question: 'how many inventory is here'"
echo "Expected: Should automatically use inventory dataset"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "how many inventory is here",
    "store_id": "demo-store"
  }' | python3 -m json.tool | head -20

echo ""
echo "---"
echo ""

# Test 2: Sales question (should auto-route to sales)
echo "💰 Test 2: Auto-detect SALES dataset"
echo "Question: 'What is the total revenue?'"
echo "Expected: Should automatically use sales dataset"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the total revenue?",
    "store_id": "demo-store"
  }' | python3 -m json.tool | head -20

echo ""
echo "---"
echo ""

# Test 3: Staff question (should auto-route to staff)
echo "👥 Test 3: Auto-detect STAFF dataset"
echo "Question: 'How many employees do we have?'"
echo "Expected: Should automatically use staff dataset"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many employees do we have?",
    "store_id": "demo-store"
  }' | python3 -m json.tool | head -20

echo ""
echo "---"
echo ""

# Test 4: Products in stock (should auto-route to inventory)
echo "📦 Test 4: Auto-detect INVENTORY from context"
echo "Question: 'Show me products that are low on stock'"
echo "Expected: Should automatically use inventory dataset (has qty_in_stock, reorder_level)"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me products that are low on stock",
    "store_id": "demo-store"
  }' | python3 -m json.tool | head -20

echo ""
echo "---"
echo ""

# Test 5: Best sellers (should auto-route to sales)
echo "💰 Test 5: Auto-detect SALES from context"
echo "Question: 'Which products are selling the most?'"
echo "Expected: Should automatically use sales dataset"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which products are selling the most?",
    "store_id": "demo-store"
  }' | python3 -m json.tool | head -20

echo ""
echo "---"
echo ""

# Test 6: Malayalam question (should auto-route)
echo "🌏 Test 6: Auto-detect with Malayalam question"
echo "Question: 'എത്ര സ്റ്റോക്ക് ഉണ്ട്?' (how much stock?)"
echo "Expected: Should automatically use inventory dataset"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "എത്ര സ്റ്റോക്ക് ഉണ്ട്?",
    "store_id": "demo-store"
  }' | python3 -m json.tool | head -20

echo ""
echo "================================"
echo "✅ Smart routing tests complete!"
echo ""
echo "💡 Check backend logs to see which dataset was auto-selected for each question:"
echo "   tail -f storage/logs/backend.log | grep 'Auto-routed: Yes'"

