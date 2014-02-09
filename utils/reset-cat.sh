#!/bin/bash

file=$1

[ -f "$file" ] || { echo "usage: $0 <account file>"; exit 0; }

reset_categories() {
	source_file=$1
	awk -v FS=';;' '{ if ($2$3) print $1 ";;" $2 ";;" $3 ";;"; else print; }' $source_file
}

auto_categorize() {
	target_file=$1
	sed_file="$(dirname "$0")"/../etc/$2
	[ -f $sed_file ] && sed -i -f $sed_file $target_file
}

categorize_rest() {
	target_file=$1
	sed -i 's|;;$|;;?|' $target_file
}

mv $file $file.sav
reset_categories $file.sav > $file
auto_categorize  $file "auto-categories.sed"
auto_categorize  $file "auto-$(basename $file .csv).sed"
categorize_rest  $file

