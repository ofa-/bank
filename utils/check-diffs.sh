#!/bin/bash

cd "$(dirname "$0")"

printf "getting local totals..."
./check-totals.sh > local
echo done

printf "getting banks totals..."
./check-boobank.sh > banks 2>/dev/null
echo done

diff -U 0 local banks
rm local banks
