def getconfig() :

    configdict = {}

    ############################################################
    #List of observables for all the PDFs.
    #The content of this dictionary determines the observables
    #to generate for and how may taggers are present.
    ############################################################

    configdict["Observables"] = {}
    configdict["Observables"] = {"BeautyMass":    {"Type"  : "RooRealVar",
                                                   "Title" : "B mass (MeV/c^2)",
                                                   "Range" : [5090, 6000]},
                                 "BeautyTime":    {"Type" : "RooRealVar",
                                                   "Title" : "B decay time (ps)",
                                                   "Range" : [0.4, 15.0]},
                                 #"BeautyTimeErr": {"Type" : "RooRealVar",
                                 #                  "Title" : "B decay time error (ps)",
                                 #                  "Range" : [0.01, 0.1]},
                                 "BacCharge":     {"Type"  : "RooCategory",
                                                   "Title" : "Bachelor charge",
                                                   "Categories": { "h+" : +1,
                                                                   "h-" : -1}},
                                 "MistagOS":      {"Type" : "RooRealVar",
                                                   "Title" : "#eta_{OS}",
                                                   "Range" : [0.0,0.5]},
                                 "MistagSS":      {"Type" : "RooRealVar",
                                                   "Title" : "#eta_{SS}",
                                                   "Range" : [0.0,0.5]},
                                 "TrueID":        {"Type" : "RooRealVar",
                                                   "Title" : "True component ID",
                                                   "Range" : [0.0,1500.0]},
                                 "TagDecOS":      {"Type"  : "RooCategory",
                                                   "Title" : "q_{t}^{OS}",
                                                   "Categories": { "B+"       : +1,
                                                                   "Untagged" : 0,
                                                                   "B-"       : -1}},
                                 "TagDecSS":      {"Type"  : "RooCategory",
                                                   "Title" : "q_{t}^{SS}",
                                                   "Categories": { "B+"       : +1,
                                                                   "Untagged" : 0,
                                                                   "B-"       : -1}}
                                 }

    ############################################################
    #List of mass hypotheses for bachelor
    #The content of this dictionary determines how many
    #bachelor PID bins the final dataset is splitted into
    ############################################################

    configdict["Hypothesys"] = ["Bd2DPi", "Bd2DK"]

    ############################################################
    #Signal decay and Charm decay mode
    ############################################################

    configdict["Decay"] = "Bd2DPi"
    configdict["CharmModes"] = ["KPiPi"]
    configdict["Years"] = ["2011","2012"]
    configdict["MergedYears"] = True

    ############################################################
    #Luminosity for splitting yields and other parameters
    ############################################################

    configdict["IntegratedLuminosity"] = {"2011": {"Down":  0.50, "Up": 0.50}, "2012":{"Down": 1.000, "Up": 1.000}}
    lum2011 =  configdict["IntegratedLuminosity"]["2011"]["Up"] + configdict["IntegratedLuminosity"]["2011"]["Down"]
    lum2012 =  configdict["IntegratedLuminosity"]["2012"]["Up"] + configdict["IntegratedLuminosity"]["2012"]["Down"]
    fracRun1 = lum2011/(lum2011 + lum2012)
    DRho_to_DKst_KHypo = 8.5000e-01
    eff_Bd2DK_DK = 6.29009e-01
    eff_Bd2DPi_DPi = 9.78927e-01

    ############################################################
    #List of components with yields to generate.
    #The content of this dictionary determines, for each
    #PID bin, how many PDF components are generated.
    #If there is only signal, a TTree ready for sFit is
    #generated directly, without need for doing a (useless)
    #mass fit.
    ############################################################

    configdict["Components"] = {}
    configdict["Components"] = {"Signal"        : {"Bd2DPi": {"2011" : {"KPiPi": [5.2848e+05*fracRun1] },
                                                              "2012" : {"KPiPi": [5.2848e+05*(1-fracRun1)] }},
                                                   "Bd2DK" : {"2011" : {"KPiPi": [((1-eff_Bd2DPi_DPi)/eff_Bd2DPi_DPi)*5.2848e+05*fracRun1] },
                                                              "2012" : {"KPiPi": [((1-eff_Bd2DPi_DPi)/eff_Bd2DPi_DPi)*5.2848e+05*(1-fracRun1)] }}},
                                "Bd2DK"         : {"Bd2DPi": {"2011" : {"KPiPi": [((1-eff_Bd2DK_DK)/eff_Bd2DK_DK)*3.0795e+04*fracRun1] },
                                                              "2012" : {"KPiPi": [((1-eff_Bd2DK_DK)/eff_Bd2DK_DK)*3.0795e+04*(1-fracRun1)] }},
                                                   "Bd2DK" : {"2011" : {"KPiPi": [3.0795e+04*fracRun1] },
                                                              "2012" : {"KPiPi": [3.0795e+04*(1-fracRun1)] }}},
                                "Bd2DRho"       : {"Bd2DPi": {"2011" : {"KPiPi": [7.5224e+04*fracRun1] },
                                                              "2012" : {"KPiPi": [7.5224e+04*(1-fracRun1)] }},
                                                   "Bd2DK" : {"2011" : {"KPiPi": [DRho_to_DKst_KHypo*3.7873e+03*fracRun1] },
                                                              "2012" : {"KPiPi": [DRho_to_DKst_KHypo*3.7873e+03*(1-fracRun1)] }}},
                                "Bd2DstPi"      : {"Bd2DPi": {"2011" : {"KPiPi": [6.1404e+04*fracRun1] },
                                                              "2012" : {"KPiPi": [6.1404e+04*(1-fracRun1)] }},
                                                   "Bd2DK" : {"2011" : {"KPiPi": [0] },
                                                              "2012" : {"KPiPi": [0] }}},
                                "Bd2DKst"       : {"Bd2DPi": {"2011" : {"KPiPi": [0] },
                                                              "2012" : {"KPiPi": [0] }},
                                                   "Bd2DK" : {"2011" : {"KPiPi": [3.7873e+03*fracRun1] },
                                                              "2012" : {"KPiPi": [3.7873e+03*(1-fracRun1)] }}},
                                "Combinatorial" :  {"Bd2DPi": {"2011" : {"KPiPi": [4.8362e+04*fracRun1] },
                                                               "2012" : {"KPiPi": [4.8362e+04*(1-fracRun1)] }},
                                                    "Bd2DK" : {"2011" : {"KPiPi": [2.1674e+04*fracRun1] },
                                                               "2012" : {"KPiPi": [2.1674e+04*(1-fracRun1)] }}}
                                }

    ############################################################
    #"Code" to identify the True ID for each component
    ############################################################

    configdict["TrueID"] = {}
    configdict["TrueID"] = {"Signal"          : 100,
                            "Bd2DK"           : 200,
                            "Bd2DRho"         : 300,
                            "Bd2DstPi"        : 400,
                            "Bd2DKst"         : 500,
                            "Combinatorial"   : 600}

    ############################################################
    #List of PDFs for "time-independent" observables
    #Dictionary structure: observable->component->bachelor hypo->year->D mode
    ############################################################

    Pipeak = 5.27849e+03
    Kpeak = 5.27907e+03

    configdict["PDFList"] = {}
    configdict["PDFList"]["BeautyMass"] = {}

    #Signal
    configdict["PDFList"]["BeautyMass"]["Signal"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DPi"]["2011"]["KPiPi"] = {"Type"       : "Ipatia",
                                                                                "mean"       : [Pipeak],
                                                                                "sigma"      : [1.96756e+01],
                                                                                "zeta"       : [0.0],
                                                                                "fb"         : [0.0],
                                                                                "l"          : [-3.14504e+00],
                                                                                "a1"         : [1.56363e+00], #left
                                                                                "a2"         : [1.77887e+00], #right
                                                                                "n1"         : [4.04491e+00], #left
                                                                                "n2"         : [6.62043e+00]} #right
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DK"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DK"]["2011"]["KPiPi"] = {"Type"       : "Ipatia",
                                                                               "mean"       : [5.32740e+03],
                                                                               "sigma"      : [2.42675e+01],
                                                                               "zeta"       : [0.0],
                                                                               "fb"         : [0.0],
                                                                               "l"          : [-5.46421e+00],
                                                                               "a1"         : [3.04325e+00],
                                                                               "a2"         : [6.62837e-01],
                                                                               "n1"         : [6.79609e-02],
                                                                               "n2"         : [2.09572e+00]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DPi"]["2012"] = configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DPi"]["2011"]
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DK"]["2012"] = configdict["PDFList"]["BeautyMass"]["Signal"]["Bd2DK"]["2011"]

    #Bd2DK
    configdict["PDFList"]["BeautyMass"]["Bd2DK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DPi"]["2011"]["KPiPi"] = {"Type"       : "Ipatia",
                                                                               "mean"       : [5.23938e+03],
                                                                               "sigma"      : [2.59213e+01],
                                                                               "zeta"       : [0.0],
                                                                               "fb"         : [0.0],
                                                                               "l"          : [-3.98519e+01],
                                                                               "a1"         : [9.68988e-01],
                                                                               "a2"         : [1.23156e+00],
                                                                               "n1"         : [3.49691e+00],
                                                                               "n2"         : [1.00524e+01]}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DK"]["2011"]["KPiPi"] = {"Type"       : "Ipatia",
                                                                              "mean"       : [Kpeak],
                                                                              "sigma"      : [1.74271e+01],
                                                                              "zeta"       : [0.0],
                                                                              "fb"         : [0.0],
                                                                              "l"          : [-3.22645e+00],
                                                                              "a1"         : [2.60724e+00],
                                                                              "a2"         : [1.0e+09],
                                                                              "n1"         : [1.00877e+00],
                                                                              "n2"         : [0.0]}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DPi"]["2012"] = configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DPi"]["2011"]
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DK"]["2012"] = configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bd2DK"]["2011"]

    #Bd2DRho
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DPi"]["2011"]["KPiPi"] = {"Type"      : "JohnsonSU",
                                                                                 "mean"      : [4.71618e+03],
                                                                                 "sigma"     : [9.01304e+02],
                                                                                 "nu"        : [-2.01671e+00],
                                                                                 "tau"       : [1.29155e+00]}
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DK"]["2011"]["KPiPi"] = {"Type"       : "DoubleGaussian",
                                                                                "mean"       : [5.14019e+03],
                                                                                "sigma1"     : [9.00002e+01],
                                                                                "sigma2"     : [1.55484e+02],
                                                                                "frac"       : [8.30742e-01]}
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DPi"]["2012"] =  configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DPi"]["2011"]
    configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DK"]["2012"] = configdict["PDFList"]["BeautyMass"]["Bd2DRho"]["Bd2DK"]["2011"]

    #Bd2DstPi
    configdict["PDFList"]["BeautyMass"]["Bd2DstPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DPi"]["2011"]["KPiPi"] = {"Type"        : "CrystalBallPlusGaussian",
                                                                                  "mean"        : [5.10033e+03],
                                                                                  "alpha"       : [-1.63404e+00],
                                                                                  "n"           : [4.65946e+00],
                                                                                  "sigmaCB"     : [4.15131e+01],
                                                                                  "sigmaG"      : [1.79617e+01],
                                                                                  "fracG"       : [1.32304e-01]}
    configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DK"]["2011"]["KPiPi"] = {"Type"        : "None"}
    configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DPi"]["2012"] = configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DPi"]["2011"]
    configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DK"]["2012"] = configdict["PDFList"]["BeautyMass"]["Bd2DstPi"]["Bd2DK"]["2011"]

    #Bd2DKst
    configdict["PDFList"]["BeautyMass"]["Bd2DKst"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DPi"]["2011"]["KPiPi"] = {"Type"        : "None"}
    configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DK"]["2011"]["KPiPi"] = {"Type"       : "Gaussian",
                                                                                "mean"       : [5.08528e+03],
                                                                                "sigma"      : [3.76140e+01]}
    configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DPi"]["2012"] = configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DPi"]["2011"]
    configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DK"]["2012"] = configdict["PDFList"]["BeautyMass"]["Bd2DKst"]["Bd2DK"]["2011"]

    #Combinatorial
    configdict["PDFList"]["BeautyMass"]["Combinatorial"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DPi"]["2011"]["KPiPi"] = {"Type"       : "ExponentialPlusConstant",
                                                                                       "cB"           : [-5.59102e-03],
                                                                                       "fracExpo"     : [8.77658e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DK"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DK"]["2011"]["KPiPi"] = {"Type"       : "ExponentialPlusConstant",
                                                                                      "cB"           : [-4.15525e-03],
                                                                                      "fracExpo"     : [9.38575e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DPi"]["2012"] = configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DPi"]["2011"]
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DK"]["2012"] = configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bd2DK"]["2011"]

    ############################################################
    #Tagging calibration and mistag PDF. If "MistagPDF" : None,
    #then a average mistag is used
    ############################################################

    configdict["Taggers"] = {}
    for comp in configdict["Components"].iterkeys():
        configdict["Taggers"][comp] = {}
        configdict["Taggers"][comp] = {"OS" : #From Bu, stat and syst combined
                                       {"Calibration":
                                        {"p0"       : [0.3737056],
                                         "p1"       : [1.028621],
                                         "deltap0"  : [0.011819],
                                         "deltap1"  : [0.043134],
                                         "avgeta"   : [0.347742], #<eta> on spline-corrected Bu->D0Pi
                                         "tageff"   : [0.371], # the correct value here is 0.371
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"       : "FromWorkspace",
                                         "File"       : "root://eoslhcb.cern.ch//eos/lhcb/wg/b2oc/TD_DPi_3fb/MistagTemplates/templates_mistag.root",
                                         "Workspace"  : "workspace",
                                         "Name"       : "sigMistagPdf_2"
                                         }
                                        },
                                       "SS": #From JpsiKst, stat and syst combined
                                       {"Calibration":
                                        {"p0"       : [0.4424049],
                                         "p1"       : [0.81302],
                                         "deltap0"  : [0.00062332],
                                         "deltap1"  : [0.0066248],
                                         "avgeta"   : [0.435], #<eta> on Bd->J/psiK*
                                         "tageff"   : [0.816], # the correct value here is 0.816
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"       : "FromWorkspace",
                                         "File"       : "root://eoslhcb.cern.ch//eos/lhcb/wg/b2oc/TD_DPi_3fb/MistagTemplates/templates_mistag.root",
                                         "Workspace"  : "workspace",
                                         "Name"       : "sigMistagPdf_1"
                                         }
                                        }
                                       }

    ############################################################
    #Time resolution and acceptance (there is a single dict because
    #they are strongly connected in the way they are built).
    #If "TimeErrorPDF" : None, then an average resolution model
    #is used.
    ############################################################

    configdict["ResolutionAcceptance"] = {}
    for comp in configdict["Components"].iterkeys():
        configdict["ResolutionAcceptance"][comp] = {}
        configdict["ResolutionAcceptance"][comp] = {"TimeErrorPDF": None,
                                                    "Acceptance":  #From ANA note v2
                                                    {"Type": "Spline",
                                                     "KnotPositions" : [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
                                                     "KnotCoefficients" : [ 0.3889, 0.5754, 0.8515, 1.0649, 1.2373, 1.4149]},
                                                    "Resolution": #From ANA note v2
                                                    {"Type": "AverageModel",
                                                     "Parameters": { 'sigmas': [ 0.05491 ], 'fractions': [] },
                                                     "Bias": [0.0],
                                                     "ScaleFactor": [1.0]}
                                                    }

    ############################################################
    #Production and detection asymmetries
    ############################################################

    configdict["ProductionAsymmetry"] = {}
    configdict["DetectionAsymmetry"] = {}
    configdict["ProductionAsymmetry"]["Signal"] = {}
    configdict["DetectionAsymmetry"]["Signal"] = {}
    configdict["ProductionAsymmetry"]["Signal"] = [-0.0124] #from ANA note v2
    configdict["DetectionAsymmetry"]["Signal"] = [0.0086] #from arXiv:1408.0275v2 (OPPOSITE SIGN!!!)
    for comp in configdict["Components"].iterkeys():
        if comp != "Signal":
            #We don't really care about background
            configdict["ProductionAsymmetry"][comp] = {}
            configdict["DetectionAsymmetry"][comp] = {}
            configdict["ProductionAsymmetry"][comp] = [0.0]
            configdict["DetectionAsymmetry"][comp] = [0.0]

    ############################################################
    #Time PDF parameters
    ############################################################

    configdict["ACP"] = {}

    #Parameters from https://svnweb.cern.ch/trac/lhcb/browser/DBASE/tags/Gen/DecFiles/v27r42/dkfiles/Bd_D-pi+,Kpipi=CPVDDalitz,DecProdCut.dec)
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

    #Signal (use more convenient interface with ArgLf_d, ArgLbarfbar_d and ModLf_d)
    configdict["ACP"]["Signal"] = { "Gamma"                : [1.0 / 1.520], #Inverse lifetime from HFAG (http://www.slac.stanford.edu/xorg/hfag/osc/summer_2016/)
                                    "DeltaGamma"           : [0.0],
                                    "DeltaM"               : [0.5050], #semileptonic measurement HFAG (http://www.slac.stanford.edu/xorg/hfag/osc/summer_2016/)
                                    #"ArgLf"                : [ArgqOverp_d + ArgAbarf_d - ArgAf_d],
                                    #"ArgLbarfbar"          : [ArgpOverq_d + ArgAfbar_d - ArgAbarfbar_d],
                                    #"ModLf"                : [ModAbarf_d/ModAf_d],
                                    "C"                    : [1.0], #we neglect r^2 terms
                                    "S"                    : [-0.031], #from decfile
                                    "Sbar"                 : [0.029], #from decfile
                                    "D"                    : [0], #from DeltaGamma=0
                                    "Dbar"                 : [0], #from DeltaGamma=0
                                    "ParameteriseIntegral" : True,
                                    "NBinsAcceptance"      : 0} #keep at zero if using spline acceptance!

    for comp in configdict["Components"].iterkeys():
        if comp != "Signal":
            #Use other interface with C, S, Sbar, D, Dbar
            #We build trivial PDFs since we don't care about background shapes in time if we use sWeights
            configdict["ACP"][comp] = { "Gamma"                 : [1.0],
                                        "DeltaGamma"            : [0.0],
                                        "DeltaM"                : [0.0],
                                        "C"                     : [0.0],
                                        "S"                     : [0.0],
                                        "Sbar"                  : [0.0],
                                        "D"                     : [0.0],
                                        "Dbar"                  : [0.0],
                                        "ParameteriseIntegral"  : True,
                                        "NBinsAcceptance"       : 0}

    return configdict
