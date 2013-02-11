#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC fit for the CP asymmetry observables        #
#   in Bs -> Ds K                                                             #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBs2DsKCPAsymmObsFitterOnData.py [-d -s]                      #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#   Author: Manuel Schiller                                                   #
#   Author: Agnieszka Dziurda                                                 #
#   Author: Vladimir Vava Gligorov                                            #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from math     import pi
import sys,os
#import GaudiPython
#GaudiPython.loaddict( 'B2DXFittersDict' )

#GeneralUtils = GaudiPython.gbl.GeneralUtils
#Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# MODELS

AcceptanceFunction       =  'PowLawAcceptance'#BdPTAcceptance'  # None/BdPTAcceptance/DTAcceptanceLHCbNote2007041

# MISCELLANEOUS
bName = 'B_{s}'

#------------------------------------------------------------------------------
def setConstantIfSoConfigured(var,myconfigfile) :
    if var.GetName() in myconfigfile["constParams"] : var.setConstant()

#------------------------------------------------------------------------------
def runBdGammaFitterOnData(debug, wsname, initvars, var, probvar, pereventmistag,
                           toys, pathName, treeName, configName, fitMeTool, scan, signal ) :

    # BLINDING
    Blinding =  False
    
    #if not Blinding and not toys :
    #    print "RUNNING UNBLINDED!"
    #    really = input('Do you really want to unblind? ')
    #    if really != "yes" :
    #        sys.exit(0)     

    import GaudiPython

    GaudiPython.loaddict('B2DXFittersDict')

    from B2DXFitters import taggingutils, cpobservables

    GeneralModels = GaudiPython.gbl.GeneralModels
    PTResModels   = GaudiPython.gbl.PTResModels

    GeneralUtils = GaudiPython.gbl.GeneralUtils
    SFitUtils = GaudiPython.gbl.SFitUtils
    Bs2Dsh2011TDAnaModels = GaudiPython.gbl.Bs2Dsh2011TDAnaModels
    
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay
    from ROOT import RooGaussModel, RooTruthModel
    from ROOT import RooAbsReal, RooDataSet
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooSimultaneous
    from ROOT import RooExponential, RooPolynomial, RooPolyVar, RooUniform
    from ROOT import RooFit,Inverse,RooBDecay
    from ROOT import FitMeTool, IfThreeWay, Dilution, IfThreeWayPdf
    from ROOT import CombBkgPTPdf,RooUniformBinning,TFile,TTree,RooDataHist
    from ROOT import BdPTAcceptance, PowLawAcceptance,RooHistFunc
    from ROOT import TString, RooEffProd,RooBinnedPdf, RooMsgService
    from ROOT import NULL, gSystem,RooUniformBinning
    from ROOT import RooUnblindCPAsymVar, RooUnblindPrecision
    from ROOT import RooNLLVar, RooMinuit, RooProfileLL, RooWorkspace    
    from ROOT import kRed, TCanvas,RooEffResModel,MistagCalibration
    
   
    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option] 
    print "=========================================================="
 
    # tune integrator configuration

    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','20Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)

    
    tVarTS         = TString(var)
    tProbVarTS     = TString(probvar)
    tagVarTS       = TString("lab0_BsTaggingTool_TAGDECISION_OS")
    tagWeightVarTS = TString("lab0_BsTaggingTool_TAGOMEGA_OS")
    idVarTS        = TString("lab1_ID") 

    if ( not toys ) and (not signal):
        workspace = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName), TString(treeName),
                                                   myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                   tVarTS, tagVarTS, tagWeightVarTS, idVarTS, debug)
    elif ( toys ) and (not signal):
        workspace = SFitUtils.ReadDataFromSWeightsToys(TString("DsPi"),TString(pathName), TString(treeName),
                                                       myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                       tVarTS, tagVarTS+TString("_idx"),
                                                       tagWeightVarTS, idVarTS+TString("_idx"),debug)
    elif (signal) and (not toys):    
        workNameTS = TString("workspace")
        workspace = GeneralUtils.LoadWorkspace(TString(pathName),workNameTS, debug)
                                                                                            
    workspace.Print()
    
    zero = RooConstVar('zero', '0', 0.)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)

    if ( not toys ):
        time = GeneralUtils.GetObservable(workspace,tVarTS, debug)
        tag  = GeneralUtils.GetObservable(workspace,tagVarTS, debug)
        mistag = GeneralUtils.GetObservable(workspace,tagWeightVarTS, debug)
        id = GeneralUtils.GetObservable(workspace,idVarTS, debug) 
    else:
        time = GeneralUtils.GetObservable(workspace,tVarTS, debug)
        tag  = GeneralUtils.GetObservable(workspace,tagVarTS+TString("_idx"), debug)
        mistag = GeneralUtils.GetObservable(workspace,tagWeightVarTS, debug)
        id = GeneralUtils.GetObservable(workspace,idVarTS+TString("_idx"), debug)
                                
    mass = RooRealVar('mass', '%s mass' % bName, 5., 6.)
    timeerr = RooRealVar('timeerr', '%s decay time error' % bName, 0.04, 0.001, 0.1, 'ps')
      
    gammas = RooRealVar('Gammas', '%s average lifetime' % bName, myconfigfile["Gammas"], 0., 5., 'ps^{-1}')
    setConstantIfSoConfigured(gammas,myconfigfile)
    deltaGammas = RooRealVar('deltaGammas', 'Lifetime difference', myconfigfile["DeltaGammas"], -1., 1., 'ps^{-1}')
    setConstantIfSoConfigured(deltaGammas,myconfigfile)

    deltaMs = RooRealVar('DeltaMs', '#Delta m_{s}', myconfigfile["DeltaMs"], 1., 30., 'ps^{-1}')
    deltaMs.setError(0.5)
    setConstantIfSoConfigured(deltaMs,myconfigfile)
    if deltaMs.GetName() in myconfigfile["constParams"] :
        Blinding = False

    # tagging
    # -------
    tagEffSig = RooRealVar('tagEffSig', 'Signal tagging efficiency'    , myconfigfile["TagEffSig"], 0., 1.)
    setConstantIfSoConfigured(tagEffSig,myconfigfile)
    
    tagOmegaSig = RooRealVar('tagOmegaSig', 'Signal mistag rate'    , myconfigfile["TagOmegaSig"], 0., 1.)
                        
    setConstantIfSoConfigured(tagOmegaSig,myconfigfile)

    # Define the observables
    # ----------------------
    if pereventmistag : 
        observables = RooArgSet(time,tag,id,mistag)       
    else : 
        observables = RooArgSet(time,tag,id)
    
    # Data set
    #-----------------------
    if toys :
        data_pos = GeneralUtils.GetDataSet(workspace,"dataSet_time_Bs2DsPi_pos", debug)#[]
        data_neg = GeneralUtils.GetDataSet(workspace,"dataSet_time_Bs2DsPi_neg", debug)
        data = data_pos
        data.append(data_neg)
        nEntries = data.numEntries()#[]
    else :
        if signal:
            data = GeneralUtils.GetDataSet(workspace,"dataSetMCBsDsPi_both", debug)
        else:    
            data = GeneralUtils.GetDataSet(workspace,"dataSet_time_Bs2DsPi", debug)
        nEntries = data.numEntries()     
        frame = time.frame()
        data.plotOn(frame)
        canvas = TCanvas('frame','frame')
        frame.Draw()
        #canvas.GetPad(0).SetLogx()
        canvas.SaveAs('WTF.pdf')
        #return canvas

    # Decay time resolution model
    # ---------------------------
    if 'PEDTE' not in myconfigfile["DecayTimeResolutionModel"] :
        trm = PTResModels.getPTResolutionModel(myconfigfile["DecayTimeResolutionModel"],
                                               time, 'Bs', debug,myconfigfile["resolutionScaleFactor"], myconfigfile["resolutionMeanBias"])
    else :
        # the decay time error is an extra observable !
        observables.add( timeerr )
        trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', 0., 'ps' )
        trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', 1.37 )
        trm = RooGaussModel( 'GaussianWithGaussPEDTE', 'GaussianWithGausPEDTE',
                             time, trm_mean, trm_scale, timeerr )
    
    # Decay time acceptance function
    # ------------------------------
    if AcceptanceFunction and not (AcceptanceFunction == None or AcceptanceFunction == 'None'):
        if AcceptanceFunction == "BdPTAcceptance" :
            tacc_slope  = RooRealVar('tacc_slope'   , 'BdPTAcceptance_slope'    , myconfigfile["tacc_slope"]    , -100.0 , 100.0 )
            tacc_offset = RooRealVar('tacc_offset'  , 'BdPTAcceptance_offset'   , myconfigfile["tacc_offset"]   , -100.0 , 100.0 )
            tacc_beta   = RooRealVar('tacc_beta'    , 'BdPTAcceptance_beta'     , myconfigfile["tacc_beta"]     , -10.00 , 10.00 )
            tacc = BdPTAcceptance('BsPTAccFunction', '%s decay time acceptance function' % bName,
                                  time, tacc_beta, tacc_slope, tacc_offset)
            setConstantIfSoConfigured(tacc_slope,myconfigfile)
            setConstantIfSoConfigured(tacc_offset,myconfigfile)
            setConstantIfSoConfigured(tacc_beta,myconfigfile)
        elif AcceptanceFunction == 'PowLawAcceptance' :
            tacc_beta       = RooRealVar('tacc_beta'    , 'PowLawAcceptance_beta',      myconfigfile["tacc_beta"]       , 0.00 , 0.15) 
            tacc_exponent   = RooRealVar('tacc_exponent', 'PowLawAcceptance_exponent',  myconfigfile["tacc_exponent"]   , 1.00 , 4.00)
            tacc_offset     = RooRealVar('tacc_offset'  , 'PowLawAcceptance_offset',    myconfigfile["tacc_offset"]     , -0.2 , 0.10)
            tacc_turnon     = RooRealVar('tacc_turnon'  , 'PowLawAcceptance_turnon',    myconfigfile["tacc_turnon"]     , 0.50 , 5.00)  
            tacc          = PowLawAcceptance('BsPowLawAcceptance', '%s decay time acceptance function' % bName,
                                                tacc_turnon, time, tacc_offset, tacc_exponent, tacc_beta)
            setConstantIfSoConfigured(tacc_beta,myconfigfile)
            setConstantIfSoConfigured(tacc_exponent,myconfigfile)
            setConstantIfSoConfigured(tacc_offset,myconfigfile)
            setConstantIfSoConfigured(tacc_turnon,myconfigfile)
            
    else :
        tacc = None
    
    sigTagWeight = RooFormulaVar("sigTagWeight",'(1-abs(@0)) + (2*abs(@0)-1)*@1',RooArgList(tag,tagEffSig))

    sigC = RooRealVar('C', 'C coeff.', 1.)
    sigS = RooRealVar('S', 'S coeff.', 0.)
    sigD = RooRealVar('D', 'D coeff.', 0.)
    sigSbar = RooRealVar('Sbar', 'Sbar coeff.', 0.)
    sigDbar = RooRealVar('Dbar', 'Dbar coeff.', 0.)
    
    sigWeightedDs = IfThreeWay('sigWeightedDs', 'sigWeightedDs', id, sigD, zero, sigDbar)
    # the following includes the minus sign in front of the sin term
    sigWeightedSs = IfThreeWay('sigWeightedSs', 'sigWeightedSs', id, sigSbar, zero, sigS)
    
    untaggedWeight = IfThreeWay('untaggedWeight', 'untaggedWeight', tag, one, two, one)
    if not pereventmistag : 
        sigDilution = Dilution('sigDilution', 'signal (DsPi) Dilution', tagOmegaSig)
    else : 
        sigDilution = RooFormulaVar('sigDilution',"(1-2*@0)",RooArgList(mistag))
    mixState = RooFormulaVar('mixState','@0*@1',RooArgList(tag,id)) 
    sigCosSin_i0 = RooProduct('sigCosSin_i0', 'sigCosSin_i0', RooArgSet(mixState, sigDilution, sigTagWeight))

    sigCosh = RooProduct('sigCosh', 'cosh coefficient', RooArgSet(untaggedWeight, sigTagWeight))
    sigSinh = RooProduct('sigSinh', 'sinh coefficient', RooArgSet(sigCosh, sigWeightedDs))
    sigCos  = RooProduct('sigCos', 'cos coefficient', RooArgSet(sigCosSin_i0, sigC))
    sigSin  = RooProduct('sigSin', 'sin coefficient', RooArgSet(sigCosSin_i0, sigWeightedSs))
   
    if not fitMeTool : 

        tauinv          = Inverse( "tauinv","tauinv", gammas)
        time_noacc      = RooBDecay('time_signal_noacc','time_signal_noacc', time, tauinv, deltaGammas, 
                                            sigCosh, sigSinh,sigCos, sigSin,
                                            deltaMs,trm, RooBDecay.SingleSided)

        sigTimePDF      = RooEffProd('time_signal','time_signal',time_noacc,tacc)
            
        totPDF = sigTimePDF
 
        if debug :
            print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!' 
            data.Print("v")
            for i in range(0,nEntries) : 
                data.get(i).Print("v")
                print data.weight()

        if scan:
            RooMsgService.instance().Print('v')
            RooMsgService.instance().deleteStream(1002)
            if debug:
                print "Likelihood scan performing"
            nll= RooNLLVar("nll","-log(sig)",totPDF,data, RooFit.NumCPU(4), RooFit.Silence(True))
            pll  = RooProfileLL("pll",  "",  nll, RooArgSet(deltaMs))
            h = pll.createHistogram("h",deltaMs,RooFit.Binning(200))
            h.SetLineColor(kRed)
            h.SetLineWidth(2)
            h.SetTitle("Likelihood Function - Delta Ms")
            like = TCanvas("like", "like", 1200, 800)
            like.cd()
            h.Draw()
            like.Update()
            n = TString("likelihood_Delta_Ms.pdf")
            like.SaveAs(n.Data())
            exit(0)
             
        if toys or not Blinding: #Unblind yourself
            myfitresult = totPDF.fitTo(data, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),\
                                             RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult.Print("v")
            myfitresult.correlationMatrix().Print()
            myfitresult.covarianceMatrix().Print()
        else :    #Don't
            myfitresult = totPDF.fitTo(data, RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),\
                                             RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            print 'Matrix quality is',myfitresult.covQual()
            par = myfitresult.floatParsFinal() 
            par[0].Print("v") 

        workout = RooWorkspace("workspace","workspace")
        getattr(workout,'import')(data)
        getattr(workout,'import')(totPDF)
        getattr(workout,'import')(myfitresult)
        workout.writeToFile(wsname)
    else :
        if 'PEDTE' not in myconfigfile["DecayTimeResolutionModel"] :
            sigTimePDF = GeneralModels.buildRooBDecayPDF(
                time, gammas, deltaGammas, deltaMs,
                sigCosh, sigSinh, sigCos, sigSin,
                trm, tacc,
                'Sig', bName, debug)
        else :
            sigTimePDF = GeneralModels.buildRooBDecayPDFWithPEDTE(
                time, timeerr, gammas, deltaGammas, deltaMs,
                sigCosh, sigSinh, sigCos, sigSin,
                terrpdf, trm, tacc,
                'Sig', bName, debug)
    
        if debug :
            print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!' 
            data.Print("v")
            for i in range(0,nEntries) : 
                data.get(i).Print("v")
                print data.weight()
    
        totPDF = sigTimePDF
                    
        fitter = FitMeTool(debug)
    
        fitter.setObservables(observables)
        fitter.setModelPDF(totPDF)
        fitter.setData(data)
    
        plot_init   = (wsname != None) and initvars
        plot_fitted = (wsname != None) and (not initvars)
    
        if plot_init :
            fitter.saveModelPDF(wsname)
            fitter.saveData(wsname)
            
        
        if scan:
            RooMsgService.instance().Print('v')
            RooMsgService.instance().deleteStream(1002)
            if debug:
                print "Likelihood scan performing"
            nll= RooNLLVar("nll","-log(sig)",totPDF,data, RooFit.NumCPU(4))
            pll  = RooProfileLL("pll",  "",  nll, RooArgSet(deltaMs))
            h = pll.createHistogram("h",deltaMs,RooFit.Binning(100))
            h.SetLineColor(kRed)
            h.SetLineWidth(2)
            h.SetTitle("Likelihood Function - Delta Ms")
            like = TCanvas("like", "like", 1200, 800)
            like.cd()
            h.Draw()
            like.Update()
            n = TString("likelihood_Delta_Ms.pdf")
            like.SaveAs(n.Data())
            exit(0)
    
        if toys or not Blinding: #Unblind yourself
            fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2), RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult = fitter.getFitResult()
            myfitresult.Print("v")
        else :    #Don't
            fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2), RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            myfitresult = fitter.getFitResult()
            print 'Matrix quality is',myfitresult.covQual()
            par = myfitresult.floatParsFinal() 
            par[0].Print("v") 
    
                            
    
        if plot_fitted :
            fitter.saveModelPDF(wsname)
            fitter.saveData(wsname)
            
        del fitter
        
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser(_usage)

parser.add_option('-d', '--debug',
                  dest    = 'debug',
                  default = False,
                  action  = 'store_true',
                  help    = 'print debug information while processing'
                  )
parser.add_option('-s', '--save',
                  dest    = 'wsname',
                  metavar = 'WSNAME',
                  default = 'WS_Time_DsPi.root',  
                  help    = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                  )
parser.add_option('-i', '--initial-vars',
                  dest    = 'initvars',
                  default = False,
                  action  = 'store_true',
                  help    = 'save the model PDF parameters before the fit (default: after the fit)'
                  )

parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_LifetimeFit_ctau',
                   help = 'set observable '
                   )

parser.add_option( '-c', '--cutvariable',
                   dest = 'ProbVar',
                   default = 'lab1_PIDK',
                   help = 'set observable for PID '
                   )


parser.add_option( '--pereventmistag',
                   dest = 'pereventmistag',
                   default = False,
                   action = 'store_true',
                   help = 'Use the per-event mistag?'
                   )

parser.add_option( '-t','--toys',
                   dest = 'toys',
                   action = 'store_true', 
                   default = False,
                   help = 'are we working with toys?'
                   )
parser.add_option( '--signal',
                   dest = 'signal',
                   action = 'store_true',
                   default = False,
                   help = 'are we working with signal MC?'
                   )

parser.add_option( '--pathName',
                   dest = 'pathName',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsPi_all_both.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--treeName',
                   dest = 'treeName',
                   default = 'merged',
                   help = 'name of the workspace'
                   )
parser.add_option( '--scan',
                   dest = 'scan',
                   default = False,
                   action = 'store_true'
                   )
                   
parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsPiConfigForNominalDMSFitPowLaw')

parser.add_option( '--fitMeTool',
                    dest = 'fitMeTool',
                    action = 'store_true',
                    default = False)

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    (options, args) = parser.parse_args()

    if len(args) > 0 :
        parser.print_help()
        exit(-1)

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    print options
    print "=========================================================="

    import sys
    sys.path.append("../data/")  
 
    runBdGammaFitterOnData( options.debug,
                            options.wsname,
                            options.initvars,
                            options.var, 
                            options.ProbVar, 
                            options.pereventmistag,
                            options.toys,
                            options.pathName,
                            options.treeName,
                            options.configName,
                            options.fitMeTool,
                            options.scan,
                            options.signal)

# -----------------------------------------------------------------------------
