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
def runBdGammaFitterOnData(debug, wsname, initvars, var, probvar, pereventmistag,
                           toys, pathName, treeName, configName, fitMeTool, scan, signal ) :

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
    #RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    #RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','20Points')
    #RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 10000)

    
    tVarTS         = TString(var)
    tProbVarTS     = TString(probvar)
    tagVarTS       = TString("lab0_BsTaggingTool_TAGDECISION_OS")
    tagWeightVarTS = TString("lab0_BsTaggingTool_TAGOMEGA_OS")
    idVarTS        = TString("lab1_ID") 
              

    if ( not toys ) and (not signal):
        workspace = SFitUtils.ReadDataFromSWeights(TString("DsPi"),TString(pathName), TString(treeName),
                                                   myconfigfile["TimeDown"], myconfigfile["TimeUp"],
                                                   #time, tag, mistag, id,
                                                   tVarTS, tagVarTS, tagWeightVarTS, idVarTS, debug)
        
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
    #timeerr = RooRealVar('timeerr', '%s decay time error' % bName, 0.04, 0.001, 0.1, 'ps')
    timeerr = RooRealVar('timeerr', 'decay time error', 1e-6, 0.25, 'ps')
    
    gammas = RooRealVar('Gammas', '%s average lifetime' % bName, myconfigfile["Gammas"], 0., 5., 'ps^{-1}')
    setConstantIfSoConfigured(gammas,myconfigfile)
    deltaGammas = RooRealVar('deltaGammas', 'Lifetime difference', myconfigfile["DeltaGammas"], -1., 1., 'ps^{-1}')
    setConstantIfSoConfigured(deltaGammas,myconfigfile)

    deltaMs = RooRealVar('DeltaMs', '#Delta m_{s}', myconfigfile["DeltaMs"], 1., 30., 'ps^{-1}')
    deltaMs.setError(0.5)
    setConstantIfSoConfigured(deltaMs,myconfigfile)
    if deltaMs.GetName() in myconfigfile["constParams"] :
        Blinding = False

    # binning
    nBinsMistag            = myconfigfile["nBinsMistag"]
    nBinsPerEventTimeErr   = myconfigfile["nBinsPerEventTimeErr"]
#    nBinsAcceptance        = myconfigfile["nBinsAcceptance"]
            

    # tagging
    # -------
    tagEffSig = RooRealVar('tagEffSig', 'Signal tagging efficiency'    , myconfigfile["TagEffSig"], 0., 1.)
    setConstantIfSoConfigured(tagEffSig,myconfigfile)
    
    tagOmegaSig = RooRealVar('tagOmegaSig', 'Signal mistag rate', myconfigfile["TagOmegaSig"], 0., 1.)
                        
    setConstantIfSoConfigured(tagOmegaSig,myconfigfile)

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
            data = GeneralUtils.GetDataSet(workspace, nameData, debug)
        nEntries = data.numEntries()     
        #frame = time.frame()
        #data.plotOn(frame)
        #canvas = TCanvas('frame','frame')
        #frame.Draw()
        #canvas.GetPad(0).SetLogx()
        #canvas.SaveAs('WTF.pdf')
        #return canvas

    data.Print("v")
    obs = data.get()
    time = obs.find(tVarTS.Data())
    mistag = obs.find(tagWeightVarTS.Data())
    id = obs.find(idVarTS.Data())
    tag = obs.find(tagVarTS.Data())
    time.Print("v")
    mistag.Print("v")
    id.Print("v")
    tag.Print("v")
    observables = RooArgSet(time,tag,id,mistag)
    #exit(0)

    
    
    # Decay time resolution model
    # ---------------------------
    if 'PEDTE' not in myconfigfile["DecayTimeResolutionModel"] :
        print 'PTResModels'
        trm = PTResModels.getPTResolutionModel(myconfigfile["DecayTimeResolutionModel"],
                                               time, 'Bs', debug,myconfigfile["resolutionScaleFactor"], myconfigfile["resolutionMeanBias"])
    else :
        # the decay time error is an extra observable !
        print 'GaussianWithGaussPEDTE'
        observables.add( timeerr )
        trm_mean  = RooRealVar( 'trm_mean' , 'Gaussian resolution model mean', 0., 'ps' )
        trm_scale = RooRealVar( 'trm_scale', 'Gaussian resolution model scale factor', 1.37 )
        trm = RooGaussModel( 'GaussianWithGaussPEDTE', 'GaussianWithGaussPEDTE',
                             time, trm_mean, trm_scale, timeerr )

    # Decay time error distribution
    # -----------------------------
    if 'PEDTE' in myconfigfile['DecayTimeResolutionModel']:
        print 'Create terrpdf'
        # resolution in ps: 7*terrpdf_shape
        terrpdf_shape = RooConstVar('terrpdf_shape', 'terrpdf_shape', 0.0352 / 7.)
        terrpdf_truth = RooTruthModel('terrpdf_truth', 'terrpdf_truth', timeerr)
        terrpdf_i0 = RooDecay('terrpdf_i0', 'terrpdf_i0', timeerr, terrpdf_shape, terrpdf_truth, RooDecay.SingleSided)
        terrpdf_i1 = RooPolynomial('terrpdf_i1','terrpdf_i1', timeerr, RooArgList(zero, zero, zero, zero, zero, zero, one), 0)
        terrpdf = RooProdPdf('terrpdf', 'terrpdf', terrpdf_i0, terrpdf_i1)
        if myconfigfile['DecayTimeErrInterpolation']:
            from ROOT import RooBinned1DQuinticBase, RooAbsPdf
            RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
            obins = timeerr.getBins()
            nbins = myconfigfile['NBinsProperTimeErr']
            if 0 == nbins:
                print 'ERROR: requested binned interpolation of timeerr %s %d %s' % ('histograms with ', nbins, ' bins - increasing to 100 bins')
                nbins = 100
                timeerr.setBins(nbins)
                hist = terrpdf.createHistogram('%s_hist' % terrpdf.GetName(), timeerr)
                hist.Scale(1. / hist.Integral())
                ROOT.SetOwnership(hist, True)
                terrpdf = RooBinned1DQuinticPdf('%s_interpol' % terrpdf.GetName(),'%s_interpol' % terrpdf.GetName(), hist, timeerr, True)
                del hist
                timeerr.setBins(obins)
                del obins
                del nbins
    else:
        terrpdf = None

     
    
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
            tacc_beta       = RooRealVar('tacc_beta'    , 'PowLawAcceptance_beta',      myconfigfile["tacc_beta"]       , 0.00 , 0.15) 
            #tacc_beta.setError(0.01)
            tacc_exponent   = RooRealVar('tacc_exponent', 'PowLawAcceptance_exponent',  myconfigfile["tacc_exponent"]   , 1.00 , 4.00)
            #tacc_exponent.setError(0.5)
            tacc_offset     = RooRealVar('tacc_offset'  , 'PowLawAcceptance_offset',    myconfigfile["tacc_offset"]     , -0.2 , 0.10)
            #tacc_offset.setError(0.01)
            tacc_turnon     = RooRealVar('tacc_turnon'  , 'PowLawAcceptance_turnon',    myconfigfile["tacc_turnon"]     , 0.50 , 5.00)  
            #tacc_turnon.setError(0.25)
            tacc          = PowLawAcceptance('BsPowLawAcceptance', '%s decay time acceptance function' % bName,
                                                tacc_turnon, time, tacc_offset, tacc_exponent, tacc_beta)
            setConstantIfSoConfigured(tacc_beta,myconfigfile)
            setConstantIfSoConfigured(tacc_exponent,myconfigfile)
            setConstantIfSoConfigured(tacc_offset,myconfigfile)
            setConstantIfSoConfigured(tacc_turnon,myconfigfile)
            
    else :
        tacc = None

    # Bin acceptance
    if myconfigfile["nBinsAcceptance"] > 0:
        # provide binning for acceptance
        from ROOT import RooUniformBinning
        acceptanceBinning = RooUniformBinning(time.getMin(), time.getMax(), myconfigfile["nBinsAcceptance"],'acceptanceBinning')
        time.setBinning(acceptanceBinning, 'acceptanceBinning')
        acceptance = RooBinnedPdf("%sBinned" % tacc.GetName(),  "%sBinnedA" % tacc.GetName(), time, 'acceptanceBinning', tacc)
        acceptance.setForceUnitIntegral(True)
        timeresmodel = RooEffResModel("%s_timeacc_%s"% (trm.GetName(), acceptance.GetName()),"trm plus acceptance", trm, acceptance)
        

    # Set per event mistag

    if pereventmistag :
        # we need calibrated mistag
        calibration_p1   = RooRealVar('calibration_p1','calibration_p1',myconfigfile["calibration_p1"])
        calibration_p0   = RooRealVar('calibration_p0','calibration_p0',myconfigfile["calibration_p0"])
        avmistag = RooRealVar('avmistag','avmistag',myconfigfile["TagOmegaSig"])
        mistagCalibrated = MistagCalibration('mistag_calibrated','mistag_calibrated',
                                             mistag, calibration_p0,calibration_p1,avmistag)
        # we need pdf
        MistagWorkspace  = GeneralUtils.LoadWorkspace(TString(myconfigfile["MistagTemplateFile"]), TString(myconfigfile["MistagTemplateWorkspace"]), debug)
        pdf    = Bs2Dsh2011TDAnaModels.GetRooHistPdfFromWorkspace(MistagWorkspace, TString(myconfigfile["MistagTemplateName"]),debug) 
        # and set the same range to pdf and obs 
        hist = pdf.dataHist().createHistogram(mistag.GetName())
        ax = hist.GetXaxis()
        nbins = hist.GetNbinsX()
        mistag.setRange(max(mistag.getMin(), ax.GetBinLowEdge(1)),
		min(mistag.getMax(), ax.GetBinUpEdge(nbins)))
	# make sure the PDF is sane (1e-37 is what a float can provide)
	for i in xrange(1, 1 + nbins):
	    c = hist.GetBinContent(i)
	    if c < 1e-37:
		hist.SetBinContent(i, 1e-37)
        dh = RooDataHist('sigMistagPdf_dhist', 'sigMistagPdf_dhist', RooArgList(mistag), hist)
        mistagHistPdf = RooHistPdf('sigMistagPdf', 'sigMistagPdf',RooArgSet(mistag), dh)
        GeneralUtils.SaveTemplateHist(dh,mistagHistPdf,mistag,TString("Mist"), TString("ag"), debug)
        #exit(0)
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
        otherargs = [ mistag, mistagHistPdf, tagEffSig ]
    else:
        otherargs = [ tagEffSig ]
    otherargs.append(mistagCalibrated) #tagOmegaSig)
    otherargs.append(aProd)
    otherargs.append(aDet)
    otherargs.append(aTagEff)
    
    cosh = DecRateCoeff('signal_cosh', 'signal_cosh', DecRateCoeff.CPEven, id, tag, one, one, *otherargs)
    sinh = DecRateCoeff('signal_sinh', 'signal_sinh', DecRateCoeff.CPEven, id, tag, D, Dbar, *otherargs)
    cos =  DecRateCoeff('signal_cos' , 'signal_cos' , DecRateCoeff.CPOdd, id, tag, C, C, *otherargs)
    sin =  DecRateCoeff('signal_sin' , 'signal_sin' ,DecRateCoeff.CPOdd, id, tag, Sbar, S, *otherargs)
    #sin =  DecRateCoeff('signal_sin' , 'signal_sin' , DecRateCoeff.CPOdd | DecRateCoeff.Minus, id, tag, S, Sbar, *otherargs)
    if debug:
        print "sin, cos, sinh, cosh created"
        cosh.Print("v")
        sinh.Print("v")
        cos.Print("v")
        sin.Print("v")
        #exit(0)
   
    if not fitMeTool : 

        tauinv          = Inverse( "tauinv","tauinv", gammas)
        time_noacc      = RooBDecay('time_signal_noacc','time_signal_noacc', time, tauinv, deltaGammas, 
                                            cosh, sinh, cos, sin,
                                            deltaMs, timeresmodel, RooBDecay.SingleSided)

        if debug:
            print '%s created '%(time_noacc.GetName())
            time_noacc.Print("v")
            
        sigTimePDF      = time_noacc # RooEffProd('time_signal','time_signal',time_noacc,tacc)
            
        totPDF = sigTimePDF
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
            myfitresult = totPDF.fitTo(data, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                                       RooFit.Verbose(True), RooFit.SumW2Error(True))
            myfitresult.Print("v")
            myfitresult.correlationMatrix().Print()
            myfitresult.covarianceMatrix().Print()
        else :    #Don't
            myfitresult = totPDF.fitTo(data, RooLinkedList(RooFit.Save(1), RooFit.Optimize(0), RooFit.Strategy(2),
                                                           RooFit.SumW2Error(True), RooFit.PrintLevel(-1)))
            print 'Matrix quality is',myfitresult.covQual()
            par = myfitresult.floatParsFinal() 
            par[0].Print("v") 

        workout = RooWorkspace("workspace","workspace")
        getattr(workout,'import')(data)
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

parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_LifetimeFit_ctau',
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
                   
parser.add_option( '--configName',
                    dest = 'configName',
                    default = 'Bs2DsPiConfigForNominalDMSFitPowLaw')

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
                            options.var, 
                            options.ProbVar, 
                            options.pereventmistag,
                            options.toys,
                            options.pathName,
                            options.treeName,
                            options.configName,
                            options.fitMeTool,
                            options.scan,
                            options.signal)

# -----------------------------------------------------------------------------
