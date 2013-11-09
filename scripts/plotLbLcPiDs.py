#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot signals MC B->DPi, Bs->DsPi, Bs->DsK                #
#                                                                             #
#   Example usage:                                                            #
#      python plotSignal.py WS.root -m both --mode BDPi                       #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 21 / 02 / 2012                                                    #
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

from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc
gROOT.SetBatch()

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True

#------------------------------------------------------------------------------
_usage = '%prog [options] <filename>'

parser = OptionParser( _usage )

parser.add_option( '-w', '--workspace',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   default = 'FitMeToolWS',
                   help = 'RooWorkspace name as stored in ROOT file'
                   )
parser.add_option( '-m', '--sample',
                   dest = 'sample',
                   metavar = 'SAMPLE',
                   default = 'up',
                   help = 'Sample: choose up or down '
                   )

parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_MassHypo_LcPi_LambdaFav',
                   help = 'set observable '
                   )
parser.add_option( '--mode',
                   dest = 'mode',
                   default = 'BsDsPi',
                   help = 'set observable '
                   )
parser.add_option( '--merge',
                   action = 'store_true',
                   dest = 'merge',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '-s', '--sufix',
                   dest = 'sufix',
                   metavar = 'SUFIX',
                   default = '',
                   help = 'Add sufix to output'
                   )


#------------------------------------------------------------------------------
def plotDataSet( dataset, frame, sample, merge ) :

    bin = 100
    if sample == "both":
        if merge == True:
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::both"),
                            RooFit.Binning( bin ) )
        else:
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up || sample==sample::down"),
                            RooFit.Binning( bin ) )
    elif sample == "up":
        dataset.plotOn( frame,
                        RooFit.Cut("sample==sample::up"),
                        RooFit.Binning( bin ) )
                                                
    elif sample == "down":
         dataset.plotOn( frame,
                         RooFit.Cut("sample==sample::down"),
                         RooFit.Binning( bin ) )
    else:
        print "[ERROR] Wrong sample!"
                                                                         
       
#------------------------------------------------------------------------------
def plotFitModel( model, frame, sam, var, merge) :
    #if debug :
    
    print "model"    
    model.Print( 't' )
    obsTS = TString(var) 

    print "frame"
    frame.Print( 'v' )
    t=TString("_")
    p=TString(",")
    nameTot = TString("FullPdf")
    if sam == "both":
        if merge == True:
            nameComb1 = TString("CombBkgEPDF_both")
            nameComb2 = TString("CombBkgEPDF_both")
            nameSig1  = TString("SignalEPDF_both")
            nameSig2  = TString("SignalEPDF_both") 
        else:
            nameSig1 = TString("CombBkgEPDF_down,CombBkgEPDF_up")
            nameSig2 = TString("CombBkgEPDF_down,CombBkgEPDF_up")
            
            
    elif sam == "down" :
        nameSig1 = TString("CombBkgEPDF_down") #TString("DblGPDFdown_G1")
        nameSig2 = TString("CombBkgEPDF_down") #TString("DblGPDFdown_G2")
        
    elif sam == "up":
        nameSig1 =  TString("CombBkgEPDF_up") #TString("DblGPDFup_G1")
        nameSig2 =  TString("CombBkgEPDF_up") #TString("DblGPDFup_G2")
        
    else:
        print "[ERROR] Wrong sample"
        exit(0)
                


    model.plotOn( frame,
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kBlue+2),
                  RooFit.LineWidth(4),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    
    model.plotOn( frame,
                  RooFit.Components(nameComb1.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kOrange),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameSig1.Data()),
                  RooFit.LineColor(kRed),
                  RooFit.LineStyle(kDashed),
                  RooFit.LineWidth(4),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    
    
    ''' 
    model.plotOn( frame,
                  RooFit.Components(nameSig2.Data()),
                  RooFit.LineColor(kMagenta-10),
                  RooFit.LineStyle(kDashed),
                  RooFit.LineWidth(4),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kBlue-6),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    '''  
#    model.paramOn( frame,
#                   RooFit.Layout( 0.56, 0.90, 0.85 ),
#                   RooFit.Format( 'NEU', RooFit.AutoPrecision( 2 ) )
#                   )

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

    from ROOT import *
    #from ROOT import TFile, TCanvas, gROOT, TLegend, TString, TLine, TH1F, TBox, TPad
    #from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack, kGray, kViolet
    #from ROOT import RooFit, RooRealVar, RooAbsReal, RooCategory, RooArgSet, RooAddPdf, RooArgList
    gROOT.SetStyle( 'Plain' )    
    #gROOT.SetBatch( False )
    
    
    f = TFile( FILENAME )

    w = f.Get( options.wsname )
    if not w :
        parser.error( 'Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      ( options.wsname, FILENAME ) )
    
    f.Close()
    mVarTS = TString(options.var)    
    mass = w.var(mVarTS.Data())
    sam = TString(options.sample)
    mode = TString(options.mode)
    merge = options.merge
    sufixTS = TString(options.sufix)
    if sufixTS != "":
        sufixTS = TString("_")+sufixTS
                
    range_dw = mass.getMin()
    range_up = mass.getMax()
        
    #Bmass_down = 5500
    #Bmass_up = 6000
    #Dmass_down = 1830 
    #Dmass_up = 1920         

    if sam == "up":
        print "Sample up"
        w.factory("SUM:FullPdf(nCombBkgEvts_up*CombBkgEPDF_up)")
        pullname2TS = TString("h_combData_Cut[sample==sample::up]")
        pullname3TS = TString("CombBkgEPDF_up")
    elif sam == "down":
        print "Sample down"
        w.factory("SUM:FullPdf(nCombBkgEvts_down*CombBkgEPDF_down)")
        pullname2TS = TString("h_combData_Cut[sample==sample::down]")
        pullname3TS = TString("CombBkgPDF_down")
    elif sam == "both":
        print merge
        if merge == True:
            print "Sample both with merge"
            w.factory("SUM:FullPdf(nCombBkg_both*CombBkgEPDF_both, nSignal_both*SignalEPDF_both)")
            pullname2TS = TString("h_combData_Cut[sample==sample::both]")
            pullname3TS = TString("CombBkgEPDF_both")
        else:
            print "Sample both"
            w.factory("SUM:FullPdf(nCombBkgEvts_down*CombBkgEPDF_down,nCombBkgEvts_up*CombBkgEPDF_up)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up || sample==sample::down]")
            pullname3TS = TString("CombBkgEPDF_down,CombBkgEPDF_up")
    else:
        print "[ERROR] Wrong sample"
        exit(0)

    dataName = TString("combData")    
    totName = TString("FullPdf")
    modelPDF = w.pdf( totName.Data() )
    dataset = w.data( dataName.Data() )
            
    if not ( modelPDF and dataset ) :
        print "Cos sie zepsulo?"
        w.Print( 'v' )
        exit( 0 )
    
    
    if mVarTS != "lab1_PIDK":
        unit = "[MeV/c^{2}]"
    else:
        unit = ""

    lhcbtext = TLatex()
    lhcbtext.SetTextFont(132)
    lhcbtext.SetTextColor(1)
    lhcbtext.SetTextSize(0.07)
    lhcbtext.SetTextAlign(12)
                    
    frame_m = mass.frame()
    frame_m.SetTitle('') 
    
    frame_m.GetXaxis().SetLabelSize( 0.05 )
    frame_m.GetYaxis().SetLabelSize( 0.05 )
    frame_m.GetXaxis().SetLabelFont( 132 )
    frame_m.GetYaxis().SetLabelFont( 132 )
    frame_m.GetXaxis().SetLabelOffset( 0.005 )
    frame_m.GetYaxis().SetLabelOffset( 0.005 )
    frame_m.GetXaxis().SetLabelColor( kWhite)
    
    frame_m.GetXaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetNdivisions(512)
    
    frame_m.GetXaxis().SetTitleOffset( 1.00 )
    frame_m.GetYaxis().SetTitleOffset( 1.0 )
    frame_m.GetYaxis().SetTitle((TString.Format("#font[12]{Candidates / ( " +
                                                str(int(mass.getBinWidth(1)))+" "+
                                                unit+")}") ).Data())
                                                    
    #frame_m.GetXaxis().SetTitle("m(#Lambda_{b}) [MeV/c^{2}]")
           
               
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS, merge )
    if plotData : plotDataSet( dataset, frame_m, sam, merge )

    frame_m.GetYaxis().SetRangeUser(0.01,frame_m.GetMaximum()*1.1)
           
    legend = TLegend( 0.55, 0.70, 0.85, 0.85 ) 
    legend.SetTextSize(0.05)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
          
    l1 = TLine()
    l1.SetLineColor(kRed)
    l1.SetLineWidth(4)
    l1.SetLineStyle(kDashed)
    legend.AddEntry(l1, "Signal", "L")

    h1=TH1F("Combinatorial","Combinatorial",5,0,1)
    h1.SetFillColor(kOrange)
    h1.SetFillStyle(1001)
    legend.AddEntry(h1, "Combinatorial", "f")
    
    
    canvas = TCanvas("canvas", "canvas", 600, 700)
    canvas.cd()
    pad1 = TPad("upperPad", "upperPad", .050, .22, 1.0, 1.0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetTickx(0);
    pad1.Draw()
    pad1.cd()

    frame_m.Draw()
    legend.Draw("same")
    if mVarTS == "lab2_MM":
        lhcbtext.DrawTextNDC(0.13,0.85,"LHCb")
    else:
        lhcbtext.DrawTextNDC(0.68,0.65,"LHCb")
                                       
    pad1.Update()

    frame_m.Print("v")

    canvas.cd()
    pad2 = TPad("lowerPad", "lowerPad", .050, .005, 1.0, .3275)
    pad2.SetBorderMode(0)
    pad2.SetBorderSize(-1)
    pad2.SetFillStyle(0)
    pad2.SetBottomMargin(0.35)
    pad2.SetTickx(0);
    pad2.Draw()
    pad2.SetLogy(0)
    pad2.cd()
                                        

    frame_p = mass.frame(RooFit.Title("pull_frame"))
    frame_p.Print("v")
    frame_p.SetTitle("")
    frame_p.GetYaxis().SetTitle("")
    frame_p.GetYaxis().SetTitleSize(0.09)
    frame_p.GetYaxis().SetTitleOffset(0.26)
    frame_p.GetYaxis().SetTitleFont(62)
    frame_p.GetYaxis().SetLabelSize(0.12)
    frame_p.GetYaxis().SetLabelOffset(0.006)
    frame_p.GetXaxis().SetTitleSize(0.15)
    frame_p.GetXaxis().SetTitleFont(132)
    frame_p.GetXaxis().SetTitleOffset(0.85)
    frame_p.GetXaxis().SetNdivisions(5)
    frame_p.GetYaxis().SetNdivisions(5)
    frame_p.GetXaxis().SetLabelSize(0.12)
    frame_p.GetXaxis().SetLabelFont( 132 )
    frame_p.GetYaxis().SetLabelFont( 132 )
    frame_p.GetXaxis().SetTitle("m(#Lambda_{b}) [MeV/c^{2}]")
    
       
    gStyle.SetOptLogy(0)
                                            
    
    pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[FullPdf]")
#TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[")+pullname3TS+TString("]")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    pullHist.SetTitle("")

    frame_p.addPlotable(pullHist,"P")
    frame_p.Draw()
        
      
        
    if ( mVarTS == "lab0_MassFitConsD_M" ):
        gStyle.SetOptLogy(0)
            
    axisX = pullHist.GetXaxis()
    axisX.Set(100,range_dw,range_up)
        
    axisY = pullHist.GetYaxis()
    max = axisY.GetXmax()
    min = axisY.GetXmin()
                
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
                                                                 
       
    frame_p.Draw()
    
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
            
    pad2.Update()
    canvas.Update()
                                                                                
    n = TString("TotEPDF_m_")+sam+TString("_paramBox")    
    pt = canvas.FindObject( n.Data() )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update()
    t = TString("_")

    canName = TString("mass_LbLcPi")+sufixTS+TString(".pdf")
    canNameROOT = TString("mass_LbLcPi")+sufixTS+TString(".root")
    canNamePng = TString("mass_LbLcPi")+sufixTS+TString(".png")
    canvas.Print(canName.Data())
    canvas.Print(canNameROOT.Data())
    canvas.Print(canNamePng.Data())
                         
#------------------------------------------------------------------------------
