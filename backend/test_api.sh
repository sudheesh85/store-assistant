#!/bin/bash
# Test API Script - Tests asking questions against different datasets

API_URL="http://localhost:8000/api/v1"

echo "🧪 Testing Store Assistant API"
echo "================================"
echo ""

# Test 1: Inventory question with inventory dataset
echo "📦 Test 1: Inventory question with inventory dataset"
echo "Question: 'How many products are in stock?'"
echo "Dataset: inventory"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many products are in stock?",
    "dataset_type": "inventory",
    "store_id": "demo-store"
  }' | python3 -m json.tool

echo ""
echo "---"
echo ""

# Test 2: Sales question with sales dataset
echo "💰 Test 2: Sales question with sales dataset"
echo "Question: 'What is the total revenue?'"
echo "Dataset: sales"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the total revenue?",
    "dataset_type": "sales",
    "store_id": "demo-store"
  }' | python3 -m json.tool

echo ""
echo "---"
echo ""

# Test 3: Staff question with staff dataset
echo "👥 Test 3: Staff question with staff dataset"
echo "Question: 'How many staff members do we have?'"
echo "Dataset: staff"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many staff members do we have?",
    "dataset_type": "staff",
    "store_id": "demo-store"
  }' | python3 -m json.tool

echo ""
echo "---"
echo ""

# Test 4: WRONG - Inventory question with sales dataset (should fail gracefully)
echo "❌ Test 4: Mismatched question and dataset (should return NO_SQL)"
echo "Question: 'How many products are in stock?'"
echo "Dataset: sales (WRONG!)"
echo ""

curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many products are in stock?",
    "dataset_type": "sales",
    "store_id": "demo-store"
  }' | python3 -m json.tool

echo ""
echo "================================"
echo "✅ Tests complete! Check backend logs for details."

