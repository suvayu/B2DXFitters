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
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from os.path  import exists

import GaudiPython
GaudiPython.loaddict( 'B2DXFittersDict' )
from ROOT import *
from ROOT import RooCruijff

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True
bName = 'B_{s}'

massBs_dw  = 5300
massBs_up  = 5800

massDs_dw = 1930
massDs_up = 2015 

PIDK_dw = 0.0
PIDK_up = 150.0
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

#------------------------------------------------------------------------------
def plotDataSet( dataset, frame, sample, mode, toy, merge, Bin ) :

    
    if sample == "both":
        if merge:
            if mode == "all":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_nonres || sample==sample::both_phipi || sample==sample::both_kstk || sample==sample::both_kpipi || sample==sample::both_pipipi"),
                                RooFit.Binning( Bin ) )
            elif mode =="3modeskkpi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_nonres || sample==sample::both_phipi || sample==sample::both_kstk"),
                                RooFit.Binning( Bin ) )
            elif mode =="3modes":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_kkpi || sample==sample::both_kpipi || sample==sample::both_pipipi"),
                                RooFit.Binning( Bin ) )
            elif mode == "nonres":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_nonres"),
                                RooFit.Binning( Bin) )
            elif mode == "phipi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_phipi"),
                                RooFit.Binning( Bin ) )
            elif mode == "kstk":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_kstk"),
                                RooFit.Binning( Bin ) )
                
            elif mode == "kkpi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_kkpi"),
                                RooFit.Binning( Bin ) )
            elif mode == "kpipi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_kpipi"),
                                RooFit.Binning( Bin ) )
            elif mode == "pipipi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_pipipi"),
                                RooFit.Binning( Bin ) )
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
def plotFitModel( model, frame, sam, var, mode, merge) :
    #if debug :
    
    print "model"    
    model.Print( 't' )

    print "frame"
    frame.Print( 'v' )
    t=TString("_")
    p=TString(",")
    if sam == "both":
        if merge:
            if mode =="all":
                print "all"
                nameTot = TString("FullPdf")
                
                mode1 = TString("nonres")
                mode2 = TString("phipi")
                mode3 = TString("kstk")
                mode4 = TString("kpipi")
                mode5 = TString("pipipi")

                nameCom1 =TString("CombBkgEPDF_m_both_")+mode1
                nameCom2 =TString("CombBkgEPDF_m_both_")+mode2
                nameCom3 =TString("CombBkgEPDF_m_both_")+mode3
                nameCom4 =TString("CombBkgEPDF_m_both_")+mode4
                nameCom5 =TString("CombBkgEPDF_m_both_")+mode5
                                
                nameCom = nameCom1+p+nameCom2+p+nameCom3+p+nameCom4+p+nameCom5
                                                               
                nameSig1 = TString("SigEPDF_both_")+mode1
                nameSig2 = TString("SigEPDF_both_")+mode2
                nameSig3 = TString("SigEPDF_both_")+mode3
                nameSig4 = TString("SigEPDF_both_")+mode4
                nameSig5 = TString("SigEPDF_both_")+mode5
                nameSig = nameSig1+p+nameSig2+p+nameSig3+p+nameSig4+p+nameSig5
                
                nameLam1 = TString("Lb2LcPiEPDF_m_both_")+mode1
                nameLam2 = TString("Lb2LcPiEPDF_m_both_")+mode2
                nameLam3 = TString("Lb2LcPiEPDF_m_both_")+mode3
                nameLam4 = TString("Lb2LcPiEPDF_m_both_")+mode4
                nameLam5 = TString("Lb2LcPiEPDF_m_both_")+mode5
                                
                nameLam = nameLam1+p+nameLam2+p+nameLam3+p+nameLam4+p+nameLam5
                
                nameRho1 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode1
                nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode2
                nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode3
                nameRho4 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode4
                nameRho5 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode5
                                
                nameRho = nameRho1+p+nameRho2+p+nameRho3+p+nameRho4+p+nameRho5
                
                nameBd1 = TString("Bd2DRhoEPDF_m_both_")+mode1
                nameBd2 = TString("Bd2DRhoEPDF_m_both_")+mode2
                nameBd3 = TString("Bd2DRhoEPDF_m_both_")+mode3
                nameBd4 = TString("Bd2DRhoEPDF_m_both_")+mode4
                nameBd5 = TString("Bd2DRhoEPDF_m_both_")+mode5
                
                nameBd6 = TString("Bd2DstPiEPDF_m_both_")+mode1
                nameBd7 = TString("Bd2DstPiEPDF_m_both_")+mode2
                nameBd8 = TString("Bd2DstPiEPDF_m_both_")+mode3
                nameBd9 = TString("Bd2DstPiEPDF_m_both_")+mode4
                nameBd10 = TString("Bd2DstPiEPDF_m_both_")+mode5

                nameBd = nameBd1+p+nameBd2+p+nameBd3+p+nameBd4+p+nameBd5+p+nameBd6+p+nameBd7+p+nameBd8+p+nameBd9+p+nameBd10
                
                nameDPi1  = TString("Bd2DPiEPDF_m_both_")+mode1
                nameDPi2  = TString("Bd2DPiEPDF_m_both_")+mode2
                nameDPi3  = TString("Bd2DPiEPDF_m_both_")+mode3
                nameDPi4  = TString("Bd2DPiEPDF_m_both_")+mode4
                nameDPi5  = TString("Bd2DPiEPDF_m_both_")+mode5
                                
                nameDPi  = nameDPi1+p+nameDPi2+p+nameDPi3+p+nameDPi4+p+nameDPi5
                
                nameBdDsPi1  = TString("Bd2DsPiEPDF_m_both_")+mode1
                nameBdDsPi2  = TString("Bd2DsPiEPDF_m_both_")+mode2
                nameBdDsPi3  = TString("Bd2DsPiEPDF_m_both_")+mode3
                nameBdDsPi4  = TString("Bd2DsPiEPDF_m_both_")+mode4
                nameBdDsPi5  = TString("Bd2DsPiEPDF_m_both_")+mode5
                                
                nameBdDsPi  = nameBdDsPi1+p+nameBdDsPi2+p+nameBdDsPi3+p+nameBdDsPi4+p+nameBdDsPi5
                
                nameBdDsstPi1  = TString("Bd2DsstPiEPDF_m_both_")+mode1
                nameBdDsstPi2  = TString("Bd2DsstPiEPDF_m_both_")+mode2
                nameBdDsstPi3  = TString("Bd2DsstPiEPDF_m_both_")+mode3
                nameBdDsstPi4  = TString("Bd2DsstPiEPDF_m_both_")+mode4
                nameBdDsstPi5  = TString("Bd2DsstPiEPDF_m_both_")+mode5
                nameBdDsstPi  = nameBdDsstPi1+p+nameBdDsstPi2+p+nameBdDsstPi3+p+nameBdDsstPi4+p+nameBdDsstPi5

                nameDsK1 = TString("Bs2DsKEPDF_m_both_")+mode1
                nameDsK2 = TString("Bs2DsKEPDF_m_both_")+mode2
                nameDsK3 = TString("Bs2DsKEPDF_m_both_")+mode3
                nameDsK4 = TString("Bs2DsKEPDF_m_both_")+mode4
                nameDsK5 = TString("Bs2DsKEPDF_m_both_")+mode5

                nameDsK = nameDsK1+p+nameDsK2+p+nameDsK3+p+nameDsK4+p+nameDsK5
                
            elif mode == "3modes":
                print "3modes"
            else:
                sam =TString("both")
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
                nameDsK = TString("Bs2DsKEPDF_m_")+sam+t+mode
                                                                                                                                                    
        else:
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
                nameDsK = TString("Bs2DsKEPDF_m_up_")+mode+p+TString("Bs2DsKEPDF_m_down_")+mode
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
            nameDsK = TString("Bs2DsKEPDF_m_")+sam+t+mode
            
                                                        
    #p=TString(",")
    
    #p=TString(",")
    nameComDPi = nameCom+p+nameDPi
    nameComDPiLam = nameComDPi+p+nameLam #  nameBd+p+nameBdDsstPi+p+nameBdDsPi
    #nameComDPiRho = nameComDPiLam+p+nameBdDsPi+p+nameBd+p+nameBdDsstPi     #nameLam
    nameAll = nameComDPiLam+p+nameRho
    nameAll2 = nameAll+p+nameDsK

                        

                
    model.plotOn( frame, #RooFit.ProjectionRange("SR"),
                  RooFit.Components(nameTot.Data()),
                  RooFit.LineColor(kBlue),
                 # RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame, #RooFit.ProjectionRange("SR"),
                  RooFit.Components(nameAll2.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kGreen+3),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.plotOn( frame, #RooFit.ProjectionRange("SR"),
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
    
    #model.plotOn( frame, #RooFit.ProjectionRange("SR"),
    #              RooFit.Components(nameComDPiRho.Data()),
    #              RooFit.DrawOption("F"),
    #              RooFit.FillStyle(1001),
    #              RooFit.FillColor(kMagenta-2),
    #              RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
    #              )
                  
    model.plotOn( frame, #RooFit.ProjectionRange("SR"),
                  RooFit.Components(nameComDPiLam.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kRed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame, #RooFit.ProjectionRange("SR"),
                  RooFit.Components(nameComDPi.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kOrange),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame, #RooFit.ProjectionRange("SR"),
                  RooFit.Components(nameCom.Data()),
                  RooFit.DrawOption("F"),
                  RooFit.FillStyle(1001),
                  RooFit.FillColor(kBlue-6),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )

    model.plotOn( frame, #RooFit.ProjectionRange("SR"),
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
    from ROOT import RooFit, RooRealVar, RooAbsReal, RooCategory, RooArgSet, RooAddPdf, RooArgList, RooBinning
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
    mean  = 5366
    sam = TString(options.sample)
    mod = TString(options.mode)


    if mVarTS == "lab1_PIDK":
        range_dw = PIDK_dw
        range_up = PIDK_up
    elif mVarTS == "lab2_MM":
        range_dw = massDs_dw
        range_up = massDs_up
    else:
        range_dw = massBs_dw
        range_up = massBs_up

    if mVarTS == "lab1_PIDK":
        Bin = RooBinning(range_dw,range_up,'P')
        Bin.addUniform(bin, range_dw, range_up)
       # Bin.addUniform(10, 0,  10 ) #range_dw, range_dw+range_up/15)
       # Bin.addUniform(20, 10, 20) # range_dw+range_up/15, range_dw+range_up/10)
       # Bin.addUniform(70, 20, 150) # range_dw+range_up/10, range_up)
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

    #exit(0)
        
       
    #dataName = TString("combData")


    if sam == "up":
        print "Doesn't work"
        exit(0)
                
        if mod == "all":
            print "Sample up, mode all"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nLb2LcPi_up_kkpi_Evts*Lb2LcPiEPDF_m_up_kkpi, nBd2DPi_up_kkpi_Evts*Bd2DPiEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi, nBd2DsPi_up_kkpi_Evts*Bd2DsPiEPDF_m_up_kkpi, nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nLb2LcPi_up_kpipi_Evts*Lb2LcPiEPDF_m_up_kpipi, nBd2DPi_up_kpipi_Evts*Bd2DPiEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi, nBd2DsPi_up_kpipi_Evts*Bd2DsPiEPDF_m_up_kpipi,nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nLb2LcPi_up_pipipi_Evts*Lb2LcPiEPDF_m_up_pipipi, nBd2DPi_up_pipipi_Evts*Bd2DPiEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi,nBd2DsPi_up_pipipi_Evts*Bd2DsPiEPDF_m_up_pipipi)")
            pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi]")
            
        elif mod == "kkpi":
            print "Sample up, mode kkpi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi,nLb2LcPi_up_kkpi_Evts*Lb2LcPiEPDF_m_up_kkpi, nBd2DPi_up_kkpi_Evts*Bd2DPiEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi, nBd2DsPi_up_kkpi_Evts*Bd2DsPiEPDF_m_up_kkpi,nBd2DRho_up_kkpi_Evts*Bd2DRhoEPDF_m_up_kkpi,nBd2DstPi_up_kkpi_Evts*Bd2DstPiEPDF_m_up_kkpi,nBd2DsstPi_up_kkpi_Evts*Bd2DsstPiEPDF_m_up_kkpi,nBs2DsK_up_kkpi_Evts*Bs2DsKEPDF_m_up_kkpi)")
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
        print "Doesn't work"
        exit(0)
        
        if mod == "all":
            print "Sample down, mode all"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nLb2LcPi_down_kkpi_Evts*Lb2LcPiEPDF_m_down_kkpi, nBd2DPi_down_kkpi_Evts*Bd2DPiEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi, nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nLb2LcPi_down_kpipi_Evts*Lb2LcPiEPDF_m_down_kpipi, nBd2DPi_down_kpipi_Evts*Bd2DPiEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi,nBd2DsPi_down_kpipi_Evts*Bd2DsPiEPDF_m_down_kpipi, nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nLb2LcPi_down_pipipi_Evts*Lb2LcPiEPDF_m_down_pipipi, nBd2DPi_down_pipipi_Evts*Bd2DPiEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi, nBd2DsPi_down_pipipi_Evts*Bd2DsPiEPDF_m_down_pipipi )")
            pullname2TS = TString("h_combData_Cut[sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi]")
        elif mod == "kkpi":
            print "Sample down, mode kkpi"
            w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nLb2LcPi_down_kkpi_Evts*Lb2LcPiEPDF_m_down_kkpi, nBd2DPi_down_kkpi_Evts*Bd2DPiEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi,nBd2DRho_down_kkpi_Evts*Bd2DRhoEPDF_m_down_kkpi, nBd2DstPi_down_kkpi_Evts*Bd2DstPiEPDF_m_down_kkpi,nBd2DsstPi_down_kkpi_Evts*Bd2DsstPiEPDF_m_down_kkpi,nBs2DsK_down_kkpi_Evts*Bs2DsKEPDF_m_down_kkpi)")
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
        if merge:
            if mod == "all":
                print "Sample down, mode nonres with merge "
                print "[WARNING] plot without Bd2DRho, nBd2DstPi, Bd2DsstPi. Bd2DsPi should be included in BsDsDsstPiRho"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_nonres_Evts*Bs2DsDsstPiRhoEPDF_m_both_nonres, nLb2LcPi_both_nonres_Evts*Lb2LcPiEPDF_m_both_nonres, nBd2DPi_both_nonres_Evts*Bd2DPiEPDF_m_both_nonres, nSig_both_nonres_Evts*SigEPDF_both_nonres, nCombBkg_both_nonres_Evts*CombBkgEPDF_m_both_nonres,nBs2DsK_both_nonres_Evts*Bs2DsKEPDF_m_both_nonres, nBs2DsDsstPiRho_both_phipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_phipi, nLb2LcPi_both_phipi_Evts*Lb2LcPiEPDF_m_both_phipi, nBd2DPi_both_phipi_Evts*Bd2DPiEPDF_m_both_phipi, nSig_both_phipi_Evts*SigEPDF_both_phipi, nCombBkg_both_phipi_Evts*CombBkgEPDF_m_both_phipi, nBs2DsK_both_phipi_Evts*Bs2DsKEPDF_m_both_phipi, nBs2DsDsstPiRho_both_kstk_Evts*Bs2DsDsstPiRhoEPDF_m_both_kstk, nLb2LcPi_both_kstk_Evts*Lb2LcPiEPDF_m_both_kstk, nBd2DPi_both_kstk_Evts*Bd2DPiEPDF_m_both_kstk, nSig_both_kstk_Evts*SigEPDF_both_kstk, nCombBkg_both_kstk_Evts*CombBkgEPDF_m_both_kstk,nBs2DsK_both_kstk_Evts*Bs2DsKEPDF_m_both_kstk, nBs2DsDsstPiRho_both_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_kpipi, nLb2LcPi_both_kpipi_Evts*Lb2LcPiEPDF_m_both_kpipi, nBd2DPi_both_kpipi_Evts*Bd2DPiEPDF_m_both_kpipi, nSig_both_kpipi_Evts*SigEPDF_both_kpipi, nCombBkg_both_kpipi_Evts*CombBkgEPDF_m_both_kpipi, nBs2DsK_both_kpipi_Evts*Bs2DsKEPDF_m_both_kpipi, nBs2DsDsstPiRho_both_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_pipipi, nLb2LcPi_both_pipipi_Evts*Lb2LcPiEPDF_m_both_pipipi,nBd2DPi_both_pipipi_Evts*Bd2DPiEPDF_m_both_pipipi, nSig_both_pipipi_Evts*SigEPDF_both_pipipi, nCombBkg_both_pipipi_Evts*CombBkgEPDF_m_both_pipipi, nBs2DsK_both_pipipi_Evts*Bs2DsKEPDF_m_both_pipipi )")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_nonres || sample==sample::both_phipi || sample==sample::both_kstk || sample==sample::both_kpipi || sample==sample::both_pipipi]")
                                 
            elif mod == "nonres":
                print "Sample down, mode nonres, Bd2DsPi should be included in BsDsDsstPiRho"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_nonres_Evts*Bs2DsDsstPiRhoEPDF_m_both_nonres, nLb2LcPi_both_nonres_Evts*Lb2LcPiEPDF_m_both_nonres, nBd2DPi_both_nonres_Evts*Bd2DPiEPDF_m_both_nonres, nSig_both_nonres_Evts*SigEPDF_both_nonres, nCombBkg_both_nonres_Evts*CombBkgEPDF_m_both_nonres, nBs2DsK_both_nonres_Evts*Bs2DsKEPDF_m_both_nonres)") #
                pullname2TS = TString("h_combData_Cut[sample==sample::both_nonres]")
                                                
            elif mod == "phipi":
                print "Sample down, mode phipi, Bd2DsPi should be included in BsDsDsstPiRho"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_phipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_phipi, nLb2LcPi_both_phipi_Evts*Lb2LcPiEPDF_m_both_phipi, nBd2DPi_both_phipi_Evts*Bd2DPiEPDF_m_both_phipi, nSig_both_phipi_Evts*SigEPDF_both_phipi, nCombBkg_both_phipi_Evts*CombBkgEPDF_m_both_phipi, nBs2DsK_both_phipi_Evts*Bs2DsKEPDF_m_both_phipi)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_phipi]")
                                                                
            elif mod == "kstk":
                print "Sample down, mode kstk, Bd2DsPi should be included in BsDsDsstPiRho"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_kstk_Evts*Bs2DsDsstPiRhoEPDF_m_both_kstk, nLb2LcPi_both_kstk_Evts*Lb2LcPiEPDF_m_both_kstk, nBd2DPi_both_kstk_Evts*Bd2DPiEPDF_m_both_kstk, nSig_both_kstk_Evts*SigEPDF_both_kstk, nCombBkg_both_kstk_Evts*CombBkgEPDF_m_both_kstk,nBs2DsK_both_kstk_Evts*Bs2DsKEPDF_m_both_kstk)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_kstk]")
                                                                
            elif mod == "kpipi":
                print "Sample down, mode kpipi, Bd2DsPi should be included in BsDsDsstPiRho"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_kpipi, nLb2LcPi_both_kpipi_Evts*Lb2LcPiEPDF_m_both_kpipi, nBd2DPi_both_kpipi_Evts*Bd2DPiEPDF_m_both_kpipi, nSig_both_kpipi_Evts*SigEPDF_both_kpipi, nCombBkg_both_kpipi_Evts*CombBkgEPDF_m_both_kpipi, nBs2DsK_both_kpipi_Evts*Bs2DsKEPDF_m_both_kpipi )")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_kpipi]")
                                                                
            elif mod == "pipipi":
                print "Sample down, mode pipipi, Bd2DsPi should be included in BsDsDsstPiRho"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_pipipi, nLb2LcPi_both_pipipi_Evts*Lb2LcPiEPDF_m_both_pipipi, nBd2DPi_both_pipipi_Evts*Bd2DPiEPDF_m_both_pipipi, nSig_both_pipipi_Evts*SigEPDF_both_pipipi, nCombBkg_both_pipipi_Evts*CombBkgEPDF_m_both_pipipi, nBs2DsK_both_pipipi_Evts*Bs2DsKEPDF_m_both_pipipi)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_pipipi]")
                                                    
            
        else:    
            if mod == "3modes":
                print "Sample both, mode 3modes"
                w.factory("SUM:FullPdf1(nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nLb2LcPi_up_kkpi_Evts*Lb2LcPiEPDF_m_up_kkpi, nBd2DPi_up_kkpi_Evts*Bd2DPiEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi, nBd2DsPi_up_kkpi_Evts*Bd2DsPiEPDF_m_up_kkpi,nBs2DsDsstPiRho_up_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kpipi, nLb2LcPi_up_kpipi_Evts*Lb2LcPiEPDF_m_up_kpipi, nBd2DPi_up_kpipi_Evts*Bd2DPiEPDF_m_up_kpipi, nSig_up_kpipi_Evts*SigEPDF_up_kpipi, nCombBkg_up_kpipi_Evts*CombBkgEPDF_m_up_kpipi,nBd2DsPi_up_kpipi_Evts*Bd2DsPiEPDF_m_up_kpipi, nBs2DsDsstPiRho_up_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_up_pipipi, nLb2LcPi_up_pipipi_Evts*Lb2LcPiEPDF_m_up_pipipi, nBd2DPi_up_pipipi_Evts*Bd2DPiEPDF_m_up_pipipi, nSig_up_pipipi_Evts*SigEPDF_up_pipipi, nCombBkg_up_pipipi_Evts*CombBkgEPDF_m_up_pipipi,nBd2DsPi_up_pipipi_Evts*Bd2DsPiEPDF_m_up_pipipi)")
                
                w.factory("SUM:FullPdf1a(nBd2DstPi_up_kkpi_Evts*Bd2DstPiEPDF_m_up_kkpi,nBd2DstPi_up_kpipi_Evts*Bd2DstPiEPDF_m_up_kpipi,nBd2DstPi_up_pipipi_Evts*Bd2DstPiEPDF_m_up_pipipi,nBd2DRho_up_kkpi_Evts*Bd2DRhoEPDF_m_up_kkpi,nBd2DRho_up_kpipi_Evts*Bd2DRhoEPDF_m_up_kpipi,nBd2DRho_up_pipipi_Evts*Bd2DRhoEPDF_m_up_pipipi,nBd2DsstPi_up_kkpi_Evts*Bd2DsstPiEPDF_m_up_kkpi,nBd2DsstPi_up_kpipi_Evts*Bd2DsstPiEPDF_m_up_kpipi,nBd2DsstPi_up_pipipi_Evts*Bd2DsstPiEPDF_m_up_pipipi)")
                
                w.factory("SUM:FullPdf2(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nLb2LcPi_down_kkpi_Evts*Lb2LcPiEPDF_m_down_kkpi, nBd2DPi_down_kkpi_Evts*Bd2DPiEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi,nBs2DsDsstPiRho_down_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kpipi, nLb2LcPi_down_kpipi_Evts*Lb2LcPiEPDF_m_down_kpipi, nBd2DPi_down_kpipi_Evts*Bd2DPiEPDF_m_down_kpipi, nSig_down_kpipi_Evts*SigEPDF_down_kpipi, nCombBkg_down_kpipi_Evts*CombBkgEPDF_m_down_kpipi, nBd2DsPi_down_kpipi_Evts*Bd2DsPiEPDF_m_down_kpipi, nBs2DsDsstPiRho_down_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_down_pipipi, nLb2LcPi_down_pipipi_Evts*Lb2LcPiEPDF_m_down_pipipi, nBd2DPi_down_pipipi_Evts*Bd2DPiEPDF_m_down_pipipi, nSig_down_pipipi_Evts*SigEPDF_down_pipipi, nCombBkg_down_pipipi_Evts*CombBkgEPDF_m_down_pipipi,nBd2DsPi_down_pipipi_Evts*Bd2DsPiEPDF_m_down_pipipi)")
                
                w.factory("SUM:FullPdf2a(nBd2DstPi_down_kkpi_Evts*Bd2DstPiEPDF_m_down_kkpi,nBd2DstPi_down_kpipi_Evts*Bd2DstPiEPDF_m_down_kpipi,nBd2DstPi_down_pipipi_Evts*Bd2DstPiEPDF_m_down_pipipi,nBd2DRho_down_kkpi_Evts*Bd2DRhoEPDF_m_down_kkpi,nBd2DRho_down_kpipi_Evts*Bd2DRhoEPDF_m_down_kpipi,nBd2DRho_down_pipipi_Evts*Bd2DRhoEPDF_m_down_pipipi,nBd2DsstPi_down_kkpi_Evts*Bd2DsstPiEPDF_m_down_kkpi,nBd2DsstPi_down_kpipi_Evts*Bd2DsstPiEPDF_m_down_kpipi,nBd2DsstPi_down_pipipi_Evts*Bd2DsstPiEPDF_m_down_pipipi)")

            
                w.factory("EXPR::N_up('nBs2DsDsstPiRho_up_kkpi_Evts+nBd2DsPi_up_kkpi_Evts+nLb2LcPi_up_kkpi_Evts+nBd2DPi_up_kkpi_Evts+nSig_up_kkpi_Evts+nCombBkg_up_kkpi_Evts+nBs2DsDsstPiRho_up_kpipi_Evts+nBd2DsPi_up_kpipi_Evts+nLb2LcPi_up_kpipi_Evts+nBd2DPi_up_kpipi_Evts+nSig_up_kpipi_Evts+nCombBkg_up_kpipi_Evts+nBs2DsDsstPiRho_up_pipipi_Evts+nBd2DsPi_up_pipipi_Evts+nLb2LcPi_up_pipipi_Evts+nBd2DPi_up_pipipi_Evts+nSig_up_pipipi_Evts+nCombBkg_up_pipipi_Evts',nBs2DsDsstPiRho_up_kkpi_Evts,nBd2DsPi_up_kkpi_Evts,nLb2LcPi_up_kkpi_Evts,nBd2DPi_up_kkpi_Evts,nSig_up_kkpi_Evts,nCombBkg_up_kkpi_Evts,nBs2DsDsstPiRho_up_kpipi_Evts,nBd2DsPi_up_kpipi_Evts,nLb2LcPi_up_kpipi_Evts,nBd2DPi_up_kpipi_Evts,nSig_up_kpipi_Evts,nCombBkg_up_kpipi_Evts,nBs2DsDsstPiRho_up_pipipi_Evts,nBd2DsPi_up_pipipi_Evts,nLb2LcPi_up_pipipi_Evts,nBd2DPi_up_pipipi_Evts,nSig_up_pipipi_Evts,nCombBkg_up_pipipi_Evts)")

                w.factory("EXPR::N_up1a('nBd2DRho_up_kkpi_Evts+nBd2DRho_up_kpipi_Evts+nBd2DRho_up_pipipi_Evts+nBd2DstPi_up_kkpi_Evts+nBd2DstPi_up_kpipi_Evts+nBd2DstPi_up_pipipi_Evts+nBd2DsstPi_up_kkpi_Evts+nBd2DsstPi_up_kpipi_Evts+nBd2DsstPi_up_pipipi_Evts',nBd2DRho_up_kkpi_Evts,nBd2DRho_up_kpipi_Evts,nBd2DRho_up_pipipi_Evts,nBd2DstPi_up_kkpi_Evts,nBd2DstPi_up_kpipi_Evts,nBd2DstPi_up_pipipi_Evts,nBd2DsstPi_up_kkpi_Evts,nBd2DsstPi_up_kpipi_Evts,nBd2DsstPi_up_pipipi_Evts)")

                w.factory("EXPR::N_dw('nBs2DsDsstPiRho_down_kkpi_Evts+nBd2DsPi_down_kkpi_Evts+nLb2LcPi_down_kkpi_Evts+nBd2DPi_down_kkpi_Evts+nSig_down_kkpi_Evts+nCombBkg_down_kkpi_Evts+nBs2DsDsstPiRho_down_kpipi_Evts+nBd2DsPi_down_kpipi_Evts+nLb2LcPi_down_kpipi_Evts+nBd2DPi_down_kpipi_Evts+nSig_down_kpipi_Evts+nCombBkg_down_kpipi_Evts+nBs2DsDsstPiRho_down_pipipi_Evts+nBd2DsPi_down_pipipi_Evts+nLb2LcPi_down_pipipi_Evts+nBd2DPi_down_pipipi_Evts+nSig_down_pipipi_Evts+nCombBkg_down_pipipi_Evts',nBs2DsDsstPiRho_down_kkpi_Evts,nBd2DsPi_down_kkpi_Evts,nLb2LcPi_down_kkpi_Evts,nBd2DPi_down_kkpi_Evts,nSig_down_kkpi_Evts,nCombBkg_down_kkpi_Evts,nBs2DsDsstPiRho_down_kpipi_Evts,nBd2DsPi_down_kpipi_Evts,nLb2LcPi_down_kpipi_Evts,nBd2DPi_down_kpipi_Evts,nSig_down_kpipi_Evts,nCombBkg_down_kpipi_Evts,nBs2DsDsstPiRho_down_pipipi_Evts,nBd2DsPi_down_pipipi_Evts,nLb2LcPi_down_pipipi_Evts,nBd2DPi_down_pipipi_Evts,nSig_down_pipipi_Evts,nCombBkg_down_pipipi_Evts)")
                
                w.factory("EXPR::N_dw2a('nBd2DRho_down_kkpi_Evts+nBd2DRho_down_kpipi_Evts+nBd2DRho_down_pipipi_Evts+nBd2DstPi_down_kkpi_Evts+nBd2DstPi_down_kpipi_Evts+nBd2DstPi_down_pipipi_Evts+nBd2DsstPi_down_kkpi_Evts+nBd2DsstPi_down_kpipi_Evts+nBd2DsstPi_down_pipipi_Evts',nBd2DRho_down_kkpi_Evts,nBd2DRho_down_kpipi_Evts,nBd2DRho_down_pipipi_Evts,nBd2DstPi_down_kkpi_Evts,nBd2DstPi_down_kpipi_Evts,nBd2DstPi_down_pipipi_Evts,nBd2DsstPi_down_kkpi_Evts,nBd2DsstPi_down_kpipi_Evts,nBd2DsstPi_down_pipipi_Evts)")
            
                w.factory("SUM:FullPdf(N_up*FullPdf1,N_dw*FullPdf2, N_up1a*FullPdf1a, N_dw2a*FullPdf2a)")
                
                pullname2TS = TString("h_combData_Cut[sample==sample::up_kkpi || sample==sample::up_kpipi || sample==sample::up_pipipi || sample==sample::down_kkpi || sample==sample::down_kpipi || sample==sample::down_pipipi]")


            elif mod == "kkpi":
                print "Sample both, mode kkpi"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_down_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_down_kkpi, nLb2LcPi_down_kkpi_Evts*Lb2LcPiEPDF_m_down_kkpi, nBd2DPi_down_kkpi_Evts*Bd2DPiEPDF_m_down_kkpi, nSig_down_kkpi_Evts*SigEPDF_down_kkpi, nCombBkg_down_kkpi_Evts*CombBkgEPDF_m_down_kkpi, nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi, nBs2DsDsstPiRho_up_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_up_kkpi, nLb2LcPi_up_kkpi_Evts*Lb2LcPiEPDF_m_up_kkpi, nBd2DPi_up_kkpi_Evts*Bd2DPiEPDF_m_up_kkpi, nSig_up_kkpi_Evts*SigEPDF_up_kkpi, nCombBkg_up_kkpi_Evts*CombBkgEPDF_m_up_kkpi,nBd2DsPi_down_kkpi_Evts*Bd2DsPiEPDF_m_down_kkpi, nBd2DstPi_down_kkpi_Evts*Bd2DstPiEPDF_m_down_kkpi, nBd2DRho_down_kkpi_Evts*Bd2DRhoEPDF_m_down_kkpi,nBd2DstPi_up_kkpi_Evts*Bd2DstPiEPDF_m_up_kkpi, nBd2DRho_up_kkpi_Evts*Bd2DRhoEPDF_m_up_kkpi,nBd2DsstPi_up_kkpi_Evts*Bd2DsstPiEPDF_m_up_kkpi,nBd2DsstPi_down_kkpi_Evts*Bd2DsstPiEPDF_m_down_kkpi,nBs2DsK_down_kkpi_Evts*Bs2DsKEPDF_m_down_kkpi,nBs2DsK_up_kkpi_Evts*Bs2DsKEPDF_m_up_kkpi)")
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
    totName = TString("FullPdf")
    modelPDF = w.pdf( totName.Data() )
    dataset = w.data( dataName.Data() )
            
    if not ( modelPDF and dataset ) :
        print "Cos sie zepsulo?"
        w.Print( 'v' )
        exit( 0 )
   # w.Print('v')
   # exit(0)
 
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
    if mVarTS == "lab1_PIDK":
        frame_m.GetXaxis().SetTitle('#font[12]{PIDK [1]}')
    elif mVarTS == "lab2_MM":
        frame_m.GetXaxis().SetTitle('#font[12]{m(D_{s}) [MeV/c^{2}]}')
    else:
        frame_m.GetXaxis().SetTitle('#font[12]{m(B_{s} #rightarrow D_{s}#pi) [MeV/c^{2}]}')
    frame_m.GetYaxis().SetTitle('#font[12]{Events/(10.0 [MeV/c^{2}])}')

    if plotData : plotDataSet( dataset, frame_m, sam, mod, ty, merge, Bin )
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS, mod, merge )
    if plotData : plotDataSet( dataset, frame_m, sam, mod, ty, merge, Bin )

    if ( mVarTS == "lab0_MassFitConsD_M"):
        gStyle.SetOptLogy(1)
                               

    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    pad1 =  TPad("pad1","pad1",0.01,0.21,0.99,0.99)
    pad2 =  TPad("pad2","pad2",0.01,0.01,0.99,0.18)
    pad1.Draw()
    pad2.Draw()

    if mVarTS == "lab1_PIDK":
        legend = TLegend( 0.56, 0.30, 0.85, 0.80 )
        #legend = TLegend( 0.16, 0.30, 0.35, 0.80 )
               
    elif mVarTS == "lab2_MM":
        legend = TLegend( 0.60, 0.30, 0.85, 0.80 )
    else:    
        legend = TLegend( 0.56, 0.30, 0.85, 0.80 )
        
    legend.SetTextSize(0.06)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    legend.SetHeader("LHCb Preliminary") # L_{int}=1.0 fb^{-1}")
                    
          
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
    #legend.AddEntry(h1, "B_{s}#rightarrow D_{s}^{(*)}(#pi,#rho)", "f")
    legend.AddEntry(h1, "B_{(d,s)}#rightarrow D_{s}^{(*)}#pi", "f")
    
    h6=TH1F("Bs2DsK","Bs2DsK",5,0,1)
    h6.SetFillColor(kGreen+3)
    h6.SetFillStyle(1001)
    legend.AddEntry(h6, "B_{s}#rightarrow D_{s}K", "f")
    
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
    #legend.AddEntry(h4, "B_{d}#rightarrow D_{(s)}^{(*)}(#pi,#rho)", "f")
                  
    h5=TH1F("Combinatorial","Combinatorial",5,0,1)
    h5.SetFillColor(kBlue-6)
    h5.SetFillStyle(1001)
    legend.AddEntry(h5, "Combinatorial", "f")
            


    pad1.cd()
    frame_m.Draw()
    legend.Draw("same")
    pad1.Update()
    

    pad2.SetLogy(0)
    pad2.cd()
    gStyle.SetOptLogy(0)
            
    frame_m.Print("v")
    gStyle.SetOptLogy(0)
    
    frame_m.Print("v")
    if mVarTS == "lab1_PIDK":
        pullnameTS = TString("FullPdf_Int[lab0_MassFitConsD_M,lab2_MM]_Norm[lab0_MassFitConsD_M,lab1_PIDK,lab2_MM]_Comp[FullPdf]")
    elif mVarTS == "lab2_MM":
        pullnameTS = TString("FullPdf_Int[lab0_MassFitConsD_M,lab1_PIDK]_Norm[lab0_MassFitConsD_M,lab1_PIDK,lab2_MM]_Comp[FullPdf]")
    else:
        pullnameTS = TString("FullPdf_Int[lab1_PIDK,lab2_MM]_Norm[lab0_MassFitConsD_M,lab1_PIDK,lab2_MM]_Comp[FullPdf]")
        
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    axisX = pullHist.GetXaxis()
    axisX.Set(Bin.numBins(), Bin.array()) #100,range_dw,range_up)
         
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

    pullHist.Draw("ap")
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
