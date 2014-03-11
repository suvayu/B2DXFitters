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
def runComparePDF( debug, direct, work, obsName, mode, signal) :

    modeTS = TString(mode) 
    obsTS = TString(obsName)
    if obsName == "lab1_PIDK":
        print "[ERROR] Plotting PIDK is not supported by this script, please use plotShapes.py"
        exit(0)

    modesDs = ["nonres", "", "phipi", "kstk", "kpipi", "pipipi"]
    ModesDs = ["NonRes", "PhiPi", "KstK", "KPiPi", "PiPiPi"]
    capDs   = ["NonRes", "", "#phi #pi","K*K", "K #pi #pi", "#pi #pi #pi"]
    capDs2  = ["KK#pi","(Non Resonant)","#phi #pi","K*K", "K #pi #pi", "#pi #pi #pi"]
    cap = []
    Ds = "D_{s} #rightarrow"
    for n in capDs2:
        if n != "(Non Resonant)":
            cap.append(Ds+n)
        else:
            cap.append(n)

    color5M = [kBlue-2, kBlue-2, kBlue-2, kBlue-2, kBlue-2]
    style5M = [1,2,3,6,9]

    color5ML = [kBlue-2, kWhite, kBlue-2, kBlue-2, kBlue-2, kBlue-2]
    style5ML = [1,1, 2,3,6,9]

    fileNamesSig = []
    workSig = []
    dataSig = []
    pdfSig = [] 
   
    if obsName == "lab0_MassFitConsD_M":
        sufSig = "Bs_5100_5500"
    else:
        sufSig = "Ds"

    for m in ModesDs:
        if signal:
            fileNamesSig.append(direct+"WS_MC_"+mode+"_"+m+"_"+sufSig+".root")                                                 
        else:
            fileNamesSig.append(direct+"WS_CombBkg_"+mode+"_"+m+"_"+sufSig+".root")
            
    for i in range(0,5):
        if fileNamesSig != "":
            workSig.append(GeneralUtils.LoadWorkspace(TString(fileNamesSig[i]),TString(work),debug))
        if signal:
            workSig[i].factory("SUM:FullPdf(nSigEvts_both*SigEPDF_both)")                                                              
        else:
            workSig[i].factory("SUM:FullPdf(nCombBkgEvts_both*CombBkgEPDF_both)")
        dataSig.append(GeneralUtils.GetDataSet(workSig[i], TString("combData"), debug))
        pdfSig.append(workSig[i].pdf("FullPdf"))
        
        print "data contains: %d"%(dataSig[i].numEntries())

    pullname2TS = TString("h_combData_Cut[sample==sample::both]")
    pullname3TS = TString("SigEPDF_both")
    pullnameTS = TString("FullPdf_Norm[")+obsTS+TString("]")
    pullHist = [ ]

    canv = TCanvas("canv","canv", 2000,1000)
    
    obs   = GeneralUtils.GetObservable(workSig[0],TString(obsName), debug)
    frame = obs.frame()
    frame.SetTitle("")

    if obsName == "lab0_MassFitConsD_M": 
        label = '#font[12]{mass B_{s} [MeV/c^{2}]}'
    elif (obsName == "lab2_MM"):
        label = '#font[12]{mass D_{s} [MeV/c^{2}]}'
    else:
        label = "log(PIDK) [1]"
    frame.GetXaxis().SetTitle(label)
    frame.GetYaxis().SetTitle(' ')
    frame.GetXaxis().SetLabelFont( 132 );
    frame.GetYaxis().SetLabelFont( 132 );
    frame.GetXaxis().SetLabelSize( 0.04 );
    frame.GetYaxis().SetLabelSize( 0.04 );
    frame.GetXaxis().SetTitleFont( 132 );
    frame.GetYaxis().SetTitleFont( 132 );
    frame.GetXaxis().SetTitleSize( 0.04 );
    frame.GetYaxis().SetTitleSize( 0.04 );

    frame2 = obs.frame()
    frame2.SetTitle("")
    frame2.GetXaxis().SetTitle(label)
    frame2.GetYaxis().SetTitle(' ')
    frame2.GetXaxis().SetLabelFont( 132 );
    frame2.GetYaxis().SetLabelFont( 132 );
    frame2.GetXaxis().SetLabelSize( 0.04 );
    frame2.GetYaxis().SetLabelSize( 0.04 );
    frame2.GetXaxis().SetTitleFont( 132 );
    frame2.GetYaxis().SetTitleFont( 132 );
    frame2.GetXaxis().SetTitleSize( 0.04 );
    frame2.GetYaxis().SetTitleSize( 0.04 );

    #frame.GetXaxis().SetLabelColor( kWhite)
    
    legend = TLegend(  0.12, 0.60, 0.35, 0.88  )

    legend.SetTextSize(0.045)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    #legend.SetHeader("LHCb")
    
    lhcbtext = TLatex()
    lhcbtext.SetTextFont(132)
    lhcbtext.SetTextColor(1)
    lhcbtext.SetTextSize(0.06)
    lhcbtext.SetTextAlign(12)

    l = []
    for i in range(0,5):
        dataSig[i].plotOn(frame2,RooFit.Cut("sample==sample::both"), RooFit.Invisible())
        pdfSig[i].plotOn(frame2, RooFit.LineColor(color5M[i]),RooFit.LineStyle(style5M[i]))
        pdfSig[i].plotOn(frame, RooFit.LineColor(color5M[i]),RooFit.LineStyle(style5M[i]))
        pullHist.append(frame2.pullHist(pullname2TS.Data(),pullnameTS.Data()))

    for i in range(0,6):    
        l.append(TLine())
        l[i].SetLineColor(color5ML[i])
        l[i].SetLineWidth(4)
        l[i].SetLineStyle(style5ML[i])
        legend.AddEntry(l[i], cap[i] , "L")
        
       
    pad1 = TPad("upperPad", "upperPad",  0.005, 0.005, 0.5, 0.99)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetBottomMargin(0.13)
    pad1.SetTopMargin(0.99)
    pad1.SetTickx(0);
    if obsName == "lab0_MassFitConsD_M":
        pad1.SetLogy(1)
    pad1.Draw() 
    pad1.cd()

    frame.Draw()
    legend.Draw("same")
    if obsName == "lab0_MassFitConsD_M":
        lhcbtext.DrawTextNDC( 0.72 , 0.85, "LHCb")
    else:
        lhcbtext.DrawTextNDC( 0.72 , 0.85, "LHCb")
    #frame.GetYaxis().SetRangeUser(0.1,250.)
    #canv.GetPad(0).SetLogy()

    frame.Print("v")
    pad1.Update()
    
    canv.cd()
    

    x = [.5, 1.0]
    y1 = [ 0.005, 0.195, 0.385, 0.575, 0.765]
    y2 = [ 0.190, 0.380, 0.570, 0.760, 0.950]
    y  = []
        
    graph = []
    graph2 = []
    graph3 = []
    pad2 = []
    frame_p = []
    text = []
    for i in range (0,5):
        canv.cd()
        namepad = "lowerPad"+str(i)
        if i == 4:
            y1A = y1[4-i]+0.01
            y2A = y2[4-i]+0.07
        elif i == 2:
            y1A = y1[4-i]-0.03
            y2A = y2[4-i]+0.03
        elif i == 0:
            y1A = y1[4-i]-0.06
            y2A = y2[4-i]
        elif i == 1:
            y1A = y1[4-i]-0.04
            y2A = y2[4-i]+0.02
        elif i == 3:
            y1A = y1[4-i]-0.01
            y2A = y2[4-i]+0.045
        else:
            y1A = y1[4-i]
            y2A = y2[4-i]

        pad2.append(TPad(namepad, namepad,  x[0], y1A, x[1], y2A))    
        pad2[i].SetBorderMode(0)
        pad2[i].SetBorderSize(-1)
        pad2[i].SetFillStyle(0)
        pad2[i].SetBottomMargin(0.35)
        pad2[i].SetTickx(0);
        pad2[i].Draw()
        pad2[i].SetLogy(0)
        pad2[i].cd()
        
        gStyle.SetOptLogy(0)
        
        frame_p.append(obs.frame(RooFit.Title("pull_frame")))
        frame_p[i].Print("v")
        frame_p[i].SetTitle("")
        frame_p[i].GetYaxis().SetTitle("")
        frame_p[i].GetYaxis().SetTitleSize(0.09)
        frame_p[i].GetYaxis().SetTitleOffset(0.26)
        frame_p[i].GetYaxis().SetTitleFont(62)
        frame_p[i].GetYaxis().SetNdivisions(106)
        frame_p[i].GetYaxis().SetLabelSize(0.12)
        frame_p[i].GetYaxis().SetLabelOffset(0.006)
        frame_p[i].GetXaxis().SetTitleSize(0.15)
        frame_p[i].GetXaxis().SetTitleFont(132)
        frame_p[i].GetXaxis().SetTitleOffset(0.85)
        frame_p[i].GetXaxis().SetNdivisions(512)
        frame_p[i].GetYaxis().SetNdivisions(5)
        frame_p[i].GetXaxis().SetLabelSize(0.15)
        frame_p[i].GetXaxis().SetLabelFont( 132 )
        frame_p[i].GetYaxis().SetLabelFont( 132 )
        frame_p[i].GetXaxis().SetTitle('#font[12]{mass B_{s} [MeV/c^{2}]}')
            
        if i != 4:
            frame_p[i].GetXaxis().SetLabelColor( kWhite)
            frame_p[i].GetXaxis().SetTitle("")

            #pullHist.append(frame2.pullHist(pullname2TS.Data(),pullnameTS.Data()))
            #pullHist[i].SetMaximum(3.99)
             #pullHist[i].SetMinimum(-3.99)
    
        range_dw = obs.getMin()        
        range_up = obs.getMax()
        
        axisY = pullHist[i].GetYaxis()
        max = axisY.GetXmax()
        min = axisY.GetXmin()
        
        graph.append(TGraph(2))
        graph[i].SetMaximum(max)
        graph[i].SetMinimum(min)
        graph[i].SetPoint(1,range_dw,0)
        graph[i].SetPoint(2,range_up,0)

        graph2.append(TGraph(2))
        graph2[i].SetMaximum(max)
        graph2[i].SetMinimum(min)
        graph2[i].SetPoint(1,range_dw,-3)
        graph2[i].SetPoint(2,range_up,-3)
        graph2[i].SetLineColor(kRed)
        
        graph3.append(TGraph(2))
        graph3[i].SetMaximum(max)
        graph3[i].SetMinimum(min)
        graph3[i].SetPoint(1,range_dw,3)
        graph3[i].SetPoint(2,range_up,3)
        graph3[i].SetLineColor(kRed)
        
        text.append(TLatex())
        text[i].SetTextFont(132)
        text[i].SetTextColor(1)
        text[i].SetTextSize(0.20)
        text[i].SetTextAlign(22)
        text[i].SetTextAngle(90)
            

        frame_p[i].addPlotable(pullHist[i],"P")
        frame_p[i].Draw()
        frame_p[i].GetYaxis().SetRangeUser(-4.0,4.0)
        graph[i].Draw("same")
        graph2[i].Draw("same")
        graph3[i].Draw("same")
        
        text[i].DrawTextNDC(0.03, 0.605, ModesDs[i])
        pad2[i].Update()

    canv.Update()

    if signal:
        canv.Print("template_Signal_%s_%s.pdf"%(obsName,mode))
        canv.Print("template_Signal_%s_%s.root"%(obsName,mode))
    else:
        canv.Print("template_CombBkg_%s_%s.pdf"%(obsName,mode))
        canv.Print("template_CombBkg_%s_%s.root"%(obsName,mode))

#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--dir',
                   dest = 'dir',
                   default = './')

parser.add_option( '--work1',
                   dest = 'work1',
                   default = 'FitMeToolWS')

parser.add_option( '--obs',
                   dest = 'obs',
                   default = 'lab0_MassFitConsD_M')
parser.add_option( '--mode',
                   dest = 'mode',
                   default = 'BsDsPi')

parser.add_option( '--signal',
                   action = 'store_true',
                   dest = 'signal',
                   default = False
                   )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    import sys
    sys.path.append("../data/")

    runComparePDF( options.debug,
                   options.dir, options.work1, 
                   options.obs, options.mode, options.signal
                   )                                
# -----------------------------------------------------------------------------
                                
