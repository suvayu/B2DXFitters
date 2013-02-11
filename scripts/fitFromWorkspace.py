#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a fit to a specified model on an input data sample   #
#   using the FitMeTool                                                       #
#                                                                             #
#   Example usage:                                                            #
#      ./runFitModelToData.py -l                                              #
#      ./fitFromWorkspace.py -f WS_blabla.root -d -w FitMeToolWS              #
#                            --pdf TotEPDF_t --data TotEPDF_tData -s MyResult #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 10 / 04 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser


# -----------------------------------------------------------------------------
# Print the file contents
# Well, only the top-level directory and the workspaces stored ;-)
# -----------------------------------------------------------------------------
def printFileContents( filename ) :
    from ROOT import TFile
    f = TFile( filename )
    if not f.IsZombie() :

        import GaudiPython
        GaudiPython.loaddict( 'B2DXFittersDict' )
        from ROOT import BdPTAcceptance
        
        f.ls()
        keys = f.GetListOfKeys()
        for k in keys :
            obj = k.ReadObj()
            if obj.ClassName() == 'RooWorkspace' :
                obj.Print( 't' )
    else :
        print '[ERROR] File "%s" does not exist! Nothing listed.' % filename
        parser.print_help()

# -----------------------------------------------------------------------------
# Run the actual fit
# -----------------------------------------------------------------------------
def runFitModelToData( filename, ws, pdf, data, outws, debug ) :
    import GaudiPython
    
    GaudiPython.loaddict( 'B2DXFittersDict' )
    
    from ROOT import RooFit
    from ROOT import FitMeTool
    
    
    fitter = FitMeTool( debug )
    
    fitter.setModelPDF( filename, ws, pdf )

    fitter.setData( filename, ws, data )

    if debug: fitter.printModelStructure()
    
    fitter.fit( True, RooFit.Strategy(2), RooFit.Timer() )
    
    if outws:
        fitter.saveModelPDF( outws )
        fitter.saveData( outws )
    
    del fitter

#------------------------------------------------------------------------------
_usage = '%prog [options] <filename>'

parser = OptionParser(_usage)

parser.add_option('-d', '--debug',
                  dest    = 'debug',
                  default = False,
                  action  = 'store_true',
                  help    = 'print debug information while processing'
                  )
parser.add_option('-l', '--list',
                  dest    = 'list',
                  default = False,
                  action  = 'store_true',
                  help    = 'print out the contents of the input ROOT file and exit'
                  )
parser.add_option('-w', '--workspace',
                  dest    = 'ws',
                  default = 'UNSPECIFIED',
                  metavar = 'WSNAME',
                  help    = 'Input workspace name containing the model PDF and the data to be fitted (default: WSNAME = "FitMeToolWS")'
                  )
parser.add_option('--pdf',
                  dest    = 'pdf',
                  default = 'UNSPECIFIED',
                  help    = 'specify the name of the model PDF stored in the workspace'
                  )
parser.add_option('--data',
                  dest    = 'data',
                  default = 'UNSPECIFIED',
                  help    = 'specify the name of the data stored in the workspace'
                  )
parser.add_option('-o', '--output',
                  dest    = 'outws',
                  default = 'FitMeToolWS',
                  metavar = 'OUTWSNAME',
                  help    = 'save the fitted data and model PDF to file named "WS_OUTWSNAME.root" (default: OUTWSNAME = "FitMeToolWS")'
                  )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    (options, args) = parser.parse_args()

    if len(args) != 1 :
        parser.print_help()
        exit(-1)

    filename = args[0]
    
    if options.list :
        printFileContents( filename )
        exit(0)
    
    runFitModelToData( filename     ,
                       options.ws   ,
                       options.pdf  ,
                       options.data ,
                       options.outws,
                       options.debug
                       )

# -----------------------------------------------------------------------------
