#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC Delta m_d fit for Bd -> D pi                #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBdDeltaMFitterToyMC.py <toy_number> [-d | --debug]           #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 30 / 05 / 2011                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# MODELS
signalModelOnly =  True
propertimeResolutionModel  =  'Gaussian'           # truth/Gaussian/DoubleGaussian
acceptanceFunction         =  'BdPTAcceptance'     # None/BdPTAcceptance/RooAcceptance

# BLINDING
blinding =  False

# PHYSICAL PARAMETERS
Gammad      =  0.656   # in ps^{-1}
DeltaGammad =  0.      # in ps^{-1}
DeltaMd     =  0.507   # in ps^{-1}

# TOY PARAMETERS
# If doing an extended likelihood fit
nSigEvts      =  5980      # signal events
nCombBkgEvts  =  3625      # combinatorial background events
nBd2DKEvts    =  198       # Bd -> D K   phys. bkg. events
# Parameters for the combinatorial background PDF in time
CombBkgPdf_a      =  0.1209
CombBkgPdf_f      =  0.996
CombBkgPdf_alpha  =  4.149
CombBkgPdf_beta   =  1.139
# Tagging
SigTagEff    =  0.221
BkgTagEff    =  0.274
SigTagOmega  =  0.314
BkgTagOmega  =  0.481

# MISCELLANEOUS
bName = 'B_{d}'


#------------------------------------------------------------------------------
def runBdDeltaMFitterToyMC( toy_num, debug ) :
    
    time = RooRealVar( "time", "%s propertime" % bName, 0., 0., 8., 'ps' )
    
    gamma = RooRealVar( "Gamma", "%s average lifetime" % bName, Gammad, 0., 5., 'ps^{-1}' )
    deltaGamma = RooRealVar( 'deltaGamma', 'Lifetime difference', DeltaGammad, 'ps^{-1}' )
    
    # "BLINDING" settings
    # -------------------
    deltaM_bs = RooCategory( "deltaM_blind_state", "DeltaM blinding State" )
    deltaM_bs.defineType( "Unblind", 0 )
    deltaM_bs.defineType( "Blind"  , 1 )
    if blinding :
        deltaM_bs.setLabel( "Blind" )
    else :
        deltaM_bs.setLabel( "Unblind" )
    
    #deltaM_ub = RooRealVar( "DeltaMd", "#Delta m_{d}", DeltaMd, 0.1, 0.9, "ps^{-1}" )
    deltaM = RooRealVar( "deltaMd", "#Delta m_{d}", DeltaMd, 0.1, 0.9, "ps^{-1}" )
    #deltaM  = blindValue( deltaM_ub, deltaM_bs, "blinded" )

    # tagging
    # -------
    sigTagEff = RooRealVar( "sigTagEff", "Signal tagging efficiency"    , SigTagEff, 0., 1. )
    bkgTagEff = RooRealVar( "bkgTagEff", "Background tagging efficiency", BkgTagEff, 0., 1. )
    sigTagOmega = RooRealVar( "sigTagOmega", "Signal mistag rate"    , SigTagOmega, 0., 0.5 )
    bkgTagOmega = RooRealVar( "bkgTagOmega", "Background mistag rate", BkgTagOmega, 0., 0.5 )

    mixState = RooCategory( 'mixstate_global', 'B/Bbar mixing state' )
    mixState.defineType( "unmixed" ,  1 )
    mixState.defineType( "mixed"   , -1 )
    mixState.defineType( "untagged",  0 )
    
    observables = RooArgSet( time, mixState )
    
    # Propertime resolution model
    # ---------------------------
    BdPTRM = PTResModels.getPTResolutionModel( propertimeResolutionModel,
                                               time, 'Bd', debug )
    
    # Propertime acceptance function
    # ------------------------------
    if acceptanceFunction :
        slope = RooRealVar( "BdPTAcc_slope" , "BdPTAcceptance_slope_sig" , 2.36 )
        offset = RooRealVar( "BdPTAcc_offset", "BdPTAcceptance_offset_sig", 0.2 )
        BdPTAcc = BdPTAcceptance( "BdPTAcc", "Bd propertime acceptance function",
                                  time, slope, offset )
    else :
        BdPTAcc = None

    # Signal EPDF
    # -----------
    nSig = RooRealVar( 'nSigEvts', 'nSigEvts', nSigEvts )
    # The 4 coefficients of the B decay rate equations ( q = mixState )
    # Weight : |q|*eff_tag + (1-|q|)*(1-eff_tag)
    #        = 1 - eff_tag for untagged events (q=0)
    #        = eff_tag     for tagged   events (q=+/-1)
    sigTagWeight = taggingutils.tagEfficiencyWeight( mixState, sigTagEff, 'Sig' )
    sigSin  = RooConstVar( "sigSin",  "sin coefficient",  0. )
    sigSinh = RooConstVar( "sigSinh", "sinh coefficient", 0. )
    sigCosh = RooFormulaVar( "sigCosh", "(2-abs(@0))*@1",
                             RooArgList( mixState, sigTagWeight ) )
    sigCosh.SetTitle( "cosh coefficient" )
    sigCos  = RooFormulaVar( "sigCcos", "@0*(1-2*@1)*@2",
                             RooArgList( mixState, sigTagOmega, sigTagWeight ) )
    sigCos.SetTitle( "cos coefficient" )
    sigPDF = GeneralModels.buildRooBDecayEPDF( time, gamma, deltaGamma, deltaM,
                                               sigCosh, sigSinh, sigCos, sigSin,
                                               BdPTRM, BdPTAcc,
                                               nSig,
                                               'Sig', bName, debug )
    
    # Create the combinatorial background EPDF
    # ----------------------------------------
    nCombBkg         = RooRealVar( 'nCombBkgEvts'  , 'nCombBkgEvts' , nCombBkgEvts )
    combBkgPdf_a     = RooRealVar( "CombBkgPdf_a"    , "CombBkgPdf_a"    , CombBkgPdf_a     )
    combBkgPdf_f     = RooRealVar( "CombBkgPdf_f"    , "CombBkgPdf_f"    , CombBkgPdf_f     )
    combBkgPdf_alpha = RooRealVar( "CombBkgPdf_alpha", "CombBkgPdf_alpha", CombBkgPdf_alpha )
    combBkgPdf_beta  = RooRealVar( "CombBkgPdf_beta" , "CombBkgPdf_beta" , CombBkgPdf_beta  )
    combBkgPDF_tdist = CombBkgPTPdf( 'CombBkgPdf_t', 'CombBkgPdf_t',
                                     time,
                                     combBkgPdf_a, combBkgPdf_f,
                                     combBkgPdf_alpha, combBkgPdf_beta
                                     )
    # The 4 coefficients of the B decay rate equations ( q = mixState )
    # Weight : |q|*eff_tag + (1-|q|)*(1-eff_tag)
    #        = 1 - eff_tag for untagged events (q=0)
    #        = eff_tag     for tagged   events (q=+/-1)
    bkgTagWeight = taggingutils.tagEfficiencyWeight( mixState, bkgTagEff, 'Bkg' )
    # bkgWeight = new RooFormulaVar( "bkgWeight", "((1+@0)*@1+(1-@0)*(1-@1))*@2",
    #                                 RooArgList( *m_mixState, *m_bkgTagOmega, *m_bkgTagWeight ) );
    # Tag PDF reads:
    #    q = 0  : 1 - eff_tag
    #    q = +1 : omega_tag * eff_tag
    #    q = -1 : ( 1 - omega_tag ) * eff_tag
    combBkgPDF_tag = RooGenericPdf( 'CombBkgPDF_tag', 'CombBkgPDF_tag',
                                    '0.5*(2-abs(@0))*((1+@0)*@1+(1-@0)*(1-@1))*@2',
                                    RooArgList( mixState, bkgTagOmega, bkgTagWeight ) )
    combBkgPDF = RooProdPdf( 'CombBkgPDF_t', 'CombBkgPDF_t',
                             combBkgPDF_tdist, combBkgPDF_tag )
    combBkgEPDF = RooExtendPdf( "CombBkgEPDF_t",
                                "Combinatorial background EPDF in propertime",
                                combBkgPDF, nCombBkg )
    
    # Create the Bd -> D K physical background EPDF
    # ---------------------------------------------
    nBd2DK    = RooRealVar( 'nBd2DKEvts', 'nBd2DKEvts', nBd2DKEvts )
    Bd2DKSin  = RooRealVar( "Bd2DKSin",  "sin coefficient",  0. )
    Bd2DKSinh = RooRealVar( "Bd2DKSinh", "sinh coefficient", 0. )
    Bd2DKCosh = RooFormulaVar( 'Bd2DK_coeff_cosh', '(2-abs(@0))*@1', 
                               RooArgList( mixState, sigTagWeight ) )
    Bd2DKCosh.SetTitle( "cosh coefficient" )
    Bd2DKCos  = RooFormulaVar( "Bd2DKCos", "@0*(1-2*@1)*@2",
                               RooArgList( mixState, sigTagOmega, sigTagWeight ) )
    Bd2DKCos.SetTitle( "cos coefficient" )
    Bd2DKPDF = GeneralModels.buildRooBDecayEPDF( time, gamma, deltaGamma, deltaM,
                                                 Bd2DKCosh, Bd2DKSinh, Bd2DKCos, Bd2DKSin,
                                                 BdPTRM, BdPTAcc,
                                                 nSig,
                                                 'Bd2DK', bName, debug )
    
    # Create the total EPDF
    # ---------------------
    totPDF = RooAddPdf( 'TotEPDF_t', 'Model (signal & background) EPDF in time',
                        RooArgList( sigPDF, combBkgEPDF, Bd2DKPDF ) )
    
    # Instantiate and run the fitter in toy MC mode
    fitter = FitMeTool( toy_num, debug )
    
    fitter.setObservables( observables )
    
    if signalModelOnly :
        fitter.setModelPDF( sigPDF )
    else :
        fitter.setModelPDF( totPDF )
    
    fitter.generate()
    fitter.getData().table( mixState ).Print( 'v' )
    
    plot_init   = options.initvars         and ( options.wsname != None )
    plot_fitted = ( not options.initvars ) and ( options.wsname != None )
    
    if plot_init :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData( options.wsname )
    
    fitter.fit( True, RooFit.NumCPU( 4 ), RooFit.Strategy( 2 ), RooFit.Timer() )
    
    if plot_fitted :
        fitter.saveModelPDF( options.wsname )
        fitter.saveData( options.wsname )
    
    del fitter

#------------------------------------------------------------------------------
_usage = '%prog [options] <toy_number>'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   help = 'print debug information while processing'
                   )
parser.add_option( '-s', '--save',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )
parser.add_option( '-i', '--initial-vars',
                   dest = 'initvars',
                   action = 'store_true',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) != 1 :
        parser.print_help()
        exit( -1 )
    
    try:
        TOY_NUMBER = int( args[ 0 ] )
    except ValueError:
        parser.error( 'The toy number is meant to be an integer ;-)!' )

    DEBUG = True if options.debug else False

    import GaudiPython
    
    GaudiPython.loaddict( 'B2DXFittersDict' )
    
    from B2DXFitters import taggingutils
    
    GeneralModels = GaudiPython.gbl.GeneralModels
    PTResModels   = GaudiPython.gbl.PTResModels

    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooCategory
    from ROOT import RooArgSet, RooArgList, RooConstVar
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf
    from ROOT import RooFit
    from ROOT import FitMeTool
    from ROOT import CombBkgPTPdf
    from ROOT import BdPTAcceptance
    
    runBdDeltaMFitterToyMC( TOY_NUMBER, DEBUG )

# -----------------------------------------------------------------------------
