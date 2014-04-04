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
exec $schedtool /usr/bin/time -v env python -O -- "$0" "$@"
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

def grabResult(filename):
    from B2DXFitters.FitResult import FitResult
    from ROOT import TFile, RooFitResult, TClass
    # common setup: rename list, blinding specification
    renames = { 'C': 'Bs2DsK_C', 'D': 'Bs2DsK_D',
                  'Dbar': 'Bs2DsK_Dbar', 'S': 'Bs2DsK_S',
                  'Sbar': 'Bs2DsK_Sbar', 'DeltaMs': 'deltaMs',
                  'p0_0': 'Bs2DsK_Mistag0CalibB_p0',
                  'p0_1': 'Bs2DsK_Mistag1CalibB_p0',
                  'p0_2': 'Bs2DsK_Mistag2CalibB_p0',
                  'p1_0': 'Bs2DsK_Mistag0CalibB_p1',
                  'p1_1': 'Bs2DsK_Mistag1CalibB_p1',
                  'p1_2': 'Bs2DsK_Mistag2CalibB_p1',
                  }
    blinds = {
            # CP parameters blinded with random offset from 13 ... 17
            '^Bs2DsK_(C|D|Dbar|S|Sbar)$': [ 13.0, 17.0 ],
            # everything else connected with DsK is blinded with random offset
            # from +3 ... +7 (efficiencies, calibrations, ...)
            '^Bs2DsK': [ 3.0, 7.0 ],
            }
    f = TFile(filename, "READ")
    # try to read cFit style fitresult
    for key in f.GetListOfKeys():
        if not TClass.GetClass(key.GetClassName()).InheritsFrom('RooFitResult'):
            continue
        fitresult = key.ReadObj()
        retVal = FitResult(fitresult, renames, blinds)
        del fitresult
        f.Close()
        return retVal
    # ok, not successful, try sFit next
    namelist = ('fitresult_signal_TimeTimeerrPdf_BDTGA_dataSet_time_BsDsK', )
    for key in f.GetListOfKeys():
        if not TClass.GetClass(key.GetClassName()).InheritsFrom('RooWorkspace'):
            continue
        ws = key.ReadObj()
        if None == ws: continue
        for n in namelist:
            obj = ws.obj(n)
            if None == obj: continue
            if not obj.InheritsFrom('RooFitResult'): continue
            retVal = FitResult(obj, renames, blinds)
            del obj
            f.Close()
            return retVal

if len(sys.argv) not in (2, 3):
    print 'usage: %s file1 [file2]' % sys.argv[0]

res1 = grabResult(sys.argv[1])
print 72 * '*'
print 'FIT1 RESULT'
print 72 * '*'
print res1
print 72 * '*'

if len(sys.argv) > 2:
    res2 = grabResult(sys.argv[2])
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

