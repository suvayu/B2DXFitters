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
                                                   "Range": [ -7.0, 5.0]},
                                 "TrueID":        {"Type" : "RooRealVar",
                                                   "Title" : "True component ID",
                                                   "Range" : [0.0,1000.0]}}

    '''
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
    '''
    
    ############################################################ 
    #List of mass hypotheses for bachelor
    #The content of this dictionary determines how many
    #bachelor PID bins the final dataset is splitted into
    ############################################################
    
    configdict["Hypothesys"] = ["Bs2DsPi"]

    ############################################################
    #Signal decay, Charm decay mode and year of data taking
    #Splitting per magnet polarity not implemented, at the moment
    ############################################################

    configdict["Decay"] = "Bs2DsPi"
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
    print fracRun1
    
    
    configdict["WorkspaceToRead"] = {"File":"/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/2nd/work_dspi_2nd_mcpid_signalpid_comb.root",
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
    configdict["Components"] = {"Signal":        {"Bs2DsPi": {"2011": {"NonRes": [15900*fracRun1], "PhiPi":[34100*fracRun1], 
                                                                       "KstK"  : [25500*fracRun1], "KPiPi":[5600*fracRun1],  "PiPiPi":[15026*fracRun1] },
                                                              "2012": {"NonRes": [15900*(1.0-fracRun1)], "PhiPi":[34100*(1.0-fracRun1)], 
                                                                       "KstK"  : [25500*(1.0-fracRun1)], "KPiPi":[5600*(1.0-fracRun1)],  "PiPiPi":[15026*(1.0-fracRun1)] }}},
                                "Combinatorial": {"Bs2DsPi": {"2011": {"NonRes": [8400*fracRun1],  "PhiPi":[2800*fracRun1],  
                                                                       "KstK"  : [3400*fracRun1],  "KPiPi":[2300*fracRun1],  "PiPiPi":[5800*fracRun1] },
                                                              "2012": {"NonRes": [8400*(1.0-fracRun1)],  "PhiPi":[2800*(1.0-fracRun1)],  
                                                                       "KstK"  : [3400*(1.0-fracRun1)],  "KPiPi":[2300*(1.0-fracRun1)],  "PiPiPi":[5800*(1.0-fracRun1)] }}},
                                "Bd2DPi":        {"Bs2DsPi": {"2011": {"NonRes": [150*fracRun1],  "PhiPi":[10*fracRun1],  
                                                                       "KstK"  : [30*fracRun1],   "KPiPi":[30.0*fracRun1],   "PiPiPi":[0.0*fracRun1] },
                                                              "2012": {"NonRes": [150*(1.0-fracRun1)],  "PhiPi":[10.0*(1.0-fracRun1)],  
                                                                       "KstK"  : [30*(1.0-fracRun1)],   "KPiPi":[30.0*(1.0-fracRun1)],   "PiPiPi":[0.0*(1.0-fracRun1)] }}},
                                "Lb2LcPi":       {"Bs2DsPi": {"2011": {"NonRes": [480.0*fracRun1], "PhiPi":[95*fracRun1],   
                                                                       "KstK"  : [150*fracRun1],   "KPiPi":[5*fracRun1],   "PiPiPi":[0.0*fracRun1] },
                                                              "2012": {"NonRes": [480.0*(1.0-fracRun1)], "PhiPi":[95*(1.0-fracRun1)],   
                                                                       "KstK"  : [150*(1.0 - fracRun1)],  "KPiPi" : [5*(1.0-fracRun1)],   "PiPiPi":[0.0*(1.0-fracRun1)] }}}, 
                                "Bs2DsK":        {"Bs2DsPi": {"2011": {"NonRes": [116.0*fracRun1], "PhiPi":[261.*fracRun1], 
                                                                       "KstK"  : [163*fracRun1], "KPiPi":[66*fracRun1], "PiPiPi":[158*fracRun1] },
                                                              "2012": {"NonRes": [116.0*(1.0-fracRun1)], "PhiPi":[261.*(1.0-fracRun1)], 
                                                                       "KstK"  : [163*(1.0-fracRun1)], "KPiPi":[66*(1.0-fracRun1)], "PiPiPi":[158*(1.0-fracRun1)] }}},
                                "Bd2DsPi":       {"Bs2DsPi": {"2011": {"NonRes": [100*fracRun1],    "PhiPi":[220*fracRun1],    
                                                                       "KstK"  : [170*fracRun1],   "KPiPi":[40*fracRun1],    "PiPiPi":[100*fracRun1] },
                                                              "2012": {"NonRes": [100*(1.0-fracRun1)],    "PhiPi":[220*(1.0-fracRun1)],    
                                                                       "KstK"  : [170*(1.0-fracRun1)],    "KPiPi":[40*(1.0-fracRun1)],    "PiPiPi":[100*(1.0-fracRun1)] }}}}
    
                                                                       
    ############################################################
    #"Code" to identify the True ID for each component
    ############################################################

    configdict["TrueID"] = {}
    configdict["TrueID"] = {"Signal"        : 100,
                            "Combinatorial" : 200,
                            "Bd2DPi"        : 300,
                            "Lb2LcPi"       : 400,
                            "Bs2DsK"        : 500,
                            "Bd2DsPi"       : 600}

    configdict["CombinedYields"] = { "Signal":["Signal"],
                                     "Combinatorial":["Combinatorial"],
                                     "Bs2DsDsstPiRho":["Bd2DsPi"]}
 

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
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5367.51], "sigma1":[1.6878e+01], "sigma2": [1.1200e+01], "alpha1": [-2.0314e+00],
                                                                                   "alpha2":[1.6351e+00], "n1":[3.6820e+00], "n2":[1.5081e+00], "frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5367.51], "sigma1":[1.7260e+01], "sigma2": [1.1436e+01], "alpha1": [-2.2307e+00],
                                                                                   "alpha2":[2.1032e+00], "n1":[2.8836e+00], "n2":[6.1945e-01],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[5367.51], "sigma1":[1.5228e+01], "sigma2": [1.2361e+01], "alpha1": [-1.7275e+00],
                                                                                  "alpha2":[1.5425e+00], "n1":[4.4322e+00], "n2":[1.5073e+00],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[5367.51], "sigma1":[1.7791e+01], "sigma2": [1.1036e+01], "alpha1": [-2.5874e+00],
                                                                                  "alpha2":[2.3644e+00], "n1":[1.7676e+00], "n2":[3.2020e-01],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5367.51], "sigma1":[1.7955e+01], "sigma2": [1.1608e+01], "alpha1": [-2.2449e+00],
                                                                                   "alpha2":[2.0136e+00], "n1":[2.7271e+00], "n2":[6.7857e-01],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5367.51], "sigma1":[1.6878e+01], "sigma2": [1.1200e+01], "alpha1": [-2.0314e+00],
                                                                                   "alpha2":[1.6351e+00], "n1":[3.6820e+00], "n2":[1.5081e+00],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[5367.51], "sigma1":[1.7260e+01], "sigma2": [1.1436e+01], "alpha1": [-2.2307e+00],
                                                                                 "alpha2":[2.1032e+00], "n1":[2.8836e+00], "n2":[6.1945e-01],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[5367.51], "sigma1":[1.5228e+01], "sigma2": [1.2361e+01], "alpha1": [-1.7275e+00],
                                                                                  "alpha2":[1.5425e+00], "n1":[4.4322e+00], "n2":[1.5073e+00],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[5367.51], "sigma1":[1.7791e+01], "sigma2": [1.1036e+01], "alpha1": [-2.5874e+00],
                                                                                  "alpha2":[2.3644e+00], "n1":[1.7676e+00], "n2":[3.2020e-01],"frac":[0.5]}
    configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[5367.51], "sigma1":[1.7955e+01], "sigma2": [1.1608e+01], "alpha1": [-2.2449e+00],
                                                                                   "alpha2":[2.0136e+00], "n1":[2.7271e+00], "n2":[6.7857e-01],"frac":[0.5]}
    
    ############################################################### 
    configdict["PDFList"]["CharmMass"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[1968.49], "sigma1":[5.2639e+00], "sigma2": [5.7588e+00], "alpha1": [-1.1429e+00],
                                                                                   "alpha2":[1.1400e+00], "n1":[1.1892e+01], "n2":[7.6655e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[1968.49], "sigma1":[5.7789e+00], "sigma2": [5.3142e+00], "alpha1": [-1.0496e+00],
                                                                                 "alpha2":[1.1819e+00], "n1":[4.9291e+01], "n2":[4.9162e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"] =  {"Type" : "DoubleCrystalBall",
                                                                                "mean":[1968.49], "sigma1":[5.5277e+00], "sigma2": [5.9173e+00], "alpha1": [-1.1662e+00],
                                                                                "alpha2":[1.1958e+00], "n1":[1.7661e+01], "n2":[9.4543e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[1968.49], "sigma1":[7.8831e+00], "sigma2": [6.5553e+00], "alpha1": [-1.2500e+00],
                                                                                 "alpha2":[1.3706e+00], "n1":[5.0000e+01], "n2":[3.0195e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[1968.49], "sigma1":[7.8627e+00], "sigma2": [9.0180e+00], "alpha1": [-1.1731e+00],
                                                                                  "alpha2":[9.0873e-01], "n1":[8.5777e+00], "n2":[2.7506e+01], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"] =  {"Type" : "DoubleCrystalBall",
                                                                                   "mean":[1968.49], "sigma1":[5.2639e+00], "sigma2": [5.7588e+00], "alpha1": [-1.1429e+00],
                                                                                   "alpha2":[1.1400e+00], "n1":[1.1892e+01], "n2":[7.6655e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[1968.49], "sigma1":[5.7789e+00], "sigma2": [5.3142e+00], "alpha1": [-1.0496e+00],
                                                                                 "alpha2":[1.1819e+00], "n1":[4.9291e+01], "n2":[4.9162e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"] =  {"Type" : "DoubleCrystalBall",
                                                                                "mean":[1968.49], "sigma1":[5.5277e+00], "sigma2": [5.9173e+00], "alpha1": [-1.1662e+00],
                                                                                "alpha2":[1.1958e+00], "n1":[1.7661e+01], "n2":[9.4543e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                 "mean":[1968.49], "sigma1":[7.8831e+00], "sigma2": [6.5553e+00], "alpha1": [-1.2500e+00],
                                                                                 "alpha2":[1.3706e+00], "n1":[5.0000e+01], "n2":[3.0195e+00], "frac":[0.5]}
    configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"] =  {"Type" : "DoubleCrystalBall",
                                                                                  "mean":[1968.49], "sigma1":[7.8627e+00], "sigma2": [9.0180e+00], "alpha1": [-1.1731e+00],
                                                                                  "alpha2":[9.0873e-01], "n1":[8.5777e+00], "n2":[2.7506e+01], "frac":[0.5]}
    ###############################################################
    configdict["PDFList"]["BacPIDK"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",  
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_nonres_2011", "Down":"PIDKShape_Bs2DsPi_down_nonres_2011"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_phipi_2011", "Down":"PIDKShape_Bs2DsPi_down_phipi_2011"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["KstK"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_kstk_2011", "Down":"PIDKShape_Bs2DsPi_down_kstk_2011"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_kpipi_2011", "Down":"PIDKShape_Bs2DsPi_down_kpipi_2011"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_pipipi_2011", "Down":"PIDKShape_Bs2DsPi_down_pipipi_2011"}}

    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_nonres_2012", "Down":"PIDKShape_Bs2DsPi_down_nonres_2012"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_phipi_2012", "Down":"PIDKShape_Bs2DsPi_down_phipi_2012"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["KstK"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_kstk_2012", "Down":"PIDKShape_Bs2DsPi_down_kstk_2012"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_kpipi_2012", "Down":"PIDKShape_Bs2DsPi_down_kpipi_2012"}}
    configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up": "PIDKShape_Bs2DsPi_up_pipipi_2012", "Down":"PIDKShape_Bs2DsPi_down_pipipi_2012"}}

    ############################################################    
    #                      Combinatorial      
    ############################################################   

    ############################################################
    configdict["PDFList"]["BeautyMass"]["Combinatorial"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["NonRes"] = {"Type":"DoubleExponential", "cB1":[-4.8467e-03], "cB2":[0.0], "frac":[7.9999e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["PhiPi"]  = {"Type":"DoubleExponential", "cB1":[-1.2569e-02], "cB2":[0.0], "frac":[7.5491e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["KstK"]   = {"Type":"DoubleExponential", "cB1":[-4.2236e-03], "cB2":[0.0], "frac":[8.7769e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["KPiPi"]  = {"Type":"DoubleExponential", "cB1":[-8.3869e-03], "cB2":[0.0], "frac":[4.9568e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["PiPiPi"] = {"Type":"DoubleExponential", "cB1":[-6.2744e-03], "cB2":[0.0], "frac":[5.9887e-01]}

    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["NonRes"] = {"Type":"DoubleExponential", "cB1":[-4.8467e-03], "cB2":[0.0], "frac":[7.9999e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["PhiPi"]  = {"Type":"DoubleExponential", "cB1":[-1.2569e-02], "cB2":[0.0], "frac":[7.5491e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["KstK"]   = {"Type":"DoubleExponential", "cB1":[-4.2236e-03], "cB2":[0.0], "frac":[8.7769e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["KPiPi"]  = {"Type":"DoubleExponential", "cB1":[-8.3869e-03], "cB2":[0.0], "frac":[4.9568e-01]}
    configdict["PDFList"]["BeautyMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["PiPiPi"] = {"Type":"DoubleExponential", "cB1":[-6.2744e-03], "cB2":[0.0], "frac":[5.9887e-01]}

    ############################################################
    
    configdict["PDFList"]["CharmMass"]["Combinatorial"] = {}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"] = {}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["NonRes"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                        "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["mean"][0]], 
                                                                                        "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["sigma1"][0]], 
                                                                                        "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["sigma2"][0]], 
                                                                                        "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["alpha1"][0]],
                                                                                        "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["alpha2"][0]], 
                                                                                        "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["n1"][0]], 
                                                                                        "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["n2"][0]], 
                                                                                        "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["frac"][0]],
                                                                                        "cB"    : [-5.0833e-03], "fracD":[4.9069e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["PhiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                       "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["mean"][0]],
                                                                                       "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["sigma1"][0]],
                                                                                       "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["sigma2"][0]],
                                                                                       "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["alpha1"][0]],
                                                                                       "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["alpha2"][0]],
                                                                                       "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["n1"][0]],
                                                                                       "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["n2"][0]],
                                                                                       "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["frac"][0]],
                                                                                      "cB"     : [-1.1455e-02], "fracD":[7.6156e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["KstK"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                      "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["mean"][0]],
                                                                                      "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["sigma1"][0]],
                                                                                      "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["sigma2"][0]],
                                                                                      "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["alpha1"][0]],
                                                                                      "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["alpha2"][0]],
                                                                                      "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["n1"][0]],
                                                                                      "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["n2"][0]],
                                                                                      "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["frac"][0]],
                                                                                      "cB"    : [-1.2313e-02], "fracD":[6.0568e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["KPiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                       "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["mean"][0]],
                                                                                       "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["sigma1"][0]],
                                                                                       "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["sigma2"][0]],
                                                                                       "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["alpha1"][0]],
                                                                                       "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["alpha2"][0]],
                                                                                       "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["n1"][0]],
                                                                                       "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["n2"][0]],       
                                                                                       "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["frac"][0]],
                                                                                       "cB"    : [-2.1421e-03], "fracD":[6.5957e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2011"]["PiPiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                        "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["mean"][0]],
                                                                                        "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["sigma1"][0]],
                                                                                        "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["sigma2"][0]],
                                                                                        "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["alpha1"][0]],
                                                                                        "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["alpha2"][0]],
                                                                                        "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["n1"][0]],
                                                                                        "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["n2"][0]],
                                                                                        "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["frac"][0]],
                                                                                        "cB"    : [-5.3817e-03], "fracD":[7.5167e-01]}
    
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["NonRes"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                        "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["mean"][0]],
                                                                                        "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["sigma1"][0]],
                                                                                        "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["sigma2"][0]],
                                                                                        "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["alpha1"][0]],
                                                                                        "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["alpha2"][0]],
                                                                                        "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["n1"][0]],
                                                                                        "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["n2"][0]],
                                                                                        "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["frac"][0]],
                                                                                        "cB"    : [-5.0833e-03], "fracD":[4.9069e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["PhiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                       "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["mean"][0]],
                                                                                       "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["sigma1"][0]],
                                                                                       "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["sigma2"][0]],
                                                                                       "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["alpha1"][0]],
                                                                                       "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["alpha2"][0]],
                                                                                       "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["n1"][0]],
                                                                                       "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["n2"][0]],
                                                                                       "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["frac"][0]],
                                                                                       "cB"    : [-1.1455e-02], "fracD":[7.6156e-01] }
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["KstK"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                      "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["mean"][0]],
                                                                                      "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["sigma1"][0]],
                                                                                      "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["sigma2"][0]],
                                                                                      "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["alpha1"][0]],
                                                                                      "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["alpha2"][0]],
                                                                                      "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["n1"][0]],
                                                                                      "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["n2"][0]],
                                                                                      "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["frac"][0]],
                                                                                      "cB"    : [-1.2313e-02], "fracD":[6.0568e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["KPiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                       "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["mean"][0]],
                                                                                       "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["sigma1"][0]],
                                                                                       "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["sigma2"][0]],
                                                                                       "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["alpha1"][0]],
                                                                                       "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["alpha2"][0]],
                                                                                       "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["n1"][0]],
                                                                                       "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["n2"][0]],
                                                                                       "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["frac"][0]],
                                                                                       "cB"    : [-2.1421e-03], "fracD":[6.5957e-01]}
    configdict["PDFList"]["CharmMass"]["Combinatorial"]["Bs2DsPi"]["2012"]["PiPiPi"] = {"Type":"ExponentialPlusDoubleCrystalBall",
                                                                                        "mean"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["mean"][0]],
                                                                                        "sigma1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["sigma1"][0]],
                                                                                        "sigma2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["sigma2"][0]],
                                                                                        "alpha1": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["alpha1"][0]],
                                                                                        "alpha2": [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["alpha2"][0]],
                                                                                        "n1"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["n1"][0]],
                                                                                        "n2"    : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["n2"][0]],
                                                                                        "frac"  : [configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["frac"][0]],
                                                                                        "cB"    : [-5.3817e-03], "fracD":[7.5167e-01]}
    ############################################################
    
    configdict["PDFList"]["BacPIDK"]["Combinatorial"] = {}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2011"]["NonRes"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[7.0243e-01]}, 
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[7.0243e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2011"]["PhiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[6.6355e-01]},
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[6.6355e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2011"]["KstK"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                    "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                    "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[6.4798e-01]},
                                                                                             "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[6.4798e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2011"]["KPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                     "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                     "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[8.6494e-01]},
                                                                                              "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[8.6494e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2011"]["PiPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2011", "Kaon":"PIDKShape_CombK_up_2011", "fracPIDK":[8.8353e-01]},
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2011", "Kaon":"PIDKShape_CombK_down_2011", "fracPIDK":[8.8353e-01]}}}


    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2012"]["NonRes"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                      "Name":  {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[7.0243e-01]},
                                                                                                "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[7.0243e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2012"]["PhiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[6.6355e-01]},
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[6.6355e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2012"]["KstK"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                    "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                    "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[6.4798e-01]},
                                                                                             "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[6.4798e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2012"]["KPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                     "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                     "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[8.6494e-01]},
                                                                                              "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[8.6494e-01]}}}
    configdict["PDFList"]["BacPIDK"]["Combinatorial"]["Bs2DsPi"]["2012"]["PiPiPi"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                      "Type": "FromWorkspace", "Workspace" : "workspace", "Contributions":["Pion","Kaon"],
                                                                                      "Name": {"Up":   {"Pion":"PIDKShape_CombPi_up_2012", "Kaon":"PIDKShape_CombK_up_2012", "fracPIDK":[8.8353e-01]},
                                                                                               "Down": {"Pion":"PIDKShape_CombPi_down_2012", "Kaon":"PIDKShape_CombK_down_2012", "fracPIDK":[8.8353e-01]}}}





    ############################################################   
    #                      Bd2DPi          
    ############################################################   
    
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsPi"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DPiPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DPi"]["Bs2DsPi"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DPiPdf_m_both_2012"}

    ############################################################
    configdict["PDFList"]["CharmMass"]["Bd2DPi"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsPi"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsPi"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DPiPdf_m_both_2011_Ds"}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DPi"]["Bs2DsPi"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBd2DPiPdf_m_both_2012_Ds"}

    
    ############################################################
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsPi"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": {"Up":"PIDKShape_Bd2DPi_up_2011", "Down":"PIDKShape_Bd2DPi_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DPi"]["Bs2DsPi"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                            "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                            "Name": {"Up":"PIDKShape_Bd2DPi_up_2012", "Down":"PIDKShape_Bd2DPi_down_2012"}}

    
    ############################################################   
    #                      Lb2LcPi              
    ############################################################         

    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsPi"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2LcPiPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Lb2LcPi"]["Bs2DsPi"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                                "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                                "Name": "PhysBkgLb2LcPiPdf_m_both_2012"}

    ############################################################                                                                                                                                       
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsPi"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsPi"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2LcPiPdf_m_both_2011_Ds"}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Lb2LcPi"]["Bs2DsPi"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgLb2LcPiPdf_m_both_2012_Ds"}


    ############################################################                                                                                                                                       
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsPi"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2LcPi_up_2011", "Down":"PIDKShape_Lb2LcPi_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Lb2LcPi"]["Bs2DsPi"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Lb2LcPi_up_2012", "Down":"PIDKShape_Lb2LcPi_down_2012"}}

    ############################################################                                                                                                                                      
    #                      Bs2DsK                                                                                                                                                              
    ############################################################                                                                                                                                  

    configdict["PDFList"]["BeautyMass"]["Bs2DsK"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsK"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsK"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsK"]["Bs2DsPi"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBs2DsKPdf_m_both_2011"}
    configdict["PDFList"]["BeautyMass"]["Bs2DsK"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Bs2DsK"]["Bs2DsPi"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                               "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                               "Name": "PhysBkgBs2DsKPdf_m_both_2012"}

    ############################################################ 
    configdict["PDFList"]["CharmMass"]["Bs2DsK"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2011"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2011"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2011"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2011"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2012"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2012"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2012"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2012"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bs2DsK"]["Bs2DsPi"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]

    ############################################################                                   
    
    configdict["PDFList"]["BacPIDK"]["Bs2DsK"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsK"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsK"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsK"]["Bs2DsPi"]["2011"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                             "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                             "Name": {"Up":"PIDKShape_Bs2DsK_up_2011", "Down":"PIDKShape_Bs2DsK_down_2011"}}
    configdict["PDFList"]["BacPIDK"]["Bs2DsK"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Bs2DsK"]["Bs2DsPi"]["2012"]["All"] = {"File": "/afs/cern.ch/work/a/adudziak/public/workspace/DsK3fbPAPER/splits/work_dspi_2nd_mcpid_signalpid_comb.root",
                                                                            "Type": "FromWorkspace", "Workspace" : "workspace",
                                                                            "Name": {"Up":"PIDKShape_Bs2DsK_up_2012", "Down":"PIDKShape_Bs2DsK_down_2012"}}

    
    ############################################################                                                                                                                                          
    #                      Bd2DsPi                                 
    ############################################################
    
    scale1_Bd2DPi = 1.00808721452
    scale2_Bd2DPi = 1.03868673310
    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["NonRes"] = {"Type" : "DoubleCrystalBall",
                                                                                   "mean" :  [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["mean"][0] - 86.8], 
                                                                                   "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["sigma1"][0]*scale1_Bd2DPi], 
                                                                                   "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["sigma1"][0]*scale2_Bd2DPi], 
                                                                                   "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["alpha1"][0]],
                                                                                   "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["alpha2"][0]], 
                                                                                   "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["n1"][0]], 
                                                                                   "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["n2"][0]], 
                                                                                   "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["PhiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                  "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["mean"][0] - 86.8],
                                                                                  "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                  "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                  "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["alpha1"][0]],
                                                                                  "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["alpha2"][0]],
                                                                                  "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["n1"][0]],
                                                                                  "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["n2"][0]],
                                                                                  "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["KstK"] = {"Type" : "DoubleCrystalBall",
                                                                                 "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["mean"][0] - 86.8],
                                                                                 "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                 "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                 "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["alpha1"][0]],
                                                                                 "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["alpha2"][0]],
                                                                                 "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["n1"][0]],
                                                                                 "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["n2"][0]],
                                                                                 "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["KPiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                  "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["mean"][0] - 86.8],
                                                                                  "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                  "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                  "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["alpha1"][0]],
                                                                                  "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["alpha2"][0]],
                                                                                  "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["n1"][0]],
                                                                                  "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["n2"][0]],
                                                                                  "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["PiPiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                   "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["mean"][0] - 86.8],
                                                                                   "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                   "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                   "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["alpha1"][0]],
                                                                                   "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["alpha2"][0]],
                                                                                   "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["n1"][0]],
                                                                                   "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["n2"][0]],
                                                                                   "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["NonRes"] = {"Type" : "DoubleCrystalBall",
                                                                                   "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["mean"][0] - 86.8],
                                                                                   "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                   "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                   "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["alpha1"][0]],
                                                                                   "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["alpha2"][0]],
                                                                                   "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["n1"][0]],
                                                                                   "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["n2"][0]],
                                                                                   "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["PhiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                  "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["mean"][0] - 86.8],
                                                                                  "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                  "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                  "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["alpha1"][0]],
                                                                                  "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["alpha2"][0]],
                                                                                  "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["n1"][0]],
                                                                                  "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["n2"][0]],
                                                                                  "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["KstK"] = {"Type" : "DoubleCrystalBall",
                                                                                 "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["mean"][0] - 86.8],
                                                                                 "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                 "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                 "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["alpha1"][0]],
                                                                                 "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["alpha2"][0]],
                                                                                 "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["n1"][0]],
                                                                                 "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["n2"][0]],
                                                                                 "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]["frac"][0]]}

    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["KPiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                  "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["mean"][0] - 86.8],
                                                                                  "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                  "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                  "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["alpha1"][0]],
                                                                                  "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["alpha2"][0]],
                                                                                  "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["n1"][0]],
                                                                                  "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["n2"][0]],
                                                                                  "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]["frac"][0]]}
    
    configdict["PDFList"]["BeautyMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["PiPiPi"] = {"Type" : "DoubleCrystalBall",
                                                                                   "mean"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["mean"][0] - 86.8],
                                                                                   "sigma1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["sigma1"][0]*scale1_Bd2DPi],
                                                                                   "sigma2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["sigma1"][0]*scale2_Bd2DPi],
                                                                                   "alpha1": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["alpha1"][0]],
                                                                                   "alpha2": [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["alpha2"][0]],
                                                                                   "n1"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["n1"][0]],
                                                                                   "n2"    : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["n2"][0]],
                                                                                   "frac"  : [configdict["PDFList"]["BeautyMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]["frac"][0]]}



    #############################################################

    configdict["PDFList"]["CharmMass"]["Bd2DsPi"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["NonRes"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["PhiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["KstK"]    =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["KPiPi"]   =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]
    configdict["PDFList"]["CharmMass"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["CharmMass"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]

    #############################################################

    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2011"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["NonRes"]  =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["NonRes"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["PhiPi"]   =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["PhiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["KstK"]    =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["KstK"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["KPiPi"]   =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["KPiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2011"]["PiPiPi"]  =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2011"]["PiPiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2012"] = {}
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["NonRes"]  =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["NonRes"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["PhiPi"]   =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["PhiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["KstK"]    =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["KstK"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["KPiPi"]   =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["KPiPi"]
    configdict["PDFList"]["BacPIDK"]["Bd2DsPi"]["Bs2DsPi"]["2012"]["PiPiPi"]  =  configdict["PDFList"]["BacPIDK"]["Signal"]["Bs2DsPi"]["2012"]["PiPiPi"]




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
