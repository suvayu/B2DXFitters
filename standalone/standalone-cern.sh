#!/bin/sh

setGCC() {
    local gccver
    gccver=`echo $CMTCONFIG | tr '-' '\n' | grep gcc | sed -e 's/gcc//g' -e 's/^[34]/\0./'`
    . /afs/cern.ch/sw/lcg/external/gcc/$gccver/$CMTCONFIG/setup.sh
}


#!/bin/sh
setenvROOT () {
    local prefix defaultversion escprefix versions ver verok pwd v validversions
    # force gcc version indicated by CMTCONFIG
    test -z "$CMTCONFIG" || setGCC
    prefix="/afs/cern.ch/sw/lcg/app/releases/ROOT/"
    defaultversion=5.34.09

    escprefix=`echo "$prefix" | sed -e 's/\//\\\\\//g'`
    versions=`ls -d "$prefix"* | sed -e 's/'"$escprefix"'//g'`
    # check if there are any valid versions
    validversions=""
    for v in `echo $versions`; do
	if test -f "$prefix""$v"/"$CMTCONFIG"/root/bin/thisroot.sh; then
	    validversions="$v"" ""$validversions"
	fi
    done
    versions=`echo $validversions`
    if test -z "$versions"; then
	echo "No valid ROOT versions found, exiting." >&2
	return 1
    fi

    ver="$1"
    # if no version set, try the default version
    test -z "$ver" && ver="$defaultversion"
    # if no default set, try the last version in the listing
    test -z "$ver" && ver=`echo "$versions" | tail -1`

    # check if we have a valid version number
    if test -n "$ver"; then
	echo "$versions" | grep -q -- "$ver"
	verok=$?
	test 0 -eq $verok -a -f "$prefix""$ver"/"$CMTCONFIG"/root/bin/thisroot.sh
	verok=$?
    else
	verok=1
    fi

    # if no valid version number (or if a list was requested), print a list
    # of available versions, and ask which one to take
    while test "-l" = "$ver" -o $verok -ne 0; do
	if test "-l" != "$ver" -a $verok -ne 0; then
	    echo "ROOT version" \""$ver"\" \
		"unavailable, please choose a different version!" >&2
	    echo >&2
	fi
	echo Available ROOT versions: "[" $versions "]"
	if tty -s; then
	    echo -n "Please choose ROOT version to use: "
	    read ver
	    if test -n "$ver"; then
		echo "$versions" | grep -q -- "$ver"
		verok=$?
		test 0 -eq $verok -a -f "$prefix""$ver"/"$CMTCONFIG"/root/bin/thisroot.sh
		verok=$?
	    else
		verok=1
	    fi
	else
	    return 1
	fi
    done

    if test -f "$prefix""$ver"/"$CMTCONFIG"/root/bin/thisroot.sh; then
	echo Using ROOT version "$ver" from "$prefix""$ver".
	pwd="$(pwd)"
	cd "$prefix""$ver"/"$CMTCONFIG"/root
	source bin/thisroot.sh
	cd "$pwd"
	# guess where this ROOT version takes its python from, and update LD_LIBRARY_PATH
	export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:"`python-config --prefix`/lib
    else
	echo "ROOT version" "$ver" "installed under" "$prefix""$ver" \
	    "is incomplete." >&2
    fi
}

# for non-system users, set up ROOT
if test 1000 -le `id -u`; then
    test -z "$ROOTSYS" && setenvROOT
    test -n "$ROOTSYS" && echo "$LD_LIBRARY_PATH" | grep -lvq "$ROOTSYS" && setenvROOT
fi
