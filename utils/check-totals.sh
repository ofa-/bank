#!/bin/bash

cd "$(dirname "$0")"
for account in $(../bin/download.sh --list); do
	curl -s localhost:1969/view/$account \
	| grep "Solde Compte" -A1 | tail -1 \
	| sed 's:<th>: :; s:€</th>::' \
	| xargs printf "%-20s %10.2f\n" "$account"
done
