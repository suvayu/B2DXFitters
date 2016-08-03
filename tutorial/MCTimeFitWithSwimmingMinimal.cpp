// demonstation file for the swimming acceptance
//
// initial version by Uli, bugs, ugly code, RooSwimmingAcceptance by Manuel
//
// compile and link against ROOT libraries and libB2DXFitters, also add
// "-std=c++11" to C++ compiler flags

// from STL
#include <cassert>
#include <sstream>
#include <utility>
#include <vector>

// from ROOT
#include "TAxis.h"
#include "TCanvas.h"
#include "TFile.h"
#include "TH1.h"
#include "TLatex.h"
#include "TROOT.h"
#include "TTree.h"

// from RooFit
#include "RooArgList.h"
#include "RooArgSet.h"
#include "RooBDecay.h"
#include "RooCategory.h"
#include "RooCmdArg.h"
#include "RooDataHist.h"
#include "RooDataSet.h"
#include "RooAbsDataStore.h"
#include "RooDecay.h"
#include "RooEffProd.h"
#include "RooFitResult.h"
#include "RooLinearVar.h"
#include "RooGaussModel.h"
#include "RooHistPdf.h"
#include "RooPlot.h"
#include "RooRealVar.h"
#include "RooNumIntConfig.h"

#include "RooConstVar.h"
#include "RooExponential.h"
#include "RooGaussian.h"
#include "RooGlobalFunc.h"
#include "RooPlot.h"
#include "RooParamBinning.h"
#include "RooMappedCategory.h"

// from P2VV
//#include "P2VV/RooAbsGaussModelEfficiency.h"
//#include "P2VV/RooBinnedFun.h"
//#include "P2VV/RooGaussEfficiencyModel.h"

// from Project
#include "B2DXFitters/RooAbsGaussModelEfficiency.h"
#include "B2DXFitters/RooBinnedFun.h"
#include "B2DXFitters/RooSwimmingAcceptance.h"
#include "B2DXFitters/RooGaussEfficiencyModel.h"
#include "B2DXFitters/DecRateCoeff.h"

using namespace RooFit;

/// fill the acceptance histogram with the intervals between begin and end
template <typename IT>
void fill_acceptance_histogram(IT begin, IT end, TH1& acceptance,
    ULong64_t n_entries)
{
    const auto lastbin = acceptance.GetNbinsX();
    const auto& ax = *acceptance.GetXaxis();
    const auto min = ax.GetBinLowEdge(1), max = ax.GetBinUpEdge(lastbin);
    const auto w = 1. / n_entries;
    for (; end != begin; ++begin) {
        const auto& iv = *begin;
        // check if completely outside histogram range
        if (iv.second < min || iv.first > max)
            continue;
        assert(iv.first <= iv.second);
        // clamp down interval to acceptance histogram interval
        const auto iv1 = (iv.first < min) ? min : iv.first;
        const auto iv2 = (iv.second > max) ? max : iv.second;
        // find the histogram bins to which this interval contributes
        auto iminbin = ax.FindBin(iv1), imaxbin = ax.FindBin(iv2);
        // get to work on the first and last histogram bins that overlap with
        // the interval (i.e. the bins that are potentially only partially
        // contained in the histogram)
        if (iminbin == imaxbin) {
            // interval fully contained in a single bin
            auto frac = (iv2 - iv1) / ax.GetBinWidth(iminbin);
            acceptance.Fill(ax.GetBinCenter(iminbin), w * frac);
        } else {
            // beginning of interval is from iv.first to bin end of iminbin,
            // end of interval is from bin start of imaxbin to iv.second
            auto frac = (ax.GetBinUpEdge(iminbin) - iv1) / ax.GetBinWidth(iminbin);
            acceptance.Fill(ax.GetBinCenter(iminbin), w * frac);
            frac = (iv2 - ax.GetBinLowEdge(imaxbin)) / ax.GetBinWidth(imaxbin);
            acceptance.Fill(ax.GetBinCenter(imaxbin), w * frac);
        }
        // fill bins completely contained inside the interval
        for (auto i = iminbin + 1; i < imaxbin; ++i) {
            acceptance.Fill(ax.GetBinCenter(i), w);
        }
    }
}

int main(int /* argc */, char* /* argv */[])
{
    // setup for nicer plots
    gROOT->SetStyle("Plain");

    // numerical integrator tuning (not used much, no worries)
    RooAbsReal::defaultIntegratorConfig()->setEpsAbs(1e-9);
    RooAbsReal::defaultIntegratorConfig()->setEpsRel(1e-9);
    RooAbsReal::defaultIntegratorConfig()->getConfigSection("RooAdaptiveGaussKronrodIntegrator1D").setCatLabel("method", "15Points");
    RooAbsReal::defaultIntegratorConfig()->getConfigSection("RooAdaptiveGaussKronrodIntegrator1D").setRealValue("maxSeg", 1000);
    RooAbsReal::defaultIntegratorConfig()->method1D().setLabel("RooAdaptiveGaussKronrodIntegrator1D");
    RooAbsReal::defaultIntegratorConfig()->method1DOpen().setLabel("RooAdaptiveGaussKronrodIntegrator1D");

    ////////////////////////////////////////////////////////////////////////
    // CREATE OBSERVABLES
    ////////////////////////////////////////////////////////////////////////
    // create dtf obersables
    RooRealVar obsTime("lab0_TAU",
        "t_{#kern[-0.3]{B}_{#kern[-0.3]{s}}^{#kern[-0.3]{0}}}",
        0.0002, 0.015, "");
    RooRealVar obsTimeError(
        "lab0_LifetimeFit_ctauErr_flat",
        "#sigma_{t_{#kern[-0.3]{B}_{#kern[-0.3]{s}}^{#kern[-0.3]{0}}}}", 0.0005,
        0.1, "");
    RooRealVar obsMass("lab0_LifetimeFit_M_flat", "lab0_LifetimeFit_M_flat", 0);

    // create turning point observables
    RooCategory obsNTP("Stripping_Trigger_nintervals", "Stripping_Trigger_nintervals");
    obsNTP.defineType("1", 1);
    obsNTP.defineType("2", 2); obsNTP.defineType("3", 3);
    obsNTP.defineType("4", 4); obsNTP.defineType("5", 5);
    obsNTP.defineType("6", 6); obsNTP.defineType("7", 7);
    obsNTP.defineType("8", 8);
    RooMappedCategory ntp("ntp", "ntp", obsNTP, "unknown", 0);
    ntp.map("1", "2", 2); ntp.map("2", "4", 4);
    ntp.map("3", "6", 6); ntp.map("4", "8", 8); ntp.map("5", "10", 10);
    ntp.map("6", "12", 12); ntp.map("7", "14", 14); ntp.map("8", "16", 16);
    RooRealVar obsTPOnTau1("Stripping_Trigger_tp_tau_2_tp_on_1",
        "Stripping_Trigger_tp_tau_2_tp_on_1", 0.0002, 0.015);
    RooRealVar obsTPOffTau1("Stripping_Trigger_tp_tau_2_tp_off_1",
        "Stripping_Trigger_tp_tau_2_tp_off_1", 0.0002,
        0.015);
    RooRealVar obsTPOnTau2("Stripping_Trigger_tp_tau_2_tp_on_2",
        "Stripping_Trigger_tp_tau_2_tp_on_2", -10, 1000);
    RooRealVar obsTPOffTau2("Stripping_Trigger_tp_tau_2_tp_off_2",
        "Stripping_Trigger_tp_tau_2_tp_off_2", -10, 1000);
    RooRealVar obsTPOnTau3("Stripping_Trigger_tp_tau_2_tp_on_3",
        "Stripping_Trigger_tp_tau_2_tp_on_3", -10, 1000);
    RooRealVar obsTPOffTau3("Stripping_Trigger_tp_tau_2_tp_off_3",
        "Stripping_Trigger_tp_tau_2_tp_off_3", -10, 1000);

    // set of per-event swimming observables
    RooArgSet observables_swimming(obsTPOnTau1, obsTPOffTau1, obsTPOnTau2,
        obsTPOffTau2, obsTPOffTau3, obsTPOnTau3, obsNTP);

    ////////////////////////////////////////////////////////////////////////
    // CREATE OBS TIME RANGES
    ////////////////////////////////////////////////////////////////////////
    // create argset time and number of turning points
    RooArgSet observables_time(obsTime, obsTimeError);

    // create argset of all observables
    RooArgSet observables(observables_time, observables_swimming);

    ////////////////////////////////////////////////////////////////////////
    // READ DATAFILE AND CREATE DATASET
    ////////////////////////////////////////////////////////////////////////
    // set tree name (same for all tuples below)
    const std::string tree_name = "DecayTree";

    // location of files
    const std::string dir = "/afs/cern.ch/work/u/ueitschb/public/Dspi_Swimming_Manuel";
    //const std::string dir = "."; // if you have local copies

    // choose a tuple file:
    // new big swum tuples DsPi
    //const std::string datafile = "SwimBs2DsPi_DVTuple_Merged_flat_NoMulCan_TPs.root";
    // new big swum tuples DsPi where first overlap on comes from trigger
    //const std::string datafile = "SwimBs2DsPi_DVTuple_Merged_flat_NoMulCan_TPs_1stfromTrig.root";
    // new big swum tuples DsPi where first overlap on comes from stripping
    //const std::string datafile = "SwimBs2DsPi_DVTuple_Merged_flat_NoMulCan_TPs_1stfromStrip.root";
    // newest big swum MC tuple DsPi, with bugfix concerning swimming of offline
    // selection
    const std::string datafile = "SwimBs2DsPi_NoPVRefitInSel_DVTuple_Merged_flat_NoMulCan_TriggerReq_TPsTau_2_ns.root";

    // litle helper to read from a ROOT file
    auto readEvtRange = [] (const std::string name, const std::string& title,
            const RooArgSet& observables,
            const std::string& fname, const std::string& tname,
            ULong64_t first = 0, ULong64_t last = 0, const std::string& cut = "") {
        // NB: ROOT as released is buggy, the ImportFromFile thing won't work,
        // and crashes horribly, bearing witness to the dangers of
        // cut-and-paste in software such as ROOT.  so you may have to open the
        // file, and read the tree yourself. A patch has been committed to
        // ROOT's master branch...
#if 1   // way things should work, and do in newer ROOT versions
        RooDataSet tmp(name.c_str(), title.c_str(), observables,
                Cut(cut.c_str()), ImportFromFile(fname.c_str(), tname.c_str()));
#else   // old buggy versions of ROOT need to use the following:
        TFile f(fname.c_str(), "READ");
        TTree* t = dynamic_cast<TTree*>(f.Get(tname.c_str()));
        RooDataSet tmp(name.c_str(), title.c_str(), t, observables,
                cut.c_str());
        f.Close();
#endif
        if (0 == first && ULong64_t(-1) == last) return tmp;
        std::unique_ptr<RooDataSet> tmp2(
                dynamic_cast<RooDataSet*>(tmp.reduce(EventRange(first, last))));
        return RooDataSet(*tmp2, 0);
    };
    RooDataSet data = readEvtRange("data", "data", observables,
            dir + "/" + datafile, tree_name, 0, 5000, // choose "0, -1," for all events
            "Stripping_Trigger_nintervals >= 1 &&" // select between 1 and 3 intervals
            "(Stripping_Trigger_nintervals <= 0 || " // no events outside intervals!
            "(Stripping_Trigger_tp_tau_2_tp_on_1 <= lab0_TAU &&"
            "lab0_TAU <= Stripping_Trigger_tp_tau_2_tp_off_1)) &&"
            "(Stripping_Trigger_nintervals <= 1 || "
            "(Stripping_Trigger_tp_tau_2_tp_on_2 <= lab0_TAU &&"
            "lab0_TAU <= Stripping_Trigger_tp_tau_2_tp_off_2)) &&"
            "(Stripping_Trigger_nintervals <= 2 || "
            "(Stripping_Trigger_tp_tau_2_tp_on_3 <= lab0_TAU &&"
            "lab0_TAU <= Stripping_Trigger_tp_tau_2_tp_off_3))");
    // check datatsets
    data.Print("v");

    ////////////////////////////////////////////////////////////////////////
    // Initialize and fill Histograms
    ////////////////////////////////////////////////////////////////////////
    // Doubles to store the TP values and num entries
    ULong64_t n_entries = data.numEntries();

    // TH1F histograms to hold the acceptance
    const int nbins = 1024;
    TH1D acceptance_first("acceptance_first", "acceptance_first", nbins, obsTime.getMin(), obsTime.getMax());
    TH1D acceptance_second("acceptance_second", "acceptance_second", nbins, obsTime.getMin(), obsTime.getMax());
    TH1D acceptance_third("acceptance_third", "acceptance_third", nbins, obsTime.getMin(), obsTime.getMax());
    TH1D acceptance_all("acceptance_all", "acceptance_all", nbins, obsTime.getMin(), obsTime.getMax());
    {
        double tp_on = 0.0;
        double tp_off = 0.0;
        // vector of pairs to fill the histograms
        std::vector<std::pair<double, double> > tps_time;
        tps_time.reserve(3 * n_entries);

        for (ULong64_t i = 0; i < n_entries; ++i) {
            tp_on = data.get(i)->getRealValue("Stripping_Trigger_tp_tau_2_tp_on_1");
            tp_off = data.get(i)->getRealValue("Stripping_Trigger_tp_tau_2_tp_off_1");
            tps_time.emplace_back(tp_on, tp_off);
        }
        fill_acceptance_histogram(tps_time.begin(), tps_time.end(),
            acceptance_first, n_entries);
        auto i1 = tps_time.end();
        for (ULong64_t i = 0; i < n_entries; ++i) {
            tp_on = data.get(i)->getRealValue("Stripping_Trigger_tp_tau_2_tp_on_2");
            tp_off = data.get(i)->getRealValue("Stripping_Trigger_tp_tau_2_tp_off_2");
            tps_time.emplace_back(tp_on, tp_off);
        }
        fill_acceptance_histogram(i1, tps_time.end(), acceptance_second, n_entries);
        auto i2 = tps_time.end();
        for (ULong64_t i = 0; i < n_entries; ++i) {
            tp_on = data.get(i)->getRealValue("Stripping_Trigger_tp_tau_2_tp_on_3");
            tp_off = data.get(i)->getRealValue("Stripping_Trigger_tp_tau_2_tp_off_3");
            tps_time.emplace_back(tp_on, tp_off);
        }
        fill_acceptance_histogram(i2, tps_time.end(), acceptance_third, n_entries);
        fill_acceptance_histogram(tps_time.begin(), tps_time.end(), acceptance_all,
            n_entries);
    }

    ////////////////////////////////////////////////////////////////////////
    // CREATE SIGNAL TIME PDF
    ////////////////////////////////////////////////////////////////////////
    // create resolution
    RooRealVar parSigTimeResOffset("parSigTimeResOffset", "parSigTimeResOffset",
        0.);
    RooRealVar parSigTimeResSigma("parSigTimeResSigma", "parSigTimeResSigma",
        0.0114);
    RooGaussModel resSigTimeGausModel("resSigTimeGausModel",
        "resSigTimeGausModel", obsTime,
        parSigTimeResOffset, parSigTimeResSigma);

    // create tau parameter
    RooRealVar parSigTimeTauCtau("parSigTimeTauCtau", "parSigTimeTauCtau", 1.5028,
        0.0100, 6.00);
    RooConstVar magic("magic", "magic", 1e-3), zero("zero", "zero", 0.);
    RooLinearVar parSigTimeTau("parSigTimeTau", "parSigTimeTau",
            parSigTimeTauCtau, magic, zero);

    // swimming acceptance
    RooSwimmingAcceptance swacc("swacc", "swacc", obsTime, ntp,
        RooArgList(obsTPOnTau1, obsTPOffTau1, obsTPOnTau2, obsTPOffTau2, obsTPOnTau3, obsTPOffTau3),
        RooSwimmingAcceptance::On);
    // tell RooFit to never cache swacc, since its value changes on every event
    // (it's kind of ugly that we have to work around RooFit in this instance,
    // but it works, and lets us do what needs doing...)
    //swacc.setAttribute("NOCache");
    RooGaussEfficiencyModel res_model("res_model", "res_model", obsTime,
                swacc, parSigTimeResOffset,     parSigTimeResSigma);

    // standard PDF swimming
    // Create signal pdf without acceptance histogram
    RooDecay pdfSigTime("pdfSigTime", "pdfSigTime", obsTime, parSigTimeTau,
        res_model, RooDecay::SingleSided);

    // PDF with histogrammed (average) acceptance from swimming
    RooBinnedFun acceptance_roobinnedfun("acceptance_roobinnedfun",
            "acceptance_roobinnedfun", obsTime, &acceptance_first);
    RooGaussEfficiencyModel acceptance_gauss_eff_res_model(
                "acceptance_gauss_eff_res_model",
                "acceptance_gauss_eff_res_model", obsTime,
                acceptance_roobinnedfun, parSigTimeResOffset,
                parSigTimeResSigma);
    RooDecay pdfSigTimePlot("pdfSigTimePlot", "pdfSigTimePlot", obsTime,
            parSigTimeTau, acceptance_gauss_eff_res_model,
            RooDecay::SingleSided);

    ////////////////////////////////////////////////////////////////////////
    // PERFORM THE SIGNAL TIME FIT
    ////////////////////////////////////////////////////////////////////////
    // read parameter values file
    pdfSigTime.getParameters(data)->readFromFile("StartingValues.txt");

    // save used parameter values for confirmation
    pdfSigTime.getParameters(data)->writeToFile("StartingValues.out");

    // fit
    RooLinkedList fitOpts;
    static const std::vector<RooCmdArg> _fitOpts{ Save(true), Verbose(true),
        Strategy(2), Timer(true), SumW2Error(true), Optimize(2), Offset(true),
        ConditionalObservables(observables_swimming) };
    for (auto& opt : _fitOpts) fitOpts.Add(&const_cast<RooCmdArg&>(opt));
    RooFitResult* fit_result = pdfSigTime.fitTo(data, fitOpts);

    // save results
    pdfSigTime.getParameters(data)->writeToFile("FitResults.out");

    //  //print results on terminal
    fit_result->Print();
    TMatrixTSym<double> corMatrix = fit_result->correlationMatrix();
    corMatrix.Print();

    ////////////////////////////////////////////////////////////////////////
    // PLOT RESULTS
    ////////////////////////////////////////////////////////////////////////
    TCanvas c("c", "c", 800, 600);

    TLatex label(
        0.7, 0.9,
        "#splitline{#it{B}_{s}^{0} #rightarrow #it{D}_{s}#it{#pi}}{MC}");
    label.SetNDC();
    label.SetTextSize(0.06);
    label.SetTextColor(1);
    label.SetTextAlign(33);

    // set up plotting options
    //
    // the important bits are ProjWData, which will do the correct per-event
    // accumulation of the pdf from the swimming observables for the plot, and
    // Normalization, which fixes the normalisation (which would otherwise be
    // off)
    RooLinkedList plotOpts, plotOpts2;
    static const std::vector<RooCmdArg> _plotOpts{ LineColor(4),
        Precision(1e-6), ProjWData(observables_swimming, data),
        Normalization(data.sumEntries(), RooAbsPdf::NumEvent) };
    for (auto& opt: _plotOpts) {
        plotOpts.Add(&const_cast<RooCmdArg&>(opt));
        plotOpts2.Add(&const_cast<RooCmdArg&>(opt));
    }
    //***** propertime distribution *******/
    // non logarithmic time plot
    c.SetLogy(false);
    RooPlot* timeplot = obsTime.frame();
    data.plotOn(timeplot);
    pdfSigTime.plotOn(timeplot, plotOpts);
    timeplot->SetMinimum(0.);
    label.Draw();
    timeplot->Draw();
    c.SaveAs("Time.pdf");

    // logarithmic time plot
    c.Clear();
    c.SetLogy(true);
    timeplot = obsTime.frame();
    data.plotOn(timeplot);
    pdfSigTime.plotOn(timeplot, plotOpts2);
    label.Draw();
    timeplot->Draw();
    c.SaveAs("TimeLog.pdf");

    // plot acceptance histograms
    c.SetLogy(false);
    acceptance_first.Draw();
    c.SaveAs("Acceptance_Intervals_First.pdf");

    acceptance_second.Draw();
    c.SaveAs("Acceptance_Intervals_Second.pdf");

    acceptance_third.Draw();
    c.SaveAs("Acceptance_Intervals_Third.pdf");

    acceptance_all.Draw();
    c.SaveAs("Acceptance_Intervals_All.pdf");

    return 0;
}
