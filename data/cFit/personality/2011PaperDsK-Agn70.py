# personality for 2011 Paper - mode DsK
{
	'UseKFactor': False,
        'Modes': [
            'Bs2DsK',
            'Bs2DsKst',
            'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho',
            'Bd2DK', 'Bd2DPi', 'Bd2DsK',
            'Lb2LcK', 'Lb2LcPi', 'Lb2Dsp', 'Lb2Dsstp',
            'CombBkg'
            ],
        'SampleCategories': [
            'nonres', 'phipi', 'kstk', 'kpipi', 'pipipi'
            ],
	'DGsOverGs':                    -0.105/0.661, # DeltaGammas / Gammas
        'DeltaMs':                      17.768, # in ps^{-1}
        'GammaLb':			0.700, # in ps^{-1}
        'GammaCombBkg':			0.800, # in ps^{-1}
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
            'Bd2DPi':           20. / 180. * pi
            },
        'ModLf': {
	    'Bs2DsK': 	0.372,
	    'Bs2DsstK': 	0.372,
	    'Bs2DsKst': 	0.372,
	    'Bs2DsstKst': 	0.372,
	    'Bd2DPi':       0.015
	    },
        'AcceptanceCorrectionFile': None,
        'CombineModesForEffCPObs': [ ],
        'NEvents':			[ 3474. ],
        'DataFileName':         ('/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/For1fbPaper/Gamma70_WProdDetAsy_NoKFactors_5M_2T_MD/MassFitResults/Nominal/DsK_Toys_Work_ForMassPlot_%d.root' if haveAFS else
            os.environ['B2DXFITTERSROOT']+'/scripts/paper-dsk-agn70-nominal/data-nok/DsK_Toys_Work_ForMassPlot_%d.root') % TOY_NUMBER,
        'DataWorkSpaceName':    'FitMeToolWS',
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
        'FitRanges': {
		'time':     [0.4, 15.],
		'timeerr':  [1e-6, 0.25],
		'mistag':   [0., 0.5],
		'mass':     [5320., 5420.],
		'dsmass':   [1930., 2015.],
		'pidk':     [0., 150.]
		},
        'MassTemplateFile':             ('/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/For1fbPaper/Gamma70_WProdDetAsy_NoKFactors_5M_2T_MD/MassFitResults/Nominal/DsK_Toys_Work_ForMassPlot_%d.root' if haveAFS else
            os.environ['B2DXFITTERSROOT']+'/scripts/paper-dsk-agn70-nominal/data-nok/DsK_Toys_Work_ForMassPlot_%d.root') % TOY_NUMBER,
        'MassTemplateWorkspace':	'FitMeToolWS',
        'MassInterpolation':		False,
        'NTaggers':                     3,
        'TagEff':                    {
            'Bs2DsK': [ 0.3870 * (1. - 0.4772), 0.4772 * (1. - 0.3870), 0.3870 * 0.4772 ],
            'Lb': [ 0.3870, 0.4772 ],
            'Bd': [ 0.3870, 0.4772 ],
            },
        'MistagTemplates': {
            'Bs2DsK': [
                {   'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_1',
                    'VarName': 'tagOmegaComb', },
                {   'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_2',
                    'VarName': 'tagOmegaComb', },
                {   'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_3',
                    'VarName': 'tagOmegaComb', },
                ],
            'Bd2DPi': [
                {   'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Mistag_BDPi.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_1',
                    'VarName': 'tagOmegaComb', },
                {   'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Mistag_BDPi.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_2',
                    'VarName': 'tagOmegaComb', },
                {   'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Mistag_BDPi.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_1',
                    'VarName': 'tagOmegaComb', },
                ],
            'CombBkg': [
                {   'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Mistag_CombBkg.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_1',
                    'VarName': 'tagOmegaComb', },
                {   'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Mistag_CombBkg.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'sigMistagPdf_2',
                    'VarName': 'tagOmegaComb', },
                {   'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Mistag_CombBkg.root',
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
                'Bd': [
                    [ [ 0., 1., 0. ] ],
                    [ [ 0.5, 0., 0. ] ],
                    [ [ 0., 1., 0. ] ],
                    ],
                },
        'Constraints': {
                'Bd2DPi_lambda': 0.3 * 0.015,
                'Bd2DPi_avgSSbar': [ '0.5*(@0+@1)', ['Bd2DPi_S', 'Bd2DPi_Sbar'], +0.046, 0.023 ],
                'Bd2DPi_difSSbar': [ '0.5*(@0-@1)', ['Bd2DPi_S', 'Bd2DPi_Sbar'], -0.022, 0.021 ],
		'Bd_AsymProd': 0.01,
		'Bs_AsymProd': 0.01,
		'Lb_AsymProd': 0.03,
		'Bd2DK_AsymDet':	0.01,
		'Bd2DPi_AsymDet':	0.01,
		'Bd2DsK_AsymDet':	0.01,
		'Bs2DsPi_AsymDet':	0.01,
		'Lb2LcK_AsymDet':	0.03,
		'Lb2LcPi_AsymDet':	0.03,
		'CombBkg_AsymDet':	0.01,
		'Lb2Dsp_AsymDet':	0.03,
		'Lb2Dsstp_AsymDet':	0.03,
		'Bs2DsstPi_AsymDet':	0.01,
		'Bs2DsRho_AsymDet':	0.01,
                },
        'Asymmetries': {
                'Prod': {
		    'Bs': -0.014,
		    'Bd': 0.011,
		    'Lb': 0.03,
		    },
		'Det': {
		        'Bs2DsK':	0.01,
			'Bd2DK':	0.01,
			'Bd2DPi':	0.005,
			'Bd2DsK':	0.01,
			'Bs2DsPi':	0.005,
			'Lb2LcK':	0.01,
			'Lb2LcPi':	0.005,
			'CombBkg':	0.01,
			'Lb2Dsp':	0.02,
			'Lb2Dsstp':	0.02,
			'Bs2DsstPi':	0.005,
			'Bs2DsRho':	0.005,
		    },
		'TagEff': {}, 'TagEff_t': {}, 'TagEff_f': {},
                },
        'DecayTimeResolutionModel':	'GaussianWithPEDTE',
        'DecayTimeResolutionScaleFactor': 1.37,
        'DecayTimeErrorTemplates': {
                'Bs2DsK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bs2DsK',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bs2DsPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bs2DsPi',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bs2DsRho': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bs2DsRho',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bs2DsstPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bs2DsstPi',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Lb2Dsp': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Lb2Dsp',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Lb2Dsstp': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Lb2Dsstp',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Lb2LcK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Lb2LcK',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Lb2LcPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Lb2LcPi',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bd2DK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bd2DK',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bd2DPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bd2DPi',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'CombBkg': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_CombBkg',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                },
        'AcceptanceFunction': 'Spline',
	'AcceptanceSplineCoeffs':   { # dspi data dsk mc dspi mc
	    'MC': {
		'Bs2DsPi':      [ 0.179, 0.294, 0.690, 1.125, 1.245, 1.270 ],
		'Bs2DsK':       [ 1.77520e-01, 2.89603e-01, 6.79455e-01, 1.11726e+00, 1.23189e+00, 1.26661e+00 ],
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
	    '.+Asym.+',
            ],
}
