from B2DXFitters import *
from ROOT import *

class Translator:
    def __init__( self, myconfigfile, name , full) :
        md = MDFitterSettings(name,name)
        if myconfigfile.has_key("dataName"):
            md.SetConfigFile(myconfigfile["dataName"])

        if myconfigfile.has_key("BasicVariables"):
            names = myconfigfile["BasicVariables"]
            for name in names:
                if  name == "BeautyMass":
                    md.SetMassB(myconfigfile["BasicVariables"][name]["InputName"], name,
                                myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif name == "CharmMass":
                    md.SetMassD(myconfigfile["BasicVariables"][name]["InputName"], name,
                                myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif name == "BeautyTime":
                    md.SetTime(myconfigfile["BasicVariables"][name]["InputName"], name,
                               myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif name == "BeautyTimeErr":
                    md.SetTerr(myconfigfile["BasicVariables"][name]["InputName"], name,
                               myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif name == "BacP":
                    md.SetMom(myconfigfile["BasicVariables"][name]["InputName"], name,
                               myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif name == "BacPT":
                    md.SetTrMom(myconfigfile["BasicVariables"][name]["InputName"], name,
                                myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif name == "BacPIDK":
                    md.SetPIDK(myconfigfile["BasicVariables"][name]["InputName"], name,
                               myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif name == "nTracks":
                    md.SetTracks(myconfigfile["BasicVariables"][name]["InputName"], name,
                                myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif name == "BacCharge":
                    md.SetID(myconfigfile["BasicVariables"][name]["InputName"], name,
                                myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif name == "BDTG":
                    md.SetBDTG(myconfigfile["BasicVariables"][name]["InputName"], name,
                               myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif "TagDec" in name :
                    md.AddTagVar(myconfigfile["BasicVariables"][name]["InputName"], name,
                                 myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif "Mistag" in name :
                    md.AddTagOmegaVar(myconfigfile["BasicVariables"][name]["InputName"], name,
                                      myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])

        else:
            print "[ERROR] You didn't defined any observable!"
            exit(0) 

        if myconfigfile.has_key('TaggingCalibration'):
            tags = ["OS", "SS"]
            for tag in tags:
                if myconfigfile["TaggingCalibration"].has_key(tag):
                    use = True
                    if myconfigfile["TaggingCalibration"][tag].has_key("use"):
                        use = myconfigfile["TaggingCalibration"][tag]["use"] 
                    md.SetCalibration(tag,
                                      myconfigfile["TaggingCalibration"][tag]["p0"],
                                      myconfigfile["TaggingCalibration"][tag]["p1"],
                                      myconfigfile["TaggingCalibration"][tag]["average"],
                                      use)
            
            

        if full == True:            
            if myconfigfile.has_key("ObtainPIDTemplates"):
                size1 = len(myconfigfile["ObtainPIDTemplates"]["Variables"])
                size2 = len(myconfigfile["ObtainPIDTemplates"]["Bins"])
                if size1 != size2:
                    print '[ERROR] Size of variables for PID weighting is not equal to size bins. Please check if you set a number of bins for each variable'
                    exit(0)
                md.SetWeightingDim(size1)
                for var in myconfigfile["ObtainPIDTemplates"]["Variables"]:
                    md.AddPIDWeightVar(var)
                for bin in myconfigfile["ObtainPIDTemplates"]["Bins"]:
                    md.AddPIDWeightBin(bin)
            
            if myconfigfile.has_key('Calibrations'):
                year = myconfigfile["Stripping"]
                particle = ["Pion","Kaon","Proton","Combinatorial"]
            
                for y in year:
                    for p in particle:
                    
                        if myconfigfile["Calibrations"][y].has_key(p):
                            polarity = myconfigfile["Calibrations"][y][p]
                            for Pol in polarity:
                                if Pol == "Down":
                                    pol = TString("down")
                                elif Pol == "Up":
                                    pol = TString("up")
                                else:
                                    pol = TString("unknown")
                                
                                strip = myconfigfile["Stripping"][y]
                                dataName = ""
                                workName = "" 
                                pidVarName = ""
                                weightName = ""
                                var1Name = ""
                                var2Name = ""
                                fileName = myconfigfile["Calibrations"][y][p][Pol]["FileName"]
                                if  myconfigfile["Calibrations"][y][p][Pol].has_key("Type"):
                                    t = myconfigfile["Calibrations"][y][p][Pol]["Type"]
                                    if t == "Special" or fileName == "":
                                        if myconfigfile["Calibrations"][y][p][Pol].has_key("WorkName"):
                                            workName = myconfigfile["Calibrations"][y][p][Pol]["WorkName"]
                                        if myconfigfile["Calibrations"][y][p][Pol].has_key("DataName"):
                                            dataName = myconfigfile["Calibrations"][y][p][Pol]["DataName"]
                                        if myconfigfile["Calibrations"][y][p][Pol].has_key("PIDVarName"):
                                            pidVarName = myconfigfile["Calibrations"][y][p][Pol]["PIDVarName"]
                                        if myconfigfile["Calibrations"][y][p][Pol].has_key("WeightName"):
                                            weightName = myconfigfile["Calibrations"][y][p][Pol]["WeightName"]
                                        if myconfigfile["Calibrations"][y][p][Pol].has_key("Variables"):
                                            var1Name = myconfigfile["Calibrations"][y][p][Pol]["Variables"][0]
                                            var2Name = myconfigfile["Calibrations"][y][p][Pol]["Variables"][1]
                                        if p == "Combinatorial":
                                            if ( fileName == "" ):
                                                md.SetPIDComboShapeFor5Modes()
                                else:
                                    t = "" 
                             
                                md.SetCalibSample(fileName, workName, dataName, p, y, pol, strip, t, var1Name, var2Name, pidVarName, weightName)


        if myconfigfile.has_key('IntegratedLuminosity'):
            if myconfigfile["IntegratedLuminosity"].has_key("2011"):
                md.SetLum("2011", myconfigfile["IntegratedLuminosity"]["2011"]["Down"], myconfigfile["IntegratedLuminosity"]["2011"]["Up"])
            if myconfigfile["IntegratedLuminosity"].has_key("2012"):
                md.SetLum("2012", myconfigfile["IntegratedLuminosity"]["2012"]["Down"], myconfigfile["IntegratedLuminosity"]["2012"]["Up"])


        if myconfigfile.has_key('AdditionalVariables'):
            size = len(myconfigfile['AdditionalVariables'])
            for t in myconfigfile['AdditionalVariables']:
                if myconfigfile['AdditionalVariables'][t].has_key('OutputName'):
                    md.AddVar(myconfigfile['AdditionalVariables'][t]["InputName"],
                              myconfigfile['AdditionalVariables'][t]["OutputName"],
                              myconfigfile["AdditionalVariables"][t]["Range"][0],
                              myconfigfile["AdditionalVariables"][t]["Range"][1])
                else:
                    md.AddVar(myconfigfile['AdditionalVariables'][t]["InputName"],
                              t,
                              myconfigfile["AdditionalVariables"][t]["Range"][0],
                              myconfigfile["AdditionalVariables"][t]["Range"][1])

        
        if myconfigfile.has_key('AdditionalCuts'):
            Dmodes = ["All","KKPi","KPiPi","PiPiPi","NonRes","KstK","PhiPi","HHHPi0"]
            i = 0
            for Dmode in Dmodes:
                if myconfigfile['AdditionalCuts'].has_key(Dmode):
                    if myconfigfile['AdditionalCuts'][Dmode].has_key("Data"):
                        md.SetDataCuts(Dmode, myconfigfile['AdditionalCuts'][Dmode]['Data'])
                    if myconfigfile['AdditionalCuts'][Dmode].has_key("MC"):
                        md.SetMCCuts(Dmode, myconfigfile['AdditionalCuts'][Dmode]['MC'])
                    if myconfigfile['AdditionalCuts'][Dmode].has_key("MCID"):
                        md.SetIDCut(Dmode, myconfigfile['AdditionalCuts'][Dmode]['MCID'])
                    if myconfigfile['AdditionalCuts'][Dmode].has_key("MCTRUEID"):
                        md.SetTRUEIDCut(Dmode, myconfigfile['AdditionalCuts'][Dmode]['MCTRUEID'])
                    if myconfigfile['AdditionalCuts'][Dmode].has_key("BKGCAT"):
                        md.SetBKGCATCut(Dmode, myconfigfile['AdditionalCuts'][Dmode]['BKGCAT'])
                    if myconfigfile['AdditionalCuts'][Dmode].has_key("DsHypo"):
                        md.SetDsHypoCut(Dmode, myconfigfile['AdditionalCuts'][Dmode]['DsHypo'])

        if myconfigfile.has_key('WeightingMassTemplates'):
            md.SetMassWeighting(False)
            if myconfigfile["WeightingMassTemplates"].has_key("Shift"):
                shift = myconfigfile["WeightingMassTemplates"]["Shift"] 
                for s in shift:
                    print myconfigfile["WeightingMassTemplates"]["Shift"][s]
                    md.SetMassShift(s,myconfigfile["WeightingMassTemplates"]["Shift"][s])
                
            hists = myconfigfile["WeightingMassTemplates"]
            for hist in hists:
                if hist != "Shift":
                    if hist != "RatioDataMC":
                        md.SetMassWeighting(True)
                    file2011 = ""
                    file2012 = ""
                    if myconfigfile["WeightingMassTemplates"][hist].has_key("FileLabel"):
                        if myconfigfile["WeightingMassTemplates"][hist]["FileLabel"].has_key("2011"):
                            file2011 = myconfigfile["WeightingMassTemplates"][hist]["FileLabel"]["2011"]
                        if myconfigfile["WeightingMassTemplates"][hist]["FileLabel"].has_key("2012"):
                            file2012 = myconfigfile["WeightingMassTemplates"][hist]["FileLabel"]["2012"]
                        if myconfigfile["WeightingMassTemplates"][hist]["FileLabel"].has_key("2011") == False and myconfigfile["WeightingMassTemplates"][hist]["FileLabel"].has_key("2012") == False: 
                            file2011 = myconfigfile["WeightingMassTemplates"][hist]["FileLabel"]
                            file2012 = file2011
                    if myconfigfile["WeightingMassTemplates"][hist].has_key("Var"):
                        var = myconfigfile["WeightingMassTemplates"][hist]["Var"]
                    if myconfigfile["WeightingMassTemplates"][hist].has_key("HistName"):
                        histName = myconfigfile["WeightingMassTemplates"][hist]["HistName"]        
                    md.SetPIDProperties(hist, file2011, file2012, var[0], var[1], histName)
                        #print hist, file2011, file2012, var[0], var[1], histName 
            if myconfigfile["WeightingMassTemplates"].has_key("RatioDataMC"):
                md.SetRatioDataMC(True)

        if myconfigfile.has_key('DsChildrenPrefix'):
            if myconfigfile['DsChildrenPrefix'].has_key("Child1"):
                md.SetChildPrefix(0,myconfigfile['DsChildrenPrefix']['Child1'])
            if myconfigfile['DsChildrenPrefix'].has_key("Child2"):
                md.SetChildPrefix(1,myconfigfile['DsChildrenPrefix']['Child2'])
            if myconfigfile['DsChildrenPrefix'].has_key("Child3"):
                md.SetChildPrefix(2,myconfigfile['DsChildrenPrefix']['Child3'])
            
        self.mdfit = md
        
    def getConfig( self ) :
        return self.mdfit
