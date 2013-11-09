# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to compare datas or pdfs                                    #
#                                                                             #
#   Example usage:                                                            #
#      python comparePDF.py                                                   #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 28 / 06 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
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
from B2DXFitters import *
from ROOT import *

from optparse import OptionParser
from math     import pi, log
import os, sys, gc

gROOT.SetBatch()

#------------------------------------------------------------------------------
def runComparePDF( debug, name1, file1, work1, text1, name2, file2, work2, text2, obs, data ) :

    workspace1 = GeneralUtils.LoadWorkspace(TString(file1),TString(work1),debug)
    workspace2 = GeneralUtils.LoadWorkspace(TString(file2),TString(work2),debug)

    obs   = GeneralUtils.GetObservable(workspace1,TString(obs), debug)
    #if not data:
        #obs.setRange(0,150)

    if not data:
        pdf1 =  Bs2Dsh2011TDAnaModels.GetRooBinned1DFromWorkspace(workspace1,TString(name1), debug)
        pdf1.SetName("pdf1")
        pdf2 =  Bs2Dsh2011TDAnaModels.GetRooBinned1DFromWorkspace(workspace2,TString(name2), debug)
        pdf2.SetName("pdf2")
    else:
        data1 = GeneralUtils.GetDataSet(workspace1,TString(name1),  debug)
        data2 = GeneralUtils.GetDataSet(workspace2,TString(name2),  debug)
    
    canv = TCanvas("canv","canv", 1200,1000)
    frame = obs.frame()
    frame.SetTitle("")

    legend = TLegend( 0.70, 0.75, 0.88, 0.88 )

    legend.SetTextSize(0.03)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    legend.SetHeader("LHCb")
    
    if data:
        scaleA = data1.sumEntries()/data2.sumEntries()
        print data1.numEntries()
        print data2.numEntries()
        print data1.sumEntries()
        print data2.sumEntries()
        print file1
        print file2
        
        data1.plotOn(frame,RooFit.MarkerColor(kBlue+2), RooFit.Binning(74))
        data2.plotOn(frame,RooFit.MarkerColor(kRed),RooFit.Rescale(scaleA), RooFit.Binning(74))

        gr = TGraphErrors(10);
        gr.SetName("gr");
        gr.SetLineColor(kBlack);
        gr.SetLineWidth(2);
        gr.SetMarkerStyle(20);
        gr.SetMarkerSize(1.3);
        gr.SetMarkerColor(kBlue+2);
        gr.Draw("P");
        legend.AddEntry("gr",text1,"lep");
        
        gr2 = TGraphErrors(10);
        gr2.SetName("gr2");
        gr2.SetLineColor(kBlack);
        gr2.SetLineWidth(2);
        gr2.SetMarkerStyle(20);
        gr2.SetMarkerSize(1.3);
        gr2.SetMarkerColor(kRed);
        gr2.Draw("P");
        legend.AddEntry("gr2",text2,"lep");
                                                                
                                                                                
    else:
        pdf1.plotOn(frame, RooFit.LineColor(kRed))
        pdf2.plotOn(frame, RooFit.LineColor(kBlue+2))

        l1 = TLine()
        l1.SetLineColor(kRed)
        l1.SetLineWidth(4)
        l1.SetLineStyle(kSolid)
        legend.AddEntry(l1, text1 , "L")

        l2 = TLine()
        l2.SetLineColor(kBlue+2)
        l2.SetLineWidth(4)
        l2.SetLineStyle(kSolid)
        legend.AddEntry(l2, text2 , "L")
                        

    frame.Draw()
    legend.Draw("same")
    #frame.GetYaxis().SetRangeUser(0.1,250.)
    #canv.GetPad(0).SetLogy()
    canv.Print("comparison.pdf")
                                                                                    

#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--name1',
                   dest = 'name1',
                   default = 'PIDKShape_Bs2DsPi_up_nonres')

parser.add_option( '--file1',
                   dest = 'file1',
                   default = 'work_dspi_pid_53005800_PIDK0_5M_BDTGA.root')

parser.add_option( '--work1',
                   dest = 'work1',
                   default = 'workspace')
parser.add_option( '--text1',
                   dest = 'text1',
                   default = 'text1')

parser.add_option( '--name2',
                   dest = 'name2',
                   default = 'PIDKShape_Bs2DsPi_up_phipi')

parser.add_option( '--file2',
                   dest = 'file2',
                   default = 'work_dspi_pid_53005800_PIDK0_5M_BDTGA.root')

parser.add_option( '--work2',
                   dest = 'work2',
                   default = 'workspace')

parser.add_option( '--text2',
                   dest = 'text2',
                   default = 'text2')

parser.add_option( '--obs',
                   dest = 'obs',
                   default = 'lab1_PIDK')

parser.add_option( '--data',
                   dest = 'data',
                   action = 'store_true',
                   default = False)

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    import sys
    sys.path.append("../data/")

    runComparePDF( options.debug,
                   options.name1 , options.file1, options.work1, options.text1,
                   options.name2 , options.file2, options.work2, options.text2,
                   options.obs, options.data
                   )                                
# -----------------------------------------------------------------------------
                                
