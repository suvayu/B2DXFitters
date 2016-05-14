#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot MDFitter results                                    #
#                                                                             #
#   Example usage:                                                            #
#      python -i plotBs2DsKMassModels.py                                      #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 21 / 06 / 2015                                                    #
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
gROOT.ProcessLine(".x ../root/.rootlogon.C")

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
bName = 'B_{s}'

bin = 120
#------------------------------------------------------------------------------
_usage = '%prog [options] <filename>'

parser = OptionParser( _usage )

parser.add_option( '-w', '--workspace',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   default = 'FitMeToolWS',
                   help = 'RooWorkspace name as stored in ROOT file'
                   )

parser.add_option( '-p', '--pol','--polarity',
                   dest = 'pol',
                   metavar = 'POL',
                   default = 'down',
                   help = 'Sample: choose up, down or both'
                   )

parser.add_option( '-m', '--mode',
                   dest = 'modeDs',
                   metavar = 'MODE',
                   default = 'kkpi',
                   help = 'Mode: choose all, kkpi, kpipi or pipipi'
                   )

parser.add_option( '--year',
                   dest = 'year',
                   default = "",
                   help = 'year of data taking can be: 2011, 2012, run1'
                   )

parser.add_option( '-t', '--toy',
                   dest = 'toy',
                   metavar = 'TOY',
                   action = 'store_true', 
                   default = False,
                   help = 'if ToyMC choose yes.'
                   )

parser.add_option( '-v', '--variable', '--var',
                   dest = 'var',
                   default = 'BeautyMass',
                   help = 'set observable '
                   )

parser.add_option( '-s', '--suffix',
                   dest = 'sufix',
                   metavar = 'SUFIX',
                   default = '',
                   help = 'Add sufix to output'
                   )
parser.add_option( '--merge',
                   dest = 'merge',
                   default = "",
                   help = 'for merging magnet polarities use: --merge pol, for merging years of data taking use: --merge year, for merging both use: --merge both'
                   )
parser.add_option( '--logscale', '--log',
                   dest = 'log',
                   action = 'store_true',
                   default = False,
                   help = 'log scale of plot'
                   )
parser.add_option( '--bin',
                   dest = 'bin',
                   default = 100,
                   help = 'set number of bins'
                   )

parser.add_option( '--legend',
                   dest = 'legend',
                   action = 'store_true',
                   default = False,
                   help = 'plot legend on the plot'
                   )

parser.add_option( '--dim',
                   dest = 'dim',
                   default = 1)

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'Bs2DsstKConfigForNominalMassFit')

#------------------------------------------------------------------------------

def getTotPDF(w, sam, mod, year, merge, comp, debug):
    c = []
    n = []

    hypo = TString("") 
    smy = sm = GeneralUtils.GetSampleModeYearHypo(TString(sam), TString(mod), TString(year), hypo, merge, debug )
    for p in comp:
        for s in smy:
            var = w.var("n%s_%s_Evts"%(p,s))
            if var:
                if p == "Sig" or p == "CombBkg":
                    c.append("n%s_%s_Evts*%sEPDF_%s"%(p,s,p,s))
                else:
                    c.append("n%s_%s_Evts*%sEPDF_m_%s"%(p,s,p,s))
                n.append("n%s_%s_Evts"%(p,s))
                print "...........n%s_%s_Evts"%(p,s)
            else:
                c.append("")
                n.append("")

    print c,
    print n,
    pdfcomp = c[0]
    #if n.__len__() < 20 or merge == True:
    for i in range(1,c.__len__()):
        pdfcomp = pdfcomp +"," +c[i]
    if debug:
        print "Total PDF to print: %s"%(pdfcomp)
    w.factory("SUM:FullPdf(%s)"%(pdfcomp))
    '''
    else:
        pdfcomp1 = c[0]
        numcomp1 = n[0]
        for i in range(1,c.__len__()/2):
            pdfcomp1 = pdfcomp1+","+c[i]
            numcomp1 = numcomp1+","+n[i]
 #           print "pdf1: %s"%(pdfcomp1) 
 #           print "num1: %s"%(numcomp1)
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
#        print "pdf2: %s"%(pdfcomp2)
 #       print "num2: %s"%(numcomp2)
        #exit(0)
        if debug:
            print "Total PDF2 to print: %s"%(pdfcomp2)
            print "Number of events to print: %s"%(numcomp2)
        w.factory("SUM:FullPdf2(%s)"%(pdfcomp2))
        
        w.factory("EXPR::N_2(%s)"%(numcomp2))
        w.factory("SUM:FullPdf(N_1*FullPdf1,N_2*FullPdf2)")
    '''
    
    totName = TString("FullPdf")
    modelPDF = w.pdf( totName.Data() )    

  #  modelPDF.Print("v")
   # exit(0) 

    return modelPDF

#------------------------------------------------------------------------------ 
def getDataCut(sam, mod, year, merge, debug):
    
    smy = sm = GeneralUtils.GetSampleModeYearHypo(TString(sam), TString(mod), TString(year), TString(""), merge, debug )

    c = [ ]
    for s in smy:
        c.append("sample==sample::%s"%(s))

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
                    RooFit.Binning( Bin ),
                    RooFit.Name("dataSetCut"))
                        
#    dataset.statOn( frame,
#                    RooFit.Layout( 0.56, 0.90, 0.90 ),
#                    RooFit.What('N') )

#------------------------------------------------------------------------------
def plotFitModel( model, frame, var, sam, mode, year, merge, decay, comp, color) :
    #if debug :

    hypo = TString("")
    smy = sm = GeneralUtils.GetSampleModeYearHypo(TString(sam), TString(mod), TString(year), TString(hypo), merge, debug )
    
    c = []
    for p in comp:
        for s in smy:
            if p == "Sig" or p == "CombBkg":
                c.append("%sEPDF_%s"%(p,s))
            elif ((p == "Lb2DsDsstP" or p == "Bs2DsDsstPiRho") and decay == "Bs2DsK"):
                c.append("PhysBkg%sPdf_m_%s_Tot"%(p,s))
            else:
                c.append("%sEPDF_m_%s"%(p,s))


    numBkg = comp.__len__()                
    numCom = c.__len__()
    numSM = smy.__len__()
    
    print numBkg
    print numSM
    
    pdfcomp = []
    n = 0
    for j in range(0,numBkg):
        for i in range(0,numSM):
            print c[n]
            print i+j*numBkg
            if i == 0:
                pdfcomp.append(c[n])
            else:    
                pdfcomp[j] = pdfcomp[j]+","+c[n]
            n = n+1

    for i in range(0,numBkg):
        if i == 0 or i == 1: continue
        pdfcomp[i] = pdfcomp[i]+","+pdfcomp[i-1]
    
    for n in pdfcomp:    
        print "PDF to plot: %s"%(n)
   # exit(0) 
    model.plotOn( frame, 
                  RooFit.Components("FullPdf"),
                  RooFit.LineColor(kBlue),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected ),
                  RooFit.Name("FullPdf")
                  )

    for i in range(1, numBkg):
        print i
        model.plotOn( frame, 
                      RooFit.Components(pdfcomp[numBkg-i]),
                      RooFit.DrawOption("F"),
                      RooFit.FillStyle(1001),
                      RooFit.FillColor(color[numBkg-i]),
                      RooFit.Normalization( 1., RooAbsReal.RelativeExpected ),
                      RooFit.Name(Form("PDF%d"%(i))))

    model.plotOn( frame, 
                  RooFit.Components(pdfcomp[0]),
                  RooFit.LineColor(color[0]),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected ),
                  RooFit.Name("PDFSig"))

#------------------------------------------------------------------------------
def getDescription(comp,decay):

    happystar = "#lower[-0.95]{#scale[0.5]{(}}#lower[-0.8]{#scale[0.5]{*}}#lower[-0.95]{#scale[0.5]{)}}"
    happystar2 = "#lower[-0.65]{#scale[0.6]{*}}"
    happypm   = "#lower[-0.95]{#scale[0.6]{#pm}}"
    happymp   = "#lower[-0.95]{#scale[0.6]{#mp}}"
    happystarpm = "#lower[-0.95]{#scale[0.6]{*#pm}}"
    happyplus = "#lower[-0.95]{#scale[0.6]{+}}"
    happymin  = "#lower[-1.15]{#scale[0.7]{-}}"
    happy0   = "#lower[-0.85]{#scale[0.6]{0}}"

    from B2DXFitters import TLatexUtils
    desc = []
    for c in comp:
        if c == "Sig" or c == "Signal":
            if decay == "Bs2DsPi":
                desc.append("Signal B_{s}#kern[-0.7]{"+happy0+"}#rightarrow D_{s}#kern[-0.3]{"+happymin+"}#kern[0.1]{#pi"+happyplus+"}")
            elif decay == "Bs2DsK":
                desc.append("Signal B_{s}#kern[-0.7]{"+happy0+"} #rightarrow D_{s}#kern[-0.3]{"+happymp+"}#kern[0.1]{K"+happypm+"}") 
            elif decay == "Bs2DsstPi":
                desc.append("Signal B_{s}#kern[-0.7]{"+happy0+"}#rightarrow D_{s}#kern[-0.3]{"+happystar+happymin+"}#kern[0.1]{#pi"+happyplus+"}")
            elif decay == "Bs2DsstK":
                desc.append("Signal B_{s}#kern[-0.7]{"+happy0+"} #rightarrow D_{s}#kern[-0.3]{"+happystar+happymp+"}#kern[0.1]{K"+happypm+"}")
            else:
                desc.append("Signal") 
        elif c == "Bs2DsDsstPiRho" and decay == "Bs2DsPi":
            desc.append("B_{(d,s)}#kern[-3.7]{"+happy0+"} #rightarrow D_{s}#kern[-0.3]{"+happymin+happystar+"}#kern[0.1]{#pi"+happyplus+"}")
        elif c == "Bs2DsDsstPiRho" and decay == "Bs2DsK":
            desc.append("B_{s}#kern[-0.7]{"+happy0+"} #rightarrow D_{s}#kern[-0.3]{"+happymin+happystar+"}#kern[0.1]{(#pi"+happyplus+",#kern[0.1]{#rho"+happyplus+"})}") 
        elif c == "Lb2DsDsstP" and decay == "Bs2DsK":
            desc.append("#Lambda_{b}#kern[-1.2]{"+happy0+"} #rightarrow D_{s}#kern[-0.3]{"+happymin+happystar+"}#kern[0.1]{p}")
        elif c == "Bs2DsDsstKKst" and decay == "Bs2DsK":
            desc.append("B_{(d,s)}#kern[-3.7]{"+happy0+"} #kern[+0.3]{#rightarrow}D_{s}#kern[-0.3]{"+happymp+happystar+"}#kern[0.1]{K"+happypm+happystar+"}")
        else:
            desc.append(str(TLatexUtils.DecDescrToTLatex(c)))
    return desc
#------------------------------------------------------------------------------
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
    bin = int(options.bin)
    mVarTS = TString(options.var)    
    mass = w.var(mVarTS.Data())
    sam = TString(options.pol)
    mod = TString(options.modeDs)
    log = options.log 
    leg = options.legend
    yr = TString(options.year) 
    debug = options.debug 
    
    config = options.configName
    last = config.rfind("/")
    directory = config[:last+1]
    configName = config[last+1:]
    p = configName.rfind(".")
    configName = configName[:p]

    import sys
    sys.path.append(directory)
    
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "PREPARING WORKSPACE IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="

    ch =  TString(myconfigfile["Decay"])

    range_dw = mass.getMin()
    range_up = mass.getMax()

    if mVarTS.Contains("PIDK") == False:
        unit = "MeV/#font[12]{c}^{2}"
    else:
        unit = ""
            
    Bin = RooBinning(range_dw,range_up,'P')
    Bin.addUniform(bin, range_dw, range_up)
          
    merge = TString(options.merge)
                
    ty = TString("ToyNo")
    if options.toy : ty = TString("ToyYes")  
    w.Print('v')
    
    if myconfigfile.has_key("PlotSettings"):

        print type(myconfigfile["PlotSettings"]["components"])
        if type(myconfigfile["PlotSettings"]["components"]) == dict: 
            compEPDF = myconfigfile["PlotSettings"]["components"]["EPDF"]
            compPDF = myconfigfile["PlotSettings"]["components"]["PDF"]
            compLEG = myconfigfile["PlotSettings"]["components"]["Legend"]
            colorPDF = myconfigfile["PlotSettings"]["colors"]["PDF"]
            colorLEG = myconfigfile["PlotSettings"]["colors"]["Legend"]
        else:
            compEPDF = myconfigfile["PlotSettings"]["components"]
            compPDF = compEPDF
            compLEG = compEPDF
            colorPDF = myconfigfile["PlotSettings"]["colors"]
            colorLEG = colorPDF 
    else:
        print "[ERROR] PlotSettings missed in the config file."
        exit(0)

    desc = getDescription(compLEG,ch) 

    datacut = getDataCut(sam,mod,yr,merge,debug)    

    dataName = TString("combData")
    totName = TString("FullPdf")
    modelPDF = getTotPDF(w, sam, mod, yr, merge, compEPDF, debug)
    dataset = w.data( dataName.Data() )
       
    if not ( modelPDF and dataset ) :
        print "[ERROR] Something went wrong: either PDF or dataSet NULL"
        w.Print( 'v' )
        exit( 0 )
 
    frame_m = mass.frame() 
    frame_m.SetTitle('')
        
    frame_m.GetXaxis().SetLabelSize( 0.065 )
    frame_m.GetYaxis().SetLabelSize( 0.065 )
    frame_m.GetXaxis().SetLabelFont( 132 )
    frame_m.GetYaxis().SetLabelFont( 132 )
    frame_m.GetXaxis().SetLabelOffset( 0.006 )
    frame_m.GetYaxis().SetLabelOffset( 0.006 )
    frame_m.GetXaxis().SetLabelColor( kWhite)
            
    frame_m.GetXaxis().SetTitleSize( 0.065 )
    frame_m.GetYaxis().SetTitleSize( 0.065 )
    frame_m.GetYaxis().SetNdivisions(512)
    
    frame_m.GetXaxis().SetTitleOffset( 1.00 )
    frame_m.GetYaxis().SetTitleOffset( 1.20 )
    frame_m.GetYaxis().SetTitle((TString.Format("#font[132]{Candidates / ( " +
                                                    "{0:0.2f}".format(mass.getBinWidth(1))+" "+
                                                    unit+")}") ).Data())

    if dataset.numEntries() > 30000:
        frame_m.GetYaxis().SetNdivisions(508)
        frame_m.GetYaxis().SetTitleOffset( 1.20 )

    if mVarTS == "CharmMass" or mVarTS.Contains("lab2") or mVarTS.Contains("Ds") or ( mVarTS.Contains("PIDK") and ch.Contains("Pi")) :
        frame_m.GetYaxis().SetNdivisions(508)

        
    if plotData : plotDataSet( dataset, frame_m,  Bin )
    if plotModel : plotFitModel( modelPDF, frame_m, mVarTS, sam, mod, yr, merge, ch, compPDF, colorPDF )
    if plotData : plotDataSet( dataset, frame_m,  Bin )

    
    if log:
        gStyle.SetOptLogy(1)
        frame_m.GetYaxis().SetRangeUser(1.5,frame_m.GetMaximum()*1.5)

    
    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    canvas.cd()
    pad1 = TPad("upperPad", "upperPad", .005, .05, 1.0, 1.0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetBottomMargin(0.30)
    pad1.SetLeftMargin(0.17)
    pad1.SetTopMargin(0.05)
    pad1.SetRightMargin(0.05)
    if mVarTS == "lab0_MassFitConsD_M" or mVarTS == "BeautyMass":
        pad1.SetRightMargin(0.08)
    pad1.SetFillStyle(0)
    pad1.SetTickx(0);
    pad1.Draw()
    pad1.cd()


    if leg:
        if myconfigfile.has_key("LegendSettings"):
            xs = myconfigfile["LegendSettings"][mVarTS.Data()]["Position"][0]
            ys = myconfigfile["LegendSettings"][mVarTS.Data()]["Position"][1]
            xe = myconfigfile["LegendSettings"][mVarTS.Data()]["Position"][2]
            ye = myconfigfile["LegendSettings"][mVarTS.Data()]["Position"][3]
            legend = TLegend( xs, ys, xe, ye )
            size = myconfigfile["LegendSettings"][mVarTS.Data()]["TextSize"]
            legend.SetTextSize(size)
            if myconfigfile["LegendSettings"][mVarTS.Data()].has_key("ScaleYSize"):
                scale = myconfigfile["LegendSettings"][mVarTS.Data()]["ScaleYSize"]
            else:
                scale = 1.2 
            if log:
                frame_m.GetYaxis().SetRangeUser(1.5,frame_m.GetMaximum()*scale)
            else:
                frame_m.GetYaxis().SetRangeUser(1.0,frame_m.GetMaximum()*scale)
        else:
            print "[ERROR] You need to specify position of legend in configfile using 'LegendSettings'"
            exit(0) 
    else:
        frame_m.GetYaxis().SetRangeUser(5.0,frame_m.GetMaximum()*1.1)
        legend = TLegend( 0.05, 0.05, 0.95, 0.95 )
        legend.SetTextSize(0.09)

    legend.SetTextFont(12) 
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)

    lhcbtext = TLatex()
    lhcbtext.SetTextFont(132)
    lhcbtext.SetTextColor(1)
    if myconfigfile.has_key("LegendSettings"):
        if myconfigfile["LegendSettings"][mVarTS.Data()].has_key("LHCbTextSize"):
            sizelhcbtext = myconfigfile["LegendSettings"][mVarTS.Data()]["LHCbTextSize"]
        else:
            sizelhcbtext = 0.08
        if myconfigfile["LegendSettings"][mVarTS.Data()].has_key("SetLegendColumns"):
            legend.SetNColumns(int(myconfigfile["LegendSettings"][mVarTS.Data()]["SetLegendColumns"]))
    else:
        sizelhcbtext = 0.08
    lhcbtext.SetTextSize(sizelhcbtext)
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
    l1.SetLineColor(colorLEG[0])
    l1.SetLineWidth(4)
    l1.SetLineStyle(kDashed)
    legend.AddEntry(l1, desc[0], "L")
                    
    h = []
    print compLEG
    print desc 

    for i in range(1, compLEG.__len__()):
        print i
        print compLEG[i]
        print desc[0]
        h.append(TH1F(compLEG[i],compLEG[i],5,0,1))
        h[i-1].SetFillColor(colorLEG[i])
        h[i-1].SetFillStyle(1001)
        legend.AddEntry(h[i-1], desc[i], "f")
    pad1.cd()
    frame_m.Draw()

    if leg:
        legend.Draw("same")
        if myconfigfile.has_key("LegendSettings"):
            xl = myconfigfile["LegendSettings"][mVarTS.Data()]["LHCbText"][0]
            yl = myconfigfile["LegendSettings"][mVarTS.Data()]["LHCbText"][1]
            lhcbtext.DrawTextNDC(xl,yl,"LHCb")
    else:
        if myconfigfile.has_key("LegendSettings"):
            xl = myconfigfile["LegendSettings"][mVarTS.Data()]["LHCbText"][0]
            yl = myconfigfile["LegendSettings"][mVarTS.Data()]["LHCbText"][1]
            lhcbtext.DrawTextNDC(xl,yl,"LHCb")
        else:
            lhcbtext.DrawTextNDC(0.75,0.87,"LHCb")

    pad1.Update()

    canvas.cd()
    pad2 = TPad("lowerPad", "lowerPad", .005, .005, 1.0, .37)
    pad2.SetBorderMode(0)
    pad2.SetBorderSize(-1)
    pad2.SetFillStyle(0)
    pad2.SetBottomMargin(0.40)
    pad2.SetLeftMargin(0.17)
    pad2.SetRightMargin(0.05)
    if mVarTS == "lab0_MassFitConsD_M" or mVarTS == "BeautyMass":
        pad2.SetRightMargin(0.08)

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
    frame_p.GetYaxis().SetLabelSize(0.16)
    frame_p.GetYaxis().SetLabelOffset(0.006)
    frame_p.GetXaxis().SetLabelOffset(0.06)
    frame_p.GetXaxis().SetTitleSize(0.16)
    frame_p.GetXaxis().SetTitleFont(132) 
    frame_p.GetXaxis().SetTitleOffset(1.2)
    frame_p.GetXaxis().SetNdivisions(5)
    frame_p.GetYaxis().SetNdivisions(5)
    frame_p.GetYaxis().SetRangeUser(-4,4)
    frame_p.GetXaxis().SetLabelSize(0.16)
    frame_p.GetXaxis().SetLabelFont( 132 )
    frame_p.GetYaxis().SetLabelFont( 132 )


    labelX = GeneralUtils.GetXLabel(ch,mVarTS,TString(mod), debug) 
    frame_p.GetXaxis().SetTitle(labelX.Data()) 

    pullnameTS = TString("FullPdf")
    pullname2TS = TString("dataSetCut")    
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
    graph2.SetPoint(0,range_dw,-3)
    graph2.SetPoint(1,range_up,-3)
    graph2.SetLineColor(kRed)

    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    graph3.SetPoint(0,range_dw,3)
    graph3.SetPoint(1,range_up,3)
    graph3.SetLineColor(kRed)

    pullHist.GetXaxis().SetLabelFont( 132 )
    pullHist.GetYaxis().SetLabelFont( 132 )
    pullHist.SetTitle("")
    

    #tex = TLatex()
    #tex.SetTextSize(0.12)
    #pullHist.Draw("ap")
    frame_p.Draw()
    frame_p.GetYaxis().SetRangeUser(-4.0,4.0)
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
    n = TString("TotEPDF_m_")+TString(sam)+TString("_paramBox")    
    pt = canvas.FindObject( n.Data() )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update()

    sufixTS = TString(options.sufix)
    if sufixTS != "":
        sufixTS = TString("_")+sufixTS
        
    if yr != "":
        yr = TString("_")+yr 

    saveName = TString("mass_")+ch+TString("_")+mVarTS+TString("_")+TString(sam)+TString("_")+mod+yr+sufixTS
    canName = saveName+TString(".pdf")
    canNamePng = saveName+TString(".png")
    canNameRoot = saveName+TString(".root")
    canNameC = saveName+TString(".C")
    canNameEps = saveName+TString(".eps")

    canvas.SaveAs(canName.Data())
    canvas.SaveAs(canNamePng.Data())
    canvas.SaveAs(canNameEps.Data())
    canvas.SaveAs(canNameC.Data())
    canvas.SaveAs(canNameRoot.Data())


    if not leg:
        canl = TCanvas("canl","canl",1200,1000)
        canl.cd()
        legend.Draw()
        canl.Update()
        saveName = TString("legend_")+ch
        canName = saveName+TString(".pdf")
        canNameC = saveName+TString(".C")
        canl.SaveAs(canName.Data())
        canl.SaveAs(canNameC.Data())

#------------------------------------------------------------------------------
