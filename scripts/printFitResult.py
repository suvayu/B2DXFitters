#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
# --------------------------------------------------------------------------- 
# @file printFitResult.py
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
        # try to find from where script is executed, use current directory as
        # fallback
        tmp="$(dirname $0)"
        tmp=${tmp:-"$cwd"}
        # convert to absolute path
        tmp=`readlink -f "$tmp"`
        # move up until standalone/setup.sh found, or root reached
        while test \( \! -d "$tmp"/standalone \) -a -n "$tmp" -a "$tmp"\!="/"; do
            tmp=`dirname "$tmp"`
        done
        if test -d "$tmp"/standalone; then
            cd "$tmp"/standalone
            . ./setup.sh
        else
            echo `basename $0`: Unable to locate standalone/setup.sh
            exit 1
        fi
        cd "$cwd"
        unset tmp
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

parser = OptionParser(usage = '%prog [options] [fit result ROOT files]')
parser.add_option('-d', '--data', action='store_true', dest='isData',
        default=None, help='files a from data fits')
parser.add_option('-t', '--toy', action='store_false', dest='isData',
        default=None, help='files are toys/MC')
parser.add_option('--unblind', action='store_false', dest='blinding',
        default=True, help='unblind data (USE WITH CARE!)')
parser.add_option('--avg', action='store_true', dest='avg', default=False,
        help='average two indep. fit results')
parser.add_option('--diff', action='store_true', dest='diff', default=False,
        help='diff mode (toy-by-toy differences etc., either indep. '
        'samples or same data set); if --avg and --diff (or --systematic) '
        'are specified simultaneously, the command takes three files with '
        'fit results, and will first average the first and second file, '
        'then form the difference between the average and the third file')
parser.add_option('--systematic', action='store_true', dest='systematic',
	default=False, help='evaluate systematic (implies --diff --samesample;'
        ' list the nominal files first)')
parser.add_option('--samesample', action='store_true', dest='sameData',
        default=True, help='fit results obtained on same sample (default)')
parser.add_option('--indepsamples', action='store_false', dest='sameData',
        help='fit results represent two independent samples')
parser.add_option('--nosamesample', action='store_false', dest='sameData',
        help='alias for --indepsamples')
parser.add_option('--noindepsamples', action='store_true', dest='sameData',
        help='alias for --samesample')
parser.add_option('--debug', action='store_true', dest='debug', default=False,
        help='print debugging info')
(options, args) = parser.parse_args()
if '-' == args[0]: args.pop(0)

if options.systematic:
    options.diff = True
    if not options.sameData:
        raise ValueError('Systematic mode needs to run on fit results for '
                'the same data sample!')

if None == options.isData:
    raise ValueError('You need to specify if you are running on DATA or TOYS (--data/--toy)')
debug = options.debug
gc.collect()

if not options.isData: options.blinding = False
if options.diff and not options.avg and len(args) != 2:
    raise ValueError('Diff/Systematic mode take exactly two ROOT files as '
            'arguments.')
elif options.avg and not options.diff and len(args) != 2:
    raise ValueError('Averaging mode take exactly two ROOT files as '
            'arguments.')
elif options.avg and options.diff and len(args) != 3:
    raise ValueError('Average/Diff mode take exactly three ROOT files as '
            'arguments.')

print 'Running with settings:'
print '\tMode: %s%s' % (
        'DATA' if options.isData else 'TOY', ', BLINDED' if options.blinding else '')
if options.diff:
    print '\tRunning in difference mode (toy-by-toy etc.)'
if options.systematic:
    print '\tRunning in systematic mode'
if options.diff:
    print '\tAssuming fit results were obtained from %s' % ('same data sample'
            if options.sameData else 'independent data samples')
print
gc.collect()

veryoldres = None
oldres = None
res = None
for fname in args:
    veryoldres = oldres
    oldres = res
    res = grabResult(options.isData, options.blinding, fname)
    if None == res:
        raise ValueError('Unable to read fit result from %s' % fname)
    print 72 * '*'
    print 'FIT RESULT FROM %s' % fname
    print 72 * '*'
    print res
    print 72 * '*'
    print

if options.diff or options.systematic or options.avg:
    for r in (res, oldres):
        if options.systematic: r.setOptions(['Systematic'])
        elif options.diff:
            if options.sameData: r.setOptions(['SameDataSet'])
    print 72 * '*'
    if options.avg:
        print 'WEIGHTED AVERAGE(FIT1, FIT2)'
        print 72 * '*'
        tmpres = (oldres + veryoldres) if None != veryoldres else (res + oldres)
        print tmpres
    else:
        print 'DIFFERENCE (FIT2 - FIT1) - IGNORE CORRELATIONS, AT LIMIT WARNINGS'
        print 72 * '*'
        print (res - oldres)
    print 72 * '*'
    print
    if None != veryoldres:
        print 72 * '*'
        print 'WEIGHTED AVERAGE(FIT1, FIT2) - FIT3 - IGNORE CORRELATIONS, AT LIMIT WARNINGS'
        print 72 * '*'
        print (tmpres - res)
        print 72 * '*'
        print


