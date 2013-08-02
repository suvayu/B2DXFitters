def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.661   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.105
    configdict["DeltaMs"]       = 17.768   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.391
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 50./180.*pi #70. / 180. * pi
    configdict["ArgLf"]         = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"]   = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]         = 0.372
    configdict["tacc_exponent"] = 1.8540e+00  #1.8518e+00 #1.75 
    configdict["tacc_offset"]   = 1.9146e-02 #1.9557e-02 #0.02
    configdict["tacc_beta"]     = 3.5104e-02 #3.5166e-02 #3.5e-02 
    configdict["tacc_turnon"]   = 1.3324e+00 #1.3300e+00 #1.3       

    #configdict["tacc_exponent"] = 3.9134e+00
    #configdict["tacc_offset"]   = 1.9146e-02
    #configdict["tacc_beta"]     = 6.6705e-02
    #configdict["tacc_turnon"]   = 5.0000e+00
    
    #configdict["tacc_exponent"] = 3.2592e+00
    #configdict["tacc_offset"]   = 1.9146e-02
    #configdict["tacc_beta"]     = 6.4844e-02
    #configdict["tacc_turnon"]   = 2.1415e+00
    
    #configdict["tacc_exponent"] = 2.4785e+00
    #configdict["tacc_offset"]   = 1.9146e-02
    #configdict["tacc_beta"]     = 2.1540e-02
    #configdict["tacc_turnon"]   = 6.9900e-01
     

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
    #configdict["constParams"].append('tacc_exponent')
    configdict["constParams"].append('tacc_offset')
    #configdict["constParams"].append('tacc_beta')
    #configdict["constParams"].append('tacc_turnon')
    #configdict["constParams"].append('DeltaMs')

    return configdict
