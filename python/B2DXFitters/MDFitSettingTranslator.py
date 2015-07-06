from B2DXFitters import *
from ROOT import *

class Translator:
    def __init__( self, myconfigfile, name ) :
        md = MDFitterSettings(name,name)

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
                elif ( name == "TagDecOS" or name == "TagDecSS"):
                    md.AddTagVar(myconfigfile["BasicVariables"][name]["InputName"], name,
                                 myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])
                elif ( name  == "MistagOS" or name == "MistagSS"):
                    md.AddTagOmegaVar(myconfigfile["BasicVariables"][name]["InputName"], name,
                                      myconfigfile["BasicVariables"][name]["Range"][0], myconfigfile["BasicVariables"][name]["Range"][1])

        else:
            print "[ERROR] You didn't defined any observable!"
            exit(0) 

        if myconfigfile.has_key('TaggingCalibration'):
            tags = ["OS","SS"]
            for tag in tags:
                if myconfigfile["TaggingCalibration"].has_key(tag):
                    md.AddCalibration(myconfigfile["TaggingCalibration"][tag]["p0"],
                                      myconfigfile["TaggingCalibration"][tag]["p1"],
                                      myconfigfile["TaggingCalibration"][tag]["average"])

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
            if myconfigfile["Calibrations"].has_key("Pion"):
                md.SetCalibPion(myconfigfile["Calibrations"]["Pion"]["FileNameUp"],
                                myconfigfile["Calibrations"]["Pion"]["FileNameDown"],
                                myconfigfile["Calibrations"]["Pion"]["WorkName"])
            
            if myconfigfile["Calibrations"].has_key("Kaon"):
                md.SetCalibKaon(myconfigfile["Calibrations"]["Kaon"]["FileNameUp"],
                                myconfigfile["Calibrations"]["Kaon"]["FileNameDown"],
                                myconfigfile["Calibrations"]["Kaon"]["WorkName"])

            if myconfigfile["Calibrations"].has_key("Proton"):
                md.SetCalibProton(myconfigfile["Calibrations"]["Proton"]["FileNameUp"],
                                  myconfigfile["Calibrations"]["Proton"]["FileNameDown"],
                                  myconfigfile["Calibrations"]["Proton"]["WorkName"])

            if myconfigfile["Calibrations"].has_key("Combinatorial"):
                md.SetCalibCombo(myconfigfile["Calibrations"]["Combinatorial"]["FileNameUp"],
                                 myconfigfile["Calibrations"]["Combinatorial"]["FileNameDown"],
                                 myconfigfile["Calibrations"]["Combinatorial"]["WorkName"])


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
            md.SetMassWeighting(True) 
            if myconfigfile["WeightingMassTemplates"].has_key("Variables"):
                variables = myconfigfile["WeightingMassTemplates"]["Variables"]
                for var in variables:
                    md.AddWeightingMassVar(var)
            if myconfigfile["WeightingMassTemplates"].has_key('PIDProton'):
                md.SetPIDProton(myconfigfile["WeightingMassTemplates"]['PIDProton'])
            if myconfigfile["WeightingMassTemplates"].has_key('PIDBach'):
                md.SetPIDBach(myconfigfile["WeightingMassTemplates"]['PIDBach'])
            if myconfigfile["WeightingMassTemplates"].has_key('PIDChild'):
                md.SetPIDChild(myconfigfile["WeightingMassTemplates"]['PIDChild'])

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
