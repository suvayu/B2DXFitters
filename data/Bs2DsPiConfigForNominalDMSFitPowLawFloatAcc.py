def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.661   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.105
    configdict["DeltaMs"]       =  17.69   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.391
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 50./180.*pi #70. / 180. * pi
    configdict["ArgLf"]         = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"]   = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]         = 0.372
    configdict["tacc_exponent"] = 1.849 #,1.83
    configdict["tacc_offset"]   = 0.0373 #,0.0200
    configdict["tacc_beta"]     = 0.0363 #0.0344
    configdict["tacc_turnon"]   = 1.215  #1.43  

    configdict["resolutionScaleFactor"] = 1.15  
    configdict["resolutionMeanBias"]    = 0.0
    configdict["DecayTimeResolutionModel"] = "TripleGaussian"
    configdict["DecayTimeErrInterpolation"] = True

    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
    
    configdict["MistagTemplateFile"]      = "../data/workspace/work_toys_dsk.root"
    configdict["MistagTemplateWorkspace"] = "workspace"
    configdict["MistagTemplateName"]      = "PhysBkgBsDsPiPdf_m_down_kkpi_mistag"
    configdict["MistagVarName"]           = "lab0_BsTaggingTool_TAGOMEGA_OS"
    configdict["MistagInterpolation"]     =   False,


    configdict["TimeDown"]     = 0.2
    configdict["TimeUp"]   = 15.0

    configdict["nBinsMistag"]   = 64
    configdict["nBinsPerEventTimeErr"]   = 64
    configdict["nBinsProperTimeErr"]   = 200
    configdict["nBinsAcceptance"]   = 300
    
    
            

    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('tagEffSig')
    #configdict["constParams"].append('DeltaMs')

    return configdict
