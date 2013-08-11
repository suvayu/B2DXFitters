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
            'nonres', 'phipi', 'kstk', 'kpipi', 'pipipi'
            ],
        'CombineModesForEffCPObs': [ ],
        'Bs2DsKCPObs':                  'LambdaPhases',
        'NEvents':			[ 43473. ],
        'MassTemplateFile':             os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/WS_Mass_DsPi_5M_BDTGA.root',
        'MassTemplateWorkspace':	'FitMeToolWS',
        'MassInterpolation':		False,
        'MistagTemplateFile':           os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/templates_BsDsPi.root',
        'MistagTemplateWorkspace':	'workspace',
        'MistagTemplateName':	        'MistagPdf_signal_BDTGA',
        'DecayTimeResolutionModel':	'GaussianWithPEDTE',
        'DecayTimeErrorTemplateFile':       os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/templates_BsDsPi.root',
        'DecayTimeErrorTemplateWorkspace':  'workspace',
        'DecayTimeErrorTemplateName':       'TimeErrorPdf_signal_BDTGA',
        'DecayTimeErrorVarName':            'lab0_LifetimeFit_ctauErr',
        'constParams': [
            'Gammas', 'deltaGammas',
            'Gammad', 'deltaGammad', 'deltaMd',
            'tagOmegaSig', 'timeerr_bias', 'timeerr_scalefactor',
            'MistagCalibB_p0', 'MistagCalibB_p1', 'MistagCalibB_avgmistag',
            'MistagCalibBbar_p0', 'MistagCalibBbar_p1', 'MistagCalibBbar_avgmistag',
            'Bs2DsKst_TagEff', 'Bs2DsKst_delta', 'Bs2DsKst_lambda', 'Bs2DsKst_phi_w',
            ],
}
