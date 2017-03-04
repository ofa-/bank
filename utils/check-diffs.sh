#!/bin/bash

cd "$(dirname "$0")"

printf "getting local totals..."
./check-totals.sh > local
echo done

printf "getting banks totals..."
./check-boobank.sh > banks
echo done

diff -U 0 local banks
rm local banks
