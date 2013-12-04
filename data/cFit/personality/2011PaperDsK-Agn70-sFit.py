# personality for 2011 Paper - mode DsK
{
        'Modes': [
            'Bs2DsK',
            'Bs2DsKst',
            'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho',
            'Bd2DK', 'Bd2DsK',
            'Lb2LcK', 'Lb2Dsp', 'Lb2Dsstp',
            'CombBkg'
            ],
        'SampleCategories': [
            'nonres', 'phipi', 'kstk', 'kpipi', 'pipipi'
            ],
        'DeltaMs':                      17.768, # in ps^{-1}
        'GammaLb':			0.700, # in ps^{-1}
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
        'AcceptanceCorrectionFile': None,
        'CombineModesForEffCPObs': [ ],
        'NEvents':			[ 3474. ],
        'DataFileName': ('/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M_2T/DsK_Toys_sWeights_ForTimeFit_%d.root' if haveAFS else
		os.environ['B2DXFITTERSROOT']+'/scripts/paper-dsk-agn70-nominal/sfit/DsK_Toys_sWeights_ForTimeFit_%d.root')% TOY_NUMBER,
        'FitMode': 'sFit',
        'DataWorkSpaceName':    'FitMeToolWS',
        'DataSetNames': 'merged',
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
        'MassTemplateFile':             ('/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M_2T/DsK_Toys_Work_ForMassPlot_%d.root' if haveAFS else
            os.environ['B2DXFITTERSROOT']+'/scripts/paper-dsk-agn70-nominal/data/DsK_Toys_Work_ForMassPlot_%d.root') % TOY_NUMBER,
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
                    'TemplateName': 'sigMistagPdf_3',
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
        'Asymmetries': {
                'Prod': {}, 'Det': { }, 'TagEff': {}, 'TagEff_t': {}, 'TagEff_f': {},
                },
        'DecayTimeResolutionModel':	'GaussianWithPEDTE',
        'DecayTimeResolutionScaleFactor': 1.37,
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
                'Bs2DsRho': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bs2DsRho',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bs2DsstPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bs2DsstPi',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Lb2Dsp': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Lb2Dsp',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Lb2Dsstp': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Lb2Dsstp',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Lb2LcK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Lb2LcK',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bd2DK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bd2DK',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'CombBkg': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_CombBkg',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                },
        'KFactorTemplates': {
                'Bs2DsPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Bs2DsPi_both',
                    'VarName': 'kfactorVar', },
                'Bs2DsstPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Bs2DsstPi_both',
                    'VarName': 'kfactorVar', },
                'Bs2DsRho': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Bs2DsRho_both',
                    'VarName': 'kfactorVar', },
                'Lb2LcK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Lb2LcK_both',
                    'VarName': 'kfactorVar', },
                'Lb2Dsp': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Lb2Dsp_both',
                    'VarName': 'kfactorVar', },
                'Lb2Dsstp': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Lb2Dsstp_both',
                    'VarName': 'kfactorVar', },
                'Bd2DK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5300_5800.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Bd2DK_both',
                    'VarName': 'kfactorVar', },
                },
        'AcceptanceFunction': 'Spline',
        'constParams': [
            'Gammas', 'deltaGammas', 'deltaMs',
            'Gammad', 'deltaGammad', 'deltaMd',
            'mistag', 'timeerr_bias', 'timeerr_scalefactor',
            '.+_Mistag[0-9]+Calib(B|Bbar)_p[0-9]+',
            'Bs2DsKst_TagEff[0-9]', 'Bs2DsKst_delta', 'Bs2DsKst_lambda', 'Bs2DsKst_phi_w',
            ],
}
