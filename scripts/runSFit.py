#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a toy MC fit for the CP asymmetry observables        #
#   in Bs -> Ds K                                                             #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python runBs2DsKCPAsymmObsFitterOnData.py [-d -s]                      #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 14 / 06 / 2011                                                    #
#   Author: Manuel Schiller                                                   #
#   Author: Agnieszka Dziurda                                                 #
#   Author: Vladimir Vava Gligorov                                            #
# --------------------------------------------------------------------------- #

# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.
# make sure the environment is set up properly
""":"
if test -n "$CMTCONFIG" \
         -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersDict.so \
	 -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersLib.so; then
    # all ok, software environment set up correctly, so don't need to do 
    # anything
    true
else
    if test -n "$CMTCONFIG"; then
	# clean up incomplete LHCb software environment so we can run
	# standalone
        echo Cleaning up incomplete LHCb software environment.
        PYTHONPATH=`echo $PYTHONPATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export PYTHONPATH
        LD_LIBRARY_PATH=`echo $LD_LIBRARY_PATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export LD_LIBRARY_PATH
        exec env -u CMTCONFIG -u B2DXFITTERSROOT "$0" "$@"
    fi
    # automatic set up in standalone build mode
    if test -z "$B2DXFITTERSROOT"; then
        cwd="$(pwd)"
        # try to find from where script is executed, use current directory as
        # fallback
        tmp="$(dirname $0)"
        tmp=${tmp:-"$cwd"}
        # convert to absolute path
        tmp=`readlink -f "$tmp"`
        # move up until standalone/setup.sh found, or root reached
        while test \( \! -d "$tmp"/standalone \) -a -n "$tmp" -a "$tmp"\!="/"; do
            tmp=`dirname "$tmp"`
        done
        if test -d "$tmp"/standalone; then
            cd "$tmp"/standalone
            . ./setup.sh
        else
            echo `basename $0`: Unable to locate standalone/setup.sh
            exit 1
        fi
	    cd "$cwd"
        unset tmp
        unset cwd
    fi
fi

# figure out which custom allocators are available
# prefer jemalloc over tcmalloc
for i in libjemalloc libtcmalloc; do
    for j in `echo "$LD_LIBRARY_PATH" | tr ':' ' '` \
	    /usr/local/lib /usr/lib /lib; do
        for k in `find "$j" -name "$i"'*.so.?' | sort -r`; do
            if test \! -e "$k"; then
	        continue
	    fi
	    echo adding $k to LD_PRELOAD
	    if test -z "$LD_PRELOAD"; then
	        export LD_PRELOAD="$k"
	        break 3
	    else
	        export LD_PRELOAD="$LD_PRELOAD":"$k"
	        break 3
	    fi
	done
    done
done

# set batch scheduling (if schedtool is available)
schedtool="`which schedtool 2>/dev/zero`"
if test -n "$schedtool" -a -x "$schedtool"; then
    echo "enabling batch scheduling for this job (schedtool -B)"
    schedtool="$schedtool -B -e"
else
    schedtool=""
fi

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((2048 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
import B2DXFitters
import ROOT
from B2DXFitters import *
from ROOT import *

from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc

gROOT.SetBatch()

AcceptanceFunction       =  'PowLawAcceptance'#BdPTAcceptance'  # None/BdPTAcceptance/DTAcceptanceLHCbNote2007041

# MISCELLANEOUS
bName = 'B_{s}'

#------------------------------------------------------------------------------                                                                                                                
def setConstantIfSoConfigured(var,myconfigfile) :
    if var.GetName() in myconfigfile["constParams"] : 
        var.setConstant()
        print "[INFO] Parameter: %s set to be constant with value %lf"%(var.GetName(),var.getValV())
    else:
        print "[INFO] Parameter: %s floats in the fit"%(var.GetName())
        print "[INFO]   ",var.Print() 

#------------------------------------------------------------------------------
def getCPparameters(decay,myconfigfile):

    from B2DXFitters import cpobservables

    if decay.Contains("K"):
        argLf = myconfigfile["StrongPhase"]-myconfigfile["WeakPhase"]
        argLbarfbar = myconfigfile["StrongPhase"]+myconfigfile["WeakPhase"]
        modLf = myconfigfile["ModLf"]
        ACPobs = cpobservables.AsymmetryObservables(argLf,argLbarfbar,modLf)
        ACPobs.printtable()
        Cf    = ACPobs.Cf()
        Sf    = ACPobs.Sf()
        Df    = ACPobs.Df()
        Sfbar = ACPobs.Sfbar()
        Dfbar = ACPobs.Dfbar()
    else:
        Cf    = 1.0
        Sf    = 0.0   
        Df    = 0.0
        Sfbar = 0.0
        Dfbar = 0.0
    

    limit = [-3.0,3.0]
    if myconfigfile.has_key("CPlimit"):
        limit[0] = myconfigfile["CPlimit"]["lower"]
        limit[1] = myconfigfile["CPlimit"]["upper"] 

    sigC = RooRealVar('C_%s'%(decay.Data()), 'C coeff.', Cf, limit[0], limit[1])
    sigS = RooRealVar('S_%s'%(decay.Data()), 'S coeff.', Sf, limit[0], limit[1])
    sigD = RooRealVar('D_%s'%(decay.Data()), 'D coeff.', Df, limit[0], limit[1])
    sigCbar = RooRealVar('Cbar_%s'%(decay.Data()), 'Cbar coeff.', Cf, limit[0], limit[1])
    sigSbar = RooRealVar('Sbar_%s'%(decay.Data()), 'Sbar coeff.', Sfbar, limit[0], limit[1])
    sigDbar = RooRealVar('Dbar_%s'%(decay.Data()), 'Dbar coeff.', Dfbar, limit[0], limit[1])
    setConstantIfSoConfigured(sigC,myconfigfile)
    setConstantIfSoConfigured(sigS,myconfigfile)
    setConstantIfSoConfigured(sigD,myconfigfile)
    setConstantIfSoConfigured(sigCbar,myconfigfile)
    setConstantIfSoConfigured(sigSbar,myconfigfile)
    setConstantIfSoConfigured(sigDbar,myconfigfile)
    
    return sigC, sigS, sigD, sigCbar, sigSbar, sigDbar


def getTagEff(myconfig, ws, mdSet, par):
    numTag = mdSet.GetNumTagVar()
    tagList = []
    for i in range(0,numTag):
        if mdSet.CheckUseTag(i) == True:
            tagList.append(str(mdSet.GetTagMatch(i)))

    from B2DXFitters.WS import WS as WS
    tagEffList = RooArgList()
    tagEffSig = [] 
    tagEff = 0.0 
    
    if tagList.__len__() == 1:
        if myconfig["TaggingCalibration"].has_key(tagList[0]): 
            if myconfig["TaggingCalibration"][tagList[0]].has_key(par):
                tagEff = myconfig["TaggingCalibration"][tagList[0]][par]
                tagEffSig.append(WS(ws,RooRealVar(par+'_'+tagList[0], 'Signal tagging efficiency', tagEff, 0.0, 1.0))) 
                setConstantIfSoConfigured(tagEffSig[0],myconfig)
                tagEffList.add(tagEffSig[0])
            else:
                print "[ERROR] Tagging efficiency is unknown. Please check the config file." 
                exit(0) 
        else:
            print "[ERROR] Tagging efficiency is unknown. Please check the config file."
            exit(0)
    elif tagList.__len__()  == 2:
        tagEff0 = myconfig["TaggingCalibration"][tagList[0]][par]
        tagEff1 = myconfig["TaggingCalibration"][tagList[1]][par]
        tagList.append("Both")
        tagValue = [tagEff0 - tagEff0*tagEff1,  tagEff1 - tagEff0*tagEff1, tagEff0*tagEff1] 
        i = 0 
        for tag in tagList:
            tagEffSig.append(WS(ws,RooRealVar(par+'_'+tag, 'Signal tagging efficiency', tagValue[i], 0.0, 1.0)))
            s = tagEffSig.__len__()
            setConstantIfSoConfigured(tagEffSig[s-1],myconfig)
            tagEffList.add(tagEffSig[s-1]) 
            i = i+1
    else:
        print "[ERROR] More than two taggers are not supported"
        exit(0) 
    return tagEffList, ws 


def getCalibratedMistag(myconfig, ws, mdSet, mistag, par):
    numTag = mdSet.GetNumTagVar()
    tagList = []
    for i in range(0,numTag):
        if mdSet.CheckUseTag(i) == True:
            tagList.append(str(mdSet.GetTagMatch(i)))

    from B2DXFitters.WS import WS as WS
    p0 = []
    p1 = []
    av = []
    
    mistagCalibList = RooArgList()
    mistagCalib = []
    print tagList 
    if tagList.__len__()  == 2:
        tagList.append("Both") 

    tagNum = mdSet.CheckNumUsedTag()
    numOfTemp = pow(2,tagNum)-1;
    
    for i in range(0,numOfTemp):
        name = par+'_'+str(tagList[i])
        p0.append(WS(ws,RooRealVar('p0_'+str(name), 'p0_B_'+str(name), myconfig["TaggingCalibration"][tagList[i]]["p0"], 0.0, 0.5)))                        
        p1.append(WS(ws,RooRealVar('p1_'+str(name), 'p1_B_'+str(name), myconfig["TaggingCalibration"][tagList[i]]["p1"], 0.5, 1.5)))                 
        av.append(WS(ws,RooRealVar('average_'+str(name), 'av_B_'+str(name), myconfig["TaggingCalibration"][tagList[i]]["average"], 0.0, 1.0)))
        s = p0.__len__()
        setConstantIfSoConfigured(p0[i],myconfig)
        setConstantIfSoConfigured(p1[i],myconfig)
        setConstantIfSoConfigured(av[i],myconfig)
        mistagCalib.append(MistagCalibration("mistagCalib_"+str(name), "mistagCalib_"+str(name), mistag, p0[i], p1[i], av[i]))
        mistagCalibList.add(mistagCalib[i])

    return mistagCalibList, ws


#------------------------------------------------------------------------------
def runSFit(debug, wsname,
            pereventmistag, pereventterr, 
            toys, pathName, treeName,
            configName, scan, 
            binned, plotsWeights, 
            sample, mode, year, merge, unblind  ) :

    from B2DXFitters import taggingutils, cpobservables
    # Get the configuration file
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option] 
    print "=========================================================="
    
    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation','WynnEpsilon')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('maxSteps','1000')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('minSteps','0')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','21Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)

    # Reading data set
    #-----------------------
    #plotSettings = PlotSettings("plotSettings","plotSettings", TString(dirPlot), extPlot , 100, True, False, True)
    #plotSettings.Print("v")
    #exit(0)                                                                                                                                                                                       
    from B2DXFitters.MDFitSettingTranslator import Translator
    mdt = Translator(myconfigfile,"MDSettings",False)
    MDSettings = mdt.getConfig()
    MDSettings.Print("v")

    workspace =[]
    workspaceW = []

    from B2DXFitters.WS import WS as WS
    ws = RooWorkspace("intWork","intWork")

    decay = TString(myconfigfile["Decay"]) 
    hypo = ""

    workspace.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, 
                                                    TString(sample), TString(mode), TString(year), TString(hypo), merge, 
                                                    False, toys, False, False, False, debug))
    workspaceW.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, 
                                                     TString(sample), TString(mode), TString(year), TString(hypo), merge,
                                                     True, toys, False, False, False, debug))
        
    workspace[0].Print()
    
    #exit(0) 
    zero = RooConstVar('zero', '0', 0.)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)
                     
    # Data set
    #-----------------------
    nameData = TString("dataSet_time")
    
    data = GeneralUtils.GetDataSet(workspace[0],   nameData, debug)
    dataWA = GeneralUtils.GetDataSet(workspaceW[0],   nameData, debug)
    nEntries = dataWA.numEntries()
                                                    
    dataWA.Print("v")
    obs = dataWA.get()
    time = obs.find(MDSettings.GetTimeVarOutName().Data())
    terr = obs.find(MDSettings.GetTerrVarOutName().Data())
    id = obs.find(MDSettings.GetIDVarOutName().Data())
    tag = obs.find("tagDecComb")
    mistag = obs.find("tagOmegaComb")
    mistag.setRange(0, 0.5)
    observables = RooArgSet(time,tag,id)
    if plotsWeights:
        name = TString("sfit")
        obs2 = data.get()
        weight2 = obs2.find("sWeights")
        swpdf = GeneralUtils.CreateHistPDF(data, weight2, name, 100, debug)
        GeneralUtils.SaveTemplate(data, swpdf, weight2, name)
        exit(0)

    # Physical parameters
    #-----------------------
        
    gammas = RooRealVar('Gammas_%s'%decay.Data(), '%s average lifetime' % bName, myconfigfile["Gammas"], 0., 5., 'ps^{-1}')
    setConstantIfSoConfigured(gammas,myconfigfile)
    deltaGammas = RooRealVar('deltaGammas_%s'%decay.Data(), 'Lifetime difference', myconfigfile["DeltaGammas"], -1., 1., 'ps^{-1}')
    setConstantIfSoConfigured(deltaGammas,myconfigfile)
    
    deltaMs = RooRealVar('DeltaMs_%s'%decay.Data(), '#Delta m_{s}', myconfigfile["DeltaMs"], 1., 30., 'ps^{-1}')
    deltaMs.setError(0.5)
    setConstantIfSoConfigured(deltaMs,myconfigfile)
    
    # Decay time acceptance model
    # ---------------------------

    print "[INFO] Acceptance model: splines"
    tMax = time.getMax()
    tMin = time.getMin()
    binName = TString("splineBinning")
    numKnots = myconfigfile["Acceptance"]["knots"].__len__()
    TimeBin = RooBinning(tMin,tMax,binName.Data())
    for i in range(0, numKnots):
        print "[INFO]   knot %s in place %s with value %s "%(str(i), str(myconfigfile["Acceptance"]["knots"][i]), 
                                                            str(myconfigfile["Acceptance"]["values"][i]))
        TimeBin.addBoundary(myconfigfile["Acceptance"]["knots"][i])
            
    TimeBin.removeBoundary(tMin)
    TimeBin.removeBoundary(tMax)
    TimeBin.removeBoundary(tMin)
    TimeBin.removeBoundary(tMax)
    TimeBin.Print("v")
    time.setBinning(TimeBin, binName.Data())
    time.setRange(tMin, tMax)
    listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, time)
    
    tacc_list = RooArgList()
    tacc_var = []
    for i in range(0,numKnots):
        tacc_var.append(RooRealVar("var"+str(i+1), "var"+str(i+1), myconfigfile["Acceptance"]["values"][i], 0.0, 10.0))
        print "[INFO]  ",tacc_var[i].GetName()
        tacc_list.add(tacc_var[i])
    tacc_var.append(RooRealVar("var"+str(numKnots+1), "var"+str(numKnots+1), 1.0))
    len = tacc_var.__len__()
    tacc_list.add(tacc_var[len-1])
    print "[INFO]   n-2: ",tacc_var[len-2].GetName()
    print "[INFO]   n-1: ",tacc_var[len-1].GetName()
    tacc_var.append(RooAddition("var"+str(numKnots+2), "var"+str(numKnots+2),
                                RooArgList(tacc_var[len-2],tacc_var[len-1]), listCoeff))
    tacc_list.add(tacc_var[len])
    print "[INFO]   n: ",tacc_var[len].GetName()
    
    spl = RooCubicSplineFun("splinePdf", "splinePdf", time, "splineBinning", tacc_list)
    
    # Decay time resolution model
    # ---------------------------
    if not pereventterr:
        print '[INFO] Resolution model: Triple gaussian model'
        trm = PTResModels.tripleGausEffModel( time, spl,
                                              myconfigfile["Resolution"]["scaleFactor"], myconfigfile["Resolution"]["meanBias"],
                                              myconfigfile["Resolution"]["shape"]["sigma1"], 
                                              myconfigfile["Resolution"]["shape"]["sigma2"], 
                                              myconfigfile["Resolution"]["shape"]["sigma3"],
                                              myconfigfile["Resolution"]["shape"]["frac1"], 
                                              myconfigfile["Resolution"]["shape"]["frac2"],
                                              debug
                                              )
        
        terrpdf = None
    else :
        # the decay time error is an extra observable !
        print '[INFO] Resolution model: Gaussian with per-event observable'

        #sf = getScaleFactor(myconfigfile, debug) 
        observables.add( terr )
        trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', myconfigfile["Resolution"]["meanBias"], 'ps' )
        trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', 1.0) #myconfigfile["Resolution"]["scaleFactor"] )
        #terr_scaled = ScaleFactor("terr_scaled", "Resolution scale factor", terr, sf[0], sf[1], sf[2])
        trm_scale_p0  = RooRealVar( 'trm_scale_p0' , 'Gaussian resolution model mean', -1.59675e-02, 'ps' )
        trm_scale_p1  = RooRealVar( 'trm_scale_p1' , 'Gaussian resolution model mean', 2.05905, 'ps' )
        trm_scale_p2  = RooRealVar( 'trm_scale_p2' , 'Gaussian resolution model mean', -7.67665, 'ps' )
        terr_scaled = RooFormulaVar( 'trm_scaled_terr',"scale", "@0+@1*@3+@2*@3*@3",RooArgList(trm_scale_p0,trm_scale_p1,trm_scale_p2,terr))
        #observables.add( terr_scaled ) 
        trm = RooGaussEfficiencyModel("resmodel", "resmodel", time, spl, trm_mean, terr_scaled, trm_mean, trm_scale )

        #terrWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["Resolution"]["templates"]["fileName"]), 
        #                                      TString(myconfigfile["Resolution"]["templates"]["workName"]), debug)
        terrpdf = GeneralUtils.CreateHistPDF(dataWA, terr, TString(myconfigfile["Resolution"]["templates"]["templateName"]), 20, debug)

    # Per-event mistag
    # ---------------------------
    
    tagNum = MDSettings.CheckNumUsedTag()
    numOfTemp = pow(2,tagNum)-1;
    print tagNum, numOfTemp 

    if pereventmistag:
        print "[INFO] Mistag model: per-event observable" 
        #mistagCalibListB, ws = getCalibratedMistag(myconfigfile,ws,MDSettings,mistag, 'B')
        #mistagCalibListBbar, ws = getCalibratedMistag(myconfigfile,ws,MDSettings,mistag, 'Bbar')
        #ws.Print() 
        #print "[INFO] Mistag model: per-event observable" 
        # we need calibrated mistag
        
        p0B = []
        p0Bbar = []
        p1B = []
        p1Bbar = []
        avB = []
        avBbar = []

        mistagCalibList = RooArgList()
        constList = RooArgSet()
        mistagCalibB = []
        mistagCalibBbar = []
        mistagCalibListB = RooArgList()
        mistagCalibListBbar = RooArgList()

        numTag = MDSettings.GetNumTagVar()
        tagList = []
        for i in range(0,numTag):
            if MDSettings.CheckUseTag(i) == True:
                tagList.append(str(MDSettings.GetTagMatch(i)))

        if tagList.__len__()  == 2:
            tagList.append("Both")

        i = 0
        print numOfTemp, tagList.__len__()
        for i in range(0,numOfTemp):
        #for tag in tagList:
            name = 'B_'+str(tagList[i])
            p0B.append(WS(ws,RooRealVar('p0_'+str(name), 'p0_'+str(name),  myconfigfile["TaggingCalibration"][tagList[i]]["p0"], 0., 0.5)))
            p1B.append(WS(ws,RooRealVar('p1_'+str(name), 'p1_'+str(name),  myconfigfile["TaggingCalibration"][tagList[i]]["p1"], 0.5, 1.5)))
            avB.append(WS(ws,RooRealVar('average_'+str(name), 'av_'+str(name),  myconfigfile["TaggingCalibration"][tagList[i]]["average"], 0.0, 1.0)))
            setConstantIfSoConfigured(p0B[i],myconfigfile)
            setConstantIfSoConfigured(p1B[i],myconfigfile)
            setConstantIfSoConfigured(avB[i],myconfigfile)
            mistagCalibB.append(MistagCalibration("mistagCalib_"+str(name), "mistagCalib_"+str(name), mistag, p0B[i], p1B[i], avB[i]))
            mistagCalibListB.add(mistagCalibB[i])
            i=i+1
        i = 0
        for i in range(0,numOfTemp):
            name = 'Bbar_'+str(tagList[i])
            p0Bbar.append(WS(ws,RooRealVar('p0_'+str(name), 'p0_'+str(name),  myconfigfile["TaggingCalibration"][tagList[i]]["p0"], 0., 0.5)))          
            p1Bbar.append(WS(ws,RooRealVar('p1_'+str(name), 'p1_'+str(name),  myconfigfile["TaggingCalibration"][tagList[i]]["p1"], 0.5, 1.5))) 
            avBbar.append(WS(ws,RooRealVar('average_'+str(name), 'av_'+str(name),  myconfigfile["TaggingCalibration"][tagList[i]]["average"], 0.0, 1.0)))
            setConstantIfSoConfigured(p0Bbar[i],myconfigfile)
            setConstantIfSoConfigured(p1Bbar[i],myconfigfile)
            setConstantIfSoConfigured(avBbar[i],myconfigfile)
            mistagCalibBbar.append(MistagCalibration("mistagCalib_"+str(name), "mistagCalib_"+str(name), mistag, p0Bbar[i], p1Bbar[i], avBbar[i]))
            mistagCalibListBbar.add(mistagCalibBbar[i])
            i = i +1
        
        mistagPDFList = SFitUtils.CreateMistagTemplates(dataWA, MDSettings, 50, True, debug)

    else :
        print "[INFO] Mistag model: average mistag" 
        mistagHistPdf = None 
        mistagCalibrated =  mistag 
    
    # CP observables
    # --------------------------
    one1 = RooConstVar('one1', '1', 1.)
    one2 = RooConstVar('one2', '1', 1.)
    C,S,D, Cbar, Sbar,Dbar = getCPparameters(decay,myconfigfile) 
    
    # Tagging                                                                                                                                                                                  
    # -------                                                                                                                                                                                  
    tagEffSigList, ws  = getTagEff(myconfigfile,ws,MDSettings,"tagEff")

    # Production, detector and tagging asymmetries
    # --------------------------------------------
    aTagEffSigList, ws  = getTagEff(myconfigfile,ws,MDSettings,"aTagEff")

    if not toys:
        ws.Print("v")
        from B2DXFitters.GaussianConstraintBuilder import GaussianConstraintBuilder
        #constraintbuilder = GaussianConstraintBuilder(ws,  myconfigfile['Constrains'])
            # remove constraints for modes which are not included                                                                                                                               
        #constList = constraintbuilder.getSetOfConstraints()
        #constList.Print("v")

    aProd = zero     # production asymmetry                                                                                                                                                    
    aDet = zero      # detector asymmetry                                                                                                                                                       
    aDet_const_mean = zero
    aDet_const_err  = zero
    aDet_const_g    = zero
    if myconfigfile.has_key("Asymmetries"):
        if myconfigfile["Asymmetries"].has_key('production') :
            aProd = RooConstVar('aprod_Signal','aprod_Signal',myconfigfile["Asymmetries"]["production"])
        if myconfigfile["Asymmetries"].has_key('detector') :
            aDet = RooRealVar('adet','adet', 0.0) #myconfigfile["adet"],-0.05,0.05)
            aDet_const_mean = RooConstVar('aDet_const_mean','aDet_const_mean',myconfigfile["Asymmetries"]["detector"])
            aDet_const_err  = RooConstVar('aDet_const_err', 'aDet_const_err', 0.005)
            aDet_const_g    = RooGaussian('aDet_const_g','aDet_const_g',aDet,aDet_const_mean,aDet_const_err)
            constList.add(aDet_const_g)


    # Coefficient in front of sin, cos, sinh, cosh
    # --------------------------------------------

    flag = 0

    if pereventmistag:
        otherargs = [ mistag, mistagPDFList, tagEffSigList ]
    else:
        otherargs = [ tagEffSigList ]
    otherargs.append(mistagCalibListB)
    otherargs.append(mistagCalibListBbar) 
    otherargs.append(aProd)
    otherargs.append(aDet)
    otherargs.append(aTagEffSigList)
    
    cosh = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven, id, tag, one1, one2, *otherargs)
    sinh = DecRateCoeff('signal_sinh', 'signal_sinh', DecRateCoeff.CPEven, id, tag, D, Dbar,  *otherargs)
    cos =  DecRateCoeff('signal_cos' , 'signal_cos' , DecRateCoeff.CPOdd,  id, tag, C, C,     *otherargs)
    sin =  DecRateCoeff('signal_sin' , 'signal_sin' , DecRateCoeff.CPOdd,  id, tag, S, Sbar,  *otherargs)
    
    #if debug:
    #    print "[INFO] sin, cos, sinh, cosh created"
    #    cosh.Print("v")
    #    sinh.Print("v")
    #    cos.Print("v")
    #    sin.Print("v")
    #    exit(0)

    # Total time PDF
    # ---------------------------
         
    tauinv          = Inverse( "tauinv","tauinv", gammas)
    
    name_time = TString("time_signal")
    timePDF = RooBDecay(name_time.Data(),name_time.Data(),
                        time, tauinv, deltaGammas,
                        cosh, sinh, cos, sin,
                        deltaMs, trm, RooBDecay.SingleSided)
            
    if pereventterr:
        noncondset = RooArgSet(time, id, tag)
        if pereventmistag:
            noncondset.add(mistag)

        name_timeterr = TString("signal_TimeTimeerrPdf")
        totPDF = RooProdPdf(name_timeterr.Data(), name_timeterr.Data(),
                                     RooArgSet(terrpdf), RooFit.Conditional(RooArgSet(timePDF), noncondset))
    else:
        totPDF = timePDF
            
    '''
    if debug :
    print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!' 
    data.Print("v")
    for i in range(0,nEntries) : 
    obs = data.get(i)
    obs.Print("v")
    w = data.weight()
    #data.get(i).Print("v")
    #print data.weight()
    #print cos.getValV(obs)
    #print sin.getValV(obs)
    #print cosh.getValV(obs)
    #print sinh.getValV(obs)
    '''        
    #exit(0)

    # Delta Ms likelihood scan
    # ---------------------------
      
    if scan:
        RooMsgService.instance().Print('v')
        RooMsgService.instance().deleteStream(1002)
        if debug:
            print "Likelihood scan performing"
        nll= RooNLLVar("nll","-log(sig)",totPDF[0],dataWA, RooFit.NumCPU(4), RooFit.Silence(True))
        pll  = RooProfileLL("pll",  "",  nll, RooArgSet(deltaMs))
        h = pll.createHistogram("h",deltaMs,RooFit.Binning(200))
        h.SetLineColor(kRed)
        h.SetLineWidth(2)
        h.SetTitle("Likelihood Function - Delta Ms")
        like = TCanvas("like", "like", 1200, 800)
        like.cd()
        h.Draw()
        like.Update()
        n = TString("likelihood_Delta_Ms.pdf")
        like.SaveAs(n.Data())
        exit(0)
        
    # Fitting
    # ---------------------------
    if binned: 
        print "[INFO] RooDataSet is binned" 
        time.setBins(250)
        terr.setBins(20)
        dataWA_binned = RooDataHist("dataWA_binned","dataWA_binned",observables,dataWA)   
        
    if toys or unblind: #Unblind yourself 
        if binned:
            myfitresult = totPDF.fitTo(dataWA_binned, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                       RooFit.Verbose(True), RooFit.SumW2Error(True), RooFit.Extended(False)) #,  RooFit.ExternalConstraints(constList))
        else:
            myfitresult = totPDF.fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                       RooFit.Verbose(True), RooFit.SumW2Error(True), RooFit.Extended(False))
        myfitresult.Print("v")
        myfitresult.correlationMatrix().Print()
        myfitresult.covarianceMatrix().Print()
    else :    #Don't
        if binned: 
            myfitresult = totPDF.fitTo(dataWA_binned, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2), RooFit.Extended(False),
                                       RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
        else:
            myfitresult = totPDF.fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2), RooFit.Extended(False),
                                       RooFit.SumW2Error(True), RooFit.PrintLevel(-1))            
        
        print '[INFO Result] Matrix quality is',myfitresult.covQual()
        par = myfitresult.floatParsFinal() 
        const = myfitresult.constPars() 
        print "[INFO Result] Status: ",myfitresult.status()
        print "[INFO Result] -------------- Constant parameters ------------- "
        for i in range(0,const.getSize()):
            print "[INFO Result] parameter %s  set to be  %0.4lf"%(const[i].GetName(), const[i].getValV())

        print "[INFO Result] -------------- Floated parameters ------------- "

        for i in range(0,par.getSize()): 
            name = TString(par[i].GetName())
            if ( name.Contains(decay)):
                print "[INFO Result] parameter %s = (XXX +/- %0.4lf)"%(par[i].GetName(), par[i].getError())
            else:    
                print "[INFO Result] parameter %s = (%0.4lf +/- %0.4lf)"%(par[i].GetName(), par[i].getValV(), par[i].getError())
 
    workout = RooWorkspace("workspace","workspace")
    getattr(workout,'import')(dataWA)
    getattr(workout,'import')(totPDF)
    getattr(workout,'import')(myfitresult)
    workout.writeToFile(wsname)

       
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser(_usage)

parser.add_option('-d', '--debug',
                  dest    = 'debug',
                  default = False,
                  action  = 'store_true',
                  help    = 'print debug information while processing'
                  )
parser.add_option('-s', '--save',
                  dest    = 'wsname',
                  metavar = 'WSNAME',
                  default = 'WS_Time_DsPi.root',  
                  help    = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                  )

parser.add_option( '--pereventmistag',
                   dest = 'pereventmistag',
                   default = False,
                   action = 'store_true',
                   help = 'Use the per-event mistag?'
                   )

parser.add_option( '--pereventterr',
                   dest = 'pereventterr',
                   default = False,
                   action = 'store_true',
                   help = 'Use the per-event time errors?'
                   )

parser.add_option( '-t','--toys',
                   dest = 'toys',
                   action = 'store_true', 
                   default = False,
                   help = 'are we working with toys?'
                   )

parser.add_option( '--fileName',
                   dest = 'fileName',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsPi_all_both.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--treeName',
                   dest = 'treeName',
                   default = 'merged',
                   help = 'name of the workspace'
                   )
parser.add_option( '--scan',
                   dest = 'scan',
                   default = False,
                   action = 'store_true'
                   )

parser.add_option( '--cat',
                   dest = 'cat',
                   default = False,
                   action = 'store_true'
                   )

parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsPiConfigForNominalDMSFit')

#parser.add_option( '--configNameMDFitter',
#                   dest = 'configNameMD',
#                   default = 'Bs2DsPiConfigForNominalMassFitBDTGA')

parser.add_option( '--plotsWeights',
                   dest = 'plotsWeights',
                   default = False,
                   action = 'store_true'
                   )
parser.add_option( '-p', '--pol','--polarity',
                   dest = 'pol',
                   metavar = 'POL',
                   default = 'down',
                   help = 'Sample: choose up or down '
                   )
parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   metavar = 'MODE',
                   default = 'all',
                   help = 'Mode: choose all, kkpi, kpipi, pipipi, nonres, kstk, phipi, 3modeskkpi'
                   )
parser.add_option( '--merge',
                   dest = 'merge',
                   default = "",
                   help = 'for merging magnet polarities use: --merge pol, for merging years of data taking use: --merge year, for merging both use: --merge both'
                   )
parser.add_option( '--binned',
                   dest = 'binned',
                   default = False,
                   action = 'store_true',
                   help = 'binned data Set'
                   )
parser.add_option( '--unblind',
                   dest = 'unblind',
                   default = False,
                   action = 'store_true',
                   help = 'unblind results'
                   )
parser.add_option( '--year',
                   dest = 'year',
                   default = "run1",
                   help = 'year of data taking can be: 2011, 2012, run1')

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    (options, args) = parser.parse_args()

    if len(args) > 0 :
        parser.print_help()
        exit(-1)

    print "=========================================================="
    print "FITTER IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    print options
    print "=========================================================="

    config = options.configName
    last = config.rfind("/")
    directory = config[:last+1]
    configName = config[last+1:]
    p = configName.rfind(".")
    configName = configName[:p]

    #configMD = options.configNameMD
    #last = configMD.rfind("/")
    #configNameMD = configMD[last+1:]
    #p = configNameMD.rfind(".")
    #configNameMD = configNameMD[:p]

    import sys
    sys.path.append(directory)

 
    runSFit( options.debug,
             options.wsname,
             options.pereventmistag,
             options.pereventterr,
             options.toys,
             options.fileName,
             options.treeName,
             configName,
             #configNameMD,
             options.scan,
             options.binned,
             options.plotsWeights,
             options.pol, 
             options.mode,
             options.year,
             options.merge,
             options.unblind)
    
# -----------------------------------------------------------------------------
