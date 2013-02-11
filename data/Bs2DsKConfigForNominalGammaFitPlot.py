def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  0.661   # in ps^{-1}
    configdict["DeltaGammas"] = -0.105
    configdict["DeltaMs"]     =  17.69   # in ps^{-1}
    configdict["TagEffSig"]   = 0.403
    configdict["TagOmegaSig"] = 0.396
    configdict["StrongPhase"] = 20. / 180. * pi
    configdict["WeakPhase"]   = 50. / 180. * pi
    configdict["ArgLf"]       = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"] = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]       = 0.372
    configdict["tacc_exponent"] = 1.849
    configdict["tacc_offset"]   = 0.0373
    configdict["tacc_beta"]     = 0.0363
    configdict["tacc_turnon"]   = 1.215
    configdict["resolutionScaleFactor"] = 1.15 
    configdict["resolutionMeanBias"]    = 0.
    configdict["DecayTimeResolutionModel"] = "TripleGaussian"
    configdict["calibration_p1"] = 1.035
    configdict["calibration_p0"] = -0.013
    configdict["sigC"] = 0.93233
    configdict["sigS"] = -0.082831
    configdict["sigD"] = -1.3475
    configdict["sigSbar"] = 1.1580
    configdict["sigDbar"] = -0.78309
    configdict["TimeDown"] = 0.0
    configdict["TimeUp"] = 0.15
        


    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('deltaMs')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_exponent')
    configdict["constParams"].append('tacc_offset')
    configdict["constParams"].append('tacc_beta')
    configdict["constParams"].append('tacc_turnon')
    configdict["constParams"].append('C')
    configdict["constParams"].append('S')
    configdict["constParams"].append('D')
    configdict["constParams"].append('Sbar')
    configdict["constParams"].append('Dbar')
    configdict["constParams"].append('Cbar')

    return configdict
