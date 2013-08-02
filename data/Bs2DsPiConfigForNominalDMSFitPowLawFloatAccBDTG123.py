def getconfig() :

    configdict = {}
    
    from math import pi

    # PHYSICAL PARAMETERS
    configdict["Gammas"]        =  0.661   # in ps^{-1}
    configdict["DeltaGammas"]   =  -0.105
    configdict["DeltaMs"]       = 17.6   # in ps^{-1}
    configdict["TagEffSig"]     = 0.403
    configdict["TagOmegaSig"]   = 0.391
    configdict["StrongPhase"]   = 20. / 180. * pi
    configdict["WeakPhase"]     = 50./180.*pi #70. / 180. * pi
    configdict["ArgLf"]         = configdict["StrongPhase"] - configdict["WeakPhase"]
    configdict["ArgLbarfbar"]   = configdict["StrongPhase"] + configdict["WeakPhase"]
    configdict["ModLf"]         = 0.372
    #configdict["tacc_exponent"] = 1.8733e+00 #1.8757e+00 #1.75 
    #configdict["tacc_offset"]   = 1.7046e-02 #1.6763e-02 #2.0e-02 
    #configdict["tacc_beta"]     = 3.4305e-02 #3.4453e-02 #0.03 
    #configdict["tacc_turnon"]   = 1.3608e+00 #1.3622e+00 #1.3   

    configdict["tacc_exponent_BDTG1"] = 3.9134e+00
    configdict["tacc_offset_BDTG1"]   = 1.9146e-02
    configdict["tacc_beta_BDTG1"]     = 6.6705e-02
    configdict["tacc_turnon_BDTG1"]   = 5.0000e+00

    configdict["tacc_exponent_BDTG2"] = 3.2592e+00 
    configdict["tacc_offset_BDTG2"]   = 1.9146e-02
    configdict["tacc_beta_BDTG2"]     = 6.4844e-02
    configdict["tacc_turnon_BDTG2"]   = 2.1415e+00

    configdict["tacc_exponent_BDTG3"] = 2.4785e+00
    configdict["tacc_offset_BDTG3"]   = 1.9146e-02
    configdict["tacc_beta_BDTG3"]     = 2.1540e-02
    configdict["tacc_turnon_BDTG3"]   = 6.9900e-01
    
    
                

    configdict["resolutionScaleFactor"] = 1.15  
    configdict["resolutionMeanBias"]    = 0.0
    configdict["DecayTimeResolutionModel"] = "PEDTETripleGaussian"
    
    configdict["calibration_p1"] = 1.035 #1.035
    configdict["calibration_p0"] = 0.392 #-0.013
    
    configdict["TemplateFile"]            = "/afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/templates_BsDsPi.root"
    configdict["TemplateWorkspace"]       = "workspace"
    configdict["MistagTemplateName"]      = "MistagPdf_signal_BDTGA"
    configdict["MistagVarName"]           = "lab0_BsTaggingTool_TAGOMEGA_OS"
    configdict["TimeErrorTemplateName"]   = "TimeErrorPdf_signal_BDTGA"
    
    configdict["TimeDown"]     = 0.2
    configdict["TimeUp"]   = 15.0

    configdict["nBinsMistag"]         = 50
    configdict["nBinsProperTimeErr"]  = 50
    configdict["nBinsAcceptance"]     = 740
    
    configdict["constParams"] = []
    configdict["constParams"].append('Gammas')
    configdict["constParams"].append('deltaGammas')
    configdict["constParams"].append('tagEffSig')
    #configdict["constParams"].append('tacc_exponent')
    #configdict["constParams"].append('tacc_offset')
    #configdict["constParams"].append('tacc_beta')
    #configdict["constParams"].append('tacc_turnon')

    #configdict["constParams"].append('tacc_exponent_BDTG1')
    configdict["constParams"].append('tacc_offset_BDTG1')
    configdict["constParams"].append('tacc_beta_BDTG1')
    configdict["constParams"].append('tacc_turnon_BDTG1')
    #configdict["constParams"].append('tacc_exponent_BDTG2')
    configdict["constParams"].append('tacc_offset_BDTG2')
    configdict["constParams"].append('tacc_beta_BDTG2')
    configdict["constParams"].append('tacc_turnon_BDTG2')
    #configdict["constParams"].append('tacc_exponent_BDTG3')
    configdict["constParams"].append('tacc_offset_BDTG3')
    configdict["constParams"].append('tacc_beta_BDTG3')
    configdict["constParams"].append('tacc_turnon_BDTG3')
                
                
    #configdict["constParams"].append('DeltaMs')

    return configdict
