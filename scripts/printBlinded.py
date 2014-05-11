#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
# --------------------------------------------------------------------------- 
# @file printBlinded.py
#
# read sFit/cFit ROOT files, and print the (blinded) results and the
# difference
# --------------------------------------------------------------------------- 

# This file is used as both a shell script and as a Python script.
""":"
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.

# make sure the environment is set up properly
if test -n "$CMTCONFIG" \
         -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersDict.so \
     -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersLib.so; then
    # all ok, software environment set up correctly, so don't need to do 
    # anything
    true
else
    if test -n "$CMTCONFIG"; then
    # clean up incomplete LHCb software environment so we can run
    # standalone
        echo Cleaning up incomplete LHCb software environment.
        PYTHONPATH=`echo $PYTHONPATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export PYTHONPATH
        LD_LIBRARY_PATH=`echo $LD_LIBRARY_PATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export LD_LIBRARY_PATH
        exec env -u CMTCONFIG -u B2DXFITTERSROOT "$0" "$@"
    fi
    # automatic set up in standalone build mode
    if test -z "$B2DXFITTERSROOT"; then
        cwd="$(pwd)"
        if test -z "$(dirname $0)"; then
        # have to guess location of setup.sh
        cd ../standalone
        . ./setup.sh
        cd "$cwd"
        else
        # know where to look for setup.sh
        cd "$(dirname $0)"/../standalone
        . ./setup.sh
        cd "$cwd"
        fi
    unset cwd
    fi
fi

# figure out which custom allocators are available
# prefer jemalloc over tcmalloc
for i in libjemalloc libtcmalloc; do
    for j in `echo "$LD_LIBRARY_PATH" | tr ':' ' '` \
        /usr/local/lib /usr/lib /lib; do
        for k in `find "$j" -name "$i"'*.so.?' | sort -r`; do
            if test \! -e "$k"; then
            continue
        fi
        echo adding $k to LD_PRELOAD
        if test -z "$LD_PRELOAD"; then
            export LD_PRELOAD="$k"
            break 3
        else
            export LD_PRELOAD="$LD_PRELOAD":"$k"
            break 3
        fi
    done
    done
done

# set batch scheduling (if schedtool is available)
schedtool="`which schedtool 2>/dev/zero`"
if test -n "$schedtool" -a -x "$schedtool"; then
    echo "enabling batch scheduling for this job (schedtool -B)"
    schedtool="$schedtool -B -e"
else
    schedtool=""
fi

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((2048 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O "$0" - "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from math     import pi, log, sqrt, fmod
import os, sys, gc

import B2DXFitters
import ROOT
from ROOT import RooFit
from B2DXFitters.FitResultGrabberUtils import grabResult

isData = True
blinding = True

if sys.argv[1] == '-': sys.argv.pop(1)
if len(sys.argv) not in (2, 3):
    print 'usage: %s file1 [file2]' % sys.argv[0]

res1 = grabResult(isData, blinding, sys.argv[1])
print 72 * '*'
print 'FIT1 RESULT'
print 72 * '*'
print res1
print 72 * '*'

if len(sys.argv) > 2:
    res2 = grabResult(isData, blinding, sys.argv[2])
    # inform that these are for the same data set
    for r in (res1, res2): r.setOptions(['SameDataSet'])
    
    print
    print 72 * '*'
    print 'FIT2 RESULT'
    print 72 * '*'
    print res2
    print 72 * '*'
    print
    print 72 * '*'
    print 'RESULT (FIT2 - FIT1) - IGNORE CORRELATIONS, AT LIMIT WARNINGS'
    print 72 * '*'
    print (res2 - res1)
    print 72 * '*'

