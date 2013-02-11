

// ROOT and RooFit includes
#include "RooFormulaVar.h"
#include "RooAddPdf.h"
#include "RooKeysPdf.h"
#include "RooExtendPdf.h"
#include "RooEffProd.h"
#include "RooGaussian.h"
#include "RooDecay.h"
#include "RooBDecay.h"
#include "RooCBShape.h"
#include "RooWorkspace.h"
#include "RooRealVar.h"
#include "RooExponential.h"
#include "TFile.h"
#include "TTree.h"
#include "RooDataSet.h"
#include "RooArgSet.h"
#include "RooHistPdf.h"
#include <string>
#include <vector>
#include <fstream>


#include "B2DXFitters/Bs2Dsh2011TDAnaModels.h"

using namespace std;


namespace Bs2Dsh2011TDAnaModels {

  //===============================================================================
  // Double crystal ball function where:
  // mean, sigma1, sigma2 are RooRealVar
  // alpha1, alpha2, n1, n2 and fraction are double  
  //===============================================================================
    
  RooAbsPdf* buildDoubleCBEPDF_fix( RooAbsReal& obs, 
				    RooRealVar& meanVar, 
				    RooRealVar& sigma1Var, double alpha1, double n1, 
				    RooRealVar& sigma2Var, double alpha2, double n2, 
				    double frac, 
				    RooRealVar& nEvents, 
				    const char* prefix, 
				    const char* bName, 
				    bool debug){
    
    if (debug == true) 
      {
	cout<<"---------------------------------------------------"<<endl;
	cout<<"=====> Build signal CB model with fixing parameters"<<endl;
	cout<<"---------------------------------------------------"<<endl;
      }
    TString name;

    // ------------------------------------------ Create RooRealVar ----------------------------------------------------//
    if (debug == true)
      {
	cout<<endl;
	cout<<"--------------- Create RooRealVar --------------"<<endl;
      }
    RooRealVar* alpha1Var = NULL;
    alpha1Var = new RooRealVar( Form( "DblCBPDF%s_alpha1", prefix ), Form( "'%s' %s DblCB PDF in %s - alpha1", prefix, bName, obs.GetName() ), alpha1);
    if (alpha1Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<alpha1Var->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}
    
    RooRealVar* alpha2Var = NULL;
    alpha2Var = new RooRealVar( Form( "DblCBPDF%s_alpha2", prefix ),Form( "'%s' %s DblCB PDF in %s - alpha2", prefix, bName, obs.GetName() ),alpha2);
    if (alpha2Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<alpha2Var->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}


    RooRealVar* n1Var = NULL;
    n1Var =  new RooRealVar( Form( "DblCBPDF%s_n1", prefix ), Form( "'%s' %s DblCB PDF in %s - n1", prefix, bName, obs.GetName() ), n1);
    if (n1Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<n1Var->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    RooRealVar* n2Var = NULL; 
    n2Var = new RooRealVar( Form( "DblCBPDF%s_n2", prefix ),Form( "'%s' %s DblCB PDF in %s - n2",prefix, bName, obs.GetName() ), n2);
    if (n2Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<n2Var->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    RooRealVar* fracVar = NULL;
    fracVar = new RooRealVar( Form( "DblCBPDF%s_frac", prefix ), Form( "'%s' %s DblCB PDF in %s - frac", prefix, bName, obs.GetName() ), frac);
    if (fracVar != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<fracVar->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    // ------------------------------------------ Create Single CB ----------------------------------------------------//
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Signle CB ---------------"<<endl;
    RooCBShape* pdf1 = NULL; 
    pdf1 = new RooCBShape( Form( "DblCBPDF%s_CB1", prefix ), Form( "'%s' %s CB1 PDF in %s", prefix, bName, obs.GetName() ),
			   obs,meanVar, sigma1Var, *alpha1Var, *n1Var);
    if (pdf1 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf1->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    RooCBShape* pdf2 = NULL;
    pdf2 = new RooCBShape( Form( "DblCBPDF%s_CB2", prefix ),Form( "'%s' %s CB2 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,meanVar, sigma2Var, *alpha2Var, *n2Var);
    if (pdf2 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf2->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Double CB ----------------------------------------------------// 
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblCBPDF%s", prefix ),Form( "'%s' %s DbleCB PDF in %s", prefix, bName, obs.GetName() ),
                                    *pdf1, *pdf2, *fracVar);
    if (pdf != NULL){ if (debug == true) cout<<"Create doubleCB PDF: "<<pdf->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
    
    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//

    RooExtendPdf* epdf = NULL;
    epdf = new RooExtendPdf( Form( "SigEPDF_%s", prefix ),Form( "SigEPDF_%s", prefix ),*pdf, nEvents);
    if( epdf != NULL) { if (debug == true) cout<<"Create extend signal model "<<epdf->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create extend signal model "<<endl; return NULL; }
    return epdf;
    
  }

  //===============================================================================
  // Double crystal ball function where all parameters are RooRealVar
  //===============================================================================

  RooAbsPdf* buildDoubleCBEPDF_sim( RooAbsReal& obs,
                                    RooRealVar& mean,
                                    RooRealVar& sigma1, 
				    RooRealVar& alpha1,
				    RooRealVar& n1,
                                    RooRealVar& sigma2, 
				    RooRealVar& alpha2,
				    RooRealVar& n2,
                                    RooRealVar& frac,
                                    RooRealVar& nEvents,
                                    const char* prefix,
                                    const char* bName,
                                    bool debug){

    if (debug == true)
      {
	cout<<"---------------------------------------------------"<<endl;
	cout<<"=====> Build signal double CB model for sim fit    "<<endl;
	cout<<"---------------------------------------------------"<<endl;
      }
    TString name;

    
    // ------------------------------------------ Create Single CB ----------------------------------------------------//
    if (debug == true)
      {
	cout<<endl;
	cout<<"--------------- Create Signle CB ---------------"<<endl;
      }
    RooCBShape* pdf1 = NULL;
    pdf1 = new RooCBShape( Form( "DblCBPDF%s_CB1", prefix ), Form( "'%s' %s CB1 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,mean, sigma1, alpha1, n1);
    if (pdf1 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf1->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    RooCBShape* pdf2 = NULL;
    pdf2 = new RooCBShape( Form( "DblCBPDF%s_CB2", prefix ),Form( "'%s' %s CB2 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,mean, sigma2, alpha2, n2);
    if (pdf2 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf2->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Double CB ----------------------------------------------------//
    
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblCBPDF%s", prefix ),Form( "'%s' %s DbleCB PDF in %s", prefix, bName, obs.GetName() ),
			 *pdf1, *pdf2, frac);
    if (pdf != NULL){ if (debug == true) cout<<"Create doubleCB PDF: "<<pdf->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//

    RooExtendPdf* epdf = NULL;
    epdf = new RooExtendPdf( Form( "SigEPDF_%s", prefix ),Form( "SigEPDF_%s", prefix ),*pdf, nEvents);
    
    if( epdf != NULL) { if (debug == true) cout<<"Create extend signal model "<<epdf->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create extend signal model "<<endl; return NULL;}

    return epdf;
  }

  //===============================================================================
  // Double crystal ball function where:
  // mean, sigma1, sigma2 are RooFormulaVar
  // alpha1, alpha2, n1, n2 and fraction are double
  // this function is used in case:
  // Bd->DsPi (for Bs->DsPi mass model)
  // Bd->DsK (for Bs->DsK mass model) 
  //===============================================================================

  RooAbsPdf* buildBdDsX( RooAbsReal& obs, 
			 RooFormulaVar &meanVar, 
			 RooFormulaVar &sigma1Var, 
			 double alpha1, 
			 double n1, 
			 RooFormulaVar &sigma2Var, 
			 double alpha2,
			 double n2, 
			 double frac,
			 TString& namemode,
			 bool debug){

    if (debug == true) 
      {
	cout<<"---------------------------------------------------"<<endl;
	cout<<"=====> Build signal CB model with fixing parameters"<<endl;
	cout<<"---------------------------------------------------"<<endl;
      }
    TString name;

    // ------------------------------------------ Create RooRealVar ----------------------------------------------------//                                 
    if (debug == true) 
      {
	cout<<endl;
	cout<<"--------------- Create RooRealVar --------------"<<endl;
	cout<<"Create RooRealVar: "<<meanVar.GetName()<<endl;
      }
    RooRealVar* alpha1Var = NULL;
    alpha1Var = new RooRealVar( "BdDsX_alpha1", "BdDsX_alpha1", alpha1);
    if (alpha1Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<alpha1Var->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    RooRealVar* alpha2Var = NULL;
    alpha2Var = new RooRealVar( "BdDsX_alpha2","BdDsX_alpha2",alpha2);
    if (alpha2Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<alpha2Var->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    RooRealVar* n1Var = NULL;
    n1Var =  new RooRealVar( "BdDsX_n1","BdDsX_n1", n1);
    if (n1Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<n1Var->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    RooRealVar* n2Var = NULL;
    n2Var = new RooRealVar( "BdDsX_n2","BdDsX_n2", n2);
    if (n2Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<n2Var->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    RooRealVar* fracVar = NULL;
    fracVar = new RooRealVar( "BdDsX_frac","BdDsX_frac", frac);
    if (fracVar != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<fracVar->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    // ------------------------------------------ Create Single CB ----------------------------------------------------//                                  
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Signle CB ---------------"<<endl;
    RooCBShape* pdf1 = NULL;
    pdf1 = new RooCBShape( "BdDsX_CB1","BdDsX_CB1", obs,meanVar, sigma1Var, *alpha1Var, *n1Var);
    if (pdf1 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf1->GetName()<<endl;} else { if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    RooCBShape* pdf2 = NULL;
    pdf2 = new RooCBShape( "BdDsX_CB2","BdDsX_CB2",obs,meanVar, sigma2Var, *alpha2Var, *n2Var);
    if (pdf2 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf2->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Double CB ----------------------------------------------------//                                  
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB ---------------"<<endl;
    RooAddPdf* pdf = NULL;
    TString n="PhysBkg"+namemode+"Pdf_m";
    pdf = new RooAddPdf( n.Data(),n.Data(),*pdf1, *pdf2, *fracVar);
    if (pdf != NULL){ if (debug == true) cout<<"Create doubleCB PDF: "<<pdf->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
 
    return pdf;
 }

  //===============================================================================
  // Background model for Bs->DsPi mass fitter.  
  //===============================================================================
  
  RooAbsPdf* buildBsDsPi_sim( RooRealVar& mass,
			      RooWorkspace* work,
			      RooRealVar& nCombBkgEvts,
			      RooRealVar& nBd2DPiEvts,
			      RooRealVar& nBs2DsDsstPiRhoEvts,
			      RooRealVar& g1_f1,
			      RooRealVar& g1_f2,
			      RooRealVar& nLb2LcPiEvts,
			      RooRealVar& nBdDsPi,
			      RooAbsPdf* pdf_BdDsPi,
			      RooRealVar& nBdDsstPi,
			      RooRealVar& nBd2DRhoEvts,
			      RooRealVar& nBd2DstPiEvts,
			      TString &sam,
			      TString &samplemode,
			      bool toys,
			      bool debug
			      ){
    if (debug == true)
      {
	cout<<"------------------------------------"<<endl;
	cout<<"=====> Build background model BsDsPi"<<endl;
	cout<<"------------------------------------"<<endl;
      }
    // ------------------------------------------ Read BdDsPi ----------------------------------------------------//
    if (debug == true){
      cout<<"-------------------------- Read BdDsPi -------------------------------"<<endl;
      if( pdf_BdDsPi != NULL ) { cout<<"Read "<<pdf_BdDsPi->GetName()<<endl;} else {cout<<"Cannot read BdDsPi pdf"<<endl; return NULL;}
    }
    // -------------------------------- Create Combinatorial Background --------------------------------------------//
    if (debug == true) cout<<"---------------  Create combinatorial background PDF -----------------"<<endl;

    Double_t slope;
 
    if ( samplemode.Contains("kkpi") == true ) {
      slope =-1.9102*pow(10,-3);
      //for toys
      if (toys) slope =-1.9977*pow(10,-3);
    }
    else if ( samplemode.Contains("kpipi") == true ){
      slope =-1.3452*pow(10,-3);
    }
    else {
      slope =-1.2634*pow(10,-3);
    }
   
    RooRealVar* pdf_combBkg_slope = NULL;
    TString name="CombBkgPDF_slope_"+samplemode;
    pdf_combBkg_slope = new RooRealVar( name.Data(), name.Data(),
					slope);
    RooExponential* pdf_combBkg = NULL;
    name="CombBkgPDF_m_"+samplemode;
    pdf_combBkg = new RooExponential( name.Data(), "Combinatorial background PDF in mass",
				      mass, *pdf_combBkg_slope );

    if( pdf_combBkg_slope != NULL && pdf_combBkg != NULL ){ if (debug == true) cout<<"Create "<<pdf_combBkg->GetName()<<endl; }
    else { if (debug == true) cout<<"Cannot create combinatorial background pdf"<<endl;}


    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;

    RooKeysPdf* pdf_Bd2DPi = NULL;
    name = "PhysBkgBd2DPiPdf_m_"+sam+"_kpipi";
    pdf_Bd2DPi = (RooKeysPdf*)work->pdf(name.Data());
    if( pdf_Bd2DPi != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi->GetName()<<endl;} else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

    RooKeysPdf* pdf_Bs2DsRho = NULL;
    name = "PhysBkgBs2DsRhoPdf_m_both";
    pdf_Bs2DsRho = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsRho != NULL ){ cout<<"Read "<<pdf_Bs2DsRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    
    RooKeysPdf* pdf_Bs2DsstRho = NULL;
    name = "PhysBkgBs2DsstRhoPdf_m_both";
    pdf_Bs2DsstRho = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsstRho != NULL  ){ cout<<"Read "<<pdf_Bs2DsstRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooKeysPdf* pdf_Bs2DsstPi = NULL;
    name = "PhysBkgBs2DsstPiPdf_m_both";
    pdf_Bs2DsstPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsstPi != NULL ){ cout<<"Read "<<pdf_Bs2DsstPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }
   
    RooKeysPdf* pdf_Bd2DsstPi = NULL;
    name = "PhysBkgBd2DsstPiPdf_m_both";
    pdf_Bd2DsstPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bd2DsstPi != NULL ){ cout<<"Read "<<pdf_Bd2DsstPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }
 
    RooKeysPdf* pdf_Lb2LcPi = NULL;
    name = "PhysBkgLb2LcPiPdf_m_both";
    pdf_Lb2LcPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Lb2LcPi != NULL){ cout<<"Read "<<pdf_Lb2LcPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }
    
    RooKeysPdf* pdf_Bd2DRho = NULL;
    name = "PhysBkgBd2DRhoPdf_m_both";
    pdf_Bd2DRho = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bd2DRho != NULL ){ cout<<"Read "<<pdf_Bd2DRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooKeysPdf* pdf_Bd2DstPi = NULL;
    name = "PhysBkgBd2DstPiPdf_m_both";
    pdf_Bd2DstPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bd2DstPi != NULL){ cout<<"Read "<<pdf_Bd2DstPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    // --------------------------------- Create RooAddPdf -------------------------------------------------//

    Bool_t rec=true;
    RooAddPdf* pdf_Bs2DsDsstPiRho = NULL;
    name = "PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode;
    pdf_Bs2DsDsstPiRho = new RooAddPdf( name.Data(),
					name.Data(),
					RooArgList(*pdf_Bs2DsstPi,*pdf_Bs2DsRho,*pdf_Bs2DsstRho),
					RooArgList(g1_f1,g1_f2), rec
					);

   
    //----------------------------------- Create Extended model ----------------------------------------------//
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Extended model ---------------"<<endl;
    
    RooExtendPdf* epdf_combBkg   = NULL;
    name = "CombBkgEPDF_m_"+samplemode;
    epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg  , nCombBkgEvts   );
    if (debug == true) { if( epdf_combBkg != NULL ){ cout<<"Create extended "<<epdf_combBkg->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}

    RooExtendPdf* epdf_Bd2DPi    = NULL;
    name = "Bd2DPiEPDF_m_"+samplemode;
    epdf_Bd2DPi = new RooExtendPdf( name.Data(),pdf_Bd2DPi->GetTitle(), *pdf_Bd2DPi, nBd2DPiEvts);
    if (debug == true){ if( epdf_Bd2DPi != NULL ){ cout<<"Create extended "<<epdf_Bd2DPi->GetName()<<endl;} 
      else { cout<<"Cannot create extendend PDF"<<endl;} }
    
    RooExtendPdf* epdf_BdDsPi = NULL;
    name = "Bd2DsPiEPDF_m_"+samplemode;
    epdf_BdDsPi = new RooExtendPdf(name.Data() , pdf_BdDsPi->GetTitle(), *pdf_BdDsPi, nBdDsPi );
    if (debug == true){ if( epdf_BdDsPi != NULL ){ cout<<"Create extended "<<epdf_BdDsPi->GetName()<<endl;} 
      else { cout<<"Cannot create extendend PDF"<<endl;} }

    RooExtendPdf* epdf_Bd2DsstPi = NULL;
    name = "Bd2DsstPiEPDF_m_"+samplemode;
    epdf_Bd2DsstPi = new RooExtendPdf(name.Data() , pdf_Bd2DsstPi->GetTitle(), *pdf_Bd2DsstPi, nBdDsstPi );
    if (debug == true){ if( epdf_Bd2DsstPi != NULL ){ cout<<"Create extended "<<epdf_Bd2DsstPi->GetName()<<endl;} 
      else { cout<<"Cannot create extendend PDF"<<endl;}}

    RooExtendPdf* epdf_Lb2LcPi = NULL;
    name = "Lb2LcPiEPDF_m_"+samplemode;
    epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi->GetTitle(), *pdf_Lb2LcPi, nLb2LcPiEvts );
    if (debug == true){ if( epdf_Lb2LcPi != NULL ){ cout<<"Create extended "<<epdf_Lb2LcPi->GetName()<<endl;} 
      else { cout<<"Cannot create extendend PDF"<<endl;}}

    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho-> GetTitle(), *pdf_Bs2DsDsstPiRho  , nBs2DsDsstPiRhoEvts);
    if (debug == true){ if( epdf_Bs2DsDsstPiRho != NULL ){ cout<<"Create extended "<<epdf_Bs2DsDsstPiRho->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}

    RooExtendPdf* epdf_Bd2DstPi = NULL;
    name = "Bd2DstPiEPDF_m_"+samplemode;
    epdf_Bd2DstPi = new RooExtendPdf( name.Data() , pdf_Bd2DstPi-> GetTitle(), *pdf_Bd2DstPi  , nBd2DstPiEvts );
    if (debug == true){ if( epdf_Bd2DstPi != NULL ){ cout<<"Create extended "<<epdf_Bd2DstPi->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}

    RooExtendPdf* epdf_Bd2DRho = NULL;
    name = "Bd2DRhoEPDF_m_"+samplemode;
    epdf_Bd2DRho= new RooExtendPdf( name.Data() , pdf_Bd2DRho-> GetTitle(), *pdf_Bd2DRho  , nBd2DRhoEvts );
    if (debug == true){ if( epdf_Bd2DRho != NULL ){ cout<<"Create extended "<<epdf_Bd2DRho->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}
    
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(),
                                RooArgList(*epdf_combBkg,
                                           *epdf_Bd2DPi,
                                           *epdf_Bs2DsDsstPiRho,
                                           *epdf_Lb2LcPi,
					   *epdf_Bd2DstPi,
					   *epdf_Bd2DRho,
					   *epdf_Bd2DsstPi,
                                           *epdf_BdDsPi));/*,
                                RooArgList( nCombBkgEvts,nBd2DPiEvts,nBs2DsDsstPiRhoEvts,nLb2LcPiEvts,
                                            nBd2DstPiEvts,nBd2DRhoEvts,nBdDsstPi,nBdDsPi));
    RooExtendPdf* epdf_totBkg = NULL;
    name = "TotBkgEPDF_m_"+samplemode;
    epdf_totBkg = new RooExtendPdf(name.Data() , pdf_totBkg-> GetTitle(),*pdf_totBkg, N_Bkg_Tot);*/
  
    if (debug == true)
      {
	cout<<endl;
	if( pdf_totBkg != NULL ){ cout<<" ------------- CREATED TOTAL BACKGROUND PDF: SUCCESFULL------------"<<endl; }
	else { cout<<" ---------- CREATED TOTAL BACKGROUND PDF: FAILED ----------------"<<endl;}
      }
    return pdf_totBkg;
  }

  //===============================================================================
  // Background model for Bs->DsK mass fitter.
  //===============================================================================

  RooAbsPdf* buildBsDsK_sim(RooRealVar& mass,
			    RooWorkspace* work,
			    RooAddPdf* pdf_Bd2DsK,
			    RooRealVar& nCombBkgEvts,
			    RooRealVar& nBs2DsDsstPiRhoEvts,
			    //RooFormulaVar& nBs2DsDsstPiRhoEvts,
			    RooRealVar& nBs2DsDssKKstEvts,
			    RooRealVar& nLb2DsDsstpEvts,
			    //RooFormulaVar& nBd2DKEvts,
			    RooRealVar& nBd2DKEvts,
			    RooRealVar& nLb2LcKEvts,
			    RooRealVar& g1_f1,
			    RooRealVar& g1_f2,
			    RooRealVar& g1_f3,
			    RooRealVar& g2_f1,
			    RooRealVar& g2_f2,
			    RooRealVar& g2_f3,
			    RooRealVar& g3_f1,
                            TString& /*sam*/,
			    TString &samplemode,bool toys, 
			    bool debug){


    if (debug == true)
      {
	cout<<"--------------------------------------------------------"<<endl;
	cout<<"=====> Build background model BsDsK for simultaneous fit"<<endl;
	cout<<"--------------------------------------------------------"<<endl;
      }
    // ------------------------------------------ Read BdDsK ----------------------------------------------------//
    if (debug == true)
      {
	cout<<"-------------------------- Read BdDsK -------------------------------"<<endl;
	if( pdf_Bd2DsK != NULL ) { cout<<"Read "<<pdf_Bd2DsK->GetName()<<endl;} else {cout<<"Cannot read BdDsK pdf"<<endl; return NULL;}
      }

    // -------------------------------- Create Combinatorial Background --------------------------------------------//                             
    if (debug == true) { cout<<"---------------  Create combinatorial background PDF -----------------"<<endl; }

    Double_t slope;
    if ( samplemode.Contains("kkpi") == true ) {
	slope = -1.5808*pow(10,-3);
    if (toys) slope = -0.001;
    }
    else if ( samplemode.Contains("kpipi") == true ){
	slope  = -1.0888*pow(10,-3);
    }
    else {
	slope = -9.9008*pow(10,-4);
    }

    
    RooRealVar* pdf_combBkg_slope = NULL;
    TString name="CombBkgPDF_slope_"+samplemode;
    pdf_combBkg_slope = new RooRealVar( name.Data(), name.Data(),  slope);
    
    RooExponential* pdf_combBkg = NULL;
    name="CombBkgPDF_m_"+samplemode;
    pdf_combBkg = new RooExponential( name.Data(), "Combinatorial background PDF in mass",
					mass, *pdf_combBkg_slope );
    if (debug == true) {
      if( pdf_combBkg_slope != NULL && pdf_combBkg != NULL ){ cout<<"Create "<<pdf_combBkg->GetName()<<endl; }
      else { cout<<"Cannot create combinatorial background pdf"<<endl;}
    }
    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//                                 
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;

    RooKeysPdf* pdf_Bd2DK = NULL;
    name = "PhysBkgBd2DKPdf_m_both";
    pdf_Bd2DK = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true) { if( pdf_Bd2DK != NULL ){ cout<<"Read "<<pdf_Bd2DK->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }
	
    RooKeysPdf* pdf_Bs2DsPi = NULL;
    name = "PhysBkgBsDsPi_m_"+samplemode;
    pdf_Bs2DsPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsPi != NULL ){ cout<<"Read "<<pdf_Bs2DsPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooKeysPdf* pdf_Bs2DsRho = NULL;
    name = "PhysBkgBs2DsRhoPdf_m_both";
    pdf_Bs2DsRho = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true) { if( pdf_Bs2DsRho != NULL ){ cout<<"Read "<<pdf_Bs2DsRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

    RooKeysPdf* pdf_Bs2DsKst = NULL;
    name = "PhysBkgBs2DsKstPdf_m_both";
    pdf_Bs2DsKst = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsKst != NULL ){ cout<<"Read "<<pdf_Bs2DsKst->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    
    RooKeysPdf* pdf_Bs2DsstPi = NULL;
    name = "PhysBkgBs2DsstPiPdf_m_both";
    pdf_Bs2DsstPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true) { if( pdf_Bs2DsstPi != NULL ){ cout<<"Read "<<pdf_Bs2DsstPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    
    RooKeysPdf* pdf_Bs2DsstK = NULL;
    name = "PhysBkgBs2DsstKPdf_m_both";
    pdf_Bs2DsstK = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf_Bs2DsstK != NULL ){ cout<<"Read "<<pdf_Bs2DsstK->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

    RooKeysPdf* pdf_Lb2DsstP = NULL;
    name = "PhysBkgLb2DsstpPdf_m_both";
    pdf_Lb2DsstP = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf_Lb2DsstP != NULL ){ cout<<"Read "<<pdf_Lb2DsstP->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

    RooKeysPdf* pdf_Lb2DsP = NULL;
    name = "PhysBkgLb2DspPdf_m_both";
    pdf_Lb2DsP = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Lb2DsP != NULL ){ cout<<"Read "<<pdf_Lb2DsP->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    
    RooKeysPdf* pdf_Lb2LcK = NULL;
    name = "PhysBkgLb2LcKPdf_m_both";
    pdf_Lb2LcK = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Lb2LcK != NULL ){ cout<<"Read "<<pdf_Lb2LcK->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    
    RooKeysPdf* pdf_Bs2DsstRho = NULL;
    name = "PhysBkgBs2DsstRhoPdf_m_both";
    pdf_Bs2DsstRho = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf_Bs2DsstRho != NULL ){ cout<<"Read "<<pdf_Bs2DsstRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

    RooKeysPdf* pdf_Bs2DsstKst = NULL;
    name = "PhysBkgBs2DsstKstPdf_m_both";
    pdf_Bs2DsstKst = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsstKst != NULL ){ cout<<"Read "<<pdf_Bs2DsstKst->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    
    // --------------------------------- Create Groups -------------------------------------------------//
    if (debug == true)
      {
	cout<<endl;
	cout<<"---------------  Create Groups -----------------"<<endl;
	
	cout<<"---------------  Group 1 -----------------"<<endl;
	cout<<"Bd->DsK"<<endl;
	cout<<"Bs->Ds*K"<<endl;
	cout<<"Bs->DsK*"<<endl;
	cout<<"Bs->Ds*K*"<<endl;
      }
    Bool_t rec=true; //recursive build 
    
    RooAddPdf* pdf_Bs2DsDsstKKst = NULL;
    name = "PhysBkgBs2DsDsstKKstPdf_m_"+samplemode;
	
    pdf_Bs2DsDsstKKst = new RooAddPdf( name.Data(),
				       name.Data(),
				       RooArgList(*pdf_Bd2DsK, *pdf_Bs2DsKst,*pdf_Bs2DsstK,*pdf_Bs2DsstKst),
				       RooArgList(g1_f1,g1_f2,g1_f3), rec
				       );

    if (debug == true){ 
      if (pdf_Bs2DsDsstKKst != NULL)
	{ cout<<"Create doubleCB PDF: "<<pdf_Bs2DsDsstKKst->GetName()<<endl;} 
      else 
	{cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
      cout<<"---------------  Group 2 -----------------"<<endl;
      cout<<"Bs->DsPi"<<endl;
      cout<<"Bs->Ds*Pi"<<endl;
      cout<<"Bs->DsRho"<<endl;
      cout<<"Bs->Ds*Rho"<<endl;
    }
    RooAddPdf* pdf_Bs2DsDsstPiRho = NULL;
    name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode;
    pdf_Bs2DsDsstPiRho = new RooAddPdf( name.Data(),
					name.Data(),
					RooArgList(*pdf_Bs2DsPi, *pdf_Bs2DsstPi,*pdf_Bs2DsRho,*pdf_Bs2DsstRho),
					RooArgList(g2_f1,g2_f2,g2_f3)); //, rec
    
    if (debug == true)
      {
	if (pdf_Bs2DsDsstPiRho != NULL)
	  { cout<<"Create doubleCB PDF: "<<pdf_Bs2DsDsstPiRho->GetName()<<endl;}
	else
	  {cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
    
	cout<<"---------------  Group 3 -----------------"<<endl;
	cout<<"Lb->Dsp"<<endl;
	cout<<"Lb->Ds*p"<<endl;
      }
    
    RooAddPdf* pdf_Lb2DsDsstP = NULL;
    name = "PhysBkgLb2DsDsstPPdf_m_"+samplemode;
    pdf_Lb2DsDsstP = new RooAddPdf( name.Data(),name.Data(),*pdf_Lb2DsP, *pdf_Lb2DsstP, g3_f1);
    
    if (debug == true)
      {
	if (pdf_Lb2DsDsstP != NULL)
	  { cout<<"Create doubleCB PDF: "<<pdf_Lb2DsDsstP->GetName()<<endl;} 
	else 
	  {cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
	//----------------------------------- Create Extended model ----------------------------------------------//                             
	cout<<endl;
	cout<<"--------------- Create Extended model ---------------"<<endl;
      }
    RooExtendPdf* epdf_combBkg   = NULL;
    name = "CombBkgEPDF_m_"+samplemode;
    epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg  , nCombBkgEvts   );
    if (debug == true){ if( epdf_combBkg != NULL ){ cout<<"Create extended "<<epdf_combBkg->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}
    
    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho-> GetTitle(), *pdf_Bs2DsDsstPiRho  , nBs2DsDsstPiRhoEvts   );
    if (debug == true){ if( epdf_Bs2DsDsstPiRho != NULL ){ cout<<"Create extended "<<epdf_Bs2DsDsstPiRho->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}

    RooExtendPdf* epdf_Bs2DsDsstKKst   = NULL;
    name = "Bs2DsDsstKKstEPDF_m_"+samplemode;
    epdf_Bs2DsDsstKKst = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstKKst   -> GetTitle(), *pdf_Bs2DsDsstKKst  , nBs2DsDssKKstEvts   );
    if (debug == true){ if( epdf_Bs2DsDsstKKst != NULL ){ cout<<"Create extended "<<epdf_Bs2DsDsstKKst->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}

    RooExtendPdf* epdf_Lb2DsDsstP   = NULL;
    name = "Lb2DsDsstPEPDF_m_"+samplemode;
    epdf_Lb2DsDsstP = new RooExtendPdf( name.Data() , pdf_Lb2DsDsstP   -> GetTitle(), *pdf_Lb2DsDsstP  , nLb2DsDsstpEvts   );
    if (debug == true) {if( epdf_Lb2DsDsstP != NULL ){ cout<<"Create extended "<<epdf_Lb2DsDsstP->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}

    RooExtendPdf* epdf_Bd2DK = NULL;
    name = "Bd2DKEPDF_m_"+samplemode;
    epdf_Bd2DK = new RooExtendPdf(name.Data() , pdf_Bd2DK->GetTitle(), *pdf_Bd2DK, nBd2DKEvts );
    if (debug == true) {if( epdf_Bd2DK != NULL ){ cout<<"Create extended "<<epdf_Bd2DK->GetName()<<endl;} else { cout<<"Cannot create extendend PDF"<<endl;}}
    
    RooExtendPdf* epdf_Lb2LcK = NULL;
    name = "Lb2LcKEPDF_m_"+samplemode;
    epdf_Lb2LcK = new RooExtendPdf(name.Data() , pdf_Lb2LcK->GetTitle(), *pdf_Lb2LcK, nLb2LcKEvts );
    if (debug == true) {if( epdf_Lb2LcK != NULL ){ cout<<"Create extended "<<epdf_Lb2LcK->GetName()<<endl;} 
      else { cout<<"Cannot create extendend PDF"<<endl;}}
    
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(),
				RooArgList(*epdf_combBkg,
					   *epdf_Bs2DsDsstPiRho,
					   *epdf_Bs2DsDsstKKst,
					   *epdf_Lb2DsDsstP,
					   *epdf_Bd2DK,
					   *epdf_Lb2LcK));
    if (debug == true) 
      {
	cout<<endl;
	if( pdf_totBkg != NULL ){ cout<<" ------------- CREATED TOTAL BACKGROUND PDF: SUCCESFULL------------"<<endl; }
	else { cout<<" ---------- CREATED TOTAL BACKGROUND PDF: FAILED ----------------"<<endl;}
      }
    return pdf_totBkg;
    	
  }

  //===============================================================================
  // Load RooKeysPdf from workspace.
  //===============================================================================

  RooKeysPdf* GetRooKeysPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug) {

    RooKeysPdf* pdf = NULL;
    pdf = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf != NULL ){ cout<<"Read "<<pdf->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf;

  }

  //===============================================================================
  // Load RooHistPdf from workspace.
  //===============================================================================

  RooHistPdf* GetRooHistPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug) {

    RooHistPdf* pdf = NULL;
    pdf = (RooHistPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf != NULL ){ cout<<"Read "<<pdf->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf;

  }




}
