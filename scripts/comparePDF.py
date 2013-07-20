# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to generate toys for DsPi                                   #
#                                                                             #
#   Example usage:                                                            #
#      python comparePDF.py                                                   #
#                                                                             #
#   Author: Vava Gligorov                                                     #
#   Date  : 14 / 06 / 2012                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 28 / 06 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

import ROOT
from ROOT import *
from math import *
import os,sys
from optparse import OptionParser
from os.path  import join


import GaudiPython
from B2DXFitters import taggingutils, cpobservables
GaudiPython.loaddict( 'B2DXFittersDict' )

GeneralUtils = GaudiPython.gbl.GeneralUtils
SFitUtils = GaudiPython.gbl.SFitUtils
Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

#------------------------------------------------------------------------------
def runComparePDF( debug, name1, file1, work1, name2, file2, work2, obs ) :

    workspace1 = GeneralUtils.LoadWorkspace(TString(file1),TString(work1),debug)
    workspace2 = GeneralUtils.LoadWorkspace(TString(file2),TString(work2),debug)

    obs   = GeneralUtils.GetObservable(workspace1,TString(obs), debug)
    obs.setRange(0,150)
    
    pdf1 =  Bs2Dsh2011TDAnaModels.GetRooBinned1DFromWorkspace(workspace1,TString(name1), debug)
    pdf1.SetName("pdf1")
    pdf2 =  Bs2Dsh2011TDAnaModels.GetRooBinned1DFromWorkspace(workspace2,TString(name2), debug)
    pdf2.SetName("pdf2")

    #data1 = GeneralUtils.GetDataSet(workspace1,TString(name1),  debug)
    #data2 = GeneralUtils.GetDataSet(workspace2,TString(name2),  debug)
    
    canv = TCanvas("canv","canv")
    frame = obs.frame()
    '''
    scaleA = data1.sumEntries()/data2.sumEntries()
    print data1.numEntries()
    print data2.numEntries()
    print data1.sumEntries()
    print data2.sumEntries()
    print file1
    print file2
    
    data1.plotOn(frame,RooFit.MarkerColor(kOrange))
    data2.plotOn(frame,RooFit.MarkerColor(kRed),RooFit.Rescale(scaleA));
    '''
    
    pdf1.plotOn(frame, RooFit.LineColor(kRed))
    pdf2.plotOn(frame, RooFit.LineColor(kBlue))
    frame.Draw()
    canv.Print("comparePDF.pdf")
                                                                                    

#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '--name1',
                   dest = 'name1',
                   default = 'PIDKShape_Bs2DsPi_up_nonres')

parser.add_option( '--file1',
                   dest = 'file1',
                   default = 'work_dspi_pid_53005800_PIDK0_5M_BDTGA.root')

parser.add_option( '--work1',
                   dest = 'work1',
                   default = 'workspace')

parser.add_option( '--name2',
                   dest = 'name2',
                   default = 'PIDKShape_Bs2DsPi_up_phipi')

parser.add_option( '--file2',
                   dest = 'file2',
                   default = 'work_dspi_pid_53005800_PIDK0_5M_BDTGA.root')

parser.add_option( '--work2',
                   dest = 'work2',
                   default = 'workspace')

parser.add_option( '--obs',
                   dest = 'obs',
                   default = 'lab1_PIDK')

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    import sys
    sys.path.append("../data/")

    runComparePDF( options.debug,
                   options.name1 , options.file1, options.work1,
                   options.name2 , options.file2, options.work2,
                   options.obs
                   )                                
# -----------------------------------------------------------------------------
                                
