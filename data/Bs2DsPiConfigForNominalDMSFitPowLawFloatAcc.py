def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.661   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.105
    configdict["DeltaMs"]       = 17.6   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.391
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 70./180.*pi
    configdict["ArgLf"]         = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"]   = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]         = 0.372
    configdict["tacc_exponent"] = 1.83165e+00 #1.75 
    configdict["tacc_offset"]   = 1.94941e-02 #0.02
    configdict["tacc_beta"]     = 3.55134e-02 #3.5e-02 
    configdict["tacc_turnon"]   = 1.31231e+00 #1.3       

    #configdict["tacc_exponent"] = 3.99829e+00
    #configdict["tacc_offset"]   = 1.94941e-02
    #configdict["tacc_beta"]     = 6.66843e-02
    #configdict["tacc_turnon"]   = 4.55085e+00
    
    #configdict["tacc_exponent"] = 3.38331e+00
    #configdict["tacc_offset"]   = -1.06548e-02
    #configdict["tacc_beta"]     = 6.66414e-02
    #configdict["tacc_turnon"]   = 2.08435e+00
    
    #configdict["tacc_exponent"] = 1.5812e+00
    #configdict["tacc_offset"]   = 7.3449e-02
    #configdict["tacc_beta"]     = 5.5636e-02
    #configdict["tacc_turnon"]   = 6.2060e-01
    

    configdict["resolutionScaleFactor"] = 1.15 
    configdict["resolutionMeanBias"]    = 0.0
    configdict["DecayTimeResolutionModel"] = "TripleGaussian"
    configdict["DecayTimeErrInterpolation"] = True

    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
    
    configdict["TemplateFile"]            = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"
    configdict["TemplateWorkspace"]       = "workspace"
    configdict["MistagTemplateName"]      = "MistagPdf_signal_BDTGA"
    configdict["MistagVarName"]           = "lab0_BsTaggingTool_TAGOMEGA_OS"
    
    configdict["TimeErrorTemplateName"]   = "TimeErrorPdf_signal_BDTGA"
    
    configdict["TimeDown"]     = 0.2
    configdict["TimeUp"]   = 15.0

    configdict["nBinsMistag"]   = 50
    configdict["nBinsProperTimeErr"]   = 50
    configdict["nBinsAcceptance"]   = 740    
    
            

    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_exponent')
    configdict["constParams"].append('tacc_offset')
    configdict["constParams"].append('tacc_beta')
    configdict["constParams"].append('tacc_turnon')
    #configdict["constParams"].append('DeltaMs')

    return configdict
