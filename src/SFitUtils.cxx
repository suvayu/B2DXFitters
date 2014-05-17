//---------------------------------------------------------------------------//
//                                                                           //
//  SFit utilities                                                           //
//                                                                           //
//  Source file                                                              //
//                                                                           //
//  Author: Agnieszka Dziurda                                                //
//  Author: Vladimir Vava Gligorov                                           //
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
#include "RooArgList.h"
// B2DXFitters includes
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/SFitUtils.h"
#include "B2DXFitters/KinHack.h"
#include "B2DXFitters/DecayTreeTupleSucksFitter.h"
#include "B2DXFitters/PlotSettings.h"
#include "B2DXFitters/MDFitterSettings.h"
#include "B2DXFitters/DLLTagCombiner.h"
#include "B2DXFitters/TagDLLToTagDec.h"
#include "B2DXFitters/TagDLLToTagEta.h"
#include "B2DXFitters/MistagCalibration.h"

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

  RooWorkspace* ReadDataFromSWeights(TString& pathFile,
				     TString& treeName,
				     MDFitterSettings* mdSet,
				     TString& part,
				     bool weighted,
				     bool toys,
				     bool applykfactor,
				     bool debug
				     )
  {
    if ( debug == true) 
      {
	std::cout<<"[INFO] ==> GeneralUtils::ReadDataFromSWeights(...). Read data set from sWeights NTuple "<<std::endl;
	std::cout<<"path of file: "<<pathFile<<std::endl;
	std::cout<<"name of tree: "<<treeName<<std::endl;
	std::cout<<"apply kfactor: "<<applykfactor<<std::endl;
	std::cout<<"Mode: "<<part<<std::endl;
      }

    RooWorkspace* work = NULL;
    work =  new RooWorkspace("workspace","workspace");
    TTree* treeSW = ReadTreeMC(pathFile.Data(),treeName.Data(), debug);
     
    RooRealVar* lab0_TAU      = new RooRealVar(mdSet->GetTimeVar(),                mdSet->GetTimeVar(),
                                               mdSet->GetTimeRangeDown(),          mdSet->GetTimeRangeUp());
    RooRealVar* lab0_TAUERR   = new RooRealVar(mdSet->GetTerrVar(),                mdSet->GetTerrVar(),
                                               mdSet->GetTerrRangeDown(),          mdSet->GetTerrRangeUp());
       
    std::vector <RooCategory*> lab0_TAG;
    if (toys == false )
      {
	if( mdSet->CheckTagVar() == true )
	  {
	    for(int i = 0; i<mdSet->GetNumTagVar(); i++)
	      {
		lab0_TAG.push_back(new RooCategory(mdSet->GetTagVar(i), "flavour tagging result"));
		TString BName = Form("B_%d",i);
		TString BbarName = Form("Bbar_%d",i);
		TString UnName = Form("Utagged_%d",i);
		lab0_TAG[i]->defineType(BName.Data(),     1);
		lab0_TAG[i]->defineType(BbarName.Data(), -1);
		lab0_TAG[i]->defineType(UnName.Data(),    0);

	      }
	  }
      }
    else
      {
	lab0_TAG.push_back(new RooCategory("tagDecComb", "flavour tagging result"));
	lab0_TAG[0]->defineType("B_3",     3);
        lab0_TAG[0]->defineType("Bbar_3", -3);
	lab0_TAG[0]->defineType("B_2",     2);
        lab0_TAG[0]->defineType("Bbar_2", -2);
	lab0_TAG[0]->defineType("B_1",     1);
	lab0_TAG[0]->defineType("Bbar_1", -1);
	lab0_TAG[0]->defineType("Untagged",0);
      }
    
    std::vector <RooRealVar*> lab0_TAGOMEGA;
    if ( toys == false )
      {
	if( mdSet->CheckTagOmegaVar() == true )
	  {
	    for(int i = 0; i<mdSet->GetNumTagOmegaVar(); i++)
	      {
		lab0_TAGOMEGA.push_back(mdSet->GetObs(mdSet->GetTagOmegaVar(i)));
	      }
	  }
      }
    else
      {
	lab0_TAGOMEGA.push_back(new RooRealVar("tagOmegaComb","tagOmegaComb",0.0, 0.5));
      }
    
    RooCategory* qf = new RooCategory("qf", "bachelor charge");
    qf->defineType("h+",  1);
    qf->defineType("h-", -1);

    
    //RooRealVar* lab1_ID = new RooRealVar(idVar.Data(),idVar.Data(),1.,-1.,1.);           
    //RooRealVar* nTracks = new RooRealVar("nTracks","nTracks",15,1000);
    //RooRealVar* lab1_P = new RooRealVar("lab1_P","lab1_P",0,650000);
    //RooRealVar* lab1_PIDK = new RooRealVar("lab1_PIDK","lab1_PIDK",log(5), log(150)); //-150,150);
    //RooRealVar* lab1_PIDp = new RooRealVar("lab1_PIDp","lab1_PIDp",-150,150);
    //RooRealVar* lab1_PT = new RooRealVar("lab1_PT","lab1_PT",0,45000);


    std::vector <TString> s;
    if( pathFile.Contains("3modeskkpi") == true or pathFile.Contains("3MODESKKPI") == true )
      {
	if(debug == true) { std::cout<<"[INFO] 3 Ds final states: NonRes, PhiPi, Kstk"<<std::endl; }
	s.push_back("both_nonres");
        s.push_back("both_phipi");
        s.push_back("both_kstk");
      }
    else
      {
	if( debug == true ) { std::cout<<"[INFO] 5 Ds final states: NonRes, PhiPi, KstK, KPiPi, PiPiPi"<<std::endl; }
	if(part.Contains("BDPi") == true ) 
	  {
	    s.push_back("both");
	  }
	else
	  {
	    if ( pathFile.Contains("both") == true || toys == true)
              {
		s.push_back("both_nonres");
                s.push_back("both_phipi");
                s.push_back("both_kstk");
                s.push_back("both_kpipi");
                s.push_back("both_pipipi");
              }
            else if ( pathFile.Contains("up") == true )
              {
                s.push_back("up_nonres");
                s.push_back("up_phipi");
                s.push_back("up_kstk");
                s.push_back("up_kpipi");
		s.push_back("up_pipipi");
              }
            else if ( pathFile.Contains("down") == true )
              {
                s.push_back("down_nonres");
                s.push_back("down_phipi");
                s.push_back("down_kstk");
                s.push_back("down_kpipi");
                s.push_back("down_pipipi");
              }

	  }
      }
    
    if ( toys == true && ( pathFile.Contains("toys1m") == true || pathFile.Contains("Toys1M") == true || pathFile.Contains("TOYS1M") == true ) )
      {
	if (debug == true ) { std::cout<<"[INFO]  1D Toys: read only PhiPi"<<std::endl;}
        s.push_back("both_phipi");
      }
	
    Int_t bound = s.size();
    if ( debug == true ) { std::cout<<"[INFO] sWeights bound: "<<bound<<std::endl;}
    TString cat;
    cat = "dataSet_time_"+part;
    
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
				   *qf);
    if ( toys == false )
      {
	if( mdSet->CheckTagVar() == true )
	  {
	    for(int i = 0; i<mdSet->GetNumTagVar(); i++)
	      {
		obs->add(*lab0_TAG[i]);
		std::cout<<"Adding "<<lab0_TAG[i]->GetName()<<std::endl;
	      }
	  }
	if( mdSet->CheckTagOmegaVar() == true )
	  {
	    for(int i = 0; i<mdSet->GetNumTagOmegaVar(); i++)
	      {
		obs->add(*lab0_TAGOMEGA[i]);
		std::cout<<"Adding "<<lab0_TAGOMEGA[i]->GetName()<<std::endl;
	      }
	  }
      }
    else
      {
	obs->add(*lab0_TAG[0]);
	obs->add(*lab0_TAGOMEGA[0]); 
      }
    TString setOfObsName = "SetOfObservables";
    obs->setName(setOfObsName.Data());
    
    TString namew = "sWeights";
    weights = new RooRealVar(namew.Data(), namew.Data(), -1.0, 1.5 );  // create weights //
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
    Int_t ID;
    Double_t sw[bound];
    Double_t trueid; 
    Double_t mass;
            
    treeSW->SetBranchAddress(mdSet->GetTimeVar().Data(), &tau);
    treeSW->SetBranchAddress(mdSet->GetTerrVar().Data(), &tauerr);
    TString nameID = mdSet->GetIDVar()+"_idx"; 
    treeSW->SetBranchAddress(nameID.Data(), &ID);
    treeSW->SetBranchAddress(mdSet->GetMassBVar().Data(), &mass);
    Int_t tag[mdSet->GetNumTagVar()];
    Double_t omega[mdSet->GetNumTagOmegaVar()];
    
    if (toys == false)
      {
	if( mdSet->CheckTagVar() == true )
	  {
	    for(int k = 0; k<mdSet->GetNumTagVar(); k++)
	      {
		TString nameTag = mdSet->GetTagVar(k)+"_idx";
		treeSW->SetBranchAddress(nameTag, &tag[k]);
	      }
	  }
	if( mdSet->CheckTagOmegaVar() == true )
	  {
	    for(int k = 0; k<mdSet->GetNumTagOmegaVar(); k++)
	      {
		treeSW->SetBranchAddress(mdSet->GetTagOmegaVar(k).Data(), &omega[k]);
	  }
	  }
      }
    else
      {
	treeSW->SetBranchAddress("tagDecComb_idx", &tag[0]);
	treeSW->SetBranchAddress("tagOmegaComb", &omega[0]);
      }

    if(toys)
      {
	treeSW->SetBranchAddress("lab0_TRUEID", &trueid);
      }
    
    
    // Double_t nTr;
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

    
    Double_t sqSumsW = 0;
    double correction=0.0;
 
    Double_t tagEff[2];
    tagEff[0] = 0;
    tagEff[1] = 0;

    for (Long64_t jentry=0; jentry<treeSW->GetEntries(); jentry++) {
      treeSW->GetEntry(jentry);
      double m = 0; 
      double merr = 0;
      //if (jentry>10000) continue;  
      if(toys)
	{
	  m =tau;
	  merr = tauerr;
	  if (applykfactor == true )
	    {
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
	    }
	  else
	    { correction = 1.; }
	  //std::cout << "The correction factor is " << correction << std::endl;
	  m *=correction;
	}
      else
	{
	  m =tau;   
	  merr = tauerr;
	}
      
      //if ( m < 0.2 ) continue; 

      lab0_TAU->setVal(m);
      lab0_TAUERR->setVal(merr);
      //if (tagweight > 0.5) tagweight = 0.5;
      //lab0_TAGOMEGA->setVal(tagweight);
      
      //lab1_P->setVal(p);
      //lab1_PT->setVal(pt);
      //nTracks->setVal(nTr);
      //lab1_PIDK->setVal(PIDK);
      //lab1_PIDp->setVal(PIDp);  
      //lab0_MM->setVal(mass);

      Double_t sum_sw=0;
      for (int i = 0; i<bound; i++) {
	sum_sw += sw[i];
      }

      
      if (ID > 0) { qf->setIndex(1); } else { qf->setIndex(-1); }
      if( toys == false)
	{
	  if(  mdSet->CheckTagVar() == true )
	    {
	      for(int k = 0; k<mdSet->GetNumTagVar(); k++)
		{
		  if( tag[k] > 0.1 ) {   tag[k] = 1; tagEff[k] += sum_sw; }
		  else if ( tag[k] < -0.1 ) { tag[k] = -1; tagEff[k] += sum_sw; }
		  else{ tag[k]=0; }
		  
		  lab0_TAG[k]->setIndex(tag[k]);
		}
	    }
	  if(  mdSet->CheckTagOmegaVar() == true )
	    {
	      for(int k = 0; k<mdSet->GetNumTagOmegaVar(); k++)
		{
		  if (omega[k] > 0.5){ omega[k] = 0.5;}
	      lab0_TAGOMEGA[k]->setVal(omega[k]);
		}
	    }
	}
      else
	{
	  lab0_TAG[0]->setIndex(tag[0]);
	  lab0_TAGOMEGA[0]->setVal(omega[0]);
	}

      //sum_sw = 1.0;
      weights->setVal(sum_sw);
      sqSumsW += sum_sw*sum_sw;
      //if ( m > mdSet->GetTimeRangeDown() && m < mdSet->GetTimeRangeUp())
      //	{
	  if (weighted == true )
	    {
	      dataSet->add(*obs,sum_sw,0);
	    }
	  else
	    {
	      dataSet->add(*obs);
	    }
	  //	}
      //std::cout << "this event has time = " << m << " and error = " << merr << " with weight = " << sum_sw << std::endl;  
      
    }
      
    if ( debug == true){
	if ( dataSet != NULL ){
	    std::cout<<"[INFO] ==> Create "<<dataSet->GetName()<<std::endl;
	    std::cout<<"Sample "<<cat<<" number of entries: "<<treeSW->GetEntries()<<" in data set: "<<dataSet->numEntries()<<std::endl;
	    std::cout<<"sum of sWeights: "<<dataSet->sumEntries()<<" squared sum of sWeights: "<<sqSumsW<<std::endl; 
	} else { std::cout<<"Error in create dataset"<<std::endl; }
    }

    std::cout<<"tagEff1: "<<tagEff[0]/dataSet->sumEntries()<<" = "<<tagEff[0]<<" / "<<dataSet->sumEntries()<<std::endl;
    std::cout<<"tagEff2: "<<tagEff[1]/dataSet->sumEntries()<<" = "<<tagEff[0]<<" / "<<dataSet->sumEntries()<<std::endl;
    if ( toys == false)
      {
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
	if(  mdSet->CheckTagVar() == true )
	  {
	    for(int k = 0; k<mdSet->GetNumTagVar(); k++)
	      {
		tagList->add(*lab0_TAG[k]);
	      }
	  }
	
	MistagCalibration* calibMistag[tagNum];
	RooRealVar* p0[tagNum];
	RooRealVar* p1[tagNum];
	RooRealVar* av[tagNum];
	
	if(  mdSet->CheckTagOmegaVar() == true )
	  {
	    for(int k = 0; k<mdSet->GetNumTagOmegaVar(); k++)
	      {
		std::cout<<"[INF0] Calibration: p0="<<mdSet->GetCalibp0(k)<<" p1: "<<mdSet->GetCalibp1(k)<<" av: "<<mdSet->GetCalibAv(k)<<std::endl;
		p0[k] = new RooRealVar(Form("p0_%d",k),Form("p0_%d",k),mdSet->GetCalibp0(k));
		p1[k] = new RooRealVar(Form("p1_%d",k),Form("p1_%d",k),mdSet->GetCalibp1(k));
		av[k] = new RooRealVar(Form("av_%d",k),Form("av_%d",k),mdSet->GetCalibAv(k));
		TString nameCalib = mdSet->GetTagOmegaVar(k)+"_calib";
		calibMistag[k] = new MistagCalibration(nameCalib.Data(), nameCalib.Data(),
						       *lab0_TAGOMEGA[k], *p0[k], *p1[k], *av[k]);
		dataSet->addColumn(*calibMistag[k]);
		tagOmegaList->add(*calibMistag[k]);
	      }
	  }
	
	if( debug == true )
	  {
	    std::cout<<"[INFO] Taggers list: "<<std::endl;
	    tagList->Print("v");
	    std::cout<<"[INFO] Mistags list: "<<std::endl;
	    tagOmegaList->Print("v");
	  }
	
	DLLTagCombiner* combiner = new DLLTagCombiner("tagCombiner","tagCombiner",*tagList,*tagOmegaList);
	TagDLLToTagDec* tagDecComb = new TagDLLToTagDec("tagDecComb","tagDecComb",*combiner,*tagList);
	TagDLLToTagEta* tagOmegaComb = new TagDLLToTagEta("tagOmegaComb","tagOmegaComb",*combiner);
	
	dataSet->addColumn(*tagDecComb);
	dataSet->addColumn(*tagOmegaComb);
      }

    work->import(*dataSet);
    return work;

  }

  //===========================================================================
  // Create Mistag templates
  //===========================================================================
  RooArgList* CreateMistagTemplates(RooDataSet* data, MDFitterSettings* mdSet, Int_t bins, bool save, bool debug)
  {
    RooArgList* pdfList = new RooArgList();
    const RooArgSet* obs = data->get();
 
    RooRealVar* mistag = (RooRealVar*)obs->find("tagOmegaComb");
    mistag->setRange(0,0.5);

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

    Int_t numOfTemp = std::pow(2,tagNum)-1;
    if (debug == true) { std::cout<<"Number of mistag templates: "<<numOfTemp<<std::endl; }
    
    RooDataSet* sliceData[numOfTemp];
    RooHistPdf* mistagPDF[numOfTemp];
    for(int i =1; i<numOfTemp+1; i++)
      {
	std::cout<<"Cut on tagger: "<<i<<" and "<<-i<<std::endl;  
	sliceData[i-1] = (RooDataSet*)data->reduce(*obs,Form("((tagDecComb == %d) || (tagDecComb == %d))",i,-i));
	std::cout<<"[INFO] sliceData "<<i<<" with entries: "<<sliceData[i-1]->numEntries()<<std::endl;
	TString namePDF = Form("sigMistagPdf_%d",i);
	mistagPDF[i-1] = NULL;
	mistagPDF[i-1] = CreateHistPDF(sliceData[i-1], mistag, namePDF, bins, debug);
	if( debug == true && mistagPDF[i-1] != NULL) {std::cout<<"[INFO] Create RooHistPDF done"<<std::endl;}
	pdfList->add(*mistagPDF[i-1]);
	TString t ="";
	PlotSettings* plotSet = new PlotSettings("plotSet","plotSet");
	plotSet->SetBin(bins);
	SaveTemplate(sliceData[i-1], mistagPDF[i-1], mistag, namePDF, t, plotSet, debug );
      }
    if( save == true)
      {
	RooWorkspace* workOut = new RooWorkspace("workspace","workspace");
	for(int i =0; i<numOfTemp; i++)
	  {
	    workOut->import(*mistagPDF[i]);
	  }
	if(debug == true ){ workOut->Print("v"); }
	workOut->SaveAs("templates_mistag.root");
      } 
    return pdfList;
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
				       PlotSettings* plotSet,
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
    
    if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

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

	if (plotSet->GetStatus() == true )
	  {
	    TString mode = "Lb2LcPi";
	    SaveDataSet(data[i], lab1_PT ,   s[i], mode, plotSet, debug);
	    SaveDataSet(data[i], nTracks ,   s[i], mode, plotSet, debug);
	    SaveDataSet(data[i], lab1_PIDK , s[i], mode, plotSet, debug);
	    SaveDataSet(data[i], lab2_MM ,   s[i], mode, plotSet, debug);
	  }
	
	
      }

    return work;
  }

} //end of namespace
