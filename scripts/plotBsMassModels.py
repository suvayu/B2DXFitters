#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot the Bd -> D pi mass models                          #
#                                                                             #
#   Example usage:                                                            #
#      python -i plotBdMassModels.py                                          #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 27 / 05 / 2011                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #
# -----------------------------------------------------------------------------
# settings for running without GaudiPython
# -----------------------------------------------------------------------------
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
exec $schedtool /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from math     import pi
import os, sys, gc

if 'CMTCONFIG' in os.environ:
    import GaudiPython
import ROOT
# avoid memory leaks - will have to explicitly relinquish and acquire ownership
# if required, but PyROOT does not do what it thinks best without our knowing
# what it does
ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
if not 'CMTCONFIG' in os.environ:
    # enable ROOT to understand Reflex dictionaries
    ROOT.gSystem.Load('libCintex')
    ROOT.Cintex.Enable()
# load RooFit
ROOT.gSystem.Load('libRooFit')
from ROOT import RooFit
# load our own B2DXFitters library
if 'CMTCONFIG' in os.environ:
    GaudiPython.loaddict('B2DXFittersDict')
else:
    # running in standalone mode, we have to load things ourselves
    ROOT.gSystem.Load(os.environ['B2DXFITTERSROOT'] +
            '/standalone/libB2DXFitters')

# figure out if we're running from inside gdb
def in_gdb():
    import os
    proclist = dict(
            (l[0], l[1:]) for l in (
                lraw.replace('\n', '').replace('\r','').split()
                for lraw in os.popen('ps -o pid= -o ppid= -o comm=').readlines()
                )
            )
    pid = os.getpid()
    while pid in proclist:
        if 'gdb' in proclist[pid][1]: return True
        pid = proclist[pid][0]
    return False

if in_gdb():
    # when running in a debugger, we want to make sure that we do not handle
    # any signals, so the debugger can catch SIGSEGV and friends, and we can
    # poke around
    ROOT.SetSignalPolicy(ROOT.kSignalFast)
    ROOT.gEnv.SetValue('Root.Stacktrace', '0')


from ROOT import *
gROOT.SetBatch()


# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True
bName = 'B_{s}'


#------------------------------------------------------------------------------
def plotDataSet( dataset, frame ) :
    dataset.plotOn( frame,
                    RooFit.Binning( 70 ) )
    dataset.statOn( frame,
                    RooFit.Layout( 0.56, 0.90, 0.90 ),
                    RooFit.What('N') )

#------------------------------------------------------------------------------
def plotFitModel( model, frame ) :
    model.plotOn( frame,
                  RooFit.Components('Bd2DPiEPDF_m'),
                  RooFit.LineColor(kYellow+1),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('Bs2DsstPiEPDF_m'),
                  RooFit.LineColor(kMagenta),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('Bs2DsRhoEPDF_m'),
                  RooFit.LineColor(kOrange+2),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('Bs2DsXEPDF_m'),
                  RooFit.LineColor(kCyan-8),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('Lb2LcPiEPDF_m'),
                  RooFit.LineColor(kCyan),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('CombBkgEPDF_m'),
                  RooFit.LineColor( kGreen ),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('CombBkgEPDF_m,Bd2DPiEPDF_m,Bs2DsRhoEPDF_m,Bs2DsstPiEPDF_m,Bs2DsXEPDF_m,Lb2LcPiEPDF_m'),
                  RooFit.DrawOption( 'F' ),
                  RooFit.FillStyle( 3002 ),
                  RooFit.FillColor( 30 ),
                  RooFit.VLines(),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('SigEPDF'),
                  RooFit.LineColor(kRed-7),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.LineColor(kBlue),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.paramOn( frame,
                   RooFit.Layout( 0.56, 0.90, 0.85 ),
                   RooFit.Format( 'NEU', RooFit.AutoPrecision( 2 ) )
                   )
    
    stat = frame.findObject( 'data_statBox' )
    if not stat:
        stat = frame.findObject( 'TotEPDF_mData_statBox' )
    if stat :
        stat.SetTextSize( 0.025 )
    pt = frame.findObject( 'TotEPDF_m_paramBox' )
    if pt :
        pt.SetTextSize( 0.02 )
        pt.SetY1NDC( 0.40 )
    # Legend of EPDF components
    leg = TLegend( 0.13, 0.57, 0.44, 0.87 )
    leg.SetFillColor( 0 )
    leg.SetTextSize( 0.02 )
    comps = model.getComponents()
    pdf = comps.find( 'Bd2DPiEPDF_m' )
    pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bd2DPiEPDF_m'
    curve = frame.findObject( pdfName )
    leg.AddEntry( curve, pdf.GetTitle(), 'l' )
    frame.addObject( leg )
    pdf = comps.find( 'Bs2DsstPiEPDF_m' )
    pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bs2DsstPiEPDF_m'
    curve2 = frame.findObject( pdfName )
    leg.AddEntry( curve2, pdf.GetTitle(), 'l' )
    frame.addObject( leg )
    pdf = comps.find( 'Bs2DsRhoEPDF_m' )
    pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bs2DsRhoEPDF_m'
    curve3 = frame.findObject( pdfName )
    leg.AddEntry( curve3, pdf.GetTitle(), 'l' )
    frame.addObject( leg )
    pdf = comps.find( 'Bs2DsXEPDF_m' )
    pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bs2DsXEPDF_m'
    curve4 = frame.findObject( pdfName )
    leg.AddEntry( curve4, pdf.GetTitle(), 'l' )
    frame.addObject( leg )
    pdf = comps.find( 'Lb2LcPiEPDF_m' )
    pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Lb2LcPiEPDF_m'
    curve5 = frame.findObject( pdfName )
    leg.AddEntry( curve5, pdf.GetTitle(), 'l' )
    frame.addObject( leg )
    pdf = comps.find( 'CombBkgEPDF_m' )
    pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'CombBkgEPDF_m'
    curve6 = frame.findObject( pdfName )
    leg.AddEntry( curve6, pdf.GetTitle(), 'l' )
    frame.addObject( leg )
    pdf = comps.find( 'SigEPDF' )
    pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'SigEPDF'
    curve7 = frame.findObject( pdfName )
    leg.AddEntry( curve7, pdf.GetTitle(), 'l' )
    frame.addObject( leg )
    if debug :
        model.Print( 't' )
        frame.Print( 'v' )

#------------------------------------------------------------------------------
_usage = '%prog [options] <filename>'

parser = OptionParser( _usage )

parser.add_option( '-w', '--workspace',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   default = 'FitterWS',
                   help = 'RooWorkspace name as stored in ROOT file'
                   )

#------------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) != 1 :
        parser.print_help()
        exit( -1 )
    
    FILENAME = ( args[ 0 ] )
    if not exists( FILENAME ) :
        parser.error( 'ROOT file "%s" not found! Nothing plotted.' % FILENAME )
        parser.print_help()
    
    from ROOT import TFile, TCanvas, gROOT, TLegend
    from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed
    from ROOT import RooFit, RooRealVar, RooAbsReal

    gROOT.SetStyle( 'Plain' )
    gROOT.SetBatch( False )
    
    f = TFile( FILENAME )

    w = f.Get( options.wsname )
    if not w :
        parser.error( 'Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      ( options.wsname, FILENAME ) )
    
    f.Close()
    
    canvas = TCanvas( 'MassCanvas', 'Mass canvas', 1200, 800 )
    canvas.SetTitle( 'Fit in mass' )
    canvas.cd()
    
    mass = w.var( 'mass' )
    mean  = 5366.
    mass = RooRealVar( "mass", "%s mass" % bName, mean, 4800, 5850, "MeV/c^{2}" )
    
    modelPDF = w.pdf( 'TotEPDF_m' )
    dataset = w.data( 'TotEPDF_mData' )
    
    frame_m = mass.frame()
    
    frame_m.SetTitle( 'Fit in reconstructed %s mass' % bName )
    
    frame_m.GetXaxis().SetLabelSize( 0.03 )
    frame_m.GetYaxis().SetLabelSize( 0.03 )
    
    if plotData : plotDataSet( dataset, frame_m )
    
    if plotModel : plotFitModel( modelPDF, frame_m )
    
    frame_m.Draw()
    
    pt = canvas.FindObject( 'TotEPDF_m_paramBox' )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update() 
    
#------------------------------------------------------------------------------
