#!/bin/bash
# Test that LLM automatically chooses the correct table
# NO dataset_type is sent - LLM analyzes ALL schemas

API_URL="http://localhost:8000/api/v1"

echo "🤖 Testing: LLM Chooses Table Automatically"
echo "============================================"
echo "These requests do NOT include dataset_type"
echo "LLM sees ALL tables and chooses the best one"
echo ""

# Test 1: Malayalam sales question
echo "💰 Test 1: Malayalam Sales Question"
echo "Question: 'ഇന്ന് മൊത്തം വിൽപ്പന എത്ര?'"
echo "Expected: LLM should choose 'sales_raw' table"
echo ""

RESULT=$(curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "ഇന്ന് മൊത്തം വിൽപ്പന എത്ര?",
    "store_id": "demo-store"
  }')

echo "$RESULT" | python3 -m json.tool | head -15

# Check if SQL contains sales_raw
if echo "$RESULT" | grep -q "sales_raw"; then
    echo "✅ SUCCESS: LLM chose sales_raw table!"
else
    echo "❌ FAILED: LLM did not choose sales_raw"
fi

echo ""
echo "---"
echo ""

# Test 2: English inventory question
echo "📦 Test 2: English Inventory Question"
echo "Question: 'how many inventory is here'"
echo "Expected: LLM should choose 'inventory_raw' table"
echo ""

RESULT=$(curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "how many inventory is here",
    "store_id": "demo-store"
  }')

echo "$RESULT" | python3 -m json.tool | head -15

# Check if SQL contains inventory_raw
if echo "$RESULT" | grep -q "inventory_raw"; then
    echo "✅ SUCCESS: LLM chose inventory_raw table!"
else
    echo "❌ FAILED: LLM did not choose inventory_raw"
fi

echo ""
echo "---"
echo ""

# Test 3: Staff question
echo "👥 Test 3: Staff Question"
echo "Question: 'Who works the night shift?'"
echo "Expected: LLM should choose 'staff_raw' table"
echo ""

RESULT=$(curl -s -X POST "$API_URL/ask/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who works the night shift?",
    "store_id": "demo-store"
  }')

echo "$RESULT" | python3 -m json.tool | head -15

# Check if SQL contains staff_raw
if echo "$RESULT" | grep -q "staff_raw"; then
    echo "✅ SUCCESS: LLM chose staff_raw table!"
else
    echo "❌ FAILED: LLM did not choose staff_raw"
fi

echo ""
echo "============================================"
echo "✅ All tests complete!"
echo ""
echo "💡 Check backend logs to see LLM's decision:"
echo "   tail -f storage/logs/backend.log | grep 'Available datasets'"

