#!/bin/sh
#
# this file must be sourced to set up the environment for a standalone build of
# B2DXFitters; ROOT must be available in your path
#
# for the (t)csh out there: get serious, and change your login shell - csh is
# ill suited for serious work, see e.g.
# 
# http://www-uxsup.csx.cam.ac.uk/misc/csh.html
#
# csh and variants will not be supported by me. bash, zsh and friends should
# be fine
#
# 2012-09-04 Manuel Schiller <manuel.schiller@nikhef.nl>
#	initial release
# 2013-07-30 Manuel Schiller <manuel.schiller@nikhef.nl>
#	add support to set up in a clean LHCb environment at CERN with ROOT
#	from AFS

echo Setting up standalone environment for B2DXFitters package.
# get directory from which the script is executed - might be relative path
if test -n "$ZSH_VERSION"; then
    scriptdir=`dirname $0`
elif test -n "$BASH_VERSION"; then
    scriptdir=`dirname $BASH_SOURCE`
else
    test -f setup.sh && scriptdir=`pwd`
    if test -z "$scriptdir"; then
	echo Don't know from where I'm run - failed to set up environment.
	exit 1
    fi
fi
# save cwd
pwd=`pwd`
# go to scriptdir and then one up - that's the root of the package
cd "$scriptdir"
cd ..
# save full path
pkgdir=`pwd`
# restore old cwd
cd "$pwd"

export B2DXFITTERSROOT="$pkgdir"

if hostname -f | grep -q "cern.ch"; then
    echo "Looks like we're running at CERN, set up our own version of ROOT..."
    source $B2DXFITTERSROOT/standalone/standalone-cern.sh
fi
# test if root-config is there, so we can build things
test -f `which root-config 2>/dev/zero`
if [ 0 -ne "$?" ]; then
    echo 'Unable to locate ROOT (root-config), environment setup failed.'
    exit 1
fi

echo B2DXFITTERSROOT="$B2DXFITTERSROOT"

# work out where to take PyROOT from
if test -z "$PYTHONPATH" ; then
    echo Adding `root-config --libdir` to PYTHONPATH.
    export PYTHONPATH=`root-config --libdir`
else
    if (echo "$PYTHONPATH" | grep -qv `root-config --libdir`); then
	echo Adding `root-config --libdir` to PYTHONPATH.
	export PYTHONPATH=`root-config --libdir`:"$PYTHONPATH"
    fi
fi

# append the package's standalone python directory
if (echo "$PYTHONPATH" | grep -qv "$B2DXFITTERSROOT/python"); then
    echo Adding "$B2DXFITTERSROOT/python" to PYTHONPATH.
    export PYTHONPATH="$B2DXFITTERSROOT/python":"$PYTHONPATH"
fi

# append the package's standalone directory to LD_LIBRARY_PATH
if (echo "$LD_LIBRARY_PATH" | grep -qv "$B2DXFITTERSROOT/standalone"); then
    echo Adding "$B2DXFITTERSROOT/standalone" to LD_LIBRARY_PATH.
    export LD_LIBRARY_PATH="$B2DXFITTERSROOT/standalone":"$LD_LIBRARY_PATH"
fi

echo Standalone environment for B2DXFitters package set up.
