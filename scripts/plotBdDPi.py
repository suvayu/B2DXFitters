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
bName = 'B_{d}'


bin = 200
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

    if sample == "both":
        if merge:
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
                                                                         
                
   # dataset.statOn( frame,
   #                 RooFit.Layout( 0.10, 0.45, 0.90  ),
   #                 RooFit.What('N') )

#------------------------------------------------------------------------------
def plotFitModel( model, frame, sam, var, merge) :
    #if debug :
    
    print "model"    
    model.Print( 't' )

    print "frame"
    frame.Print( 'v' )
    t=TString("_")
    p=TString(",")
    nameTot = TString("FullPdf")
    if sam == "both":
        if merge:
            nameSig = TString("SigEPDF_both")
            nameBkg = TString("BkgEPDF_both")
            nameBDK = nameBkg + TString(",BkgBDKEPDF_both")
            nameBsDsPi = nameBDK + TString(",BkgBsDsPiEPDF_both")
            nameLbLcPi = nameBsDsPi + TString(",BkgLbLcPiEPDF_both")
            nameBkgX = nameLbLcPi + TString(",BkgBkgXEPDF_both")
            nameDRho = nameLbLcPi+TString(",BkgBdDRhoEPDF_both")
            nameDstPi = nameDRho + TString(",BkgBdDstPiEPDF_both")
                                                                                                        
        else:
            nameSig1 = TString("DblCBPDFdown_CB1,DblCBPDFup_CB1")
            nameSig2 = TString("DblCBPDFdown_CB2,DblCBPDFup_CB2")
            nameSig  = TString("SigEPDF_down,SigEPDF_up") 
            nameBkg = TString("BkgEPDF_down,BkgEPDF_up")
            nameBDK = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBDKEPDF_up,BkgEPDF_up")
            nameBsDsPi = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_down,BkgBsDsPiEPDF_up")
            nameLbLcPi = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_down,BkgBsDsPiEPDF_up,BkgLbLcPiEPDF_down,BkgLbLcPiEPDF_up")
            nameBkgX = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_down,BkgBsDsPiEPDF_up,BkgLbLcPiEPDF_down,BkgLbLcPiEPDF_up,BkgBkgXEPDF_down,BkgBkgXEPDF_up")
            nameDRho = nameLbLcPi+TString(",BkgBdDRhoEPDF_down,BkgBdDRhoEPDF_up")
            nameDstPi = nameDRho + TString(",BkgBdDstPiEPDF_down,BkgBdDstPiEPDF_up")

    elif sam == "down" :
        #nameSig1 = TString("DblCBPDFdown_CB1")
        #nameSig2 = TString("DblCBPDFdown_CB2")
        nameSig1 = TString("DblGPDFdown_G1")
        nameSig2 = TString("DblGPDFdown_G2")
                
        nameSig  = TString("SigEPDF_down")
        nameBkg = TString("BkgEPDF_down")
        nameBDK = TString("BkgBDKEPDF_down,BkgEPDF_down")
        nameBsDsPi = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBsDsPiEPDF_down")
        nameLbLcPi = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBsDsPiEPDF_down,BkgLbLcPiEPDF_down")
        nameBkgX = TString("BkgBDKEPDF_down,BkgEPDF_down,BkgBsDsPiEPDF_down,BkgLbLcPiEPDF_down,BkgBkgXEPDF_down")
        
    elif sam == "up":
        #nameSig1 = TString("DblCBPDFup_CB1")
        #nameSig2 = TString("DblCBPDFup_CB2")
        #nameSig  = TString("SigEPDF_up")
        #nameBkg = TString("BkgEPDF_up")
        nameSig1 = TString("DblGPDFup_G1")
        nameSig2 = TString("DblGPDFup_G2")

        nameSig  = TString("SigEPDF_up")
        nameBkg = TString("BkgEPDF_up")
        nameBDK = TString("BkgBDKEPDF_up,BkgEPDF_up")
        nameBsDsPi = TString("BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_up")
        nameLbLcPi = TString("BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_up,BkgLbLcPiEPDF_up")
        nameBkgX =  TString("BkgBDKEPDF_up,BkgEPDF_up,BkgBsDsPiEPDF_up,BkgLbLcPiEPDF_up,BkgBkgXEPDF_up")
        
                                
    else:
        print "[ERROR] Wrong sample"
        exit(0)

    model.plotOn( frame,
                  RooFit.Components(nameDstPi.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-3),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameDRho.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kYellow-7),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
     
    model.plotOn( frame,
                  RooFit.Components(nameLbLcPi.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kRed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    

    model.plotOn( frame,
                  RooFit.Components(nameBsDsPi.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-10),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameBDK.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kOrange),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameBkg.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-6),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    
    model.plotOn( frame,
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kMagenta-2),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    model.plotOn( frame,
                  RooFit.Components(nameSig.Data()),
                  RooFit.LineColor(kRed-4),
                  RooFit.LineStyle(7),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    
    #model.plotOn( frame,
    #              RooFit.Components(nameSig.Data()),
    #              RooFit.LineColor(kMagenta-2),
    #              RooFit.LineStyle(kDashed),
    #              RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
    #              )
'''     
    model.plotOn( frame,
                  RooFit.Components(nameSig2.Data()),
                  RooFit.LineColor(kBlue-10),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components(nameSig1.Data()),
                  RooFit.LineColor(kBlue-10),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    model.plotOn( frame,
                  RooFit.Components(nameSig.Data()),
                  RooFit.LineColor(kBlue),
                  RooFit.LineStyle(7),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
'''                        
    #model.plotOn( frame,
    #              RooFit.Components(nameBkg.Data()),
    #              RooFit.LineColor(kRed),
    #              RooFit.LineStyle(7),
    #              RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
    #              )

    #model.plotOn( frame,
    #              RooFit.Components(nameBDK.Data()),
    #              RooFit.LineColor(kOrange),
    #              RooFit.LineStyle(7),
    #              RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
    #              )
    
       
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
   # gROOT.SetBatch( False )

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
    #mass.setRange(Bmass_dw,Bmass_up)
    sam = TString(options.sample)
    sufixTS = TString(options.sufix)
    merge = options.merge
    if merge and sam != "both":
        print "You cannot run option megrge with sample up or down"
        exit(0)
    if sufixTS != "":
        sufixTS = TString("_")+sufixTS
                
    range_dw = mass.getMin()
    range_up = mass.getMax()
        
    
    w.Print('v')
    #exit(0)
        
       
    dataName = TString("combData")


    if sam == "up":
        print "Sample up"
        w.factory("SUM:FullPdf(nSig_up_Evts*SigEPDF_up,nBkg_up_Evts*BkgEPDF_up,nBd2DK_up_Evts*BkgBDKEPDF_up)")
        pullname2TS = TString("h_combData_Cut[sample==sample::up]")
    elif sam == "down":
        print "Sample down"
        w.factory("SUM:FullPdf(nSig_down_Evts*SigEPDF_down,nBkg_down_Evts*BkgEPDF_down,nBd2DK_down_Evts*BkgBDKEPDF_down)")
        pullname2TS = TString("h_combData_Cut[sample==sample::down]")
    elif sam == "both":
        if merge:
            print "Sample both with merge"
            w.factory("SUM:FullPdf(nSig_both_Evts*SigEPDF_both,nBkg_both_Evts*BkgEPDF_both,nBd2DK_both_Evts*BkgBDKEPDF_both,nBs2DsPi_both_Evts*BkgBsDsPiEPDF_both, nLb2LcPi_both_Evts*BkgLbLcPiEPDF_both, nBd2DRho_both_Evts*BkgBdDRhoEPDF_both,nBd2DstPi_both_Evts*BkgBdDstPiEPDF_both)")
            pullname2TS = TString("h_combData_Cut[sample==sample::both]")
                        
        else:
            print "Sample both"
            w.factory("SUM:FullPdf(nSig_down_Evts*SigEPDF_down,nSig_up_Evts*SigEPDF_up,nBkg_down_Evts*BkgEPDF_down,nBkg_up_Evts*BkgEPDF_up,nBd2DK_down_Evts*BkgBDKEPDF_down,nBd2DK_up_Evts*BkgBDKEPDF_up, nBs2DsPi_down_Evts*BkgBsDsPiEPDF_down, nBs2DsPi_up_Evts*BkgBsDsPiEPDF_up, nLb2LcPi_down_Evts*BkgLbLcPiEPDF_down, nLb2LcPi_up_Evts*BkgLbLcPiEPDF_up,nBd2DRho_up_Evts*BkgBdDRhoEPDF_up,nBd2DRho_down_Evts*BkgBdDRhoEPDF_down,nBd2DstPi_up_Evts*BkgBdDstPiEPDF_up, nBd2DstPi_down_Evts*BkgBdDstPiEPDF_down)") #, nBkgX_down_Evts*BkgBkgXEPDF_down, nBkgX_up_Evts*BkgBkgXEPDF_up)")
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
       
    frame_m.SetTitle("") #'Fit in reconstructed %s mass' % bName )
    
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
                                                str((mass.getBinWidth(1)))+" "+
                                                unit+")}") ).Data())
    
                                                
    if ( mVarTS == "lab0_MassFitConsD_M"):
        frame_m.GetXaxis().SetTitle("m(B_{d}) [MeV/c^{2}]")
    else:
        frame_m.GetXaxis().SetTitle("m(D) [MeV/c^{2}]")
                     
           
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS, merge )
    if plotData : plotDataSet( dataset, frame_m, sam, merge )

    if ( mVarTS == "lab0_MassFitConsD_M"):
        gStyle.SetOptLogy(1)

        
    canvas = TCanvas("canvas", "canvas",1200, 1000)
    canvas.SetTitle( 'Fit in mass' )
    canvas.cd()

    pad1 = TPad("upperPad", "upperPad", .050, .22, 1.0, 1.0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetTickx(0);
    pad1.Draw()
    pad1.cd()
    
    if ( mVarTS == "lab0_MassFitConsD_M"):
        legend = TLegend( 0.60, 0.45, 0.85, 0.85 )
    else:
        legend = TLegend( 0.12, 0.45, 0.35, 0.85 )
    legend.SetTextSize(0.05)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
                        
    lhcbtext = TLatex()
    lhcbtext.SetTextFont(132)
    lhcbtext.SetTextColor(1)
    lhcbtext.SetTextSize(0.07)
    lhcbtext.SetTextAlign(12)
    

    l1 = TLine()
    l1.SetLineColor(kRed-4)
    l1.SetLineWidth(4)
    l1.SetLineStyle(7)
    legend.AddEntry(l1, "Signal B^{0} #rightarrow D^{-}#pi^{+}", "L")

    h1=TH1F("Combinatorial","Combinatorial",5,0,1)
    h1.SetFillColor(kBlue-6)
    h1.SetFillStyle(1001)
    legend.AddEntry(h1, "Combinatorial", "f")
    
    h2=TH1F("B2DK","B2DK",5,0,1)
    h2.SetFillColor(kOrange)
    h2.SetFillStyle(1001)
    legend.AddEntry(h2, "B_{d}#rightarrow DK", "f")

    h3=TH1F("Bs2DsPi","Bs2DsPi",5,0,1)
    h3.SetFillColor(kBlue-10)
    h3.SetFillStyle(1001)
    legend.AddEntry(h3, "B_{s}#rightarrow D_{s}#pi", "f")

    h4=TH1F("Lb2LcPi","Lb2LcPi",5,0,1)
    h4.SetFillColor(kRed)
    h4.SetFillStyle(1001)
    legend.AddEntry(h4, "#Lambda_{b}#rightarrow #Lambda_{c}#pi", "f")

    h5=TH1F("BkgX","BkgX",5,0,1)
    h5.SetFillColor(kYellow-7)
    h5.SetFillStyle(1001)
#    legend.AddEntry(h5, "BkgX", "f")

    h6=TH1F("Bd2DRho","B2DRho",5,0,1)
    h6.SetFillColor(kYellow-7)
    h6.SetFillStyle(1001)
    legend.AddEntry(h6, "B_{d}#rightarrow D#rho", "f")

    h7=TH1F("Bd2DstPi","B2DstPi",5,0,1)
    h7.SetFillColor(kBlue-3)
    h7.SetFillStyle(1001)
    legend.AddEntry(h7, "B_{d}#rightarrow D^{*}#pi", "f")
                
    
    pad1.cd()
    frame_m.Draw()
    legend.Draw("same")
    if mVarTS == "lab2_MM":
        lhcbtext.DrawTextNDC(0.75,0.82,"LHCb")
    else:
        lhcbtext.DrawTextNDC(0.48,0.85,"LHCb")
        
    pad1.Update()
    
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
                                       
    gStyle.SetOptLogy(0)
       
    frame_m.Print("v")

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
        frame_p.GetXaxis().SetTitle("m(B_{d}) [MeV/c^{2}]")
    else:
        frame_p.GetXaxis().SetTitle("m(D) [MeV/c^{2}]")
        
    pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[FullPdf]")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    pullHist.SetTitle("")

    frame_p.addPlotable(pullHist,"P")
    frame_p.Draw()
       
    axisX = pullHist.GetXaxis()
    axisX.Set(bin,range_dw,range_up)
    
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
                                                                                

      
#    frame_m.Draw()
    n = TString("TotEPDF_m_")+sam+TString("_paramBox")    
    pt = canvas.FindObject( n.Data() )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update()
    canName = TString("mass_BDPi_")+mVarTS+TString("_")+sam+sufixTS+TString(".pdf")
    canvas.SaveAs(canName.Data())
    canNamePng = TString("mass_BDPi_")+mVarTS+TString("_")+sam+sufixTS+TString(".png")
    canvas.SaveAs(canNamePng.Data())
    canNameROOT = TString("mass_BDPi_")+mVarTS+TString("_")+sam+sufixTS+TString(".root")
    canvas.SaveAs(canNameROOT.Data())

    templates = true
    if templates == true:
        canvasBkg = TCanvas("canvasBkg", "canvas",1200, 1000)
        canvasBkg.SetTitle('')
        canvasBkg.cd()
        
        nameBkg = [TString("bkgProdBDKPDF_both"), TString("bkgProdBsDsPiPDF_both"), TString("bkgProdLbLcPiPDF_both"),
                TString("bkgProdBdRhoPDF_both"), TString("bkgProdBdDstPiPDF_both")]

        nameLtx = ["B_{d}#rightarrow DK", "B_{s}#rightarrow D_{s}#pi", "#Lambda_{b}#rightarrow #Lambda_{c}#pi",
                   "B_{d}#rightarrow D#rho", "B_{d}#rightarrow D^{*}#pi"]
        
        color = [kOrange, kBlue-10, kRed, kGreen+3, kBlue+3 ]
        style = [1,1,1,1,1,2,3,6,9]
        
        frame_b = mass.frame()
        
        frame_b.SetTitle("") #'Fit in reconstructed %s mass' % bName )
        
        frame_b.GetXaxis().SetLabelSize( 0.05 )
        frame_b.GetYaxis().SetLabelSize( 0.05 )
        frame_b.GetXaxis().SetLabelFont( 132 )
        frame_b.GetYaxis().SetLabelFont( 132 )
        frame_b.GetXaxis().SetLabelOffset( 0.005 )
        frame_b.GetYaxis().SetLabelOffset( 0.005 )
                
        frame_b.GetXaxis().SetTitleSize( 0.05 )
        frame_b.GetYaxis().SetTitleSize( 0.05 )
        frame_b.GetXaxis().SetTitleFont( 132 )
        frame_b.GetYaxis().SetTitleFont( 132 )
                
        frame_b.GetXaxis().SetNdivisions(5)
        frame_b.GetYaxis().SetNdivisions(5)
               
        frame_b.GetXaxis().SetTitleOffset( 1.00 )
        frame_b.GetYaxis().SetTitleOffset( 1.0 )

        if ( mVarTS == "lab0_MassFitConsD_M"):
            frame_b.GetXaxis().SetTitle("m(B_{d}) [MeV/c^{2}]")
        else:
            frame_b.GetXaxis().SetTitle("m(D) [MeV/c^{2}]")
        frame_b.GetYaxis().SetTitle("")                        

        if ( mVarTS == "lab0_MassFitConsD_M"):
            legend_bkg = TLegend( 0.60, 0.45, 0.85, 0.80 )
        else:
            legend_bkg = TLegend( 0.12, 0.12, 0.35, 0.30 )

        legend_bkg.SetTextSize(0.05)
        legend_bkg.SetTextFont(12)
        legend_bkg.SetFillColor(4000)
        legend_bkg.SetShadowColor(0)
        legend_bkg.SetBorderSize(0)
        legend_bkg.SetTextFont(132)
        
        lhcbtext_bkg = TLatex()
        lhcbtext_bkg.SetTextFont(132)
        lhcbtext_bkg.SetTextColor(1)
        lhcbtext_bkg.SetTextSize(0.07)
        lhcbtext_bkg.SetTextAlign(12)
                                                                            
        line = []
        pdfBkg = []
        r = [0,1,2,3,4]
        for i in r:
            line.append(TLine())
            line[i].SetLineColor(color[i])
            line[i].SetLineWidth(5)
            line[i].SetLineStyle(style[i])
            print nameBkg[i]
            pdfBkg.append(w.pdf( nameBkg[i].Data() ))
            if pdfBkg[i] == NULL:
                print "Cannot read"
                                            
        for i in r:
            print i
            print pdfBkg[i].GetName()
            if  mVarTS == "lab2_MM" and ( i==1 or i == 2):
                print i
                pdfBkg[i].plotOn(frame_b, RooFit.LineColor(color[i]), RooFit.LineStyle(style[i]),  RooFit.LineWidth(5) )
                legend_bkg.AddEntry(line[i], nameLtx[i] , "L")
            elif mVarTS == "lab0_MassFitConsD_M":
                pdfBkg[i].plotOn(frame_b, RooFit.LineColor(color[i]), RooFit.LineStyle(style[i]),  RooFit.LineWidth(5) )
                legend_bkg.AddEntry(line[i], nameLtx[i] , "L")
                                
        frame_b.GetYaxis().SetTitle('')    
        frame_b.Draw()
        legend_bkg.Draw("same")
        if ( mVarTS == "lab2_MM"):
            lhcbtext_bkg.DrawTextNDC( 0.12 , 0.35, "LHCb")
        else:
            lhcbtext_bkg.DrawTextNDC( 0.60 , 0.85, "LHCb")
        nameSavePdf = TString("templateBkg_BDPi_")+mVarTS+TString("_")+sam+sufixTS+TString(".pdf")
        nameSaveRoot = TString("templateBkg_BDPi_")+mVarTS+TString("_")+sam+sufixTS+TString(".root")
        canvasBkg.Print(nameSavePdf.Data())
        canvasBkg.Print(nameSaveRoot.Data())
                                                                                                                                                                
                
            
        
#------------------------------------------------------------------------------
