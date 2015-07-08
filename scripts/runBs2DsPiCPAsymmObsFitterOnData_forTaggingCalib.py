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
              
#------------------------------------------------------------------------------
def setConstantIfSoConfigured(var,myconfigfile) :
    if var.GetName() in myconfigfile["constParams"] : var.setConstant()

#------------------------------------------------------------------------------
def runBdGammaFitterOnData(debug, wsname,
                           tVar, terrVar, tagVar, tagOmegaVar, idVar, mVar,
                           pereventmistag, toys, pathName, treeName,
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
                            

    #Giulia 16/09/2013: changing the name of tagging variables--->no more _BsTaggingTool_
    
    config = TString("../data/")+TString(configNameMD)+TString(".py")
    MDSettings = MDFitterSettings("MDSettings","MDFSettings",config)
    MDSettings.SetTimeVar(TString(tVar))
    MDSettings.SetTerrVar(TString(terrVar))
    MDSettings.SetTagVar(TString(tagVar))
    MDSettings.SetTagOmegaVar(TString(tagOmegaVar))
    MDSettings.SetIDVar(TString(idVar))
    MDSettings.SetMassBVar(TString(mVar))

    MDSettings.Print
    
    if BDTGbins:
        bound = 3
        Bin = [TString("BDTG1"), TString("BDTG2"), TString("BDTG3")]
    else:
        bound = 1
        Bin = [TString("BDTGA")]

    workspace =[]
    workspaceW = []
    
    for i in range (0,3):
        workspace.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, TString("DsPi"),
                                                        false, toys, false, debug))
        workspaceW.append(SFitUtils.ReadDataFromSWeights(TString(pathName), TString(treeName), MDSettings, TString("DsPi"),
                                                         true, toys, false, debug))
         
    workspace[0].Print()
        
    
    #exit(0)
    zero = RooConstVar('zero', '0', 0.)
    one = RooConstVar('one', '1', 1.)
    minusone = RooConstVar('minusone', '-1', -1.)
    two = RooConstVar('two', '2', 2.)
                                                         
                      
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
    
    #Giulia 16/09/2013: try to fix the mistag for obtaing just the acceptance parameters
    tagOmegaSig = RooRealVar('tagOmegaSig', 'Signal mistag rate', myconfigfile["TagOmegaSig"], 0., 1.)
    setConstantIfSoConfigured(tagOmegaSig,myconfigfile)

    # Data set
    #-----------------------
    
    nameData = TString("dataSet_time_Bs2DsPi")
    data  = []
    dataW = []
    
    for i in range(0, bound):
        data.append(GeneralUtils.GetDataSet(workspace[i],   nameData, debug))
        dataW.append(GeneralUtils.GetDataSet(workspace[i],   nameData, debug))
        
    dataWA = dataW[0]
    dataA = data[0]
    if BDTGbins:
        dataWA.append(dataW[1])
        dataWA.append(dataW[2])
        dataA.append(data[1])
        dataA.append(data[2])
                
    nEntries = dataWA.numEntries()
           

    dataWA.Print("v")
    obs = dataWA.get()
    time = obs.find(tVar)
    mistag = obs.find(tagOmegaVar)
    id = obs.find("qf")
    tag = obs.find("qt")
    weight = obs.find("sWeights")
    observables = RooArgSet(time,tag,id)
    
    newdata = RooDataSet("newdata", "newdata", dataA.get(), "sWeights")
    for i in xrange(0, dataA.numEntries()):
        obs2 = dataA.get(i)
        if 0 == obs2.find(tag.GetName()).getIndex(): continue
        newdata.add(obs, obs2.find("sWeights").getVal())
    workspace[0].__getattribute__("import")(newdata)
    newdata = workspace[0].data("newdata")
    dataA.Print("v")
    newdata.Print("v")
    #Giulia & Manuel 17 October: reducing data set for fitting just on tagged events -> but something wrong happens
    #dataW = dataW.reduce(RooFit.Cut("0 != %s" % tag.GetName()))
    data = dataA.reduce(RooFit.Cut("0 != %s" % tag.GetName()))

    if debug:
        frame = time.frame()
        dataWA.plotOn(frame)
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
        
    
    # Decay time acceptance function
    # ---------------------------

    tMax = time.getMax()
    tMin = time.getMin()
    binName = TString("splineBinning")
    TimeBin = RooBinning(tMin,tMax,binName.Data())
    for i in range(0, myconfigfile["tacc_size"]):
        print " knot %s in place %s with value %s "%(str(i), str(myconfigfile["tacc_knots"][i]), str(myconfigfile["tacc_values"][i]))
        TimeBin.addBoundary(myconfigfile["tacc_knots"][i])
            
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
    for i in range(0,myconfigfile["tacc_size"]):
        tacc_var.append(RooRealVar("var"+str(i+1), "var"+str(i+1), myconfigfile["tacc_values"][i]))
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
            #terrpdf.append(Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(terrWork, TString(myconfigfile["TerrTempName"]), debug))
            terrpdf.append((GeneralUtils.CreateHistPDF(dataWA, terr, TString("TimeErrorPDF"), 20, debug)))

    
    #Giulia 17/09/2013: Evaluation of tagging efficiency on data
    tagged = 0.0
    untagged = 0.0
    tageff = 0.0
    nEntries = newdata.numEntries()
    if debug :
      for i in xrange(0,nEntries) :
            obs2 = newdata.get(i)
            #obs.Print("v")
            #print "tag===========",obs.find(tag.GetName()).getIndex()
            if obs2.find(tag.GetName()).getIndex()!=0 :
             tagged = tagged + newdata.weight()
            else : 
             untagged = untagged + newdata.weight()
             

    tageff = tagged/(tagged + untagged)
    tagEffSig.setVal(tageff)
    print "********************",tagEffSig.getVal()
    setConstantIfSoConfigured(tagEffSig,myconfigfile)                               
    # Set per event mistag
    if pereventmistag :
        #data.Print("v")
        data.table(RooArgSet(tag)).Print("v")
        sum1 = 0.0
        sum2 = 0.0
        avMistag = 0.0
        m = 0.0
        w = 0.0
        nEntries = newdata.numEntries()
        if debug :
            for i in xrange(0,nEntries) :
                obs2 = newdata.get(i)
                #obs2.Print("v")
                if obs2.find(tag.GetName()).getIndex()!=0 :
                 w = newdata.weight()
                 m = obs2.find(mistag.GetName()).getVal()
                 sum1 += m*w
                 sum2 += w


            avMistag = sum1/sum2
            print ("%s / %s = %s")%(str(sum1),str(sum2), str(sum1/sum2))
        avmistag = RooRealVar('avmistag','avmistag',0.,0.5)
        #avMistag = heta.getMean() 
        avmistag.setVal(avMistag)
        #avmistag.setConstant(kTRUE)
        print 'average mistag is %f'%(avmistag.getVal())
        calibration_p1   = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"],0.,2.5)
        calibration_p0   = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"],0.,2.)
        setConstantIfSoConfigured(calibration_p1,myconfigfile)
        setConstantIfSoConfigured(calibration_p0,myconfigfile) 
        #avmistag = RooRealVar('avmistag','avmistag',myconfigfile["TagOmegaSig"],0.,0.5)
        setConstantIfSoConfigured(avmistag,myconfigfile) 
        mistagCalibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',
                                             mistag, calibration_p0,calibration_p1,avmistag)
        observables.add( mistag )
        name = TString("sigMistagPdf")
        if debug:
            print "[INFO] Set binning for mistag: %d"%(myconfigfile['nBinsMistag'])
            mistagPDF = GeneralUtils.CreateHistPDF(newdata, mistag, name, myconfigfile["nBinsMistag"], debug)
        #Giulia & Manuel 17 October 2013: Plotting the eta predicted
            fr = mistag.frame()
            mistagPDF.plotOn(fr)
            fr.Draw()
            from ROOT import gPad
            gPad.Print("foo.eps")
            #mistagPDF = GeneralUtils.CreateBinnedPDF(dataW, mistag, name, myconfigfile["nBinsMistag"], debug)
            #mistagPDF  = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(templateWorkspace, TString(myconfigfile["MistagTemplateName"]), debug)
        else:
            mistagHistPdf = None 
            mistagCalibrated =  mistag 
                
#-----------------------------------------------------------------------------------------------------------------------------------
    aProd = zero     # production asymmetry
    aDet = zero      # detector asymmetry
    aTagEff = zero   # taginng eff asymmetry 
    
    
    C = RooRealVar('C', 'C coeff.', 1.)#/1.109)
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
   
    tauinv          = Inverse( "tauinv","tauinv", gammas)
    
    if BDTGbins:
        timePDF = []
        for i in range(0,3):
            name_time = TString("time_signal_")+Bin[i]
            timePDF.append(RooBDecay(name_time.Data(),name_time.Data(), time, tauinv, deltaGammas,
                                     cosh, sinh, cos, sin,
                                     deltaMs, trm, RooBDecay.SingleSided))
            
    else:
        timePDF         = RooBDecay('time_signal','time_signal', time, tauinv, deltaGammas, 
                                    cosh, sinh, cos, sin,
                                    deltaMs, trm, RooBDecay.SingleSided)
        
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
            
            
            totPDFSim = RooSimultaneous("simPdf","simultaneous pdf",BdtgBin)
            totPDFSim.addPdf(totPDF[0], Bin[0].Data())
            totPDFSim.addPdf(totPDF[1], Bin[1].Data())
            totPDFSim.addPdf(totPDF[2], Bin[2].Data())
        else:
            BdtgBin = RooCategory("bdtgbin","bidtgbin")
            BdtgBin.defineType(Bin[0].Data())
            
            obs.Print()
            weight = obs.find("sWeights")
            print "&&&&&&&&&&",weight
            observables.Print()
            weight.Print()
            observables.add( weight )
            
            combData = RooDataSet("combData","combined data",RooArgSet(observables),
                                  RooFit.Index(BdtgBin),
                                  RooFit.Import(Bin[0].Data(),data),
                                  RooFit.WeightVar("sWeights")) #,
                                  #RooFit.SumW2Error(True))
                                  
            totPDFSim = RooSimultaneous("simPdf","simultaneous pdf",BdtgBin)
            totPDFSim.addPdf(totPDF,  Bin[0].Data())
            

    pdf = RooAddPdf('totPDFtot', 'totPDFtot', RooArgList(totPDFSim), RooArgList())
       
      
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
            myfitresult = pdf.fitTo(combData, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                          RooFit.Verbose(False), RooFit.SumW2Error(True), RooFit.Extended(False))
        else:    
            myfitresult = totPDF.fitTo(dataWA, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
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
        getattr(workout,'import')(dataW)
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
                    default = 'Bs2DsPiConfigForTagCalib')

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
