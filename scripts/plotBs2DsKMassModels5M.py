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
from math import log

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

import GaudiPython
GaudiPython.loaddict( 'B2DXFittersDict' )
from ROOT import *
from ROOT import RooCruijff

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True
bName = 'B_{s}'

PIDK_down = log(5)
PIDK_up = 5
Dmass_down = 1930
Dmass_up = 2015
Bmass_down = 5300
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
                   default = 'both',
                   help = 'Sample: choose up or down '
                   )
parser.add_option( '-o', '--mode',
                   dest = 'mode',
                   metavar = 'MODE',
                   default = 'all',
                   help = 'Mode: choose all, kkpi, kpipi or pipipi'
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

parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '
                   )
#------------------------------------------------------------------------------
def plotDataSet( dataset, frame, sample, mode, merge) :

    if sample == "both":
        if merge:
            if mode == "all":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_nonres || sample==sample::both_phipi || sample==sample::both_kstk || sample==sample::both_kpipi || sample==sample::both_pipipi"),
                                RooFit.Binning( 70 ) )
            elif mode =="3modeskkpi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_nonres || sample==sample::both_phipi || sample==sample::both_kstk"),
                                RooFit.Binning( 70 ) )
            elif mode =="3modes":    
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_kkpi || sample==sample::both_kpipi || sample==sample::both_pipipi"),
                                RooFit.Binning( 70 ) )
            elif mode == "nonres":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_nonres"),
                                RooFit.Binning( 70 ) )
            elif mode == "phipi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_phipi"),
                                RooFit.Binning( 70 ) )
            elif mode == "kstk":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_kstk"),
                                RooFit.Binning( 70 ) )                
            elif mode == "kkpi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_kkpi"),
                                RooFit.Binning( 70 ) )
            elif mode == "kpipi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_kpipi"),
                                RooFit.Binning( 70 ) )
            elif mode == "pipipi":
                dataset.plotOn( frame,
                                RooFit.Cut("sample==sample::both_pipipi"),
                                RooFit.Binning( 70 ) )
            else:
                print "[ERROR] Sample: both, wrong mode!"
                                                                                                                
            
        else:    
            
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
def plotFitModel( model, frame, sam, var,mode, merge) :
    #if debug :
    
    print "model"    
    model.Print( 't' )

    print "frame"
    frame.Print( 'v' )
    t=TString("_")
    p=TString(",")
    if sam == "both":
        if merge:
            if mode == "all":
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
                
                nameLam1 = TString("Lb2DsDsstPEPDF_m_both_")+mode1
                nameLam2 = TString("Lb2DsDsstPEPDF_m_both_")+mode2
                nameLam3 = TString("Lb2DsDsstPEPDF_m_both_")+mode3
                nameLam4 = TString("Lb2DsDsstPEPDF_m_both_")+mode4
                nameLam5 = TString("Lb2DsDsstPEPDF_m_both_")+mode5
                nameLam = nameLam1+p+nameLam2+p+nameLam3+p+nameLam4+p+nameLam5
                
                nameLamK1 = TString("Lb2LcKEPDF_m_both_")+mode1
                nameLamK2 = TString("Lb2LcKEPDF_m_both_")+mode2
                nameLamK3 = TString("Lb2LcKEPDF_m_both_")+mode3
                nameLamK4 = TString("Lb2LcKEPDF_m_both_")+mode4
                nameLamK5 = TString("Lb2LcKEPDF_m_both_")+mode5
                nameLamK = nameLamK1+p+nameLamK2+p+nameLamK3+p+nameLamK4+p+nameLamK5

                nameRho1 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode1+p+TString("Bs2DsPiEPDF_m_both_")+mode1
                nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode2+p+TString("Bs2DsPiEPDF_m_both_")+mode2
                nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode3+p+TString("Bs2DsPiEPDF_m_both_")+mode3
                nameRho4 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode4+p+TString("Bs2DsPiEPDF_m_both_")+mode4
                nameRho5 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode5+p+TString("Bs2DsPiEPDF_m_both_")+mode5
                nameRho = nameRho1+p+nameRho2+p+nameRho3+p+nameRho4+p+nameRho5

                nameKst1 = TString("Bs2DsDsstKKstEPDF_m_both_")+mode1
                nameKst2 = TString("Bs2DsDsstKKstEPDF_m_both_")+mode2
                nameKst3 = TString("Bs2DsDsstKKstEPDF_m_both_")+mode3
                nameKst4 = TString("Bs2DsDsstKKstEPDF_m_both_")+mode4
                nameKst5 = TString("Bs2DsDsstKKstEPDF_m_both_")+mode5
                nameKst = nameKst1+p+nameKst2+p+nameKst3+p+nameKst4+p+nameKst5
                
                nameDK1  = TString("Bd2DKEPDF_m_both_")+mode1
                nameDK2  = TString("Bd2DKEPDF_m_both_")+mode2
                nameDK3  = TString("Bd2DKEPDF_m_both_")+mode3
                nameDK4  = TString("Bd2DKEPDF_m_both_")+mode4
                nameDK5  = TString("Bd2DKEPDF_m_both_")+mode5
                nameDK  = nameDK1+p+nameDK2+p+nameDK3+p+nameDK4+p+nameDK5
                                
            elif mode.Contains("3modes"):
                nameTot = TString("FullPdf")

                if mode.Contains("kkpi"):
                    mode1 = TString("nonres")
                    mode2 = TString("phipi")
                    mode3 = TString("kstk")
                else:
                    mode1 = TString("kkpi")
                    mode2 = TString("kpipi")
                    mode3 = TString("pipipi")
                
                nameCom1 =TString("CombBkgEPDF_m_both_")+mode1
                nameCom2 =TString("CombBkgEPDF_m_both_")+mode2
                nameCom3 =TString("CombBkgEPDF_m_both_")+mode3
                nameCom = nameCom1+p+nameCom2+p+nameCom3
                
                nameSig1 = TString("SigEPDF_both_")+mode1
                nameSig2 = TString("SigEPDF_both_")+mode2
                nameSig3 = TString("SigEPDF_both_")+mode3
                nameSig = nameSig1+p+nameSig2+p+nameSig3
                
                nameLam1 = TString("Lb2DsDsstPEPDF_m_both_")+mode1
                nameLam2 = TString("Lb2DsDsstPEPDF_m_both_")+mode2
                nameLam3 = TString("Lb2DsDsstPEPDF_m_both_")+mode3
                nameLam = nameLam1+p+nameLam2+p+nameLam3
                
                nameLamK1 = TString("Lb2LcKEPDF_m_both_")+mode1
                nameLamK2 = TString("Lb2LcKEPDF_m_both_")+mode2
                nameLamK3 = TString("Lb2LcKEPDF_m_both_")+mode3
                nameLamK = nameLamK1+p+nameLamK2+p+nameLamK3
                              
                nameRho1 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode1+p+TString("Bs2DsPiEPDF_m_both_")+mode1
                nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode2+p+TString("Bs2DsPiEPDF_m_both_")+mode2
                nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode3+p+TString("Bs2DsPiEPDF_m_both_")+mode3
                nameRho = nameRho1+p+nameRho2+p+nameRho3

                nameKst1 = TString("Bs2DsDsstKKstEPDF_m_both_")+mode1
                nameKst2 = TString("Bs2DsDsstKKstEPDF_m_both_")+mode2
                nameKst3 = TString("Bs2DsDsstKKstEPDF_m_both_")+mode3
                nameKst = nameKst1+p+nameKst2+p+nameKst3
                
                nameDK1  = TString("Bd2DKEPDF_m_both_")+mode1
                nameDK2  = TString("Bd2DKEPDF_m_both_")+mode2
                nameDK3  = TString("Bd2DKEPDF_m_both_")+mode3
                nameDK  = nameDK1+p+nameDK2+p+nameDK3
                
            else:
                nameTot = TString("FullPdf")
                nameCom = TString("CombBkgEPDF_m_both_")+mode
                nameSig = TString("SigEPDF_both_")+mode
                nameLam = TString("Lb2DsDsstPEPDF_m_both_")+mode
                nameLamK = TString("Lb2LcKEPDF_m_both_")+mode
                nameRho = TString("Bs2DsDsstPiRhoEPDF_m_both_")+mode+p+TString("Bs2DsPiEPDF_m_both_")+mode
                nameKst = TString("Bs2DsDsstKKstEPDF_m_both_")+mode
                nameDK  = TString("Bd2DKEPDF_m_both_")+mode
                
                
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
                
                nameLam1 = TString("Lb2DsDsstPEPDF_m_up_")+mode1+p+TString("Lb2DsDsstPEPDF_m_down_")+mode1
                nameLam2 = TString("Lb2DsDsstPEPDF_m_up_")+mode2+p+TString("Lb2DsDsstPEPDF_m_down_")+mode2
                nameLam3 = TString("Lb2DsDsstPEPDF_m_up_")+mode3+p+TString("Lb2DsDsstPEPDF_m_down_")+mode3
                nameLam = nameLam1+p+nameLam2+p+nameLam3
                
                nameLamK1 = TString("Lb2LcKEPDF_m_up_")+mode1+p+TString("Lb2LcKEPDF_m_down_")+mode1
                nameLamK2 = TString("Lb2LcKEPDF_m_up_")+mode2+p+TString("Lb2LcKEPDF_m_down_")+mode2
                nameLamK3 = TString("Lb2LcKEPDF_m_up_")+mode3+p+TString("Lb2LcKEPDF_m_down_")+mode3
                nameLamK = nameLamK1+p+nameLamK2+p+nameLamK3
                   
                
                nameRho1 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode1+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode1+p+TString("Bs2DsPiEPDF_m_up_")+mode1+p+TString("Bs2DsPiEPDF_m_down_")+mode1
                nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode2+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode2+p+TString("Bs2DsPiEPDF_m_up_")+mode2+p+TString("Bs2DsPiEPDF_m_down_")+mode2
                nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode3+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode3+p+TString("Bs2DsPiEPDF_m_up_")+mode3+p+TString("Bs2DsPiEPDF_m_down_")+mode3
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
                nameRho = TString("Bs2DsDsstPiRhoEPDF_m_up_")+mode+p+TString("Bs2DsDsstPiRhoEPDF_m_down_")+mode+p+TString("Bs2DsPiEPDF_m_up_")+mode+p+TString("Bs2DsPiEPDF_m_down_")+mode
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
                                            

            nameRho1 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("kkpi")+TString("Bs2DsPiEPDF_m_")+sam+t+TString("kkpi")
            nameRho2 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("kpipi")+TString("Bs2DsPiEPDF_m_")+sam+t+TString("kpipi")
            nameRho3 = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+TString("pipipi")+TString("Bs2DsPiEPDF_m_")+sam+t+TString("pipipi")
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
            nameRho = TString("Bs2DsDsstPiRhoEPDF_m_")+sam+t+mode+p+TString("Bs2DsPiEPDF_m_")+sam+t+mode
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
    #mass = RooRealVar( 'mass', '%s mass' % bName, mean, 5000, 5800, 'MeV/c^{2}' )
    sam = TString(options.sample)
    mod = TString(options.mode)
    sufixTS = TString(options.sufix)
    if sufixTS != "":
        sufixTS = TString("_")+sufixTS
    
    merge = options.merge
    if sam != "both" and merge == True:
        print "You cannot plot with option sample up or down!"
        exit(0)
        
    w.Print('v')
    #exit(0)
        
       
    dataName = TString("combData")


    if sam == "up":
        print "Doesn't work"
        exit(0)
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
        print "Doesn't work"
        exit(0)
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
        if merge:
            if mod =="all":
                print "Sample both, mode all with options merge"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_nonres_Evts*Bs2DsDsstPiRhoEPDF_m_both_nonres, nBs2DsDssKKst_both_nonres_Evts*Bs2DsDsstKKstEPDF_m_both_nonres, nLb2DsDsstp_both_nonres_Evts*Lb2DsDsstPEPDF_m_both_nonres, nBd2DK_both_nonres_Evts*Bd2DKEPDF_m_both_nonres, nSig_both_nonres_Evts*SigEPDF_both_nonres, nCombBkg_both_nonres_Evts*CombBkgEPDF_m_both_nonres, nLb2LcK_both_nonres_Evts*Lb2LcKEPDF_m_both_nonres, nBs2DsDsstPiRho_both_phipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_phipi, nBs2DsDssKKst_both_phipi_Evts*Bs2DsDsstKKstEPDF_m_both_phipi, nLb2DsDsstp_both_phipi_Evts*Lb2DsDsstPEPDF_m_both_phipi, nBd2DK_both_phipi_Evts*Bd2DKEPDF_m_both_phipi, nSig_both_phipi_Evts*SigEPDF_both_phipi, nCombBkg_both_phipi_Evts*CombBkgEPDF_m_both_phipi, nLb2LcK_both_phipi_Evts*Lb2LcKEPDF_m_both_phipi, nBs2DsDsstPiRho_both_kstk_Evts*Bs2DsDsstPiRhoEPDF_m_both_kstk, nBs2DsDssKKst_both_kstk_Evts*Bs2DsDsstKKstEPDF_m_both_kstk, nLb2DsDsstp_both_kstk_Evts*Lb2DsDsstPEPDF_m_both_kstk, nBd2DK_both_kstk_Evts*Bd2DKEPDF_m_both_kstk, nSig_both_kstk_Evts*SigEPDF_both_kstk, nCombBkg_both_kstk_Evts*CombBkgEPDF_m_both_kstk, nLb2LcK_both_kstk_Evts*Lb2LcKEPDF_m_both_kstk, nBs2DsDsstPiRho_both_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_kpipi, nBs2DsDssKKst_both_kpipi_Evts*Bs2DsDsstKKstEPDF_m_both_kpipi, nLb2DsDsstp_both_kpipi_Evts*Lb2DsDsstPEPDF_m_both_kpipi, nBd2DK_both_kpipi_Evts*Bd2DKEPDF_m_both_kpipi, nSig_both_kpipi_Evts*SigEPDF_both_kpipi, nCombBkg_both_kpipi_Evts*CombBkgEPDF_m_both_kpipi, nLb2LcK_both_kpipi_Evts*Lb2LcKEPDF_m_both_kpipi, nBs2DsDsstPiRho_both_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_pipipi, nBs2DsDssKKst_both_pipipi_Evts*Bs2DsDsstKKstEPDF_m_both_pipipi, nLb2DsDsstp_both_pipipi_Evts*Lb2DsDsstPEPDF_m_both_pipipi, nBd2DK_both_pipipi_Evts*Bd2DKEPDF_m_both_pipipi, nSig_both_pipipi_Evts*SigEPDF_both_pipipi, nCombBkg_both_pipipi_Evts*CombBkgEPDF_m_both_pipipi, nLb2LcK_both_pipipi_Evts*Lb2LcKEPDF_m_both_pipipi, nBs2DsPi_both_nonres_Evts*Bs2DsPiEPDF_m_both_nonres, nBs2DsPi_both_kstk_Evts*Bs2DsPiEPDF_m_both_kstk, nBs2DsPi_both_phipi_Evts*Bs2DsPiEPDF_m_both_phipi, nBs2DsPi_both_kpipi_Evts*Bs2DsPiEPDF_m_both_kpipi, nBs2DsPi_both_pipipi_Evts*Bs2DsPiEPDF_m_both_pipipi)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_nonres || sample==sample::both_phipi || sample==sample::both_kstk || sample==sample::both_kpipi || sample==sample::both_pipipi]")
            elif mod == "3modeskkpi":
                print "Sample both, mode 3modes with options merge"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_nonres_Evts*Bs2DsDsstPiRhoEPDF_m_both_nonres, nBs2DsDssKKst_both_nonres_Evts*Bs2DsDsstKKstEPDF_m_both_nonres, nLb2DsDsstp_both_nonres_Evts*Lb2DsDsstPEPDF_m_both_nonres, nBd2DK_both_nonres_Evts*Bd2DKEPDF_m_both_nonres, nSig_both_nonres_Evts*SigEPDF_both_nonres, nCombBkg_both_nonres_Evts*CombBkgEPDF_m_both_nonres, nLb2LcK_both_nonres_Evts*Lb2LcKEPDF_m_both_nonres, nBs2DsDsstPiRho_both_phipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_phipi, nBs2DsDssKKst_both_phipi_Evts*Bs2DsDsstKKstEPDF_m_both_phipi, nLb2DsDsstp_both_phipi_Evts*Lb2DsDsstPEPDF_m_both_phipi, nBd2DK_both_phipi_Evts*Bd2DKEPDF_m_both_phipi, nSig_both_phipi_Evts*SigEPDF_both_phipi, nCombBkg_both_phipi_Evts*CombBkgEPDF_m_both_phipi, nLb2LcK_both_phipi_Evts*Lb2LcKEPDF_m_both_phipi,nBs2DsDsstPiRho_both_kstk_Evts*Bs2DsDsstPiRhoEPDF_m_both_kstk, nBs2DsDssKKst_both_kstk_Evts*Bs2DsDsstKKstEPDF_m_both_kstk, nLb2DsDsstp_both_kstk_Evts*Lb2DsDsstPEPDF_m_both_kstk, nBd2DK_both_kstk_Evts*Bd2DKEPDF_m_both_kstk, nSig_both_kstk_Evts*SigEPDF_both_kstk, nCombBkg_both_kstk_Evts*CombBkgEPDF_m_both_kstk,nLb2LcK_both_kstk_Evts*Lb2LcKEPDF_m_both_kstk, nBs2DsPi_both_nonres_Evts*Bs2DsPiEPDF_m_both_nonres, nBs2DsPi_both_kstk_Evts*Bs2DsPiEPDF_m_both_kstk, nBs2DsPi_both_phipi_Evts*Bs2DsPiEPDF_m_both_phipi)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_nonres || sample==sample::both_phipi || sample==sample::both_kstk]")
                                                
            elif mod == "3modes":
                print "Sample both, mode 3modes with options merge"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_both_kkpi, nBs2DsDssKKst_both_kkpi_Evts*Bs2DsDsstKKstEPDF_m_both_kkpi, nLb2DsDsstp_both_kkpi_Evts*Lb2DsDsstPEPDF_m_both_kkpi, nBd2DK_both_kkpi_Evts*Bd2DKEPDF_m_both_kkpi, nSig_both_kkpi_Evts*SigEPDF_both_kkpi, nCombBkg_both_kkpi_Evts*CombBkgEPDF_m_both_kkpi, nLb2LcK_both_kkpi_Evts*Lb2LcKEPDF_m_both_kkpi, nBs2DsDsstPiRho_both_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_kpipi, nBs2DsDssKKst_both_kpipi_Evts*Bs2DsDsstKKstEPDF_m_both_kpipi, nLb2DsDsstp_both_kpipi_Evts*Lb2DsDsstPEPDF_m_both_kpipi, nBd2DK_both_kpipi_Evts*Bd2DKEPDF_m_both_kpipi, nSig_both_kpipi_Evts*SigEPDF_both_kpipi, nCombBkg_both_kpipi_Evts*CombBkgEPDF_m_both_kpipi, nLb2LcK_both_kpipi_Evts*Lb2LcKEPDF_m_both_kpipi, nBs2DsDsstPiRho_both_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_pipipi, nBs2DsDssKKst_both_pipipi_Evts*Bs2DsDsstKKstEPDF_m_both_pipipi, nLb2DsDsstp_both_pipipi_Evts*Lb2DsDsstPEPDF_m_both_pipipi, nBd2DK_both_pipipi_Evts*Bd2DKEPDF_m_both_pipipi, nSig_both_pipipi_Evts*SigEPDF_both_pipipi, nCombBkg_both_pipipi_Evts*CombBkgEPDF_m_both_pipipi,nLb2LcK_both_pipipi_Evts*Lb2LcKEPDF_m_both_pipipi, nBs2DsPi_both_kkpi_Evts*Bs2DsPiEPDF_m_both_kkpi, nBs2DsPi_both_kpipi_Evts*Bs2DsPiEPDF_m_both_kpipi, nBs2DsPi_both_pipipi_Evts*Bs2DsPiEPDF_m_both_pipipi)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_kkpi || sample==sample::both_kpipi || sample==sample::both_pipipi]")
            elif mod == "nonres":
                print "Sample down, mode nonres with options merge"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_nonres_Evts*Bs2DsDsstPiRhoEPDF_m_both_nonres, nBs2DsDssKKst_both_nonres_Evts*Bs2DsDsstKKstEPDF_m_both_nonres, nLb2DsDsstp_both_nonres_Evts*Lb2DsDsstPEPDF_m_both_nonres, nBd2DK_both_nonres_Evts*Bd2DKEPDF_m_both_nonres, nSig_both_nonres_Evts*SigEPDF_both_nonres, nCombBkg_both_nonres_Evts*CombBkgEPDF_m_both_nonres, nLb2LcK_both_nonres_Evts*Lb2LcKEPDF_m_both_nonres, nBs2DsPi_both_nonres_Evts*Bs2DsPiEPDF_m_both_nonres)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_nonres]")
            elif mod == "phipi":
                print "Sample down, mode phipi with options merge"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_phipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_phipi, nBs2DsDssKKst_both_phipi_Evts*Bs2DsDsstKKstEPDF_m_both_phipi, nLb2DsDsstp_both_phipi_Evts*Lb2DsDsstPEPDF_m_both_phipi, nBd2DK_both_phipi_Evts*Bd2DKEPDF_m_both_phipi, nSig_both_phipi_Evts*SigEPDF_both_phipi, nCombBkg_both_phipi_Evts*CombBkgEPDF_m_both_phipi, nLb2LcK_both_phipi_Evts*Lb2LcKEPDF_m_both_phipi, nBs2DsPi_both_phipi_Evts*Bs2DsPiEPDF_m_both_phipi)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_phipi]")
            elif mod == "kstk":
                print "Sample down, mode kstk with options merge"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_kstk_Evts*Bs2DsDsstPiRhoEPDF_m_both_kstk, nBs2DsDssKKst_both_kstk_Evts*Bs2DsDsstKKstEPDF_m_both_kstk, nLb2DsDsstp_both_kstk_Evts*Lb2DsDsstPEPDF_m_both_kstk, nBd2DK_both_kstk_Evts*Bd2DKEPDF_m_both_kstk, nSig_both_kstk_Evts*SigEPDF_both_kstk, nCombBkg_both_kstk_Evts*CombBkgEPDF_m_both_kstk, nLb2LcK_both_kstk_Evts*Lb2LcKEPDF_m_both_kstk, nBs2DsPi_both_kstk_Evts*Bs2DsPiEPDF_m_both_kstk)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_kstk]")
                                                
            elif mod == "kkpi":
                print "Sample down, mode kkpi with options merge"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_kkpi_Evts*Bs2DsDsstPiRhoEPDF_m_both_kkpi, nBs2DsDssKKst_both_kkpi_Evts*Bs2DsDsstKKstEPDF_m_both_kkpi, nLb2DsDsstp_both_kkpi_Evts*Lb2DsDsstPEPDF_m_both_kkpi, nBd2DK_both_kkpi_Evts*Bd2DKEPDF_m_both_kkpi, nSig_both_kkpi_Evts*SigEPDF_both_kkpi, nCombBkg_both_kkpi_Evts*CombBkgEPDF_m_both_kkpi, nLb2LcK_both_kkpi_Evts*Lb2LcKEPDF_m_both_kkpi, nBs2DsPi_both_kkpi_Evts*Bs2DsPiEPDF_m_both_kkpi)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_kkpi]")

            elif mod == "kpipi":
                print "Sample down, mode kpipi with options merge"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_kpipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_kpipi, nBs2DsDssKKst_both_kpipi_Evts*Bs2DsDsstKKstEPDF_m_both_kpipi, nLb2DsDsstp_both_kpipi_Evts*Lb2DsDsstPEPDF_m_both_kpipi, nBd2DK_both_kpipi_Evts*Bd2DKEPDF_m_both_kpipi, nSig_both_kpipi_Evts*SigEPDF_both_kpipi, nCombBkg_both_kpipi_Evts*CombBkgEPDF_m_both_kpipi, nLb2LcK_both_kpipi_Evts*Lb2LcKEPDF_m_both_kpipi, nBs2DsPi_both_kpipi_Evts*Bs2DsPiEPDF_m_both_kpipi)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_kpipi]")
                
            elif mod == "pipipi":
                print "Sample down, mode pipipi with options merge"
                w.factory("SUM:FullPdf(nBs2DsDsstPiRho_both_pipipi_Evts*Bs2DsDsstPiRhoEPDF_m_both_pipipi, nBs2DsDssKKst_both_pipipi_Evts*Bs2DsDsstKKstEPDF_m_both_pipipi, nLb2DsDsstp_both_pipipi_Evts*Lb2DsDsstPEPDF_m_both_pipipi, nBd2DK_both_pipipi_Evts*Bd2DKEPDF_m_both_pipipi, nSig_both_pipipi_Evts*SigEPDF_both_pipipi, nCombBkg_both_pipipi_Evts*CombBkgEPDF_m_both_pipipi, nLb2LcK_both_pipipi_Evts*Lb2LcKEPDF_m_both_pipipi, nBs2DsPi_both_pipipi_Evts*Bs2DsPiEPDF_m_both_pipipi)")
                pullname2TS = TString("h_combData_Cut[sample==sample::both_pipipi]")
                                                                                                                                    
        else:    
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
        frame_m.GetXaxis().SetTitle('#font[12]{ln(PIDK) [1]}')
    elif mVarTS == "lab2_MM":
        frame_m.GetXaxis().SetTitle('#font[12]{m(D_{s}) [MeV/c^{2}]}')
    else:
        frame_m.GetXaxis().SetTitle('#font[12]{m(B_{s} #rightarrow D_{s}#pi) [MeV/c^{2}]}')
                                        
    
    frame_m.GetYaxis().SetTitle('#font[12]{Events/(10.0 [MeV/c^{2}])}')
    
    if plotData : plotDataSet( dataset, frame_m, sam, mod , merge)
    if plotModel : plotFitModel( modelPDF, frame_m, sam, mVarTS, mod , merge)
    if plotData : plotDataSet( dataset, frame_m, sam, mod , merge)
    

    canvas = TCanvas("canvas", "canvas", 1400, 1000)
    pad1 =  TPad("pad1","pad1",0.01,0.21,0.99,0.99)
    pad2 =  TPad("pad2","pad2",0.01,0.01,0.99,0.20)
    pad1.Draw()
    pad2.Draw()

    if mVarTS == "lab1_PIDK":
        legend = TLegend( 0.65, 0.38, 0.85, 0.88 )
    elif mVarTS == "lab2_MM":
        legend = TLegend( 0.60, 0.38, 0.87, 0.88 )
    else:
        legend = TLegend( 0.56, 0.30, 0.85, 0.80 )
                                        
    
    legend.SetTextSize(0.05)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)
    
    legend.SetHeader("LHCb Preliminary L_{int}=1fb^{-1}")

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
    if mVarTS == "lab1_PIDK":
        pullnameTS = TString("FullPdf_Int[lab0_MassFitConsD_M,lab2_MM]_Norm[lab0_MassFitConsD_M,lab1_PIDK,lab2_MM]_Comp[FullPdf]")
    elif mVarTS == "lab2_MM":
        pullnameTS = TString("FullPdf_Int[lab0_MassFitConsD_M,lab1_PIDK]_Norm[lab0_MassFitConsD_M,lab1_PIDK,lab2_MM]_Comp[FullPdf]")
    else:
        pullnameTS = TString("FullPdf_Int[lab1_PIDK,lab2_MM]_Norm[lab0_MassFitConsD_M,lab1_PIDK,lab2_MM]_Comp[FullPdf]")
        
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    axisX = pullHist.GetXaxis()
    axisX.Set(70,Bmass_down,Bmass_up)
    if mVarTS == "lab2_MM":
        axisX.Set(70,Dmass_down,Dmass_up)
    if mVarTS == "lab1_PIDK":
        axisX.Set(70,PIDK_down,PIDK_up)
                    
                
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
    graph.SetPoint(1,Bmass_down,0)
    graph.SetPoint(2,Bmass_up,0)
    if mVarTS == "lab2_MM":
        graph.SetPoint(1,Dmass_down,0)
        graph.SetPoint(2,Dmass_up,0)
    if mVarTS == "lab1_PIDK":
        graph.SetPoint(1,PIDK_down,0)
        graph.SetPoint(2,PIDK_up,0)
                        

    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    graph2.SetPoint(1,Bmass_down,-3)
    graph2.SetPoint(2,Bmass_up,-3)
    if mVarTS == "lab2_MM":
        graph2.SetPoint(1,Dmass_down,-3)
        graph2.SetPoint(2,Dmass_up,-3)
    if mVarTS == "lab1_PIDK":
        graph2.SetPoint(1,PIDK_down,-3)
        graph2.SetPoint(2,PIDK_up,-3)
                        
    graph2.SetLineColor(kRed)
    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    graph3.SetPoint(1,Bmass_down,3)
    graph3.SetPoint(2,Bmass_up,3)
    if mVarTS == "lab2_MM":
        graph3.SetPoint(1,Dmass_down,3)
        graph3.SetPoint(2,Dmass_up,3)
    if mVarTS == "lab1_PIDK":
        graph3.SetPoint(1,PIDK_down,3)
        graph3.SetPoint(2,PIDK_up,3)
                
    graph3.SetLineColor(kRed)

    pullHist.SetTitle("")
    pullHist.GetXaxis().SetLabelFont( 132 )
    pullHist.GetYaxis().SetLabelFont( 132 )
    #print log(5)
    
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
    

      
    n = TString("TotEPDF_m_")+sam+TString("_paramBox")    
    pt = canvas.FindObject( n.Data() )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update()
    canName = TString("mass_BsDsK_")+mVarTS+TString("_")+sam+TString("_")+mod+sufixTS+TString(".pdf")
    canvas.Print(canName.Data())
    canName = TString("mass_BsDsK_")+mVarTS+TString("_")+sam+TString("_")+mod+sufixTS+TString(".png")
    canvas.Print(canName.Data())
    canName = TString("mass_BsDsK_")+mVarTS+TString("_")+sam+TString("_")+mod+sufixTS+TString(".root")
    canvas.Print(canName.Data())
        
#------------------------------------------------------------------------------
