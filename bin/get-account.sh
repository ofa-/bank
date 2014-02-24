#!/bin/bash

cd "$(dirname "$0")"
ACCOUNT=$1

ACCOUNT_FILE="../update/$ACCOUNT.csv"
CONTEXT_FILE="../update/$ACCOUNT.ctx"
ACCOUNTS="../etc/accounts"
BOOBANK="boobank -I"

get_account() {
	printf "Downloading %-15s %-30s " "$ACCOUNT" "($ID)"

	download=../update/download-$ACCOUNT
	do_download $ID $download

	if [ -f $CONTEXT_FILE ] ; then
		get_update_NB_LINES $CONTEXT_FILE $download
		head -$NB_LINES $download > $ACCOUNT_FILE
	else
		cat $download > $ACCOUNT_FILE
		NB_LINES=$(cat $download | wc -l)
	fi
	head  $download > $CONTEXT_FILE
	rm -f $download

	if [ $NB_LINES -eq 0 ] ; then
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
	| sed '0, /id;date;rdate;vdate;type;raw;category;label;amount/ d' \
	| awk -v 'FS=;' '{
		date=$2; amount=$9; label=$6;
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

get_update_NB_LINES() {
	context=$1
	target=$2

	nb_matches=$(grep -c -F -f $context $target)
	if [ $nb_matches = 0 ] ; then
		NB_LINES=$(cat $target | wc -l)
		return 1
	fi	
	NB_LINES=$(grep -n -F -f $context $target | cut -d: -f1 | sort -n | head -1)
	NB_LINES=$((NB_LINES - 1))
}

fail() {
	echo $2
	exit $1
}


get_account_ID
get_account
