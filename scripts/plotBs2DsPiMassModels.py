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
#------------------------------------------------------------------------------
def plotDataSet( dataset, frame, sample, mode, toy ) :

    bin = 70
    if sample == "both":
        if mode == "all":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi || sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi"),
                            RooFit.Binning( bin ) )
        elif mode == "kkpi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kkpi || sample==sample::down_kkpi"),
                            RooFit.Binning( bin ) )
        elif mode == "kpipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kpipi || sample==sample::down_kpipi"),
                            RooFit.Binning( bin ) )
        elif mode == "pipipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_pipipi || sample==sample::down_pipipi"),
                            RooFit.Binning( bin ) )
        else:
            print "[ERROR] Sample: both, wrong mode!"

    elif sample == "up":
        if mode == "all":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi"),
                            RooFit.Binning( bin ) )
        elif mode == "kkpi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kkpi"),
                            RooFit.Binning( bin ) )
        elif mode == "kpipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_kpipi"),
                            RooFit.Binning( bin ) )
        elif mode == "pipipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::up_pipipi"),
                            RooFit.Binning( bin ) )
        else:
            print "[ERROR] Sample: up, wrong mode!"
            
    elif sample == "down":
        if mode == "all":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi"),
                            RooFit.Binning( bin ) )
        elif mode == "kkpi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::down_kkpi"),
                            RooFit.Binning( bin ) )
        elif mode == "kpipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::down_kpipi"),
                            RooFit.Binning( bin ) )
        elif mode == "pipipi":
            dataset.plotOn( frame,
                            RooFit.Cut("sample==sample::down_pipipi"),
                            RooFit.Binning( bin ) )
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
                                                
            nameLam1 = TString("Lb2LcPiEPDF_m_up_")+mode1+p+TString("Lb2LcPiEPDF_m_down_")+mode1
            nameLam2 = TString("Lb2LcPiEPDF_m_up_")+mode2+p+TString("Lb2LcPiEPDF_m_down_")+mode2
            nameLam3 = TString("Lb2LcPiEPDF_m_up_")+mode3+p+TString("Lb2LcPiEPDF_m_down_")+mode3
            nameLam = nameLam1+p+nameLam2+p+nameLam3

            nameRho1 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode1+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode1
            nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode2+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode2
            nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode3+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode3
            nameRho = nameRho1+p+nameRho2+p+nameRho3

            nameBd1 = TString("Bd2DRhoEPDF_m_up_")+mode1+p+TString("Bd2DRhoEPDF_m_down_")+mode1
            nameBd2 = TString("Bd2DRhoEPDF_m_up_")+mode2+p+TString("Bd2DRhoEPDF_m_down_")+mode2
            nameBd3 = TString("Bd2DRhoEPDF_m_up_")+mode3+p+TString("Bd2DRhoEPDF_m_down_")+mode3

            nameBd4 = TString("Bd2DstPiEPDF_m_up_")+mode1+p+TString("Bd2DstPiEPDF_m_down_")+mode1
            nameBd5 = TString("Bd2DstPiEPDF_m_up_")+mode2+p+TString("Bd2DstPiEPDF_m_down_")+mode2
            nameBd6 = TString("Bd2DstPiEPDF_m_up_")+mode3+p+TString("Bd2DstPiEPDF_m_down_")+mode3
                            

            nameBd = nameBd1+p+nameBd2+p+nameBd3+p+nameBd4+p+nameBd5+p+nameBd6                                                

#            nameRho1 = TString("PhysBkgBs2DsRhoPdf_m_up_")+mode1+p+TString("PhysBkgBs2DsRhoPdf_m_down_")+mode1
#            nameRho2 = TString("PhysBkgBs2DsRhoPdf_m_up_")+mode2+p+TString("PhysBkgBs2DsRhoPdf_m_down_")+mode2
#            nameRho3 = TString("PhysBkgBs2DsRhoPdf_m_up_")+mode3+p+TString("PhysBkgBs2DsRhoPdf_m_down_")+mode3
#            nameRho = nameRho1+p+nameRho2+p+nameRho3

#            nameDsstPi1 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode1+p+TString("_m_down_")+mode1
#            nameDsstPi2 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode2+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode2
#            nameDsstPi3 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode3+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode3
#            nameDsstPi = nameDsstPi1+p+nameDsstPi2+p+nameDsstPi3
                                                

            nameDPi1  = TString("Bd2DPiEPDF_m_up_")+mode1+p+TString("Bd2DPiEPDF_m_down_")+mode1
            nameDPi2  = TString("Bd2DPiEPDF_m_up_")+mode2+p+TString("Bd2DPiEPDF_m_down_")+mode2
            nameDPi3  = TString("Bd2DPiEPDF_m_up_")+mode3+p+TString("Bd2DPiEPDF_m_down_")+mode3
            nameDPi  = nameDPi1+p+nameDPi2+p+nameDPi3

            nameBdDsPi1  = TString("Bd2DsPiEPDF_m_up_")+mode1+p+TString("Bd2DsPiEPDF_m_down_")+mode1
            nameBdDsPi2  = TString("Bd2DsPiEPDF_m_up_")+mode2+p+TString("Bd2DsPiEPDF_m_down_")+mode2
            nameBdDsPi3  = TString("Bd2DsPiEPDF_m_up_")+mode3+p+TString("Bd2DsPiEPDF_m_down_")+mode3
            nameBdDsPi  = nameBdDsPi1+p+nameBdDsPi2+p+nameBdDsPi3

            nameBdDsstPi1  = TString("Bd2DsstPiEPDF_m_up_")+mode1+p+TString("Bd2DsstPiEPDF_m_down_")+mode1
            nameBdDsstPi2  = TString("Bd2DsstPiEPDF_m_up_")+mode2+p+TString("Bd2DsstPiEPDF_m_down_")+mode2
            nameBdDsstPi3  = TString("Bd2DsstPiEPDF_m_up_")+mode3+p+TString("Bd2DsstPiEPDF_m_down_")+mode3
            nameBdDsstPi  = nameBdDsstPi1+p+nameBdDsstPi2+p+nameBdDsstPi3
                                    
                                               

        else:
            nameTot = TString("FullPdf")
            nameCom1 = TString("CombBkgEPDF_m_up_")+mode
            nameCom2 = TString("CombBkgEPDF_m_down_")+mode
            nameCom = nameCom1+p+nameCom2
            nameSig = TString("SigEPDF_up_")+mode+p+TString("SigEPDF_down_")+mode
            nameLam = TString("Lb2LcPiEPDF_m_up_")+mode+p+TString("Lb2LcPiEPDF_m_down_")+mode
            nameRho = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode
            nameDPi  = TString("Bd2DPiEPDF_m_up_")+mode+p+TString("Bd2DPiEPDF_m_down_")+mode
            nameBdDsPi  = TString("Bd2DsPiEPDF_m_up_")+mode+p+TString("Bd2DsPiEPDF_m_down_")+mode
            nameBd1 = TString("Bd2DRhoEPDF_m_up_")+mode+p+TString("Bd2DRhoEPDF_m_down_")+mode
            nameBd2 = TString("Bd2DstPiEPDF_m_up_")+mode+p+TString("Bd2DstPiEPDF_m_down_")+mode
            nameBdDsstPi = TString("Bd2DsstPiEPDF_m_up_")+mode+p+TString("Bd2DsstPiEPDF_m_down_")+mode
            nameBd = nameBd1+p+nameBd2
            
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

            nameLam1 = TString("Lb2LcPiEPDF_m_")+sam+t+TString("kkpi")
            nameLam2 = TString("Lb2LcPiEPDF_m_")+sam+t+TString("kpipi")
            nameLam3 = TString("Lb2LcPiEPDF_m_")+sam+t+TString("pipipi")
            nameLam = nameLam1+p+nameLam2+p+nameLam3

            nameRho1 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("kkpi")
            nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("kpipi")
            nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("pipipi")
            nameRho = nameRho1+p+nameRho2+p+nameRho3

#            nameRho1 = TString("")+sam+t+TString("kkpi")
#            nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("kpipi")
#            nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("pipipi")
#            nameRho = nameRho1+p+nameRho2+p+nameRho3



            nameDPi1  = TString("Bd2DPiEPDF_m_")+sam+t+TString("kkpi")
            nameDPi2  = TString("Bd2DPiEPDF_m_")+sam+t+TString("kpipi")
            nameDPi3  = TString("Bd2DPiEPDF_m_")+sam+t+TString("pipipi")
            nameDPi  = nameDPi1+p+nameDPi2+p+nameDPi3

            nameBdDsPi1  = TString("Bd2DsPiEPDF_m_")+sam+t+TString("kkpi")
            nameBdDsPi2  = TString("Bd2DsPiEPDF_m_")+sam+t+TString("kpipi")
            nameBdDsPi3  = TString("Bd2DsPiEPDF_m_")+sam+t+TString("pipipi")
            nameBdDsPi  = nameBdDsPi1+p+nameBdDsPi2+p+nameBdDsPi3

            nameBdDsstPi1  = TString("Bd2DsstPiEPDF_m_")+sam+t+TString("kkpi")
            nameBdDsstPi2  = TString("Bd2DsstPiEPDF_m_")+sam+t+TString("kpipi")
            nameBdDsstPi3  = TString("Bd2DsstPiEPDF_m_")+sam+t+TString("pipipi")
            nameBdDsstPi  = nameBdDsstPi1+p+nameBdDsstPi2+p+nameBdDsstPi3
                                                

            nameBd1  = TString("Bd2DstPiEPDF_m_")+sam+t+TString("kkpi")
            nameBd2  = TString("Bd2DstPiEPDF_m_")+sam+t+TString("kpipi")
            nameBd3  = TString("Bd2DstPiEPDF_m_")+sam+t+TString("pipipi")

            nameBd4  = TString("Bd2DRhoEPDF_m_")+sam+t+TString("kkpi")
            nameBd5  = TString("Bd2DRhoEPDF_m_")+sam+t+TString("kpipi")
            nameBd6  = TString("Bd2DRhoEPDF_m_")+sam+t+TString("pipipi")
                                    

            nameBd  = nameBd1+p+nameBd2+p+nameBd3+p+nameBd4+p+nameBd5+p+nameBd6
                                                
                                                
        
        else:
            nameTot = TString("FullPdf")
            nameCom = TString("CombBkgEPDF_m_")+sam+t+mode
            nameSig = TString("SigEPDF_")+sam+t+mode
            nameLam = TString("Lb2LcPiEPDF_m_")+sam+t+mode
            nameRho = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+mode
            nameDPi  = TString("Bd2DPiEPDF_m_")+sam+t+mode
            nameBdDsPi  = TString("Bd2DsPiEPDF_m_")+sam+t+mode
            nameBd1  = TString("Bd2DstPiEPDF_m_")+sam+t+mode
            nameBd2  = TString("Bd2DRhoEPDF_m_")+sam+t+mode
            nameBd = nameBd1+p+nameBd2
            nameBdDsstPi  = TString("Bd2DsstPiEPDF_m_")+sam+t+mode
                                                        
    #p=TString(",")
    
    #p=TString(",")
    nameComDPi = nameCom+p+nameDPi
    nameComDPiRho = nameComDPi+p+nameBd+p+nameBdDsstPi+p+nameBdDsPi
    nameComDPiLam = nameComDPi+p+nameLam
    nameAll = nameComDPiRho+p+nameRho
#    nameTot = nameAll+p+nameSig+p+nameLam
    #nameAll = nameComDPiLamDsstPi+p+nameBdDPi
                        

                
    model.plotOn( frame,
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kBlue),
                 # RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components(nameAll.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-10),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    #model.plotOn( frame,
    #              RooFit.Components(nameComDPiLamDsstPi.Data()),
    #              RooFit.DrawOption("F"),
    #              RooFit.FillStyle(1001),
    #              RooFit.FillColor(kBlue-10),
    #              RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
    #              )

    model.plotOn( frame,
                  RooFit.Components(nameComDPiRho.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kMagenta-2),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components(nameComDPiLam.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kRed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components(nameComDPi.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kOrange),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components(nameCom.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-6),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    model.plotOn( frame,
                  RooFit.Components(nameSig.Data()),
                  RooFit.LineColor(kRed-7),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
                        
#    model.paramOn( frame,
#
#RooFit.Layout( 0.56, 0.90, 0.85 ),
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
    
    from ROOT import TFile, TCanvas, gROOT, TLegend, TString, TLine, TH1F, TBox, TPad, TGraph, TMarker, TGraphErrors, TLatex
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
    mass.setMax(5800)
    mean  = 5366
    #mass = RooRealVar( 'mass', '%s mass' % bName, mean, 5000, 5800, 'MeV/c^{2}' )
    sam = TString(options.sample)
    mod = TString(options.mode)
    ty = TString("ToyNo")
    if options.toy : ty = TString("ToyYes")  
    w.Print('v')
    #exit(0)
        
       
    #dataName = TString("combData")


    if sam == "up":
        if mod == "all":
            print "Sample up, mode all"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nLb2LcPi_up_kkpi_Evts*Lb2LcPiEPDF_m_up_kkpi, nBd2DPi_up_kkpi_Evts*Bd2DPiEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi, nBd2DsPi_up_kkpi_Evts*Bd2DsPiEPDF_m_up_kkpi, nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nLb2LcPi_up_kpipi_Evts*Lb2LcPiEPDF_m_up_kpipi, nBd2DPi_up_kpipi_Evts*Bd2DPiEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi, nBd2DsPi_up_kpipi_Evts*Bd2DsPiEPDF_m_up_kpipi,nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nLb2LcPi_up_pipipi_Evts*Lb2LcPiEPDF_m_up_pipipi, nBd2DPi_up_pipipi_Evts*Bd2DPiEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi,nBd2DsPi_up_pipipi_Evts*Bd2DsPiEPDF_m_up_pipipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi]")
            
        elif mod == "kkpi":
            print "Sample up, mode kkpi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi,nLb2LcPi_up_kkpi_Evts*Lb2LcPiEPDF_m_up_kkpi, nBd2DPi_up_kkpi_Evts*Bd2DPiEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi, nBd2DsPi_up_kkpi_Evts*Bd2DsPiEPDF_m_up_kkpi,nBd2DRho_up_kkpi_Evts*Bd2DRhoEPDF_m_up_kkpi,nBd2DstPi_up_kkpi_Evts*Bd2DstPiEPDF_m_up_kkpi,nBd2DsstPi_up_kkpi_Evts*Bd2DsstPiEPDF_m_up_kkpi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi]")
            
        elif mod == "kpipi":        
            print "Sample up, mode kpipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nLb2LcPi_up_kpipi_Evts*Lb2LcPiEPDF_m_up_kpipi, nBd2DPi_up_kpipi_Evts*Bd2DPiEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi, nBd2DsPi_up_kpipi_Evts*Bd2DsPiEPDF_m_up_kpipi,nBd2DRho_up_kpipi_Evts*Bd2DRhoEPDF_m_up_kpipi,nBd2DstPi_up_kpipi_Evts*Bd2DstPiEPDF_m_up_kpipi,nBd2DsstPi_up_kpipi_Evts*Bd2DsstPiEPDF_m_up_kpipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kpipi]")
            
        elif mod == "pipipi":
            print "Sample up, mode pipipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nLb2LcPi_up_pipipi_Evts*Lb2LcPiEPDF_m_up_pipipi, nBd2DPi_up_pipipi_Evts*Bd2DPiEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi, nBd2DsPi_up_pipipi_Evts*Bd2DsPiEPDF_m_up_pipipi,nBd2DsstPi_up_pipipi_Evts*Bd2DsstPiEPDF_m_up_pipipi,nBd2DRho_up_pipipi_Evts*Bd2DRhoEPDF_m_up_pipipi,nBd2DstPi_up_pipipi_Evts*Bd2DstPiEPDF_m_up_pipipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_pipipi]")
            
        else:
            print "[ERROR] Wrong mode"
    elif sam == "down":
        if mod == "all":
            print "Sample down, mode all"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nLb2LcPi_down_kkpi_Evts*Lb2LcPiEPDF_m_down_kkpi, nBd2DPi_down_kkpi_Evts*Bd2DPiEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi, nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nLb2LcPi_down_kpipi_Evts*Lb2LcPiEPDF_m_down_kpipi, nBd2DPi_down_kpipi_Evts*Bd2DPiEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi,nBd2DsPi_down_kpipi_Evts*Bd2DsPiEPDF_m_down_kpipi, nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nLb2LcPi_down_pipipi_Evts*Lb2LcPiEPDF_m_down_pipipi, nBd2DPi_down_pipipi_Evts*Bd2DPiEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi, nBd2DsPi_down_pipipi_Evts*Bd2DsPiEPDF_m_down_pipipi )")
            pullname2TS = TString("h_combData_Cut[sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi]")
        elif mod == "kkpi":
            print "Sample down, mode kkpi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nLb2LcPi_down_kkpi_Evts*Lb2LcPiEPDF_m_down_kkpi, nBd2DPi_down_kkpi_Evts*Bd2DPiEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi,nBd2DRho_down_kkpi_Evts*Bd2DRhoEPDF_m_down_kkpi, nBd2DstPi_down_kkpi_Evts*Bd2DstPiEPDF_m_down_kkpi,nBd2DsstPi_down_kkpi_Evts*Bd2DsstPiEPDF_m_down_kkpi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::down_kkpi]")

        elif mod == "kpipi":
            print "Sample down, mode kpipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nLb2LcPi_down_kpipi_Evts*Lb2LcPiEPDF_m_down_kpipi, nBd2DPi_down_kpipi_Evts*Bd2DPiEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi, nBd2DsPi_down_kpipi_Evts*Bd2DsPiEPDF_m_down_kpipi,nBd2DRho_down_kpipi_Evts*Bd2DRhoEPDF_m_down_kpipi, nBd2DstPi_down_kpipi_Evts*Bd2DstPiEPDF_m_down_kpipi,nBd2DsstPi_down_kpipi_Evts*Bd2DsstPiEPDF_m_down_kpipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::down_kpipi]")
            
        elif mod == "pipipi":
            print "Sample down, mode pipipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nLb2LcPi_down_pipipi_Evts*Lb2LcPiEPDF_m_down_pipipi, nBd2DPi_down_pipipi_Evts*Bd2DPiEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi,nBd2DsPi_down_pipipi_Evts*Bd2DsPiEPDF_m_down_pipipi, nBd2DRho_down_pipipi_Evts*Bd2DRhoEPDF_m_down_pipipi, nBd2DstPi_down_pipipi_Evts*Bd2DstPiEPDF_m_down_pipipi,nBd2DsstPi_down_pipipi_Evts*Bd2DsstPiEPDF_m_down_pipipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::down_pipipi]")
        else:
            print "[ERROR] Wrong mode"
    elif sam == "both":
        if mod == "all":
            print "Sample both, mode all"
            w.factory("SUM:FullPdf1(nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nLb2LcPi_up_kkpi_Evts*Lb2LcPiEPDF_m_up_kkpi, nBd2DPi_up_kkpi_Evts*Bd2DPiEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi, nBd2DsPi_up_kkpi_Evts*Bd2DsPiEPDF_m_up_kkpi,nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nLb2LcPi_up_kpipi_Evts*Lb2LcPiEPDF_m_up_kpipi, nBd2DPi_up_kpipi_Evts*Bd2DPiEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi,nBd2DsPi_up_kpipi_Evts*Bd2DsPiEPDF_m_up_kpipi, nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nLb2LcPi_up_pipipi_Evts*Lb2LcPiEPDF_m_up_pipipi, nBd2DPi_up_pipipi_Evts*Bd2DPiEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi,nBd2DsPi_up_pipipi_Evts*Bd2DsPiEPDF_m_up_pipipi)")

            w.factory("SUM:FullPdf1a(nBd2DstPi_up_kkpi_Evts*Bd2DstPiEPDF_m_up_kkpi,nBd2DstPi_up_kpipi_Evts*Bd2DstPiEPDF_m_up_kpipi,nBd2DstPi_up_pipipi_Evts*Bd2DstPiEPDF_m_up_pipipi,nBd2DRho_up_kkpi_Evts*Bd2DRhoEPDF_m_up_kkpi,nBd2DRho_up_kpipi_Evts*Bd2DRhoEPDF_m_up_kpipi,nBd2DRho_up_pipipi_Evts*Bd2DRhoEPDF_m_up_pipipi,nBd2DsstPi_up_kkpi_Evts*Bd2DsstPiEPDF_m_up_kkpi,nBd2DsstPi_up_kpipi_Evts*Bd2DsstPiEPDF_m_up_kpipi,nBd2DsstPi_up_pipipi_Evts*Bd2DsstPiEPDF_m_up_pipipi)")
            
            w.factory("SUM:FullPdf2(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nLb2LcPi_down_kkpi_Evts*Lb2LcPiEPDF_m_down_kkpi, nBd2DPi_down_kkpi_Evts*Bd2DPiEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi,nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nLb2LcPi_down_kpipi_Evts*Lb2LcPiEPDF_m_down_kpipi, nBd2DPi_down_kpipi_Evts*Bd2DPiEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi, nBd2DsPi_down_kpipi_Evts*Bd2DsPiEPDF_m_down_kpipi, nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nLb2LcPi_down_pipipi_Evts*Lb2LcPiEPDF_m_down_pipipi, nBd2DPi_down_pipipi_Evts*Bd2DPiEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi,nBd2DsPi_down_pipipi_Evts*Bd2DsPiEPDF_m_down_pipipi)")

            w.factory("SUM:FullPdf2a(nBd2DstPi_down_kkpi_Evts*Bd2DstPiEPDF_m_down_kkpi,nBd2DstPi_down_kpipi_Evts*Bd2DstPiEPDF_m_down_kpipi,nBd2DstPi_down_pipipi_Evts*Bd2DstPiEPDF_m_down_pipipi,nBd2DRho_down_kkpi_Evts*Bd2DRhoEPDF_m_down_kkpi,nBd2DRho_down_kpipi_Evts*Bd2DRhoEPDF_m_down_kpipi,nBd2DRho_down_pipipi_Evts*Bd2DRhoEPDF_m_down_pipipi,nBd2DsstPi_down_kkpi_Evts*Bd2DsstPiEPDF_m_down_kkpi,nBd2DsstPi_down_kpipi_Evts*Bd2DsstPiEPDF_m_down_kpipi,nBd2DsstPi_down_pipipi_Evts*Bd2DsstPiEPDF_m_down_pipipi)")

            
            w.factory("EXPR::N_up('nBs2DsDsstPiRho_up_kkpi_Evts+nBd2DsPi_up_kkpi_Evts+nLb2LcPi_up_kkpi_Evts+nBd2DPi_up_kkpi_Evts+nSig_up_kkpi_Evts+nCombBkg_up_kkpi_Evts+nBs2DsDsstPiRho_up_kpipi_Evts+nBd2DsPi_up_kpipi_Evts+nLb2LcPi_up_kpipi_Evts+nBd2DPi_up_kpipi_Evts+nSig_up_kpipi_Evts+nCombBkg_up_kpipi_Evts+nBs2DsDsstPiRho_up_pipipi_Evts+nBd2DsPi_up_pipipi_Evts+nLb2LcPi_up_pipipi_Evts+nBd2DPi_up_pipipi_Evts+nSig_up_pipipi_Evts+nCombBkg_up_pipipi_Evts',nBs2DsDsstPiRho_up_kkpi_Evts,nBd2DsPi_up_kkpi_Evts,nLb2LcPi_up_kkpi_Evts,nBd2DPi_up_kkpi_Evts,nSig_up_kkpi_Evts,nCombBkg_up_kkpi_Evts,nBs2DsDsstPiRho_up_kpipi_Evts,nBd2DsPi_up_kpipi_Evts,nLb2LcPi_up_kpipi_Evts,nBd2DPi_up_kpipi_Evts,nSig_up_kpipi_Evts,nCombBkg_up_kpipi_Evts,nBs2DsDsstPiRho_up_pipipi_Evts,nBd2DsPi_up_pipipi_Evts,nLb2LcPi_up_pipipi_Evts,nBd2DPi_up_pipipi_Evts,nSig_up_pipipi_Evts,nCombBkg_up_pipipi_Evts)")

            w.factory("EXPR::N_up1a('nBd2DRho_up_kkpi_Evts+nBd2DRho_up_kpipi_Evts+nBd2DRho_up_pipipi_Evts+nBd2DstPi_up_kkpi_Evts+nBd2DstPi_up_kpipi_Evts+nBd2DstPi_up_pipipi_Evts+nBd2DsstPi_up_kkpi_Evts+nBd2DsstPi_up_kpipi_Evts+nBd2DsstPi_up_pipipi_Evts',nBd2DRho_up_kkpi_Evts,nBd2DRho_up_kpipi_Evts,nBd2DRho_up_pipipi_Evts,nBd2DstPi_up_kkpi_Evts,nBd2DstPi_up_kpipi_Evts,nBd2DstPi_up_pipipi_Evts,nBd2DsstPi_up_kkpi_Evts,nBd2DsstPi_up_kpipi_Evts,nBd2DsstPi_up_pipipi_Evts)")

            w.factory("EXPR::N_dw('nBs2DsDsstPiRho_down_kkpi_Evts+nBd2DsPi_down_kkpi_Evts+nLb2LcPi_down_kkpi_Evts+nBd2DPi_down_kkpi_Evts+nSig_down_kkpi_Evts+nCombBkg_down_kkpi_Evts+nBs2DsDsstPiRho_down_kpipi_Evts+nBd2DsPi_down_kpipi_Evts+nLb2LcPi_down_kpipi_Evts+nBd2DPi_down_kpipi_Evts+nSig_down_kpipi_Evts+nCombBkg_down_kpipi_Evts+nBs2DsDsstPiRho_down_pipipi_Evts+nBd2DsPi_down_pipipi_Evts+nLb2LcPi_down_pipipi_Evts+nBd2DPi_down_pipipi_Evts+nSig_down_pipipi_Evts+nCombBkg_down_pipipi_Evts',nBs2DsDsstPiRho_down_kkpi_Evts,nBd2DsPi_down_kkpi_Evts,nLb2LcPi_down_kkpi_Evts,nBd2DPi_down_kkpi_Evts,nSig_down_kkpi_Evts,nCombBkg_down_kkpi_Evts,nBs2DsDsstPiRho_down_kpipi_Evts,nBd2DsPi_down_kpipi_Evts,nLb2LcPi_down_kpipi_Evts,nBd2DPi_down_kpipi_Evts,nSig_down_kpipi_Evts,nCombBkg_down_kpipi_Evts,nBs2DsDsstPiRho_down_pipipi_Evts,nBd2DsPi_down_pipipi_Evts,nLb2LcPi_down_pipipi_Evts,nBd2DPi_down_pipipi_Evts,nSig_down_pipipi_Evts,nCombBkg_down_pipipi_Evts)")

            w.factory("EXPR::N_dw2a('nBd2DRho_down_kkpi_Evts+nBd2DRho_down_kpipi_Evts+nBd2DRho_down_pipipi_Evts+nBd2DstPi_down_kkpi_Evts+nBd2DstPi_down_kpipi_Evts+nBd2DstPi_down_pipipi_Evts+nBd2DsstPi_down_kkpi_Evts+nBd2DsstPi_down_kpipi_Evts+nBd2DsstPi_down_pipipi_Evts',nBd2DRho_down_kkpi_Evts,nBd2DRho_down_kpipi_Evts,nBd2DRho_down_pipipi_Evts,nBd2DstPi_down_kkpi_Evts,nBd2DstPi_down_kpipi_Evts,nBd2DstPi_down_pipipi_Evts,nBd2DsstPi_down_kkpi_Evts,nBd2DsstPi_down_kpipi_Evts,nBd2DsstPi_down_pipipi_Evts)")
            
            #w.factory("EXPR::Fulldw('Bd2DRhoEPDF_m_down_kkpi+Bd2DRhoEPDF_m_down_kpipi+Bd2DRhoEPDF_m_down_pipipi+Bd2DstPiEPDF_m_down_kkpi+Bd2DstPiEPDF_m_down_kpipi+Bd2DstPiEPDF_m_down_pipipi+Bd2DsstPiEPDF_m_down_kkpi+Bd2DsstPiEPDF_down_kpipi+Bd2DsstPiEPDF_m_down_pipipi',Bd2DRhoEPDF_m_down_kkpi,Bd2DRhoEPDF_m_down_kpipi,Bd2DRhoEPDF_m_down_pipipi,Bd2DstPiEPDF_m_down_kkpi,Bd2DstPiEPDF_m_down_kpipi, Bd2DstPiEPDF_m_down_pipipi,Bd2DsstPiEPDF_m_down_kkpi,Bd2DsstPiEPDF_m_down_kpipi,Bd2DsstPiEPDF_m_down_pipipi)")


            w.factory("SUM:FullPdf(N_up*FullPdf1,N_dw*FullPdf2, N_up1a*FullPdf1a, N_dw2a*FullPdf2a)")
            #w.factory("SUM:FullPdf(N_up*FullPdf1,N_dw*FullPdf2, N_up1a*FullPdf1a, N_dw2a*Fulldw)")
                        
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi || sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi]")


        elif mod == "kkpi":
            print "Sample both, mode kkpi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nLb2LcPi_down_kkpi_Evts*Lb2LcPiEPDF_m_down_kkpi, nBd2DPi_down_kkpi_Evts*Bd2DPiEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi, nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nLb2LcPi_up_kkpi_Evts*Lb2LcPiEPDF_m_up_kkpi, nBd2DPi_up_kkpi_Evts*Bd2DPiEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi,nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi, nBd2DstPi_down_kkpi_Evts*Bd2DstPiEPDF_m_down_kkpi, nBd2DRho_down_kkpi_Evts*Bd2DRhoEPDF_m_down_kkpi,nBd2DstPi_up_kkpi_Evts*Bd2DstPiEPDF_m_up_kkpi, nBd2DRho_up_kkpi_Evts*Bd2DRhoEPDF_m_up_kkpi,nBd2DsstPi_up_kkpi_Evts*Bd2DsstPiEPDF_m_up_kkpi,nBd2DsstPi_down_kkpi_Evts*Bd2DsstPiEPDF_m_down_kkpi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi || sample==sample::down_kkpi]")


        elif  mod == "kpipi":
            print "Sample both, mode kpipi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nLb2LcPi_down_kpipi_Evts*Lb2LcPiEPDF_m_down_kpipi, nBd2DPi_down_kpipi_Evts*Bd2DPiEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi, nBd2DsPi_up_kpipi_Evts*Bd2DsPiEPDF_m_up_kpipi, nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nLb2LcPi_up_kpipi_Evts*Lb2LcPiEPDF_m_up_kpipi, nBd2DPi_up_kpipi_Evts*Bd2DPiEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi, nBd2DsPi_down_kpipi_Evts*Bd2DsPiEPDF_m_down_kpipi,nBd2DstPi_down_kpipi_Evts*Bd2DstPiEPDF_m_down_kpipi, nBd2DRho_down_kpipi_Evts*Bd2DRhoEPDF_m_down_kpipi,nBd2DstPi_up_kpipi_Evts*Bd2DstPiEPDF_m_up_kpipi, nBd2DRho_up_kpipi_Evts*Bd2DRhoEPDF_m_up_kpipi,nBd2DsstPi_up_kpipi_Evts*Bd2DsstPiEPDF_m_up_kpipi,nBd2DsstPi_down_kpipi_Evts*Bd2DsstPiEPDF_m_down_kpipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kpipi || sample==sample::down_kpipi]")
            

        elif  mod == "pipipi":
           print "Sample both, mode kpipi"
           w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nLb2LcPi_down_pipipi_Evts*Lb2LcPiEPDF_m_down_pipipi, nBd2DPi_down_pipipi_Evts*Bd2DPiEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi, nBd2DsPi_down_pipipi_Evts*Bd2DsPiEPDF_m_down_pipipi, nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nLb2LcPi_up_pipipi_Evts*Lb2LcPiEPDF_m_up_pipipi, nBd2DPi_up_pipipi_Evts*Bd2DPiEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi,nBd2DsPi_up_pipipi_Evts*Bd2DsPiEPDF_m_up_pipipi,nBd2DstPi_down_pipipi_Evts*Bd2DstPiEPDF_m_down_pipipi,nBd2DRho_down_pipipi_Evts*Bd2DRhoEPDF_m_down_pipipi,nBd2DstPi_up_pipipi_Evts*Bd2DstPiEPDF_m_up_pipipi, nBd2DRho_up_pipipi_Evts*Bd2DRhoEPDF_m_up_pipipi,nBd2DsstPi_up_pipipi_Evts*Bd2DsstPiEPDF_m_up_pipipi,nBd2DsstPi_down_pipipi_Evts*Bd2DsstPiEPDF_m_down_pipipi)")
           pullname2TS = TString("h_combData_Cut[sample==sample::up_pipipi || sample==sample::down_pipipi]")
        else:
           print "Sample both, wrong mode!"
 
    else:
        print "[ERROR] Wrong sample"
        exit(0)

    dataName = TString("combData")
#    dataName = TString("TotEPDF_mup_kkpiData")
    totName = TString("FullPdf")
    modelPDF = w.pdf( totName.Data() )
    dataset = w.data( dataName.Data() )
            
    if not ( modelPDF and dataset ) :
        print "Cos sie zepsulo?"
        w.Print( 'v' )
        exit( 0 )
   # w.Print('v')
   # exit(0)
#    canvas = TCanvas( 'MassCanvas', 'Mass canvas', 1200, 800 )
#    canvas.SetTitle( 'Fit in mass' )
#    canvas.cd()
    
    frame_m = mass.frame(100)
    
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
    frame_m.GetXaxis().SetTitle('#font[12]{m(B_{s} #rightarrow D_{s}#pi) [MeV/c^{2}]}')
    frame_m.GetYaxis().SetTitle('#font[12]{Events/(10.0 [MeV/c^{2}])}')
           
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS, mod )
    if plotData : plotDataSet( dataset, frame_m, sam, mod, ty )
    

    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    pad1 =  TPad("pad1","pad1",0.01,0.21,0.99,0.99)
    pad2 =  TPad("pad2","pad2",0.01,0.01,0.99,0.18)
    #pad1.SetFillStyle(4000)
    #pad2.SetFillStyle(4000)
    pad1.Draw()
    pad2.Draw()

    legend = TLegend( 0.56, 0.30, 0.85, 0.80 )
    legend.SetTextSize(0.06)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    legend.SetHeader("LHCb Preliminary L_{int}=1.0 fb^{-1}")
                    
          
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
    legend.AddEntry(l1, "Signal B_{s}#rightarrow D_{s}#pi", "L")
                    

    h1=TH1F("Bs2DsDsstPiRho","Bs2DsDsstPiRho",5,0,1)
    h1.SetFillColor(kBlue-10)
    h1.SetFillStyle(1001)
    legend.AddEntry(h1, "B_{s}#rightarrow D_{s}^{(*)}(#pi,#rho)", "f")

    h2=TH1F("B2DPi","B2DPi",5,0,1)
    h2.SetFillColor(kOrange-2)
    h2.SetFillStyle(1001)
    legend.AddEntry(h2, "B_{d}#rightarrow D#pi", "f")
                
    h3=TH1F("Lb2LcPi","Lb2LcPi",5,0,1)
    h3.SetFillColor(kRed)
    h3.SetFillStyle(1001)
    legend.AddEntry(h3, "#Lambda_{b}#rightarrow #Lambda_{c}#pi", "f")
                
    h4=TH1F("B2DsDsstPiRho","B2DsDsstPiRho",5,0,1)
    h4.SetFillColor(kMagenta-2)
    h4.SetFillStyle(1001)
    legend.AddEntry(h4, "B_{d}#rightarrow D_{(s)}^{(*)}(#pi,#rho)", "f")
                 
    h5=TH1F("Combinatorial","Combinatorial",5,0,1)
    h5.SetFillColor(kBlue-6)
    h5.SetFillStyle(1001)
    legend.AddEntry(h5, "Combinatorial", "f")
            


    pad1.cd()
    frame_m.Draw()
    legend.Draw("same")
    pad1.Update()

#    Blabla = "CombBkgEPDF_m_up_kkpi,CombBkgEPDF_m_down_kkpi,CombBkgEPDF_m_up_kpipi,CombBkgEPDF_m_down_kpipi,CombBkgEPDF_m_up_pipipi,CombBkgEPDF_m_down_pipipi,Bd2DPiEPDF_m_up_kkpi,Bd2DPiEPDF_m_down_kkpi,Bd2DPiEPDF_m_up_kpipi,Bd2DPiEPDF_m_down_kpipi,Bd2DPiEPDF_m_up_pipipi,Bd2DPiEPDF_m_down_pipipi,Bd2DRhoEPDF_m_up_kkpi,Bd2DRhoEPDF_m_down_kkpi,Bd2DRhoEPDF_m_up_kpipi,Bd2DRhoEPDF_m_down_kpipi,Bd2DRhoEPDF_m_up_pipipi,Bd2DRhoEPDF_m_down_pipipi,Bd2DstPiEPDF_m_up_kkpi,Bd2DstPiEPDF_m_down_kkpi,Bd2DstPiEPDF_m_up_kpipi,Bd2DstPiEPDF_m_down_kpipi,Bd2DstPiEPDF_m_up_pipipi,Bd2DstPiEPDF_m_down_pipipi,Bd2DsstPiEPDF_m_up_kkpi,Bd2DsstPiEPDF_m_down_kkpi,Bd2DsstPiEPDF_m_up_kpipi,Bd2DsstPiEPDF_m_down_kpipi,Bd2DsstPiEPDF_m_up_pipipi,Bd2DsstPiEPDF_m_down_pipipi,Bd2DsPiEPDF_m_up_kkpi,Bd2DsPiEPDF_m_down_kkpi,Bd2DsPiEPDF_m_up_kpipi,Bd2DsPiEPDF_m_down_kpipi,Bd2DsPiEPDF_m_up_pipipi,Bd2DsPiEPDF_m_down_pipipi,Bs2DsDsstPiRhoEPDF_m_up_kkpi,Bs2DsDsstPiRhoEPDF_m_down_kkpi,Bs2DsDsstPiRhoEPDF_m_up_kpipi,Bs2DsDsstPiRhoEPDF_m_down_kpipi,Bs2DsDsstPiRhoEPDF_m_up_pipipi,Bs2DsDsstPiRhoEPDF_m_down_pipipi,SigEPDF_up_kkpi,SigEPDF_down_kkpi,SigEPDF_up_kpipi,SigEPDF_down_kpipi,SigEPDF_up_pipipi,SigEPDF_down_pipipi,Lb2LcPiEPDF_m_up_kkpi,Lb2LcPiEPDF_m_down_kkpi,Lb2LcPiEPDF_m_up_kpipi,Lb2LcPiEPDF_m_down_kpipi,Lb2LcPiEPDF_m_up_pipipi,Lb2LcPiEPDF_m_down_pipipi"
    Blabla = "FullPdf"

    #pullname2TS = TString("h_TotEPDF_mup_kkpiData")

    frame_m.Print("v")
    
    pullnameTS = TString("FullPdf_Norm[")+mVarTS+TString("]_Comp[")+Blabla+TString("]")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
#    pullHist  = frame_m.pullHist()
#    pullHist.SetMaximum(5800.00)
#    pullHist.SetMinimum(5100.00)
    axisX = pullHist.GetXaxis()
    axisX.Set(100,5100,5800)
    axisY = pullHist.GetYaxis()
    max = axisY.GetXmax()
    min = axisY.GetXmin()
    axisY.SetLabelSize(0.12)
    axisY.SetNdivisions(5)
    
    axisX.SetLabelSize(0.12)        

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


    pullHist.GetXaxis().SetLabelFont( 132 )
    pullHist.GetYaxis().SetLabelFont( 132 )
        
    pullHist.SetTitle("")
    #pullHist.GetXaxis().SetLabelSize( 0.12 )
    #pullHist.GetXaxis().SetTitleSize( 0.06 )
    #pullHist.GetXaxis().SetTitleOffset( 1.2 )
    #pullHist.GetXaxis().SetTitle('#font[12]{m(B_{s} #rightarrow D_{s}#pi) [MeV/c^{2}]}')
    #size = pullHist.GetXaxis().GetTitleSize()
    #print size

    #tex = TLatex()
    #tex.SetTextSize(0.12)

    pad2.cd()
    pullHist.Draw("ap")
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
    #tex.DrawLatex(0.50,0.30,"m(B_{s} #rightarrow D_{s}#pi) [MeV/c^{2}]")
         
    #line.Draw()
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
        canName = TString("mass_BsDsPi_ToyMC_")+sam+TString("_")+mod+TString(".pdf")
        canNameEps = TString("mass_BsDsPi_ToyMC_")+sam+TString("_")+mod+TString(".eps") 
    else:
        canName = TString("mass_BsDsPi_")+sam+TString("_")+mod+TString(".pdf")
        canNameEps = TString("mass_BsDsPi_")+sam+TString("_")+mod+TString(".eps")
    canvas.Print(canName.Data())
    canvas.Print(canNameEps.Data())
    
#------------------------------------------------------------------------------
