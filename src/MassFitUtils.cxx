//---------------------------------------------------------------------------//
//                                                                           //
//  General utilities                                                        //
//                                                                           //
//  Source file                                                              //
//                                                                           //
//  Authors: Agnieszka Dziurda, Eduardo Rodrigues                            //
//  Date   : 12 / 04 / 2012                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

// STL includes
#include <cmath>
#include <string>
#include <vector>
#include <fstream>
#include <stdexcept>
#include <algorithm>

#include "B2DXFitters/icc_fpclass_workaround.h"

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
#include "RooArgSet.h"
#include "RooPlot.h"
#include "RooNLLVar.h"
#include "RooMinuit.h"
#include "RooFitResult.h"
#include "TH2F.h"
#include "TRandom3.h"
#include "RooHistPdf.h"
#include "RooDataHist.h"
#include "RooCategory.h"
// B2DXFitters includes
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/MassFitUtils.h"
#include "B2DXFitters/KinHack.h"
#include "B2DXFitters/DecayTreeTupleSucksFitter.h"

#define DEBUG(COUNT, MSG)				   \
  std::cout << "SA-DEBUG: [" << COUNT << "] (" << __func__ << ") " \
  << MSG << std::endl; \
  COUNT++;

#define ERROR(COUNT, MSG) \
  std::cerr << "SA-ERROR: [" << COUNT << "] (" << __func__ << ") " \
  << MSG << std::endl; \
  COUNT++;

using namespace GeneralUtils;

namespace MassFitUtils {

  
  //===========================================================================
  // Obtain data set 
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // PIDcut - cut for bachelor particle (depends of mode) 
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar - name of mass observable (for example lab0_MM)
  // tVar - name of time observable
  // tagVar - name of tag observable
  // tagOmegaVar - name of mistag observable
  // idVar - name of id observable 
  // mProbVar - variable using in PID cut (for example lab1_PIDK) 
  // mode - mode of decay
  // tagtool - add to workspace RooHistPdf with mistag distribution
  // workspace - workspace where data set should be saved  
  //==========================================================================

  RooWorkspace* ObtainData(TString& filesDir, TString& sig,
			   int PIDcut, 
			   double Pcut_down, double Pcut_up,
			   double BDTGCut,
			   double Dmass_down, double Dmass_up,
			   double Bmass_down, double Bmass_up,
			   double time_down, double time_up,
			   TString& mVar, 
			   TString& tVar,
			   TString& tagVar,
			   TString& tagOmegaVar,
			   TString& idVar,
			   TString& mProbVar,
			   TString& mode,
			   Bool_t tagtool,
			   RooWorkspace* workspace, 
			   bool debug)
  {
  
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainData(...). Start preparing DataSet "<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"PIDK cut: "<< PIDcut<<std::endl;
	std::cout<<"BDTGResponse cut: "<<BDTGCut<<std::endl;
	std::cout<<"Bachelor momentum range: ("<<Pcut_down<<","<<Pcut_up<<")"<<std::endl;
	std::cout<<"D(s) mass range: ("<<Dmass_down<<","<<Dmass_up<<")"<<std::endl;
	std::cout<<"Name of mass observable: "<<mVar<<std::endl;
	std::cout<<"Name of time observable: "<<tVar<<std::endl;
	std::cout<<"Name of tag observable: "<<tagVar<<std::endl;
	std::cout<<"Name of mistag observable: "<<tagOmegaVar<<std::endl;
	std::cout<<"Name of id observable: "<<idVar<<std::endl;
	std::cout<<"Name of PID  observable: "<<mProbVar<<std::endl;
	std::cout<<"Mode: "<<mode<<std::endl;
	std::cout<<"Tagtool: "<<tagtool<<std::endl;
      }
	
    double BMassRange[2];
    BMassRange[0] = Bmass_down; BMassRange[1]=Bmass_up;
    if ( debug == true)
      {
	std::cout<<"B(s) mass range: ("<<BMassRange[0]<<","<<BMassRange[1]<<")"<<std::endl;
	std::cout<<"B(s) time range: ("<<time_down<<","<<time_up<<")"<<std::endl;
      }
    RooWorkspace* work = NULL;
    if (workspace == NULL ) { work =  new RooWorkspace("workspace","workspace"); }
    else { work = workspace; }

    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);
    RooRealVar* lab0_TAU = new RooRealVar(tVar.Data(),tVar.Data(), time_down, time_up);
    RooRealVar* lab0_TAG = new RooRealVar(tagVar.Data(),tagVar.Data(),-2,2);
    RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,1.); 
    RooRealVar* lab1_ID = new RooRealVar(idVar.Data(),idVar.Data(),-1000,1000); 

    TString tagsskaonVar, tagosmuonVar, tagoselectronVar, tagoskaonVar, tagvtxchargeVar, pVar, ptVar;
    if( tagtool == true )
      {
	std::cout<<"[INFO] TagTool added"<<std::endl;
	tagsskaonVar      = "lab0_BsTaggingTool_SS_Kaon_PROB";
	tagosmuonVar      = "lab0_BsTaggingTool_OS_Muon_PROB";
	tagoselectronVar  = "lab0_BsTaggingTool_OS_Electron_PROB";
	tagoskaonVar      = "lab0_BsTaggingTool_OS_Kaon_PROB";
	tagvtxchargeVar   = "lab0_BsTaggingTool_VtxCharge_PROB";
	pVar              = "lab1_P";
	ptVar             = "lab1_PT";
      }
    
    RooRealVar* lab0_TAG_SS_Kaon=NULL;
    RooRealVar* lab0_TAG_OS_Muon=NULL;
    RooRealVar* lab0_TAG_OS_Electron=NULL;
    RooRealVar* lab0_TAG_OS_Kaon=NULL;
    RooRealVar* lab0_TAG_VtxCharge=NULL;
    RooRealVar* lab1_P=NULL;
    RooRealVar* lab1_PT=NULL;

    if ( tagtool == true )
      {
	lab0_TAG_SS_Kaon = new RooRealVar(tagsskaonVar.Data(), tagsskaonVar.Data(), -3., 1.);
	lab0_TAG_OS_Muon = new RooRealVar(tagosmuonVar.Data(), tagosmuonVar.Data(), -3., 1.);
	lab0_TAG_OS_Electron = new RooRealVar(tagoselectronVar.Data(),tagoselectronVar.Data(),-3.,1.);
	lab0_TAG_OS_Kaon = new RooRealVar(tagoskaonVar.Data(),tagoskaonVar.Data(),-3.,1.);
	lab0_TAG_VtxCharge = new RooRealVar(tagvtxchargeVar.Data(), tagvtxchargeVar.Data(), -3.,1.);
	lab1_P = new RooRealVar(pVar.Data(),pVar.Data(),0,1800000);
	lab1_PT = new RooRealVar(ptVar.Data(),ptVar.Data(),0,1800000);
      }
    std::vector <std::string> FileName;

    ReadOneName(filesDir,FileName,sig, debug);
    
    TTree* tree[2];
    
    for( int i=0; i<2; i++)
      {
	tree[i] = NULL;
        tree[i] = ReadTreeData(FileName,i, debug);
      }

    // Read sample (means down or up)  from path // 
    // Read mode (means D mode: kkpi, kpipi or pipipi) from path //
    TString smp[2], md[2];

    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
      md[i-1] = CheckDMode(FileName[i], debug);
    }

    //Set PID cut depends on mode// 
    TCut PID_cut;  
    if( mode.Contains("Pi") ) { PID_cut = Form("%s < %d",mProbVar.Data(),PIDcut); if ( debug == true)  std::cout<<"Mode with Pi"<<std::endl;}
    else if (mode.Contains("K")) { PID_cut = Form("%s > %d",mProbVar.Data(),PIDcut);  if ( debug == true)  std::cout<<"Mode with K"<<std::endl; }
    else { if ( debug == true) std::cout<<"[ERROR] Wrong mode"; return work; }

    //Set other cuts//
    TCut P_cut = Form("lab1_P > %f && lab1_P < %f",Pcut_down,Pcut_up);
    TCut BDTG_cut = Form("BDTGResponse_1 > %f",BDTGCut);
    TCut mass_cut = Form("%s > %f && %s < %f",mVar.Data(),BMassRange[0],mVar.Data(),BMassRange[1]);
    TCut massD_cut = Form("lab2_MM > %f %% lab2_MM < %f",Dmass_down,Dmass_up);
    
    TCut All_cut = PID_cut&&P_cut&&BDTG_cut&&mass_cut&&massD_cut;

    RooDataSet*  dataSet[2];
    RooDataSet*  dataSetTagTool[2];

    // Create Data Set //
    for (int i = 0; i< 2; i++){
		TString name = "dataSet"+mode+"_"+smp[i]+"_"+md[i];
		TString nametagtool = "dataSetTagTool"+mode+"_"+smp[i]+"_"+md[i];
		if( tagtool == true )
		  {
		    dataSetTagTool[i] = new RooDataSet(nametagtool.Data(),nametagtool.Data(),RooArgSet(*lab0_MM,
												       *lab0_TAG_SS_Kaon, 
												       *lab0_TAG_OS_Muon, 
												       *lab0_TAG_OS_Electron, 
												       *lab0_TAG_OS_Kaon, 
												       *lab0_TAG_VtxCharge, 
												       *lab1_P,
												       *lab1_PT));
		  }
		dataSet[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MM,*lab0_TAU,*lab0_TAG,*lab0_TAGOMEGA,*lab1_ID));
		
		TTree* treetmp=NULL;
		treetmp = TreeCut(tree[i],All_cut,smp[i],mode, debug);
	
		Float_t lab0_MM3,lab0_TAU3,lab0_TAG3,lab0_TAGOMEGA3,lab1_ID3;
		treetmp->SetBranchAddress(mVar.Data(), &lab0_MM3);
		treetmp->SetBranchAddress(tVar.Data(),&lab0_TAU3);
		treetmp->SetBranchAddress(tagVar.Data(),&lab0_TAG3);
		treetmp->SetBranchAddress(tagOmegaVar.Data(),&lab0_TAGOMEGA3);
		treetmp->SetBranchAddress(idVar.Data(),&lab1_ID3);
	
		Float_t lab0_TAG_SS_Kaon3, lab0_TAG_OS_Muon3, lab0_TAG_OS_Electron3, lab0_TAG_OS_Kaon3, lab0_TAG_VtxCharge3;
		Float_t lab1_P3, lab1_PT3;
		if ( tagtool == true )
		  {
		    treetmp->SetBranchAddress(tagsskaonVar.Data(),&lab0_TAG_SS_Kaon3);
		    treetmp->SetBranchAddress(tagosmuonVar.Data(),&lab0_TAG_OS_Muon3);
		    treetmp->SetBranchAddress(tagoselectronVar.Data(),&lab0_TAG_OS_Electron3);
		    treetmp->SetBranchAddress(tagoskaonVar.Data(),&lab0_TAG_OS_Kaon3);
		    treetmp->SetBranchAddress(tagvtxchargeVar.Data(),&lab0_TAG_VtxCharge3);
		    treetmp->SetBranchAddress(pVar.Data(), &lab1_P3);
		    treetmp->SetBranchAddress(ptVar.Data(), &lab1_PT3);
		  }

		//Float_t m;
		for (Long64_t jentry=0; jentry<treetmp->GetEntries(); jentry++) {
		  treetmp->GetEntry(jentry);
		  //m = lab0_MM3;
		  lab0_MM->setVal(lab0_MM3);
		  lab0_TAU->setVal(lab0_TAU3);
		  lab0_TAG->setVal(lab0_TAG3);
		  lab0_TAGOMEGA->setVal(lab0_TAGOMEGA3);
		  lab1_ID->setVal(lab1_ID3);  
		  if (tagtool == true )
		    {
		      lab0_TAG_SS_Kaon->setVal(lab0_TAG_SS_Kaon3);
		      lab0_TAG_OS_Muon->setVal(lab0_TAG_OS_Muon3);
		      lab0_TAG_OS_Electron->setVal(lab0_TAG_OS_Electron3);
		      lab0_TAG_OS_Kaon->setVal(lab0_TAG_OS_Kaon3);
		      lab0_TAG_VtxCharge->setVal(lab0_TAG_VtxCharge3);
		      lab1_P->setVal(lab1_P3);
		      lab1_PT->setVal(lab1_PT3);
		      dataSetTagTool[i]->add(RooArgSet(*lab0_MM,*lab0_TAG_SS_Kaon, *lab0_TAG_OS_Muon, *lab0_TAG_OS_Electron,
						       *lab0_TAG_OS_Kaon, *lab0_TAG_VtxCharge, *lab1_P, *lab1_PT));
		    }
		  dataSet[i]->add(RooArgSet(*lab0_MM,*lab0_TAU,*lab0_TAG,*lab0_TAGOMEGA,*lab1_ID));
		  
		}
	 
		if ( debug == true)
		  {
		    if ( dataSet != NULL  ){
		      std::cout<<"[INFO] ==> Create "<<dataSet[i]->GetName()<<std::endl;
		      std::cout<<"Sample "<<smp[i]<<" number of entries: "<<tree[i]->GetEntries()<<" in data set: "<<dataSet[i]->numEntries()<<std::endl;
		    } else { std::cout<<"Error in create dataset"<<std::endl; }
		  }

		TString s = smp[i]+"_"+md[i];
		SaveDataSet(dataSet[i], lab0_MM, s, mode, debug);
		saveDataTemplateToFile( dataSet[i], NULL, lab0_MM,
				      mode.Data(), "root", s.Data(), debug );
		work->import(*dataSet[i]);
		if ( tagtool == true )
		  {
		    work->import(*dataSetTagTool[i]);
		  }

    }
    return work;
    
  }

  

  //==========================================================================
  // Obtain Bs->DsPi under Bs->DsK
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // PIDcut - cut for bachelor particle (depends of mode)
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  // workspace - workspace where data set should be saved
  //==========================================================================

  
  RooWorkspace* ObtainMissForBsDsK(TString& filesDir, TString& sig,
				   int PIDmisscut,
				   double Pcut_down, double Pcut_up,
				   double BDTGCut,
				   double Dmass_down, double Dmass_up,  
				   double Bmass_down, double Bmass_up,
				   TString& mVar, TString& mProbVar,
				   TString& mode,
				   RooWorkspace* workspace, Bool_t mistag, bool debug)
  {
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainMissForBsDsK(...). Obtain Bs->DsPi under Bs->DsK  "<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"PIDK cut: "<< PIDmisscut<<std::endl;
	std::cout<<"BDTGResponse cut: "<<BDTGCut<<std::endl;
	std::cout<<"Bachelor momentum range: ("<<Pcut_down<<","<<Pcut_up<<")"<<std::endl;
	std::cout<<"D(s) mass range: ("<<Dmass_down<<","<<Dmass_up<<")"<<std::endl;
	std::cout<<"Name of observable: "<<mVar<<std::endl;
	std::cout<<"Name of PID variable: "<<mProbVar<<std::endl;
	std::cout<<"Mode: "<<mode<<std::endl;
      }

    double BMassRange[2];
    BMassRange[0] = Bmass_down;  BMassRange[1]=Bmass_up;
    if ( debug == true)
      {
	std::cout<<"B(s) mass range: ("<<BMassRange[0]<<","<<BMassRange[1]<<")"<<std::endl;
      }
    
    RooWorkspace* work = NULL;
    if (workspace == NULL ) { work =  new RooWorkspace("workspace","workspace"); }
    else { work = workspace; }

    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);
    TString tagOmegaVar = "lab0_BsTaggingTool_TAGOMEGA_OS";
    TString tagName = "lab0_BsTaggingTool_TAGDECISION_OS";
    RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,0.,0.6);
    lab0_TAGOMEGA->setBins(30);
    
    std::vector <std::string> FileName;
    std::vector <std::string> FileNamePID;
    std::vector <std::string> FileNamePID2;

    TString PID = "#PID";
    TString PID2 = "#PID2";
    ReadOneName(filesDir,FileName,sig,debug);
    ReadOneName(filesDir,FileNamePID,PID,debug);
    ReadOneName(filesDir,FileNamePID2,PID2,debug);
  
    TTree* tree[2];

    for( int i=0; i<2; i++)
      {
	tree[i] = NULL;
	tree[i] = ReadTreeData(FileName,i,debug);
      }

    // Read sample (means down or up)  from path //
    // Read mode (means D mode: kkpi, kpipi or pipipi) from path //
    TString smp[2], md[2];

    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
      md[i-1] = CheckDMode(FileName[i], debug);
    }

    //Read necessary misID histograms from file// 
    TH1F* heffmiss1[2];
    TH1F* heffmiss2[2];
    TH1F* heffmiss[2];
    TString namehist;
    for( int i = 0; i<2; i++ )
      {
	heffmiss1[i]=NULL; 
	namehist = Form("MyPionMisID_%d;1",PIDmisscut);
	heffmiss1[i] = ReadPIDHist(FileNamePID,namehist,i,debug);
	heffmiss2[i]=NULL;
	heffmiss2[i] = ReadPIDHist(FileNamePID2,namehist,i,debug);
      }
    
    Double_t histent1[2];
    Double_t histent2[2];
    histent1[1] = 5092049.0;
    histent1[0] = 6883094.0;
    histent2[1] = 5866006.0;
    histent2[0] = 9122416.0;
    for (int i = 0; i<2; i++)
      {
	heffmiss[i]=NULL;
	heffmiss[i]=AddHist(heffmiss1[i],  histent1[i], heffmiss2[i], histent2[i],debug);
      }

    //Set cuts//
    TCut PID_cut;
    PID_cut = Form("%s < %d",mProbVar.Data(),PIDmisscut);  
    TCut P_cut = Form("lab1_P > %f && lab1_P < %f",Pcut_down,Pcut_up);
    TCut BDTG_cut = Form("BDTGResponse_1 > %f",BDTGCut);
    TCut mass_cut = Form(" %s > 5300 && %s < 5420",mVar.Data(),mVar.Data());
  

    TCut All_cut = mass_cut&&P_cut&&BDTG_cut&&PID_cut;
  

    RooRealVar* weights[2];
    RooDataSet* dataSet[2];
    RooDataHist* dataHist[2];
    TTree* treetmp[2];
    RooKeysPdf* pdfDataMiss[2];
  

    for (int i = 0; i<2; i++){
      
      TString s = smp[i]+"_"+md[i];
      
      dataSet[i] = NULL;
      dataHist[i] = NULL;
      pdfDataMiss[i] = NULL;
      treetmp[i] = NULL;
      
      TString namew = "weights_Miss_"+smp[i];
      weights[i] = new RooRealVar(namew.Data(), namew.Data(), 0.0, 1.0 );  // create weights //

      TString name = "dataSet_Miss_"+s;
      TString namehist ="data_mistag_"+s;
      //dataSet[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MM,*weights[i]),namew.Data());  // create data set //

      if( mistag == true)
        {
          dataHist[i] = new RooDataHist(namehist.Data(),namehist.Data(),RooArgSet(*lab0_TAGOMEGA)); //create new data set /
        }
      dataSet[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MM,*weights[i]),namew.Data()); //create new data set //
        


      treetmp[i] = TreeCut(tree[i],All_cut, smp[i], mode, debug);  // obtain new tree after applied all cuts //


      // Load all necessary variables to change hypo Pi->K from tree //
      Float_t lab1_P3, lab2_P3;
      Float_t lab1_PX3, lab1_PY3, lab1_PZ3;
      Float_t lab2_PX3, lab2_PY3, lab2_PZ3;
      Float_t lab2_MM3;

      Float_t masshypo;
      Double_t w;
      
      treetmp[i]->SetBranchAddress("lab1_P",  &lab1_P3);
      treetmp[i]->SetBranchAddress("lab1_PX", &lab1_PX3);
      treetmp[i]->SetBranchAddress("lab1_PY", &lab1_PY3);
      treetmp[i]->SetBranchAddress("lab1_PZ", &lab1_PZ3);
      
      treetmp[i]->SetBranchAddress("lab2_P",  &lab2_P3);
      treetmp[i]->SetBranchAddress("lab2_PX", &lab2_PX3);
      treetmp[i]->SetBranchAddress("lab2_PY", &lab2_PY3);
      treetmp[i]->SetBranchAddress("lab2_PZ", &lab2_PZ3);
      
      treetmp[i]->SetBranchAddress("lab2_MM", &lab2_MM3);

      Float_t lab0_TAGOMEGA2, tag;
      if (mistag == true )
	{
	  treetmp[i]->SetBranchAddress(tagOmegaVar.Data(),&lab0_TAGOMEGA2);
	  treetmp[i]->SetBranchAddress(tagName.Data(), &tag);
	}

      
      for (Long64_t jentry=0; jentry<treetmp[i]->GetEntries(); jentry++) {
	treetmp[i]->GetEntry(jentry);
	Int_t bin;
	
	masshypo = (Float_t)sqrt(pow(sqrt(pow(493.677,2)+pow(lab1_P3,2))+sqrt(pow(lab2_MM3,2)+pow(lab2_P3,2)),2)
				 -pow(lab1_PX3+lab2_PX3,2)
				 -pow(lab1_PY3+lab2_PY3,2)
				 -pow(lab1_PZ3+lab2_PZ3,2)); // change hypo Pi->K

	//std::cout<<"mass: "<<masshypo<<std::endl;
	if (masshypo > BMassRange[0] && masshypo < BMassRange[1]) {  // accept event only is in range, usually 5100,5800 // 
	  bin = heffmiss[i]->FindBin(lab1_P3);  //reweight momentum of bachelor
	  w = heffmiss[i]->GetBinContent(bin);
	  weights[i]->setVal(w);
	  lab0_MM->setVal(masshypo);
	  //	  dataSet[i]->add(RooArgSet(*lab0_MM,*weights[i]),w,0);  // add event to data set //
	  if( mistag == true)
	    {
	      //std::cout<<"mistag: "<<lab0_TAGOMEGA2<<std::endl;
	      if ( tag != 0 && lab0_TAGOMEGA2 < 0.495)
		{
		  //std::cout<<"omega: "<<lab0_TAGOMEGA2<<" tag: "<<tag<<" mass: "<<mass<<std::endl;
		  lab0_TAGOMEGA->setVal(lab0_TAGOMEGA2);
		  dataHist[i]->add(RooArgSet(*lab0_TAGOMEGA));
		}
	    }
	  dataSet[i]->add(RooArgSet(*lab0_MM,*weights[i]),w,0);
	  

	}
      }
      
      if ( debug == true)
	{
	  if ( dataSet[i] != NULL ){
	    std::cout<<"[INFO] ==> Create dataSet for missID BsDsPi background"<<std::endl;
	    std::cout<<"Number of events in dataSet: "<<dataSet[i]->numEntries()<<std::endl;
	  } else { std::cout<<"Error in create dataset"<<std::endl; }
	
	  if( mistag == true)
	    {
	      if ( dataHist[i] != NULL ){
		std::cout<<"[INFO] ==> Create dataHist for missID BsDsPi background"<<std::endl;
		std::cout<<"Number of events in dataSet: "<<dataHist[i]->numEntries()<<std::endl;
	      } else { std::cout<<"Error in create dataset"<<std::endl; }
	      
	    }
	}
      // create RooKeysPdf for misID background //
      name="PhysBkgBsDsPi_m_"+s;
      pdfDataMiss[i] = new RooKeysPdf(name.Data(),name.Data(),*lab0_MM,*dataSet[i]);
      if ( debug == true) 
	{
	  if( pdfDataMiss[i] != NULL ){ std::cout<<"=====> Create RooKeysPdf for misID BsDsPi: "<<pdfDataMiss[i]->GetName()<<std::endl;}
	  else { std::cout<<"Cannot create RooKeysPdf for BsDsPi under BsDsK."<<std::endl;}
	}
      SaveTemplate(dataSet[i], pdfDataMiss[i], lab0_MM,s,mode,debug);
      saveDataTemplateToFile( dataSet[i], pdfDataMiss[i], lab0_MM,
			      mode.Data(), "root", s.Data(), debug );
      
      work->import(*pdfDataMiss[i]);
      if (mistag == true)
        {
	  
          TString namepdf ="PhysBkg"+mode+"Pdf_m_"+s+"_mistag";
	  RooHistPdf* pdf = NULL;
	  pdf = new RooHistPdf(namepdf.Data(), namepdf.Data(), RooArgSet(*lab0_TAGOMEGA), *dataHist[i]);

	  TString mdd = s+"_mistag";
          SaveTemplateHist(dataHist[i], pdf, lab0_TAGOMEGA, mdd,mode, debug);
          work->import(*pdf);
        }

    }
    return work;

  }

  //===========================================================================
  // Obtain Bd->DPi under Bs->DsPi
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // PIDcut - cut for bachelor particle (depends of mode)
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  // workspace - workspace where data set should be saved
  //==========================================================================


  RooWorkspace* ObtainMissForBsDsPi(TString& filesDir, TString& sig,
				    int PIDmisscut,
				    double Pcut_down, double Pcut_up,
				    double BDTGCut,
				    double Dmass_down, double Dmass_up,
				    double Bmass_down, double Bmass_up,
				    TString& mVar, TString& mProbVar,
				    TString& mode,
				    RooWorkspace* workspace, Bool_t mistag, bool debug)
  {
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainMissForBsDsK(...). Obtain Bs->DsPi under Bs->DsK  "<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"PIDK cut: "<< PIDmisscut<<std::endl;
	std::cout<<"BDTGResponse cut: "<<BDTGCut<<std::endl;
	std::cout<<"Bachelor momentum range: ("<<Pcut_down<<","<<Pcut_up<<")"<<std::endl;
	std::cout<<"D(s) mass range: ("<<Dmass_down<<","<<Dmass_up<<")"<<std::endl;
	std::cout<<"Name of observable: "<<mVar<<std::endl;
	std::cout<<"Name of PID variable: "<<mProbVar<<std::endl;
	std::cout<<"Mode: "<<mode<<std::endl;
      }
    
    double BMassRange[2];
    BMassRange[0] = Bmass_down; BMassRange[1]=Bmass_up;
    if ( debug == true) std::cout<<"B(s) mass range: ("<<BMassRange[0]<<","<<BMassRange[1]<<")"<<std::endl;

    RooWorkspace* work = NULL;
    if (workspace == NULL ) { work =  new RooWorkspace("workspace","workspace"); }
    else { work = workspace; }
    
    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);
    TString tagOmegaVar = "lab0_BdTaggingTool_TAGOMEGA_OS";
    TString tagName = "lab0_BdTaggingTool_TAGDECISION_OS";
    RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,0.,0.6);
    lab0_TAGOMEGA->setBins(30);

    
    std::vector <std::string> FileName;
    std::vector <std::string> FileNamePID;
    std::vector <std::string> FileNamePID2;

    TString PID = "#PID";
    TString PID2 = "#PID2";
    ReadOneName(filesDir,FileName,sig,debug);
    ReadOneName(filesDir,FileNamePID,PID,debug);
    ReadOneName(filesDir,FileNamePID2,PID2,debug);
    
    TTree* tree[2];
    
    for( int i=0; i<2; i++)
      {
	tree[i] = NULL;
	tree[i] = ReadTreeData(FileName,i,debug);
      }

    // Read sample (means down or up)  from path //
    // Read mode (means D mode: kkpi, kpipi or pipipi) from path //
    TString smp[2], md[2];

    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
      md[i-1] = CheckDMode(FileName[i], debug);
    }

   
   //Read necessary misID histograms from file//
    TH1F* heffmiss1[2];
    TH1F* heffmiss2[2];
    TH1F* heffmiss[2];
    TString namehist;
    for( int i = 0; i<2; i++ )
      {
	heffmiss1[i]=NULL;
        namehist = Form("MyPionMisID_%d;1",PIDmisscut);
	heffmiss1[i] = ReadPIDHist(FileNamePID,namehist,i,debug);
        heffmiss2[i]=NULL;
        heffmiss2[i] = ReadPIDHist(FileNamePID2,namehist,i,debug);
      }


    Double_t histent1[2];
    Double_t histent2[2];
    histent1[1] = 5092049.0;
    histent1[0] = 6883094.0;
    histent2[1] = 5866006.0;
    histent2[0] = 9122416.0;
    for (int i = 0; i<2; i++)
      {
	heffmiss[i]=NULL;
	heffmiss[i]=AddHist(heffmiss1[i],  histent1[i], heffmiss2[i], histent2[i], debug);
      }

    
    //Set cuts//
    TCut PID_cut;
    PID_cut = Form("%s < %d",mProbVar.Data(),PIDmisscut);  
    TCut P_cut = Form("lab1_P > %f && lab1_P < %f",Pcut_down,Pcut_up);
    TCut BDTG_cut = Form("BDTGResponse_1 > %f",BDTGCut);
    TCut mass_cut = Form("%s > 5200 && %s < 5340",mVar.Data(),mVar.Data());
    
    TCut All_cut = mass_cut&&P_cut&&BDTG_cut&&PID_cut;
    
    RooRealVar* weights[2];
    RooDataSet* dataSet[2];
    RooDataHist* dataHist[2];
    TTree* treetmp[2];
    RooKeysPdf* pdfDataMiss[2];
    
    Double_t tmpc[2];
    Int_t bin=0;
    Float_t w=0.0;
    
    for (int i = 0; i<2; i++){
      tmpc[i]=0;
      TString s = smp[i]+"_"+md[i];
      
      dataSet[i] = NULL;
      dataHist[i] = NULL;
      weights[i]=NULL;
      
      treetmp[i] = NULL;
      
      TString namew = "weights_Miss_"+s;
      weights[i] = new RooRealVar(namew.Data(), namew.Data(), 0.0, 1.0 ); // create weights //
      
      TString name = "dataSet_Miss_"+s;
      TString namehist ="data_mistag_"+s;
      
      if( mistag == true)
	{
          dataHist[i] = new RooDataHist(namehist.Data(),namehist.Data(),RooArgSet(*lab0_TAGOMEGA)); //create new data hist /
	}
      dataSet[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MM,*weights[i]),namew.Data()); //create new data set //

      treetmp[i] = TreeCut(tree[i],All_cut,smp[i],md[i],debug);  // obtain new tree after applied all cuts //
      
      // Load all necessary variables to change hypo D->Ds from tree //
      Float_t lab1_P2;
      Float_t lab1_PX2, lab1_PY2, lab1_PZ2;
      Float_t lab3_PX2, lab3_PY2, lab3_PZ2;
      Float_t lab4_PX2, lab4_PY2, lab4_PZ2;
      Float_t lab5_PX2, lab5_PY2, lab5_PZ2;
      Float_t lab1_M2;
      Float_t masshypo, phypo, masshypod;
      Float_t lab0_TAGOMEGA2,tag;

      treetmp[i]->SetBranchAddress("lab1_P",  &lab1_P2);
      treetmp[i]->SetBranchAddress("lab1_PX", &lab1_PX2);
      treetmp[i]->SetBranchAddress("lab1_PY", &lab1_PY2);
      treetmp[i]->SetBranchAddress("lab1_PZ", &lab1_PZ2);
      treetmp[i]->SetBranchAddress("lab1_M", &lab1_M2);
      
      treetmp[i]->SetBranchAddress("lab3_PX", &lab3_PX2);
      treetmp[i]->SetBranchAddress("lab3_PY", &lab3_PY2);
      treetmp[i]->SetBranchAddress("lab3_PZ", &lab3_PZ2);
      
      treetmp[i]->SetBranchAddress("lab4_PX", &lab4_PX2);
      treetmp[i]->SetBranchAddress("lab4_PY", &lab4_PY2);
      treetmp[i]->SetBranchAddress("lab4_PZ", &lab4_PZ2);
      
      treetmp[i]->SetBranchAddress("lab5_PZ",  &lab5_PZ2);
      treetmp[i]->SetBranchAddress("lab5_PX", &lab5_PX2);
      treetmp[i]->SetBranchAddress("lab5_PY", &lab5_PY2);

      if (mistag == true )
	{
	  treetmp[i]->SetBranchAddress(tagOmegaVar.Data(),&lab0_TAGOMEGA2);
	  treetmp[i]->SetBranchAddress(tagName.Data(), &tag);
	}

      
      for (Long64_t jentry=0; jentry<treetmp[i]->GetEntries(); jentry++) {
	treetmp[i]->GetEntry(jentry);
	//std::cout<<"3: "<<lab3_PX2<<" "<<lab3_PY2<<" "<<lab3_PZ2<<std::endl;
	//std::cout<<"4: "<<lab4_PX2<<" "<<lab4_PY2<<" "<<lab4_PZ2<<std::endl;
	//std::cout<<"5: "<<lab5_PX2<<" "<<lab5_PY2<<" "<<lab5_PZ2<<std::endl;
	
	TLorentzVector v3, v4, v5;
	v3.SetPx(lab3_PX2); v4.SetPx(lab4_PX2); v5.SetPx(lab5_PX2);
	v3.SetPy(lab3_PY2); v4.SetPy(lab4_PY2); v5.SetPy(lab5_PY2);
	v3.SetPz(lab3_PZ2); v4.SetPz(lab4_PZ2); v5.SetPz(lab5_PZ2);
	
	Double_t E3, E4, E5;
	
	//Everything is calculated considering two case: 
	//1. lab3 is miss as kaon
	//2. lab4 is miss as kaon
	//event is acceptable is one of this case is satisfied
	
	for( int k=0; k<2; k++)
	  {
	    if(k == 0 ) {
	      E3 = sqrt(v3.P()*v3.P()+493.677*493.677);
	      E4 = sqrt(v4.P()*v4.P()+139.57*139.57);
	      E5 = sqrt(v5.P()*v5.P()+493.677*493.677);
	      v3.SetE(E3); v4.SetE(E4); v5.SetE(E5);
	      phypo = v3.P();
	    }
	    else if (k == 1){
	      E3 = sqrt(v3.P()*v3.P()+139.57*139.57);
	      E4 = sqrt(v4.P()*v4.P()+493.677*493.677);
	      E5 = sqrt(v5.P()*v5.P()+493.677*493.677);
	      v3.SetE(E3); v4.SetE(E4); v5.SetE(E5);
	      phypo = v4.P();
	    }

	    TLorentzVector vd = v3+v4+v5; // build Ds
	    masshypod = vd.M(); 
	    
	    //std::cout<<"massd: "<<masshypod<<std::endl;
	    
	    if (masshypod > Dmass_down && masshypod < Dmass_up)  //only events which fall into Ds mass window are acceptable
	      {

		masshypo = (Float_t) sqrt( pow(sqrt(pow(lab1_M2,2) + pow(lab1_P2,2))
					       + sqrt(pow(vd.M(),2)+pow(vd.P(),2)),2)
					   - pow(lab1_PX2+vd.Px(),2)-pow(lab1_PY2+vd.Py(),2)-pow(lab1_PZ2+vd.Pz(),2)
					   );  // build Bs
		
		//std::cout<<"massb: "<<masshypo<<std::endl;
		
		if( masshypo > BMassRange[0] && masshypo < BMassRange[1]){ // only events which fall into Bs mass range are acceptable
		  tmpc[i] += w;
		  lab0_MM->setVal(masshypo);
		  bin = heffmiss[i]->FindBin(phypo); //reweighting procedure is applied for Ds child (lab3 or lab4)
		  w = heffmiss[i]->GetBinContent(bin);
		  weights[i]->setVal(w);
		  //dataSet[i]->add(RooArgSet(*lab0_MM,*weights[i]),w,0);
		  
		  if( mistag == true)
		    {
		      if ( tag != 0 && lab0_TAGOMEGA2 < 0.495)
			{
			  //std::cout<<"omega: "<<lab0_TAGOMEGA2<<" tag: "<<tag<<" mass: "<<mMC<<std::endl;
			  lab0_TAGOMEGA->setVal(lab0_TAGOMEGA2);
			  dataHist[i]->add(RooArgSet(*lab0_TAGOMEGA));
			}
		    }
		  dataSet[i]->add(RooArgSet(*lab0_MM,*weights[i]),w,0);
		  

		}
	      }
	  }
      }
      
      
      if ( debug == true)
	{
	  if ( dataSet[i] != NULL ){
	    std::cout<<"=====> Create dataSet for missID BdDPi background"<<std::endl;
	    std::cout<<"Number of events in dataSet: "<<dataSet[i]->numEntries()<<" nMisID: "<<tmpc[i]<<std::endl;
	  } else { std::cout<<"Error in create dataset"<<std::endl; }
	  
	  if( mistag == true)
	    {
	      if ( dataHist[i] != NULL ){
		std::cout<<"[INFO] ==> Create dataHist for missID BsDsPi background"<<std::endl;
		std::cout<<"Number of events in dataSet: "<<dataHist[i]->numEntries()<<std::endl;
	      } else { std::cout<<"Error in create dataset"<<std::endl; }
	    }
	}

      //Create RooKeysPdf for misID background//
      
      name="PhysBkgBd2DPiPdf_m_"+s;
      pdfDataMiss[i] = new RooKeysPdf(name.Data(),name.Data(),*lab0_MM,*dataSet[i]);
      if( pdfDataMiss[i] != NULL ){ std::cout<<"=====> Create RooKeysPdf for misID BdDPi: "<<pdfDataMiss[i]->GetName()<<std::endl;} 
      else {std::cout<<"Cannot create pdf"<<std::endl;}

      SaveTemplate(dataSet[i], pdfDataMiss[i], lab0_MM,smp[i],md[i], debug);
      saveDataTemplateToFile( dataSet[i], pdfDataMiss[i], lab0_MM,
			      md[i].Data(), "root", smp[i].Data(), debug);

      work->import(*pdfDataMiss[i]);
      if (mistag == true)
	{
	  TString namepdf ="PhysBkg"+mode+"Pdf_m_"+s+"_mistag";
          RooHistPdf* pdf = NULL;
          pdf = new RooHistPdf(namepdf.Data(), namepdf.Data(), RooArgSet(*lab0_TAGOMEGA), *dataHist[i]);

          TString mdd = s+"_mistag";
          SaveTemplateHist(dataHist[i], pdf, lab0_TAGOMEGA, mdd, mode, debug);
          work->import(*pdf);
	}
    }
    return work;
  }


  //===========================================================================
  // Obtain dataSets for all partially reconstructed backgrounds
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // sigtree - signature for tree name
  // PIDcut - cut for bachelor particle (depends of mode)
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  // workspace - workspace where data set should be saved
  // save dataSet as RooKeysPdf in .pdf's 
  //==========================================================================

  RooWorkspace* ObtainSpecBack(TString& filesDir, TString& sig, TString& sigtree,
			       int PIDcut,
			       int PIDmisscut,
			       int pPIDcut,
			       double Pcut_down, double Pcut_up,
			       double BDTGCut,
			       double Dmass_down, double Dmass_up,
			       double Bmass_down, double Bmass_up,
			       TString& mVar, TString& mProbVar,
			       TString& hypo,
			       RooWorkspace* workspace, 
			       Bool_t save, Bool_t mistag, bool debug)
  {
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainSpecBack(...). Obtain dataSets for all partially reconstructed backgrounds"<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"PID cut: "<< PIDcut<<std::endl;
	std::cout<<"PIDmiss cut: "<< PIDmisscut<<std::endl;
	std::cout<<"PIDp cut: "<< pPIDcut<<std::endl;
	std::cout<<"BDTGResponse cut: "<<BDTGCut<<std::endl;
	std::cout<<"Bachelor momentum range: ("<<Pcut_down<<","<<Pcut_up<<")"<<std::endl;
	std::cout<<"D(s) mass range: ("<<Dmass_down<<","<<Dmass_up<<")"<<std::endl;
	std::cout<<"Name of observable: "<<mVar<<std::endl;
	std::cout<<"Name of PID variable: "<<mProbVar<<std::endl;
	std::cout<<"Data mode: "<<hypo<<std::endl;
      }
    double BMassRange[2];
    BMassRange[0] = Bmass_down; BMassRange[1]=Bmass_up;
    if ( debug == true) std::cout<<"B(s) mass range: ("<<BMassRange[0]<<","<<BMassRange[1]<<")"<<std::endl;

    RooWorkspace* work = NULL;
    if (workspace == NULL ) { work =  new RooWorkspace("workspace","workspace"); }
    else { work = workspace; }
    
    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);
    TString tagOmegaVar = "lab0_BsTaggingTool_TAGOMEGA_OS";
    TString tagName = "lab0_BsTaggingTool_TAGDECISION_OS";
    RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,0.,0.6);
    lab0_TAGOMEGA->setBins(30);
       
    std::vector <std::string> MCFileName;
    std::vector <std::string> MCTreeName;
    
    ReadOneName(filesDir,MCFileName,sig,debug);
    ReadOneName(filesDir,MCTreeName,sigtree,debug);

    // Read MC File //                                      
    if ( debug == true)  std::cout<<"=====> Read MC File"<<std::endl;
    const int size1 = MCFileName.size();
    const int size2 = MCTreeName.size();
    if( size2 != size1 ){ if ( debug == true) std::cout<<"Cannot open MCFile: size of MCTreeName != size of MCFileName"<<std::endl; return NULL;}
    
    TTree* treeMC[size1];
    std::vector <std::string> mode;

    for( int i =0; i<size1; i++)
      {
	treeMC[i] = NULL;
	treeMC[i] = ReadTreeMC(MCFileName[i].c_str(), MCTreeName[i].c_str(),debug);
      }
    
    ReadMode(MCFileName, mode, false, debug);
    
    //Read all necessary histogram for misID//
    
    std::vector <std::string> FileNamePID;
    std::vector <std::string> FileNamePIDp;
    std::vector <std::string> FileNamePID2;
    
    TString PID = "#PID";
    TString PID2 = "#PID2";
    TString PIDp = "#PIDp";
    ReadOneName(filesDir,FileNamePID,PID,debug);
    ReadOneName(filesDir,FileNamePID2,PID2,debug);
    ReadOneName(filesDir,FileNamePIDp,PIDp,debug);

    TH1F* heff[2];
    TH1F* heffmiss[2];
    TH1F* heff1[2];
    TH1F* heffmiss1[2];
    TH1F* heff2[2];
    TH1F* heffmiss2[2];
    TH1F* heffProton[2];

    Double_t histent1[2];
    Double_t histent2[2];
    histent1[1] = 5092049.0;
    histent1[0] = 6883094.0;
    histent2[1] = 5866006.0;
    histent2[0] = 9122416.0;
    
    TString namehist;
    TString smpmiss[2];
    TString smpProton[2];
    for( int i = 0; i<2; i++ )
      {
	heff1[i]=NULL;
	namehist = Form("MyPionMisID_%d;1",PIDcut);
	heff1[i] = ReadPIDHist(FileNamePID,namehist,i,debug);

	heff2[i]=NULL;
	heff2[i] = ReadPIDHist(FileNamePID2,namehist,i,debug);

	heff[i]=NULL;
	heff[i]=AddHist(heff1[i],  histent1[i], heff2[i], histent2[i],debug);

	heffmiss1[i]=NULL;
	namehist = Form("MyPionMisID_%d;1",PIDmisscut);
	heffmiss1[i] = ReadPIDHist(FileNamePID,namehist,i,debug);

	heffmiss2[i]=NULL;
	heffmiss2[i] = ReadPIDHist(FileNamePID2,namehist,i,debug);

	heffmiss[i]=NULL;
	heffmiss[i]=AddHist(heffmiss1[i],  histent1[i], heffmiss2[i], histent2[i],debug);

	smpmiss[i] = CheckPolarity(FileNamePID[i+1], debug);

	heffProton[i]=NULL; 
	namehist = Form("MyProtonMisID_pK%d;1",pPIDcut);
	heffProton[i] = ReadPIDHist(FileNamePIDp,namehist,i);
	
	smpProton[i] = CheckPolarity(FileNamePIDp[i+1], debug);
	
      }

    // Read sample (means down or up)  from path //
    TString smp[size1];

    if (debug == true) { std::cout<<"Polarities of MC samples:"<<std::endl;}
    for (int i=0; i<size1; i++){
      smp[i] = CheckPolarity(MCFileName[i], debug);
    }
        
    //Set id for bachelor //
    int id_lab1=0;
    if( hypo.Contains("Pi") ) { id_lab1=211; if ( debug == true) std::cout<<" Hypo with Pi"<<std::endl;}
    else if (hypo.Contains("K")) { id_lab1=321; if ( debug == true) std::cout<<"Hypo with K"<<std::endl; }
    
    // Set id for D child //
    int id_lab4=0;
    if (hypo.Contains("Ds") == true ) { id_lab4=321; if ( debug == true) std::cout<<"Hypo with Ds"<<std::endl; }
    else if (hypo.Contains("D") == true && hypo.Contains("Ds") == false) { id_lab4=211;  if ( debug == true) std::cout<<"Hypo with D"<<std::endl;}
    
    // Set other cuts//
    TCut P_cut = Form("lab1_P > %f && lab1_P < %f",Pcut_down,Pcut_up);
    TCut BDTG_cut = Form("BDTGResponse_1 > %f",BDTGCut);
    TCut MCTriggerCut="lab0Hlt1TrackAllL0Decision_TOS && (lab0Hlt2Topo2BodyBBDTDecision_TOS || lab0Hlt2Topo3BodyBBDTDecision_TOS || lab0Hlt2Topo4BodyBBDTDecision_TOS)";
    
    TCut MCBsIDCut = Form("abs(lab1_ID)==%d && abs(lab5_ID)==321 && abs(lab3_ID)==211 && abs(lab4_ID)==%d && (lab5_ID/abs(lab5_ID)) != (lab1_ID/abs(lab1_ID)) && lab0_BKGCAT < 60",id_lab1, id_lab4);
    
    TCut MCCut, MCCut1;
    TCut MCD = Form("lab2_MM > %f && lab2_MM < %f",Dmass_down,Dmass_up);
    TCut MCB = Form("%s > %f && %s < %f",mVar.Data(),BMassRange[0],mVar.Data(),BMassRange[1]);
    TCut hypoKaon = "lab1_M > 200";  // hypo Kaon //
    TCut hypoPion = "lab1_M < 200";  // hypo Pion //

    if ( debug == true) std::cout<<"[INFO] ==> Create RooKeysPdf for PartReco backgrounds" <<std::endl;
    
    RooRealVar* weightsMC[size1];
    RooDataSet* dataSetMC[size1];
    RooDataHist* dataHistMC[size1];
    RooKeysPdf* pdfMC[size1];

    TTree* treetmp[size1];
    
    
    Int_t nentriesMC[size1];
    Int_t binMC=0;
    Float_t wMC(0), mMC(0);
    
    for(int i = 0; i< size1; i++ )
      {
	TString md= mode[i];
	if ( (mode[i].find("Bs") != std::string::npos) || ( (mode[i].find("Ds") != std::string::npos) && (mode[i].find("Dst") == std::string::npos))) {
	  MCCut1 = "lab2_BKGCAT < 30";
	}
	else { MCCut1 = "lab2_BKGCAT == 30"; }
	
	if ( mode[i] == "Bs2DsstKst" || mode[i] == "Bs2DsKst") { MCCut1 = "lab2_BKGCAT == 30";}  // because in fact this is Bd2DKst sample //
	if ( mode[i] == "Bd2DsstPi" ){ MCCut1 = "lab2_BKGCAT < 30";} // bacause in fact this is Bs2DsstPi sample //
	if ( debug == true) std::cout<<"mode: "<<mode[i]<<std::endl;
	
	if (hypo.Contains("K"))  // consider PartReco backgrounds for BsDsK
	  {  
	    MCCut = MCBsIDCut&&MCCut1&&MCTriggerCut&&MCD&&P_cut&&BDTG_cut&&hypoKaon;
	  }
	else //consider PartReco backgrounds for BsDsPi//
	  {
	    MCCut = MCBsIDCut&&MCCut1&&MCTriggerCut&&MCD&&P_cut&&BDTG_cut&&hypoPion;
	  }
	
	treetmp[i] = NULL;
	treetmp[i] = TreeCut(treeMC[i], MCCut, smp[i], md, debug);  // create new tree after applied all cuts // 
	
	//load from tree all necessary variable (which have to be reweighted) and observable // 
	float  lab1_P2, lab0_MM2, lab4_P2, lab0_TAGOMEGA2;
	Int_t tag;
	
	treetmp[i]->SetBranchAddress("lab1_P", &lab1_P2);
	treetmp[i]->SetBranchAddress(mVar.Data(), &lab0_MM2);
	treetmp[i]->SetBranchAddress("lab4_P", &lab4_P2);
	if (mistag == true )
	  {
	    treetmp[i]->SetBranchAddress(tagOmegaVar.Data(),&lab0_TAGOMEGA2);
	    treetmp[i]->SetBranchAddress(tagName.Data(), &tag);
	  }
	nentriesMC[i] = treetmp[i]->GetEntries();
	
	if ( debug == true) std::cout<<"Calculating "<<mode[i]<<" "<<smp[i]<<std::endl;
	weightsMC[i] = NULL;
	dataSetMC[i] = NULL;
	dataHistMC[i] = NULL;

	TString nm = mode[i]+"_"+smp[i];
	TString namew = "weights_"+nm;
	weightsMC[i] = new RooRealVar(namew.Data(), namew.Data(), 0.0, 1.0);  // create new data set //
	
	TString name="dataSetMC_"+nm;
	TString namehist ="dataHistMC_"+nm;
	if( mistag == true) 
	  {
	    dataHistMC[i] = new RooDataHist(namehist.Data(),namehist.Data(),RooArgSet(*lab0_TAGOMEGA)); //create new data hist //
	  }
	dataSetMC[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MM,*weightsMC[i]),namew.Data()); //create new data set //
	
	// take good histogram (for correct md or mu sample) //
	TH1F* hmiss=NULL;
	TH1F* h=NULL;
	TH1F* hProton=NULL;

	for(int k = 0; k < 2; k++)
	  {
	    for(int j = 0; j< 2; j++)
	      {
		if (smp[k] == smpmiss[j] ) { hmiss = heffmiss[j]; h = heff[j]; }
		if (smp[k] == smpProton[j] ) { hProton = heffProton[j]; }
	      }
	  }
	
	if ( debug == true) std::cout<<"Number of entries: "<<nentriesMC[i]<<std::endl;
	Double_t sh=3.9;

	long ag_counter(0), ag_shifted_counter(0), sa_counter(0);

	for (Long64_t jentry=0; jentry<nentriesMC[i]; jentry++) {
	  
	  treetmp[i]->GetEntry(jentry);
	  
	  // Please note that Ds and D mass hypo all applied in NTuple so no need to change mass hypo //
	  
	  if (hypo.Contains("K"))  // PartReco for BsDsK 
	    {
	      
	      if( mode[i].find("Kst") != std::string::npos  || mode[i].find("K") != std::string::npos  )
		{
		  if( mode[i] == "Bs2DsKst" )  // this is in fact Bd2DKst and we shift this 86.6 upward //
		    {
		      Double_t shift=86.6;
		      mMC = lab0_MM2+shift-sh;
		      binMC = hmiss->FindBin(lab4_P2);  // this has to be reweighted becasue in fact this is D mode
		      wMC = hmiss->GetBinContent(binMC);
		      weightsMC[i]->setVal(wMC);
		      lab0_MM->setVal(mMC);
		    }
		  else if ( mode[i] == "Bs2DsstKst" ) // this is in fact Bd2DKst and we shift this 86.6 (Bs-Bd) upward and 200 (Ds-D) downward //
		    {
		      Double_t shift=86.6-200;
		      mMC = lab0_MM2+shift-sh;
		      binMC = hmiss->FindBin(lab4_P2);  // this has to be reweighted becasue in fact this is D mode
		      wMC = hmiss->GetBinContent(binMC);
		      weightsMC[i]->setVal(wMC);
		      lab0_MM->setVal(mMC);
		    }
		  else if ( mode[i].find("Bd") != std::string::npos )
		    {
		      mMC=lab0_MM2-sh;
		      binMC = hmiss->FindBin(lab4_P2);  // this has to be reweighted becasue in fact this is D mode
                      wMC = hmiss->GetBinContent(binMC);
                      weightsMC[i]->setVal(wMC);
                      lab0_MM->setVal(mMC);
		    }
		  else // typical mode with K, nothing to do 
		    {
		      mMC=lab0_MM2-sh;
		      wMC =1.0;
		      lab0_MM->setVal(mMC);
		      weightsMC[i]->setVal(wMC);
		    }
		}
	      else   // mode with {Pi,Rho}, bachelor has to be reweighted //  
		{
		  binMC = h->FindBin(lab1_P2);
		  wMC = h->GetBinContent(binMC);
		  weightsMC[i]->setVal(wMC);
		  mMC=lab0_MM2-sh;
		  lab0_MM->setVal(mMC);
		  
		}
	    }
	  else if (hypo.Contains("Pi")){  //PartReco for BsDsPi 
	    mMC = lab0_MM2-sh;
	    if( mode[i] == "Lb2LcPi" || mode[i] == "Bd2DstPi" || mode[i] == "Bd2DRho"){ // Lc child has to be reweighted
	      
	      binMC = hProton->FindBin(lab4_P2);
	      wMC = hProton->GetBinContent(binMC);
	      weightsMC[i]->setVal(wMC);
	    }
	    else if ( mode[i] == "Bd2DsstPi") { // this is in fact Bs2DsstPi and we shift this 86.6 downward //
	      wMC =1.0;
	      weightsMC[i]->setVal(wMC);
	      mMC = mMC-86.6;
	    }
	    else { //nothing done, mode with Pi //
	      wMC =1.0;
	      weightsMC[i]->setVal(wMC);
	    }
	    lab0_MM->setVal(mMC);
	    	    
	  }

	  if (5320 < lab0_MM2 and lab0_MM2 < 5420) sa_counter++;
	  if (BMassRange[0] < lab0_MM2 and lab0_MM2 < BMassRange[1]) ag_counter++;
	  
	  if ( mMC > BMassRange[0] && mMC < BMassRange[1])
	    {
	      if( mistag == true) 
		{
		  //std::cout<<"mistag: "<<lab0_TAGOMEGA2<<std::endl;
		  if ( tag != 0 && lab0_TAGOMEGA2 < 0.495) 
		    {
		      // std::cout<<"omega: "<<lab0_TAGOMEGA2<<" tag: "<<tag<<" mass: "<<mMC<<std::endl; 
		      lab0_TAGOMEGA->setVal(lab0_TAGOMEGA2);
		      dataHistMC[i]->add(RooArgSet(*lab0_TAGOMEGA));
		    }
		  }
	      dataSetMC[i]->add(RooArgSet(*lab0_MM,*weightsMC[i]),wMC,0);
	      ag_shifted_counter++;
	    }
	  
	}

	if ( debug == true){
	std::cout << "DEBUG: AG - shifted " << ag_shifted_counter
		  << " no shift " << ag_counter
		  << " SA - no shift " << sa_counter << std::endl;
	
	std::cout<<"Create dataSet MC: "<<dataSetMC[i]->GetName()<<" with entries: "<<dataSetMC[i]->numEntries()<<std::endl;
	}
	if( save == true){
	  pdfMC[i] = NULL;
	  TString mdd = md+"before";
	  if ( mistag == true )
	    {
	      TString namepdf ="PhysBkg"+mode[i]+"Pdf_m_"+smp[i]+"_mistag";
	      RooHistPdf* pdf = NULL;
	      pdf = new RooHistPdf(namepdf.Data(), namepdf.Data(), RooArgSet(*lab0_TAGOMEGA), *dataHistMC[i]);

	      TString mddd = mdd+"_mistag";
	      SaveTemplateHist(dataHistMC[i], pdf, lab0_TAGOMEGA, mddd ,smp[i], debug);
	      work->import(*pdf);
	    }
	  else
	    {
	      pdfMC[i] = CreatePDFMC(dataSetMC[i], lab0_MM, smp[i], mdd, false, debug);
	      
	      SaveTemplate(dataSetMC[i], pdfMC[i], lab0_MM, smp[i],mdd, debug);
	      saveDataTemplateToFile( dataSetMC[i], pdfMC[i], lab0_MM,
				      mdd.Data(), "root", smp[i].Data(), debug );
	    }
	}
	//work->import(*pdfMC[i]);
	if (mistag == true )
	  {
	    work->import(*dataHistMC[i]);
	  }
	work->import(*dataSetMC[i]);
	
      }
    return work;
  }


  /**
   * Get k factors for partially reconstructed backgrounds, use
   * kinematics hack to get kfactors for backgrounds with missing MC
   * samples.
   *
   */

  RooWorkspace* getSpecBkg4kfactor(TString& filesDir, TString& sig,
				   TString& sigtree, int PIDcut,
				   int PIDmisscut, int pPIDcut,
				   double Pcut_down, double Pcut_up,
				   double BDTGCut, double Dmass_down,
				   double Dmass_up, TString& mVar,
				   TString& hypo, RooWorkspace* workspace,
				   TFile &ffile, bool mass_win, bool debug)
  {
    long gmsg_count(0), gerr_count(0);

    if ( debug == true)
      {
	std::cout << "[INFO] ==> GeneralUtils::getSpecBkg4kfactor(...)."
		  << " Obtain dataSets for partially reconstructed backgrounds"
		  << std::endl;
	std::cout << "name of config file: " << filesDir << std::endl;
	std::cout << "PID cut: "<< PIDcut << std::endl;
	std::cout << "PIDmiss cut: "<< PIDmisscut << std::endl;
	std::cout << "PIDp cut: "<< pPIDcut << std::endl;
	std::cout << "BDTGResponse cut: " << BDTGCut << std::endl;
	std::cout << "Bachelor momentum range: (" << Pcut_down << ","
		  << Pcut_up << ")" << std::endl;
	std::cout << "D(s) mass range: (" << Dmass_down << "," << Dmass_up
	      << ")" << std::endl;
	std::cout << "Name of observable: " << mVar << std::endl;
	std::cout << "Data mode: " << hypo << std::endl;
      }

    double BMassRange[2] = {5100, 5800};
    //BMassRange[0] = 5320; BMassRange[1]=5980;
    if (workspace == NULL)
      workspace = new RooWorkspace("workspace","workspace");

    // read root filenames into the variables below
    std::vector <std::string> MCFileName, MCTreeName;
    ReadOneName(filesDir, MCFileName, sig, debug);
    ReadOneName(filesDir, MCTreeName, sigtree, debug);

    // Read MC File
    // std::cout << "=====> Read MC File" << std::endl;
    const unsigned ndsets(MCFileName.size());

    if(MCTreeName.size() != ndsets) {
      ERROR(gerr_count, "Incompatible file list size: MCTreeName and MCFileName");
      return NULL;
    }

    TTree* treeMC[ndsets];
    std::vector <std::string> mode;
    for( unsigned i =0; i < ndsets; i++) {
      treeMC[i] = ReadTreeMC(MCFileName[i].c_str(), MCTreeName[i].c_str(), debug);
    }
    ReadMode(MCFileName, mode, true, debug);

    // Read all necessary histogram for misID
    std::vector <std::string> FileNamePID;
    std::vector <std::string> FileNamePID2;
    std::vector <std::string> FileNamePIDp;
    TString PID = "#PID";
    TString PID2 = "#PID2";
    TString PIDp = "#PIDp";
    ReadOneName(filesDir, FileNamePID, PID, debug);
    ReadOneName(filesDir, FileNamePID2, PID2, debug);
    ReadOneName(filesDir, FileNamePIDp, PIDp, debug);

    TH1F* heff[2];
    TH1F* heffmiss[2];
    TH1F* heff1[2];
    TH1F* heffmiss1[2];
    TH1F* heff2[2];
    TH1F* heffmiss2[2];
    TH1F* heffProton[2];

    Double_t histent1[2];
    Double_t histent2[2];
    histent1[1] = 5092049.0;
    histent1[0] = 6883094.0;
    histent2[1] = 5866006.0;
    histent2[0] = 9122416.0;

    TString namehist;
    TString smpmiss[2];
    TString smpProton[2];

    for (int i = 0; i < 2; i++) {
      heff1[i]=NULL;
      namehist = Form("MyPionMisID_%d;1",PIDcut);
      heff1[i] = ReadPIDHist(FileNamePID,namehist,i);

      heff2[i]=NULL;
      heff2[i] = ReadPIDHist(FileNamePID2,namehist,i);

      heff[i]=NULL;
      heff[i]=AddHist(heff1[i],  histent1[i], heff2[i], histent2[i]);

      heffmiss1[i]=NULL;
      namehist = Form("MyPionMisID_%d;1",PIDmisscut);
      heffmiss1[i] = ReadPIDHist(FileNamePID,namehist,i);

      heffmiss2[i]=NULL;
      heffmiss2[i] = ReadPIDHist(FileNamePID2,namehist,i);

      heffmiss[i]=NULL;
      heffmiss[i]=AddHist(heffmiss1[i],  histent1[i], heffmiss2[i], histent2[i]);
      
      smpmiss[i] = CheckPolarity(FileNamePID[i+1], debug);

      heffProton[i] = NULL;
      namehist = Form("MyProtonMisID_pK%d;1", pPIDcut);
      heffProton[i] = ReadPIDHist(FileNamePIDp, namehist, i, debug);
      
      smpProton[i] = CheckPolarity(FileNamePIDp[i+1], debug);


      if (heff[i]) {}; // hush up compiler warning
      if (heffmiss[i]) {}; // hush up compiler warning
      if (heffProton[i]) {}; // hush up compiler warning
    } // end of for loop

    //Read sample (means down or up) from path//
    TString smp[ndsets];
    for (unsigned i = 0; i< ndsets; i++) {
      smp[i] = CheckPolarity(MCFileName[i], debug);
    }

    //Set id for bachelor //
    int id_lab1=0;
    if (hypo.Contains("Pi")) {
      id_lab1=211;
      if ( debug == true) std::cout << " Hypo with Pi" << std::endl;
    } else if (hypo.Contains("K")) {
      id_lab1=321;
      if ( debug == true) std::cout << "Hypo with K" << std::endl;
    }

    // Set id for D child //
    int id_lab4=0;
    if (hypo.Contains("Ds") == true) {
      id_lab4 = 321;
      if ( debug == true) std::cout << "Hypo with Ds" << std::endl;
    } else if (hypo.Contains("D") == true &&
	       hypo.Contains("Ds") == false) {
      id_lab4=211;
      if ( debug == true) std::cout << "Hypo with D" << std::endl;
    }

    // Set other cuts//
    TCut P_cut = Form("lab1_P > %f && lab1_P < %f", Pcut_down, Pcut_up);
    TCut BDTG_cut = Form("BDTGResponse_1 > %f", BDTGCut);
    TCut MCTriggerCut = "lab0Hlt1TrackAllL0Decision_TOS && (lab0Hlt2Topo2BodyBBDTDecision_TOS || lab0Hlt2Topo3BodyBBDTDecision_TOS || lab0Hlt2Topo4BodyBBDTDecision_TOS)";

    TCut MCBsIDCut =
      Form("abs(lab1_ID)==%d && abs(lab5_ID)==321 && abs(lab3_ID)==211 && abs(lab4_ID)==%d && (lab5_ID/abs(lab5_ID)) != (lab1_ID/abs(lab1_ID)) && lab0_BKGCAT < 60",
	   id_lab1, id_lab4);

    TCut MCCut, MCCut1;
    TCut MCD = Form("lab2_MM > %f && lab2_MM < %f", Dmass_down, Dmass_up);
    TCut MCB = Form("%s > %f && %s < %f", mVar.Data(), BMassRange[0],
		    mVar.Data(), BMassRange[1]);
    TCut hypoKaon = "lab1_M > 200";  // hypo Kaon //
    TCut hypoPion = "lab1_M < 200";  // hypo Pion //

    // some constants
    const double BSMASS(5366.3), DSMASS(1968.49), KMASS(493.677),
      BDMASS(5279.53), DMASS(1869.62), PIMASS(139.57018),
      DSSTMASS(2112.34), KSTMASS(891.66), LBMASS(5620.2),
      LCMASS(2286.46), PMASS(938.27203)/*, RHOMASS(775.49),
      DSTMASS(2010.25), DSTMASS2(2460.1)*/;

    long veto_counter(0);
    const double pgratio_cut(5E-3), gratio_cut(5E-2);

    // std::string nratio("hratio_"), nratiop("hratiop_"), sample;
    // if (sig.Contains("MU")) {
    //   sample = "_MU";
    // }
    // if (sig.Contains("MD")) {
    //   sample = "_MD";
    // }

    // TH1D hderatio((nratio+"dE"+sample).c_str(),   "", 100, 0, 0.1);
    // TH1D hpxratio((nratio+"Px"+sample).c_str(),   "", 100, 0, 0.1);
    // TH1D hpyratio((nratio+"Py"+sample).c_str(),   "", 100, 0, 0.1);
    // TH1D hpzratio((nratio+"Pz"+sample).c_str(),   "", 100, 0, 0.1);
    // TH1D hgratio((nratio+"global"+sample).c_str(),   "", 100, 0, 0.1);

    // TH1D hderatiop((nratiop+"dE"+sample).c_str(), "", 100, 0, 0.1);
    // TH1D hpxratiop((nratiop+"Px"+sample).c_str(), "", 100, 0, 0.1);
    // TH1D hpyratiop((nratiop+"Py"+sample).c_str(), "", 100, 0, 0.1);
    // TH1D hpzratiop((nratiop+"Pz"+sample).c_str(), "", 100, 0, 0.1);
    // TH1D hgratiop((nratiop+"global"+sample).c_str(), "", 100, 0, 0.1);

    for (unsigned i = 0; i < ndsets; i++) {
      std::string sanemode(mode[i].substr(0, mode[i].find("_")));

      // debug: Skip over Bs › DsK*, no MC
      // Skip over Bs › Ds*K*, no MC
      if ("Bs2DsstKst" == sanemode
	  // or "Bd2DsstK" == sanemode
	  // or "Bd2DsKst" == sanemode
	  // or "Bs2DsKst" == sanemode
	  ) {
      	continue;
      }

      // // debug: run over only noMC
      // if (not ("Bd2DsstK" == sanemode
      // 	       or "Bd2DsKst" == sanemode
      // 	       or "Bs2DsKst" == sanemode))
      // 	continue;
      // if (not (sanemode == "Bs2DsRho"
      // 	       or sanemode == "Bs2DsKst"))
      // 	continue;

      TString md= mode[i];
      if (((mode[i].find("Ds") != std::string::npos) and
	   (mode[i].find("Dst") == std::string::npos)) or
	  (mode[i].find("Bs") != std::string::npos)) {
	MCCut1 = "lab2_BKGCAT < 30";
      } else {
	MCCut1 = "lab2_BKGCAT == 30";
      }

      if (mode[i] == "Bs2DsstKst" or // mode[i] == "Bs2DsKst" or
	  mode[i] == "Bd2DsKst") {
	MCCut1 = "lab2_BKGCAT == 30";
      }  // because in fact this is Bd2DKst sample
      if (mode[i] == "Bd2DsstPi" ) {
	MCCut1 = "lab2_BKGCAT < 30";
      } // because in fact this is Bs2DsstPi sample
      if (mode[i] == "Bd2DsstK" ) {
	MCCut1 = "lab2_BKGCAT < 30";
      } // because in fact this is Bs2DsstK sample

      if (hypo.Contains("K")) { // consider PartReco backgrounds for BsDsK
	MCCut = MCBsIDCut && MCCut1 && MCTriggerCut && MCD && P_cut &&
	  BDTG_cut && hypoKaon;
      } else { // consider PartReco backgrounds for BsDsPi
	MCCut = MCBsIDCut && MCCut1 && MCTriggerCut && MCD && P_cut &&
	  BDTG_cut && hypoPion;
      }

      /**
       * Calculate and return a dataset with correction factors for
       * partially reconstructed backgrounds.
       *
       */

      // create new tree after applied all cuts
      TTree *ftree = TreeCut(treeMC[i], MCCut, smp[i], md, debug);

      int BPID(0), DPID(0), hPID(0);

      // Read variables from tree
      float Bmom(0.), Bmass(0.),
	B_tru_PE(0.), B_tru_PX(0.), B_tru_PY(0.), B_tru_PZ(0.),
	D_tru_PE(0.), D_tru_PX(0.), D_tru_PY(0.), D_tru_PZ(0.),
	h_tru_PE(0.), h_tru_PX(0.), h_tru_PY(0.), h_tru_PZ(0.),
	B_PE(0.), B_PX(0.), B_PY(0.), B_PZ(0.);

      ftree->SetBranchAddress("lab0_TRUEID", &BPID);
      ftree->SetBranchAddress("lab2_TRUEID", &DPID);
      ftree->SetBranchAddress("lab1_TRUEID", &hPID);

      ftree->SetBranchAddress("lab0_P", &Bmom);
      ftree->SetBranchAddress("lab0_MassFitConsD_M", &Bmass);

      ftree->SetBranchAddress("lab0_TRUEP_E", &B_tru_PE);
      ftree->SetBranchAddress("lab0_TRUEP_X", &B_tru_PX);
      ftree->SetBranchAddress("lab0_TRUEP_Y", &B_tru_PY);
      ftree->SetBranchAddress("lab0_TRUEP_Z", &B_tru_PZ);

      ftree->SetBranchAddress("lab2_TRUEP_E", &D_tru_PE);
      ftree->SetBranchAddress("lab2_TRUEP_X", &D_tru_PX);
      ftree->SetBranchAddress("lab2_TRUEP_Y", &D_tru_PY);
      ftree->SetBranchAddress("lab2_TRUEP_Z", &D_tru_PZ);

      ftree->SetBranchAddress("lab1_TRUEP_E", &h_tru_PE);
      ftree->SetBranchAddress("lab1_TRUEP_X", &h_tru_PX);
      ftree->SetBranchAddress("lab1_TRUEP_Y", &h_tru_PY);
      ftree->SetBranchAddress("lab1_TRUEP_Z", &h_tru_PZ);

      ftree->SetBranchAddress("lab0_PE", &B_PE);
      ftree->SetBranchAddress("lab0_PX", &B_PX);
      ftree->SetBranchAddress("lab0_PY", &B_PY);
      ftree->SetBranchAddress("lab0_PZ", &B_PZ);

      long long nentries = ftree->GetEntries();

      std::string dname ("kfactor_dataset_" + mode[i] + "_" + smp[i]);
      RooRealVar kfactorVar("kfactorVar", "Correction factor", 0.5, 1.5);
      RooDataSet dataset(dname.c_str(), dname.c_str(), RooArgSet(kfactorVar));

      ffile.cd();
      std::string hname("_"+mode[i]+"_"+smp[i]);
      TTree mBresn(std::string("mBresn"+hname).c_str(),
		   std::string("mBresn"+hname).c_str());

      double mBdiff(0.0), kfactor(0.0), kfactorp(0.0);
      mBresn.Branch("mBdiff", &mBdiff, "mBdiff/D");
      mBresn.Branch("kfactor", &kfactor, "kfactor/D");
      mBresn.Branch("kfactorp", &kfactorp, "kfactorp/D");

      unsigned long fill_counter(0), loop_counter(0);

      DEBUG(gmsg_count, "decay mode " << mode[i] << "_" << smp[i]
	    << " with " << nentries << " entries");

      bool ispartial(false);
      if (mode[i].find("st") != std::string::npos or
	  mode[i].find("Rho") != std::string::npos) ispartial = true;

      // mo-cos ... mode codes
      enum mode_t { Bd2DK, Bd2DsK, Bd2DsKst, Bd2DsstK, Bs2DsKst,
		    Bs2DsRho, Bs2DsstK, Bs2DsstPi, Bs2DsstRho,
		    Lb2Dsp, Lb2Dsstp, Lb2LcK, Bs2DsPi } current_mode=Bd2DK;

      double SocksFitterArgs[5] = {BSMASS, DSMASS, PIMASS, -1.0, -1.0};

      bool Ds_hypo(true), h_hypo(false),
	noMC(false);

      if ("Bd2DK" == sanemode) {
	current_mode = Bd2DK;
	SocksFitterArgs[0] = BDMASS;
	SocksFitterArgs[1] = DMASS;
	SocksFitterArgs[2] = KMASS;
	Ds_hypo = false;
      } else if ("Bd2DsK" == sanemode) {
	// FIXME: Is it because of low stats (only 5,3)?
	current_mode = Bd2DsK;
	SocksFitterArgs[0] = BDMASS;
	SocksFitterArgs[2] = KMASS;
	h_hypo = true;
      } else if ("Bd2DsKst" == sanemode) {
	// FIXME: it is actually Bd2DKst, fix with proper MC
	current_mode = Bd2DsKst;
	SocksFitterArgs[0] = BDMASS;
	SocksFitterArgs[1] = DMASS;
	SocksFitterArgs[2] = KMASS;
	SocksFitterArgs[3] = KSTMASS;
	SocksFitterArgs[4] = PIMASS;
	noMC = true;
	h_hypo = true;
      } else if ("Bd2DsstK" == sanemode) {
	// FIXME: it is actually Bs2DsstK, fix with proper MC
	current_mode = Bd2DsstK;
	SocksFitterArgs[2] = KMASS;
	SocksFitterArgs[3] = DSSTMASS;
	noMC = true;
	h_hypo = true;
      } else if ("Bs2DsKst" == sanemode) { // Not in PDG?
	// FIXME: it is actually Bs2DsRho, fix with proper MC
	current_mode = Bs2DsKst;
	SocksFitterArgs[4] = PIMASS;
	noMC = true;
	h_hypo = true;		// should not have any effect either way
      } else if ("Bs2DsRho" == sanemode) {
	// FIXME: Only high statistics sample with large ?mB (~20
	// MeV). The ? decays quickly, so it is reconstructed as a
	// ? and the other ? is missed! This should be considered
	// as a partially reconstructed decay with a ?
	// intermediate state.
	current_mode = Bs2DsRho;
	SocksFitterArgs[4] = PIMASS;
      } else if ("Bs2DsstK" == sanemode) {
	// FIXME: Is it because of low stats (only 4,5)?
	current_mode = Bs2DsstK;
	SocksFitterArgs[2] = KMASS;
	SocksFitterArgs[3] = DSSTMASS;
	h_hypo = true;
      } else if ("Bs2DsstPi" == sanemode) {
	current_mode = Bs2DsstPi;
	SocksFitterArgs[3] = DSSTMASS;
      } else if ("Bs2DsstRho" == sanemode) {
	// FIXME: Is it because of low stats (only 3,11)?
	current_mode = Bs2DsstRho;
      } else if ("Lb2Dsp" == sanemode) {
	current_mode = Lb2Dsp;
	SocksFitterArgs[0] = LBMASS;
	SocksFitterArgs[2] = PMASS;
      } else if ("Lb2Dsstp" == sanemode) {
	current_mode = Lb2Dsstp;
	SocksFitterArgs[0] = LBMASS;
	SocksFitterArgs[2] = PMASS;
	SocksFitterArgs[3] = DSSTMASS;
      } else if ("Lb2LcK" == sanemode) {
	current_mode = Lb2LcK;
	SocksFitterArgs[0] = LBMASS;
	SocksFitterArgs[1] = LCMASS;
	SocksFitterArgs[2] = KMASS;
	Ds_hypo = false;
	h_hypo = true;
      } else if ("Bs2DsPi" == sanemode) {
	current_mode = Bs2DsPi;
      }

      for (Long64_t jentry=0; jentry < nentries; jentry++) {
	long msg_count(0), err_count(0);
	ftree->GetEntry(jentry);

	// if (fill_counter > 200) break; // debug

	TLorentzVector Bs(B_tru_PX, B_tru_PY, B_tru_PZ, B_tru_PE),
	  Ds(D_tru_PX, D_tru_PY, D_tru_PZ, D_tru_PE),
	  bach(h_tru_PX, h_tru_PY, h_tru_PZ, h_tru_PE),
	  Bs_rec(0.0, 0.0, 0.0, 0.0), Bs_ref(B_PX, B_PY, B_PZ, B_PE);
	TLorentzVector Bs_tru(Bs);

	// VETO:
	if (std::abs(hPID) == 13) { // no pesky bachelor muons
	  veto_counter++;
	  continue;
	}
	TLorentzVector Bs_diff = Bs - Ds - bach;
	double dEratio(std::abs(Bs_diff.E()/Bs.E())),
	  dPxratio(std::abs(Bs_diff.Px()/Bs.Px())),
	  dPyratio(std::abs((Bs_diff.Py()/Bs.Py()))),
	  dPzratio(std::abs(Bs_diff.Pz()/Bs.Pz()));
	double gratio(dEratio + dPxratio + dPyratio + dPzratio);

	if (ispartial and (gratio < pgratio_cut)) {
	  DEBUG(msg_count, "Vetoing " << mode[i] << "_" << smp[i]);
	  continue;
	} else if (not ispartial and (gratio > gratio_cut)) {
	  DEBUG(msg_count, "Vetoing " << mode[i] << "_" << smp[i]);
	  continue;
	}

	double Blv[4] = {B_tru_PE, B_tru_PX, B_tru_PY, B_tru_PZ};
	double Dlv[4] = {D_tru_PE, D_tru_PX, D_tru_PY, D_tru_PZ};
	double hlv[4] = {h_tru_PE, h_tru_PX, h_tru_PY, h_tru_PZ};
	double mlv[4] = {
	  B_tru_PE - D_tru_PE - h_tru_PE,
	  B_tru_PX - D_tru_PX - h_tru_PX,
	  B_tru_PY - D_tru_PY - h_tru_PY,
	  B_tru_PZ - D_tru_PZ - h_tru_PZ};

	DEBUG(msg_count, "Bs (" << BPID << ") mass from ntuple " << Bs.M());
	DEBUG(msg_count, "Ds (" << DPID << ") mass from ntuple " << Ds.M());
	DEBUG(msg_count, "bachelor (" << hPID << ") mass from ntuple " << bach.M());
	DEBUG(msg_count, mode[i] << "_" << smp[i] << " 4-momenta before fit");
	Bs.Print();
	Ds.Print();
	bach.Print();

	// in the Dsst case, autodetect gamma/pi, but only if the other B
	// daughter is fully reconstructed
	switch (current_mode) {
	case Bs2DsstK: // fall-through intended
	case Bs2DsstPi:
	case Lb2Dsstp:
	    {
		const double m2 = mlv[0] * mlv[0] - mlv[1] * mlv[1] -
		    mlv[2] * mlv[2] - mlv[3] * mlv[3];
		// cut at (half the pion mass)^2
		if (m2 < 0.25 * PIMASS * PIMASS)
		    SocksFitterArgs[4] = 0.;
		else
		    SocksFitterArgs[4] = PIMASS;
	    }
	    break;
	default:
	  break;
	}

	DecayTreeTupleSucksFitter fitter(SocksFitterArgs[0], SocksFitterArgs[1],
					 SocksFitterArgs[2], SocksFitterArgs[3],
					 SocksFitterArgs[4]);
	bool fit_status(false);
	if (ispartial)
	  fit_status = fitter.fit(Blv, Dlv, hlv, mlv);
	else
	  fit_status = fitter.fit(Blv, Dlv, hlv);

	if (not fit_status) {
	  ERROR(err_count, "DecayTreeTupleSucksFitter::fit(..) failed");
	  continue;
	}

	TLorentzVector fBs(Blv[1], Blv[2], Blv[3], Blv[0]),
	  fDs(Dlv[1], Dlv[2], Dlv[3], Dlv[0]),
	  fbach(hlv[1], hlv[2], hlv[3], hlv[0]),
	  fmiss(mlv[1], mlv[2], mlv[3], mlv[0]);
	TLorentzVector fstarred(0.0, 0.0, 0.0, 0.0);

	DEBUG(msg_count, mode[i] << "_" << smp[i] << " 4-momenta after fit");
	fBs.Print();
	fDs.Print();
	fbach.Print();
	if (ispartial) fmiss.Print();

	switch (current_mode) {
	case Bd2DsKst:	// MC from Bd2DKst
	  {
	    fstarred = fmiss + fbach;

	    TwoBodyDecay dmissing(fmiss);
	    TwoBodyDecay dDs(fDs);
	    TwoBodyDecay dbach(fbach);
	    TwoBodyDecay dKst(fstarred, &dbach, &dmissing);
	    TwoBodyDecay dBs(fBs, &dKst, &dDs);

	    DEBUG(msg_count, "Bd2DsKst before");
	    dBs.Print();
	    dBs.toRestFrame();
	    dDs.setMass(DSMASS);
	    dBs.update_momenta();
	    dBs.toParentFrame();
	    DEBUG(msg_count, "Bd2DsKst after");
	    dBs.Print();
	  }
	  break;

	case Bd2DsstK:	// MC from Bs2DsstK
	  {
	    fstarred = fmiss + fDs;

	    TwoBodyDecay dmissing(fmiss);
	    TwoBodyDecay dDs(fDs);
	    TwoBodyDecay dbach(fbach);
	    TwoBodyDecay dDsstar(fstarred, &dDs, &dmissing);
	    TwoBodyDecay dBs(fBs, &dDsstar, &dbach);

	    DEBUG(msg_count, "Bd2DsstK before");
	    dBs.Print();
	    dBs.toRestFrame();
	    dBs.setMass(BDMASS);
	    dBs.update_momenta();
	    dBs.toParentFrame();
	    DEBUG(msg_count, "Bd2DsstK after");
	    dBs.Print();
	  }
	  break;

	case Bs2DsKst:	// MC from Bs2DsRho
	  {
	    fstarred = fmiss + fbach;

	    TwoBodyDecay dmissing(fmiss);
	    TwoBodyDecay dDs(fDs);
	    TwoBodyDecay dbach(fbach);
	    TwoBodyDecay dKst(fstarred, &dbach, &dmissing);
	    TwoBodyDecay dBs(fBs, &dKst, &dDs);

	    DEBUG(msg_count, "Bs2DsKst before");
	    dBs.Print();
	    dBs.toRestFrame();
	    dbach.setMass(KMASS);
	    dKst.setMass(KSTMASS);
	    dBs.update_momenta();
	    dBs.toParentFrame();
	    DEBUG(msg_count, "Bs2DsKst after");
	    dBs.Print();
	  }
	  break;
	default:
	  break;
	}

	Bs = fBs;
	if (Ds_hypo == false) Ds.SetVectM(fDs.Vect(), DSMASS);
	else Ds = fDs;
	if (h_hypo == false) bach.SetVectM(fbach.Vect(), KMASS);
	else bach = fbach;

	Bs_rec = Ds + bach;
	kfactorp = Bs_rec.P() / Bs.P();
	kfactor = kfactorp * Bs.M() / Bs_rec.M();

	if (std::isnan(kfactor) || std::isinf(kfactor) || kfactor <= 0. ||
	    std::isnan(kfactorp) || std::isinf(kfactorp) || kfactorp <= 0.) {
	  DEBUG(msg_count, "K-factor is invalid: " << kfactor);
	  if ("Bd2DsstK" == sanemode or "Bd2DsKst" == sanemode
	      or "Bs2DsKst" == sanemode) {
	    DEBUG(msg_count, sanemode << "Bs_ref.M() = " << Bs_ref.M()
		  << " Bmass (LHCb) = " << Bmass);
	    DEBUG(msg_count, sanemode << "K-factor (m/p) = " << kfactor
		  << " K-factor (p) = " << kfactorp);
	  }
	  continue;
	}

	double Bs_mass(Bs_rec.M());
	bool in_mass_win(false);

	if (noMC) {
	  if (5320.0 < Bs_mass && Bs_mass < 5420.0) { // Bs my reco mass window
	    in_mass_win = true;
	  }
	} else {
	  if (5320.0 < Bmass && Bmass < 5420.0) { // Bs LHCb reco mass window
	    in_mass_win = true;
	  }
	}

	if (not mass_win) in_mass_win = true; 	// when no mass window

	if (in_mass_win) {
	  mBdiff = Bs_rec.M() - Bs_ref.M();
	  DEBUG(msg_count, "mBdiff = " << mBdiff << "k(m/p) = "
		<< kfactor << ", k(p) = " << kfactorp);
	  // DEBUG(msg_count, "pass: (" << loop_counter << ") My B mass: "
	  // 	<< Bs_mass << ", LHCb mass: " << Bmass);

	  // if (std::abs(mBdiff) > 100.) { // debug
	  //   double moverp_tru(Bs.M() / Bs.P()),
	  //     moverp_rec(Bs_rec.M() / Bs_rec.P());
	  //   DEBUG(msg_count, "delta m = " << mBdiff);
	  //   DEBUG(msg_count, "k(m/p) = " << kfactor << ", k(p) = " << kfactorp);
	  //   DEBUG(msg_count, "True m/p = " << moverp_tru << ", Reco m/p = " << moverp_rec);
	  //   DEBUG(msg_count, "gratio = " << gratio);
	  //   DEBUG(msg_count, "Veto B 4-momenta diff");
	  //   Bs_diff.Print();
	  //   DEBUG(msg_count, "True B 4-momenta");
	  //   Bs.Print();
	  //   DEBUG(msg_count, "True D 4-momenta");
	  //   Ds.Print();
	  //   DEBUG(msg_count, "PID corrected true bachelor 4-momenta");
	  //   bach.Print();
	  //   DEBUG(msg_count, "Reco B 4-momenta");
	  //   Bs_rec.Print();
	  //   DEBUG(msg_count, "Reference B 4-momenta");
	  //   Bs_ref.Print();
	  // }

	  // if (ispartial) {
	  //   hderatiop.Fill(dEratio);
	  //   hpxratiop.Fill(dPxratio);
	  //   hpyratiop.Fill(dPyratio);
	  //   hpzratiop.Fill(dPzratio);
	  //   hgratiop.Fill(gratio);
	  // } else {
	  //   hderatio.Fill(dEratio);
	  //   hpxratio.Fill(dPxratio);
	  //   hpyratio.Fill(dPyratio);
	  //   hpzratio.Fill(dPzratio);
	  //   hgratio.Fill(gratio);
	  // }

	  // Fill selected events
	  mBresn.Fill();
	  kfactorVar.setVal(kfactor);
	  dataset.add(RooArgSet(kfactorVar));
	  fill_counter++;
	}//  else if (current_mode == Bs2DsKst) {
	//   DEBUG(msg_count, "fail: (" << loop_counter << ") My B mass: "
	// 	<< Bs_mass << ", LHCb mass: " << Bmass);
	// }
	loop_counter++;
      }	// end of loop over tree entries

      DEBUG(gmsg_count, "decay mode " << mode[i] << "_" << smp[i]);
      DEBUG(gmsg_count, "Looped " << loop_counter << ", Filled " << fill_counter);

      workspace->import(dataset);
      ffile.WriteObject(&mBresn, mBresn.GetName());
    } // end of loop on datasets/modes

    // ffile.WriteObject(&hderatio, hderatio.GetName());
    // ffile.WriteObject(&hpxratio, hpxratio.GetName());
    // ffile.WriteObject(&hpyratio, hpyratio.GetName());
    // ffile.WriteObject(&hpzratio, hpzratio.GetName());
    // ffile.WriteObject(&hgratio, hgratio.GetName());

    // ffile.WriteObject(&hderatiop, hderatiop.GetName());
    // ffile.WriteObject(&hpxratiop, hpxratiop.GetName());
    // ffile.WriteObject(&hpyratiop, hpyratiop.GetName());
    // ffile.WriteObject(&hpzratiop, hpzratiop.GetName());
    // ffile.WriteObject(&hgratiop, hgratiop.GetName());

    DEBUG(gmsg_count, "Vetoed " << veto_counter << " events");
    return workspace;
  }


  //===========================================================================
  // Obtain Signal sample
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // sigtree - signature for tree name
  // PIDcut - cut for bachelor particle (depends of mode)
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  // workspace - workspace where data set should be saved
  //==========================================================================

  RooWorkspace* ObtainSignal( TString& filesDir, TString& sig,
			      int PIDcut, 
			      double Pcut_down, double Pcut_up,
			      double BDTGcut, 
			      double Dmass_down, double Dmass_up,
			      double Bmass_down, double Bmass_up,
			      double time_down, double time_up,
			      TString &mVar,
			      TString& tVar,
                              TString& tagVar,
                              TString& tagOmegaVar,
                              TString& idVar,
			      TString &mProbVar,
			      TString& mode,
			      RooWorkspace* workspace,
			      bool debug
			      )

  {
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainSpecBack(...). Obtain dataSets for all partially reconstructed backgrounds"<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"PIDK cut: "<< PIDcut<<std::endl;
	std::cout<<"BDTGResponse cut: "<<BDTGcut<<std::endl;
	std::cout<<"Bachelor momentum range: ("<<Pcut_down<<","<<Pcut_up<<")"<<std::endl;
	std::cout<<"D(s) mass range: ("<<Dmass_down<<","<<Dmass_up<<")"<<std::endl;
	std::cout<<"Name of mass observable: "<<mVar<<std::endl;
	std::cout<<"Name of time observable: "<<tVar<<std::endl;
	std::cout<<"Name of tag observable: "<<tagVar<<std::endl;
	std::cout<<"Name of mistag observable: "<<tagOmegaVar<<std::endl;
	std::cout<<"Name of id observable: "<<idVar<<std::endl;
	std::cout<<"Name of PID variable: "<<mProbVar<<std::endl;
	std::cout<<"Data mode: "<<mode<<std::endl;
      }
     

    double BMassRange[2];
    BMassRange[0] = Bmass_down; BMassRange[1]=Bmass_up;
    if ( debug == true) std::cout<<"B(s) mass range: ("<<Bmass_down<<","<<Bmass_up<<")"<<std::endl;
    if ( debug == true) std::cout<<"B(s) time range: ("<<time_down<<","<<time_up<<")"<<std::endl;

    // BMassRange[0] = 5330.; BMassRange[1]=5410.;
    
    
    std::vector <std::string> FileName;
    
    ReadOneName(filesDir,FileName,sig,debug);
    
    
    TTree* tree[2];
    
    for( int i=0; i<2; i++)
      {
	tree[i] = NULL;
	tree[i] = ReadTreeData(FileName,i, debug);
      }
    
  
    RooWorkspace* work = NULL;
    if (workspace == NULL){ work =  new RooWorkspace("workspace","workspace");}
    else {work = workspace; }
    
    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);
    RooRealVar* lab0_TAU = new RooRealVar(tVar.Data(),tVar.Data(),time_down,time_up);
    RooRealVar* lab0_TAG = new RooRealVar(tagVar.Data(),tagVar.Data(),-1.,1.);
    RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,1.);
    RooRealVar* lab1_ID = new RooRealVar(idVar.Data(),idVar.Data(),-1.,1.);

    lab0_TAGOMEGA->setBins(30);

    // Read sample (down,up) from path//
    TString smp[2];
    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
    }
    

    //Set all cuts//
    TCut PID_cut=""; 
    int id_lab1=0;
  
    TCut BachHypo;
    if( mode.Contains("Pi") ) { 
      PID_cut = Form("%s < %d",mProbVar.Data(),PIDcut); 
      id_lab1=211; 
      BachHypo = "lab1_M < 200"; 
      if ( debug == true) std::cout<<"Mode with Pi"<<std::endl;
    }
    else if (mode.Contains("K")) { 
      PID_cut = Form("%s > %d",mProbVar.Data(),PIDcut); 
      id_lab1=321; 
      BachHypo = "lab1_M > 200"; 
      if ( debug == true) std::cout<<"Mode with K"<<std::endl; 
    }
    
    int id_lab4=0;
    if (mode.Contains("Ds") == true ) { id_lab4=321; if ( debug == true) std::cout<<"Mode with Ds"<<std::endl; }
    else if (mode.Contains("D") == true && mode.Contains("Ds") == false) { id_lab4=211;  if ( debug == true) std::cout<<"Mode with D"<<std::endl;}
    
    TCut P_cut = Form("lab1_P > %f && lab1_P < %f",Pcut_down,Pcut_up);
    TCut BDTG_cut = Form("BDTGResponse_1 > %f",BDTGcut);
    TCut FDCHI2 = "lab2_FDCHI2_ORIVX > 2";

    TCut MCTriggerCut="lab0Hlt1TrackAllL0Decision_TOS && (lab0Hlt2Topo2BodyBBDTDecision_TOS || lab0Hlt2Topo3BodyBBDTDecision_TOS || lab0Hlt2Topo4BodyBBDTDecision_TOS)";
    
    TCut KKPiHypo = "lab3_M < 200 && lab4_M > 200 && lab5_M > 200";
    TCut PIDchild_cut = "lab4_PIDK > 5 && lab3_PIDK < 0 && lab5_PIDK>5";
    
    TCut MCBsIDCut = Form("abs(lab1_ID)==%d && abs(lab5_ID)==321 && abs(lab3_ID)==211 && abs(lab4_ID)==%d && lab0_BKGCAT < 30",id_lab1, id_lab4);
    TCut MCBsTRUEIDCut = Form("abs(lab1_TRUEID)==%d && abs(lab5_TRUEID)==321 && abs(lab3_TRUEID)==211 && abs(lab4_TRUEID)==%d",id_lab1, id_lab4);

 
    TCut MCCut, MCCut1;
    TCut MCD = Form("lab2_MM > %f && lab2_MM < %f",Dmass_down,Dmass_up);
    TCut MCB = Form("%s > %f && %s < %f",mVar.Data(),BMassRange[0],mVar.Data(),BMassRange[1]);
    
    if ( (mode.Contains("Bs") != -1) || ( (mode.Contains("Ds") != -1) && (mode.Contains("Dst") == -1))) {
      MCCut1 = "(lab2_BKGCAT<30 || lab2_BKGCAT == 50)";
    }
    else { MCCut1 = "lab2_BKGCAT == 30"; }
    
    if ( debug == true) std::cout<<"mode: "<<mode<<std::endl;
    
    MCCut = MCBsIDCut&&MCTriggerCut&&MCD&&MCB&&MCCut1&&MCBsTRUEIDCut&&BachHypo&&KKPiHypo&&P_cut&&BDTG_cut&&FDCHI2; //all cuts//
    
    TTree* treetmp = NULL;
    RooDataSet* dataSetMC[2];
       
    Float_t c = 299792458.;
    Float_t factor = 1e9/c;
 
    for(int i = 0; i<2; i++)
    { 
      treetmp = TreeCut(tree[i], MCCut, smp[i], mode, debug);  //obtain new tree with applied all cuts//
      Int_t nentriesMC = treetmp->GetEntries();
      
      Float_t lab0_MM3,lab0_TAU3[10],lab0_TAGOMEGA3;
      Int_t lab1_ID3, lab0_TAG3;
      treetmp->SetBranchAddress(mVar.Data(), &lab0_MM3);
      treetmp->SetBranchAddress(tVar.Data(),&lab0_TAU3);
      treetmp->SetBranchAddress(tagVar.Data(),&lab0_TAG3);
      treetmp->SetBranchAddress(tagOmegaVar.Data(),&lab0_TAGOMEGA3);
      treetmp->SetBranchAddress(idVar.Data(),&lab1_ID3);


      TString name="dataSetMC"+mode+"_"+smp[i];
      TString namehist = "dataHistMC"+mode+"_"+smp[i];
      dataSetMC[i] = NULL;
      dataSetMC[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MM,*lab0_TAU,*lab0_TAG,*lab0_TAGOMEGA,*lab1_ID)); //create new data set//
	
      
      for (Long64_t jentry=0; jentry<nentriesMC; jentry++) {
	treetmp->GetEntry(jentry);

    if (lab0_TAG3 < -10) continue;

	if ( lab0_MM3 > BMassRange[0] && lab0_MM3 < BMassRange[1])
	  {

	    Int_t id;
            if (lab1_ID3 > 0) { id = 1.0; }
            else { id = -1.0; }

            if ( lab0_TAGOMEGA3 > 0.5) { lab0_TAGOMEGA3 = 0.5;}

            if ( lab0_TAG3 > 0.5 ) { lab0_TAG3 = 1.0; }
            else if (lab0_TAG3 < 0.5 ) {lab0_TAG3 = -1.0; }
            else { lab0_TAG3 = 0;}

	    lab0_MM->setVal(lab0_MM3);
	    Float_t time = lab0_TAU3[0]*factor;
	    lab0_TAU->setVal(time);
            lab0_TAG->setVal(lab0_TAG3);
            lab0_TAGOMEGA->setVal(lab0_TAGOMEGA3);
            lab1_ID->setVal(id);
	    
	    dataSetMC[i]->add(RooArgSet(*lab0_MM,*lab0_TAU,*lab0_TAG,*lab0_TAGOMEGA,*lab1_ID));
	    
	  }
	
      }

      if ( debug == true) std::cout<<"Number of entries: "<<dataSetMC[i]->numEntries()<<std::endl;
      SaveDataSet(dataSetMC[i],lab0_MM, smp[i], mode, debug);
      saveDataTemplateToFile( dataSetMC[i], NULL, lab0_MM,
			      mode.Data(), "root", smp[i].Data(), debug );
      
      work->import(*dataSetMC[i]);

    }
    TString nameboth="dataSetMC"+mode+"_both";
    RooDataSet* databoth = NULL;
    databoth = new RooDataSet(nameboth.Data(),nameboth.Data(),RooArgSet(*lab0_MM,*lab0_TAU,*lab0_TAG,*lab0_TAGOMEGA,*lab1_ID));
    databoth->append(*dataSetMC[0]);
    databoth->append(*dataSetMC[1]);
    if ( debug == true) std::cout<<" data: "<<databoth->numEntries()<<std::endl;
    work->import(*databoth);
    
    return work;

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
  RooWorkspace* CreatePdfSpecBackground(TString& filesDirMU, TString& sigMU,
					TString& filesDirMD, TString& sigMD,
					TString &mVar,
					double Bmass_down, double Bmass_up,
					RooWorkspace* work, 
					Bool_t mistag,
					bool debug
					)
  {

    if ( debug == true)
      {
	std::cout << "[INFO] ==> GeneralUtils::CreatePdfSpecBackground(...)."
                  << " Obtain RooKeysPdf for partially reconstructed backgrounds"
                  << std::endl;
      }
    double BMassRange[2];
    BMassRange[0] = Bmass_down; BMassRange[1]=Bmass_up;
    
    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);
    if(debug == true) std::cout<<"B(s) mass range: ("<<BMassRange[0]<<","<<BMassRange[1]<<")"<<std::endl;
    
    TString tagOmegaVar = "lab0_BsTaggingTool_TAGOMEGA_OS";
    RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,0.,1.);

    std::vector <std::string> MCFileNameMD;
    std::vector <std::string> MCFileNameMU;

    ReadOneName(filesDirMD,MCFileNameMD,sigMD,debug);
    ReadOneName(filesDirMU,MCFileNameMU,sigMU,debug);
    
    std::vector <std::string> modeMD;
    ReadMode(MCFileNameMD, modeMD, false, debug);
    
    std::vector <std::string> modeMU;
    ReadMode(MCFileNameMU, modeMU, false, debug);

    Int_t sizeMD = modeMD.size();
    Int_t sizeMU = modeMU.size();

    TString smpMD[sizeMD];

    // Read sample (down.up) from paths for MD// 
    for(int i = 0; i< sizeMD; i++ )
      {
	smpMD[i] = CheckPolarity(MCFileNameMD[i], debug);
      }

    //Read sample (down,up) from path for MU// 
    TString smpMU[sizeMU];
    for(int i = 0; i< sizeMU; i++ )
      {
	smpMU[i] = CheckPolarity(MCFileNameMU[i], debug);
      }
    
    //Merged data sets//

    double minsize = std::min(sizeMD, sizeMU);
    if (minsize) {}; // hush up compiler warning
  
    std::vector <RooDataSet*> data;
    std::vector <TString> mode;
    std::vector <RooKeysPdf*> pdfMC;
  
    for( int i = 0; i<sizeMU; i++)
    {
      for (int j = 0; j < sizeMD; j++)
	{
	  // std::cout<<" modeMD: "<<modeMD[j]<<" modeMU: "<<modeMU[i]<<std::endl;
	  if ( modeMU[i] == modeMD[j] )
	    {
	      TString nmMD = modeMD[j]+"_"+smpMD[j];
	      TString nmMU = modeMU[i]+"_"+smpMU[i];
	      
	      TString nameMD="dataSetMC_"+nmMD;
	      RooDataSet*  dataMD = GetDataSet(work,nameMD,debug);
	      TString nameMU="dataSetMC_"+nmMU;
              RooDataSet*  dataMU = GetDataSet(work,nameMU,debug);
	      
	      TString namew = "weight_"+modeMD[i];
	      RooRealVar* weights = new RooRealVar(namew.Data(), namew.Data(), 0.0, 1.0);
	      TString name = "dataSetMC_"+modeMD[i];
	      RooDataSet* datatmp = NULL;
	      if ( mistag == true )
		{
		  datatmp = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MM,*lab0_TAGOMEGA,*weights), namew.Data());   
		}
	      else
		{
		  datatmp = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MM,*weights), namew.Data());
		}
	      datatmp->append(*dataMD);
	      datatmp->append(*dataMU);
	      if(debug == true) std::cout<<"dataMD: "<<dataMD->numEntries()<<" dataMU: "<<dataMU->numEntries()<<" data: "<<datatmp->numEntries()<<std::endl;

	      data.push_back(datatmp);
	      mode.push_back(modeMD[i]);
           
	      TString s="both";
	      TString m = modeMD[j];
	      pdfMC.push_back(CreatePDFMC(datatmp, lab0_MM, s, m, false, debug));
	      int size = pdfMC.size();
	      SaveTemplate(datatmp, pdfMC[size-1], lab0_MM, s , m, debug);
	      saveDataTemplateToFile( datatmp, pdfMC[size-1], lab0_MM,
				      m.Data(), "root", s.Data(), debug );

	      work->import(*pdfMC[size-1]);

	      if (mistag == true)
		{

		  TString nameMD="dataHistMC_"+nmMD;
		  RooDataHist*  datahistMD = GetDataHist(work,nameMD);
		  TString nameMU="dataHistMC_"+nmMU;
		  RooDataHist*  datahistMU = GetDataHist(work,nameMU);


		  Int_t bin=25;
		  Double_t x_min = 0.0;
		  Double_t x_max = 0.5;

		  RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,x_min,x_max);
		  lab0_TAGOMEGA->setBins(bin);

		  TH1* histMU = datahistMU->createHistogram("hist_MU",*lab0_TAGOMEGA,RooFit::Binning(bin,x_min,x_max));
		  TH1* histMD = datahistMD->createHistogram("hist_MD",*lab0_TAGOMEGA,RooFit::Binning(bin,x_min,x_max));

		  TH1F* hist = new TH1F("hist","hist",bin,x_min,x_max);
		  
		  for(int i=0; i<bin; i++)
		    {
		      Double_t con1 = histMU->GetBinContent(i);
		      Double_t con2 = histMD->GetBinContent(i);
		      hist->SetBinContent(i,con1+con2);
		    }
		  	  
		  TString namehist = "DataHistTmp";
		  RooDataHist* dataHist = new RooDataHist(namehist.Data(),namehist.Data(),RooArgList(*lab0_TAGOMEGA),hist);
		  
		  /*
		  TString tagOmegaVar = "lab0_BsTaggingTool_TAGOMEGA_OS";
		  Float_t tagomegaMD, tagomegaMU;
		  trMD->SetBranchAddress(tagOmegaVar.Data(),&tagomegaMD);
		  trMU->SetBranchAddress(tagOmegaVar.Data(),&tagomegaMU);

		  for(int i =0; i<treeMD->GetEntries(); i++)
		    {
		      lab0_TAGOMEGA->setVal(tagomegaMD);
		      datahistMD->add(RooArgSet(*lab0_TAGOMEGA));
		    }
		  for(int i =0; i<treeMU->GetEntries(); i++)
                    {
                      lab0_TAGOMEGA->setVal(tagomegaMU);
                      datahistMU->add(RooArgSet(*lab0_TAGOMEGA));
                    }
		  
		  */
		  
		  TString s = "mistag";
		  TString namepdf ="PhysBkg"+modeMD[j]+"Pdf_m_both_"+s;
		  RooHistPdf* pdf = NULL;
		  pdf = new RooHistPdf(namepdf.Data(), namepdf.Data(), RooArgSet(*lab0_TAGOMEGA), *dataHist);
		  SaveTemplateHist(dataHist, pdf, lab0_TAGOMEGA, s, m, debug);
		  work->import(*pdf);
		  
		  /*		  
		  TString s="mistag";
		  TString m = modeMD[j];
		  pdfMC.push_back(CreatePDFMC(datatmp, lab0_TAGOMEGA, s, m, true));
		  int size = pdfMC.size();
		  SaveTemplate(datatmp, pdfMC[size-1], lab0_TAGOMEGA, s , m);
		  saveDataTemplateToFile( datatmp, pdfMC[size-1], lab0_TAGOMEGA,
					  m.Data(), "root", s.Data(), true );

		  work->import(*pdfMC[size-1]);
		  */
		}
              
	    }
	}
    
    }
  return work;
  }

  //===========================================================================
  // Calculate expected number of yields and misID 
  // filesDirMU - name of config .txt file from where data are loaded
  // sig  - signature Monte Carlo which  should be loaded
  // PIDcut - PID cut
  // PIDmisscut - PID miss cut 
  // sigPID - signature PID histogram which should be loaded
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  //==========================================================================

  void ExpectedYield(TString& filesDir, TString& sigBs, TString& sigBd,
		     TString& sigPID_1, TString& PIDcut_1,
		     TString& sigPID_2, TString& PIDcut_2,
		     double Pcut_down, double Pcut_up,
		     double BDTGCut,
		     double Dmass_down, double Dmass_up,
		     TString &mVar, TString& /*mProbVar*/,
		     TString& mode,TString &mode2)
  {
    
    std::cout<<"[INFO] ==> GeneralUtils::ExpectedYield(...). Calculate expected yield misID backgrouds"<<std::endl;
    std::cout<<"name of config file: "<<filesDir<<std::endl;
    std::cout<<"hist1: "<<PIDcut_1<<std::endl;
    std::cout<<"hist2: "<<PIDcut_2<<std::endl;
          
    std::cout<<"=====> Preparing signal from MC"<<std::endl;
    
       
    std::vector <std::string> FileName;
    ReadOneName(filesDir,FileName,sigBs, true);
        
    TTree* tree[2];

    for( int i=0; i<2; i++)
      {
	tree[i] = NULL;
	tree[i] = ReadTreeData(FileName,i, true);
      }
    
    std::vector <std::string> FileNameBd;
    ReadOneName(filesDir,FileNameBd,sigBd, true);

    TTree* treeBd[2];

    for( int i=0; i<2; i++)
      {
        treeBd[i] = NULL;
        treeBd[i] = ReadTreeData(FileNameBd,i, true);
      }

           
    TString smp[2], smpBd[2];
    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], true);
      smpBd[i-1] = CheckPolarity(FileNameBd[i], true);
    }
    
    std::vector <std::string> FileNamePID_1;
    std::vector <std::string> FileNamePID_2;
    std::vector <std::string> FileNamePID2_1;
    std::vector <std::string> FileNamePID2_2;

    ReadOneName(filesDir,FileNamePID_1,sigPID_1, true);
    ReadOneName(filesDir,FileNamePID_2,sigPID_2, true);
    

    if( sigPID_1 == "#PID") 
      { 
	TString sigPID2_1="#PID2";
	ReadOneName(filesDir,FileNamePID2_1,sigPID2_1, true); 
      }

    if( sigPID_2 == "#PID")
      {
        TString sigPID2_2="#PID2";
        ReadOneName(filesDir,FileNamePID2_2,sigPID2_2, true);
      }

    TH1F* h_1[2];
    TH1F* h_2[2];

    TH1F* h_11[2];
    TH1F* h_21[2];

    TH1F* h_12[2];
    TH1F* h_22[2];

    Double_t histent1[2];
    Double_t histent2[2];
    histent1[1] = 5092049.0;
    histent1[0] = 6883094.0;
    histent2[1] = 5866006.0;
    histent2[0] = 9122416.0;
  
    TString namehist;
    //TString smpmiss[2];
    for( int i = 0; i<2; i++ )
      {
	std::cout<<FileNamePID_1[0]<<std::endl;
	std::cout<<FileNamePID_1[i+1]<<std::endl;
	h_11[i]=NULL;
	h_12[i]=NULL;
	h_11[i] = ReadPIDHist(FileNamePID_1,PIDcut_1,i, true);
	if ( sigPID_1 == "#PID" )
	  {
	    std::cout<<FileNamePID2_1[0]<<std::endl;
	    std::cout<<FileNamePID2_1[i+1]<<std::endl;
	    
	    h_12[i] = ReadPIDHist(FileNamePID2_1,PIDcut_1,i, true);
	    h_1[i] = NULL;
	    h_1[i]=AddHist(h_11[i],  histent1[i], h_12[i], histent2[i], true);
	  }
	else {
	  h_1[i] = h_11[i];
	}

      }
    if( mode != "BsDsPi")
      {
	for( int i = 0; i<2; i++ )
	  {
	    std::cout<<FileNamePID_2[0]<<std::endl;
	    std::cout<<FileNamePID_2[i+1]<<std::endl;
	    h_21[i]=NULL;
	    h_21[i] = ReadPIDHist(FileNamePID_2,PIDcut_2,i, true);
	    if ( sigPID_2 == "#PID" )
	      {
		std::cout<<FileNamePID2_2[0]<<std::endl;
		std::cout<<FileNamePID2_2[i+1]<<std::endl;
		h_22[i]=NULL;
		h_22[i] = ReadPIDHist(FileNamePID2_2,PIDcut_2,i, true);
		h_2[i] = NULL;
		h_2[i]=AddHist(h_21[i],  histent1[i], h_22[i], histent2[i], true);
	      }
	    else
	      {
		h_2[i]=h_21[i];
	      }
	  }
      }
    else
      {
	h_2[0]=NULL; h_2[1]=NULL;
      }
  
       
    TCut P_cut = Form("lab1_P > %f && lab1_P < %f",Pcut_down,Pcut_up);
    TCut BDTG_cut = Form("BDTGResponse_1 > %f",BDTGCut);
    TCut Bd_Cut="";
    TCut Bs_Cut="";

    TString nameMeson, nameHypo, nameDMeson, nameDHypo;
    if(mode == "BdDPi" || mode == "Bd2DPi" || mode == "BDPi" || mode == "B2DPi")
      {
	nameMeson = "Bs->DsPi"; 
	nameHypo = "Bd->DPi";
	nameDHypo = "D->KPiPi";
	Bd_Cut = "lab4_M < 200 && lab1_M < 200 && lab3_M <200 && lab5_M > 200";
	if ( mode2 =="kkpi" )
	  {
	    nameDMeson = "Ds->KKPi";
	    Bs_Cut = Form("lab4_M > 200 && lab3_M <200 && lab5_M > 200 && lab1_M < 200 && lab2_M > %f && lab2_M <%f",Dmass_down,Dmass_up);
	  }
	else if(mode2 == "kpipi")
	  {
	    nameDMeson = "Ds->KPiPi";
	    Bs_Cut = Form("lab4_M < 200 && lab3_M <200 && lab5_M > 200 && lab1_M < 200 && lab2_M > %f && lab2_M <%f",Dmass_down,Dmass_up);
	  }

      }
    else if ( mode=="LbLcPi")
      {
	Bd_Cut = "lab1_M < 200 && lab3_M <200 && lab5_M > 200";
	nameMeson = "Bs->DsPi";
        nameHypo = "Lb->LcPi";
        nameDHypo = "Lc->pKPi";
	if ( mode2 =="kpipi" )
	  {
	    nameDMeson = "Ds->KPiPi";
	    Bs_Cut = Form("lab3_M < 200 && lab4_M < 200 && lab5_M >200 && lab1_M < 200 && lab2_M > %f && lab2_M <%f",Dmass_down,Dmass_up);
	  }
	else if(mode2 == "kkpi")
	  {
	    nameDMeson = "Ds->KKPi";
	    Bs_Cut = Form("lab3_M < 200 && lab4_M > 200 && lab5_M >200 && lab1_M < 200 && lab2_M > %f && lab2_M <%f",Dmass_down,Dmass_up);
	  }
	else if(mode2 == "pipipi")
	  {
	    nameDMeson = "Ds->PiPiPi";
	    Bs_Cut = Form("lab3_M < 200 && lab4_M < 200 && lab5_M <200 && lab1_M < 200 && lab2_M > %f && lab2_M <%f",Dmass_down,Dmass_up);
	  }
      }
    else if ( mode.Contains("DsPi") )
      {
	  nameMeson = "Bs->DsK";
          nameHypo = "Bs->DsPi";
	  Bd_Cut = "lab1_M < 200";
	  Bs_Cut = Form("lab1_M > 200 && %s > 5340 && %s < 5400",mVar.Data(),mVar.Data());
	  
      }
    else if ( mode == "LbDsp" || mode == "LbDsstp")
      {
	Bd_Cut = "";
	// Bs_Cut = Form("lab1_M > 200 && %s > 5320 && %s < 5420",mVar.Data(),mVar.Data());
	Bs_Cut = "lab1_M > 200";
      } 

    TCut All_cut = Bs_Cut; //&&BDTG_cut&&P_cut;

    Float_t ratio[2];

    TTree* ttmp[2];
    TTree* ttmp2[2];

    Double_t cal_lab4[2];
    Double_t cal_lab5[2];
    Double_t cal_lab1[2];

    Long_t n_events[2];
    Long_t n_events_Bd[2];
    
    TString h_lab4_name;
    TString h_lab5_name;
    TString h_lab1_name;
    TString heff10_name;
    TString heff0_name;

    for(int i=0; i<2; i++)
      {
	ttmp[i] = NULL;
        ttmp[i] = TreeCut(treeBd[i],Bd_Cut,smpBd[i],mode, true);
	ttmp2[i] = NULL;
	ttmp2[i] = TreeCut(tree[i],All_cut,smp[i],mode, true);
	n_events_Bd[i] = ttmp[i]->GetEntries();
	n_events[i] = ttmp2[i]->GetEntries();
	ratio[i] = (Float_t)n_events[i]/n_events_Bd[i];
	std::cout<<"initial_cut: "<<n_events_Bd[i]<<" cut: "<<n_events<<" ratio: "<<ratio[i]<<std::endl; 
	
	cal_lab4[i] = 0;
	cal_lab5[i] = 0;
	cal_lab1[i] = 0; 
	
	TAxis* axis=h_1[i]->GetXaxis();
	Double_t max = axis->GetXmax();
	//Double_t min = 0;
	
	Int_t nbins = h_1[i]->GetNbinsX();
	
	TH1F* h_lab4 = new TH1F("h_lab4","h_lab4",nbins,0,max);
	TH1F* h_lab5 = new TH1F("h_lab5","h_lab5",nbins,0,max);
	TH1F* h_lab1 = new TH1F("h_lab1","h_lab1",nbins,0,max);
	TH2F *hist2D_1 = new TH2F("hist2D_1","hist2D_1", nbins, 0, max, nbins, 0, max);

	//std::cout<<"nbins"<<nbins<<" min: "<<min<<" max: "<<max<<std::endl;
	if (mode == "BdDPi" || mode == "LbLcPi")
	  {
	    ttmp2[i]->Draw("lab4_P>>h_lab4","", "goff");
	    ttmp2[i]->Draw("lab5_P>>h_lab5","", "goff");
	    ttmp2[i]->Draw("lab1_P>>h_lab1","", "goff");
	    if ( mode == "BdDPi" || mode2 == "kpipi")
	      {
		ttmp2[i]->Draw("lab4_P:lab5_P>>hist2D_1","", "goff");
	      }

	  }
	else
	  {
	    ttmp2[i]->Draw("lab1_P>>h_lab1","", "goff");
	  }
	h_lab4_name = h_lab4->GetName();
	h_lab5_name = h_lab5->GetName();
	h_lab1_name = h_lab1->GetName();
		
	std::cout<<"Numbers of bins:"<<nbins<<std::endl;
	TH1F* heff0_1 = NULL;
	TH1F* heff10_1 = NULL;
	TH1F* heff0_2 = NULL;
	TH1F* heff10_2 = NULL;
	TH1F* heff0 = NULL;
        TH1F* heff10 = NULL;

	if ( mode == "BdDPi" || mode == "LbLcPi")
	  {
	    std::vector <std::string> FileNamePID2;
	    TString sig2 = "#PID";
	    ReadOneName(filesDir,FileNamePID2,sig2, true);

	    std::vector <std::string> FileNamePID3;
	    TString sig3 = "#PID2";
            ReadOneName(filesDir,FileNamePID3,sig3, true);

	    TString name = "MyPionEff_0";
	    heff0_1 = ReadPIDHist(FileNamePID2,name,i, true);
	    heff0_2 = ReadPIDHist(FileNamePID3,name,i, true);
	    heff0_name = heff0_1->GetName();
	    name = "MyKaonEff_10";
	    heff10_1 = ReadPIDHist(FileNamePID2,name,i, true);
	    heff10_2 = ReadPIDHist(FileNamePID3,name,i, true);
	    heff10_name = heff10_1->GetName();

	             
	    heff0=AddHist(heff0_1,  histent1[i], heff10_2, histent2[i], true);
	    heff10=AddHist(heff10_1,  histent1[i], heff10_2, histent2[i], true);
	  }
	if (heff0_2) {}; // hush up compiler warning
	//std::cout<<"Tuuu"<<std::endl;
	//TH2F *hist2D_1 = new TH2F("hist2D_1","hist2D_1", nbins, 0, max, nbins, 0, max);
	TH2F *hist2D_2 = new TH2F("hist2D_2","hist2D_2", nbins, 0, max, nbins, 0, max);   
	
	if ( mode == "BdDPi" && mode2 == "kpipi")
	  {
	    for (Int_t k=1;k<nbins;k++) 
	      {
		Double_t con2 = h_1[i]->GetBinContent(k);
		for (Int_t j=1;j<nbins;j++) 
		  {
		    Double_t con4 = h_2[i]->GetBinContent(j);
		    Double_t con = con2*con4;
		    hist2D_2->SetBinContent(k,j,con);
		  }
	      }




	      // for( int j=1; j<nbins; j++)
	      // {
	      // 	Double_t con2 = h_1[i]->GetBinContent(j);
	      //	Double_t con4 = h_2[i]->GetBinContent(j);
	      
	      // 	hist2D_2->Fill(con2,con4);
	      // }
	    
	  }

        std::cout<<"[INFO] Everything is read"<<std::endl;
	for(int j=1; j< nbins; j++)
	  {
	    //std::cout<<"lalala"<<std::endl;
	    if(  mode == "BdDPi" || mode == "LbLcPi" )
	      {
		
		Double_t con1 = h_lab4->GetBinContent(j);
		Double_t con3 = h_lab5->GetBinContent(j);
		Double_t con2 = h_1[i]->GetBinContent(j);
		Double_t con4 = h_2[i]->GetBinContent(j);
		
		Double_t y = con1*con2;
		Double_t y2 = con3*con4;

		if ( mode == "BdDPi" && mode2 == "kpipi")
		  {
		    for (int k = 1; k< nbins; k++)
		      {
			Double_t con5 = hist2D_1->GetBinContent(k,j);
			Double_t con6 = hist2D_2->GetBinContent(k,j);
			//Double_t con2 = h_1[i]->GetBinContent(k);
			//Double_t con4 = h_2[i]->GetBinContent(j);

			Double_t y3 = con5*con6;
			//Double_t y4 = con5*con4;
			cal_lab4[i] = cal_lab4[i]+y3;
			cal_lab5[i] = n_events[i];
		      }

		  }
		else
		  {
		    cal_lab4[i] = cal_lab4[i]+y;
		    cal_lab5[i] = cal_lab5[i]+y2;
		  }
		std::cout<<"j: "<<j<<" "<<h_lab4->GetName()<<" "<<con1<<" "<<h_1[i]->GetName()<<" "<<con2<<" ";
		std::cout<<h_lab5->GetName()<<" "<<con3<<" "<<h_2[i]->GetName()<<" "<<con4<<std::endl;
		std::cout<<"lab4: "<<cal_lab4[i]<<" lab_5: "<<cal_lab5[i]<<std::endl;
	      }
	    else if (mode == "BsDsPi")
	      {
		
		Double_t con1 = h_lab1->GetBinContent(j);
		Double_t con2 = h_1[i]->GetBinContent(j);
		Double_t y = con1*con2;
		cal_lab1[i] = cal_lab1[i]+y;
		std::cout<<"j: "<<j<<" "<<h_lab1->GetName()<<" "<<con1<<" "<<h_1[i]->GetName()<<" "<<con2<<" "<<std::endl;

	      }
	    else if (mode == "LbDsp" || mode == "LbDsstp")
	      {
		Double_t con1 = h_lab1->GetBinContent(j);
                Double_t con2 = h_1[i]->GetBinContent(j);
		Double_t y = con1*con2; 
                cal_lab1[i] = cal_lab1[i]+y;
		std::cout<<"y :"<<y<<std::endl; 
                std::cout<<"j: "<<j<<" "<<h_lab1->GetName()<<" "<<con1<<" "<<h_1[i]->GetName()<<" "<<con2<<" "<<" "<<" cal_lab1: "<<cal_lab1[i]<<std::endl;
		
	      }
	  }
	Double_t all_misID = 0;
	if( mode=="BdDPi" || mode =="LbLcPi" )
	  {
	    all_misID = cal_lab4[i]*ratio[i]/n_events[i]*cal_lab5[i]*ratio[i]/n_events[i];
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	    std::cout<<"For: "<<mode<<" "<<mode2<<" sample "<<smp[i]<<std::endl;
	    std::cout<<"misIDP: "<<cal_lab4[i]<<" procent: "<<cal_lab4[i]*ratio[i]/n_events[i]*100<<"%"<<std::endl;
	    std::cout<<"misIDK: "<<cal_lab5[i]<<" procent: "<<cal_lab5[i]*ratio[i]/n_events[i]*100<<"%"<<std::endl;
	    if ( mode == "BdDPi" && mode2 == "kpipi")
	      {
	    		all_misID = cal_lab4[i]*ratio[i]/n_events[i];
	    	std::cout<<"AllmisID: "<<cal_lab4[i]*ratio[i]/n_events[i]*100<<"%"<<std::endl;
	      }
	    else
	      {
		std::cout<<"AllmisID: "<<cal_lab4[i]*ratio[i]/n_events[i]*cal_lab5[i]*ratio[i]/n_events[i]*100<<"%"<<std::endl;
		      }
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	  }
	else if (mode == "BsDsPi")
	  {
	    all_misID = cal_lab1[i]*ratio[i]/n_events[i];
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	    std::cout<<"For: "<<mode<<" "<<mode2<<" sample"<<smp[i]<<std::endl;
	    std::cout<<"misID: "<<cal_lab1[i]<<" procent: "<<cal_lab1[i]*ratio[i]/n_events[i]*100<<"%"<<std::endl;
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	  }
	else if (mode == "LbDsp" || mode == "LbDsstp")
	  {
	    all_misID = cal_lab1[i]*ratio[i]/n_events[i];
            std::cout<<"----------------------------------------------------------------"<<std::endl;
            std::cout<<"For: "<<mode<<" "<<mode2<<" sample"<<smp[i]<<std::endl;
            std::cout<<"misID: "<<cal_lab1[i]<<" procent: "<<cal_lab1[i]*ratio[i]/n_events[i]*100<<"%"<<std::endl;
	    std::cout<<"total: "<<cal_lab1[i]/0.271811<<" procent: "<<cal_lab1[i]*ratio[i]/n_events[i]*100/0.271811<<"%"<<std::endl;
            std::cout<<"----------------------------------------------------------------"<<std::endl;
	  }

	if ( mode == "BdDPi" || mode == "LbLcPi")
          {
            for(int j=1; j< nbins; j++)
	      {
		Double_t con2 = h_lab1->GetBinContent(j);
		Double_t con3 = heff0->GetBinContent(j);
		Double_t con4 = heff10->GetBinContent(j);
		Double_t y = con2/con3*con4;
		cal_lab1[i] = cal_lab1[i]+y;
		std::cout<<"j: "<<j<<" "<<h_lab1->GetName()<<" "<<con2<<" "<<heff0->GetName()<<" "<<con3<<" ";
		std::cout<<heff10->GetName()<<" "<<con4<<std::endl;
		
	      }
        
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	    std::cout<<"For bachelor K "<<mode2<<" sample"<<smp[i]<<std::endl;
	    std::cout<<"misID: "<<cal_lab1[i]<<" procent: "<<cal_lab1[i]/n_events[i]*100<<"%"<<std::endl;
	    std::cout<<"All_misID: "<<all_misID*cal_lab1[i]/n_events[i]*100<<"%"<<std::endl;
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	    
	    }
      }
    
    //Constant variable//
    //B(Bs->DsPi)//
    Float_t B_Bs_DsPi   = 2.95e-3;
    Float_t B_Bs_DsPi_u = 0.05e-3;
    //B(B->DPi)//
    Float_t B_Bd_DPi    = 2.68e-3;
    Float_t B_Bd_DPi_u  = 0.13e-3;
    //B(Lb->LcPi)//
    Float_t B_Lb_LcPi   = 8.8e-3;
    Float_t B_Lb_LcPi_u = 3.2e-3;  
    //B(Bs->DsK)//
    Float_t B_Bs_DsK   = 1.90e-4;
    Float_t B_Bs_DsK_u = 0.12e-4;
    //B(Lb->Dsp)//
    //Float_t B_Lb_Dsp   = 2e-6;

    //B(D->KPiPi)//
    Float_t B_D_KPiPi   = 9.13e-2;
    Float_t B_D_KPiPi_u = 0.19e-2;
    //B(Ds->KKPi)//
    Float_t B_Ds_KKPi   = 5.49e-2;
    Float_t B_Ds_KKPi_u = 0.27e-2;
    //B(Ds->KPiPi)//
    Float_t B_Ds_KPiPi   = 6.9e-3;
    Float_t B_Ds_KPiPi_u = 0.5e-3;
    //B(Lc->pKPi)//
    Float_t B_Lc_pKPi   = 5.0e-2;
    Float_t B_Lc_pKPi_u = 1.3e-2;
      

    //fragmentation factor//
    Float_t fsfd = 0.268;
    Float_t fsfd_u = 0.008;

    Float_t B_1=0;
    Float_t B_2=0;
    Float_t B_u_1=0;
    Float_t B_u_2=0;
    
    Float_t B_3=0;
    Float_t B_4=0;
    Float_t B_u_3=0;
    Float_t B_u_4=0;
    if (mode == "BdDPi")
      {
	B_1 = B_Bd_DPi; B_u_1 = B_Bd_DPi_u;
	B_2 = B_Bs_DsPi; B_u_2 = B_Bs_DsPi_u;
	B_3 = B_D_KPiPi; B_u_3 = B_D_KPiPi_u;
	if (mode2 == "kkpi")
	  {
	    B_4 = B_Ds_KKPi; B_u_4 = B_Ds_KKPi_u;
	  }
	else if (mode2 == "kpipi")
	  {
	    B_4 = B_Ds_KPiPi; B_u_4 = B_Ds_KPiPi_u;
	  }
      }
    else if (mode == "LbLcPi")
      {
	B_1 = B_Lb_LcPi; B_u_1 = B_Lb_LcPi_u;
        B_2 = B_Bs_DsPi; B_u_2 = B_Bs_DsPi_u;
        B_3 = B_Lc_pKPi; B_u_3 = B_Lc_pKPi_u;
	B_4 = B_Ds_KKPi; B_u_4 = B_Ds_KKPi_u;
      }
    else if( mode == "BsDsPi")
      {
	B_1 = B_Bs_DsPi; B_u_2 = B_Bs_DsPi_u;
	B_2 = B_Bs_DsK; B_u_2 = B_Bs_DsK_u;
      }

    //ratio B mesons//
    Float_t rB_B   = B_1/B_2;
    Float_t rB_B_u   = rB_B*(B_u_1/B_1+B_u_2/B_2);
    Float_t rB_B2=0;
    Float_t rB_B2_u=0;

    if( mode == "LbLcPi")
      {
	rB_B2 = B_1/B_Bd_DPi;
	rB_B2_u   = rB_B2*(B_u_1/B_1+B_Bd_DPi_u/B_Bd_DPi);
      }

    //ratio D mesons//
    Float_t rB_D=0; 
    Float_t rB_D_u=0;
    if ( mode != "BsDsPi")
      {
	rB_D = B_3/B_4;
	rB_D_u = rB_D*(B_u_3/B_3+B_u_4/B_4);
      }
    Float_t rB_D2=0; 
    Float_t rB_D2_u=0;
    if( mode == "LbLcPi")
      {
        rB_D2 = B_3/B_D_KPiPi;
        rB_D2_u   = rB_D2*(B_u_3/B_3+B_D_KPiPi_u/B_D_KPiPi);
      }

    
    //Ratio N events//
    Float_t rN=0;
    Float_t rN_u=0;
    Float_t rNBd=0;
    Float_t rNBd_u=0;
    if ( mode == "BdDPi")
      {
	rN = rB_B*rB_D/fsfd;
	rN_u = rN*(rB_B_u/rB_B+rB_D_u/rB_D+fsfd_u/fsfd);
      }
    else if (mode == "LbLcPi")
      {
	rN = rB_B*rB_D;
        rN_u = rN*(rB_B_u/rB_B+rB_D_u/rB_D);
	rNBd = rB_B2*rB_D2;
        rNBd_u = rNBd*(rB_B2_u/rB_B2+rB_D2_u/rB_D2);
      }
    else if (mode == "BsDsPi")
      {
	rN =rB_B; rN_u = rB_B_u;
      }
        
    
    
    std::cout<<"----------------------------------------------------------"<<std::endl;
    std::cout<<"Calculation for "<<nameHypo<<", "<<nameDHypo<<" under "<<nameMeson<<", "<<nameDMeson<<std::endl;
    std::cout<<"----------------------------------------------------------"<<std::endl;
    std::cout<<std::endl;
    std::cout<<"------------ Branching fractions for beauty mesons ------------"<<std::endl;
    std::cout<<"B("<<nameHypo<<")=("<<B_1<<" +/- "<<B_u_1<<")"<<std::endl;
    std::cout<<"B("<<nameMeson<<")=("<<B_2<<" +/- "<<B_u_2<<")"<<std::endl;
    
    std::cout<<"B("<<nameHypo<<")/B("<<nameMeson<<")=("<<rB_B<<" +/- "<<rB_B_u<<")"<<std::endl;
    if ( mode != "BsDsPi")
      {
	std::cout<<"------------ Branching fractions for charm mesons ------------"<<std::endl;
	std::cout<<"B("<<nameDHypo<<")=("<<B_3<<" +/- "<<B_u_3<<")"<<std::endl;
	std::cout<<"B("<<nameDMeson<<")=("<<B_4<<" +/- "<<B_u_4<<")"<<std::endl;
	std::cout<<"B("<<nameDHypo<<")/B("<<nameDMeson<<")=("<<rB_D<<" +/- "<<rB_D_u<<")"<<std::endl;
	std::cout<<"------------------ Fragmentation factor ------------------"<<std::endl;
	std::cout<<"fsfd = ("<<fsfd<<" +/- "<<fsfd_u<<")"<<std::endl;
	std::cout<<"--------------- Ratio of number of events ----------------"<<std::endl;
	std::cout<<"N("<<nameHypo<<")/N("<<nameMeson<<") = B("<<nameHypo<<")/B("<<nameMeson;
	if ( mode == "BdDPi"){
	  std::cout<<")*B("<<nameDHypo<<")/B("<<nameDMeson<<")/(fs/fd)="<<std::endl;
	}
	else {
	  std::cout<<")*B("<<nameDHypo<<")/B("<<nameDMeson<<")="<<std::endl;
	}
	std::cout<<"("<<rN<<" +/- "<<rN_u<<")"<<std::endl;
      }
    std::cout<<std::endl;
    //std::cout<<"----------------------------------------------------------"<<std::endl;
    std::cout<<"==================== Selection ==========================="<<std::endl;
    //std::cout<<"----------------------------------------------------------"<<std::endl;

    std::cout<<"initial_cut: "<<Bd_Cut<<std::endl;
    std::cout<<"Selected: DOWM: "<<n_events_Bd[0]<<" UP: "<<n_events_Bd[1]<<std::endl;
    std::cout<<"cut: "<<Bs_Cut<<std::endl;
    std::cout<<"Selected: DOWM: "<<n_events[0]<<" UP:"<<n_events[1]<<std::endl;
    std::cout<<"ratio = NOE_cut/NOE_initial_cut"<<std::endl;
    std::cout<<"Obtained: DOWN: "<<ratio[0]<<" UP: "<<ratio[1]<<std::endl;

    if ( mode != "BsDsPi")
      {
	std::cout<<"---------------------- Histograms ------------------------"<<std::endl;
	std::cout<<"The histogram: "<<h_lab4_name<<" is multiplied by "<<h_1[0]->GetName()<<std::endl;
	std::cout<<"The histogram: "<<h_lab5_name<<" is multiplied by "<<h_2[0]->GetName()<<std::endl;
	std::cout<<"The histogram: "<<h_lab1_name<<" is multiplied by "<<heff10_name<<" and divided by "<<heff0_name<<std::endl;

	std::cout<<"--------------- Calculations for histograms ---------------"<<std::endl;
	std::cout<<"===> calculations for lab4 "<<std::endl;
	std::cout<<"cal_lab4 = sum of "<<h_lab4_name<<"*"<<h_1[0]->GetName()<<std::endl;
	std::cout<<"DOWN: "<<cal_lab4[0]<<" UP: "<<cal_lab4[1]<<std::endl;
	std::cout<<"cal_lab4*ratio/NOE_cut ="<<std::endl;
	Float_t v_lab4_1, v_lab4_2;
	v_lab4_1 = cal_lab4[0]*ratio[0]/n_events[0];
	v_lab4_2 = cal_lab4[1]*ratio[1]/n_events[1];
	std::cout<<"DOWN: "<<v_lab4_1<<" UP: "<<v_lab4_2<<std::endl;
    
	std::cout<<std::endl;
	std::cout<<"===> calculations for lab5 "<<std::endl;
	std::cout<<"cal_lab5 = sum of "<<h_lab5_name<<"*"<<h_2[0]->GetName()<<std::endl;
	std::cout<<"DOWN: "<<cal_lab5[0]<<" UP: "<<cal_lab5[1]<<std::endl;
	std::cout<<"cal_lab5*ratio/NOE_cut ="<<std::endl;
	Float_t v_lab5_1, v_lab5_2;
	v_lab5_1 = cal_lab5[0]*ratio[0]/n_events[0];
	v_lab5_2 = cal_lab5[1]*ratio[1]/n_events[1];
	std::cout<<"DOWN: "<<v_lab5_1<<" UP: "<<v_lab5_2<<std::endl;

	std::cout<<std::endl;
	std::cout<<"===> Final result for lab4 and lab5 "<<std::endl;
	
	std::cout<<"result = cal_lab4*ratio/NOE_cut*cal_lab5*ratio/NOE_cut"<<std::endl;
	Float_t v_lab45_1, v_lab45_2;
	if ( mode == "BdDPi" && mode2 =="kpipi")
	  {
	    v_lab45_1 = v_lab4_1;
            v_lab45_2 = v_lab4_2;
	  }
	else 
	  {
	    v_lab45_1 = v_lab5_1*v_lab4_1;
	    v_lab45_2 = v_lab5_2*v_lab4_2;
	  }
	Float_t v_lab45_av, v_lab45_u;
	v_lab45_av = (v_lab45_1+v_lab45_2)/2;
	v_lab45_u = pow((pow(v_lab45_1-v_lab45_av,2)+pow(v_lab45_2-v_lab45_av,2))/2,0.5)*1.414214;
	
	std::cout<<"DOWN: "<<v_lab45_1<<" UP: "<<v_lab45_2<<std::endl;
	std::cout<<"= ("<<v_lab45_av*100<<" +/- "<<v_lab45_u*100<<")%"<<std::endl;

	std::cout<<std::endl;
	std::cout<<"===> Expected misID yield: "<<nameHypo<<","<<nameDHypo<<std::endl;
	std::cout<<"First method: "<<std::endl;
	
	Float_t fitted_BdDPi_1, fitted_BdDPi_1_u,  fitted_BdDPi_2, fitted_BdDPi_2_u;
	
	// BDTG>0.3
	//	fitted_BdDPi_1 = 8.7683e4;
	//	fitted_BdDPi_1_u = 3.70e2;
	//      fitted_BdDPi_2 = 6.3372e4;
	//	fitted_BdDPi_2_u = 4.71e2;
	
	//BDTG > 0.5
	fitted_BdDPi_1 = 8.3438e4;
	fitted_BdDPi_1_u = 4.06e2;
        fitted_BdDPi_2 = 5.9924e4;
        fitted_BdDPi_2_u = 1.47e3;

	std::cout<<"===> Fitted yield to real data Bd->DPi, D->KPiPi"<<std::endl;
	std::cout<<"DOWN: ("<<fitted_BdDPi_1<<" +/- "<<fitted_BdDPi_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<fitted_BdDPi_2<<" +/- "<<fitted_BdDPi_2_u<<")"<<std::endl;
	
	if(mode == "LbLcPi")
	  {
	    Float_t temp, temp_u;
	    temp = fitted_BdDPi_1*rNBd;
	    temp_u = temp*(fitted_BdDPi_1_u/fitted_BdDPi_1 + rNBd_u/rNBd);
	    fitted_BdDPi_1 = temp;
	    fitted_BdDPi_1_u = temp_u;
	    temp = fitted_BdDPi_2*rNBd;
	    temp_u = temp*(fitted_BdDPi_2_u/fitted_BdDPi_2 + rNBd_u/rNBd);
	    fitted_BdDPi_2 = temp;
	    fitted_BdDPi_2_u = temp_u;
	    std::cout<<"===> Fitted yield to real data Bd->DPi, D->KPiPi scaled by N(Lb->LcPi)/N(Bd->DPi)"<<std::endl;
	    std::cout<<"N(Lb->LcPi)/N(Bd->DPi)= B(Lb->LcPi)/B(Bd->DPi)*B(Lc->pKPi)/N(D->KPiPi)"<<std::endl;
	    std::cout<<"("<<rNBd<<" +/- "<<rNBd_u<<")"<<std::endl;
	    std::cout<<"DOWN: ("<<fitted_BdDPi_1<<" +/- "<<fitted_BdDPi_1_u<<")"<<std::endl;
	    std::cout<<"UP: ("<<fitted_BdDPi_2<<" +/- "<<fitted_BdDPi_2_u<<")"<<std::endl;
	  }


	std::cout<<"===> Number of expected events = fitted yield multiplied by expected misID"<<std::endl;
    


	Float_t N_ev_1=0;
	Float_t N_ev_1_u=0; 
	Float_t N_ev_2=0; 
	Float_t N_ev_2_u=0;
	N_ev_1 = fitted_BdDPi_1*v_lab45_av;
	N_ev_1_u = N_ev_1*(v_lab45_u/v_lab45_av + fitted_BdDPi_1_u/fitted_BdDPi_1)+N_ev_1*0.1;
	N_ev_2 = fitted_BdDPi_2*v_lab45_av;
	N_ev_2_u = N_ev_2*(v_lab45_u/v_lab45_av + fitted_BdDPi_2_u/fitted_BdDPi_2)+N_ev_2*0.1;
	std::cout<<"----------------------------------------------------"<<std::endl;
	std::cout<<"DOWN: ("<<N_ev_1<<" +/- "<<N_ev_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<N_ev_2<<" +/- "<<N_ev_2_u<<")"<<std::endl;
	std::cout<<"----------------------------------------------------"<<std::endl;

	std::cout<<std::endl;
	std::cout<<"Second method: "<<std::endl;
	std::cout<<"===> misID*N("<<nameHypo<<")/N("<<nameMeson<<") ="<<std::endl;
	Float_t N2_ev_1=0;
	Float_t N2_ev_1_u=0;
	N2_ev_1 = rN*v_lab45_av;
	N2_ev_1_u = N2_ev_1*(v_lab45_u/v_lab45_av + rN_u/rN);
	std::cout<<"("<<N2_ev_1<<" +/- "<<N2_ev_1_u<<")"<<std::endl;

	Float_t fitted_BsDsPi_1=0; 
	Float_t fitted_BsDsPi_1_u=0; 
	Float_t fitted_BsDsPi_2=0; 
	Float_t fitted_BsDsPi_2_u=0;
	if( mode2 == "kkpi")
	  {
	    // BDTG> 0.3
	    //fitted_BsDsPi_1   = 1.3690e4;
	    //fitted_BsDsPi_1_u = 1.33e2;
	    //fitted_BsDsPi_2   = 9.6268e3;
	    //fitted_BsDsPi_2_u = 1.10e2;
	    fitted_BsDsPi_1   = 1.3002e4;
            fitted_BsDsPi_1_u = 1.29e2;
            fitted_BsDsPi_2   = 9.1756e3;
            fitted_BsDsPi_2_u = 1.08e2;

	  }
	else if (mode2 == "kpipi")
	  {
	    fitted_BsDsPi_1   = 1.0579e3;
	    fitted_BsDsPi_1_u = 3.52e1;
	    fitted_BsDsPi_2   = 7.2634e2;
	    fitted_BsDsPi_2_u = 2.90e1;
	  }
	std::cout<<"===> Fitted yield to real data "<<nameMeson<<","<<nameDMeson<<std::endl;
	std::cout<<"DOWN: ("<<fitted_BsDsPi_1<<" +/- "<<fitted_BsDsPi_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<fitted_BsDsPi_2<<" +/- "<<fitted_BsDsPi_2_u<<")"<<std::endl;

	std::cout<<"===> Number of expected events = fitted yield multiplied by expected misID"<<std::endl;
	Float_t N3_ev_1=0;
	Float_t N3_ev_1_u=0;
	Float_t N3_ev_2=0;
	Float_t N3_ev_2_u=0;
	
	N3_ev_1 = fitted_BsDsPi_1*N2_ev_1;
	N3_ev_1_u = N3_ev_1*(N2_ev_1_u/N2_ev_1 + fitted_BsDsPi_1_u/fitted_BsDsPi_1);
	
	N3_ev_2 = fitted_BsDsPi_2*N2_ev_1;
	N3_ev_2_u = N3_ev_1*(N2_ev_1_u/N2_ev_1 + fitted_BsDsPi_2_u/fitted_BsDsPi_2);
	std::cout<<"----------------------------------------------------"<<std::endl;
	std::cout<<"DOWN: ("<<N3_ev_1<<" +/- "<<N3_ev_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<N3_ev_2<<" +/- "<<N3_ev_2_u<<")"<<std::endl;
	std::cout<<"----------------------------------------------------"<<std::endl;

    
	std::cout<<std::endl;
	std::cout<<"===> calculations for lab1 "<<std::endl;
	std::cout<<"cal_lab1 = sum of "<<h_lab1_name<<"*"<<heff10_name<<"/"<<heff0_name<<std::endl;
	std::cout<<"DOWN: "<<cal_lab1[0]<<" UP: "<<cal_lab1[1]<<std::endl;
	std::cout<<"cal_lab1/NOE_cut ="<<std::endl;
	Float_t v_lab1_1, v_lab1_2;
	v_lab1_1 = cal_lab1[0]/n_events[0];
	v_lab1_2 = cal_lab1[1]/n_events[1];
	std::cout<<"DOWN: "<<v_lab1_1<<" UP: "<<v_lab1_2<<std::endl;
	Float_t v_lab1_av, v_lab1_u;
	v_lab1_av = (v_lab1_1+v_lab1_2)/2;
	v_lab1_u = pow((pow(v_lab1_1-v_lab1_av,2)+pow(v_lab1_2-v_lab1_av,2))/2,0.5)*1.414214;
	std::cout<<"= ("<<v_lab1_av*100<<" +/- "<<v_lab1_u*100<<")%"<<std::endl;
	
	std::cout<<std::endl;
	std::cout<<"===> misID for K mode"<<std::endl;
	std::cout<<"result_K = result*cal_lab1/NOE_cut"<<std::endl;
	Float_t v_lab1_all, v_lab1_all_u;
	v_lab1_all = v_lab1_av*v_lab45_av;
	v_lab1_all_u = v_lab1_all*(v_lab1_u/v_lab1_av +v_lab45_u/v_lab45_av);
	std::cout<<"= ("<<v_lab1_all*100<<" +/- "<<v_lab1_all_u*100<<")%"<<std::endl;
    
	std::cout<<"===> Number of expected events for K mode"<<std::endl;
	std::cout<<"First method: "<<std::endl;
	std::cout<<"N_events_K = result_K*fitted_yield_BdPi/15"<<std::endl;

	Float_t NK_ev_1, NK_ev_1_u, NK_ev_2, NK_ev_2_u;
	NK_ev_1 = fitted_BdDPi_1*v_lab1_all/15;
	NK_ev_1_u = NK_ev_1*(v_lab1_all_u/v_lab1_all + fitted_BdDPi_1_u/fitted_BdDPi_1)+NK_ev_1*0.1;
	NK_ev_2 = fitted_BdDPi_2*v_lab1_all/15;
	NK_ev_2_u = NK_ev_2*(v_lab1_all_u/v_lab1_all + fitted_BdDPi_2_u/fitted_BdDPi_2)+NK_ev_2*0.1;
	std::cout<<"----------------------------------------------------"<<std::endl;
	std::cout<<"DOWN: ("<<NK_ev_1<<" +/- "<<NK_ev_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<NK_ev_2<<" +/- "<<NK_ev_2_u<<")"<<std::endl;
	std::cout<<"----------------------------------------------------"<<std::endl;
	
	std::cout<<std::endl;
	std::cout<<"Second method: "<<std::endl;
	std::cout<<"===> result_K*N("<<nameHypo<<")/N("<<nameMeson<<")/15 ="<<std::endl;
	Float_t NK2_ev_1, NK2_ev_1_u;
	NK2_ev_1 = rN*v_lab1_all/15;
	NK2_ev_1_u = NK2_ev_1*(v_lab1_all_u/v_lab1_all + rN_u/rN);
	std::cout<<"("<<NK2_ev_1<<" +/- "<<NK2_ev_1_u<<")"<<std::endl;
	
	std::cout<<"===> Number of expected events = fitted yield multiplied by expected misID(=result_K)"<<std::endl;
	Float_t NK3_ev_1, NK3_ev_1_u, NK3_ev_2, NK3_ev_2_u;
	NK3_ev_1 = fitted_BsDsPi_1*NK2_ev_1;
	NK3_ev_1_u = NK3_ev_1*(NK2_ev_1_u/NK2_ev_1 + fitted_BsDsPi_1_u/fitted_BsDsPi_1);

	NK3_ev_2 = fitted_BsDsPi_2*NK2_ev_1;
	NK3_ev_2_u = NK3_ev_1*(NK2_ev_1_u/NK2_ev_1 + fitted_BsDsPi_2_u/fitted_BsDsPi_2);
	std::cout<<"----------------------------------------------------"<<std::endl;
	std::cout<<"DOWN: ("<<NK3_ev_1<<" +/- "<<NK3_ev_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<NK3_ev_2<<" +/- "<<NK3_ev_2_u<<")"<<std::endl;
	std::cout<<"----------------------------------------------------"<<std::endl;
      }
    else
      {

	
	std::cout<<"===> misID ="<<std::endl;
        Float_t v_lab1_av, v_lab1_u, v_lab1_1, v_lab1_2;
	v_lab1_1 = cal_lab1[0]*ratio[0]/n_events[0];
	v_lab1_2 = cal_lab1[1]*ratio[1]/n_events[1];
        v_lab1_av = (v_lab1_1+v_lab1_2)/2;
        v_lab1_u = pow((pow(v_lab1_1-v_lab1_av,2)+pow(v_lab1_2-v_lab1_av,2))/2,0.5)*1.414214;
        std::cout<<"("<<v_lab1_av*100<<" +/- "<<v_lab1_u*100<<")%"<<std::endl;

        Float_t fitted_BsDsPi_1=0; 
	Float_t fitted_BsDsPi_1_u=0;  
	Float_t fitted_BsDsPi_2=0; 
	Float_t fitted_BsDsPi_2_u=0;
        if( mode2 == "kkpi")
          {
	    fitted_BsDsPi_1   = 1.3002e4;
            fitted_BsDsPi_1_u = 1.29e2;
            fitted_BsDsPi_2   = 9.1756e3;
            fitted_BsDsPi_2_u = 1.08e2;
          }
        else if (mode2 == "kpipi")
	  {
	    fitted_BsDsPi_1   = 1.0579e3;
	    fitted_BsDsPi_1_u = 3.52e1;
            fitted_BsDsPi_2   = 7.2634e2;
            fitted_BsDsPi_2_u = 2.90e1;
	  }
	else if (mode2 == "pipipi")
	  {
	    fitted_BsDsPi_1   = 2.3101e3;
            fitted_BsDsPi_1_u = 5.12e1;
            fitted_BsDsPi_2   = 1.6758e3;
            fitted_BsDsPi_2_u = 4.34e1;
	  }
	
	std::cout<<"===> Number of expected events = fitted yield multiplied by expected misID"<<std::endl;

        Float_t N_ev_1, N_ev_1_u, N_ev_2, N_ev_2_u;
        N_ev_1 = fitted_BsDsPi_1*v_lab1_av;
        N_ev_1_u = N_ev_1*(v_lab1_u/v_lab1_av + fitted_BsDsPi_1_u/fitted_BsDsPi_1);
        N_ev_2 = fitted_BsDsPi_2*v_lab1_av;
        N_ev_2_u = N_ev_2*(v_lab1_u/v_lab1_av + fitted_BsDsPi_2_u/fitted_BsDsPi_2);
        std::cout<<"----------------------------------------------------"<<std::endl;
        std::cout<<"DOWN: ("<<N_ev_1<<" +/- "<<N_ev_1_u<<")"<<std::endl;
        std::cout<<"UP: ("<<N_ev_2<<" +/- "<<N_ev_2_u<<")"<<std::endl;
        std::cout<<"----------------------------------------------------"<<std::endl;


      }
	
          
  }

 

  RooWorkspace* Blabla(TString& filesDir, TString& sig, 
		       int PIDcut,
		       double Pcut_down, double Pcut_up,
		       double BDTGCut,
		       double Dmass_down, double Dmass_up,
		       TString &mVar, TString& mProbVar,
		       TString& mode, Bool_t MC, TString& hypo )

  {
    std::cout<<"[INFO] ==> GeneralUtils::ExpectedYield(...). Calculate expected yield misID backgrouds"<<std::endl;
    std::cout<<"name of config file: "<<filesDir<<std::endl;
    std::cout<<"PIDK cut: "<< PIDcut<<std::endl;
    std::cout<<"BDTGResponse cut: "<<BDTGCut<<std::endl;
    std::cout<<"Bachelor momentum range: ("<<Pcut_down<<","<<Pcut_up<<")"<<std::endl;
    std::cout<<"D(s) mass range: ("<<Dmass_down<<","<<Dmass_up<<")"<<std::endl;
    std::cout<<"Name of observable: "<<mVar<<std::endl;
    std::cout<<"Name of PID variable: "<<mProbVar<<std::endl;
    std::cout<<"Data mode: "<<mode<<std::endl;

    RooWorkspace* work = NULL;
    work =  new RooWorkspace("workspace","workspace");
    

    //Double_t number=0;

    std::cout<<"=====> Preparing signal from MC"<<std::endl;

    double BMassRange[2];
    if ( MC == false )
      {
	BMassRange[0] = 5200; BMassRange[1]=5400;
      }
    else
      {
	BMassRange[0] = 5100; BMassRange[1]=5800;
      }
    std::cout<<"B(s) mass range: ("<<BMassRange[0]<<","<<BMassRange[1]<<")"<<std::endl;
    std::vector <std::string> FileName;
    ReadOneName(filesDir,FileName,sig, true);

    TTree* tree[2];

    for( int i=0; i<2; i++)
      {
        tree[i] = NULL;
	tree[i] = ReadTreeData(FileName,i, true);
      }

    TCut P_cut = Form("lab1_P > %f && lab1_P < %f",Pcut_down,Pcut_up);
    TCut BDTG_cut = Form("BDTGResponse_1 > %f",BDTGCut);
    TCut PID_cut;
    if (hypo == "DsK")
      {
	PID_cut = Form("%s > %d",mProbVar.Data(),PIDcut);
      }
    else if (hypo == "DsPi")
      {
	PID_cut = Form("%s < %d",mProbVar.Data(),PIDcut);
      }
    TCut FDCHI2 = "lab2_FDCHI2_ORIVX > 2"; 
    TCut Hypo;

    TCut All;
    if (MC == false ) 
      {
	All = P_cut&&BDTG_cut&&PID_cut&&FDCHI2;
      }
    else
      {
	TCut MCTriggerCut="lab0Hlt1TrackAllL0Decision_TOS && (lab0Hlt2Topo2BodyBBDTDecision_TOS || lab0Hlt2Topo3BodyBBDTDecision_TOS || lab0Hlt2Topo4BodyBBDTDecision_TOS)";
	TCut MCBsIDCut;

	TCut MCCut, MCCut1;
	TCut MCD = Form("lab2_MM > %f && lab2_MM < %f",Dmass_down,Dmass_up);
	TCut MCB = Form("%s > %f && %s < %f",mVar.Data(),BMassRange[0],mVar.Data(),BMassRange[1]);

	if ( (mode.Contains("Bs") != -1) || ( (mode.Contains("Ds") != -1) && (mode.Contains("Dst") == -1))) {
	  MCCut1 = "(lab2_BKGCAT < 30 || lab2_BKGCAT == 50)";
	}
	else { MCCut1 = "lab2_BKGCAT == 30"; }
	TCut PionHypo = "lab1_M < 200";
	TCut KaonHypo = "lab1_M > 200";
	
	if ( hypo == "DsPi") 
	  {
	    Hypo = PionHypo;  
	    MCBsIDCut = "abs(lab1_ID)==211 && abs(lab5_ID)==321 && abs(lab3_ID)==211 && abs(lab4_ID)==321 && (lab5_ID/abs(lab5_ID))\
 != (lab1_ID/abs(lab1_ID)) && lab0_BKGCAT < 60";
	    All = MCCut1&&MCTriggerCut&&MCBsIDCut&&P_cut&&BDTG_cut&&MCD&&Hypo;
	  }
	if ( hypo == "DsK")
	  {
	    Hypo = KaonHypo;
	    MCBsIDCut = "abs(lab1_ID)==321 && abs(lab5_ID)==321 && abs(lab3_ID)==211 && abs(lab4_ID)==321 && (lab5_ID/abs(lab5_ID))\
 != (lab1_ID/abs(lab1_ID)) && lab0_BKGCAT < 60";
	    All = MCCut1&&MCTriggerCut&&MCBsIDCut&&P_cut&&BDTG_cut&&MCD&&Hypo;
	    
	  }
      }


    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);
    //RooRealVar* lab0_MMdsk = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);

    TString smp[2];
    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], true);
    }
    
    TTree* tr[2];
    RooDataSet* dataSetMC[2];
    //RooDataSet* dataSetMCDsK[2];
    //RooFitResult* result[2];
    Int_t n_ev[2];
    Int_t n_wm[2];
    //Int_t n_evdsk[2];
    for(int i=0; i<2; i++)
      {
        tr[i] = NULL;
	tr[i] = TreeCut(tree[i],All,smp[i],mode, true);
        
	Float_t  lab0_MM2;
	tr[i]->SetBranchAddress(mVar.Data(), &lab0_MM2);
	TString s = mode+"_"+smp[i];
	n_wm[i] = tr[i]->GetEntries();

	TString name="dataSetMC"+s;
	dataSetMC[i] = NULL;
	dataSetMC[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MM));
	
	/*
	if ( MC == true )
	  {
	    TString name="dataSetMCDsK"+s;
	    dataSetMCDsK[i] = NULL;
	    dataSetMCDsK[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*lab0_MMdsk));
	  }
	
	Float_t lab1_P3, lab2_P3;
	Float_t lab1_PX3, lab1_PY3, lab1_PZ3;
	Float_t lab2_PX3, lab2_PY3, lab2_PZ3;
	Float_t lab2_MM3;

	Float_t masshypo;
	Double_t w;
	
	tr[i]->SetBranchAddress("lab1_P",  &lab1_P3);
	tr[i]->SetBranchAddress("lab1_PX", &lab1_PX3);
	tr[i]->SetBranchAddress("lab1_PY", &lab1_PY3);
	tr[i]->SetBranchAddress("lab1_PZ", &lab1_PZ3);
	
	tr[i]->SetBranchAddress("lab2_P",  &lab2_P3);
	tr[i]->SetBranchAddress("lab2_PX", &lab2_PX3);
	tr[i]->SetBranchAddress("lab2_PY", &lab2_PY3);
	tr[i]->SetBranchAddress("lab2_PZ", &lab2_PZ3);
	*/

	for (Long64_t jentry=0; jentry<tr[i]->GetEntries(); jentry++)
	  {
	    tr[i]->GetEntry(jentry);
	    if ( MC == true) {lab0_MM2 = lab0_MM2-3.9;}
	    if (lab0_MM2 > BMassRange[0] && lab0_MM2 < BMassRange[1])
	      {
		lab0_MM->setVal(lab0_MM2);
		dataSetMC[i]->add(RooArgSet(*lab0_MM));
		/*
		if (MC == true)
		  {
		    masshypo = (Float_t)sqrt(pow(sqrt(pow(493.677,2)+pow(lab1_P3,2))+sqrt(pow(lab2_MM3,2)+pow(lab2_P3,2)),2)
					     -pow(lab1_PX3+lab2_PX3,2)
					     -pow(lab1_PY3+lab2_PY3,2)
					     -pow(lab1_PZ3+lab2_PZ3,2)); // change hypo Pi->K

		    if (masshypo > BMassRange[0] && masshypo < BMassRange[1])
		      {
			lab0_MMdsk->setVal(masshypo);
			dataSetMCDsK[i]->add(RooArgSet(*lab0_MMdsk));
		      }
		      }*/

	      }
	  }
	SaveDataSet(dataSetMC[i],lab0_MM, smp[i], mode, true);
	std::cout<<"Number of entries: "<<dataSetMC[i]->numEntries()<<std::endl;
	n_ev[i]=dataSetMC[i]->numEntries();
	//n_evdsk[i]=dataSetMCDsK[i]->numEntries();
	work->import(*dataSetMC[i]);
    
      }
    
 
    if(MC == true)
      {
	  Int_t n_gen = 0;
	  Float_t n_proc;
            if( mode == "BsDsPi") { n_gen = 999495;}
	    else if( mode == "BsDsstPi") {n_gen = 524098; }
	    else if( mode == "BsDsRho")  { n_gen = 2019391; }
	    else if( mode == "BsDsstRho") { n_gen =1019191; }
	     
	    
	    n_proc = (Float_t) (n_ev[0]+n_ev[1])/n_gen*100;
	    std::cout<<"------------------------------------------------------"<<std::endl;
	    std::cout<<"Mode: "<<mode<<std::endl;
	    std::cout<<"Under hypo:"<<hypo<<" "<<Hypo<<std::endl;
	    std::cout<<"Number of events: "<<n_wm[0]+n_wm[1]<<std::endl;
	    std::cout<<"Number of envents in mass (5100,5800): "<<n_ev[0]+n_ev[1]<<std::endl;
	    std::cout<<"Percent: NOE/NOE_M = "<<(Float_t)(n_ev[0]+n_ev[1])/(n_wm[0]+n_wm[1])*100<<"%"<<std::endl;
	    std::cout<<"Generated entries: "<<n_gen<<std::endl;
	    std::cout<<"Percent: "<<n_proc<<"%"<<std::endl;
	    std::cout<<"------------------------------------------------------"<<std::endl;
	    
      }	
    return work;
  } 

} //end of namespace
