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
    configdict["WeakPhase"]     = 70./180.*pi
    configdict["ArgLf"]         = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"]   = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]         = 0.372

    configdict["tacc_size"]   = 6
    configdict["tacc_knots"]  = [0.50, 1.0,  1.5, 2.0, 3.0, 12.0]
    configdict["tacc_values"] = [0.459, 0.690, 0.885, 1.130, 1.223, 1.228]
    
    configdict["resolutionScaleFactor"] = 1.37 
    configdict["resolutionMeanBias"]    = 0.0
    configdict["DecayTimeResolutionModel"] = "TripleGaussian"  #TripleGaussian,PEDTE
    configdict["DecayTimeErrInterpolation"] = True
    configdict["resolutionSigma1"] = 2.14946e-02
    configdict["resolutionSigma2"] = 3.67643e-02
    configdict["resolutionSigma3"] = 6.37859e-02
    configdict["resolutionFrac1"]  = 3.72147e-01
    configdict["resolutionFrac2"]  = 5.65150e-01
    
    
    configdict["calibration_p1"] = 1.035
    configdict["calibration_p0"] = 0.392
    
    configdict["MistagFile"]     = "../data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root"
    configdict["MistagWork"]     = "workspace"
    configdict["MistagTempName"] = ["sigMistagPdf_1", "sigMistagPdf_2", "sigMistagPdf_3"]

    configdict["TerrFile"]     = "../data/workspace/MDFitter/template_Data_Terr_Bs2DsPi_BDTGA.root"
    configdict["TerrWork"]     = "workspace"
    configdict["TerrTempName"] = "TimeErrorPdf_Bs2DsPi"
    
    
    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('DeltaMs')
    configdict["constParams"].append('TagOmegaSig')
    #configdict["constParams"].append('calibration_p1')
    #configdict["constParams"].append('calibration_p0')
    configdict["constParams"].append('avmistag')
    
    return configdict
