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
              
#------------------------------------------------------------------------------
def setConstantIfSoConfigured(var,myconfigfile) :
    if var.GetName() in myconfigfile["constParams"] : var.setConstant()

#------------------------------------------------------------------------------
def runBdGammaFitterOnData(debug, wsname,
                           tVar, terrVar, tagVar, tagOmegaVar, idVar, mVar,
                           pereventmistag, pereventterr, 
                           toys, pathName, treeName,
                           configName, configNameMD, scan, 
                           BDTGbins, pathName2, pathName3, Cat ) :

    # BLINDING
    Blinding =  False
    
    #if not Blinding and not toys :
    #    print "RUNNING UNBLINDED!"
    #    really = input('Do you really want to unblind? ')
    #    if really != "yes" :
    #        sys.exit(0)     

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
 
    # tune integrator configuration

    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation','WynnEpsilon')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('maxSteps','1000')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('minSteps','0')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','21Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)

    # Reading data set
    #-----------------------
                               
    config = TString("../data/")+TString(configNameMD)+TString(".py")
    MDSettings = MDFitterSettings("MDSettings","MDFSettings",config)
    MDSettings.SetTimeVar(TString(tVar))
    MDSettings.SetTerrVar(TString(terrVar))
    #MDSettings.SetTagVar(TString(tagVar))
    #MDSettings.SetTagOmegaVar(TString(tagOmegaVar))
    MDSettings.SetIDVar(TString(idVar))
    MDSettings.SetMassBVar(TString(mVar))

    MDSettings.Print("v")

    if BDTGbins:
        bound = 3
        Bin = [TString("BDTG1"), TString("BDTG2"), TString("BDTG3")]
    else:
        bound = 1
        Bin = [TString("BDTGA")]
                       
        
    workspace =[]
    workspaceW = []
    part = "BsDsPi"
    for i in range (0,bound):
        workspace.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, TString(part),
                                                        false, toys, false, debug))
        workspaceW.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, TString(part),
                                                         true, toys, false, debug))
        
    workspace[0].Print()
      
    #exit(0)
    zero = RooConstVar('zero', '0', 0.)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)
                     
    # Data set
    #-----------------------
    nameData = TString("dataSet_time_")+TString(part)
    data  = []
    dataW = []
    
    for i in range(0, bound):
        data.append(GeneralUtils.GetDataSet(workspace[i],   nameData, debug))
        dataW.append(GeneralUtils.GetDataSet(workspaceW[i],   nameData, debug))
        
    dataWA = data[0]
    if BDTGbins:
        dataWA.append(dataW[1])
        dataWA.append(dataW[2])
        
    nEntries = dataWA.numEntries()
                                                    
    dataWA.Print("v")
    obs = dataWA.get()
    time = obs.find(tVar)
    terr = obs.find(terrVar)
    id = obs.find("qf")
    tag = obs.find("tagDecComb")
    mistag = obs.find("tagOmegaComb")
    mistag.setRange(0, 0.5)
    weight = obs.find("sWeights")
    observables = RooArgSet(time,tag,id)
    weight.setRange(-1,1.5)
    if debug:
        name = TString("pdf")
        swpdf = GeneralUtils.CreateHistPDF(dataWA, weight, name, 100, debug)
        GeneralUtils.SaveTemplate(dataWA, swpdf, weight, name)
        #exit(0)
    
    # Physical parameters
    #-----------------------
        
    gammas = RooRealVar('Gammas', '%s average lifetime' % bName, myconfigfile["Gammas"], 0., 5., 'ps^{-1}')
    setConstantIfSoConfigured(gammas,myconfigfile)
    deltaGammas = RooRealVar('deltaGammas', 'Lifetime difference', myconfigfile["DeltaGammas"], -1., 1., 'ps^{-1}')
    setConstantIfSoConfigured(deltaGammas,myconfigfile)
    
    deltaMs = RooRealVar('DeltaMs', '#Delta m_{s}', myconfigfile["DeltaMs"], 1., 30., 'ps^{-1}')
    deltaMs.setError(0.5)
    setConstantIfSoConfigured(deltaMs,myconfigfile)
    if deltaMs.GetName() in myconfigfile["constParams"] :
        Blinding = False
                                        
    # Decay time acceptance model
    # ---------------------------
        
    binName = TString("splineBinning")
    TimeBin = RooBinning(0.2,15,binName.Data())
    for i in range(0, myconfigfile["tacc_size"]):
        TimeBin.addBoundary(myconfigfile["tacc_knots"][i])
            
    TimeBin.removeBoundary(0.2)
    TimeBin.removeBoundary(15.0)
    TimeBin.removeBoundary(0.2)
    TimeBin.removeBoundary(15.0)
    TimeBin.Print("v")
    time.setBinning(TimeBin, binName.Data())
    time.setRange(0.2, 15.0)
    listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, time)
    
    tacc_list = RooArgList()
    tacc_var = []
    for i in range(0,myconfigfile["tacc_size"]):
        tacc_var.append(RooRealVar("var"+str(i+1), "var"+str(i+1), myconfigfile["tacc_values"][i], 0.0, 2.0))
        print tacc_var[i].GetName()
        tacc_list.add(tacc_var[i])
    tacc_var.append(RooRealVar("var"+str(myconfigfile["tacc_size"]+1), "var"+str(myconfigfile["tacc_size"]+1), 1.0))
    len = tacc_var.__len__()
    tacc_list.add(tacc_var[len-1])
    print "n-2: ",tacc_var[len-2].GetName()
    print "n-1: ",tacc_var[len-1].GetName()
    tacc_var.append(RooAddition("var"+str(myconfigfile["tacc_size"]+2), "var"+str(myconfigfile["tacc_size"]+2),
                                RooArgList(tacc_var[len-2],tacc_var[len-1]), listCoeff))
    tacc_list.add(tacc_var[len])
    print "n: ",tacc_var[len].GetName()
    
    spl = RooCubicSplineFun("splinePdf", "splinePdf", time, "splineBinning", tacc_list)
    
       
    # Decay time resolution model
    # ---------------------------
    if not pereventterr:
        print 'Triple gaussian model'
        trm = PTResModels.tripleGausEffModel( time,
                                              spl,
                                              myconfigfile["resolutionScaleFactor"],
                                              myconfigfile["resolutionMeanBias"],
                                              myconfigfile["resolutionSigma1"],
                                              myconfigfile["resolutionSigma2"],
                                              myconfigfile["resolutionSigma3"],
                                              myconfigfile["resolutionFrac1"],
                                              myconfigfile["resolutionFrac2"],
                                              debug
                                              )
        
        terrpdf = None
    else :
        # the decay time error is an extra observable !
        print 'GaussianWithGaussPEDTE'

        observables.add( terr )
        trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', myconfigfile["resolutionMeanBias"], 'ps' )
        trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', myconfigfile["resolutionScaleFactor"] )
        trm = RooGaussEfficiencyModel("resmodel", "resmodel", time, spl, trm_mean, terr, trm_scale, trm_scale )

        terrWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["TerrFile"]), TString(myconfigfile["TerrWork"]), debug)
        terrpdf = []
        for i in range(0,bound):
            terrpdf.append(Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(terrWork, TString(myconfigfile["TerrTempName"]), debug))
            
    # Tagging
    # -------
    tagEffSigList = RooArgList()
    tagEffSig = []
    for i in range(0,3):
        tagEffSig.append(RooRealVar('tagEffSig_'+str(i+1), 'Signal tagging efficiency', myconfigfile["TagEffSig"][i]))
        print tagEffSig[i].GetName()
        tagEffSigList.add(tagEffSig[i])
        #setConstantIfSoConfigured(tagEffSig,myconfigfile)

    # Per-event mistag
    # ---------------------------
    
    if pereventmistag :
        # we need calibrated mistag
        observables.add( mistag )
        
        mistagCalibList = RooArgList()
        for i in range(0,3):
            mistagCalibList.add(mistag)

        mistagWork = GeneralUtils.LoadWorkspace(TString(myconfigfile["MistagFile"]), TString(myconfigfile["MistagWork"]), debug)
        mistagPDF = []
        mistagPDFList = RooArgList()
        for i in range(0,3):
            mistagPDF.append(Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(mistagWork, TString(myconfigfile["MistagTempName"][i]), debug))
            mistagPDFList.add(mistagPDF[i])                 
                             
        #mistagPDF = SFitUtils.CreateMistagTemplates(dataWA,MDSettings,50,true, debug)
        #calibration_p1   = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"])
        #calibration_p0   = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"])
        #avmistag = RooRealVar('avmistag','avmistag',myconfigfile["TagOmegaSig"])
        #
        #mistagCalibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',
        #                                     mistag, calibration_p0,calibration_p1,avmistag)
    else:
        mistagHistPdf = None 
        mistagCalibrated =  mistag 

    # CP observables
    # ---------------------------
         
    one1 = RooConstVar('one1', '1', 1.)
    one2 = RooConstVar('one2', '1', 1.)
    C = RooRealVar('C', 'C coeff.', 1.)
    S = RooRealVar('S', 'S coeff.', 0.)
    D = RooRealVar('D', 'D coeff.', 0.)
    Sbar = RooRealVar('Sbar', 'Sbar coeff.', 0.)
    Dbar = RooRealVar('Dbar', 'Dbar coeff.', 0.)
                            
    
    # Production, detector and tagging asymmetries
    # --------------------------------------------
         
    aProd = RooConstVar("aProd","aProd",0.0)  #zero     # production asymmetry
    aDet = RooConstVar("aDet","aDet",0.0)     #zero      # detector asymmetry
    
    aTagEffSig = []
    aTagEffSigList = RooArgList()
    for i in range(0,3):
        aTagEffSig.append(RooRealVar('aTagEff_'+str(i+1), 'atageff', myconfigfile["aTagEffSig"][i]))
        print aTagEffSig[i].GetName()
        aTagEffSigList.add(aTagEffSig[i])

    # Coefficient in front of sin, cos, sinh, cosh
    # --------------------------------------------

    flag = 0

    if pereventmistag:
        otherargs = [ mistag, mistagPDFList, tagEffSigList ]
    else:
        otherargs = [ tagEffSigList ]
    otherargs.append(mistagCalibList) 
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
    
    timePDF = []
    print bound
    for i in range(0,bound):
        name_time = TString("time_signal_")+Bin[i]
        timePDF.append(RooBDecay(name_time.Data(),name_time.Data(),
                                 time, tauinv, deltaGammas,
                                 cosh, sinh, cos, sin,
                                 deltaMs, trm, RooBDecay.SingleSided)) #timeresmodel[i], RooBDecay.SingleSided))
        
        #if debug:
        #    print '[INFO] %s created '%(timePDF[i].GetName())
        #    timePDF[i].Print("v")
            
    if pereventterr:
        noncondset = RooArgSet(time, id, tag)
        if pereventmistag:
            noncondset.add(mistag)
            totPDF = []
        for i in range(0,bound):
            name_timeterr = TString("signal_TimeTimeerrPdf_")+Bin[i]
            totPDF.append(RooProdPdf(name_timeterr.Data(), name_timeterr.Data(),
                                     RooArgSet(terrpdf[i]), RooFit.Conditional(RooArgSet(timePDF[i]), noncondset)))
            
            
    else:
        totPDF = []
        for i in range(0,bound):
            print i
            totPDF.append(timePDF[i])
            #totPDF[i].Print("v")    
                
            
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
                                  RooFit.Import(Bin[0].Data(),data[0]),
                                  RooFit.Import(Bin[1].Data(),data[1]),
                                  RooFit.Import(Bin[2].Data(),data[2]),
                                  RooFit.WeightVar("sWeights")) 
            
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
                                  RooFit.Import(Bin[0].Data(),data[0]),
                                  RooFit.WeightVar("sWeights")) 
            
            totPDFSim = RooSimultaneous("simPdf","simultaneous pdf",BdtgBin)
            totPDFSim.addPdf(totPDF[0],  Bin[0].Data())
            
        pdf = RooAddPdf('totPDFtot', 'totPDFtot', RooArgList(totPDFSim), RooArgList())
            
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
        
    # Fitting
    # ---------------------------
        
    if toys or not Blinding: #Unblind yourself
        if Cat:
            myfitresult = totPDFSim.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                          RooFit.Verbose(False), RooFit.SumW2Error(True), RooFit.Extended(False))
        else:    
            myfitresult = totPDF[0].fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                          RooFit.Verbose(True), RooFit.SumW2Error(True), RooFit.Extended(False))
            
        myfitresult.Print("v")
        myfitresult.correlationMatrix().Print()
        myfitresult.covarianceMatrix().Print()
    else :    #Don't
        if Cat:
            myfitresult = pdf.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                    RooFit.Verbose(False), RooFit.SumW2Error(True), RooFit.Extended(False))
        else:
            myfitresult = totPDF.fitTo(dataWA, RooLinkedList(RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                                            RooFit.SumW2Error(True), RooFit.PrintLevel(-1)))
            
        print 'Matrix quality is',myfitresult.covQual()
        par = myfitresult.floatParsFinal() 
        par[0].Print("v") 
        
    workout = RooWorkspace("workspace","workspace")
    if Cat:
        getattr(workout,'import')(combData)
        getattr(workout,'import')(totPDFSim)
    else:
        getattr(workout,'import')(dataWA)
        getattr(workout,'import')(totPDF[0])
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

parser.add_option( '--tagvar',
                   dest = 'tagvar',
                   default = 'lab0_TAGDECISION_OS',
                   help = 'set observable '
                   )
parser.add_option( '--tagomegavar',
                   dest = 'tagomegavar',
                   default = 'lab0_TAGOMEGA_OS',
                   help = 'set observable '
                   )

parser.add_option( '--idvar',
                   dest = 'idvar',
                   default = 'lab1_ID',
                   help = 'set observable '
                   )

parser.add_option( '--mvar',
                   dest = 'mvar',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '
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

parser.add_option( '--configNameMDFitter',
                   dest = 'configNameMD',
                   default = 'Bs2DsPiConfigForNominalMassFitBDTGA')


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
                            options.tvar,
                            options.terrvar,
                            options.tagvar,
                            options.tagomegavar,
                            options.idvar,
                            options.mvar,
                            options.pereventmistag,
                            options.pereventterr,
                            options.toys,
                            options.pathName,
                            options.treeName,
                            options.configName,
                            options.configNameMD,
                            options.scan,
                            options.BDTGbins,
                            options.pathName2,
                            options.pathName3,
                            options.Cat)

# -----------------------------------------------------------------------------
