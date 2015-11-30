from B2DXFitters import *
from B2DXFitters.WS import WS as WS
from ROOT import *
from ROOT import RooFit
from ROOT import RooWorkspace 
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc

def getExpectedValue(var,par,year,dsmode,pol,myconfigfile):
    #print var, par, year, dsmode                                                                                                                                                         
    if type(myconfigfile[var][par][year.Data()][dsmode.Data()]) == float:
        return myconfigfile[var][par][year.Data()][dsmode.Data()]
    else:
        return myconfigfile[var][par][year.Data()][dsmode.Data()][pol.Data()]

    exit(0)


def getExpectedYield(mode,year,dsmode,pol,merge, myconfigfile):
    #print mode, year, dsmode                                                                                                                                                               
    p = GeneralUtils.CheckPolarityCapital(TString(pol),False) 
    if merge == "pol":
        if type(myconfigfile["Yields"][mode][year.Data()][dsmode.Data()]) == float:
            return myconfigfile["Yields"][mode][year.Data()][dsmode.Data()]
        elif (myconfigfile["Yields"][mode][year.Data()][dsmode.Data()].has_key("Up") and myconfigfile["Yields"][mode][year.Data()][dsmode.Data()].has_key("Down")):
            return myconfigfile["Yields"][mode][year.Data()][dsmode.Data()]["Up"]+myconfigfile["Yields"][mode][year.Data()][dsmode.Data()]["Down"]
        elif myconfigfile["Yields"][mode][year.Data()][dsmode.Data()].has_key("Both"):
            return myconfigfile["Yields"][mode][year.Data()][dsmode.Data()]["Both"]
    elif merge == "year":
        
        if myconfigfile["Yields"][mode].has_key("Run1"):
            if type(myconfigfile["Yields"][mode]["Run1"][dsmode.Data()]) == float:
                return myconfigfile["Yields"][mode]["Run1"][dsmode.Data()]
            elif myconfigfile["Yields"][mode]["Run1"][dsmode.Data()].has_key(p.Data()): 
                return myconfigfile["Yields"][mode]["Run1"][dsmode.Data()][p.Data()]
            elif myconfigfile["Yields"][mode]["Run1"][dsmode.Data()].has_key("Both"):
                return myconfigfile["Yields"][mode]["Run1"][dsmode.Data()]["Both"]
        else: 
            y2011 = 0.0
            y2012 = 0.0
            if myconfigfile["Yields"][mode].has_key("2011") and myconfigfile["Yields"][mode].has_key("2012"):
                if type(myconfigfile["Yields"][mode]["2011"][dsmode.Data()]) == float:
                    y2011 =  myconfigfile["Yields"][mode]["2011"][dsmode.Data()]
                elif myconfigfile["Yields"][mode]["2011"][dsmode.Data()].has_key(p.Data()):
                    y2011 =  myconfigfile["Yields"][mode]["2011"][dsmode.Data()][p]
                elif myconfigfile["Yields"][mode]["2011"][dsmode.Data()].has_key("Both"):
                    y2011 = myconfigfile["Yields"][mode]["2011"][dsmode.Data()]["Both"]
                
                if type(myconfigfile["Yields"][mode]["2012"][dsmode.Data()]) == float:
                    y2012 =  myconfigfile["Yields"][mode]["2012"][dsmode.Data()]
                elif myconfigfile["Yields"][mode]["2012"][dsmode.Data()].has_key(p.Data()):
                    y2012 =  myconfigfile["Yields"][mode]["2012"][dsmode.Data()][p.Data()]
                elif myconfigfile["Yields"][mode]["2012"][dsmode.Data()].has_key("Both"):
                    y2012 = myconfigfile["Yields"][mode]["2012"][dsmode.Data()]["Both"]

                return y2011+y2012
    elif merge == "both":
        if myconfigfile["Yields"][mode].has_key("Run1"):
            if type(myconfigfile["Yields"][mode]["Run1"][dsmode.Data()]) == float:
                return myconfigfile["Yields"][mode]["Run1"][dsmode.Data()]
            elif myconfigfile["Yields"][mode]["Run1"][dsmode.Data()].has_key(p.Data()):
                return myconfigfile["Yields"][mode]["Run1"][dsmode.Data()][p.Data()]
            elif myconfigfile["Yields"][mode]["Run1"][dsmode.Data()].has_key("Both"):
                return myconfigfile["Yields"][mode]["Run1"][dsmode.Data()]["Both"]
        else:
            y2011 = 0.0
            y2012 = 0.0
            if myconfigfile["Yields"][mode].has_key("2011") and myconfigfile["Yields"][mode].has_key("2012"):
                if type(myconfigfile["Yields"][mode]["2011"][dsmode.Data()]) == float:
                    y2011 =  myconfigfile["Yields"][mode]["2011"][dsmode.Data()]
                elif myconfigfile["Yields"][mode]["2011"][dsmode.Data()].has_key("Up") and myconfigfile["Yields"][mode]["2011"][dsmode.Data()].has_key("Down"):
                    y2011 =  myconfigfile["Yields"][mode]["2011"][dsmode.Data()]["Up"]+myconfigfile["Yields"][mode]["2011"][dsmode.Data()]["Down"]
                elif myconfigfile["Yields"][mode]["2011"][dsmode.Data()].has_key("Both"):
                    y2011 = myconfigfile["Yields"][mode]["2011"][dsmode.Data()]["Both"]

                if type(myconfigfile["Yields"][mode]["2012"][dsmode.Data()]) == float:
                    y2012 =  myconfigfile["Yields"][mode]["2012"][dsmode.Data()]
                elif myconfigfile["Yields"][mode]["2012"][dsmode.Data()].has_key("Up") and myconfigfile["Yields"][mode]["2012"][dsmode.Data()].has_key("Down"):
                    y2012 =  myconfigfile["Yields"][mode]["2012"][dsmode.Data()]["Up"] + myconfigfile["Yields"][mode]["2012"][dsmode.Data()]["Down"]
                elif myconfigfile["Yields"][mode]["2012"][dsmode.Data()].has_key("Both"):
                    y2012 = myconfigfile["Yields"][mode]["2012"][dsmode.Data()]["Both"]
                return y2011+y2012

    else:
        if year != "":
            if type ( myconfigfile["Yields"][mode][year.Data()][dsmode.Data()] ) == float:
                return myconfigfile["Yields"][mode][year.Data()][dsmode.Data()]
            elif myconfigfile["Yields"][mode][year.Data()][dsmode.Data()].has_key(pol.Data):
                return myconfigfile["Yields"][mode][year.Data()][dsmode.Data()][pol.Data]
        elif year == "run1":
            print "[ERROR] Merge option tells that polarities should be merged, while magnet polarity is %s"%(pol)
            exit(0)
        else:
            print "[ERROR] Wrong year: %s"%(year)
            exit(0)

def setConstantIfSoConfigured(var, par, mode, dmode, pol, myconfigfile):
    if type(myconfigfile[par][mode]["Fixed"]) == bool:
        if myconfigfile[par][mode]["Fixed"] == True :
            var.setConstant()
            print "[INFO] Parameter: %s set to be constant with value %lf"%(var.GetName(),var.getValV())
        else:
            print "[INFO] Parameter: %s floats in the fit"%(var.GetName())
    elif myconfigfile[par][mode]["Fixed"].has_key(dmode):
        if myconfigfile[par][mode]["Fixed"][dmode]:
            var.setConstant()
            print "[INFO] Parameter: %s set to be constant with value %lf"%(var.GetName(),var.getValV())
        else:
            print "[INFO] Parameter: %s floats in the fit"%(var.GetName())
    else:
        print "[INFO] Parameter: %s floats in the fit"%(var.GetName())

def getObservables (MDSettings, workData, toys, debug):

    if (not toys ):
        observables = MDSettings.GetObsSet(False,True,True,True,True, True)
    else:
        observables = MDSettings.GetObsSet(False,True,True,True,False, False)

    if MDSettings.CheckTagVar() == True:
        tagDecCombName = TString("tagDecComb")
        tagDecComb = GeneralUtils.GetCategory(workData, tagDecCombName, debug)
        tagOmegaCombName= TString("tagOmegaComb")
        tagOmegaComb = GeneralUtils.GetObservable(workData, tagOmegaCombName, debug)

        observables.add(tagDecComb)
        observables.add(tagOmegaComb)

    if debug:
        observables.Print("v")

    return observables

def readVariables(myconfigfile,label, prefix, workInt, sm, merge, bound, debug):

    t = TString("_")
    variables = []

    names = []

    for i in range(0,bound):

        labelTS = TString(label)
        print labelTS
        if myconfigfile.has_key(label):
            if myconfigfile[label]["type"] != "RooKeysPdf":
                var = myconfigfile[label]
                for v in var:
                    if v != "type" and v != "scaleSigma" and v != "components" and v!= "name" and v!= "decay":
                        lTS = TString(label)
                        
                        year = myconfigfile[label][v]
                        for y in year:
                            if y != "Fixed":
                                mode = myconfigfile[label][v][y]
                                for m in mode:
                                    pol = myconfigfile[label][v][y][m]
                                    if type(pol) == float:
                                        pol = ["both"]

                                    for p in pol:
                                        pp = GeneralUtils.CheckPolarity(TString(p),False) 
                                        yy = GeneralUtils.CheckDataYear(TString(y),False)
                                        mm = GeneralUtils.CheckDMode(TString(m),False)
                                        if mm == "":
                                            mm = GeneralUtils.CheckKKPiMode(TString(m),False)
                                        if m == "All":
                                            mm = "all"
                                        if yy == "run1": 
                                            yr2 = TString("Run1")
                                        else:
                                            yr2 = TString(y)
                                        if pp == "both":
                                            p2 = TString("Both")
                                        else:
                                            p2 = TString(p) 
                                        t = TString("_")
                                        ssmm = t + pp + t + mm + t + yy

                                        nameVar = TString(prefix) + t + v + ssmm
                                        
                                        if nameVar in names:
                                            continue
                                        else:
                                            names.append(nameVar)
                                        expectedValue = getExpectedValue(label,v,yr2,TString(m),p2,myconfigfile)
                                        vTS = TString(v)
                                        if vTS.Contains("frac"):
                                            boundDown = 0.0
                                            boundUp = 1.0
                                        elif vTS.Contains("mean"):
                                            boundDown = expectedValue-50.0;
                                            boundUp = expectedValue+50.0;
                                        else:
                                            if expectedValue < 0.0:
                                                boundUp = 0.0
                                                boundDown = expectedValue*2.0
                                            else:
                                                boundDown = 0.0
                                                boundUp =expectedValue*2.0

                                        if myconfigfile[label].has_key("scaleSigma") and ( v == "sigma1" or v == "sigma2"):
                                            f1 =  myconfigfile[label]["scaleSigma"][yr2.Data()]["frac1"]
                                            f2 =  myconfigfile[label]["scaleSigma"][yr2.Data()]["frac2"]

                                            if v == "sigma1":
                                                expectedValue2 = getExpectedValue(label,"sigma2",yr2,TString(m),p2,myconfigfile)
                                            elif v == "sigma2":
                                                expectedValue2 = getExpectedValue(label,"sigma1",yr2,TString(m),p2,myconfigfile)

                                            oldvalue = expectedValue
                                            if expectedValue>expectedValue2:
                                                f = f1
                                            else:
                                                f = f2
                                            expectedValue = expectedValue*f
                                            print "[INFO] Change value %s to %s = %s * %s"%(str(oldvalue), str(expectedValue), str(oldvalue), str(f))
                                            
                                        variables.append(WS(workInt, RooRealVar(nameVar.Data() , nameVar.Data(), expectedValue,  boundDown, boundUp)))
                                        setConstantIfSoConfigured(variables[variables.__len__()-1], label, v, m, p, myconfigfile)
        #else:
        #    print "[ERROR] Cannot find the label: %s. Please specify in config file"%(label)
        #    exit(0)

    return workInt 

def getPDFNameFromConfig(myconfigfile, key, var, pdfcontainer):

    t = TString("_") 
    names = [] 
    if myconfigfile.has_key(key):
        if myconfigfile[key].has_key("name"):
            year = myconfigfile[key]["name"]
            print year
            for y in year:
                mode = myconfigfile[key]["name"][y]
                print mode
                for m in mode:
                    pol = myconfigfile[key]["name"][y][m]
                    print pol 
                    if type(pol) == float:
                        pol = ["both"]
                    for p in pol:
                        pp = GeneralUtils.CheckPolarity(TString(p),False)
                        yy = GeneralUtils.CheckDataYear(TString(y),False)
                        mm = GeneralUtils.CheckDMode(TString(m),False)
                        if mm == "":
                            mm = GeneralUtils.CheckKKPiMode(TString(m),False)

                        if myconfigfile[key]["name"][y][m] == "Both" or myconfigfile[key]["name"][y][m] == "Up" or myconfigfile[key]["name"][y][m] == "Down":
                            namepdf = myconfigfile[key]["name"][y][m][p]
                        else:
                            namepdf = myconfigfile[key]["name"][y][m]
                        name = var + t + pp + t + mm + t + yy     
                        if name in names:
                            continue
                        else:
                            names.append(name)
                        pdfcontainer = GeneralUtils.AddToList2D(pdfcontainer, namepdf, name)

    return pdfcontainer 

def getType(myconfigfile, key):
    if myconfigfile.has_key(key):
        if myconfigfile[key].has_key("type"):
            return  TString(myconfigfile[key]["type"])
    return  TString("None")

def getPIDKComponents(myconfigfile, key, component):
    if myconfigfile.has_key(key):
        if myconfigfile[key].has_key("components"):
            if myconfigfile[key]["components"][component] == True:
                return "true"
            else:
                return "false"
    return "none"

def getSigOrCombPDF(myconfigfile,keys, typemode, work, workInt,sm, merge, bound,dim, obs, debug):

    beautyMass = obs[0]
    charmMass = obs[1]
    bacPIDK = obs[2]
    if dim > 0:
        prefix1 = typemode+"_"+beautyMass.GetName()
        workInt = readVariables(myconfigfile, keys[0], prefix1, workInt, sm, merge, bound, debug)
    if dim > 1:
        charmMass = obs[1]
        prefix2 = typemode+"_"+charmMass.GetName()
        workInt = readVariables(myconfigfile, keys[1], prefix2, workInt, sm, merge, bound, debug)
    if dim > 2:
        bacPIDK = obs[2]
        prefix3 = typemode+"_"+bacPIDK.GetName()
        workInt = readVariables(myconfigfile, keys[2], prefix3, workInt, sm, merge, bound, debug)

    typeBs = getType(myconfigfile,keys[0])
    typeDs = getType(myconfigfile,keys[1])
    typePIDK = getType(myconfigfile,keys[2])

    types = GeneralUtils.GetList(typeBs, typeDs, typePIDK)

    if dim>2: 
        nameKaon = getPIDKComponents(myconfigfile, keys[2], "Kaon")
        namePion = getPIDKComponents(myconfigfile, keys[2], "Pion")
        nameProton = getPIDKComponents(myconfigfile, keys[2], "Proton")
        pidkNames = GeneralUtils.GetList(nameKaon, namePion, nameProton)
    else:
        pidkNames = GeneralUtils.GetList(TString("None"), TString("None"), TString("None"))
    decay =  TString(myconfigfile["Decay"])
    
    combEPDF = []
    for i in range(0,bound):
        pdfNames = GeneralUtils.GetList2D(TString("pdf_names"), TString("pdf_keys"));
        
        if dim > 0:
            pdfNames = getPDFNameFromConfig(myconfigfile, keys[0], prefix1, pdfNames )
        if dim > 1:
            pdfNames = getPDFNameFromConfig(myconfigfile, keys[1], prefix2, pdfNames )
        if dim > 2:
            pdfNames = getPDFNameFromConfig(myconfigfile, keys[2], prefix3, pdfNames )

        if debug:    
            GeneralUtils.printList2D(pdfNames)
        EPDF = Bs2Dsh2011TDAnaModels.build_SigOrCombo(beautyMass,charmMass, bacPIDK, work, workInt, sm[i], TString(typemode), 
                                                      merge, decay, types, pdfNames, pidkNames, dim, debug)
        combEPDF.append(WS(workInt,EPDF))

    return combEPDF, workInt


#------------------------------------------------------------------------------                                                                                                           
def setBs2DsXParameters(myconfigfile,workInt,sm, merge, bound, beautyMass,debug):
    
    if myconfigfile.has_key("Bd2Ds(st)XShape"):
        if myconfigfile["Bd2Ds(st)XShape"].has_key("decay"):
            decay = myconfigfile["Bd2Ds(st)XShape"]["decay"]
        else:
            decay = "Bd2DsX"
        if myconfigfile["Bd2Ds(st)XShape"].has_key("type"):
            shapeType = myconfigfile["Bd2Ds(st)XShape"]["type"]
        else:
            shapeType = "Unknown"
            
        if shapeType == "ShiftedSignal":
            prefix1 = decay+"_"+beautyMass.GetName()
            workInt = readVariables(myconfigfile, "Bd2Ds(st)XShape", prefix1, workInt, sm, merge, bound, debug)
            
    return workInt
