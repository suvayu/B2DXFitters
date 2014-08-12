"""cFit defaults configuration settings

  The `defaultConfig' dictionary contains default settings.  It is
  updated with dictionary entries according to a "personality" which
  is loaded from a file. 

  The dictionaries `generatorConfig' and `fitConfig' contain settings
  to use during generation and fit respectively.  They can be updated
  in two ways: either by inserting code below (see example), or by
  using job options (which take a string or a file with python code
  which must evaluate to a dictionary)

"""


from math import pi, log
import os


defaultConfig = {
        # personality of the fit
        'Personality': '2011Conf',
        # fit mode: cFit, cFitWithWeights, sFit
        'FitMode': 'cFit',
        # modes to fit for
        'Modes': [
            'Bs2DsK',
            'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst',
            'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bs2DsstRho',
            'Bd2DK', 'Bd2DsK',
            'Lb2LcK', 'Lb2Dsp', 'Lb2Dsstp',
            'CombBkg'
            ],
        # declare sample categories we'll use
        'SampleCategories': [
            'up_kkpi', 'up_kpipi', 'up_pipipi',
            'down_kkpi', 'down_kpipi', 'down_pipipi'
            ],
        # fit ranges in various observables
        'FitRanges': {
            'time':     [0.2, 15.],
            'timeerr':  [1e-6, 0.25],
            'mistag':   [0., 0.5],
            'mass':     [5320., 5420.],
            'dsmass':   [1930., 2015.],
            'pidk':     [0., 150.]
            },
        # combine CP observables for these modes into effective CP obs.
        'CombineModesForEffCPObs': [
            # you may want to combine these during fitting
            'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst'
            ],
        # fit DsK CP observables in which mode:
        # 'CDS' 		- C, D, Dbar, S, Sbar
        # 'CDSConstrained'	- same as CDS, but constrain C^2+D^2+S^2 = 1
        #			  (same for bar)
        # 'CADDADS'		- C, <D>, Delta D, <S>, Delta S
        #			  (<D>=(D+Dbar)/2, Delta D=(D-Dbar)/2 etc.)
        # 'LambdaPhases'	- |lambda|, strong and weak phase
        'Bs2DsKCPObs': 			'CDS',
        'SqSumCDSConstraintWidth':	0.01,

        # BLINDING
        'Blinding':			True,

        # PHYSICAL PARAMETERS
        'Gammad':			0.656, # in ps^{-1}
        'Gammas':			0.661, # in ps^{-1}
        'DeltaGammad':			0.,    # in ps^{-1}
        'DGsOverGs':			-0.106/0.661, # DeltaGammas / Gammas
        'DeltaMd':			0.507, # in ps^{-1}
        'DeltaMs':			17.719, # in ps^{-1}
        'GammaLb':			0.719, # in ps^{-1}
        'GammaCombBkg':			0.800, # in ps^{-1}
        'DGammaCombBkg':                0.000, # in ps^{-1}
        'CombBkg_D':                    0.000, # D parameter (common for both final states)
        # CP observables
        'StrongPhase': {
            'Bs2DsK':		20. / 180. * pi,
            'Bs2DsstK': 	-160. / 180. * pi,
            'Bs2DsKst': 	-160. / 180. * pi,
            'Bs2DsstKst': 	20. / 180. * pi,
            'Bd2DPi':           20. / 180. * pi,
            },
        'WeakPhase': {
                'Bs2DsK':	50. / 180. * pi,
                'Bs2DsstK':	50. / 180. * pi,
                'Bs2DsKst':	50. / 180. * pi,
                'Bs2DsstKst':	50. / 180. * pi,
                'Bd2DPi':       50. / 180. * pi,
                },
        'ModLf': {
                'Bs2DsK': 	0.372,
                'Bs2DsstK': 	0.470,
                'Bs2DsKst': 	0.372,
                'Bs2DsstKst': 	0.470,
                'Bd2DPi':       0.0187
                },
    # asymmetries
    'Asymmetries' : {
            'Prod': {
                #'Bs': 0., 'Bd': 0.
                },
            'Det': {
                #'Bs2DsK': 0.,
                #'Bs2DsstK': 0.,
                #'Bs2DsPi': 0.,
                #'Bd2DK': 0.,
                #'Lb': 0.,
                #'CombBkg': 0.
                },
            'TagEff': [ # one per tagger
                {
                #'Bs': 0., 'Bd': 0.
                }
                ],
            'TagEff_f': [ # one per tagger
                { },
                ],
            'TagEff_t': [ # one per tagger
                { 'Lb': 0.0, 'CombBkg': -0.04 },
                ],
            },
    # Tagging
    'NTaggers':                         1, # 1 - only one tagger (e.g. OS), 2 - e.g. OS + SSK
    'TagEff':			{
            'Bs2DsK': [ 0.403 ], # one per tagger
            },
    'TagOmegaSig':			0.396,
    'MistagCalibrationParams':	{
            # format:
            # 'mode1': [ [ [p0, p1, <eta>] ]_tagger1, ... ],
            # 'mode2': ...
            # with one or two sets of calibration parameters per tagger; if
            # there are two sets, the first is for true B, the second for true
            # Bbar
            'Bs2DsK': [ [
                [ 0.392, 1.035, 0.391 ], # true B
                #[ 0.392, 1.035, 0.391 ], # true Bbar
                ] ],
            },
    # truth/Gaussian/DoubleGaussian/GaussianWithPEDTE/GaussianWithLandauPEDTE/GaussianWithScaleAndPEDTE
    'DecayTimeResolutionModel':         'TripleGaussian',
    'DecayTimeResolutionBias':          0.,
    'DecayTimeResolutionScaleFactor':   1.15,
    # None/BdPTAcceptance/DTAcceptanceLHCbNote2007041,PowLawAcceptance,Spline
    'AcceptanceFunction':		'PowLawAcceptance',
    'AcceptanceCorrectionFile':         os.environ['B2DXFITTERSROOT']+'/data/acceptance-ratio-hists.root',
    'AcceptanceCorrectionHistName':	'haccratio_cpowerlaw',
    'AcceptanceCorrectionInterpolation': False,
    # acceptance can really be made a histogram/spline interpolation
    'StaticAcceptance':		False,
    'AcceptanceInterpolation':	False,
    # acceptance parameters BdPTAcceptance
    'BdPTAcceptance_slope':	1.09,
    'BdPTAcceptance_offset':	0.187,
    'BdPTAcceptance_beta':	0.039,
    # acceptance parameters PowLawAcceptance
    'PowLawAcceptance_turnon':	1.215,
    'PowLawAcceptance_offset':	0.0373,
    'PowLawAcceptance_expo':	1.849,
    'PowLawAcceptance_beta':	0.0363,
    # spline acceptance parameters
    'AcceptanceSplineKnots':    [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
    'AcceptanceSplineCoeffs':   {
            # first index: DATA for data fits, MC for MC/toy fits
            'MC': {
                # second index: Bs2DsK or Bs2DsPi, depending on what the
                # signal mode is
                'Bs2DsPi':      [ 5.12341e-01, 7.44868e-01, 9.95795e-01, 1.13071e+00, 1.23135e+00, 1.22716e+00 ],
                'Bs2DsK':       [ 4.97708e-01, 7.42075e-01, 9.80824e-01, 1.16280e+00, 1.24252e+00, 1.28482e+00 ],
                # alternatively, you could have per-mode acceptances:
                # 'Bs2DsK': {
                #    'Bs2DsK': [ ... ],
                #    'Bs2DsPi': [ ... ],
                #    'Lb': [ ... ],
                # }
                },
            'DATA': {
                'Bs2DsPi':      [ 4.5853e-01, 6.8963e-01, 8.8528e-01, 1.1296e+00, 1.2232e+00, 1.2277e+00 ],
                'Bs2DsK':       [
		    4.5853e-01 * 4.97708e-01 / 5.12341e-01,
		    6.8963e-01 * 7.42075e-01 / 7.44868e-01,
		    8.8528e-01 * 9.80824e-01 / 9.95795e-01,
		    1.1296e+00 * 1.16280e+00 / 1.13071e+00,
		    1.2232e+00 * 1.24252e+00 / 1.23135e+00,
		    1.2277e+00 * 1.28482e+00 / 1.22716e+00
		    ],
                }
            },

    'PerEventMistag': 		True,

    # divide mistag into categories?
    #
    # number of categories
    'NMistagCategories':        None,
    # sorted list of category boundaries, e.g [ 0., 0.1, 0.2, 0.4, 0.5 ]
    'MistagCategoryBinBounds':  None,
    # starting values for per-category mistags
    'MistagCategoryOmegas':     None,
    # per category tagging efficiencies (N_cat_i / N_(tagged + untagged)
    'MistagCategoryTagEffs':    None,
    # parameter range if per-cat. omegas are floated
    'MistagCategoryOmegaRange': [ 0., 0.5 ],

    'TrivialMistag':		False,

    'UseKFactor':		True,

    # fitter settings
    'Optimize':			1,
    'Strategy':			2,
    'Offset':			True,
    'Minimizer':		[ 'Minuit', 'migrad' ],
    'NumCPU':			1,
    'ParameteriseIntegral':     True,
    'Debug':			False,

    # list of constant parameters
    'constParams': [
            'Gammas', 'deltaGammas', 'deltaMs',
            'Gammad', 'deltaGammad', 'deltaMd',
            'mistag', 'timeerr_bias', 'timeerr_scalefactor',
            '.+_Mistag[0-9]+Calib(B|Bbar)_p[0-9]+'
            ],
    # dictionary of constrained parameters
    'Constraints': {
            # two possible formats:
            # - 'paramname': error
            #   the parameter's value is taken to be the central value, and a
            #   Gaussian constraint with that central value and the given
            #   error is applied
            # - 'formulaname': [ 'formula', [ 'par1', 'par2', ... ], mean, error ]
            #   construct a RooFormulaVar named formulaname with formula
            #   formula, giving the arguments in the list as constructor
            #   arguments; then use a Gaussian constraint to bring the value
            #   of that formula to mean with an uncertainty of error
            },

    # mass templates
    'MassTemplateFile':		os.environ['B2DXFITTERSROOT']+'/data/workspace/WS_Mass_DsK.root',
    'MassTemplateWorkspace':	'FitMeToolWS',
    'MassInterpolation':	False,
    # fudge the default template lookup order
    'MassTemplatePolaritySearch':	[ 'both' ],
    # either one element or 6 (kkpi,kpipi,pipipi)x(up,down) in "sample" order
    'NEvents':			[ 1731. ],
    # target S/B: None means keep default
    'S/B': None,
    # mistag template
    'MistagTemplates':	{
            # general format:
            # 'mode1': [ { dict tagger 1 }, ..., { dict tagger N } ],
            # 'mode2': ...
            # where {dict tagger i} contains properties 'File', 'Workspace',
            # 'TemplateName', 'VarName'
            'Bs2DsK': [ { 
                    'File':             os.environ['B2DXFITTERSROOT']+'/data/workspace/work_toys_dsk.root',
                    'Workspace':        'workspace',
                    'TemplateName':     'PhysBkgBsDsPiPdf_m_down_kkpi_mistag',
                    'VarName':          'lab0_BsTaggingTool_TAGOMEGA_OS',
                } ]
            },
    'MistagInterpolation':	False,
    # decay time error template
    'DecayTimeErrorTemplates': {
            # general format:
            # 'mode1': { dict },
            # 'mode2': ...
            # where { dict } contains properties 'File', 'Workspace',
            # 'TemplateName', 'VarName'
            'Bs2DsK': {
                'File':         None,
                'Workspace':    None,
                'TemplateName': None,
                'VarName':      None,
                },
            },
    'DecayTimeErrInterpolation':	False,

    # k-factor templates
    'KFactorTemplates': {
            # general format:
            # 'mode1': { dict },
            # 'mode2': ...
            # where { dict } contains properties 'File', 'Workspace',
            # 'TemplateName', 'VarName'
            },

    # verify settings and sanitise where (usually) sensible
    'Sanitise':			True,

    # fitter on speed: binned PDFs
    'NBinsAcceptance':		300,   # if >0, bin acceptance
    'NBinsTimeKFactor':		0,     # if >0, use binned cache for k-factor integ.
    'NBinsMistag':		50,    # if >0, parametrize Mistag integral
    'NBinsProperTimeErr':	100,   # if >0, parametrize proper time int.
    'NBinsMass':		200,   # if >0, bin mass templates

    # Data file settings
    'IsToy':			True,
    'DataFileName':		None,
    'DataWorkSpaceName':	'workspace',
    'DataSetNames':		{
            'up_kkpi':          'dataSetBsDsK_up_kkpi',
            'up_kpipi':         'dataSetBsDsK_up_kpipi',
            'up_pipipi':        'dataSetBsDsK_up_pipipi',
            'down_kkpi':	'dataSetBsDsK_down_kkpi',
            'down_kpipi':	'dataSetBsDsK_down_kpipi',
            'down_pipipi':	'dataSetBsDsK_down_pipipi'
            },
    'DataSetCuts': None,                # cut string or None
    # variable name mapping: our name -> name in dataset
    'DataSetVarNameMapping': {
            'sample':   'sample',
            'mass':     'lab0_MassFitConsD_M',
            'pidk':     'lab1_PIDK',
            'dsmass':   'lab2_MM',
            'time':     'lab0_LifetimeFit_ctau',
            'timeerr':  'lab0_LifetimeFit_ctauErr',
            'mistag':   'lab0_BsTaggingTool_TAGOMEGA_OS',
            'qf':       'lab1_ID',
            'qt':       'lab0_BsTaggingTool_TAGDECISION_OS',
            'weight':   'nSig_both_nonres_Evts_sw+nSig_both_phipi_Evts_sw+nSig_both_kstk_Evts_sw+nSig_both_kpipi_Evts_sw+nSig_both_pipipi_Evts_sw'
            },
    # write data set to file name
    'WriteDataSetFileName': None,
    'WriteDataSetTreeName': 'data',
    'QuitAfterGeneration': False,
    # bug-for-bug compatibility flags
    'BugFlags': [
            # 'PdfSSbarSwapMinusOne',
            # 	swap and multiply S and Sbar in the pdf, state of
            # 	affairs before discovery of bug on 2012-09-13 
            # 'OutputCompatSSbarSwapMinusOne',
            #	with the bug from PdfSSbarSwapMinusOne fixed, the
            #	output of the fit parameters is no longer comparable to
            #	old fits - fix in the final output routine by applying
            #	that transformation during the output stage (MINUIT log
            #	output and fit results will be "wrong", though)
            #'RooFitTopSimultaneousWorkaround',
            # this will work around a problem in present RooFit versions which
            # produce different LH values if the top-level PDF is a
            # RooSimultaneous
            ],
    }
