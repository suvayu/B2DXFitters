def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.661   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.105
    configdict["DeltaMs"]       = 17.77 # 17.69   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.391
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 50./180.*pi #70. / 180. * pi
    configdict["ArgLf"]         = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"]   = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]         = 0.372
    configdict["tacc_exponent"] = 1.8606e+00 #1.75 #,1.83
    configdict["tacc_offset"]   = 1.7117e-02 #0.01 #,0.0200
    configdict["tacc_beta"]     = 3.4987e-02 #0.01 #0.0344
    configdict["tacc_turnon"]   = 1.3298e+00 #1.4  #1.43  

    configdict["resolutionScaleFactor"] = 1.15  
    configdict["resolutionMeanBias"]    = 0.0
    configdict["DecayTimeResolutionModel"] = "PEDTETripleGaussian"
    configdict["DecayTimeErrInterpolation"] = True

    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
    
    configdict["TemplateFile"]      = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"
    configdict["TemplateWorkspace"] = "workspace"
    configdict["MistagTemplateName"]      = "MistagPdf_signal_BDTGA"
    configdict["MistagVarName"]           = "lab0_BsTaggingTool_TAGOMEGA_OS"
    configdict["MistagInterpolation"]     =   False,

    configdict["TimeErrorTemplateName"]   = "TimeErrorPdf_signal_BDTGA"
    
    configdict["TimeDown"]     = 0.2
    configdict["TimeUp"]   = 15.0

    configdict["nBinsMistag"]   = 100 #64
    configdict["nBinsPerEventTimeErr"]   = 100# 64
    configdict["nBinsProperTimeErr"]   = 40
    configdict["nBinsAcceptance"]   = 500
    
    
            

    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('tagEffSig')
    #configdict["constParams"].append('tacc_exponent')
    #configdict["constParams"].append('tacc_offset')
    #configdict["constParams"].append('tacc_beta')
    #configdict["constParams"].append('tacc_turnon')
    configdict["constParams"].append('DeltaMs')

    return configdict
