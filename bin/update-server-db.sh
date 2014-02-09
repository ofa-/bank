#!/bin/bash

cd "$(dirname "$0")"
ACCOUNT=$1

UPDATE_FILE="../update/$ACCOUNT.csv"
SERVER_FILE="../server/$ACCOUNT.csv"
AUTOSED_DIR="../etc"

update_server_db() {
	all_caps $UPDATE_FILE
	auto_categorize $UPDATE_FILE "auto-categories.sed"
	auto_categorize $UPDATE_FILE "auto-$ACCOUNT.sed"
	sed -i 's|;;$|;;?|' $UPDATE_FILE
	sed -i 's|$|;*|'    $UPDATE_FILE
	mv -f $SERVER_FILE $SERVER_FILE.bak
	cat $UPDATE_FILE $SERVER_FILE.bak > $SERVER_FILE
	echo -n > $UPDATE_FILE
}

auto_categorize() {
	target_file=$1
	sed_file=$AUTOSED_DIR/$2
	[ -f $sed_file ] && sed -i -f $sed_file $target_file
}

all_caps() {
	cat $1 | tr '[a-z]' '[A-Z]' > $1.up
	mv $1.up $1
}

sanity_check() {
	[ -f $UPDATE_FILE ] || { echo "no update file for account: $ACCOUNT"; exit 1; }
	[ -f $SERVER_FILE ] || touch $SERVER_FILE
}

sanity_check
update_server_db
