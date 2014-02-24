#!/bin/bash

ACCOUNTS="../etc/accounts"
cd "$(dirname "$0")"

usage() {
	echo "usage: $(basename "$0") <account> [<account> ...]"
	echo "       $(basename "$0") --all"
	echo "       $(basename "$0") --list"
}

main() {
	case $* in
		--all|-a)
			download $(list_accounts)
			;;
		--list|-l)
			list_accounts
			;;
		"")
			usage
			;;
		*)
			download $*
			;;
esac
}

list_accounts() {
	cat $ACCOUNTS | egrep -v "^[[:space:]]*#" | awk '$1 {print $1}'
}

download() {
	for account in $*; do
		./get-account.sh $account || continue
		./update-server-db.sh $account
	done
}


sanity_checks() {
	[ -f $ACCOUNTS ]		|| { echo "accounts file '$ACCOUNTS' not found"; exit 1; }
	[ -x get-account.sh ]		|| { echo "utility 'get-account.sh' not found"; exit 1; }
	[ -x update-server-db.sh ]	|| { echo "utility 'update-server-db.sh' not found"; exit 1; }
	boobank --version &> /dev/null	|| { echo "utility 'boobank' not found"; exit 1; }
}

sanity_checks

main $*
