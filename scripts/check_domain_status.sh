#!/bin/bash
echo "=== Current Domain Status ==="
for dir in app/rule_cards/*/; do 
    count=$(find "$dir" -name "*.yml" 2>/dev/null | wc -l)
    domain=$(basename "$dir")
    if [ $count -eq 0 ]; then
        status="❌ Empty"
    else
        status="✅ Populated"
    fi
    echo "$status $domain: $count rules"
done | sort