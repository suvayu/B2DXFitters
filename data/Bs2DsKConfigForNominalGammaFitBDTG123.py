def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]      =  0.661   # in ps^{-1}
    configdict["DeltaGammas"] = -0.105
    configdict["DeltaMs"]     =  17.768   # in ps^{-1}
    configdict["TagEffSig"]   = 0.403
    configdict["TagOmegaSig"] = 0.396
    configdict["StrongPhase"] = -40. / 180. * pi
    configdict["WeakPhase"]   = 100. / 180. * pi
    configdict["ArgLf"]       = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"] = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]       = 0.372
    #configdict["tacc_exponent"] = 1.8733e+00 #1.8757e+00 #1.75
    #configdict["tacc_offset"]   = 1.7046e-02 #1.6763e-02 #2.0e-02
    #configdict["tacc_beta"]     = 3.4305e-02 #3.4453e-02 #0.03
    #configdict["tacc_turnon"]   = 1.3608e+00 #1.3622e+00 #1.3

    configdict["tacc_exponent_BDTG1"] = 3.99829e+00
    configdict["tacc_offset_BDTG1"]   = -8.55864e-02
    configdict["tacc_beta_BDTG1"]     = 6.66843e-02
    configdict["tacc_turnon_BDTG1"]   = 4.55085e+00
    
    configdict["tacc_exponent_BDTG2"] = 3.38331e+00
    configdict["tacc_offset_BDTG2"]   = -1.06548e-02
    configdict["tacc_beta_BDTG2"]     = 6.66414e-02
    configdict["tacc_turnon_BDTG2"]   = 2.08435e+00
    
    configdict["tacc_exponent_BDTG3"] = 1.5812e+00
    configdict["tacc_offset_BDTG3"]   = 7.3449e-02
    configdict["tacc_beta_BDTG3"]     = 5.5636e-02
    configdict["tacc_turnon_BDTG3"]   = 6.2060e-01
    
    
    configdict["resolutionScaleFactor"] = 1.15 
    configdict["resolutionMeanBias"]    = 0.
    configdict["DecayTimeResolutionModel"] = "PEDTETripleGaussian"
    #configdict["calibration_p1"] = 1.035
    #configdict["calibration_p0"] = -0.013
    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
        
    configdict["TimeDown"] = 0.2
    configdict["TimeUp"] = 15.0
        
    configdict["nBinsMistag"]   = 50
    configdict["nBinsProperTimeErr"]   = 50
    configdict["nBinsAcceptance"]   = 740 #500

    configdict["TemplateFile"]      = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"
    configdict["TemplateWorkspace"] = "workspace"
    configdict["MistagTemplateName"]      = "MistagPdf_signal_BDTGA"
    configdict["MistagVarName"]           = "lab0_BsTaggingTool_TAGOMEGA_OS"
    configdict["MistagInterpolation"]     =   False
    configdict["TimeErrorTemplateBDTG1"]  = "TimeErrorPdf_signal_BDTG1"
    configdict["TimeErrorTemplateBDTG2"]  = "TimeErrorPdf_signal_BDTG2"
    configdict["TimeErrorTemplateBDTG3"]  = "TimeErrorPdf_signal_BDTG3"
    
    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('deltaMs')
    configdict["constParams"].append('tagEffSig')
    configdict["constParams"].append('tacc_exponent')
    configdict["constParams"].append('tacc_offset')
    configdict["constParams"].append('tacc_beta')
    configdict["constParams"].append('tacc_turnon')
    configdict["constParams"].append('tacc_exponent_BDTG1')
    configdict["constParams"].append('tacc_offset_BDTG1')
    configdict["constParams"].append('tacc_beta_BDTG1')
    configdict["constParams"].append('tacc_turnon_BDTG1')
    configdict["constParams"].append('tacc_exponent_BDTG2')
    configdict["constParams"].append('tacc_offset_BDTG2')
    configdict["constParams"].append('tacc_beta_BDTG2')
    configdict["constParams"].append('tacc_turnon_BDTG2')
    configdict["constParams"].append('tacc_exponent_BDTG3')
    configdict["constParams"].append('tacc_offset_BDTG3')
    configdict["constParams"].append('tacc_beta_BDTG3')
    configdict["constParams"].append('tacc_turnon_BDTG3')
    

    return configdict
