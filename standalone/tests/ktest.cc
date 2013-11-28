#include <TH1.h>
#include <TF1.h>

#include <RooGaussModel.h>
#include <RooTruthModel.h>
#include "RooProduct.h"
#include "RooProdPdf.h"
#include <RooRealVar.h>
#include <RooRealConstant.h>
#include <RooBDecay.h>
#include <RooHistPdf.h>
#include <RooDataHist.h>
#include <RooDataSet.h>
#include <RooArgSet.h>
#include <RooArgList.h>
#include <RooAddPdf.h>
#include <RooNameSet.h>

#include "B2DXFitters/RooKResModel.h"
#include "B2DXFitters/Inverse.h"

// plotting
#include <TCanvas.h>
#include <TPad.h>
#include <TStyle.h>
#include <RooPlot.h>
#include <RooHist.h>

#include <boost/format.hpp>


TH1D* fill_hist(TH1D &hist, std::vector<double> &templ);

void plot_w_pull(TCanvas &canvas, std::string fname, RooRealVar &xvar, TH1 &hist,
		 RooAbsData &dataset, RooAbsReal &phys1, RooAbsReal &phys2,
		 bool withk=false);

int main()
{
  RooRealVar xvar("xvar", "Time [ps]", 0.0, 15.0);
  xvar.setBins(500);
  xvar.setBins(1500, "cache");

  RooRealVar kvar("kvar", "K-factor", 0.01, 2.);
  RooRealVar kvar2("kvar2", "K-factor", 0.01, 2.);

  RooRealVar gamma("gamma", "gamma", 2.0 / 3.0, 0., 3.);
  RooRealVar dGamma("dGamma", "dGamma", -0.15, -3., 3.);
  RooRealVar dM("dM", "dM", 17.6, 0.1, 20.);

  RooRealVar C("C", "C", 1., 0., 2.);

  RooConstVar one("one", "one", 1.);
  RooConstVar zero("zero", "zero", 0.);

  RooProduct kgamma("kgamma", "kgamma", RooArgList(gamma, kvar2));
  RooProduct kdGamma("kdGamma", "kdGamma", RooArgList(dGamma, kvar2));
  RooProduct kdM("kdM", "kdM", RooArgList(dM, kvar2));

  Inverse tau("tau", "tau", gamma);
  Inverse tauk("tauk", "tauk", kgamma);

  RooTruthModel tres("tres", "tres", xvar);
  RooBDecay phys1t("phys1t", "Reference model", xvar, tau, dGamma, one, zero,
		   C, zero, dM, tres, RooBDecay::SingleSided);

  RooGaussModel gres("gres", "gres", xvar, RooRealConstant::value(0.0),
  		     RooRealConstant::value(0.045));
  RooBDecay phys1g("phys1g", "Reference model", xvar, tau, dGamma, one, zero,
		   C, zero, dM, gres, RooBDecay::SingleSided);

  // k-factor distribution
  // TH1D hist("hist", "hist", 400, 0.01, 2.);
  // TF1 tfg1("tfg1", "exp(-0.5*(((x-0.3)/0.0625)**2))/sqrt(2.*3.141592*0.0625*0.0625)");
  // TF1 tfg2("tfg2", "exp(-0.5*(((x-0.5)/0.0625)**2))/sqrt(2.*3.141592*0.0625*0.0625)");
  // TF1 tfg3("tfg3", "exp(-0.5*(((x-1.0)/0.0625)**2))/sqrt(2.*3.141592*0.0625*0.0625)");
  // TF1 tfg4("tfg4", "exp(-0.5*(((x-1.3)/0.0625)**2))/sqrt(2.*3.141592*0.0625*0.0625)");

  const int kbins(400);
  std::vector<std::string> fns;
  fns.push_back("1e2*exp(-((x-1)/1e-2)**2)/sqrt(22/7)"); // delta function = 1
  fns.push_back("1e2*exp(-((x-0.5)/1e-2)**2)/sqrt(22/7)"); // delta function = 0.5
  fns.push_back("1e2*exp(-((x-1.5)/1e-2)**2)/sqrt(22/7)"); // delta function = 1.5
  fns.push_back("1e2*exp(-((x-1)/1e-2)**2)/sqrt(22/7)"
  		"+ 1e2*exp(-((x-1.5)/1e-2)**2)/sqrt(22/7)"); // delta function = 1 & 1.5
  fns.push_back("1e2*exp(-((x-0.5)/1e-2)**2)/sqrt(22/7)"
  		"+ 1e2*exp(-((x-1.5)/1e-2)**2)/sqrt(22/7)"); // delta function = 0.5 & 1.5
  fns.push_back("1e1*exp(-((x-1)/1e-1)**2)/sqrt(22/7)"); // fat delta = 1
  fns.push_back("1e1*exp(-((x-1.2)/1e-1)**2)/sqrt(22/7)"); // fat delta = 1.2
  fns.push_back("(x<1.5 && x>0.5)?100:0"); // step function < 1
  fns.push_back("(x>1)?100:0"); // step function > 1
  fns.push_back("(x>0.5)?(2.0*x/3.0 - 1.0/3.0):0");	 // triangular
  fns.push_back("(x>1.2)?(2.0*x/3.0 - 1.0/3.0):0");	 // triangular

  std::string fname("RooKResModel_test");
  // fname += str(boost::format("%d") % i);
  fname += ".pdf";

  TCanvas canvas("canvas", "", 800, 500);
  gStyle->SetOptStat(0);
  canvas.Print((fname+"[").c_str()); // open pdf file for plotting

  const int nevents(2E5);

  std::cout << "===== With truth resolution: =====" << std::endl;
  for (unsigned i = 0; i < fns.size(); ++i) {
    TF1 func("func", fns[i].c_str(), 0, 2);
    std::cout << "Fn: "<< fns[i] << std::endl;
    TH1D hist("hist", "", kbins, 0.0, 2.0);
    hist.FillRandom("func", 1E4);

    std::cout << "GENERATING WITHOUT K-FACTOR" << std::endl;
    RooDataSet *dataset1 = phys1t.generate(RooArgSet(xvar),
					   RooFit::NumEvents(nevents));
    std::cout << "GENERATING USING K-FACTOR AS PER-EVENT OBSERVABLE" << std::endl;
    TH1D * hist2 = dynamic_cast<TH1D*>(hist.Clone("hist2"));
    hist2->Reset("ices");
    RooDataSet *dataset2 = new RooDataSet("dataset2", "dataset2", RooArgSet(xvar));
    for (unsigned j = 0; j < unsigned(dataset1->numEntries()); ++j) {
      double k = hist.GetRandom();
      double x = dataset1->get(j)->getRealValue(xvar.GetName());
      hist2->Fill(k);
      xvar.setVal(x/k);
      dataset2->add(RooArgSet(xvar));
    }
    std::cout << "GENERATION DONE." << std::endl;

    // std::vector<double> templ;
    // // templ.push_back(0.3);
    // // templ.push_back(0.5);
    // templ.push_back(1.0);
    // // templ.push_back(1.3);
    // fill_hist(hist, templ);

    kvar.setRange(hist2->GetXaxis()->GetBinLowEdge(1),
		  hist2->GetXaxis()->GetBinUpEdge(hist2->GetNbinsX()));
    kvar.setBins(hist2->GetNbinsX());
    kvar.setConstant(true);

    RooDataHist datahist("datahist", "", RooArgList(kvar), hist2);
    RooHistPdf histpdf("histpdf", "", RooArgSet(kvar), datahist);

    RooKResModel ktres("ktres", "", tres, histpdf, kvar,
		       RooArgSet(gamma, dM, dGamma), RooArgSet(xvar));
    RooBDecay phys2a("phys2a", "k-factor smeared model", xvar, tau, dGamma,
		     one, zero, C, zero, dM, ktres, RooBDecay::SingleSided);
    delete dataset2;
    std::cout << "GENERATION NOT QUITE DONE." << std::endl;
    dataset2 = phys2a.generate(RooArgSet(xvar), RooFit::NumEvents(nevents),
    	    RooFit::Verbose());
    dataset2->Print("v");
    std::cout << "GENERATION REALLY DONE." << std::endl;

    // phys1t.fitTo(*dataset1, RooFit::Timer(), RooFit::Verbose(),
    // 	      RooFit::Strategy(2), RooFit::Offset());
    // phys2a.fitTo(*dataset2, RooFit::Timer(), RooFit::Verbose(),
    // 	       RooFit::Strategy(2), RooFit::Offset());

    plot_w_pull(canvas, fname, xvar, *hist2, *dataset2, phys1t, phys2a);

    // if (fns.size() - 2 == i) {
    //   RooConstVar mone("mone", "minus one", -1.);
    //   RooBDecay env1("env1", "", xvar, tau, dGamma, one, zero, one, zero,
    // 		     dM, kgres, RooBDecay::SingleSided);
    //   RooBDecay env2("env2", "", xvar, tau, dGamma, one, zero, mone, zero,
    // 		     dM, kgres, RooBDecay::SingleSided);
    //   RooAddPdf env("env", "", RooArgList(env1, env2),
    // 		    RooArgList(RooRealConstant::value(0.5), RooRealConstant::value(0.5)));
    //   TCanvas c("c", "", 800, 500);
    //   RooPlot * xfr = xvar.frame();
    //   env.plotOn(xfr, RooFit::Color(kAzure), RooFit::Components("env1"));
    //   env.plotOn(xfr, RooFit::Color(kAzure), RooFit::LineStyle(kDashed));
    //   xfr->Draw();
    //   xfr->SetTitle("B decay with Gaussian time resolution & k-factor smearing");
    //   gPad->Print("B_decay_w_kfactor_Rose.pdf");
    // }

    delete hist2;
    delete dataset2;
  }

  canvas.Print((fname+"]").c_str());
  return 0;
  std::cout << "===== With Gaussian resolution: =====" << std::endl;
  for (unsigned i = 0; i < fns.size(); ++i) {
    TF1 func("func", fns[i].c_str(), 0, 2);
    std::cout << "Fn: "<< fns[i] << std::endl;
    TH1D hist("hist", "", kbins, 0.0, 2.0);
    hist.FillRandom("func", nevents);

    kvar2.setRange(hist.GetXaxis()->GetBinLowEdge(1),
		   hist.GetXaxis()->GetBinUpEdge(hist.GetNbinsX()));
    kvar2.setBins(hist.GetNbinsX());

    RooDataHist datahist("datahist", "", RooArgList(kvar2), &hist);
    RooHistPdf histpdf("histpdf", "", RooArgSet(kvar2), datahist);

    RooKResModel kgres("kgres", "", gres, histpdf, kvar2,
		       RooArgSet(gamma, dM, dGamma)); // RooArgSet(xvar)
    RooBDecay phys2a("phys2a", "k-factor smeared model", xvar, tau, dGamma,
		     one, zero, C, zero, dM, kgres, RooBDecay::SingleSided);

    RooBDecay phys3x("phys3x", "model with k-factor applied as per-event obs.",
		     xvar, tauk, kdGamma, one, zero, C, zero, kdM, gres,
		     RooBDecay::SingleSided);
    RooProdPdf phys3("phys3", "model with k-factor applied as per-event obs.",
		     histpdf, RooFit::Conditional(RooArgSet(phys3x),
						  RooArgSet(xvar)));

    std::cout << "GENERATING USING K-FACTOR AS PER-EVENT OBSERVABLE" << std::endl;
    RooDataSet *dataset3 = phys3.generate(RooArgSet(xvar, kvar2),
					  RooFit::NumEvents(nevents));
    dataset3->Print("v");
    std::cout << "GENERATION DONE." << std::endl;

    plot_w_pull(canvas, fname, xvar, hist, *dataset3, phys1g, phys2a, true);
  }

  // close pdf file
  canvas.Print((fname+"]").c_str());

  return 0;
}


void plot_w_pull(TCanvas &canvas, std::string fname, RooRealVar &xvar, TH1 &hist,
		 RooAbsData &dataset, RooAbsReal &phys1, RooAbsReal &phys2,
		 bool withk)
{
  // main frame
  RooPlot *xframe = xvar.frame();
  dataset.plotOn(xframe, RooFit::MarkerStyle(kDot));
  phys1.plotOn(xframe, RooFit::LineColor(kAzure), RooFit::LineWidth(2));
  phys2.plotOn(xframe, RooFit::LineColor(kGreen+2), RooFit::LineWidth(2),
	       RooFit::Precision(1e-6));

  xframe->Print("v");

  // pull frame
  std::string name(phys2.GetName());
  if (withk) {
    name += "_Int[";
    name += "kvar2";
    name += "]";
  }
  name += "_Norm[";
  if (withk) {
    name += "kvar2,";
  }
  name += xvar.GetName();
  name += "]";
  std::cout << "pdf: " << name << std::endl;

  std::string hpullname("h_");
  hpullname += dataset.GetName();

  RooHist * hpull = xframe->pullHist(hpullname.c_str(), name.c_str());

  // phys3_Int[kvar2]_Norm[kvar2,xvar]
  RooPlot * xframe_pull = xvar.frame();
  RooConstVar zeroaxis = RooRealConstant::value(0.0);
  zeroaxis.plotOn(xframe_pull, RooFit::LineColor(kBlack),
		  RooFit::LineWidth(1));
  xframe_pull->addPlotable(hpull, "E1");

  // plotting
  canvas.cd();
  TPad mainpl("mainpl", "", 0, 0.2, 1, 1);
  mainpl.SetTopMargin(0.08);
  mainpl.SetBottomMargin(0.02);
  mainpl.Draw();
  mainpl.cd();
  xframe->Draw();
  xframe->SetTitle("B decay");
  xframe->GetXaxis()->SetTitle("");
  xframe->GetXaxis()->SetLabelOffset(0.1);

  TPad inset("inset", "", 0.57, 0.5, 0.92, 0.92);
  inset.SetFillStyle(4000);
  inset.Draw();
  inset.cd();
  hist.SetFillColor(kAzure);
  hist.SetLineColor(kAzure);
  hist.GetXaxis()->SetLabelSize(0.07);
  hist.Draw();

  TPad pullpl("pullpl", "", 0, 0, 1, 0.2);
  canvas.cd();
  pullpl.SetTopMargin(0);
  pullpl.SetBottomMargin(0.4);
  pullpl.Draw();
  pullpl.cd();
  xframe_pull->Draw();
  xframe_pull->SetTitle("");
  xframe_pull->GetXaxis()->SetLabelSize(0.15);
  xframe_pull->GetXaxis()->SetTitleSize(0.15);
  xframe_pull->GetYaxis()->SetTitle("");
  xframe_pull->GetYaxis()->SetLabelSize(0.13);
  xframe_pull->GetYaxis()->SetNdivisions(208);

  canvas.Print(fname.c_str());
  //mainpl.SetLogy();
  //canvas.Print(fname.c_str());
  return;
}


TH1D* fill_hist(TH1D &hist, std::vector<double> &templ)
{
  for (unsigned bin=0; bin < templ.size(); ++bin) {
    for (unsigned i=0; i<100; ++i) {
      hist.Fill(templ[bin]);
    }
  }
  // hist.Print("all");
  return &hist;
}
