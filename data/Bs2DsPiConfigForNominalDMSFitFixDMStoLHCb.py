def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.657   # in ps^{-1}
    configdict["DeltaGammas"]   = -0.104
    configdict["DeltaMs"]       =  17.725   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.396
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 70. / 180. * pi
    configdict["ArgLf"]         = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"]   = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]         = 0.384
    configdict["tacc_exponent"] = 1.849
    configdict["tacc_offset"]   = 0.0373
    configdict["tacc_beta"]     = 0.0363
    configdict["tacc_turnon"]   = 1.215  
    configdict["resolutionScaleFactor"] = 1.15  
    configdict["resolutionMeanBias"]    = 0.
    configdict["DecayTimeResolutionModel"] = "TripleGaussian"
    configdict["TimeDown"]     = 0.0
    configdict["TimeUp"]   = 15.0
         

    configdict["constParams"] = []
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_exponent')
    configdict["constParams"].append('tacc_offset')
    configdict["constParams"].append('tacc_beta')
    configdict["constParams"].append('tacc_turnon')
    configdict["constParams"].append('DeltaMs')

    return configdict
