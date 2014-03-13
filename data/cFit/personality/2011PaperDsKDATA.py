# personality for 2011 Paper - mode DsK for DATA
{
        'IsToy':                False,
        'DataFileName':         os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/WS_Mass_DsK_5M_BDTGA.root',
        'DataWorkSpaceName':    'FitMeToolWS',
        'DataSetNames':         'combData',
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
        'DeltaMs':                      17.768, # in ps^{-1}
        'GammaLb':			0.700, # in ps^{-1}
        'GammaCombBkg':			0.971, # in ps^{-1}
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
        'MassTemplateFile':             os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/WS_Mass_DsK_5M_BDTGA.root',
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
                    [ [ 0.3834, 0.9994, 0.3834 ] ],
                    [ [ 0.4244, 1.0002, 0.4244 ] ],
                    [ [ 0.3625, 0.9998, 0.3625 ] ],
                    ],
                'Bd': [
                    [ [ 0.3834, 0.9994, 0.3834 ] ],
                    [ [ 0.5, 0., 0. ] ],
                    [ [ 0.3625, 0.9998, 0.3625 ] ],
                    ],
                },
        'Constraints': {
                'Bs2DsK_Mistag0CalibB_p0': 0.0042,
                'Bs2DsK_Mistag0CalibB_p1': 0.0382,
                'Bs2DsK_Mistag1CalibB_p0': 0.0112,
                'Bs2DsK_Mistag1CalibB_p1': 0.1502,
                'Bs2DsK_Mistag2CalibB_p0': 0.0051,
                'Bs2DsK_Mistag2CalibB_p1': 0.0407,
                'Bd_Mistag0CalibB_p0': 0.0042,
                'Bd_Mistag0CalibB_p1': 0.0382,
                'Bd_Mistag2CalibB_p0': 0.0051,
                'Bd_Mistag2CalibB_p1': 0.0407,
                'Bd2DPi_lambda': 0.3 * 0.0187,
                'Bd2DPi_avgSSbar': [ '0.5*(@0+@1)', ['Bd2DPi_S', 'Bd2DPi_Sbar'], +0.046, 0.023 ],
                'Bd2DPi_difSSbar': [ '0.5*(@0-@1)', ['Bd2DPi_S', 'Bd2DPi_Sbar'], -0.022, 0.021 ],
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
                'Lb2LcPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Lb2LcPi',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bd2DK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bd2DK',
                    'VarName': 'lab0_LifetimeFit_ctauErr', },
                'Bd2DPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_Data_Terr_BsDsK.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'TimeErrorPdf_Bd2DPi',
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
                'Bs2DsstPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5320_5420.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Bs2DsstPi_both',
                    'VarName': 'kfactorVar', },
                'Bs2DsRho': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5320_5420.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Bs2DsRho_both',
                    'VarName': 'kfactorVar', },
                'Lb2LcK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5320_5420.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Lb2LcK_both',
                    'VarName': 'kfactorVar', },
                'Lb2LcPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5320_5420.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Lb2LcPi_both',
                    'VarName': 'kfactorVar', },
                'Lb2Dsp': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5320_5420.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Lb2Dsp_both',
                    'VarName': 'kfactorVar', },
                'Lb2Dsstp': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5320_5420.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Lb2Dsstp_both',
                    'VarName': 'kfactorVar', },
                'Bd2DK': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5320_5420.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Bd2DK_both',
                    'VarName': 'kfactorVar', },
                'Bd2DPi': {
                    'File': os.environ['B2DXFITTERSROOT']+'/data/workspace/MDFitter/template_MC_KFactor_BsDsK_5320_5420.root',
                    'Workspace': 'workspace',
                    'TemplateName': 'kFactor_Bd2DPi_both',
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
