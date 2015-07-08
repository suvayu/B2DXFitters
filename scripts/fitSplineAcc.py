# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to compare datas or pdfs                                    #
#                                                                             #
#   Example usage:                                                            #
#      python comparePDF.py                                                   #
#                                                                             #
#   Author: Agnieszka Dziurda                                                 #
#   Date  : 28 / 06 / 2012                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
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
from B2DXFitters import *
from ROOT import *

from optparse import OptionParser
from math     import pi, log
import os, sys, gc

gROOT.SetBatch()

P_down = 0.0
P_up = 650000000.0
PT_down  = 500.0
PT_up = 45000.0
nTr_down = 15.0
nTr_up = 1000.0
Terr_down = 0.005
Terr_up = 0.1

tauH = 1.536875
tauL = 1.407125
gammaH = 1.0/tauH
gammaL = 1.0/tauL
gamma = (gammaH + gammaL) / 2.0
tau = 1.0 / gamma
dgamma = gammaH - gammaL

dataName      = '../data/config_fitSignal.txt'


#------------------------------------------------------------------------------
def runFitSplineAcc( debug, var , mode, modeDs, spline, read, fileNameIn, fileNameOut,
                     workName,BDTG_down,BDTG_up,Time_down,Time_up ) :

    #convert to floats
    BDTG_down = float(BDTG_down)
    BDTG_up = float(BDTG_up)
    Time_down = float(Time_down)
    Time_up = float(Time_up)
    
    RooAbsData.setDefaultStorageType(RooAbsData.Tree)
    
    plotSettings = PlotSettings("plotSettings","plotSettings", "PlotLbLcPi", "pdf", 100, true, false, true)
    plotSettings.Print("v")
    
    MDSettings = MDFitterSettings("MDSettings","MDFSettings")
    
    MDSettings.SetMassBVar(TString("lab0_MassFitConsD_M"))
    MDSettings.SetMassDVar(TString("lab2_MM"))
    MDSettings.SetTimeVar(TString("lab0_LifetimeFit_ctau"))
    MDSettings.SetTerrVar(TString("lab0_LifetimeFit_ctauErr"))
    MDSettings.SetIDVar(TString("lab1_ID"))
    MDSettings.SetPIDKVar(TString("lab1_PIDK"))
    MDSettings.SetBDTGVar(TString("BDTGResponse_1"))
    MDSettings.SetMomVar(TString("lab1_P"))
    MDSettings.SetTrMomVar(TString("lab1_PT"))
    MDSettings.SetTracksVar(TString("nTracks"))
    MDSettings.SetAddMCCuts(TString("lab2_TAU>0"))
    MDSettings.SetAddDataCuts(TString("lab2_TAU>0"))

    dataTS = TString(dataName)
    modeTS = TString(mode)
    if modeTS  == "BsDsK":
        PIDcut = 5
        MDSettings.SetPIDKRange(log(PIDcut),log(150))
    else:
        PIDcut = 0
        MDSettings.SetPIDKRange(PIDcut,150)
    obsTS = TString(var)
    if modeTS == "BDPi":
        modeDsTS = TString("KPiPi")
        Dmass_down = 1770 #1830 #1930
        Dmass_up = 1920 #2015
        Bmass_down = 5000
        Bmass_up = 5500
        if ( obsTS == "lab2_MM"):
            mean  =  1869 #1968.49
        else:
            mean  = 5279 #367.51

    else:
        modeDsTS=TString(modeDs)
        Dmass_down = 1930
        Dmass_up = 2015
        Bmass_down = 5300
        Bmass_up = 5800
        if ( obsTS == "lab2_MM"):
            mean  =  1968.49
        else:
            mean  = 5367.51
            
                                                                
    MDSettings.SetMassBRange(Bmass_down, Bmass_up)
    MDSettings.SetMassDRange(Dmass_down, Dmass_up)
    MDSettings.SetTimeRange(Time_down,  Time_up )
    MDSettings.SetMomRange(P_down, P_up  )
    MDSettings.SetTrMomRange(PT_down, PT_up  )
    MDSettings.SetTracksRange(nTr_down, nTr_up  )
    MDSettings.SetBDTGRange( BDTG_down, BDTG_up  )
    MDSettings.SetPIDBach(PIDcut)
    MDSettings.SetTerrRange(Terr_down, Terr_up  )
    MDSettings.SetIDRange( -1000.0, 1000.0 )
    
    MDSettings.SetLumDown(0.59)
    MDSettings.SetLumUp(0.44)
    MDSettings.SetLumRatio()

    if modeDsTS == "HHHPi0":
	    MDSettings.SetNotation(0)
	    MDSettings.SetMassBVar(TString("Bs_MassConsDs_M"))
	    MDSettings.SetMassDVar(TString("Ds_MM"))
	    MDSettings.SetTimeVar(TString("Bs_LifetimeFit_ctau"))
	    MDSettings.SetTerrVar(TString("Bs_LifetimeFit_ctauErr"))
	    MDSettings.SetIDVar(TString("Bac_ID"))
	    MDSettings.SetPIDKVar(TString("Bac_PIDK"))
	    MDSettings.SetBDTGVar(TString(""))
	    MDSettings.SetMomVar(TString("Bac_P"))
	    MDSettings.SetTrMomVar(TString("Bac_PT"))
	    MDSettings.SetTracksVar(TString("nTracks"))
	    obsTS = TString("Bs_LifetimeFit_ctau")
    MDSettings.Print("v")
    workspace = RooWorkspace("workspace","workspace")

    if read == false:
        wD = 2*(0.59)/(0.59+0.44) #Multiply by 2 to make weights closer to 1+-epsilon 
        wU = 2*(0.44)/(0.59+0.44) #Multiply by 2 to make weights closer to 1+-epsilon
        if modeDsTS == "All":
            mDs = ["NonRes", "PhiPi", "KstK", "KPiPi", "PiPiPi"]
            if mode == "BsDsPi" :
                if (BDTG_down == 0.3 and BDTG_up == 1.0) :
                    yieldsindatafit = [4592.,10097.,7177.,1641.,4249.]
                    sizeofmcdataset = [65688.,139404.,107608.,52179.,80699.]
                elif (BDTG_down == 0.6 and BDTG_up == 1.0) :
                    yieldsindatafit = [4251.,9287.,6487.,1492.,3826.]
                    sizeofmcdataset = [60952.,130734.,98981.,48212.,74180.]
                elif (BDTG_down == 0.9 and BDTG_up == 1.0) :
                    yieldsindatafit = [2105.,4963.,3123.,733.,1845.]
                    sizeofmcdataset = [33203.,73539.,51598.,25787.,38566.]
                elif (BDTG_down == 0.3 and BDTG_up == 0.9) :
                    yieldsindatafit = [2387.,4967.,3948.,868.,2310.]
                    sizeofmcdataset = [31075.,62406.,53827.,25240.,40364.] 
                datatotal = sum(yieldsindatafit)
                mctotal = sum(sizeofmcdataset)
                modeweights = []
                for i in range(0,5):
                    modeweights.append(yieldsindatafit[i]*mctotal/(sizeofmcdataset[i]*datatotal))
            else :
                if (BDTG_down == 0.3 and BDTG_up == 1.0) :
                    yieldsindatafit = [305.,569.,469.,106.,297.]
                    sizeofmcdataset = [68658.,146411.,112245.,16859.,79436.]
                elif (BDTG_down == 0.6 and BDTG_up == 1.0) :
                    yieldsindatafit = [278.,512.,426.,94.,276.]
                    sizeofmcdataset = [63936.,137556.,103223.,15632.,73021.]
                elif (BDTG_down == 0.9 and BDTG_up == 1.0) :
                    yieldsindatafit = [138.,273.,224.,45.,118.]
                    sizeofmcdataset = [34958.,78046.,54088.,8317.,38155.]
                elif (BDTG_down == 0.3 and BDTG_up == 0.9) :
                    yieldsindatafit = [163.,283.,244.,58.,171.]
                    sizeofmcdataset = [32154.,64877.,55871.,8160.,39466.]
                datatotal = sum(yieldsindatafit)
                mctotal = sum(sizeofmcdataset)
                modeweights = []
                for i in range(0,5):
                    modeweights.append(yieldsindatafit[i]*mctotal/(sizeofmcdataset[i]*datatotal))
            wGD = modeweights
            wGU = modeweights
        else:
            mDs = [modeDsTS]
            wGD = [1.0]
            wGU = [1.0]
        i=0
    
        for m in mDs:
            nameTS = TString("#Signal ")+modeTS+TString(" ")+TString(m)
            print nameTS
            print "global weight for down = %lf, global weight for up = %lf"%(wD*wGD[i],wU*wGU[i])
            workspace = MassFitUtils.ObtainSignal(dataTS, nameTS,
                                                  MDSettings, modeTS, false, false, workspace, false,
                                                  wD*wGD[i], wU*wGU[i], plotSettings, debug)
            i+=1

        extrastring = modeDs+"_"
        if modeDsTS=="All" :
            extrastring = ""
        if mode == "BsDsPi":    
            GeneralUtils.SaveWorkspace(workspace,TString(fileNameOut+"work_dspi_spline_"+extrastring+str(BDTG_down)+"_"+str(BDTG_up)+"_"+str(Time_down)+"_"+str(Time_up)+".root"), debug)
        else:
            GeneralUtils.SaveWorkspace(workspace,TString(fileNameOut+"work_dsk_spline_"+extrastring+str(BDTG_down)+"_"+str(BDTG_up)+"_"+str(Time_down)+"_"+str(Time_up)+".root"), debug)
    
    
    else:
        extrastring = modeDs+"_"
        if modeDsTS=="All" :
            extrastring = ""
        if mode == "BsDsPi":
            workspace = GeneralUtils.LoadWorkspace(TString(fileNameIn+"work_dspi_spline_"+extrastring+str(BDTG_down)+"_"+str(BDTG_up)+"_"+str(Time_down)+"_"+str(Time_up)+".root"), TString(workName),debug)
        else :
            workspace = GeneralUtils.LoadWorkspace(TString(fileNameIn+"work_dsk_spline_"+extrastring+str(BDTG_down)+"_"+str(BDTG_up)+"_"+str(Time_down)+"_"+str(Time_up)+".root"), TString(workName),debug)
        workspace.Print("v")

    time = GeneralUtils.GetObservable(workspace,obsTS, debug)
    weight = GeneralUtils.GetObservable(workspace,TString("weights"), debug)
    observables = RooArgSet( time, weight )
    
    if modeDsTS == "All":
        mDs2 = ["nonres","phipi","kstk","kpipi","pipipi"]
    else:
        modeDsTS = TString(modeDs.lower())
        temp = GeneralUtils.CheckDMode(modeDsTS)
        if temp == "kkpi" or temp == "":
            temp = GeneralUtils.CheckKKPiMode(modeDsTS)
        mDs2 = [ temp ]    

    data= []
    nEntries = []
    sample = [TString("up"),TString("down")]

    for m in mDs2:
        for i in range(0,2):
            datasetTS = TString("dataSetMC_")+modeTS+TString("_")+sample[i]+TString("_")+TString(m)
            data.append(GeneralUtils.GetDataSet(workspace,datasetTS, debug))
            size = data.__len__()
            nEntries.append(data[size-1].numEntries())
            print "Data set: %s with number of events: %s"%(data[size-1].GetName(),nEntries[size-1])
        
    sample = [TString("both"),TString("both")]
    if modeDsTS == "All":
        for i in range(1,10):
            print "Add data set: %s"%(data[i].GetName())
            data[0].append(data[i])
    else:
        data[0].append(data[1])
        data[0].Print()

    time.setBins(200)
    dataF = RooDataSet("data_fit", "data_fit", data[0].get(), RooFit.Import(data[0]), RooFit.WeightVar("weights"))
    dataF_binned = RooDataHist("data_fit_binned","data_fit_binned",RooArgSet(time,weight),dataF)
    
    #terr = GeneralUtils.GetObservable(workspace,TString("lab0_LifetimeFit_ctauErr"), debug)
    #nameTerrPDF = "sigTimeErrorPdf_"+mode
    #terrpdf = GeneralUtils.CreateHistPDF(dataF, terr, TString(nameTerrPDF), 40, debug)
    #workout = RooWorkspace("workspace","workspace")
    #getattr(workout,'import')(terrpdf)
    #getattr(workout,'import')(dataF)
    #saveName = "template_MC_Terr_"+mode+".root"
    #workout.Print()
    #GeneralUtils.SaveWorkspace(workout,TString(saveName), debug)
    #exit(0)
    nEntriesF  = dataF.numEntries()
    print "Data set: %s with number of events: %s"%(dataF.GetName(),nEntriesF)
    #exit(0)
    
    if spline:
        binName = TString("splineBinning")
        TimeBin = RooBinning(Time_down,Time_up,binName.Data())
        if (Time_down < 0.5) :
            TimeBin.addBoundary(0.5)
        elif (Time_down < 0.6) :
            TimeBin.addBoundary(0.6)
        else :
            TimeBin.addBoundary(0.8)
        TimeBin.addBoundary(1.0)
        TimeBin.addBoundary(1.5)
        TimeBin.addBoundary(2.0)
        TimeBin.addBoundary(3.0)
        TimeBin.addBoundary(12.0) #(was 10)
        TimeBin.removeBoundary(Time_down)
        TimeBin.removeBoundary(Time_up)
        TimeBin.removeBoundary(Time_down)
        TimeBin.removeBoundary(Time_up)
        
        var1 = RooRealVar("var1", "var1", 0.16, 0.0, 10.0) #1.56933e-01) #1.77520e-01, 0.0, 3.0) 
        var2 = RooRealVar("var2", "var2", 0.27, 0.0, 10.0) #2.69653e-01) #2.89603e-01, 0.0, 3.0)  
        var3 = RooRealVar("var3", "var3", 0.65, 0.0, 10.0) #6.48147e-01) #6.79455e-01, 0.0, 3.0)  
        var4 = RooRealVar("var4", "var4", 1.11, 0.0, 10.0) #1.11342e+00) #1.11726e+00, 0.0, 3.0) 
        var5 = RooRealVar("var5", "var5", 1.23, 0.0, 10.0) #1.23416e+00) #1.23189e+00, 0.0, 3.0) 
        var6 = RooRealVar("var6", "var6", 1.28, 0.0, 10.0) 
        var8 = RooRealVar("var8", "var8", 1.00, 0.0, 10.0)  
        if (BDTG_down > 0.6) :
            TimeBin.addBoundary(6)
            TimeBin.addBoundary(11)
            TimeBin.addBoundary(14)
            TimeBin.removeBoundary(12.0)
            TimeBin.removeBoundary(12.0)
            time.setBinning(TimeBin, binName.Data())
            time.setRange(Time_down,Time_up)
            TimeBin.Print("v")
            var9 = RooRealVar("var9","var9",1.0,0.0,10.0)
            listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, time)
            var10 = RooRealVar("var10","var10",1.0)
            var11 = RooAddition("var11","var11", RooArgList(var9,var10), listCoeff)
            Var = RooArgList(var1,var2,var3,var4,var5,var6,var8,var9)
            Var.add(var10)
            Var.add(var11)
        elif (BDTG_up < 1.0) :
            TimeBin.addBoundary(6)
            TimeBin.addBoundary(11)
            TimeBin.removeBoundary(12.0)
            TimeBin.removeBoundary(12.0)
            time.setBinning(TimeBin, binName.Data())
            time.setRange(Time_down,Time_up)
            TimeBin.Print("v")
            listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, time)
            var10 = RooRealVar("var10","var10",1.0)
            var11 = RooAddition("var11","var11", RooArgList(var8,var10), listCoeff)
            Var = RooArgList(var1,var2,var3,var4,var5,var6,var8)
            Var.add(var10)
            Var.add(var11)
        else :
            time.setBinning(TimeBin, binName.Data())
            time.setRange(Time_down,Time_up)
            TimeBin.Print("v")
            listCoeff = GeneralUtils.GetCoeffFromBinning(TimeBin, time)
            var8.setConstant(1)
            var9 = RooAddition("var9","var9", RooArgList(var6,var8), listCoeff) 
            Var = RooArgList(var1,var2,var3,var4,var5,var6,var8,var9)
        
        spl = RooCubicSplineFun("spline", "spline", time, "splineBinning", Var)
        
        if modeTS  == "BsDsPi":
            trm = PTResModels.tripleGausEffModel( time,
                                                  spl,
                                                  1.195,
                                                  0.0,
                                                  2.15934e-02,
                                                  3.71992e-02,
                                                  6.50957e-02,
                                                  3.88398e-01,
                                                  5.55078e-01,
                                                  debug)
        else:
            trm = PTResModels.tripleGausEffModel( time,
                                                  spl,
                                                  1.195,
                                                  0.0,
                                                  2.14295e-02,
                                                  3.68152e-02,
                                                  6.25371e-02,
                                                  3.71673e-01,
                                                  5.57606e-01,
                                                  debug)
            
        
        pdf = RooBDecay('Bdecay', 'Bdecay', time, RooRealConstant.value(tau),
                        RooRealConstant.value(dgamma), RooRealConstant.value(1.0),  RooRealConstant.value(0.0),
                        RooRealConstant.value(0.0),  RooRealConstant.value(0.0),  RooRealConstant.value(0.0),
                        trm, RooBDecay.SingleSided)
    else:
        tacc_beta       = RooRealVar('tacc_beta'    , 'tacc_beta',      0.03,   0.0,  0.50  )
        tacc_exponent   = RooRealVar('tacc_exponent', 'tacc_exponent',  1.9,    0.0,  10.0 )
        tacc_offset     = RooRealVar('tacc_offset'  , 'tacc_offset',    0.008,   -1.0,  10.0 )
        tacc_turnon     = RooRealVar('tacc_turnon'  , 'tacc_turnon',    1.45,    0.0,  10.0 )
        tacc            = PowLawAcceptance('tacc', 'tacc', tacc_turnon, time, tacc_offset, tacc_exponent, tacc_beta)

        
        if modeTS  == "BsDsPi":
            trm = PTResModels.tripleGausResolutionModel( time,
                                                         1.195,
                                                         0.0,
                                                         2.15934e-02,
                                                         3.71992e-02,
                                                         6.50957e-02,
                                                         3.88398e-01,
                                                         5.55078e-01,
                                                         debug)
        else:
            trm = PTResModels.tripleGausResolutionModel( time,
                                                         1.195,
                                                         0.0,
                                                         2.14295e-02,
                                                         3.68152e-02,
                                                         6.25371e-02,
                                                         3.71673e-01,
                                                         5.57606e-01,
                                                         debug)
            
                                                     

        pdfD = RooBDecay('Bdecay_noacc', 'Bdecay_noacc', time, RooRealConstant.value(tau),
                         RooRealConstant.value(dgamma), RooRealConstant.value(1.0),  RooRealConstant.value(0.0),
                         RooRealConstant.value(0.0),  RooRealConstant.value(0.0),  RooRealConstant.value(0.0),
                         trm, RooBDecay.SingleSided)

        pdf = RooEffProd('Bdecay','Bdecay',pdfD,tacc)

        
    myfitresult = pdf.fitTo(dataF_binned, RooFit.Save(1), RooFit.Optimize(2), RooFit.Strategy(2),
                            RooFit.Verbose(True), RooFit.SumW2Error(True), RooFit.Extended(False),
                            RooFit.Offset(True))


    range_dw = time.getMin()
    range_up = time.getMax()

    lhcbtext = TLatex()
    lhcbtext.SetTextFont(132)
    lhcbtext.SetTextColor(1)
    lhcbtext.SetTextSize(0.07)
    lhcbtext.SetTextAlign(12)

    legend = TLegend( 0.62, 0.70, 0.88, 0.88 )

    legend.SetTextSize(0.05)
    legend.SetTextFont(12)
    legend.SetFillColor(4000)
    legend.SetShadowColor(0)
    legend.SetBorderSize(0)
    legend.SetTextFont(132)

    l1 = TLine()
    l1.SetLineColor(kBlue+3)
    l1.SetLineWidth(4)
    l1.SetLineStyle(kSolid)
    legend.AddEntry(l1, "decay", "L")

    l2 = TLine()
    l2.SetLineColor(kRed)
    l2.SetLineWidth(4)
    l2.SetLineStyle(kSolid)
    legend.AddEntry(l2, "acceptance", "L")
                    
        
    frame_m = time.frame()
    frame_m.SetTitle('')
    
    frame_m.GetXaxis().SetLabelSize( 0.05 )
    frame_m.GetYaxis().SetLabelSize( 0.05 )
    frame_m.GetXaxis().SetLabelFont( 132 )
    frame_m.GetYaxis().SetLabelFont( 132 )
    frame_m.GetXaxis().SetLabelOffset( 0.006 )
    frame_m.GetYaxis().SetLabelOffset( 0.006 )
    frame_m.GetXaxis().SetLabelColor( kWhite)
    
    frame_m.GetXaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetTitleSize( 0.05 )
    frame_m.GetYaxis().SetNdivisions(512)
    unit = "[ps]"
    frame_m.GetXaxis().SetTitleOffset( 1.00 )
    frame_m.GetYaxis().SetTitleOffset( 1.10 )
    #frame_m.GetYaxis().SetTitle((TString.Format("#font[12]{Candidates / ( " +
    #                                            str(time.getBinWidth(1))+" "+
    #                                            unit+")}") ).Data())
                                                        
    bin = 100
    dataF.plotOn(frame_m,RooFit.Binning( bin ))
    pdf.plotOn(frame_m, RooFit.LineColor(kBlue+3))
    if modeDsTS == "HHHPi0":
	    rel = 50
    else:
	    rel = 4000
    if spline:
        spl.plotOn(frame_m, RooFit.LineColor(kRed), RooFit.Normalization(rel, RooAbsReal.Relative))
    else:
        tacc.plotOn(frame_m, RooFit.LineColor(kRed), RooFit.Normalization(rel, RooAbsReal.Relative))
    canvas = TCanvas("canvas", "canvas", 1200, 1000)
    canvas.cd()
    pad1 = TPad("upperPad", "upperPad", .050, .22, 1.0, 1.0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(-1)
    pad1.SetFillStyle(0)
    pad1.SetTickx(0);
    pad1.Draw()
    pad1.cd()
    frame_m.GetYaxis().SetRangeUser(0.1,frame_m.GetMaximum()*1.0)
    frame_m.Draw()
    legend.Draw("same")
    lhcbtext.DrawTextNDC(0.50,0.85,"LHCb")
        
        
    canvas.cd()
    pad2 = TPad("lowerPad", "lowerPad", .050, .005, 1.0, .3275)
    pad2.SetBorderMode(0)
    pad2.SetBorderSize(-1)
    pad2.SetFillStyle(0)
    pad2.SetBottomMargin(0.35)
    pad2.SetTickx(0);
    pad2.Draw()
    pad2.SetLogy(0)
    pad2.cd()
    
    gStyle.SetOptLogy(0)
    frame_m.Print("v")
    #exit(0)
    frame_p = time.frame(RooFit.Title("pull_frame"))
    frame_p.Print("v")
    frame_p.SetTitle("")
    frame_p.GetYaxis().SetTitle("")
    frame_p.GetYaxis().SetTitleSize(0.09)
    frame_p.GetYaxis().SetTitleOffset(0.26)
    frame_p.GetYaxis().SetTitleFont(62)
    frame_p.GetYaxis().SetNdivisions(106)
    frame_p.GetYaxis().SetLabelSize(0.12)
    frame_p.GetYaxis().SetLabelOffset(0.006)
    frame_p.GetXaxis().SetTitleSize(0.15)
    frame_p.GetXaxis().SetTitleFont(132)
    frame_p.GetXaxis().SetTitleOffset(0.85)
    frame_p.GetXaxis().SetNdivisions(515)
    frame_p.GetYaxis().SetNdivisions(5)
    frame_p.GetXaxis().SetLabelSize(0.12)
    frame_p.GetXaxis().SetLabelFont( 132 )
    frame_p.GetYaxis().SetLabelFont( 132 )
    frame_p.GetXaxis().SetTitle('#font[12]{#tau(B_{s}) [ps]}')

    pullnameTS = TString("Bdecay_Norm[")+obsTS+TString("]")
    pullname2TS = TString("h_data_fit")
    pullHist  = frame_m.pullHist(pullname2TS.Data(),pullnameTS.Data())
    frame_p.addPlotable(pullHist,"P")

    chi2 = frame_m.chiSquare();
    chi22 = frame_m.chiSquare(pullnameTS.Data(),pullname2TS.Data());
    
    print "chi2: %f"%(chi2)
    print "chi22: %f"%(chi22)
    
    
    axisX = pullHist.GetXaxis()
    Bin = RooBinning(range_dw,range_up,'P')
    Bin.addUniform(bin, range_dw, range_up)
    axisX.Set(Bin.numBins(), Bin.array())
    
    axisY = pullHist.GetYaxis()
    max = 5.0 #axisY.GetXmax()
    min = -5.0 #axisY.GetXmin()
    axisY.SetLabelSize(0.12)
    axisY.SetNdivisions(5)
    axisX.SetLabelSize(0.12)
    
    rangeX = max-min
    zero = max/rangeX
    print "max: %s, min: %s, range: %s, zero:%s"%(max,min,rangeX,zero)
    
    graph = TGraph(2)
    graph.SetMaximum(max)
    graph.SetMinimum(min)
    graph.SetPoint(1,range_dw,0)
    graph.SetPoint(2,range_up,0)
    
    graph2 = TGraph(2)
    graph2.SetMaximum(max)
    graph2.SetMinimum(min)
    graph2.SetPoint(1,range_dw,-3)
    graph2.SetPoint(2,range_up,-3)
    graph2.SetLineColor(kRed)
    
    graph3 = TGraph(2)
    graph3.SetMaximum(max)
    graph3.SetMinimum(min)
    graph3.SetPoint(1,range_dw,3)
    graph3.SetPoint(2,range_up,3)
    graph3.SetLineColor(kRed)
    
    pullHist.GetXaxis().SetLabelFont( 132 )
    pullHist.GetYaxis().SetLabelFont( 132 )
    pullHist.SetTitle("")
                                                             
    frame_p.GetYaxis().SetRangeUser(-5.0,5.0)
    frame_p.Draw()
        
    graph.Draw("same")
    graph2.Draw("same")
    graph3.Draw("same")
    #tex.DrawLatex(0.50,0.30,"m(B_{s} #rightarrow D_{s}#pi) [MeV/c^{2}]")
    
    pad2.Update()
    canvas.Update()
    if spline:
        suf = "spline"
    else:
        suf = "powlaw"

    namePDF = fileNameOut+"data_sPline_"+mode+"_"+modeDs+"_"+suf+"_"+str(BDTG_down)+"_"+str(BDTG_up)+"_"+str(Time_down)+"_"+str(Time_up)+".pdf"    
    nameROOT = fileNameOut+"data_sPline_"+mode+"_"+modeDs+"_"+suf+"_"+str(BDTG_down)+"_"+str(BDTG_up)+"_"+str(Time_down)+"_"+str(Time_up)+".root"
    canvas.SaveAs(namePDF)
    canvas.SaveAs(nameROOT)
    return canvas 
                
#------------------------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
                   action = 'store_true',
                   dest = 'debug',
                   default = False,
                   help = 'print debug information while processing'
                   )

parser.add_option( '-v', '--variable',
                   dest = 'var',
                   default = 'lab0_LifetimeFit_ctau',
                   help = 'set observable '
                   )

parser.add_option( '-m', '--mode',
                   dest = 'mode',
                   default = 'BsDsPi',
                   help = 'set observable '
                   )

parser.add_option( '--BDTG_down',
                    dest = 'BDTG_down',
                    default = '0.3',
                    )

parser.add_option( '--BDTG_up',
                    dest = 'BDTG_up',
                    default = '1.0',
                    )  

parser.add_option( '--Time_down',
                    dest = 'Time_down',
                    default = '0.4',
                    )   

parser.add_option( '--Time_up',
                    dest = 'Time_up',
                    default = '15.0',
                    )

parser.add_option( '--modeDs',
                   dest = 'modeDs',
                   default = 'All',
                   help = 'set observable '
                   )
parser.add_option( '--spline',
                   dest = 'spline',
                   action = 'store_true',
                   default = False,
                   )

parser.add_option( '--read',
                   dest = 'read',
                   action = 'store_true',
                   default = False,
                   )
parser.add_option( '--fileNameIn',
                   dest = 'fileIn',
                   default = '/afs/cern.ch/work/g/gligorov//public/Bs2DsKPlotsForPaper/NominalFit/',
                   help = 'set observable '
                   )

parser.add_option( '--fileNameOut',
                   dest = 'fileOut',
                   default = '/afs/cern.ch/work/g/gligorov//public/Bs2DsKPlotsForPaper/NominalFit/')

parser.add_option( '--workName',
                   dest = 'work',
                   default = 'workspace',
                   help = 'set observable '
                   )

# -----------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) > 0 :
        parser.print_help()
        exit( -1 )
        
        
    import sys
    sys.path.append("../data/")

    runFitSplineAcc( options.debug, options.var, options.mode, options.modeDs, options.spline,
                     options.read, options.fileIn, options.fileOut, options.work,
                     options.BDTG_down,options.BDTG_up,options.Time_down,options.Time_up)
# -----------------------------------------------------------------------------
                                
