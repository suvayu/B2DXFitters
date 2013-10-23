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
    #configdict["tacc_exponent"] = 1.83165e+00 #1.75 
    #configdict["tacc_offset"]   = 1.94941e-02 #0.02
    #configdict["tacc_beta"]     = 3.55134e-02 #3.5e-02 
    #configdict["tacc_turnon"]   = 1.31231e+00 #1.3

    #Giulia 16/09/2013: They were uncommented before
    #configdict["tacc_exponent"] = 1.83214e+00
    #configdict["tacc_offset"]   = 1.98046e-02
    #configdict["tacc_beta"]     = 3.55307e-02
    #configdict["tacc_turnon"]   = 1.31250e+00

    #Giulia 16/09/2013: New acceptance parameters for my ntuples Reco12 2011 strip17 DVv33r6 Urania v1r1
    configdict["tacc_exponent"] = 1.86044e+00
    configdict["tacc_offset"]   = 1.63120e-02
    configdict["tacc_beta"]     = 3.47647e-02
    configdict["tacc_turnon"]   = 1.30957e+00
                

    #configdict["tacc_exponent"] = 1.83184e+00
    #configdict["tacc_offset"]   = 1.94729e-02
    #configdict["tacc_beta"]     = 3.55230e-02                
    #configdict["tacc_turnon"]   = 1.31231e+00
    

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
    configdict["calibration_p0"] = 0.392 #-0.013
    
    configdict["TemplateFile"]            = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"
    #"/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"
    configdict["TemplateWorkspace"]       = "workspace"
    configdict["MistagTemplateName"]      = "MistagPdf_signal_BDTGA"
    configdict["MistagVarName"]           = "lab0_BsTaggingTool_TAGOMEGA_OS"
    
    configdict["TimeErrorTemplateName"]   = "TimeErrorPdf_signal_BDTGA"
    
    configdict["TimeDown"]     = 0.2
    configdict["TimeUp"]   = 15.0

    configdict["nBinsMistag"]   = 50
    configdict["nBinsProperTimeErr"]   = 50 #740
    configdict["nBinsAcceptance"]   = 370 #740    
    
            

    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_exponent')
    configdict["constParams"].append('tacc_offset')
    configdict["constParams"].append('tacc_beta')
    configdict["constParams"].append('tacc_turnon')
    configdict["constParams"].append('DeltaMs')
    configdict["constParams"].append('TagOmegaSig')
    #configdict["constParams"].append('calibration_p1')
    #configdict["constParams"].append('calibration_p0')
    configdict["constParams"].append('avmistag')
    
    return configdict
