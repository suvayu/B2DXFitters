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
#include "B2DXFitters/SFitUtils.h"
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

namespace SFitUtils {

  
  //===========================================================================
  // Read observables tVar, tagVar, tagOmegaVar, idVar from sWeights file
  // Name of file is read from filesDir and signature sig 
  // time_{up,down} - range for tVar
  // part means mode (DsPi, DsK and so on)
  //===========================================================================

  RooWorkspace* ReadDataFromSWeights(TString& part, 
				     TString& pathFile,
				     TString& treeName,
				     double time_down, double time_up,
				     TString& tVar,
				     TString& terrVar,
				     TString& tagName,
				     TString& tagOmegaVar,
				     TString& idVar,
				     bool weighted,
				     bool debug,
                     bool applykfactor
				     )
  {
    if ( debug == true) 
      {
	std::cout<<"[INFO] ==> GeneralUtils::ReadDataFromSWeights(...). Read data set from sWeights NTuple "<<std::endl;
	std::cout<<"path of file: "<<pathFile<<std::endl;
	std::cout<<"name of tree: "<<treeName<<std::endl;
	std::cout<<"B(s) time range: ("<<time_down<<","<<time_up<<")"<<std::endl;
	std::cout<<"B(s) time  error range: (0.01,0.1)"<<std::endl;
	std::cout<<"B(s) mistag range: (0.0,0.5)"<<std::endl;
	std::cout<<"Name of time observable: "<<tVar<<std::endl;
	std::cout<<"Name of time error observable: "<<terrVar<<std::endl;
	std::cout<<"Name of tag observable: "<<tagName<<std::endl;
	std::cout<<"Name of mistag observable: "<<tagOmegaVar<<std::endl;
	std::cout<<"Name of id observable: "<<idVar<<std::endl;
	std::cout<<"Mode: "<<part<<std::endl;
      }

    RooWorkspace* work = NULL;
    work =  new RooWorkspace("workspace","workspace");
    TTree* treeSW = ReadTreeMC(pathFile.Data(),treeName.Data(), debug);
     
    RooRealVar* lab0_TAU = new RooRealVar(tVar.Data(),tVar.Data(),1.,time_down,time_up);
    RooRealVar* lab0_TAUERR = new RooRealVar(terrVar.Data(),terrVar.Data(), 0.01, 0.0075, 0.2);
    RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,0.,0.5);
    
    RooCategory* qt = new RooCategory("qt", "flavour tagging result");
    qt->defineType("B"       ,  1);
    qt->defineType("Bbar"    , -1);
    qt->defineType("Untagged",  0);

    RooCategory* qf = new RooCategory("qf", "bachelor charge");
    qf->defineType("h+",  1);
    qf->defineType("h-", -1);

    
    //RooRealVar* lab1_ID = new RooRealVar(idVar.Data(),idVar.Data(),1.,-1.,1.);           
    //RooRealVar* nTracks = new RooRealVar("nTracks","nTracks",0,1000);
    //RooRealVar* lab1_P = new RooRealVar("lab1_P","lab1_P",0,650000);
    //RooRealVar* lab1_PIDK = new RooRealVar("lab1_PIDK","lab1_PIDK",log(5), log(150)); //-150,150);
    //RooRealVar* lab1_PIDp = new RooRealVar("lab1_PIDp","lab1_PIDp",-150,150);
    //RooRealVar* lab1_PT = new RooRealVar("lab1_PT","lab1_PT",0,45000);


    std::vector <TString> s;
    if( pathFile.Contains("3modeskkpi") == true )
      {
	if(debug == true) { std::cout<<"[INFO] 3 Ds final states: NonRes, PhiPi, Kstk"<<std::endl; }
	s.push_back("both_nonres");
        s.push_back("both_phipi");
        s.push_back("both_kstk");
      }
    else if(pathFile.Contains("toys1m") == true || pathFile.Contains("Toys1M") == true || pathFile.Contains("TOYS1M") == true)  
      {
	if (debug == true ) { std::cout<<"[INFO]  1D Toys: read only PhiPi"<<std::endl;}
	s.push_back("both_phipi");
      }
    else
      {
	if( debug == true ) { std::cout<<"[INFO] 5 Ds final states: NonRes, PhiPi, KstK, KPiPi, PiPiPi"<<std::endl; }
	s.push_back("both_nonres");
        s.push_back("both_phipi");
        s.push_back("both_kstk");
	s.push_back("both_kpipi");
        s.push_back("both_pipipi");
      }
	
    Int_t bound = s.size();
    if ( debug == true ) { std::cout<<"[INFO] sWeights bound: "<<bound<<std::endl;}
    TString cat;
    if (part == "DsPi" ) {
      cat = "dataSet_time_Bs2DsPi";
    } else {
      cat = "dataSet_time_Bs2DsK";
    }

    /*
    std::vector <TString> catcont2;
    catcont2.push_back("Mixed");
    catcont2.push_back("Unmixed");
    catcont2.push_back("Untagged");
    */

    RooDataSet*  dataSet;
    RooRealVar*  weights;

    RooArgSet* obs = new RooArgSet(*lab0_TAU,
				   *lab0_TAUERR,
				   *lab0_TAGOMEGA,
				   *qf,
				   *qt);
 
    TString setOfObsName = "SetOfObservables";
    obs->setName(setOfObsName.Data());
    
    TString namew = "sWeights";
    weights = new RooRealVar(namew.Data(), namew.Data(), -1.0, 2.0 );  // create weights //
    obs->add(*weights);

    //obs->add(*lab1_P);
    //obs->add(*lab1_PT);
    //obs->add(*lab1_PIDp);
    //obs->add(*lab1_PIDK);
    //obs->add(*nTracks);
    //obs->add(*lab0_MM);

    if (weighted == true)
      {
	dataSet = new RooDataSet(   cat.Data(), cat.Data(), *obs, namew.Data());  // create data set //
      }
    else
      {
	dataSet = new RooDataSet(   cat.Data(), cat.Data(), *obs); 
      }
        
    Double_t tau;
    Double_t tauerr;
    Double_t tag, ID;
    Double_t tagweight;
    Double_t sw[bound];
    Double_t trueid; 
    Double_t mass;
    //Double_t p, pt;
    //Double_t nTr;
    //Double_t PIDK, PIDp;
    
    treeSW->SetBranchAddress(tVar.Data(), &tau);
    treeSW->SetBranchAddress(terrVar.Data(), &tauerr);
    treeSW->SetBranchAddress(tagOmegaVar.Data(), &tagweight);

    if(pathFile.Contains("toys") == true || pathFile.Contains("Toys") == true || pathFile.Contains("TOYS") == true)
      {
	TString name = tagName+"_idx";
	treeSW->SetBranchAddress(name.Data(), &tag);
        treeSW->SetBranchAddress("lab1_ID_idx", &ID);
        treeSW->SetBranchAddress("lab0_TRUEID", &trueid);
      }
    else
      {
	treeSW->SetBranchAddress(tagName.Data(), &tag);
	treeSW->SetBranchAddress("lab1_ID", &ID);
      }    
    
    treeSW->SetBranchAddress("lab0_MassFitConsD_M", &mass);
    //treeSW->SetBranchAddress("lab1_P", &p);
    //treeSW->SetBranchAddress("nTracks",&nTr);
    //treeSW->SetBranchAddress("lab1_PIDK",&PIDK);
    //treeSW->SetBranchAddress("lab1_PIDp",&PIDp);
    //treeSW->SetBranchAddress("lab1_PT", &pt);
    
    for (int i = 0; i<bound; i++)
      {
	TString swname = "nSig_"+s[i]+"_Evts_sw";
        treeSW->SetBranchAddress(swname.Data(), &sw[i]);
	if (debug == true ) { std::cout<<"[INFO] sWeights names: "<<swname<<std::endl; }
      }

    Float_t c = 299792458.;
    Double_t sqSumsW = 0;
    double correction=0.0;
 
    for (Long64_t jentry=0; jentry<treeSW->GetEntries(); jentry++) {
      treeSW->GetEntry(jentry);
      double m = 0; 
      double merr = 0;
      //if (jentry>10000) continue;  
      if(pathFile.Contains("toys") == true || pathFile.Contains("Toys") == true || pathFile.Contains("TOYS") == true)
	{
	  m =tau;
	  merr = tauerr;
      if ((trueid > 1.5) && (trueid < 9.5)) {
        //Apply k-factor smearing
        if (fabs(trueid-2) < 0.5 || fabs(trueid-8) < 0.5) {
            //correctionmean  = 1+2*(mass-5279.)/5279.;
            correction      = mass/5279.;//gR->Gaus(correctionmean,0.0001);  
        } else if (fabs(trueid-4) < 0.5 || fabs(trueid-7) < 0.5 || fabs(trueid-8) < 0.5) {
            correction      = mass/5369.;
        } else if (fabs(trueid-5) < 0.5 || fabs(trueid-6) < 0.5) {
            correction      = mass/5620.;
        }   
        //cout << "Applying k-factor correction " << trueid << " " << mass << " " << tau << " " << correction << endl;
      } else correction = 1.; 
      if (!applykfactor) correction = 1.;
      std::cout << "The correction factor is " << correction << std::endl;
      m *=correction;
	}
      else
	{
	  m =tau*1e9/c;   
	  merr = tauerr*1e9/c;
	}
      if (m < 0.2) continue;  
      lab0_TAU->setVal(m);
      lab0_TAUERR->setVal(merr);

      if (tagweight > 0.5) tagweight = 0.5;
      lab0_TAGOMEGA->setVal(tagweight);
      
      //lab1_P->setVal(p);
      //lab1_PT->setVal(pt);
      //nTracks->setVal(nTr);
      //lab1_PIDK->setVal(PIDK);
      //lab1_PIDp->setVal(PIDp);  
      //lab0_MM->setVal(mass);

      if (ID > 0) { qf->setIndex(1); } else { qf->setIndex(-1); }

      if( tag > 0.1 ) {   qt->setIndex(1); }
      else if ( tag < -0.1 ) { qt->setIndex(-1);}
      else{ qt->setIndex(0);}

      Double_t sum_sw=0;
      for (int i = 0; i<bound; i++) {
	      sum_sw += sw[i];
	  }
      //sum_sw = 1.0;
      weights->setVal(sum_sw);
      sqSumsW += sum_sw*sum_sw;
      if (weighted == true )
	{
	  dataSet->add(*obs,sum_sw,0);
	}
      else
	{
	  dataSet->add(*obs);
	}
      //std::cout << "this event has time = " << m << " and error = " << merr << " with weight = " << sum_sw << std::endl;  
      
    }
      
    if ( debug == true){
	if ( dataSet != NULL ){
	    std::cout<<"[INFO] ==> Create "<<dataSet->GetName()<<std::endl;
	    std::cout<<"Sample "<<cat<<" number of entries: "<<treeSW->GetEntries()<<" in data set: "<<dataSet->numEntries()<<std::endl;
	    std::cout<<"sum of sWeights: "<<dataSet->sumEntries()<<" squared sum of sWeights: "<<sqSumsW<<std::endl; 
	} else { std::cout<<"Error in create dataset"<<std::endl; }
    }
            
    work->import(*dataSet);
    return work;

  }

  //===========================================================================
  // Read observables tVar, tagVar, tagOmegaVar, idVar from sWeights file
  // Name of file is read from filesDir and signature sig
  // time_{up,down} - range for tVar
  // part means mode (DsPi, DsK and so on)
  //===========================================================================

  RooWorkspace* ReadDataFromSWeights2(TString& part,
				      TString& pathFile,
				      TString& treeName,
				      double time_down, double time_up,
				      TString& tVar,
				      TString& terrVar,
				      TString& tagName,
				      TString& tagOmegaVar,
				      TString& idVar,
				      bool weighted,
				      bool debug
				      )
  {
    if ( debug == true)
      {
	std::cout<<"[INFO] ==> GeneralUtils::ReadDataFromSWeights(...). Read data set from sWeights NTuple "<<std::endl;
	std::cout<<"path of file: "<<pathFile<<std::endl;
	std::cout<<"name of tree: "<<treeName<<std::endl;
	std::cout<<"B(s) time range: ("<<time_down<<","<<time_up<<")"<<std::endl;
	std::cout<<"B(s) time  error range: (0.01,0.1)"<<std::endl;
	std::cout<<"B(s) mistag range: (0.0,0.5)"<<std::endl;
	std::cout<<"Name of time observable: "<<tVar<<std::endl;
	std::cout<<"Name of time error observable: "<<terrVar<<std::endl;
	std::cout<<"Name of tag observable: "<<tagName<<std::endl;
	std::cout<<"Name of mistag observable: "<<tagOmegaVar<<std::endl;
	std::cout<<"Name of id observable: "<<idVar<<std::endl;
	std::cout<<"Mode: "<<part<<std::endl;
      }

    RooWorkspace* work = NULL;
    work =  new RooWorkspace("workspace","workspace");
    TTree* treeSW = ReadTreeMC(pathFile.Data(),treeName.Data(), debug);

    RooRealVar* lab0_TAU = new RooRealVar(tVar.Data(),tVar.Data(),1.,time_down,time_up);
    RooRealVar* lab0_TAUERR = new RooRealVar(terrVar.Data(),terrVar.Data(), 0.01, 0.01, 0.1);
    RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,0.,0.5);


    RooCategory* qt = new RooCategory("qt", "flavour tagging result");
    qt->defineType("B"       ,  1);
    qt->defineType("Bbar"    , -1);
    qt->defineType("Untagged",  0);

    RooCategory* qf = new RooCategory("qf", "bachelor charge");
    qf->defineType("h+",  1);
    qf->defineType("h-", -1);
    
    std::vector <TString> s;
    if( pathFile.Contains("3modeskkpi") == true )
      {
        s.push_back("both_nonres");
        s.push_back("both_phipi");
        s.push_back("both_kstk");
      }
    else if(pathFile.Contains("toys1m") == true || pathFile.Contains("Toys1M") == true || pathFile.Contains("TOYS1M") == true)
      {
        s.push_back("both_phipi");
      }
    else
      {
        s.push_back("both_nonres");
        s.push_back("both_phipi");
        s.push_back("both_kstk");
        s.push_back("both_kpipi");
        s.push_back("both_pipipi");
      }

    Int_t bound = s.size();

    std::vector <TString> catcont;
    catcont.push_back("B_h+");
    catcont.push_back("B_h-");
    catcont.push_back("Bbar_h+");
    catcont.push_back("Bbar_h-");
    catcont.push_back("Untagged_h+");
    catcont.push_back("Untagged_h-");
  
    TString cat;
    if (part == "DsPi" ) {
      cat = "dataSet_time_Bs2DsPi";
    } else {
      cat = "dataSet_time_Bs2DsK";
    }
    
    RooRealVar*  weights;
    RooArgSet* obs = new RooArgSet(*lab0_TAU,
                                   *lab0_TAUERR,
                                   *lab0_TAGOMEGA,
                                   *qf,
                                   *qt);

    TString setOfObsName = "SetOfObservables";
    obs->setName(setOfObsName.Data());

    TString namew = "sWeights";
    weights = new RooRealVar(namew.Data(), namew.Data(), -1.0, 2.0 );  // create weights //
    obs->add(*weights);
   
    RooDataSet* dataSetContr[6];
    for ( int i = 0; i < bound; i++)
      {
	TString namecontr = cat+TString("_")+catcont[i];
	dataSetContr[i] = new RooDataSet(  namecontr.Data(), namecontr.Data(), *obs);  // create data set //
      }
        
    Double_t tau;
    Double_t tauerr;
    Double_t tag, ID;
    Double_t tagweight;
    Double_t sw[bound];

    treeSW->SetBranchAddress(tVar.Data(), &tau);
    treeSW->SetBranchAddress(terrVar.Data(), &tauerr);
    treeSW->SetBranchAddress(tagOmegaVar.Data(), &tagweight);

    if(pathFile.Contains("toys") == true || pathFile.Contains("Toys") == true || pathFile.Contains("TOYS") == true)
      {
        TString name = tagName+"_idx";
        treeSW->SetBranchAddress(name.Data(), &tag);
        treeSW->SetBranchAddress("lab1_ID_idx", &ID);
      }
    else
      {
	treeSW->SetBranchAddress(tagName.Data(), &tag);
        treeSW->SetBranchAddress("lab1_ID", &ID);
      }
    
    for (int i = 0; i<bound; i++)
      {
        TString swname = "nSig_"+s[i]+"_Evts_sw";
        treeSW->SetBranchAddress(swname.Data(), &sw[i]);
      }

    Float_t c = 299792458.;
    Double_t sqSumsW = 0;

    for (Long64_t jentry=0; jentry<treeSW->GetEntries(); jentry++) {
      treeSW->GetEntry(jentry);
      double m = 0;
      double merr = 0;
      if(pathFile.Contains("toys") == true || pathFile.Contains("Toys") == true || pathFile.Contains("TOYS") == true)
        {
          m =tau;
          merr = tauerr;
        }
      else
        {
          m =tau*1e9/c;
          merr = tauerr*1e9/c;
	    }
      if (m < 0.2) continue;
      lab0_TAU->setVal(m);
      lab0_TAUERR->setVal(merr);

      if (tagweight > 0.5) tagweight = 0.5;
      lab0_TAGOMEGA->setVal(tagweight);
      
      if (ID > 0) { qf->setIndex(1); } 
      else {  qf->setIndex(-1); }

      if( tag > 0.1 ){ qt->setIndex(1); }
      else if ( tag < -0.1 )  { qt->setIndex(-1); }
      else{ qt->setIndex(0); }
      
      Double_t sum_sw=0;
      for (int i = 0; i<bound; i++) {
	sum_sw += sw[i];
      }
      weights->setVal(sum_sw);
      sqSumsW += sum_sw*sum_sw;
      
      if( tag == 0 )
	{
	  if( ID > 0 ) { dataSetContr[4]->add(*obs);}  else{  dataSetContr[5]->add(*obs); }
	}
      else if ( tag == -1)
	{
	  if ( ID > 0 ){ dataSetContr[2]->add(*obs); } else { dataSetContr[3]->add(*obs); }
	}
      else if ( tag == 1)
	{
	  if( ID > 0) {  dataSetContr[0]->add(*obs); } else { dataSetContr[1]->add(*obs); }
	}
      else { std::cout<<"Wrong event!"<<std::endl;}
      
    }

    RooDataSet* dataSet;
    if (weighted == true)
      {
        dataSet = new RooDataSet(   cat.Data(), cat.Data(), *obs, namew.Data());  // create data set //
      }
    else
      {
        dataSet = new RooDataSet(   cat.Data(), cat.Data(), *obs);
      }
       


    /*    if ( weighted == true )
      {
	dataSet = new RooDataSet(cat.Data(),cat.Data(), *obs,

	
	dataSet = new RooDataSet(cat.Data(),cat.Data(), *obs, 
				 RooFit::Import(catcont[0].Data(), *dataSetContr[0]),
				 RooFit::Import(catcont[1].Data(), *dataSetContr[1]),
				 RooFit::Import(catcont[2].Data(), *dataSetContr[2]),
				 RooFit::Import(catcont[3].Data(), *dataSetContr[3]),
				 RooFit::Import(catcont[4].Data(), *dataSetContr[4]),
				 RooFit::Import(catcont[5].Data(), *dataSetContr[5]),
				 RooFit::WeightVar("sWeights"));
	
      }
    else
      {
	
	
	dataSet = new RooDataSet(cat.Data(),cat.Data(), *obs, 
				 RooFit::Import(catcont[0].Data(), *dataSetContr[0]),
                                 RooFit::Import(catcont[1].Data(), *dataSetContr[1]),
                                 RooFit::Import(catcont[2].Data(), *dataSetContr[2]),
                                 RooFit::Import(catcont[3].Data(), *dataSetContr[3]),
                                 RooFit::Import(catcont[4].Data(), *dataSetContr[4]),
	                       RooFit::Import(catcont[5].Data(), *dataSetContr[5]));
      }
    */

    if ( debug == true){
      if ( dataSet != NULL ){
	std::cout<<"[INFO] ==> Create "<<dataSet->GetName()<<std::endl;
	std::cout<<"Sample "<<cat<<" number of entries: "<<treeSW->GetEntries()<<" in data set: "<<dataSet->numEntries()<<std::endl;
	std::cout<<"sum of sWeights: "<<dataSet->sumEntries()<<" squared sum of sWeights: "<<sqSumsW<<std::endl;
      } else { std::cout<<"Error in create dataset"<<std::endl; }
    }

    work->import(*dataSet, true);
    for (int i = 0; i< 6; i++)
      {
        work->import(*dataSetContr[i]);
      }
    return work;

    
  }

  //===========================================================================
  // Copy Data for Toys, changeRooCategory to RooRealVar
  //===========================================================================

  RooDataSet* CopyDataForToys(TTree* tree, 
			      TString& mVar, 
			      TString& mDVar,
			      TString& PIDKVar,
			      TString& tVar,
			      TString& terrVar,
			      TString& tagVar, 
			      TString& tagOmegaVar,
			      TString& idVar, 
			      TString& trueIDVar,
			      TString& dataName, 
			      bool debug)
  {
    if(debug == true) 
      {
	std::cout<<"Name of tree: "<<tree->GetName()<<std::endl;
	std::cout<<"Name of B(s) mass observable: "<<mVar<<std::endl;
	std::cout<<"Name of D(s) mass observable: "<<mDVar<<std::endl;
	std::cout<<"Name of PIDK observable: "<<PIDKVar<<std::endl;
	std::cout<<"Name of time observable: "<<tVar<<std::endl;
	std::cout<<"Name of time error observable: "<<terrVar<<std::endl;
	std::cout<<"Name of tag observable: "<<tagVar<<std::endl;
	std::cout<<"Name of mistag observable: "<<tagOmegaVar<<std::endl;
	std::cout<<"Name of id observable: "<<idVar<<std::endl;
	std::cout<<"Name of trueid variable: "<<trueIDVar<<std::endl;
	std::cout<<"Name of data set: "<<dataName<<std::endl;
	

      }
    RooDataSet* dataout = NULL;

    
    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),5300, 5800);
    RooRealVar* lab2_MM = new RooRealVar(mDVar.Data(),mDVar.Data(),1930, 2015);
    RooRealVar* lab1_PIDK = NULL;
    if ( dataName.Contains("Pi") == true )
      {  lab1_PIDK= new RooRealVar(PIDKVar.Data(),PIDKVar.Data(),0,150);}
    else
      {  lab1_PIDK= new RooRealVar(PIDKVar.Data(),PIDKVar.Data(),log(5),log(150));}
    RooRealVar* lab0_TAU = new RooRealVar(tVar.Data(),tVar.Data(),0.,15.);
    RooRealVar* lab0_TERR = new RooRealVar(terrVar.Data(),terrVar.Data(),0.,0.1);
    RooRealVar* lab0_TAG = new RooRealVar(tagVar.Data(),tagVar.Data(),-2.0,2.0);
    RooRealVar* lab0_TAGOMEGA = new RooRealVar(tagOmegaVar.Data(),tagOmegaVar.Data(),0.,1.);
    RooRealVar* lab1_ID = new RooRealVar(idVar.Data(),idVar.Data(),-1000,1000);
    RooRealVar* lab0_TRUEID = new RooRealVar(trueIDVar.Data(),trueIDVar.Data(),0,100);

    dataout = new RooDataSet(dataName.Data(),dataName.Data(),
			     RooArgSet(*lab0_MM,*lab0_TAU, *lab0_TERR, *lab0_TAG,*lab0_TAGOMEGA,*lab1_ID,*lab0_TRUEID,*lab2_MM,*lab1_PIDK));

    Double_t lab0_MM3,lab0_TAU3, lab0_TERR3, lab2_MM3, lab1_PIDK3;
    Int_t  lab0_TAG3;
    Double_t lab0_TAGOMEGA3, lab0_TRUEID3;
    Int_t lab1_ID3;
    
    
    tree->SetBranchAddress(mVar.Data(), &lab0_MM3);
    tree->SetBranchAddress(mDVar.Data(), &lab2_MM3);
    tree->SetBranchAddress(PIDKVar.Data(), &lab1_PIDK3);
    tree->SetBranchAddress(tVar.Data(),&lab0_TAU3);
    tree->SetBranchAddress(terrVar.Data(),&lab0_TERR3);
    tree->SetBranchAddress(tagVar.Data(),&lab0_TAG3);
    tree->SetBranchAddress(tagOmegaVar.Data(),&lab0_TAGOMEGA3);
    tree->SetBranchAddress(idVar.Data(),&lab1_ID3);
    tree->SetBranchAddress(trueIDVar.Data(),&lab0_TRUEID3);

    for (Long64_t jentry=0; jentry<tree->GetEntries(); jentry++) {

      tree->GetEntry(jentry);

      lab0_MM->setVal(lab0_MM3);
      lab2_MM->setVal(lab2_MM3);
      lab1_PIDK->setVal(lab1_PIDK3);
      lab0_TAU->setVal(lab0_TAU3);
      lab0_TERR->setVal(lab0_TERR3);
      lab0_TAG->setVal(lab0_TAG3);
      lab0_TAGOMEGA->setVal(lab0_TAGOMEGA3);
      lab1_ID->setVal(lab1_ID3);
      lab0_TRUEID->setVal(lab0_TRUEID3);

      dataout->add(RooArgSet(*lab0_MM,*lab0_TAU,*lab0_TERR,*lab0_TAG,*lab0_TAGOMEGA,*lab1_ID,*lab0_TRUEID,*lab2_MM,*lab1_PIDK));
    }

    if (debug == true) 
      {
	if ( dataout != NULL ){
	  std::cout<<"[INFO] ==> Create "<<dataout->GetName()<<std::endl;
	  std::cout<<"number of entries in tree: "<<tree->GetEntries()<<" in data set: "<<dataout->numEntries()<<std::endl;
	} else { std::cout<<"Error in create dataset"<<std::endl; }
      }
    return dataout;
  }

  RooWorkspace* ReadLbLcPiFromSWeights(TString& pathFile,
                                       TString& treeName,
				       double P_down, double P_up,
				       double PT_down, double PT_up,
                                       double nTr_down, double nTr_up,
				       double PID_down,double PID_up,
                                       TString& mVar,
				       TString& mDVar,
				       TString& pVar,
				       TString& ptVar,
				       TString& nTrVar,
				       TString& pidVar,
				       RooWorkspace* workspace, 
                                       bool debug
                                       )

  {

    RooAbsData::setDefaultStorageType(RooAbsData::Tree);

    if ( debug == true)
      {
	std::cout << "[INFO] ==> SFitUtils::ReadLbLcPiFromSWeights(...)."
                  << " Obtain dataSets from sWeights for LbLcPi"
                  << std::endl;
	std::cout << "Name of path file: " << pathFile << std::endl;
	std::cout << "Name of tree name: " << treeName << std::endl;
	std::cout << "Name of Lb: " << mVar << std::endl;
	std::cout << "Name of Lc: " << mDVar << std::endl;
	std::cout << "Name of p: " << pVar << " in range ("<<P_down<<","<<P_up<<")"<<std::endl;
	std::cout << "Name of pt: " << ptVar << " in range ("<<PT_down<<","<<PT_up<<")"<<std::endl;
	std::cout << "Name of nTr: " << nTrVar <<" in range ("<<nTr_down<<","<<nTr_up<<")"<<std::endl;
	std::cout << "Name of PIDK: " << pidVar <<" in range ("<<PID_down<<","<<PID_up<<")"<<std::endl;
	
      }

    RooWorkspace* work = NULL;
    if (workspace == NULL){ work =  new RooWorkspace("workspace","workspace");}
    else {work = workspace; }

    Double_t Dmass_down = 2200;
    Double_t Dmass_up = 2380;
    Double_t Bmass_down = 5400;
    Double_t Bmass_up = 5800;
    RooRealVar* lab0_MM = new RooRealVar(mVar.Data(),mVar.Data(),Bmass_down, Bmass_up);
    RooRealVar* lab2_MM = new RooRealVar(mDVar.Data(),mDVar.Data(),Dmass_down, Dmass_up);
    RooRealVar* lab1_PIDK = new RooRealVar(pidVar.Data(), pidVar.Data(), PID_down, PID_up);
    RooRealVar* lab1_P  = new RooRealVar(pVar.Data(),pVar.Data(),log(P_down),log(P_up));
    RooRealVar* lab1_PT  = new RooRealVar(ptVar.Data(),ptVar.Data(),log(PT_down),log(PT_up));
    RooRealVar* nTracks  = new RooRealVar(nTrVar.Data(),nTrVar.Data(),log(nTr_down),log(nTr_up));

    TTree* treeSW = ReadTreeMC(pathFile.Data(),treeName.Data(), debug);

    RooDataSet* data[2];

    std::vector <TString> s;
    s.push_back("down");
    s.push_back("up");

    TString namew = "sWeights";
    RooRealVar* weights;
    weights = new RooRealVar(namew.Data(), namew.Data(), -2.0, 2.0 );  // create weights //

    
    for(int i = 0; i <2; i++)
      {
	TString dataName = "ProtonsSample_"+s[i];
	data[i] = NULL;
	data[i] = new RooDataSet(   dataName.Data(), dataName.Data(),
				    RooArgSet(*lab0_MM,*lab2_MM,*lab1_PT,*lab1_P,*nTracks,*lab1_PIDK,*weights),namew.Data());
	
	Double_t sw;
	Double_t p, pt;
	Double_t nTr;
	Double_t PIDK;
	Double_t massB;
	Double_t massD; 

	treeSW->SetBranchAddress(mVar.Data(), &massB);
	treeSW->SetBranchAddress(mDVar.Data(), &massD);
	treeSW->SetBranchAddress(pVar.Data(), &p);
	treeSW->SetBranchAddress(nTrVar.Data(),&nTr);
	treeSW->SetBranchAddress(pidVar.Data(),&PIDK);
	treeSW->SetBranchAddress(ptVar.Data(), &pt);
	
	TString swname = "nSig_"+s[i]+"_Evts_sw";
	treeSW->SetBranchAddress(swname.Data(), &sw);

	for (Long64_t jentry=0; jentry<treeSW->GetEntries(); jentry++) {
	  treeSW->GetEntry(jentry);
	  lab0_MM->setVal(massB);
	  lab1_P->setVal(log(p));
	  lab1_PT->setVal(log(pt));
	  lab1_PIDK->setVal(PIDK); 
	  nTracks->setVal(log(nTr));
	  lab2_MM->setVal(massD);
	  weights->setVal(sw);
	  data[i]->add(RooArgSet(*lab0_MM,*lab2_MM,*lab1_PT,*lab1_P,*nTracks,*lab1_PIDK,*weights),sw,0);
	}
	
	if ( data[i] != NULL  ){
	  std::cout<<"[INFO] ==> Create "<<data[i]->GetName()<<std::endl;
	  std::cout<<" number of entries in data set: "<<data[i]->numEntries()<<" with sum: "<<data[i]->sumEntries()<<std::endl;
	} else { std::cout<<"Error in create dataset"<<std::endl; }
	
	work->import(*data[i]);

	TString dupa = "LbLcPi_TrMom";
        SaveDataSet(data[i], lab1_PT , s[i], dupa, debug);
        TString dupa2 = "LbLcPi_Tracks";
        SaveDataSet(data[i], nTracks , s[i], dupa2, debug);
	TString dupa3 = "LbLcPi_PIDK";
        SaveDataSet(data[i], lab1_PIDK , s[i], dupa3, debug);
        TString dupa4 = "LbLcPi_MassD";
        SaveDataSet(data[i], lab2_MM , s[i], dupa4, debug);
	TString dupa5 = "LbLcPi_Mom";
	//SaveDataSet(data[i], lab1_P , s[i], dupa5, debug);
	
	
      }

    return work;
  }

} //end of namespace
