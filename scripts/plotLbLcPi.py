#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot the Bd -> D pi mass models                          #
#                                                                             #
#   Example usage:                                                            #
#      python -i plotBs2DsKMassModels.py                                      #
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
bName = 'B_{d}'

Dmass_dw = 2200
Dmass_up = 2380

Bmass_dw = 5400
Bmass_up = 5800
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
                                      default = 'lab0_MassFitConsD_M',
                                      help = 'set observable '
                                      )
#------------------------------------------------------------------------------
def plotDataSet( dataset, frame, sample ) :

    if sample == "both":
        dataset.plotOn( frame,
                        RooFit.Cut("sample==sample::up || sample==sample::down"),
                        RooFit.Binning( 70 ) )
    elif sample == "up":
        dataset.plotOn( frame,
                        RooFit.Cut("sample==sample::up"),
                        RooFit.Binning( 70 ) )
                                                
    elif sample == "down":
         dataset.plotOn( frame,
                         RooFit.Cut("sample==sample::down"),
                         RooFit.Binning( 70 ) )
    else:
        print "[ERROR] Wrong sample!"
                                                                         
                
   # dataset.statOn( frame,
   #                 RooFit.Layout( 0.10, 0.45, 0.90  ),
   #                 RooFit.What('N') )

#------------------------------------------------------------------------------
def plotFitModel( model, frame, sam, var) :
    #if debug :
    
    print "model"    
    model.Print( 't' )

    print "frame"
    frame.Print( 'v' )
    t=TString("_")
    p=TString(",")
    nameTot = TString("FullPdf")
    if sam == "both":
        nameSig  = TString("SigEPDF_down,SigEPDF_up") 
        nameBkg = TString("BkgEPDF_down,BkgEPDF_up")
                        
    elif sam == "down" :
        nameSig  = TString("SigEPDF_down")
        nameBkg = TString("BkgEPDF_down")
         
    elif sam == "up":
        nameSig  = TString("SigEPDF_up")
        nameBkg = TString("BkgEPDF_up")
                                        
    else:
        print "[ERROR] Wrong sample"
        exit(0)

       
    model.plotOn( frame,
                  RooFit.Components(nameBkg.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kRed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    
    model.plotOn( frame,
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kMagenta-2),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    model.plotOn( frame,
                  RooFit.Components(nameSig.Data()),
                  RooFit.LineColor(kBlue),
                  RooFit.LineStyle(7),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
          
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

    #from ROOT import *
    #from ROOT import RooCruijff, TCanvas, TPad
    
    #from ROOT import TFile, TCanvas, gROOT, TLegend, TString, TLine, TH1F, TBox, TPad
    #from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack, kGray, kViolet
    #from ROOT import RooFit, RooRealVar, RooAbsReal, RooCategory, RooArgSet, RooAddPdf, RooArgList
    gROOT.SetStyle( 'Plain' )    
   
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
    
    pdf = RooCruijff()
    f = TFile( FILENAME )
    
    w = f.Get( options.wsname )
    if not w :
        parser.error( 'Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      ( options.wsname, FILENAME ) )
    
    f.Close()
    mVarTS = TString(options.var)    
    mass = w.var(mVarTS.Data())
    sam = TString(options.sample)
     
    w.Print('v')
    #exit(0)
        
       
    dataName = TString("combData")


    if sam == "up":
        print "Sample up"
        w.factory("SUM:FullPdf(nSig_up_Evts*SigEPDF_up,nBkg_up_Evts*BkgEPDF_up)")
        pullname2TS = TString("h_combData_Cut[sample==sample::up]")
    elif sam == "down":
        print "Sample down"
        w.factory("SUM:FullPdf(nSig_down_Evts*SigEPDF_down,nBkg_down_Evts*BkgEPDF_down)")
        pullname2TS = TString("h_combData_Cut[sample==sample::down]")
    elif sam == "both":
        print "Sample both"
        w.factory("SUM:FullPdf(nSig_down_Evts*SigEPDF_down,nSig_up_Evts*SigEPDF_up,nBkg_down_Evts*BkgEPDF_down,nBkg_up_Evts*BkgEPDF_up)")
        pullname2TS = TString("h_combData_Cut[sample==sample::up || sample==sample::down]")
    else:
        print "[ERROR] Wrong sample"
        exit(0)

    totName = TString("FullPdf")
    modelPDF = w.pdf( totName.Data() )
    dataset = w.data( dataName.Data() )
            
    if not ( modelPDF and dataset ) :
        print "Cos sie zepsulo?"
        w.Print( 'v' )
        exit( 0 )
    #w.Print('v')
    #exit(0)

    if mVarTS != "lab1_PIDK":
        unit = "[MeV/c^{2}]"
    else:
        unit = ""
                
          
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
                  

    if ( mVarTS == "lab0_MassFitConsD_M"):
        frame_m.GetXaxis().SetTitle("m(#Lambda_{b}) [MeV/c^{2}]")
    else:
        frame_m.GetXaxis().SetTitle("m(#Lambda_{c}) [MeV/c^{2}]")
                            
              
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS )
    if plotData : plotDataSet( dataset, frame_m, sam )

    frame_m.GetYaxis().SetRangeUser(0.01,frame_m.GetMaximum()*1.1)
        
    canvas = TCanvas("canvas", "canvas",700, 700)
    canvas.SetTitle( '' )
    canvas.cd()
    
    pad1 = TPad("upperPad", "upperPad", .050, .22, 1.0, 1.0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetTickx(0);
    pad1.Draw()
    pad1.cd()
    
    

    if ( mVarTS == "lab0_MassFitConsD_M"):
        legend = TLegend( 0.60, 0.50, 0.85, 0.85 )
    else:
        legend = TLegend( 0.12, 0.70, 0.40, 0.88 )
    legend.SetTextSize(0.05)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)

    l1 = TLine()
    l1.SetLineColor(kBlue)
    l1.SetLineWidth(4)
    l1.SetLineStyle(7)
    legend.AddEntry(l1, "#Lambda_{c} #rightarrow K#pi p", "L")


    h1=TH1F("Combinatorial","Combinatorial",5,0,1)
    h1.SetFillColor(kRed)
    h1.SetFillStyle(1001)
    legend.AddEntry(h1, "Combinatorial", "f")
    
    lhcbtext = TLatex()
    lhcbtext.SetTextFont(132)
    lhcbtext.SetTextColor(1)
    lhcbtext.SetTextSize(0.07)
    lhcbtext.SetTextAlign(12)
       
    pad1.cd()
    frame_m.Draw()
    legend.Draw("same")
    if mVarTS == "lab2_MM":
        lhcbtext.DrawTextNDC(0.72,0.85,"LHCb")
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
    
    if ( mVarTS == "lab0_MassFitConsD_M"):
        frame_p.GetXaxis().SetTitle("m(#Lambda_{b}) [MeV/c^{2}]")
    else:
        frame_p.GetXaxis().SetTitle("m(#Lambda_{c}) [MeV/c^{2}]")

    gStyle.SetOptLogy(0)    

    pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[FullPdf]")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    pullHist.SetTitle("")

    frame_p.addPlotable(pullHist,"P")
    frame_p.Draw()
        

    
    #pullHist.SetMaximum(5800.00)
    #pullHist.SetMinimum(5100.00)
    axisX = pullHist.GetXaxis()
    if ( mVarTS == "lab0_MassFitConsD_M"):
        axisX.Set(70,Bmass_dw,Bmass_up)
    else:
        axisX.Set(70,Dmass_dw,Dmass_up)
    axisY = pullHist.GetYaxis()
    max = axisY.GetXmax()
    min = axisY.GetXmin()
    range = max-min
    zero = max/range
    print "max: %s, min: %s, range: %s, zero:%s"%(max,min,range,zero)
    #line = TLine(0.11,0.31,0.99,0.20)
    graph = TGraph(2)
    graph.SetMaximum(max)
    graph.SetMinimum(min)
    if ( mVarTS == "lab0_MassFitConsD_M"):
        graph.SetPoint(1,Bmass_dw,0)
        graph.SetPoint(2,Bmass_up,0)
    else:
        graph.SetPoint(1,Dmass_dw,0)
        graph.SetPoint(2,Dmass_up,0)
    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    if ( mVarTS == "lab0_MassFitConsD_M"):
        graph2.SetPoint(1,Bmass_dw,-3)
        graph2.SetPoint(2,Bmass_up,-3)
    else:
        graph2.SetPoint(1,Dmass_dw,-3)
        graph2.SetPoint(2,Dmass_up,-3)
    graph2.SetLineColor(kRed)
    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    if ( mVarTS == "lab0_MassFitConsD_M"):
        graph3.SetPoint(1,Bmass_dw,3)
        graph3.SetPoint(2,Bmass_up,3)
    else:
        graph3.SetPoint(1,Dmass_dw,3)
        graph3.SetPoint(2,Dmass_up,3)
    graph3.SetLineColor(kRed)
                                            
    
    frame_p.Draw()
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
    pad2.Update()
    canvas.Update()
                                                                                

      
#    frame_m.Draw()
    n = TString("TotEPDF_m_")+sam+TString("_paramBox")    
    pt = canvas.FindObject( n.Data() )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update()
    canName = TString("mass_LbLcPi_")+mVarTS+TString("_")+sam+TString(".pdf")
    canvas.SaveAs(canName.Data())
    canNamePng = TString("mass_LbLcPi_")+mVarTS+TString("_")+sam+TString(".png")
    canvas.SaveAs(canNamePng.Data())
    canNameROOT = TString("mass_LbLcPi_")+mVarTS+TString("_")+sam+TString(".root")
    canvas.SaveAs(canNameROOT.Data())
        
    
        
#------------------------------------------------------------------------------
