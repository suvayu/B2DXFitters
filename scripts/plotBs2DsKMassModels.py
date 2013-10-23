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
bName = 'B_{s}'

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


parser.add_option( '-v', '--variable',
                                      dest = 'var',
                                      default = 'lab0_MassFitConsD_M',
                                      help = 'set observable '
                                      )
#------------------------------------------------------------------------------
def plotDataSet( dataset, frame, sample, mode ) :

    if sample == "both":
        if mode == "all":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi || sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi"),
                            RooFit.Binning( 70 ) )
        elif mode == "kkpi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kkpi || sample==sample::down_kkpi"),
                            RooFit.Binning( 70 ) )
        elif mode == "kpipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kpipi || sample==sample::down_kpipi"),
                            RooFit.Binning( 70 ) )
        elif mode == "pipipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_pipipi || sample==sample::down_pipipi"),
                            RooFit.Binning( 70 ) )
        else:
            print "[ERROR] Sample: both, wrong mode!"

    elif sample == "up":
        if mode == "all":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi"),
                            RooFit.Binning( 70 ) )
        elif mode == "kkpi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kkpi"),
                            RooFit.Binning( 70 ) )
        elif mode == "kpipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kpipi"),
                            RooFit.Binning( 70 ) )
        elif mode == "pipipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_pipipi"),
                            RooFit.Binning( 70 ) )
        else:
            print "[ERROR] Sample: up, wrong mode!"
                                             
    elif sample == "down":
         if mode == "all":
             dataset.plotOn( frame,
                             RooFit.Cut("sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi"),
                             RooFit.Binning( 70 ) )
         elif mode == "kkpi":
             dataset.plotOn( frame,
                             RooFit.Cut("sample==sample::down_kkpi"),
                             RooFit.Binning( 70 ) )
         elif mode == "kpipi":
             dataset.plotOn( frame,
                             RooFit.Cut("sample==sample::down_kpipi"),
                             RooFit.Binning( 70 ) )
         elif mode == "pipipi":
             dataset.plotOn( frame,
                             RooFit.Cut("sample==sample::down_pipipi"),
                             RooFit.Binning( 70 ) )
         else:
             print "[ERROR] Sample: down, wrong mode!"
    else:
        print "[ERROR] Wrong sample!"
                                                                         
                
#    dataset.statOn( frame,
#                    RooFit.Layout( 0.56, 0.90, 0.90 ),
#                    RooFit.What('N') )

#------------------------------------------------------------------------------
def plotFitModel( model, frame, sam, var,mode) :
    #if debug :
    
    print "model"    
    model.Print( 't' )

    print "frame"
    frame.Print( 'v' )
    t=TString("_")
    p=TString(",")
    if sam == "both":
        if mode == "all":
            nameTot = TString("FullPdf")

            mode1 = TString("kkpi")
            mode2 = TString("kpipi")
            mode3 = TString("pipipi")
                                   
            nameCom1 =TString("CombBkgEPDF_m_up_")+mode1+p+TString("CombBkgEPDF_m_down_")+mode1
            nameCom2 =TString("CombBkgEPDF_m_up_")+mode2+p+TString("CombBkgEPDF_m_down_")+mode2
            nameCom3 =TString("CombBkgEPDF_m_up_")+mode3+p+TString("CombBkgEPDF_m_down_")+mode3
            nameCom = nameCom1+p+nameCom2+p+nameCom3
                                                
            nameSig1 = TString("SigEPDF_up_")+mode1+p+TString("SigEPDF_down_")+mode1
            nameSig2 = TString("SigEPDF_up_")+mode2+p+TString("SigEPDF_down_")+mode2
            nameSig3 = TString("SigEPDF_up_")+mode3+p+TString("SigEPDF_down_")+mode3            
            nameSig = nameSig1+p+nameSig2+p+nameSig3
                                                
            nameLam1 = TString("Lb2DsDsstPEPDF_m_up_")+mode1+p+TString("Lb2DsDsstPEPDF_m_down_")+mode1
            nameLam2 = TString("Lb2DsDsstPEPDF_m_up_")+mode2+p+TString("Lb2DsDsstPEPDF_m_down_")+mode2
            nameLam3 = TString("Lb2DsDsstPEPDF_m_up_")+mode3+p+TString("Lb2DsDsstPEPDF_m_down_")+mode3
            nameLam = nameLam1+p+nameLam2+p+nameLam3

            nameLamK1 = TString("Lb2LcKEPDF_m_up_")+mode1+p+TString("Lb2LcKEPDF_m_down_")+mode1
            nameLamK2 = TString("Lb2LcKEPDF_m_up_")+mode2+p+TString("Lb2LcKEPDF_m_down_")+mode2
            nameLamK3 = TString("Lb2LcKEPDF_m_up_")+mode3+p+TString("Lb2LcKEPDF_m_down_")+mode3
            nameLamK = nameLamK1+p+nameLamK2+p+nameLamK3
                                                


            nameRho1 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode1+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode1
            nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode2+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode2
            nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode3+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode3
            nameRho = nameRho1+p+nameRho2+p+nameRho3

            nameKst1 = TString("Bs2DsDsstKKstEPDF_m_up_")+mode1+p+TString("Bs2DsDsstKKstEPDF_m_down_")+mode1
            nameKst2 = TString("Bs2DsDsstKKstEPDF_m_up_")+mode2+p+TString("Bs2DsDsstKKstEPDF_m_down_")+mode2
            nameKst3 = TString("Bs2DsDsstKKstEPDF_m_up_")+mode3+p+TString("Bs2DsDsstKKstEPDF_m_down_")+mode3
            nameKst = nameKst1+p+nameKst2+p+nameKst3

            nameDK1  = TString("Bd2DKEPDF_m_up_")+mode1+p+TString("Bd2DKEPDF_m_down_")+mode1
            nameDK2  = TString("Bd2DKEPDF_m_up_")+mode2+p+TString("Bd2DKEPDF_m_down_")+mode2
            nameDK3  = TString("Bd2DKEPDF_m_up_")+mode3+p+TString("Bd2DKEPDF_m_down_")+mode3
            nameDK  = nameDK1+p+nameDK2+p+nameDK3
           

        else:
            nameTot = TString("FullPdf")
            nameCom1 = TString("CombBkgEPDF_m_up_")+mode
            nameCom2 = TString("CombBkgEPDF_m_down_")+mode
            nameCom = nameCom1+p+nameCom2
            nameSig = TString("SigEPDF_up_")+mode+p+TString("SigEPDF_down_")+mode
            nameLam = TString("Lb2DsDsstPEPDF_m_up_")+mode+p+TString("Lb2DsDsstPEPDF_m_down_")+mode
            nameLamK = TString("Lb2LcKEPDF_m_up_")+mode+p+TString("Lb2LcKEPDF_m_down_")+mode
            nameRho = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode
            nameKst = TString("Bs2DsDsstKKstEPDF_m_up_")+mode+p+TString("Bs2DsDsstKKstEPDF_m_down_")+mode
            nameDK  = TString("Bd2DKEPDF_m_up_")+mode+p+TString("Bd2DKEPDF_m_down_")+mode
                                                                                    
    else:
        if mode == "all":
            nameTot = TString("FullPdf")

            mode1 = TString("kkpi")
            mode2 = TString("kpipi")
            mode3 = TString("pipipi")
        
            nameCom1 =TString("CombBkgEPDF_m_")+sam+t+mode1
            nameCom2 =TString("CombBkgEPDF_m_")+sam+t+mode2
            nameCom3 =TString("CombBkgEPDF_m_")+sam+t+mode3
            nameCom = nameCom1+p+nameCom2+p+nameCom3

            nameSig1 = TString("SigEPDF_")+sam+t+mode1
            nameSig2 = TString("SigEPDF_")+sam+t+mode2
            nameSig3 = TString("SigEPDF_")+sam+t+mode3
            nameSig = nameSig1+p+nameSig2+p+nameSig3

            nameLam1 = TString("Lb2DsDsstPEPDF_m_")+sam+t+TString("kkpi")
            nameLam2 = TString("Lb2DsDsstPEPDF_m_")+sam+t+TString("kpipi")
            nameLam3 = TString("Lb2DsDsstPEPDF_m_")+sam+t+TString("pipipi")
            nameLam = nameLam1+p+nameLam2+p+nameLam3

            nameLamK1 = TString("Lb2LcKEPDF_m_")+sam+t+TString("kkpi")
            nameLamK2 = TString("Lb2LcKEPDF_m_")+sam+t+TString("kpipi")
            nameLamK3 = TString("Lb2LcKEPDF_m_")+sam+t+TString("pipipi")
            nameLamK = nameLamK1+p+nameLamK2+p+nameLamK3
                                            

            nameRho1 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("kkpi")
            nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("kpipi")
            nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("pipipi")
            nameRho = nameRho1+p+nameRho2+p+nameRho3

            nameKst1 = TString("Bs2DsDsstKKstEPDF_m_")+sam+t+TString("kkpi")
            nameKst2 = TString("Bs2DsDsstKKstEPDF_m_")+sam+t+TString("kpipi")
            nameKst3 = TString("Bs2DsDsstKKstEPDF_m_")+sam+t+TString("pipipi")
            nameKst = nameKst1+p+nameKst2+p+nameKst3

            nameDK1  = TString("Bd2DKEPDF_m_")+sam+t+TString("kkpi")
            nameDK2  = TString("Bd2DKEPDF_m_")+sam+t+TString("kpipi")
            nameDK3  = TString("Bd2DKEPDF_m_")+sam+t+TString("pipipi")
            nameDK  = nameDK1+p+nameDK2+p+nameDK3
        
        else:
            nameTot = TString("FullPdf")
            nameCom = TString("CombBkgEPDF_m_")+sam+t+mode
            nameSig = TString("SigEPDF_")+sam+t+mode
            nameLam = TString("Lb2DsDsstPEPDF_m_")+sam+t+mode
            nameLamK = TString("Lb2LcKEPDF_m_")+sam+t+mode
            nameRho = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+mode
            nameKst = TString("Bs2DsDsstKKstEPDF_m_")+sam+t+mode
            nameDK  = TString("Bd2DKEPDF_m_")+sam+t+mode
                                                        
    #p=TString(",")
    
    nameLamKCom = nameLamK+p+nameCom
    nameLamCom = nameLamKCom+p+nameLam
    nameAllDsPi = nameLamCom+p+nameRho
    nameAllDK   = nameAllDsPi+p+nameDK
    nameAllDsK  = nameAllDK+p+nameKst

                
    model.plotOn( frame,
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kBlue),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameAllDsK.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-10),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components(nameAllDK.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kRed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameAllDsPi.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-6),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )        

    
    model.plotOn( frame,
                  RooFit.Components(nameLamCom.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kYellow-9),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    model.plotOn( frame,
                  RooFit.Components(nameLamKCom.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kGreen-3),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
     
            
    model.plotOn( frame,
                  RooFit.Components(nameCom.Data()),
                  RooFit.DrawOption("F"),                  
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kMagenta-2),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame,
                  RooFit.Components(nameSig.Data()),
                  RooFit.LineColor(kRed-7),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
       
#    model.paramOn( frame,
#                   RooFit.Layout( 0.56, 0.90, 0.85 ),
#                   RooFit.Format( 'NEU', RooFit.AutoPrecision( 2 ) )
#                   )

#    decays = ["Combinatorial",
#              "B^{0}#rightarrow D^{-}_{s}K^{+}"]
#    compColor = [kBlack, kGray]                 
    #decayNameLatex="B^{0}_{s}#rightarrow D^{#pm}_{s}K^{#mp}"

    #where = [0.55,0.30,0.87,0.61]
#    legend = TLegend( 0.13, 0.57, 0.44, 0.87 )
    ## Signal
#    l1 = TLine()
#    l1.SetLineColor(kRed)
#    l1.SetLineStyle(kDashed)
#    legend.AddEntry(l1, "Signa", "L")
    #hs = []

    #for cC in xrange(len(compColor)):
    #    print 'mamma',decays[cC], compColor[cC]
    #    hs.append(TH1F("h%s"%(cC),"h%s"%(cC),10,0,1))
    #    hs[-1].SetFillColor(compColor[cC])
    #    hs[-1].SetFillStyle(1001)
    #    legend.AddEntry(hs[-1], "%s"%decays[cC], "f")
    #legend.SetTextFont(12)
#    legend.Draw()                                                                        

    
    #stat = frame.findObject( 'data_statBox' )
    #if not stat:
    #    statTS = TString("TotEPDF_m_")+sam+TString("_Data_statBox")
    #    stat = frame.findObject( statTS.Data() )
    #if stat :
    #    stat.SetTextSize( 0.025 )
    #ptTS = TString("TotEPDF_m_")+sam+TString("_paramBox")    
    #pt = frame.findObject( ptTS.Data() )
    #if pt :
    #    pt.SetTextSize( 0.02 )
    # Legend of EPDF components

    #leg = TLegend( 0.13, 0.57, 0.44, 0.87 )
    #leg.SetFillColor( 0 )
    #leg.SetTextSize( 0.02 )

    #comps = model.getComponents()

    #pdf = comps.find(nameSig.Data())
    #pdfNameTS = TString("TotEPDF_m_")+sam+TString("_Norm[")+var+TString("]_Comp[")+nameSig.Data()+TString("]") 
    #pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bs2DsPiEPDF'

    #h=TH1F(nameSig.Data(),nameSig.Data(),10,0,1)
    #h.SetFillColor(kRed)
    #h.SetFillStyle(1001)

    #curve = frame.findObject( pdfNameTS.Data() )

    #decay = TString("Signal")
    #leg.AddEntry(curve, decay.Data(), 'l' )
    #leg.Draw()
    
    #leg.AddEntry( curve, pdf.GetTitle(), 'l' )
    #frame.addObject( leg )
    #pdf = comps.find( 'CombBkgEPDF_m' )
    #pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'CombBkgEPDF_m'
    #curve5 = frame.findObject( pdfName )
    #leg.AddEntry( curve5, pdf.GetTitle(), 'l' )
    #frame.addObject( leg )
    #pdf = comps.find( 'SigEPDF' )
    #pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'SigEPDF'
    #curve6 = frame.findObject( pdfName )
    #leg.AddEntry( curve6, pdf.GetTitle(), 'l' )
    #frame.addObject( leg )
    #pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'CombBkgEPDF_m,Bs2DsPiEPDF'
    #curve7 = frame.findObject( pdfName )
    #leg.AddEntry( curve7, 'All but %s' % pdf.GetTitle(), 'f' )
    #curve7.SetLineColor(0)

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
    
    from ROOT import TFile, TCanvas, gROOT, TLegend, TString, TLine, TH1F, TBox, TPad, TGraph,  TMarker, TGraphErrors, TLatex
    
    from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed, kBlack, kGray, kViolet
    from ROOT import RooFit, RooRealVar, RooAbsReal, RooCategory, RooArgSet, RooAddPdf, RooArgList
    gROOT.SetStyle( 'Plain' )    
    gROOT.SetBatch( False )
    
    
    f = TFile( FILENAME )

    w = f.Get( options.wsname )
    if not w :
        parser.error( 'Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      ( options.wsname, FILENAME ) )
    
    f.Close()
    mVarTS = TString(options.var)    
    mass = w.var(mVarTS.Data())
    mean  = 5366
    #mass = RooRealVar( 'mass', '%s mass' % bName, mean, 5000, 5800, 'MeV/c^{2}' )
    sam = TString(options.sample)
    mod = TString(options.mode)  
    w.Print('v')
    #exit(0)
        
       
    dataName = TString("combData")


    if sam == "up":
        if mod == "all":
            print "Sample up, mode all"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nBs2DsDssKKst_up_kkpi_Evts*Bs2DsDsstKKstEPDF_m_up_kkpi, nLb2DsDsstp_up_kkpi_Evts*Lb2DsDsstPEPDF_m_up_kkpi, nBd2DK_up_kkpi_Evts*Bd2DKEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi, nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nBs2DsDssKKst_up_kpipi_Evts*Bs2DsDsstKKstEPDF_m_up_kpipi, nLb2DsDsstp_up_kpipi_Evts*Lb2DsDsstPEPDF_m_up_kpipi, nBd2DK_up_kpipi_Evts*Bd2DKEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi,nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nBs2DsDssKKst_up_pipipi_Evts*Bs2DsDsstKKstEPDF_m_up_pipipi, nLb2DsDsstp_up_pipipi_Evts*Lb2DsDsstPEPDF_m_up_pipipi, nBd2DK_up_pipipi_Evts*Bd2DKEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi]")
            
        elif mod == "kkpi":
            print "Sample up, mode kkpi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nBs2DsDssKKst_up_kkpi_Evts*Bs2DsDsstKKstEPDF_m_up_kkpi, nLb2DsDsstp_up_kkpi_Evts*Lb2DsDsstPEPDF_m_up_kkpi, nBd2DK_up_kkpi_Evts*Bd2DKEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi, nLb2LcK_up_kkpi_Evts*Lb2LcKEPDF_m_up_kkpi )")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi]")
            
        elif mod == "kpipi":        
            print "Sample up, mode kpipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nBs2DsDssKKst_up_kpipi_Evts*Bs2DsDsstKKstEPDF_m_up_kpipi, nLb2DsDsstp_up_kpipi_Evts*Lb2DsDsstPEPDF_m_up_kpipi, nBd2DK_up_kpipi_Evts*Bd2DKEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi, nLb2LcK_up_kpipi_Evts*Lb2LcKEPDF_m_up_kpipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kpipi]")
            
        elif mod == "pipipi":
            print "Sample up, mode pipipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nBs2DsDssKKst_up_pipipi_Evts*Bs2DsDsstKKstEPDF_m_up_pipipi, nLb2DsDsstp_up_pipipi_Evts*Lb2DsDsstPEPDF_m_up_pipipi, nBd2DK_up_pipipi_Evts*Bd2DKEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi, nLb2LcK_up_pipipi_Evts*Lb2LcKEPDF_m_up_pipipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_pipipi]")
            
        else:
            print "[ERROR] Wrong mode"
    elif sam == "down":
        if mod == "all":
            print "Sample down, mode all"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nBs2DsDssKKst_down_kkpi_Evts*Bs2DsDsstKKstEPDF_m_down_kkpi, nLb2DsDsstp_down_kkpi_Evts*Lb2DsDsstPEPDF_m_down_kkpi, nBd2DK_down_kkpi_Evts*Bd2DKEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nBs2DsDssKKst_down_kpipi_Evts*Bs2DsDsstKKstEPDF_m_down_kpipi, nLb2DsDsstp_down_kpipi_Evts*Lb2DsDsstPEPDF_m_down_kpipi, nBd2DK_down_kpipi_Evts*Bd2DKEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi,nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nBs2DsDssKKst_down_pipipi_Evts*Bs2DsDsstKKstEPDF_m_down_pipipi, nLb2DsDsstp_down_pipipi_Evts*Lb2DsDsstPEPDF_m_down_pipipi, nBd2DK_down_pipipi_Evts*Bd2DKEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi]")
        elif mod == "kkpi":
            print "Sample down, mode kkpi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nBs2DsDssKKst_down_kkpi_Evts*Bs2DsDsstKKstEPDF_m_down_kkpi, nLb2DsDsstp_down_kkpi_Evts*Lb2DsDsstPEPDF_m_down_kkpi, nBd2DK_down_kkpi_Evts*Bd2DKEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nLb2LcK_down_kkpi_Evts*Lb2LcKEPDF_m_down_kkpi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::down_kkpi]")

        elif mod == "kpipi":
            print "Sample down, mode kpipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nBs2DsDssKKst_down_kpipi_Evts*Bs2DsDsstKKstEPDF_m_down_kpipi, nLb2DsDsstp_down_kpipi_Evts*Lb2DsDsstPEPDF_m_down_kpipi, nBd2DK_down_kpipi_Evts*Bd2DKEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi, nLb2LcK_down_kpipi_Evts*Lb2LcKEPDF_m_down_kpipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::down_kpipi]")
            
        elif mod == "pipipi":
            print "Sample down, mode pipipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nBs2DsDssKKst_down_pipipi_Evts*Bs2DsDsstKKstEPDF_m_down_pipipi, nLb2DsDsstp_down_pipipi_Evts*Lb2DsDsstPEPDF_m_down_pipipi, nBd2DK_down_pipipi_Evts*Bd2DKEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi, nLb2LcK_down_pipipi_Evts*Lb2LcKEPDF_m_down_pipipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::down_pipipi]")
        else:
            print "[ERROR] Wrong mode"
    elif sam == "both":
        if mod == "all":
            print "Sample both, mode all"
            w.factory("SUM:FullPdf1(nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nBs2DsDssKKst_up_kkpi_Evts*Bs2DsDsstKKstEPDF_m_up_kkpi, nLb2DsDsstp_up_kkpi_Evts*Lb2DsDsstPEPDF_m_up_kkpi, nBd2DK_up_kkpi_Evts*Bd2DKEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi,nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nBs2DsDssKKst_up_kpipi_Evts*Bs2DsDsstKKstEPDF_m_up_kpipi, nLb2DsDsstp_up_kpipi_Evts*Lb2DsDsstPEPDF_m_up_kpipi, nBd2DK_up_kpipi_Evts*Bd2DKEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi,nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nBs2DsDssKKst_up_pipipi_Evts*Bs2DsDsstKKstEPDF_m_up_pipipi, nLb2DsDsstp_up_pipipi_Evts*Lb2DsDsstPEPDF_m_up_pipipi, nBd2DK_up_pipipi_Evts*Bd2DKEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi)")

            w.factory("SUM:FullLamUp(nLb2LcK_up_kkpi_Evts*Lb2LcKEPDF_m_up_kkpi, nLb2LcK_up_kpipi_Evts*Lb2LcKEPDF_m_up_kpipi,nLb2LcK_up_pipipi_Evts*Lb2LcKEPDF_m_up_pipipi)")
            w.factory("SUM:FullLamDw(nLb2LcK_down_kkpi_Evts*Lb2LcKEPDF_m_down_kkpi, nLb2LcK_down_kpipi_Evts*Lb2LcKEPDF_m_down_kpipi,nLb2LcK_down_pipipi_Evts*Lb2LcKEPDF_m_down_pipipi)")
            
            w.factory("SUM:FullPdf2(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nBs2DsDssKKst_down_kkpi_Evts*Bs2DsDsstKKstEPDF_m_down_kkpi, nLb2DsDsstp_down_kkpi_Evts*Lb2DsDsstPEPDF_m_down_kkpi, nBd2DK_down_kkpi_Evts*Bd2DKEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nBs2DsDssKKst_down_kpipi_Evts*Bs2DsDsstKKstEPDF_m_down_kpipi, nLb2DsDsstp_down_kpipi_Evts*Lb2DsDsstPEPDF_m_down_kpipi, nBd2DK_down_kpipi_Evts*Bd2DKEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi,nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nBs2DsDssKKst_down_pipipi_Evts*Bs2DsDsstKKstEPDF_m_down_pipipi, nLb2DsDsstp_down_pipipi_Evts*Lb2DsDsstPEPDF_m_down_pipipi, nBd2DK_down_pipipi_Evts*Bd2DKEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi)")

            w.factory("EXPR::N_up('nBs2DsDsstPiRho_up_kkpi_Evts+nBs2DsDssKKst_up_kkpi_Evts+nLb2DsDsstp_up_kkpi_Evts+nBd2DK_up_kkpi_Evts+nSig_up_kkpi_Evts+nCombBkg_up_kkpi_Evts+nBs2DsDsstPiRho_up_kpipi_Evts+nBs2DsDssKKst_up_kpipi_Evts+nLb2DsDsstp_up_kpipi_Evts+nBd2DK_up_kpipi_Evts+nSig_up_kpipi_Evts+nCombBkg_up_kpipi_Evts+nBs2DsDsstPiRho_up_pipipi_Evts+nBs2DsDssKKst_up_pipipi_Evts+nLb2DsDsstp_up_pipipi_Evts+nBd2DK_up_pipipi_Evts+nSig_up_pipipi_Evts+nCombBkg_up_pipipi_Evts',nBs2DsDsstPiRho_up_kkpi_Evts,nBs2DsDssKKst_up_kkpi_Evts,nLb2DsDsstp_up_kkpi_Evts,nBd2DK_up_kkpi_Evts,nSig_up_kkpi_Evts,nCombBkg_up_kkpi_Evts,nBs2DsDsstPiRho_up_kpipi_Evts,nBs2DsDssKKst_up_kpipi_Evts,nLb2DsDsstp_up_kpipi_Evts,nBd2DK_up_kpipi_Evts,nSig_up_kpipi_Evts,nCombBkg_up_kpipi_Evts,nBs2DsDsstPiRho_up_pipipi_Evts,nBs2DsDssKKst_up_pipipi_Evts,nLb2DsDsstp_up_pipipi_Evts,nBd2DK_up_pipipi_Evts,nSig_up_pipipi_Evts,nCombBkg_up_pipipi_Evts)")

            w.factory("EXPR::NL_Up('nLb2LcK_up_kkpi_Evts+nLb2LcK_up_kpipi_Evts+nLb2LcK_up_pipipi_Evts',nLb2LcK_up_kkpi_Evts,nLb2LcK_up_kpipi_Evts,nLb2LcK_up_pipipi_Evts)")
            w.factory("EXPR::NL_Dw('nLb2LcK_down_kkpi_Evts+nLb2LcK_down_kpipi_Evts+nLb2LcK_down_pipipi_Evts',nLb2LcK_down_kkpi_Evts,nLb2LcK_down_kpipi_Evts,nLb2LcK_down_pipipi_Evts)")
            
            w.factory("EXPR::N_dw('nBs2DsDsstPiRho_down_kkpi_Evts+nBs2DsDssKKst_down_kkpi_Evts+nLb2DsDsstp_down_kkpi_Evts+nBd2DK_down_kkpi_Evts+nSig_down_kkpi_Evts+nCombBkg_down_kkpi_Evts+nBs2DsDsstPiRho_down_kpipi_Evts+nBs2DsDssKKst_down_kpipi_Evts+nLb2DsDsstp_down_kpipi_Evts+nBd2DK_down_kpipi_Evts+nSig_down_kpipi_Evts+nCombBkg_down_kpipi_Evts+nBs2DsDsstPiRho_down_pipipi_Evts+nBs2DsDssKKst_down_pipipi_Evts+nLb2DsDsstp_down_pipipi_Evts+nBd2DK_down_pipipi_Evts+nSig_down_pipipi_Evts+nCombBkg_down_pipipi_Evts',nBs2DsDsstPiRho_down_kkpi_Evts,nBs2DsDssKKst_down_kkpi_Evts,nLb2DsDsstp_down_kkpi_Evts,nBd2DK_down_kkpi_Evts,nSig_down_kkpi_Evts,nCombBkg_down_kkpi_Evts,nBs2DsDsstPiRho_down_kpipi_Evts,nBs2DsDssKKst_down_kpipi_Evts,nLb2DsDsstp_down_kpipi_Evts,nBd2DK_down_kpipi_Evts,nSig_down_kpipi_Evts,nCombBkg_down_kpipi_Evts,nBs2DsDsstPiRho_down_pipipi_Evts,nBs2DsDssKKst_down_pipipi_Evts,nLb2DsDsstp_down_pipipi_Evts,nBd2DK_down_pipipi_Evts,nSig_down_pipipi_Evts,nCombBkg_down_pipipi_Evts)")

            w.factory("SUM:FullPdf(N_up*FullPdf1,N_dw*FullPdf2,NL_Up*FullLamUp,NL_Dw*FullLamDw)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi || sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi]")
        elif mod == "kkpi":
            print "Sample both, mode kkpi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nBs2DsDssKKst_down_kkpi_Evts*Bs2DsDsstKKstEPDF_m_down_kkpi, nLb2DsDsstp_down_kkpi_Evts*Lb2DsDsstPEPDF_m_down_kkpi, nBd2DK_down_kkpi_Evts*Bd2DKEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi,nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nBs2DsDssKKst_up_kkpi_Evts*Bs2DsDsstKKstEPDF_m_up_kkpi, nLb2DsDsstp_up_kkpi_Evts*Lb2DsDsstPEPDF_m_up_kkpi, nBd2DK_up_kkpi_Evts*Bd2DKEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi, nLb2LcK_up_kkpi_Evts*Lb2LcKEPDF_m_up_kkpi, nLb2LcK_down_kkpi_Evts*Lb2LcKEPDF_m_down_kkpi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi || sample==sample::down_kkpi]")
        elif  mod == "kpipi":
            print "Sample both, mode kpipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nBs2DsDssKKst_down_kpipi_Evts*Bs2DsDsstKKstEPDF_m_down_kpipi, nLb2DsDsstp_down_kpipi_Evts*Lb2DsDsstPEPDF_m_down_kpipi, nBd2DK_down_kpipi_Evts*Bd2DKEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi,nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nBs2DsDssKKst_up_kpipi_Evts*Bs2DsDsstKKstEPDF_m_up_kpipi, nLb2DsDsstp_up_kpipi_Evts*Lb2DsDsstPEPDF_m_up_kpipi, nBd2DK_up_kpipi_Evts*Bd2DKEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi, nLb2LcK_up_kpipi_Evts*Lb2LcKEPDF_m_up_kpipi, nLb2LcK_down_kpipi_Evts*Lb2LcKEPDF_m_down_kpipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kpipi || sample==sample::down_kpipi]")
            
        elif  mod == "pipipi":
           print "Sample both, mode kpipi"
           w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nBs2DsDssKKst_down_pipipi_Evts*Bs2DsDsstKKstEPDF_m_down_pipipi, nLb2DsDsstp_down_pipipi_Evts*Lb2DsDsstPEPDF_m_down_pipipi, nBd2DK_down_pipipi_Evts*Bd2DKEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi,nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nBs2DsDssKKst_up_pipipi_Evts*Bs2DsDsstKKstEPDF_m_up_pipipi, nLb2DsDsstp_up_pipipi_Evts*Lb2DsDsstPEPDF_m_up_pipipi, nBd2DK_up_pipipi_Evts*Bd2DKEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi, nLb2LcK_up_pipipi_Evts*Lb2LcKEPDF_m_up_pipipi, nLb2LcK_down_pipipi_Evts*Lb2LcKEPDF_m_down_pipipi)")
           pullname2TS = TString("h_combData_Cut[sample==sample::up_pipipi || sample==sample::down_pipipi]")
        else:
           print "Sample both, wrong mode!"
 
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
#    canvas = TCanvas( 'MassCanvas', 'Mass canvas', 1200, 800 )
#    canvas.SetTitle( 'Fit in mass' )
#    canvas.cd()
    
    frame_m = mass.frame()
    
    #frame_m.SetTitle( 'Fit in reconstructed %s mass' % bName )
    frame_m.SetTitle('')
    
    frame_m.GetXaxis().SetLabelSize( 0.05 )
    frame_m.GetYaxis().SetLabelSize( 0.05 )
    frame_m.GetXaxis().SetLabelFont( 132 )
    frame_m.GetYaxis().SetLabelFont( 132 )
    frame_m.GetXaxis().SetLabelOffset( 0.01 )
    frame_m.GetYaxis().SetLabelOffset( 0.01 )
    
    frame_m.GetXaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetNdivisions(5)
    
    frame_m.GetXaxis().SetTitleOffset( 0.95 )
    frame_m.GetYaxis().SetTitleOffset( 0.85 )
    frame_m.GetXaxis().SetTitle('#font[12]{m(B_{s} #rightarrow D_{s}K) [MeV/c^{2}]}')
    frame_m.GetYaxis().SetTitle('#font[12]{Events/(10.0 [MeV/c^{2}])}')
    
                                        
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS, mod )
    if plotData : plotDataSet( dataset, frame_m, sam, mod )
    

    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    pad1 =  TPad("pad1","pad1",0.01,0.21,0.99,0.99)
    pad2 =  TPad("pad2","pad2",0.01,0.01,0.99,0.20)
    pad1.Draw()
    pad2.Draw()

    legend = TLegend( 0.56, 0.35, 0.85, 0.85 )
    legend.SetTextSize(0.05)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    
    legend.SetHeader("LHCb Preliminary L_{int}=1fb^{-1}")
            ## Signal


#    l2 = TLine()
#    l2.SetLineColor(0)
#    l2.SetLineWidth(4)
#    #l1.SetLineStyle(kDashed)
#    legend.AddEntry(l2, "LHCb L_{int}=1fb^{-1}", "L")


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
    l1.SetLineColor(kRed-7)
    l1.SetLineWidth(4)
    l1.SetLineStyle(kDashed)
    legend.AddEntry(l1, "Signal B_{s}#rightarrow D_{s}K", "L")
                      

    h1=TH1F("Bs2DsDsstKKst","Bs2DsDsstKKst",5,0,1)
    h1.SetFillColor(kBlue-10)
    h1.SetFillStyle(1001)
    legend.AddEntry(h1, "B_{(d,s)}#rightarrow D^{(*)}_{s}K^{(*)}", "f")

    h2=TH1F("Bs2DsDsstPiRho","Bs2DsDsstPiRho",5,0,1)
    h2.SetFillColor(kBlue-6)
    h2.SetFillStyle(1001)
    legend.AddEntry(h2, "B_{s}#rightarrow D_{s}^{(*)}(#pi,#rho)", "f")
                
    h3=TH1F("Lb2DsDsstP","Lb2DsDsstP",5,0,1)
    h3.SetFillColor(kYellow-9)
    h3.SetFillStyle(1001)
    legend.AddEntry(h3, "#Lambda_{b} #rightarrow D_{s}^{(*)}p", "f")

    h6=TH1F("Lb2LcK","Lb2LcK",5,0,1)
    h6.SetFillColor(kGreen-3)
    h6.SetFillStyle(1001)
    legend.AddEntry(h6, "#Lambda_{b} #rightarrow #Lambda_{c}K", "f")
       
            
    h4=TH1F("BDK","BDK",5,0,1)
    h4.SetFillColor(kRed)
    h4.SetFillStyle(1001)
    legend.AddEntry(h4, "B_{d} #rightarrow DK", "f")

    h5=TH1F("Combinatorial","Combinatorial",5,0,1)
    h5.SetFillColor(kMagenta-2)
    h5.SetFillStyle(1001)
    legend.AddEntry(h5, "Combinatorial", "f")
                
             


    pad1.cd()
    frame_m.Draw()
    legend.Draw("same")
    pad1.Update()

    frame_m.Print("v")
    pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[FullPdf]")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    #pullHist.SetMaximum(5800.00)
    #pullHist.SetMinimum(5100.00)
    #pad2.cd()
    #pullHist.Draw("ap")
    axisX = pullHist.GetXaxis()
    axisX.Set(70,5100,5800)
    axisY = pullHist.GetYaxis()
    axisY.SetLabelSize(0.12)
    axisY.SetNdivisions(5)
    axisX.SetLabelSize(0.12)
            
    max = axisY.GetXmax()
    min = axisY.GetXmin()
    range = max-min
    zero = max/range
    print "max: %s, min: %s, range: %s, zero:%s"%(max,min,range,zero)
    #line = TLine(0.11,0.31,0.99,0.20)
    graph = TGraph(2)
    graph.SetMaximum(max)
    graph.SetMinimum(min)
    graph.SetPoint(1,5100,0)
    graph.SetPoint(2,5800,0)
    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    graph2.SetPoint(1,5100,-3)
    graph2.SetPoint(2,5800,-3)
    graph2.SetLineColor(kRed)
    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    graph3.SetPoint(1,5100,3)
    graph3.SetPoint(2,5800,3)
    graph3.SetLineColor(kRed)

    pullHist.SetTitle("")
    pullHist.GetXaxis().SetLabelFont( 132 )
    pullHist.GetYaxis().SetLabelFont( 132 )
        
    
    pad2.cd()
    pullHist.Draw("ap")
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
    
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
    canName = TString("mass_BsDsK_")+sam+TString("_")+mod+TString(".pdf")
    canvas.Print(canName.Data())
    canName = TString("mass_BsDsK_")+sam+TString("_")+mod+TString(".eps")
    canvas.Print(canName.Data())
    
#------------------------------------------------------------------------------
