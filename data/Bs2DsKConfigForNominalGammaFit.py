def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  0.66 #0.661   # in ps^{-1}
    configdict["DeltaGammas"] = -0.11 #-0.105
    configdict["DeltaMs"]     =  17.72 #17.768   # in ps^{-1}
    configdict["TagEffSig"]   = 0.403
    configdict["TagOmegaSig"] = 0.39 #0.396
    configdict["StrongPhase"] = -40. / 180. * pi
    configdict["WeakPhase"]   = 100. / 180. * pi
    configdict["ArgLf"]       = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"] = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]       = 0.372
    #configdict["tacc_exponent"] = 1.8491e+00 #1.8518e+00 #1.75
    #configdict["tacc_offset"]   = 1.9146e-02 #1.9557e-02 #0.02
    #configdict["tacc_beta"]     = 3.5365e-02 #3.5166e-02 #3.5e-02
    #configdict["tacc_turnon"]   = 1.3322e+00 #1.3300e+00 #1.3

    #configdict["tacc_exponent"] = 1.83214e+00
    #configdict["tacc_offset"]   = 1.98046e-02
    #configdict["tacc_beta"]     = 3.55307e-02
    #configdict["tacc_turnon"]   = 1.31250e+00

    configdict["tacc_exponent"] = 1.83184e+00
    configdict["tacc_offset"]   = 1.94729e-02
    configdict["tacc_beta"]     = 3.55230e-02
    configdict["tacc_turnon"]   = 1.31231e+00
                
    
    configdict["resolutionScaleFactor"] = 1.37 
    configdict["resolutionMeanBias"]    = 0.
    configdict["DecayTimeResolutionModel"] = "TripleGaussianPEDTE"
    configdict["DecayTimeErrInterpolation"] = True

    configdict["resolutionSigma1"] = 2.21465e-02
    configdict["resolutionSigma2"] = 3.72057e-02
    configdict["resolutionSigma3"] = 6.37859e-02
    configdict["resolutionFrac1"]  = 3.62689e-01
    configdict["resolutionFrac2"]  = 5.65100e-01
                    

    configdict["calibration_p1"] = 1.03 #1.035 #1.035
    configdict["calibration_p0"] = 0.39 #0.392 #-0.013
        
    configdict["TimeDown"] = 0.2
    configdict["TimeUp"] = 15.0
        
    configdict["nBinsMistag"]   = 50
    configdict["nBinsProperTimeErr"]   = 50
    configdict["nBinsAcceptance"]   = 740

    configdict["TemplateFilePi"]      = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"
    configdict["TemplateFileK"]      = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsK.root"
    
    configdict["TemplateWorkspace"]       = "workspace"
    configdict["MistagTemplateName"]      = "MistagPdf_signal_BDTGA"
    configdict["MistagVarName"]           = "lab0_BsTaggingTool_TAGOMEGA_OS"
    configdict["MistagInterpolation"]     =   False
    configdict["TimeErrorTemplateBDTGA"]  = "TimeErrorPdf_signal_BDTGA"
    
    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('deltaMs')
    #configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_exponent')
    configdict["constParams"].append('tacc_offset')
    configdict["constParams"].append('tacc_beta')
    configdict["constParams"].append('tacc_turnon')

    return configdict
