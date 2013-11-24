def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  0.661 #0.661   # in ps^{-1}
    configdict["DeltaGammas"] = -0.105 #-0.105
    configdict["DeltaMs"]     =  17.72 #17.768   # in ps^{-1}
    configdict["StrongPhase"] = -40. / 180. * pi
    configdict["WeakPhase"]   = 100. / 180. * pi
    configdict["ArgLf"]       = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"] = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]       = 0.372

    configdict["calibration_p0"]  = [0.3927, 0.4244]
    configdict["calibration_p1"]  = [0.9818, 1.2550]
    configdict["calibration_av"]  = [0.3919, 0.4097]
    
    configdict["tacc_values"] = [1.4525e-01*1.86413e-01/1.93184e-01,
                                 2.0995e-01*2.83214e-01/3.35302e-01,
                                 6.2524e-01*7.24952e-01/7.39033e-01,
                                 1.0291e+00*1.18847e+00/1.16141e+00,
                                 1.2577e+00*1.33798e+00/1.29660e+00,
                                 1.2405e+00*1.32593e+00/1.31712e+00]
    
    configdict["tagEff_OS"] = 0.387
    configdict["tagEff_SS"] = 0.4772
    
    configdict["TagEffSig"]    = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                  configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                  configdict["tagEff_OS"]*configdict["tagEff_SS"]]

    configdict["aTagEffSig"]    = [0.0, 0.0, 0.0]
    
    configdict["resolutionScaleFactor"] = 1.37 
    configdict["resolutionMeanBias"]    = 0.
    configdict["DecayTimeResolutionModel"] = "PEDTETripleGaussian"
    configdict["DecayTimeErrInterpolation"] = True

    configdict["resolutionSigma1"] = 2.21465e-02
    configdict["resolutionSigma2"] = 3.72057e-02
    configdict["resolutionSigma3"] = 6.37859e-02
    configdict["resolutionFrac1"]  = 3.62689e-01
    configdict["resolutionFrac2"]  = 5.65100e-01
               
    configdict["nBinsMistag"]   = 50
    configdict["nBinsProperTimeErr"]   = 50
    configdict["nBinsAcceptance"]   = 740

    configdict["TemplateFilePi"]      = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"
    configdict["TemplateFileK"]      = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsK.root"
    
    configdict["TemplateWorkspace"]       = "workspace"
    configdict["MistagTemplateName"]      = "MistagPdf_signal_BDTGA"
    configdict["MistagVarName"]           = "lab0_BsTaggingTool_TAGOMEGA_OS"
    configdict["MistagInterpolation"]     =   False
    configdict["TimeErrorTemplateBDTGA"]  = "TimeErrorPdf_signal_BDTGA"
    
    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('deltaMs')
    #configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_exponent_BDTGA')
    configdict["constParams"].append('tacc_offset_BDTGA')
    configdict["constParams"].append('tacc_beta_BDTGA')
    configdict["constParams"].append('tacc_turnon_BDTGA')

    return configdict
