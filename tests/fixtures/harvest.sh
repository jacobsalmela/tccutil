#!/bin/bash
# Print a test fixture for this Mac's TCC.db: the exact schema text SQLite stores,
# plus the digest tccutil.py computes from the `access` table.
#
# Usage: tests/fixtures/harvest.sh [user|system|/path/to/TCC.db] > fixture.sql
#
# Reading the user database needs Full Disk Access for your terminal; the system
# database also needs sudo. Only the schema is read, never any rows.
set -euo pipefail

scope="${1:-user}"
case "$scope" in
  user)   db="$HOME/Library/Application Support/com.apple.TCC/TCC.db" ;;
  system) db="/Library/Application Support/com.apple.TCC/TCC.db" ;;
  /*)     db="$scope"; scope="path" ;;
  *)      echo "usage: $0 [user|system|/path/to/TCC.db]" >&2; exit 2 ;;
esac

access="$(sqlite3 -readonly "$db" "SELECT sql FROM sqlite_master WHERE name='access' AND type='table'")"
digest="$(printf %s "$access" | shasum -a 1 | cut -c1-10)"

echo "-- digest: $digest"
echo "-- macos: $(sw_vers -productVersion) ($(sw_vers -buildVersion))"
echo "-- database: $scope"
sqlite3 -readonly "$db" \
  "SELECT sql || ';' FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY rowid"
