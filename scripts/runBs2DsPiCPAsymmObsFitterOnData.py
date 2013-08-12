#!/bin/sh
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
""":"
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.

# make sure the environment is set up properly
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
        if test -z "$(dirname $0)"; then
	    # have to guess location of setup.sh
	    cd ../standalone
	    . ./setup.sh
	    cd "$cwd"
        else
	    # know where to look for setup.sh
	    cd "$(dirname $0)"/../standalone
	    . ./setup.sh
	    cd "$cwd"
        fi
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
from optparse import OptionParser
from math     import pi
import os, sys, gc

if 'CMTCONFIG' in os.environ:
    import GaudiPython
import ROOT
# avoid memory leaks - will have to explicitly relinquish and acquire ownership
# if required, but PyROOT does not do what it thinks best without our knowing
# what it does
ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
if not 'CMTCONFIG' in os.environ:
    # enable ROOT to understand Reflex dictionaries
    ROOT.gSystem.Load('libCintex')
    ROOT.Cintex.Enable()
# load RooFit
ROOT.gSystem.Load('libRooFit')
from ROOT import RooFit
# load our own B2DXFitters library
if 'CMTCONFIG' in os.environ:
    GaudiPython.loaddict('B2DXFittersDict')
else:
    # running in standalone mode, we have to load things ourselves
    ROOT.gSystem.Load(os.environ['B2DXFITTERSROOT'] +
	    '/standalone/libB2DXFitters')

# figure out if we're running from inside gdb
def in_gdb():
    import os
    proclist = dict(
	    (l[0], l[1:]) for l in (
		lraw.replace('\n', '').replace('\r','').split()
		for lraw in os.popen('ps -o pid= -o ppid= -o comm=').readlines()
		)
	    )
    pid = os.getpid()
    while pid in proclist:
	if 'gdb' in proclist[pid][1]: return True
	pid = proclist[pid][0]
    return False

if in_gdb():
    # when running in a debugger, we want to make sure that we do not handle
    # any signals, so the debugger can catch SIGSEGV and friends, and we can
    # poke around
    ROOT.SetSignalPolicy(ROOT.kSignalFast)
    ROOT.gEnv.SetValue('Root.Stacktrace', '0')

AcceptanceFunction       =  'PowLawAcceptance'#BdPTAcceptance'  # None/BdPTAcceptance/DTAcceptanceLHCbNote2007041

# MISCELLANEOUS
bName = 'B_{s}'

#------------------------------------------------------------------------------
              
#------------------------------------------------------------------------------
def setConstantIfSoConfigured(var,myconfigfile) :
    if var.GetName() in myconfigfile["constParams"] : var.setConstant()

#------------------------------------------------------------------------------
def runBdGammaFitterOnData(debug, wsname, initvars, tvar, terrvar, probvar, pereventmistag,
                           toys, pathName, treeName, configName, fitMeTool, scan, signal,
                           BDTGbins, pathName2, pathName3, Cat ) :

    # BLINDING
    Blinding =  False
    
    #if not Blinding and not toys :
    #    print "RUNNING UNBLINDED!"
    #    really = input('Do you really want to unblind? ')
    #    if really != "yes" :
    #        sys.exit(0)     

    from B2DXFitters import taggingutils, cpobservables

    from ROOT import GeneralModels, PTResModels, GeneralUtils, SFitUtils, Bs2Dsh2011TDAnaModels
    
    from ROOT import RooRealVar, RooStringVar, RooFormulaVar, RooProduct
    from ROOT import RooCategory, RooMappedCategory, RooConstVar
    from ROOT import RooArgSet, RooArgList, RooGaussian, RooLandau, RooDecay
    from ROOT import RooGaussModel, RooTruthModel
    from ROOT import RooAbsReal, RooDataSet
    from ROOT import RooAddPdf, RooProdPdf, RooExtendPdf, RooGenericPdf, RooSimultaneous
    from ROOT import RooExponential, RooPolynomial, RooPolyVar, RooUniform
    from ROOT import RooFit,Inverse,RooBDecay
    from ROOT import FitMeTool, IfThreeWay, Dilution, IfThreeWayPdf
    from ROOT import CombBkgPTPdf,RooUniformBinning,TFile,TTree,RooDataHist
    from ROOT import BdPTAcceptance, PowLawAcceptance,RooHistFunc, RooHistPdf
    from ROOT import TString, RooEffProd,RooBinnedPdf, RooMsgService
    from ROOT import NULL, gSystem,RooUniformBinning
    from ROOT import RooUnblindCPAsymVar, RooUnblindPrecision
    from ROOT import RooNLLVar, RooMinuit, RooProfileLL, RooWorkspace, RooLinkedList    
    from ROOT import kRed, TCanvas, RooEffResModel, MistagCalibration
    from ROOT import RooBinnedPdf, SquaredSum, DecRateCoeff, CPObservable, TagEfficiencyWeight
   
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
 
    # tune integrator configuration

    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation','WynnEpsilon')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('maxSteps','1000')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('minSteps','0')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','21Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
                            

    
    tVarTS         = TString(tvar)
    terrVarTS      = TString(terrvar)
    tProbVarTS     = TString(probvar)
    tagVarTS       = TString("lab0_BsTaggingTool_TAGDECISION_OS")
    tagWeightVarTS = TString("lab0_BsTaggingTool_TAGOMEGA_OS")
    idVarTS        = TString("lab1_ID") 
              

    if ( not toys ) and (not signal):
        
        if BDTGbins:
            workspace = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName), TString(treeName),
                                                       myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                       #time, tag, mistag, id,
                                                       tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, False, debug)
                        
            workspace2 = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName2), TString(treeName),
                                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                        tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, False, debug)

            workspace3 = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName3), TString(treeName),
                                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                        tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, False, debug)

            workspaceW = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName), TString(treeName),
                                                       myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                       #time, tag, mistag, id,
                                                       tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, True, debug)
            
            workspace2W = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName2), TString(treeName),
                                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                        tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, True, debug)
            
            workspace3W = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName3), TString(treeName),
                                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                        tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, True, debug)
            
        else:
            workspace = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName), TString(treeName),
                                                       myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                       tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, False, debug)
            workspaceW = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName), TString(treeName),
                                                        myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                        tVarTS, terrVarTS, tagVarTS, tagWeightVarTS, idVarTS, True, debug)
            
            
    elif ( toys ) and (not signal):
        workspace = SFitUtils.ReadDataFromSWeightsToys(TString("DsPi"),TString(pathName), TString(treeName),
                                                       myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                       tVarTS, tagVarTS+TString("_idx"),
                                                       tagWeightVarTS, idVarTS+TString("_idx"),debug)
    elif (signal) and (not toys):    
        workNameTS = TString("workspace")
        workspace = GeneralUtils.LoadWorkspace(TString(pathName),workNameTS, debug)
                                                                                            
    #workspace.Print()
    #workspace.writeToFile("Reweighted_Bs2DsPi.root")
    
    
    #exit(0)
    zero = RooConstVar('zero', '0', 0.)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)

                                                          
    tagVarTS       = TString("qt")
    idVarTS        = TString("qf")
    '''
    if ( not toys ):
        time = GeneralUtils.GetObservable(workspace,tVarTS, debug)
        tag  = GeneralUtils.GetCategory(workspace,tagVarTS, debug)
        mistag = GeneralUtils.GetObservable(workspace,tagWeightVarTS, debug)
        id = GeneralUtils.GetCategory(workspace,idVarTS, debug) 
    else:
        time = GeneralUtils.GetObservable(workspace,tVarTS, debug)
        tag  = GeneralUtils.GetCategory(workspace,tagVarTS+TString("_idx"), debug)
        mistag = GeneralUtils.GetObservable(workspace,tagWeightVarTS, debug)
        id = GeneralUtils.GetCategory(workspace,idVarTS+TString("_idx"), debug)

    tag.Print("v")
    time.Print("v")
    mistag.Print("v")
    id.Print("v")
    '''
    
    mass = RooRealVar('mass', '%s mass' % bName, 5., 6.)
        
    gammas = RooRealVar('Gammas', '%s average lifetime' % bName, myconfigfile["Gammas"], 0., 5., 'ps^{-1}')
    setConstantIfSoConfigured(gammas,myconfigfile)
    deltaGammas = RooRealVar('deltaGammas', 'Lifetime difference', myconfigfile["DeltaGammas"], -1., 1., 'ps^{-1}')
    setConstantIfSoConfigured(deltaGammas,myconfigfile)

    deltaMs = RooRealVar('DeltaMs', '#Delta m_{s}', myconfigfile["DeltaMs"], 1., 30., 'ps^{-1}')
    deltaMs.setError(0.5)
    setConstantIfSoConfigured(deltaMs,myconfigfile)
    if deltaMs.GetName() in myconfigfile["constParams"] :
        Blinding = False

    # tagging
    # -------
    tagEffSig = RooRealVar('tagEffSig', 'Signal tagging efficiency'    , myconfigfile["TagEffSig"], 0., 1.)
    setConstantIfSoConfigured(tagEffSig,myconfigfile)
    
    #tagOmegaSig = RooRealVar('tagOmegaSig', 'Signal mistag rate', myconfigfile["TagOmegaSig"], 0., 1.)
    #setConstantIfSoConfigured(tagOmegaSig,myconfigfile)

    # Define the observables
    # ----------------------
    #if pereventmistag : 
    #    observables = RooArgSet(time,tag,id,mistag)       
    #else : 
    #    observables = RooArgSet(time,tag,id)

      
    # Data set
    #-----------------------
    
    if toys :
        nameData1 = TString("dataSet_time_Bs2DsPi_pos")
        data_pos = GeneralUtils.GetDataSet(workspace,nameData1, debug)#[]
        nameData2 = TString("dataSet_time_Bs2DsPi_neg")
        data_neg = GeneralUtils.GetDataSet(workspace,nameData2, debug)
        data = data_pos
        data.append(data_neg)
        nEntries = data.numEntries()#[]
    else :
        if signal:
            nameData = TString("dataSetMCBsDsPi_both") 
            data = GeneralUtils.GetDataSet(workspace, nameData, debug)
        else:
            nameData = TString("dataSet_time_Bs2DsPi")
            if BDTGbins:
                data   = GeneralUtils.GetDataSet(workspace,   nameData, debug)
                data2  = GeneralUtils.GetDataSet(workspace2,  nameData, debug)
                data3  = GeneralUtils.GetDataSet(workspace3,  nameData, debug)
                data1W = GeneralUtils.GetDataSet(workspaceW,  nameData, debug)
                data2W = GeneralUtils.GetDataSet(workspace2W, nameData, debug)
                data3W = GeneralUtils.GetDataSet(workspace3W, nameData, debug)
                dataWW = [data1W, data2W, data3W] 
                dataW  = GeneralUtils.GetDataSet(workspaceW,  nameData, debug) 
                dataW.append(data2W)
                dataW.append(data3W)
            else:
                data  = GeneralUtils.GetDataSet(workspace, nameData, debug)
                dataW = GeneralUtils.GetDataSet(workspaceW, nameData, debug) 
        
    dataW.Print("v")
    obs = data.get()
    time = obs.find(tVarTS.Data())
    mistag = obs.find(tagWeightVarTS.Data())
    id = obs.find(idVarTS.Data())
    tag = obs.find(tagVarTS.Data())
    terr = obs.find(terrVarTS.Data())
    observables = RooArgSet(time,tag,id)

    if debug:
        frame = time.frame()
        dataW.plotOn(frame)
        canvas = TCanvas("canvas", "canvas", 1200, 1000)
        canvas.cd()
        frame.Draw()
        frame.GetYaxis().SetRangeUser(0.1,3000)
        canvas.GetPad(0).SetLogy()
        canvas.SaveAs('data_time_DsPi.pdf')

    #workout = RooWorkspace("workspace","workspace")
    #getattr(workout,'import')(dataW)
    #saveNameTS = TString("data_time_dspi_bdtg123.root")
    #workout.Print()
    #GeneralUtils.SaveWorkspace(workout,saveNameTS, debug)
         
    #exit(0)
                                                       
    templateWorkspace = GeneralUtils.LoadWorkspace(TString(myconfigfile["TemplateFile"]), TString(myconfigfile["TemplateWorkspace"]), debug)

    if BDTGbins:
        Bin = [TString("BDTG1"), TString("BDTG2"), TString("BDTG3")]
    else:
        Bin = [TString("BDTGA")]
    
    # Decay time resolution model
    # ---------------------------
    if 'PEDTE' not in myconfigfile["DecayTimeResolutionModel"] :
        print 'PTResModels'
        trm = PTResModels.getPTResolutionModel(myconfigfile["DecayTimeResolutionModel"],
                                               time, 'Bs', debug,myconfigfile["resolutionScaleFactor"], myconfigfile["resolutionMeanBias"])
        terrpdf = None
    else :
        # the decay time error is an extra observable !
        print 'GaussianWithGaussPEDTE'

        observables.add( terr )
        trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', myconfigfile["resolutionMeanBias"], 'ps' )
        trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', myconfigfile["resolutionScaleFactor"] )
        trm = RooGaussModel( 'GaussianWithGaussPEDTE', 'GaussianWithGaussPEDTE', time, trm_mean, terr, trm_scale)

        #if debug:
        #    print '[INFO] %s created '%(trm.GetName())
        #    trm.Print("v")
        
        if BDTGbins:
            terrpdf = []
            for i in range(0,3):
                name = TString("sigTimeErrorPdf_%s"%Bin[i].Data())
                terrpdf.append(GeneralUtils.CreateHistPDF(dataWW[i], terr, name, myconfigfile['nBinsProperTimeErr'], debug))
        else:
            name = TString("sigTimeErrorPdf")
            terrpdf = GeneralUtils.CreateHistPDF(dataW, terr, name, myconfigfile['nBinsProperTimeErr'], debug)
            
    # Decay time acceptance function
    # ------------------------------
    if AcceptanceFunction and not (AcceptanceFunction == None or AcceptanceFunction == 'None'):
        if AcceptanceFunction == "BdPTAcceptance" :
            tacc_slope  = RooRealVar('tacc_slope'   , 'BdPTAcceptance_slope'    , myconfigfile["tacc_slope"]    , -100.0 , 100.0 )
            tacc_offset = RooRealVar('tacc_offset'  , 'BdPTAcceptance_offset'   , myconfigfile["tacc_offset"]   , -100.0 , 100.0 )
            tacc_beta   = RooRealVar('tacc_beta'    , 'BdPTAcceptance_beta'     , myconfigfile["tacc_beta"]     , -10.00 , 10.00 )
            tacc = BdPTAcceptance('BsPTAccFunction', '%s decay time acceptance function' % bName,
                                  time, tacc_beta, tacc_slope, tacc_offset)
            setConstantIfSoConfigured(tacc_slope,myconfigfile)
            setConstantIfSoConfigured(tacc_offset,myconfigfile)
            setConstantIfSoConfigured(tacc_beta,myconfigfile)
        elif AcceptanceFunction == 'PowLawAcceptance' :
            if BDTGbins:
                tacc_beta = []
                tacc_exponent = []
                tacc_offset = []
                tacc_turnon = []
                tacc = []

                for i in range(0,3):
                    name_beta = TString("tacc_beta_")+Bin[i]
                    tacc_beta.append(RooRealVar(name_beta.Data(), name_beta.Data(), myconfigfile[name_beta.Data()],  0.00 , 0.15))
                    name_exponent = TString("tacc_exponent_")+Bin[i]
                    tacc_exponent.append(RooRealVar(name_exponent.Data(), name_exponent.Data(), myconfigfile[name_exponent.Data()], 1.00 , 4.00))
                    name_offset = TString("tacc_offset_")+Bin[i]
                    tacc_offset.append(RooRealVar(name_offset.Data(), name_offset.Data(), myconfigfile[name_offset.Data()], -0.2 , 0.10))
                    name_turnon = TString("tacc_turnon_")+Bin[i] 
                    tacc_turnon.append(RooRealVar(name_turnon.Data(), name_turnon.Data(), myconfigfile[name_turnon.Data()], 0.50 , 7.00))
                    name_tacc = TString("BsPowLawAcceptance_")+Bin[i] 
                    tacc.append(PowLawAcceptance(name_tacc.Data(), name_tacc.Data(),
                                                 tacc_turnon[i], time, tacc_offset[i], tacc_exponent[i], tacc_beta[i]))
                    setConstantIfSoConfigured(tacc_beta[i],myconfigfile)
                    setConstantIfSoConfigured(tacc_exponent[i],myconfigfile)
                    setConstantIfSoConfigured(tacc_offset[i],myconfigfile)
                    setConstantIfSoConfigured(tacc_turnon[i],myconfigfile)
                    if debug:
                        print "[INFO] Create %s with parameters %s, %s, %s, %s"%(name_tacc.Data(),
                                                                                 name_beta.Data(),
                                                                                 name_exponent.Data(),
                                                                                 name_offset.Data(),
                                                                                 name_turnon.Data())
            else:
                tacc_beta       = RooRealVar('tacc_beta'    , 'PowLawAcceptance_beta',      myconfigfile["tacc_beta"]       , 0.00 , 0.15) 
                tacc_exponent   = RooRealVar('tacc_exponent', 'PowLawAcceptance_exponent',  myconfigfile["tacc_exponent"]   , 1.00 , 4.00)
                tacc_offset     = RooRealVar('tacc_offset'  , 'PowLawAcceptance_offset',    myconfigfile["tacc_offset"]     , -0.2 , 0.10)
                tacc_turnon     = RooRealVar('tacc_turnon'  , 'PowLawAcceptance_turnon',    myconfigfile["tacc_turnon"]     , 0.50 , 5.00)  
                tacc          = PowLawAcceptance('BsPowLawAcceptance', '%s decay time acceptance function' % bName,
                                                 tacc_turnon, time, tacc_offset, tacc_exponent, tacc_beta)
                setConstantIfSoConfigured(tacc_beta,myconfigfile)
                setConstantIfSoConfigured(tacc_exponent,myconfigfile)
                setConstantIfSoConfigured(tacc_offset,myconfigfile)
                setConstantIfSoConfigured(tacc_turnon,myconfigfile)
            
    else :
        tacc = None
    #if debug:
    #    print '[INFO] %s created '%(tacc.GetName())
    #    tacc.Print("v")
                        
        
    # Bin acceptance
    if myconfigfile["nBinsAcceptance"] > 0:
        # provide binning for acceptance
        if debug:
            print "[INFO] Set binning for time acceptance: %d"%(myconfigfile['nBinsAcceptance'])
        from ROOT import RooUniformBinning
        acceptanceBinning = RooUniformBinning(time.getMin(), time.getMax(), myconfigfile["nBinsAcceptance"],'acceptanceBinning')
        time.setBinning(acceptanceBinning, 'acceptanceBinning')
        if BDTGbins:
            acceptance = []
            timeresmodel = []
            for i in range(0,3):
                acceptance.append(RooBinnedPdf("%sBinned"%tacc[i].GetName(),"%sBinnedA"%tacc[i].GetName(), time, 'acceptanceBinning', tacc[i]))
                acceptance[i].setForceUnitIntegral(True)
                timeresmodel.append(RooEffResModel("%s_timeacc_%s"% (trm.GetName(), acceptance[i].GetName()),
                                                   "trm plus acceptance", trm, acceptance[i]))
        else:
            acceptance = RooBinnedPdf("%sBinned" % tacc.GetName(),  "%sBinnedA" % tacc.GetName(), time, 'acceptanceBinning', tacc)
            acceptance.setForceUnitIntegral(True)
            timeresmodel = RooEffResModel("%s_timeacc_%s"% (trm.GetName(), acceptance.GetName()),"trm plus acceptance", trm, acceptance)
                   

    if 'PEDTE' in myconfigfile["DecayTimeResolutionModel"] and 0 != myconfigfile['nBinsProperTimeErr']:
        if debug:
            print "[INFO] Set binning for time error: %d"%(myconfigfile['nBinsProperTimeErr'])
        terr.setBins(myconfigfile['nBinsProperTimeErr'], 'cache')
        if BDTGbins:
            for i in range(0,3):
                timeresmodel[i].setParameterizeIntegral(RooArgSet(terr))
        else:    
            timeresmodel.setParameterizeIntegral(RooArgSet(terr))

    #if debug:
    #    print '[INFO] %s created '%(timeresmodel.GetName())
    #    timeresmodel.Print("v")
                                
    # Set per event mistag

    if pereventmistag :
        # we need calibrated mistag
        calibration_p1   = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"])
        calibration_p0   = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"])
        avmistag = RooRealVar('avmistag','avmistag',myconfigfile["TagOmegaSig"])

        mistagCalibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',
                                             mistag, calibration_p0,calibration_p1,avmistag)
        observables.add( mistag )
        name = TString("sigMistagPdf")
        if debug:
            print "[INFO] Set binning for mistag: %d"%(myconfigfile['nBinsMistag'])
        #mistagPDF = GeneralUtils.CreateHistPDF(dataW, mistag, name, myconfigfile["nBinsMistag"], debug)
        #mistagPDF = GeneralUtils.CreateBinnedPDF(dataW, mistag, name, myconfigfile["nBinsMistag"], debug)
        mistagPDF  = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(templateWorkspace, TString(myconfigfile["MistagTemplateName"]), debug)
    else:
        mistagHistPdf = None 
        mistagCalibrated =  mistag 

                                  

    aProd = zero     # production asymmetry
    aDet = zero      # detector asymmetry
    aTagEff = zero   # taginng eff asymmetry 
    
    
    C = RooRealVar('C', 'C coeff.', 1.)
    S = RooRealVar('S', 'S coeff.', 0.)
    D = RooRealVar('D', 'D coeff.', 0.)
    Sbar = RooRealVar('Sbar', 'Sbar coeff.', 0.)
    Dbar = RooRealVar('Dbar', 'Dbar coeff.', 0.)

    flag = 0

    if pereventmistag:
        otherargs = [ mistag, mistagPDF, tagEffSig ]
    else:
        otherargs = [ tagEffSig ]
    otherargs.append(mistagCalibrated) 
    otherargs.append(aProd)
    otherargs.append(aDet)
    otherargs.append(aTagEff)
    
    cosh = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven, id, tag, one, one, *otherargs)
    sinh = DecRateCoeff('signal_sinh', 'signal_sinh', DecRateCoeff.CPEven, id, tag, D, Dbar, *otherargs)
    cos =  DecRateCoeff('signal_cos' , 'signal_cos' , DecRateCoeff.CPOdd, id, tag, C, C, *otherargs)
    sin =  DecRateCoeff('signal_sin' , 'signal_sin' , DecRateCoeff.CPOdd, id, tag, S, Sbar, *otherargs)
    
    #if debug:
    #    print "[INFO] sin, cos, sinh, cosh created"
    #    cosh.Print("v")
    #    sinh.Print("v")
    #    cos.Print("v")
    #    sin.Print("v")
    #    exit(0)
   
    if not fitMeTool : 

        tauinv          = Inverse( "tauinv","tauinv", gammas)

        if BDTGbins:
            timePDF = []
            for i in range(0,3):
                name_time = TString("time_signal_")+Bin[i]
                timePDF.append(RooBDecay(name_time.Data(),name_time.Data(), time, tauinv, deltaGammas,
                                        cosh, sinh, cos, sin,
                                        deltaMs, timeresmodel[i], RooBDecay.SingleSided))
            
        else:
            timePDF         = RooBDecay('time_signal','time_signal', time, tauinv, deltaGammas, 
                                        cosh, sinh, cos, sin,
                                        deltaMs, timeresmodel, RooBDecay.SingleSided)

        #if debug:
        #    print '[INFO] %s created '%(timePDF.GetName())
        #    timePDF.Print("v")
                                    
        if 'PEDTE' in myconfigfile["DecayTimeResolutionModel"]:
            noncondset = RooArgSet(time, id, tag)
            if pereventmistag:
                noncondset.add(mistag)

            if BDTGbins:
                totPDF = []
                for i in range(0,3):
                    name_timeterr = TString("signal_TimeTimeerrPdf_")+Bin[i]
                    totPDF.append(RooProdPdf(name_timeterr.Data(), name_timeterr.Data(),
                                             RooArgSet(terrpdf[i]), RooFit.Conditional(RooArgSet(timePDF[i]), noncondset)))
                   
            else:
                totPDF = RooProdPdf('signal_TimeTimeerrPdf', 'signal_TimeTimerrPdf', 
                                RooArgSet(terrpdf), RooFit.Conditional(RooArgSet(timePDF), noncondset))
                           
        else:
            if BDTGbins:
                totPDF = []
                for i in range(0,3):
                    totPDF.append(timePDF)
            else:
                totPDF  = timePDF
            
                                           
        #totPDF.SetName("sigTotPDF")    
        #if debug:
        #    print '[INFO] %s created '%(totPDF.GetName())
        #    totPDF.Print("v")

            
        if Cat:
            if BDTGbins:
                BdtgBin = RooCategory("bdtgbin","bidtgbin")
                for i in range(0,3):
                    BdtgBin.defineType(Bin[i].Data())
                    
                weight = obs.find("sWeights")
                observables.add( weight )    
                combData = RooDataSet("combData","combined data", RooArgSet(observables),
                                      RooFit.Index(BdtgBin),
                                      RooFit.Import(Bin[0].Data(),data),
                                      RooFit.Import(Bin[1].Data(),data2),
                                      RooFit.Import(Bin[2].Data(),data3),
                                      RooFit.WeightVar("sWeights")) #
                                  #RooFit.SumW2Error(True))
                                  
                totPDFSim = RooSimultaneous("simPdf","simultaneous pdf",BdtgBin)
                totPDFSim.addPdf(totPDF[0], Bin[0].Data())
                totPDFSim.addPdf(totPDF[1], Bin[1].Data())
                totPDFSim.addPdf(totPDF[2], Bin[2].Data())
            else:
                BdtgBin = RooCategory("bdtgbin","bidtgbin")
                BdtgBin.defineType(Bin[0].Data())
                
                weight = obs.find("sWeights")
                observables.add( weight )
                
                combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                      RooFit.Index(BdtgBin),
                                      RooFit.Import(Bin[0].Data(),data),
                                      RooFit.WeightVar("sWeights")) #,
                                  #RooFit.SumW2Error(True))
            
                totPDFSim = RooSimultaneous("simPdf","simultaneous pdf",BdtgBin)
                totPDFSim.addPdf(totPDF,  Bin[0].Data())
            
            
        #sigTimePDF      = time # RooEffProd('time_signal','time_signal',time_noacc,tacc)
        #totPDF = time
        #totPDF.Print("v")
        '''
        if debug :
            print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!' 
            data.Print("v")
            for i in range(0,nEntries) : 
                obs = data.get(i)
                obs.Print("v")
                #data.get(i).Print("v")
                print data.weight()
                print cos.getValV(obs)
                print sin.getValV(obs)
                print cosh.getValV(obs)
                print sinh.getValV(obs)
        '''        
        #exit(0)
        
        if scan:
            RooMsgService.instance().Print('v')
            RooMsgService.instance().deleteStream(1002)
            if debug:
                print "Likelihood scan performing"
            nll= RooNLLVar("nll","-log(sig)",totPDF,data, RooFit.NumCPU(4), RooFit.Silence(True))
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
             
        if toys or not Blinding: #Unblind yourself
            if Cat:
                myfitresult = totPDFSim.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                              RooFit.Verbose(False), RooFit.SumW2Error(True), RooFit.Extended(False))
            else:    
                myfitresult = totPDF.fitTo(dataW, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                           RooFit.Verbose(True), RooFit.SumW2Error(True), RooFit.Extended(False))
            
            myfitresult.Print("v")
            myfitresult.correlationMatrix().Print()
            myfitresult.covarianceMatrix().Print()
        else :    #Don't
            if Cat:
                myfitresult = totPDFSim.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                              RooFit.Verbose(False), RooFit.SumW2Error(True), RooFit.Extended(False))
            else:
                myfitresult = totPDF.fitTo(dataW, RooLinkedList(RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                                                RooFit.SumW2Error(True), RooFit.PrintLevel(-1)))

            print 'Matrix quality is',myfitresult.covQual()
            par = myfitresult.floatParsFinal() 
            par[0].Print("v") 

        workout = RooWorkspace("workspace","workspace")
        if Cat:
            getattr(workout,'import')(combData)
            getattr(workout,'import')(totPDFSim)
        else:
            getattr(workout,'import')(dataW)
            getattr(workout,'import')(totPDF)
        getattr(workout,'import')(myfitresult)
        workout.writeToFile(wsname)
    else :
        if 'PEDTE' not in myconfigfile["DecayTimeResolutionModel"] :
            sigTimePDF = GeneralModels.buildRooBDecayPDF(
                time, gammas, deltaGammas, deltaMs,
                sigCosh, sigSinh, sigCos, sigSin,
                trm, tacc,
                'Sig', bName, debug)
        else :
            sigTimePDF = GeneralModels.buildRooBDecayPDFWithPEDTE(
                time, timeerr, gammas, deltaGammas, deltaMs,
                sigCosh, sigSinh, sigCos, sigSin,
                terrpdf, trm, tacc,
                'Sig', bName, debug)
    
        if debug :
            print 'DATASET NOW CONTAINS', nEntries, 'ENTRIES!!!!' 
            data.Print("v")
            for i in range(0,nEntries) : 
                data.get(i).Print("v")
                print data.weight()
    
        totPDF = sigTimePDF
                    
        fitter = FitMeTool(debug)
    
        fitter.setObservables(observables)
        fitter.setModelPDF(totPDF)
        fitter.setData(data)
    
        plot_init   = (wsname != None) and initvars
        plot_fitted = (wsname != None) and (not initvars)
    
        if plot_init :
            fitter.saveModelPDF(wsname)
            fitter.saveData(wsname)
            
        
        if scan:
            RooMsgService.instance().Print('v')
            RooMsgService.instance().deleteStream(1002)
            if debug:
                print "Likelihood scan performing"
            nll= RooNLLVar("nll","-log(sig)",totPDF,data, RooFit.NumCPU(4))
            pll  = RooProfileLL("pll",  "",  nll, RooArgSet(deltaMs))
            h = pll.createHistogram("h",deltaMs,RooFit.Binning(100))
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
    
        if toys or not Blinding: #Unblind yourself
            fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2), RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult = fitter.getFitResult()
            myfitresult.Print("v")
        else :    #Don't
            fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2), RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
            myfitresult = fitter.getFitResult()
            print 'Matrix quality is',myfitresult.covQual()
            par = myfitresult.floatParsFinal() 
            par[0].Print("v") 
    
                            
    
        if plot_fitted :
            fitter.saveModelPDF(wsname)
            fitter.saveData(wsname)
            
        del fitter
        
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
parser.add_option('-i', '--initial-vars',
                  dest    = 'initvars',
                  default = False,
                  action  = 'store_true',
                  help    = 'save the model PDF parameters before the fit (default: after the fit)'
                  )

parser.add_option( '--tvar',
                   dest = 'tvar',
                   default = 'lab0_LifetimeFit_ctau',
                   help = 'set observable '
                   )
parser.add_option( '--terrvar',
                   dest = 'terrvar',
                   default = 'lab0_LifetimeFit_ctauErr',
                   help = 'set observable '
                   )

parser.add_option( '-c', '--cutvariable',
                   dest = 'ProbVar',
                   default = 'lab1_PIDK',
                   help = 'set observable for PID '
                   )


parser.add_option( '--pereventmistag',
                   dest = 'pereventmistag',
                   default = False,
                   action = 'store_true',
                   help = 'Use the per-event mistag?'
                   )

parser.add_option( '-t','--toys',
                   dest = 'toys',
                   action = 'store_true', 
                   default = False,
                   help = 'are we working with toys?'
                   )
parser.add_option( '--signal',
                   dest = 'signal',
                   action = 'store_true',
                   default = False,
                   help = 'are we working with signal MC?'
                   )

parser.add_option( '--pathName',
                   dest = 'pathName',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsPi_all_both.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--pathName2',
                   dest = 'pathName2',
                   default = '/afs/cern.ch/work/a/adudziak/public/sWeights/sWeights_BsDsPi_all_both.root',
                   help = 'name of the inputfile'
                   )

parser.add_option( '--pathName3',
                   dest = 'pathName3',
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

parser.add_option( '--BDTGbins',
                   dest = 'BDTGbins',
                   default = False,
                   action = 'store_true'
                   )
parser.add_option( '--cat',
                   dest = 'Cat',
                   default = False,
                   action = 'store_true'
                   )


parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsPiConfigForNominalDMSFit')

parser.add_option( '--fitMeTool',
                    dest = 'fitMeTool',
                    action = 'store_true',
                    default = False)

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

    import sys
    sys.path.append("../data/")  
 
    runBdGammaFitterOnData( options.debug,
                            options.wsname,
                            options.initvars,
                            options.tvar,
                            options.terrvar,
                            options.ProbVar, 
                            options.pereventmistag,
                            options.toys,
                            options.pathName,
                            options.treeName,
                            options.configName,
                            options.fitMeTool,
                            options.scan,
                            options.signal,
                            options.BDTGbins,
                            options.pathName2,
                            options.pathName3,
                            options.Cat)

# -----------------------------------------------------------------------------
