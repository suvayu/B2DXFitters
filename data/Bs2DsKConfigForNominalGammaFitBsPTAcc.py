def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  0.657   # in ps^{-1}
    configdict["DeltaGammas"] = -0.104
    configdict["DeltaMs"]     =  17.69   # in ps^{-1}
    configdict["TagEffSig"]   = 0.403
    configdict["TagOmegaSig"] = 0.396
    configdict["StrongPhase"] = 20. / 180. * pi
    configdict["WeakPhase"]   = 50. / 180. * pi
    configdict["ArgLf"]       = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"] = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]       = 0.372
    configdict["tacc_slope"]  = 1.09
    configdict["tacc_offset"] = 0.187
    configdict["tacc_beta"]   = 0.039
    configdict["resolutionScaleFactor"] = 1.15 
    configdict["resolutionMeanBias"]    = 0.
    configdict["DecayTimeResolutionModel"] = "TripleGaussian"
    configdict["calibration_p1"] = 1.035
    configdict["calibration_p0"] = -0.013
    configdict["TimeDown"] = 0.0
    configdict["TimeUp"] = 15.0
        


    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('deltaMs')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_slope')
    configdict["constParams"].append('tacc_offset')
    configdict["constParams"].append('tacc_beta')

    return configdict
