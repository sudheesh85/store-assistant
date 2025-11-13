#!/bin/bash
# Database Inspector Script
# Usage: ./inspect_database.sh [table_name]

DB_PATH="storage/stores/demo-store.db"

if [ ! -f "$DB_PATH" ]; then
    echo "❌ Database not found at: $DB_PATH"
    exit 1
fi

echo "📊 Database Inspector for Store Assistant"
echo "=========================================="
echo ""

# If a specific table is requested
if [ -n "$1" ]; then
    TABLE_NAME="$1"
    echo "🔍 Inspecting table: $TABLE_NAME"
    echo ""
    
    # Check if table exists
    TABLE_EXISTS=$(sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='$TABLE_NAME';" 2>/dev/null)
    
    if [ -z "$TABLE_EXISTS" ]; then
        echo "❌ Table '$TABLE_NAME' does not exist."
        echo ""
        echo "Available tables:"
        sqlite3 "$DB_PATH" ".tables"
        exit 1
    fi
    
    echo "📋 Schema:"
    sqlite3 -header -column "$DB_PATH" "PRAGMA table_info($TABLE_NAME);"
    echo ""
    
    echo "📊 Row count:"
    sqlite3 -header -column "$DB_PATH" "SELECT COUNT(*) as total_rows FROM $TABLE_NAME;"
    echo ""
    
    echo "👀 Sample data (first 5 rows):"
    sqlite3 -header -column "$DB_PATH" "SELECT * FROM $TABLE_NAME LIMIT 5;"
    
else
    # Show all tables overview
    echo "📚 Available Tables:"
    echo ""
    sqlite3 "$DB_PATH" ".tables"
    echo ""
    
    echo "📊 Summary:"
    echo ""
    
    # Inventory
    if sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_raw';" | grep -q "inventory_raw"; then
        echo "📦 Inventory (inventory_raw):"
        sqlite3 -header -column "$DB_PATH" "SELECT COUNT(*) as total_products, COUNT(DISTINCT category) as categories, SUM(qty_in_stock) as total_stock FROM inventory_raw;"
        echo ""
    fi
    
    # Sales
    if sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='sales_raw';" | grep -q "sales_raw"; then
        echo "💰 Sales (sales_raw):"
        sqlite3 -header -column "$DB_PATH" "SELECT COUNT(*) as total_transactions, SUM(total_price) as total_revenue, COUNT(DISTINCT date) as unique_dates FROM sales_raw;"
        echo ""
    fi
    
    # Staff
    if sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='staff_raw';" | grep -q "staff_raw"; then
        echo "👥 Staff (staff_raw):"
        sqlite3 -header -column "$DB_PATH" "SELECT COUNT(*) as total_staff, COUNT(DISTINCT role) as unique_roles, COUNT(DISTINCT store_id) as stores FROM staff_raw;"
        echo ""
    fi
    
    echo "💡 Tip: Run './inspect_database.sh <table_name>' for detailed view"
    echo "   Examples:"
    echo "   - ./inspect_database.sh inventory_raw"
    echo "   - ./inspect_database.sh sales_raw"
    echo "   - ./inspect_database.sh staff_raw"
fi

