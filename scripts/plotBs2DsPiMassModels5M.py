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
bName = 'B_{s}'

bin = 100
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
                   default = 'down',
                   help = 'Sample: choose up or down '
                   )
parser.add_option( '-o', '--mode',
                   dest = 'mode',
                   metavar = 'MODE',
                   default = 'kkpi',
                   help = 'Mode: choose all, kkpi, kpipi or pipipi'
                   )

parser.add_option( '-t', '--toy',
                   dest = 'toy',
                   metavar = 'TOY',
                   action = 'store_true', 
                   default = False,
                   help = 'if ToyMC choose yes.'
                   )

parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '
                   )

parser.add_option( '-s', '--sufix',
                   dest = 'sufix',
                   metavar = 'SUFIX',
                   default = '',
                   help = 'Add sufix to output'
                   )
parser.add_option( '--merge',
                   dest = 'merge',
                   action = 'store_true',
                   default = False,
                   help = 'merge magnet polarity'
                   )
parser.add_option( '--bin',
                   dest = 'bin',
                   action = 'store_true',
                   default = 100,
                   help = 'set number of bins'
                   )
parser.add_option( '--dim',
                   dest = 'dim',
                   default = 3)
parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

#------------------------------------------------------------------------------

def getTotPDF(w, sam, mod, merge, comp, debug):
    c = []
    n = []

    print "Sample %s, %s "%(sam,mod)
    if merge:
        sp = ["both"]
    else:
        sp = GeneralUtils.GetSample(sam, debug)

    md = GeneralUtils.GetMode(mod,debug)

    for s in sp:
        for m in md:
            for p in comp:
                if p == "Sig":
                    c.append("n%s_%s_%s_Evts*%sEPDF_%s_%s"%(p,s,m,p,s,m))
                else:
                    c.append("n%s_%s_%s_Evts*%sEPDF_m_%s_%s"%(p,s,m,p,s,m))
                n.append("n%s_%s_%s_Evts"%(p,s,m))
    
    if sam == "up" or sam == "down" or (sam == "both" and merge == True):
        pdfcomp = c[0]
        for i in range(1,c.__len__()):
            pdfcomp = pdfcomp +"," +c[i]
        if debug:    
            print "Total PDF to print: %s"%(pdfcomp)
        w.factory("SUM:FullPdf(%s)"%(pdfcomp)) #                                                                                                          
    else:
        pdfcomp1 = c[0]
        numcomp1 = n[0]
        for i in range(1,c.__len__()/2):
            pdfcomp1 = pdfcomp1+","+c[i]
            numcomp1 = numcomp1+","+n[i]
        if debug:
            print "Total PDF1 to print: %s"%(pdfcomp1)
            print "Number of events to print: %s"%(numcomp1)
        w.factory("SUM:FullPdf1(%s)"%(pdfcomp1))
        w.factory("EXPR::N_1(%s)"%(numcomp1))

        pdfcomp2 = c[int(c.__len__()/2)]
        numcomp2 = n[int(n.__len__()/2)]
        for i in range(c.__len__()/2+1,c.__len__()):
            pdfcomp2 = pdfcomp2+","+c[i]
            numcomp2 = numcomp2+","+n[i]
        if debug:
            print "Total PDF2 to print: %s"%(pdfcomp2)
            print "Number of events to print: %s"%(numcomp2)
        w.factory("SUM:FullPdf2(%s)"%(pdfcomp1))
        w.factory("EXPR::N_2(%s)"%(numcomp1))
        w.factory("SUM:FullPdf(N_1*FullPdf1,N_2*FullPdf2)")

    totName = TString("FullPdf")
    modelPDF = w.pdf( totName.Data() )    
    
    return modelPDF

#------------------------------------------------------------------------------ 
def getDataCut(sam, mod, debug):
    
    print "Sample %s, %s "%(sam,mod)
    if merge:
        sp = ["both"]
    else:
        sp = GeneralUtils.GetSample(sam, debug)

    md = GeneralUtils.GetMode(mod,debug)

    c = [ ]
    for s in sp:
        for m in md:
            c.append("sample==sample::%s_%s"%(s,m))
            
    cut = c[0]
    for i in range(1,c.__len__()):
        cut = cut +" || " +c[i]
    if debug:    
        print "Total cut on data: %s"%(cut)
        
    return cut

#------------------------------------------------------------------------------
def plotDataSet( dataset, frame, Bin ) :

    dataset.plotOn( frame,
                    RooFit.Cut(datacut),
                    RooFit.Binning( Bin ) )
                        
#    dataset.statOn( frame,
#                    RooFit.Layout( 0.56, 0.90, 0.90 ),
#                    RooFit.What('N') )

#------------------------------------------------------------------------------
def plotFitModel( model, frame, var, sam, mode, comp, color) :
    #if debug :
    
    print "model"    
    model.Print( 't' )

    if merge:
        sp = ["both"]
    else:
        sp = GeneralUtils.GetSample(sam, debug)

    md = GeneralUtils.GetMode(mod,debug)
    c = []
    for s in sp:
        for m in md:
            for p in comp:
                if p == "Sig":
                    c.append("%sEPDF_%s_%s"%(p,s,m))
                else:
                    c.append("%sEPDF_m_%s_%s"%(p,s,m))
                    
    numBkg = comp.__len__()                
    numCom = c.__len__()
    numSM = int(numCom/numBkg)
    
    pdfcomp = []
    for j in range(0,numBkg):
        for i in range(0,numSM):
            if i == 0:
                pdfcomp.append(c[j+i*numBkg])
            else:    
                pdfcomp[j] = pdfcomp[j]+","+c[j+i*numBkg]

    for i in range(0,numBkg):
        if i == 0 or i == 1: continue
        pdfcomp[i] = pdfcomp[i]+","+pdfcomp[i-1]
    
    for n in pdfcomp:    
        print "PDF to plot: %s"%(n)
                
    model.plotOn( frame, 
                  RooFit.Components("FullPdf"),
                  RooFit.LineColor(kBlue),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    for i in range(1, numBkg):
        print i
        model.plotOn( frame, 
                      RooFit.Components(pdfcomp[numBkg-i]),
                      RooFit.DrawOption("F"),
                      RooFit.FillStyle(1001),
                      RooFit.FillColor(color[numBkg-i]),
                      RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                      )

    model.plotOn( frame, 
                  RooFit.Components(pdfcomp[0]),
                  RooFit.LineColor(color[0]),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
                        
#    model.paramOn( frame,
#
#RooFit.Layout( 0.56, 0.90, 0.85 ),
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
    gROOT.SetStyle( 'Plain' )    
    #gROOT.SetBatch( False )
    
    
    f = TFile( FILENAME )

    w = f.Get( options.wsname )
    if not w :
        parser.error( 'Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      ( options.wsname, FILENAME ) )    

    f.Close()
    dim = int(options.dim)
    bin = options.bin
    mVarTS = TString(options.var)    
    mass = w.var(mVarTS.Data())
    sam = TString(options.sample)
    mod = TString(options.mode)
    debug = options.debug 

    range_dw = mass.getMin()
    range_up = mass.getMax()

    if mVarTS != "lab1_PIDK":
        unit = "[MeV/c^{2}]"
    else:
        unit = ""
            
    if mVarTS == "lab1_PIDK":
        Bin = RooBinning(range_dw,range_up,'P')
        Bin.addUniform(bin, range_dw, range_up)
    else:
        Bin = RooBinning(range_dw,range_up,'P')
        Bin.addUniform(bin, range_dw, range_up)
          
    sufixTS = TString(options.sufix)
    if sufixTS != "":
        sufixTS = TString("_")+sufixTS

    merge = options.merge
    if sam != "both" and merge == True:
        print "You cannot plot with option sample up or down!"
        exit(0)
                
    ty = TString("ToyNo")
    if options.toy : ty = TString("ToyYes")  
    w.Print('v')

    if mod != "hhhpi0":
        comp = ["Sig", "CombBkg", "Bd2DPi", "Lb2LcPi", "Bs2DsDsstPiRho", "Bs2DsK"]
        color = [kRed-7, kBlue-6, kOrange, kRed, kBlue-10, kGreen+3]
        desc  = ["Signal B_{s}#rightarrow D_{s}#pi", 
                 "Combinatorial",
                 "B_{d}#rightarrow D#pi",
                 "#Lambda_{b}#rightarrow #Lambda_{c}#pi",
                 "B_{(d,s)}#rightarrow D_{s}^{(*)}#pi",
                 "B_{s}#rightarrow D_{s}K"]
    else:
        comp = ["Sig", "CombBkg", "Bd2DPi", "Lb2LcPi", "Bs2DsDsstPiRho", "Bd2DsstPi"]
        color = [kRed-7, kBlue-6, kOrange, kRed, kBlue-10, kMagenta-2]
        desc  = ["Signal B_{s}#rightarrow D_{s}#pi",
                 "Combinatorial",
                 "B_{d}#rightarrow D#pi",
                 "#Lambda_{b}#rightarrow #Lambda_{c}#pi",
                 "B_{(d,s)}#rightarrow D_{s}^{(*)}#pi",
                 "B_{d}#rightarrow D_{(s)}^{(*)}(#pi,#rho)"]

    datacut = getDataCut(sam,mod,debug)    
    pullfake = "h_combData_Cut[%s]"%(datacut)
    pullname2TS = TString(pullfake)

    dataName = TString("combData")
    totName = TString("FullPdf")
    modelPDF = getTotPDF(w, sam, mod, merge, comp, debug)
    dataset = w.data( dataName.Data() )
            
    if not ( modelPDF and dataset ) :
        print "[ERROR] Something went wrong: either PDF or dataSet NULL"
        w.Print( 'v' )
        exit( 0 )
 
    frame_m = mass.frame() 
    frame_m.SetTitle('')
        
    frame_m.GetXaxis().SetLabelSize( 0.05 )
    frame_m.GetYaxis().SetLabelSize( 0.05 )
    frame_m.GetXaxis().SetLabelFont( 132 )
    frame_m.GetYaxis().SetLabelFont( 132 )
    frame_m.GetXaxis().SetLabelOffset( 0.006 )
    frame_m.GetYaxis().SetLabelOffset( 0.006 )
    frame_m.GetXaxis().SetLabelColor( kWhite)
            
    frame_m.GetXaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetNdivisions(512)
    
    frame_m.GetXaxis().SetTitleOffset( 1.00 )
    frame_m.GetYaxis().SetTitleOffset( 1.10 )
    frame_m.GetYaxis().SetTitle((TString.Format("#font[12]{Candidates / ( " +                             
                                                    str(int(mass.getBinWidth(1)))+" "+
                                                    unit+")}") ).Data())
    

    if plotData : plotDataSet( dataset, frame_m,  Bin )
    if plotModel : plotFitModel( modelPDF, frame_m, mVarTS, sam, mod, comp, color )
    if plotData : plotDataSet( dataset, frame_m,  Bin )

    if ( mVarTS == "lab0_MassFitConsD_M" or mVarTS == "lab1_PIDK"):
        gStyle.SetOptLogy(1)
        if ((mod == "all" or mod == "pipipi") and mVarTS == "lab0_MassFitConsD_M"):
            frame_m.GetYaxis().SetRangeUser(10,frame_m.GetMaximum()*1.35)
        else:
            frame_m.GetYaxis().SetRangeUser(1.5,frame_m.GetMaximum()*1.35)
    elif ( mVarTS == "Ds_MM" ):
        frame_m.GetYaxis().SetRangeUser(1,frame_m.GetMaximum()*1.1)
    else:
        frame_m.GetYaxis().SetRangeUser(1,frame_m.GetMaximum()*1.1)
                               
    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    canvas.cd()
    pad1 = TPad("upperPad", "upperPad", .050, .22, 1.0, 1.0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetTickx(0);
    pad1.Draw()
    pad1.cd()
       
    if mVarTS == "lab1_PIDK":
        legend = TLegend( 0.60, 0.50, 0.88, 0.88 )
    elif mVarTS == "lab2_MM":
        legend = TLegend( 0.60, 0.50, 0.88, 0.88 )
    else:    
        legend = TLegend( 0.60, 0.50, 0.88, 0.88 )
        
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
          
    gr = TGraphErrors(10);
    gr.SetName("gr");
    gr.SetLineColor(kBlack);
    gr.SetLineWidth(2);
    gr.SetMarkerStyle(20);
    gr.SetMarkerSize(1.3);
    gr.SetMarkerColor(kBlack);
    gr.Draw("P");
    legend.AddEntry("gr","Data","lep");

    l1 = TLine()
    l1.SetLineColor(color[0])
    l1.SetLineWidth(4)
    l1.SetLineStyle(kDashed)
    legend.AddEntry(l1, desc[0], "L")
                    
    h = []
    for i in range(1, comp.__len__()):
        print i
        h.append(TH1F(comp[i],comp[i],5,0,1))
        h[i-1].SetFillColor(color[i])
        h[i-1].SetFillStyle(1001)
        legend.AddEntry(h[i-1], desc[i], "f")

    pad1.cd()
    frame_m.Draw()
    if ( mVarTS != "Ds_MM" ):
        legend.Draw("same")
    if mVarTS == "lab2_MM":
        lhcbtext.DrawTextNDC(0.13,0.85,"LHCb")
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
    frame_p.GetYaxis().SetNdivisions(106)
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
        

    if mVarTS == "lab1_PIDK" or mVarTS == "Bac_PIDK":
        frame_p.GetXaxis().SetTitle('#font[12]{bachelor -PIDK [1]}')
    elif mVarTS == "lab2_MM" or mVarTS == "Ds_MM":
        frame_p.GetXaxis().SetTitle('#font[12]{m(D_{s}) [MeV/c^{2}]}')
    else:
        frame_p.GetXaxis().SetTitle('#font[12]{m(B_{s} #rightarrow D_{s}#pi) [MeV/c^{2}]}')
                                        
                                          
    if dim == 3:
        if mVarTS == "lab1_PIDK":
            pullnameTS = TString("FullPdf_Int[lab0_MassFitConsD_M,lab2_MM]_Norm[lab0_MassFitConsD_M,lab1_PIDK,lab2_MM]_Comp[FullPdf]")
        elif mVarTS == "lab2_MM":
            pullnameTS = TString("FullPdf_Int[lab0_MassFitConsD_M,lab1_PIDK]_Norm[lab0_MassFitConsD_M,lab1_PIDK,lab2_MM]_Comp[FullPdf]")
        else:
            pullnameTS = TString("FullPdf_Int[lab1_PIDK,lab2_MM]_Norm[lab0_MassFitConsD_M,lab1_PIDK,lab2_MM]_Comp[FullPdf]")
    elif dim == 2:
        if mVarTS == "lab2_MM":
            pullnameTS = TString("FullPdf_Int[lab0_MassFitConsD_M]_Norm[lab0_MassFitConsD_M,lab2_MM]_Comp[FullPdf]")
        elif mVarTS == "lab0_MassFitConsD_M":
            pullnameTS = TString("FullPdf_Int[lab2_MM]_Norm[lab0_MassFitConsD_M,lab2_MM]_Comp[FullPdf]")
        elif mVarTS == "Ds_MM":
            pullnameTS = TString("FullPdf_Int[Bs_MassConsDs_M]_Norm[Bs_MassConsDs_M,Ds_MM]_Comp[FullPdf]")
        else:
            pullnameTS = TString("FullPdf_Int[Ds_MM]_Norm[Bs_MassConsDs_M,Ds_MM]_Comp[FullPdf]")
    elif dim == 1:
        pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[FullPdf]")
    
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    frame_p.addPlotable(pullHist,"P")
    frame_p.Draw()
        
    axisX = pullHist.GetXaxis()
    axisX.Set(Bin.numBins(), Bin.array())
    
    axisY = pullHist.GetYaxis()
    max = axisY.GetXmax()
    min = axisY.GetXmin()
    axisY.SetLabelSize(0.12)
    axisY.SetNdivisions(5)
    axisX.SetLabelSize(0.12)        

    range = max-min
    zero = max/range
    print "max: %s, min: %s, range: %s, zero:%s"%(max,min,range,zero)
    
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

    pullHist.GetXaxis().SetLabelFont( 132 )
    pullHist.GetYaxis().SetLabelFont( 132 )
    pullHist.SetTitle("")
    

    #tex = TLatex()
    #tex.SetTextSize(0.12)
    #pullHist.Draw("ap")
    frame_p.Draw()
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
    #tex.DrawLatex(0.50,0.30,"m(B_{s} #rightarrow D_{s}#pi) [MeV/c^{2}]")
         
    pad2.Update()
    canvas.Update()
                                                                                
    chi2 = frame_m.chiSquare();
    chi22 = frame_m.chiSquare(pullnameTS.Data(),pullname2TS.Data());
    
    print "chi2: %f"%(chi2)
    print "chi22: %f"%(chi22) 
      
#    frame_m.Draw()
    n = TString("TotEPDF_m_")+sam+TString("_paramBox")    
    pt = canvas.FindObject( n.Data() )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update()
    if ty == "yes":
        canName = TString("mass_BsDsPi_ToyMC_")+sam+TString("_")+mod+sufixTS+TString(".pdf")
        canNamePng = TString("mass_BsDsPi_ToyMC_")+sam+TString("_")+mod+sufixTS+TString(".png")
        canNameEps = TString("mass_BsDsPi_ToyMC_")+sam+TString("_")+mod+sufixTS+TString(".root") 
    else:
        canName = TString("mass_BsDsPi_")+mVarTS+TString("_")+sam+TString("_")+mod+sufixTS+TString(".pdf")
        canNamePng = TString("mass_BsDsPi_")+mVarTS+TString("_")+sam+TString("_")+mod+sufixTS+TString(".png")
        canNameEps = TString("mass_BsDsPi_")+mVarTS+TString("_")+sam+TString("_")+mod+sufixTS+TString(".root")
    canvas.Print(canName.Data())
    canvas.Print(canNamePng.Data())
    canvas.Print(canNameEps.Data())
    
#------------------------------------------------------------------------------
