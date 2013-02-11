def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.661   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.105
    configdict["DeltaMs"]       =  17.69   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.396
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 70. / 180. * pi
    configdict["ArgLf"]         = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"]   = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]         = 0.372
    configdict["tacc_exponent"] = 1.83
    configdict["tacc_offset"]   = 0.0200
    configdict["tacc_beta"]     = 0.0344
    configdict["tacc_turnon"]   = 1.43  
    configdict["resolutionScaleFactor"] = 1.15  
    configdict["resolutionMeanBias"]    = 0.0
    configdict["DecayTimeResolutionModel"] = "TripleGaussian"
    configdict["TimeDown"]     = 0.0
    configdict["TimeUp"]   = 15.0
        

    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('DeltaMs')

    return configdict
