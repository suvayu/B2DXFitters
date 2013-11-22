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
#include "B2DXFitters/KinHack.h"
#include "B2DXFitters/DecayTreeTupleSucksFitter.h"
#include "B2DXFitters/RooCruijff.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"
#include "B2DXFitters/PlotSettings.h"
#include "B2DXFitters/MDFitterSettings.h"

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


  TString CheckTreeLabel(TString& fileCalib, bool debug)
  {
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::CheckTreeLabel("<<fileCalib<<")"<< std::endl;
      }

    TString Par;
    if( fileCalib.Contains("CalibDSt") == true && fileCalib.Contains("Pi") ) { Par = "Pi"; }
    else if (fileCalib.Contains("CalibDSt") == true && fileCalib.Contains("K") ) { Par = "K"; }
    else if (fileCalib.Contains("CalibLam0") == true && fileCalib.Contains("P") ) { Par = "P"; }
    else {Par = "";}
    if( debug == true) { std::cout<<"Return: "<<Par<<std::endl;}
    return Par;
  }

  

  TString CheckTreeLabel(TString& fileCalib, TString& check, bool debug)
  {
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::CheckTreeLabel("<<fileCalib<<","<<check<<")"<< std::endl;
      }

    TString Par;
    if( fileCalib.Contains("CalibDSt") == true && fileCalib.Contains("Pi") ) { Par = "Pi"; }
    else if (fileCalib.Contains("CalibDSt") == true && fileCalib.Contains("K") ) { Par = "K"; }
    else if (fileCalib.Contains("CalibLam0") == true && fileCalib.Contains("P") ) { Par = "P"; }
    else {Par = "";}
  
    TString label ="";
    if ( check == "nTracks" ) {  label = "nTracks"; }
    else if ( check == "lab1_P" ) {  label = Par+"_P"; }
    else if ( check == "lab1_PT" ) {  label = Par+"_PT"; }
  
    if( debug == true) { std::cout<<"Return: "<<label<<std::endl;}
    return label;
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

    if ( type.Contains("Comb") == true && type.Contains("Pion") == true)
      {
        if ( type.Contains("Down") == true || type.Contains("down") == true) { nm = "down"; } else {  nm = "up"; }
        name="dataCombBkg_"+nm;
        histName = "hist2D_Comb_"+nm;
        histNameR = "hist2D_Comb_ratio_"+nm;
	nameCalib = "CalibSample_CombPi_"+nm; 
      }
    else if ( type.Contains("Comb") == true && type.Contains("Kaon") == true)
      {
        if ( type.Contains("Down") == true || type.Contains("down") == true) { nm = "down"; } else {  nm = "up"; }
        name="dataCombBkg_"+nm;
        histName = "hist2DK_Comb_"+nm;
        histNameR = "hist2DK_Comb_ratio_"+nm;
	nameCalib = "CalibSample_CombK_"+nm;
      }
    else if ( type.Contains("Comb") == true && type.Contains("Proton") == true)
      {
        if ( type.Contains("Down") == true || type.Contains("down") == true) { nm = "down"; } else {  nm = "up"; }
        name="dataCombBkg_"+nm;
        histName = "hist2DP_Comb_"+nm;
        histNameR = "hist2DP_Comb_ratio_"+nm;
	nameCalib = "CalibSample_CombP_"+nm;
      }
    else if ( type.Contains("DPi") == true)
      {
        if ( type.Contains("Down") == true || type.Contains("down") == true) { nm = "down"; } else {  nm = "up"; }
        name = "dataSet_Miss_"+nm+"_kpipi";
        histName = "hist2D_Miss_"+nm;
        histNameR = "hist2D_Miss_ratio_"+nm;
	nameCalib = "CalibSample_Miss_"+nm;
      }
    else if( type.Contains("BsDsPi") == true && type.Contains("MC") == true )
      {
	sample = CheckPolarity(type,debug);
        mode = CheckDMode(type, debug);
        if ( mode == "kkpi" || mode == "") { mode = CheckKKPiMode(type, debug); }
	nm = "BsDsPi_"+sample+"_"+mode;
        name="dataSetMC_"+nm;
        histName = "hist2D_"+nm;
        histNameR = "hist2D_ratio_"+nm;
	nameCalib = "CalibSample_"+nm;
      }
    else if (type.Contains("BsDsK") == true && type.Contains("MC") == true)
      {
        sample = CheckPolarity(type,debug);
        mode = CheckDMode(type, debug);
        if ( mode == "kkpi"|| mode == "") { mode = CheckKKPiMode(type, debug); }
        nm = "BsDsK_"+sample+"_"+mode;
        name="dataSetMC_"+nm;
        histName = "hist2D_"+nm;
	histNameR = "hist2D_ratio_"+nm;
	nameCalib = "CalibSample_"+nm;

      }
    else if( type.Contains("BsDsPi") == true && type.Contains("MC") != true )
      {
	sample = CheckPolarity(type,debug);
	mode = CheckDMode(type, debug);
	if ( mode == "kkpi" || mode == "") { mode = CheckKKPiMode(type, debug); }
	nm = sample+"_"+mode;
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
	if( label1.Contains("BsDsK") == true) {legendBool = kFALSE;} else {legendBool = kTRUE;}
      }
    else if ( label1.Contains("Comb") == true ) 
      { 
	if( label1.Contains("Down") == true) { name="dataCombBkg_down";} else { name = "dataCombBkg_up";}
	if ( label1.Contains("CombPi") == true ) { legendBool = kTRUE; } else {legendBool = kFALSE; }
      }
    else if ( label1.Contains("BsDsPi") == true && label1.Contains("MC") != true)
      {
	TString sample = CheckPolarity(label1,debug);
        TString mode = CheckDMode(label1, debug);
	if ( mode == "kkpi") { mode = CheckKKPiMode(label1, debug); }
	TString mm = sample+"_"+mode;
        name="dataSet_Miss_"+mm;
	legendBool = kFALSE;
      }  
    else {
      legendBool =kTRUE;
      if( label1.Contains("Down") == true) { name="dataSet_Miss_down_kpipi";} else { name = "dataSet_Miss_up_kpipi";}
    }

    RooDataSet*  dataMC = GetDataSet(work,name,debug);
    RooDataSet*  dataMCNW = GetDataSet(work,name,debug);
    if ( label1.Contains("MC") == true )
      { dataMC = new RooDataSet(dataMC->GetName(), dataMC->GetTitle(), *(dataMC->get()), RooFit::Import(*dataMC), RooFit::WeightVar("weights"));}


    double scaleA = dataCalib->sumEntries()/dataMC->sumEntries();
    double scaleB = dataCalib->sumEntries()/dataCalibRW->sumEntries();
    double scaleC = dataCalib->sumEntries()/dataMCNW->sumEntries();
  

    std::cout<<" scaleA: "<<scaleA<<" = "<<dataMC->sumEntries()<<"/"<<dataCalib->sumEntries()<<std::endl;
    std::cout<<" scaleA: "<<scaleB<<" = "<<dataCalibRW->sumEntries()<<"/"<<dataCalib->sumEntries()<<std::endl;
    std::cout<<" scaleC: "<<scaleC<<" = "<<dataMC->sumEntries()<<"/"<<dataMCNW->sumEntries()<<std::endl;

    TLegend* legend = new TLegend( 0.12, 0.66, 0.30, 0.88 );
    legend->SetTextSize(0.045);
    legend->SetTextFont(12);
    legend->SetFillColor(4000);
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
    legend2->SetFillColor(4000);
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
    dataCalibRW->plotOn(mframe_PID,RooFit::MarkerColor(plotSet->GetColorData(0)), RooFit::Binning(bin3));
    if ( label1.Contains("Comb") != true )
      {
	dataMC->plotOn(mframe_PID,RooFit::MarkerColor(plotSet->GetColorData(2)), RooFit::Binning(bin3), RooFit::Rescale(scaleA));
      }
    //mframe_Var2->GetXaxis()->SetTitle(l2.Data());
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
    
  }
  
  void PlotWeightingSample(TString& nm, RooDataSet* dataCalib, RooDataSet* dataCalibRW,
                           RooRealVar* Var1, RooRealVar* Var2, RooRealVar* Var3, RooRealVar* PID,
                           Int_t bin1, Int_t bin2, Int_t bin3, Int_t binPID,
                           TString& label1, TString& label2, TString& label3, 
			   RooWorkspace* work, 
			   PlotSettings* plotSet,
			   bool debug )

  {
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::PlotWeightingSample("
		  <<Var1->GetName()<<","<<Var2->GetName()<<","<<Var3->GetName()
		  <<","<<bin1<<","<<bin2<<","<<bin3<<")"<<std::endl;
      }
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }
    TString dir= plotSet->GetDir();
    TString ext= plotSet->GetExt();


    TCanvas *ch_RW = new TCanvas("c2h_RW","",10,10,1200,1200);
    ch_RW->SetFillColor(0);
    ch_RW->Divide(2,2);
    
    TString name;
    if ( label1.Contains("MC") == true ) {name="dataSetMC_"+nm;}
    else if ( label1.Contains("Comb") == true )
      {
        if( label1.Contains("Down") == true) { name="dataCombBkg_down";} else { name = "dataCombBkg_up";}
      }
    else if ( label1.Contains("BsDsPi") == true && label1.Contains("MC") != true)
      {
        TString sample = CheckPolarity(label1,debug);
        TString mode = CheckDMode(label1, debug);
	if ( mode == "kkpi") { mode = CheckKKPiMode(label1, debug); }
        nm = sample+"_"+mode;
        name="dataSet_Miss_"+nm;
      }
    else {
      if( label1.Contains("Down") == true) { name="dataSet_Miss_down_kpipi";} else { name = "dataSet_Miss_up_kpipi";}
    }

    RooDataSet*  dataMC = GetDataSet(work,name,debug);
    if ( label1.Contains("MC") == true )
      { dataMC = new RooDataSet(dataMC->GetName(), dataMC->GetTitle(), *(dataMC->get()), RooFit::Import(*dataMC), RooFit::WeightVar("weights"));}


    Double_t scaleA = dataCalib->sumEntries()/dataMC->sumEntries();
    Double_t scaleB = dataCalib->sumEntries()/dataCalibRW->sumEntries();
    
    std::cout<<" scaleA: "<<scaleA<<" = "<<dataMC->sumEntries()<<"/"<<dataCalib->sumEntries()<<std::endl;
    std::cout<<" scaleA: "<<scaleB<<" = "<<dataCalibRW->sumEntries()<<"/"<<dataCalib->sumEntries()<<std::endl;
    TLegend* legend = new TLegend( 0.11, 0.66, 0.30, 0.88 );
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

    TGraphErrors* grMC = new TGraphErrors(10);
    grMC->SetName("grMC");
    grMC->SetLineColor(kBlack);
    grMC->SetLineWidth(2);
    grMC->SetMarkerStyle(20);
    grMC->SetMarkerSize(1.3);
    grMC->SetMarkerColor(plotSet->GetColorData(1));
    grMC->Draw("P");

    TGraphErrors* grMCRW = new TGraphErrors(10);
    grMCRW->SetName("grMCRW");
    grMCRW->SetLineColor(kBlack);
    grMCRW->SetLineWidth(2);
    grMCRW->SetMarkerStyle(20);
    grMCRW->SetMarkerSize(1.3);
    grMCRW->SetMarkerColor(plotSet->GetColorData(2));
    grMCRW->Draw("P");

    legend->AddEntry("gr",label3.Data(),"lep");
    legend->AddEntry("grMC",label2.Data(),"lep");
    legend->AddEntry("grMCRW",nm.Data(),"lep");

    TString l1, l2, l3;
    TString nameVar1 = Var1->GetName();
    TString nameVar2 = Var2->GetName();
    TString nameVar3 = Var3->GetName();

    l1 = CheckWeightLabel(nameVar1,debug);
    l2 = CheckWeightLabel(nameVar2,debug);
    l3 = CheckWeightLabel(nameVar3,debug);

   
    RooPlot* mframe_Var1 = (RooPlot*)Var1->frame();
    TString frameName = "frame_"+nm+Var1->GetName();
    mframe_Var1->SetName(frameName.Data());
    mframe_Var1->GetXaxis()->SetTitle(l1.Data());
    TString Title = "";
    mframe_Var1->SetTitle(Title.Data());
    mframe_Var1->SetLabelFont(132);
    mframe_Var1->SetTitleFont(132);
    dataCalib->plotOn(mframe_Var1, RooFit::MarkerColor(plotSet->GetColorData(1)), RooFit::Binning(bin1), RooFit::DataError(RooAbsData::SumW2)); 
    //dataMC->plotOn(mframe_Var1, RooFit::MarkerColor(kRed), RooFit::Binning(bin1), RooFit::Rescale(scaleA), RooFit::DataError(RooAbsData::SumW2));
    if ( label1.Contains("Comb") != true )
      {
	dataMC->plotOn(mframe_Var1, RooFit::MarkerColor(plotSet->GetColorData(2)), RooFit::Binning(bin1), 
		       RooFit::Rescale(scaleA), RooFit::DataError(RooAbsData::SumW2));
      }
    else
      {
	dataMC->plotOn(mframe_Var1, RooFit::MarkerColor(plotSet->GetColorData(2)), RooFit::Binning(bin1), RooFit::Rescale(scaleA));
      }
    dataCalibRW->plotOn(mframe_Var1, RooFit::MarkerColor(plotSet->GetColorData(0)),  RooFit::Binning(bin1), 
			RooFit::Rescale(scaleB), RooFit::DataError(RooAbsData::SumW2));
    
    RooPlot* mframe_Var2 = (RooPlot*)Var2->frame();
    dataCalib->plotOn(mframe_Var2,RooFit::MarkerColor(plotSet->GetColorData(1)), RooFit::Binning(bin2),RooFit::DataError(RooAbsData::SumW2));
    if ( label1.Contains("Comb") != true )
      {
	dataMC->plotOn(mframe_Var2,RooFit::MarkerColor(plotSet->GetColorData(2)), RooFit::Binning(bin2), 
		       RooFit::Rescale(scaleA), RooFit::DataError(RooAbsData::SumW2));
      }
    else
      {
	dataMC->plotOn(mframe_Var2,RooFit::MarkerColor(plotSet->GetColorData(2)), RooFit::Binning(bin2), RooFit::Rescale(scaleA));
      }
    dataCalibRW->plotOn(mframe_Var2,RooFit::MarkerColor(plotSet->GetColorData(0)), RooFit::Binning(bin2), 
			RooFit::Rescale(scaleB), RooFit::DataError(RooAbsData::SumW2));
    mframe_Var2->GetXaxis()->SetTitle(l2.Data());
    mframe_Var2->SetTitle(Title.Data());
    mframe_Var2->SetLabelFont(132);
    mframe_Var2->SetTitleFont(132);

    RooPlot* mframe_Var3 = (RooPlot*)Var3->frame();
    dataCalib->plotOn(mframe_Var3,RooFit::MarkerColor(plotSet->GetColorData(1)), RooFit::Binning(bin3), RooFit::DataError(RooAbsData::SumW2)); 
    //dataMC->plotOn(mframe_Var3,RooFit::MarkerColor(kRed), RooFit::Binning(bin3), RooFit::Rescale(scaleA), RooFit::DataError(RooAbsData::SumW2));
    
    if ( label1.Contains("Comb") != true )
      {
	dataMC->plotOn(mframe_Var3,RooFit::MarkerColor(plotSet->GetColorData(2)), RooFit::Binning(bin3), 
		       RooFit::Rescale(scaleA), RooFit::DataError(RooAbsData::SumW2));
      }
    else
      {
        dataMC->plotOn(mframe_Var3,RooFit::MarkerColor(plotSet->GetColorData(2)), 
		       RooFit::Binning(bin3), RooFit::Rescale(scaleA));
      }
    dataCalibRW->plotOn(mframe_Var3,RooFit::MarkerColor(plotSet->GetColorData(0)), RooFit::Binning(bin3), 
			RooFit::Rescale(scaleB), RooFit::DataError(RooAbsData::SumW2));
    
    mframe_Var3->GetXaxis()->SetTitle(l3.Data());
    mframe_Var3->SetTitle(Title.Data());
    mframe_Var3->SetLabelFont(132);
    mframe_Var3->SetTitleFont(132);

    std::cout<<"Plot PID variable"<<std::endl;
    RooPlot* mframe_PID = PID->frame();
    //dataMC->plotOn(mframe_PID,RooFit::MarkerColor(kRed), RooFit::Binning(binPID), RooFit::DataError(RooAbsData::SumW2));
    //dataCalib->plotOn(mframe_PID,RooFit::MarkerColor(kOrange), RooFit::Binning(binPID), RooFit::DataError(RooAbsData::SumW2));
    //dataCalibRW->plotOn(mframe_PID,RooFit::MarkerColor(kBlue), RooFit::Binning(binPID), RooFit::DataError(RooAbsData::SumW2));
    if ( label1.Contains("Comb") != true )
      {
	dataCalibRW->plotOn(mframe_PID,RooFit::MarkerColor(plotSet->GetColorData(0)), RooFit::Binning(binPID), RooFit::DataError(RooAbsData::SumW2));
        dataMC->plotOn(mframe_PID,RooFit::MarkerColor(plotSet->GetColorData(2)), RooFit::Binning(binPID), 
		       RooFit::Rescale(scaleA), RooFit::DataError(RooAbsData::SumW2));
      }
    else
      {
	dataCalibRW->plotOn(mframe_PID,RooFit::MarkerColor(plotSet->GetColorData(0)), RooFit::Binning(binPID));
      }
    //mframe_Var2->GetXaxis()->SetTitle(l2.Data());
    mframe_PID->SetTitle(Title.Data());
    mframe_PID->SetLabelFont(132);
    mframe_PID->SetTitleFont(132);

    TString save1 = dataCalibRW->GetName();
    TString save = dir+"/"+save1+"."+ext;
    //TCanvas *ch_RW = new TCanvas("c2h_RW","",10,10,1200,1200);
    //ch_RW->SetFillColor(0);
    //ch_RW->Divide(2,2);
    ch_RW->cd(1);
    mframe_Var1->Draw();
    legend->Draw("same");
    ch_RW->cd(2);
    mframe_Var2->Draw();
    legend->Draw("same");
    ch_RW->cd(3);
    mframe_Var3->Draw();
    legend->Draw("same");
    ch_RW->cd(4);
    mframe_PID->Draw();
    //legend->Draw("same");
    ch_RW->Update();
    ch_RW->SaveAs(save.Data());
  }


  RooDataSet* GetDataCalibSample(TString& fileName, TString& workName, 
				 RooRealVar* Var1, RooRealVar* Var2,
				 PlotSettings* plotSet,
				 bool debug )
  {
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::Get2DHistCalibSample(...)."
                  << std::endl;
      }
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    RooDataSet* dataRW;
    //TH2F* hist=NULL;
    TString dataName; 
    if ( fileName.Contains("Calib") == true)
      {
	dataName = "data";
      }
    else
      {
	TString s = CheckPolarity(fileName,debug);
	dataName = "ProtonsSample_"+s;
      }
    RooWorkspace* workC = LoadWorkspace(fileName, workName, debug);
    RooDataSet* dataC = GetDataSet(workC, dataName, debug );
    const TTree* treeConst = dataC->tree();
    TTree* treeC = new TTree("name","name"); 
    treeC = treeConst->GetTree();
    Double_t nsig_sw3,Var13, Var23;

    TString nameVar1 = Var1->GetName();
    TString nameVar2 = Var2->GetName();
    TString label1, label2, swlabel;
    TString nVar1, nVar2;
    if ( nameVar1 != nameVar2 )
      {
	label1 = CheckWeightLabel(nameVar1,debug);
	label2 = CheckWeightLabel(nameVar2,debug);
	if(fileName.Contains("Calib") == true)
	  {
	    swlabel = "nsig_sw";
	    nVar1 = CheckTreeLabel(fileName, nameVar1, debug);
	    nVar2 = CheckTreeLabel(fileName, nameVar2, debug);
	  }
	else
	  {
	    swlabel = "sWeights";
	    nVar1 = nameVar1;
	    nVar2 = nameVar2;
	  }
      }
    else { if(debug == true) std::cout<<"The same name of variables: "<<nameVar1<<"  "<<nameVar2<<std::endl; }

    treeC->SetBranchAddress(swlabel.Data(), &nsig_sw3);
    treeC->SetBranchAddress(nVar1.Data(), &Var13);
    treeC->SetBranchAddress(nVar2.Data(), &Var23);

    TString namew = "weights";
    RooRealVar* weights;
    weights = new RooRealVar(namew.Data(), namew.Data(), -50.0, 50.0 );
    TString nameCalib = "CalibSample";
    
    dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*Var1,*Var2,*weights), namew.Data());

    
    for (Long64_t jentry=0; jentry<treeC->GetEntries(); jentry++)
      {

	treeC->GetEntry(jentry);
	Var1->setVal(Var13);
	Var2->setVal(Var23);
	//std::cout<<" weight: "<<wA<<" nsigSW: "<<nsig_sw3<<" wRW "<<wRW<<" "<<nameVar1<<": "<<Var13<<" "<<nameVar2<<": "<<Var23<<std::endl;
	weights->setVal(nsig_sw3);
	dataRW->add(RooArgSet(*Var1,*Var2,*weights),nsig_sw3,0);
      }
    if ( dataRW != NULL  ){
      std::cout<<"[INFO] ==> Create "<<dataRW->GetName()<<std::endl;
      std::cout<<" number of entries in data set: "<<dataRW->numEntries()<<std::endl;
    } else { std::cout<<"Error in create dataset"<<std::endl; }
    
    TString smp = "Calib";
    TString mode = "sample";
    if( plotSet->GetStatus() ==true )
      {
        SaveDataSet(dataRW, Var1 , smp, mode, plotSet, debug);
        SaveDataSet(dataRW, Var2 , smp, mode, plotSet, debug);
      }


    return dataRW;
    
  }

  RooDataSet* GetDataCalibSample(TString& fileName, TString& workName,
                                 RooRealVar* Var1, RooRealVar* Var2, RooRealVar* Var3,
				 PlotSettings* plotSet,
                                 bool debug )
  {
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::Get2DHistCalibSample(...)."
                  << std::endl;
      }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    RooDataSet* dataRW;
    //TH2F* hist=NULL;
    TString dataName = "data";
    RooWorkspace* workC = LoadWorkspace(fileName, workName, debug);
    RooDataSet* dataC = GetDataSet(workC, dataName, debug );
    const TTree* treeConst = dataC->tree();
    TTree* treeC = new TTree("name","name");
    treeC = treeConst->GetTree();
    Double_t nsig_sw3,Var13, Var23, Var33;

    TString nameVar1 = Var1->GetName();
    TString nameVar2 = Var2->GetName();
    TString nameVar3 = Var3->GetName();

    TString label1, label2, label3;
    if ( nameVar1 != nameVar2 && nameVar1 != nameVar3 && nameVar2 != nameVar3)
      {
        label1 = CheckWeightLabel(nameVar1,debug);
        label2 = CheckWeightLabel(nameVar2,debug);
	label3 = CheckWeightLabel(nameVar3,debug);
      }
    else { if(debug == true) std::cout<<"The same name of variables: "<<nameVar1<<"  "<<nameVar2<<" "<<nameVar3<<std::endl; }

    treeC->SetBranchAddress("nsig_sw", &nsig_sw3);
    TString nVar1 = CheckTreeLabel(fileName, nameVar1, debug);
    treeC->SetBranchAddress(nVar1.Data(), &Var13);
    TString nVar2 = CheckTreeLabel(fileName, nameVar2, debug);
    treeC->SetBranchAddress(nVar2.Data(), &Var23);
    TString nVar3 = CheckTreeLabel(fileName, nameVar3, debug);
    treeC->SetBranchAddress(nVar3.Data(), &Var33);

    TString namew = "weights";
    RooRealVar* weights;
    weights = new RooRealVar(namew.Data(), namew.Data(), -50.0, 50.0 );
    TString nameCalib = "CalibSample";

    dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*Var1,*Var2,*Var3, *weights), namew.Data());


    for (Long64_t jentry=0; jentry<treeC->GetEntries(); jentry++)
      {

        treeC->GetEntry(jentry);
        Var1->setVal(Var13);
        Var2->setVal(Var23);
	Var3->setVal(Var33);
        //std::cout<<"nsigSW: "<<nsig_sw3<<" "<<nameVar1<<": "<<Var13<<" "<<nameVar2<<": "<<Var23<<nameVar3<<": "<<Var33<<std::endl;
        weights->setVal(nsig_sw3);
        dataRW->add(RooArgSet(*Var1,*Var2,*Var3,*weights),nsig_sw3,0);
      }
    if ( dataRW != NULL  ){
      std::cout<<"[INFO] ==> Create "<<dataRW->GetName()<<std::endl;
      std::cout<<" number of entries in data set: "<<dataRW->numEntries()<<" with the sum: "<<dataRW->sumEntries()<<std::endl;
    } else { std::cout<<"Error in create dataset"<<std::endl; }

    TString smp = "Calib";
    TString mode = "sample";
    if( plotSet->GetStatus() == true )
      {
	SaveDataSet(dataRW, Var1 , smp, mode, plotSet, debug);
	SaveDataSet(dataRW, Var2 , smp, mode, plotSet, debug);
	SaveDataSet(dataRW, Var3 , smp, mode, plotSet, debug);
      }

    return dataRW;

  }


  RooAbsPdf* FitPDFShapeForPIDBsDsPiPi(RooDataSet* data, RooRealVar* Var, TString& samplemode, PlotSettings* plotSet, bool debug)
  {

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    RooAbsPdf* pdfPID = NULL;
    
    RooRealVar* c2 = NULL;
    RooRealVar* c1 = NULL;
    RooRealVar* mean = NULL;
    RooRealVar* sigma = NULL; 
    RooRealVar* f1 = NULL;
    RooRealVar* f2 = NULL;
    
    Double_t c1Var  = 6.3627*pow(10,-2);
    Double_t c2Var  = 0.59618;
    Double_t meanVar  =  -26.002;
    Double_t sigmaVar = 22.430;
    Double_t f1Var = 0.55927;
    Double_t f2Var = 0.17911;

    
    TString nameVar = "c1_"+samplemode;
    c1 =  new RooRealVar(nameVar.Data(),"coefficient #2", c1Var, c1Var-0.5*c1Var,c1Var+0.5*c1Var);
    nameVar = "c2_"+samplemode; //"_"+type;
    c2 = new RooRealVar(nameVar.Data(),"coefficient #2", c2Var, c2Var-0.5*c2Var,c2Var+0.5*c2Var);
    nameVar = "mean_"+samplemode; //"_"+type;
    mean = new RooRealVar(nameVar.Data(), "mean", meanVar, meanVar+0.5*meanVar, meanVar-1.0*meanVar);
    nameVar = "sigma_"+samplemode; //+"_"+type;
    sigma = new RooRealVar(nameVar.Data(),"sigma",sigmaVar, sigmaVar-0.5*sigmaVar,sigmaVar+0.5*sigmaVar);
    nameVar = "f1_"+samplemode; //+"_"+type;
    f1 = new RooRealVar(nameVar.Data(),"signal fraction",f1Var, 0.0, 1.0);
    nameVar = "f2_"+samplemode; //+"_"+type;
    f2  = new RooRealVar(nameVar.Data(),"signal fraction",f2Var, 0.0, 1.0 );


    nameVar = "PIDKbkg1_"+samplemode; //"_"+type;
    RooExponential* bkg1 = new  RooExponential(nameVar.Data(), "bkg p.d.f." , *Var, *c1);
    nameVar = "PIDKbkg2_"+samplemode; //+"_"+type;
    RooExponential* bkg2 = new  RooExponential(nameVar.Data(), "bkg p.d.f." , *Var, *c2);
    nameVar = "PIDKbkg3_"+samplemode; //+"_"+type;
    RooGaussian* bkg3 = new RooGaussian(nameVar.Data(),"signal p.d.f.",*Var, *mean, *sigma);
    nameVar = "ShapePIDK_"+samplemode; //+"_"+type;
    pdfPID = new RooAddPdf(nameVar.Data(),"model",RooArgList(*bkg1,*bkg2, *bkg3),RooArgList(*f1,*f2),true);

    if ( data->numEntries() > 20 )
      {
	pdfPID->fitTo(*data,RooFit::Strategy(2),RooFit::SumW2Error(kTRUE));
      }
    c1->setConstant();
    c2->setConstant();
    mean->setConstant();
    sigma->setConstant();
    f1->setConstant();
    f2->setConstant();

    if( plotSet->GetStatus() == true )
      {
	TLegend* legend = new TLegend( 0.11, 0.66, 0.30, 0.88 );
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
	frame->GetXaxis()->SetTitle("PIDK [1]");
	frame->GetYaxis()->SetTitleFont(132);
	frame->GetYaxis()->SetLabelFont(132);
	data->plotOn(frame,RooFit::MarkerColor(plotSet->GetColorData(0)));
	pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(0)), RooFit::LineStyle(plotSet->GetStylePdf(0)));

	
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

  RooAbsPdf* FitPDFShapeForPIDBsDsPiK(RooDataSet* data, RooRealVar* Var, TString& samplemode, PlotSettings* plotSet, bool debug)
  {
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }
    
    RooAbsPdf* pdfPID = NULL;

    RooRealVar* c2 = NULL;
    RooRealVar* c1 = NULL;
    RooRealVar* f1 = NULL;
    
    Double_t c1Var  = -7.68778*pow(10,-2);
    Double_t c2Var  = -4.92792*pow(10,-2);
    Double_t f1Var = 5.83968*pow(10,-1);
    
    TString nameVar = "cK1_"+samplemode;
    c1 =  new RooRealVar(nameVar.Data(),"coefficient #2", c1Var, c1Var+5.0*c1Var,c1Var-1.0*c1Var);
    nameVar = "cK2_"+samplemode; //"_"+type;
    c2 = new RooRealVar(nameVar.Data(),"coefficient #2", c2Var, c2Var+5.0*c2Var,c2Var-1.0*c2Var);
    nameVar = "fK1_"+samplemode; //+"_"+type;
    f1 = new RooRealVar(nameVar.Data(),"signal fraction",f1Var, 0.0, 1.0);
    
    nameVar = "PIDKKbkg1_"+samplemode; //"_"+type;
    RooExponential* bkg1 = new  RooExponential(nameVar.Data(), "bkg p.d.f." , *Var, *c1);
    nameVar = "PIDKKbkg2_"+samplemode; //+"_"+type;
    RooExponential* bkg2 = new  RooExponential(nameVar.Data(), "bkg p.d.f." , *Var, *c2);
    nameVar = "PIDKShape_"+samplemode; //+"_"+type;
    pdfPID = new RooAddPdf(nameVar.Data(),"model",RooArgList(*bkg1,*bkg2),RooArgList(*f1));

    if ( data->numEntries() > 20 )
      {
        pdfPID->fitTo(*data,RooFit::Strategy(2),RooFit::SumW2Error(kTRUE));
      }
    c1->setConstant();
    c2->setConstant();
    f1->setConstant();
    
    if( plotSet->GetStatus() == true )
      {

	TLegend* legend = new TLegend( 0.11, 0.66, 0.30, 0.88 );
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
	frame->GetXaxis()->SetTitle("PIDK [1]");
	frame->GetYaxis()->SetTitleFont(132);
	frame->GetYaxis()->SetLabelFont(132);
	data->plotOn(frame,RooFit::MarkerColor(plotSet->GetColorData(0)));
	pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(0)), RooFit::LineStyle(plotSet->GetStylePdf(0)) );
	nameVar = "PIDKKbkg1_"+samplemode;
	pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(1)), RooFit::LineStyle(plotSet->GetStylePdf(1)), RooFit::Components(nameVar.Data()));
        nameVar = "PIDKKbkg2_"+samplemode;
        pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(2)),  RooFit::LineStyle(plotSet->GetStylePdf(2)),RooFit::Components(nameVar.Data()));
	nameVar = "PIDKKbkg3_"+samplemode;
        pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(3)),  RooFit::LineStyle(plotSet->GetStylePdf(3)),RooFit::Components(nameVar.Data()));


	if( samplemode.Contains("Comb_down") == true ) { samplemode ="CombK_down";}
	else if( samplemode.Contains("Comb_up") == true) { samplemode = "CombK_up";}
	
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

  RooAbsPdf* FitPDFShapeForPIDBsDsKK(RooDataSet* data, RooRealVar* Var, TString& samplemode, PlotSettings* plotSet, bool debug)
  {
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    Double_t alpha1Var= -1.27837*10; 
    Double_t alpha2Var=  0.109525; 

    Double_t f1Var=      0.118439; 
   
    Double_t mean1Var= 3.82002; 
    Double_t mean2Var=3.26303; 
     
    Double_t n1Var=15.2535; 
    Double_t n2Var=1.62263; 
    Double_t sigma1Var=0.275319; 
    Double_t sigma2Var=0.379595; 
    

    RooRealVar *n1 = NULL;
    RooRealVar *alpha1 = NULL;
    RooRealVar *mean1 = NULL;
    RooRealVar *sigma1  = NULL;

    RooRealVar *n2 = NULL;
    RooRealVar *alpha2 = NULL;
    RooRealVar *mean2 = NULL;
    RooRealVar *sigma2  = NULL;
    
    RooRealVar *f1 = NULL;
    
    RooAbsPdf* pdfPID = NULL;
    
    TString nameVar = "mean1dCB_"+samplemode;
    mean1 =  new RooRealVar(nameVar.Data(),"mean1", mean1Var, 2.5, 4.0 ); //mean1Var-0.5*mean1Var, mean1Var+0.5*mean1Var);
    nameVar = "sigma1dCB_"+samplemode;
    sigma1 = new RooRealVar(nameVar.Data(),"sigma1", sigma1Var, 0.1, 0.8); //sigma1Var-sigma1Var*1.0, sigma1Var+sigma1Var*1.0);
    nameVar = "n1dCB_"+samplemode;
    n1 = new RooRealVar(nameVar.Data(), "n1", n1Var, n1Var-1.0*n1Var, n1Var+2.0*n1Var); //, meanVar - 10, meanVar+10);
    nameVar = "alpha1dCB_"+samplemode;
    alpha1 = new RooRealVar(nameVar.Data(), "alpha1", alpha1Var, alpha1Var+1.0*alpha1Var, alpha1Var-2.0*alpha1Var); 
    
    nameVar = "mean2dCB_"+samplemode;
    mean2 =  new RooRealVar(nameVar.Data(),"mean2", mean2Var, 2.5, 4.0); // mean2Var-0.5*mean2Var, mean2Var+0.5*mean2Var);
    nameVar = "sigma2dCB_"+samplemode;
    sigma2 = new RooRealVar(nameVar.Data(),"sigma2", sigma2Var, 0.1, 0.8); //sigma2Var-sigma2Var*1.0, sigma2Var+sigma2Var*1.0);
    nameVar = "n2dCB_"+samplemode;
    n2 = new RooRealVar(nameVar.Data(), "n2", n2Var, n2Var-1.0*n2Var, n2Var+2.0*n2Var); //, meanVar - 10, meanVar+10);
    nameVar = "alphad2CB_"+samplemode;
    alpha2 = new RooRealVar(nameVar.Data(), "alpha2", alpha2Var, alpha2Var-1.0*alpha2Var, alpha2Var+2.0*alpha2Var); 
    

    nameVar = "f1dcB_"+samplemode;
    f1 = new RooRealVar(nameVar.Data(),"signal fraction",f1Var, 0.0, 1.0);
        
    nameVar = "PIDKCB1_"+samplemode;
    RooCBShape* bkg1 = new  RooCBShape(nameVar.Data(), "bkg p.d.f." , *Var, *mean1, *sigma1, *alpha1, *n1);
    nameVar = "PIDKCB2_"+samplemode;
    RooCBShape* bkg2 = new RooCBShape(nameVar.Data(),"signal p.d.f.",*Var, *mean2, *sigma2, *alpha2, *n2);
   
    pdfPID = new RooAddPdf(nameVar.Data(),"model",RooArgList(*bkg1,*bkg2),RooArgList(*f1));

    if ( data->numEntries() != 0 )
      {
	pdfPID->fitTo(*data,RooFit::Strategy(2),RooFit::SumW2Error(kTRUE),RooFit::Verbose(kTRUE));
      }
    
    mean1->setConstant();
    sigma1->setConstant();
    mean2->setConstant();
    sigma2->setConstant();
    
    n1->setConstant();
    alpha1->setConstant();
    n2->setConstant();
    alpha2->setConstant();
    f1->setConstant();
    
    if ( plotSet->GetStatus()  == true )
      {
	TLegend* legend = new TLegend( 0.66, 0.66, 0.88, 0.88 );
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
	nameVar = "PIDKCB1_"+samplemode;
	pdfPID->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(1)), RooFit::LineStyle(plotSet->GetStylePdf(1)), RooFit::Components(nameVar.Data()));
	nameVar = "PIDKCB2_"+samplemode;
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
				TString& fileCalib, TString& workCalib,
				Int_t bin1, Int_t bin2,
				TString nameVar1, TString nameVar2,
				double Var1_down, double Var1_up,
				double Var2_down, double Var2_up,
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

    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(),nameVar1.Data(),log(Var1_down), log(Var1_up));
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(),nameVar2.Data(),log(Var2_down), log(Var2_up)); //-5,6);
    
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
    
    Int_t size=0;

    ReadOneName(filesDir,FileName,sig,debug);
    if ( type.Contains("MC") == true)
      {
	ReadMode(FileName, mode, false, debug);
	size = mode.size();
      }
    else { if( debug == true) std::cout<<"[ERROR] Wrong sample andmode"<<std::endl; }
    
    std::vector<TString> smp(size); 
    if ( type.Contains("MC") == true )
      {
	for(int i = 0; i< size; i++ )
	  {
	    smp[i] = CheckPolarity(sig, debug);
	  }
      }
    else 
      {
	if( debug == true) {std::cout<<"[ERROR] Wrong sample and mode"<<std::endl; } return NULL;
      }
    
    TString ext = "pdf";

    std::vector <TH2F*> hist2Data;
    std::vector <TH2F*> hist2Ratio;
    RooDataSet* dataCalib = NULL;
    dataCalib = GetDataCalibSample( fileCalib,  workCalib, Var1, Var2, plotSet, debug );
    TString histNameCalib = "hist2D_Calib";
    TH2F* histCalib = Get2DHist(dataCalib,Var1, Var2, bin1, bin2, histNameCalib, debug);
    Save2DHist(histCalib, plotSet);
    
    Double_t binMC, binData, binRatio;
    Double_t binMCErr, binDataErr, binRatioErr;
    
    
    TString l2 = "Calib";
    TString l3 = "Ratio";

    for( int i = 0; i<size; i++)
      {
	TString m = mode[i]; 
	if ( (type.Contains("Kaon") == true && (m.Contains("Kst") == true   || m.Contains("K") == true)) || 
	     (type.Contains("Pion") == true && (m.Contains("Pi") == true  || m.Contains("Rho") == true)) ||
	     (type.Contains("Proton") == true && (mode[i] == "Lb2Dsp" || mode[i] == "Lb2Dsstp" )))
	  {
	    TString nm, name;
	    TString histName;
	    TString histNameR;
	    if ( type.Contains("MC") == true )
	      {
		nm = mode[i]+"_"+smp[i]; 
		name="dataSetMC_"+nm;
		histName = "hist2D_"+nm;    
		histNameR = "hist2D_ratio_"+nm;
	      }
	    else
	      {
		if( debug == true) {std::cout<<"[ERROR] Wrong sample and mode"<<std::endl;} return NULL;
	      }

	    RooDataSet*  data = GetDataSet(work,name,debug);
	    if ( type.Contains("MC") == true ) 
	      { data = new RooDataSet(data->GetName(), data->GetTitle(), *(data->get()), RooFit::Import(*data), RooFit::WeightVar("weights"));}
	    
	    double scaleA = dataCalib->sumEntries()/data->sumEntries();
	    
	    hist2Data.push_back(Get2DHist(data,Var1, Var2, bin1, bin2, histName, debug));
	    
	    hist2Ratio.push_back(new TH2F(histNameR.Data(),histNameR.Data(),
					  bin1,log(Var1_down),log(Var1_up),
					  bin2,log(Var2_down),log(Var2_up)));
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
	  }
      }
  return work;

  }

  
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 3D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  RooWorkspace* ObtainHistRatio(TString& filesDir, TString& sig,
                                TString& fileCalib, TString& workCalib,
				Int_t bin1, Int_t bin2, Int_t bin3,
                                TString nameVar1, TString nameVar2, TString nameVar3,
                                double Var1_down, double Var1_up,
                                double Var2_down, double Var2_up,
				double Var3_down, double Var3_up,
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
                  << " Obtain 3D histogram MC/Calibration sample"
                  << std::endl;
      }
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(),nameVar1.Data(),log(Var1_down), log(Var1_up));
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(),nameVar2.Data(),log(Var2_down), log(Var2_up)); //-5,6);
    RooRealVar* Var3 = new RooRealVar(nameVar3.Data(),nameVar3.Data(),log(Var3_down), log(Var3_up));

    TString label1, label2, label3;
    if ( nameVar1 != nameVar2 && nameVar1 != nameVar3 && nameVar2 != nameVar3 )
      {
        label1 = CheckWeightLabel(nameVar1, debug);
        label2 = CheckWeightLabel(nameVar2, debug);
	label3 = CheckWeightLabel(nameVar3, debug);
      }
    else { if(debug == true) std::cout<<"The same name of variables: "<<nameVar1<<"  "<<nameVar2<<" "<<nameVar3<<std::endl; }

    if(debug == true) std::cout<<nameVar1<<" range: ("<<Var1_down<<","<<Var1_up<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar2<<" range: ("<<Var2_down<<","<<Var2_up<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar3<<" range: ("<<Var3_down<<","<<Var3_up<<")"<<std::endl;

    std::vector <std::string> FileName;
    std::vector <std::string> mode;

    Int_t size=0;

    ReadOneName(filesDir,FileName,sig,debug);
    if ( type.Contains("MC") == true)
      {
        ReadMode(FileName, mode, false, debug);
        size = mode.size();
      }
    else { if( debug == true) { std::cout<<"[ERROR] Wrong sample and mode"<<std::endl;} return NULL; }

    std::vector<TString> smp(size); 

    if ( type.Contains("MC") == true )
      {
        for(int i = 0; i< size; i++ )
          {
            smp[i] = CheckPolarity(sig, debug);
          }
      }
    else
      {
        if( debug == true){ std::cout<<"[ERROR] Wrong sample and mode"<<std::endl;} return NULL;
      }

    TString ext = "pdf";

    std::vector <TH3F*> hist2Data;
    std::vector <TH3F*> hist2Ratio;
    RooDataSet* dataCalib = GetDataCalibSample( fileCalib,  workCalib, Var1, Var2, Var3, plotSet, debug );
    std::cout<<"dataCalib: "<<dataCalib->sumEntries()<<" "<<dataCalib->numEntries()<<std::endl;
    Double_t sumEntriesCalib = dataCalib->sumEntries();
    TString histNameCalib = "hist2D_Calib";
    TH3F* histCalib = new TH3F(histNameCalib.Data(),histNameCalib.Data(),
			       bin1,log(Var1_down),log(Var1_up),
			       bin2,log(Var2_down),log(Var2_up),
			       bin3,log(Var3_down),log(Var3_up));
    histCalib = Get3DHist(dataCalib,Var1, Var2, Var3, histCalib, debug);
			  //bin1, bin2, bin3, histNameCalib, debug);
    Save3DHist(histCalib, plotSet);

    Double_t binMC, binData, binRatio;
    Double_t binMCErr, binDataErr, binRatioErr;


    TString l2 = "Calib";
    TString l3 = "Ratio";

    for( int i = 0; i<size; i++)
      {
        TString m = mode[i];
        if ( (type.Contains("Kaon") == true && (m.Contains("Kst") == true   || m.Contains("K") == true)) ||
             (type.Contains("Pion") == true && (m.Contains("Pi") == true  || m.Contains("Rho") == true)) ||
             (type.Contains("Proton") == true && (mode[i] == "Lb2Dsp" || mode[i] == "Lb2Dsstp" )))
          {
            TString nm, name;
            TString histName;
            TString histNameR;
            if ( type.Contains("MC") == true )
              {
                nm = mode[i]+"_"+smp[i];
                name="dataSetMC_"+nm;
                histName = "hist2D_"+nm;
		histNameR = "hist2D_ratio_"+nm;
              }
            else
              {
                if( debug == true) std::cout<<"[ERROR] Wrong sample andmode"<<std::endl;
              }

            RooDataSet*  data = GetDataSet(work,name,debug);
	    if ( type.Contains("MC") == true )
              { data = new RooDataSet(data->GetName(), data->GetTitle(), *(data->get()), RooFit::Import(*data), RooFit::WeightVar("weights"));}

	    std::cout<<"data MC"<<std::endl;
	    std::cout<<"entries: "<<data->sumEntries()<<" "<<data->numEntries()<<std::endl;
	    Double_t sumEntriesMC = data->sumEntries();
	    Double_t scaleA = sumEntriesCalib/sumEntriesMC; //dataCalib->sumEntries()/data->sumEntries();
	    std::cout<<"Scale A: "<<scaleA<<std::endl;
	    hist2Data.push_back(new TH3F(histName.Data(),histName.Data(),
					 bin1,log(Var1_down),log(Var1_up),
					 bin2,log(Var2_down),log(Var2_up),
					 bin3,log(Var3_down),log(Var3_up)));
	    
	    int sizehistData = hist2Data.size();
	    std::cout<<"Create histogram: "<<hist2Data[sizehistData-1]->GetName()<<std::endl;
	    std::cout<<"Size histogram: "<<sizehistData<<std::endl;
	    hist2Data[sizehistData-1] = Get3DHist(data,Var1, Var2, Var3, hist2Data[sizehistData-1], debug);

	    //            hist2Data.push_back(Get3DHist(data,Var1, Var2, Var3, bin1, bin2, bin3, histName, debug));

            hist2Ratio.push_back(new TH3F(histNameR.Data(),histNameR.Data(),
                                          bin1,log(Var1_down),log(Var1_up),
                                          bin2,log(Var2_down),log(Var2_up),
					  bin3,log(Var3_down),log(Var3_up)));
            int sizehist = hist2Ratio.size();
            hist2Ratio[sizehist-1]->SetStats(kFALSE);
            hist2Ratio[sizehist-1]->GetXaxis()->SetTitle(label1.Data());
            hist2Ratio[sizehist-1]->GetYaxis()->SetTitle(label2.Data());
	    hist2Ratio[sizehist-1]->GetZaxis()->SetTitle(label3.Data());
            TString TitleHist="";
            hist2Ratio[sizehist-1]->SetTitle(TitleHist.Data());

	    for(int k = 1; k<bin1; k++)
              {
                for (int j = 1; j<bin2; j++)
                  {
		    for (int l = 1; l < bin3; l++)
		      {
			binMC = histCalib->GetBinContent(k,j,l);
			binData = hist2Data[sizehist-1]->GetBinContent(k,j,l);
			binMCErr = histCalib->GetBinError(k,j,l);
			binDataErr = hist2Data[sizehist-1]->GetBinError(k,j,l);
			
			if ( binMC == 0 || binData < 0 || binData == 0 ) { binRatio = 0; binRatioErr=0; }
			else {
			  binRatio = binData/binMC*scaleA;
			  binRatioErr = binRatio*sqrt((binDataErr*binDataErr)/(binData*binData)+(binMCErr*binMCErr)/(binMC*binMC));
			}
			hist2Ratio[sizehist-1]->SetBinContent(k,j,l,binRatio);
			hist2Ratio[sizehist-1]->SetBinError(k,j,l,binRatioErr);
		      }
		  }
	      }
	    
            work->import(*hist2Ratio[sizehist-1]);
            work->import(*hist2Data[sizehist-1]);
          }
    }
  return work;

  }

  RooWorkspace* ObtainHistRatio(TString& filesDir, TString& sig,
                                MDFitterSettings* md,
                                TString& type,
                                RooWorkspace* work,
				PlotSettings* plotSet,
                                bool debug
                                )
  {
    TString fileCalib = "";
    TString workCalib = "";

    TString bach = CheckBachelor(type, debug);
    TString pol = CheckPolarity(type, debug);
   
    if ( bach == "Pi" )     
      { 
	if ( pol == "up" ) { fileCalib = md->GetCalibPionUp(); } else { fileCalib = md->GetCalibPionDown(); }  
	workCalib = md->GetCalibPionWorkName();
      }
    else if ( bach == "K" ) 
      {
        if ( pol == "up" ) { fileCalib = md->GetCalibKaonUp(); } else { fileCalib = md->GetCalibKaonDown(); }
        workCalib = md->GetCalibKaonWorkName();
      }
    else if ( bach == "P" ) 
      {
        if ( pol == "up" ) { fileCalib = md->GetCalibProtonUp(); } else { fileCalib = md->GetCalibProtonDown(); }
        workCalib = md->GetCalibProtonWorkName();
      }


    if( md->GetWeightingDim() == 2 )
      {
        work = ObtainHistRatio(filesDir, sig,
			       fileCalib, workCalib,
                               md->GetBin(0), md->GetBin(1),
                               md->GetVar(0), md->GetVar(1),
                               md->GetRangeDown(md->GetVar(0)), md->GetRangeUp(md->GetVar(0)),
			       md->GetRangeDown(md->GetVar(1)), md->GetRangeUp(md->GetVar(1)),
                               type,
                               work,
                               plotSet,
                               debug
			       );
      }
    else
      {
	work = ObtainHistRatio(filesDir, sig,
                               fileCalib, workCalib,
                               md->GetBin(0), md->GetBin(1), md->GetBin(2),
                               md->GetVar(0), md->GetVar(1), md->GetVar(2),
                               md->GetRangeDown(md->GetVar(0)), md->GetRangeUp(md->GetVar(0)),
			       md->GetRangeDown(md->GetVar(1)), md->GetRangeUp(md->GetVar(1)),
			       md->GetRangeDown(md->GetVar(2)), md->GetRangeUp(md->GetVar(2)),
                               type,
                               work,
                               plotSet,
                               debug
                               );

      }
    
	return work;
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 2D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


  RooWorkspace* ObtainPIDShapeFromCalibSample(TString& filesDir, TString& sig, 
					      TString& fileCalib, TString& workCalib, 
					      TString namePID, TString nameVar1, TString nameVar2,
					      double PID_down, double PID_up,
					      double Var1_down, double Var1_up,
					      double Var2_down, double Var2_up,
					      Int_t bin1, Int_t bin2,
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

    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(),nameVar1.Data(),log(Var1_down), log(Var1_up));
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(),nameVar2.Data(),log(Var2_down), log(Var2_up)); 
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

    Int_t size=0;

    ReadOneName(filesDir,FileName,sig,debug);
    if ( type.Contains("MC") == true )
      {
	ReadMode(FileName, mode, false, debug);
        size = mode.size();
      }
    else { if( debug == true) {std::cout<<"[ERROR] Wrong sample andmode"<<std::endl;} return NULL; }

    std::vector<TString> smp(size); 
    if ( type.Contains("MC") == true )
      {
        for(int i = 0; i< size; i++ )
          {
            smp[i] = CheckPolarity(sig, debug);
          }
      }
    else
      {
        if( debug == true) {std::cout<<"[ERROR] Wrong sample andmode"<<std::endl;} return NULL;
      }

    TString ext = "pdf";
    TString dataName;
    if ( fileCalib.Contains("Calib") == true)
      {
        dataName = "data";
      }
    else
      {
        TString s = CheckPolarity(fileCalib,debug);
	dataName = "ProtonsSample_"+s;
      }

    RooWorkspace* workC = NULL; 
    RooDataSet* dataC = NULL;     

    workC = LoadWorkspace(fileCalib, workCalib, debug);
    dataC = GetDataSet(workC, dataName, debug );
    dataC->Print("v");
    const TTree* treeConst = dataC->tree();
    TTree* treeC = new TTree("name","name"); 
    treeC = treeConst->GetTree();
    Double_t nsig_sw3,PID3,Var13, Var23; 

    if ( type.Contains("Proton") != true )
      {
	TString Par;
	Par = CheckTreeLabel(fileCalib, debug); 
	treeC->SetBranchAddress("nsig_sw", &nsig_sw3);
	TString nameDLL = Par+"_CombDLLK";
	treeC->SetBranchAddress(nameDLL.Data(), &PID3);
	TString nVar1 = CheckTreeLabel(fileCalib, nameVar1, debug);
	treeC->SetBranchAddress(nVar1.Data(), &Var13);
	TString nVar2 = CheckTreeLabel(fileCalib, nameVar2, debug);
	treeC->SetBranchAddress(nVar2.Data(), &Var23);
      }
    else
      {
	treeC->SetBranchAddress("sWeights", &nsig_sw3);
	treeC->SetBranchAddress(namePID.Data(), &PID3);
	treeC->SetBranchAddress(nameVar1.Data(), &Var13);
	treeC->SetBranchAddress(nameVar2.Data(), &Var23);
      }
    //treeC->Print();
    Double_t wRW(0), wA(0);
    TH2F* histRW;

    TString l1 = "MC";
    TString l2 = "Calib";
    TString l3 = "Calib weighted";

    RooDataSet* dataCalib = NULL;
    dataCalib = GetDataCalibSample( fileCalib,  workCalib, Var1, Var2, plotSet, debug );
    
    TString histNameCalib = "hist2D_Calib";
    TH2F* histCalib = Get2DHist(dataCalib,Var1, Var2, bin1, bin2, histNameCalib, debug);

    RooAbsPdf* pdfPID[size];
        
    for( int i = 0; i<size; i++)
      {
		
	TString m = mode[i];
        if ( (type.Contains("Kaon") == true && (m.Contains("Kst") == true   || m.Contains("K") == true)) ||
             (type.Contains("Pion") == true && (m.Contains("Pi") == true  || m.Contains("Rho") == true)) ||
             (type.Contains("Proton") == true && (mode[i] == "Lb2Dsp" || mode[i] == "Lb2Dsstp" )))
	  {
	    TH2F* hist = NULL;
	    TH2F* histMC = NULL;
	    
	    TString nm, name;
	    TString histName;
	    TString histNameR;
	    TString nameCalib;
	    if ( type.Contains("MC") == true )
	      {
		nm = mode[i]+"_"+smp[i];
		histName = "hist2D_"+nm;
		histNameR = "hist2D_ratio_"+nm;
		nameCalib = "CalibSample_"+nm;
	      }
	    else
	      {
		if( debug == true) std::cout<<"[ERROR] Wrong sample and mode"<<std::endl;
	      }
	    
	 
	    
	    if( debug == true) std::cout<<"Calculating for "<<nm<<std::endl;
	    //TString histName = "hist2D_ratio_"+nm;
	    hist = (TH2F*)work->obj(histNameR.Data());
	    if ( hist != NULL ) { std::cout<<" Read histogram: "<<hist->GetName()<<std::endl;} 
	    else {std::cout<<" Cannot read histogram: "<<histName.Data()<<std::endl;}
	    histMC = (TH2F*)work->obj(histName.Data());
	    
    
	    TString namew = "weights";
	    RooRealVar* weights;
	    weights = new RooRealVar(namew.Data(), namew.Data(), -50.0, 50.0 );
	    RooDataSet* dataRW = NULL;

	    TH1* histPID = NULL;
            TString namehist = "histPID_"+nm;
	    if( type.Contains("MC") == true && type.Contains("BsDsPi")==true)
	      {
		histPID = new TH1D(namehist.Data(), namehist.Data(), 200, PID_down, PID_up);
		dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights), namew.Data());
	      }
	    else
	      {
		histPID = new TH1D(namehist.Data(), namehist.Data(), 50, PID_down, PID_up);
		dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights), namew.Data());
	      }

	    //std::cout<<"tuuuu"<<std::endl;
	    for (Long64_t jentry=0; jentry<treeC->GetEntries(); jentry++)
	      {
		treeC->GetEntry(jentry);
		if( type.Contains("MC") == true && type.Contains("BsDsPi")==true)
		  {
		    PID3 = -PID3;
		    lab1_PIDK->setVal(PID3);
		  }
		else
		  {
		    lab1_PIDK->setVal(PID3);
		  }
		Var1->setVal(Var13);
		Var2->setVal(Var23);
		//std::cout<<"Var13: "<<Var13<<" Var23: "<<Var23<<std::endl;
		Int_t binRW = hist->FindBin(Var13,Var23);
		wRW = hist->GetBinContent(binRW);
		wA = nsig_sw3*wRW;
		//std::cout<<" weight: "<<wA<<" nsigSW: "<<nsig_sw3<<" wRW "<<wRW<<" "<<nameVar1<<": "<<Var13<<" "<<nameVar2<<": "<<Var23<<std::endl;
		weights->setVal(wA);
		if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true))
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
	    if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true) )
              {
                binHist = 200;
		histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(200,PID_down,PID_up));
	      }
            else
              {
		binHist = 50;
		histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(50,PID_down,PID_up));
              }
	    histPID->SetName(namehist.Data());
	    histPID->SaveAs("hist_PID.root");
	    Double_t zero = 1e-20;
	    for(int k = 1; k<binHist; k++)
	      {
		Double_t cont = histPID->GetBinContent(k);
		if( cont < 0 ) { histPID->SetBinContent(k,zero); }
	      }
	    
	   	    	    
	    pdfPID[i] = NULL;
	    if( type.Contains("MC") == true && type.Contains("BsDsPi")==true) 
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
	    else if ( type.Contains("BsDsK") == true )
	      {
		TString dir = "PlotBsDsK2D";
		if (debug == true) PlotWeightingSample(nm, dataCalib, dataRW, Var1, Var2, lab1_PIDK, bin1, bin2, bin3, 
						       type, l2, l3, work, plotSet,  debug);
		if ( type.Contains("Pion") == true)
		  {
		    pdfPID[i] = FitPDFShapeForPIDBsDsKPi(dataRW, lab1_PIDK, nm,  plotSet,  debug);
		    work->import(*pdfPID[i]);

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
		    pdfPID[i] = FitPDFShapeForPIDBsDsKP(dataRW, lab1_PIDK, nm, plotSet,  debug);
		    work->import(*pdfPID[i]);
		  }
	      }
	    //work->import(*pdfPID[i]);
	    
	  }
	
      }
    return work;
  } 
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 3D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  RooWorkspace* ObtainPIDShapeFromCalibSample(TString& filesDir, TString& sig,
					      TString& fileCalib, TString& workCalib,
					      TString namePID, TString nameVar1, TString nameVar2, TString nameVar3,
                                              double PID_down, double PID_up,
                                              double Var1_down, double Var1_up,
                                              double Var2_down, double Var2_up,
					      double Var3_down, double Var3_up,
                                              Int_t bin1, Int_t bin2, Int_t bin3,
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

    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(),nameVar1.Data(),log(Var1_down), log(Var1_up));
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(),nameVar2.Data(),log(Var2_down), log(Var2_up));
    RooRealVar* Var3 = new RooRealVar(nameVar3.Data(),nameVar3.Data(),log(Var3_down), log(Var3_up));
    RooRealVar* lab1_PIDK = new RooRealVar(namePID.Data(), namePID.Data(), PID_down, PID_up);
    
    TString label1, label2, label3;
    if ( nameVar1 != nameVar2 )
      {
        label1 = CheckWeightLabel(nameVar1, debug);
        label2 = CheckWeightLabel(nameVar2, debug);
	label3 = CheckWeightLabel(nameVar2, debug);
      }
    else { if(debug == true) std::cout<<"The same name of variables: "<<nameVar1<<"  "<<nameVar2<<std::endl; }

    if(debug == true) std::cout<<nameVar1<<" range: ("<<log(Var1_down)<<","<<log(Var1_up)<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar2<<" range: ("<<log(Var2_down)<<","<<log(Var2_up)<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar3<<" range: ("<<log(Var3_down)<<","<<log(Var3_up)<<")"<<std::endl;
    if(debug == true) std::cout<<namePID<<" range: ("<<PID_down<<","<<PID_up<<")"<<std::endl;

    std::vector <std::string> FileName;
    std::vector <std::string> mode;

    Int_t size=0;

    ReadOneName(filesDir,FileName,sig,debug);
    if ( type.Contains("MC") == true )
      {
        ReadMode(FileName, mode, false, debug);
        size = mode.size();
      }
    else { if( debug == true) {std::cout<<"[ERROR] Wrong sample andmode"<<std::endl;} return NULL; }

    std::vector<TString> smp(size); 
    
    if ( type.Contains("MC") == true )
      {
        for(int i = 0; i< size; i++ )
          {
            smp[i] = CheckPolarity(sig, debug);
          }
      }
    else
      {
        if( debug == true) {std::cout<<"[ERROR] Wrong sample andmode"<<std::endl;} return NULL;
      }

    TString ext = "pdf";
    
    TString dataName = "data";
    RooWorkspace* workC = LoadWorkspace(fileCalib, workCalib, debug);
    RooDataSet* dataC = GetDataSet(workC, dataName, debug );
    const TTree* treeConst = dataC->tree();
    TTree* treeC = new TTree("name","name"); //     treeConst->CloneTree(0);
    treeC = treeConst->GetTree();
    //treeConst->CopyEntries(treeC);
    Double_t nsig_sw3,PID3,Var13, Var23, Var33;

    TString Par;
    Par = CheckTreeLabel(fileCalib, debug);
    treeC->SetBranchAddress("nsig_sw", &nsig_sw3);
    TString nameDLL = Par+"_CombDLLK";
    treeC->SetBranchAddress(nameDLL.Data(), &PID3);
    TString nVar1 = CheckTreeLabel(fileCalib, nameVar1, debug);
    treeC->SetBranchAddress(nVar1.Data(), &Var13);
    TString nVar2 = CheckTreeLabel(fileCalib, nameVar2, debug);
    treeC->SetBranchAddress(nVar2.Data(), &Var23);
    TString nVar3 = CheckTreeLabel(fileCalib, nameVar3, debug);
    treeC->SetBranchAddress(nVar3.Data(), &Var33);
    treeC->Print();
    Double_t wRW(0), wA(0);
    
    TH3F* histRW;

    TString l1 = "MC";
    TString l2 = "Calib";
    TString l3 = "Calib weighted";

    RooDataSet* dataCalib = GetDataCalibSample( fileCalib,  workCalib, Var1, Var2, Var3, plotSet, debug );
    std::cout<<"dataCalib: "<<dataCalib->sumEntries()<<" "<<dataCalib->numEntries()<<std::endl;
    TString histNameCalib = "hist2D_Calib_"+Par;
    TH3F* histCalib = new TH3F(histNameCalib.Data(),histNameCalib.Data(),
                               bin1,log(Var1_down),log(Var1_up),
                               bin2,log(Var2_down),log(Var2_up),
                               bin3,log(Var3_down),log(Var3_up));
    histCalib = Get3DHist(dataCalib,Var1, Var2, Var3, histCalib, debug);
    
    RooAbsPdf* pdfPID[size];
    for( int i = 0; i<size; i++)
      {

        TString m = mode[i];
        if ( (type.Contains("Kaon") == true && (m.Contains("Kst") == true   || m.Contains("K") == true)) ||
             (type.Contains("Pion") == true && (m.Contains("Pi") == true  || m.Contains("Rho") == true)) ||
             (type.Contains("Proton") == true && (mode[i] == "Lb2Dsp" || mode[i] == "Lb2Dsstp" )))
          {
            TH3F* hist = NULL;
            TH3F* histMC = NULL;

	    if (hist) {}
	    if (histMC) {}

            TString nm, name;
            TString histName;
            TString histNameR;
            TString nameCalib;
            if ( type.Contains("MC") == true )
              {
                nm = mode[i]+"_"+smp[i];
                histName = "hist2D_"+nm;
                histNameR = "hist2D_ratio_"+nm;
                nameCalib = "CalibSample_"+nm;
              }
	    else
              {
                if( debug == true) std::cout<<"[ERROR] Wrong sample and mode"<<std::endl;
              }
            if( debug == true) std::cout<<"Calculating for "<<nm<<std::endl;
            //TString histName = "hist2D_ratio_"+nm;
            hist = (TH3F*)work->obj(histNameR.Data());
            if ( hist != NULL ) { std::cout<<" Read histogram: "<<hist->GetName()<<std::endl;}
            else {std::cout<<" Cannot read histogram: "<<histName.Data()<<std::endl;}
            histMC = (TH3F*)work->obj(histName.Data());


            TString namew = "weights";
            RooRealVar* weights;
            weights = new RooRealVar(namew.Data(), namew.Data(), -50.0, 50.0 );
            //TString nameCalib = "CalibSample_"+nm;
            RooDataSet* dataRW = NULL;
	    
	    histRW = NULL;
            histName = "hist2D_rw_"+nm;
	    histRW = new TH3F(histName.Data(),histName.Data(),
			      bin1,log(Var1_down),log(Var1_up),
			      bin2,log(Var2_down),log(Var2_up),
			      bin3,log(Var3_down),log(Var3_up));

            //std::cout<<"tuuuu"<<std::endl;

	    TH1* histPID = NULL;
	    TString namehist = "histPID_"+nm;
	    if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true) )
	      {
		histPID = new TH1D(namehist.Data(), namehist.Data(), 200, PID_down, PID_up);
		dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*Var3,*weights), namew.Data());
	      }
	    else
	      {
		histPID = new TH1D(namehist.Data(), namehist.Data(), 50, PID_down, PID_up);
		dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*Var3,*weights), namew.Data());
	      }

	    for (Long64_t jentry=0; jentry<treeC->GetEntries(); jentry++)
              {
                treeC->GetEntry(jentry);
		if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true) )
		  {
		    PID3 = -PID3;
		    lab1_PIDK->setVal(PID3);
		  }
		else
		  {
		    lab1_PIDK->setVal(PID3);
		  }
                Var1->setVal(Var13);
                Var2->setVal(Var23);
		Var3->setVal(Var33);
                //std::cout<<"Var13: "<<Var13<<" Var23: "<<Var23<<std::endl;
                Int_t binRW = hist->FindBin(Var13,Var23,Var33);
                wRW = hist->GetBinContent(binRW);
                wA = nsig_sw3*wRW;
                //std::cout<<" weight: "<<wA<<" nsigSW: "<<nsig_sw3<<" wRW "<<wRW<<" "<<nameVar1<<": "<<Var13<<" "<<nameVar2<<": "<<Var23<<std::endl;
		weights->setVal(wA);
		if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true))
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

		histRW->Fill(Var13,Var23,Var33,wA);
              }
	    if ( dataRW != NULL  ){
	      std::cout<<"[INFO] ==> Create "<<dataRW->GetName()<<std::endl;
	      std::cout<<" number of entries in data set: "<<dataRW->numEntries()<<" with the sum: "<<dataRW->sumEntries()<<std::endl;
	    } else { std::cout<<"Error in create dataset"<<std::endl; }
	    /*
	    TString dupa = "TrMom";
	    SaveDataSet(dataRW, Var1 , nm, dupa, debug);
	    TString dupa2 = "nTr";
	    SaveDataSet(dataRW, Var2 , nm, dupa2, debug);
	    TString dupa3 = "Mom";
	    SaveDataSet(dataRW, Var3 , nm, dupa3, debug);
	    TString dupa4 = "PID";
            SaveDataSet(dataRW, lab1_PIDK , nm, dupa4, debug);
	    */
               
            Int_t binPIDK = 50;
	    Int_t binHist = 1;
	    RooBinned1DQuinticBase<RooAbsPdf>* pdfPID2 = NULL;
	    if ( pdfPID2 ) {}

	    if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true) )
	      {
		histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(200,PID_down,PID_up));
		binHist = 200;
	      }
	    else
	      {
		histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(50,PID_down,PID_up));
		binHist = 50;
	      }
	    histPID->SetName(namehist.Data());
            histPID->SaveAs("hist_PID.root");
	    Double_t zero = 1e-20;
	    for(int k = 1; k<binHist; k++)
	      {
		Double_t cont = histPID->GetBinContent(k);
                if( cont < 0 ) { histPID->SetBinContent(k,zero); }
              }


            pdfPID[i] = NULL;
            if( type.Contains("MC") == true && type.Contains("BsDsPi")==true)
              {
                TString dir = "PlotBsDsPi";
		PlotWeightingSample(nm, dataCalib, dataRW, Var1, Var2, Var3, lab1_PIDK, 
				    bin1, bin2, bin3, binPIDK, type, l2, l3, work, plotSet, debug);
		
		if ( type.Contains("Pion") == true)
                  {
                    TString namepdf = "PIDKShape_"+nm;
                    pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
                    RooAbsPdf* pdfSave = pdfPID2;
		    TString t = "";
                    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nm,  t, plotSet, debug );
                    work->import(*pdfPID2);
                  }
                else
                  {
                    pdfPID[i] = FitPDFShapeForPIDBsDsPiK(dataRW, lab1_PIDK, nm, plotSet, debug);
		    work->import(*pdfPID[i]);
		  }
              }
            else if ( type.Contains("BsDsK") == true )
	      {
                TString dir = "PlotBsDsK";
                PlotWeightingSample(nm, dataCalib, dataRW, Var1, Var2, Var3, lab1_PIDK, 
				    bin1, bin2, bin3, binPIDK,
				    type, l2, l3, work, plotSet, debug);
                if ( type.Contains("Pion") == true)
                  {
                    pdfPID[i] = FitPDFShapeForPIDBsDsKPi(dataRW, lab1_PIDK, nm,  plotSet, debug);
		    work->import(*pdfPID[i]);
		  }
                else if ( type.Contains("Kaon") == true)
                  {
                    //pdfPID[i] = FitPDFShapeForPIDBsDsKK(dataRW, lab1_PIDK, nm, plotSet,  debug);
		    TString namepdf = "PIDKShape_"+nm;
		    pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
		    work->import(*pdfPID2);
		  }
                else
                  {
                    pdfPID[i] = FitPDFShapeForPIDBsDsKP(dataRW, lab1_PIDK, nm,  plotSet, debug);
		    work->import(*pdfPID[i]);
                  }
              }
	    //work->import(*pdfPID[i]);

	  }
	
      }
    return work;
  }

  RooWorkspace* ObtainPIDShapeFromCalibSample(TString& filesDir, TString& sig,
                                              MDFitterSettings* md,
					      TString& type,
                                              RooWorkspace* work,
                                              PlotSettings* plotSet,
                                              bool debug)
  {
    TString fileCalib = "";
    TString workCalib = "";

    TString bach = CheckBachelor(type, debug);
    TString pol = CheckPolarity(type, debug);

    if ( bach == "Pi" )
      {
	if ( pol == "up" ) { fileCalib = md->GetCalibPionUp(); } else { fileCalib = md->GetCalibPionDown(); }
        workCalib = md->GetCalibPionWorkName();
      }
    else if ( bach == "K" )
      {
        if ( pol == "up" ) { fileCalib = md->GetCalibKaonUp(); } else { fileCalib = md->GetCalibKaonDown(); }
        workCalib = md->GetCalibKaonWorkName();
      }
    else if ( bach == "P" )
      {
        if ( pol == "up" ) { fileCalib = md->GetCalibProtonUp(); } else { fileCalib = md->GetCalibProtonDown(); }
        workCalib = md->GetCalibProtonWorkName();
      }
    
    if( md->GetWeightingDim() == 2 )
      {
	work =  ObtainPIDShapeFromCalibSample(filesDir, sig,
					      fileCalib, workCalib,
					      md->GetPIDKVar(), md->GetVar(0), md->GetVar(1),
					      md->GetPIDKRangeDown(), md->GetPIDKRangeUp(),
					      md->GetRangeDown(md->GetVar(0)), md->GetRangeUp(md->GetVar(0)),
					      md->GetRangeDown(md->GetVar(1)), md->GetRangeUp(md->GetVar(1)),
					      md->GetBin(0), md->GetBin(1),
					      type,
					      work,
					      plotSet,
					      debug);
	  
	  }
    else
      {
	work =  ObtainPIDShapeFromCalibSample(filesDir, sig,
                                              fileCalib, workCalib,
                                              md->GetPIDKVar(), md->GetVar(0), md->GetVar(1), md->GetVar(2),
                                              md->GetPIDKRangeDown(), md->GetPIDKRangeUp(),
                                              md->GetRangeDown(md->GetVar(0)), md->GetRangeUp(md->GetVar(0)),
                                              md->GetRangeDown(md->GetVar(1)), md->GetRangeUp(md->GetVar(1)),
                                              md->GetRangeDown(md->GetVar(2)), md->GetRangeUp(md->GetVar(2)),
					      md->GetBin(0), md->GetBin(1), md->GetBin(2),
					      type,
                                              work,
                                              plotSet,
                                              debug);

      }

    return work; 
  }


  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 2D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  RooWorkspace* ObtainHistRatioOneSample(TString& fileCalib, TString& workCalib,
					 Int_t bin1, Int_t bin2,
					 TString nameVar1, TString nameVar2,
					 double Var1_down, double Var1_up,
					 double Var2_down, double Var2_up,
					 TString& type,
					 RooWorkspace* work,
					 RooWorkspace* workL,
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
    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(),nameVar1.Data(),log(Var1_down), log(Var1_up));
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(),nameVar2.Data(),log(Var2_down), log(Var2_up)); //-5,6);

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
    RooDataSet* dataCalib = GetDataCalibSample( fileCalib,  workCalib, Var1, Var2, plotSet, debug );
    TString histNameCalib = "hist2D_Calib";
    TH2F* histCalib = Get2DHist(dataCalib,Var1, Var2, bin1, bin2, histNameCalib, debug);
    Save2DHist(histCalib, plotSet);

    
    Double_t binMC, binData, binRatio;
    Double_t binMCErr, binDataErr, binRatioErr;

    TString l2 = "Calib";
    TString l3 = "Ratio";

    std::cout<<"type: "<<type<<std::endl;
    std::vector <TString> names = CheckWeightNames(type, debug);
    TString nm = names[0];
    TString name = names[1]; 
    TString histName = names[2];
    TString histNameR = names [3] ;

    RooDataSet*  data = GetDataSet(workL,name,debug);
    if ( type.Contains("MC") == true )
      { data = new RooDataSet(data->GetName(), data->GetTitle(), *(data->get()), RooFit::Import(*data), RooFit::WeightVar("weights"));}

    double scaleA = dataCalib->sumEntries()/data->sumEntries();
    
    hist2Data.push_back(Get2DHist(data,Var1, Var2, bin1, bin2, histName, debug));
    std::cout<<"Debug"<<std::endl;
    hist2Ratio.push_back(new TH2F(histNameR.Data(),histNameR.Data(),
				  bin1,log(Var1_down),log(Var1_up),
				  bin2,log(Var2_down),log(Var2_up)));
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
	      binRatioErr = binRatio*sqrt((binDataErr*binDataErr)/(binData*binData)+(binMCErr*binMCErr)/(binMC*binMC));
	    }
	    //      if( debug == true) std::cout<<"bin1D: "<<k<<" bin2D: "<<j<<" scale: "<<scaleA<<" binMC: "<<binMC<<" +/- "<<binMCErr<<" binData "<<binData<<" +/- "<<binDataErr<<" Ratio: "<<binRatio<<" +/- "<<binRatioErr<<std::endl;
	    hist2Ratio[sizehist-1]->SetBinContent(k,j,binRatio);
	    hist2Ratio[sizehist-1]->SetBinError(k,j,binRatioErr);
	  }
      }
    //std::cout<<"Debug2"<<std::endl;
    Save2DComparison(hist2Data[sizehist-1], type, histCalib, l2, hist2Ratio[sizehist-1], l3, plotSet);
    //std::cout<<"Debug3"<<std::endl;
    //Save2DHist(hist2Data[sizehist-1], ext);
    //Save2DHist(hist2Ratio[sizehist-1], ext);
    work->import(*hist2Ratio[sizehist-1]);
    work->import(*hist2Data[sizehist-1]);
    //std::cout<<"Debug4"<<std::endl;

    if ( type.Contains("Comb") == true) {  work->import(*data); }
    
    return work;
    
  }
  
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 3D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  RooWorkspace* ObtainHistRatioOneSample(TString& fileCalib, TString& workCalib,
                                         Int_t bin1, Int_t bin2, Int_t bin3, 
                                         TString nameVar1, TString nameVar2, TString nameVar3,
                                         double Var1_down, double Var1_up,
                                         double Var2_down, double Var2_up,
					 double Var3_down, double Var3_up,
                                         TString& type,
                                         RooWorkspace* work,
                                         RooWorkspace* workL,
					 PlotSettings* plotSet,
                                         bool debug
					 )

  {
    if ( debug == true)
      {
	std::cout << "[INFO] ==> WeightingUtils::ObtainHistRatioOneSample(...)."
                  << " Obtain 2D histogram MC/Calibration sample"
                  << std::endl;
      }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }
    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(),nameVar1.Data(),log(Var1_down), log(Var1_up));
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(),nameVar2.Data(),log(Var2_down), log(Var2_up)); //-5,6);
    RooRealVar* Var3 = new RooRealVar(nameVar3.Data(),nameVar3.Data(),log(Var3_down), log(Var3_up));

    TString label1, label2, label3;
    if ( nameVar1 != nameVar2 && nameVar1 != nameVar3 && nameVar2 != nameVar3)
      {
        label1 = CheckWeightLabel(nameVar1, debug);
        label2 = CheckWeightLabel(nameVar2, debug);
	label3 = CheckWeightLabel(nameVar3, debug);
      }
    else { if(debug == true) std::cout<<"The same name of variables: "<<nameVar1<<"  "<<nameVar2<<std::endl; }

    if(debug == true) std::cout<<nameVar1<<" range: ("<<log(Var1_down)<<","<<log(Var1_up)<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar2<<" range: ("<<log(Var2_down)<<","<<log(Var2_up)<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar3<<" range: ("<<log(Var3_down)<<","<<log(Var3_up)<<")"<<std::endl;


    std::vector <std::string> FileName;
    std::vector <std::string> mode;

    
    std::vector <TH3F*> hist2Data;
    std::vector <TH3F*> hist2Ratio;

    RooDataSet* dataCalib = GetDataCalibSample( fileCalib,  workCalib, Var1, Var2, Var3, plotSet, debug );
    std::cout<<"dataCalib: "<<dataCalib->sumEntries()<<" "<<dataCalib->numEntries()<<std::endl;
    TString histNameCalib = "hist2D_Calib";
    TH3F* histCalib = new TH3F(histNameCalib.Data(),histNameCalib.Data(),
                               bin1,log(Var1_down),log(Var1_up),
                               bin2,log(Var2_down),log(Var2_up),
                               bin3,log(Var3_down),log(Var3_up));
    histCalib = Get3DHist(dataCalib,Var1, Var2, Var3, histCalib, debug);
    Save3DHist(histCalib, plotSet);
   
    Double_t binMC, binData, binRatio;
    Double_t binMCErr, binDataErr, binRatioErr;

    TString l2 = "Calib";
    TString l3 = "Ratio";

    std::cout<<"type: "<<type<<std::endl;
    std::vector <TString> names = CheckWeightNames(type, debug);
    TString nm = names[0];
    TString name = names[1];
    TString histName = names[2];
    TString histNameR = names [3] ;

    std::cout<<"name: "<<name<<std::endl;
    RooDataSet*  data = GetDataSet(workL,name,debug);
    if ( type.Contains("MC") == true )
      { data = new RooDataSet(data->GetName(), data->GetTitle(), *(data->get()), RooFit::Import(*data), RooFit::WeightVar("weights"));}

    double scaleA = dataCalib->sumEntries()/data->sumEntries();
    std::cout<<"ratio: "<<scaleA<<" = "<<dataCalib->sumEntries()<<"/"<<data->sumEntries()<<std::endl;

    TString dupa1 = "Comb2";
    TString dupa2 = "_TrMom";
    SaveDataSet(data, Var1 , dupa1, dupa2, plotSet, debug);


    hist2Data.push_back(new TH3F(histName.Data(),histName.Data(),
				 bin1,log(Var1_down),log(Var1_up),
				 bin2,log(Var2_down),log(Var2_up),
				 bin3,log(Var3_down),log(Var3_up)));

    int sizehistData = hist2Data.size();
    std::cout<<"Create histogram: "<<hist2Data[sizehistData-1]->GetName()<<std::endl;
    std::cout<<"Size histogram: "<<sizehistData<<std::endl;
    hist2Data[sizehistData-1] = Get3DHist(data,Var1, Var2, Var3, hist2Data[sizehistData-1], debug);
    Save3DHist(hist2Data[sizehistData-1], plotSet);

    dupa1 = "Calib2";
    dupa2 = "_TrMom";
    SaveDataSet(data, Var1 , dupa1, dupa2, plotSet, debug);

    hist2Ratio.push_back(new TH3F(histNameR.Data(),histNameR.Data(),
				  bin1,log(Var1_down),log(Var1_up),
				  bin2,log(Var2_down),log(Var2_up),
				  bin3,log(Var3_down),log(Var3_up)));
    int sizehist = hist2Ratio.size();
    hist2Ratio[sizehist-1]->SetStats(kFALSE);
    hist2Ratio[sizehist-1]->GetXaxis()->SetTitle(label1.Data());
    hist2Ratio[sizehist-1]->GetYaxis()->SetTitle(label2.Data());
    hist2Ratio[sizehist-1]->GetZaxis()->SetTitle(label3.Data());
    TString TitleHist="";
    hist2Ratio[sizehist-1]->SetTitle(TitleHist.Data());
  

    for(int k = 1; k<bin1; k++)
      {
        for (int j = 1; j<bin2; j++)
          {
	    for (int l = 1; l < bin3; l++)
	      {
		binMC = histCalib->GetBinContent(k,j,l);
		binData = hist2Data[sizehist-1]->GetBinContent(k,j,l);
		binMCErr = histCalib->GetBinError(k,j,l);
		binDataErr = hist2Data[sizehist-1]->GetBinError(k,j,l);
		
		if ( binMC < 0 || binMC == 0 || binData < 0 || binData == 0 ) { binRatio = 0; binRatioErr=0; }
		else {
		  binRatio = binData/binMC*scaleA;
		  binRatioErr = binRatio*sqrt((binDataErr*binDataErr)/(binData*binData)+(binMCErr*binMCErr)/(binMC*binMC));
		}
		hist2Ratio[sizehist-1]->SetBinContent(k,j,l,binRatio);
		hist2Ratio[sizehist-1]->SetBinError(k,j,l,binRatioErr);
		if( binRatio != 0 )
		  {
		    std::cout<<k<<" "<<j<<" "<<l<<" "<<binData<<" "<<binMC<<" "<<binRatio<<" "<<binRatioErr<<std::endl;
		  }
	      }
	  }
      }
    work->import(*hist2Ratio[sizehist-1]);
    work->import(*hist2Data[sizehist-1]);
    Save3DHist(hist2Ratio[sizehist-1], plotSet);
    //Save3DHist(hist2Data[sizehist-1], ext);

    if ( type.Contains("Comb") == true) {  work->import(*data); }

    return work;

  }

  RooWorkspace* ObtainHistRatioOneSample(MDFitterSettings* md,
                                         TString& type,
                                         RooWorkspace* work,
                                         RooWorkspace* workL,
                                         PlotSettings* plotSet,
                                         bool debug
					 )

  {
    TString fileCalib = "";
    TString workCalib = "";

    TString bach = CheckBachelor(type, debug);
    TString pol = CheckPolarity(type, debug);

    if ( bach == "Pi" )
      {
        if ( pol == "up" ) { fileCalib = md->GetCalibPionUp(); } else { fileCalib = md->GetCalibPionDown(); }
        workCalib = md->GetCalibPionWorkName();
      }
    else if ( bach == "K" )
      {
	if ( pol == "up" ) { fileCalib = md->GetCalibKaonUp(); } else { fileCalib = md->GetCalibKaonDown(); }
        workCalib = md->GetCalibKaonWorkName();
      }
    else if ( bach == "P" )
      {
        if ( pol == "up" ) { fileCalib = md->GetCalibProtonUp(); } else { fileCalib = md->GetCalibProtonDown(); }
        workCalib = md->GetCalibProtonWorkName();
      }

    if( md->GetWeightingDim() == 2 )
      {
	work = ObtainHistRatioOneSample(fileCalib, workCalib,
					md->GetBin(0), md->GetBin(1),
					md->GetVar(0), md->GetVar(1),
					md->GetRangeDown(md->GetVar(0)), md->GetRangeUp(md->GetVar(0)),
					md->GetRangeDown(md->GetVar(1)), md->GetRangeUp(md->GetVar(1)),
					type,
					work,
					workL,
					plotSet,
					debug
					);
      }
    else
      {
	work = ObtainHistRatioOneSample(fileCalib, workCalib,
                                        md->GetBin(0), md->GetBin(1), md->GetBin(2),
					md->GetVar(0), md->GetVar(1), md->GetVar(2),
					md->GetRangeDown(md->GetVar(0)), md->GetRangeUp(md->GetVar(0)),
                                        md->GetRangeDown(md->GetVar(1)), md->GetRangeUp(md->GetVar(1)),
                                        md->GetRangeDown(md->GetVar(2)), md->GetRangeUp(md->GetVar(2)),
					type,
                                        work,
                                        workL,
                                        plotSet,
					debug
                                        );
      }
    
    return work;
    
  }

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //// 2D weighting
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  
  RooWorkspace* ObtainPIDShapeFromCalibSampleOneSample(TString& fileCalib, TString& workCalib,
						       TString namePID, TString nameVar1, TString nameVar2,
						       double PID_down, double PID_up,
						       double Var1_down, double Var1_up,
						       double Var2_down, double Var2_up,
						       Int_t bin1, Int_t bin2,
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
    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(),nameVar1.Data(),log(Var1_down), log(Var1_up));
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(),nameVar2.Data(),log(Var2_down), log(Var2_up));
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

    TString dataName;
    if ( fileCalib.Contains("Calib") == true)
      {
        dataName = "data";
      }
    else
      {
        TString s = CheckPolarity(fileCalib,debug);
        dataName = "ProtonsSample_"+s;
      }

    RooWorkspace* workC = LoadWorkspace(fileCalib, workCalib, debug);
    RooDataSet* dataC = GetDataSet(workC, dataName, debug );
    const TTree* treeConst = dataC->tree();
    TTree* treeC = new TTree("name","name"); //     treeConst->CloneTree(0);
    treeC = treeConst->GetTree();
    //treeConst->CopyEntries(treeC);
    Double_t nsig_sw3,PID3,Var13, Var23;

    if ( type.Contains("Proton") != true )
      {
        TString Par;
        Par = CheckTreeLabel(fileCalib, debug);
        treeC->SetBranchAddress("nsig_sw", &nsig_sw3);
        TString nameDLL = Par+"_CombDLLK";
        treeC->SetBranchAddress(nameDLL.Data(), &PID3);
        TString nVar1 = CheckTreeLabel(fileCalib, nameVar1, debug);
        treeC->SetBranchAddress(nVar1.Data(), &Var13);
        TString nVar2 = CheckTreeLabel(fileCalib, nameVar2, debug);
        treeC->SetBranchAddress(nVar2.Data(), &Var23);
      }
    else
      {
        treeC->SetBranchAddress("sWeights", &nsig_sw3);
        treeC->SetBranchAddress(namePID.Data(), &PID3);
        treeC->SetBranchAddress(nameVar1.Data(), &Var13);
        treeC->SetBranchAddress(nameVar2.Data(), &Var23);
      }


    treeC->Print();
    Double_t wRW(0), wA(0);
    TH2F* histRW;
    
    //TString l1 = "MC";
    TString l2 = "Calib";
    TString l3 = "Calib weighted";

    RooDataSet* dataCalib = GetDataCalibSample( fileCalib,  workCalib, Var1, Var2, plotSet, debug );
    TString histNameCalib = "hist2D_Calib";
    TH2F* histCalib = Get2DHist(dataCalib,Var1, Var2, bin1, bin2, histNameCalib, debug);

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
        
    hist = (TH2F*)work->obj(histNameR.Data());
    if ( hist != NULL ) { std::cout<<" Read histogram: "<<hist->GetName()<<std::endl;}
    else {std::cout<<"[ERROR] Cannot read histogram: "<<histName.Data()<<std::endl;}
    histMC = (TH2F*)work->obj(histName.Data());
    
    TString nn;
    if( type.Contains("Comb") == true) { nn = "Comb_"+nm; }
    else if (type.Contains("DPi") == true) { nn = "Bd2DPi_"+nm;}
    else if (type.Contains("BsDsPi") == true && type.Contains("MC") != true) { nn = "BsDsPi_"+nm; }
    else {nn=nm;}

    TString namew = "weights";
    RooRealVar* weights;
    weights = new RooRealVar(namew.Data(), namew.Data(), -50.0, 50.0 );
    //TString nameCalib = "CalibSample_"+nm;
    RooDataSet* dataRW = NULL;
    TH1* histPID = NULL;
    TString namehist = "histPID_"+nn;

    if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true) || type.Contains("DPi") == true || type.Contains("CombPi") == true )
      {
	dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights), namew.Data());
	histPID = new TH1D(namehist.Data(), namehist.Data(), 200, PID_down, PID_up); //50, log(0.0001), log(-PID_down));
      }
    else
      {
	dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*weights), namew.Data());
	histPID = new TH1D(namehist.Data(), namehist.Data(), 50, PID_down, PID_up);
      }
	
    
    //std::cout<<"tuuuu"<<std::endl;
    for (Long64_t jentry=0; jentry<treeC->GetEntries(); jentry++)
      {
	treeC->GetEntry(jentry);
	if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true) || type.Contains("DPi") == true || type.Contains("CombPi") == true )
	  {
	    PID3 = -PID3; 
	    lab1_PIDK->setVal(PID3);
	  }
	else
	  {
	    lab1_PIDK->setVal(PID3);
	  }
	Var1->setVal(Var13);
	Var2->setVal(Var23);
	//std::cout<<"Var13: "<<Var13<<" Var23: "<<Var23<<std::endl;
	Int_t binRW = hist->FindBin(Var13,Var23);
	wRW = hist->GetBinContent(binRW);
	wA = nsig_sw3*wRW;
	//std::cout<<" weight: "<<wA<<" nsigSW: "<<nsig_sw3<<" wRW "<<wRW<<" "<<nameVar1<<": "<<Var13<<" "<<nameVar2<<": "<<Var23<<std::endl;
	weights->setVal(wA);
	if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true) || type.Contains("DPi") == true || type.Contains("CombPi") == true)
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
    Int_t histBin = 1;
    RooBinned1DQuinticBase<RooAbsPdf>* pdfPID2 = NULL;
    if ( (type.Contains("BsDsPi") == true && type.Contains("MC") == true) || type.Contains("DPi") == true || type.Contains("CombPi") == true )
      {
	histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(200, PID_down, PID_up)); //45,log(0.0001),log(-PID_down)));
	histBin = 200;
      }
    else
      {
	histPID = dataRW->createHistogram(namehist.Data(),*lab1_PIDK, RooFit::Binning(50,PID_down,PID_up));
	histBin = 50;
      }
    histPID->SetName(namehist.Data());
    histPID->SaveAs("hist_PID.root");
    Double_t zero = 1e-20;
    for(int k = 1; k<histBin; k++)
      {
	Double_t cont = histPID->GetBinContent(k);
	if( cont < zero ) 
	  { 
	    histPID->SetBinContent(k,zero);
	    std::cout<<"[WARNING] Histogram value lower than zero: "<<cont<<". Force Bin content to be: "<<zero<<std::endl; 
	  }
	//else
	//  {
	//    std::cout<<"k: "<<k<<" cont: "<<cont<<std::endl;
	//  }
      }


    pdfPID = NULL;
    if( (type.Contains("MC") == true  && type.Contains("BsDsPi") == true ) || type.Contains("DPi") == true || type.Contains("CombPi") == true)
      {
	if (debug == true) PlotWeightingSample(nn, dataCalib, dataRW, Var1, Var2, lab1_PIDK, bin1, bin2, bin3,
					       type, l2, l3, work, plotSet, debug);
	if ( type.Contains("Pion") == true)
	  {
	    //pdfPID = FitPDFShapeForPIDBsDsPiPi(dataRW, lab1_PIDK, nn,  debug);
	    //work->import(*pdfPID);
	    if (type.Contains("BsDsPi") == true && type.Contains("MC") == true) { nn = "Bs2DsPi_"+sample+"_"+mode; }
	    TString namepdf = "PIDKShape_"+nn;
            pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
            RooAbsPdf* pdfSave = pdfPID2;
            TString t = "";
	    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nn, t, plotSet, debug );
            work->import(*pdfPID2);

	  }
	else
	  {
	    if( type.Contains("CombPi") == true ) { nn = "CombK_"+nm; }
	    TString namepdf = "PIDKShape_"+nn;
	    pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
	    RooAbsPdf* pdfSave = pdfPID2;
	    TString t = "";
	    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nn, t, plotSet, debug );
	    work->import(*pdfPID2);
	    
	    //pdfPID = FitPDFShapeForPIDBsDsPiK(dataRW, lab1_PIDK, nn,  plotSet, debug);
	    //work->import(*pdfPID);
	  }
      }
    else if ( (type.Contains("MC") == true && type.Contains("BsDsK") == true ) || 
	      (type.Contains("MC") != true && type.Contains("BsDsPi") == true) ||
	      type.Contains("CombK") == true)
      {
	TString dir = "PlotBsDsK2D";
        if (debug == true) PlotWeightingSample(nn, dataCalib, dataRW, Var1, Var2, lab1_PIDK, bin1, bin2, bin3,
					       type, l2, l3, work, plotSet, debug);

	if ( type.Contains("Pion") == true)
	  {
	    if( type.Contains("CombK") == true ) { nn = "CombPi_"+nm; }
	    if (type.Contains("BsDsPi") == true && type.Contains("MC") != true) { nn = "Bs2DsPi_"+sample+"_"+mode; }
	    pdfPID = FitPDFShapeForPIDBsDsKPi(dataRW, lab1_PIDK, nn, plotSet, debug);
	    work->import(*pdfPID);
	  }
	else if ( type.Contains("Kaon") == true)
	  {
	    if( type.Contains("CombK") == true ) { nn = "CombK_"+nm; }
	    if (type.Contains("BsDsK") == true && type.Contains("MC") == true) { nn = "Bs2DsK_"+sample+"_"+mode; }
    	    TString namepdf = "PIDKShape_"+nn;
	    pdfPID2= new RooBinned1DQuinticBase<RooAbsPdf>(namepdf.Data(), namepdf.Data(), *histPID, *lab1_PIDK, true);
	    RooAbsPdf* pdfSave = pdfPID2;
	    TString t = "";
	    SaveTemplate( dataRW, pdfSave, lab1_PIDK,  nn, t, plotSet, debug );
	    work->import(*pdfPID2);
	  }
	else
	  {
	    if( type.Contains("CombK") == true ) { nn = "CombP_"+nm; }
	    pdfPID = FitPDFShapeForPIDBsDsKP(dataRW, lab1_PIDK, nn,  plotSet, debug);
	    work->import(*pdfPID);
	  }
      }
    //work->import(*pdfPID);
  
  return work;
}

  RooWorkspace* ObtainPIDShapeFromCalibSampleOneSample(TString& fileCalib, TString& workCalib,
                                                       TString namePID, TString nameVar1, TString nameVar2, TString nameVar3,
                                                       double PID_down, double PID_up,
                                                       double Var1_down, double Var1_up,
                                                       double Var2_down, double Var2_up,
                                                       double Var3_down, double Var3_up,
						       Int_t bin1, Int_t bin2, Int_t bin3,
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

    RooRealVar* Var1 = new RooRealVar(nameVar1.Data(),nameVar1.Data(),log(Var1_down), log(Var1_up));
    RooRealVar* Var2 = new RooRealVar(nameVar2.Data(),nameVar2.Data(),log(Var2_down), log(Var2_up));
    RooRealVar* Var3 = new RooRealVar(nameVar3.Data(),nameVar3.Data(),log(Var3_down), log(Var3_up));
    RooRealVar* lab1_PIDK = new RooRealVar(namePID.Data(), namePID.Data(), PID_down, PID_up);
    	
    
    TString label1, label2, label3;
    if ( nameVar1 != nameVar2 && nameVar1 != nameVar3 && nameVar2 != nameVar3)
      {
	label1 = CheckWeightLabel(nameVar1, debug);
        label2 = CheckWeightLabel(nameVar2, debug);
	label3 = CheckWeightLabel(nameVar3, debug);
      }
    else { if(debug == true) std::cout<<"The same name of variables: "<<nameVar1<<"  "<<nameVar2<<" "<<nameVar3<<std::endl; }

    if(debug == true) std::cout<<nameVar1<<" range: ("<<log(Var1_down)<<","<<log(Var1_up)<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar2<<" range: ("<<log(Var2_down)<<","<<log(Var2_up)<<")"<<std::endl;
    if(debug == true) std::cout<<nameVar3<<" range: ("<<log(Var3_down)<<","<<log(Var3_up)<<")"<<std::endl;

    TString dataName = "data";
    RooWorkspace* workC = LoadWorkspace(fileCalib, workCalib, debug);
    RooDataSet* dataC = GetDataSet(workC, dataName, debug );
    const TTree* treeConst = dataC->tree();
    TTree* treeC = new TTree("name","name"); //     treeConst->CloneTree(0);
    treeC = treeConst->GetTree();
    //treeConst->CopyEntries(treeC);
    Double_t nsig_sw3,PID3,Var13, Var23, Var33;

    TString Par;
    Par = CheckTreeLabel(fileCalib, debug);
    treeC->SetBranchAddress("nsig_sw", &nsig_sw3);
    TString nameDLL = Par+"_CombDLLK";
    treeC->SetBranchAddress(nameDLL.Data(), &PID3);
    TString nVar1 = CheckTreeLabel(fileCalib, nameVar1, debug);
    treeC->SetBranchAddress(nVar1.Data(), &Var13);
    TString nVar2 = CheckTreeLabel(fileCalib, nameVar2, debug);
    treeC->SetBranchAddress(nVar2.Data(), &Var23);
    TString nVar3 = CheckTreeLabel(fileCalib, nameVar3, debug);
    treeC->SetBranchAddress(nVar3.Data(), &Var33);
    treeC->Print();
    Double_t wRW(0), wA(0);
    
    //TString l1 = "MC";
    TString l2 = "Calib";
    TString l3 = "Calib weighted";

    RooDataSet* dataCalib = GetDataCalibSample( fileCalib,  workCalib, Var1, Var2, Var3, plotSet, debug );
    std::cout<<"dataCalib: "<<dataCalib->sumEntries()<<" "<<dataCalib->numEntries()<<std::endl;
    TString histNameCalib = "hist2D_Calib";
    TH3F* histCalib = new TH3F(histNameCalib.Data(),histNameCalib.Data(),
                               bin1,log(Var1_down),log(Var1_up),
                               bin2,log(Var2_down),log(Var2_up),
                               bin3,log(Var3_down),log(Var3_up));
    histCalib = Get3DHist(dataCalib,Var1, Var2, Var3, histCalib, debug);
    Save3DHist(histCalib, plotSet);

    RooAbsPdf* pdfPID;

    TH3F* hist = NULL;
    TH3F* histMC = NULL;

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

    hist = (TH3F*)work->obj(histNameR.Data());
    if ( hist != NULL ) { std::cout<<" Read histogram: "<<hist->GetName()<<std::endl;}
    else {std::cout<<" Cannot read histogram: "<<histName.Data()<<std::endl;}
    histMC = (TH3F*)work->obj(histName.Data());
    
    TString namew = "weights";
    RooRealVar* weights;
    weights = new RooRealVar(namew.Data(), namew.Data(), -50.0, 50.0 );
    //TString nameCalib = "CalibSample_"+nm;
    RooDataSet* dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*lab1_PIDK,*Var1,*Var2,*Var3,*weights), namew.Data());
    
    TH3F* histRW = NULL;
    histName = "hist2D_rw_"+nm;
    histRW = new TH3F(histName.Data(),histName.Data(),
		      bin1,log(Var1_down),log(Var1_up),
		      bin2,log(Var2_down),log(Var2_up),
		      bin3,log(Var3_down),log(Var3_up));

    //std::cout<<"tuuuu"<<std::endl;
    for (Long64_t jentry=0; jentry<treeC->GetEntries(); jentry++)
      {
        treeC->GetEntry(jentry);
        lab1_PIDK->setVal(PID3);
        Var1->setVal(Var13);
        Var2->setVal(Var23);
	Var3->setVal(Var33);
        //std::cout<<"Var13: "<<Var13<<" Var23: "<<Var23<<std::endl;
        Int_t binRW = hist->FindBin(Var13,Var23,Var33);
        wRW = hist->GetBinContent(binRW);
        wA = nsig_sw3*wRW;
        //std::cout<<" weight: "<<wA<<" nsigSW: "<<nsig_sw3<<" wRW "<<wRW<<" "<<nameVar1<<": "<<Var13<<" "<<nameVar2<<": "<<Var23<<std::endl;
        weights->setVal(wA);
        dataRW->add(RooArgSet(*lab1_PIDK,*Var1,*Var2,*Var3,*weights),wA,0);
	histRW->Fill(Var13,Var23,Var33,wA);
      }
    
    if ( dataRW != NULL  ){
      std::cout<<"[INFO] ==> Create "<<dataRW->GetName()<<std::endl;
      std::cout<<" number of entries in data set: "<<dataRW->numEntries()<<" with the sum: "<<dataRW->sumEntries()<<std::endl;
    } else { std::cout<<"Error in create dataset"<<std::endl; }

    Int_t binPIDK = 50;
    TString nn;
    if( type.Contains("Comb") == true) { nn = "Comb_"+nm; }
    else if (type.Contains("DPi") == true) { nn = "DPi_"+nm;}
    else {nn=nm;}

    pdfPID = NULL;
    if( (type.Contains("MC") == true  && type.Contains("BsDsPi") == true ) || type.Contains("DPi") == true || type.Contains("CombPi") == true)
      {
	PlotWeightingSample(nn, dataCalib, dataRW, Var1, Var2, Var3, lab1_PIDK,
			    bin1, bin2, bin3, binPIDK, type, l2, l3, work, plotSet, debug);

        if ( type.Contains("Pion") == true)
          {
            pdfPID = FitPDFShapeForPIDBsDsPiPi(dataRW, lab1_PIDK, nn,  plotSet, debug);
          }
        else
          {
            pdfPID = FitPDFShapeForPIDBsDsPiK(dataRW, lab1_PIDK, nn, plotSet, debug);
          }
      }
    else if ( (type.Contains("MC") == true && type.Contains("BsDsK") == true) 
	      || (type.Contains("MC") != true && type.Contains("BsDsPi") == true) ||
	      type.Contains("CombK") == true)
      {
        
	PlotWeightingSample(nn, dataCalib, dataRW, Var1, Var2, Var3, lab1_PIDK,
			    bin1, bin2, bin3, binPIDK, type, l2, l3,  work, plotSet, debug);

        if ( type.Contains("Pion") == true)
          {
            pdfPID = FitPDFShapeForPIDBsDsKPi(dataRW, lab1_PIDK, nn, plotSet, debug);
          }
        else if ( type.Contains("Kaon") == true)
          {
            pdfPID = FitPDFShapeForPIDBsDsKK(dataRW, lab1_PIDK, nn, plotSet, debug);

          }
        else
          {
            pdfPID = FitPDFShapeForPIDBsDsKP(dataRW, lab1_PIDK, nn, plotSet, debug);
          }
      }
    work->import(*pdfPID);

    return work;
  }

  RooWorkspace* ObtainPIDShapeFromCalibSampleOneSample(MDFitterSettings* md,
                                                       TString& type,
                                                       RooWorkspace* work,
                                                       PlotSettings* plotSet,
                                                       bool debug)

  {
    
    TString fileCalib = "";
    TString workCalib = "";

    TString bach = CheckBachelor(type, debug);
    TString pol = CheckPolarity(type, debug);

    if ( bach == "Pi" )
      {
        if ( pol == "up" ) { fileCalib = md->GetCalibPionUp(); } else { fileCalib = md->GetCalibPionDown(); }
        workCalib = md->GetCalibPionWorkName();
      }
    else if ( bach == "K" )
      {
        if ( pol == "up" ) { fileCalib = md->GetCalibKaonUp(); } else { fileCalib = md->GetCalibKaonDown(); }
        workCalib = md->GetCalibKaonWorkName();
      }
    else if ( bach == "P" )
      {
        if ( pol == "up" ) { fileCalib = md->GetCalibProtonUp(); } else { fileCalib = md->GetCalibProtonDown(); }
	workCalib = md->GetCalibProtonWorkName();
      }

    if( md->GetWeightingDim() == 2 )
      {
	work = ObtainPIDShapeFromCalibSampleOneSample(fileCalib, workCalib,
						      md->GetPIDKVar(), md->GetVar(0), md->GetVar(1),
						      md->GetPIDKRangeDown(), md->GetPIDKRangeUp(),
						      md->GetRangeDown(md->GetVar(0)), md->GetRangeUp(md->GetVar(0)),
						      md->GetRangeDown(md->GetVar(1)), md->GetRangeUp(md->GetVar(1)),
						      md->GetBin(0), md->GetBin(1),
						      type,
						      work,
						      plotSet,
						      debug);

      }
    else
      {
	work = ObtainPIDShapeFromCalibSampleOneSample(fileCalib, workCalib,
                                                      md->GetPIDKVar(), md->GetVar(0), md->GetVar(1), md->GetVar(1),
                                                      md->GetPIDKRangeDown(), md->GetPIDKRangeUp(),
                                                      md->GetRangeDown(md->GetVar(0)), md->GetRangeUp(md->GetVar(0)),
                                                      md->GetRangeDown(md->GetVar(1)), md->GetRangeUp(md->GetVar(1)),
						      md->GetRangeDown(md->GetVar(2)), md->GetRangeUp(md->GetVar(2)),
                                                      md->GetBin(0), md->GetBin(1), md->GetBin(2),
                                                      type,
                                                      work,
                                                      plotSet,
                                                      debug);

      }
    
    return work;
    
  }
  
  TH1* GetHist(RooDataSet* data, RooRealVar* obs, Int_t bin, bool debug)
  {
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
