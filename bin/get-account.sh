#!/bin/bash

cd "$(dirname "$0")"
ACCOUNT=$1

ACCOUNT_FILE="../update/$ACCOUNT.csv"
CONTEXT_FILE="../update/$ACCOUNT.ctx"
ACCOUNTS="../etc/accounts"
BOOBANK="boobank -I"

get_account() {
	printf "Downloading %-15s %-40s " "$ACCOUNT" "($ID)"

	download=../update/download-$ACCOUNT
	do_download $ID $download

	if [ -f $CONTEXT_FILE ] ; then
		diff -u $CONTEXT_FILE $download \
		| sed '1,2 d' \
		| egrep '^\+'  \
		| sed 's:^+::' > $ACCOUNT_FILE
	else
		cat $download > $ACCOUNT_FILE
	fi
	mv $download $CONTEXT_FILE

	if [ `wc -l < $ACCOUNT_FILE` -eq 0 ] ; then
		fail -1 "DONE (no changes)"
	fi
	echo "DONE"
}

get_account_ID() {
	ID=$(egrep ^$ACCOUNT $ACCOUNTS | tr -s '\t' | cut -f2)
	if [ -z "$ACCOUNT" ] || [ -z "$ID" ] ; then
		fail 1 "unknown account: $ACCOUNT"
	fi
}

do_download() {
	account_id=$1
	target=$2
	error=$target.error

	# header line (= format) may be preceeded by parse errors
	$BOOBANK "count off; formatter csv; history $account_id" 2> $error \
	| sed '0, /id;url;date;rdate;vdate;type;raw;category;label;amount/ d' \
	| awk -v 'FS=;' '{
		date=$3; amount=$10; label=$7;
		split(date, d, "-"); dd=d[3]; mm=d[2]; yy=substr(d[1], 3);
		if (amount > 0) amount="+" amount
		print dd "/" mm "/" yy ";;" label ";;" amount ";;"
	}' > $target

	if egrep -q 'WARNING:|(Bug|Error)\(.*\):' $error ; then
		fail 2 "FAIL (download)"
	fi
	if ! egrep -q '.*' $target ; then
		fail 3 "FAIL (download)"
	fi
	rm -f $error
}

fail() {
	echo $2
	exit $1
}


get_account_ID
get_account
