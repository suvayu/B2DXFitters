//---------------------------------------------------------------------------//
//                                                                           //
//  Mass fit utilities                                                       //
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

//#include "B2DXFitters/icc_fpclass_workaround.h"

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
#include "RooBinning.h"
#include "RooAbsArg.h"
#include "TLeaf.h"
#include "TStyle.h"

// B2DXFitters includes
#include "RooArgSet.h"
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/MassFitUtils.h"
#include "B2DXFitters/DecayTreeTupleSucksFitter.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"
#include "B2DXFitters/PlotSettings.h"
#include "B2DXFitters/MDFitterSettings.h"
#include "B2DXFitters/HistPID1D.h"
#include "B2DXFitters/HistPID2D.h"
#include "B2DXFitters/DLLTagCombiner.h"
#include "B2DXFitters/TagDLLToTagDec.h"
#include "B2DXFitters/TagDLLToTagEta.h"
#include "B2DXFitters/MistagCalibration.h"
#include "B2DXFitters/MCBackground.h"

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

  void InitializeRealObs(TString tB, std::vector <Double_t> &varD, std::vector <Int_t> &varI, std::vector <Float_t> &varF, Bool_t debug)
  {
    tB = tB; 
    varD.push_back(0.0);  varI.push_back(0); varF.push_back(0.0);
    if ( debug == true ) { } 
  }

  Double_t GetValue( TString tB, Double_t &varD, Int_t &varI, Float_t &varF )
  {
    Double_t val = 0;
    if ( tB == "Double_t") { val = varD; }
    else if( tB == "Int_t" ) { val = varI;  }
    else if( tB == "Float_t" ) { val = varF; }
    return val; 

  }

  Double_t SetValRealObs(MDFitterSettings* mdSet, RooArgSet* obs,
		     TString tN, TString tB,
		     Double_t &varD, Int_t &varI, Float_t &varF,
		     TString mode, Double_t shift)
  {
    RooRealVar* obsVar = (RooRealVar*)obs->find(tN.Data()); 
    Double_t val = GetValue(tB, varD, varI, varF); 
    Float_t c = 299792458.0;
    Float_t corr = c/1e9;
    corr = corr; 

    if ( tN != "" )
      {
	if ( tN == mdSet->GetTimeVarOutName() || tN == mdSet->GetTerrVarOutName() )
	  {
	    val = val/corr; 
	  }
	else if ( tN == mdSet->GetPIDKVarOutName() )
	  {
	    if ( mode.Contains("Pi") == true )
	      {
	        val = -val; 
	      }
	    else
	      {
		val = log(val); 
	      }
	  }
	else if ( tN == mdSet->GetTracksVarOutName() || tN == mdSet->GetMomVarOutName() || tN == mdSet->GetTrMomVarOutName() )
	  {
	    val = log(val); 
	  }
	else if ( tN == mdSet->GetMassBVarOutName() )
	  {
	    //    std::cout<<"val: "<<val<<" shift: "<<shift;
	    val = val + shift; 
	    //std::cout<<" val+shift: "<<val<<std::endl; 
	  }
	obsVar->setVal(val);
      }
    return val; 
  }
  
  
  Double_t SetValCatObs(MDFitterSettings* mdSet, RooArgSet* obs,
		    TString tN, TString tB,
		    Double_t &varD, Int_t &varI, Float_t &varF)
  {
    RooCategory* obsCat = (RooCategory*)obs->find(tN.Data());  
    Double_t val = GetValue(tB, varD, varI, varF);
    if ( tN != "" )
      {
	if ( tN == mdSet->GetIDVarOutName() )
	  {
	    if ( val > 0 ) { obsCat->setIndex(1); } else {obsCat->setIndex(-1); }
	  }
	else 
	  {
	    if ( val > 0.1) { obsCat->setIndex(1); }
	    else if ( val < -0.1) { obsCat->setIndex(1); }
	    else { obsCat->setIndex(0); } 
	  }
      }
    return val; 
  }

  void SetBranchAddress(TTree* tr, TString tB, TString tN, 
			Double_t &varD, Int_t &varI, Float_t &varF,
			Bool_t debug)
  {
    if ( tB == "Double_t") {  tr->SetBranchAddress(tN.Data(),    &varD); }
    else if( tB == "Int_t" ) { tr->SetBranchAddress(tN.Data(),    &varI); }
    else if( tB == "Float_t" ) { tr->SetBranchAddress(tN.Data(),    &varF); }
    if ( debug  ) { } 
  }

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
			   MDFitterSettings* mdSet,
			   TString& mode,
			   PlotSettings* plotSet,
			   RooWorkspace* workspace, 
			   bool debug)
  {
  
    RooAbsData::setDefaultStorageType(RooAbsData::Tree);
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainData(...). Start preparing DataSet "<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	
      }
    
    RooWorkspace* work = NULL;
    if (workspace == NULL ) { work =  new RooWorkspace("workspace","workspace"); }
    else { work = workspace; }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }
    RooArgSet* obs = mdSet->GetObsSet();
    obs->Print("v"); 
    std::vector <TString> tN = mdSet->GetVarNames();

    std::vector <std::string> FileName;
    ReadOneName(filesDir,FileName,sig, debug);
    TTree* tree[2];
    for( int i=0; i<2; i++)
      {
	tree[i] = NULL;
        tree[i] = ReadTreeData(FileName,i, debug);
      }
    
    //Read sample (means down or up)  from path // 
    //Read mode (means D mode: kkpi, kpipi or pipipi) from path //
    TString smp[2], md[2], y[2];

    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
      md[i-1] = CheckDMode(sig, debug);
      y[i-1] = CheckDataYear(sig, debug);
      if ( md[i-1] == "kkpi" || md[i-1] == ""){ md[i-1] = CheckKKPiMode(sig, debug);}
      if ( y[i-1] != "") { y[i-1] = "_"+y[i-1]; }
    }
    
    //Set PID cut depends on mode// 
    TCut PID_cut;  
   if( mode.Contains("Pi") )    { 
      PID_cut = Form("%s < %lf",mdSet->GetPIDKVar().Data(), mdSet->GetPIDKRangeDown()); 
      if ( debug == true)  std::cout<<"Mode with Pi"<<std::endl;}
    else if (mode.Contains("K")) { 
      PID_cut = Form("%s > %lf",mdSet->GetPIDKVar().Data(), exp(mdSet->GetPIDKRangeDown())); 
      if ( debug == true)  std::cout<<"Mode with K"<<std::endl; }
    else { if ( debug == true) std::cout<<"[ERROR] Wrong mode"; return work; }

    //Set other cuts//
    TCut P_cut      = mdSet->GetCut(mdSet->GetMomVar()); 
    TCut PT_cut     = mdSet->GetCut(mdSet->GetTrMomVar()); 
    TCut nTr_cut    = mdSet->GetCut(mdSet->GetTracksVar()); 
    TCut BDTG_cut   = mdSet->GetCut(mdSet->GetBDTGVar()); 
    TCut mass_cut   = mdSet->GetCut(mdSet->GetMassBVar()); 
    TCut massD_cut  = mdSet->GetCut(mdSet->GetMassDVar()); 
    TCut Time_cut = mdSet->GetCut(mdSet->GetTimeVar());
    TCut Terr_cut = mdSet->GetCut(mdSet->GetTerrVar());
    
    TCut addCuts = (TCut)mdSet->GetDataCuts(md[0]); 
    std::cout<<"[INFO] Data cuts from MDFit: "<<addCuts<<std::endl; 

    TCut All_cut = "";
    if ( mode.Contains("Comb") == true )
      {
	All_cut = addCuts;
      }
    else
      {
	All_cut = PID_cut&&P_cut&&BDTG_cut&&mass_cut&&massD_cut&&PT_cut&&nTr_cut&&Time_cut&&Terr_cut&&addCuts;
      }
    if( debug == true) std::cout<<All_cut<<std::endl;

    RooDataSet*  dataSet[2];
   
    // Create Data Set //
    for (int i = 0; i< 2; i++){
      TString name = "dataSet"+mode+"_"+smp[i]+"_"+md[i]+y[i];
      dataSet[i] = new RooDataSet(name.Data(),name.Data(), *obs);
      
      TTree* treetmp=NULL;
      treetmp = TreeCut(tree[i],All_cut,smp[i],mode, debug);
      
      std::vector <TString> tB; 		
      std::vector <Double_t> varD; std::vector <Int_t> varI; std::vector <Float_t> varF;
      for(unsigned int i = 0; i<tN.size(); i++ )
	{
	  if ( tN[i] != "" ){ tB.push_back(treetmp->GetLeaf(tN[i].Data())->GetTypeName()); }
	  else { tB.push_back(""); }
	  InitializeRealObs(tB[i], varD, varI, varF, debug); 
	}
      
      for(unsigned int k =0; k<tN.size(); k++ )
	{
	  SetBranchAddress(treetmp, tB[k], tN[k], varD[k], varI[k], varF[k], debug);
	}
      for (Long64_t jentry=0; jentry<treetmp->GetEntries(); jentry++) {
	treetmp->GetEntry(jentry);
	for(unsigned k = 0; k < tN.size(); k++)
	  {
	 
	    Bool_t cat = false;
	    if ( tN[k] == mdSet->GetIDVar() ) { cat = true; }
	    if(  mdSet->CheckTagVar() == true )                                                                                                                                       
	      {                                                                                                                                                                       
		for(int m = 0; m<mdSet->GetNumTagVar(); m++)                                                                                                                          
		  {                                                               
		    if ( tN[k] ==  mdSet->GetTagVar(m) ) 
		      {
			cat = true;
			break;
		      }
		  }
	      }
	    TString name = mdSet->GetVarOutName(tN[k]); 
	    if ( cat == true ) { SetValCatObs(mdSet, obs, name , tB[k], varD[k], varI[k], varF[k]); }
	    else{ SetValRealObs(mdSet, obs, name, tB[k], varD[k], varI[k], varF[k], mode); }
	  }
	if ( mode.Contains("Comb") == true )
	  {
	    if ( jentry < 10000 )
	      {
		dataSet[i]->add(*obs);
	      }
	  }
	else
	  {
	    dataSet[i]->add(*obs);
	  }
      }
		
      if ( debug == true)
	{
	  if ( dataSet[i] != NULL  ){
	    std::cout<<"[INFO] ==> Create "<<dataSet[i]->GetName()<<std::endl;
	    std::cout<<"Sample "<<smp[i]<<" number of entries: "<<tree[i]->GetEntries()
		     <<" in data set: "<<dataSet[i]->numEntries()<<std::endl;
	  } else { std::cout<<"Error in create dataset"<<std::endl; }
	}
      
      RooArgList* tagList= new RooArgList();
      RooArgList* tagOmegaList = new RooArgList();
      
      Int_t tagNum = mdSet->GetNumTagVar();
      Int_t mistagNum = mdSet->GetNumTagOmegaVar();
      
      if (tagNum != mistagNum)
	{
	  std::cout<<"[ERROR] number of tagging decisions  different from number of mistag distributions"<<std::endl;
	  return NULL;
	}
      else
	{
	  if (debug == true) { std::cout<<"[INFO] Number of taggers "<<tagNum<<std::endl;}
	}
      
      MistagCalibration* calibMistag[tagNum];
      RooRealVar* p0[tagNum];
      RooRealVar* p1[tagNum];
      RooRealVar* av[tagNum];
      
      if(  mdSet->CheckTagVar() == true )
	{
	  for(int k = 0; k<mdSet->GetNumTagVar(); k++)
	    {
	      RooCategory* tagVar = (RooCategory*)obs->find(mdSet->GetTagVarOutName(k)); 
	      tagList->add(*tagVar);
	    }
	  
	  if(  mdSet->CheckTagOmegaVar() == true )
	    {
	      for(int k = 0; k<mdSet->GetNumTagOmegaVar(); k++)
		{
		  RooRealVar* tagOmegaVar = (RooRealVar*) obs->find(mdSet->GetTagOmegaVarOutName(k));
		  std::cout<<"[INF0] Calibration: p0="<<mdSet->GetCalibp0(k)<<" p1: "<<mdSet->GetCalibp1(k)<<" av: "<<mdSet->GetCalibAv(k)<<std::endl;
		  p0[k] = new RooRealVar(Form("p0_%d",k),Form("p0_%d",k),mdSet->GetCalibp0(k));
		  p1[k] = new RooRealVar(Form("p1_%d",k),Form("p1_%d",k),mdSet->GetCalibp1(k));
		  av[k] = new RooRealVar(Form("av_%d",k),Form("av_%d",k),mdSet->GetCalibAv(k));
		  TString nameCalib = mdSet->GetVarOutName(mdSet->GetTagOmegaVar(k))+"_calib";
		  calibMistag[k] = new MistagCalibration(nameCalib.Data(), nameCalib.Data(), 
							 *tagOmegaVar, *p0[k], *p1[k], *av[k]);
		  dataSet[i]->addColumn(*calibMistag[k]);
		  tagOmegaList->add(*calibMistag[k]);
		}
	    }
	  
	  /*
	    if( debug == true )
	    {
	    std::cout<<"[INFO] Taggers list: "<<std::endl;
	    tagList->Print("v");
	    std::cout<<"[INFO] Mistags list: "<<std::endl;
	    tagOmegaList->Print("v");
	    }
	  */
	  DLLTagCombiner* combiner = new DLLTagCombiner("tagCombiner","tagCombiner",*tagList,*tagOmegaList);
	  TagDLLToTagDec* tagDecComb = new TagDLLToTagDec("tagDecComb","tagDecComb",*combiner,*tagList);
	  TagDLLToTagEta* tagOmegaComb = new TagDLLToTagEta("tagOmegaComb","tagOmegaComb",*combiner);
	  
	  dataSet[i]->addColumn(*tagDecComb);
	  dataSet[i]->addColumn(*tagOmegaComb);
	}
      
      TString s = smp[i]+"_"+md[i];
      
      if ( plotSet->GetStatus()  == true )
	{
	  for (unsigned int k = 0; k<tN.size(); k++ )
	    {
	      
	      Bool_t cat = false;
	      if ( tN[k] == mdSet->GetIDVar() ) { cat = true; }
	      if(  mdSet->CheckTagVar() == true )
		{
		  for(int m = 0; m<mdSet->GetNumTagVar(); m++)
		    {
		      if ( tN[k] ==  mdSet->GetTagVar(m) )
			{
			  cat = true;
			  break;
			}
		    }
		}
	      if ( cat == false )
		{
		  TString name = mdSet->GetVarOutName(tN[k]);
		  RooRealVar* var = (RooRealVar*)obs->find(name.Data());  
		  //std::cout<<"var: "<<var->GetName()<<std::endl; 
		  SaveDataSet(dataSet[i], var, s, mode, plotSet, debug);
		}
	    }
	}
      
      work->import(*dataSet[i]);
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
				   MDFitterSettings* mdSet,
				   TString& mode,
				   RooWorkspace* workspace, 
				   PlotSettings* plotSet,
				   bool pdf,
				   bool debug)
  {
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainMissForBsDsK(...). Obtain Bs->DsPi under Bs->DsK  "<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"Mode: "<<mode<<std::endl;
      }

    RooWorkspace* work = NULL;
    if (workspace == NULL ) { work =  new RooWorkspace("workspace","workspace"); }
    else { work = workspace; }
    
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    RooRealVar* lab0_MM       = mdSet->GetObs(mdSet->GetMassBVar());
    RooRealVar* lab0_TAUERR   = mdSet->GetObs(mdSet->GetTerrVar());
    RooRealVar* lab2_MM       = mdSet->GetObs(mdSet->GetMassDVar());
    RooRealVar* lab1_PIDK     = mdSet->GetObs(mdSet->GetPIDKVar());
    RooRealVar* nTracks       = mdSet->GetObs(mdSet->GetTracksVar(), false, true);
    RooRealVar* lab1_P        = mdSet->GetObs(mdSet->GetMomVar(), false, true);
    RooRealVar* lab1_PT       = mdSet->GetObs(mdSet->GetTrMomVar(), false, true);
    //RooRealVar* lab0_TAU2  = new RooRealVar("lab0_TAU","lab0_TAU",0.2,     15.0);
    //RooRealVar* lab0_TAU2ERR  = new RooRealVar("lab0_TAUTERR","lab0_TAUTERR", 0.01,  0.1 );

    RooArgSet* obs = new RooArgSet(*lab0_MM,*lab2_MM,*lab1_PIDK,
				   *lab1_PT, *lab1_P, *nTracks);
    
    obs->add(*lab0_TAUERR); 
    //obs->add(*lab0_TAU2);
    //obs->add(*lab0_TAU2ERR);

    
    std::vector <std::string> FileName;
    TString PID = "#PID";
    TString PID2 = "#PID2";
    ReadOneName(filesDir,FileName,sig,debug);
     
    TTree* tree[2];

    for( int i=0; i<2; i++)
      {
	tree[i] = NULL;
	tree[i] = ReadTreeData(FileName,i,debug);
      }

    // Read sample (means down or up)  from path //
    // Read mode (means D mode: kkpi, kpipi or pipipi) from path //
    TString smp[2], md[2], y[2];

    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
      md[i-1] = CheckDMode(FileName[i], debug);
      y[i-1] = CheckDataYear(sig, debug);
      if ( md[i-1] == "kkpi" || md[i-1] == ""){ md[i-1] = CheckKKPiMode(FileName[i], debug);}
      if ( y[i-1] != "") { y[i-1] = "_"+y[i-1]; }
    }

    //Read necessary misID histograms from file// 
    TString nameHistMiss = Form("MyPionMisID_%d;1",mdSet->GetPIDBach());
    HistPID1D hmisID(nameHistMiss, nameHistMiss, filesDir, PID, PID2);
    TString nameHistEff = "MyPionEff_0";
    HistPID1D heff(nameHistEff, nameHistEff, filesDir, PID, PID2);
    if ( debug == true ) { std::cout<<hmisID<<std::endl; std::cout<<heff<<std::endl; }
    
    //Set cuts//
    TCut PID_cut = Form("%s < 0",mdSet->GetPIDKVar().Data());  

    TCut P_cut      = mdSet->GetCut(mdSet->GetMomVar());
    TCut PT_cut     = mdSet->GetCut(mdSet->GetTrMomVar());
    TCut nTr_cut    = mdSet->GetCut(mdSet->GetTracksVar());
    TCut BDTG_cut   = mdSet->GetCut(mdSet->GetBDTGVar());
        
    TCut mass_cut   = Form("%s > 5300 && %s < 5420",
			   mdSet->GetMassBVar().Data(), mdSet->GetMassBVar().Data());

    TCut FDCHI2 = "";
    if( md[0] == "kkpi" || md[0] == "nonres" || md[0] == "kstk" || md[0] == "phipi" ) {  FDCHI2 = "lab2_FDCHI2_ORIVX > 2"; }
    else{  FDCHI2 = "lab2_FDCHI2_ORIVX > 9"; }

    TCut All_cut = mass_cut&&P_cut&&BDTG_cut&&PID_cut&&PT_cut&&nTr_cut&&FDCHI2;
    if( debug == true) std::cout<<All_cut<<std::endl;
   
    RooRealVar* weights;
    RooDataSet* dataSet[2];
    RooKeysPdf* pdfDataMiss[2];
    RooKeysPdf* pdfDataDMiss[2];

    TString namew = "weights";
    weights = new RooRealVar(namew.Data(), namew.Data(), 0.0, 1.0 );  // create weights //
    obs->add(*weights);

    Float_t c = 299792458.0;
    Float_t corr = 1e9/c;

    for (int i = 0; i<2; i++){
      
      TString s = smp[i]+"_"+md[i]+y[i];
      
      dataSet[i] = NULL;
      pdfDataMiss[i] = NULL;
      pdfDataDMiss[i] = NULL;
      TTree* treetmp = NULL;
      
      TString name = "dataSet_Miss_"+s;
      dataSet[i] = new RooDataSet(name.Data(),name.Data(),*obs,namew.Data()); //create new data set //
      
      treetmp = TreeCut(tree[i],All_cut, smp[i], mode, debug);  // obtain new tree after applied all cuts //

      // Load all necessary variables to change hypo Pi->K from tree //
      Double_t lab1_P3, lab2_P3, lab1_PX3, lab1_PY3, lab1_PZ3, lab2_PX3, lab2_PY3, lab2_PZ3;
            
      Float_t masshypo;
      Double_t w, wE, wA;
      
      treetmp->SetBranchAddress("lab1_P",  &lab1_P3);
      treetmp->SetBranchAddress("lab1_PX", &lab1_PX3);
      treetmp->SetBranchAddress("lab1_PY", &lab1_PY3);
      treetmp->SetBranchAddress("lab1_PZ", &lab1_PZ3);
      
      treetmp->SetBranchAddress("lab2_P",  &lab2_P3);
      treetmp->SetBranchAddress("lab2_PX", &lab2_PX3);
      treetmp->SetBranchAddress("lab2_PY", &lab2_PY3);
      treetmp->SetBranchAddress("lab2_PZ", &lab2_PZ3);

      Float_t lab0_TAUERR3[10];
      Double_t lab2_MM3, lab1_PIDK3;
      Int_t nTracks3;
      Double_t lab1_PT3;
      //Double_t lab0_TAU23, lab0_TAU2TERR3;

      //treetmp->SetBranchAddress("lab0_TAU",     &lab0_TAU23);
      //treetmp->SetBranchAddress("lab0_TAUERR",  &lab0_TAU2TERR3);
      treetmp->SetBranchAddress(mdSet->GetTerrVar().Data(), &lab0_TAUERR3);
      treetmp->SetBranchAddress(mdSet->GetMassDVar().Data(),    &lab2_MM3);
      treetmp->SetBranchAddress(mdSet->GetPIDKVar().Data(),     &lab1_PIDK3);
      treetmp->SetBranchAddress(mdSet->GetTracksVar().Data(),   &nTracks3);
      treetmp->SetBranchAddress(mdSet->GetMomVar().Data(),      &lab1_P3);
      treetmp->SetBranchAddress(mdSet->GetTrMomVar().Data(),    &lab1_PT3);
      
      for (Long64_t jentry=0; jentry<treetmp->GetEntries(); jentry++) {
	treetmp->GetEntry(jentry);
		
	masshypo = (Float_t)std::sqrt(std::pow(std::sqrt(std::pow(493.677,2)+std::pow(lab1_P3,2))+std::sqrt(std::pow(lab2_MM3,2)+std::pow(lab2_P3,2)),2)
				      -std::pow(lab1_PX3+lab2_PX3,2)
				      -std::pow(lab1_PY3+lab2_PY3,2)
				      -std::pow(lab1_PZ3+lab2_PZ3,2)); // change hypo Pi->K

	
	if (masshypo > mdSet->GetMassBRangeDown() && masshypo < mdSet->GetMassBRangeUp() 
	    && lab2_MM3 > mdSet->GetMassDRangeDown()  && lab2_MM3 < mdSet->GetMassBRangeUp()) 
	  {  // accept event only is in range, usually 5100,5800 // 
	   
	    w = hmisID.GetWeight(lab1_P3, smp[i]);
	    wE = heff.GetWeight(lab1_P3, smp[i]); 

	    if( wE == 0 ) { wA = 0; } else { wA = w/wE;}
	    weights->setVal(wA);
	    lab0_MM->setVal(masshypo);
	    lab2_MM->setVal(lab2_MM3);
	    lab1_P->setVal(log(lab1_P3));
	    lab1_PIDK->setVal(log(lab1_PIDK3));
	    nTracks->setVal(log(nTracks3));
	    lab1_PT->setVal(log(lab1_PT3));
	    //lab0_TAU2->setVal(lab0_TAU23*1000);
	    //lab0_TAU2ERR->setVal(lab0_TAU2TERR3*1000);
	    lab0_TAUERR->setVal(lab0_TAUERR3[0]*corr);
		    
	    dataSet[i]->add(*obs,wA,0);
	  }
	
      }
      
      if ( debug == true)
	{
	  if ( dataSet[i] != NULL ){
	    std::cout<<"[INFO] ==> Create dataSet for missID BsDsPi background"<<std::endl;
	    std::cout<<"Number of events in dataSet: "<<dataSet[i]->numEntries()<<std::endl;
	  } else { std::cout<<"Error in create dataset"<<std::endl; }

	}
      
      // create RooKeysPdf for misID background //
      
      name="PhysBkgBs2DsPiPdf_m_"+s;
      TString name2=name+"_Ds";

      if ( pdf == true )
	{
	  pdfDataMiss[i] = new RooKeysPdf(name.Data(),name.Data(),*lab0_MM,*dataSet[i]);
	  pdfDataDMiss[i] = new RooKeysPdf(name2.Data(),name2.Data(),*lab2_MM,*dataSet[i]);
	  if ( debug == true) 
	    {
	      if( pdfDataMiss[i] != NULL ){ std::cout<<"=====> Create RooKeysPdf for misID BsDsPi: "<<pdfDataMiss[i]->GetName()<<std::endl;}
	      else { std::cout<<"Cannot create RooKeysPdf for BsDsPi under BsDsK."<<std::endl;}
	      
	      if( pdfDataDMiss[i] != NULL ){ std::cout<<"=====> Create RooKeysPdf for Ds mass misID BsDsPi: "<<pdfDataDMiss[i]->GetName()<<std::endl;}
	      else { std::cout<<"Cannot create RooKeysPdf for Ds mass BsDsPi under BsDsK."<<std::endl;}
	      
	    }
	  
	  if (plotSet->GetStatus() == true )
	    {
	      SaveTemplate(dataSet[i], pdfDataMiss[i],  lab0_MM, s, mode, plotSet, debug);
	      SaveTemplate(dataSet[i], pdfDataDMiss[i], lab2_MM, s, mode, plotSet, debug);
	    }
	  work->import(*pdfDataMiss[i]);
	  work->import(*pdfDataDMiss[i]);
	}

      work->import(*dataSet[i]);
           

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
				    TString& hypo, 
				    MDFitterSettings* mdSet,
				    TString& mode,
				    RooWorkspace* workspace, 
				    PlotSettings* plotSet,
				    bool pdf, 
				    bool debug)
  {
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainMissForBsDsK(...). Obtain Bs->DsPi under Bs->DsK  "<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"Mode: "<<mode<<std::endl;
	std::cout<<"Hypo: "<<hypo<<std::endl; 
      }
    
    RooWorkspace* work = NULL;
    if (workspace == NULL ) { work =  new RooWorkspace("workspace","workspace"); }
    else { work = workspace; }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    RooRealVar* lab0_MM       = mdSet->GetObs(mdSet->GetMassBVar());
    RooRealVar* lab0_TAUERR   = mdSet->GetObs(mdSet->GetTerrVar());
    //RooRealVar* lab0_TAG      = mdSet->GetObs(mdSet->GetTagVar());
    //RooRealVar* lab0_TAGOMEGA = mdSet->GetObs(mdSet->GetTagOmegaVar());
    RooRealVar* lab2_MM       = mdSet->GetObs(mdSet->GetMassDVar());
    RooRealVar* lab1_PIDK     = mdSet->GetObs(mdSet->GetPIDKVar());
    RooRealVar* nTracks       = mdSet->GetObs(mdSet->GetTracksVar(), false, true);
    RooRealVar* lab1_P        = mdSet->GetObs(mdSet->GetMomVar(), false, true);
    RooRealVar* lab1_PT       = mdSet->GetObs(mdSet->GetTrMomVar(), false, true);
    //RooRealVar* lab0_TAU2  = new RooRealVar("lab0_TAU","lab0_TAU",0.2,     15.0);
    //RooRealVar* lab0_TAU2ERR  = new RooRealVar("lab0_TAUTERR","lab0_TAUTERR", 0.01,  0.1 );

    RooArgSet* obs = new RooArgSet(*lab0_MM,*lab2_MM,*lab1_PIDK,
                                   *lab1_PT, *lab1_P, *nTracks);

    obs->add(*lab0_TAUERR);
    //obs->add(*lab0_TAU2);
    //obs->add(*lab0_TAU2ERR);


    std::vector <std::string> FileName;
    
    TString PID = "#PID";
    TString PID2 = "#PID2";
    TString PID2m2 = "#PID2m2";
    TString PID2m22 = "#PID2m22";
    
    ReadOneName(filesDir,FileName,sig,debug);
    TTree* tree[2];
    
    for( int i=0; i<2; i++)
      {
	tree[i] = NULL;
	tree[i] = ReadTreeData(FileName,i,debug);
      }

    // Read sample (means down or up)  from path //
    // Read mode (means D mode: kkpi, kpipi or pipipi) from path //
    TString smp[2], md[2], y[2];

    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
      md[i-1] = CheckDMode(FileName[i], debug);
      y[i-1] = CheckDataYear(sig, debug);
      if ( md[i-1] == "kkpi" || md[i-1] == ""){ md[i-1] = CheckKKPiMode(FileName[i], debug);}
      if ( y[i-1] != "") { y[i-1] = "_"+y[i-1]; }
    }

   
    //Read necessary misID histograms from file//
    TString nameHmisID = "MyPionMisID_10"; 
    TString nameHmisIDL = "MyPionMisID_10_pKm5";
    TString nameHeff = "MyKaonEff_5";
    TString nameHeff5 = "MyKaonEff_5";
    TString nameHeff0 = "MyPionEff_5";

    HistPID1D hmisID(nameHmisID, nameHmisID, filesDir, PID, PID2); 
    HistPID1D hmisIDL(nameHmisIDL, nameHmisIDL, filesDir, PID2m2, PID2m22);
    HistPID1D heff(nameHeff, nameHeff, filesDir, PID, PID2);
    HistPID1D heff5(nameHeff5, nameHeff5, filesDir, PID, PID2);
    HistPID1D heff0(nameHeff0, nameHeff0, filesDir, PID, PID2);
    if ( debug == true )
      {
	std::cout<<hmisID<<std::endl;
	std::cout<<hmisIDL<<std::endl;
	std::cout<<heff<<std::endl;
	std::cout<<heff5<<std::endl;
	std::cout<<heff0<<std::endl;
      }
    hmisID.SavePlot(plotSet);
    hmisIDL.SavePlot(plotSet);
    heff.SavePlot(plotSet);
    heff5.SavePlot(plotSet);
    heff0.SavePlot(plotSet);

    //Set cuts//
    TCut PID_cut;
    TCut P_cut      = mdSet->GetCut(mdSet->GetMomVar());
    TCut PT_cut     = mdSet->GetCut(mdSet->GetTrMomVar());
    TCut nTr_cut    = mdSet->GetCut(mdSet->GetTracksVar());
    TCut BDTG_cut   = mdSet->GetCut(mdSet->GetBDTGVar());
    
    TCut mass_cut   = Form("%s > 5200 && %s < 5340",
                           mdSet->GetMassBVar().Data(), mdSet->GetMassBVar().Data());
    
    TCut PIDBach_cut = Form("%s < %f",mdSet->GetPIDKVar().Data(),0.0);
    
    TCut FDCHI2 = "lab2_FDCHI2_ORIVX > 2";

    TCut All_cut = mass_cut&&P_cut&&BDTG_cut&&PT_cut&&nTr_cut&&PIDBach_cut&&FDCHI2;
    if( debug == true) std::cout<<All_cut<<std::endl;
    
    RooRealVar* weights;
    RooDataSet* dataSet[2];
    RooKeysPdf* pdfDataMiss[2];
    RooKeysPdf* pdfDataDMiss[2];

    TString namew = "weights";
    weights = new RooRealVar(namew.Data(), namew.Data(), 0.0, 1.0 );  // create weights //
    obs->add(*weights);
    
    Double_t tmpc[2];
    Float_t w=0.0;

    Float_t c = 299792458.0;
    Float_t corr = 1e9/c;
    
    for (int i = 0; i<2; i++){
      tmpc[i]=0;
      TString s = smp[i]+"_"+md[i]+y[i]; //+"_"+hypo;
      
      pdfDataMiss[i]=NULL;
      pdfDataDMiss[i]=NULL;

      dataSet[i] = NULL;
      TTree* treetmp = NULL;
      
      TString name = "dataSet_Miss_"+s;
      TString namehist ="data_mistag_"+s;
      
      dataSet[i] =  new RooDataSet(name.Data(),name.Data(),*obs,namew.Data()); 
//create new data set //

      treetmp = TreeCut(tree[i],All_cut,smp[i],md[i],debug);  // obtain new tree after applied all cuts //
      //Double_t lab0_TAU23, lab0_TAU2TERR3;
      // Load all necessary variables to change hypo D->Ds from tree //
      Double_t lab1_P2, lab1_PT2;
      Double_t lab1_PX2, lab1_PY2, lab1_PZ2;
      Double_t lab3_PX2, lab3_PY2, lab3_PZ2;
      Double_t lab4_PX2, lab4_PY2, lab4_PZ2;
      Double_t lab5_PX2, lab5_PY2, lab5_PZ2;
      Double_t lab1_M2;
      Double_t masshypo(0.0), phypo(0.0), masshypod(0.0), phypolc(0.0), masshypolb(0.0), p2(0.0);

      //treetmp->SetBranchAddress("lab0_TAU",     &lab0_TAU23);
      //treetmp->SetBranchAddress("lab0_TAUERR",  &lab0_TAU2TERR3);

      treetmp->SetBranchAddress("lab1_P",  &lab1_P2);
      treetmp->SetBranchAddress("lab1_PT", &lab1_PT2);
      treetmp->SetBranchAddress("lab1_PX", &lab1_PX2);
      treetmp->SetBranchAddress("lab1_PY", &lab1_PY2);
      treetmp->SetBranchAddress("lab1_PZ", &lab1_PZ2);
      treetmp->SetBranchAddress("lab1_M",  &lab1_M2);
      
      treetmp->SetBranchAddress("lab3_PX", &lab3_PX2);
      treetmp->SetBranchAddress("lab3_PY", &lab3_PY2);
      treetmp->SetBranchAddress("lab3_PZ", &lab3_PZ2);
      
      treetmp->SetBranchAddress("lab4_PX", &lab4_PX2);
      treetmp->SetBranchAddress("lab4_PY", &lab4_PY2);
      treetmp->SetBranchAddress("lab4_PZ", &lab4_PZ2);
      
      treetmp->SetBranchAddress("lab5_PZ",  &lab5_PZ2);
      treetmp->SetBranchAddress("lab5_PX", &lab5_PX2);
      treetmp->SetBranchAddress("lab5_PY", &lab5_PY2);
      
      Float_t lab0_TAUERR3[10];
      Double_t lab1_PIDK3;
      Int_t  nTracks3;
            
      treetmp->SetBranchAddress(mdSet->GetTerrVar().Data(), &lab0_TAUERR3);
      treetmp->SetBranchAddress(mdSet->GetPIDKVar().Data(),     &lab1_PIDK3);
      treetmp->SetBranchAddress(mdSet->GetTracksVar().Data(),   &nTracks3);
      
      for (Long64_t jentry=0; jentry<treetmp->GetEntries(); jentry++) {
	treetmp->GetEntry(jentry);
	//std::cout<<"3: "<<lab3_PX2<<" "<<lab3_PY2<<" "<<lab3_PZ2<<std::endl;
	//std::cout<<"4: "<<lab4_PX2<<" "<<lab4_PY2<<" "<<lab4_PZ2<<std::endl;
	//std::cout<<"5: "<<lab5_PX2<<" "<<lab5_PY2<<" "<<lab5_PZ2<<std::endl;
	
	TLorentzVector v3, v4, v5;
	TLorentzVector vL3, vL4, vL5;

	v3.SetPx(lab3_PX2); v4.SetPx(lab4_PX2); v5.SetPx(lab5_PX2);
	v3.SetPy(lab3_PY2); v4.SetPy(lab4_PY2); v5.SetPy(lab5_PY2);
	v3.SetPz(lab3_PZ2); v4.SetPz(lab4_PZ2); v5.SetPz(lab5_PZ2);

	vL3.SetPx(lab3_PX2); vL4.SetPx(lab4_PX2); vL5.SetPx(lab5_PX2);
        vL3.SetPy(lab3_PY2); vL4.SetPy(lab4_PY2); vL5.SetPy(lab5_PY2);
        vL3.SetPz(lab3_PZ2); vL4.SetPz(lab4_PZ2); vL5.SetPz(lab5_PZ2);
	
	Double_t E3, E4, E5;
	Double_t EL3, EL4, EL5;
	
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
	      p2 = v4.P();

	      EL3 = sqrt(vL3.P()*vL3.P()+938.2*938.2);
              EL4 = sqrt(vL4.P()*vL4.P()+139.57*139.57);
              EL5 = sqrt(vL5.P()*vL5.P()+493.677*493.677);
              vL3.SetE(E3); vL4.SetE(E4); vL5.SetE(E5);
	      phypolc = vL3.P(); 
	    }
	    else if (k == 1){
	      E3 = sqrt(v3.P()*v3.P()+139.57*139.57);
	      E4 = sqrt(v4.P()*v4.P()+493.677*493.677);
	      E5 = sqrt(v5.P()*v5.P()+493.677*493.677);
	      v3.SetE(E3); v4.SetE(E4); v5.SetE(E5);
	      phypo = v4.P();
	      p2= v3.P();

	      EL3 = sqrt(vL3.P()*vL3.P()+139.57*139.57);
              EL4 = sqrt(vL4.P()*vL4.P()+938.2*938.2);
              EL5 = sqrt(vL5.P()*vL5.P()+493.677*493.677);
              vL3.SetE(EL3); vL4.SetE(EL4); vL5.SetE(EL5);
	      phypolc = vL4.P();
	    }

	    TLorentzVector vd = v3+v4+v5; // build Ds
	    TLorentzVector vL = vL3+vL4+vL5; // build Lc
	    masshypod = vd.M(); 
	    
	    //std::cout<<"massd: "<<masshypod<<std::endl;
	    
	    if (masshypod > mdSet->GetMassDRangeDown() && masshypod < mdSet->GetMassDRangeUp()) //only events which fall into Ds mass window are acceptable
	      {

		masshypo = (Float_t) std::sqrt( std::pow(std::sqrt(std::pow(lab1_M2,2) + std::pow(lab1_P2,2))
							 + std::sqrt(pow(vd.M(),2)+std::pow(vd.P(),2)),2)
						- std::pow(lab1_PX2+vd.Px(),2)-std::pow(lab1_PY2+vd.Py(),2)-std::pow(lab1_PZ2+vd.Pz(),2));  // build Bs
		
		masshypolb = (Float_t) std::sqrt( std::pow(std::sqrt(std::pow(lab1_M2,2) + std::pow(lab1_P2,2))
							 + std::sqrt(pow(vL.M(),2)+std::pow(vd.P(),2)),2)
                                                - std::pow(lab1_PX2+vd.Px(),2)-std::pow(lab1_PY2+vd.Py(),2)-std::pow(lab1_PZ2+vd.Pz(),2));  // build Lb

		//std::cout<<"massb: "<<masshypo<<std::endl;
		
		if( masshypo > mdSet->GetMassBRangeDown()  && masshypo < mdSet->GetMassBRangeUp()){ // only events which fall into Bs mass range are acceptable
		  tmpc[i] += w;
		  lab0_MM->setVal(masshypo);
		  lab2_MM->setVal(masshypod);
		  lab1_P->setVal(log(lab1_P2));
		  lab1_PT->setVal(log(lab1_PT2));
		  nTracks->setVal(log(nTracks3));
		  //lab0_TAU2->setVal(lab0_TAU23*1000);
		  //lab0_TAU2ERR->setVal(lab0_TAU2TERR3*1000);
		  lab1_PIDK->setVal(-lab1_PIDK3);
		  Double_t w1=1.0;
		  if ( fabs(masshypolb -2285)<30 )  {  w1 = hmisIDL.GetWeight(phypolc,smp[i]);    }
		  else{   w1 = hmisID.GetWeight(phypo,smp[i]);   }

		  Double_t w2 = heff.GetWeight(p2,smp[i]); 
		  Double_t w0 = heff0.GetWeight(lab1_P2, smp[i]); 
		  Double_t w5 = heff5.GetWeight(lab1_P2, smp[i]); 
		  Double_t w = 1.0;
		  if ( w0 != 0 ) { w = w1*w2/w0*w5;} else {w =  w1*w2*w5;}
		  weights->setVal(w);

		  lab0_TAUERR->setVal(lab0_TAUERR3[0]*corr);
		  	  
		  dataSet[i]->add(*obs,w,0);
		  
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
	    
	}

      //Create RooKeysPdf for misID background//
      
      if ( pdf == true )
	{
	  name="PhysBkgBd2DPiPdf_m_"+s;
	  pdfDataMiss[i] = new RooKeysPdf(name.Data(),name.Data(),*lab0_MM,*dataSet[i],RooKeysPdf::MirrorBoth,1.5);
	  
	  TString nameD=name+"_Ds";
	  pdfDataDMiss[i] = new RooKeysPdf(nameD.Data(),nameD.Data(),*lab2_MM,*dataSet[i], RooKeysPdf::MirrorBoth,1.5);
	  
	  
	  if (debug == true) 
	    {
	      if( pdfDataMiss[i] != NULL ){ std::cout<<"=====> Create RooKeysPdf for misID BdDPi: "<<pdfDataMiss[i]->GetName()<<std::endl;} 
	      else {std::cout<<"Cannot create pdf"<<std::endl;}
	      
	      if( pdfDataDMiss[i] != NULL ){ std::cout<<"=====> Create RooKeysPdf for Ds mass misID BdDPi: "<<pdfDataDMiss[i]->GetName()<<std::endl;}
	      else {std::cout<<"Cannot create pdf"<<std::endl;}
	      
	    }
	}

      if( plotSet->GetStatus() == true )
	{
	  TString s = smp[i]+"_"+md[i]; 
	  SaveDataSet(dataSet[i],  lab1_PT, s, mode, plotSet, debug);
	  SaveDataSet(dataSet[i],  nTracks, s, mode, plotSet, debug);
	  SaveDataSet(dataSet[i],  lab1_PIDK, s, mode, plotSet, debug);
	  if (pdf == true )
	    {
	      SaveTemplate(dataSet[i], pdfDataMiss[i],  lab0_MM, s, mode, plotSet, debug);
	      SaveTemplate(dataSet[i], pdfDataDMiss[i], lab2_MM, s, mode, plotSet, debug);
	    }
	}
      
      work->import(*dataSet[i]);
      
      if ( pdf == true )
	{
	  work->import(*pdfDataMiss[i]);
	  work->import(*pdfDataDMiss[i]);
	} 
    }
    return work;
  }

  //===========================================================================                                                                                                            
  // Get background category cut for background MC                                                                                                                                         
  //===========================================================================                        
  TCut GetBKGCATCutBkg( MDFitterSettings* mdSet, TString mode, TString hypo, bool debug )
  {
    TCut BKGCut = 0;
    TCut MCCut1 = "";
    TCut MCCut2 = ""; 

    //Set prefixes                                                                                                                                                                         
    TString DsPrefix    = "";
    TString BsPrefix    = "";

    DsPrefix = mdSet->GetPrefix(mdSet->GetMassDVar());
    BsPrefix = mdSet->GetPrefix(mdSet->GetMassBVar());

    if ( (mode.Contains("Bs") == true) || ( (mode.Contains("Ds") == true) && (mode.Contains("Dst") != true)))
      {
	MCCut1 = Form("%s_BKGCAT < 30 || %s_BKGCAT == 50",DsPrefix.Data(), DsPrefix.Data());
      }
    else { MCCut1 = Form("%s_BKGCAT == 30",DsPrefix.Data()); }
    MCCut2 = Form("%s_BKGCAT < 60",BsPrefix.Data());

    if ( hypo.Contains("Bd"))
      {
	if ( ( (mode.Contains("D") == true) && (mode.Contains("Ds") != true) )
	     || (mode.Contains("Dst") == true))
	  {
	    MCCut1 = Form("(%s_BKGCAT < 30 || %s_BKGCAT == 50 )",DsPrefix.Data(),DsPrefix.Data());
	  }
	else {
	  MCCut1 = Form("(%s_BKGCAT == 30)",DsPrefix.Data());
	}
      }

    BKGCut = MCCut1&&MCCut2;
    if ( debug ) { } 
    return BKGCut;
  }
  
  //===========================================================================                                                                                                            
  // Get MCID cut for background MC                                                                                                                                                        
  //===========================================================================        
  TCut GetMCIDCutBkg( MDFitterSettings* mdSet, TString hypo, bool debug)
  {
    TCut MCID = "";
    //Set id for bachelor //                                                                                                                                                               
    int id_lab1=0;
    if( hypo.Contains("Pi") ) { id_lab1=211; if ( debug == true) std::cout<<" Hypo with Pi"<<std::endl;}
    else if (hypo.Contains("K")) { id_lab1=321; if ( debug == true) std::cout<<"Hypo with K"<<std::endl; }

    // Set id for D child //                                                                                                                                                               
    int id_lab4=0;
    if (hypo.Contains("Ds") == true ) { id_lab4=321; if ( debug == true) std::cout<<"Hypo with Ds"<<std::endl; }
    else if (hypo.Contains("D") == true && hypo.Contains("Ds") == false) { id_lab4=211;  if ( debug == true) std::cout<<"Hypo with D"<<std::endl;}

    TString BachPrefix = mdSet->GetPrefix(mdSet->GetPIDKVar());
    TString DsCh1Prefix = mdSet->GetChildPrefix(0);
    TString DsCh2Prefix = mdSet->GetChildPrefix(1);
    TString DsCh3Prefix = mdSet->GetChildPrefix(2);
    
    MCID = Form("abs(%s_ID)==%d && abs(%s_ID)==321 && abs(%s_ID)==211 && abs(%s_ID)==%d",                                                                                       
		BachPrefix.Data(), id_lab1, DsCh1Prefix.Data(), DsCh3Prefix.Data(), DsCh2Prefix.Data(), id_lab4);                           
    if ( debug ) { } 
    return MCID;
  }
    
  //===========================================================================
  // Get global cut for background MC
  //===========================================================================

TCut GetCutMCBkg( MDFitterSettings* mdSet, TString mode, TString hypo, TString Dmode, bool debug )
  {
    TCut MCCut= ""; 

    TCut P_cut      = mdSet->GetCut(mdSet->GetMomVar());
    TCut PT_cut     = mdSet->GetCut(mdSet->GetTrMomVar());
    TCut nTr_cut    = mdSet->GetCut(mdSet->GetTracksVar());
    TCut BDTG_cut   = mdSet->GetCut(mdSet->GetBDTGVar());

    TCut addCuts = (TCut)mdSet->GetMCCuts(Dmode);
    
    TCut BKGCATCut = "";
    if ( mdSet->CheckBKGCATCut(Dmode) == true )
      {
	BKGCATCut = GetBKGCATCutBkg( mdSet, mode, hypo, debug);
      }

    TCut MCID = "";
    if ( mdSet->CheckIDCut(Dmode) == true )
      {
	MCID = GetMCIDCutBkg( mdSet, hypo, debug);
      }

    MCCut = BKGCATCut&&MCID&&P_cut&&BDTG_cut&&PT_cut&&nTr_cut&&addCuts;  
    if (debug == true )
      {
	std::cout<<"------Cut-----"<<std::endl;
	std::cout<<MCCut<<std::endl;
	std::cout<<"--------------"<<std::endl;
      }
    if ( debug == true ) { } 
    return MCCut;

  }

  //===========================================================================
  // Get name of PID hist for bachelor  - background MC
  //===========================================================================
  TString GetHistNameBachPIDBkgMC(MDFitterSettings* mdSet, TString hypo, bool debug )
  {
    TString nameHistBach = "";

    if ( hypo.Contains("Bd")) {  nameHistBach = Form("MyKaonMisID_%d;1",mdSet->GetPIDBach()); }
    else { nameHistBach = Form("MyPionMisID_%d;1", mdSet->GetPIDBach()); }
    if( mdSet->GetPIDBach() == -5) {nameHistBach = "MyPionMisID_Minus5";}
    if( mdSet->GetPIDBach() > 10 ) {nameHistBach = "MyPionMisID_10";}
    
    if ( debug == true ) { std::cout<<"[INFO] Bachelor PID histogram: "<< nameHistBach<<std::endl; } 

    return nameHistBach;
  }

  //===========================================================================
  // Get name of PID hist for Ds child -  background MC
  //===========================================================================
  TString GetHistNameChildPIDBkgMC(MDFitterSettings* mdSet, TString hypo, bool debug)
  {
    TString nameHistChild = "";

    if ( hypo.Contains("Bd")) { nameHistChild = Form("MyKaonMisID_%d;1",mdSet->GetPIDChild()); }
    else { nameHistChild = Form("MyPionMisID_%d;1", mdSet->GetPIDChild()); }

    if ( debug == true ) { std::cout<<"[INFO] Ds child PID histogram: "<< nameHistChild<<std::endl; }

    return nameHistChild;
  }

  //===========================================================================
  // Get name of PID hist for proton veto - background MC
  //===========================================================================
  TString GetHistNameProtonPIDBkgMC(MDFitterSettings* mdSet, TString hypo, bool debug)
  {
    TString nameHistProton = "";

    if ( hypo.Contains("Bd") == true) { nameHistProton = Form("MyProtonMisID_p%d;1",mdSet->GetPIDProton());}
    else {  nameHistProton = "MyProtonMisID_pKm5_KPi5"; }
    
    if ( debug == true ) { std::cout<<"[INFO] Proton PID histogram: "<< nameHistProton<<std::endl; }
    
    return nameHistProton;
  }

  //===========================================================================
  // Get name of PID hist for bachelor eff -  background MC
  //===========================================================================
  TString GetHistNameBachPIDEffBkgMC(MDFitterSettings* mdSet, TString hypo, bool debug)
  {
    TString nameHistEff = "";

    if ( hypo.Contains("Pi")) { nameHistEff = Form("MyPionEff_%d;1",mdSet->GetPIDBach()); }
    else { nameHistEff = Form("MyKaonEff_%d;1", mdSet->GetPIDBach()); }

    if ( debug == true ) { std::cout<<"[INFO] Bachelor PID eff histogram: "<< nameHistEff<<std::endl; }

    return nameHistEff;
  }

  //===========================================================================                                                                     
  // Get correlation factor between observables                                                                                                           
  //=========================================================================== 
  Double_t CheckCorr(RooDataSet* data, RooRealVar* obs1, RooRealVar* obs2, TString corrName, 
		 PlotSettings* plotSet, bool debug )
  {
    if (debug == true ) 
      {
	std::cout<<"[INFO] ==> GeneralUtils::CheckCorr(...)"<<std::endl;
      }
    Int_t bin1 = 40;
    Int_t bin2 = 40;
    TH2F* corr = NULL;
   
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    TString obs1Name = obs1->GetName();
    TString obs2Name = obs2->GetName();
    TString label1Name = CheckObservable(obs1Name, debug);
    TString label2Name = CheckObservable(obs2Name, debug);
    if (debug == true )
      {
	std::cout<<"[INFO] ==> Obs1: "<<obs1Name<<std::endl;
	std::cout<<"[INFO] ==> Obs2: "<<obs2Name<<std::endl;
      }

    corr = data->createHistogram(*obs1, *obs2, bin1, bin2, "", corrName.Data());
    corr->SetName(corrName.Data());
    corr->GetXaxis()->SetTitle(label1Name.Data());
    corr->GetYaxis()->SetTitle(label2Name.Data());
    Double_t corr1 = corr->GetCorrelationFactor();
    
    std::cout<<"[INFO] ==> Correlation between  "<<obs1Name<<" and "<<obs2Name<<" = "<<corr1<<std::endl;
       
    return corr1; 
  }

  TH2F* GetCorrHist(RooDataSet* data, RooDataSet* dataPID, RooArgSet* obs, std::vector <TString> &obsName, 
		    TString corrHistName, PlotSettings* plotSet, bool debug )
  {
    if (debug == true )
      {
	std::cout<<"[INFO] ==> GeneralUtils::GetCorrHist(...)"<<std::endl;
      }

    TH2F* histCorr = NULL;    
    Int_t size = obsName.size(); 
    TString Title1 = GetLabel(corrHistName);
    TString histTitle = "Correlations for "+Title1; 
    histCorr = new TH2F(corrHistName.Data(), histTitle.Data(), size, 0, size, size, 0, size);
    histCorr->LabelsOption("d"); 
    histCorr->SetStats(false); 
    histCorr->GetXaxis()->SetLabelSize(0.05);
    histCorr->GetYaxis()->SetLabelSize(0.05);
    
    for(int i = 0; i < size; i++ )
      {
	RooRealVar* obs1 = (RooRealVar*)obs->find(obsName[i].Data());
	TString obs1Name = obs1->GetName();
       	histCorr->GetXaxis()->SetBinLabel(i+1, obs1Name.Data());
	histCorr->GetYaxis()->SetBinLabel(i+1, obs1Name.Data());
	for (int j = 0; j <size; j++ )
	  {
	    RooRealVar* obs2 = (RooRealVar*)obs->find(obsName[j].Data()); 
	    Double_t corr = 0;
	    TString obs2Name = obs2->GetName();
	    TString corrName = "Correlation_"+obs1Name+"_"+obs2Name; 
	    if ( obsName[i].Contains("PIDK") == true|| obsName[j].Contains("PIDK") == true )
	      {
		corr = CheckCorr(dataPID, obs1, obs2, corrName,plotSet, debug );
	      }
	    else
	      {
		corr = CheckCorr(data, obs1, obs2, corrName, plotSet, debug );
	      }
	    histCorr->SetBinContent(i+1,j+1,corr);
	    
	  }
      }
    TStyle *style = new TStyle();
    style->SetPalette(55,0);
    
    TString dir = plotSet->GetDir();
    TString ext = plotSet->GetExt();
    TString save = dir+"/"+corrHistName+"."+ext;
    TCanvas *rat = new TCanvas("can","",10,10,2000,1200);
    rat->SetLeftMargin(0.25); 
    rat->SetRightMargin(0.20);
    rat->SetBottomMargin(0.20);
    rat->SetFillColor(0);
    rat->cd();
    histCorr->GetZaxis()->SetRangeUser(-1.0, 1.0);
    histCorr->Draw("COLZ TEXT45");
    rat->Update();
    rat->SaveAs(save.Data());
    return histCorr;
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

  RooWorkspace* ObtainSpecBack(TString& filesDir, TString& sig,
			       MDFitterSettings* mdSet,
			       TString& hypo,
			       RooWorkspace* workspace, 
			       Bool_t correlations,
			       double globalWeight,
			       PlotSettings* plotSet, 
			       bool debug)
  {
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainSpecBack(...). Obtain dataSets for all partially reconstructed backgrounds"<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"Data mode: "<<hypo<<std::endl;
	std::cout<<"Global weight: "<<globalWeight<<std::endl;
      }
    
    RooWorkspace* work = NULL;
    if (workspace == NULL ) { work =  new RooWorkspace("workspace","workspace"); }
    else { work = workspace; }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }
    RooArgSet* obs = mdSet->GetObsSet(false, true, false, false, true, true);
    obs->Print("v");
    std::vector <TString> tN = mdSet->GetVarNames(true,false,false,true,true);
    for(unsigned int i = 0; i<tN.size(); i++ )
      {
	std::cout<<"tN: "<<tN[i]<<std::endl;
      }

    // Read MC File // 
    std::vector <MCBackground*> MCBkg; 
    Int_t numBkg = CheckNumberOfBackgrounds(filesDir,sig, debug);  
    for(int i = 1; i<numBkg+1; i++ )
      {
	MCBkg.push_back(new MCBackground(Form("MCBkg%d",i),"MCBackground",filesDir,sig,i));
	MCBkg[i-1]->Print("v"); 
      }
    
    HistPID1D* hBach = NULL;
    HistPID1D* hChild = NULL;
    HistPID1D* hBachEff = NULL;
    HistPID1D* hProton = NULL;
    
    if ( mdSet->CheckMassWeighting() == true)
      {
	//Read all necessary histogram for misID//
	TString PID = "#PID";
	TString PID2 = "#PID2";
	TString PIDp = "";
	if ( hypo.Contains("Bd") == true) { PIDp = "#PIDp"; } else { PIDp = "#PIDp3";}
   
	TString nameHistBach = GetHistNameBachPIDBkgMC(mdSet,hypo,debug); 
	TString nameHistMiss = GetHistNameChildPIDBkgMC(mdSet,hypo,debug);
	TString nameHistEff  = GetHistNameBachPIDEffBkgMC(mdSet,hypo,debug);
	TString nameHistProton = GetHistNameProtonPIDBkgMC(mdSet,hypo,debug);
    
	hBach = new HistPID1D(nameHistBach, nameHistBach, filesDir, PID, PID2);
	hChild = new HistPID1D(nameHistMiss, nameHistMiss, filesDir, PID, PID2);
	hBachEff = new HistPID1D(nameHistEff, nameHistEff, filesDir, PID, PID2);
	hProton = new HistPID1D(nameHistProton, nameHistProton, filesDir, PIDp);
	if ( debug == true )
	  {
	    std::cout<<hBach<<std::endl;
	    std::cout<<hChild<<std::endl;
	    std::cout<<hBachEff<<std::endl;
	    std::cout<<hProton<<std::endl;
	  }
	hBach->SavePlot(plotSet);
	hChild->SavePlot(plotSet);
	hBachEff->SavePlot(plotSet);
	hProton->SavePlot(plotSet);
      }

    HistPID2D* hRDM = NULL;
    if (mdSet->CheckDataMCWeighting() == true )
      {
	TString RDM = "#RatioDataMC2D";
	TString nameHistRatio = "histRatio";
	hRDM = new HistPID2D(nameHistRatio, nameHistRatio, filesDir, RDM);
      }

    // Read sample (means down or up)  from path //
    TString modeD;
    modeD = CheckDMode(sig, debug);
       
    if ( debug == true) std::cout<<"[INFO] ==> Create RooKeysPdf for PartReco backgrounds" <<std::endl;

    TString namew = "weights";
    RooRealVar* weight  = new RooRealVar(namew.Data(), namew.Data(), 0.0, 5.0);
    RooDataSet* dataSetMC[numBkg];
    RooDataSet* dataSetMCtmp[numBkg];
    //TH2F* corrHist[numBkg];  
    
    Int_t nentriesMC[numBkg];
    Float_t wMC(1.0), wRW(1.0), mMC(0), mDMC(0);
    
    if ( mdSet->CheckDataMCWeighting() == true || mdSet->CheckMassWeighting() == true) 
      {
	obs->add(*weight);
      }  
    
    for(int i = 0; i< numBkg; i++ )
      {
	//corrHist[i] = NULL; 
	TTree* treeMC = MCBkg[i]->GetTree();
	TString md= MCBkg[i]->GetMode();
	TString smp = MCBkg[i]->GetPolarity();   
	TString year = MCBkg[i]->GetYear(); 
	TCut MCCut = GetCutMCBkg(mdSet, md, hypo, modeD, debug); 
	//	if ( md == "Bs2Combinatorial" ) { MCCut = "FBs_M>5100&&FDs_M>1950&&FDs_M<1990&&FBDT_Var>0&&FDelta_R<1.0&&FDelta_M>190.&&((FDsBac_M-FDs_M)<3370||(FDsBac_M-FDs_M)>3440)"; }
	
	TTree* treetmp = NULL;
	treetmp = TreeCut(treeMC, MCCut, smp, md, debug);  // create new tree after applied all cuts // 

	std::vector <TString> tB;
	std::vector <Double_t> varD; std::vector <Int_t> varI; std::vector <Float_t> varF;
	for(unsigned int k = 0; k<tN.size(); k++ )
	  {
	    if ( tN[k] != "" ){ tB.push_back(treetmp->GetLeaf(tN[k].Data())->GetTypeName()); }
	    else { tB.push_back(""); }
	    InitializeRealObs(tB[k], varD, varI, varF, debug);
	  }

	for(unsigned int k =0; k<tN.size(); k++ )
	  {
	    SetBranchAddress(treetmp, tB[k], tN[k], varD[k], varI[k], varF[k], debug);
	  }

	std::vector <TString> tBW;
	std::vector <TString> tNW;
	std::vector <Double_t> varDW; std::vector <Int_t> varIW; std::vector <Float_t> varFW;
	if ( mdSet->CheckMassWeighting()==true )
	  {
	    tNW = mdSet->GetMassWeightingVar(); 
	    for(unsigned int k = 0; k<tNW.size(); k++ )
	      {
		tBW.push_back(treetmp->GetLeaf(tNW[k].Data())->GetTypeName()); 
		InitializeRealObs(tBW[k], varDW, varIW, varFW, debug);
	      }
	    for(unsigned int k =0; k<tNW.size(); k++ )
	      {
		SetBranchAddress(treetmp, tBW[k], tNW[k], varDW[k], varIW[k], varFW[k], debug);
	      }

	  }
	nentriesMC[i] = treetmp->GetEntries();
	
	if ( debug == true) std::cout<<"Calculating "<<md<<" "<<smp<<std::endl;
	dataSetMC[i] = NULL;
	
	TString nm = MCBkg[i]->GetSampleModeYear();
	TString name="dataSetMC_"+nm;
	
	if ( mdSet->CheckMassWeighting() == true ||  mdSet->CheckDataMCWeighting() == true)
	  {
	    dataSetMC[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*obs), namew.Data()); //create new data set //
	    dataSetMCtmp[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*obs), namew.Data());
	  }
	else
	  {
	    dataSetMC[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*obs)); //create new data set //                                                                    
            dataSetMCtmp[i] = new RooDataSet(name.Data(),name.Data(),RooArgSet(*obs));
	  }
	if  (debug == true) std::cout<<"Number of entries: "<<nentriesMC[i]<<std::endl;
	Double_t sh= -3.9;
	if ( hypo.Contains("Bd") ) { sh = 3.75; } 
	if ( (md == "Bd2DsstKst" && hypo.Contains("DsstK") ) || ( md == "Bd2DsKst" && hypo.Contains("DsstK") ))
	  {
	    sh = sh-86.8;
	  }


	long ag_counter(0), ag_shifted_counter(0), sa_counter(0);

	for (Long64_t jentry=0; jentry<nentriesMC[i]; jentry++) {
	  
	  treetmp->GetEntry(jentry);
	  if (hypo.Contains("Bd") == true && ( md == "Bs2DsPi") && jentry%8 != 0 ) continue;
          if (hypo.Contains("Bd") == true && ( md == "Bd2DK" ) && jentry%4 != 0 ) continue;
          if (hypo.Contains("Bd") == true && ( md == "Bd2DstPi" ) && jentry%2 != 0 ) continue;
          if (hypo.Contains("DsPi") == true && ( md == "Bs2DsK" ) && jentry%16 != 0 ) continue;
          if (hypo.Contains("DsK") == true && ( md == "Bs2DsPi" ) && jentry%16 != 0 ) continue;
          if (hypo.Contains("DsK") == true && ( md == "Bd2DK" ) && jentry%2 != 0 ) continue;

	  Double_t nTr(0), pT(0), p(0), pidk(0);
	  Double_t val(0); 
	  for(unsigned k = 0; k < tN.size(); k++)
	    {
	      Bool_t cat = false;
	      if ( tN[k] == mdSet->GetIDVar() ) { cat = true; }
	      if(  mdSet->CheckTagVar() == true )
		{
		  for(int m = 0; m<mdSet->GetNumTagVar(); m++)
		    {
		      if ( tN[k] ==  mdSet->GetTagVar(m) )
			{
			  cat = true;
			  break;
			}
		    }
		}
	      TString name = mdSet->GetVarOutName(tN[k]);

	      if ( cat == true ) { val = SetValCatObs(mdSet, obs, name , tB[k], varD[k], varI[k], varF[k]); }
	      else{ val = SetValRealObs(mdSet, obs, name, tB[k], varD[k], varI[k], varF[k], hypo, sh ); }
	      if ( tN[k] == mdSet->GetMomVar() ) { p = val; }
	      if ( tN[k] == mdSet->GetTrMomVar() ) { pT = val; }
	      if ( tN[k] == mdSet->GetTracksVar() ) { nTr = val; }
	      if ( tN[k] == mdSet->GetMassBVar() ) { mMC = val; }
	      if ( tN[k] == mdSet->GetMassDVar() ) { mDMC = val;}
	      if ( tN[k] == mdSet->GetPIDKVar() ) { pidk = val; }
	    }

	  if ( mdSet->CheckDataMCWeighting() == true )
	    {
	      wRW = hRDM->GetWeight(pT,nTr, smp);
	    }

	  if ( mdSet->CheckMassWeighting() == true )
	    {
	      std::vector <Double_t> pV;
	      for(unsigned k = 0; k < tNW.size(); k++)
		{
		  pV.push_back(GetValue( tBW[k], varDW[k], varIW[k], varFW[k] ));
		}
	      
	      // Please note that Ds and D mass hypo all applied in NTuple so no need to change mass hypo //
	      if (hypo.Contains("K"))  // PartReco for BsDsK 
		{
	      
		  if( md.Contains("Kst") == true  || md.Contains("K") == true  )
		    {
		      if ( md.Contains("Bd")  == true ) { wMC = hChild->GetWeight(pV[0],smp)*hBachEff->GetWeight(exp(p),smp); }
		      else if ( md.Contains("Lb") == true ) { wMC = hProton->GetWeight(pV[0],smp)*hBachEff->GetWeight(exp(p),smp); }
		      else{ wMC = hBachEff->GetWeight(exp(p),smp); }
		    }
		  else   // mode with {Pi,Rho}, bachelor has to be reweighted //  
		    {
		      if ( md.Contains("Bd") == true ) { wMC = hChild->GetWeight(pV[0],smp)*hBach->GetWeight(exp(p),smp); }
		      else if ( md.Contains("Lb") == true) { wMC = hProton->GetWeight(pV[0],smp)*hBach->GetWeight(exp(p),smp); }
		      else{ wMC = hBach->GetWeight(exp(p),smp); }
		    }
		}
	      else if (hypo.Contains("Pi")){  //PartReco for BsDsPi 
		if ( hypo.Contains("Bd") == true )
		  {
		    if( md == "Lb2LcPi" ){ wMC = hProton->GetWeight(pV[0],smp)*hBachEff->GetWeight(exp(p),smp); }
		    else if( md == "Bs2DsPi") { wMC = hChild->GetWeight(pV[1],smp)*hBachEff->GetWeight(exp(p),smp); }
		    else if( md == "Bd2DK" ) { wMC = hBach->GetWeight(exp(p),smp); }
		    else { wMC = hBachEff->GetWeight(exp(p),smp); }
		  }
		else
		  {
		    if( md == "Lb2LcPi" ) { wMC = hProton->GetWeight(pV[1],smp)*hBachEff->GetWeight(exp(p),smp); }
		    else if (md.Contains("Bd") == true ){ wMC = hChild->GetWeight(pV[0],smp)*hBachEff->GetWeight(exp(p),smp);}
		    else if ( md.Contains("Kst") == true  || md.Contains("K") == true ){ wMC = hBach->GetWeight(exp(p),smp); }
		    else { wMC = hBachEff->GetWeight(exp(p),smp); }
		  }
	      }
	    }

	  if (  mdSet->CheckDataMCWeighting() == true ||  mdSet->CheckMassWeighting() == true )
	    {
	      weight->setVal(wMC*wRW*globalWeight);
	    }
	  
	  if (5320 < mMC and mMC < 5420) sa_counter++;
	  if (mdSet->GetMassBRangeDown() < mMC and mMC < mdSet->GetMassBRangeUp()) ag_counter++;
  
	  if ( mMC > mdSet->GetMassBRangeDown() && mMC < mdSet->GetMassBRangeUp() 
	      && mDMC > mdSet->GetMassDRangeDown()  && mDMC < mdSet->GetMassDRangeUp()  )
	   {
	    
	     if ( mdSet->CheckDataMCWeighting() == true ||  mdSet->CheckMassWeighting() == true )  { dataSetMC[i]->add(*obs,wMC*wRW*globalWeight,0); } 
	     else { dataSetMC[i]->add(*obs); }

	     ag_shifted_counter++;
	      
	      if (hypo.Contains("Pi"))
		{
		  if ( pidk > mdSet->GetPIDBach())
                    {
		      if( mdSet->CheckDataMCWeighting() == true ||  mdSet->CheckMassWeighting() == true )  { dataSetMCtmp[i]->add(*obs,wMC*wRW*globalWeight,0); }
		      else { dataSetMCtmp[i]->add(*obs); }
                    }
		}
	      else if ( hypo.Contains("K") == true )
		{
		  if ( pidk > log(mdSet->GetPIDBach()))
		    {
		      if( mdSet->CheckDataMCWeighting() == true ||  mdSet->CheckMassWeighting() == true )  { dataSetMCtmp[i]->add(*obs,wMC*wRW*globalWeight,0); }
                      else { dataSetMCtmp[i]->add(*obs); }
		    }
		}
	    }
	  
	}

	if ( debug == true){
	std::cout << "DEBUG: AG - shifted " << ag_shifted_counter
		  << " no shift " << ag_counter
		  << " SA - no shift " << sa_counter << std::endl;
	
	std::cout<<"Create dataSet MC: "<<dataSetMC[i]->GetName()<<" with entries: "<<dataSetMC[i]->numEntries()<<std::endl;
	}

	if ( correlations == true )
	  { 
	    std::vector <TString> obsName;
	    obsName.push_back(mdSet->GetMassBVarOutName());
	    obsName.push_back(mdSet->GetMassDVarOutName());
	    obsName.push_back(mdSet->GetPIDKVarOutName()); 
	    obsName.push_back(mdSet->GetTimeVarOutName());
	    obsName.push_back(mdSet->GetTerrVarOutName());
	    if(  mdSet->CheckTagOmegaVar() == true )                                                                                                       
              {                                                                                                                                         
                for(int k = 0; k<mdSet->GetNumTagOmegaVar(); k++)                                                                                          
                  {                
		    obsName.push_back(mdSet->GetTagOmegaVarOutName(k));
		  }
	      }
	    TString corrName = "corr_"+nm;
	    GetCorrHist(dataSetMC[i], dataSetMCtmp[i], obs, obsName, corrName, plotSet, debug );
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

  RooWorkspace* getSpecBkg4kfactor(TString& filesDir, TString& sig, TString& sigtree,
				   MDFitterSettings* mdSet,
				   TString& hypo,
				   RooWorkspace* workspace,
				   double globalWeight,
				   TFile &ffile,  bool debug)
  {
    long gmsg_count(0), gerr_count(0);

    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::getSpecBkg4kfactor(...)"<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"Data mode: "<<hypo<<std::endl;
      }

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
      ERROR(gerr_count, "Incompatible file list size: MCTreeName("
	    << MCTreeName.size() << ") and MCFileName(" << ndsets <<")");
      return NULL;
    }

    TTree* treeMC[ndsets];
    std::vector <std::string> mode;
    for( unsigned i =0; i < ndsets; i++) {
      treeMC[i] = ReadTreeMC(MCFileName[i].c_str(), MCTreeName[i].c_str(), debug);
      assert(treeMC[i]);
    }
    ReadMode(MCFileName, mode, true, debug);

    // Read all necessary histogram for misID
    TString PID = "#PID";
    TString PID2 = "#PID2";
    TString PIDp = "";
    if ( hypo.Contains("Bd") == true) {
      PIDp = "#PIDp";
    } else {
      PIDp = "#PIDp3";
    }

    TString RDM = "#RatioDataMC2D";
    TString nameHistBach = GetHistNameBachPIDBkgMC(mdSet,hypo,debug);
    TString nameHistMiss = GetHistNameChildPIDBkgMC(mdSet,hypo,debug);
    TString nameHistEff  = GetHistNameBachPIDEffBkgMC(mdSet,hypo,debug);
    TString nameHistProton = GetHistNameProtonPIDBkgMC(mdSet,hypo,debug);
    TString nameHistRatio = "histRatio";

    HistPID1D hBach(nameHistBach, nameHistBach, filesDir, PID, PID2);
    HistPID1D hChild(nameHistMiss, nameHistMiss, filesDir, PID, PID2);
    HistPID1D hBachEff(nameHistEff, nameHistEff, filesDir, PID, PID2);
    HistPID1D hProton(nameHistProton, nameHistProton, filesDir, PIDp);
    HistPID2D hRDM(nameHistRatio, nameHistRatio, filesDir, RDM);
    if ( debug == true )
      {
	std::cout<<hBach<<std::endl;
	std::cout<<hChild<<std::endl;
	std::cout<<hBachEff<<std::endl;
	std::cout<<hProton<<std::endl;
	std::cout<<hRDM<<std::endl;
      }

    //Read sample (means down or up) from path//
    std::vector<TString> smp(ndsets);
    for (unsigned i = 0; i< ndsets; i++) {
      smp[i] = CheckPolarity(sig, debug);
    }
    TString modeD;
    modeD = CheckDMode(sig, debug);
   
    /**
     * Calculate and return datasets with k-factors for partially
     * reconstructed backgrounds.
     *
     */

    bool isDsK(hypo.Contains("K"));

    // some constants
    const double BSMASS(5366.77), BDMASS(5279.58), DSMASS(1968.49),
      DSSTMASS(2112.3), DMASS(1869.62), PIMASS(139.57018), KMASS(493.677),
      LBMASS(5619.4), LCMASS(2286.46), PMASS(938.272046);
    // , RHOMASS(775.49), KSTMASS(891.66), PI0MASS(134.9766);

    long veto_counter(0);
    const double pgratio_cut(5E-3), gratio_cut(5E-2);
    double wMC(0), wRW(0);

    for (unsigned i = 0; i < ndsets; i++) {
      std::string sanemode(mode[i].substr(0, mode[i].find("_")));

      bool ispartial(false);
      if (mode[i].find("st") != std::string::npos or
	  mode[i].find("Rho") != std::string::npos) ispartial = true;

      // mo-cos ... mode codes
      enum mode_t { Bd2DK, Bd2DsK, Bd2DsKst, Bd2DsstK, Bs2DsKst,
		    Bs2DsRho, Bs2DsstK, Bs2DsstPi, Bs2DsstRho,
		    Lb2Dsp, Lb2Dsstp, Lb2LcK, Bs2DsPi, Bd2DsPi,
		    Lb2LcPi, Bd2DPi, Bs2DsK} current_mode=Bd2DK;

      double SocksFitterArgs[5] = {BSMASS, DSMASS, PIMASS, -1.0, -1.0};

      // noMC is redundant now that we have all MC, keep for reference.
      // bool noMC(false);

      if (isDsK) {
	// ordered in increasing yields under DsK
	if ("Bd2DK" == sanemode) {
	  current_mode = Bd2DK;
	  SocksFitterArgs[0] = BDMASS;
	  SocksFitterArgs[1] = DMASS;
	  SocksFitterArgs[2] = KMASS;
	} else if ("Lb2LcK" == sanemode) {
	  current_mode = Lb2LcK;
	  SocksFitterArgs[0] = LBMASS;
	  SocksFitterArgs[1] = LCMASS;
	  SocksFitterArgs[2] = KMASS;
	} else if ("Lb2Dsstp" == sanemode) {
	  current_mode = Lb2Dsstp;
	  SocksFitterArgs[0] = LBMASS;
	  // SocksFitterArgs[1] = DSMASS;
	  SocksFitterArgs[2] = PMASS;
	  SocksFitterArgs[3] = DSSTMASS;
	} else if ("Lb2Dsp" == sanemode) {
	  current_mode = Lb2Dsp;
	  SocksFitterArgs[0] = LBMASS;
	  // SocksFitterArgs[1] = DSMASS;
	  SocksFitterArgs[2] = PMASS;
	} else if ("Bs2DsstPi" == sanemode) {
	  current_mode = Bs2DsstPi;
	  // SocksFitterArgs[0] = BSMASS;
	  // SocksFitterArgs[1] = DSMASS;
	  // SocksFitterArgs[2] = PIMASS;
	  SocksFitterArgs[3] = DSSTMASS;
	} else if ("Bs2DsRho" == sanemode) {
	  // FIXME: Only high statistics sample with large delta mB (~20
	  // MeV). The Rho decays quickly, so it is reconstructed as a
	  // Pi?  and the other Pi is missed! This should be considered
	  // as a partially reconstructed decay with a Rho intermediate
	  // state.  Do not constrain the rho mass, as it is very wide.
	  current_mode = Bs2DsRho;
	  // SocksFitterArgs[0] = BSMASS;
	  // SocksFitterArgs[1] = DSMASS;
	  // SocksFitterArgs[2] = PIMASS;
	  SocksFitterArgs[4] = PIMASS;
	} else if ("Bs2DsPi" == sanemode) {
	  current_mode = Bs2DsPi;
	} else if ("Lb2LcPi" == sanemode or "Lb2Lambdacpi" == sanemode) {
	  current_mode = Lb2LcPi;
	  SocksFitterArgs[0] = LBMASS;
	  SocksFitterArgs[1] = LCMASS;
	  // SocksFitterArgs[2] = PIMASS;
	} else if ("Bd2DPi" == sanemode) {
	  current_mode = Bd2DPi;
	  SocksFitterArgs[0] = BDMASS;
	  SocksFitterArgs[1] = DMASS;
	  // SocksFitterArgs[2] = PIMASS;
	}
      } else {
	// FIXME: need to add DsPi background modes
	if ("Bd2DsPi" == sanemode) {
	  current_mode = Bd2DsPi;
	  SocksFitterArgs[0] = BDMASS;
	  // SocksFitterArgs[1] = DSMASS;
	  // SocksFitterArgs[2] = PIMASS;
	} else if ("Bs2DsstPi" == sanemode) {
	  current_mode = Bs2DsstPi;
	  // SocksFitterArgs[0] = BSMASS;
	  // SocksFitterArgs[1] = DSMASS;
	  // SocksFitterArgs[2] = PIMASS;
	  SocksFitterArgs[3] = DSSTMASS;
	} else	if ("Bs2DsK" == sanemode) {
	  current_mode = Bs2DsK;
	  // SocksFitterArgs[0] = BSMASS;
	  // SocksFitterArgs[1] = DSMASS;
	  SocksFitterArgs[2] = KMASS;
	} else if ("Lb2LcPi" == sanemode or "Lb2Lambdacpi" == sanemode) {
	  current_mode = Lb2LcPi;
	  SocksFitterArgs[0] = LBMASS;
	  SocksFitterArgs[1] = LCMASS;
	  // SocksFitterArgs[2] = PIMASS;
	} else if ("Bd2DPi" == sanemode) {
	  current_mode = Bd2DPi;
	  SocksFitterArgs[0] = BDMASS;
	  SocksFitterArgs[1] = DMASS;
	  // SocksFitterArgs[2] = PIMASS;
	}
      }

      // create new tree after appling all cuts
      TString md(mode[i]);
      TCut MCCut = GetCutMCBkg(mdSet, md, hypo, modeD);
      TTree *ftree = TreeCut(treeMC[i], MCCut, smp[i], md, debug);
      assert(ftree);

      // variables to read from tree
      int BPID(0), DPID(0), hPID(0), nTr(0);
      float Bmass(0.);
      double Bmom(0.), Dmass(0.),
	B_tru_PE(0.), B_tru_PX(0.), B_tru_PY(0.), B_tru_PZ(0.),
	D_tru_PE(0.), D_tru_PX(0.), D_tru_PY(0.), D_tru_PZ(0.),
	h_tru_PE(0.), h_tru_PX(0.), h_tru_PY(0.), h_tru_PZ(0.),
	B_PE(0.), B_PX(0.), B_PY(0.), B_PZ(0.),
	lab4_P2(0), lab1_P2(0), lab1_PT2(0), lab5_P2(0);

      ftree->SetBranchAddress("lab0_TRUEID", &BPID);
      ftree->SetBranchAddress("lab2_TRUEID", &DPID);
      ftree->SetBranchAddress("lab1_TRUEID", &hPID);

      ftree->SetBranchAddress(mdSet->GetTracksVar().Data(), &nTr);
      ftree->SetBranchAddress(mdSet->GetMomVar().Data(),    &lab1_P2);
      ftree->SetBranchAddress(mdSet->GetTrMomVar().Data(),  &lab1_PT2);
      ftree->SetBranchAddress("lab4_P",                     &lab4_P2);
      ftree->SetBranchAddress("lab5_P",                     &lab5_P2);

      ftree->SetBranchAddress("lab0_P", &Bmom);
      ftree->SetBranchAddress(mdSet->GetMassBVar().Data(),  &Bmass);
      ftree->SetBranchAddress(mdSet->GetMassDVar().Data(),  &Dmass);

      // ftree->SetBranchAddress("lab0_TRUEP_E", &B_tru_PE);
      ftree->SetBranchAddress("lab0_TRUEP_X", &B_tru_PX);
      ftree->SetBranchAddress("lab0_TRUEP_Y", &B_tru_PY);
      ftree->SetBranchAddress("lab0_TRUEP_Z", &B_tru_PZ);

      // ftree->SetBranchAddress("lab2_TRUEP_E", &D_tru_PE);
      ftree->SetBranchAddress("lab2_TRUEP_X", &D_tru_PX);
      ftree->SetBranchAddress("lab2_TRUEP_Y", &D_tru_PY);
      ftree->SetBranchAddress("lab2_TRUEP_Z", &D_tru_PZ);

      // ftree->SetBranchAddress("lab1_TRUEP_E", &h_tru_PE);
      ftree->SetBranchAddress("lab1_TRUEP_X", &h_tru_PX);
      ftree->SetBranchAddress("lab1_TRUEP_Y", &h_tru_PY);
      ftree->SetBranchAddress("lab1_TRUEP_Z", &h_tru_PZ);

      ftree->SetBranchAddress("lab0_PE", &B_PE);
      ftree->SetBranchAddress("lab0_PX", &B_PX);
      ftree->SetBranchAddress("lab0_PY", &B_PY);
      ftree->SetBranchAddress("lab0_PZ", &B_PZ);

      double D_PE(0.), D_PX(0.), D_PY(0.), D_PZ(0.),
	h_PE(0.), h_PX(0.), h_PY(0.), h_PZ(0.);

      ftree->SetBranchAddress("lab2_PE", &D_PE);
      ftree->SetBranchAddress("lab2_PX", &D_PX);
      ftree->SetBranchAddress("lab2_PY", &D_PY);
      ftree->SetBranchAddress("lab2_PZ", &D_PZ);

      ftree->SetBranchAddress("lab1_PE", &h_PE);
      ftree->SetBranchAddress("lab1_PX", &h_PX);
      ftree->SetBranchAddress("lab1_PY", &h_PY);
      ftree->SetBranchAddress("lab1_PZ", &h_PZ);

      long long nentries = ftree->GetEntries();

      std::string dname ("kfactor_dataset_" + mode[i] + "_" + smp[i]);
      RooRealVar kfactorVar("kfactorVar", "Correction factor", 0.5, 1.5);
      RooRealVar weight("weight", "Event weight", 0., 500.0);
      RooDataSet dataset(dname.c_str(), dname.c_str(),
			 RooArgSet(kfactorVar, weight), "weight");

      ffile.cd();
      std::string hname("_"+mode[i]+"_"+smp[i]);
      TTree mBresn(std::string("mBresn"+hname).c_str(),
		   std::string("mBresn"+hname).c_str());

      double mBdiff(0.0), kfactor(0.0), kfactorm(0.0), kfactorp(0.0);
      mBresn.Branch("mBdiff", &mBdiff, "mBdiff/D");
      mBresn.Branch("kfactor", &kfactor, "kfactor/D");
      mBresn.Branch("kfactorm", &kfactorm, "kfactorm/D");
      mBresn.Branch("kfactorp", &kfactorp, "kfactorp/D");
      mBresn.Branch("wMC", &wMC, "wMC/D");
      mBresn.Branch("wRW", &wRW, "wRW/D");
      mBresn.Branch("globalWeight", &globalWeight, "globalWeight/D");

      unsigned long fill_counter(0), loop_counter(0);

      DEBUG(gmsg_count, "decay mode " << mode[i] << "_" << smp[i]
	    << " with " << nentries << " entries");

      for (Long64_t jentry=0; jentry < nentries; jentry++) {
	long msg_count(0), err_count(0);
	// if (loop_counter > 5000) break; // debug
	ftree->GetEntry(jentry);

	B_tru_PE = pe_from_pid(BPID, B_tru_PX, B_tru_PY, B_tru_PZ);
	D_tru_PE = pe_from_pid(DPID, D_tru_PX, D_tru_PY, D_tru_PZ);
	h_tru_PE = pe_from_pid(hPID, h_tru_PX, h_tru_PY, h_tru_PZ);
	TLorentzVector Bs(B_tru_PX, B_tru_PY, B_tru_PZ, B_tru_PE),
	  Ds(D_tru_PX, D_tru_PY, D_tru_PZ, D_tru_PE),
	  bach(h_tru_PX, h_tru_PY, h_tru_PZ, h_tru_PE),
	  Bs_rec(0.0, 0.0, 0.0, 0.0), Bs_ref(B_PX, B_PY, B_PZ, B_PE);
	TLorentzVector Bs_tru(Bs);

	// VETO:
	if (std::fabs(hPID) == 13) { // no pesky bachelor muons
	  veto_counter++;
	  continue;
	}
	TLorentzVector Bs_diff = Bs - Ds - bach;
	double dEratio(std::fabs(Bs_diff.E()/Bs.E())),
	  dPxratio(std::fabs(Bs_diff.Px()/Bs.Px())),
	  dPyratio(std::fabs((Bs_diff.Py()/Bs.Py()))),
	  dPzratio(std::fabs(Bs_diff.Pz()/Bs.Pz()));
	double gratio(dEratio + dPxratio + dPyratio + dPzratio);

	if (ispartial and (gratio < pgratio_cut)) {
	  DEBUG(msg_count, "Vetoing " << mode[i] << "_" << smp[i]
		<< " (" << gratio <<" < " << pgratio_cut << ")");
	  veto_counter++;
	  continue;
	} else if (not ispartial and (gratio > gratio_cut)) {
	  DEBUG(msg_count, "Vetoing " << mode[i] << "_" << smp[i] 
		<< " (" << gratio <<" > " << gratio_cut << ")");
	  veto_counter++;
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

	// DEBUG(msg_count, "Bs (" << BPID << ") mass from ntuple " << Bs.M());
	// DEBUG(msg_count, "Ds (" << DPID << ") mass from ntuple " << Ds.M());
	// DEBUG(msg_count, "bachelor (" << hPID << ") mass from ntuple " << bach.M());
	// DEBUG(msg_count, mode[i] << "_" << smp[i] << " 4-momenta before fit");
	// Bs.Print();
	// Ds.Print();
	// bach.Print();

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
	  ERROR(err_count, "DecayTreeTupleSucksFitter::fit(..) failed\n"
		<< mode[i] << "_" << smp[i] << " 4-momenta after fit\n"
		<< "Bs(t,x,y,z) = " << Blv[0] << "," << Blv[1] << ","
		<< Blv[2] << "," << Blv[3] << std::endl
		<< "Ds(t,x,y,z) = " << Dlv[0] << "," << Dlv[1] << ","
		<< Dlv[2] << "," << Dlv[3] << std::endl
		<< "h(t,x,y,z) = " << hlv[0] << "," << hlv[1] << ","
		<< hlv[2] << "," << hlv[3] << std::endl);
	  continue;
	}

	TLorentzVector fBs(Blv[1], Blv[2], Blv[3], Blv[0]),
	  fDs(Dlv[1], Dlv[2], Dlv[3], Dlv[0]),
	  fbach(hlv[1], hlv[2], hlv[3], hlv[0]),
	  fmiss(mlv[1], mlv[2], mlv[3], mlv[0]);
	TLorentzVector fstarred(0.0, 0.0, 0.0, 0.0);

	/*
	DEBUG(msg_count, mode[i] << "_" << smp[i] << " 4-momenta after fit");
	fBs.Print();
	fDs.Print();
	fbach.Print();
	if (ispartial) fmiss.Print();
	*/

	// No need to shift 4-momenta, no missing MC anymore

	// switch (current_mode) {
	// case Bd2DsKst:	// MC from Bd2DKst
	//   {
	//     fstarred = fmiss + fbach;

	//     TwoBodyDecay dmissing(fmiss);
	//     TwoBodyDecay dDs(fDs);
	//     TwoBodyDecay dbach(fbach);
	//     TwoBodyDecay dKst(fstarred, &dbach, &dmissing);
	//     TwoBodyDecay dBs(fBs, &dKst, &dDs);

	//     DEBUG(msg_count, "Bd2DsKst before");
	//     // dBs.Print();
	//     dBs.toRestFrame();
	//     dDs.setMass(DSMASS);
	//     dBs.update_momenta();
	//     dBs.toParentFrame();
	//     DEBUG(msg_count, "Bd2DsKst after");
	//     // dBs.Print();
	//   }
	//   break;

	// case Bd2DsstK:	// MC from Bs2DsstK
	//   {
	//     fstarred = fmiss + fDs;

	//     TwoBodyDecay dmissing(fmiss);
	//     TwoBodyDecay dDs(fDs);
	//     TwoBodyDecay dbach(fbach);
	//     TwoBodyDecay dDsstar(fstarred, &dDs, &dmissing);
	//     TwoBodyDecay dBs(fBs, &dDsstar, &dbach);

	//     DEBUG(msg_count, "Bd2DsstK before");
	//     // dBs.Print();
	//     dBs.toRestFrame();
	//     dBs.setMass(BDMASS);
	//     dBs.update_momenta();
	//     dBs.toParentFrame();
	//     DEBUG(msg_count, "Bd2DsstK after");
	//     // dBs.Print();
	//   }
	//   break;

	// case Bs2DsKst:	// MC from Bs2DsRho
	//   {
	//     fstarred = fmiss + fbach;

	//     TwoBodyDecay dmissing(fmiss);
	//     TwoBodyDecay dDs(fDs);
	//     TwoBodyDecay dbach(fbach);
	//     TwoBodyDecay dKst(fstarred, &dbach, &dmissing);
	//     TwoBodyDecay dBs(fBs, &dKst, &dDs);

	//     DEBUG(msg_count, "Bs2DsKst before");
	//     // dBs.Print();
	//     dBs.toRestFrame();
	//     dbach.setMass(KMASS);
	//     dKst.setMass(KSTMASS);
	//     dBs.update_momenta();
	//     dBs.toParentFrame();
	//     DEBUG(msg_count, "Bs2DsKst after");
	//     // dBs.Print();
	//   }
	//   break;
	// default:
	//   break;
	// }

	// PID reweighting
	if (isDsK) {
	  // weights for Bs2DsK
	  switch (current_mode) {
	  case Bd2DK:
	    {
	      wMC = hChild.GetWeight(lab4_P2,smp[i])*hBachEff.GetWeight(lab1_P2,smp[i]);
	    }
	    break;
	  case Lb2LcK:
	    {
	      wMC = hBachEff.GetWeight(lab1_P2,smp[i])*hBachEff.GetWeight(lab1_P2,smp[i]);
	    }
	    break;
	  case Lb2Dsstp:	// intentional pass, common weights for Lb with proton
	  case Lb2Dsp:
	    {
	      wMC = hProton.GetWeight(lab4_P2,smp[i])*hBach.GetWeight(lab1_P2,smp[i]);
	    }
	    break;
	  case Bs2DsstPi:	// common weight for modes with Pi
	  case Bs2DsRho:
	  case Bs2DsPi:
	    {
	      wMC = hBach.GetWeight(lab1_P2,smp[i]);
	    }
	    break;
	  default:		// typical modes with K
	    wMC = hBachEff.GetWeight(lab1_P2,smp[i]);
	    break;
	  }
	} else {
	  // weights for Bs2DsPi
	  switch (current_mode) {
	  case Lb2LcPi:
	    {
	      wMC = hProton.GetWeight(lab5_P2,smp[i])*hBachEff.GetWeight(lab1_P2,smp[i]);
	    }
	    break;
	  case Bd2DsPi:		// intentional pass, modes with Bd
	  case Bd2DPi:
	    {
	      wMC = hChild.GetWeight(lab4_P2,smp[i])*hBachEff.GetWeight(lab1_P2,smp[i]);
	    }
	    break;
	  case Bs2DsK:
	    {
	      wMC = hBach.GetWeight(lab1_P2,smp[i]);
	    }
	    break;
	  case Bs2DsstPi:  // nothing done, mode with Pi
	  default:
	    wMC = hBachEff.GetWeight(lab1_P2,smp[i]);
	    break;
	  }
	}

	// data-MC reweighting
	wRW = hRDM.GetWeight(log(lab1_PT2),log(nTr), smp[i]);

	// emulating mis-reconstruction
	Bs = fBs;
	Ds.SetVectM(fDs.Vect(), DSMASS);
	if (isDsK) bach.SetVectM(fbach.Vect(), KMASS);
	else bach.SetVectM(fbach.Vect(), PIMASS);
	Bs_rec = Ds + bach;

	kfactorp = Bs_rec.P() / Bs.P();
	kfactorm = Bs.M() / Bs_rec.M();
	kfactor = kfactorp * kfactorm;

	if (std::isnan(kfactor) || std::isinf(kfactor) || kfactor <= 0. ||
	    std::isnan(kfactorp) || std::isinf(kfactorp) || kfactorp <= 0.) {
	  DEBUG(msg_count, "K-factor is invalid: " << kfactor);
	  continue;
	}

	bool in_mass_win(false);

	if (mdSet->GetMassBRangeDown() <= 0
	    or mdSet->GetMassBRangeUp() <= 0
	    or mdSet->GetMassBRangeUp() == mdSet->GetMassBRangeDown()
	    or mdSet->GetMassDRangeDown() <= 0
	    or mdSet->GetMassDRangeUp() <= 0
	    or mdSet->GetMassDRangeUp() == mdSet->GetMassDRangeDown()) {
	  in_mass_win = true; 	// no mass window
	} else {
	  if (Bmass > mdSet->GetMassBRangeDown()
	      and Bmass < mdSet->GetMassBRangeUp()
	      and Dmass > mdSet->GetMassDRangeDown()
	      and Dmass < mdSet->GetMassDRangeUp()) { // Bs LHCb reco mass window
	    in_mass_win = true;
	  }
	}

	if (in_mass_win) {
	  mBdiff = Bs_rec.M() - Bs_ref.M();

	  // Fill selected events
	  mBresn.Fill();
	  kfactorVar.setVal(kfactor);
	  weight.setVal(wMC*wRW*globalWeight);
	  dataset.add(RooArgSet(kfactorVar, weight), weight.getVal());
	  fill_counter++;
	}
	loop_counter++;
      }	// end of loop over tree entries

      DEBUG(gmsg_count, "decay mode " << mode[i] << "_" << smp[i]);
      DEBUG(gmsg_count, "Looped " << loop_counter << ", Filled " << fill_counter);

      workspace->import(dataset);
      ffile.WriteObject(&mBresn, mBresn.GetName());

      // house cleaning
      TFile * treefile = ftree->GetCurrentFile();
      delete ftree;
      delete treefile;
    } // end of loop on datasets/modes

    DEBUG(gmsg_count, "Vetoed " << veto_counter << " events");
    return workspace;
  }

  //===========================================================================                                                                                                            
  // Get background category cut for signal MC                                                                                                                                             
  //===========================================================================  
  TCut GetBKGCATCutSig( MDFitterSettings* mdSet, bool debug)
  {
    TCut BKGCAT = "";

    //Set prefixes                                                                                                                                                                         
    TString DsPrefix    = "";
    TString BsPrefix    = "";

    DsPrefix = mdSet->GetPrefix(mdSet->GetMassDVar());
    BsPrefix = mdSet->GetPrefix(mdSet->GetMassBVar());
    
    BKGCAT = Form("(%s_BKGCAT < 30 || %s_BKGCAT == 50) && (%s_BKGCAT<30 || %s_BKGCAT == 50)",
		  BsPrefix.Data(),BsPrefix.Data(), DsPrefix.Data(), DsPrefix.Data());
    if ( debug ) { } 
    return BKGCAT; 
  }

  //===========================================================================                                                                                                            
  // Get MCID cut for signal MC                                                                                                                                                            
  //===========================================================================                                                                                                            
  TCut GetMCIDCutSig( MDFitterSettings* mdSet, TString hypo, TString modeD, bool debug)
  {
    TCut MCID = "";
    //Set id for bachelor //                                                                                                                                                               
    int id_lab1=0;
    if( hypo.Contains("Pi") ) { id_lab1=211; if ( debug == true) std::cout<<" Hypo with Pi"<<std::endl;}
    else if (hypo.Contains("K")) { id_lab1=321; if ( debug == true) std::cout<<"Hypo with K"<<std::endl; }

    // Set id for D children //                                                                                                                                     
    int id_lab4(0), id_lab3(0), id_lab5(0);
    if ( modeD.Contains("kkpi") == true || modeD.Contains("nonres") == true ||
         modeD.Contains("kstk") == true || modeD.Contains("phipi") == true || modeD.Contains("hhhpi0") == true)
      {
	id_lab3=211; id_lab4=321; id_lab5 = 321;
      }
    else if (modeD.Contains("kpipi") == true )
      {
	id_lab3=211; id_lab4=211; id_lab5 = 321;
      }
    else if (modeD.Contains("pipipi") == true )
      {
        id_lab3=211; id_lab4=211; id_lab5 = 211;
      }

    TString BachPrefix = mdSet->GetPrefix(mdSet->GetPIDKVar());
    TString DsCh1Prefix = mdSet->GetChildPrefix(0);
    TString DsCh2Prefix = mdSet->GetChildPrefix(1);
    TString DsCh3Prefix = mdSet->GetChildPrefix(2);
    
    MCID = Form("abs(%s_ID)==%d && abs(%s_ID)==%d && abs(%s_ID)==%d && abs(%s_ID)==%d",
		BachPrefix.Data(), id_lab1, DsCh1Prefix.Data(), id_lab5, DsCh3Prefix.Data(), id_lab3, DsCh2Prefix.Data(), id_lab4);
    if ( debug ) {} 
    return MCID; 

  }

  //===========================================================================                                                                                                            
  // Get MC TRUEID cut for signal MC                                                                                                                                                      
  //===========================================================================                                                                                                            
  TCut GetMCTRUEIDCutSig( MDFitterSettings* mdSet, TString hypo, TString modeD, bool debug)
  {
    TCut MCTRUEID = "";
    //Set id for bachelor //                                                                                                                                                               
    int id_lab1=0;
    if( hypo.Contains("Pi") ) { id_lab1=211; if ( debug == true) std::cout<<" Hypo with Pi"<<std::endl;}
    else if (hypo.Contains("K")) { id_lab1=321; if ( debug == true) std::cout<<"Hypo with K"<<std::endl; }

    // Set id for D children //                                                                                                                                                             
    int id_lab4(0), id_lab3(0), id_lab5(0);
    if ( modeD.Contains("kkpi") == true || modeD.Contains("nonres") == true ||
         modeD.Contains("kstk") == true || modeD.Contains("phipi") == true || modeD.Contains("hhhpi0") == true)
      {
        id_lab3=211; id_lab4=321; id_lab5 = 321;
      }
    else if (modeD.Contains("kpipi") == true )
      {
        id_lab3=211; id_lab4=211; id_lab5 = 321;
      }
    else if (modeD.Contains("pipipi") == true )
      {
        id_lab3=211; id_lab4=211; id_lab5 = 211;
      }

    TString BachPrefix = mdSet->GetPrefix(mdSet->GetPIDKVar());
    TString DsCh1Prefix = mdSet->GetChildPrefix(0);
    TString DsCh2Prefix = mdSet->GetChildPrefix(1);
    TString DsCh3Prefix = mdSet->GetChildPrefix(2);

    MCTRUEID = Form("abs(%s_TRUEID)==%d && abs(%s_TRUEID)==%d && abs(%s_TRUEID)==%d && abs(%s_TRUEID)==%d",
		    BachPrefix.Data(), id_lab1, DsCh1Prefix.Data(), id_lab5, DsCh3Prefix.Data(), id_lab3, DsCh2Prefix.Data(), id_lab4);
    if ( debug )  {} 
    return MCTRUEID;
  }


  //===========================================================================                                                                                                            
  // Get Ds Hypo cut for signal MC                                                                                                                                                 
  //===========================================================================                                                                                                            
  TCut GetDsHypoCutSig( MDFitterSettings* mdSet, TString modeD, bool debug)
  {
    TCut DHypo = "";
    TString BachPrefix = mdSet->GetPrefix(mdSet->GetPIDKVar());
    TString DsCh1Prefix = mdSet->GetChildPrefix(0);
    TString DsCh2Prefix = mdSet->GetChildPrefix(1);
    TString DsCh3Prefix = mdSet->GetChildPrefix(2);

    if ( modeD.Contains("kkpi") == true || modeD.Contains("nonres") == true ||
         modeD.Contains("kstk") == true || modeD.Contains("phipi") == true || modeD.Contains("hhhpi0") == true)
      {
        DHypo = Form("%s_M < 200 && %s_M > 200 && %s_M > 200",DsCh3Prefix.Data(), DsCh2Prefix.Data(), DsCh1Prefix.Data());
      }
    else if (modeD.Contains("kpipi") == true )
      {
        DHypo = Form("%s_M < 200 && %s_M < 200 && %s_M > 200",DsCh3Prefix.Data(), DsCh2Prefix.Data(), DsCh1Prefix.Data());
      }
    else if (modeD.Contains("pipipi") == true )
      {
        DHypo = Form("%s_M < 200 && %s_M < 200 && %s_M < 200",DsCh3Prefix.Data(), DsCh2Prefix.Data(), DsCh1Prefix.Data());
      }
    if ( debug ) {} 
    return DHypo; 

  }
  
  //===========================================================================                                                                                                            
  // Get global cut for signal MC                                                                                                                                                          
  //===========================================================================                            
  TCut GetCutMCSig( MDFitterSettings* mdSet, TString modeB, TString modeD, bool debug )
  {
    TCut cut = "";

    TCut P_cut      = mdSet->GetCut(mdSet->GetMomVar());
    TCut PT_cut     = mdSet->GetCut(mdSet->GetTrMomVar());
    TCut nTr_cut    = mdSet->GetCut(mdSet->GetTracksVar());
    TCut BDTG_cut   = mdSet->GetCut(mdSet->GetBDTGVar());
    TCut MCB        = mdSet->GetCut(mdSet->GetMassBVar());
    TCut MCD        = mdSet->GetCut(mdSet->GetMassDVar());
    Float_t c = 299792458.0;
    Float_t corr = c/1e9;
    TCut Time_cut = Form("%s[0] > %f && %s[0] < %f", mdSet->GetTimeVar().Data(), mdSet->GetTimeRangeDown()*corr,
                         mdSet->GetTimeVar().Data(), mdSet->GetTimeRangeUp()*corr);
    
    TCut BKGCATCut = "";
    if ( mdSet->CheckBKGCATCut(modeD) == true )
      {
        BKGCATCut = GetBKGCATCutSig( mdSet, debug);
      }

    TCut MCID = "";
    if ( mdSet->CheckIDCut(modeD) == true )
      {
	MCID = GetMCIDCutSig( mdSet, modeB, modeD, debug);
      }

    TCut MCTRUEID = "";
    if ( mdSet->CheckTRUEIDCut(modeD) == true )
      {
        MCTRUEID = GetMCTRUEIDCutSig( mdSet, modeB, modeD, debug);
      }
    
    TCut DHypo = "";
    if ( mdSet->CheckDsHypoCut(modeD) == true )
      {
	DHypo = GetDsHypoCutSig(mdSet, modeD,debug);
      }

    TCut addCuts = (TCut)mdSet->GetMCCuts(modeD);

    cut = MCID&&MCTRUEID&&MCD&&MCB&&P_cut&&BDTG_cut&&DHypo&&Time_cut&&addCuts&&BKGCATCut;

    if (debug == true )
      {
	std::cout<<"------Cut-----"<<std::endl;
	std::cout<<cut<<std::endl;
	std::cout<<"--------------"<<std::endl;
      }
    return cut;
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
			      MDFitterSettings* mdSet,
			      TString& mode,
			      Bool_t reweight,
			      Bool_t veto,
			      RooWorkspace* workspace,
			      Bool_t mistag,
			      double globalWeightMD,
			      double globalWeightMU,
			      PlotSettings* plotSet,
			      bool debug
			      )

  {
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ObtainSignal(...). "<<std::endl;
	std::cout<<"name of config file: "<<filesDir<<std::endl;
	std::cout<<"Data mode: "<<mode<<std::endl;
	std::cout<<"Reweight: "<<reweight<<std::endl;
	std::cout<<"Veto: "<<veto<<std::endl;
	
      }
    
    RooWorkspace* work = NULL;
    if (workspace == NULL){ work =  new RooWorkspace("workspace","workspace");}
    else {work = workspace; }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

    RooArgSet* obs = mdSet->GetObsSet(false, true, false, false, true, true);
    obs->Print("v");
    std::vector <TString> tN = mdSet->GetVarNames(true,false,false,true,true);
    for(unsigned int i = 0; i<tN.size(); i++ )
      {
	std::cout<<"tN: "<<tN[i]<<std::endl;
      }

    TString wname = "weights";
    RooRealVar* weight = new RooRealVar(wname.Data(), wname.Data(), 0.0, 5.0);
  
    if (  mdSet->CheckDataMCWeighting() == true ||  mdSet->CheckMassWeighting() == true || reweight == true)
      {
	obs->add(*weight);
      }
    std::vector <std::string> FileName;
    ReadOneName(filesDir,FileName,sig,debug);

    HistPID2D* hRDM = NULL;
    if (  mdSet->CheckDataMCWeighting() == true || reweight == true )
      {
	TString RDM = "#RatioDataMC2D";
	TString nameHistRDM = "histRatio";
	hRDM = new HistPID2D(nameHistRDM, nameHistRDM, filesDir, RDM); 
      }

    TTree* tree[2];
    
    for( int i=0; i<2; i++)
      {
	tree[i] = NULL;
	tree[i] = ReadTreeData(FileName,i, debug);
      }

    HistPID1D* heff = NULL;
    if (  mdSet->CheckMassWeighting() == true || reweight == true)
      {
	TString PID = "#PID";
	TString PID2 = "#PID2";
	
	TString histNamePre = "";
	TString histNameSuf = "";
	
	if( mdSet->GetPIDBach() == -5) { histNameSuf = "Minus5";}
	else { histNameSuf = Form("%d",mdSet->GetPIDBach()); }

	if ( mode.Contains("Pi") == true || mode.Contains("pi") == true){histNamePre = "MyPionEff_"; }
	else{ histNamePre = "MyKaonEff_";}
	
	TString namehist    = histNamePre+histNameSuf;
	heff = new HistPID1D(namehist, namehist, filesDir, PID, PID2);  
      }

    // Read sample (down,up) from path//
    TString smp[2], md[2], y[2];
    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
      md[i-1] = CheckDMode(sig, debug);
      y[i-1] = CheckDataYear(sig, debug);
      if ( md[i-1] == "kkpi" || md[i-1] == ""){ md[i-1] = CheckKKPiMode(sig, debug);}
      if ( y[i-1] != "") { y[i-1] = "_"+y[i-1]; }

    }
       
    if ( debug == true) std::cout<<"mode: "<<mode<<std::endl;
    
    TTree* treetmp = NULL;
    RooDataSet* dataSetMC[2];
    RooDataSet* dataSetMCtmp[2];
    
    Double_t wRW=0;
    Double_t wE = 0;
    
    for(int i = 0; i<2; i++)
    { 
      TCut MCCut = GetCutMCSig(mdSet,mode,md[i],debug);

      treetmp = TreeCut(tree[i], MCCut, smp[i], mode, debug);  //obtain new tree with applied all cuts//
      Int_t nentriesMC = treetmp->GetEntries();
      
      std::vector <TString> tB;
      std::vector <Double_t> varD; std::vector <Int_t> varI; std::vector <Float_t> varF;
      for(unsigned int k = 0; k<tN.size(); k++ )
	{
	  if ( tN[k] != "" ){ tB.push_back(treetmp->GetLeaf(tN[k].Data())->GetTypeName()); }
	  else { tB.push_back(""); }
	  InitializeRealObs(tB[k], varD, varI, varF, debug);
	}

      for(unsigned int k =0; k<tN.size(); k++ )
	{
	  SetBranchAddress(treetmp, tB[k], tN[k], varD[k], varI[k], varF[k], debug);
	}

      if ( mdSet->CheckDataMCWeighting() == true && smp[i] == "both"){ smp[i] = hRDM->GetPolarity(i); }
      if (  mdSet->CheckMassWeighting() == true  && smp[i] == "both"){ smp[i] = heff->GetPolarity(i); }

      Double_t globalWeight = 1.0;
      if( smp[i] == "up") { globalWeight = globalWeightMU; }
      else if ( smp[i] == "down" ) { globalWeight = globalWeightMD; }
      else if ( smp[i] == "both" ) { globalWeight = globalWeightMU+globalWeightMD; }
      if( debug == true ) { std::cout<<"[INFO] Global weight: "<<globalWeight<<std::endl; }
      
      TString name="dataSetMC_"+mode+"_"+smp[i]+"_"+md[i]+y[i];
      TString namehist = "dataHistMC"+mode+"_"+smp[i];
      dataSetMC[i] = NULL;

      if (reweight == true || mdSet->CheckDataMCWeighting() ||  mdSet->CheckMassWeighting())
	{
	  dataSetMC[i] = new RooDataSet(name.Data(),name.Data(), *obs, wname.Data());
	  dataSetMCtmp[i] = new RooDataSet(name.Data(),name.Data(), *obs, wname.Data());
	}
      else
	{
	  dataSetMC[i] = new RooDataSet(name.Data(),name.Data(), *obs);
	  dataSetMCtmp[i] = new RooDataSet(name.Data(),name.Data(), *obs);
	}
	
      for (Long64_t jentry=0; jentry<nentriesMC; jentry++) {
	treetmp->GetEntry(jentry); 

	Double_t nTr(0), pT(0), p(0), pidk(0);
	Double_t val(0);
	for(unsigned k = 0; k < tN.size(); k++)
	  {
	    Bool_t cat = false;
	    if ( tN[k] == mdSet->GetIDVar() ) { cat = true; }
	    if(  mdSet->CheckTagVar() == true )
	      {
		for(int m = 0; m<mdSet->GetNumTagVar(); m++)
		  {
		    if ( tN[k] ==  mdSet->GetTagVar(m) )
		      {
			cat = true;
			break;
		      }
		  }
	      }
	    TString name = mdSet->GetVarOutName(tN[k]);
	    if ( cat == true ) { val = SetValCatObs(mdSet, obs, name , tB[k], varD[k], varI[k], varF[k]); }
	    else{ val = SetValRealObs(mdSet, obs, name, tB[k], varD[k], varI[k], varF[k], mode); }
	    if ( tN[k] == mdSet->GetMomVar() ) { p = val; }
	    if ( tN[k] == mdSet->GetTrMomVar() ) { pT = val; }
	    if ( tN[k] == mdSet->GetTracksVar() ) { nTr = val; }
	    if ( tN[k] == mdSet->GetPIDKVar() ) { pidk = val; }
	  }
       
	if ( mdSet->CheckDataMCWeighting() == true )
	  {
	    wRW = hRDM->GetWeight(pT,nTr, smp[i]); 
	  }
	if (  mdSet->CheckMassWeighting() == true )
	  {
	    wE = heff->GetWeight(exp(p), smp[i]); 
	  }

	if (  mdSet->CheckDataMCWeighting() == true ||  mdSet->CheckMassWeighting() == true || reweight == true)
	  {
	    weight->setVal(wE*globalWeight); 
	    dataSetMC[i]->add(*obs,wRW*wE*globalWeight,0);
	  }
	else
	  {
	    dataSetMC[i]->add(*obs);
	  }
       
	if (mode.Contains("Pi"))
	  {
	    if ( pidk > mdSet->GetPIDBach())
	      {
		if( mdSet->CheckDataMCWeighting() == true ||  mdSet->CheckMassWeighting() == true || reweight == true )  { dataSetMCtmp[i]->add(*obs,wE*wRW*globalWeight,0); }
		else { dataSetMCtmp[i]->add(*obs); }
	      }
	  }
	else if ( mode.Contains("K") == true )
	  {
	    if ( pidk > log(mdSet->GetPIDBach()))
	      {
		if( mdSet->CheckDataMCWeighting() == true ||  mdSet->CheckMassWeighting() == true || reweight )  { dataSetMCtmp[i]->add(*obs,wE*wRW*globalWeight,0); }
		else { dataSetMCtmp[i]->add(*obs); }
	      }
	  }
	
	
      }
      
      /*
      const TTree* treeConst = dataSetMC[i]->tree();
      TTree* treeC = new TTree("DecayTree","DecayTree");
      treeC = treeConst->GetTree();
      treeC->SetName("DecayTree"); 
      if( debug == true ) { std::cout<<"[INFO] Create tree with entries: "<<treeC->GetEntries()<<std::endl;}
      
      TString nameFile = "Signal_"+mode+"_"+smp[i]+"_"+md[i]+"_PIDK"+histNameSuf+".root";
      TFile* outfile  = new TFile(nameFile.Data(),"RECREATE");
      treeC->Write();
      outfile->Write();
      outfile->Close();

      if( debug == true ) {  std::cout<<"[INFO] Close file: "<<nameFile<<std::endl; }
      if ( debug == true) std::cout<<"Number of entries: "<<dataSetMC[i]->numEntries()<<std::endl;
      */
      TString s = smp[i]+"_"+md[i];

      std::vector <TString> obsName;
      obsName.push_back(mdSet->GetMassBVarOutName());
      obsName.push_back(mdSet->GetMassDVarOutName());
      obsName.push_back(mdSet->GetPIDKVarOutName());
      obsName.push_back(mdSet->GetTimeVarOutName());
      obsName.push_back(mdSet->GetTerrVarOutName());
      if(  mdSet->CheckTagOmegaVar() == true )
	{
	  for(int k = 0; k<mdSet->GetNumTagOmegaVar(); k++)
	    {
	      obsName.push_back(mdSet->GetTagOmegaVarOutName(k));
	    }
	  TString corrName = "corr_"+mode+"_"+s;
	  GetCorrHist(dataSetMC[i], dataSetMCtmp[i], obs, obsName, corrName, plotSet, debug );
	}

      
      TString m = mode+"MC";

      if ( plotSet->GetStatus()  == true )
	{
	  for (unsigned int k = 0; k<tN.size(); k++ )
            {

	      Bool_t cat = false;
              if ( tN[k] == mdSet->GetIDVar() ) { cat = true; }
              if(  mdSet->CheckTagVar() == true )
                {
                  for(int m = 0; m<mdSet->GetNumTagVar(); m++)
                    {
                      if ( tN[k] ==  mdSet->GetTagVar(m) )
                        {
                          cat = true;
                          break;
                        }
                    }
                }
              if ( cat == false )
                {
                  TString name = mdSet->GetVarOutName(tN[k]);
                  RooRealVar* var = (RooRealVar*)obs->find(name.Data());
		  std::cout<<"var: "<<var->GetName()<<std::endl;
                  SaveDataSet(dataSetMC[i], var, s, mode, plotSet, debug);
                }
            }
	}


      if (mistag == true)
	{
	  std::cout<<"[WARNING] mistag option not available"<<std::endl;
	  /*
	  TString condition = mdSet->GetTagVar()+" != 0";
	  Int_t bin = 50;

	  RooAbsData*  dataRed = dataSetMC[i]->reduce(condition.Data());
	  TString histName = "hist_PhysBkg"+mode+"Pdf_m_"+smp[i]+"_mistag";
	  TH1* hist = dataRed->createHistogram(histName.Data(), *lab0_TAGOMEGA, RooFit::Binning(bin));

	  TString namepdf ="PhysBkg"+mode+"Pdf_m_"+smp[i]+"_mistag";
	  RooHistPdf* pdf = CreateHistPDF(hist, lab0_TAGOMEGA, namepdf, bin, debug);
	  work->import(*pdf);
	  */
	}

      work->import(*dataSetMC[i]);

    }
     
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
					TString mVar,
					TString mDVar,
					TString tagVar,
					TString tagOmegaVar,
					RooWorkspace* work, 
					Bool_t mistag,
					PlotSettings* plotSet,
					bool debug
					)
  {

    if ( debug == true)
      {
	std::cout << "[INFO] ==> GeneralUtils::CreatePdfSpecBackground(...)."
                  << " Obtain RooKeysPdf for partially reconstructed backgrounds"
                  << std::endl;
      }

    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }
    tagVar = tagVar;
    tagOmegaVar = tagOmegaVar; 

    std::vector <MCBackground*> MCBkgMU;
    Int_t numBkgMU = CheckNumberOfBackgrounds(filesDirMU,sigMU, debug);
    for(int i = 1; i<numBkgMU+1; i++ )
      {
        MCBkgMU.push_back(new MCBackground(Form("MCBkg%d",i),"MCBackground",filesDirMU,sigMU,i));
        MCBkgMU[i-1]->Print("v");
      }

    std::vector <MCBackground*> MCBkgMD;
    Int_t numBkgMD = CheckNumberOfBackgrounds(filesDirMD,sigMD, debug);
    for(int i = 1; i<numBkgMD+1; i++ )
      {
        MCBkgMD.push_back(new MCBackground(Form("MCBkg%d",i),"MCBackground",filesDirMD,sigMD,i));
        MCBkgMD[i-1]->Print("v");
      }
        
    //Merged data sets//
    double minsize = std::min(numBkgMU, numBkgMD);
    if (minsize) {}; // hush up compiler warning
  
    std::vector <RooDataSet*> data;
    std::vector <TString> mode;
    std::vector <RooKeysPdf*> pdfMC;
    std::vector <RooKeysPdf*> pdfDMC;
      
    RooRealVar* lab0_MM = GetObservable(work,mVar,debug);
    RooRealVar* lab2_MM = GetObservable(work,mDVar,debug);

    for( int i = 0; i<numBkgMU; i++)
    {
      TString modeMU = MCBkgMU[i]->GetMode(); 
      for (int j = 0; j < numBkgMD; j++)
	{
	  TString modeMD = MCBkgMD[j]->GetMode(); 
	  TString yearMD = MCBkgMD[j]->GetYear();
	  if ( yearMD != "" ) { yearMD = "_"+yearMD;}
	  // std::cout<<" modeMD: "<<modeMD[j]<<" modeMU: "<<modeMU[i]<<std::endl;
	  if ( modeMU == modeMD )
	    {

	      TString nmMD = modeMD+"_down"+yearMD;
	      TString nmMU = modeMU+"_up"+yearMD;
	      
	      TString nameMD="dataSetMC_"+nmMD;
	      RooDataSet*  dataMD = GetDataSet(work,nameMD,debug);
	      TString nameMU="dataSetMC_"+nmMU;
              RooDataSet*  dataMU = GetDataSet(work,nameMU,debug);
	      
	      TString namew = "weights";
	      RooDataSet* datatmpMD = NULL;
	      RooDataSet* datatmpMU = NULL;
	      const RooArgSet* obs = dataMD->get(); 
	      	      	      
	      datatmpMD = new RooDataSet(nameMD.Data(), nameMD.Data(), *obs, RooFit::Import(*dataMD), RooFit::WeightVar("weights"));
	      datatmpMU = new RooDataSet(nameMU.Data(), nameMU.Data(), *obs, RooFit::Import(*dataMU), RooFit::WeightVar("weights"));
	      datatmpMD->append(*datatmpMU);
	      if(debug == true) std::cout<<"dataMD: "<<dataMD->numEntries()<<" dataMU: "<<dataMU->numEntries()
					 <<" data: "<<datatmpMD->numEntries()<<std::endl;
	      
	      
	      data.push_back(datatmpMD);
	      mode.push_back(modeMD);
	      int sizeData = data.size();
                   
	      TString s="both"+yearMD;
	      TString m = modeMD;
	      
	      Double_t rhoMD = MCBkgMD[j]->GetRho();
	      Double_t rhoMU = MCBkgMU[i]->GetRho();
	      Double_t rho = rhoMD;
	      if (rhoMD != rhoMU ) { 
		rho = 1.5; 
		std::cout<<"[WARNING] Rho option different between magnet up and down: "<<rhoMD<<" != "<<rhoMU<<". Default option Rho=1.5 applied."<<std::endl;
	      } 
	      
	      TString mirrorMD = MCBkgMD[j]->GetMirror();
	      TString mirrorMU  = MCBkgMU[i]->GetMirror();
	      TString mirror = mirrorMD;
	      if ( mirrorMU != mirrorMD ) { std::cout<<"[WARNING] Mirror option different for magnet up and down: "
						     <<mirrorMD<<" != "<< mirrorMU<<". Default BothMirror applied."<<std::endl; }

	      pdfMC.push_back(CreatePDFMC(data[sizeData-1], lab0_MM, s, m, rho, mirror, debug));
	      int size = pdfMC.size();
	      if (plotSet->GetStatus() == true)
		{
		  SaveTemplate(data[sizeData-1], pdfMC[size-1], lab0_MM, s , m, plotSet, debug);
		}
	      
	      TString s1="both"+yearMD+"_Ds";
	      pdfDMC.push_back(CreatePDFMC(data[sizeData-1], lab2_MM, s1, m, rho, mirror, debug));
              int size1 = pdfDMC.size();
	      if (plotSet->GetStatus() == true)
		{
		  SaveTemplate(data[sizeData-1], pdfDMC[size1-1], lab2_MM, s , m, plotSet, debug);
		}
	      
	      work->import(*pdfMC[size-1]);
	      work->import(*pdfDMC[size1-1]);
	      
	      if (mistag == true)
		{
		  std::cout<<"[WARNING] mistag option not available"<<std::endl;
		  /*
		  TString condition = tagVar+" != 0";
		  RooRealVar* lab0_TAGOMEGA =  GetObservable(work, tagOmegaVar, debug);
		  Int_t bin = 50;

		  RooAbsData*  dataRed = data[sizeData-1]->reduce(condition.Data());
		  TString histName = "hist_PhysBkg"+modeMD[j]+"Pdf_m_both_mistag";
		  TH1* hist = dataRed->createHistogram(histName.Data(), *lab0_TAGOMEGA, RooFit::Binning(bin));
		  
		  TString namepdf ="PhysBkg"+modeMD[j]+"Pdf_m_both_mistag";
		  RooHistPdf* pdf = CreateHistPDF(hist, lab0_TAGOMEGA, namepdf, bin, debug);
		  work->import(*pdf);
		  */
		}
              
	    }
	}
    
    }
  return work;
  }

  RooWorkspace* CreatePdfSpecBackground(TString filesDirMU, TString sigMU,
                                        TString filesDirMD, TString sigMD,
					MDFitterSettings* mdSet,
                                        RooWorkspace* work,
                                        Bool_t mistag,
                                        PlotSettings* plotSet,
					bool debug
                                        )
  {
    if ( mistag == false )
      {
	TString nl = ""; 
	work =  CreatePdfSpecBackground(filesDirMU, sigMU,
					filesDirMD, sigMD,
					mdSet->GetMassBVarOutName(),
					mdSet->GetMassDVarOutName(),
					nl,
					nl,
					work,
					mistag,
					plotSet,
					debug
					);
      }
    else
      {
	work =  CreatePdfSpecBackground(filesDirMU, sigMU,
                                        filesDirMD, sigMD,
                                        mdSet->GetMassBVarOutName(),
                                        mdSet->GetMassDVarOutName(),
                                        mdSet->GetTagVarOutName(0),
                                        mdSet->GetTagOmegaVarOutName(0),
                                        work,
                                        mistag,
                                        plotSet,
                                        debug
                                        );
      }

    return work;

  }


  RooWorkspace* CreatePdfSpecBackground(MDFitterSettings* mdSet,
					TString& filesDir, TString& sig,
					TString obsName,
					TString mode,
					Double_t rho,
					TString mirror, 
					RooWorkspace* workspace,
                                        PlotSettings* plotSet,
                                        bool debug
                                        )
  {

    RooWorkspace* work = NULL;
    if (workspace == NULL ) { work =  new RooWorkspace("workspace","workspace"); }
    else { work = workspace; }

    std::vector <std::string> FileName;
    ReadOneName(filesDir,FileName,sig, debug);
    //TTree* tree[2];

    //Read sample (means down or up)  from path //                                                                                                                                              
    //Read mode (means D mode: kkpi, kpipi or pipipi) from path //                                                                                                                              
    TString smp[2], md[2], y[2];

    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
      md[i-1] = CheckDMode(sig, debug);
      y[i-1] = CheckDataYear(sig, debug);
      if ( md[i-1] == "kkpi" || md[i-1] == ""){ md[i-1] = CheckKKPiMode(sig, debug);}
      if ( y[i-1] != "") { y[i-1] = "_"+y[i-1]; }
      if ( md[i-1] != "") { md[i-1] = "_"+md[i-1]; }
    }
    
    RooRealVar* obs = GetObservable(work,obsName,debug);
    std::vector <RooDataSet*> data;

    for(int i = 0; i<2; i++)
      {
	TString name = "dataSet"+mode+"_"+smp[i]+md[i]+y[i];
        data.push_back(GetDataSet(work,name,debug));
      }
    data[0]->append(*data[1]);

    TString s1 = "both"+md[0]+y[0];

    if (mdSet->GetMassDVarOutName() == obsName )
      {
	s1 = s1+"_Ds"; 

      }
    RooKeysPdf* pdf = CreatePDFMC(data[0], obs, s1, mode, rho, mirror, debug);
    work->import(*pdf);

    if (plotSet->GetStatus() == true)
      {
	SaveTemplate(data[0], pdf, obs, s1 , mode, plotSet, debug);
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

  void ExpectedYield(TString& filesDir, TString& sigHypo, TString& sigOwn,
		     TString& sigPID_1, TString& PIDhist_1,
		     TString& sigPID_2, TString& PIDhist_2,
		     TString& sigPID_3, TString& PIDhist_3,
		     double Pcut_down, double Pcut_up,
		     double BDTG_down, double BDTG_up,
		     double Dmass_down, double Dmass_up,
		     TString &mVar, TString& mProbVar,
		     TString& mode,TString &mode2)
  {
    
    std::cout<<"[INFO] ==> GeneralUtils::ExpectedYield(...). Calculate expected yield misID backgrouds"<<std::endl;
    std::cout<<"name of config file: "<<filesDir<<std::endl;
    std::cout<<"hist1: "<<PIDhist_1<<std::endl;
    std::cout<<"hist2: "<<PIDhist_2<<std::endl;
    mProbVar = mProbVar;
    //Read MC samples//       
    std::vector <std::string> FileNameHypo;
    ReadOneName(filesDir,FileNameHypo,sigHypo, true);
        
    TTree* treeHypo[2];

    for( int i=0; i<2; i++)
      {
	treeHypo[i] = NULL;
	treeHypo[i] = ReadTreeData(FileNameHypo,i, true);
      }
    
    std::vector <std::string> FileNameOwn;
    ReadOneName(filesDir,FileNameOwn,sigOwn, true);

    TTree* treeOwn[2];

    for( int i=0; i<2; i++)
      {
        treeOwn[i] = NULL;
        treeOwn[i] = ReadTreeData(FileNameOwn,i, true);
      }

    // Check polarity of MC samples //
    TString smpHypo[2], smpOwn[2];
    for (int i=1; i<3; i++){
      smpHypo[i-1] = CheckPolarity(FileNameHypo[i], true);
      smpOwn[i-1] = CheckPolarity(FileNameOwn[i], true);
    }
    
    //Read names for PID histograms //
    std::vector <std::string> FileNamePID_1;  //the first half of the first histogram PIDhist_1
    std::vector <std::string> FileNamePID_2;  //the second half of the second histogram PIDhist_1
    std::vector <std::string> FileNamePID_3;  //the second half of the second histogram PIDhist_1

    std::vector <std::string> FileNamePID2_1; //the first half of the second histogram PIDhist_2
    std::vector <std::string> FileNamePID2_2; //the second half of the second histogram PIDhist_2
    std::vector <std::string> FileNamePID2_3; //the first half of the second histogram PIDhist_3
    
    ReadOneName(filesDir,FileNamePID_1,sigPID_1, true);
    ReadOneName(filesDir,FileNamePID_2,sigPID_2, true);
    ReadOneName(filesDir,FileNamePID_3,sigPID_3, true);
    
    if( sigPID_1 == "#PID" || sigPID_1 == "#PID2m2") 
      { 
	TString sigPID2_1=sigPID_1+"2";
	ReadOneName(filesDir,FileNamePID2_1,sigPID2_1, true); 
      }

    if( sigPID_2 == "#PID" || sigPID_2 == "#PID2m2")
      {
        TString sigPID2_2=sigPID_2+"2";
        ReadOneName(filesDir,FileNamePID2_2,sigPID2_2, true);
      }
    
    if( sigPID_3 == "#PID" || sigPID_3 == "#PID2m2")
      {
        TString sigPID3_2=sigPID_3+"2";
        ReadOneName(filesDir,FileNamePID2_3,sigPID3_2, true);
      }
    
    TH1F* h_1[2];
    TH1F* h_2[2];
    TH1F* h_3[2];

    TH1F* h_11[2];
    TH1F* h_21[2];
    TH1F* h_31[2];

    TH1F* h_12[2];
    TH1F* h_22[2];
    TH1F* h_32[2];

       
    TString namehist;
    //Read first PID histogram: PIDhist_1 //
    for( int i = 0; i<2; i++ )
      {
	std::cout<<FileNamePID_1[0]<<std::endl;
	std::cout<<FileNamePID_1[i+1]<<std::endl;
	h_11[i]=NULL;
	h_12[i]=NULL;
	h_11[i] = ReadPIDHist(FileNamePID_1,PIDhist_1,i, true); //load the first part
	h_11[i] ->SaveAs("Plot/hist11.root");
	if ( sigPID_1 == "#PID" || sigPID_1 == "#PID2m2" )
	  {
	    std::cout<<FileNamePID2_1[0]<<std::endl;
	    std::cout<<FileNamePID2_1[i+1]<<std::endl;
	    
	    h_12[i] = ReadPIDHist(FileNamePID2_1,PIDhist_1,i, true); //load the second part
	    h_1[i] = NULL;
	    h_1[i] = WeightHist(h_11[i],  h_12[i], true); //add both parts
	  }
	else {
	  h_1[i] = h_11[i];
	}
      }
    //Read second histogram PIDhist_2 (in case of lab4 and lab5) 
    if( mode != "BsDsPi" && mode != "BDK")
      {
	for( int i = 0; i<2; i++ )
	  {
	    std::cout<<FileNamePID_2[0]<<std::endl;
	    std::cout<<FileNamePID_2[i+1]<<std::endl;
	    h_21[i]=NULL;
	    h_21[i] = ReadPIDHist(FileNamePID_2,PIDhist_2,i, true); // load the first part
	    if ( sigPID_2 == "#PID" || sigPID_2 == "#PID2m2" )
	      {
		std::cout<<FileNamePID2_2[0]<<std::endl;
		std::cout<<FileNamePID2_2[i+1]<<std::endl;
		h_22[i]=NULL;
		h_22[i] = ReadPIDHist(FileNamePID2_2,PIDhist_2,i, true); // load the second part
		h_2[i] = NULL;
		h_2[i]=WeightHist(h_21[i],  h_22[i], true); // add both parts
	      }
	    else
	      {
		h_2[i]=h_21[i];
	      }
	  }
      }
    else
      {
	h_21[0] = NULL; h_21[1] = NULL;
	h_22[0] = NULL; h_22[1] = NULL;
	h_2[0]=NULL; h_2[1]=NULL;
      }
    
    if( mode != "BsDsPi" && mode != "BDK")
      {
	for( int i = 0; i<2; i++ )
	  {
	    std::cout<<FileNamePID_3[0]<<std::endl;
	    std::cout<<FileNamePID_3[i+1]<<std::endl;
	    h_31[i]=NULL;
	    h_31[i] = ReadPIDHist(FileNamePID_3,PIDhist_3, i, true); // load the first part
	    if ( sigPID_3 == "#PID" || sigPID_3 == "#PID2m2" )
	    {
	      std::cout<<FileNamePID2_3[0]<<std::endl;
	      std::cout<<FileNamePID2_3[i+1]<<std::endl;
	      h_32[i]=NULL;
	      h_32[i] = ReadPIDHist(FileNamePID2_3,PIDhist_3,i, true); // load the second part
	      h_3[i] = NULL;
	      h_3[i]=WeightHist(h_31[i],  h_32[i], true); // add both parts
	    }
	    else
	      {
		h_3[i]=h_31[i];
	    }
	  }
      }
    else
      {
        h_31[0] = NULL; h_31[1] = NULL;
        h_32[0] = NULL; h_32[1] = NULL;
        h_3[0]=NULL; h_3[1]=NULL;
      }
    
    ///h_1[0] -> SaveAs("Plot/h_10.root");
    //h_1[1] -> SaveAs("Plot/h_11.root");
    //h_2[0] -> SaveAs("Plot/h_20.root");
    //h_2[1] -> SaveAs("Plot/h_21.root");

    TString RDM = "#RatioDataMC2D";
    std::vector <std::string> FileNameRDM;
    ReadOneName(filesDir,FileNameRDM,RDM,true);
    
    TH2F* hrdm[2];

    TString namehistRDM;
    TString smpRDM[2];

    for( int i = 0; i<2; i++ )
      {
	hrdm[i] = NULL;
        namehistRDM = "histRatio";
        hrdm[i] = Read2DHist(FileNameRDM,namehistRDM,i,true);
	//hrdm[i]  = Read3DHist(FileNameRDM,namehistRDM,i);
        smpRDM[i] = CheckPolarity(FileNameRDM[i+1], true);
      }


    /*
    Int_t nbins = h_1[0] -> GetNbinsX();
    TAxis* axis=h_1[0]->GetXaxis();
    Double_t max = axis->GetXmax();
    Double_t min = axis->GetXmin();;
    //std::cout<<"min: "<<min<<" max: "<<max<<std::endl;
    RooBinning* Mom_Bin = new RooBinning(min,max,"P");
    for (int k = 1; k < nbins; k++ )
      {
	Double_t cen = h_1[0] -> GetBinCenter(k);
	Double_t width = h_1[0] -> GetBinWidth(k);
	max = cen + width/2; 
	//Mom_Bin->addUniform(1, min, max);
	Mom_Bin->addBoundary(max);
	//std::cout<<"k: "<<k<<" min: "<<min<<" max: "<<max<<" cen: "<<cen<<" =? "<<max-width/2<<" w: "<<width<<std::endl;
      }
    */ 
    TCut P_cut = Form("lab1_P > %f && lab1_P < %f",Pcut_down,Pcut_up);
    TCut BDTG_cut = Form("BDTGResponse_1 > %f && BDTGResponse_1 < %f",BDTG_down, BDTG_up);
    TCut Own_Cut=""; //cut under its own hypo
    TCut Hypo_Cut=""; //cut under different hypo

    TString nameMeson, nameHypo, nameDMeson, nameDHypo;
    TString nameRes="";

    if ( sigHypo.Contains("NonRes") == true ) {
      nameRes = "((!(abs(lab45_MM-1020)<20)) && (!(abs(lab34_MM-892.0) < 50.))) && !(lab45_MM > 1840) && !(lab2_FDCHI2_ORIVX < 2) && !(lab2_FD_ORIVX < 0)";
    }
    else if ( sigHypo.Contains("PhiPi") == true ) {
      nameRes = "(abs(lab45_MM-1020)<20) && !(lab45_MM > 1840) && !(lab2_FDCHI2_ORIVX < 2) && !(lab2_FD_ORIVX < 0)";
    }
    else if ( sigHypo.Contains("KstK") == true ) {
      nameRes = "((!(abs(lab45_MM-1020)<20 )) && ((abs(lab34_MM-892.0) < 50.))) && !(lab45_MM > 1840) && !(lab2_FDCHI2_ORIVX < 2) && !(lab2_FD_ORIVX < 0)";
    }
    else if (mode2 =="kpipi") {
      nameRes ="lab45_MM < 1750 && !(lab2_FDCHI2_ORIVX < 9) && !(lab2_FD_ORIVX < 0)";
    }
    else if (mode2 == "pipipi" ){
      nameRes = "!(lab35_MM > 1700 || lab45_MM > 1700) && !(lab2_FDCHI2_ORIVX < 9) && !(lab2_FD_ORIVX < 0)";
    }

    if(mode == "BdDPi" || mode == "Bd2DPi" || mode == "BDPi" || mode == "B2DPi")
      {
	nameMeson= "Bs->DsPi"; 
	nameHypo  = "Bd->DPi";
	nameDHypo = "D->KPiPi";
	if ( mode2 =="kkpi" )
	  {
	    nameDMeson = "Ds->KKPi";
	    Hypo_Cut = Form("lab4_M > 200 && lab3_M <200 && lab5_M > 200 && lab1_M < 200 && lab2_MM > %f && lab2_MM <%f && %s > 5300 && %s < 5600",
			    Dmass_down,Dmass_up,mVar.Data(),mVar.Data());
	    Own_Cut  = "lab4_M < 200 && lab1_M < 200 && lab3_M <200 && lab5_M > 200";
	    Hypo_Cut = Hypo_Cut&&nameRes;
	  }
	else if(mode2 == "kpipi")
	  {
	    nameDMeson = "Ds->KPiPi";
	    Own_Cut = "lab4_M < 200 && lab1_M < 200 && lab3_M <200 && lab5_M > 200";
	    Hypo_Cut = Form("lab4_M < 200 && lab3_M <200 && lab5_M > 200 && lab1_M < 200 && lab2_MM > %f && lab2_MM <%f && %s > 5300 && %s < 5600 ",
			    Dmass_down,Dmass_up,mVar.Data(),mVar.Data());
	    Hypo_Cut = Hypo_Cut&&nameRes;
	  }

      }
    else if ( mode=="LbLcPi")
      {
	Own_Cut = "lab1_M < 200 && lab3_M <200 && lab4_M > 200 && lab5_P> 5000";
	nameMeson = "Bs->DsPi";
        nameHypo = "Lb->LcPi";
        nameDHypo = "Lc->pKPi";
	if ( mode2 =="kpipi" )
	  {
	    nameDMeson = "Ds->KPiPi";
	    Hypo_Cut = Form("lab3_M < 200 && lab4_M < 200 && lab5_M >200 && lab1_M < 200 && lab2_MM > %f && lab2_MM <%f && %s > 5300 && %s < 6000 && lab5_P>5000 ",
			    Dmass_down,Dmass_up,mVar.Data(),mVar.Data());
	    Hypo_Cut = Hypo_Cut&&nameRes;
	  }
	else if(mode2 == "kkpi")
	  {
	    nameDMeson = "Ds->KKPi";
	    Hypo_Cut = Form("lab3_M < 200 && lab4_M > 200 && lab5_M >200 && lab1_M < 200 && lab2_MM > %f && lab2_MM <%f && %s > 5300 && %s < 6000 && lab5_P >5000",
			    Dmass_down,Dmass_up,mVar.Data(),mVar.Data());
	    Hypo_Cut = Hypo_Cut&&nameRes;
	  }
	else if(mode2 == "pipipi")
	  {
	    nameDMeson = "Ds->PiPiPi";
	    Hypo_Cut = Form("lab3_M < 200 && lab4_M < 200 && lab5_M <200 && lab1_M < 200 && lab2_MM > %f && lab2_MM <%f && %s > 5300 && %s < 6000 && lab5_P >5000",
			    Dmass_down,Dmass_up,mVar.Data(),mVar.Data());
	    Hypo_Cut = Hypo_Cut&&nameRes;
	  }
      }
    else if ( mode.Contains("DsPi") )
      {
	  nameMeson = "Bs->DsK";
          nameHypo = "Bs->DsPi";
	  if ( mode2 == "kkpi") {
	    nameDHypo = "Ds->KKPi";
	    Own_Cut = "lab1_M < 200 && lab3_M < 200 && lab4_M > 200 && lab5_M >200";
	    Hypo_Cut = Form("lab1_M > 200 && %s > 5300 && %s < 5800 && lab2_MM > 1930 && lab2_MM < 2015 && lab3_M < 200 && lab4_M > 200 && lab5_M >200",
			    mVar.Data(),mVar.Data());
	  } 
	  else if (mode2=="kpipi"){ 
	    nameDHypo = "Ds->KPiPi";
	    Own_Cut = "lab1_M < 200 && lab3_M < 200 && lab4_M < 200 && lab5_M >200";
	    Hypo_Cut = Form("lab1_M > 200 && %s > 5300 && %s < 5800 && lab2_MM > 1930 && lab2_MM < 2015 && lab3_M < 200 && lab4_M < 200 && lab5_M >200",
			    mVar.Data(),mVar.Data());
	  } else if (mode2 == "pipipi"){ 
	    nameDHypo = "Ds->PiPiPi";
	    Own_Cut = "lab1_M < 200 && lab3_M < 200 && lab4_M < 200 && lab5_M <200";
	    Hypo_Cut = Form("lab1_M > 200 && %s > 5300 && %s < 5800 && lab2_MM > 1930 && lab2_MM < 2015 && lab3_M < 200 && lab4_M < 200 && lab5_M <200",
			    mVar.Data(),mVar.Data());
	  }
	  Hypo_Cut = Hypo_Cut&&nameRes;
      }
    else if (mode.Contains("DsK"))
      {
	nameMeson = "Bs->DsPi";
	nameHypo = "Bs->DsK";
	if ( mode2 == "kkpi") {
	  nameDHypo = "Ds->KKPi";
	  Own_Cut = "lab1_M > 200 && lab3_M < 200 && lab4_M > 200 && lab5_M >200";
	  Hypo_Cut = Form("lab1_M < 200 && %s > 5300 && %s < 5800 && lab2_MM > 1930 && lab2_MM < 2015 && lab3_M < 200 && lab4_M > 200 && lab5_M >200",
			  mVar.Data(),mVar.Data());
	}
	else if (mode2=="kpipi"){
	  nameDHypo = "Ds->KPiPi";
	  Own_Cut = "lab1_M > 200 && lab3_M < 200 && lab4_M < 200 && lab5_M >200";
	  Hypo_Cut = Form("lab1_M < 200 && %s > 5300 && %s < 5800 && lab2_MM > 1930 && lab2_MM < 2015 && lab3_M < 200 && lab4_M < 200 && lab5_M >200",
			  mVar.Data(),mVar.Data());
	} else if (mode2 == "pipipi"){
	  nameDHypo = "Ds->PiPiPi";
	  Own_Cut = "lab1_M > 200 && lab3_M < 200 && lab4_M < 200 && lab5_M <200";
	  Hypo_Cut = Form("lab1_M < 200 && %s > 5300 && %s < 5800 && lab2_MM > 1930 && lab2_MM < 2015 && lab3_M < 200 && lab4_M < 200 && lab5_M <200",
			  mVar.Data(),mVar.Data());
	}
	Hypo_Cut = Hypo_Cut&&nameRes;
      }
    else if ( mode == "BDK" )
      {
	nameMeson = "Bd->DPi"; 
	nameHypo = "Bd->DK"; 
	Own_Cut = "lab1_M > 200";
	Hypo_Cut = Form("lab1_M < 200 && %s > 5000 && %s < 6000 && lab2_MM > %f && lab2_MM <%f && (lab2_MM-(sqrt(pow(sqrt(pow(lab4_M,2)+pow(lab4_P,2))+sqrt(pow(lab5_M,2)+pow(lab5_P,2)),2)-pow(lab4_PX+lab5_PX,2)-pow(lab4_PY+lab5_PY,2)-pow(lab4_PZ+lab5_PZ,2))) >200) && (lab2_MM-(sqrt(pow(sqrt(pow(lab5_M,2)+pow(lab5_P,2))+sqrt(pow(lab3_M,2)+pow(lab3_P,2)),2)-pow(lab5_PX+lab3_PX,2)-pow(lab5_PY+lab3_PY,2)-pow(lab5_PZ+lab3_PZ,2))) > 200) && !((sqrt(pow(sqrt(pow(lab5_M,2)+pow(lab5_P,2))+sqrt(pow(lab3_M,2)+pow(lab3_P,2)),2)-pow(lab5_PX+lab3_PX,2)-pow(lab5_PY+lab3_PY,2)-pow(lab5_PZ+lab3_PZ,2)))< 840 || (sqrt(pow(sqrt(pow(lab4_M,2)+pow(lab4_P,2))+sqrt(pow(lab5_M,2)+pow(lab5_P,2)),2)-pow(lab4_PX+lab5_PX,2)-pow(lab4_PY+lab5_PY,2)-pow(lab4_PZ+lab5_PZ,2))) < 840)",mVar.Data(),mVar.Data(),Dmass_down,Dmass_up);
      }
    else if ( mode == "LbDsp" || mode == "LbDsstp")
      {
	Own_Cut = "";
	Hypo_Cut = Form("lab1_M > 200 && %s > 5300 && %s < 5600",mVar.Data(),mVar.Data());
	//Hypo_Cut = "lab1_M > 200";
      } 

    TCut All_Own_cut = Own_Cut&&BDTG_cut;
    TCut All_Hypo_cut = Hypo_Cut&&BDTG_cut; //&&P_cut;
    std::cout<<All_Own_cut<<std::endl;
    std::cout<<All_Hypo_cut<<std::endl;
    
    Float_t ratio[2];

    TTree* ttmp[2];
    TTree* ttmp2[2];

    Double_t nE_lab45[2];   // number of events after weighting
    Double_t nE_lab1[2];
    Double_t nE_RAW[2];
    Double_t nE_lab1MisID[2];

    Long_t n_events_Hypo[2];
    Long_t n_events_Own[2];
    
    TString h_lab1_name; //histogram from tree for lab1
    TString h_hist2D_1_name;
    TString h_hist2D_2_name;
    TString heff10_name;
    TString heff0_name;
    TString hmisID5_name;
    
    Double_t nE_RDM[2];
    
    for(int i=0; i<2; i++)
      {
	ttmp[i] = NULL;
        ttmp[i] = TreeCut(treeOwn[i],All_Own_cut,smpOwn[i],mode, true);
	ttmp2[i] = NULL;
	ttmp2[i] = TreeCut(treeHypo[i],All_Hypo_cut,smpHypo[i],mode, true);
	n_events_Own[i] = ttmp[i]->GetEntries();
	//nentriesMC = ttmp2[i]->GetEntries();
	n_events_Hypo[i] = ttmp2[i]->GetEntries();
	ratio[i] = (Float_t)n_events_Hypo[i]/n_events_Own[i]; // ratio hypo/own events
	std::cout<<"initial_cut: "<<n_events_Own[i]<<" cut: "<<n_events_Hypo[i]<<" ratio: "<<ratio[i]<<std::endl; 
	
	nE_lab45[i] = 0; // number of events after weighting by PID histograms for lab4
	nE_lab1[i] = 0;
	nE_RAW[i] = 0;
	nE_RDM[i] = 0;

	Double_t lab3_P2, lab4_P2, lab5_P2, lab1_P2, lab1_PT2; 
	Int_t nTrack2; 
	Float_t hypo;

	ttmp2[i]->SetBranchAddress("lab3_P", &lab3_P2);
	ttmp2[i]->SetBranchAddress("lab4_P", &lab4_P2);
	ttmp2[i]->SetBranchAddress("lab5_P", &lab5_P2);
	ttmp2[i]->SetBranchAddress("lab1_P", &lab1_P2);
	ttmp2[i]->SetBranchAddress("lab1_PT", &lab1_PT2);
	ttmp2[i]->SetBranchAddress("nTracks", &nTrack2);

	Float_t masshypo = 0.0;
	Float_t tol = 0.0;

	if ( mode == "BdDPi" )
	  {
	    ttmp2[i]->SetBranchAddress("lab2_MassHypo_KKPi_Lambda", &hypo);
	    masshypo = 2285;
	    tol = 30;
	  }
	else if ( mode == "LbLcPi")
	  {
	    ttmp2[i]->SetBranchAddress("lab2_MassHypo_KKPi_D", &hypo);
	    masshypo = 1870;
	    tol = 30;
	  }

	/*
	TH1F* h_lab1 = new TH1F("h_lab1","h_lab1",Mom_Bin->numBins(), Mom_Bin->array());
	TString name2D = "lab4_P_Vs_lab5_P";
	TH2F* hist2D_1 = new TH2F(name2D.Data(),name2D.Data(), Mom_Bin->numBins(), Mom_Bin->array(), Mom_Bin->numBins(), Mom_Bin->array());
	hist2D_1 -> SetBins(Mom_Bin->numBins(), Mom_Bin->array(), Mom_Bin->numBins(), Mom_Bin->array());

	if (mode == "BdDPi" || mode == "LbLcPi" )
	  {
	    ttmp2[i]->Draw("lab1_P>>h_lab1","", "goff"); // take lab1_P as histogram 
	    ttmp2[i]->Draw("lab4_P:lab5_P>>lab4_P_Vs_lab5_P","", "goff"); // in case of BDPi, LcPi under BsDsPi, KPiPi take 2D histogram lab4_P vs lab5_P
	  }
	else
	  {
	    ttmp2[i]->Draw("lab1_P>>h_lab1","", "goff"); // take only lab1_P as histogram (for bachelor misID)
	  }
	h_lab1_name = h_lab1->GetName();
	h_hist2D_1_name = hist2D_1->GetName();
	std::cout<<"Number of events from MC sample in hist: "<<hist2D_1->GetEntries()<<std::endl;
	std::cout<<"Numbers of bins:"<<nbins<<std::endl;
	*/

	//Read MyKaonEff_5(10) and MyPionEff_0 for counting BDK and LcK under BsDsK 
	TH1F* heff0_1 = NULL;
	TH1F* heff10_1 = NULL;
	TH1F* hmisID5_1 = NULL;
	TH1F* heff0_2 = NULL;
	TH1F* heff10_2 = NULL;
	TH1F* hmisID5_2 = NULL;
	TH1F* heff0 = NULL;
        TH1F* heff10 = NULL;
	TH1F* hmisID5 = NULL;

	if ( heff0_1 ){}
	if ( heff10_1 ) {}
	if ( hmisID5_1) {}
	if ( heff0_2 ) {}
	if ( heff10_2 ) {}
	if ( hmisID5_2 ) {}
	if ( heff0  ) {}
	if ( heff10 ) {}
	if ( hmisID5 ) {}

	std::vector <std::string> FileNamePID2;
	TString sig2 = "#PID";
	ReadOneName(filesDir,FileNamePID2,sig2, true); //read name of the first histogram
	
	std::vector <std::string> FileNamePID3;
	TString sig3 = "#PID2";
	ReadOneName(filesDir,FileNamePID3,sig3, true); //read name of the second histogram
	
	TString name = "MyPionEff_0";
	heff0_1 = ReadPIDHist(FileNamePID2,name,i, true); // read the first part of MyPionEff_0
	heff0_2 = ReadPIDHist(FileNamePID3,name,i, true); // read the second part of MyPionEff_0 
	heff0_name = heff0_1->GetName();
	name = "MyKaonEff_5";
	heff10_1 = ReadPIDHist(FileNamePID2,name,i, true); // read the first part of MyKaonEff_5
	heff10_2 = ReadPIDHist(FileNamePID3,name,i, true); // read the seconf part of MyKaonEff_5
	heff10_name = heff10_1->GetName();
	
	heff0=WeightHist(heff0_1,  heff10_2, true);   // add both MyPionEff_0 histograms
	heff10=WeightHist(heff10_1,  heff10_2, true); // add both MyKaonEff_5 histograms 

	name = "MyPionMisID_5";
	hmisID5_1 = ReadPIDHist(FileNamePID2,name,i, true); // read the first part of MyKaonEff_5                                                    
        hmisID5_2 = ReadPIDHist(FileNamePID3,name,i, true); // read the seconf part of MyKaonEff_5                                             
	hmisID5_name = hmisID5_1->GetName();
	hmisID5=WeightHist(hmisID5_1, hmisID5_2, true); // add both MyKaonEff_5 histograms       

	hmisID5->SaveAs("hmisID5.root");

	TH1F* hpeff1 =NULL ;
	if ( hpeff1 ) {}
		
	if ( mode == "LbLcPi" )
	  {
	    TString pname = "MyProtonEff_pK5_p0";
	    hpeff1 =  ReadPIDHist(FileNamePID_3, pname, i, true);
	  }
	// for BDPi under BsDsPi, KPiPi take 2D histogram of lab4_P vs lab5_P from MC tree 
	/*
	TString h_1_name = h_1[i]->GetName();
	TString h_2_name = h_2[i]->GetName();
	name2D = h_1_name+"_Vs_"+ h_2_name;
	TH2F *hist2D_2 = new TH2F(name2D.Data(),name2D.Data(), Mom_Bin->numBins(), Mom_Bin->array(), Mom_Bin->numBins(), Mom_Bin->array());   
	h_hist2D_2_name = hist2D_2->GetName();
	if ( mode == "BdDPi" || mode == "LbLcPi" )
	  {
	    for (Int_t k=1;k<nbins;k++) 
	      {
		Double_t con2 = h_1[i]->GetBinContent(k);
		for (Int_t j=1;j<nbins;j++) 
		  {
		    Double_t con4 = h_2[i]->GetBinContent(j);
		    Double_t con = con2*con4;
		    hist2D_2->SetBinContent(k,j,con);
		    //std::cout<<"j: "<<j<<" k: "<<k<<" con2: "<<con2<<" con4: "<<con4<<" con: "<<con<<std::endl;
		  }
	      }
    	    
	  }
	std::cout<<"Number of events from MC sample in hist: "<<hist2D_2->GetEntries()<<std::endl;
        std::cout<<"[INFO] Everything is read"<<std::endl;

	hist2D_2->SaveAs("Plot/hist2D_2.root");
	hist2D_1->SaveAs("Plot/hist2D_1.root");
	*/

	//Magical weighting using PID histograms, depends on mode
	
	if(  mode == "BdDPi" || mode == "LbLcPi" ) // reweighting with change charm meson hypothesis 
	  {
	    
	    for (Long64_t jentry=0; jentry< n_events_Hypo[i]; jentry++) 
	      {
		ttmp2[i]->GetEntry(jentry);
		Float_t lab1_PT3F = lab1_PT2;
                Float_t nTr3F = nTrack2;
                Int_t binRW = hrdm[i]->FindBin(log(lab1_PT3F),log(nTr3F)); //,log(lab1_P3));
                Double_t wRW = hrdm[i]->GetBinContent(binRW);

		Double_t w4 = 1.0;
		//if( mode != "LbLcPi") 
		//  {
		Int_t bin4 = h_1[i]->FindBin(lab4_P2*wRW);
		w4 = h_1[i]->GetBinContent(bin4);
		    //  }
		Int_t bin5 = 1;  	
		Double_t w5 = 1.0;  
		if ( mode2 == "kkpi" )
		  {
		    if( fabs(hypo-masshypo) < tol) 
		      {
			bin5 = h_3[i]->FindBin(lab5_P2*wRW);
			w5 = h_3[i]->GetBinContent(bin5);
		      }
		    else
		      {
			bin5 = h_2[i]->FindBin(lab5_P2*wRW);
			w5 = h_2[i]->GetBinContent(bin5);
			  }
		  }
		else if( mode2 == "kpipi")
		  {
		    bin5 = h_2[i]->FindBin(lab5_P2*wRW);
		    w5 = h_2[i]->GetBinContent(bin5);
		  }
		Double_t w51 = 1.0; 
		if ( mode == "LbLcPi") 
		  {
		    bin5 = hpeff1->FindBin(lab5_P2*wRW);
		    w51 = hpeff1->GetBinContent(bin5);
		  }
		Double_t y = 0.0;
		if ( w51 > 0.0 ) { 
		  y = w4*w5/w51;
		  nE_RDM[i] = nE_RDM[i]+wRW;
		} 
		else { 
		  y = 0.0;  
		}
		
		nE_lab45[i] = nE_lab45[i]+y;
		    
	      }
	  }
	else if ( mode == "BDK" || mode == "BsDsK" || mode == "LbDsp" || mode == "LbDsstp" || mode == "BsDsPi" ) // only bachelor weighting
	  {

	    for (Long64_t jentry=0; jentry< n_events_Hypo[i]; jentry++)
              {
                ttmp2[i]->GetEntry(jentry);
		Float_t lab1_PT3F = lab1_PT2;
		Float_t nTr3F = nTrack2;
                Int_t binRW = hrdm[i]->FindBin(log(lab1_PT3F),log(nTr3F)); //,log(lab1_P3));
                Double_t wRW = hrdm[i]->GetBinContent(binRW);
		
                Int_t bin1 = h_1[i]->FindBin(lab1_P2*wRW);
                Double_t w1 = h_1[i]->GetBinContent(bin1);
		
		bin1 = heff0->FindBin(lab1_P2*wRW);
		Double_t weff = heff0->GetBinContent(bin1);
		Double_t weff2 = 1.0;

		if ( mode  == "BsDsPi") 
		  { 
		    bin1 = heff10->FindBin(lab1_P2*wRW); 
		    weff2 = heff10->GetBinContent(bin1); 
		  }
		if ( mode  == "BsDsK")  { weff = 1.0;}
                Double_t y = 0; 
		if ( weff != 0.0 ) { y = w1/weff*weff2;}

		nE_lab1[i] = nE_lab1[i]+y;
		nE_RAW[i] = nE_RAW[i]+w1;

              }
	  }
	
	//Plot results and obtain global misID//
	Double_t all_misID = 0;
	if( mode=="BdDPi" || mode =="LbLcPi" )
	  {
	    all_misID =nE_lab45[i]*ratio[i]/nE_RDM[i]; //n_events_Hypo[i];
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	    std::cout<<"For: "<<mode<<" "<<mode2<<" sample "<<smpOwn[i]<<std::endl;
	    std::cout<<"nE_lab45[i]: "<<nE_lab45[i]<<" nE_RDM[i]: "<<nE_RDM[i]<<std::endl;
	    std::cout<<"AllmisID: "<<nE_lab45[i]*ratio[i]/n_events_Hypo[i]*100<<"%"<<std::endl;
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	  }
	else if (mode == "BsDsPi" || mode == "BDK" || mode == "BsDsK" )
	  {
	    all_misID =nE_lab1[i]*ratio[i]/n_events_Hypo[i];
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	    std::cout<<"For: "<<mode<<" "<<mode2<<" sample"<<smpOwn[i]<<std::endl;
	    std::cout<<"misID RAW: "<<nE_RAW[i]<<" procent: "<<nE_RAW[i]*ratio[i]/n_events_Hypo[i]*100<<"%"<<std::endl;
	    std::cout<<"misID: "<<nE_lab1[i]<<" procent: "<<nE_lab1[i]*ratio[i]/n_events_Hypo[i]*100<<"%"<<std::endl;
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	  }
	else if (mode == "LbDsp" || mode == "LbDsstp")
	  {
	    all_misID = nE_lab1[i]*ratio[i]/n_events_Hypo[i];
            std::cout<<"----------------------------------------------------------------"<<std::endl;
            std::cout<<"For: "<<mode<<" "<<mode2<<" sample"<<smpOwn[i]<<std::endl;
            std::cout<<"misID: "<<nE_lab1[i]<<" procent: "<<nE_lab1[i]*ratio[i]/n_events_Hypo[i]*100<<"%"<<std::endl;
	    std::cout<<"total: "<<nE_lab1[i]/0.271811<<" procent: "<<nE_lab1[i]*ratio[i]/n_events_Hypo[i]*100/0.271811<<"%"<<std::endl;
            std::cout<<"----------------------------------------------------------------"<<std::endl;
	  }
	
	// Reweighting for DK and LcK under DsK by MyPionEff_0 and MyKaonEff_5 
	// with plotting results
	
	if ( mode == "BdDPi" || mode == "LbLcPi")
          {
	    for (Long64_t jentry=0; jentry< n_events_Hypo[i]; jentry++)
              {
                ttmp2[i]->GetEntry(jentry);
		Float_t lab1_PT3F = lab1_PT2;
		Float_t nTr3F = nTrack2;
                Int_t binRW = hrdm[i]->FindBin(log(lab1_PT3F),log(nTr3F)); //,log(lab1_P3));
                Double_t wRW = hrdm[i]->GetBinContent(binRW);
                
		Int_t bin1 = h_1[i]->FindBin(lab1_P2*wRW);
                Double_t w1 = h_1[i]->GetBinContent(bin1);
		
		bin1 = heff0->FindBin(lab1_P2*wRW);
		Double_t weff0 = heff0->GetBinContent(bin1);
		
		bin1 = heff10->FindBin(lab1_P2*wRW);
                Double_t weff10 = heff10->GetBinContent(bin1);

		bin1 = hmisID5->FindBin(lab1_P2*wRW);
                Double_t wmisID5 = hmisID5->GetBinContent(bin1);
                
		Double_t y=0;
		if ( weff0 != 0 && weff10 !=0) { y = w1/weff0*weff10;}

		Double_t y2=0;
		if ( weff0 != 0 && wmisID5 !=0) { y2 = w1/weff0*wmisID5;}
		
		nE_lab1[i] = nE_lab1[i]+y;
		nE_lab1MisID[i] = nE_lab1MisID[i]+y2;
		//std::cout<<"jentry: "<<jentry<<" "<<w1<<" "<<weff0<<" ";
		//std::cout<<weff10<<" "<<y<<td::endl;

              }
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	    std::cout<<"For bachelor K "<<mode2<<" sample"<<smpOwn[i]<<std::endl;
	    std::cout<<"eff1: "<<nE_lab1[i]<<" procent: "<<nE_lab1[i]/n_events_Hypo[i]*100<<"%"<<std::endl;
	    std::cout<<"misID1: "<<nE_lab1MisID[i]<<" procent: "<<nE_lab1MisID[i]/n_events_Hypo[i]*100<<"%"<<std::endl;
	    std::cout<<"All_misID: "<<all_misID*nE_lab1[i]/n_events_Hypo[i]*100<<"%"<<std::endl;
	    std::cout<<"All_misID2: "<<all_misID*nE_lab1MisID[i]/n_events_Hypo[i]*100<<"%"<<std::endl;
	    std::cout<<"----------------------------------------------------------------"<<std::endl;
	    
	  }
	
      }
    
    //Constant variable: branching fractions//
    //B(Bs->DsPi)//
    Float_t B_Bs_DsPi   = 3.2e-3;
    Float_t B_Bs_DsPi_u = 0.4e-3;
    //B(B->DPi)//
    Float_t B_Bd_DPi    = 2.68e-3;
    Float_t B_Bd_DPi_u  = 0.13e-3;
    //B(Lb->LcPi)//
    Float_t B_Lb_LcPi   = 5.7e-3;
    Float_t B_Lb_LcPi_u = 3.2e-3;  
    //B(Bs->DsK)//
    Float_t B_Bs_DsK   = 2.90e-4;
    Float_t B_Bs_DsK_u = 0.60e-4;
    //B(Lb->Dsp)//
    //Float_t B_Lb_Dsp   = 2e-6;
    //B(D->DK)//
    Float_t B_Bd_DK    = 1.94e-4;
    Float_t B_Bd_DK_u  = 0.21e-4;

    //B(D->KPiPi)//
    Float_t B_D_KPiPi   = 9.13e-2;
    Float_t B_D_KPiPi_u = 0.19e-2;
    //B(Ds->KKPi)//
    Float_t B_Ds_KKPi   = 5.49e-2;
    Float_t B_Ds_KKPi_u = 0.27e-2;
    //B(Ds->PiPiPi)//
    Float_t B_Ds_PiPiPi   = 0.0110;
    Float_t B_Ds_PiPiPi_u = 0.0006;
    //B(Ds->KPiPi)//
    Float_t B_Ds_KPiPi   = 6.9e-3;
    Float_t B_Ds_KPiPi_u = 0.5e-3;
    //B(Lc->pKPi)//
    Float_t B_Lc_pKPi   = 6.84e-2;
    Float_t B_Lc_pKPi_u = 0.24e-2;
      

    //fragmentation factor//
    Float_t fsfd = 0.259;
    Float_t fsfd_u = 0.015;
    Float_t flfd = 0.4;
    Float_t flfd_u = 0.0;

    Float_t B_1=0;
    Float_t B_2=0;
    Float_t B_u_1=0;
    Float_t B_u_2=0;
    
    Float_t B_3=0;
    Float_t B_4=0;
    Float_t B_u_3=0;
    Float_t B_u_4=0;
    Float_t frag =0;
    Float_t frag_u = 0;
    
    //set correct branching fration//
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
	frag = flfd;     frag_u = flfd_u;
      }
    else if( mode == "BsDsPi")
      {
	B_1 = B_Bs_DsPi; B_u_1 = B_Bs_DsPi_u;
	B_2 = B_Bs_DsK; B_u_2 = B_Bs_DsK_u;
	if ( mode2 == "kkpi") {B_3 = B_Ds_KKPi; B_u_3 = B_Ds_KKPi_u;} 
	else if (mode2 == "kpipi") {  B_3 = B_Ds_KPiPi; B_u_3 = B_Ds_KPiPi_u;}
 	else if (mode2 == "pipipi") { B_3 = B_Ds_PiPiPi; B_u_3 = B_Ds_PiPiPi_u;} 
	frag = fsfd; frag_u = fsfd_u;   
      }
    else if( mode == "BsDsK")
      {
	B_1 = B_Bs_DsK; B_u_1 = B_Bs_DsK_u;
        B_2 = B_Bs_DsPi; B_u_2 = B_Bs_DsPi_u;
        if ( mode2 == "kkpi") {B_3 = B_Ds_KKPi; B_u_3 = B_Ds_KKPi_u;}
        else if (mode2 == "kpipi") {  B_3 = B_Ds_KPiPi; B_u_3 = B_Ds_KPiPi_u;}
	else if (mode2 == "pipipi") { B_3 = B_Ds_PiPiPi; B_u_3 = B_Ds_PiPiPi_u;}
        frag = fsfd; frag_u = fsfd_u;
      }
    else if( mode =="BDK")
      {
	B_1 = B_Bd_DK; B_u_1 = B_Bd_DK_u;
        B_2 = B_Bd_DPi; B_u_2 = B_Bd_DPi_u;
      }


    //ratio of branching fractions for B mesons//
    Float_t rB_B     = B_1/B_2;  // branching fraction 1 / branching fraction 2 
    Float_t rB_B_u   = rB_B*std::sqrt(std::pow(B_u_1/B_1,2)+std::pow(B_u_2/B_2,2)); //uncertainty of branching ratios
    Float_t rB_B2=0;
    Float_t rB_B2_u=0;

    if( mode == "LbLcPi" || mode == "BsDsPi" || mode == "BsDsK")
      {
	rB_B2     = B_1/B_Bd_DPi*frag; // branchig fraction LbLcPi with respoect to DPi 
	rB_B2_u   = rB_B2*std::sqrt(std::pow(B_u_1/B_1,2) + std::pow(B_Bd_DPi_u/B_Bd_DPi,2) + std::pow(frag_u/frag,2)); // uncertainty
      }
    Double_t fake = rB_B2_u;
    
    //ratio of branching fractions for D mesons//
    Float_t rB_D=0; 
    Float_t rB_D_u=0;
    if ( mode != "BsDsPi" && mode != "BDK" && mode != "BsDsK") // for charm meson misID 
      {
	rB_D = B_3/B_4; 
	rB_D_u = rB_D*std::sqrt(std::pow(B_u_3/B_3,2)+std::pow(B_u_4/B_4,2)); //uncertainty
      }
    Float_t rB_D2=0; 
    Float_t rB_D2_u=0;
    if( mode == "LbLcPi" || mode =="BsDsPi" || mode == "BsDsK" ) // branching fraction B(Lc->pKPi) with respect to B(D->KPiPi);   
      {
        rB_D2 = B_3/B_D_KPiPi;
        rB_D2_u   = rB_D2*std::sqrt( std::pow(B_u_3/B_3,2) + std::pow(B_D_KPiPi_u/B_D_KPiPi,2) ); // uncertainty 
      }
    fake = rB_D2_u;
    if ( fake > 2.0 ) {}

    //Ratio N events : N(own)/N(hypo), applied fragmentation factor if necessary //
    Float_t rN=0;
    Float_t rN_u=0;
    Float_t rNBd=0;
    Float_t rNBd_u=0;
    if ( mode == "BdDPi") // number of expected DPi/DsPi events  
      {
	rN = rB_B*rB_D/fsfd;
	rN_u = rN*std::sqrt(std::pow(rB_B_u/rB_B,2) + std::pow(rB_D_u/rB_D,2) + std::pow(fsfd_u/fsfd,2));  // uncertainty
      }
    else if (mode == "LbLcPi" || mode == "BsDsPi" || mode == "BsDsK") // number of expected LcPi/DsPi and LcPi/DPi events 
      {
	rN = rB_B*rB_D;
        rN_u = rN*std::sqrt( std::pow(rB_B_u/rB_B,2) + std::pow(rB_D_u/rB_D,2)); // uncertainty
	rNBd = B_1/B_Bd_DPi*frag*B_3/B_D_KPiPi;
        rNBd_u = rNBd*std::sqrt( std::pow(B_u_1/B_1,2) + + std::pow(B_Bd_DPi_u/B_Bd_DPi,2)+ std::pow(B_u_3/B_3,2) + std::pow(B_D_KPiPi_u/B_D_KPiPi,2) ) ; // uncertainty
      }
    //    else if (mode == "BsDsPi" || mode == "BDK" || mode ==  "BsDsK") // number of N(own)/N(hypo) for bachelor misID
    //  {
    //	rN =rB_B; rN_u = rB_B_u;
    //  }
        
    
    //Some plotting, the most important information about branching ratios, applied cuts and so on // 
    std::cout<<"----------------------------------------------------------"<<std::endl;
    std::cout<<"Calculation for "<<nameHypo<<", "<<nameDHypo<<" under "<<nameMeson<<", "<<nameDMeson<<std::endl;
    std::cout<<"----------------------------------------------------------"<<std::endl;
    std::cout<<std::endl;
    std::cout<<"------------ Branching fractions for beauty mesons ------------"<<std::endl;
    std::cout<<"B("<<nameHypo<<")=("<<B_1<<" +/- "<<B_u_1<<")"<<std::endl;
    std::cout<<"B("<<nameMeson<<")=("<<B_2<<" +/- "<<B_u_2<<")"<<std::endl;
    
    std::cout<<"B("<<nameHypo<<")/B("<<nameMeson<<")=("<<rB_B<<" +/- "<<rB_B_u<<")"<<std::endl;
    if ( mode != "BsDsPi" && mode != "BDK")
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
    std::cout<<"==================== Selection ==========================="<<std::endl;
    std::cout<<"initial_cut: "<<Own_Cut<<std::endl;
    std::cout<<"Selected: DOWM: "<<n_events_Own[0]<<" UP: "<<n_events_Own[1]<<std::endl;
    std::cout<<"cut: "<<Hypo_Cut<<std::endl;
    std::cout<<"Selected: DOWM: "<<n_events_Hypo[0]<<" UP:"<<n_events_Hypo[1]<<std::endl;
    std::cout<<"ratio = NOE_cut/NOE_initial_cut"<<std::endl;
    std::cout<<"Obtained: DOWN: "<<ratio[0]<<" UP: "<<ratio[1]<<std::endl;
    
    Double_t corr = 0; 
    //Obtaining misID//
    if ( mode != "BsDsPi" && mode != "BDK" && mode != "BsDsK") //obtain misID in case where change charm meson hypo 
      {
	std::cout<<"---------------------- Histograms ------------------------"<<std::endl;
	std::cout<<"The histogram: "<<h_hist2D_1_name<<" is multiplied by "<<h_hist2D_2_name<<std::endl;
	//std::cout<<"The histogram: "<<h_lab5_name<<" is multiplied by "<<h_2[0]->GetName()<<std::endl;
	std::cout<<"The histogram: "<<h_lab1_name<<" is multiplied by "<<heff10_name<<" and divided by "<<heff0_name<<std::endl;

	std::cout<<"--------------- Calculations for histograms ---------------"<<std::endl;
	std::cout<<"===> calculations for lab4 "<<std::endl;
	std::cout<<"nE_lab45 = sum of "<<h_hist2D_1_name<<"*"<<h_hist2D_2_name<<std::endl;
	std::cout<<"DOWN: "<<nE_lab45[0]<<" UP: "<<nE_lab45[1]<<std::endl;
	std::cout<<"nE_lab45*ratio/NOE_cut ="<<std::endl;
	
	Float_t misID_1, misID_2; //misID
	if ( mode != "LbLcPi" )
	  {
	    misID_1 = nE_lab45[0]*ratio[0]/n_events_Hypo[0]; 
	    misID_2 = nE_lab45[1]*ratio[1]/n_events_Hypo[1]; 
	  }
	else
	  {
	    misID_1 = nE_lab45[0]/n_events_Hypo[0]; 
            misID_2 = nE_lab45[1]/n_events_Hypo[1]; 
	  }
	Float_t misID_av, misID_u;
	misID_av = (misID_1+misID_2)/2;
	misID_u =  std::sqrt((std::pow(misID_1-misID_av,2)+std::pow(misID_2-misID_av,2))/2)*1.41; //uncertainty
	
	std::cout<<"DOWN: "<<misID_1<<" UP: "<<misID_2<<std::endl;
	std::cout<<"= ("<<misID_av*100<<" +/- "<<misID_u*100<<")%"<<std::endl;
	std::cout<<std::endl;
	std::cout<<"===> Expected misID yield: "<<nameHypo<<","<<nameDHypo<<std::endl;
	std::cout<<"First method: "<<std::endl;
	/*
	Float_t misIDEff_1, misIDEff_2; //misID/Eff
	misIDEff_1 = misID_1*nE_lab1_Eff1[0]/n_events_Hypo[0];
	misIDEff_2 = misID_2*nE_lab1_Eff1[1]/n_events_Hypo[1];
	
	Float_t misIDEff_av, misIDEff_u;
	misIDEff_av = (misIDEff_1+misIDEff_2)/2;
        misIDEff_u =  std::sqrt((std::pow(misIDEff_1-misIDEff_av,2)+std::pow(misIDEff_2-misIDEff_av,2))/2)*1.41; //uncertainty
	*/
	
	Float_t fitted_BdDPi_1(0.0), fitted_BdDPi_1_u(0.0),  fitted_BdDPi_2(0.0), fitted_BdDPi_2_u(0.0); //fitted BDPi under its own hypo
	
	if ( mode != "LbLcPi" )
	  { 
	    if ( BDTG_down == 0.3 )
	      {
		if ( BDTG_up == 1.0)
		  {
		    if ( mode2 == "kkpi" ) { corr = 1.325365; } 
		    else if ( mode2 == "kpipi") { corr = 1.163431;} 
		    else if ( mode2 == "pipipi") { corr = 1.181686; }
		    
		    fitted_BdDPi_1   = 1.0964e+05*corr; //138330;
		    fitted_BdDPi_1_u = 357*corr; //427;
		    fitted_BdDPi_2   = 1.0964e+05*corr; //138330;
		    fitted_BdDPi_2_u = 357*corr; //427;
		  }
		else
		  {
		    if ( mode2 == "kkpi" ) { corr = 1.374069; }
		    else if ( mode2 == "kpipi") { corr = 1.166546;}
		    else if ( mode2 == "pipipi") { corr = 1.182656; }
		    
		    fitted_BdDPi_1   = 18366*corr; //23407;
		    fitted_BdDPi_1_u = 167*corr; //206;
		    fitted_BdDPi_2   = 18366*corr; //23407;
		    fitted_BdDPi_2_u = 167*corr; //206;
		  }
	      }
	    else if( BDTG_down == 0.5  && BDTG_up == 1.0)
	      {
		if ( mode2 == "kkpi" ) { corr = 1.321063; }
		else if ( mode2 == "kpipi") { corr = 1.163413;}
		else if ( mode2 == "pipipi") { corr = 1.181004; }
		
		fitted_BdDPi_1   = 103260*corr; //131290;
		fitted_BdDPi_1_u = 385*corr;
		fitted_BdDPi_2   = 103260*corr; //131290;
		fitted_BdDPi_2_u = 385*corr; //441;
	      }
	    else if( BDTG_down == 0.7 && BDTG_up == 0.9)
	      {
		if ( mode2 == "kkpi" ) { corr = 1.317133; }
		else if ( mode2 == "kpipi") { corr = 1.152342;}
		else if ( mode2 == "pipipi") { corr = 1.175217; }
		
		fitted_BdDPi_1   = 40271*corr; //51409;
		fitted_BdDPi_1_u = 271*corr; //289;
		fitted_BdDPi_2   = 40271*corr;
		fitted_BdDPi_2_u = 271*corr; //289;
	      }
	    else if( BDTG_down == 0.9 && BDTG_up == 1.0)
	      {
		if ( mode2 == "kkpi" ) { corr = 1.313953; }
		else if ( mode2 == "kpipi") { corr = 1.175892;}
		else if ( mode2 == "pipipi") { corr = 1.19494; }
		
		fitted_BdDPi_1   = 50565*corr; //64008;
		fitted_BdDPi_1_u = 235*corr; //274;
		fitted_BdDPi_2   = 50565*corr; //64008;
            fitted_BdDPi_2_u = 235*corr; //274;
	      }
	  }
	else
	  {
	    fitted_BdDPi_1   = 1.0; //64008;
	    fitted_BdDPi_1_u = 1.0; //274;
	    fitted_BdDPi_2   = 1.0; //64008;
            fitted_BdDPi_2_u = 1.0; //274;
	  }
	std::cout<<"===> Fitted yield to real data Bd->DPi, D->KPiPi"<<std::endl;
	std::cout<<"DOWN: ("<<fitted_BdDPi_1<<" +/- "<<fitted_BdDPi_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<fitted_BdDPi_2<<" +/- "<<fitted_BdDPi_2_u<<")"<<std::endl;
	/*
	if(mode == "LbLcPi")  // LcPi under DsPi calculated from BDPi 
	  {
	    Float_t temp, temp_u;
	    temp = fitted_BdDPi_1*rNBd;
	    temp_u = temp*std::sqrt(std::pow(fitted_BdDPi_1_u/fitted_BdDPi_1,2) + std::pow(rNBd_u/rNBd,2)); //uncertainty
	    fitted_BdDPi_1 = temp;
	    fitted_BdDPi_1_u = temp_u;
	    temp = fitted_BdDPi_2*rNBd;
	    temp_u = temp*std::sqrt(std::pow(fitted_BdDPi_2_u/fitted_BdDPi_2,2)  + std::pow(rNBd_u/rNBd,2)); //uncertainty
	    fitted_BdDPi_2 = temp;
	    fitted_BdDPi_2_u = temp_u;
	    std::cout<<"===> Fitted yield to real data Bd->DPi, D->KPiPi scaled by N(Lb->LcPi)/N(Bd->DPi)"<<std::endl;
	    std::cout<<"N(Lb->LcPi)/N(Bd->DPi)= B(Lb->LcPi)/B(Bd->DPi)*B(Lc->pKPi)/N(D->KPiPi)*fLc/fd"<<std::endl;
	    std::cout<<"("<<rNBd<<" +/- "<<rNBd_u<<")"<<std::endl;
	    std::cout<<"DOWN: ("<<fitted_BdDPi_1<<" +/- "<<fitted_BdDPi_1_u<<")"<<std::endl;
	    std::cout<<"UP: ("<<fitted_BdDPi_2<<" +/- "<<fitted_BdDPi_2_u<<")"<<std::endl;
	  }
	*/
	std::cout<<"===> Number of expected events = fitted yield multiplied by expected misID"<<std::endl;
    
	Float_t N_ev_1=0;
	Float_t N_ev_1_u=0; 
	Float_t N_ev_2=0; 
	Float_t N_ev_2_u=0;
	N_ev_1 = fitted_BdDPi_1*misID_av; // number of misID events 
	N_ev_1_u = N_ev_1*std::sqrt(std::pow(misID_u/misID_av,2) + std::pow(fitted_BdDPi_1_u/fitted_BdDPi_1,2)); //uncertainty
	N_ev_2 = fitted_BdDPi_2*misID_av; // number of misID events
	N_ev_2_u = N_ev_2*std::sqrt( std::pow(misID_u/misID_av,2) + std::pow(fitted_BdDPi_2_u/fitted_BdDPi_2,2)); //uncertainty
	std::cout<<"----------------------------------------------------"<<std::endl;
	std::cout<<"DOWN: ("<<N_ev_1<<" +/- "<<N_ev_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<N_ev_2<<" +/- "<<N_ev_2_u<<")"<<std::endl;
	std::cout<<"----------------------------------------------------"<<std::endl;
	/*
	std::cout<<std::endl;
	std::cout<<"Second method (using branching ratios): "<<std::endl;
	std::cout<<"===> misID*N("<<nameHypo<<")/N("<<nameMeson<<") ="<<std::endl;
	
	Float_t N2_ev_1=0;
	Float_t N2_ev_1_u=0;
	N2_ev_1 = rN*misID_av; 
	N2_ev_1_u = N2_ev_1*std::sqrt( std::pow(misID_u/misID_av,2) + std::pow(rN_u/rN,2));
	std::cout<<"("<<N2_ev_1<<" +/- "<<N2_ev_1_u<<")"<<std::endl;
	*/

	Float_t fitted_BsDsPi_1=0; 
	Float_t fitted_BsDsPi_1_u=0; 
	Float_t fitted_BsDsPi_2=0; 
	Float_t fitted_BsDsPi_2_u=0;
	
	if( mode2 == "kkpi")
	  {
	    // BDTG> 0.3
	    //  fitted_BsDsPi_1   = 1.3690e4;
	    //  fitted_BsDsPi_1_u = 1.33e2;
	    //  fitted_BsDsPi_2   = 9.6268e3;
	    //  fitted_BsDsPi_2_u = 1.10e2;
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
	/*
	std::cout<<"===> Fitted yield to real data "<<nameMeson<<","<<nameDMeson<<std::endl;
	std::cout<<"DOWN: ("<<fitted_BsDsPi_1<<" +/- "<<fitted_BsDsPi_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<fitted_BsDsPi_2<<" +/- "<<fitted_BsDsPi_2_u<<")"<<std::endl;
	
	std::cout<<"===> Number of expected events = fitted yield multiplied by expected misID"<<std::endl;
	Float_t N3_ev_1=0;
	Float_t N3_ev_1_u=0;
	Float_t N3_ev_2=0;
	Float_t N3_ev_2_u=0;
	
	N3_ev_1 = fitted_BsDsPi_1*N2_ev_1;
	N3_ev_1_u = N3_ev_1*std::sqrt( std::pow(N2_ev_1_u/N2_ev_1,2) + std::pow(fitted_BsDsPi_1_u/fitted_BsDsPi_1,2)); //uncertainty
	
	N3_ev_2 = fitted_BsDsPi_2*N2_ev_1;
	N3_ev_2_u = N3_ev_1*std::sqrt( std::pow(N2_ev_1_u/N2_ev_1,2) + std::pow(fitted_BsDsPi_2_u/fitted_BsDsPi_2,2)); //uncertainty
	std::cout<<"----------------------------------------------------"<<std::endl;
	std::cout<<"DOWN: ("<<N3_ev_1<<" +/- "<<N3_ev_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<N3_ev_2<<" +/- "<<N3_ev_2_u<<")"<<std::endl;
	std::cout<<"----------------------------------------------------"<<std::endl;
	*/
	std::cout<<std::endl;
	std::cout<<"===> calculations for lab1 "<<std::endl;
	std::cout<<"nE_lab1_Eff1 = sum of "<<h_lab1_name<<"*"<<heff10_name<<"/"<<heff0_name<<std::endl;
	std::cout<<"DOWN: "<<nE_lab1[0]<<" UP: "<<nE_lab1[1]<<std::endl;
	//std::cout<<"nE_lab1_Eff1 = sum of "<<h_lab1_name<<"*"<<heff10_name<<std::endl;
	//std::cout<<"DOWN: "<<nE_lab1_Eff1[0]<<" UP: "<<nE_lab1_Eff2[1]<<std::endl;
	std::cout<<"nE_lab1*NOE_cut ="<<std::endl;

	Float_t misID_lab1_1, misID_lab1_2;
	misID_lab1_1 = nE_lab1[0]/n_events_Hypo[0]; //*nE_lab1_Eff2[0]/n_events_Hypo[0];
	misID_lab1_2 = nE_lab1[1]/n_events_Hypo[1]; //*nE_lab1_Eff2[0]/n_events_Hypo[0];;

	std::cout<<"DOWN: "<<misID_lab1_1<<" UP: "<<misID_lab1_2<<std::endl;

	Float_t misID_lab1_av, misID_lab1_u;
	misID_lab1_av = (misID_lab1_1+misID_lab1_2)/2;
	misID_lab1_u = std::sqrt((std::pow(misID_lab1_1-misID_lab1_av,2)+std::pow(misID_lab1_2-misID_lab1_av,2))/2)*1.414214;

	std::cout<<"= ("<<misID_lab1_av*100<<" +/- "<<misID_lab1_u*100<<")%"<<std::endl;
	
	std::cout<<std::endl;
	std::cout<<"===> misID for K mode"<<std::endl;
	std::cout<<"result_K = result*nE_lab1/NOE_cut"<<std::endl;

	Float_t misID_lab1_all, misID_lab1_all_u;
	misID_lab1_all = misID_lab1_av*misID_av;
	misID_lab1_all_u = misID_lab1_all*std::sqrt( std::pow(misID_lab1_u/misID_lab1_av,2)  +  std::pow(misID_u/misID_av,2));

	std::cout<<"= ("<<misID_lab1_all*100<<" +/- "<<misID_lab1_all_u*100<<")%"<<std::endl;
    
	std::cout<<"===> Number of expected events for K mode"<<std::endl;
	std::cout<<"First method: "<<std::endl;
	std::cout<<"N_events_K = result_K*fitted_yield_BdPi/15"<<std::endl;

	Float_t NK_ev_1, NK_ev_1_u, NK_ev_2, NK_ev_2_u;
	NK_ev_1 = fitted_BdDPi_1*misID_lab1_all/15;
	NK_ev_1_u = NK_ev_1*std::sqrt( std::pow(misID_lab1_all_u/misID_lab1_all,2) + std::pow(fitted_BdDPi_1_u/fitted_BdDPi_1,2));
	NK_ev_2 = fitted_BdDPi_2*misID_lab1_all/15;
	NK_ev_2_u = NK_ev_2*std::sqrt( std::pow(misID_lab1_all_u/misID_lab1_all,2) + std::pow(fitted_BdDPi_2_u/fitted_BdDPi_2,2));

	std::cout<<"----------------------------------------------------"<<std::endl;
	std::cout<<"DOWN: ("<<NK_ev_1<<" +/- "<<NK_ev_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<NK_ev_2<<" +/- "<<NK_ev_2_u<<")"<<std::endl;
	std::cout<<"----------------------------------------------------"<<std::endl;

	//---- DPi under DsK ---//
	Float_t misID_lab1_m1, misID_lab1_m2;
        misID_lab1_m1 = nE_lab1MisID[0]/n_events_Hypo[0]; //*nE_lab1_Eff2[0]/n_events_Hypo[0];                                                          
        misID_lab1_m2 = nE_lab1MisID[1]/n_events_Hypo[1]; //*nE_lab1_Eff2[0]/n_events_Hypo[0];;  
	std::cout<<"DOWN: "<<misID_lab1_m1<<" UP: "<<misID_lab1_m2<<std::endl;

        Float_t misID_lab1_mav, misID_lab1_mu;
        misID_lab1_mav = (misID_lab1_m1+misID_lab1_m2)/2;
        misID_lab1_mu = std::sqrt((std::pow(misID_lab1_m1-misID_lab1_mav,2)+std::pow(misID_lab1_m2-misID_lab1_mav,2))/2)*1.414214;

	std::cout<<"= ("<<misID_lab1_mav*100<<" +/- "<<misID_lab1_mu*100<<")%"<<std::endl;

	std::cout<<std::endl;
	std::cout<<"===> misID for K mode"<<std::endl;
	std::cout<<"result_K_misID = result*nE_lab1MisID/NOE_cut"<<std::endl;

        Float_t misID_lab1_mall, misID_lab1_mall_u;
        misID_lab1_mall = misID_lab1_mav*misID_av;
        misID_lab1_mall_u = misID_lab1_mall*std::sqrt( std::pow(misID_lab1_mu/misID_lab1_mav,2)  +  std::pow(misID_u/misID_av,2));

	std::cout<<"= ("<<misID_lab1_mall*100<<" +/- "<<misID_lab1_mall_u*100<<")%"<<std::endl;
	
	std::cout<<"===> Number of expected events for K mode"<<std::endl;
	std::cout<<"First method: "<<std::endl;
	std::cout<<"N_events_K_misID = result_K_misID*fitted_yield_BdPi"<<std::endl;

        Float_t NK_mev_1, NK_mev_1_u, NK_mev_2, NK_mev_2_u;
        NK_mev_1 = fitted_BdDPi_1*misID_lab1_mall;
        NK_mev_1_u = NK_mev_1*std::sqrt( std::pow(misID_lab1_mall_u/misID_lab1_mall,2) + std::pow(fitted_BdDPi_1_u/fitted_BdDPi_1,2));
	NK_mev_2 = fitted_BdDPi_2*misID_lab1_mall;
        NK_mev_2_u = NK_mev_2*std::sqrt( std::pow(misID_lab1_mall_u/misID_lab1_mall,2) + std::pow(fitted_BdDPi_2_u/fitted_BdDPi_2,2));

	std::cout<<"----------------------------------------------------"<<std::endl;
	std::cout<<"DOWN: ("<<NK_mev_1<<" +/- "<<NK_mev_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<NK_mev_2<<" +/- "<<NK_mev_2_u<<")"<<std::endl;
	std::cout<<"----------------------------------------------------"<<std::endl;
	
	std::cout<<std::endl;
	std::cout<<"Second method: "<<std::endl;
	std::cout<<"===> result_K*N("<<nameHypo<<")/N("<<nameMeson<<")/15 ="<<std::endl;

	Float_t NK2_ev_1, NK2_ev_1_u;
	NK2_ev_1 = rN*misID_lab1_all/15;
	NK2_ev_1_u = NK2_ev_1*std::sqrt(std::pow(misID_lab1_all_u/misID_lab1_all,2) + std::pow(rN_u/rN,2));
	std::cout<<"("<<NK2_ev_1<<" +/- "<<NK2_ev_1_u<<")"<<std::endl;
	
	std::cout<<"===> Number of expected events = fitted yield multiplied by expected misID(=result_K)"<<std::endl;

	Float_t NK3_ev_1, NK3_ev_1_u, NK3_ev_2, NK3_ev_2_u;
	NK3_ev_1 = fitted_BsDsPi_1*NK2_ev_1;
	NK3_ev_1_u = NK3_ev_1*std::sqrt(std::pow(NK2_ev_1_u/NK2_ev_1,2) + std::pow(fitted_BsDsPi_1_u/fitted_BsDsPi_1,2));

	NK3_ev_2 = fitted_BsDsPi_2*NK2_ev_1;
	NK3_ev_2_u = NK3_ev_1*std::sqrt( std::pow(NK2_ev_1_u/NK2_ev_1,2) + std::pow(fitted_BsDsPi_2_u/fitted_BsDsPi_2,2));

	std::cout<<"----------------------------------------------------"<<std::endl;
	std::cout<<"DOWN: ("<<NK3_ev_1<<" +/- "<<NK3_ev_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<NK3_ev_2<<" +/- "<<NK3_ev_2_u<<")"<<std::endl;
	std::cout<<"----------------------------------------------------"<<std::endl;

      }
    else // misID for bachelor
      {

	std::cout<<"===> misID ="<<std::endl;

        Float_t misID_lab1_av, misID_lab1_u, misID_lab1_1, misID_lab1_2; //misID
	misID_lab1_1 = nE_lab1[0]*ratio[0]/n_events_Hypo[0];
	misID_lab1_2 = nE_lab1[1]*ratio[1]/n_events_Hypo[1];
        misID_lab1_av = (misID_lab1_1+misID_lab1_2)/2;
        misID_lab1_u = std::sqrt((std::pow(misID_lab1_1-misID_lab1_av,2) + std::pow(misID_lab1_2-misID_lab1_av,2))/2)*1.414214;
        std::cout<<"("<<misID_lab1_av*100<<" +/- "<<misID_lab1_u*100<<")%"<<std::endl;

        Float_t fitted_BdDPi_1=0; 
	Float_t fitted_BdDPi_1_u=0;  
	Float_t fitted_BdDPi_2=0; 
	Float_t fitted_BdDPi_2_u=0;
	
	if ( BDTG_down == 0.3 )
          {
            if ( BDTG_up == 1.0)
              {
                if ( mode2 == "kkpi" ) { corr = 1.325365; }
		else if ( mode2 == "kpipi") { corr = 1.163431;}
		else if ( mode2 == "pipipi") { corr = 1.181686; }

                fitted_BdDPi_1   = 1.0964e+05*corr; //138330;
                fitted_BdDPi_1_u = 357*corr; //427;
                fitted_BdDPi_2   = 1.0964e+05*corr; //138330;
		fitted_BdDPi_2_u = 357*corr; //427;
	      }
            else
              {
		if ( mode2 == "kkpi" ) { corr = 1.374069; }
                else if ( mode2 == "kpipi") { corr = 1.166546;}
                else if ( mode2 == "pipipi") { corr = 1.182656; }

		fitted_BdDPi_1   = 18366*corr; //23407;
                fitted_BdDPi_1_u = 167*corr; //206;
		fitted_BdDPi_2   = 18366*corr; //23407;
                fitted_BdDPi_2_u = 167*corr; //206;
              }
          }
	else if( BDTG_down == 0.5  && BDTG_up == 1.0)
          {
            if ( mode2 == "kkpi" ) { corr = 1.321063; }
            else if ( mode2 == "kpipi") { corr = 1.163413;}
            else if ( mode2 == "pipipi") { corr = 1.181004; }

            fitted_BdDPi_1   = 103260*corr; //131290;
            fitted_BdDPi_1_u = 385*corr;
            fitted_BdDPi_2   = 103260*corr; //131290;
            fitted_BdDPi_2_u = 385*corr; //441;
          }
        else if( BDTG_down == 0.7 && BDTG_up == 0.9)
          {
            if ( mode2 == "kkpi" ) { corr = 1.317133; }
            else if ( mode2 == "kpipi") { corr = 1.152342;}
            else if ( mode2 == "pipipi") { corr = 1.175217; }

            fitted_BdDPi_1   = 40271*corr; //51409;
            fitted_BdDPi_1_u = 271*corr; //289;
            fitted_BdDPi_2   = 40271*corr;
            fitted_BdDPi_2_u = 271*corr; //289;
          }
	else if( BDTG_down == 0.9 && BDTG_up == 1.0)
          {
            if ( mode2 == "kkpi" ) { corr = 1.313953; }
            else if ( mode2 == "kpipi") { corr = 1.175892;}
            else if ( mode2 == "pipipi") { corr = 1.19494; }

            fitted_BdDPi_1   = 50565*corr; //64008;
            fitted_BdDPi_1_u = 235*corr; //274;
            fitted_BdDPi_2   = 50565*corr; //64008;
            fitted_BdDPi_2_u = 235*corr; //274;
          }

	std::cout<<"===> Fitted yield to real data Bd->DPi, D->KPiPi"<<std::endl;
	std::cout<<"DOWN: ("<<fitted_BdDPi_1<<" +/- "<<fitted_BdDPi_1_u<<")"<<std::endl;
	std::cout<<"UP: ("<<fitted_BdDPi_2<<" +/- "<<fitted_BdDPi_2_u<<")"<<std::endl;

	if ( mode == "BsDsPi" || mode == "BsDsK")
	  {
	    Float_t temp, temp_u;
            temp = fitted_BdDPi_1*rNBd;
            temp_u = temp*std::sqrt(std::pow(fitted_BdDPi_1_u/fitted_BdDPi_1,2) + std::pow(rNBd_u/rNBd,2)); //uncertainty
            fitted_BdDPi_1 = temp;
            fitted_BdDPi_1_u = temp_u;
            temp = fitted_BdDPi_2*rNBd;
            temp_u = temp*std::sqrt(std::pow(fitted_BdDPi_2_u/fitted_BdDPi_2,2)  + std::pow(rNBd_u/rNBd,2)); //uncertainty
            fitted_BdDPi_2 = temp;
            fitted_BdDPi_2_u = temp_u;
	    std::cout<<"===> Fitted yield to real data Bd->DPi, D->KPiPi scaled by N("<<nameHypo<<")/N(Bd->DPi)"<<std::endl;
	    std::cout<<"N("<<nameHypo<<")/N(Bd->DPi)= B("<<nameHypo<<")/B(Bd->DPi)*B("<<nameDHypo<<")/N(D->KPiPi)*fragfrac"<<std::endl;
	    std::cout<<"("<<rNBd<<" +/- "<<rNBd_u<<")"<<std::endl;
	    std::cout<<"DOWN: ("<<fitted_BdDPi_1<<" +/- "<<fitted_BdDPi_1_u<<")"<<std::endl;
	    std::cout<<"UP: ("<<fitted_BdDPi_2<<" +/- "<<fitted_BdDPi_2_u<<")"<<std::endl;
	  }

	std::cout<<"===> Number of expected events = fitted yield multiplied by expected misID"<<std::endl;
        Float_t N_ev_1, N_ev_1_u, N_ev_2, N_ev_2_u;
	if (mode == "BDK")
	  {
	    N_ev_1 = fitted_BdDPi_1*misID_lab1_av*rN;
            N_ev_1_u = N_ev_1*std::sqrt(std::pow(misID_lab1_u/misID_lab1_av,2) + std::pow(fitted_BdDPi_1_u/fitted_BdDPi_1,2) + std::pow(rN_u/rN,2));
            N_ev_2 = fitted_BdDPi_2*misID_lab1_av*rN;
            N_ev_2_u = N_ev_2*std::sqrt(std::pow(misID_lab1_u/misID_lab1_av,2) + std::pow(fitted_BdDPi_2_u/fitted_BdDPi_2,2) +  std::pow(rN_u/rN,2));
	  }
	else
	  {
	    N_ev_1 = fitted_BdDPi_1*misID_lab1_av;
	    N_ev_1_u = N_ev_1*std::sqrt(std::pow(misID_lab1_u/misID_lab1_av,2) + std::pow(fitted_BdDPi_1_u/fitted_BdDPi_1,2));
	    N_ev_2 = fitted_BdDPi_2*misID_lab1_av;
	    N_ev_2_u = N_ev_2*std::sqrt(std::pow(misID_lab1_u/misID_lab1_av,2) + std::pow(fitted_BdDPi_2_u/fitted_BdDPi_2,2));
	  }
	std::cout<<"----------------------------------------------------"<<std::endl;
        std::cout<<"DOWN: ("<<N_ev_1<<" +/- "<<N_ev_1_u<<")"<<std::endl;
        std::cout<<"UP: ("<<N_ev_2<<" +/- "<<N_ev_2_u<<")"<<std::endl;
        std::cout<<"----------------------------------------------------"<<std::endl;
      }
      
  }

 

  RooWorkspace* ObtainBDPi(TString& filesDir, TString& sig, 
			   int PIDcut,
			   double Pcut_down, double Pcut_up,
			   double BDTG_down, double BDTG_up,
			   double Bmass_down, double Bmass_up,
			   double Dmass_down, double Dmass_up,
			   TString &mVar, TString& mProbVar,
			   TString& mode, Bool_t MC, TString& hypo )

  {
    std::cout<<"[INFO] ==> GeneralUtils::ExpectedYield(...). Calculate expected yield misID backgrouds"<<std::endl;
    std::cout<<"name of config file: "<<filesDir<<std::endl;
    std::cout<<"PIDK cut: "<< PIDcut<<std::endl;
    //std::cout<<"BDTGResponse cut: "<<BDTGCut<<std::endl;
    std::cout<<"BDTG range: ("<<BDTG_down<<","<<BDTG_up<<")"<<std::endl;
    std::cout<<"Bachelor momentum range: ("<<Pcut_down<<","<<Pcut_up<<")"<<std::endl;
    std::cout<<"D(s) mass range: ("<<Dmass_down<<","<<Dmass_up<<")"<<std::endl;
    std::cout<<"Name of observable: "<<mVar<<std::endl;
    std::cout<<"Name of PID variable: "<<mProbVar<<std::endl;
    std::cout<<"Data mode: "<<mode<<std::endl;

    RooWorkspace* work = NULL;
    work =  new RooWorkspace("workspace","workspace");
    PlotSettings* plotSet = NULL;
    plotSet = new PlotSettings("plotSet","plotSet");

    //Double_t number=0;

    std::cout<<"=====> Preparing signal from MC"<<std::endl;

    double BMassRange[2];
    /*if ( MC == false )
      {
	BMassRange[0] = 5200; BMassRange[1]=5400;
      }
    else
      {
	BMassRange[0] = 5100; BMassRange[1]=5800;
	}*/
    BMassRange[0] = Bmass_down; 
    BMassRange[1] = Bmass_up;
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
    TCut MCD = Form("lab2_MM > %f && lab2_MM < %f",Dmass_down,Dmass_up);
    TCut MCB = Form("%s > %f && %s < %f",mVar.Data(),BMassRange[0],mVar.Data(),BMassRange[1]);

    TCut BDTG_cut = Form("BDTGResponse_1 > %f && BDTGResponse_1 < %f",BDTG_down, BDTG_up);
    TCut PID_cut="";
    //    TCut PID_child_cut = "lab5_PIDK>0 && lab4_PIDp < 5 && lab3_PIDp <5";
    TCut PID_child_cut = "(!(abs(lab2_MassHypo_Lambda_pi1-2285.) < 30. && lab4_PIDp > 0 )) && (!(abs(lab2_MassHypo_Lambda_pi2-2285.) < 30. && lab3_PIDp > 0 ))";
    //TCut Veto = "abs(sqrt(pow(sqrt(pow(139.57,2)+pow(lab3_P,2))+sqrt(pow(139.57,2)+pow(lab1_P,2)),2)-pow(lab3_PX+lab1_PX,2)-pow(lab3_PY+lab1_PY,2)-pow(lab3_PZ+lab1_PZ,2))-1300) > 200"; 

    if (hypo == "DsK")      {
	PID_cut = Form("%s > %d",mProbVar.Data(),PIDcut);
      }
    else if (hypo == "DsPi")
      {
	PID_cut = Form("%s < %d",mProbVar.Data(),PIDcut);
      }
    TCut FDCHI2 = "lab2_FDCHI2_ORIVX > 9"; 
    TCut TAU_cut = "lab2_TAU > 0";
    TCut Hypo;
    TCut Veto1 = "lab1_PIDmu < 2";
    TCut Veto2 = "(lab2_MassHypo_Ds_pi2 < 1950 || lab2_MassHypo_Ds_pi2 > 2030 || lab3_PIDK < 0)";
    TCut Veto3 = "(lab2_MassHypo_Ds_pi1 < 1950 || lab2_MassHypo_Ds_pi1 > 2030 || lab4_PIDK < 0)";
    TCut Veto4 = "!(lab35_MM < 840 || lab45_MM < 840)";
    TCut Veto5 = "!((abs(sqrt(pow(sqrt(pow(493.67,2)+pow(lab1_P,2))+sqrt(pow(lab3_M,2)+pow(lab3_P,2)),2)-pow(lab1_PX+lab3_PX,2)-pow(lab1_PY+lab3_PY,2)-pow(lab1_PZ+lab3_PZ,2))-1870)<20))";
    TCut Veto6 = "!((abs(sqrt(pow(sqrt(pow(493.67,2)+pow(lab1_P,2))+sqrt(pow(lab4_M,2)+pow(lab4_P,2)),2)-pow(lab1_PX+lab4_PX,2)-pow(lab1_PY+lab4_PY,2)-pow(lab1_PZ+lab4_PZ,2))-1870)<20))";
    TCut Veto7 = "!(fabs(lab2_MassHypo_Lambda_pi1-2285.) < 30. && lab4_PIDp > 0)";
    TCut Veto8 = "!(fabs(lab2_MassHypo_Lambda_pi2-2285.) < 30. && lab3_PIDp > 0)";
    TCut Veto9 = "!(lab2_MM-lab45_MM < 200)";
    TCut Veto10= "!(lab2_MM-lab35_MM < 200)";
    TCut AddCut = "(lab2_FD_ORIVX > 0)";
    TCut Veto = Veto1&&Veto2&&Veto3&&Veto4&&Veto5&&Veto6&&Veto7&&Veto8&&AddCut;

    TCut All;
    if (MC == false ) 
      {
	All = P_cut&&BDTG_cut&&PID_cut&&FDCHI2&&MCB&&MCD&&Veto; //PID_child_cut&&MCD&&MCB&&Veto; //&&TAU_cut;
      }
    else
      {
	TCut MCTriggerCut="lab0Hlt1TrackAllL0Decision_TOS && (lab0Hlt2Topo2BodyBBDTDecision_TOS || lab0Hlt2Topo3BodyBBDTDecision_TOS || lab0Hlt2Topo4BodyBBDTDecision_TOS)";
	TCut MCBsIDCut;

	TCut MCCut, MCCut1;
	
	if (mode.Contains("Bs") || (mode.Contains("Ds") && !mode.Contains("Dst"))) {
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
    std::cout<<"[INFO] ------CUT------"<<std::endl;
    std::cout<<All<<std::endl;
    std::cout<<"----------------------"<<std::endl;


    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);
    RooRealVar* lab2_MM = new RooRealVar("lab2_MM","lab2_MM",Dmass_down, Dmass_up);
    RooRealVar* lab1_P = new RooRealVar("lab1_P","lab1_P",Pcut_down,Pcut_up);
    RooRealVar* lab0_P = new RooRealVar("lab0_P","lab0_P",Pcut_down,Pcut_up);
    RooRealVar* lab1_PT = new RooRealVar("lab1_PT","lab1_PT",0,50000);
    RooRealVar* nTracks = new RooRealVar("nTracks","nTracks",0,1000);
    RooRealVar* lab0_TAU = new RooRealVar("lab0_LifetimeFit_ctau","lab0_LifetimeFit_ctau",0,15);
    RooRealVar* lab0_TAUERR = new RooRealVar("lab0_LifetimeFit_ctauErr","lab0_LifetimeFit_ctauErr",0.01,0.1);
    RooRealVar* lab0_TAGOMEGA_OS = new RooRealVar("lab0_TAGOMEGA_OS","lab0_TAGOMEGA_OS",0,0.6);
    RooRealVar* lab0_TAGOMEGA_SS = new RooRealVar("lab0_SS_nnetKaon_PROB","lab0_SS_nnetKaon_PROB",0,0.5);
    RooCategory* lab1_ID = new RooCategory("lab1_ID", "bachelor charge");
    lab1_ID->defineType("h+",  1);
    lab1_ID->defineType("h-", -1);
    RooCategory* lab0_TAG_OS = new RooCategory("lab0_TAGDECISION_OS", "flavour tagging result");
    lab0_TAG_OS->defineType("B_OS",     1);
    lab0_TAG_OS->defineType("Bbar_OS", -1);
    lab0_TAG_OS->defineType("Untagged_OS",0);
    RooCategory* lab0_TAG_SS = new RooCategory("lab0_SS_nnetKaon_DEC", "flavour tagging result");
    lab0_TAG_SS->defineType("B_SS",     1);
    lab0_TAG_SS->defineType("Bbar_SS", -1);
    lab0_TAG_SS->defineType("Untagged_SS",0);

    RooArgSet* obs = new RooArgSet(*lab0_MM,*lab2_MM,*lab1_P,*lab0_P,*lab1_PT,*nTracks);
    obs->add(*lab0_TAG_OS);
    obs->add(*lab0_TAG_SS);
    obs->add(*lab0_TAGOMEGA_OS);
    obs->add(*lab0_TAGOMEGA_SS);
    obs->add(*lab0_TAU);
    obs->add(*lab0_TAUERR);
    obs->add(*lab1_ID); 

    //RooRealVar* lab0_MMdsk = new RooRealVar(mVar.Data(),mVar.Data(),BMassRange[0], BMassRange[1]);

    TString smp[2];
    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], true);
    }
    
    TTree* tr[2];
    RooDataSet* dataSetMC[2];

    Float_t c = 299792458.;
    Float_t corr = 1e9/c;
     
    //RooDataSet* dataSetMCDsK[2];
    //RooFitResult* result[2];
    Int_t n_ev[2];
    Int_t n_wm[2];
    //Int_t n_evdsk[2];
    for(int i=0; i<2; i++)
      {
        tr[i] = NULL;
	tr[i] = TreeCut(tree[i],All,smp[i],mode, true);
        Float_t lab0_MM2;
	Double_t  lab0_P2, lab1_P2, lab1_PT2, lab2_MM2;
	Int_t nTracks2, ID;
	Int_t tag_OS, tag_SS;
	Double_t mistag_OS, mistag_SS; 
	Float_t time[10];
	Float_t terr[10];

	tr[i]->SetBranchAddress(mVar.Data(), &lab0_MM2);
	tr[i]->SetBranchAddress("lab2_MM", &lab2_MM2);
	tr[i]->SetBranchAddress("lab1_P",  &lab1_P2);
	tr[i]->SetBranchAddress("lab0_P",  &lab0_P2);
	tr[i]->SetBranchAddress("lab1_PT", &lab1_PT2);
	tr[i]->SetBranchAddress("nTracks", &nTracks2);
	tr[i]->SetBranchAddress("lab0_TAGDECISION_OS", &tag_OS);
	tr[i]->SetBranchAddress("lab0_SS_nnetKaon_DEC", &tag_SS);
	tr[i]->SetBranchAddress("lab0_TAGOMEGA_OS", &mistag_OS);
        tr[i]->SetBranchAddress("lab0_SS_nnetKaon_PROB", &mistag_SS);
	tr[i]->SetBranchAddress("lab0_LifetimeFit_ctau", &time);
        tr[i]->SetBranchAddress("lab0_LifetimeFit_ctauErr", &terr);
	tr[i]->SetBranchAddress("lab1_ID", &ID);

	TString s = mode+"_"+smp[i];
	n_wm[i] = tr[i]->GetEntries();

	TString name="dataSetMC"+s;
	dataSetMC[i] = NULL;
	dataSetMC[i] = new RooDataSet(name.Data(),name.Data(),*obs);
	

	
	for (Long64_t jentry=0; jentry<tr[i]->GetEntries(); jentry++)
	  {
	    tr[i]->GetEntry(jentry);
	    if ( MC == true) {lab0_MM2 = lab0_MM2-3.9;}
	    if (lab0_MM2 > BMassRange[0] && lab0_MM2 < BMassRange[1])
	      {
		lab0_MM->setVal(lab0_MM2);
		lab2_MM->setVal(lab2_MM2);
		lab1_P->setVal(lab1_P2);
		lab0_P->setVal(lab0_P2); 
		lab1_PT->setVal(lab1_PT2);
		nTracks->setVal(nTracks2);
		if( tag_OS > 0.1 ) {   tag_OS = 1; }
		else if ( tag_OS < -0.1 ) { tag_OS = -1;}
		else{ tag_OS = 0; }
		if( tag_SS > 0.1 ) {   tag_SS = 1; }
                else if ( tag_SS < -0.1 ) { tag_SS = -1;}
                else{ tag_SS = 0; }

		if ( ID > 0) { lab1_ID->setIndex(1); } else {lab1_ID->setIndex(-1); }

		lab0_TAG_OS->setIndex(tag_OS);
		lab0_TAG_SS->setIndex(tag_SS);
		
		lab0_TAGOMEGA_OS->setVal(mistag_OS);
		lab0_TAGOMEGA_SS->setVal(mistag_SS);
		
		lab0_TAU->setVal(time[0]*corr);
		lab0_TAUERR->setVal(terr[0]*corr);

		dataSetMC[i]->add(*obs);
	      }
	  }
	if( plotSet -> GetStatus()  == true )
	  {
	    SaveDataSet(dataSetMC[i],lab0_MM, smp[i], mode, plotSet, true);
	  }
	std::cout<<"Number of entries: "<<dataSetMC[i]->numEntries()<<std::endl;
	n_ev[i]=dataSetMC[i]->numEntries();
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

  RooWorkspace* ObtainLbLcPi( TString& filesDir, TString& sig,
			      int PIDcut,
			      double Pcut_down, double Pcut_up,
                              double PT_down, double PT_up,
                              double nTr_down, double nTr_up,
			      TString& mVar,
                              TString& mDVar,
                              TString& mode,
			      RooWorkspace* workspace,
                              bool debug
                              )
  {
    if ( debug == true)
      {
	std::cout << "[INFO] ==> GeneralUtils::ObtainLbLcPi(...)."
                  << " Obtain dataSets for LbLcPi"
                  << std::endl;
	std::cout << "name of config file: " << filesDir << std::endl;
	std::cout << "Name of observable: " << mVar << std::endl;
	std::cout << "Data mode: " << mode << std::endl;
      }

    RooWorkspace* work = NULL;
    if (workspace == NULL){ work =  new RooWorkspace("workspace","workspace");}
    else {work = workspace; }
    PlotSettings* plotSet = NULL;
    plotSet = new PlotSettings("plotSet","plotSet");

    Double_t Dmass_down = 2200;
    Double_t Dmass_up = 2380;
    Double_t Bmass_down = 5400;
    Double_t Bmass_up = 5800;
    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),Bmass_down, Bmass_up);
    RooRealVar* lab2_MM = new RooRealVar(mDVar.Data(),mDVar.Data(),Dmass_down, Dmass_up);
    RooRealVar* lab1_PIDK = new RooRealVar("lab1_PIDK", "lab1_PIDK", log(PIDcut), log(150));
    RooRealVar* lab1_P  = new RooRealVar("lab1_P","lab1_P",Pcut_down,Pcut_up);
    RooRealVar* lab1_PT  = new RooRealVar("lab1_PT","lab1_PT",PT_down,PT_up);
    RooRealVar* nTracks  = new RooRealVar("nTracks","nTracks",nTr_down,nTr_up);

    RooArgSet* obs = new RooArgSet(*lab0_MM,*lab2_MM,
                                   *lab1_P, *lab1_PT, *nTracks,
				   *lab1_PIDK);


    TCut BDTG = "(BDTGResponse_1 > 0.0)";  
    TCut PIDchildCut = "(lab3_PIDK < 5 && lab4_PIDK > 0)";
    TCut Veto1 = "(abs(sqrt(pow(sqrt(pow(lab3_M,2)+pow(lab3_P,2))+sqrt(pow(lab4_M,2)+pow(lab4_P,2))+sqrt(pow(139.57,2)+pow(lab5_P,2)),2)-pow(lab3_PX+lab4_PX+lab5_PX,2)-pow(lab3_PY+lab4_PY+lab5_PY,2)-pow(lab3_PZ+lab4_PZ+lab5_PZ,2))-1870)>30)";
    TCut Veto2 = "(abs(sqrt(pow(sqrt(pow(lab3_M,2)+pow(lab3_P,2))+sqrt(pow(lab4_M,2)+pow(lab4_P,2))+sqrt(pow(139.57,2)+pow(lab5_P,2)),2)-pow(lab3_PX+lab4_PX+lab5_PX,2)-pow(lab3_PY+lab4_PY+lab5_PY,2)-pow(lab3_PZ+lab4_PZ+lab5_PZ,2))-2010)>30)";
    TCut Veto3 = "(abs(sqrt(pow(sqrt(pow(lab3_M,2)+pow(lab3_P,2))+sqrt(pow(lab4_M,2)+pow(lab4_P,2))+sqrt(pow(493.67,2)+pow(lab5_P,2)),2)-pow(lab3_PX+lab4_PX+lab5_PX,2)-pow(lab3_PY+lab4_PY+lab5_PY,2)-pow(lab3_PZ+lab4_PZ+lab5_PZ,2))-1870)>30)";
    TCut Veto4 = "(abs(sqrt(pow(sqrt(pow(lab3_M,2)+pow(lab3_P,2))+sqrt(pow(lab4_M,2)+pow(lab4_P,2))+sqrt(pow(493.67,2)+pow(lab5_P,2)),2)-pow(lab3_PX+lab4_PX+lab5_PX,2)-pow(lab3_PY+lab4_PY+lab5_PY,2)-pow(lab3_PZ+lab4_PZ+lab5_PZ,2))-1970)>30)";
    TCut MB = "(abs(lab0_MassFitConsD_M - 5620)<50)";
    TCut MCD = Form("lab2_MM > %f && lab2_MM < %f",Dmass_down,Dmass_up);
    
    TCut PID_cut = Form("lab5_PIDK > %d",PIDcut);
    TCut CutAll = BDTG&&Veto1&&Veto2&&Veto3&&Veto4&&MB&&PIDchildCut&&PID_cut&&MCD;

    std::vector <std::string> FileName;
    ReadOneName(filesDir,FileName,sig,debug);

    TTree* tree[2];

    for( int i=0; i<2; i++)
      {
        tree[i] = NULL;
        tree[i] = ReadTreeData(FileName,i, debug);
      }

    TString smp[2];
    for (int i=1; i<3; i++){
      smp[i-1] = CheckPolarity(FileName[i], debug);
    }
    
    TTree* treetmp = NULL;
    RooDataSet* dataSet[2];
    
    
    for(int i = 0; i<2; i++)
      {
	treetmp = TreeCut(tree[i], CutAll, smp[i], mode, debug);  //obtain new tree with applied all cuts//
	Int_t nentriesMC = treetmp->GetEntries();

	Float_t lab0_MM3;
	Double_t lab2_MM3, lab1_P3, lab1_PT3, lab1_PIDK3;
	Int_t nTr3;

	treetmp->SetBranchAddress(mVar.Data(), &lab0_MM3);
	treetmp->SetBranchAddress(mDVar.Data(), &lab2_MM3);
	treetmp->SetBranchAddress("nTracks", &nTr3);
	treetmp->SetBranchAddress("lab5_P", &lab1_P3);
	treetmp->SetBranchAddress("lab5_PT", &lab1_PT3);
	treetmp->SetBranchAddress("lab5_PIDK", &lab1_PIDK3);
	
	TString name="dataSetLb2LcPi_"+smp[i];
	dataSet[i] = NULL;

	dataSet[i] = new RooDataSet(name.Data(),name.Data(), *obs);
	
	for (Long64_t jentry=0; jentry<nentriesMC; jentry++) {
	  treetmp->GetEntry(jentry);
	  lab0_MM->setVal(lab0_MM3);
	  lab2_MM->setVal(lab2_MM3);
	  lab1_P->setVal(lab1_P3);
	  lab1_PT->setVal(lab1_PT3);
	  nTracks->setVal(nTr3);
	  lab1_PIDK->setVal(log(lab1_PIDK3));

	  dataSet[i]->add(*obs);
	
	}

	if ( debug == true) std::cout<<"Number of entries: "<<dataSet[i]->numEntries()<<std::endl;
	if(plotSet->GetStatus() == true )
	  {
	    SaveDataSet(dataSet[i],lab1_PT, smp[i], mode, plotSet, debug);
	  }
	work->import(*dataSet[i]);
      }
    return work;
  }

} //end of namespace
