//---------------------------------------------------------------------------//
//                                                                           //
//  General utilities                                                        //
//                                                                           //
//  Source file                                                              //
//                                                                           //
//  Authors: Agnieszka Dziurda                                               //
//  Date   : 12 / 04 / 2012                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

// STL includes
#include <string>
#include <vector>
#include <fstream>
#include <stdexcept>

// ROOT and RooFit includes
#include "TH1D.h"
#include "TProfile.h"
#include "TFile.h"
#include "TCanvas.h"
#include "TLorentzVector.h"
#include "RooFormulaVar.h"
#include "RooAddPdf.h"
#include "RooExtendPdf.h"
#include "RooEffProd.h"
#include "RooGaussian.h"
#include "RooDecay.h"
#include "RooBDecay.h"
#include "RooCBShape.h"
#include "RooExponential.h"
#include "RooArgSet.h"
#include "RooAbsRealLValue.h"
#include "RooPlot.h"
#include "RooNLLVar.h"
#include "RooMinuit.h"
#include "RooFitResult.h"
#include "TH2F.h"
#include "TH3F.h"
#include "TRandom3.h"
#include "RooHistPdf.h"
#include "RooDataHist.h"
#include "RooCategory.h"
#include "TGraphErrors.h"
#include "TLegend.h"
#include "TLatex.h"

// B2DXFitters includes
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/WeightingUtils.h"
#include "B2DXFitters/Bs2Dsh2011TDAnaModels.h"
#include "B2DXFitters/DecayTreeTupleSucksFitter.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"
#include "B2DXFitters/PlotSettings.h"
#include "B2DXFitters/MDFitterSettings.h"
#include "B2DXFitters/MCBackground.h"
#include "B2DXFitters/PIDCalibrationSample.h" 

#define DEBUG(COUNT, MSG)				   \
  std::cout << "SA-DEBUG: [" << COUNT << "] (" << __func__ << ") " \
  << MSG << std::endl; \
  COUNT++;

#define ERROR(COUNT, MSG) \
  std::cerr << "SA-ERROR: [" << COUNT << "] (" << __func__ << ") " \
  << MSG << std::endl; \
  COUNT++;
using namespace GeneralUtils;
using namespace WeightingUtils; 
using namespace Bs2Dsh2011TDAnaModels;

namespace WeightingUtils {

  
  //===========================================================================
  // 
  //===========================================================================
  TString CheckWeightLabel(TString& check, bool debug)
  {
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::CheckWeightLabel("<<check<<")"<< std::endl;
      }
    TString lab;
    if( check == "lab1_P" ) { lab = "log(p) [MeV/c]";}
    else if (check =="lab1_PT" ) { lab = "log(p_{t}) [MeV/c]";}
    else if ( check == "nTracks") { lab = "log(nTracks) [1]";}
    else {lab="";}

    return lab;
  }

  std::vector <TString> CheckWeightNames(TString type, bool debug)
  {
    std::vector <TString> names;
    TString nm = "";
    TString name = "";
    TString histName = "";
    TString histNameR = ""; 
    TString nameCalib = "";
    TString sample = "";
    TString mode = ""; 
    TString year = ""; 

    if ( type.Contains("Comb") == true && type.Contains("Pion") == true)
      {
        if ( type.Contains("Down") == true || type.Contains("down") == true) { nm = "down"; } else {  nm = "up"; }
	if ( type.Contains("2011") == true ) { nm = nm +"_2011"; } 
	else if ( type.Contains("2012") == true ) { nm = nm+"_2012";}
	else { nm = nm+"_unknown"; } 
        name="name";
        //name = "dataSetBsDsPi_"+nm+"_hhhpi0";
	histName = "hist2D_CombPi_"+nm;
        histNameR = "hist2D_CombPi_ratio_"+nm;
	nameCalib = "CalibSample_CombPi_"+nm; 
      }
    else if ( type.Contains("Comb") == true && type.Contains("Kaon") == true)
      {
        if ( type.Contains("Down") == true || type.Contains("down") == true) { nm = "down"; } else {  nm = "up"; }
        if ( type.Contains("2011") == true ) { nm = nm +"_2011"; }
        else if ( type.Contains("2012") == true ) { nm = nm+"_2012";}
	else { nm = nm+"_unknown"; }
	name="name";
        //name = "dataSetBsDsPi_"+nm+"_hhhpi0";
	histName = "hist2D_CombK_"+nm;
        histNameR = "hist2D_CombK_ratio_"+nm;
	nameCalib = "CalibSample_CombK_"+nm;
      }
    else if ( type.Contains("Comb") == true && type.Contains("Proton") == true)
      {
        if ( type.Contains("Down") == true || type.Contains("down") == true) { nm = "down"; } else {  nm = "up"; }
        if ( type.Contains("2011") == true ) { nm = nm +"_2011"; }
        else if ( type.Contains("2012") == true ) { nm = nm+"_2012";}
	else { nm = nm+"_unknown"; }

	name="name";
        histName = "hist2D_CombP_"+nm;
        histNameR = "hist2D_CombP_ratio_"+nm;
	nameCalib = "CalibSample_CombP_"+nm;
      }
    else if ( type.Contains("DPi") == true)
      {
        if ( type.Contains("Down") == true || type.Contains("down") == true) { nm = "down"; } else {  nm = "up"; }
	if ( type.Contains("2011") == true ) { year = "_2011"; }
        else if ( type.Contains("2012") == true ) { year = "_2012";}
	else { year = "unknown"; } 
	sample = CheckPolarity(type,debug);
	name = "dataSet_Miss_"+nm+"_kpipi"+year;
        histName = "hist2D_Miss_"+nm;
        histNameR = "hist2D_Miss_ratio_"+nm;
	nameCalib = "CalibSample_Miss_"+nm;
	nm = "Bd2DPi_"+sample+"_kpipi"+year; 
      }
    else if( type.Contains("Bs2DsPi") == true && type.Contains("MC") == true )
      {
	sample = CheckPolarity(type,debug);
        mode = CheckDMode(type, debug);
        if ( mode == "kkpi" || mode == "") { mode = CheckKKPiMode(type, debug); }
	year = CheckDataYear(type,debug);
	if ( year != "") { year = "_"+year; }
	nm = "Bs2DsPi_"+sample+"_"+mode+year;
        name="dataSetMC_"+nm;
        histName = "hist2D_"+nm;
        histNameR = "hist2D_ratio_"+nm;
	nameCalib = "CalibSample_"+nm;
      }
    else if( type.Contains("Bs2DsstPi") == true && type.Contains("MC") == true )
      {
        sample = CheckPolarity(type,debug);
        mode = CheckDMode(type, debug);
        if ( mode == "kkpi" || mode == "") { mode = CheckKKPiMode(type, debug); }
        year = CheckDataYear(type,debug);
        if ( year != "") { year = "_"+year; }
        nm = "Bs2DsstPi_"+sample+"_"+mode+year;
        name="dataSetMC_"+nm;
        histName = "hist2D_"+nm;
        histNameR = "hist2D_ratio_"+nm;
        nameCalib = "CalibSample_"+nm;
      }
    else if (type.Contains("Bs2DsK") == true && type.Contains("MC") == true)
      {
        sample = CheckPolarity(type,debug);
        mode = CheckDMode(type, debug);
        if ( mode == "kkpi"|| mode == "") { mode = CheckKKPiMode(type, debug); }
	year = CheckDataYear(type,debug);
	if ( year != "") { year = "_"+year; }
        nm = "Bs2DsK_"+sample+"_"+mode+year;
        name="dataSetMC_"+nm;
        histName = "hist2D_"+nm;
	histNameR = "hist2D_ratio_"+nm;
	nameCalib = "CalibSample_"+nm;

      }
    else if (type.Contains("Bs2DsstK") == true && type.Contains("MC") == true)
      {
        sample = CheckPolarity(type,debug);
        mode = CheckDMode(type, debug);
        if ( mode == "kkpi"|| mode == "") { mode = CheckKKPiMode(type, debug); }
        year = CheckDataYear(type,debug);
        if ( year != "") { year = "_"+year; }
        nm = "Bs2DsstK_"+sample+"_"+mode+year;
        name="dataSetMC_"+nm;
        histName = "hist2D_"+nm;
        histNameR = "hist2D_ratio_"+nm;
        nameCalib = "CalibSample_"+nm;

      }
    else if( type.Contains("Bs2DsPi") == true && type.Contains("MC") != true )
      {
	sample = CheckPolarity(type,debug);
	mode = CheckDMode(type, debug);
	if ( mode == "kkpi" || mode == "") { mode = CheckKKPiMode(type, debug); }
	year = CheckDataYear(type,debug); 
	if ( year != "") { year = "_"+year; }
	nm = sample+"_"+mode+year;
	name="dataSet_Miss_"+nm;
	histName = "hist2D_"+nm;
	histNameR = "hist2D_ratio_"+nm;
	nameCalib = "CalibSample_"+nm;
      }

    names.push_back(nm);
    names.push_back(name);
    names.push_back(histName);
    names.push_back(histNameR);
    names.push_back(nameCalib); 
    names.push_back(sample);
    names.push_back(mode); 

    return names; 
    
  }

  TH2F*  Get2DHist(RooDataSet* data, 
		   RooRealVar* Var1, RooRealVar* Var2,
		   Int_t bin1, Int_t bin2,
		   TString& histName1,
		   bool debug)
  {
    TH2F* hist = NULL;
    TString nameVar1 = Var1->GetName();
    TString nameVar2 = Var2->GetName();
    TString label1, label2;
    if ( nameVar1 != nameVar2 )
      {
        label1 = CheckWeightLabel(nameVar1,debug);
        label2 = CheckWeightLabel(nameVar2,debug);
      }
    else { if(debug == true) std::cout<<"The same name of variables: "<<nameVar1<<"  "<<nameVar2<<std::endl; }

    hist = NULL;
    TString histName = histName1;
    hist =data->createHistogram(*Var1, *Var2, bin1, bin2, "", histName.Data());
    hist->SetName(histName.Data());
    hist->SetStats(kFALSE);
    hist->GetXaxis()->SetTitle(label1.Data());
    hist->GetYaxis()->SetTitle(label2.Data());
    TString TitleHist = "";
    hist->SetTitle(TitleHist.Data());

    if ( hist != NULL && debug == true) { std::cout<<"[INFO] Read histogram: "<<hist->GetName()<<std::endl; }

    return hist;
  }



  TH3F*  Get3DHist(RooDataSet* data,
                   RooRealVar* Var1, RooRealVar* Var2, RooRealVar* Var3,
                   TH3F* hist,
		   bool debug )
  {
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::Get3DHist("<<data->GetName()<<","
		  <<Var1->GetName()<<","<<Var2->GetName()<<","<<Var3->GetName()<<","
		  <<hist->GetName()<<")"<< std::endl;
      }
    
       
    TString nameVar1 = Var1->GetName();
    TString nameVar2 = Var2->GetName();
    TString nameVar3 = Var3->GetName();
    
    const RooArgSet* set = data->get();
    RooAbsReal* plotVarX= (RooAbsReal*)set->find(nameVar1.Data());
    RooAbsReal* plotVarY= (RooAbsReal*)set->find(nameVar2.Data());
    RooAbsReal* plotVarZ= (RooAbsReal*)set->find(nameVar3.Data());
    	
    
    for (Long64_t jentry=0; jentry<data->numEntries(); jentry++)
      {
	
	const RooArgSet* setT = data->get(jentry);
        if (setT) {}

	Double_t Var13 = plotVarX->getVal();
	Double_t Var23 = plotVarY->getVal();
	Double_t Var33 = plotVarZ->getVal();

	hist->Fill(Var13,Var23,Var33,data->weight());
	std::cout<<Var13<<" "<<Var23<<" "<<Var33<<" "<<data->weight()<<std::endl;
      }

    hist->SetStats(kFALSE);
    hist->GetXaxis()->SetTitle(nameVar1.Data());
    hist->GetYaxis()->SetTitle(nameVar2.Data());
    hist->GetZaxis()->SetTitle(nameVar3.Data());
    TString TitleHist = "";
    hist->SetTitle(TitleHist.Data());

    if ( hist != NULL && debug == true) { std::cout<<"[INFO] Read histogram: "<<hist->GetName()<<" with entries: "
						   <<hist->GetEntries()<<std::endl; }

        
    return hist;
  }
  void PlotWeightingSample(TString& nm, RooDataSet* dataCalib, RooDataSet* dataCalibRW,
			   RooRealVar* Var1, RooRealVar* Var2, RooRealVar* PID,
			   Int_t bin1, Int_t bin2, Int_t bin3,
			   TString& label1, TString& label2, TString& label3, 
			   RooWorkspace* work, 
			   PlotSettings* plotSet,
			   bool debug )

  {

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }
    TString dir = plotSet->GetDir();
    TString ext = plotSet->GetExt(); 

    TString name;
    Bool_t legendBool;
    if ( label1.Contains("MC") == true ) 
      {
	name="dataSetMC_"+nm;
	if( label1.Contains("Bs2DsK") == true) {legendBool = kFALSE;} else {legendBool = kTRUE;}
      }
    else if ( label1.Contains("Comb") == true ) 
      { 
	name = "CalibSample"+nm;

	if ( label1.Contains("CombPi") == true ) { legendBool = kTRUE; } else {legendBool = kFALSE; }
      }
    else if ( label1.Contains("Bs2DsPi") == true && label1.Contains("MC") != true)
      {
	TString sample = CheckPolarity(label1,debug);
        TString mode = CheckDMode(label1, debug);
	TString year = CheckDataYear(label1,debug); 
	if ( year != "" ) { year = "_"+year; }  
	if ( mode == "kkpi") { mode = CheckKKPiMode(label1, debug); }
	TString mm = sample+"_"+mode+year;
        name="dataSet_Miss_"+mm;
	legendBool = kFALSE;
      }  
    else {
      legendBool =kTRUE;
      TString year = CheckDataYear(label1,debug);
      if ( year != "" ) { year = "_"+year; }
      if( label1.Contains("Down") == true) { name="dataSet_Miss_down_kpipi"+year;} else { name = "dataSet_Miss_up_kpipi"+year;}
    }

    RooDataSet*  dataMC = GetDataSet(work,name,debug);
    RooDataSet*  dataMCNW = GetDataSet(work,name,debug);
    if ( label1.Contains("MC") == true && dataMC->isWeighted() == false )
      { 
	if (debug == true ) { std::cout<<"[INFO] Data sample: "<<dataMC->GetTitle()<<" not weighted, apply weights"<<std::endl; } 
	dataMC = new RooDataSet(dataMC->GetName(), dataMC->GetTitle(), *(dataMC->get()), RooFit::Import(*dataMC), RooFit::WeightVar("weights"));
      }


    double scaleA = dataCalib->sumEntries()/dataMC->sumEntries();
    double scaleB = dataCalib->sumEntries()/dataCalibRW->sumEntries();
    double scaleC = dataCalib->sumEntries()/dataMCNW->sumEntries();
  

    std::cout<<" scaleA: "<<scaleA<<" = "<<dataMC->sumEntries()<<"/"<<dataCalib->sumEntries()<<std::endl;
    std::cout<<" scaleA: "<<scaleB<<" = "<<dataCalibRW->sumEntries()<<"/"<<dataCalib->sumEntries()<<std::endl;
    std::cout<<" scaleC: "<<scaleC<<" = "<<dataMC->sumEntries()<<"/"<<dataMCNW->sumEntries()<<std::endl;

    TLegend* legend = new TLegend( 0.12, 0.66, 0.30, 0.88 );
    legend->SetTextSize(0.045);
    legend->SetTextFont(12);
    legend->SetFillColor(kWhite);
    legend->SetShadowColor(0);
    legend->SetBorderSize(0);
    legend->SetTextFont(132);
            
    TLegend* legend2 = NULL;
    if ( legendBool == kTRUE )
      {
	legend2 = new TLegend( 0.11, 0.66, 0.30, 0.88 );
      }
    else
      {
	legend2 = new TLegend( 0.50, 0.66, 0.70, 0.88 );
      }
    legend2->SetTextSize(0.05);
    legend2->SetTextFont(12);
    legend2->SetFillColor(kWhite);
    legend2->SetShadowColor(0);
    legend2->SetBorderSize(0);
    legend2->SetTextFont(132);
    

    TGraphErrors* gr = new TGraphErrors(10);
    gr->SetName("gr");
    gr->SetLineColor(kBlack);
    gr->SetLineWidth(1);
    gr->SetMarkerStyle(22);
    gr->SetMarkerSize(3);
    gr->SetMarkerColor(plotSet->GetColorData(1));
    gr->Draw("P");

    TGraphErrors* grMC = new TGraphErrors(10);
    grMC->SetName("grMC");
    grMC->SetLineColor(kBlack);
    grMC->SetLineWidth(1);
    grMC->SetMarkerStyle(20);
    grMC->SetMarkerSize(3);
    grMC->SetMarkerColor(plotSet->GetColorData(2));
    grMC->Draw("P");

    TGraphErrors* grMCRW = new TGraphErrors(10);
    grMCRW->SetName("grMCRW");
    grMCRW->SetLineColor(kBlack);
    grMCRW->SetLineWidth(1);
    grMCRW->SetMarkerStyle(21);
    grMCRW->SetMarkerSize(3);
    grMCRW->SetMarkerColor(plotSet->GetColorData(0));
    grMCRW->Draw("P");
    
    TGraphErrors* grMCNW = new TGraphErrors(10);
    grMCNW->SetName("grMCNW");
    grMCNW->SetLineColor(kBlack);
    grMCNW->SetLineWidth(1);
    grMCNW->SetMarkerStyle(23);
    grMCNW->SetMarkerSize(3);
    grMCNW->SetMarkerColor(plotSet->GetColorData(3));
    grMCNW->Draw("P");

    TString labelMode = GetLabel(nm, debug);

    legend->AddEntry("gr",label3.Data(),"lep");
    if ( label1.Contains("MC") == true )
      {
	legend->AddEntry("grMCRW","MC weighted","lep");
      }
    else
      {
	legend->AddEntry("grMCRW","Data","lep");
      }
    legend->AddEntry("grMC",label2.Data(),"lep");
    if ( label1.Contains("MC") == true )
      {
	legend->AddEntry("grMCNW","MC","lep");
      }
    legend->SetHeader(labelMode.Data()); 
    
    legend2->AddEntry("gr",label3.Data(),"lep");
    legend2->AddEntry("grMCRW",labelMode.Data(),"lep");
    


    TString l1, l2;
    TString nameVar1 = Var1->GetName();
    TString nameVar2 = Var2->GetName();
    l1 = CheckWeightLabel(nameVar1,debug);
    l2 = CheckWeightLabel(nameVar2,debug);

    RooPlot* mframe_Var1 = Var1->frame();
    dataCalib->plotOn(mframe_Var1,RooFit::MarkerColor(plotSet->GetColorData(2)), 
		      RooFit::Binning(bin1), RooFit::MarkerStyle(20), RooFit::MarkerSize(2.75)); //, RooFit::Rescale(1/scaleA));
    if ( label1.Contains("MC") == true )
      {
	dataMCNW->plotOn(mframe_Var1,RooFit::MarkerColor(plotSet->GetColorData(3)), RooFit::Binning(bin1),
			 RooFit::Rescale(scaleC),RooFit::MarkerStyle(23), RooFit::MarkerSize(2.75));
      }
    dataMC->plotOn(mframe_Var1,RooFit::MarkerColor(plotSet->GetColorData(0)), 
		   RooFit::Binning(bin1), RooFit::Rescale(scaleA), RooFit::MarkerStyle(21), RooFit::MarkerSize(2.75));
    dataCalibRW->plotOn(mframe_Var1, RooFit::MarkerColor(plotSet->GetColorData(1)),  
			RooFit::Binning(bin1), RooFit::MarkerStyle(22), RooFit::MarkerSize(2.75), RooFit::Rescale(scaleB));     
        
    mframe_Var1->GetXaxis()->SetTitle(l1.Data());
    mframe_Var1->SetLabelFont(132);
    mframe_Var1->SetTitleFont(132);
    mframe_Var1->GetXaxis()->SetTitleFont(132);
    mframe_Var1->GetXaxis()->SetLabelFont(132);
    mframe_Var1->GetYaxis()->SetTitleFont(132);
    mframe_Var1->GetYaxis()->SetLabelFont(132);
    mframe_Var1->GetYaxis()->SetTitleSize(0.05);
    mframe_Var1->GetYaxis()->SetLabelSize(0.05);
    mframe_Var1->GetXaxis()->SetTitleSize(0.05);
    mframe_Var1->GetXaxis()->SetLabelSize(0.05);
    TString Title = "";
    mframe_Var1->GetYaxis()->SetTitle(Title.Data());
    mframe_Var1->SetTitle(Title.Data());


    RooPlot* mframe_Var2 = Var2->frame();
    dataCalib->plotOn(mframe_Var2,RooFit::MarkerColor(plotSet->GetColorData(2)), 
		      RooFit::Binning(bin2), RooFit::MarkerStyle(20), RooFit::MarkerSize(2.75)); //, RooFit::Rescale(1/scaleA));
    if ( label1.Contains("MC") == true )
      {
	dataMCNW->plotOn(mframe_Var2,RooFit::MarkerColor(plotSet->GetColorData(3)), RooFit::Binning(bin1),
			 RooFit::Rescale(scaleC), RooFit::MarkerStyle(23),RooFit::MarkerSize(2.75));
      }    
    dataMC->plotOn(mframe_Var2,RooFit::MarkerColor(plotSet->GetColorData(0)), RooFit::Binning(bin2), 
		   RooFit::Rescale(scaleA), RooFit::MarkerStyle(21), RooFit::MarkerSize(2.75));
    dataCalibRW->plotOn(mframe_Var2,RooFit::MarkerColor(plotSet->GetColorData(1)), RooFit::Binning(bin2),
			RooFit::MarkerStyle(22), RooFit::MarkerSize(2.75),RooFit::Rescale(scaleB)); 
       
    mframe_Var2->GetXaxis()->SetTitle(l2.Data());
    mframe_Var2->SetLabelFont(132);
    mframe_Var2->SetTitleFont(132);
    mframe_Var2->GetXaxis()->SetTitleFont(132);
    mframe_Var2->GetXaxis()->SetLabelFont(132);
    mframe_Var2->GetYaxis()->SetTitleFont(132);
    mframe_Var2->GetYaxis()->SetLabelFont(132);
    mframe_Var2->GetYaxis()->SetTitleSize(0.05);
    mframe_Var2->GetYaxis()->SetLabelSize(0.05);
    mframe_Var2->GetXaxis()->SetTitleSize(0.05);
    mframe_Var2->GetXaxis()->SetLabelSize(0.05);
    mframe_Var2->GetYaxis()->SetTitle(Title.Data());
    mframe_Var2->SetTitle(Title.Data());

    RooPlot* mframe_PID = PID->frame();
    dataCalib->plotOn(mframe_PID,RooFit::MarkerColor(plotSet->GetColorData(2)), RooFit::Binning(bin3));
    dataCalibRW->plotOn(mframe_PID,RooFit::MarkerColor(plotSet->GetColorData(0)), RooFit::Binning(bin3));
    mframe_PID->SetTitle(Title.Data());
    mframe_PID->SetLabelFont(132);
    mframe_PID->SetTitleFont(132);

    mframe_Var1->GetYaxis()->SetRangeUser(0,mframe_Var1->GetMaximum()*1.2);
    mframe_Var2->GetYaxis()->SetRangeUser(0,mframe_Var2->GetMaximum()*1.2);
    
    TLatex* lhcbtext = new TLatex();
    lhcbtext->SetTextFont(132);
    lhcbtext->SetTextColor(1);
    lhcbtext->SetTextSize(0.07);
    lhcbtext->SetTextAlign(12);

    TText* tit = new TText();
    tit->SetTextFont(132);
    tit->SetTextColor(1);
    tit->SetTextSize(0.06);
    tit->SetTextAlign(32);

    

    TString save1 = dataCalibRW->GetName();
    TString save = dir+"/"+save1+"."+ext;
    TCanvas *ch_RW = new TCanvas("c2h_RW","",10,10,2400,1200);
    ch_RW->SetFillColor(0);
    ch_RW->Divide(2,1);
    ch_RW->cd(1);
    mframe_Var1->Draw();
    legend->Draw("same");
    lhcbtext->DrawTextNDC( 0.72 , 0.80, "LHCb");
    //tit->DrawTextNDC( 0.6, 0.85, labelMode.Data()); 
    ch_RW->cd(2);
    mframe_Var2->Draw();
    legend->Draw("same");
    lhcbtext->DrawTextNDC( 0.72 , 0.80, "LHCb");
    //ch_RW->cd(3);
    //mframe_PID->Draw();
    //legend2->Draw("same");
    ch_RW->Update();
    ch_RW->SaveAs(save.Data());

    TString savePIDK1 = dataCalibRW->GetName();
    TString savePIDK = dir+"/pidk_"+savePIDK1+"."+ext;
    TCanvas *ch_PIDK = new TCanvas("c2h_PIDK","",10,10,2400,1200);
    ch_PIDK->SetFillColor(0);
    mframe_PID->Draw();
    legend->Draw("same");
    lhcbtext->DrawTextNDC( 0.72 , 0.80, "LHCb");                                                                                                                                
    ch_PIDK->Update();
    ch_PIDK->SaveAs(savePIDK.Data());


    /*
    delete dataMC;
    delete dataMCNW;
    delete legend;
    delete legend2; 
    delete lhcbtext;
    delete tit; 
    delete ch_RW;
    delete mframe_PID;
    delete mframe_Var2;
    delete mframe_Var1; 
    delete grMC;
    delete grMCRW;
    delete grMCNW;
    delete gr;*/ 
  }
  
  RooAbsPdf* FitPDFShapeForPIDBsDsKPi(RooDataSet* data, RooRealVar* Var, TString& samplemode, PlotSettings* plotSet, bool debug)
  {
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    RooAbsPdf* pdfPID = NULL;
    RooRealVar* mean1 = NULL;
    RooRealVar* sigma1 = NULL;
    RooRealVar* c1 = NULL;
    RooRealVar* f1 = NULL;

    RooGaussian* bkg1 = NULL;
    RooExponential* bkg3 = NULL;

    Double_t meanG = 2.0;
    Double_t sigma1Var = 0.50;
    Double_t f1Var = 0.65;

    TString nameVar = "mean1G_"+samplemode;
    mean1 =  new RooRealVar(nameVar.Data(),"mean1", meanG, 1.0, 3.0); //meanG-2*meanG,  meanG+2*meanG);
    nameVar = "sigma1G_"+samplemode;
    sigma1 = new RooRealVar(nameVar.Data(),"sigma1",sigma1Var, 0.25, 1.0); //sigma1Var-sigma1Var*1.0, sigma1Var+sigma1Var*2.0); //, sigmaVar-10, sigmaVar+10);
    
    nameVar = "PIDKShape_Gaussian1_"+samplemode;
    bkg1 = new  RooGaussian(nameVar.Data(), "bkg p.d.f." , *Var, *mean1, *sigma1);
    
    Double_t c1Var  = -3.0; //-6.3627*pow(10,-2);
    nameVar = "c1_"+samplemode;
    c1 =  new RooRealVar(nameVar.Data(),"coefficient #2", c1Var, -5.0,-0.1);
    nameVar = "PIDKShape_exp_"+samplemode; //"_"+type;
    bkg3 = new  RooExponential(nameVar.Data(), "bkg p.d.f." , *Var, *c1);

    nameVar = "fG_"+samplemode; //+"_"+type;
    f1 = new RooRealVar(nameVar.Data(),"signal fraction",f1Var, 0.0, 1.0);
    nameVar = "PIDKShape_"+samplemode;
    pdfPID = new RooAddPdf(nameVar.Data(), nameVar.Data(), RooArgList(*bkg1,*bkg3),RooArgList(*f1));
    
    if ( data->numEntries() != 0 )
      {
	pdfPID->fitTo(*data,RooFit::Strategy(2),RooFit::SumW2Error(kTRUE));
      }
    mean1->setConstant();
    sigma1->setConstant();
    c1->setConstant();
    f1->setConstant();
    
    if ( plotSet->GetStatus() == true )
      {
	TLegend* legend = new TLegend( 0.50, 0.66, 0.88, 0.88 );
	legend->SetTextSize(0.05);
	legend->SetTextFont(12);
	legend->SetFillColor(4000);
	legend->SetShadowColor(0);
	legend->SetBorderSize(0);
	legend->SetTextFont(132);
	legend->SetHeader("LHCb");
	
	TGraphErrors* gr = new TGraphErrors(10);
	gr->SetName("gr");
	gr->SetLineColor(kBlack);
	gr->SetLineWidth(2);
	gr->SetMarkerStyle(20);
	gr->SetMarkerSize(1.3);
	gr->SetMarkerColor(plotSet->GetColorData(0));
	gr->Draw("P");
	
	TString labelMode = GetLabel(samplemode, debug);
	legend->AddEntry("gr",labelMode.Data(),"lep");
	
	RooPlot* frame= Var->frame();
	TString Title = "";
	frame->SetTitle(Title.Data());
	frame->SetLabelFont(132);
	frame->SetTitleFont(132);
	frame->GetXaxis()->SetTitle("log(PIDK) [1]");
	frame->GetYaxis()->SetTitleFont(132);
	frame->GetYaxis()->SetLabelFont(132);
	data->plotOn(frame,RooFit::MarkerColor(plotSet->GetColorData(0)));
	pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(0)),RooFit::LineStyle(plotSet->GetStylePdf(0)));
	nameVar = "PIDKShape_exp_"+samplemode;
	pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(1)), RooFit::LineStyle(plotSet->GetStylePdf(1)), RooFit::Components(nameVar.Data()));
	nameVar = "PIDKShape_Gaussian1_"+samplemode;
	pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(2)),  RooFit::LineStyle(plotSet->GetStylePdf(2)),RooFit::Components(nameVar.Data()));

	
	TString ext = plotSet->GetExt();
	TString dir = plotSet->GetDir();
	TString varName = Var->GetName();
	TString save = dir +"/template_"+ varName+"_"+samplemode+"."+ext;
	
	TCanvas *pidCan= new TCanvas("pidCan","",10,10,800,600);
	pidCan->SetFillColor(0);
	pidCan->cd();
	frame->Draw();
	legend->Draw("same");
	pidCan->Update();
	pidCan->SaveAs(save.Data());
      }
    return pdfPID;

  }


  RooAbsPdf* FitPDFShapeForPIDBsDsKP(RooDataSet* data, RooRealVar* Var, TString& samplemode, PlotSettings* plotSet, bool debug)
  {
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    RooAbsPdf* pdfPID = NULL;

    Double_t f1Var = 0.13448;
    Double_t f2Var = 0.37990;
    Double_t mean1Var = 3.044;
    Double_t mean2Var = 2.5895;
    Double_t mean3Var = 1.8059;
    Double_t sigma1Var = 0.27778;
    Double_t sigma2Var= 0.36536;
    Double_t sigma3Var = 0.50996;

    RooRealVar *mean1 = NULL;
    RooRealVar *mean2 = NULL;
    RooRealVar *mean3 = NULL;
    RooRealVar *sigma1  = NULL;
    RooRealVar *sigma2  = NULL;
    RooRealVar *sigma3  = NULL;
    RooRealVar *f1 = NULL;
    RooRealVar *f2 = NULL;

    TString nameVar = "mean1TR_"+samplemode;
    mean1 =  new RooRealVar(nameVar.Data(),"mean1", mean1Var, mean1Var-0.5*mean1Var, mean1Var+0.5*mean1Var);
    nameVar = "mean2TR_"+samplemode;
    mean2 = new RooRealVar(nameVar.Data(),"mean2", mean2Var, mean2Var-0.5*mean2Var, mean2Var+0.5*mean2Var);
    nameVar = "mean3TR_"+samplemode;
    mean3 = new RooRealVar(nameVar.Data(), "mean3", mean3Var, mean3Var-0.5*mean3Var, mean3Var+0.5*mean3Var); //, meanVar - 10, meanVar+10);

    nameVar = "sigma1TR_"+samplemode;
    sigma1 = new RooRealVar(nameVar.Data(),"sigma1",sigma1Var, sigma1Var-0.5*sigma1Var, sigma1Var+0.5*sigma1Var); //, sigmaVar-10, sigmaVar+10);
    nameVar = "sigma2TR_"+samplemode;
    sigma2 = new RooRealVar(nameVar.Data(),"sigma2",sigma2Var, sigma2Var-0.5*sigma2Var, sigma2Var+0.5*sigma2Var); //, sigmaVar-10, sigmaVar+10);
    nameVar = "sigma3TR_"+samplemode;
    sigma3 = new RooRealVar(nameVar.Data(),"sigma3",sigma3Var, sigma3Var-0.5*sigma3Var, sigma3Var+0.5*sigma3Var); //, sigmaVar-10, sigmaVar+10);

    nameVar = "f1TripleGaussian_"+samplemode;
    f1 = new RooRealVar(nameVar.Data(),"signal fraction",f1Var,0.0,1.0);
    nameVar = "f2TripleGaussian_"+samplemode;
    f2  = new RooRealVar(nameVar.Data(),"signal fraction",f2Var,0.0,1.0);


    nameVar = "PIDKGaussian1_"+samplemode;
    RooGaussian* bkg1 = new  RooGaussian(nameVar.Data(), "bkg p.d.f." , *Var, *mean1, *sigma1);
    nameVar = "PIDKGaussian2_"+samplemode;
    RooGaussian* bkg2 = new  RooGaussian(nameVar.Data(), "bkg p.d.f." , *Var, *mean2, *sigma2);
    nameVar = "PIDKGaussian3_"+samplemode;
    RooGaussian* bkg3 = new RooGaussian(nameVar.Data(),"signal p.d.f.",*Var, *mean3, *sigma3);
    nameVar = "PIDKShape_"+samplemode;
    pdfPID = new RooAddPdf(nameVar.Data(),"model",RooArgList(*bkg1,*bkg2, *bkg3),RooArgList(*f1,*f2),true);

    if ( data->numEntries() != 0 )
      {
	pdfPID->fitTo(*data,RooFit::Strategy(2),RooFit::SumW2Error(kTRUE));
      }
    
    mean1->setConstant();
    sigma1->setConstant();
    mean2->setConstant();
    sigma2->setConstant();
    mean3->setConstant();
    sigma3->setConstant();
    f1->setConstant();
    f2->setConstant();

    if ( plotSet->GetStatus() == true )
      {
	TLegend* legend = new TLegend( 0.50, 0.66, 0.88, 0.88 );
	legend->SetTextSize(0.05);
	legend->SetTextFont(12);
	legend->SetFillColor(4000);
	legend->SetShadowColor(0);
	legend->SetBorderSize(0);
	legend->SetTextFont(132);
	legend->SetHeader("LHCb");
	
	TGraphErrors* gr = new TGraphErrors(10);
	gr->SetName("gr");
	gr->SetLineColor(kBlack);
	gr->SetLineWidth(2);
	gr->SetMarkerStyle(20);
	gr->SetMarkerSize(1.3);
	gr->SetMarkerColor(plotSet->GetColorData(0));
	gr->Draw("P");
	TString labelMode = GetLabel(samplemode, debug);
	legend->AddEntry("gr",labelMode.Data(),"lep");
	
	RooPlot* frame= Var->frame();
	TString Title = "";
	frame->SetTitle(Title.Data());
	frame->SetLabelFont(132);
	frame->SetTitleFont(132);
	frame->GetXaxis()->SetTitle("log(PIDK) [1]");
	frame->GetYaxis()->SetTitleFont(132);
	frame->GetYaxis()->SetLabelFont(132);
	data->plotOn(frame,RooFit::MarkerColor(plotSet->GetColorData(0)));
	pdfPID->plotOn(frame, RooFit::LineColor(kBlue+2), RooFit::LineStyle(plotSet->GetStylePdf(0)));
	nameVar = "PIDKGaussian1_"+samplemode;
	pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(1)), RooFit::LineStyle(plotSet->GetStylePdf(1)), RooFit::Components(nameVar.Data()));
        nameVar = "PIDKGaussian2_"+samplemode;
	pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(2)),  RooFit::LineStyle(plotSet->GetStylePdf(2)), RooFit::Components(nameVar.Data()));
	nameVar = "PIDKGaussian3_"+samplemode;
        pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(3)),  RooFit::LineStyle(plotSet->GetStylePdf(3)),RooFit::Components(nameVar.Data()));

	
	TString ext = plotSet->GetExt();
        TString dir = plotSet->GetDir();
        TString varName = Var->GetName();
        TString save = dir +"/template_"+ varName+"_"+samplemode+"."+ext;

	TCanvas *pidCan= new TCanvas("pidCan","",10,10,800,600);
	pidCan->SetFillColor(0);
	pidCan->cd();
	frame->Draw();
	legend->Draw("same");
	pidCan->Update();
	pidCan->SaveAs(save.Data());
      }

    return pdfPID;
   
  }
  

  //===========================================================================
  // Create final RooKeysPdf for Part Reco background
  // filesDirMU - name of config .txt file from where Monte Carlo MU are loaded
  // filesDirMU - name of config .txt file from where Monte Carlo MD are loaded
  // sigMu - signature Monte Carlo MU which should be loaded
  // sigMu - signature Monte Carlo MD which should be loaded
  // mVar -  observable (for example lab0_MM)
  // workspace - workspace where Part Reco background are saved
  //==========================================================================
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 2D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  RooWorkspace* ObtainHistRatio(TString& filesDir, TString& sig,
                                MDFitterSettings* md,
                                TString& type,
                                RooWorkspace* work,
                                PlotSettings* plotSet,
                                bool debug
                                )
  {

    RooAbsData::setDefaultStorageType(RooAbsData::Tree);
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::ObtainHistRatio(...)."
                  << " Obtain 2D histogram MC/Calibration sample"
                  << std::endl;
      }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    TString bach = CheckBachelorLong(type, debug);
    TString pol = CheckPolarity(type, debug);
    TString year = CheckDataYear(type, debug);
    TString strip = CheckStrippingNumber(type, debug);

    PIDCalibrationSample calib = md->GetCalibSample(bach, year, pol, strip, debug);
    
    TString nameVar1 = md->GetVar(0);
    TString nameVar2 = md->GetVar(1);
    calib.ObtainVar1Name(nameVar1, debug);
    calib.ObtainVar2Name(nameVar2, debug);

    TString namePID = md->GetPIDKVarOutName();
    Double_t PID_up = md->GetPIDKRangeUp();
    Double_t PID_down = md->GetPIDKRangeDown();

    Double_t Var1_down = md->GetRangeDown(md->GetVar(0));
    Double_t Var1_up = md->GetRangeUp(md->GetVar(0));
    Double_t Var2_down = md->GetRangeDown(md->GetVar(1));
    Double_t Var2_up = md->GetRangeUp(md->GetVar(1));
    if ( nameVar1 == "BacEta") { Var1_down = 1.5; Var1_up = 5.0;}
    else { if ( debug ) { std::cout<<"[INFO] Applying log scale for Var1 range: "<<Var1_down<<","<<Var1_up<<")"<<std::endl; }
      Var1_down = log(Var1_down); Var1_up = log(Var1_up); }
    if ( nameVar2 == "BacEta") { Var2_down = 1.5; Var2_up = 5.0;}
    else {
      std::cout<<"[INFO] Applying log scale for Var2 range: ("<<Var2_down<<","<<Var2_up<<")"<<std::endl;
      Var2_down = log(Var2_down); Var2_up = log(Var2_up);
    }
    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(), nameVar1.Data(), Var1_down, Var1_up);
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(), nameVar2.Data(), Var2_down, Var2_up);
    RooRealVar* lab1_PIDK = new RooRealVar(namePID.Data(), namePID.Data(), PID_down, PID_up);

    
    TString label1, label2;
    if ( nameVar1 != nameVar2 )
      {
	label1 = CheckWeightLabel(nameVar1, debug);
        label2 = CheckWeightLabel(nameVar2, debug);
      }
    else { if(debug == true) std::cout<<"The same name of variables: "<<nameVar1<<"  "<<nameVar2<<std::endl; }

    if(debug == true) std::cout<<nameVar1<<" range: ("<<md->GetRangeDown(md->GetVar(0))<<","<<md->GetRangeUp(md->GetVar(0))<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar2<<" range: ("<<md->GetRangeDown(md->GetVar(1))<<","<<md->GetRangeUp(md->GetVar(1))<<")"<<std::endl;
    

    std::vector <MCBackground*> MCBkg;
    Int_t numBkg = CheckNumberOfBackgrounds(filesDir,sig, debug);
    for(int i = 1; i<numBkg+1; i++ )
      {
        MCBkg.push_back(new MCBackground(Form("MCBkg%d",i),"MCBackground",filesDir,sig,i));
        MCBkg[i-1]->Print("v");
      }

    TString ext = "pdf";

    std::vector <TH2F*> hist2Data;
    std::vector <TH2F*> hist2Ratio;
    RooDataSet* dataCalib = NULL;
    dataCalib = calib.PrepareDataSet( Var1, Var2, lab1_PIDK, plotSet, debug); // GetDataCalibSample( calib, Var1, Var2, plotSet, debug );
    TString histNameCalib = "hist2D_Calib";
    TH2F* histCalib = Get2DHist(dataCalib,Var1, Var2, md->GetBin(0), md->GetBin(1), histNameCalib, debug);
    Save2DHist(histCalib, plotSet);
    
    Double_t binMC, binData, binRatio;
    Double_t binMCErr, binDataErr, binRatioErr;
    
    
    TString l2 = "Calib";
    TString l3 = "Ratio";

    for( int i = 0; i<numBkg; i++)
      {
	TString m = MCBkg[i]->GetMode();
	TString smp = MCBkg[i]->GetPolarity();
	TString y = MCBkg[i]->GetYear();
	if ( y  != "" ) { y = "_"+y;}
	if ( (type.Contains("Kaon") == true && (m.Contains("Kst") == true   || m.Contains("K") == true)) || 
	     (type.Contains("Pion") == true && (m.Contains("Pi") == true  || m.Contains("Rho") == true)) ||
	     (type.Contains("Proton") == true && (m == "Lb2Dsp" || m == "Lb2Dsstp" )))
	  {
	    TString nm, name;
	    TString histName;
	    TString histNameR;
	    if ( type.Contains("MC") == true )
	      {
		nm = m+"_"+smp+y; 
		name="dataSetMC_"+nm;
		histName = "hist2D_"+nm;    
		histNameR = "hist2D_ratio_"+nm;
	      }
	    else
	      {
		if( debug == true) {std::cout<<"[ERROR] Wrong sample and mode"<<std::endl;} return NULL;
	      }

	    RooDataSet*  data = GetDataSet(work,name,debug);
	    if ( type.Contains("MC") == true && data->isWeighted() == false) 
	      { data = new RooDataSet(data->GetName(), data->GetTitle(), *(data->get()), RooFit::Import(*data), RooFit::WeightVar("weights"));}
	    //else {data = new RooDataSet(data->GetName(), data->GetTitle(), *(data->get()), RooFit::Import(*data)); }
	    
	    double scaleA = dataCalib->sumEntries()/data->sumEntries();
	    
	    hist2Data.push_back(Get2DHist(data,Var1, Var2, md->GetBin(0), md->GetBin(1), histName, debug));
	    
	    hist2Ratio.push_back(new TH2F(histNameR.Data(),histNameR.Data(),
                                          md->GetBin(0),Var1_down,Var1_up,
                                          md->GetBin(1),Var2_down,Var2_up));

	    int sizehist = hist2Ratio.size();
	    hist2Ratio[sizehist-1]->SetStats(kFALSE);
	    hist2Ratio[sizehist-1]->GetXaxis()->SetTitle(label1.Data());
	    hist2Ratio[sizehist-1]->GetYaxis()->SetTitle(label2.Data());
	    TString TitleHist="";
	    hist2Ratio[sizehist-1]->SetTitle(TitleHist.Data());
	    
	    for(int k = 1; k<md->GetBin(0); k++)
	      {
		for (int j = 1; j<md->GetBin(1); j++)
		  {
		    binMC = histCalib->GetBinContent(k,j);
		    binData = hist2Data[sizehist-1]->GetBinContent(k,j);
		    binMCErr = histCalib->GetBinError(k,j);
		    binDataErr = hist2Data[sizehist-1]->GetBinError(k,j);
		    
		    if ( binMC == 0 || binData < 0 || binData == 0 ) { binRatio = 0; binRatioErr=0; }
		    else {
		      binRatio = binData/binMC*scaleA;
		      binRatioErr = binRatio*sqrt((binDataErr*binDataErr)/(binData*binData)+(binMCErr*binMCErr)/(binMC*binMC));
		    }
		    //	if( debug == true) std::cout<<"bin1D: "<<k<<" bin2D: "<<j<<" scale: "<<scaleA<<" binMC: "<<binMC<<" +/- "<<binMCErr<<" binData "<<binData<<" +/- "<<binDataErr<<" Ratio: "<<binRatio<<" +/- "<<binRatioErr<<std::endl;
		    hist2Ratio[sizehist-1]->SetBinContent(k,j,binRatio);
		    hist2Ratio[sizehist-1]->SetBinError(k,j,binRatioErr);
		  }
	      }
	    Save2DComparison(hist2Data[sizehist-1], type, histCalib, l2, hist2Ratio[sizehist-1], l3, plotSet);
	    
	    //Save2DHist(hist2Data[sizehist-1], ext);
	    //Save2DHist(hist2Ratio[sizehist-1], ext);
	    work->import(*hist2Ratio[sizehist-1]);
	    work->import(*hist2Data[sizehist-1]);
	    //delete data;
	  }
      }

    delete Var1;
    delete Var2; 
    delete dataCalib;
    delete histCalib; 

  return work;


  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 2D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  RooWorkspace* ObtainPIDShapeFromCalibSample(TString& filesDir, TString& sig,
                                              MDFitterSettings* md,
                                              TString& type,
                                              RooWorkspace* work,
                                              PlotSettings* plotSet,
                                              bool debug)
  {
  
    RooAbsData::setDefaultStorageType(RooAbsData::Tree);

    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::ObtainPIDShapeFromCalibSample(...)."
                  << " Obtain PID RooKeysPdf for partially reconstructed backgrounds from calibration sample"
                  << std::endl;
      }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    TString bach = CheckBachelorLong(type, debug);
    TString pol = CheckPolarity(type, debug);
    TString year = CheckDataYear(type, debug);
    TString strip = CheckStrippingNumber(type, debug);

    PIDCalibrationSample calib = md->GetCalibSample(bach, year, pol, strip, debug);
    
    TString nameVar1 = md->GetVar(0);
    TString nameVar2 = md->GetVar(1);
    TString namePID = md->GetPIDKVarOutName();
    Double_t PID_up = md->GetPIDKRangeUp();
    Double_t PID_down = md->GetPIDKRangeDown();
    Int_t bin1 = md->GetBin(0);
    Int_t bin2 = md->GetBin(1);

    calib.ObtainVar1Name(nameVar1, debug);
    calib.ObtainVar2Name(nameVar2, debug);

    Double_t Var1_down = md->GetRangeDown(md->GetVar(0));
    Double_t Var1_up = md->GetRangeUp(md->GetVar(0));
    Double_t Var2_down = md->GetRangeDown(md->GetVar(1));
    Double_t Var2_up = md->GetRangeUp(md->GetVar(1));
    if ( nameVar1 == "BacEta") { Var1_down = 1.5; Var1_up = 5.0;}
    else { if ( debug ) { std::cout<<"[INFO] Applying log scale for Var1 range: ("<<Var1_down<<","<<Var1_up<<")"<<std::endl; }
      Var1_down = log(Var1_down); Var1_up = log(Var1_up); }
    if ( nameVar2 == "BacEta") { Var2_down = 1.5; Var2_up = 5.0;}
    else {
      std::cout<<"[INFO] Applying log scale for Var2 range: ("<<Var2_down<<","<<Var2_up<<")"<<std::endl;
      Var2_down = log(Var2_down); Var2_up = log(Var2_up);
    }
    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(), nameVar1.Data(), Var1_down, Var1_up);
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(), nameVar2.Data(), Var2_down, Var2_up);

    RooRealVar* lab1_PIDK = new RooRealVar(namePID.Data(), namePID.Data(), PID_down, PID_up);
     
    if(debug == true) std::cout<<nameVar1<<" range: ("<<Var1_down<<","<<Var1_up<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar2<<" range: ("<<Var2_down<<","<<Var2_up<<")"<<std::endl;

    std::vector <MCBackground*> MCBkg;
    Int_t numBkg = CheckNumberOfBackgrounds(filesDir,sig, debug);
    for(int i = 1; i<numBkg+1; i++ )
      {
        MCBkg.push_back(new MCBackground(Form("MCBkg%d",i),"MCBackground",filesDir,sig,i));
	MCBkg[i-1]->Print("v");
      }

    TString ext = "pdf";

    RooDataSet* dataC = calib.PrepareDataSet( Var1, Var2, lab1_PIDK, plotSet, debug);
    if (debug == true ) { dataC->Print("v"); }

    RooRealVar* CalibWeight = NULL;
    RooRealVar* CalibVar1 = NULL;
    RooRealVar* CalibVar2 = NULL;
    RooRealVar* CalibPIDK = NULL; 
    TString nameDLL = calib.CheckPIDVarName();
    TString nVar1 = calib.GetVar1Name();
    TString nVar2 = calib.GetVar2Name();
    TString swlabel = calib.GetWeightName();

    if (dataC->isWeighted() == false )
      {
	CalibWeight = (RooRealVar*)dataC->get()->find(swlabel.Data());
      }
    CalibPIDK = (RooRealVar*)dataC->get()->find(namePID.Data());
    CalibVar1 = (RooRealVar*)dataC->get()->find(nameVar1.Data());
    CalibVar2 = (RooRealVar*)dataC->get()->find(nameVar2.Data());

    if (debug == true )
      {
        if ( CalibVar1 != NULL ) { std::cout<<"[INFO] Read "<<nameVar1<<" from "<<dataC->GetName()<<std::endl; } else { std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
        if ( CalibVar2 != NULL ) { std::cout<<"[INFO] Read "<<nameVar2<<" from "<<dataC->GetName()<<std::endl; } else{ std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
	if ( CalibPIDK != NULL ) { std::cout<<"[INFO] Read "<<namePID<<" from "<<dataC->GetName()<<std::endl; } else{ std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
        if ( CalibWeight != NULL ) { std::cout<<"[INFO] Read "<<swlabel<<" from "<<dataC->GetName()<<std::endl; }
        else{
          if ( dataC->isWeighted() == true ) { std::cout<<"[INFO] Weight directly taken from RooDataSet"<<std::endl; }
          else{ std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
        }
      }
    
    //treeC->Print();
    Double_t wRW(0), wA(0);
    TH2F* histRW;

    TString l1 = "MC";
    TString l2 = "Calib";
    TString l3 = "Calib weighted";

    RooDataSet* dataCalib = NULL;
    dataCalib = calib.PrepareDataSet( Var1, Var2, lab1_PIDK, plotSet, debug); 
    
    TString histNameCalib = "hist2D_Calib";
    TH2F* histCalib = Get2DHist(dataCalib,Var1, Var2, bin1, bin2, histNameCalib, debug);

    RooAbsPdf* pdfPID[numBkg];
        
    for( int i = 0; i<numBkg; i++)
      {
		
	TString m = MCBkg[i]->GetMode();
        TString smp = MCBkg[i]->GetPolarity();
	TString y = MCBkg[i]->GetYear(); 
	if ( y != "") { y = "_"+y; }

        if ( (type.Contains("Kaon") == true && (m.Contains("Kst") == true   || m.Contains("K") == true)) ||
             (type.Contains("Pion") == true && (m.Contains("Pi") == true  || m.Contains("Rho") == true)) ||
             (type.Contains("Proton") == true && (m == "Lb2Dsp" || m == "Lb2Dsstp" )))
	  {
	    TH2F* hist = NULL;
	    TH2F* histMC = NULL;
	    
	    TString nm, name;
	    TString histName;
	    TString histNameR;
	    TString nameCalib;
	    if ( type.Contains("MC") == true )
	      {
		
		nm = m+"_"+smp+y;
		histName = "hist2D_"+nm;
		histNameR = "hist2D_ratio_"+nm;
		nameCalib = "CalibSample_"+nm;
	      }
	    else
	      {
		if( debug == true) std::cout<<"[ERROR] Wrong sample and mode"<<std::endl;
	      }
	    
	    if( debug == true) std::cout<<"Calculating for "<<nm<<std::endl;
	    hist = (TH2F*)work->obj(histNameR.Data());
	    if ( hist != NULL ) { std::cout<<"Read histogram: "<<hist->GetName()<<std::endl;} 
	    else {std::cout<<" Cannot read histogram: "<<histName.Data()<<std::endl;}
	    histMC = (TH2F*)work->obj(histName.Data());
    
	    TString namew = "weights";
	    RooRealVar* weights;
	    weights = new RooRealVar(namew.Data(), namew.Data(), -50.0, 50.0 );
	    RooDataSet* dataRW = NULL;

	    TH1* histPID = NULL;
            TString namehist = "histPID_"+nm;
	    if( type.Contains("MC") == true && ( type.Contains("Bs2DsPi")==true || type.Contains("Bs2DsstPi") == true ))
	      {
		histPID = new TH1D(namehist.Data(), namehist.Data(), 200, PID_down, PID_up);
		dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights), namew.Data());
	      }
	    else
	      {
		histPID = new TH1D(namehist.Data(), namehist.Data(), 50, PID_down, PID_up);
		dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights), namew.Data());
	      }

	    for (Long64_t jentry=0; jentry<dataC->numEntries(); jentry++)                                                                                            
	      {         
		const RooArgSet* setInt = dataC->get(jentry);
		Double_t Var13 = CalibVar1->getValV(setInt);
		Double_t Var23 = CalibVar2->getValV(setInt);
		Double_t PID3 = CalibPIDK->getValV(setInt); 
		Double_t nsig_sw3 = 1.0;

		if (  dataC->isWeighted() == true )
		  {
		    nsig_sw3 = dataC->weight();
		  }
		else
		  {
		    nsig_sw3 = CalibWeight->getValV(setInt);
		  }

		if( type.Contains("MC") == true && ( type.Contains("Bs2DsPi")==true || type.Contains("Bs2DsstPi") == true ))
		  {
		    //PID3 = -PID3;
		    lab1_PIDK->setVal(PID3);
		  }
		else
		  {
		    lab1_PIDK->setVal(PID3);
		  }
		Var1->setVal(Var13);
		Var2->setVal(Var23);
	       
		Int_t binRW = hist->FindBin(Var13,Var23);
		wRW = hist->GetBinContent(binRW);
		wA = nsig_sw3*wRW;
		//std::cout<<" weight: "<<wA<<" nsigSW: "<<nsig_sw3<<" wRW "<<wRW<<" "<<nameVar1<<": "<<Var13<<" "<<nameVar2<<": "<<Var23<<std::endl;
		weights->setVal(wA);
		if ( ( ( type.Contains("Bs2DsPi") == true || type.Contains("Bs2DsstPi") == true ) && type.Contains("MC") == true))
		  {
		    if ( PID3 > PID_down && PID3 < PID_up)
		      {
			dataRW->add(RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights),wA,0);
		      }
		  }
		else
		  {
		    if (PID3 > PID_down && PID3 < PID_up)
		      {
			dataRW->add(RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights),wA,0);
		      }
                  }
	      }
	    
	    
	    histRW = NULL;
	    histName = "hist2D_rw_"+nm;
	    histRW = Get2DHist(dataRW, Var1, Var2, bin1, bin2, histName, debug);
	    Save2DComparison(histMC, type, histCalib, l2, histRW, l3, plotSet);
	    Int_t bin3 = 50;
	    Int_t binHist = 1;

	    RooBinned1DQuinticBase<RooAbsPdf>* pdfPID2 = NULL;
	    if ( (type.Contains("Pi") == true && type.Contains("MC") == true) )
              {
                if ( type.Contains("Pion") )
		  {
		    histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(100, PID_down, PID_up)); //45,log(0.0001),log(-PID_down)));                   
		    binHist = 100;
		  }
		else
		  {
		    histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(50, PID_down, PID_up));
		    binHist = 50;
		  }
	      }
            else
              {
		binHist = 50;
		histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(50,PID_down,PID_up));
              }
	    histPID->SetName(namehist.Data());
	    Double_t zero = 1e-20;
	    for(int k = 1; k<binHist; k++)
	      {
		Double_t cont = histPID->GetBinContent(k);
		if( cont < 0 ) { histPID->SetBinContent(k,zero); }
	      }
	    
	   	    	    
	    pdfPID[i] = NULL;
	    if( type.Contains("MC") == true && ( type.Contains("Bs2DsPi")==true || type.Contains("Bs2DsstPi") == true ) ) 
	      {
		TString dir = "PlotBsDsPi2D";
		if (debug == true) PlotWeightingSample(nm, dataCalib, dataRW, Var1, Var2, lab1_PIDK, bin1, bin2, bin3, 
						       type, l2, l3, work,  plotSet, debug);
		if ( type.Contains("Pion") == true)
		  {
		    //pdfPID[i] = FitPDFShapeForPIDBsDsPiPi(dataRW, lab1_PIDK, nm, plotSet, debug);
		    //work->import(*pdfPID[i]);
		    TString namepdf = "PIDKShape_"+nm;
                    pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
                    RooAbsPdf* pdfSave = pdfPID2;
		    TString t = "";
                    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nm, t, plotSet, debug );
                    work->import(*pdfPID2);
		  }
		else
		  {
		    TString namepdf = "PIDKShape_"+nm;
                    pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
                    RooAbsPdf* pdfSave = pdfPID2;
                    TString t = "";
                    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nm, t, plotSet, debug );
                    work->import(*pdfPID2);

		    //pdfPID[i] = FitPDFShapeForPIDBsDsPiK(dataRW, lab1_PIDK, nm,  plotSet, debug);
		    //work->import(*pdfPID[i]);
		  }
	      }
	    else if ( type.Contains("Bs2DsK") == true || type.Contains("Bs2DsstK") == true )
	      {
		TString dir = "PlotBsDsK2D";
		if (debug == true) PlotWeightingSample(nm, dataCalib, dataRW, Var1, Var2, lab1_PIDK, bin1, bin2, bin3, 
						       type, l2, l3, work, plotSet,  debug);
		if ( type.Contains("Pion") == true)
		  {
		    TString namepdf = "PIDKShape_"+nm;
		    TString strip = CheckStripping(type,debug);
		    if ( strip == "str17" )
		      {
			pdfPID[i] = FitPDFShapeForPIDBsDsKPi(dataRW, lab1_PIDK, nm,  plotSet,  debug);                                
			work->import(*pdfPID[i]);   
		      }
		    else
		      {
			pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
			RooAbsPdf* pdfSave = pdfPID2;
			TString t = "";
			SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nm, t, plotSet, debug );
			work->import(*pdfPID2);
		      }
		  }
		else if ( type.Contains("Kaon") == true)
		  {
		    //pdfPID[i] = FitPDFShapeForPIDBsDsKK(dataRW, lab1_PIDK, nm,  debug);
		    TString namepdf = "PIDKShape_"+nm;
		    pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
		    RooAbsPdf* pdfSave = pdfPID2;
		    TString t = ""; 
		    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nm, t, plotSet, debug );
		    work->import(*pdfPID2);
		  }
		else
		  {
		    if ( strip == "str17" )
                      {
			pdfPID[i] = FitPDFShapeForPIDBsDsKP(dataRW, lab1_PIDK, nm, plotSet,  debug);
			work->import(*pdfPID[i]);
		      }
		    else
		      {
			TString namepdf = "PIDKShape_"+nm;
			pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
			RooAbsPdf* pdfSave = pdfPID2;
                        TString t = "";
			SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nm, t, plotSet, debug );
                        work->import(*pdfPID2);
		      }
		  }
		//delete pdfPID2; 
		//delete dataRW; 
		//delete histPID; 
	      }
	  }
      }
    delete Var1;
    delete Var2;
    delete lab1_PIDK;
    delete dataC;
    //   delete CalibWeight;
    //delete CalibVar1;
    //delete CalibVar2;
    //delete CalibPIDK;
    //delete dataCalib;
    //delete histCalib;
    
    return work;
  } 
  

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 2D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  RooWorkspace* ObtainHistRatioOneSample(MDFitterSettings* md,
                                         TString& type,
                                         RooWorkspace* work,
                                         PlotSettings* plotSet,
                                         bool debug
                                         )
    
  {
    RooAbsData::setDefaultStorageType(RooAbsData::Tree);
    
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::ObtainHistRatioOneSample(...)."
                  << " Obtain 2D histogram MC/Calibration sample"
                  << std::endl;
      }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    TString bach = CheckBachelorLong(type, debug);
    TString pol = CheckPolarity(type, debug);
    TString year = CheckDataYear(type, debug);
    TString strip = CheckStrippingNumber(type, debug);

    PIDCalibrationSample calib = md->GetCalibSample(bach, year, pol, strip, debug);

    TString nameVar1 = md->GetVar(0);
    TString nameVar2 = md->GetVar(1);
    TString namePID = md->GetPIDKVarOutName();
    Double_t PID_up = md->GetPIDKRangeUp();
    Double_t PID_down = md->GetPIDKRangeDown();
    Int_t bin1 = md->GetBin(0);
    Int_t bin2 = md->GetBin(1);

    calib.ObtainVar1Name(nameVar1, debug);
    calib.ObtainVar2Name(nameVar2, debug);

    Double_t Var1_down = md->GetRangeDown(md->GetVar(0));
    Double_t Var1_up = md->GetRangeUp(md->GetVar(0));
    Double_t Var2_down = md->GetRangeDown(md->GetVar(1));
    Double_t Var2_up = md->GetRangeUp(md->GetVar(1));
    if ( nameVar1 == "BacEta") { Var1_down = 1.5; Var1_up = 5.0;}
    else { if ( debug ) { std::cout<<"[INFO] Applying log scale for Var1 range: "<<Var1_down<<","<<Var1_up<<")"<<std::endl; }
      Var1_down = log(Var1_down); Var1_up = log(Var1_up); }
    if ( nameVar2 == "BacEta") { Var2_down = 1.5; Var2_up = 5.0;}
    else {
      std::cout<<"[INFO] Applying log scale for Var2 range: ("<<Var2_down<<","<<Var2_up<<")"<<std::endl;
      Var2_down = log(Var2_down); Var2_up = log(Var2_up);
    }
    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(), nameVar1.Data(), Var1_down, Var1_up);
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(), nameVar2.Data(), Var2_down, Var2_up);
    RooRealVar* lab1_PIDK = new RooRealVar(namePID.Data(), namePID.Data(), PID_down, PID_up);

    TString label1, label2;
    if ( nameVar1 != nameVar2 )
      {
        label1 = CheckWeightLabel(nameVar1, debug);
	label2 = CheckWeightLabel(nameVar2, debug);
      }
    else { if(debug == true) std::cout<<"The same name of variables: "<<nameVar1<<"  "<<nameVar2<<std::endl; }

    if(debug == true) std::cout<<nameVar1<<" range: ("<<Var1_down<<","<<Var1_up<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar2<<" range: ("<<Var2_down<<","<<Var2_up<<")"<<std::endl;

    std::vector <std::string> FileName;
    std::vector <std::string> mode;

    TString ext = "pdf";

    std::vector <TH2F*> hist2Data;
    std::vector <TH2F*> hist2Ratio;
    RooDataSet* dataCalib = calib.PrepareDataSet( Var1, Var2, lab1_PIDK, plotSet, debug);
    TString histNameCalib = "hist2D_Calib";
    TH2F* histCalib = Get2DHist(dataCalib,Var1, Var2, bin1, bin2, histNameCalib, debug);
    //Save2DHist(histCalib, plotSet);
    
    Double_t binMC, binData, binRatio;
    Double_t binMCErr, binDataErr, binRatioErr;

    TString l2 = "Calib";
    TString l3 = "Ratio";

    std::vector <TString> names = CheckWeightNames(type, debug);
    TString nm = names[0];
    TString name = names[1]; 
    TString histName = names[2];
    TString histNameR = names [3] ;
   

    RooDataSet*  data = NULL;

    if ( type.Contains("Comb") == true )
      {
	PIDCalibrationSample calibComb = md->GetCalibSample("Combinatorial", year, pol, strip, debug);
	if ( md->CheckPIDComboShapeForDsModes() )
	  {
	    TString dmode = CheckDMode(type,debug);
	    if ( dmode == "kkpi" || dmode == ""){ dmode = CheckKKPiMode(type, debug);}
	    name = calibComb.GetDataName();
	    name = name +"_"+pol+"_"+dmode+"_"+year;
	    data = GetDataSet(work,name,debug);
	    TString pre = "Comb"; 
	    if ( type.Contains("Kaon") == true ) { pre = "CombK"; }
	    else if ( type.Contains("Pion") == true ) { pre = "CombPi"; }
	    else if ( type.Contains("Proton") == true ) { pre = "CombP"; }
	    histName = "hist2D_"+pre+"_"+pol+"_"+dmode+"_"+year;
	    histNameR = "hist2D_"+pre+"_ratio_"+pol+"_"+dmode+"_"+year;
	    TString newName = "CalibSampleCombinatorial_"+pre+"_"+pol+"_"+dmode+"_"+year;
            data = (RooDataSet*) data->Clone(newName.Data());

	  }
	else
	  {
	    data = calibComb.PrepareDataSet( Var1, Var2, NULL, plotSet, debug);
	  }
      }
    else
      {
	data = GetDataSet(work,name,debug);
      }

    //if ( type.Contains("MC") == true )
    if ( data->isWeighted() == false )
      {
	if ( debug == true ) { std::cout<<"[INFO] Data sample: "<<data->GetTitle()<<" not weighted, apply weights: "<<std::endl; } 
	data = new RooDataSet(data->GetName(), data->GetTitle(), *(data->get()), RooFit::Import(*data), RooFit::WeightVar("weights"));
      }
    double scaleA = dataCalib->sumEntries()/data->sumEntries();
    if ( debug )
      {
	std::cout<<"[INFO] scale = "<<scaleA<<"  = ( "<<dataCalib->sumEntries()<<" / "<< data->sumEntries() <<" ) "<<std::endl; 
      }
    hist2Data.push_back(Get2DHist(data,Var1, Var2, bin1, bin2, histName, debug));
    hist2Ratio.push_back(new TH2F(histNameR.Data(),histNameR.Data(),
                                  bin1,Var1_down,Var1_up,
                                  bin2,Var2_down,Var2_up));
    int sizehist = hist2Ratio.size();
    hist2Ratio[sizehist-1]->SetStats(kFALSE);
    hist2Ratio[sizehist-1]->GetXaxis()->SetTitle(label1.Data());
    hist2Ratio[sizehist-1]->GetYaxis()->SetTitle(label2.Data());
    TString TitleHist="";
    hist2Ratio[sizehist-1]->SetTitle(TitleHist.Data());
    
    for(int k = 1; k<bin1; k++)
      {
	for (int j = 1; j<bin2; j++)
	  {
	    //std::cout<<"k"<<k<<" j"<<j<<std::endl;
	    binMC = histCalib->GetBinContent(k,j);
	    binData = hist2Data[sizehist-1]->GetBinContent(k,j);
	    binMCErr = histCalib->GetBinError(k,j);
	    binDataErr = hist2Data[sizehist-1]->GetBinError(k,j);
	    
	    if ( binMC == 0 || binData < 0 || binData == 0 ) { binRatio = 0; binRatioErr=0; }
	    else {
	      binRatio = binData/binMC*scaleA;
	      binRatioErr = binRatio*sqrt(((binDataErr*binDataErr)/(binData*binData))+((binMCErr*binMCErr)/(binMC*binMC)));
	    }
	    if( debug == true) std::cout<<"bin1D: "<<k<<" bin2D: "<<j<<" scale: "<<scaleA<<" binMC: "<<binMC<<" +/- "<<binMCErr<<" binData "<<binData<<" +/- "<<binDataErr<<" Ratio: "<<binRatio<<" +/- "<<binRatioErr<<std::endl;
	    hist2Ratio[sizehist-1]->SetBinContent(k,j,binRatio);
	    hist2Ratio[sizehist-1]->SetBinError(k,j,binRatioErr);
	  }
      }
    Save2DComparison(hist2Data[sizehist-1], type, histCalib, l2, hist2Ratio[sizehist-1], l3, plotSet);
    //Save2DHist(hist2Data[sizehist-1], ext);
    //Save2DHist(hist2Ratio[sizehist-1], ext);
    work->import(*hist2Ratio[sizehist-1],kTRUE);
    work->import(*hist2Data[sizehist-1],kTRUE);

    if ( type.Contains("Comb") == true) {  work->import(*data); }
    
    delete Var1;
    delete Var2;
    delete dataCalib;
    delete histCalib;

    return work;
    
  }
  

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 2D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  
  RooWorkspace* ObtainPIDShapeFromCalibSampleOneSample(MDFitterSettings* md,
                                                       TString& type,
                                                       RooWorkspace* work,
                                                       PlotSettings* plotSet,
                                                       bool debug)
  {
    RooAbsData::setDefaultStorageType(RooAbsData::Tree);

    if ( debug == true)
      {
        std::cout << "[INFO] ==> WeightingUtils::ObtainPIDShapeFromCalibSample(...)."
                  << " Obtain PID RooKeysPdf for partially reconstructed backgrounds from calibration sample"
                  << std::endl;
      }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }


    TString bach = CheckBachelorLong(type, debug);
    TString pol = CheckPolarity(type, debug);
    TString year = CheckDataYear(type, debug);
    TString strip = CheckStrippingNumber(type, debug);

    PIDCalibrationSample calib = md->GetCalibSample(bach, year, pol, strip, debug);

    TString nameVar1 = md->GetVar(0);
    TString nameVar2 = md->GetVar(1);
    TString namePID = md->GetPIDKVarOutName();
    Double_t PID_up = md->GetPIDKRangeUp();
    Double_t PID_down = md->GetPIDKRangeDown();
    Int_t bin1 = md->GetBin(0);
    Int_t bin2 = md->GetBin(1);

    calib.ObtainVar1Name(nameVar1, debug);
    calib.ObtainVar2Name(nameVar2, debug);

    Double_t Var1_down = md->GetRangeDown(md->GetVar(0));
    Double_t Var1_up = md->GetRangeUp(md->GetVar(0));
    Double_t Var2_down = md->GetRangeDown(md->GetVar(1));
    Double_t Var2_up = md->GetRangeUp(md->GetVar(1));
    if ( nameVar1 == "BacEta") { Var1_down = 1.5; Var1_up = 5.0;}
    else { if ( debug ) { std::cout<<"[INFO] Applying log scale for Var1 range: "<<Var1_down<<","<<Var1_up<<")"<<std::endl; }
      Var1_down = log(Var1_down); Var1_up = log(Var1_up); }
    if ( nameVar2 == "BacEta") { Var2_down = 1.5; Var2_up = 5.0;}
    else {
      std::cout<<"[INFO] Applying log scale for Var2 range: ("<<Var2_down<<","<<Var2_up<<")"<<std::endl;
      Var2_down = log(Var2_down); Var2_up = log(Var2_up);
    }
    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(), nameVar1.Data(), Var1_down, Var1_up);
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(), nameVar2.Data(), Var2_down, Var2_up);

    RooRealVar* lab1_PIDK = new RooRealVar(namePID.Data(), namePID.Data(), PID_down, PID_up);

    
    if(debug == true) std::cout<<nameVar1<<" range: ("<<Var1_down<<","<<Var1_up<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar2<<" range: ("<<Var2_down<<","<<Var2_up<<")"<<std::endl;

    RooDataSet* dataC = calib.PrepareDataSet( Var1, Var2, lab1_PIDK, plotSet, debug);
    if (debug == true ) { dataC->Print("v"); }

    RooRealVar* CalibWeight = NULL;
    RooRealVar* CalibVar1 = NULL;
    RooRealVar* CalibVar2 = NULL;
    RooRealVar* CalibPIDK = NULL;
    //TString nameDLL = calib.CheckPIDVarName();
    //TString nVar1 = Var1->GetName(); //calib.GetVar1Name();
    //TString nVar2 = Var2calib.GetVar2Name();
    //TString swlabel = calib.GetWeightName();

    if (dataC->isWeighted() == false )
      {
        CalibWeight = (RooRealVar*)dataC->get()->find("weights");
      }
    CalibPIDK = (RooRealVar*)dataC->get()->find(namePID.Data());
    CalibVar1 = (RooRealVar*)dataC->get()->find(nameVar1.Data());
    CalibVar2 = (RooRealVar*)dataC->get()->find(nameVar2.Data());

    if (debug == true )
      {
	if ( CalibVar1 != NULL ) { std::cout<<"[INFO] Read "<<nameVar1<<" from "<<dataC->GetName()<<std::endl; } else { std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
        if ( CalibVar2 != NULL ) { std::cout<<"[INFO] Read "<<nameVar2<<" from "<<dataC->GetName()<<std::endl; } else{ std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
        if ( CalibPIDK != NULL ) { std::cout<<"[INFO] Read "<<namePID<<" from "<<dataC->GetName()<<std::endl; } else{ std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
        if ( CalibWeight != NULL ) { std::cout<<"[INFO] Read weights from "<<dataC->GetName()<<std::endl; }
	else{
          if ( dataC->isWeighted() == true ) { std::cout<<"[INFO] Weight directly taken from RooDataSet"<<std::endl; }
          else{ std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
        }
      }

    Double_t wRW(0), wA(0);
    TH2F* histRW;
    
    //TString l1 = "MC";
    TString l2 = "Calib";
    TString l3 = "Calib weighted";

    //RooDataSet* dataCalib = dataC->Clone("data"); // calib.PrepareDataSet( Var1, Var2, NULL, plotSet, debug);
    TString histNameCalib = "hist2D_Calib";
    TH2F* histCalib = Get2DHist(dataC,Var1, Var2, bin1, bin2, histNameCalib, debug);

    RooAbsPdf* pdfPID;

    TH2F* hist = NULL;
    TH2F* histMC = NULL;

    if (hist) {}
    if (histMC) {}

    std::cout<<"type: "<<type<<std::endl;
    std::vector <TString> names = CheckWeightNames(type, debug);
    TString nm = names[0];
    TString name = names[1];
    TString histName = names[2];
    TString histNameR = names [3] ;
    TString nameCalib = names[4];
    TString sample = names[5];
    TString mode = names[6];
    
    TString nn;
    if( type.Contains("Comb") == true) 
      { 
	PIDCalibrationSample calibComb = md->GetCalibSample("Combinatorial", year, pol, strip, debug);
        if ( md->CheckPIDComboShapeForDsModes() )
          {
            TString dmode = CheckDMode(type,debug);
	    if ( dmode == "kkpi" || dmode == ""){ dmode = CheckKKPiMode(type, debug);}
	    nm = pol+"_"+dmode+"_"+year;
	    TString pre= "Comb";
	    if ( type.Contains("Kaon") == true ) { pre = "CombK"; }
            else if ( type.Contains("Pion") == true ) { pre = "CombPi"; }
            else if ( type.Contains("Proton") == true ) { pre = "CombP"; }
            histName = "hist2D_"+pre+"_"+pol+"_"+dmode+"_"+year;
            histNameR = "hist2D_"+pre+"_ratio_"+pol+"_"+dmode+"_"+year;
	    nn = "Combinatorial_"+pre+"_"+pol+"_"+dmode+"_"+year;
          }
        else
          {
	    nn = calibComb.GetLabel(); 
	  }
      }
 
    else if (type.Contains("Bs2DsPi") == true && type.Contains("MC") != true) { nn = "Bs2DsPi_"+nm; }
    else {nn=nm;}

    hist = (TH2F*)work->obj(histNameR.Data());
    if ( hist != NULL ) { std::cout<<"[INFO] Read histogram: "<<hist->GetName()<<std::endl;}
    else {std::cout<<"[ERROR] Cannot read histogram: "<<histNameR.Data()<<std::endl;}
    histMC = (TH2F*)work->obj(histName.Data());
    if ( histMC != NULL ) { std::cout<<"[INFO] Read histogram: "<<histMC->GetName()<<std::endl;}
    else {std::cout<<"[ERROR] Cannot read histogram: "<<histName.Data()<<std::endl;}


    TString namew = "weights";
    RooRealVar* weights;
    weights = new RooRealVar(namew.Data(), namew.Data(), -50.0, 50.0 );
    //TString nameCalib = "CalibSample_"+nm;
    RooDataSet* dataRW = NULL;
    TH1* histPID = NULL;
    TString namehist = "histPID_"+nn;

    if ( (type.Contains("Bs2DsPi") == true && type.Contains("MC") == true) || type.Contains("DPi") == true 
	 || type.Contains("CombPi") == true || (type.Contains("Bs2DsstPi") == true && type.Contains("MC") == true) )
      {
	dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights), namew.Data());
	//histPID = new TH1D(namehist.Data(), namehist.Data(), 200, PID_down, PID_up); //50, log(0.0001), log(-PID_down));
      }
    else
      {
	dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights), namew.Data());
	///	histPID = new TH1D(namehist.Data(), namehist.Data(), 50, PID_down, PID_up);
      }
	   
    for (Long64_t jentry=0; jentry<dataC->numEntries(); jentry++)
      {
	const RooArgSet* setInt = dataC->get(jentry);
	Double_t Var13 = CalibVar1->getValV(setInt);
	Double_t Var23 = CalibVar2->getValV(setInt);
	Double_t PID3 = CalibPIDK->getValV(setInt);
	Double_t nsig_sw3 = 1.0;

	if (  dataC->isWeighted() == true )
	  {
	    nsig_sw3 = dataC->weight();
	  }
	else
	  {
	    nsig_sw3 = CalibWeight->getValV(setInt);
	  }
	lab1_PIDK->setVal(PID3);
	Var1->setVal(Var13);
	Var2->setVal(Var23);

	//std::cout<<"Var13: "<<Var13<<" Var23: "<<Var23<<std::endl;
	Int_t binRW = hist->FindBin(Var13,Var23);
	wRW = hist->GetBinContent(binRW);
	wA = nsig_sw3*wRW;
	//std::cout<<" weight: "<<wA<<" nsigSW: "<<nsig_sw3<<" wRW "<<wRW<<" "<<nameVar1<<": "<<Var13<<" "<<nameVar2<<": "<<Var23<<std::endl;
	weights->setVal(wA);
	if ( (type.Contains("Bs2DsPi") == true && type.Contains("MC") == true) || type.Contains("DPi") == true || 
	     type.Contains("CombPi") == true || (type.Contains("Bs2DsstPi") == true && type.Contains("MC") == true)) 
	  {
	    if ( PID3 > PID_down && PID3 < PID_up)
	      {
		dataRW->add(RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights),wA,0);
	      }
	  }
	else
	  {
	    if (PID3 > PID_down && PID3 < PID_up)
	      {
		dataRW->add(RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights),wA,0);
	      }
	  }
      }
  
    if ( dataRW != NULL ) 
      { 
	if ( debug )
	  {
	    std::cout<<"[INFO] Created weighted RooDataSet: "<<dataRW->GetName()<<" with number of entries: "<<dataRW->numEntries()<<" and sum: "<<dataRW->sumEntries()<<std::endl; 
	  }
      }
    else
      {
	std::cout<<"[ERROR] Weighted data set not created"<<std::endl; 
      }
  
    histRW = NULL;
    histName = "hist2D_rw_"+nm;
    histRW = Get2DHist(dataRW, Var1, Var2, bin1, bin2, histName, debug);
    Save2DComparison(histMC, type, histCalib, l2, histRW, l3, plotSet);
    Int_t bin3 = 50;
    Int_t histBin = 1;
    RooBinned1DQuinticBase<RooAbsPdf>* pdfPID2 = NULL;
    if ( (type.Contains("Bs2DsPi") == true && type.Contains("MC") == true) || type.Contains("DPi") == true 
	 || type.Contains("CombPi") == true || (type.Contains("Bs2DsstPi") == true && type.Contains("MC") == true) )
      {

	if ( type.Contains("Pion") )
	  {
	    histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(100, PID_down, PID_up)); //45,log(0.0001),log(-PID_down)));
	    histBin = 100;
	  }
	else
	  {
	    histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(50, PID_down, PID_up));   
            histBin = 50;
	  }
      }
    else
      {
	histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(50,PID_down,PID_up));
	histBin = 50;
      }
    Double_t zero = 1e-20;
    for(int k = 1; k<histBin; k++)
      {
	Double_t cont = histPID->GetBinContent(k);
	if( cont < zero ) 
	  { 
	    histPID->SetBinContent(k,zero);
	    std::cout<<"[WARNING] Histogram value lower than zero: "<<cont<<". Force Bin content to be: "<<zero<<std::endl; 
	  }
      }


    pdfPID = NULL;
    if (year !="" ) { year = "_"+year;}
    

    if( (type.Contains("MC") == true  && type.Contains("Bs2DsPi") == true ) || type.Contains("DPi") == true 
	|| type.Contains("CombPi") == true || (type.Contains("Bs2DsstPi") == true && type.Contains("MC") == true))
      {
	if ( debug == true )
	  {
	    PlotWeightingSample(nn, dataC, dataRW, Var1, Var2, lab1_PIDK, bin1, bin2, bin3,
				type, l2, l3, work, plotSet, debug);
	  }
	
	
	if ( type.Contains("Pion") == true)
	  {
	    
	    if( type.Contains("CombPi") == true ) { nn = "CombPi_"+nm; }
	    if (type.Contains("Bs2DsPi") == true && type.Contains("MC") == true) { nn = "Bs2DsPi_"+sample+"_"+mode+year; }
	    if (type.Contains("Bs2DsstPi") == true && type.Contains("MC") == true) { nn = "Bs2DsstPi_"+sample+"_"+mode+year; }
	    //nn = nn+year;
	    TString namepdf = "PIDKShape_"+nn;
            pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
            RooAbsPdf* pdfSave = pdfPID2;
            TString t = "";
	    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nn, t, plotSet, debug );
            work->import(*pdfPID2);

	  }
	else  if ( type.Contains("Kaon") == true)
	  {
	    if( type.Contains("CombPi") == true ) { nn = "CombK_"+nm; }
	    TString namepdf = "PIDKShape_"+nn;
	    pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
	    RooAbsPdf* pdfSave = pdfPID2;
	    TString t = "";
	    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nn, t, plotSet, debug );
	    work->import(*pdfPID2);
	    
	  }
	else
          {
            TString strip = CheckStripping(type,debug);
            if ( strip == "str17" )
              {
                if( type.Contains("CombPi") == true ) { nn = "CombP_"+nm;}                                                          
                pdfPID = FitPDFShapeForPIDBsDsKP(dataRW, lab1_PIDK, nn,  plotSet, debug);
                work->import(*pdfPID);
              }
            else
              {
                if( type.Contains("CombPi") == true ) { nn = "CombP_"+nm;} 
                TString namepdf = "PIDKShape_"+nn;
                pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
                RooAbsPdf* pdfSave = pdfPID2;
                TString t = "";
                SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nn, t, plotSet, debug );
                work->import(*pdfPID2);
              }
          }
      }
    else if ( (type.Contains("MC") == true && type.Contains("Bs2DsK") == true ) ||
	      (type.Contains("MC") == true && type.Contains("Bs2DsstK") == true ) ||
	      (type.Contains("MC") != true && type.Contains("Bs2DsPi") == true) ||
	      type.Contains("CombK") == true)
      {
	TString dir = "PlotBsDsK2D";
        if (debug == true) PlotWeightingSample(nn, dataC, dataRW, Var1, Var2, lab1_PIDK, bin1, bin2, bin3,
					       type, l2, l3, work, plotSet, debug);

	if ( type.Contains("Pion") == true)
	  {
	    
	    if( type.Contains("CombK") == true ) { nn = "CombPi_"+nm; } 
	    if (type.Contains("Bs2DsPi") == true && type.Contains("MC") != true) { nn = "Bs2DsPi_"+sample+"_"+mode+year; }
	    if (type.Contains("Bs2DsstPi") == true && type.Contains("MC") != true) { nn = "Bs2DsstPi_"+sample+"_"+mode+year; }

	    TString namepdf = "PIDKShape_"+nn;
	    TString strip = CheckStripping(type,debug);
	    if ( strip == "str17" )
	      {
		pdfPID = FitPDFShapeForPIDBsDsKPi(dataRW, lab1_PIDK, nn,  plotSet,  debug);
		work->import(*pdfPID);
	      }
	    else
	      {
		pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
		RooAbsPdf* pdfSave = pdfPID2;
		TString t = "";
		SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nn, t, plotSet, debug );
		work->import(*pdfPID2);
	      }
	  }
	else if ( type.Contains("Kaon") == true)
	  {
	    if( type.Contains("CombK") == true ) { nn = "CombK_"+nm; } //nn = nn+year;}
	    if (type.Contains("Bs2DsK") == true && type.Contains("MC") == true) { nn = "Bs2DsK_"+sample+"_"+mode+year; }
	    if (type.Contains("Bs2DsstK") == true && type.Contains("MC") == true) { nn = "Bs2DsstK_"+sample+"_"+mode+year; }
    	    TString namepdf = "PIDKShape_"+nn;
	    pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
	    RooAbsPdf* pdfSave = pdfPID2;
	    TString t = "";
	    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nn, t, plotSet, debug );
	    work->import(*pdfPID2);
	  }
	else
	  {
	    TString strip = CheckStripping(type,debug);
	    if ( strip == "str17" )
              {
		if( type.Contains("CombK") == true ) { nn = "CombP_"+nm;} // nn = nn+year; }
		pdfPID = FitPDFShapeForPIDBsDsKP(dataRW, lab1_PIDK, nn,  plotSet, debug);
		work->import(*pdfPID);
	      }
	    else
	      {
		if( type.Contains("CombK") == true ) { nn = "CombP_"+nm;} // nn = nn+year;}
		TString namepdf = "PIDKShape_"+nn;
		pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
		RooAbsPdf* pdfSave = pdfPID2;
		TString t = "";
		SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nn, t, plotSet, debug );
		work->import(*pdfPID2);
	      }
	  }
	//	delete pdfPID2;
	//delete dataRW;
	//delete histPID;

      }
    delete Var1;
    delete Var2;
    delete lab1_PIDK;
    delete dataC;
    //delete CalibWeight;
    //delete CalibVar1;
    //delete CalibVar2;
    //delete CalibPIDK;
    //delete histCalib;

  return work;
}
  
  TH1* GetHist(RooDataSet* data, RooRealVar* obs, Int_t bin, bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] WeightingUtils.GetHist() "<<std::endl; } 

    TH1* hist = NULL;
    TString dataName = data->GetName();
    TString nameHist = "hist_"+dataName;
    
    hist = data->createHistogram(nameHist.Data(), *obs, RooFit::Binning(bin));
    hist->SetName(nameHist); 

    for (int i = 1; i< bin+1; i++)
      {
	Double_t c1 = hist->GetBinContent(i);
	if (c1 < 1e-37)
          {
            hist->SetBinContent(i, 1e-37);
          }
      }

    return hist;
  }

  TH1* GetHistRatio(RooDataSet* data1, RooDataSet* data2, RooRealVar* obs, TString histName, Int_t bin, bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] WeightingUtils.GetHistRatio() "<<std::endl; }

    TH1* hist1 = NULL;
    TH1* hist2 = NULL;
    TString nameHist1 = "hist1";
    TString nameHist2 = "hist2";

    hist1 = data1->createHistogram(nameHist1.Data(), *obs, RooFit::Binning(bin));
    hist1->SetName(nameHist1.Data());
    hist1->SaveAs("hist1.root");
    hist2 = data2->createHistogram(nameHist2.Data(), *obs, RooFit::Binning(bin));
    hist2->SetName(nameHist2.Data());
    hist2->SaveAs("hist2.root");

    for (int i = 1; i< bin+1; i++)
      {
        Double_t c1 = hist1->GetBinContent(i);
	if (c1 < 1e-37)
          {
            hist1->SetBinContent(i, 1e-37);
          }
	Double_t c2 = hist2->GetBinContent(i);
        if (c2 < 1e-37)
          {
            hist2->SetBinContent(i, 1e-37);
          }
      }
    TH1* hist = new TH1F(histName.Data(), histName.Data(), bin, obs->getMin(), obs->getMax());
    Double_t scaleA = data2->sumEntries()/data1->sumEntries();
    
    for (int i = 1; i<bin; i++)
      {
	Float_t binH1 = hist1->GetBinContent(i);
	Float_t binH2 = hist2->GetBinContent(i);
	Float_t errH1 = hist1->GetBinError(i);
	Float_t errH2 = hist2->GetBinError(i);
	
	Float_t binRatio = 0;
	Float_t errRatio = 0; 

	if ( binH1 <= 0 || binH2 <= 0 ) { binRatio = 0; errRatio=0; }
	else {
	  binRatio = binH1/binH2*scaleA;
	  errRatio = binRatio*sqrt((errH1*errH1)/(binH1*binH1)+(errH2+errH2)/(binH2*binH2));
	}
	std::cout<<"i: "<<i<<" binH1: "<<binH1<<" binH2: "<<binH2<<" bin: "<<binRatio<<std::endl;
	hist->SetBinContent(i,binRatio);
	hist->SetBinError(i,errRatio);
      }
    
    return hist;
  }

  
  
  TH1* GetHistRatio(TH1* hist1, TH1* hist2, RooRealVar* obs, TString histName,bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] WeightingUtils.GetHistRatio() "<<std::endl; }
    
    Int_t bin1 = hist1->GetNbinsX();
    Int_t bin2 = hist2->GetNbinsX();
    Int_t bin;
    
    if( bin1 == bin2 ) { bin = bin1; }
    else{ std::cout<<"[ERROR] Not the same number of bins: "<<bin1<<" != "<<bin2<<std::endl; return NULL; }

    TH1* hist = new TH1F(histName.Data(), histName.Data(), bin, obs->getMin(), obs->getMax());
    Double_t scaleA = hist2->GetSumOfWeights()/hist1->GetSumOfWeights() ;

    for (int i = 1; i<bin; i++)
      {
        Float_t binH1 = hist1->GetBinContent(i);
	Float_t binH2 = hist2->GetBinContent(i);
        Float_t errH1 = hist1->GetBinError(i);
        Float_t errH2 = hist2->GetBinError(i);

        Float_t binRatio = 0;
        Float_t errRatio = 0;

        if ( binH1 <= 0 || binH2 <= 0 ) { binRatio = 0; errRatio=0; }
        else {
          binRatio = binH1/binH2*scaleA;
          errRatio = binRatio*sqrt((errH1*errH1)/(binH1*binH1)+(errH2+errH2)/(binH2*binH2));
        }
	std::cout<<"i: "<<i<<" binH1: "<<binH1<<" binH2: "<<binH2<<" bin: "<<binRatio<<std::endl;

        hist->SetBinContent(i,binRatio);
        hist->SetBinError(i,errRatio);
      }

    return hist;
  }

  TH1* MultiplyHist(TH1* hist1, TH1* hist2, RooRealVar* obs, TString histName,bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] WeightingUtils.MultiplyHist() "<<std::endl; }

    Int_t bin1 = hist1->GetNbinsX();
    Int_t bin2 = hist2->GetNbinsX();
    Int_t bin;

    if( bin1 == bin2 ) { bin = bin1; }
    else{ std::cout<<"[ERROR] Not the same number of bins: "<<bin1<<" != "<<bin2<<std::endl; return NULL; }

    TH1* hist = new TH1F(histName.Data(), histName.Data(), bin, obs->getMin(), obs->getMax());
    Double_t scaleA = hist2->GetSumOfWeights()/hist1->GetSumOfWeights() ;

    for (int i = 1; i<bin; i++)
      {
	Float_t binH1 = hist1->GetBinContent(i);
        Float_t binH2 = hist2->GetBinContent(i);
        Float_t errH1 = hist1->GetBinError(i);
	Float_t errH2 = hist2->GetBinError(i);

	Float_t binRatio = 0;
        Float_t errRatio = 0;
	
	binRatio = binH1*binH2*scaleA; 
	errRatio = binRatio*sqrt((errH1*errH1)/(binH1*binH1)+(errH2+errH2)/(binH2*binH2));
	std::cout<<"i: "<<i<<" binH1: "<<binH1<<" binH2: "<<binH2<<" bin: "<<binRatio<<std::endl;

        hist->SetBinContent(i,binRatio);
	hist->SetBinError(i,errRatio);
      }

    return hist;

  }

}
// end of namespace
