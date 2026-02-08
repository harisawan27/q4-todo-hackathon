#!/usr/bin/env bash
set -euo pipefail

echo "=== Secret Scan: Checking for hardcoded credentials ==="
echo ""

FOUND_ISSUES=0

# Patterns to check for
PATTERNS=(
    "password\s*=\s*['\"][^'\"]*['\"]"
    "api[_-]?key\s*=\s*['\"][^'\"]*['\"]"
    "secret\s*=\s*['\"][^'\"]*['\"]"
    "connection[_-]?string\s*=\s*['\"][^'\"]*['\"]"
    "postgresql://[^{]"
    "redis://[^{]"
    "mongodb://[^{]"
    "Bearer [A-Za-z0-9]"
)

SEARCH_DIRS=(
    "services/chat-api/app"
    "services/notification-service/app"
    "services/recurring-engine/app"
)

for dir in "${SEARCH_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "WARNING: Directory $dir not found, skipping..."
        continue
    fi

    for pattern in "${PATTERNS[@]}"; do
        MATCHES=$(grep -rn -E "$pattern" "$dir" --include="*.py" 2>/dev/null | grep -v "CHANGE_ME" | grep -v "test" | grep -v "#.*$pattern" || true)
        if [ -n "$MATCHES" ]; then
            echo "POTENTIAL SECRET FOUND with pattern: $pattern"
            echo "$MATCHES"
            echo ""
            FOUND_ISSUES=$((FOUND_ISSUES + 1))
        fi
    done
done

echo ""
if [ "$FOUND_ISSUES" -eq 0 ]; then
    echo "PASS: No hardcoded secrets detected."
    exit 0
else
    echo "FAIL: Found $FOUND_ISSUES potential hardcoded secrets."
    echo "Please use Dapr Secrets API for all credentials."
    exit 1
fi
