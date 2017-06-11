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
                                                   "Range" : [5300, 5800]},
                                 "CharmMass":     {"Type" : "RooRealVar",
                                                   "Title" : "D mass (MeV/c^2)",
                                                   "Range" : [1930, 2015]},
                                 "BacPIDK":       {"Type"  : "RooRealVar",
                                                   "Title": "log(fabs(PIDK))",
                                                   "Range": [1.61,    5.0]}, 
                                 "BeautyTime":    {"Type" : "RooRealVar",
                                                   "Title" : "B decay time (ps)",
                                                   "Range" : [0.4, 15.0]},
                                 "BeautyTimeErr": {"Type" : "RooRealVar",
                                                   "Title" : "B decay time error (ps)",
                                                   "Range" : [0.01, 0.1]},
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
    
    configdict["Hypothesys"] = ["Bs2DsK"]

    ############################################################
    #Signal decay, Charm decay mode and year of data taking
    #Splitting per magnet polarity not implemented, at the moment
    ############################################################

    configdict["Decay"] = "Bs2DsK"
    configdict["CharmModes"] = ["NonRes","PhiPi","KstK","KPiPi","PiPiPi"]
    configdict["Years"] = ["2011","2012"]
    configdict["MergedYears"] = True
    

    ############################################################
    #For PIDK shapes we need also polarities
    ############################################################
    configdict["Polarity"] = ["Up","Down"]
    configdict["IntegratedLuminosity"] = {"2011": {"Down":  0.50, "Up": 0.50}, "2012":{"Down": 1.000, "Up": 1.000}}
    configdict["FractionsLuminosity"] = {"2011": (configdict["IntegratedLuminosity"]["2011"]["Up"]/(configdict["IntegratedLuminosity"]["2011"]["Up"] + configdict["IntegratedLuminosity"]["2011"]["Down"])),
                                         "2012": (configdict["IntegratedLuminosity"]["2012"]["Up"]/(configdict["IntegratedLuminosity"]["2012"]["Up"] + configdict["IntegratedLuminosity"]["2012"]["Down"]))}
    
    lum2011 =  configdict["IntegratedLuminosity"]["2011"]["Up"] + configdict["IntegratedLuminosity"]["2011"]["Down"] 
    lum2012 =  configdict["IntegratedLuminosity"]["2012"]["Up"] + configdict["IntegratedLuminosity"]["2012"]["Down"]
    fracRun1 = lum2011/(lum2011 + lum2012) 
    
    configdict["WorkspaceToRead"] = {"File":"/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                     "Workspace" : "workspace"}

    ############################################################ 
    #List of components with yields to generate.
    #The content of this dictionary determines, for each
    #PID bin and year, how many PDF components are generated.
    #If there is only signal, a TTree ready for sFit is
    #generated directly, without need for doing a (useless)
    #mass fit.
    ############################################################
    
    #configdict["Components"] = {}
    #configdict["Components"]["Signal"] = {}
    configdict["Components"] = {"Signal":        {"Bs2DsK": {"2011": {"NonRes": [931*fracRun1], "PhiPi":[1956*fracRun1], 
                                                                       "KstK"  : [1611*fracRun1], "KPiPi":[385*fracRun1],  "PiPiPi":[931*fracRun1] },
                                                              "2012": {"NonRes": [931*(1.0-fracRun1)], "PhiPi":[1956*(1.0-fracRun1)], 
                                                                       "KstK"  : [1611*(1.0-fracRun1)], "KPiPi":[385*(1.0-fracRun1)],  "PiPiPi":[931*(1.0-fracRun1)] }}},
                                "Combinatorial": {"Bs2DsK": {"2011": {"NonRes": [900*fracRun1],  "PhiPi":[801*fracRun1],  
                                                                       "KstK"  : [508*fracRun1],  "KPiPi":[909*fracRun1],  "PiPiPi":[2000*fracRun1] },
                                                              "2012": {"NonRes": [900*(1.0-fracRun1)],  "PhiPi":[801*(1.0-fracRun1)],  
                                                                       "KstK"  : [508*(1.0-fracRun1)],  "KPiPi":[909*(1.0-fracRun1)],  "PiPiPi":[2000*(1.0-fracRun1)] }}},

	                	"Bs2DsPi":       {"Bs2DsK": {"2011": {"NonRes": [392.9*fracRun1], "PhiPi":[827.0*fracRun1], 
                                                                      "KstK"  : [631.9*fracRun1], "KPiPi":[117*fracRun1], "PiPiPi":[443*fracRun1] },
                                                             "2012": {"NonRes": [392.9*(1.0-fracRun1)], "PhiPi":[827.0*(1.0-fracRun1)], 
                                                                      "KstK"  : [631.9*(1.0-fracRun1)], "KPiPi":[117*(1.0-fracRun1)], "PiPiPi":[443*(1.0-fracRun1)] }}},    
				"Bs2DsstPi":     {"Bs2DsK": {"2011": {"NonRes": [134.3*fracRun1], "PhiPi":[282.6*fracRun1], 
                                                                      "KstK"  : [216.0*fracRun1], "KPiPi":[40.0*fracRun1], "PiPiPi":[151.6*fracRun1] },
                                                             "2012": {"NonRes": [134.3*(1.0-fracRun1)], "PhiPi":[282.6*(1.0-fracRun1)], 
                                                                      "KstK"  : [216.0*(1.0-fracRun1)], "KPiPi":[40.0*(1.0-fracRun1)], "PiPiPi":[151*(1.0-fracRun1)] }}},   
				"Bs2DsRho":      {"Bs2DsK": {"2011": {"NonRes": [134.3*fracRun1], "PhiPi":[282.6*fracRun1], 
                                                                      "KstK"  : [216.0*fracRun1], "KPiPi":[40.0*fracRun1], "PiPiPi":[151*fracRun1] },
                                                             "2012": {"NonRes": [134.3*(1.0-fracRun1)], "PhiPi":[282.6*(1.0-fracRun1)], 
                                                                      "KstK"  : [216.0*(1.0-fracRun1)], "KPiPi":[40.0*(1.0-fracRun1)], "PiPiPi":[151*(1.0-fracRun1)] }}},     
                                
				"Bd2DPi":        {"Bs2DsK": {"2011": {"NonRes" : [50*fracRun1],    "PhiPi":[2.6*fracRun1],  
                                                                       "KstK"  : [38.6*fracRun1],  "KPiPi":[0.0*fracRun1],   "PiPiPi":[0.0*fracRun1] },
                                                              "2012": {"NonRes": [50*(1.0-fracRun1)],    "PhiPi":[2.6*(1.0-fracRun1)],  
                                                                       "KstK"  : [38.6*(1.0-fracRun1)],  "KPiPi":[0.0*(1.0-fracRun1)],   "PiPiPi":[0.0*(1.0-fracRun1)] }}},
                                "Bd2DK":        {"Bs2DsK": {"2011": {"NonRes"  : [83.1*fracRun1],  "PhiPi":[4.6*fracRun1],  
                                                                       "KstK"  : [65.6*fracRun1],  "KPiPi":[0.0*fracRun1],   "PiPiPi":[0.0*fracRun1] },
                                                              "2012": {"NonRes": [83.1*(1.0-fracRun1)],  "PhiPi":[4.6*(1.0-fracRun1)],  
                                                                       "KstK"  : [65.6*(1.0-fracRun1)],  "KPiPi":[0.0*(1.0-fracRun1)],   "PiPiPi":[0.0*(1.0-fracRun1)] }}},

				"Lb2LcPi":       {"Bs2DsK": {"2011": {"NonRes" : [27.1*fracRun1],  "PhiPi":[4.2*fracRun1],   
                                                                       "KstK"  : [8.0*fracRun1],   "KPiPi":[0.0*fracRun1],       "PiPiPi":[0.0*fracRun1] },
                                                             "2012": {"NonRes" : [27.1*(1.0-fracRun1)], "PhiPi":[4.2*(1.0-fracRun1)],   
                                                                      "KstK"   : [8.0*(1.0 - fracRun1)],    "KPiPi" : [0.0*(1.0-fracRun1)],   "PiPiPi":[0.0*(1.0-fracRun1)] }}}, 
                                "Lb2LcK":       {"Bs2DsK": {"2011": {"NonRes"  : [45.3*fracRun1],   "PhiPi":[7.4*fracRun1],   
                                                                     "KstK"    : [13.6*fracRun1],    "KPiPi":[0.0*fracRun1],   "PiPiPi":[0.0*fracRun1] },
                                                            "2012": {"NonRes"  : [45.3*(1.0-fracRun1)],   "PhiPi":[7.4*(1.0-fracRun1)],   
                                                                     "KstK"    : [13.6*(1.0 - fracRun1)], "KPiPi" : [0.0*(1.0-fracRun1)],   "PiPiPi":[0.0*(1.0-fracRun1)] }}},    
                                
     				"Lb2Dsp":       {"Bs2DsK": {"2011": {"NonRes": [26.7*fracRun1],  "PhiPi":[56.1*fracRun1],   
                                                                     "KstK"  : [42.9*fracRun1],   "KPiPi":[7.9*fracRun1],   "PiPiPi":[30.0*fracRun1] },
                                                            "2012": {"NonRes": [26.7*(1.0-fracRun1)],   "PhiPi":[56.1*(1.0-fracRun1)],   
                                                                     "KstK"  : [42.9*(1.0 - fracRun1)], "KPiPi" : [7.9*(1.0-fracRun1)],   "PiPiPi":[30.0*(1.0-fracRun1)] }}}, 
                                "Lb2Dsstp":       {"Bs2DsK": {"2011": {"NonRes": [8.9*fracRun1], "PhiPi":[19*fracRun1],   
                                                                       "KstK"  : [14.3*fracRun1], "KPiPi":[2.6*fracRun1],   "PiPiPi":[10.0*fracRun1] },
                                                              "2012": {"NonRes": [8.9*(1.0-fracRun1)], "PhiPi":[19*(1.0-fracRun1)],   
                                                                       "KstK"  : [14.3*(1.0 - fracRun1)],  "KPiPi" : [2.6*(1.0-fracRun1)],   "PiPiPi":[10.0*(1.0-fracRun1)] }}},    

                                "Bd2DsK":       {"Bs2DsK": {"2011": {"NonRes": [22*fracRun1],    "PhiPi":[57*fracRun1],    
                                                                     "KstK"  : [50*fracRun1],    "KPiPi":[18*fracRun1],    "PiPiPi":[32*fracRun1] },
                                                            "2012": {"NonRes": [22*(1.0-fracRun1)],    "PhiPi":[57*(1.0-fracRun1)],    
                                                                     "KstK"  : [50*(1.0-fracRun1)],    "KPiPi":[18*(1.0-fracRun1)],    "PiPiPi":[32*(1.0-fracRun1)] }}}}
                                

    ############################################################
    #"Code" to identify the True ID for each component
    ############################################################

    configdict["TrueID"] = {}
    configdict["TrueID"] = {"Signal"        : 100,
                            "Combinatorial" : 200,
	                    "Bs2DsPi"       : 300,
	                    "Bs2DsstPi"     : 400,
	                    "Bs2DsRho"      : 500, 
                            "Bd2DPi"        : 600,
		            "Bd2DK"         : 700, 
                            "Lb2LcPi"       : 800,
                            "Lb2LcK"        : 900, 
                            "Lb2Dsp"        :1000,
                            "Lb2Dsstp"      :1100,
                            "Bd2DsK"        :1200}

    ############################################################
    #List of PDFs for "time-independent" observables
    #Dictionary structure: observable->component->bachelor hypo->year->D mode
    ############################################################

    ############################################################
    #                      Signal                               
    ############################################################

    ############################################################
    configdict["PDFList"] = {}
    configdict["PDFList"]["BeautyMass"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"] = {} 
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5365.51], "sigma1":[1.4463e+01], "sigma2": [1.0932e+01], "alpha1": [-2.1830e+00],
                                                                                   "alpha2":[1.7323e+00], "n1":[2.7064e+00], "n2":[1.5260e+00], "frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5365.51], "sigma1":[1.6022e+01], "sigma2": [1.0656e+01], "alpha1": [-2.2974e+00],
                                                                                   "alpha2":[2.5001e+00], "n1":[3.5139e+00], "n2":[2.9885e-01],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[5365.51], "sigma1":[1.6527e+01], "sigma2": [1.0469e+01], "alpha1": [-2.3682e+00],
                                                                                  "alpha2":[2.6768e+00], "n1":[1.8813e+00], "n2":[1.1171e-01],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[5365.51], "sigma1":[1.5252e+01], "sigma2": [1.0961e+01], "alpha1": [-2.6083e+00],
                                                                                  "alpha2":[1.8731e+00], "n1":[1.6047e+00], "n2":[1.2051e+00],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5365.51], "sigma1":[1.6541e+01], "sigma2": [1.0652e+01], "alpha1": [-2.3757e+00],
                                                                                   "alpha2":[1.8091e+00], "n1":[3.2171e+00], "n2":[1.3755e+00],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5365.51], "sigma1":[1.4463e+01], "sigma2": [1.0932e+01], "alpha1": [-2.1830e+00],
                                                                                   "alpha2":[1.7323e+00], "n1":[2.7064e+00], "n2":[1.5260e+00],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[5365.51], "sigma1":[1.6022e+01], "sigma2": [1.0656e+01], "alpha1": [-2.2974e+00],
                                                                                 "alpha2":[2.5001e+00], "n1":[3.5139e+00], "n2":[2.9885e-01],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[5365.51], "sigma1":[1.6527e+01], "sigma2": [1.0469e+01], "alpha1": [-2.3682e+00],
                                                                                  "alpha2":[2.6768e+00], "n1":[1.8813e+00], "n2":[1.1171e-01],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[5365.51], "sigma1":[1.5252e+01], "sigma2": [1.0961e+01], "alpha1": [-2.6083e+00],
                                                                                  "alpha2":[1.8731e+00], "n1":[1.6047e+00], "n2":[1.2051e+00],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5365.51], "sigma1":[1.6541e+01], "sigma2": [1.0652e+01], "alpha1": [-2.3757e+00],
                                                                                   "alpha2":[1.8091e+00], "n1":[3.2171e+00], "n2":[1.3755e+00],"frac":[0.5]}
    
    ############################################################### 
    configdict["PDFList"]["CharmMass"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[1968.49], "sigma1":[4.7027e+00], "sigma2": [7.3516e+00], "alpha1": [-1.9272e+00],
                                                                                   "alpha2":[1.8145e+00], "n1":[2.3283e+00], "n2":[2.5187e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[1968.49], "sigma1":[4.5595e+00], "sigma2": [7.5857e+00], "alpha1": [-2.1355e+00],
                                                                                 "alpha2":[1.7106e+00], "n1":[1.6544e+00], "n2":[3.5765e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"] =  {"Type" : "DoubleCrystalBall",
                                                                                "mean":[1968.49], "sigma1":[4.7236e+00], "sigma2": [7.4875e+00], "alpha1": [-1.9435e+00],
                                                                                "alpha2":[1.7592e+00], "n1":[2.4362e+00], "n2":[3.9442e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[1968.49], "sigma1":[7.8797e+00], "sigma2": [6.4160e+00], "alpha1": [-1.3572e+00],
                                                                                 "alpha2":[1.6532e+00], "n1":[2.8660e+01], "n2":[1.8414e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[1968.49], "sigma1":[7.6187e+00], "sigma2": [8.4359e+00], "alpha1": [-1.0018e+00],
                                                                                  "alpha2":[8.6154e-01], "n1":[4.5603e+01], "n2":[5.0000e+01], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[1968.49], "sigma1":[4.7027e+00], "sigma2": [7.3516e+00], "alpha1": [-1.9272e+00],
                                                                                   "alpha2":[1.8145e+00], "n1":[2.3283e+00], "n2":[2.5187e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[1968.49], "sigma1":[4.5595e+00], "sigma2": [7.5857e+00], "alpha1": [-2.1355e+00],
                                                                                 "alpha2":[1.7106e+00], "n1":[1.6544e+00], "n2":[3.5765e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"] =  {"Type" : "DoubleCrystalBall",
                                                                                "mean":[1968.49], "sigma1":[4.7236e+00], "sigma2": [7.4875e+00], "alpha1": [-1.9435e+00],
                                                                                "alpha2":[1.7592e+00], "n1":[2.4362e+00], "n2":[3.9442e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[1968.49], "sigma1":[7.8797e+00], "sigma2": [6.4160e+00], "alpha1": [-1.3572e+00],
                                                                                 "alpha2":[1.6532e+00], "n1":[2.8660e+01], "n2":[1.8414e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[1968.49], "sigma1":[7.6187e+00], "sigma2": [8.4359e+00], "alpha1": [-1.0018e+00],
                                                                                  "alpha2":[8.6154e-01], "n1":[4.5603e+01], "n2":[5.0000e+01], "frac":[0.5]}
    ###############################################################
    configdict["PDFList"]["BacPIDK"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["NonRes"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",  
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_nonres_2011", "Down":"PIDKShape_Bs2DsK_down_nonres_2011"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_phipi_2011", "Down":"PIDKShape_Bs2DsK_down_phipi_2011"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["KstK"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_kstk_2011", "Down":"PIDKShape_Bs2DsK_down_kstk_2011"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_kpipi_2011", "Down":"PIDKShape_Bs2DsK_down_kpipi_2011"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_pipipi_2011", "Down":"PIDKShape_Bs2DsK_down_pipipi_2011"}}

    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["NonRes"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_nonres_2012", "Down":"PIDKShape_Bs2DsK_down_nonres_2012"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_phipi_2012", "Down":"PIDKShape_Bs2DsK_down_phipi_2012"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["KstK"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_kstk_2012", "Down":"PIDKShape_Bs2DsK_down_kstk_2012"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_kpipi_2012", "Down":"PIDKShape_Bs2DsK_down_kpipi_2012"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsK_up_pipipi_2012", "Down":"PIDKShape_Bs2DsK_down_pipipi_2012"}}

    ############################################################    
    #                      Combinatorial      
    ############################################################   

    ############################################################
    configdict["PDFList"]["BeautyMass"]["Combinatorial"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2011"]["NonRes"] = {"Type":"Exponential", "cB":[-4.8467e-03]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2011"]["PhiPi"]  = {"Type":"Exponential", "cB":[-1.2569e-02]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2011"]["KstK"]   = {"Type":"Exponential", "cB":[-4.2236e-03]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2011"]["KPiPi"]  = {"Type":"Exponential", "cB":[-8.3869e-03]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2011"]["PiPiPi"] = {"Type":"Exponential", "cB":[-6.2744e-03]}

    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2012"]["NonRes"] = {"Type":"Exponential", "cB":[-4.8467e-03]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2012"]["PhiPi"]  = {"Type":"Exponential", "cB":[-1.2569e-02]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2012"]["KstK"]   = {"Type":"Exponential", "cB":[-4.2236e-03]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2012"]["KPiPi"]  = {"Type":"Exponential", "cB":[-8.3869e-03]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsK"]["2012"]["PiPiPi"] = {"Type":"Exponential", "cB":[-6.2744e-03]}

    ############################################################
    
    configdict["PDFList"]["CharmMass"]["Combinatorial"] = {}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2011"]["NonRes"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                        "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["mean"][0]], 
                                                                                        "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["sigma1"][0]], 
                                                                                        "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["sigma2"][0]], 
                                                                                        "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["alpha1"][0]],
                                                                                        "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["alpha2"][0]], 
                                                                                        "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["n1"][0]], 
                                                                                        "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["n2"][0]], 
                                                                                        "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["frac"][0]],
                                                                                        "cB"    : [-5.0833e-03], "fracD":[4.9069e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2011"]["PhiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                       "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["mean"][0]],
                                                                                       "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["sigma1"][0]],
                                                                                       "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["sigma2"][0]],
                                                                                       "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["alpha1"][0]],
                                                                                       "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["alpha2"][0]],
                                                                                       "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["n1"][0]],
                                                                                       "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["n2"][0]],
                                                                                       "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["frac"][0]],
                                                                                      "cB"     : [-1.1455e-02], "fracD":[7.6156e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2011"]["KstK"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                      "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["mean"][0]],
                                                                                      "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["sigma1"][0]],
                                                                                      "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["sigma2"][0]],
                                                                                      "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["alpha1"][0]],
                                                                                      "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["alpha2"][0]],
                                                                                      "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["n1"][0]],
                                                                                      "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["n2"][0]],
                                                                                      "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["frac"][0]],
                                                                                      "cB"    : [-1.2313e-02], "fracD":[6.0568e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2011"]["KPiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                       "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["mean"][0]],
                                                                                       "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["sigma1"][0]],
                                                                                       "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["sigma2"][0]],
                                                                                       "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["alpha1"][0]],
                                                                                       "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["alpha2"][0]],
                                                                                       "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["n1"][0]],
                                                                                       "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["n2"][0]],       
                                                                                       "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["frac"][0]],
                                                                                       "cB"    : [-2.1421e-03], "fracD":[6.5957e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2011"]["PiPiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                        "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["mean"][0]],
                                                                                        "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["sigma1"][0]],
                                                                                        "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["sigma2"][0]],
                                                                                        "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["alpha1"][0]],
                                                                                        "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["alpha2"][0]],
                                                                                        "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["n1"][0]],
                                                                                        "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["n2"][0]],
                                                                                        "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["frac"][0]],
                                                                                        "cB"    : [-5.3817e-03], "fracD":[7.5167e-01]}
    
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2012"]["NonRes"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                        "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["mean"][0]],
                                                                                        "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["sigma1"][0]],
                                                                                        "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["sigma2"][0]],
                                                                                        "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["alpha1"][0]],
                                                                                        "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["alpha2"][0]],
                                                                                        "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["n1"][0]],
                                                                                        "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["n2"][0]],
                                                                                        "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["frac"][0]],
                                                                                        "cB"    : [-5.0833e-03], "fracD":[4.9069e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2012"]["PhiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                       "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["mean"][0]],
                                                                                       "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["sigma1"][0]],
                                                                                       "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["sigma2"][0]],
                                                                                       "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["alpha1"][0]],
                                                                                       "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["alpha2"][0]],
                                                                                       "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["n1"][0]],
                                                                                       "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["n2"][0]],
                                                                                       "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["frac"][0]],
                                                                                       "cB"    : [-1.1455e-02], "fracD":[7.6156e-01] }
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2012"]["KstK"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                      "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["mean"][0]],
                                                                                      "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["sigma1"][0]],
                                                                                      "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["sigma2"][0]],
                                                                                      "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["alpha1"][0]],
                                                                                      "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["alpha2"][0]],
                                                                                      "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["n1"][0]],
                                                                                      "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["n2"][0]],
                                                                                      "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["frac"][0]],
                                                                                      "cB"    : [-1.2313e-02], "fracD":[6.0568e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2012"]["KPiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                       "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["mean"][0]],
                                                                                       "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["sigma1"][0]],
                                                                                       "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["sigma2"][0]],
                                                                                       "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["alpha1"][0]],
                                                                                       "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["alpha2"][0]],
                                                                                       "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["n1"][0]],
                                                                                       "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["n2"][0]],
                                                                                       "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["frac"][0]],
                                                                                       "cB"    : [-2.1421e-03], "fracD":[6.5957e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsK"]["2012"]["PiPiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                        "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["mean"][0]],
                                                                                        "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["sigma1"][0]],
                                                                                        "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["sigma2"][0]],
                                                                                        "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["alpha1"][0]],
                                                                                        "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["alpha2"][0]],
                                                                                        "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["n1"][0]],
                                                                                        "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["n2"][0]],
                                                                                        "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["frac"][0]],
                                                                                        "cB"    : [-5.3817e-03], "fracD":[7.5167e-01]}
    ############################################################
    
    configdict["PDFList"]["BacPIDK"]["Combinatorial"] = {}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2011"]["NonRes"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[7.0243e-01]}, 
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[7.0243e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2011"]["PhiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[6.6355e-01]},
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[6.6355e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2011"]["KstK"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                    "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                    "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[6.4798e-01]},
                                                                                             "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[6.4798e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2011"]["KPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                     "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                     "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[8.6494e-01]},
                                                                                              "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[8.6494e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2011"]["PiPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[8.8353e-01]},
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[8.8353e-01]}}}


    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2012"]["NonRes"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                      "Name":  {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[0.5]},
                                                                                                "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[0.5]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2012"]["PhiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[6.6355e-01]},
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[6.6355e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2012"]["KstK"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                    "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                    "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[6.4798e-01]},
                                                                                             "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[6.4798e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2012"]["KPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                     "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                     "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[8.6494e-01]},
                                                                                              "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[8.6494e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsK"]["2012"]["PiPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":{"Kaon","Pion"},
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[8.8353e-01]},
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[8.8353e-01]}}}


    ############################################################                                                                                                                                      
    #                      Bs2DsPi                                                                                                                                                              
    ############################################################                                                                                                                                  

    configdict["PDFList"]["BeautyMass"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBs2DsPiPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Bs2DsPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBs2DsPiPdf_m_both_2012"}

    ############################################################ 
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2011"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2011"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2011"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2011"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2012"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2012"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2012"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2012"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsPi"]["Bs2DsK"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]

    ############################################################                                   
    
    configdict["PDFList"]["BacPIDK"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Bs2DsPi_up_2011", "Down":"PIDKShape_Bs2DsPi_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Bs2DsPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                            "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                            "Name": {"Up":"PIDKShape_Bs2DsPi_up_2012", "Down":"PIDKShape_Bs2DsPi_down_2012"}}

   ############################################################                                                                                                                                      
    #                      Bs2DsstPi                                                                                                                                                              
    ############################################################                                                                                                                                  

    configdict["PDFList"]["BeautyMass"]["Bs2DsstPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsstPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsstPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsstPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBs2DsstPiPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Bs2DsstPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsstPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBs2DsstPiPdf_m_both_2012"}

    ############################################################ 
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2011"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2011"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2011"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2011"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2012"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2012"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2012"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2012"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsstPi"]["Bs2DsK"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]

    ############################################################                                   
    
    configdict["PDFList"]["BacPIDK"]["Bs2DsstPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsstPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsstPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsstPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Bs2DsstPi_up_2011", "Down":"PIDKShape_Bs2DsstPi_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Bs2DsstPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsstPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                            "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                            "Name": {"Up":"PIDKShape_Bs2DsstPi_up_2012", "Down":"PIDKShape_Bs2DsstPi_down_2012"}}

    
    ############################################################                                                                                                                                      
    #                      Bs2DsRho                                                                                                                                                              
    ############################################################                                                                                                                                  

    configdict["PDFList"]["BeautyMass"]["Bs2DsRho"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsRho"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsRho"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsRho"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBs2DsRhoPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Bs2DsRho"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsRho"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBs2DsRhoPdf_m_both_2012"}

    ############################################################ 
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2011"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2011"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2011"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2011"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2012"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2012"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2012"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2012"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsRho"]["Bs2DsK"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]

    ############################################################                                   
    
    configdict["PDFList"]["BacPIDK"]["Bs2DsRho"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsRho"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsRho"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsRho"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Bs2DsRho_up_2011", "Down":"PIDKShape_Bs2DsRho_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Bs2DsRho"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsRho"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                            "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                            "Name": {"Up":"PIDKShape_Bs2DsRho_up_2012", "Down":"PIDKShape_Bs2DsRho_down_2012"}}

    ############################################################   
    #                      Bd2DPi          
    ############################################################   
    
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DPiPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DPiPdf_m_both_2012"}

    ############################################################
    configdict["PDFList"]["CharmMass"]["Bd2DPi"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DPiPdf_m_both_2011_Ds"}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DPiPdf_m_both_2012_Ds"}

    
    ############################################################
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up":"PIDKShape_Bd2DPi_up_2011", "Down":"PIDKShape_Bd2DPi_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                            "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                            "Name": {"Up":"PIDKShape_Bd2DPi_up_2012", "Down":"PIDKShape_Bd2DPi_down_2012"}}

    ############################################################   
    #                      Bd2DK          
    ############################################################   
    
    configdict["PDFList"]["BeautyMass"]["Bd2DK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": "PhysBkgBd2DKPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DK"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": "PhysBkgBd2DKPdf_m_both_2012"}

    ############################################################
    configdict["PDFList"]["CharmMass"]["Bd2DK"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DK"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DK"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DK"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DKPdf_m_both_2011_Ds"}
    configdict["PDFList"]["CharmMass"]["Bd2DK"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DK"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DKPdf_m_both_2012_Ds"}

    
    ############################################################
    configdict["PDFList"]["BacPIDK"]["Bd2DK"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DK"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DK"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DK"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up":"PIDKShape_Bd2DK_up_2011", "Down":"PIDKShape_Bd2DK_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Bd2DK"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DK"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                            "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                            "Name": {"Up":"PIDKShape_Bd2DK_up_2012", "Down":"PIDKShape_Bd2DK_down_2012"}}
    
    ############################################################   
    #                      Lb2LcPi              
    ############################################################         

    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2LcPiPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                                "Name": "PhysBkgLb2LcPiPdf_m_both_2012"}

    ############################################################                                                                                                                                       
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2LcPiPdf_m_both_2011_Ds"}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2LcPiPdf_m_both_2012_Ds"}


    ############################################################                                                                                                                                       
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2LcPi_up_2011", "Down":"PIDKShape_Lb2LcPi_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2LcPi_up_2012", "Down":"PIDKShape_Lb2LcPi_down_2012"}}

    ############################################################   
    #                      Lb2LcK             
    ############################################################         

    configdict["PDFList"]["BeautyMass"]["Lb2LcK"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcK"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcK"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcK"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2LcPiPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Lb2LcK"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcK"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                                "Name": "PhysBkgLb2LcPiPdf_m_both_2012"}

    ############################################################                                                                                                                                       
    configdict["PDFList"]["CharmMass"]["Lb2LcK"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcK"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcK"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcK"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2LcPiPdf_m_both_2011_Ds"}
    configdict["PDFList"]["CharmMass"]["Lb2LcK"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcK"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2LcPiPdf_m_both_2012_Ds"}


    ############################################################                                                                                                                                       
    configdict["PDFList"]["BacPIDK"]["Lb2LcK"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcK"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcK"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcK"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2LcPi_up_2011", "Down":"PIDKShape_Lb2LcPi_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Lb2LcK"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcK"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2LcPi_up_2012", "Down":"PIDKShape_Lb2LcPi_down_2012"}}


    ############################################################   
    #                      Lb2Dsp             
    ############################################################         

    configdict["PDFList"]["BeautyMass"]["Lb2Dsp"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsp"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsp"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsp"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2DspPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsp"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsp"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                                "Name": "PhysBkgLb2DspPdf_m_both_2012"}

    ############################################################ 
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2011"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2011"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2011"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2011"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2012"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2012"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2012"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2012"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsp"]["Bs2DsK"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]				    

    ############################################################                                                                                                                                       
    configdict["PDFList"]["BacPIDK"]["Lb2Dsp"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsp"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsp"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsp"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2Dsp_up_2011", "Down":"PIDKShape_Lb2Dsp_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsp"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsp"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2Dsp_up_2012", "Down":"PIDKShape_Lb2Dsp_down_2012"}}

    ############################################################   
    #                      Lb2Dsstp             
    ############################################################         

    configdict["PDFList"]["BeautyMass"]["Lb2Dsstp"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsstp"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsstp"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsstp"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2DspPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsstp"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2Dsstp"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                                "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                                "Name": "PhysBkgLb2DspPdf_m_both_2012"}

    ############################################################ 
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2011"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2011"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2011"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2011"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2012"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2012"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2012"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2012"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Lb2Dsstp"]["Bs2DsK"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]				    

    ############################################################                                                                                                                                       
    configdict["PDFList"]["BacPIDK"]["Lb2Dsstp"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsstp"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsstp"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsstp"]["Bs2DsK"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2Dsstp_up_2011", "Down":"PIDKShape_Lb2Dsstp_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsstp"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2Dsstp"]["Bs2DsK"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dsk_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2Dsstp_up_2012", "Down":"PIDKShape_Lb2Dsstp_down_2012"}}

    ############################################################                                                                                                                                          
    #                      Bd2DsK                                 
    ############################################################
    
    scale1_Bd2DPi = 1.00808721452
    scale2_Bd2DPi = 1.03868673310
    configdict["PDFList"]["BeautyMass"]["Bd2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["NonRes"] = {"Type" : "DoubleCrystalBall",
                                                                                   "mean" :  [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["mean"][0] - 86.8], 
                                                                                   "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["sigma1"][0]*scale1_Bd2DPi], 
                                                                                   "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["sigma1"][0]*scale2_Bd2DPi], 
                                                                                   "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["alpha1"][0]],
                                                                                   "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["alpha2"][0]], 
                                                                                   "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["n1"][0]], 
                                                                                   "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["n2"][0]], 
                                                                                   "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["PhiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                  "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["mean"][0] - 86.8],
                                                                                  "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                  "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                  "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["alpha1"][0]],
                                                                                  "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["alpha2"][0]],
                                                                                  "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["n1"][0]],
                                                                                  "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["n2"][0]],
                                                                                  "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["KstK"] = {"Type" : "DoubleCrystalBall",
                                                                                 "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["mean"][0] - 86.8],
                                                                                 "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                 "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                 "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["alpha1"][0]],
                                                                                 "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["alpha2"][0]],
                                                                                 "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["n1"][0]],
                                                                                 "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["n2"][0]],
                                                                                 "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["KPiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                  "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["mean"][0] - 86.8],
                                                                                  "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                  "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                  "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["alpha1"][0]],
                                                                                  "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["alpha2"][0]],
                                                                                  "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["n1"][0]],
                                                                                  "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["n2"][0]],
                                                                                  "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["PiPiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                   "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["mean"][0] - 86.8],
                                                                                   "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                   "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                   "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["alpha1"][0]],
                                                                                   "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["alpha2"][0]],
                                                                                   "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["n1"][0]],
                                                                                   "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["n2"][0]],
                                                                                   "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["NonRes"] = {"Type" : "DoubleCrystalBall",
                                                                                   "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["mean"][0] - 86.8],
                                                                                   "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                   "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                   "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["alpha1"][0]],
                                                                                   "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["alpha2"][0]],
                                                                                   "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["n1"][0]],
                                                                                   "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["n2"][0]],
                                                                                   "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["PhiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                  "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["mean"][0] - 86.8],
                                                                                  "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                  "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                  "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["alpha1"][0]],
                                                                                  "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["alpha2"][0]],
                                                                                  "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["n1"][0]],
                                                                                  "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["n2"][0]],
                                                                                  "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["KstK"] = {"Type" : "DoubleCrystalBall",
                                                                                 "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["mean"][0] - 86.8],
                                                                                 "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                 "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                 "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["alpha1"][0]],
                                                                                 "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["alpha2"][0]],
                                                                                 "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["n1"][0]],
                                                                                 "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["n2"][0]],
                                                                                 "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["KPiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                  "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["mean"][0] - 86.8],
                                                                                  "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                  "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                  "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["alpha1"][0]],
                                                                                  "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["alpha2"][0]],
                                                                                  "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["n1"][0]],
                                                                                  "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["n2"][0]],
                                                                                  "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]["frac"][0]]}
    
    configdict["PDFList"]["BeautyMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["PiPiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                   "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["mean"][0] - 86.8],
                                                                                   "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                   "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                   "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["alpha1"][0]],
                                                                                   "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["alpha2"][0]],
                                                                                   "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["n1"][0]],
                                                                                   "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["n2"][0]],
                                                                                   "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]["frac"][0]]}



    #############################################################

    configdict["PDFList"]["CharmMass"]["Bd2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsK"]["Bs2DsK"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]

    #############################################################

    configdict["PDFList"]["BacPIDK"]["Bd2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2011"]["NonRes"]  =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["NonRes"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2011"]["PhiPi"]   =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["PhiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2011"]["KstK"]    =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["KstK"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2011"]["KPiPi"]   =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["KPiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2011"]["PiPiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2012"]["NonRes"]  =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["NonRes"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2012"]["PhiPi"]   =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["PhiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2012"]["KstK"]    =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["KstK"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2012"]["KPiPi"]   =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["KPiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsK"]["Bs2DsK"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsK"]["2012"]["PiPiPi"]




    ############################################################ 
    #Tagging calibration and mistag PDF. If "MistagPDF" : None,
    #then a average mistag is used
    ############################################################
    
    configdict["Taggers"] = {}
    for comp in configdict["Components"].iterkeys():
        configdict["Taggers"][comp] = {}
        configdict["Taggers"][comp] = {"OS" :
                                       {"Calibration":
                                        {"p0"       : [0.0],
                                         "p1"       : [1.0],
                                         "deltap0"  : [0.0],
                                         "deltap1"  : [0.0],
                                         "avgeta"   : [0.35],
                                         "tageff"   : [0.6],
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"     : "Mock",
                                         "eta0"     : [0.0],
                                         "etaavg"   : [0.35],
                                         "f"        : [0.25]
                                         }
                                        },
                                       "SS":
                                       {"Calibration":
                                        {"p0"       : [0.0],
                                         "p1"       : [1.0],
                                         "deltap0"  : [0.0],
                                         "deltap1"  : [0.0],
                                         "avgeta"   : [0.35],
                                         "tageff"   : [0.6],
                                         "tagasymm" : [0.0]
                                         },
                                        "MistagPDF" :
                                        {"Type"     : "Mock",
                                         "eta0"     : [0.0],
                                         "etaavg"   : [0.35],
                                         "f"        : [0.25]
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
        configdict["ResolutionAcceptance"][comp] = {"TimeErrorPDF": #None,
                                                    {"Type": "Mock",
                                                     "ResolutionAverage" : [0.5]
                                                     },
                                                    "Acceptance":
                                                    {"Type": "Spline",
                                                     "KnotPositions" : [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
                                                     "KnotCoefficients" : [ 4.5853e-01, 6.8963e-01, 8.8528e-01,
                                                                            1.1296e+00, 1.2232e+00, 1.2277e+00 ]},
                                                    #"Resolution":
                                                    #{"Type": "AverageModel",
                                                    # "Parameters": { 'sigmas': [ 0.050 ], 'fractions': [] },
                                                    # "Bias": [0.0],
                                                    # "ScaleFactor": [1.0]}
                                                    "Resolution":
                                                    {"Type": "GaussianWithPEDTE",
                                                     "Average": [0.5],
                                                     "Bias": [0.0],
                                                     "ScaleFactor": [1.0]}
                                                    }
        
    ############################################################ 
    #Production and detection asymmetries
    ############################################################
    
    configdict["ProductionAsymmetry"] = {}
    configdict["DetectionAsymmetry"] = {}
    for comp in configdict["Components"].iterkeys():
        configdict["ProductionAsymmetry"][comp] = {}
        configdict["DetectionAsymmetry"][comp] = {}
        configdict["ProductionAsymmetry"][comp] = [0.1]
        configdict["DetectionAsymmetry"][comp] = [0.1]

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
    configdict["ACP"]["Signal"] = { "Gamma"                : [0.656],
                                    "DeltaGamma"           : [0.00267],
                                    "DeltaM"               : [0.510],
                                    "ArgLf"                : [ArgqOverp_d + ArgAbarf_d - ArgAf_d],
                                    "ArgLbarfbar"          : [ArgpOverq_d + ArgAfbar_d - ArgAbarfbar_d],
                                    "ModLf"                : [ModAbarf_d/ModAf_d],
                                    "ParameteriseIntegral" : True,
                                    "NBinsAcceptance"      : 0, #keep at zero if using spline acceptance!
                                    "NBinsProperTimeErr"   : 100}

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
                                        "NBinsAcceptance"       : 0, #keep at zero if using spline acceptance!
                                        "NBinsProperTimeErr"    : 100}
    
    return configdict
