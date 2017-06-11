from ROOT import *

def getconfig() :

    configdict = {}
    
    from math import pi
    from math import log
    
    # considered decay mode
    configdict["Decay"] = "Bd2DPi"
    configdict["CharmModes"] = {"KPiPi"} 
    # year of data taking
    configdict["YearOfDataTaking"] = {"2012"} 
    # stripping (necessary in case of PIDK shapes)
    configdict["Stripping"] = {"2012":"21"}
    # integrated luminosity in each year of data taking (necessary in case of PIDK shapes) 
    configdict["IntegratedLuminosity"] = {"2012": {"Down": 0.59, "Up": 0.44}}
    configdict["LumRatio"] = {"2012" :
                              configdict["IntegratedLuminosity"]["2012"]["Up"] / ( configdict["IntegratedLuminosity"]["2012"]["Up"] + configdict["IntegratedLuminosity"]["2012"]["Down"] ) }
    # file name with paths to MC/data samples
    configdict["dataName"]   = "../data/Bd2DPi_3fbCPV/Bd2DPi/config_Bd2DPi.txt"
        
    # basic variables
    configdict["BasicVariables"] = {}
    configdict["BasicVariables"]["BeautyMass"]    = { "Range"                  : [5000,    6000    ],
                                                      "Sideband"               : [5500,    6000    ],
                                                      "Name"                   : "BeautyMass",
                                                      "InputName"              : "lab0_MassFitConsD_M"}

    configdict["BasicVariables"]["CharmMass"]     = { "Range"                  : [1830,    1910    ],
                                                      "Name"                   : "CharmMass",
                                                      "InputName"              : "lab2_MM"}

    configdict["BasicVariables"]["BeautyTime"]    = { "Range"                  : [0.0,     15.0    ],
                                                      "Bins"                   : 40,
                                                      "Name"                   : "BeautyTime",
                                                      "InputName"              : "lab0_LifetimeFit_ctau"}
    
    configdict["BasicVariables"]["BacP"]          = { "Range"                  : [3000.0,  650000.0],
                                                      "Name"                   : "BacP",
                                                      "InputName"              : "lab1_P"}

    configdict["BasicVariables"]["BacPT"]         = { "Range"                  : [400.0,   45000.0 ],
                                                      "Name"                   : "BacPT",
                                                      "InputName"              : "lab1_PT"}

    configdict["BasicVariables"]["BacPIDK"]       = { "Range"                  : [1.61,    5.0     ],
                                                      "Name"                   : "BacPIDK",
                                                      "InputName"              : "lab1_PIDK"}

    configdict["BasicVariables"]["nTracks"]       = { "Range"                  : [15.0,    1000.0  ],
                                                      "Name"                   : "nTracks",
                                                      "InputName"              : "nTracks"}

    configdict["BasicVariables"]["BeautyTimeErr"] = { "Range"                  : [0.01,    0.1     ],
                                                      "Name"                   : "BeautyTimeErr",
                                                      "InputName"              : "lab0_LifetimeFit_ctauErr"}

    configdict["BasicVariables"]["BacCharge"]     = { "Range"                  : [-1000.0, 1000.0  ],
                                                      "Name"                   : "BacCharge",
                                                      "InputName"              : "lab1_ID"}

    configdict["BasicVariables"]["TagDecOS"]      = { "Range"                  : [-1.0,    1.0     ],
                                                      "Name"                   : "TagDecOS",
                                                      "InputName"              : "lab0_TAGDECISION_OS"}

    configdict["BasicVariables"]["TagDecSS"]      = { "Range"                  : [-1.0,    1.0     ],
                                                      "Name"                   : "TagDecSS",
                                                      "InputName"              : "lab0_SS_Pion_DEC"} 

    configdict["BasicVariables"]["MistagOS"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                      "Name"                   : "MistagOS",
                                                      "InputName"              : "lab0_TAGOMEGA_OS"}

    configdict["BasicVariables"]["MistagSS"]      = { "Range"                  : [ 0.0,    0.5     ],
                                                      "Name"                   : "MistagSS",
                                                      "InputName"              : "lab0_SS_Pion_PROB"}

    # additional MC variables in data sets
    configdict["MCVariables"] = {}
    configdict["MCVariables"]["BeautyBkgCat"]  =  { "Range"                    : [ -1.0,    1000.0 ],
                                                    "Name"                     : "BeautyBkgCat",
                                                    "InputName"                : "lab0_BKGCAT"}
    
    configdict["MCVariables"]["BeautyTrueID"]  =  { "Range"                    : [ -1000.0, 1000.0 ],
                                                    "Name"                     : "BeautyTrueID",
                                                    "InputName"                : "lab0_TRUEID"}
    

    # additional taggers
    configdict["AdditionalTagDec"] = {}
    configdict["AdditionalTagDec"]["TagDecSSProton"]   =  { "Range"            : [-1.0,    1.0     ],
                                                            "Name"             : "TagDecSSProton",
                                                            "InputName"        : "lab0_SS_Proton_DEC"}

    configdict["AdditionalTagDec"]["TagDecSSPion"]  =  { "Range"               : [-1.0,    1.0     ],
                                                         "Name"                : "TagDecSSPionBDT",
                                                         "InputName"           : "lab0_SS_PionBDT_DEC"}
    
    configdict["AdditionalTagDec"]["TagDecOSCharm"]   =  { "Range"            : [-1.0,    1.0     ],
                                                           "Name"             : "TagDecOSCharm",
                                                           "InputName"        : "lab0_OS_Charm_DEC"}
    
    
    configdict["AdditionalTagOmega"] = {}
    configdict["AdditionalTagOmega"]["MistagSSProton"]  =  { "Range"           : [0.0,     0.5     ],
                                                             "Name"            : "MistagSSProton",
                                                             "InputName"       : "lab0_SS_Proton_PROB"}
    
    configdict["AdditionalTagOmega"]["MistagSSPion"] =  { "Range"              : [0.0,     0.5     ],
                                                          "Name"               : "MistagSSPionBDT",
                                                          "InputName"          : "lab0_SS_PionBDT_PROB"}
    
    configdict["AdditionalTagOmega"]["MistagOSCharm"]  =  { "Range"           : [0.0,     0.5     ],
                                                            "Name"            : "MistagOSCharm",
                                                            "InputName"       : "lab0_OS_Charm_PROB"}
    

    # tagging calibration
    configdict["TaggingCalibration"] = {}
    configdict["TaggingCalibration"]["OS"]    = {"p0"   : 0.365517, "p1"   : 0.950216, "average"   : 0.371147,
                                                 "p0Bar": 0.376730, "p1Bar": 1.048155, "averageBar": 0.371147}
    configdict["TaggingCalibration"]["SS"]    = {"p0"   : 0.424801, "p1"   : 1.004340, "average"   : 0.414892,
                                                 "p0Bar": 0.404896, "p1Bar": 0.995879, "averageBar": 0.414892}
    configdict["TaggingCalibration"]["OS+SS"] = {"p0"   : 0.338781, "p1"   : 0.971845, "average"   : 0.338493,
                                                 "p0Bar": 0.338363, "p1Bar": 1.027861, "averageBar": 0.338493}

    # taggers to be combined in a new tree
    configdict["CombTaggers"] = {}
    configdict["CombTaggers"]["SS"] = {"InputDec"            : [ "lab0_SS_PionBDT_DEC"   , "lab0_SS_Pion_DEC"     , "lab0_SS_Proton_DEC"  ],
                                       "InputDecFormat"      : [ "S"                     , "S"                    , "S"                   ],
                                       "InputOmega"          : [ "lab0_SS_PionBDT_PROB"  , "lab0_SS_Pion_PROB"    , "lab0_SS_Proton_PROB" ],
                                       "InputOmegaFormat"    : [ "F"                     , "F"                    , "F"                   ],
                                       "OutputDec"           : "lab0_TAGDECISION_SS",
                                       "OutputDecFormat"     : "I",
                                       "OutputOmega"         : "lab0_TAGOMEGA_SS",
                                       "OutputOmegaFormat"   : "D"}

    # tagging efficiency and asymmetry
    configdict["tagEff_OS"] = 0.387
    configdict["tagEff_SS"] = 0.4772
    configdict["tagEff_OS_Lb"] = 0.001
    configdict["tagEff_SS_Lb"] = 0.999
    configdict["tagEff_OS_Combo"] = 0.594
    configdict["tagEff_SS_Combo"] = 0.462
    configdict["tagEff_Lb2LcPi"] = [configdict["tagEff_OS_Lb"] - configdict["tagEff_OS_Lb"]*configdict["tagEff_SS_Lb"],
                                    configdict["tagEff_SS_Lb"] - configdict["tagEff_OS_Lb"]*configdict["tagEff_SS_Lb"],
                                    configdict["tagEff_OS_Lb"]*configdict["tagEff_SS_Lb"]]
    configdict["tagEff_Signal"]    = [configdict["tagEff_OS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_SS"] - configdict["tagEff_OS"]*configdict["tagEff_SS"],
                                      configdict["tagEff_OS"]*configdict["tagEff_SS"]]
    configdict["tagEff_Combo"]     = [configdict["tagEff_OS_Combo"] - configdict["tagEff_OS_Combo"]*configdict["tagEff_SS_Combo"],
                                      configdict["tagEff_SS_Combo"] - configdict["tagEff_OS_Combo"]*configdict["tagEff_SS_Combo"],
                                      configdict["tagEff_OS_Combo"]*configdict["tagEff_SS_Combo"]]

    configdict["TagEff"] = {}
    configdict["TagEff"]["Signal"]    = configdict["tagEff_Signal"]
    configdict["TagEff"]["Bd2DK"]     = configdict["tagEff_Signal"]
    configdict["TagEff"]["Bs2DsPi"]   = configdict["tagEff_Signal"]
    configdict["TagEff"]["Lb2LcPi"]   = configdict["tagEff_Lb2LcPi"]
    configdict["TagEff"]["Combo"]     = configdict["tagEff_Combo"]
    configdict["TagEff"]["ComboFull"] = [ [1.0, 0.0, 0.0],
                                          [0.0, 1.0, 0.0],   
                                          [0.0, 0.0, 1.0],
                                          [0.0, 0.0, 0.0] ]
    configdict["TagEff"]["Bd2DRho"]   = configdict["tagEff_Signal"]
    configdict["TagEff"]["Bd2DstPi"]  = configdict["tagEff_Signal"]
                            

    configdict["ATagEff"] = {}
    configdict["ATagEff"]["Signal"]   = [0.0, 0.0, 0.0]
    configdict["ATagEff"]["Bd2DK"]    = [0.0, 0.0, 0.0]
    configdict["ATagEff"]["Bs2DsPi"]  = [0.0, 0.0, 0.0]
    configdict["ATagEff"]["Lb2LcPi"]  = [0.0, 0.0, 0.0]
    configdict["ATagEff"]["Combo"]    = [0.0, 0.0, 0.0]
    configdict["ATagEff"]["Bd2DRho"]  = [0.0, 0.0, 0.0]
    configdict["ATagEff"]["Bd2DstPi"] = [0.0, 0.0, 0.0]

    # k factor (not implemented at all for Bd->DPi...)
    configdict["UseKFactor"] = False

    # production and detection asymmetries
    configdict["AProd"] = {}
    configdict["AProd"]["Signal"]   = 0.00943518
    configdict["AProd"]["Bd2DK"]    = 0.00943518
    configdict["AProd"]["Bs2DsPi"]  = -0.0175698
    configdict["AProd"]["Lb2LcPi"]  = 0.0301775
    configdict["AProd"]["Combo"]    = -0.01
    configdict["AProd"]["Bd2DRho"]  = 0.0
    configdict["AProd"]["Bd2DstPi"] = 0.0
                           

    configdict["ADet"] = {}
    configdict["ADet"]["Signal"]   = 0.00502173
    configdict["ADet"]["Bd2DK"]    = 0.0100174
    configdict["ADet"]["Bs2DsPi"]  = 0.00608738
    configdict["ADet"]["Lb2LcPi"]  = 0.00515764
    configdict["ADet"]["Combo"]    = 0.00987629
    configdict["ADet"]["Bd2DRho"] = 0.0
    configdict["ADet"]["Bd2DstPi"] = 0.0

    # decay rate and CP parameters (see https://svnweb.cern.ch/trac/lhcb/browser/DBASE/tags/Gen/DecFiles/v27r42/dkfiles/Bd_D-pi+,Kpipi=CPVDDalitz,DecProdCut.dec)
    ModqOverp_d     =  1          
    ArgqOverp_d     =  -0.746     
    ModpOverq_d     =  1          
    ArgpOverq_d     =  0.746      
    ModAf_d         =  0.0849     
    ArgAf_d         =  0.002278   
    ModAbarf_d      =  0.00137    
    ArgAbarf_d      =  -1.128958  
    ModAfbar_d      =  0.00137    
    ArgAfbar_d      =  1.3145     
    ModAbarfbar_d   =  0.0849     
    ArgAbarfbar_d   =  0.002278   

    StrongPhase_s   = 4. / 180. * pi
    WeakPhase       = 116. / 180. * pi
    
    configdict["DecayRate"] = {}
    configdict["DecayRate"]["Gammad"]          = 0.656
    configdict["DecayRate"]["DeltaGammad"]     = 0.00267 #-> arXiv:1007.5135 (SM only, no new physics)
    configdict["DecayRate"]["DeltaMd"]         = 0.510
    configdict["DecayRate"]["Gammas"]          = 0.661
    configdict["DecayRate"]["DeltaGammas"]     = -0.105
    configdict["DecayRate"]["DeltaMs"]         = 17.768
    configdict["DecayRate"]["GammaLb"]         = 0.676
    configdict["DecayRate"]["GammaCombo"]      = [ 0.913,  1.451,  1.371,  0.745] #
    configdict["DecayRate"]["DeltaGammaCombo"] = [ 0.845,  1.266,  1.282,  0.753] # Combo: one value for each tagging cat (OS, SS OS+SS, UN)
    configdict["DecayRate"]["D_Combo"]         = [-0.908, -0.775, -0.913, -0.938] #
    configdict["DecayRate"]["ArgLf_d"]         = ArgqOverp_d + ArgAbarf_d - ArgAf_d
    configdict["DecayRate"]["ArgLbarfbar_d"]   = ArgpOverq_d + ArgAfbar_d - ArgAbarfbar_d
    configdict["DecayRate"]["ModLf_d"]         = ModAbarf_d/ModAf_d
    configdict["DecayRate"]["ArgLf_s"]         = StrongPhase_s - WeakPhase  
    configdict["DecayRate"]["ArgLbarfbar_s"]   = StrongPhase_s + WeakPhase
    configdict["DecayRate"]["ModLf_s"]         = 0.51                            

    configdict['UseAvgDelta'] = False

    # time acceptance configuration (spline)
    configdict["AcceptanceFunction"] = 'Spline'
    configdict["AcceptanceKnots"] = [0.5, 1.0, 1.5, 2.0, 3.0, 12.0]
    configdict["AcceptanceValues"] = [0.4453873694523979, 0.6869245867352556, 0.8719680916278891, 1.1614426699209424, 1.2341250036543179, 1.2852701638596233]
    configdict["NBinsAcceptance"] = 0

    # time resolution model configuration
    configdict["DecayTimeResolutionPEDTE"] = 'GaussianWithPEDTE'
    configdict["DecayTimeResolutionMeanModel"] = [ [2.21465e-02, 3.72057e-02, 6.37859e-02],
                                                   [3.62689e-01, 5.65100e-01] ]
    configdict["DecayTimeResolutionQuasiPerfect"] = [ [0.00005], []]
    
    configdict["DecayTimeResolutionBias"] = 0.0
    configdict["DecayTimeResolutionScaleFactor"] = 1.37

    configdict["NBinsProperTimeErr"] = 100
    
    # parameterize time resolution x acceptance integral (speed up generation with per-event time error)
    configdict["ParameteriseIntegral"] = True
    
    # children prefixes used in MCID, MCTRUEID, BKGCAT cuts   
    # order of particles: KPiPi 
    configdict["DsChildrenPrefix"] = {"Child1":"lab3","Child2":"lab4","Child3":"lab5"}

    # Bs signal shapes                                                                   
    configdict["BsSignalShape"] = {}
    configdict["BsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["BsSignalShape"]["mean"]    = {"All":5279.58} #From PDG 2014
    configdict["BsSignalShape"]["sigma1"]  = {"2012": {"KPiPi":1.0717e+01}, "Fixed":True}
    configdict["BsSignalShape"]["sigma2"]  = {"2012": {"KPiPi":1.6005e+01}, "Fixed":True}
    configdict["BsSignalShape"]["alpha1"]  = {"2012": {"KPiPi":2.2118e+00}, "Fixed":True}
    configdict["BsSignalShape"]["alpha2"]  = {"2012": {"KPiPi":-2.4185e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n1"]      = {"2012": {"KPiPi":1.0019e+00}, "Fixed":True}
    configdict["BsSignalShape"]["n2"]      = {"2012": {"KPiPi":3.1469e+00}, "Fixed":True}
    configdict["BsSignalShape"]["frac"]    = {"2012": {"KPiPi":6.1755e-01}, "Fixed":True}
    configdict["BsSignalShape"]["scaleSigma"] = { "2012": {"frac1": 1.0, "frac2":1.0}}

    #Ds signal shapes                                                                                                
    configdict["DsSignalShape"] = {}
    configdict["DsSignalShape"]["type"]    = "DoubleCrystalBall"
    configdict["DsSignalShape"]["mean"]    = {"All":1869.61} #From PDG 2014
    configdict["DsSignalShape"]["sigma1"]  = {"2012": {"KPiPi":5.3468e+00}, "Fixed":True}
    configdict["DsSignalShape"]["sigma2"]  = {"2012": {"KPiPi":5.1848e+00}, "Fixed":True}
    configdict["DsSignalShape"]["alpha1"]  = {"2012": {"KPiPi":1.2252e+00}, "Fixed":True}
    configdict["DsSignalShape"]["alpha2"]  = {"2012": {"KPiPi":-1.1167e+00}, "Fixed":True}
    configdict["DsSignalShape"]["n1"]      = {"2012": {"KPiPi":4.6625e+00}, "Fixed":True}
    configdict["DsSignalShape"]["n2"]      = {"2012": {"KPiPi":6.9989e+01}, "Fixed":True}
    configdict["DsSignalShape"]["frac"]    = {"2012": {"KPiPi":4.7565e-01}, "Fixed":True}
    configdict["DsSignalShape"]["scaleSigma"] = { "2012": {"frac1": 1.0, "frac2":1.0}}
 
    # combinatorial background                                                                              
    configdict["BsCombinatorialShape"] = {}
    configdict["BsCombinatorialShape"]["type"] = "Exponential"
    configdict["BsCombinatorialShape"]["cB"]   = {"2012":{"KPiPi":-9.8158e-04}, "Fixed":True}

    configdict["DsCombinatorialShape"] = {}
    configdict["DsCombinatorialShape"]["type"]  = "ExponentialPlusSignal"
    configdict["DsCombinatorialShape"]["cD"]         = {"2012": {"KPiPi":-1.0743e-03}, "Fixed":True}
    configdict["DsCombinatorialShape"]["fracCombD"]   = {"2012": {"KPiPi":1.0}, "Fixed":{"KPiPi":True}}

    
    #expected yields
    size = 0.1
    configdict["Yields"] = {}
    configdict["Yields"]["Bd2DK"]              = {"2012": {"KPiPi":1825*(490000.0/109420.0)*size}, "Fixed":False}
    configdict["Yields"]["Bs2DsPi"]            = {"2012": {"KPiPi":1294*(490000.0/109420.0)*size}, "Fixed":False}
    configdict["Yields"]["Bd2DRho"]            = {"2012": {"KPiPi":54240*(490000.0/109420.0)*size}, "Fixed":False}
    configdict["Yields"]["Bd2DstPi"]           = {"2012": {"KPiPi":24395*(490000.0/109420.0)*size}, "Fixed":False}
    configdict["Yields"]["Lb2LcPi"]            = {"2012": {"KPiPi":213*(490000.0/109420.0)*size}, "Fixed":False}
    configdict["Yields"]["Combo"]              = {"2012": {"KPiPi":23413*(490000.0/109420.0)*size},  "Fixed":False}
    configdict["Yields"]["Signal"]             = {"2012": {"KPiPi":490000*size} , "Fixed":False}

    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#            
    ###                                                               MDfit plotting settings                                                                                 
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------# 
    
    configdict["PlotSettings"] = {}
    configdict["PlotSettings"]["components"] = { "EPDF": ["Sig", "CombBkg", "Lb2LcPi", "Bd2DK", "Bs2DsPi", "Bd2DRho", "Bd2DstPi"],
                                                 "PDF":  ["Sig", "CombBkg", "Lb2LcPi", "Bd2DK", "Bs2DsPi", "Bd2DRho", "Bd2DstPi"],
                                                 "Legend": ["Sig", "CombBkg", "Lb2LcPi", "Bd2DK", "Bs2DsPi", "Bd2DRho", "Bd2DstPi"]}
    configdict["PlotSettings"]["colors"] = { "PDF": [kRed-7, kMagenta-2, kGreen-3, kYellow-9, kBlue-6, kRed, kBlue-10],
                                             "Legend": [kRed-7, kMagenta-2, kGreen-3, kYellow-9, kBlue-6, kRed, kBlue-10]}

    configdict["LegendSettings"] = {}
    configdict["LegendSettings"]["BeautyMass"] = {"Position":[0.53, 0.45, 0.90, 0.91], "TextSize": 0.05, "LHCbText":[0.35,0.9]}
    configdict["LegendSettings"]["CharmMass"]  = {"Position":[0.20, 0.69, 0.93, 0.93], "TextSize": 0.05, "LHCbText":[0.8,0.66],
                                                  "ScaleYSize":1.5, "SetLegendColumns":2, "LHCbTextSize":0.075 }
    
    configdict["ControlPlots"] = {}
    configdict["ControlPlots"]["Directory"] = "/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Templates/NoSelection_test"
    configdict["ControlPlots"]["Extension"] = "eps"

    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                                                   Workspaces                                                                    
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#

    #Toy generation and fitting
    configdict["Toys"] = {}
    configdict["Toys"]["fileName"]                         = "/afs/cern.ch/work/v/vibattis/public/B2DX/Bd2DPi/Workspace/NoSelection/work_dpi.root"
    configdict["Toys"]["fileNameTerr"]                     = "../data/workspace/MDFitter/template_Data_Terr_Bs2DsK_BDTGA.root"
    configdict["Toys"]["fileNameMistag"]                   = "../data/workspace/MDFitter/template_Data_Mistag_BsDsPi.root"
    configdict["Toys"]["fileNameMistagBDPi"]               = "../data/workspace/MDFitter/template_Data_Mistag_BDPi.root"
    configdict["Toys"]["fileNameMistagComb"]               = "../data/workspace/MDFitter/template_Data_Mistag_CombBkg.root"
    configdict["Toys"]["fileNameNoMistag"]                 = "../data/workspace/MDFitter/NoMistag.root"
    configdict["Toys"]["Workspace"]                        = "workspace"
    configdict["Toys"]["TerrTempName"]                     = "TimeErrorPdf_Bs2DsK"
    configdict["Toys"]["MistagTempName"]                   = ["sigMistagPdf_1", "sigMistagPdf_2", "sigMistagPdf_3"]


    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    ###                                               Constant parameters in the time fit                                                                 ###
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------#

    
    configdict["constParams"] = []
    configdict["constParams"].append('Gammad')
    configdict["constParams"].append('C')
    configdict["constParams"].append('Cbar')
    configdict["constParams"].append('D')
    configdict["constParams"].append('Dbar')
    #configdict["constParams"].append('S')
    #configdict["constParams"].append('Sbar')
    configdict["constParams"].append('deltaGammad')
    configdict["constParams"].append('deltaMd')
    configdict["constParams"].append('tagEffSig_OS')
    configdict["constParams"].append('tagEffSig_SS')
    configdict["constParams"].append('tagEffSig_OS+SS')
    configdict["constParams"].append('aprod')
    configdict["constParams"].append('adet')
    configdict["constParams"].append('aTagEff_OS')
    configdict["constParams"].append('aTagEff_SS')
    configdict["constParams"].append('aTagEff_OS+SS')
    configdict["constParams"].append('p0_B_OS')
    configdict["constParams"].append('p0_B_SS')
    configdict["constParams"].append('p0_B_OS+SS')
    configdict["constParams"].append('p1_B_OS')
    configdict["constParams"].append('p1_B_SS')
    configdict["constParams"].append('p1_B_OS+SS')
    configdict["constParams"].append('p0_Bbar_OS')
    configdict["constParams"].append('p0_Bbar_SS')
    configdict["constParams"].append('p0_Bbar_OS+SS')
    configdict["constParams"].append('p1_Bbar_OS')
    configdict["constParams"].append('p1_Bbar_SS')
    configdict["constParams"].append('p1_Bbar_OS+SS')
    configdict["constParams"].append('.*_scalefactor')
                                    
    return configdict
