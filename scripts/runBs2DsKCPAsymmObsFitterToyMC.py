#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC fit for the CP asymmetry observables        #
#   in Bs -> Ds K                                                             #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBs2DsKCPAsymmObsFitterToyMC.py <toy_number> [-d | --debug]   #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from math     import pi

import GaudiPython
import ROOT
ROOT.gSystem.Load('libRooFitCore')
ROOT.gSystem.Load('libRooFit')
from ROOT import RooFit
GaudiPython.loaddict('B2DXFittersDict')

# -----------------------------------------------------------------------------
# Configuration settings
#
# defaultConfig contains default settings
# generatorConfig contains settings to use during generation
# fitConfig contains settings to use during fit
#
# fitConfig and generatorConfig can be updated to suit your needs
# there are two ways: either by inserting code below (see example), or by
# using job options (which take a string or a file with python code which
# must evaluate to a dictionary)
# -----------------------------------------------------------------------------
defaultConfig = {
	'SignalModelOnly':		False,
	'DoDsK':			True,
	'DoDsPi':			True,
	# truth/Gaussian/DoubleGaussian/GaussianWithPEDTE/GaussianWithLandauPEDTE/GaussianWithScaleAndPEDTE
	'DecayTimeResolutionModel':	'Gaussian',
	# None/BdPTAcceptance/DTAcceptanceLHCbNote2007041
	'AcceptanceFunction':		'BdPTAcceptance',
	'PerEventMistag': 		False,
	'UseKFactor':			False,

	# BLINDING
	'Blinding':			False,

	# PHYSICAL PARAMETERS
	'Gammad':			0.656, # in ps^{-1}
	'Gammas':			0.679, # in ps^{-1}
	'DeltaGammad':			0.,    # in ps^{-1}
	'DGsOverGs':			-0.17629, # DeltaGammas / Gammas
	'DeltaMd':			0.507, # in ps^{-1}
	'DeltaMs':			17.77, # in ps^{-1}

	# TOY PARAMETERS
	# If doing an extended likelihood fit
	'NSigEvts':			1600, # signal events
	'NBs2DsPiEvts':			 800, # Bs -> Ds pi phys. bkg. events
	'NCombBkgEvts':			4000, # combinatorial background events
	# Parameters for the combinatorial background PDF in mass
	'MPDFCombBkg_shape':		-4.,
	# Parameters for the combinatorial background PDF in time
	'TPDFCombBkg_a':		0.1209,
	'TPDFCombBkg_f':		0.996,
	'TPDFCombBkg_alpha':		4.149,
	'TPDFCombBkg_beta':		1.139,
	# Tagging
	'TagEffSig':			0.6123,
	'TagOmegaSig':			0.3696,
	'TagEffBkg':			0.200,
	'TagOmegaBkg':			0.480,
	# CP observables
	'StrongPhase':			0. / 180. * pi,
	'WeakPhase':			70. / 180. * pi,
	'ModLf':			0.372,
	# list of constant parameters
	'constParams': [
	    'Gammas', 'deltaGammas', 'deltaMs',
	    'tagOmegaSig',
	    'tagEffSig', 'tagOmegaBkg', 'tagEffBkg'
	    ],
	# acceptance parameters
	'BdPTAcceptance_slope': 2.36,
	'BdPTAcceptance_offset': 0.2,
	'BdPTAcceptance_beta': 0.0,

	# fitter on speed: binned PDFs
	'NBinsAcceptance':		100,   # if >0, bin acceptance
	'NBinsTimeKFactor':		200,   # if >0, use binned cache for k-factor integ.
	'NBinsMistag':			0,   # if >0, parametrize Mistag integral
	'NBinsProperTime':		0,   # if >0, parametrize proper time int.
	}

# MISCELLANEOUS
bName = 'B_{s}'

#------------------------------------------------------------------------------
def setConstantIfSoConfigured(config, obj):
    from ROOT import RooAbsPdf
    if obj.InheritsFrom(RooAbsPdf.Class()):
	i = obj.getVariables().iterator()
	o = i
	while None != o:
	    o = i.Next()
	    if None != o:
		setConstantIfSoConfigured(config, o)
    else:
	if obj.GetName() in config['constParams']:
	    obj.setConstant(True)

# "swallow" object into a workspace, returns swallowed object
def WS(ws, obj, opts = [RooFit.RecycleConflictNodes()]):
    name = obj.GetName()
    if obj.InheritsFrom('RooAbsArg') or obj.InheritsFrom('RooDataSet'):
        if len(opts) > 0:
            ws.__getattribute__('import')(obj, *opts)
        else:
            ws.__getattribute__('import')(obj)
    else:  
            ws.__getattribute__('import')(obj, name)
    return ws.obj(name)

# build B decay time pdf
def buildBDecayTimePdf(
        config,					# config dictionary
	name,					# 'Signal', 'DsPi', ...
	ws,					# RooWorkspace into which to put the PDF
	time, timeerr, qt, qf, mistag, tageff,	# potential observables
	Gamma, DeltaGamma, DeltaM,		# decay parameters
	C, D, Dbar, S, Sbar,			# CP parameters
	timeresmodel = None,			# decay time resolution model
	acceptance = None,			# acceptance function
	timeerrpdf = None,			# pdf for per event time error
	mistagpdf = None,			# pdf for per event mistag
	kfactorpdf = None,			# distribution k factor smearing
	kvar = None,				# variable k which to integrate out

	nBinsMistag = 64,		# parameterize time integral in bins of mistag
	nBinsPerEventTimeErr = 64,	# parameterize time integral in bins of time err
	nBinsAcceptance = 200,		# approximate acceptance function in bins
	nBinsTimeKfactor = 200		# binned time cache when using k-factor
	):
    # Look in LHCb-INT-2011-051 for the conventions used
    from ROOT import ( RooConstVar, TagEfficiencyWeight, IfThreeWayCat,
	    Dilution, RooProduct, RooTruthModel, RooGaussModel, Inverse,
	    RooBDecay, RooProdPdf, RooBinnedPdf, RooEffResModel, RooEffProd,
	    RooUniformBinning, RooArgSet, RooFit, RooWorkspace,
	    RooGeneralisedSmearingBase, RooPolyVar, RooArgList,
            IfThreeWayCatPdf, RooAbsPdf )
    RooNumGenSmearPdf = RooGeneralisedSmearingBase(RooAbsPdf)

    # constants used
    zero = WS(ws, RooConstVar('zero', 'zero', 0.))
    one = WS(ws, RooConstVar('one', 'one', 1.))
    two = WS(ws, RooConstVar('two', 'two', 2.))
    minusone = WS(ws, RooConstVar('minusone', 'minusone', -1.))
    minustwo = WS(ws, RooConstVar('minustwo', 'minustwo', -2.))

    # if no time resolution model is set, fake one
    if timeresmodel == None:
	timeresmodel = WS(ws, RooTruthModel('%s_TimeResModel' % name,
	    '%s time resolution model' % name, time))
    elif timeresmodel == 'Gaussian':
	timeresmodel = WS(ws, RooGaussModel('%s_TimeResModel' % name,
	    '%s time resolution model' % name, time, zero, timeerr))

    # apply acceptance (if needed)
    if None != acceptance and 0 < nBinsAcceptance:
	# bin acceptance
	acceptanceBinning = WS(ws, RooUniformBinning(
	    time.getMin(), time.getMax(), nBinsAcceptance,
	    'acceptanceBinning'))
	time.setBinning(acceptanceBinning, 'acceptanceBinning')
	tacc = WS(ws, RooBinnedPdf(
	    "%sBinnedAcceptance" % acceptance.GetName(),
	    "%sBinnedAcceptance" % acceptance.GetName(),
	    time, 'acceptanceBinning', acceptance))
	tacc.setForceUnitIntegral(True)
	timeresmodel = WS(ws, RooEffResModel(
	    '%s_timeacc_%s' % (timeresmodel.GetName(), tacc.GetName()),
	    '%s plus time acceptance %s' % (timeresmodel.GetTitle(), tacc.GetTitle()),
	    timeresmodel, tacc))

    if not ('ManuelStyleCondPDF' in config):
        # intermediate tagging quantities
        tagWeight = WS(ws, TagEfficiencyWeight('%sTagEffWeight' % name,
		    '%s tag efficiency weight' % name, qt, tageff))
        untaggedWeight = WS(ws, IfThreeWayCat('%sUntaggedWeight' % name,
		    '%sUntaggedWeight' % name, qt, one, two, one))
        dilution = WS(ws, Dilution('%sDilution' % name, '%s Dilution' % name,
		    mistag))
        # intermediate terms for terms in from of cosh, sinh, cos, sin terms in
        # RooBDecay
        weightedDs = WS(ws, IfThreeWayCat('%sWeightedDs' % name,
		    '%sWeightedDs' % name, qf, D, zero, Dbar))
        # the following includes the minus sign in front of the sin term
        weightedSs = WS(ws, IfThreeWayCat('%sWeightedSs' % name,
		    '%sWeightedSs' % name, qf, Sbar, zero, S))
    
        cosSin_i0 = WS(ws, RooProduct('%sCosSin_i0' % name,
		    '%sCosSin_i0' % name, RooArgSet(qt, qf, dilution, tagWeight)))
    
        # terms to go into RooBDecay
        cosh = WS(ws, RooProduct('%sCosh' % name,
		    '%s cosh coefficient' % name, RooArgSet(untaggedWeight, tagWeight)))
        sinh = WS(ws, RooProduct('%sSinh' % name, '%s sinh coefficient' % name,
		    RooArgSet(cosh, weightedDs)))
        cos  = WS(ws, RooProduct('%sCos' % name, '%s cos coefficient' % name,
		    RooArgSet(cosSin_i0, C)))
        sin = WS(ws, RooProduct('%sSin' % name, '%s sin coefficient' % name,
		    RooArgSet(cosSin_i0, weightedSs)))
    else:
        doubleOneMinusTagEff = WS(ws, RooPolyVar(
            '%s_doubleOneMinusTagEff' % name, '%s_doubleOneMinusTagEff' % name,
            minustwo, RooArgList(two, tageff), 0));
        qtpdf = WS(ws, IfThreeWayCatPdf('%s_qtpdf' % name, '%s_qtpdf' % name,
            qt, tageff, doubleOneMinusTagEff, tageff))
        qfpdf = WS(ws, IfThreeWayCatPdf('%s_qfpdf' % name, '%s_qfpdf' % name,
            qf, one, zero, one))
        dilution = WS(ws, Dilution('%sDilution' % name, '%s Dilution' % name,
            mistag))
        # intermediate terms for terms in from of cosh, sinh, cos, sin terms in
        # RooBDecay
        weightedDs = WS(ws, IfThreeWayCat('%sWeightedDs' % name,
            '%sWeightedDs' % name, qf, D, zero, Dbar))
        # the following includes the minus sign in front of the sin term
        weightedSs = WS(ws, IfThreeWayCat('%sWeightedSs' % name,
            '%sWeightedSs' % name, qf, Sbar, zero, S))
    
        cosSin_i0 = WS(ws, RooProduct('%sCosSin_i0' % name,
            '%sCosSin_i0' % name, RooArgSet(qt, qf, dilution)))
    
        # terms to go into RooBDecay
        cosh = one
        sinh = weightedDs
        cos  = WS(ws, RooProduct('%sCos' % name, '%s cos coefficient' % name,
            RooArgSet(cosSin_i0, C)))
        sin = WS(ws, RooProduct('%sSin' % name, '%s sin coefficient' % name,
            RooArgSet(cosSin_i0, weightedSs)))

    # perform the actual k-factor smearing integral (if needed)
    # if we have to perform k-factor smearing, we need "smeared" variants of
    # Gamma, DeltaGamma, DeltaM
    if None != kfactorpdf and None != kvar:
	kGamma = WS(ws, RooProduct('%sKGamma' % name, '%s k * #Gamma' % name,
	    RooArgSet(kvar, Gamma)))
	kDeltaGamma = WS(ws, RooProduct('%sKDeltaGamma' % name,
	    '%s k * #Delta#Gamma' % name, RooArgSet(kvar, DeltaGamma)))
	kDeltaM = WS(ws, RooProduct('%sKDeltaM' % name,
	    '%s k * #Delta m' % name, RooArgSet(kvar, DeltaM)))
    else:
	# otherwise, we can get away with giving old variables new names
	kGamma, kDeltaGamma, kDeltaM = Gamma, DeltaGamma, DeltaM

    # perform the actual k-factor smearing integral (if needed)
    # build (raw) time pdf
    tau = WS(ws, Inverse('%sTau' % name, '%s #tau' % name, kGamma))
    rawtimepdf = WS(ws, RooBDecay('%s_RawTimePdf' % name,
	'%s raw time pdf' % name, time, tau, kDeltaGamma, cosh, sinh, cos, sin,
	kDeltaM, timeresmodel, RooBDecay.SingleSided))

    # perform the actual k-factor smearing integral (if needed)
    if None != kfactorpdf and None != kvar:
	krawtimepdf = WS(ws, RooNumGenSmearPdf('%s_kSmearedRawTimePdf' % name,
	    '%s raw time pdf smeared with k factor' % name,
	    kvar, rawtimepdf, kfactorpdf))
	center = WS(ws, RooConstVar(
	    '%s_kFactorCenter' % name, '%s_kFactorCenter' % name, 1.0))
	width = WS(ws, RooConstVar(
	    '%s_kFactorWidth' % name, '%s_kFactorWidth' % name, 0.005))
	# since we fine-tune the range of the k-factor distributions, and we
	# know that the distributions are well-behaved, we can afford to be a
	# little sloppy
	krawtimepdf.setConvolutionWindow(center, width, 1.0)
        krawtimepdf.convIntConfig().setEpsAbs(1e-9)
        krawtimepdf.convIntConfig().setEpsRel(1e-9)
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
        krawtimepdf.convIntConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
        krawtimepdf.convIntConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
        krawtimepdf.convIntConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
	if 0 < nBinsTimeKfactor:
	    kfactortimebinning = WS(ws, RooUniformBinning(     
		time.getMin(), time.getMax(), nBinsTimeKfactor,
		'%s_timeBinnedCache' % name))
	    krawtimepdf.setBinnedCache(time, kfactortimebinning, RooArgSet(qt, qf))
    else:
	krawtimepdf = rawtimepdf

    # figure out if we need a conditional pdf product for per event
    # decay time error or per event mistag
    if not ('ManuelStyleCondPDF' in config):
        condpdfs = [ ]
    else:
        condpdfs = [ qtpdf, qfpdf ]
    parameterizeSet =[ ]
    if None != mistagpdf:
	condpdfs.append(mistagpdf)
	if 0 < nBinsMistag:
	    parameterizeSet.append(mistag)
	    mistag.setBins(nBinsMistag, 'cache')
    if None != timeerrpdf:
	condpdfs.append(timeerrpdf)
	if 0 < nBinsPerEventTimeErr:
	    parameterizeSet.append(timeerr)
	    timeerr.setBins(nBinsPerEventTimeErr, 'cache')

    # perform conditional pdf product if needed
    if 0 < len(condpdfs):
	if 0 < len(parameterizeSet):
	    krawtimepdf.setParameterizeIntegral(RooArgSet(*parameterizeSet))
	retVal = WS(ws, RooProdPdf('%s_NoAccTimePdf' % name,
	    '%s no-acceptance time pdf', RooArgSet(*condpdfs),
	    RooFit.Conditional(RooArgSet(krawtimepdf),
		RooArgSet(time))))
    else:
	retVal = krawtimepdf
    
    if None != acceptance and 0 >= nBinsAcceptance:
	# do not bin acceptance
	retVal = WS(ws, RooEffProd('%s_TimePdf' % name,
	    '%s full time pdf' % name, retVal, acceptance))
    retVal.SetNameTitle('%s_TimePdf' % name, '%s full time pdf' % name)

    # return the copy of retVal which is inside the workspace
    return retVal

#------------------------------------------------------------------------------
def getMasterPDF(config, name, debug = False):
    from B2DXFitters import taggingutils, cpobservables

    GeneralModels = GaudiPython.gbl.GeneralModels
    PTResModels   = GaudiPython.gbl.PTResModels
    
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooMultiCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay
    from ROOT import RooGaussModel, RooTruthModel
    from ROOT import RooAbsReal, RooWorkspace, RooAbsArg
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf
    from ROOT import RooExponential, RooPolynomial, RooPolyVar, RooUniform
    from ROOT import RooFit, RooUniformBinning
    from ROOT import IfThreeWayCat, Dilution, IfThreeWayCatPdf
    from ROOT import CombBkgPTPdf, CPObservable
    from ROOT import BdPTAcceptance, MistagDistribution
    from ROOT import RooBinnedPdf, RooEffHistProd

    ws = RooWorkspace('WS_%s' % name)

    # tune integrator configuration
    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')

    zero = WS(ws, RooConstVar('zero', '0', 0.))
    one = WS(ws, RooConstVar('one', '1', 1.))
    minusone = WS(ws, RooConstVar('minusone', '-1', -1.))
    two = WS(ws, RooConstVar('two', '2', 2.))

    time = WS(ws, RooRealVar('time', '%s decay time' % bName,
		1., config['BdPTAcceptance_offset'], 10., 'ps'))
    mass = WS(ws, RooRealVar('mass', '%s mass' % bName, 5., 6.))
    timeerr = WS(ws, RooRealVar('timeerr', '%s decay time error' % bName,
	0.04, 0.001, 0.1, 'ps'))
    
    mBs = WS(ws, RooConstVar('mBs', 'Bs mass', 5.3663))
    mBsmisrec = WS(ws, RooConstVar('mBsmisrec', 'Bs mass', 5.3663 + 0.1))
    mWidth = WS(ws, RooConstVar('mWidth', 'mWidth', 0.03))
    mWidthmisrec = WS(ws, RooConstVar('mWidthmisrec', 'mWidthmisrec', 0.07))
    
    gammas = WS(ws, RooRealVar('Gammas', '%s average lifetime' % bName,
	config['Gammas'], 0., 5., 'ps^{-1}'))
    deltaGammas = WS(ws, RooRealVar('deltaGammas', 'Lifetime difference',
	config['DGsOverGs'] * config['Gammas'], -1., 1., 'ps^{-1}'))

    if config['UseKFactor']:
	k = WS(ws, RooRealVar('k', 'k factor', 1.))
        tiny = WS(ws, RooConstVar('tiny', 'tiny', 1e-3))
        kfactorpdf = WS(ws, RooGaussian('kfactorpdf', 'kfactorpdf', k, one, tiny))
    else:
        k = kfactorpdf = None
    
    # "BLINDING" settings
    # -------------------
    deltaM_bs = WS(ws, RooCategory('deltaM_blind_state', 'DeltaM blinding State'))
    deltaM_bs.defineType('Unblind', 0)
    deltaM_bs.defineType('Blind'  , 1)
    if config['Blinding']:
        deltaM_bs.setLabel('Blind')
    else :
        deltaM_bs.setLabel('Unblind')

    #deltaM_ub = WS(ws, RooRealVar('DeltaMs', '#Delta m_{s}',
    #    config['DeltaMs'], 0.1, 0.9, 'ps^{-1}'))
    deltaMs = WS(ws, RooRealVar('deltaMs', '#Delta m_{s}',
	config['DeltaMs'], 5., 30., 'ps^{-1}'))
    #deltaM  = WS(ws, blindValue(deltaM_ub, deltaM_bs, 'blinded'))

    # tagging
    # -------
    tagEffSig = WS(ws, RooRealVar(
	    'tagEffSig', 'Signal tagging efficiency',
	    config['TagEffSig'], 0., 1.))
    tagEffBkg = WS(ws, RooRealVar(
	    'tagEffBkg', 'Background tagging efficiency',
	    config['TagEffBkg'], 0., 1.))
    tagOmegaSig = WS(ws, RooRealVar(
	    'tagOmegaSig', 'Signal mistag rate',
	    config['TagOmegaSig'], 0., 1.))
    tagOmegaBkg = WS(ws, RooRealVar(
	'tagOmegaBkg', 'Background mistag rate',
	config['TagOmegaBkg'], 0., 1.))

    bTagMap = WS(ws, RooCategory('bTagMap', 'flavour tagging result'))
    bTagMap.defineType('B'       ,  1)
    bTagMap.defineType('Bbar'    , -1)
    bTagMap.defineType('Untagged',  0)

    fChargeMap = WS(ws, RooCategory('fChargeMap', 'bachelor charge'))
    fChargeMap.defineType('h+',  1)
    fChargeMap.defineType('h-', -1)

    # form a "raw combination" of bTagMap and fChargeMap
    decayPathRaw = WS(ws, RooMultiCategory("decayPathRaw", "decayPathRaw",
	    RooArgSet(bTagMap, fChargeMap)))
    # use the raw version to build a decayPath with a nice name
    decayPath = WS(ws, RooMappedCategory("decayPath", "decayPath",
	    decayPathRaw, 'NotMapped', 9000))
    decayPath.map('{B;h+}', 'Bs2Ds-K+', 1)
    decayPath.map('{B;h-}', 'Bs2Ds+K-', 2)
    decayPath.map('{Bbar;h+}', 'Bsbar2Ds-K+', 3)
    decayPath.map('{Bbar;h-}', 'Bsbar2Ds+K-', 4)
    decayPath.map('{Untagged;h+}', 'Untagged2Ds-K+', 5)
    decayPath.map('{Untagged;h-}', 'Untagged2Ds+K-', 6)

    mixState = WS(ws, RooMappedCategory('mixState', 'mixState = bTag * fCharge',
	    decayPathRaw, 'NotMapped', 9000))
    mixState.map('{B;h+}', "NotMixed", 1)
    mixState.map('{Bbar;h-}', "NotMixed", 1)
    mixState.map('{B;h-}', "Mixed", -1)
    mixState.map('{Bbar;h+}', "Mixed", -1)
    mixState.map('{Untagged;h*}', "Untagged", 0)

    # Define the observables
    # ----------------------
    observables = [ mass, time, bTagMap, fChargeMap ]

    # Decay time resolution model
    # ---------------------------
    if 'PEDTE' not in config['DecayTimeResolutionModel']:
        trm = WS(ws, PTResModels.getPTResolutionModel(
	    config['DecayTimeResolutionModel'],
	    time, 'Bs', debug))
    else :
        # the decay time error is an extra observable!
        observables.append(timeerr)
        # time, mean, scale, timeerr
        trm = WS(ws, RooGaussModel('GaussianWithLandauPEDTE',
	    'GaussianWithLandauPEDTE',
	    time, RooFit.RooConst(0.), RooFit.RooConst(1.), timeerr ))

    # Decay time acceptance function
    # ------------------------------
    if config['AcceptanceFunction'] and not (
	    config['AcceptanceFunction'] == None or
	    config['AcceptanceFunction'] == 'None'):
        tacc_slope  = WS(ws, RooRealVar('tacc_slope' , 'BdPTAcceptance_slope',
	    config['BdPTAcceptance_slope']))
        tacc_offset = WS(ws, RooRealVar('tacc_offset', 'BdPTAcceptance_offset',
	    config['BdPTAcceptance_offset']))
        tacc_beta = WS(ws, RooRealVar('tacc_beta', 'BdPTAcceptance_beta',
	    config['BdPTAcceptance_beta']))
        tacc = WS(ws, BdPTAcceptance('BsPTAccFunction',
	    '%s decay time acceptance function' % bName,
	    time, tacc_beta, tacc_slope, tacc_offset))
    else:
        tacc = None
    
    # Decay time error distribution
    # -----------------------------
    if 'PEDTE' in config['DecayTimeResolutionModel']:
        #terrpdf_mean  = WS(ws, RooConstVar( 'terrpdf_mean' , 'terrpdf_mean' ,  0.04 ))
        #terrpdf_sigma = WS(ws, RooConstVar( 'terrpdf_sigma', 'terrpdf_sigma',  0.02 ))
        #terrpdf = WS(ws, RooLandau( 'terrpdf', '%s decay time error PDF',
        #                     timeerr, terrpdf_mean, terrpdf_sigma ))

	# resolution in ps: 3/terrpdf_shape
        terrpdf_shape = WS(ws, RooConstVar('terrpdf_shape', 'terrpdf_shape', -60.))
        terrpdf_truth = WS(ws, RooTruthModel('terrpdf_truth', 'terrpdf_truth', timeerr))
        terrpdf_i0 = WS(ws, RooDecay('terrpdf_i0', 'terrpdf_i0', timeerr, terrpdf_shape,
                terrpdf_truth, RooDecay.SingleSided))
        terrpdf_i1 = WS(ws, RooPolynomial('terrpdf_i1','terrpdf_i1',
                timeerr, RooArgList(zero, zero, one), 0))
        terrpdf = WS(ws, RooProdPdf('terrpdf', 'terrpdf', terrpdf_i0, terrpdf_i1))

        #terrpdf_mean  = WS(ws, RooConstVar( 'terrpdf_mean' , 'terrpdf_mean' , 0.03 ))
        #terrpdf_sigma = WS(ws, RooConstVar( 'terrpdf_sigma', 'terrpdf_sigma', 0.01 ))
        #terrpdf = WS(ws, RooGaussian( 'terrpdf', 'terrpdf',
        #                       timeerr, terrpdf_mean, terrpdf_sigma ))
    else:
	terrpdf = None
    
    if config['PerEventMistag']:
	sigMistagOmega0 = WS(ws, RooConstVar(
	    'sigMistagOmega0', 'sigMistagOmega0', 0.07))
	sigMistagOmegaAvg = WS(ws, RooConstVar(
	    'sigMistagOmegaAvg', 'sigMistagOmegaAvg', config['TagOmegaSig']))
	sigMistagFracHalf = WS(ws, RooConstVar(
	    'sigMistagFracHalf', 'sigMistagFracHalf', 0.25))
	sigMistagPDF = WS(ws, MistagDistribution('sigMistagPDF', 'sigMistagPDF',
		tagOmegaSig, sigMistagOmega0, sigMistagOmegaAvg, sigMistagFracHalf))
	observables.append(tagOmegaSig)
    else:
	sigMistagPDF = None

    # Signal EPDF
    # -----------
    # Bs -> Ds K
    # ----------
    # Bs    -> Ds- K+    bTag = +1   fCharge = +1
    # Bs    -> Ds+ K-    bTag = +1   fCharge = -1
    # Bsbar -> Ds- K+    bTag = -1   fCharge = +1
    # Bsbar -> Ds+ K-    bTag = -1   fCharge = -1
    # untag -> Ds- K+    bTag =  0   fCharge = +1
    # untag -> Ds+ K-    bTag =  0   fCharge = -1
    #
    # The 4 coefficients of the B decay rate equations (q = bTag)
    # Weight : |q|*eff_tag + (1-|q|)*(1-eff_tag)
    #        = 1 - eff_tag for untagged events (q=0)
    #        = eff_tag     for tagged   events (q=+/-1)
    ArgLf       = config['StrongPhase'] - config['WeakPhase']
    ArgLbarfbar = config['StrongPhase'] + config['WeakPhase']
    ACPobs = cpobservables.AsymmetryObservables(ArgLf, ArgLbarfbar, config['ModLf'])
    ACPobs.printtable()
    if True:
        sigC    = WS(ws, RooRealVar(   'C',    'C coeff.', ACPobs.Cf(), -3., 3.))
        sigS    = WS(ws, RooRealVar(   'S',    'S coeff.', ACPobs.Sf(), -3., 3.))
        sigD    = WS(ws, RooRealVar(   'D',    'D coeff.', ACPobs.Df(), -3., 3.))
        sigSbar = WS(ws, RooRealVar('Sbar', 'Sbar coeff.', ACPobs.Sfbar(), -3., 3.))
        sigDbar = WS(ws, RooRealVar('Dbar', 'Dbar coeff.', ACPobs.Dfbar(), -3., 3.))
    else:
        Lambda = WS(ws, RooRealVar('%s_lambda' % 'Sig', '%s_lambda' % 'Sig',
    		config['ModLf'], 0., 10.))
        delta = WS(ws, RooRealVar('%s_delta' % 'Sig', '%s_delta' % 'Sig',
    		config['StrongPhase'], -10. * pi, 10. * pi))
        phi_w = WS(ws, RooRealVar('%s_phi_w' % 'Sig', '%s_phi_w' % 'Sig',
    		config['WeakPhase'], -10. * pi, 10. * pi))
        sigC    = WS(ws, CPObservable('%s_C' % 'Sig', '%s_C' % 'Sig',
    		Lambda, delta, phi_w, CPObservable.C))
        sigD    = WS(ws, CPObservable('%s_D' % 'Sig', '%s_D' % 'Sig',
    		Lambda, delta, phi_w, CPObservable.D))
        sigS    = WS(ws, CPObservable('%s_S' % 'Sig', '%s_S' % 'Sig',
    		Lambda, delta, phi_w, CPObservable.S))
        sigDbar = WS(ws, CPObservable('%s_Dbar' % 'Sig', '%s_Dbar' % 'Sig',
    		Lambda, delta, phi_w, CPObservable.Dbar))
        sigSbar = WS(ws, CPObservable('%s_Sbar' % 'Sig', '%s_Sbar' % 'Sig',
    		Lambda, delta, phi_w, CPObservable.Sbar))

    nSigEvts = WS(ws, RooRealVar('nSigEvts', 'nSigEvts', 0. + config['NSigEvts'], 0., 1e7))

    sigMassPDF = WS(ws, RooGaussian('SigMassPDF', 'SigMassPDF', mass, mBs, mWidth))
    sigTimePDF = buildBDecayTimePdf(config, 'Sig', ws,
	    time, timeerr, bTagMap, fChargeMap, tagOmegaSig, tagEffSig,
	    gammas, deltaGammas, deltaMs, sigC, sigD, sigDbar, sigS, sigSbar,
	    trm, tacc, terrpdf, sigMistagPDF,
	    kfactorpdf, k,
            config['NBinsMistag'], config['NBinsProperTime'],
            config['NBinsAcceptance'], config['NBinsTimeKFactor'])

    sigPDF = WS(ws, RooProdPdf('SigPDF', 'SigPDF', sigMassPDF, sigTimePDF))
    sigEPDF = WS(ws, RooExtendPdf('SigEPDF', 'SigEPDF', sigPDF, nSigEvts))

    # Create the Bs -> Ds Pi physical background EPDF
    # -----------------------------------------------
    # Bs    -> Ds- pi+    bTag = +1   fCharge = +1   ==> unmixed = +1
    # Bs    -> Ds+ pi-    bTag = +1   fCharge = -1   ==> mixed   = -1
    # Bsbar -> Ds- pi+    bTag = -1   fCharge = +1   ==> mixed   = -1
    # Bsbar -> Ds+ pi-    bTag = -1   fCharge = -1   ==> unmixed = +1
    #
    #  --> q = mixState = bTag * fCharge
    nBs2DsPiEvts = WS(ws, RooRealVar(
	'nBs2DsPiEvts', 'nBs2DsPiEvts', 0. + config['NBs2DsPiEvts'], 0., 1e7))
    Bs2DsPiTimePDF = buildBDecayTimePdf(config, 'Bs2DsPi', ws,
	    time, timeerr, bTagMap, fChargeMap, tagOmegaSig, tagEffSig,
	    gammas, deltaGammas, deltaMs, one, zero, zero, zero, zero,
	    trm, tacc, terrpdf, sigMistagPDF,
	    kfactorpdf, k,
            config['NBinsMistag'], config['NBinsProperTime'],
            config['NBinsAcceptance'], config['NBinsTimeKFactor'])

    Bs2DsPiMassPDF = RooGaussian('Bs2DsPiMassPDF', 'Bs2DsPiMassPDF', mass, mBsmisrec, mWidthmisrec)

    Bs2DsPiPDF = RooProdPdf( 'Bs2DsPiPDF', 'Bs2DsPiPDF', Bs2DsPiMassPDF, Bs2DsPiTimePDF )
    Bs2DsPiEPDF = RooExtendPdf( 'Bs2DsPiEPDF', 'Bs2DsPiEPDF', Bs2DsPiPDF, nBs2DsPiEvts )

    # Create the combinatorial background EPDF
    # ----------------------------------------
    nCombBkgEvts     = WS(ws, RooRealVar(
	'nCombBkgEvts'  , 'nCombBkgEvts' , 0. + config['NCombBkgEvts'], 0., 1e7))
    
    tpdfCombBkg_a     = WS(ws, RooRealVar(
	'tpdfCombBkg_a', 'tpdfCombBkg_a', config['TPDFCombBkg_a']))
    tpdfCombBkg_f     = WS(ws, RooRealVar(
	'tpdfCombBkg_f', 'tpdfCombBkg_f', config['TPDFCombBkg_f']))
    tpdfCombBkg_alpha = WS(ws, RooRealVar(
	'tpdfCombBkg_alpha', 'tpdfCombBkg_alpha', config['TPDFCombBkg_alpha']))
    tpdfCombBkg_beta  = WS(ws, RooRealVar(
	'tpdfCombBkg_beta', 'tpdfCombBkg_beta', config['TPDFCombBkg_beta']))
    
    tpdfCombBkg = WS(ws, CombBkgPTPdf( 'tpdfCombBkg', 'tpdfCombBkg',
                                time,
                                tpdfCombBkg_a, tpdfCombBkg_f,
                                tpdfCombBkg_alpha, tpdfCombBkg_beta ))
    # The 4 coefficients of the B decay rate equations (q = mixState)
    # Weight : |q|*eff_tag + (1-|q|)*(1-eff_tag)
    #        = 1 - eff_tag for untagged events (q=0)
    #        = eff_tag     for tagged   events (q=+/-1)
    bkgTagWeight = taggingutils.tagEfficiencyWeight(mixState, tagEffBkg, 'Bkg')
    # Tag PDF reads:
    #    q = +1 : omega_tag * eff_tag
    #    q = -1 : (1 - omega_tag) * eff_tag
    #    q = 0  : 1 - eff_tag
    # with q = mixState = bTag * fCharge
    tagEffBkgEffPlus = WS(ws, RooProduct('tagEffBkgEffPlus', 'tagEffBkgEffPlus',
	    RooArgSet(bkgTagWeight, tagOmegaBkg)))
    oneMinusTagOmegaBkg = WS(ws, RooPolyVar('oneMinusTagOmegaBkg', '1-tagOmegaBkg',
	    tagOmegaBkg, RooArgList(one, minusone), 0))
    tagEffBkgEffMinus = WS(ws, RooProduct('tagEffBkgEffMinus', 'tagEffBkgEffMinus',
	    RooArgSet(bkgTagWeight, oneMinusTagOmegaBkg)))
    tagpdfCombBkg = WS(ws, IfThreeWayCatPdf('tagpdfCombBkg', 'tagpdfCombBkg',
	    mixState, tagEffBkgEffPlus, bkgTagWeight, tagEffBkgEffMinus))
    
    tagtpdfCombBkg = WS(ws, RooProdPdf('CombBkgPDF_tagt', 'CombBkgPDF_tagt',
	    tagpdfCombBkg, tpdfCombBkg))
    
    mpdfCombBkg_shape= WS(ws, RooConstVar(
	'mpdfCombBkg_shape', 'mpdfCombBkg_shape', config['MPDFCombBkg_shape']))
    mpdfCombBkg = WS(ws, RooExponential(
	'mpdfCombBkg', 'mpdfCombBkg', mass, mpdfCombBkg_shape))

    mtpdfCombBkg = WS(ws, RooProdPdf('CombBkgPDF_t', 'CombBkgPDF_t',
                              mpdfCombBkg, tagtpdfCombBkg))
    
    mtepdfCombBkg = WS(ws, RooExtendPdf( 'CombBkgEPDF_t',
                                  'Combinatorial background EPDF in time',
                                  mtpdfCombBkg, nCombBkgEvts ))

    # Create the total EPDF
    # ---------------------
    # due to RooFit being quirky, we need the PDFs for generation;
    # fitting with EPDFs works fine
    allPDFs = []
    allEPDFs = []
    fractions = []
    if config['DoDsK']:
	allPDFs.append(sigPDF)
	allEPDFs.append(sigEPDF)
	fractions.append(nSigEvts)
    if config['DoDsPi']:
	allPDFs.append(Bs2DsPiPDF)
	allEPDFs.append(Bs2DsPiEPDF)
	fractions.append(nBs2DsPiEvts)
    if not config['SignalModelOnly']:
	allPDFs.append(mtpdfCombBkg)
	allEPDFs.append(mtepdfCombBkg)
	fractions.append(nCombBkgEvts)

    totPDF = WS(ws, RooAddPdf('TotPDF_t', 'Model (signal & background) PDF in time',
	    RooArgList(*allPDFs), RooArgList(*fractions)))
    totEPDF = WS(ws, RooAddPdf('TotEPDF_t', 'Model (signal & background) EPDF in time',
	    RooArgList(*allEPDFs)))
    
    # set variables constant if they are supposed to be constant
    setConstantIfSoConfigured(config, totPDF)
    setConstantIfSoConfigured(config, totEPDF)
    
    retVal = {
	    'ws': ws,
	    'pdf': totPDF,
	    'epdf': totEPDF,
	    'observables': RooArgSet(*observables)
	    }
    return retVal

def runBsGammaFitterToyMC(generatorConfig, fitConfig, toy_num, debug, wsname, initvars) :
    from ROOT import FitMeTool
    from B2DXFitters import taggingutils, cpobservables

    GeneralModels = GaudiPython.gbl.GeneralModels
    PTResModels   = GaudiPython.gbl.PTResModels
    
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooMultiCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay
    from ROOT import RooGaussModel, RooTruthModel
    from ROOT import RooAbsReal, RooWorkspace, RooAbsArg
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf
    from ROOT import RooExponential, RooPolynomial, RooPolyVar, RooUniform
    from ROOT import RooFit, RooUniformBinning
    from ROOT import IfThreeWayCat, Dilution, IfThreeWayCatPdf
    from ROOT import CombBkgPTPdf
    from ROOT import BdPTAcceptance, MistagDistribution
    from ROOT import RooBinnedPdf, RooEffHistProd

    # Instantiate and run the fitter in toy MC mode
    # (generate using the PDFs)
    fitter = FitMeTool(toy_num, debug)

    print '########################################################################'
    print 'generator config:'
    print
    for k in generatorConfig:
        print '%32s: %s' % (k, str(generatorConfig[k]))
    print '########################################################################'
    pdf = getMasterPDF(generatorConfig, 'GEN', debug)
    
    fitter.setObservables(pdf['observables'])
    fitter.setModelPDF(pdf['pdf'])

    print "TOTPDF - BEG"
    modelPDF = fitter.printModelStructure()
    print "TOTPDF - END"

    fitter.generate()

    # we want our own copy of the data set to do with as we please
    dataset = fitter.getData().Clone()

    ws = pdf['ws']
    decayPath = ws.obj('decayPath')
    bTagMap = ws.obj('bTagMap')
    fChargeMap = ws.obj('fChargeMap')
    mixState = ws.obj('mixState')
    dataset.table(decayPath).Print('v')
    dataset.table(bTagMap).Print('v')
    dataset.table(fChargeMap).Print('v')
    dataset.table(mixState).Print('v')
    dataset.table(RooArgSet(bTagMap, fChargeMap)).Print('v')

    # to speed things up during the fit, we sort events by qf and qt
    # this avoids "cache poisoning" by making pdf argument changes rarer
    oldds = [ dataset ]
    del dataset
    # split according to category
    for s in [ bTagMap, fChargeMap ]:
        newds = [ ]
        # loop over datasets, split each in subsamples, one per category index
        for ds in oldds:
            it = s.typeIterator()
            while True:
                obj = it.Next()
                if None == obj:
                    break
                newds.append(ds.reduce(
                    RooFit.Cut('%s==%s' % (s.GetName(), obj.getVal()))))
                del obj
            del it
        # split step for current category done
        oldds = newds
        del newds
    # now merge all datasets
    while len(oldds) > 1:
        oldds[0].append(oldds[1])
        del oldds[1]
    dataset = oldds[0]
    del oldds

    # delete the fitter, create a new one with the EPDFs for fitting
    # and use the dataset just generated
    del fitter
    del pdf

    print '########################################################################'
    print 'fit config:'
    print
    for k in fitConfig:
        print '%32s: %s' % (k, str(fitConfig[k]))
    print '########################################################################'
    pdf2 = getMasterPDF(fitConfig, 'FIT', debug)

    fitter = FitMeTool(toy_num, debug)

    dataset = dataset.reduce(RooFit.SelectVars(pdf2['observables']))
    fitter.setObservables(pdf2['observables'])
    fitter.setModelPDF(pdf2['epdf'])
    fitter.setData(dataset)

    plot_init   = (wsname != None) and initvars
    plot_fitted = (wsname != None) and (not initvars)

    if plot_init :
        fitter.saveModelPDF(wsname)
        fitter.saveData(wsname)

    constraints = []
    if 'ModLfErr' in fitConfig:
        sigCprime = fitter.getModelPDF().getVariables().find('C')
        xs = RooFormulaVar('xs', '(1.-@0)/sqrt(1.-@0*@0)', RooArgList(sigCprime))
        xsVal = RooConstVar('xsVal', 'xsVal', fitConfig['ModLf'])
        xsErr = RooConstVar('xsErr', 'xsErr', fitConfig['ModLfErr'])
        xsConstraint = RooGaussian('xsConstraint', 'xsConstraint', xs, xsVal, xsErr)
        constraints.append(xsConstraint)

    # more recent RooFit versions need Optimize(1) to work correctly
    # with our complicated (E)PDFs
    constraints = RooArgSet(*constraints)
    fitter.fit(True, RooFit.Optimize(1), RooFit.Strategy(2), RooFit.Timer(),
	    RooFit.Verbose(True), RooFit.ExternalConstraints(constraints))

    if plot_fitted :
        fitter.saveModelPDF(wsname)
        fitter.saveData(wsname)
    
    del fitter
        
#------------------------------------------------------------------------------
_usage = '%prog [options] <toy_number>'

parser = OptionParser(_usage)

parser.add_option('-d', '--debug',
	dest    = 'debug',
	default = False,
	action  = 'store_true',
	help    = 'print debug information while processing'
	)
parser.add_option('-s', '--save',
	dest    = 'wsname',
	type = 'string',
	metavar = 'WSNAME',
	help    = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
	)
parser.add_option('-i', '--initial-vars',
	dest    = 'initvars',
	default = False,
	action  = 'store_true',
	help    = 'save the model PDF parameters before the fit (default: after the fit)'
	)
parser.add_option('-F', '--fit-config-string',
	dest = 'fitConfigString',
	type = 'string',
	action = 'store',
	help = 'string with fit configuration changes (dictionary, takes precedence)'
	)
parser.add_option('-f', '--fit-config-file',
	dest = 'fitConfigFile',
	type = 'string',
	action = 'store',
	help = 'name of file with fit configuration changes (dictionary)'
	)
parser.add_option('-G', '--gen-config-string',
	dest = 'genConfigString',
	type = 'string',
	action = 'store',
	help = 'string with generator configuration changes (dictionary, takes precedence)'
	)
parser.add_option('-g', '--gen-config-file',
	dest = 'genConfigFile',
	type = 'string',
	action = 'store',
	help = 'name of file with generator configuration changes (dictionary)'
	)

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    generatorConfig = dict(defaultConfig)
    fitConfig = dict(defaultConfig)
    #
    # example: change Gammas in fitting:
    # fitConfig.update({'Gammas': 0.700})

    (options, args) = parser.parse_args()

    if len(args) != 1 :
	parser.print_help()
	exit(-1)

    try:
	TOY_NUMBER = int(args[ 0 ])
    except ValueError:
	parser.error('The toy number is meant to be an integer ;-)!')
    # parse fit/generator configuration options
    if None != options.fitConfigFile:
	try:
	    lines = file(options.fitConfigFile, 'r').readlines();
	except:
	    parser.error('Unable to read fit configuration file %s' %
		    options.fitConfigFile)
	try:
	    d = eval(compile(''.join(lines), options.fitConfigFile, 'eval'))
	    fitConfig.update(d)
            del d
	except:
	    parser.error('Unable to parse fit configuration in file %s' %
		    options.fitConfigFile)
        del lines
    if None != options.fitConfigString:
	try:
	    d = eval(compile(options.fitConfigString, '[command line]', 'eval'))
	    fitConfig.update(d)
            del d
	except:
	    parser.error('Unable to parse fit configuration in \'%s\'' %
		    options.fitConfigString)
    if None != options.genConfigFile:
	try:
	    lines = file(options.genConfigFile, 'r').readlines();
	except:
	    parser.error('Unable to read generator configuration file %s' %
		    options.genConfigFile)
	try:
	    d = eval(compile(''.join(lines), options.genConfigFile, 'eval'))
	    generatorConfig.update(d)
            del d
	except:
	    parser.error('Unable to parse generator configuration in file %s' %
		    options.genConfigFile)
        del lines
    if None != options.genConfigString:
	try:
	    d = eval(compile(options.genConfigString, '[command line]', 'eval'))
	    generatorConfig.update(d)
            del d
	except:
	    parser.error('Unable to parse generator configuration in \'%s\'' %
		    options.genConfigString)
    
    runBsGammaFitterToyMC(
            generatorConfig,
            fitConfig,
            TOY_NUMBER,
	    options.debug,
	    options.wsname,
	    options.initvars)
    #from ROOT import RooWorkspace, RooRealVar
    #ws = RooWorkspace('ws', 'ws')
    #mass = RooRealVar('mass', 'mass', 5320., 5420.)
    #masstemplates = getMassTemplates('WS_DsK_Mass.root', 'FitMeToolWS', ws, mass)
    #ws.Print('v')
    #ws = RooWorkspace('ws', 'ws')
    #k = RooRealVar('k', 'k', 0.1, 1.9)
    #ktemplates = getKFactorTemplates('kfactor_wspace.root', 'workspace', ws, k)
    #print sorted(masstemplates.keys())
    #print sorted(ktemplates.keys())
    ##ws.Print('v')

    # -----------------------------------------------------------------------------
