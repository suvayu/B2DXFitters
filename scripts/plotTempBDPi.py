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
from B2DXFitters import *
from ROOT import *

from optparse import OptionParser
from math     import pi, log
import os, sys, gc

gROOT.SetBatch()

#------------------------------------------------------------------------------
def runComparePDF( debug, file1, work1, obsName) :

    workspace1 = GeneralUtils.LoadWorkspace(TString(file1),TString(work1),debug)
    obs   = GeneralUtils.GetObservable(workspace1,TString(obsName), debug)
    workspace1.Print("v")

    if obsName == "lab0_MassFitConsD_M":
        namePDF1 = "PhysBkgBd2DPiPdf_m_down_kpipi"
        namePDF2 = "PhysBkgBd2DPiPdf_m_up_kpipi"
    elif obsName == "lab2_MM":
        namePDF1 = "PhysBkgBd2DPiPdf_m_down_kpipi_Ds"
        namePDF2 = "PhysBkgBd2DPiPdf_m_up_kpipi_Ds"
    else:
        namePDF1 = "PIDKShape_Bd2DPi_down"
        namePDF2 = "PIDKShape_Bd2DPi_up"

    pdf1 =  Bs2Dsh2011TDAnaModels.GetRooBinned1DFromWorkspace(workspace1,TString(namePDF1), debug)
    pdf2 =  Bs2Dsh2011TDAnaModels.GetRooBinned1DFromWorkspace(workspace1,TString(namePDF2), debug)

    frac = RooRealVar("frac","frac",0.427184466019);
    namePDF = "PhysBkgBd2DPiPdf_m_both_kpipi"
    pdf = RooAddPdf( namePDF, namePDF,RooArgList(pdf2,pdf1), RooArgList(frac))

    nameData1 = "dataSet_Miss_down_kpipi"
    data1 = GeneralUtils.GetDataSet(workspace1,TString(nameData1),  debug)
    nameData2 = "dataSet_Miss_up_kpipi"
    data2 = GeneralUtils.GetDataSet(workspace1,TString(nameData2),  debug)    
    data1.append(data2)
    
    canv = TCanvas("canv","canv", 1200,1000)
    frame = obs.frame()
    frame.SetTitle("")
    
    if obsName == "lab0_MassFitConsD_M":
        label = "mass B_{s} [MeV/c^{2}]"
    elif obsName == "lab2_MM":
        label = "mass D_{s} [MeV/c^{2}]"
    else:
        label = "-PIDK [1]"

    frame.GetXaxis().SetTitle(label)
    frame.GetYaxis().SetTitle(' ')
    frame.GetXaxis().SetLabelFont( 132 );
    frame.GetYaxis().SetLabelFont( 132 );
    frame.GetXaxis().SetLabelSize( 0.05 );
    frame.GetYaxis().SetLabelSize( 0.05 );
    frame.GetXaxis().SetTitleFont( 132 );
    frame.GetYaxis().SetTitleFont( 132 );
    frame.GetXaxis().SetTitleSize( 0.04 );
    frame.GetYaxis().SetTitleSize( 0.04 );
    if obsName != "lab1_PIDK":
        frame.GetXaxis().SetLabelColor( kWhite)

    if obsName != "lab2_MM":
        legend = TLegend(  0.60, 0.53, 0.88, 0.88  )
    else:
        legend = TLegend(  0.60, 0.18, 0.88, 0.45  )

    legend.SetTextSize(0.06)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    legend.SetHeader("LHCb")
    

    scaleA = data1.sumEntries()/data2.sumEntries()
    if obsName != "lab1_PIDK":
        data1.plotOn(frame,RooFit.MarkerColor(kOrange-3), RooFit.Binning(100))

    text1 = "B_{d} #rightarrow D #pi"
    gr = TGraphErrors(10);
    gr.SetName("gr");
    gr.SetLineColor(kBlack);
    gr.SetLineWidth(2);
    gr.SetMarkerStyle(20);
    gr.SetMarkerSize(2.5);
    gr.SetMarkerColor(kOrange-3);
    gr.Draw("P");
    if obsName != "lab1_PIDK":
        legend.AddEntry("gr",text1,"lep");
    
    pdf.plotOn(frame, RooFit.LineColor(kOrange-3))

    l1 = TLine()
    l1.SetLineColor(kOrange-3)
    l1.SetLineWidth(4)
    l1.SetLineStyle(kSolid)
    legend.AddEntry(l1, text1 , "L")

    if obsName != "lab1_PIDK":
        pad1 = TPad("upperPad", "upperPad", .050, .20, 1.0, 1.0)
        pad1.SetBorderMode(0)
        pad1.SetBorderSize(-1)
        pad1.SetFillStyle(0)
        pad1.SetBottomMargin(0.13)
        pad1.SetTopMargin(0.99)
        pad1.SetTickx(0);
        pad1.Draw() 
        pad1.cd()

    frame.Draw()
    legend.Draw("same")
    #frame.GetYaxis().SetRangeUser(0.1,250.)
    #canv.GetPad(0).SetLogy()

    frame.Print("v")
    
    if obsName != "lab1_PIDK":
        pad1.Update()

        canv.cd()
        pad2 = TPad("lowerPad", "lowerPad", .050, .005, 1.0, .3275)
        pad2.SetBorderMode(0)
        pad2.SetBorderSize(-1)
        pad2.SetFillStyle(0)
        pad2.SetBottomMargin(0.35)
        pad2.SetTickx(0);
        pad2.Draw()
        pad2.SetLogy(0)
        pad2.cd()
        
        gStyle.SetOptLogy(0)

        frame_p = obs.frame(RooFit.Title("pull_frame"))
        frame_p.Print("v")
        frame_p.SetTitle("")
        frame_p.GetYaxis().SetTitle("")
        frame_p.GetYaxis().SetTitleSize(0.09)
        frame_p.GetYaxis().SetTitleOffset(0.26)
        frame_p.GetYaxis().SetTitleFont(62)
        frame_p.GetYaxis().SetNdivisions(106)
        frame_p.GetYaxis().SetLabelSize(0.12)
        frame_p.GetYaxis().SetLabelOffset(0.006)
        frame_p.GetXaxis().SetTitleSize(0.15)
        frame_p.GetXaxis().SetTitleFont(132)
        frame_p.GetXaxis().SetTitleOffset(0.85)
        frame_p.GetXaxis().SetNdivisions(512)
        frame_p.GetYaxis().SetNdivisions(5)
        frame_p.GetXaxis().SetLabelSize(0.12)
        frame_p.GetXaxis().SetLabelFont( 132 )
        frame_p.GetYaxis().SetLabelFont( 132 )
        if obsName == "lab0_MassFitConsD_M":
            frame_p.GetXaxis().SetTitle('#font[12]{mass B_{s} [MeV/c^{2}]}')
        else:
            frame_p.GetXaxis().SetTitle('#font[12]{mass D_{s} [MeV/c^{2}]}')
        pullHist  = frame.pullHist()
        pullHist.SetMaximum(4.00)
        pullHist.SetMinimum(-4.00)
        
        range_dw = obs.getMin()
        range_up = obs.getMax()
    
        max = 4.0
        min = -4.0
        graph = TGraph(2)
        graph.SetMaximum(max)
        graph.SetMinimum(min)
        graph.SetPoint(1,range_dw,0)
        graph.SetPoint(2,range_up,0)
        

        graph2 = TGraph(2)
        graph2.SetMaximum(max)
        graph2.SetMinimum(min)
        graph2.SetPoint(1,range_dw,-3)
        graph2.SetPoint(2,range_up,-3)
        
        graph2.SetLineColor(kRed)
        graph3 = TGraph(2)
        graph3.SetMaximum(max)
        graph3.SetMinimum(min)
        graph3.SetPoint(1,range_dw,3)
        graph3.SetPoint(2,range_up,3)
        graph3.SetLineColor(kRed)

    

        frame_p.addPlotable(pullHist,"P")
        frame_p.Draw()
        frame_p.GetYaxis().SetRangeUser(-4.0,4.0)
        graph.Draw("same")
        graph2.Draw("same")
        graph3.Draw("same")
        
        pad2.Update()
    canv.Update()    

    canv.Print("template_BsDsPi_%s_Bd2DPi.pdf"%(obsName))
    canv.Print("template_BsDsPi_%s_Bd2DPi.pdf"%(obsName))

#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--file1',
                   dest = 'file1',
                   default = 'work_dspi_pid_53005800_PIDK0_5M_BDTGA.root')

parser.add_option( '--work1',
                   dest = 'work1',
                   default = 'workspace')

parser.add_option( '--obs',
                   dest = 'obs',
                   default = 'lab1_PIDK')

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    import sys
    sys.path.append("../data/")

    runComparePDF( options.debug,
                   options.file1, options.work1,
                   options.obs
                   )                                
# -----------------------------------------------------------------------------
                                
