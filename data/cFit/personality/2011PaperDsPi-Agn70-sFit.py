# personality for 2011 Paper - mode DsPi
{
        'Modes': [
            'Bs2DsPi',
            'Bd2DPi', 'Bs2DsstPi',
            'Bd2DsPi',
            'Bs2DsK',
            'Lb2LcPi',
            'CombBkg'
            ],
        'SampleCategories': [
            'phipi'
            ],
        'DeltaMs':                      17.768, # in ps^{-1}
        'GammaLb':			0.700, # in ps^{-1}
        'GammaCombBkg':			1.057, # in ps^{-1}
        'WeakPhase': {
            'Bs2DsK':           70. / 180. * pi,
            'Bs2DsstK':         70. / 180. * pi,
            'Bs2DsKst':         70. / 180. * pi,
            'Bs2DsstKst':	70. / 180. * pi,
            'Bd2DPi':           70. / 180. * pi
            },
        'StrongPhase': {
            'Bs2DsK':           30. / 180. * pi,
            'Bs2DsstK':         -150. / 180. * pi,
            'Bs2DsKst':         -150. / 180. * pi,
            'Bs2DsstKst':       30. / 180. * pi,
            'Bd2DPi':           30. / 180. * pi
            },
        'CombineModesForEffCPObs': [ ],
        'Bs2DsKCPObs':                  'LambdaPhases',
        'NEvents':			[ 33672. ],
        'DataFileName': '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/PETE/DsPi_Toys1M_sWeights_ForTimeFit_%d.root' % TOY_NUMBER,
        'DataSetNames': 'merged',
        'FitMode': 'sFit',
        'DataWorkSpaceName':    'FitMeToolWS',
	'DataSetVarNameMapping': {
	    'sample':   'sample',
	    'mass':     'lab0_MassFitConsD_M',
	    'pidk':     'lab1_PIDK',
            'dsmass':   'lab2_MM',
            'time':     'lab0_LifetimeFit_ctau',
            'timeerr':  'lab0_LifetimeFit_ctauErr',
            'mistag': 'lab0_BsTaggingTool_TAGOMEGA_OS',
            'qf':       'lab1_ID_idx',
            'qt':       'lab0_BsTaggingTool_TAGDECISION_OS_idx',
            'weight':   'nSig_both_nonres_Evts_sw+nSig_both_phipi_Evts_sw+nSig_both_kstk_Evts_sw+nSig_both_kpipi_Evts_sw+nSig_both_pipipi_Evts_sw'
            },
        'MassTemplateFile':             ('/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/PETE/DsPi_Toys_Work_ForMassPlot_%d.root' if haveAFS else
            os.environ['B2DXFITTERSROOT']+'/scripts/mdfit-005/data/DsPi_Toys_Work_ForMassPlot_%d.root') % TOY_NUMBER,
        'MassTemplateWorkspace':	'FitMeToolWS',
        'MassInterpolation':		False,
        'MistagTemplateFile':           os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/templates_BsDsPi.root',
        'MistagTemplateWorkspace':	'workspace',
        'MistagTemplateName':	        'MistagPdf_signal_BDTGA',
        'DecayTimeResolutionModel':	'GaussianWithPEDTE',
        'DecayTimeResolutionScaleFactor': 1.37,
        'DecayTimeErrorTemplateFile':       os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/templates_BsDsPi.root',
        'DecayTimeErrorTemplateWorkspace':  'workspace',
        'DecayTimeErrorTemplateName':       'TimeErrorPdf_signal_BDTGA',
        'DecayTimeErrorVarName':            'lab0_LifetimeFit_ctauErr',
        'PowLawAcceptance_turnon':	1.3291e+00,
        'PowLawAcceptance_offset':	1.6710e-02,
        'PowLawAcceptance_expo':	1.8627e+00,
        'PowLawAcceptance_beta':	3.4938e-02,
        'AcceptanceCorrectionFile':     None,
        'AcceptanceCorrectionHistName': None,
        'NBinsAcceptance':              600,
        'constParams': [
            'Gammas', 'deltaGammas',
            'Gammad', 'deltaGammad', 'deltaMd',
            'mistag', 'timeerr_bias', 'timeerr_scalefactor',
            'MistagCalibB_p0', 'MistagCalibB_p1', 'MistagCalibB_avgmistag',
            'MistagCalibBbar_p0', 'MistagCalibBbar_p1', 'MistagCalibBbar_avgmistag',
            'Bs2DsKst_TagEff', 'Bs2DsKst_delta', 'Bs2DsKst_lambda', 'Bs2DsKst_phi_w',
            ],
}
