# personality for 2011 Paper - mode DsK - mixed from official MC (Gauss/Boole/...)
{
        'Modes': [
            'Bs2DsK',
            'Bs2DsPi',
            'CombBkg'
            ],
        #'FitMode': 'sFit',
        #'FitRanges': {
        #    'time':     [0.2, 15.],
        #    'timeerr':  [1e-6, 0.25],
        #    'mistag':   [0., 0.5],
        #    'mass':     [5300., 5800.],
        #    'dsmass':   [1930., 2015.],
        #    'pidk':     [0., 150.]
        #    },
        'SampleCategories': [
            'nonres', 'phipi', 'kstk', 'kpipi', 'pipipi'
            ],
        'Gammas':                       0.679,
	'DGsOverGs':                    -0.060/0.679, # DeltaGammas / Gammas
        'DeltaMs':                      17.800, # in ps^{-1}
        'GammaLb':			0.700, # in ps^{-1}
        'GammaCombBkg':			0.800, # in ps^{-1}
        'WeakPhase': {
            'Bs2DsK':           70. / 180. * pi,
            },
        'StrongPhase': {
            'Bs2DsK':           30. / 180. * pi,
            },
        'ModLf': {
	    'Bs2DsK': 	        0.0,
	    },
        'AcceptanceCorrectionFile': None,
        'CombineModesForEffCPObs': [ ],
        'NEvents':			[ 3474. ],
        #'DataFileName':         '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/sWeights_BsDsK_all_both_FullMC.root',
        #'DataFileName':         '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/sWeights_BsDsK_all_both_FullMC_DsKCombo.root',
        #'DataFileName':         '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/sWeights_BsDsK_all_both_FullMC_DsKDsPi.root',
        #'DataFileName':         '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/sWeights_BsDsK_all_both_FullMC_Signal.root',
        'DataFileName':         '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/WS_Mass_DsK_5M_FullMC2.root',
        #'DataFileName':         '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/WS_Mass_DsK_5M_FullMC_DsKCombo2.root',
        #'DataFileName':         '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/WS_Mass_DsK_5M_FullMC_DsKDsPi.root',
        #'DataFileName':         '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/WS_Mass_DsK_5M_FullMC_Signal.root',
        'DataWorkSpaceName':    'FitMeToolWS',
        #'DataSetNames':         'merged',
        'DataSetNames':         'combData',
	'DataSetVarNameMapping': {
	    'sample':   'sample',
	    'mass':     'lab0_MassFitConsD_M',
	    'pidk':     'lab1_PIDK',
            'dsmass':   'lab2_MM',
            'time':     'lab0_LifetimeFit_ctau',
            'timeerr':  'lab0_LifetimeFit_ctauErr',
            'mistag':   'tagOmegaComb',
            'qf':       'lab1_ID',
            'qt':       'tagDecComb',
            'weight':   'nSig_both_nonres_Evts_sw+nSig_both_phipi_Evts_sw+nSig_both_kstk_Evts_sw+nSig_both_kpipi_Evts_sw+nSig_both_pipipi_Evts_sw'
            },
        'MassTemplateFile':             '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/WS_Mass_DsK_5M_FullMC2.root',
        #'MassTemplateFile':             '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/WS_Mass_DsK_5M_FullMC_DsKCombo2.root',
        #'MassTemplateFile':             '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/WS_Mass_DsK_5M_FullMC_DsKDsPi.root',
        #'MassTemplateFile':             '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/WS_Mass_DsK_5M_FullMC_Signal.root',
        'MassTemplateWorkspace':	'FitMeToolWS',
        'MassInterpolation':		False,
        'NTaggers':                     3,
        'TagEff':                    {
            'Bs2DsK': [ 0.3979 * (1. - 0.6137), 0.6137 * (1. - 0.3979), 0.3979 * 0.6137 ],
            },
        'MistagTemplates': {
            'Bs2DsK': [
                {   'File': '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/templates_mistag.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_1',
                    'VarName': 'tagOmegaComb', },
                {   'File': '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/templates_mistag.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_2',
                    'VarName': 'tagOmegaComb', },
                {   'File': '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/templates_mistag.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_3',
                    'VarName': 'tagOmegaComb', },
                ],
            'CombBkg': [
                {   'File': '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/templates_mistag.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_1',
                    'VarName': 'tagOmegaComb', },
                {   'File': '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/templates_mistag.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_2',
                    'VarName': 'tagOmegaComb', },
                {   'File': '/afs/cern.ch/work/a/adudziak/public/workspace/DsKReview/FullMCDsK/templates_mistag.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_3',
                    'VarName': 'tagOmegaComb', },
                ],
            },
        'MistagCalibrationParams': {
                'Bs2DsK': [
                    [ [ 0., 1., 0. ] ],
                    [ [ 0., 1., 0. ] ],
                    [ [ 0., 1., 0. ] ],
                    ],
                },
        'Constraints': {
		'Bs_AsymProd': 0.01,
		'Bs2DsK_AsymDet':	0.01,
		#'Bs2DsK_AsymTagEff0':	0.01,
		#'Bs2DsK_AsymTagEff1':	0.01,
		#'Bs2DsK_AsymTagEff2':	0.01,
		'Bs2DsPi_AsymDet':	0.01,
		'CombBkg_AsymDet':	0.01,
                },
        'Asymmetries': {
                'Prod': {
                    'Bs': 0.0,
		    },
		'Det': {
		        'Bs2DsK':	0.0,
			'Bs2DsPi':	0.0,
			'CombBkg':	0.0,
		    },
		'TagEff': {
                    },
                'TagEff_t': {
                    },
                'TagEff_f': {
                        },
                },
        'DecayTimeResolutionModel':	'GaussianWithPEDTE',
        'DecayTimeResolutionScaleFactor': 1.195,
        'DecayTimeErrorTemplates': {
                'Bs2DsK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bs2DsK',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bs2DsPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bs2DsPi',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'CombBkg': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_CombBkg',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                },
        'KFactorTemplates': {
                'Bs2DsPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5320_5420.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Bs2DsPi_both',
                    'VarName': 'kfactorVar', },
                },
        'AcceptanceFunction': 'Spline',
	'AcceptanceSplineCoeffs':   { # dspi data dsk mc dspi mc
	    'MC': {
		'Bs2DsPi':      [ 0.179, 0.294, 0.690, 1.125, 1.245, 1.270 ],
                #'Bs2DsK':       [ 1.40502e-01, 2.52286e-01, 5.77488e-01, 1.07557e+00, 1.08338e+00, 1.29397e+00 ],
                'Bs2DsK':       {
                    'Bs2DsK': [ 1.40502e-01, 2.52286e-01, 5.77488e-01, 1.07557e+00, 1.08338e+00, 1.29397e+00 ],
                    'Bs2DsPi': [ 0.181620, 0.164733, 0.511894, 0.80871, 0.98914, 1.14692 ],
                    },
		},
	    'DATA': {
		'Bs2DsPi':      [ 0.145, 0.210, 0.625, 1.029, 1.258, 1.241 ],
		'Bs2DsK':       [ 0.128, 0.193, 0.590, 1.023, 1.250, 1.253 ],
		}
	    },
        'constParams': [
            'Gammas', 'deltaGammas', 'deltaMs',
            'Gammad', 'deltaGammad', 'deltaMd',
            'mistag', 'timeerr_bias', 'timeerr_scalefactor',
            '.+_Mistag[0-9]+Calib(B|Bbar)_p[0-9]+',
            'Bs2DsKst_TagEff[0-9]', 'Bs2DsKst_delta', 'Bs2DsKst_lambda', 'Bs2DsKst_phi_w',
	    #'.+Asym.+',
            #'.+TagEff.+',
            ],
}
