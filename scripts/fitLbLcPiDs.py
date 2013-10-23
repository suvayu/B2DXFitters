#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to run a signal fit on MC for B->DPi, Bs->DsPi, Bs->DsK     #
#   with the FitMeTool fitter                                                 #
#                                                                             #
#   Example usage:                                                            #
#      python fitSignal.py --mode BDPi -s WS.root --debug --veto              #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 08 / 06 / 2011                                                    #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 21 / 02 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# settings for running without GaudiPython
# -----------------------------------------------------------------------------
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
import B2DXFitters
import ROOT
from ROOT import RooFit
from optparse import OptionParser
from math     import pi, log
import os, sys, gc
gROOT.SetBatch()

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------


# INITIAL PARAMETERS
mean  = 5367.51
sigma1 = 10.00
sigma2 = 15.00
alpha1 = 2.0
alpha2 = -2.0
n1 = 0.01
n2 = 5.0
frac = 0.50
                        
Pcut_down = 0.0
Pcut_up = 650000000.0
Time_down = 0.0
Time_up = 15.0
PT_down  = 500.0
PT_up = 45000.0
nTr_down = 1.0
nTr_up = 1000.0

dataName      = '../data/config_LbLcPi.txt'

# DATA FILES
# MISCELLANEOUS
bName = 'B_{s}'


#------------------------------------------------------------------------------
def fitCombBkg( debug, var , mode, modeDs, merge, BDTG, configName, WS) :

    BDTGTS = TString(BDTG)
    if  BDTGTS == "BDTGA":
        configName = "Bs2DsPiConfigForNominalMassFitBDTGA"
    elif BDTGTS == "BDTGC":
        configName = "Bs2DsPiConfigForNominalMassFitBDTGC"
    elif BDTGTS== "BDTG1":
        configName = "Bs2DsPiConfigForNominalMassFitBDTG1"
    elif BDTGTS== "BDTG2":
        configName = "Bs2DsPiConfigForNominalMassFitBDTG2"
    elif BDTGTS== "BDTG3":
        configName = "Bs2DsPiConfigForNominalMassFitBDTG3"
                                                                            
    myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
    myconfigfile = myconfigfilegrabber()
    
    print "=========================================================="
    print "PREPARING WORKSPACE IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
    for option in myconfigfile :
        if option == "constParams" :
            for param in myconfigfile[option] :
                print param, "is constant in the fit"
        else :
            print option, " = ", myconfigfile[option]
    print "=========================================================="
                                                                
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
    
    dataTS = TString(dataName)
    mVarTS = TString("lab0_MassHypo_LcPi_LambdaFav")
    mdVarTS = TString("lab2_MM")
    tVarTS = TString("lab0_LifetimeFit_ctau")
    tagVarTS = TString("lab0_BsTaggingTool_TAGDECISION_OS")
    tagOmegaVarTS = TString("lab0_BsTaggingTool_TAGOMEGA_OS")
    idVarTS = TString("lab1_ID")
    modeTS = TString(mode)
    mProbVarTS = TString("lab1_PIDK")
    modeTSDs = TString(modeDs)
    
    if modeTSDs == "KPiPi":
        mVarTS = TString("lab0_MassHypo_LcPi_LambdaSup")

    print mVarTS

    BDTGTS = TString(BDTG)
    if  BDTGTS == "BDTGA":
        BDTG_down = 0.3
        BDTG_up = 1.0
    elif BDTGTS == "BDTGC":
        BDTG_down = 0.5
        BDTG_up= 1.0
    elif BDTGTS== "BDTG1":
        BDTG_down = 0.3
        BDTG_up= 0.7
    elif BDTGTS== "BDTG2":
        BDTG_down = 0.7
        BDTG_up= 0.9
    elif BDTGTS== "BDTG3":
        BDTG_down = 0.9
        BDTG_up= 1.0
        
    print "BDTG Range: (%f,%f)"%(BDTG_down,BDTG_up)
                                                                                                    

    PIDcut = 150
    obsTS = mVarTS   
    modeDsTS=TString(modeDs)
    Dmass_down = 1930
    Dmass_up = 2015
    Bmass_down = 5500
    Bmass_up = 6000

    if ( modeDsTS == "NonRes" or modeDsTS == "KstK" or modeDsTS == "PhiPi" or modeDsTS == "All"):
        if WS:
            nameTS = TString("#")+modeTS+TString(" KKPi ")+modeDsTS+ TString(" WS")
        else:
            nameTS = TString("#")+modeTS+TString(" KKPi ")+modeDsTS
        if modeDsTS == "NonRes" :
            modeDsTS2 = "nonres"
            index = 0
        elif modeDsTS == "KstK":
            modeDsTS2 = "kstk"
            index = 2
        elif modeDsTS == "PhiPi":
            modeDsTS2 = "phipi"
            index = 1
        else:
            modeDsTS2 = "kkpi"
            index = 1                            
    else:
        if WS:
            nameTS = TString("#")+modeTS+TString(" ")+modeDsTS+TString(" WS") 
        else:
            nameTS = TString("#")+modeTS+TString(" ")+modeDsTS
        if modeDsTS == "KPiPi" :
            modeDsTS2 = "kpipi"
            index = 3
        elif modeDsTS == "PiPiPi":
            modeDsTS2 = "pipipi"
            index = 4
        else:
            modeDsTS2 = "kkpi"
            index = 1
            
    print nameTS
    print index
    if modeTS == "BDPi":
        index = 0
        
    sigma1Name = TString("sigma1") #TString("BsDsPi_") + BDTGTS + TString ("_sigma1")
    sigma2Name = TString("sigma2") #TString("BsDsPi_") + BDTGTS + TString ("_sigma2")
    n1Name = TString("n1") #TString("BsDsPi_") + BDTGTS + TString ("_n1")
    n2Name = TString("n2") #TString("BsDsPi_") + BDTGTS + TString ("_n2")
    alpha1Name = TString("alpha1") #TString("BsDsPi_") + BDTGTS + TString ("_alpha1")
    alpha2Name = TString("alpha2") #TString("BsDsPi_") + BDTGTS + TString ("_alpha2")
    fracName = TString("frac") #TString("BsDsPi_") + BDTGTS + TString ("_frac")
    print sigma1Name
    print sigma2Name
    print n1Name
    print n2Name
    print alpha1Name
    print alpha2Name
    print fracName
    
    workspace = MassFitUtils.ObtainData(dataTS, nameTS,
                                        PIDcut,
                                        Pcut_down, Pcut_up,
                                        BDTG_down, BDTG_up,
                                        Dmass_down, Dmass_up,
                                        Bmass_down, Bmass_up,
                                        Time_down, Time_up,
                                        mVarTS, mdVarTS, tVarTS, tagVarTS,
                                        tagOmegaVarTS, idVarTS,
                                        mProbVarTS,
                                        modeTS, false, NULL, debug)
    
    workspace.Print("v")
    mass = GeneralUtils.GetObservable(workspace,obsTS, debug)
    observables = RooArgSet( mass )
    
    
    data= []
    nEntries = []
    sample = [TString("up"),TString("down")]
    if merge:
        bound = 1
    else:    
        bound = 2
        
        
    for i in range(0,2):
        datasetTS = TString("dataSet")+modeTS+TString("_")+sample[i]+TString("_")+modeDsTS2
        data.append(GeneralUtils.GetDataSet(workspace,datasetTS, debug))
        nEntries.append(data[i].numEntries())
        print "Data set: %s with number of events: %s"%(data[i].GetName(),nEntries[i])
    #exit(0)    
    if merge:
        bound = 1
        sample = [TString("both"),TString("both")]
    else:
        bound =2

    sam = RooCategory("sample","sample")
    for i in range(0, bound):
        sam.defineType(sample[i].Data())
        
    if merge:
        data[0].append(data[1])
        nEntries[0] = nEntries[0] + nEntries[1]
        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(sam),
                              RooFit.Import(sample[0].Data(),data[0]))
        
    else:
        combData = RooDataSet("combData","combined data",RooArgSet(observables),
                              RooFit.Index(sam),
                              RooFit.Import(sample[0].Data(),data[0]),
                              RooFit.Import(sample[1].Data(),data[1]))
        
        
    mean = 5600
    c = -0.0001
    c2 = -0.011
    sigma1Var =  RooRealVar( "sigma1", "sigma1", myconfigfile[sigma1Name.Data()][index], 1.0, 30.0)
    sigma2Var =  RooRealVar( "sigma2", "sigma2", myconfigfile[sigma2Name.Data()][index], 1.0, 30.0)
    n1Var =  RooRealVar( "n1", "n1", myconfigfile[n1Name.Data()][index])
    n2Var =  RooRealVar( "n2", "n2", myconfigfile[n2Name.Data()][index])
    alpha1Var =  RooRealVar( "alpha1", "alhpa1", myconfigfile[alpha1Name.Data()][index])
    alpha2Var =  RooRealVar( "alpha2", "alpha2", myconfigfile[alpha2Name.Data()][index])
    fracVar   =  RooRealVar( "frac",   "frac",    myconfigfile[fracName.Data()][index])
    


    #sigma1Var =  RooRealVar( "sigma1", "sigma1", 10.0, 5.0, 30.0)
    #sigma2Var =  RooRealVar( "sigma2", "sigma2", 10.0, 5.0, 30.0)
    #n1Var =  RooRealVar( "n1", "n1", 10.0, 0, 50.0)
    #n2Var =  RooRealVar( "n2", "n2", 10.0, 0, 50.0)
    #alpha1Var =  RooRealVar( "alpha1", "alhpa1", -2.0, -5.0, 0.0)
    #alpha2Var =  RooRealVar( "alpha2", "alpha2",  2.0,  0.0, 5.0)
    #fracVar   =  RooRealVar( "frac",   "frac",    0.5,  0.0, 1.0)

    meanVar   =  [RooRealVar( "DblCBPDF_mean_up" ,  "mean",    mean,   mean-200, mean+200, "MeV/c^{2}"),
                  RooRealVar( "DblCBPDF_mean_down" ,  "mean",    mean,    mean-200, mean+200, "MeV/c^{2}")]
      
    c2Var =  RooRealVar( "c2Var", "c2Var",  c2,  -0.1,  0, "MeV/c^{2}")
    frac2Var   =  RooRealVar( "frac2",   "frac2",    0.5, 0.0, 1.0)
    c1Var =  RooRealVar( "c1Var", "c1Var",  c,  -0.1,  0, "MeV/c^{2}")
              
    nCombBkgEvts = []
    nSigEvts = []
    nSig = []
    nCombBkg = []
    sigPDF = []
    combBkgPDF = []
    sigEPDF = []
    combBkgEPDF = []
    TotEPDF = []
    
    for i in range(0,bound):
        nSigEvts.append(0.9*nEntries[i])
        nameSig = TString("nSignal_")+sample[i]
        nSig.append(RooRealVar( nameSig.Data(), nameSig.Data(), nSigEvts[i], 0.3*nEntries[i], nEntries[i]))
        nCombBkgEvts.append(0.1*nEntries[i])
        nameCombBkg = TString("nCombBkg_")+sample[i]
        nCombBkg.append(RooRealVar( nameCombBkg.Data(), nameCombBkg.Data(), nCombBkgEvts[i], 0.2*nEntries[i], 0.8*nEntries[i]))
                
        nameExp = TString("Exp")
        nameGauss = TString("Gauss")
        nameAdd = TString("Add")
        combBkgPDF.append(RooExponential(nameExp.Data(), nameExp.Data(), mass, c1Var))
        sigPDF.append(Bs2Dsh2011TDAnaModels.buildDoubleCBEPDF_sim(mass, meanVar[i], sigma1Var, alpha1Var, n1Var, sigma2Var,
                                                                   alpha2Var, n2Var, fracVar, nSig[i], sample[i].Data(), bName, debug ))
        #sigPDF.append(RooAddPdf(nameAdd.Data(), nameAdd.Data(), sigPDF1[i], sigPDF2[i], frac2Var))
                               
        nameEPDF = TString("SignalEPDF_")+sample[i]
        sigEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), sigPDF[i]  , nSig[i]  ))
        nameEPDF = TString("CombBkgEPDF_")+sample[i]
        combBkgEPDF.append(RooExtendPdf( nameEPDF.Data() , nameEPDF.Data(), combBkgPDF[i]  , nCombBkg[i]  ))

                
        TotEPDF.append(RooAddPdf(nameAdd.Data(), nameAdd.Data(), RooArgList(sigEPDF[i], combBkgEPDF[i])))

       

    totPDF = RooSimultaneous("simPdf","simultaneous pdf",sam)
    for i in range(0,bound):
        totPDF.addPdf(TotEPDF[i], sample[i].Data())
               
                    
    # Instantiate and run the fitter
    c = TString("no")
    if( c == "yes"):
        nll= RooNLLVar("nll","-log(sig)",totPDF,combData, RooFit.NumCPU(4));

        pll  = RooProfileLL("pll",  "",  nll, RooArgSet(sigma1Var));
        pll1 = RooProfileLL("pll1", "",  nll, RooArgSet(sigma2Var));
        pll2 = RooProfileLL("pll2", "",  nll, RooArgSet(alpha1Var));
        pll3 = RooProfileLL("pll3", "",  nll, RooArgSet(alpha2Var));
        pll4 = RooProfileLL("pll4", "",  nll, RooArgSet(n1Var));
        pll5 = RooProfileLL("pll5", "",  nll, RooArgSet(n2Var));
    #pll6 = RooProfileLL("pll6", "",  nll, RooArgSet(*cbmean1));
        pll7 = RooProfileLL("pll7", "",  nll, RooArgSet(fracVar));
    

        hsigma1 = pll.createHistogram("hsigma1",sigma1Var,RooFit.Binning(40));
        hsigma1.SetLineColor(kBlue);
        hsigma1.SetLineWidth(2);
        hsigma1.SetTitle("Likelihood Function - Sigma1");

        hsigma2 = pll1.createHistogram("hsigma2",sigma2Var,RooFit.Binning(40));
        hsigma2.SetLineColor(kBlue);
        hsigma2.SetLineWidth(2);
        hsigma2.SetTitle("Likelihood Function - Sigma2");


        halpha1 = pll2.createHistogram("halpha1",alpha1Var,RooFit.Binning(40));
        halpha1.SetLineColor(kRed);
        halpha1.SetLineWidth(2);
        halpha1.SetTitle("Likelihood Function - Alpha1");
    
        halpha2 = pll3.createHistogram("halpha2",alpha2Var,RooFit.Binning(40));
        halpha2.SetLineColor(kRed);
        halpha2.SetLineWidth(2);
        halpha2.SetTitle("Likelihood Function - Alpha2");


        hn1 = pll4.createHistogram("hn1",n1Var,RooFit.Binning(40));
        hn1.SetLineColor(kGreen);
        hn1.SetLineWidth(2);
        hn1.SetTitle("Likelihood Function - N1");

        hn2 = pll5.createHistogram("hn2",n2Var,RooFit.Binning(40));
        hn2.SetLineColor(kGreen);
        hn2.SetLineWidth(2);
        hn2.SetTitle("Likelihood Function - N2");
        
        hfrac = pll7.createHistogram("hfrac",fracVar,RooFit.Binning(40));
        hfrac.SetLineColor(42);
        hfrac.SetLineWidth(2);
        hfrac.SetTitle("Likelihood Function - Fraction");
    
        m1 = RooMinuit(nll);
        
        m1.setVerbose(kFALSE);
        m1.setLogFile("out.log");
        
        m1.setStrategy(2);
        m1.simplex();
        m1.migrad();
    
        m1.minos();
        m1.hesse();
        
        result=m1.save("result","result");
        result.Print();

        like = TCanvas("like", "like", 1200, 800);
        like.Divide(4,2)
        like.cd(1)
        hsigma1.Draw()
        like.cd(5)
        hsigma2.Draw()
        like.cd(2)
        halpha1.Draw()
        like.cd(6)
        halpha2.Draw()
        like.cd(3)
        hn1.Draw()
        like.cd(7)
        hn2.Draw()
        like.cd(8)
        hfrac.Draw()
        like.Update()
        n = TString("likelihood_BsDsPi.pdf")
        like.SaveAs(n.Data())
    

    else:    
   
        fitter = FitMeTool( debug )
        
        fitter.setObservables( observables )
        
        fitter.setModelPDF( totPDF )
        
        fitter.setData(combData) 
        
        plot_init   = options.initvars         and ( options.wsname != None )
        plot_fitted = ( not options.initvars ) and ( options.wsname != None )
        
        if plot_init :
            fitter.saveModelPDF( options.wsname )
            fitter.saveData ( options.wsname )
    
        fitter.fit(True, RooFit.Optimize(0), RooFit.Strategy(2),  RooFit.InitialHesse(True)) #RooFit.Verbose(True), RooFit.InitialHesse(True))
            
        if plot_fitted :
            fitter.saveModelPDF( options.wsname )
            fitter.saveData ( options.wsname )

        gROOT.SetStyle( 'Plain' )
    
        gStyle.SetOptLogy(1)

        result = fitter.getFitResult()
        result.Print()
        model = fitter.getModelPDF()
        
    
        integral = model.createIntegral(observables,"all")
        integralVal = integral.getVal()
        print "Integral %f"%(integralVal)

        del fitter

#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )
parser.add_option( '-s', '--save',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   help = 'save the model PDF and generated dataset to file "WS_WSNAME.root"'
                   )
parser.add_option( '-i', '--initial-vars',
                   dest = 'initvars',
                   action = 'store_true',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )
parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_MassFitConsD_M',
                   help = 'set observable '
                   )

parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   default = 'LbLcPi',
                   help = 'set observable '
                   )
parser.add_option( '--modeDs',
                   dest = 'modeDs',
                   default = 'KKPi',
                   help = 'set observable '
                   )
parser.add_option( '--merge',
                   action = 'store_true',
                   dest = 'merge',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )

parser.add_option( '--WS',
                   action = 'store_true',
                   dest = 'WS',
                   default = False,
                   help = 'save the model PDF parameters before the fit (default: after the fit)'
                   )

parser.add_option( '--BDTG',
                   dest = 'BDTG',
                   default = 'BDTGA',
                   help = 'Set BDTG range '
                   )

parser.add_option( '--configName',
                   dest = 'configName',
                   default = 'CombBkgConfigForNominalMassFit')

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()

    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )

    import sys
    sys.path.append("../data/")
      
    fitCombBkg(options.debug, options.var, options.mode, options.modeDs,
               options.merge, options.BDTG, options.configName, options.WS)

# -----------------------------------------------------------------------------
