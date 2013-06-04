def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  0.657   # in ps^{-1}
    configdict["DeltaGammas"] = -0.104
    configdict["DeltaMs"]     =  17.768 #17.5   # in ps^{-1}
    configdict["TagEffSig"]   = 0.403
    configdict["TagOmegaSig"] = 0.396
    configdict["StrongPhase"] = 20. / 180. * pi
    configdict["WeakPhase"]   = 70. / 180. * pi
    configdict["ArgLf"]       = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"] = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]       = 0.372
    configdict["tacc_exponent"] = 1.8540e+00 #1.849
    configdict["tacc_offset"]   = 1.9149e-02 #0.0373
    configdict["tacc_beta"]     = 3.7524e-02 #0.0363
    configdict["tacc_turnon"]   = 1.3339e+00 #1.215
            
    #configdict["tacc_slope"]  = 1.09
    #configdict["tacc_offset"] = 0.187
    #configdict["tacc_beta"]   = 0.039
    configdict["resolutionScaleFactor"] = 1.15  
    configdict["resolutionMeanBias"]    = 0.
    configdict["DecayTimeResolutionModel"] = "TripleGaussian"
    configdict["TimeDown"] = 0.0
    configdict["TimeUp"]   = 15.0
        


    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('DeltaMs')

    return configdict
