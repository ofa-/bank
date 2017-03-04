#!/bin/bash

BOOBANK_DL=`mktemp`
boobank -I ls > $BOOBANK_DL

cd "$(dirname "$0")"
for account in $(../bin/download.sh --list); do
	account_id=$(awk '$1 == "'$account'" {print $2}' ../etc/accounts)
	total=$(awk '$1 == "'$account_id'" {print $NF}' $BOOBANK_DL)
	printf "%-20s %10.2f\n" "$account" $total
done
rm $BOOBANK_DL
