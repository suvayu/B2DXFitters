

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
#include "RooProdPdf.h"
#include "TFile.h"
#include "TTree.h"
#include "RooDataSet.h"
#include "RooArgSet.h"
#include "RooHistPdf.h"
#include <string>
#include <vector>
#include <fstream>


#include "B2DXFitters/Bs2Dsh2011TDAnaModels.h"
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/RooCruijff.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"

using namespace std;
using namespace GeneralUtils;

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
    alpha1Var = new RooRealVar( Form( "DblCBPDF_alpha1_%s_%s", bName, prefix ), Form( "'%s' %s DblCB PDF in %s - alpha1", prefix, bName, obs.GetName() ), alpha1);
    if (alpha1Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<alpha1Var->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}
    
    RooRealVar* alpha2Var = NULL;
    alpha2Var = new RooRealVar( Form( "DblCBPDF_alpha2_%s_%s", bName, prefix ),Form( "'%s' %s DblCB PDF in %s - alpha2", prefix, bName, obs.GetName() ),alpha2);
    if (alpha2Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<alpha2Var->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}


    RooRealVar* n1Var = NULL;
    n1Var =  new RooRealVar( Form( "DblCBPDF_n1_%s_%s", bName, prefix ), Form( "'%s' %s DblCB PDF in %s - n1", prefix, bName, obs.GetName() ), n1);
    if (n1Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<n1Var->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    RooRealVar* n2Var = NULL; 
    n2Var = new RooRealVar( Form("DblCBPDF_n2_%s_%s", bName, prefix ),Form( "'%s' %s DblCB PDF in %s - n2",prefix, bName, obs.GetName() ), n2);
    if (n2Var != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<n2Var->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    RooRealVar* fracVar = NULL;
    fracVar = new RooRealVar( Form( "DblCBPDF_frac_%s_%s", bName, prefix ), Form( "'%s' %s DblCB PDF in %s - frac", prefix, bName, obs.GetName() ), frac);
    if (fracVar != NULL){ if (debug == true) cout<<"Create RooRealVar: "<<fracVar->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create RooRealVar"<<endl; return NULL;}

    // ------------------------------------------ Create Single CB ----------------------------------------------------//
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Signle CB ---------------"<<endl;
    RooCBShape* pdf1 = NULL; 
    pdf1 = new RooCBShape( Form( "DblCBPDF_CB1_%s_%s", bName, prefix ), Form( "'%s' %s CB1 PDF in %s", prefix, bName, obs.GetName() ),
			   obs,meanVar, sigma1Var, *alpha1Var, *n1Var);
    if (pdf1 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf1->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    RooCBShape* pdf2 = NULL;
    pdf2 = new RooCBShape( Form( "DblCBPDF_CB2_%s_%s", bName, prefix ),Form( "'%s' %s CB2 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,meanVar, sigma2Var, *alpha2Var, *n2Var);
    if (pdf2 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf2->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Double CB ----------------------------------------------------// 
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblCBPDF_%s_%s", bName, prefix ),Form( "'%s' %s DbleCB PDF in %s", prefix, bName, obs.GetName() ),
                                    *pdf1, *pdf2, *fracVar);
    if (pdf != NULL){ if (debug == true) cout<<"Create doubleCB PDF: "<<pdf->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
    
    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//

    RooExtendPdf* epdf = NULL;
    epdf = new RooExtendPdf( Form( "SigEPDF_%s", prefix ),Form( "SigEPDF_%s", prefix ),*pdf, nEvents);
    if( epdf != NULL) { if (debug == true) cout<<"Create extend signal model "<<epdf->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create extend signal model "<<endl; return NULL; }
    return pdf;
    
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
    pdf1 = new RooCBShape( Form( "DblCBPDF%s%s_CB1", bName, prefix ), Form( "'%s' %s CB1 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,mean, sigma1, alpha1, n1);
    if (pdf1 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf1->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    RooCBShape* pdf2 = NULL;
    pdf2 = new RooCBShape( Form( "DblCBPDF%s%s_CB2", bName, prefix ),Form( "'%s' %s CB2 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,mean, sigma2, alpha2, n2);
    if (pdf2 != NULL){ if (debug == true) cout<<"Create CB PDF: "<<pdf2->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create CB PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Double CB ----------------------------------------------------//
    
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblCBPDF%s%s", bName, prefix ),Form( "'%s' %s DbleCB PDF in %s", prefix, bName, obs.GetName() ),
			 *pdf1, *pdf2, frac);
    if (pdf != NULL){ if (debug == true) cout<<"Create doubleCB PDF: "<<pdf->GetName()<<endl;} 
    else {if (debug == true) cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//
    RooRealVar nE = nEvents;
    return pdf; 

    /*
    RooExtendPdf* epdf = NULL;
    epdf = new RooExtendPdf( Form( "SigEPDF_%s", prefix ),Form( "SigEPDF_%s", prefix ),*pdf, nEvents);
    
    if( epdf != NULL) { if (debug == true) cout<<"Create extend signal model "<<epdf->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create extend signal model "<<endl; return NULL;}

    return epdf;
    */
  }

  //===============================================================================
  // Double crystal ball function where all parameters are RooRealVar
  //===============================================================================

  RooAbsPdf* buildDoubleCBPDF_sim( RooAbsReal& obs,
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

    RooRealVar nE = nEvents;
    return pdf;
  
  }

  //===============================================================================
  // Double gaussian function where all parameters are RooRealVar
  //===============================================================================

  RooAbsPdf* buildDoubleGEPDF_sim( RooAbsReal& obs,
				   RooRealVar& mean,
				   RooRealVar& sigma1,
				   RooRealVar& sigma2,
				   RooRealVar& frac,
				   RooRealVar& nEvents,
				   const char* prefix,
				   const char* bName,
				   bool extendend, 
				   bool debug){

    if (debug == true)
      {
	cout<<"-------------------------------------------------------"<<endl;
        cout<<"=====> Build signal double Gaussian model for sim fit    "<<endl;
        cout<<"-------------------------------------------------------"<<endl;
      }
    TString name;

    // ------------------------------------------ Create Single CB ----------------------------------------------------//
    if (debug == true)
      {
        cout<<endl;
        cout<<"--------------- Create Signle CB ---------------"<<endl;
      }
    RooGaussian* pdf1 = NULL;
    pdf1 = new RooGaussian( Form( "DblGPDF%s_G1", prefix ), Form( "'%s' %s G1 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,mean, sigma1);
    if (pdf1 != NULL){ if (debug == true) cout<<"Create Gaussian PDF: "<<pdf1->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot create Gaussian PDF"<<endl; return NULL;}

    RooGaussian* pdf2 = NULL;
    pdf2 = new RooGaussian( Form( "DblGPDF%s_G2", prefix ),Form( "'%s' %s G2 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,mean, sigma2);
    if (pdf2 != NULL){ if (debug == true) cout<<"Create Gaussian PDF: "<<pdf2->GetName()<<endl;}
    else {if (debug == true) cout<<"Cannot create Gaussian PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Double CB ----------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblGPDF%s", prefix ),Form( "'%s' %s DbleGaussian PDF in %s", prefix, bName, obs.GetName() ),
                         *pdf1, *pdf2, frac);
    if (pdf != NULL){ if (debug == true) cout<<"Create doubleGaussian PDF: "<<pdf->GetName()<<endl;}
    else {if (debug == true) cout<<"Cannot create doubleGaussian PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//
    
    RooExtendPdf* epdf = NULL;
    
    if (extendend == true)
      {
	epdf = new RooExtendPdf( Form( "SigGEPDF_%s", prefix ),Form( "SigGEPDF_%s", prefix ),*pdf, nEvents);
	
	if( epdf != NULL) { if (debug == true) cout<<"Create extend signal model "<<epdf->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot create extend signal model "<<endl; return NULL;}
	return epdf;
      }
    else
      {
	return pdf;
      }

   
  }

  //===============================================================================
  // Double gaussian function where all parameters are RooRealVar
  //===============================================================================

  RooAbsPdf* buildDoubleGEPDF_sim( RooAbsReal& obs,
                                   RooRealVar& mean,
                                   RooRealVar& sigma1,
                                   RooRealVar& sigma2,
                                   RooRealVar& frac,
                                   RooFormulaVar& nEvents,
                                   const char* prefix,
                                   const char* bName,
                                   bool extendend,
                                   bool debug){

    if (debug == true)
      {
        cout<<"-------------------------------------------------------"<<endl;
        cout<<"=====> Build signal double Gaussian model for sim fit    "<<endl;
        cout<<"-------------------------------------------------------"<<endl;
      }
    TString name;

    // ------------------------------------------ Create Single CB ----------------------------------------------------//
    if (debug == true)
      {
        cout<<endl;
        cout<<"--------------- Create Signle CB ---------------"<<endl;
      }
    RooGaussian* pdf1 = NULL;
    pdf1 = new RooGaussian( Form( "DblGPDF%s_G1", prefix ), Form( "'%s' %s G1 PDF in %s", prefix, bName, obs.GetName() ),
			    obs,mean, sigma1);
    if (pdf1 != NULL){ if (debug == true) cout<<"Create Gaussian PDF: "<<pdf1->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot create Gaussian PDF"<<endl; return NULL;}

    RooGaussian* pdf2 = NULL;
    pdf2 = new RooGaussian( Form( "DblGPDF%s_G2", prefix ),Form( "'%s' %s G2 PDF in %s", prefix, bName, obs.GetName() ),
			    obs,mean, sigma2);
    if (pdf2 != NULL){ if (debug == true) cout<<"Create Gaussian PDF: "<<pdf2->GetName()<<endl;}
    else {if (debug == true) cout<<"Cannot create Gaussian PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Double CB ----------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblGPDF%s", prefix ),Form( "'%s' %s DbleGaussian PDF in %s", prefix, bName, obs.GetName() ),
                         *pdf1, *pdf2, frac);
    if (pdf != NULL){ if (debug == true) cout<<"Create doubleGaussian PDF: "<<pdf->GetName()<<endl;}
    else {if (debug == true) cout<<"Cannot create doubleGaussian PDF"<<endl; return NULL;}

    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//

    RooExtendPdf* epdf = NULL;

    if (extendend == true)
      {
        epdf = new RooExtendPdf( Form( "SigGEPDF_%s", prefix ),Form( "SigGEPDF_%s", prefix ),*pdf, nEvents);

        if( epdf != NULL) { if (debug == true) cout<<"Create extend signal model "<<epdf->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot create extend signal model "<<endl; return NULL;}
        return epdf;
      }
    else
      {
        return pdf;
      }
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
			      RooRealVar& nBs2DsKEvts,
			      RooRealVar& cB1Var,
			      RooRealVar& cB2Var,
			      RooRealVar& fracComb,
			      TString &samplemode,
			      RooRealVar& lumRatio,
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

    TString Sam;
    if (samplemode.Contains("down")) { Sam = "Down";} else { Sam = "Up"; }
    TString sam;
    bool merge = false;
    if (samplemode.Contains("down") == true )
      {
        sam = "down";
      }
    else if (samplemode.Contains("up") == true )
      {
        sam = "up";
      }
    else
      {
        sam == "both";
	merge = true;
      }

    TString Mode;
    if ( samplemode.Contains("kkpi") == true ) {
      Mode = "kkpi";
    }
    else if ( samplemode.Contains("kpipi") == true ){
      Mode = "kpipi";
    }
    else if(samplemode.Contains("pipipi") == true ){
      Mode = "pipipi";
    }
    else if(samplemode.Contains("nonres") == true ){
      Mode = "nonres";
    }
    else if(samplemode.Contains("phipi") == true ){
      Mode = "phipi";
    }
    else if(samplemode.Contains("kstk") == true ){
      Mode = "kstk";
    }

    RooExponential* pdf_combBkg1 = NULL;
    TString name="CombBkgPDF1_m_"+Mode;
    pdf_combBkg1 = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, cB1Var );

    RooExponential* pdf_combBkg2 = NULL;
    name="CombBkgPDF2_m_"+Mode;
    pdf_combBkg2 = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, cB2Var );


    RooAddPdf* pdf_combBkg = NULL;
    name="CombBkgPDF_"+samplemode;
    pdf_combBkg = new RooAddPdf( name.Data(), name.Data(),  RooArgList(*pdf_combBkg1,*pdf_combBkg2), fracComb);
    if( pdf_combBkg != NULL ){ if (debug == true) cout<<"Create "<<pdf_combBkg->GetName()<<endl; }
    else { if (debug == true) cout<<"Cannot create combinatorial background pdf"<<endl;}


    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;

    RooAbsPdf* pdf_Bd2DPi = NULL;
    RooKeysPdf* pdf_Bd2DPi1 = NULL;
    RooKeysPdf* pdf_Bd2DPi2 = NULL;

    if ( pdf_Bd2DPi ) {}
    if ( pdf_Bd2DPi1 ) {}
    if ( pdf_Bd2DPi2 ) {}

    if (merge == true)
      {
        name = "PhysBkgBd2DPiPdf_m_down_kpipi";
	pdf_Bd2DPi1 = (RooKeysPdf*)work->pdf(name.Data());
        if( pdf_Bd2DPi1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi1->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "PhysBkgBd2DPiPdf_m_up_kpipi";
        pdf_Bd2DPi2 = (RooKeysPdf*)work->pdf(name.Data());
        if( pdf_Bd2DPi2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

        name = "PhysBkgBd2DPiPdf_m_both_kpipi";
        pdf_Bd2DPi = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bd2DPi2,*pdf_Bd2DPi1), RooArgList(lumRatio));
        if( pdf_Bd2DPi != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    else
      {
        name = "PhysBkgBd2DPiPdf_m_"+sam+"_kpipi";
        pdf_Bd2DPi = (RooKeysPdf*)work->pdf(name.Data());
	if( pdf_Bd2DPi != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    
    RooKeysPdf* pdf_Bs2DsRho = NULL;
    name = "PhysBkgBs2DsRhoPdf_m_both";
    pdf_Bs2DsRho = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsRho != NULL ){ cout<<"Read "<<pdf_Bs2DsRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

    RooKeysPdf* pdf_Bs2DsK = NULL;
    name = "PhysBkgBs2DsKPdf_m_both";
    pdf_Bs2DsK = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsK != NULL){ cout<<"Read "<<pdf_Bs2DsK->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }
    
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
    
    RooExtendPdf* epdf_Bs2DsK = NULL;
    name = "Bs2DsKEPDF_m_"+samplemode;
    epdf_Bs2DsK = new RooExtendPdf(name.Data() , pdf_Bs2DsK->GetTitle(), *pdf_Bs2DsK, nBs2DsKEvts );
    if (debug == true){ if( epdf_Bs2DsK != NULL ){ cout<<"Create extended "<<epdf_Bs2DsK->GetName()<<endl;}
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
                                           *epdf_BdDsPi,
					   *epdf_Bs2DsK));/*,
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
  RooAbsPdf* buildBsDsPi_PIDK(RooAbsReal* obs,
			      Double_t c1Var,
			      Double_t c2Var,
			      Double_t f1Var,
			      Double_t f2Var,
			      Double_t sigmaVar,
			      Double_t meanVar,
			      TString& samplemode
			      )
  {

    RooRealVar *c1 = NULL;
    RooRealVar *c2 = NULL;
    RooRealVar *mean = NULL;
    RooRealVar *sigma  = NULL;
    RooRealVar *f1 = NULL;
    RooRealVar *f2 = NULL;
    TString mode;
    
    TString nameVar = "c1_"+samplemode; 
    c1 =  new RooRealVar(nameVar.Data(),"coefficient #2", c1Var, c1Var-0.5*c1Var,c1Var+0.5*c1Var);
    nameVar = "c2_"+samplemode; 
    c2 = new RooRealVar(nameVar.Data(),"coefficient #2", c2Var, c2Var-0.5*c2Var,c2Var+0.5*c2Var);
    nameVar = "mean_"+samplemode; 
    mean = new RooRealVar(nameVar.Data(), "mean", meanVar, meanVar+0.5*meanVar, meanVar-0.5*meanVar);
    nameVar = "sigma_"+samplemode; 
    sigma = new RooRealVar(nameVar.Data(),"sigma",sigmaVar, sigmaVar-0.5*sigmaVar,sigmaVar+0.5*sigmaVar);
    nameVar = "f1_"+samplemode; 
    f1 = new RooRealVar(nameVar.Data(),"signal fraction",f1Var, 0.0, 1.0);
    nameVar = "f2_"+samplemode; 
    f2  = new RooRealVar(nameVar.Data(),"signal fraction",f2Var, 0.0, 1.0 );
    

    nameVar = "PIDKbkg1_"+samplemode; 
    RooExponential* bkg1 = new  RooExponential(nameVar.Data(), "bkg p.d.f." , *obs, *c1);
    nameVar = "PIDKbkg2_"+samplemode; 
    RooExponential* bkg2 = new  RooExponential(nameVar.Data(), "bkg p.d.f." , *obs, *c2);
    nameVar = "PIDKbkg3_"+samplemode; 
    RooGaussian* bkg3 = new RooGaussian(nameVar.Data(),"signal p.d.f.",*obs, *mean, *sigma);
    nameVar = "ShapePIDK_"+samplemode; 
    RooAddPdf *bkg = new RooAddPdf(nameVar.Data(),"model",RooArgList(*bkg1,*bkg2, *bkg3),RooArgList(*f1,*f2),true);
     
    return bkg;
    
  }




  
  //===============================================================================
  // Background 2D model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf* buildBsDsPi_2D( RooAbsReal& mass,
			     RooAbsReal& massDs,
			     RooWorkspace* work,
			     RooWorkspace* workID,
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
			     RooRealVar& nBs2DsKEvts,
			     RooAbsPdf* pdf_SignalDs,
			     RooRealVar& cBVar,
			     RooRealVar& cB2Var,
			     RooRealVar& fracBsComb,
                             RooRealVar& cDVar,
                             RooRealVar& fracDsComb,
			     RooRealVar& fracPIDComb,
			     TString &samplemode,
			     RooRealVar& lumRatio,
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
      //if( pdf_BdDsPi != NULL ) { cout<<"Read "<<pdf_BdDsPi->GetName()<<endl;} else {cout<<"Cannot read BdDsPi pdf"<<endl; return NULL;}
    }
    TString name="fake_"+samplemode;
    RooRealVar fake( name.Data(), name.Data(), 0);

    TString Sam;
    if (samplemode.Contains("down")) { Sam = "Down";} else { Sam = "Up"; }
    TString sam;
    bool merge = false;
    if (samplemode.Contains("down") == true )
      {
        sam = "down";
      }
    else if (samplemode.Contains("up") == true )
      {
	sam = "up";
      }
    else
      {
        sam == "both";
	merge = true;
      }

    TString Mode;
    if ( samplemode.Contains("kkpi") == true ) {
      Mode = "kkpi";
    }
    else if ( samplemode.Contains("kpipi") == true ){
      Mode = "kpipi";
    }
    else if(samplemode.Contains("pipipi") == true ){
      Mode = "pipipi";
    }
    else if(samplemode.Contains("nonres") == true ){
      Mode = "nonres";
    }
    else if(samplemode.Contains("phipi") == true ){
      Mode = "phipi";
    }
    else if(samplemode.Contains("kstk") == true ){
      Mode = "kstk";
    }


    RooAbsPdf* pdf_BdDsPi_Ds = NULL;
    pdf_BdDsPi_Ds = pdf_SignalDs; 

    RooAbsPdf* pdf_BdDsPi_PIDK = NULL;
    RooAbsPdf* pdf_BdDsPi_PIDK1 = NULL;
    RooAbsPdf* pdf_BdDsPi_PIDK2 = NULL;

    if (pdf_BdDsPi_PIDK){}
    if (pdf_BdDsPi_PIDK1){}
    if (pdf_BdDsPi_PIDK2){}

    if (merge == true)
      {
	name = "PIDshape_BsDsPi_both_"+Mode+"_down"; //sam; 
        pdf_BdDsPi_PIDK1 = GetRooBinned1DFromWorkspace(workID, name, debug);

        name ="PIDshape_BsDsPi_both_"+Mode+"_up"; //sam;
        pdf_BdDsPi_PIDK2 = GetRooBinned1DFromWorkspace(workID, name, debug);
	
	name = "ShapePIDK_BsDsPi_both";
	pdf_BdDsPi_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_BdDsPi_PIDK2,*pdf_BdDsPi_PIDK1), RooArgList(lumRatio));
	if( pdf_BdDsPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_BdDsPi_PIDK->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

      }
    else
      {
	name = "PIDshape_BsDsPi_both_"+Mode+"_"+sam;
	pdf_BdDsPi_PIDK = GetRooBinned1DFromWorkspace(workID, name, debug);
      }

    RooProdPdf* pdf_BdDsPi_Tot = NULL;
    name="PhysBkgBd2DsPiPdf_m_"+samplemode+"_Tot";
    pdf_BdDsPi_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_BdDsPi,*pdf_BdDsPi_Ds,*pdf_BdDsPi_PIDK));

    if( pdf_BdDsPi_Tot != NULL ){ 
      if (debug == true) cout<<"Create "<<pdf_BdDsPi_Tot->GetName()<<endl;} 
    else { if (debug == true) cout<<"Cannot create PDF"<<endl;}

    RooExtendPdf* epdf_BdDsPi = NULL;
    name = "Bd2DsPiEPDF_m_"+samplemode;
    epdf_BdDsPi = new RooExtendPdf(name.Data() , pdf_BdDsPi_Ds->GetTitle(), *pdf_BdDsPi_Tot, nBdDsPi );
    if (debug == true){ if( epdf_BdDsPi != NULL ){ cout<<"Create extended "<<epdf_BdDsPi->GetName()<<endl;}
      else { cout<<"Cannot create extendend PDF"<<endl;} }

    
    // -------------------------------- Create Combinatorial Background --------------------------------------------//
   
    if (debug == true) cout<<"---------------  Create combinatorial background PDF -----------------"<<endl;

    RooExponential* pdf_combBkg1 = NULL;
    name="CombBkgPDF1_m_"+Mode;
    pdf_combBkg1 = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, cBVar );
    
    RooExponential* pdf_combBkg2 = NULL;
    name="CombBkgPDF2_m_"+Mode;
    pdf_combBkg2 = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, cB2Var );
    
    
    RooAddPdf* pdf_combBkg = NULL;
    name="CombBkgPDF_"+samplemode;
    pdf_combBkg = new RooAddPdf( name.Data(), name.Data(),  RooArgList(*pdf_combBkg1,*pdf_combBkg2), fracBsComb);
    //if( pdf_combBkg_slopeDs != NULL && pdf_combBkg_Ds != NULL ){ if (debug == true) cout<<"Create "<<pdf_combBkg_Ds->GetName()<<endl; }
    //else { if (debug == true) cout<<"Cannot create combinatorial background pdf"<<endl;}

    //if( pdf_combBkg2 != NULL ){ if (debug == true) cout<<"Create "<<pdf_combBkg->GetName()<<endl; }
    //else { if (debug == true) cout<<"Cannot create combinatorial background pdf"<<endl;}
    
    RooExponential* pdf_combBkg_slope_Ds = NULL;
    name="CombBkgPDF_slope_"+samplemode+"_Ds";
    pdf_combBkg_slope_Ds = new RooExponential( name.Data(), name.Data(), massDs, cDVar );

    RooAddPdf* pdf_combBkg_Ds = NULL;
    name="CombBkgPDF_"+samplemode+"_Ds";
    pdf_combBkg_Ds = new RooAddPdf( name.Data(), name.Data(),  RooArgList(*pdf_combBkg_slope_Ds,*pdf_SignalDs), fracDsComb );
    if( pdf_combBkg_slope_Ds != NULL && pdf_combBkg_Ds != NULL ){ if (debug == true) cout<<"Create "<<pdf_combBkg_Ds->GetName()<<endl; }
    else { if (debug == true) cout<<"Cannot create combinatorial background pdf"<<endl;}
        
    RooAbsPdf* pdf_combBkg_PIDK1 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK2 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK11 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK21 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK12 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK22 = NULL;

    if( pdf_combBkg_PIDK1 ) {}
    if( pdf_combBkg_PIDK2 ) {}
    if( pdf_combBkg_PIDK11 ) {}
    if( pdf_combBkg_PIDK21 ){}
    if( pdf_combBkg_PIDK12 ){}
    if( pdf_combBkg_PIDK22 ){}

    if( merge == true )
      {
	/*
	name = "ShapePIDK_Comb_down";
        pdf_combBkg_PIDK11 = (RooAddPdf*)workID->pdf(name.Data());
        if( pdf_combBkg_PIDK11 != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK11->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	*/

        name = "ShapeKPIDK_Comb_down";
        pdf_combBkg_PIDK21 = (RooAddPdf*)workID->pdf(name.Data());
        if( pdf_combBkg_PIDK21 != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK21->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	
	name = "PIDshape_Comb_down";
	pdf_combBkg_PIDK11 = GetRooBinned1DFromWorkspace(workID, name, debug);
	/*
	name = "ShapePIDK_Comb_up";
        pdf_combBkg_PIDK12 = (RooAddPdf*)workID->pdf(name.Data());
        if( pdf_combBkg_PIDK12 != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK12->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	*/
        name = "ShapeKPIDK_Comb_up";
        pdf_combBkg_PIDK22 = (RooAddPdf*)workID->pdf(name.Data());
        if( pdf_combBkg_PIDK22 != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK22->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	
	name = "PIDshape_Comb_up";
        pdf_combBkg_PIDK12 = GetRooBinned1DFromWorkspace(workID, name, debug);

	name = "ShapePIDK_Comb_both";
	pdf_combBkg_PIDK1 = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_combBkg_PIDK12,*pdf_combBkg_PIDK11), RooArgList(lumRatio));
	if( pdf_combBkg_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK1->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapeKPIDK_Comb_both";
        pdf_combBkg_PIDK2 = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_combBkg_PIDK22,*pdf_combBkg_PIDK21), RooArgList(lumRatio));
        if( pdf_combBkg_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    else
      {
	name = "ShapePIDK_Comb_"+sam;
	pdf_combBkg_PIDK1 = (RooAddPdf*)workID->pdf(name.Data());
	if( pdf_combBkg_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK1->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	/*
	name = "ShapeKPIDK_Comb_"+sam;
	pdf_combBkg_PIDK2 = (RooAddPdf*)workID->pdf(name.Data());
	if( pdf_combBkg_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK2->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	*/
	name = "PIDshape_Comb_"+sam;
        pdf_combBkg_PIDK2 = GetRooBinned1DFromWorkspace(workID, name, debug);
	
      }

    RooAddPdf* pdf_combBkg_PIDK = NULL;
    name = "ShapePIDKAll_Comb_"+sam;
    pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
				      name.Data(),
				      RooArgList(*pdf_combBkg_PIDK1,*pdf_combBkg_PIDK2), fracPIDComb);

    if( pdf_combBkg_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
    

    RooProdPdf* pdf_combBkg_Tot = NULL;
    name="CombBkgPDF_m_"+samplemode+"_Tot";
    pdf_combBkg_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_combBkg,*pdf_combBkg_Ds,*pdf_combBkg_PIDK));

    if( pdf_combBkg_Tot != NULL ){
      if (debug == true) cout<<"Read "<<pdf_combBkg_Tot->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

    RooExtendPdf* epdf_combBkg   = NULL;
    name = "CombBkgEPDF_m_"+samplemode;
    epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg_Tot  , nCombBkgEvts   );
    if (debug == true) { if( epdf_combBkg != NULL ){ cout<<"Create extended "<<epdf_combBkg->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}


    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;

    RooAbsPdf* pdf_Bd2DPi = NULL;
    RooKeysPdf* pdf_Bd2DPi1 = NULL;
    RooKeysPdf* pdf_Bd2DPi2 = NULL;

    if ( pdf_Bd2DPi ) {}
    if ( pdf_Bd2DPi1 ) {}
    if ( pdf_Bd2DPi2 ) {}

    if (merge == true)
      {
	name = "PhysBkgBd2DPiPdf_m_down_kpipi";
        pdf_Bd2DPi1 = (RooKeysPdf*)work->pdf(name.Data());
        if( pdf_Bd2DPi1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi1->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "PhysBkgBd2DPiPdf_m_up_kpipi";
        pdf_Bd2DPi2 = (RooKeysPdf*)work->pdf(name.Data());
        if( pdf_Bd2DPi2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "PhysBkgBd2DPiPdf_m_both_kpipi";
        pdf_Bd2DPi = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bd2DPi2,*pdf_Bd2DPi1), RooArgList(lumRatio));
        if( pdf_Bd2DPi != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    else
      {
	name = "PhysBkgBd2DPiPdf_m_"+sam+"_kpipi";
	pdf_Bd2DPi = (RooKeysPdf*)work->pdf(name.Data());
	if( pdf_Bd2DPi != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi->GetName()<<endl;} 
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }

    RooAbsPdf* pdf_Bd2DPi_Ds = NULL;
    RooKeysPdf* pdf_Bd2DPi_Ds1 = NULL;
    RooKeysPdf* pdf_Bd2DPi_Ds2 = NULL;

    if ( pdf_Bd2DPi_Ds ) {}
    if ( pdf_Bd2DPi_Ds1 ){}
    if ( pdf_Bd2DPi_Ds2 ) {}

    if ( merge == true)
      {
	name = "PhysBkgBd2DPiPdf_m_down_kpipi_Ds";
        pdf_Bd2DPi_Ds1 = (RooKeysPdf*)work->pdf(name.Data());
        if( pdf_Bd2DPi_Ds1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi_Ds1->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "PhysBkgBd2DPiPdf_m_up_kpipi_Ds";
        pdf_Bd2DPi_Ds2 = (RooKeysPdf*)work->pdf(name.Data());
        if( pdf_Bd2DPi_Ds2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi_Ds2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "PhysBkgBd2DPiPdf_m_both_kpipi_Ds";
        pdf_Bd2DPi_Ds = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bd2DPi_Ds2,*pdf_Bd2DPi_Ds1), RooArgList(lumRatio));
        if( pdf_Bd2DPi_Ds != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi_Ds->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

      }
    else
      {
	name = "PhysBkgBd2DPiPdf_m_"+sam+"_kpipi_Ds";
	pdf_Bd2DPi_Ds = (RooKeysPdf*)work->pdf(name.Data());
	if( pdf_Bd2DPi_Ds != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi_Ds->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    RooAbsPdf* pdf_Bd2DPi_PIDK = NULL;
    RooAbsPdf* pdf_Bd2DPi_PIDK1 = NULL;
    RooAbsPdf* pdf_Bd2DPi_PIDK2 = NULL;

    if (pdf_Bd2DPi_PIDK) {}
    if (pdf_Bd2DPi_PIDK1) {}
    if (pdf_Bd2DPi_PIDK2) {}

    if (merge == true)
      {
	/*
	name = "ShapePIDK_DPi_down"; //+"_kpipi";
        pdf_Bd2DPi_PIDK1 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bd2DPi_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi_PIDK1->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	
	name = "ShapePIDK_DPi_up"; //+"_kpipi";
        pdf_Bd2DPi_PIDK2 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bd2DPi_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi_PIDK2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	*/
	
	name ="PIDshape_DPi_down"; //sam;
        pdf_Bd2DPi_PIDK1 = GetRooBinned1DFromWorkspace(work, name, debug);
	
	name ="PIDshape_DPi_up"; //sam;
        pdf_Bd2DPi_PIDK2 = GetRooBinned1DFromWorkspace(work, name, debug);

	name = "ShapePIDK_DPi_both";
        pdf_Bd2DPi_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bd2DPi_PIDK2,*pdf_Bd2DPi_PIDK1), RooArgList(lumRatio));
        if( pdf_Bd2DPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi_PIDK->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	
      }
    else
      {
	name ="PIDshape_DPi_"+sam;
        pdf_Bd2DPi_PIDK = GetRooBinned1DFromWorkspace(workID, name, debug);

	/*
	name = "ShapePIDK_DPi_"+sam; //+"_kpipi";
	pdf_Bd2DPi_PIDK = (RooAddPdf*)work->pdf(name.Data());
	if( pdf_Bd2DPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DPi_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	*/
	}

    RooProdPdf* pdf_Bd2DPi_Tot = NULL;
    name="PhysBkgBd2DPiPdf_m_"+samplemode+"_Tot";
    pdf_Bd2DPi_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bd2DPi,*pdf_Bd2DPi_Ds, *pdf_Bd2DPi_PIDK));

    if( pdf_Bd2DPi_Tot != NULL ){
      if (debug == true) cout<<"Read "<<pdf_Bd2DPi_Tot->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

    RooExtendPdf* epdf_Bd2DPi    = NULL;
    name = "Bd2DPiEPDF_m_"+samplemode;
    epdf_Bd2DPi = new RooExtendPdf( name.Data(),pdf_Bd2DPi->GetTitle(), *pdf_Bd2DPi_Tot, nBd2DPiEvts);
    if (debug == true){ if( epdf_Bd2DPi != NULL ){ cout<<"Create extended "<<epdf_Bd2DPi->GetName()<<endl;}
      else { cout<<"Cannot create extendend PDF"<<endl;} }


    //-----------------------------------------//

    RooKeysPdf* pdf_Bs2DsRho = NULL;
    name = "PhysBkgBs2DsRhoPdf_m_both";
    pdf_Bs2DsRho = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsRho != NULL ){ cout<<"Read "<<pdf_Bs2DsRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

    RooKeysPdf* pdf_Bs2DsstRho = NULL;
    name = "PhysBkgBs2DsstRhoPdf_m_both";
    pdf_Bs2DsstRho = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsstRho != NULL  ){ cout<<"Read "<<pdf_Bs2DsstRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

    RooKeysPdf* pdf_Bs2DsstPi = NULL;
    name = "PhysBkgBs2DsstPiPdf_m_both";
    pdf_Bs2DsstPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsstPi != NULL ){ cout<<"Read "<<pdf_Bs2DsstPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooKeysPdf* pdf_Bd2DsstPi = NULL;
    name = "PhysBkgBd2DsstPiPdf_m_both";
    pdf_Bd2DsstPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bd2DsstPi != NULL ){ cout<<"Read "<<pdf_Bd2DsstPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooAbsPdf* pdf_Bd2DsstPi_Ds = NULL;
    pdf_Bd2DsstPi_Ds = pdf_SignalDs; 

    RooAddPdf* pdf_Bd2DsstPi_PIDK = NULL;
    RooAddPdf* pdf_Bd2DsstPi_PIDK1 = NULL;
    RooAddPdf* pdf_Bd2DsstPi_PIDK2 = NULL;
    
    if( pdf_Bd2DsstPi_PIDK ){}
    if( pdf_Bd2DsstPi_PIDK1 ){}
    if( pdf_Bd2DsstPi_PIDK2 ){}

    if (merge == true)
      {
	name = "ShapePIDK_Bd2DsstPi_down";
        pdf_Bd2DsstPi_PIDK1 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bd2DsstPi_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DsstPi_PIDK1->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapePIDK_Bd2DsstPi_up";
        pdf_Bd2DsstPi_PIDK2 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bd2DsstPi_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DsstPi_PIDK2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapePIDK_Bd2DsstPi_both";
        pdf_Bd2DsstPi_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bd2DsstPi_PIDK2,*pdf_Bd2DsstPi_PIDK1), RooArgList(lumRatio));
        if( pdf_Bd2DsstPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DsstPi_PIDK->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    else
      {
	name = "ShapePIDK_Bd2DsstPi_"+sam;
	pdf_Bd2DsstPi_PIDK = (RooAddPdf*)work->pdf(name.Data());
	if( pdf_Bd2DsstPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DsstPi_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    
    RooProdPdf* pdf_Bd2DsstPi_Tot = NULL;
    name="PhysBkgBd2DsstPiPdf_m_"+samplemode+"_Tot";
    pdf_Bd2DsstPi_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bd2DsstPi,*pdf_Bd2DsstPi_Ds,*pdf_Bd2DsstPi_PIDK));

    if( pdf_Bd2DsstPi_Tot != NULL ){
      if (debug == true) cout<<"Read "<<pdf_Bd2DsstPi_Tot->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

    RooExtendPdf* epdf_Bd2DsstPi = NULL;
    name = "Bd2DsstPiEPDF_m_"+samplemode;
    epdf_Bd2DsstPi = new RooExtendPdf(name.Data() , pdf_Bd2DsstPi->GetTitle(), *pdf_Bd2DsstPi_Tot, nBdDsstPi );
    if (debug == true){ if( epdf_Bd2DsstPi != NULL ){ cout<<"Create extended "<<epdf_Bd2DsstPi->GetName()<<endl;}
      else { cout<<"Cannot create extendend PDF"<<endl;}}


    //-----------------------------------------//


    RooKeysPdf* pdf_Lb2LcPi = NULL;
    name = "PhysBkgLb2LcPiPdf_m_both";
    pdf_Lb2LcPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Lb2LcPi != NULL){ cout<<"Read "<<pdf_Lb2LcPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooKeysPdf* pdf_Lb2LcPi_Ds = NULL;
    name = "PhysBkgLb2LcPiPdf_m_both_Ds";
    pdf_Lb2LcPi_Ds = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Lb2LcPi_Ds != NULL){ cout<<"Read "<<pdf_Lb2LcPi_Ds->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooAbsPdf* pdf_Lb2LcPi_PIDK = NULL;
    RooAbsPdf* pdf_Lb2LcPi_PIDK1 = NULL;
    RooAbsPdf* pdf_Lb2LcPi_PIDK2 = NULL;

    if ( pdf_Lb2LcPi_PIDK ) {}
    if ( pdf_Lb2LcPi_PIDK1 ) {}
    if ( pdf_Lb2LcPi_PIDK2 ) {}
    
    if ( merge == true)
      {
	/*
	name = "ShapePIDK_Lb2LcPi_down";
        pdf_Lb2LcPi_PIDK1 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Lb2LcPi_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2LcPi_PIDK1->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapePIDK_Lb2LcPi_up";
        pdf_Lb2LcPi_PIDK2 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Lb2LcPi_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2LcPi_PIDK2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	*/
	
	name ="ShapePIDK_Lb2LcPi_down"; //sam;
        pdf_Lb2LcPi_PIDK1 = GetRooBinned1DFromWorkspace(work, name, debug);

        name ="ShapePIDK_Lb2LcPi_up"; //sam;
        pdf_Lb2LcPi_PIDK2 = GetRooBinned1DFromWorkspace(work, name, debug);

	
	name = "ShapePIDK_Lb2LcPi_both";
        pdf_Lb2LcPi_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Lb2LcPi_PIDK2,*pdf_Lb2LcPi_PIDK1), RooArgList(lumRatio));
        if( pdf_Lb2LcPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2LcPi_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    else
      {
	name = "ShapePIDK_Lb2LcPi_"+sam;
	pdf_Lb2LcPi_PIDK = (RooAddPdf*)work->pdf(name.Data());
	if( pdf_Lb2LcPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2LcPi_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    RooProdPdf* pdf_Lb2LcPi_Tot = NULL;
    name="PhysBkgLb2LcPiPdf_m_"+samplemode+"_Tot";
    pdf_Lb2LcPi_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Lb2LcPi,*pdf_Lb2LcPi_Ds,*pdf_Lb2LcPi_PIDK));

    if( pdf_Lb2LcPi_Tot != NULL ){
      if (debug == true) cout<<"Read "<<pdf_Lb2LcPi_Tot->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
    
    RooExtendPdf* epdf_Lb2LcPi = NULL;
    name = "Lb2LcPiEPDF_m_"+samplemode;
    epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi->GetTitle(), *pdf_Lb2LcPi_Tot, nLb2LcPiEvts );
    if (debug == true){ if( epdf_Lb2LcPi != NULL ){ cout<<"Create extended "<<epdf_Lb2LcPi->GetName()<<endl;}
      else { cout<<"Cannot create extendend PDF"<<endl;}}

    //-----------------------------------------//


    RooKeysPdf* pdf_Bs2DsK = NULL;
    name = "PhysBkgBs2DsKPdf_m_both";
    pdf_Bs2DsK = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bs2DsK != NULL){ cout<<"Read "<<pdf_Bs2DsK->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooAbsPdf* pdf_Bs2DsK_Ds = NULL;
    pdf_Bs2DsK_Ds = pdf_SignalDs; 
    
    RooAddPdf* pdf_Bs2DsK_PIDK = NULL;
    RooAddPdf* pdf_Bs2DsK_PIDK1 = NULL;
    RooAddPdf* pdf_Bs2DsK_PIDK2 = NULL;

    if ( pdf_Bs2DsK_PIDK  ) {}
    if ( pdf_Bs2DsK_PIDK1 ) {}
    if ( pdf_Bs2DsK_PIDK2 ) {}

    if ( merge == true)
      {
	name = "ShapeKPIDK_Bs2DsK_down";
        pdf_Bs2DsK_PIDK1 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bs2DsK_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsK_PIDK1->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapeKPIDK_Bs2DsK_up";
        pdf_Bs2DsK_PIDK2 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bs2DsK_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsK_PIDK2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapePIDK_Bs2DsK_both";
        pdf_Bs2DsK_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsK_PIDK2,*pdf_Bs2DsK_PIDK1), RooArgList(lumRatio));
        if( pdf_Bs2DsK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsK_PIDK->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    else
      {
	name = "ShapeKPIDK_Bs2DsK_"+sam;
	pdf_Bs2DsK_PIDK = (RooAddPdf*)work->pdf(name.Data());
	if( pdf_Bs2DsK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsK_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }

    RooProdPdf* pdf_Bs2DsK_Tot = NULL;
    name="PhysBkgBs2DsKPdf_m_"+samplemode+"_Tot";
    pdf_Bs2DsK_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs2DsK,*pdf_Bs2DsK_Ds,*pdf_Bs2DsK_PIDK));

    if( pdf_Bs2DsK_Tot != NULL ){
      if (debug == true) cout<<"Read "<<pdf_Bs2DsK_Tot->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

    RooExtendPdf* epdf_Bs2DsK = NULL;
    name = "Bs2DsKEPDF_m_"+samplemode;
    epdf_Bs2DsK = new RooExtendPdf(name.Data() , pdf_Bs2DsK->GetTitle(), *pdf_Bs2DsK_Tot, nBs2DsKEvts );
    if (debug == true){ if( epdf_Bs2DsK != NULL ){ cout<<"Create extended "<<epdf_Bs2DsK->GetName()<<endl;}
      else { cout<<"Cannot create extendend PDF"<<endl;}}


    //-----------------------------------------//

    RooKeysPdf* pdf_Bd2DRho = NULL;
    name = "PhysBkgBd2DRhoPdf_m_both";
    pdf_Bd2DRho = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bd2DRho != NULL ){ cout<<"Read "<<pdf_Bd2DRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooKeysPdf* pdf_Bd2DRho_Ds = NULL;
    name = "PhysBkgBd2DRhoPdf_m_both_Ds";
    pdf_Bd2DRho_Ds = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bd2DRho_Ds != NULL ){ cout<<"Read "<<pdf_Bd2DRho_Ds->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooAddPdf* pdf_Bd2DRho_PIDK = NULL;
    RooAddPdf* pdf_Bd2DRho_PIDK1 = NULL;
    RooAddPdf* pdf_Bd2DRho_PIDK2 = NULL;

    if ( pdf_Bd2DRho_PIDK ) {}
    if ( pdf_Bd2DRho_PIDK1 ) {}
    if ( pdf_Bd2DRho_PIDK2 ) {}

    if (merge == true)
      {
	name = "ShapePIDK_Bd2DRho_down";
        pdf_Bd2DRho_PIDK1 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bd2DRho_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DRho_PIDK1->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapePIDK_Bd2DRho_up";
        pdf_Bd2DRho_PIDK2 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bd2DRho_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DRho_PIDK2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	
	name = "ShapePIDK_Bd2DRho_both";
        pdf_Bd2DRho_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bd2DRho_PIDK2,*pdf_Bd2DRho_PIDK1), RooArgList(lumRatio));
        if( pdf_Bd2DRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DRho_PIDK->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    else
      {
	name = "ShapePIDK_Bd2DRho_"+sam;
	pdf_Bd2DRho_PIDK = (RooAddPdf*)work->pdf(name.Data());
	if( pdf_Bd2DRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DRho_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }

    RooProdPdf* pdf_Bd2DRho_Tot = NULL;
    name="PhysBkgBd2DRhoPdf_m_"+samplemode+"_Tot";
    pdf_Bd2DRho_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bd2DRho,*pdf_Bd2DRho_Ds,*pdf_Bd2DRho_PIDK));

    if( pdf_Bd2DRho_Tot != NULL ){
      if (debug == true) cout<<"Read "<<pdf_Bd2DRho_Tot->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

    RooExtendPdf* epdf_Bd2DRho = NULL;
    name = "Bd2DRhoEPDF_m_"+samplemode;
    epdf_Bd2DRho= new RooExtendPdf( name.Data() , pdf_Bd2DRho-> GetTitle(), *pdf_Bd2DRho_Tot  , nBd2DRhoEvts );
    if (debug == true){ if( epdf_Bd2DRho != NULL ){ cout<<"Create extended "<<epdf_Bd2DRho->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}


    //-----------------------------------------//

    RooKeysPdf* pdf_Bd2DstPi = NULL;
    name = "PhysBkgBd2DstPiPdf_m_both";
    pdf_Bd2DstPi = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bd2DstPi != NULL){ cout<<"Read "<<pdf_Bd2DstPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

    RooKeysPdf* pdf_Bd2DstPi_Ds = NULL;
    name = "PhysBkgBd2DstPiPdf_m_both_Ds";
    pdf_Bd2DstPi_Ds = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true){ if( pdf_Bd2DstPi_Ds != NULL){ cout<<"Read "<<pdf_Bd2DstPi_Ds->GetName()<<endl;} 
      else { cout<<"Cannot read PDF"<<endl;} }

    RooAddPdf* pdf_Bd2DstPi_PIDK = NULL;
    RooAddPdf* pdf_Bd2DstPi_PIDK1 = NULL;
    RooAddPdf* pdf_Bd2DstPi_PIDK2 = NULL;

    if ( pdf_Bd2DstPi_PIDK  ){}
    if ( pdf_Bd2DstPi_PIDK1 ){}
    if ( pdf_Bd2DstPi_PIDK2 ){}


    if ( merge == true)
      {
	name = "ShapePIDK_Bd2DstPi_down";
        pdf_Bd2DstPi_PIDK1 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bd2DstPi_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DstPi_PIDK1->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapePIDK_Bd2DstPi_up";
        pdf_Bd2DstPi_PIDK2 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bd2DstPi_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DstPi_PIDK2->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapePIDK_Bd2DstPi_both";
        pdf_Bd2DstPi_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bd2DstPi_PIDK2,*pdf_Bd2DstPi_PIDK1), RooArgList(lumRatio));
        if( pdf_Bd2DstPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DstPi_PIDK->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    else
      {
	name = "ShapePIDK_Bd2DstPi_"+sam;
	pdf_Bd2DstPi_PIDK = (RooAddPdf*)work->pdf(name.Data());
	if( pdf_Bd2DstPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DstPi_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
      }
    RooProdPdf* pdf_Bd2DstPi_Tot = NULL;
    name="PhysBkgBd2DstPiPdf_m_"+samplemode+"_Tot";
    pdf_Bd2DstPi_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bd2DstPi,*pdf_Bd2DstPi_Ds,*pdf_Bd2DstPi_PIDK));

    if( pdf_Bd2DstPi_Tot != NULL ){
      if (debug == true) cout<<"Read "<<pdf_Bd2DstPi_Tot->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

    RooExtendPdf* epdf_Bd2DstPi = NULL;
    name = "Bd2DstPiEPDF_m_"+samplemode;
    epdf_Bd2DstPi = new RooExtendPdf( name.Data() , pdf_Bd2DstPi-> GetTitle(), *pdf_Bd2DstPi_Tot  , nBd2DstPiEvts );
    if (debug == true){ if( epdf_Bd2DstPi != NULL ){ cout<<"Create extended "<<epdf_Bd2DstPi->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}


    // --------------------------------- Create RooAddPdf -------------------------------------------------//
    Bool_t rec=true;
    
    RooAddPdf* pdf_Bs2DsDsstPiRho = NULL;
    name = "PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode;
    pdf_Bs2DsDsstPiRho = new RooAddPdf( name.Data(),
                                        name.Data(),
                                        RooArgList(*pdf_Bs2DsstPi, *pdf_BdDsPi), //, *pdf_Bs2DsRho), //,*pdf_Bs2DsstRho),
                                        RooArgList(g1_f1) //,g1_f2), rec
                                        );
    
    
    RooAbsPdf* pdf_Bs2DsDsstPiRho_Ds = NULL;
    pdf_Bs2DsDsstPiRho_Ds = pdf_SignalDs; 
    /*
    RooAbsPdf* pdf_Bs2DsstPi_Ds = NULL;
    pdf_Bs2DsstPi_Ds = pdf_SignalDs;

    RooAbsPdf* pdf_Bs2DsRho_Ds = NULL;
    pdf_Bs2DsRho_Ds = pdf_SignalDs;

    RooAddPdf* pdf_Bs2DsDsstPiRho_Ds = NULL;
    name = "PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode+"_Ds";
    pdf_Bs2DsDsstPiRho_Ds = new RooAddPdf( name.Data(),
					   name.Data(),
					   RooArgList(*pdf_Bs2DsstPi_Ds, *pdf_BdDsPi_Ds, pdf_Bs2DsRho_Ds), //,*pdf_Bs2DsstRho),
					   RooArgList(g1_f1,g1_f2), rec
					   );
    */


    RooAddPdf* pdf_Bs2DsstPi_PIDK = NULL;
    RooAbsPdf* pdf_Bs2DsstPi_PIDK1 = NULL;
    RooAbsPdf* pdf_Bs2DsstPi_PIDK2 = NULL;

    RooAddPdf* pdf_Bs2DsRho_PIDK = NULL;
    RooAbsPdf* pdf_Bs2DsRho_PIDK1 = NULL;
    RooAbsPdf* pdf_Bs2DsRho_PIDK2 = NULL;

    RooAddPdf* pdf_Bs2DsstRho_PIDK = NULL;
    RooAbsPdf* pdf_Bs2DsstRho_PIDK1 = NULL;
    RooAbsPdf* pdf_Bs2DsstRho_PIDK2 = NULL;

    if (pdf_Bs2DsstPi_PIDK) {}
    if (pdf_Bs2DsstPi_PIDK1){}
    if (pdf_Bs2DsstPi_PIDK2) {}
    if (pdf_Bs2DsRho_PIDK){}
    if (pdf_Bs2DsRho_PIDK1){}
    if (pdf_Bs2DsRho_PIDK2){}
    if (pdf_Bs2DsstRho_PIDK){}
    if (pdf_Bs2DsstRho_PIDK){}
    if (pdf_Bs2DsstRho_PIDK1){}
    if (pdf_Bs2DsstRho_PIDK2){}

    if ( merge == true )
      {
	//name = "ShapePIDK_Bs2DsstPi_down";
        //name = "ShapePIDK_BsDsPi_down";
        //pdf_Bs2DsstPi_PIDK1 = (RooAddPdf*)workID->pdf(name.Data());
        //if( pdf_Bs2DsstPi_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstPi_PIDK1->GetName()<<endl;}
	//else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "PIDshape_BsDsPi_both_"+Mode+"_down"; //sam;
        pdf_Bs2DsstPi_PIDK1 = GetRooBinned1DFromWorkspace(workID, name, debug);

        name = "ShapePIDK_Bs2DsRho_down";
        pdf_Bs2DsRho_PIDK1 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bs2DsRho_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsRho_PIDK1->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

        name = "ShapePIDK_Bs2DsstRho_down";
        pdf_Bs2DsstRho_PIDK1 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bs2DsstRho_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstRho_PIDK1->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	//name = "ShapePIDK_Bs2DsstPi_up";
        //name = "ShapePIDK_BsDsPi_up";
        name = "PIDshape_BsDsPi_both_"+Mode+"_up"; //sam;
        pdf_Bs2DsstPi_PIDK2 = GetRooBinned1DFromWorkspace(workID, name, debug);

	//pdf_Bs2DsstPi_PIDK2 = (RooAddPdf*)workID->pdf(name.Data());
        //if( pdf_Bs2DsstPi_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstPi_PIDK2->GetName()<<endl;}
	//else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

        name = "ShapePIDK_Bs2DsRho_up";
        pdf_Bs2DsRho_PIDK2 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bs2DsRho_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsRho_PIDK2->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

        name = "ShapePIDK_Bs2DsstRho_up";
        pdf_Bs2DsstRho_PIDK2 = (RooAddPdf*)work->pdf(name.Data());
        if( pdf_Bs2DsstRho_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstRho_PIDK2->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	
	name = "ShapePIDK_Bs2DsstPi_both";
        pdf_Bs2DsstPi_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsstPi_PIDK2,*pdf_Bs2DsstPi_PIDK1), RooArgList(lumRatio));
        if( pdf_Bs2DsstPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstPi_PIDK->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapePIDK_Bs2DsRho_both";
        pdf_Bs2DsRho_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsRho_PIDK2,*pdf_Bs2DsRho_PIDK1), RooArgList(lumRatio));
        if( pdf_Bs2DsRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsRho_PIDK->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	name = "ShapePIDK_Bs2DsstRho_both";
        pdf_Bs2DsstRho_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsstRho_PIDK2,*pdf_Bs2DsstRho_PIDK1), RooArgList(lumRatio));
        if( pdf_Bs2DsstRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstPi_PIDK->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

      }
    else
      {
	//name = "ShapePIDK_Bs2DsstPi_"+sam;
	name = "ShapePIDK_BsDsPi_"+sam;
	pdf_Bs2DsstPi_PIDK = (RooAddPdf*)workID->pdf(name.Data());
	if( pdf_Bs2DsstPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstPi_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	
	name = "ShapePIDK_Bs2DsRho_"+sam;
	pdf_Bs2DsRho_PIDK = (RooAddPdf*)work->pdf(name.Data());
	if( pdf_Bs2DsRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsRho_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	
	name = "ShapePIDK_Bs2DsstRho_"+sam;
	pdf_Bs2DsstRho_PIDK = (RooAddPdf*)work->pdf(name.Data());
	if( pdf_Bs2DsstRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstRho_PIDK->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	
      }
    RooAddPdf* pdf_Bs2DsDsstPiRho_PIDK = NULL;
    name = "PhysBkgBs2DsDsstPiRhoPdf_PIDK_"+samplemode;
    pdf_Bs2DsDsstPiRho_PIDK = new RooAddPdf( name.Data(),
					     name.Data(),
					     RooArgList(*pdf_Bs2DsstPi_PIDK,*pdf_BdDsPi_PIDK), //, *pdf_Bs2DsRho_PIDK), //*pdf_Bs2DsstRho_PIDK),
					     RooArgList(g1_f1) //,g1_f2), rec
					     );

    if( pdf_Bs2DsDsstPiRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsDsstPiRho_PIDK->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}


    RooProdPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    name="PhysBkgBs2DsDsstPiPdf_m_"+samplemode+"_Tot";
    pdf_Bs2DsDsstPiRho_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs2DsDsstPiRho,*pdf_Bs2DsDsstPiRho_Ds,*pdf_Bs2DsDsstPiRho_PIDK));
    //pdf_Bs2DsDsstPiRho_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs2DsstPi,*pdf_Bs2DsDsstPiRho_Ds,*pdf_Bs2DsstPi_PIDK));

    if( pdf_Bs2DsDsstPiRho_Tot != NULL ){
      if (debug == true) cout<<"Read "<<pdf_Bs2DsDsstPiRho_Tot->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho-> GetTitle(), *pdf_Bs2DsDsstPiRho_Tot  , nBs2DsDsstPiRhoEvts);
    if (debug == true){ if( epdf_Bs2DsDsstPiRho != NULL ){ cout<<"Create extended "<<epdf_Bs2DsDsstPiRho->GetName()<<endl; }
      else { cout<<"Cannot create extendend PDF"<<endl;}}


    
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(),
                                RooArgList(*epdf_combBkg,
                                           *epdf_Bd2DPi,
					   *epdf_Bs2DsDsstPiRho,
                                           *epdf_Lb2LcPi,
                                           //*epdf_Bd2DstPi,
                                           //*epdf_Bd2DRho, 
                                           //*epdf_Bd2DsstPi,
                                           //*epdf_BdDsPi,
					   *epdf_Bs2DsK));
					   
    
      if (debug == true)
	{
	  cout<<endl;
	  if( pdf_totBkg != NULL ){ cout<<" ------------- CREATED TOTAL BACKGROUND PDF: SUCCESFULL------------"<<endl; }
	  else { cout<<" ---------- CREATED TOTAL BACKGROUND PDF: FAILED ----------------"<<endl;}
	}
      return pdf_totBkg;
    
  }

  RooAbsPdf* buildBsDsK_PIDK_TripleGaussian(RooAbsReal* obs,
					    Double_t mean1Var,
					    Double_t mean2Var,
					    Double_t mean3Var,
					    Double_t sigma1Var,
					    Double_t sigma2Var,
					    Double_t sigma3Var,
					    Double_t f1Var,
					    Double_t f2Var,
					    TString& samplemode,
					    TString& type
					    )
  {

    RooRealVar *mean1 = NULL;
    RooRealVar *mean2 = NULL;
    RooRealVar *mean3 = NULL;
    RooRealVar *sigma1  = NULL;
    RooRealVar *sigma2  = NULL;
    RooRealVar *sigma3  = NULL;
    RooRealVar *f1 = NULL;
    RooRealVar *f2 = NULL;
    TString mode;
    if ( samplemode.Contains("down")) { mode = "down"; } else { mode = "up"; }

    TString nameVar = "mean1TR_"+mode+"_"+type;
    mean1 =  new RooRealVar(nameVar.Data(),"mean1", mean1Var, mean1Var - 100, mean1Var+100);
    nameVar = "mean2TR_"+mode+"_"+type;
    mean2 = new RooRealVar(nameVar.Data(),"mean2", mean2Var, mean2Var - 100, mean2Var+100);
    nameVar = "mean3TR_"+mode+"_"+type;
    mean3 = new RooRealVar(nameVar.Data(), "mean3", mean3Var, mean3Var - 100, mean3Var+100);
    
    nameVar = "sigma1TR_"+mode+"_"+type;
    sigma1 = new RooRealVar(nameVar.Data(),"sigma1",sigma1Var, sigma1Var-10, sigma1Var+10);
    nameVar = "sigma2TR_"+mode+"_"+type;
    sigma2 = new RooRealVar(nameVar.Data(),"sigma2",sigma2Var, sigma2Var-10, sigma2Var+10);
    nameVar = "sigma3TR_"+mode+"_"+type;
    sigma3 = new RooRealVar(nameVar.Data(),"sigma3",sigma3Var, sigma3Var-10, sigma3Var+10);

    
    nameVar = "f1TripleGaussian_"+mode+"_"+type;
    f1 = new RooRealVar(nameVar.Data(),"signal fraction",f1Var);
    nameVar = "f2TripleGaussian_"+mode+"_"+type;
    f2  = new RooRealVar(nameVar.Data(),"signal fraction",f2Var);


    nameVar = "PIDKGaussian1_"+mode+"_"+type;
    RooGaussian* bkg1 = new  RooGaussian(nameVar.Data(), "bkg p.d.f." , *obs, *mean1, *sigma1);
    nameVar = "PIDKGaussian2_"+mode+"_"+type;
    RooGaussian* bkg2 = new  RooGaussian(nameVar.Data(), "bkg p.d.f." , *obs, *mean2, *sigma2);
    nameVar = "PIDKGaussian3_"+mode+"_"+type;
    RooGaussian* bkg3 = new RooGaussian(nameVar.Data(),"signal p.d.f.",*obs, *mean3, *sigma3);
    nameVar = "PIDKTipleGaussian_"+mode+"_"+type;
    RooAddPdf *bkg = new RooAddPdf(nameVar.Data(),"model",RooArgList(*bkg1,*bkg2, *bkg3),RooArgList(*f1,*f2),true);

    return bkg;

  }

  RooAbsPdf* buildBsDsK_PIDK_DoubleGaussian(RooAbsReal* obs,
                                            Double_t mean1Var,
					    Double_t mean2Var,
                                            Double_t sigma1Var,
					    Double_t sigma2Var,
                                            Double_t f1Var,
					    TString& samplemode,
                                            TString& type
                                            )
  {

    RooRealVar *mean1 = NULL;
    RooRealVar *mean2 = NULL;
    RooRealVar *sigma1  = NULL;
    RooRealVar *sigma2  = NULL;
    RooRealVar *f1 = NULL;
    TString mode;
    if ( samplemode.Contains("down")) { mode = "down"; } else { mode = "up"; }

    TString nameVar = "mean1DG_"+mode+"_"+type;
    mean1 =  new RooRealVar(nameVar.Data(),"mean1", mean1Var);
    nameVar = "mean2DG_"+mode+"_"+type;
    mean2 = new RooRealVar(nameVar.Data(),"mean2", mean2Var);
    
    nameVar = "sigma1DG_"+mode+"_"+type;
    sigma1 = new RooRealVar(nameVar.Data(),"sigma1",sigma1Var); //, sigmaVar-10, sigmaVar+10);
    nameVar = "sigma2DG_"+mode+"_"+type;
    sigma2 = new RooRealVar(nameVar.Data(),"sigma2",sigma2Var); //, sigmaVar-10, sigmaVar+10);
    
    nameVar = "f1DG_"+mode+"_"+type;
    f1 = new RooRealVar(nameVar.Data(),"signal fraction",f1Var);
    
    nameVar = "PIDKGaussian1_"+mode+"_"+type;
    RooGaussian* bkg1 = new  RooGaussian(nameVar.Data(), "bkg p.d.f." , *obs, *mean1, *sigma1);
    nameVar = "PIDKGaussian2_"+mode+"_"+type;
    RooGaussian* bkg2 = new  RooGaussian(nameVar.Data(), "bkg p.d.f." , *obs, *mean2, *sigma2);
    nameVar = "PIDKDoubleeGaussian_"+mode+"_"+type;
    RooAddPdf *bkg = new RooAddPdf(nameVar.Data(),"model",RooArgList(*bkg1,*bkg2),RooArgList(*f1));

    return bkg;

  }


  RooAbsPdf* buildBsDsK_PIDK_Gaussian(RooAbsReal* obs,
				      Double_t mean1Var,
				      Double_t sigma1Var,
				      TString& samplemode,
				      TString& type
				      )
  {

    RooRealVar *mean1 = NULL;
    RooRealVar *sigma1  = NULL;
    
    TString mode;
    if ( samplemode.Contains("down")) { mode = "down"; } else { mode = "up"; }

    TString nameVar = "mean1G_"+mode+"_"+type;
    mean1 =  new RooRealVar(nameVar.Data(),"mean1", mean1Var);

    nameVar = "sigma1G_"+mode+"_"+type;
    sigma1 = new RooRealVar(nameVar.Data(),"sigma1",sigma1Var, sigma1Var-sigma1Var*0.5, sigma1Var+sigma1Var*0.5); //, sigmaVar-10, sigmaVar+10);

    nameVar = "PIDKGaussian_"+mode+"_"+type;
    RooGaussian* bkg = new  RooGaussian(nameVar.Data(), "bkg p.d.f." , *obs, *mean1, *sigma1);

    return bkg;
  }


  RooAbsPdf* buildBsDsK_PIDK_DoubleCB(RooAbsReal* obs,
				      Double_t mean1Var,
				      Double_t mean2Var,
				      Double_t sigma1Var,
				      Double_t sigma2Var,
				      Double_t n1Var,
				      Double_t n2Var,
				      Double_t alpha1Var,
				      Double_t alpha2Var,
				      Double_t f1Var,
				      TString& samplemode,
				      TString& type
				      )
  {

    RooRealVar *n1 = NULL;
    RooRealVar *alpha1 = NULL;
    RooRealVar *mean1 = NULL;
    RooRealVar *sigma1  = NULL;

    RooRealVar *n2 = NULL;
    RooRealVar *alpha2 = NULL;
    RooRealVar *mean2 = NULL;
    RooRealVar *sigma2  = NULL;

    RooRealVar *f1 = NULL;
    TString mode;
    if ( samplemode.Contains("down")) { mode = "down"; } else { mode = "up"; }

    TString nameVar = "mean1dCB_"+mode+"_"+type;
    mean1 =  new RooRealVar(nameVar.Data(),"mean1", mean1Var);
    nameVar = "sigma1dCB_"+mode+"_"+type;
    sigma1 = new RooRealVar(nameVar.Data(),"sigma1", sigma1Var, sigma1Var-sigma1Var*0.5, sigma1Var+sigma1Var*0.5);
    nameVar = "n1dCB_"+mode+"_"+type;
    n1 = new RooRealVar(nameVar.Data(), "n1", n1Var); //, meanVar - 10, meanVar+10);
    nameVar = "alpha1dCB_"+mode+"_"+type;
    alpha1 = new RooRealVar(nameVar.Data(), "alpha1", alpha1Var); //, meanVar - 10, meanVar+10);

    nameVar = "mean2dCB_"+mode+"_"+type;
    mean2 =  new RooRealVar(nameVar.Data(),"mean2", mean2Var);
    nameVar = "sigma2dCB_"+mode+"_"+type;
    sigma2 = new RooRealVar(nameVar.Data(),"sigma2", sigma2Var, sigma2Var-sigma2Var*0.5, sigma2Var+sigma2Var*0.5);
    nameVar = "n2dCB_"+mode+"_"+type;
    n2 = new RooRealVar(nameVar.Data(), "n2", n2Var); //, meanVar - 10, meanVar+10);
    nameVar = "alphad2CB_"+mode+"_"+type;
    alpha2 = new RooRealVar(nameVar.Data(), "alpha2", alpha2Var); //, meanVar - 10, meanVar+10);
    
    nameVar = "f1dcB_"+mode+"_"+type;
    f1 = new RooRealVar(nameVar.Data(),"signal fraction",f1Var);

    nameVar = "PIDKCB1_"+mode+"_"+type;
    RooCBShape* bkg1 = new  RooCBShape(nameVar.Data(), "bkg p.d.f." , *obs, *mean1, *sigma1, *alpha1, *n1);
    nameVar = "PIDKCB2_"+mode+"_"+type;
    RooCBShape* bkg2 = new RooCBShape(nameVar.Data(),"signal p.d.f.",*obs, *mean2, *sigma2, *alpha2, *n2);
    nameVar = "PIDKdCB_"+mode+"_"+type;
    RooAddPdf *bkg = new RooAddPdf(nameVar.Data(),"model",RooArgList(*bkg1,*bkg2),RooArgList(*f1));

    return bkg;
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
                            TString &sam,
			    TString &samplemode,
			    bool toys, 
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

    TString s = sam; 

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
					RooArgList(g2_f1,g2_f2,g2_f3)); //, rec));
    
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
  // Background 2D model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf* buildBsDsK_2D(RooAbsReal& mass,
			   RooAbsReal& massDs,
			   RooWorkspace* work,
			   RooWorkspace* workID,
			   RooWorkspace* workID2,
                           RooAddPdf* pdf_Bd2DsK,
                           RooRealVar& nCombBkgEvts,
                           RooRealVar& nBs2DsDsstPiRhoEvts,
			   RooRealVar& nBs2DsPiEvts,
			   RooRealVar& nBs2DsDssKKstEvts,
                           RooRealVar& nLb2DsDsstpEvts,
			   RooRealVar& nBd2DKEvts,
                           RooRealVar& nLb2LcKEvts,
                           RooRealVar& g1_f1,
                           RooRealVar& g1_f2,
                           RooRealVar& g1_f3,
                           RooRealVar& g2_f1,
                           //RooRealVar& g2_f2,
                           //RooRealVar& g2_f3,
                           RooRealVar& g3_f1,
			   RooRealVar& g4_f1,
			   RooRealVar& g4_f2,
			   RooAbsPdf* pdf_SignalDs,
			   RooRealVar& cBVar,
			   RooRealVar& cDVar,
			   RooRealVar& fracComb,
			   TString &samplemode,
			   //bool merge,
			   RooRealVar& lumRatio,
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
    RooRealVar fake_g1_f2 = g1_f2;
    RooRealVar fake_g1_f3 = g1_f3;
    //RooRealVar fake_g2_f3 = g2_f3;
    TString sam;
    bool merge = false;
    if (samplemode.Contains("down") == true )
      {
	sam = "down";
      }
    else if (samplemode.Contains("up") == true )
      {
	sam = "up";
      }
    else
      {
	sam = "both";
	merge = true;
      }

    TString mode;
    if ( samplemode.Contains("kkpi") == true ) {
      mode = "kkpi";
    }
    else if ( samplemode.Contains("kpipi") == true ){
      mode = "kpipi";
    }
    else if ( samplemode.Contains("pipipi") == true ){
      mode = "pipipi";
    }
    else if (samplemode.Contains("nonres") == true ){
      mode = "nonres";
    }
    else if (samplemode.Contains("kstk") == true ){
      mode = "kstk";
    }
    else if (samplemode.Contains("phipi") == true ){
      mode = "phipi";
    }


    TString name; 
    RooAbsPdf* pdf_Bd2DsK_PIDK = NULL;
    RooAbsPdf* pdf_Bd2DsK_PIDK1 = NULL;
    RooAbsPdf* pdf_Bd2DsK_PIDK2 = NULL;

    if ( pdf_Bd2DsK_PIDK ) {}
    if ( pdf_Bd2DsK_PIDK1 ) {}
    if ( pdf_Bd2DsK_PIDK2 ) {}
    
    if ( merge == true )
      {
	name = "PIDshape_BsDsK_both_"+mode+"_down";
        pdf_Bd2DsK_PIDK1 = GetRooBinned1DFromWorkspace(workID2, name, debug);

	name = "PIDshape_BsDsK_both_"+mode+"_up";
        pdf_Bd2DsK_PIDK2 = GetRooBinned1DFromWorkspace(workID2, name, debug);
	
	/*
	name = "PIDKShape_dCB_BsDsK_down";
	pdf_Bd2DsK_PIDK1 = (RooAddPdf*)workID2->pdf(name.Data());
	name = "PIDKShape_dCB_BsDsK_up";
	pdf_Bd2DsK_PIDK2 = (RooAddPdf*)workID2->pdf(name.Data());
	*/
	name = "PIDKShape_BsDsK_both";
	pdf_Bd2DsK_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bd2DsK_PIDK2,*pdf_Bd2DsK_PIDK1), RooArgList(lumRatio));
      }
    else
      {  
	name = "PIDshape_BsDsK_both_"+mode+"_"+sam;
	pdf_Bd2DsK_PIDK = GetRooBinned1DFromWorkspace(workID2, name, debug);
      }
    if( pdf_Bd2DsK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DsK_PIDK->GetName()<<endl;}
    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

    name="fake_"+samplemode;

    RooRealVar fake( name.Data(), name.Data(), 0);

            
    // -------------------------------- Create Combinatorial Background --------------------------------------------//                       

      if (debug == true) { cout<<"---------------  Create combinatorial background PDF -----------------"<<endl; }

      
      RooExponential* pdf_combBkg = NULL;
      name="CombBkgPDF_m_"+samplemode;
      pdf_combBkg = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, cBVar);

      RooExponential* pdf_combBkg_slope_Ds = NULL;
      name="CombBkgPDF_slope_"+samplemode+"_Ds";
      pdf_combBkg_slope_Ds = new RooExponential( name.Data(), name.Data(), massDs, cDVar );
      if( pdf_combBkg_slope_Ds != NULL ){ if (debug == true) cout<<"Create "<<pdf_combBkg_slope_Ds->GetName()<<endl; }
      else { if (debug == true) cout<<"Cannot create combinatorial background pdf"<<endl;}

      RooAddPdf* pdf_combBkg_Ds = NULL;
      name="CombBkgPDF_"+samplemode+"_Ds";
      pdf_combBkg_Ds = new RooAddPdf( name.Data(), name.Data(),  RooArgList(*pdf_combBkg_slope_Ds,*pdf_SignalDs), fracComb );
      if( pdf_combBkg_slope_Ds != NULL && pdf_combBkg_Ds != NULL ){ if (debug == true) cout<<"Create "<<pdf_combBkg_Ds->GetName()<<endl; }
      else { if (debug == true) cout<<"Cannot create combinatorial background pdf"<<endl;}
           
      RooAddPdf* pdf_CombPi_PIDK = NULL;
      RooAbsPdf* pdf_CombK_PIDK = NULL;
      RooAddPdf* pdf_CombP_PIDK = NULL;
      RooAddPdf* pdf_CombPi_PIDK1 = NULL;
      RooAbsPdf* pdf_CombK_PIDK1 = NULL;
      RooAddPdf* pdf_CombP_PIDK1 = NULL;
      RooAddPdf* pdf_CombPi_PIDK2 = NULL;
      RooAbsPdf* pdf_CombK_PIDK2= NULL;
      RooAddPdf* pdf_CombP_PIDK2 = NULL;

      if ( pdf_CombPi_PIDK ) {}
      if ( pdf_CombK_PIDK ) {}
      if ( pdf_CombP_PIDK ) {}
      if ( pdf_CombPi_PIDK1 ) {}
      if ( pdf_CombK_PIDK1 ) {}
      if ( pdf_CombP_PIDK1 ) {}
      if ( pdf_CombPi_PIDK2 ) {}
      if ( pdf_CombK_PIDK2 ) {}
      if ( pdf_CombP_PIDK2 ) {}

      if (merge == true )
	{
	  name = "PIDKShape_expGauss_CombPi_down";
          pdf_CombPi_PIDK1 = (RooAddPdf*)workID2->pdf(name.Data());
          if( pdf_CombPi_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombPi_PIDK1->GetName()<<endl;}
          else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

          /*name = "PIDKShape_dCB_CombK_down";
          pdf_CombK_PIDK1 = (RooAddPdf*)workID2->pdf(name.Data());
          if( pdf_CombK_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombK_PIDK1->GetName()<<endl;}
          else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	  */
	  name = "PIDshape_CombK_down";
	  pdf_CombK_PIDK1 = GetRooBinned1DFromWorkspace(workID2, name, debug);
          
	  name = "PIDKTipleGaussian_CombP_down";
          pdf_CombP_PIDK1 = (RooAddPdf*)workID2->pdf(name.Data());
          if( pdf_CombP_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombP_PIDK1->GetName()<<endl;}
	  else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	  name = "PIDKShape_expGauss_CombPi_up";
          pdf_CombPi_PIDK2 = (RooAddPdf*)workID2->pdf(name.Data());
          if( pdf_CombPi_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombPi_PIDK2->GetName()<<endl;}
          else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	  /*
          name = "PIDKShape_dCB_CombK_up";
          pdf_CombK_PIDK2 = (RooAddPdf*)workID2->pdf(name.Data());
          if( pdf_CombK_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombK_PIDK2->GetName()<<endl;}
          else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	  */
	
	  name = "PIDshape_CombK_up";
          pdf_CombK_PIDK2 = GetRooBinned1DFromWorkspace(workID2, name, debug);

          name = "PIDKTipleGaussian_CombP_down";
          pdf_CombP_PIDK2 = (RooAddPdf*)workID2->pdf(name.Data());
          if( pdf_CombP_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombP_PIDK2->GetName()<<endl;}
          else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	  name = "PIDKShape_expGauss_CombPi_both";
	  pdf_CombPi_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_CombPi_PIDK2,*pdf_CombPi_PIDK1), RooArgList(lumRatio));
	  if( pdf_CombPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombPi_PIDK->GetName()<<endl;}
          else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	  name = "PIDKShape_dCB_CombK_both";
	  pdf_CombK_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_CombK_PIDK2,*pdf_CombK_PIDK1), RooArgList(lumRatio));
	  if( pdf_CombK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombK_PIDK->GetName()<<endl;}
          else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	  name = "PIDKTipleGaussian_CombP_both";
	  pdf_CombP_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_CombP_PIDK2,*pdf_CombP_PIDK1), RooArgList(lumRatio));
	  if( pdf_CombP_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombP_PIDK->GetName()<<endl;}
          else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	}
      else
	{
	  name = "PIDKShape_expGauss_CombPi_"+sam; 
	  pdf_CombPi_PIDK = (RooAddPdf*)workID2->pdf(name.Data());
	  if( pdf_CombPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombPi_PIDK->GetName()<<endl;}
	  else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	  /*
	  name = "PIDKShape_dCB_CombK_"+sam;
	  pdf_CombK_PIDK = (RooAddPdf*)workID2->pdf(name.Data());
	  if( pdf_CombK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombK_PIDK->GetName()<<endl;}
	  else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	  */
	  name = "PIDshape_CombK_"+sam;
          pdf_CombK_PIDK = GetRooBinned1DFromWorkspace(workID2, name, debug);

	  name = "PIDKTipleGaussian_CombP_"+sam;
	  pdf_CombP_PIDK = (RooAddPdf*)workID2->pdf(name.Data());
	  if( pdf_CombP_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_CombP_PIDK->GetName()<<endl;}
	  else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	}
      RooAddPdf* pdf_combBkg_PIDK = NULL;
      name = "ShapePIDKAll_Comb_"+sam;
      pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
					name.Data(),
					RooArgList(*pdf_CombK_PIDK,*pdf_CombPi_PIDK, *pdf_CombP_PIDK), 
					RooArgList(g4_f1,g4_f2), 
					true);

      if( pdf_combBkg_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_combBkg_PIDK->GetName()<<endl;}
      else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

      
      
      RooProdPdf* pdf_combBkg_Tot = NULL;
      name="CombBkgPDF_m_"+samplemode+"_Tot";
      pdf_combBkg_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_combBkg,*pdf_combBkg_Ds,*pdf_combBkg_PIDK));

      if( pdf_combBkg_Tot != NULL ){
	if (debug == true) cout<<"Read "<<pdf_combBkg_Tot->GetName()<<endl;}
      else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

      RooExtendPdf* epdf_combBkg   = NULL;
      name = "CombBkgEPDF_m_"+samplemode;
      epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg_Tot  , nCombBkgEvts   );
      if (debug == true) { if( epdf_combBkg != NULL ){ cout<<"Create extended "<<epdf_combBkg->GetName()<<endl; }
	else { cout<<"Cannot create extendend PDF"<<endl;}}
      
      // --------------------------------- Read PDFs from Workspace -------------------------------------------------//                      

	if (debug == true) cout<<endl;
	if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;

	RooKeysPdf* pdf_Bd2DK = NULL;
	name = "PhysBkgBd2DKPdf_m_both";
	pdf_Bd2DK = (RooKeysPdf*)work->pdf(name.Data());
	if (debug == true) { if( pdf_Bd2DK != NULL ){ cout<<"Read "<<pdf_Bd2DK->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

	RooKeysPdf* pdf_Bd2DK_Ds = NULL;
	name = "PhysBkgBd2DKPdf_m_both_Ds";
	pdf_Bd2DK_Ds = (RooKeysPdf*)work->pdf(name.Data());
	if( pdf_Bd2DK_Ds != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DK_Ds->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	RooAbsPdf* pdf_Bd2DK_PIDK = NULL;
	RooAbsPdf* pdf_Bd2DK_PIDK1 = NULL;
	RooAbsPdf* pdf_Bd2DK_PIDK2 = NULL;

	if ( pdf_Bd2DK_PIDK ) {}
	if ( pdf_Bd2DK_PIDK1 ) {}
	if ( pdf_Bd2DK_PIDK2 ) {}

	if ( merge == true )
	  {
	    
	    name = "PIDshape_Bd2DK_down";
	    pdf_Bd2DK_PIDK1 = GetRooBinned1DFromWorkspace(workID, name, debug);

	    name = "PIDshape_Bd2DK_up";
	    pdf_Bd2DK_PIDK2 = GetRooBinned1DFromWorkspace(workID, name, debug);
	    /*
	    name = "PIDKShape_dCB_Bd2DK_down";
            pdf_Bd2DK_PIDK1 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Bd2DK_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DK_PIDK1->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF: "<<name<<endl;}

	    name = "PIDKShape_dCB_Bd2DK_up";
            pdf_Bd2DK_PIDK2 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Bd2DK_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DK_PIDK2->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF: "<<name<<endl;}
	    */
	    name = "PIDKShape_Bd2DK_both";
	    pdf_Bd2DK_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bd2DK_PIDK2,*pdf_Bd2DK_PIDK1), RooArgList(lumRatio));
	    if( pdf_Bd2DK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DK_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	  }
	else
	  {
	    name = "PIDshape_Bd2DK_"+sam;
            pdf_Bd2DK_PIDK= GetRooBinned1DFromWorkspace(workID, name, debug);

	    /*
	    name = "PIDKShape_dCB_Bd2DK_"+sam;
	    pdf_Bd2DK_PIDK = (RooAddPdf*)workID->pdf(name.Data());
	    if( pdf_Bd2DK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bd2DK_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF: "<<name<<endl;}
	    */
	  }

	RooProdPdf* pdf_Bd2DK_Tot = NULL;
	name="PhysBkgBd2DKPdf_m_"+samplemode+"_Tot";
	pdf_Bd2DK_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bd2DK,*pdf_Bd2DK_Ds,*pdf_Bd2DK_PIDK));

	if( pdf_Bd2DK_Tot != NULL ){
	  if (debug == true) cout<<"Read "<<pdf_Bd2DK_Tot->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	RooExtendPdf* epdf_Bd2DK    = NULL;
	name = "Bd2DKEPDF_m_"+samplemode;
	epdf_Bd2DK = new RooExtendPdf( name.Data(),pdf_Bd2DK->GetTitle(), *pdf_Bd2DK_Tot, nBd2DKEvts);
	if (debug == true){ if( epdf_Bd2DK != NULL ){ cout<<"Create extended "<<epdf_Bd2DK->GetName()<<endl;}
	  else { cout<<"Cannot create extendend PDF"<<endl;} }

	//-----------------------------------------//
	
	RooKeysPdf* pdf_Bs2DsKst = NULL;
	name = "PhysBkgBs2DsKstPdf_m_both";
	pdf_Bs2DsKst = (RooKeysPdf*)work->pdf(name.Data());
	if (debug == true){ if( pdf_Bs2DsKst != NULL ){ cout<<"Read "<<pdf_Bs2DsKst->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
	/*
	RooKeysPdf* pdf_Bs2DsstK = NULL;
	name = "PhysBkgBs2DsstKPdf_m_both";
	pdf_Bs2DsstK = (RooKeysPdf*)work->pdf(name.Data());
	if (debug == true) {if( pdf_Bs2DsstK != NULL ){ cout<<"Read "<<pdf_Bs2DsstK->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

	RooKeysPdf* pdf_Bs2DsstKst = NULL;
	name = "PhysBkgBs2DsstKstPdf_m_both";
	pdf_Bs2DsstKst = (RooKeysPdf*)work->pdf(name.Data());
	if (debug == true){ if( pdf_Bs2DsstKst != NULL ){ cout<<"Read "<<pdf_Bs2DsstKst->GetName()<<endl;} 
	  else { cout<<"Cannot read PDF"<<endl;}}
	*/

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
					   RooArgList(*pdf_Bd2DsK, *pdf_Bs2DsKst), //*pdf_Bs2DsstK,*pdf_Bs2DsstKst),
					   RooArgList(g1_f1) //g1_f2, g1_f3), 
					   //rec
					   );

	RooAbsPdf* pdf_Bs2DsDsstKKst_Ds = NULL;
	name = "Bs2DsDsstKKst"+samplemode;
	TString name2 = "Bs";
	//pdf_Bs2DsDsstKKst_Ds = buildDoubleGEPDF_sim(massDs, meanDs, sigma1Ds, sigma2Ds, fracDs, fake, name.Data(), name2.Data(), false, debug);
	pdf_Bs2DsDsstKKst_Ds = pdf_SignalDs; //new RooCruijff(name.Data(), name.Data(),massDs, meanDs, sigma1Ds, sigma2Ds,alpha1Ds, alpha2Ds);
	

	RooAbsPdf* pdf_Bs2DsKst_PIDK = NULL;
	RooAbsPdf* pdf_Bs2DsKst_PIDK1 = NULL;
	RooAbsPdf* pdf_Bs2DsKst_PIDK2 = NULL;

	RooAbsPdf* pdf_Bs2DsstK_PIDK = NULL;
	RooAbsPdf* pdf_Bs2DsstK_PIDK1 = NULL;
	RooAbsPdf* pdf_Bs2DsstK_PIDK2 = NULL;

	RooAbsPdf* pdf_Bs2DsstKst_PIDK = NULL;
	RooAbsPdf* pdf_Bs2DsstKst_PIDK1 = NULL;
	RooAbsPdf* pdf_Bs2DsstKst_PIDK2 = NULL;

	if ( pdf_Bs2DsKst_PIDK  ) {}
	if ( pdf_Bs2DsKst_PIDK1 ) {}
	if ( pdf_Bs2DsKst_PIDK2 ) {}

	if ( pdf_Bs2DsstK_PIDK ) {}
	if ( pdf_Bs2DsstK_PIDK1 ) {}
	if ( pdf_Bs2DsstK_PIDK2 ) {}
	
	if ( pdf_Bs2DsstKst_PIDK ) {}
	if ( pdf_Bs2DsstKst_PIDK1 ) {}
	if ( pdf_Bs2DsstKst_PIDK2 ) {}

	if ( merge == true)
	  {
	    name = "PIDshape_Bs2DsKst_down";
            pdf_Bs2DsKst_PIDK1 = GetRooBinned1DFromWorkspace(workID, name, debug); 
	    
	    /*
              name = "PIDKShape_Bs2DsstK_down";
	      pdf_Bs2DsstK_PIDK1 = GetRooBinned1DFromWorkspace(workID, name, debug);
	      //(RooAddPdf*)workID->pdf(name.Data());
              if( pdf_Bs2DsKst_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsKst_PIDK1->GetName()<<endl;}
	            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

              name = "PIDKShape_Bs2DsstKst_down";
              pdf_Bs2DsstKst_PIDK1 = GetRooBinned1DFromWorkspace(workID, name, debug);
	      //(RooAddPdf*)workID->pdf(name.Data());
              if( pdf_Bs2DsstKst_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstKst_PIDK1->GetName()<<endl;}
              else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    */

	    name = "PIDshape_Bs2DsKst_up";
            pdf_Bs2DsKst_PIDK2 = GetRooBinned1DFromWorkspace(workID, name, debug); //(RooAddPdf*)workID->pdf(name.Data());
            /*
              name = "PIDKShape_Bs2DsstK_up";
              pdf_Bs2DsstK_PIDK2 = GetRooBinned1DFromWorkspace(workID, name, debug); //(RooAddPdf*)workID->pdf(name.Data());
              if( pdf_Bs2DsKst_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsKst_PIDK2->GetName()<<endl;}
	                  else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

              name = "PIDKShape_Bs2DsstKst_up";
              pdf_Bs2DsstKst_PIDK2 = GetRooBinned1DFromWorkspace(workID, name, debug); //(RooAddPdf*)workID->pdf(name.Data());
              if( pdf_Bs2DsstKst_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstKst_PIDK2->GetName()<<endl;}
              else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    */
	    
	    name = "PIDKShape_Bs2DsKst_both";
            pdf_Bs2DsKst_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsKst_PIDK2,*pdf_Bs2DsKst_PIDK1), RooArgList(lumRatio));
            //if( pdf_Bs2DsKst_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsKst_PIDK->GetName()<<endl;}
            //else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    /*
	      name = "PIDKShape_Bs2DsstK_both";
	      pdf_Bs2DsstK_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsstK_PIDK2,*pdf_Bs2DsstK_PIDK1), RooArgList(lumRatio));
	      if( pdf_Bs2DsstK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstK_PIDK->GetName()<<endl;}
	      else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	      
	      name = "PIDKShape_Bs2DsstKst_both";
	      pdf_Bs2DsstKst_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsstKst_PIDK2,*pdf_Bs2DsstKst_PIDK1), RooArgList(lumRatio));
	      if( pdf_Bs2DsstKst_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstKst_PIDK->GetName()<<endl;}
	      else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    */
	  }
	else
	  {
	    name = "PIDKShape_Bs2DsKst_"+sam;
	    pdf_Bs2DsKst_PIDK = GetRooBinned1DFromWorkspace(workID, name, debug); //(RooAddPdf*)workID->pdf(name.Data());
	    if( pdf_Bs2DsKst_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsKst_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    /*
	      name = "PIDKShape_Bs2DsstK_"+sam;
	      pdf_Bs2DsstK_PIDK = GetRooBinned1DFromWorkspace(workID, name, debug); //(RooAddPdf*)workID->pdf(name.Data());
	      if( pdf_Bs2DsKst_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsKst_PIDK->GetName()<<endl;}
	      else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	      
	      name = "PIDKShape_Bs2DsstKst_"+sam;
	      pdf_Bs2DsstKst_PIDK = GetRooBinned1DFromWorkspace(workID, name, debug); //(RooAddPdf*)workID->pdf(name.Data());
	      if( pdf_Bs2DsstKst_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstKst_PIDK->GetName()<<endl;}
	      else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    */
	  }
	
	RooAddPdf* pdf_Bs2DsDsstKKst_PIDK = NULL;
        name = "PhysBkgBs2DsDsstKKstPdf_m_"+samplemode+"_PIDK";

        pdf_Bs2DsDsstKKst_PIDK = new RooAddPdf( name.Data(),
						name.Data(),
						RooArgList(*pdf_Bd2DsK_PIDK, *pdf_Bs2DsKst_PIDK), //*pdf_Bs2DsstK_PIDK, *pdf_Bs2DsstKst_PIDK),
						RooArgList(g1_f1) //g1_f2, g1_f3), 
						//rec
						);
	
	RooProdPdf* pdf_Bs2DsDsstKKst_Tot = NULL;
	name="PhysBkgBs2DsDsstKKstPdf_m_"+samplemode+"_Tot";
	pdf_Bs2DsDsstKKst_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs2DsDsstKKst,*pdf_Bs2DsDsstKKst_Ds,*pdf_Bs2DsDsstKKst_PIDK));

	if( pdf_Bs2DsDsstKKst_Tot != NULL ){
	  if (debug == true) cout<<"Create "<<pdf_Bs2DsDsstKKst_Tot->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot create PDF"<<endl;}

	RooExtendPdf* epdf_Bs2DsDsstKKst   = NULL;
	name = "Bs2DsDsstKKstEPDF_m_"+samplemode;
	epdf_Bs2DsDsstKKst = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstKKst   -> GetTitle(), 
					       *pdf_Bs2DsDsstKKst_Tot  , nBs2DsDssKKstEvts   );
	if (debug == true){ if( epdf_Bs2DsDsstKKst != NULL ){ cout<<"Create extended "<<epdf_Bs2DsDsstKKst->GetName()<<endl; }
	  else { cout<<"Cannot create extendend PDF"<<endl;}}

	//-----------------------------------------//

	RooAbsPdf* pdf_Bs2DsPi = NULL;
	RooAbsPdf* pdf_Bs2DsPi1 = NULL;
	RooAbsPdf* pdf_Bs2DsPi2 = NULL;

	if ( pdf_Bs2DsPi ) {}
	if ( pdf_Bs2DsPi1 ) {}
	if ( pdf_Bs2DsPi2 ) {}

	if ( merge == true )
	  {
	    name = "PhysBkgBsDsPi_m_down_"+mode;
            pdf_Bs2DsPi1 = (RooKeysPdf*)work->pdf(name.Data());
            if (debug == true){ if( pdf_Bs2DsPi1 != NULL ){ cout<<"Read "<<pdf_Bs2DsPi1->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }

	    name = "PhysBkgBsDsPi_m_up_"+mode;
            pdf_Bs2DsPi2 = (RooKeysPdf*)work->pdf(name.Data());
            if (debug == true){ if( pdf_Bs2DsPi2 != NULL ){ cout<<"Read "<<pdf_Bs2DsPi2->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }
	    
	    name = "PhysBkgBsDsPi_m_both_"+mode;
	    pdf_Bs2DsPi = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsPi2,*pdf_Bs2DsPi1), RooArgList(lumRatio));
	    if( pdf_Bs2DsPi != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsPi->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	  }
	else
	  {
	    name = "PhysBkgBsDsPi_m_"+samplemode;
	    pdf_Bs2DsPi = (RooKeysPdf*)work->pdf(name.Data());
	    if (debug == true){ if( pdf_Bs2DsPi != NULL ){ cout<<"Read "<<pdf_Bs2DsPi->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;} }
	  }
	RooKeysPdf* pdf_Bs2DsstPi = NULL;
	name = "PhysBkgBs2DsstPiPdf_m_both";
	pdf_Bs2DsstPi = (RooKeysPdf*)work->pdf(name.Data());
	if (debug == true) { if( pdf_Bs2DsstPi != NULL ){ cout<<"Read "<<pdf_Bs2DsstPi->GetName()<<endl;} 
	  else { cout<<"Cannot read PDF"<<endl;}}
	/*
	RooKeysPdf* pdf_Bs2DsstRho = NULL;
	name = "PhysBkgBs2DsstRhoPdf_m_both";
	pdf_Bs2DsstRho = (RooKeysPdf*)work->pdf(name.Data());
	if (debug == true) {if( pdf_Bs2DsstRho != NULL ){ cout<<"Read "<<pdf_Bs2DsstRho->GetName()<<endl;} 
	  else { cout<<"Cannot read PDF"<<endl;}}
	*/
	RooKeysPdf* pdf_Bs2DsRho = NULL;
	name = "PhysBkgBs2DsRhoPdf_m_both";
	pdf_Bs2DsRho = (RooKeysPdf*)work->pdf(name.Data());
	if (debug == true) { if( pdf_Bs2DsRho != NULL ){ cout<<"Read "<<pdf_Bs2DsRho->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

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
	/*
	RooAddPdf* pdf_Bs2DsDsstPiRho = NULL;
	name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode;
	pdf_Bs2DsDsstPiRho = new RooAddPdf( name.Data(),
					    name.Data(),
					    RooArgList(*pdf_Bs2DsPi, *pdf_Bs2DsstPi,*pdf_Bs2DsRho), //*pdf_Bs2DsstRho),
					    RooArgList(g2_f1,g2_f2), rec); ///, g2_f3), rec);
	*/
	RooAddPdf* pdf_Bs2DsDsstPiRho = NULL;
        name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode;
        pdf_Bs2DsDsstPiRho = new RooAddPdf( name.Data(),
                                            name.Data(),
                                            RooArgList(*pdf_Bs2DsstPi,*pdf_Bs2DsRho), //*pdf_Bs2DsstRho),
                                            RooArgList(g2_f1)); ///, g2_f3), rec);


	if (debug == true)
	  {
	    if (pdf_Bs2DsDsstPiRho != NULL)
	      { cout<<"Create doubleCB PDF: "<<pdf_Bs2DsDsstPiRho->GetName()<<endl;}
	    else
	      {cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
	  }    
	    
	RooAbsPdf* pdf_Bs2DsDsstPiRho_Ds = NULL;
        name="Bs2DsDsstPiRho"+samplemode;
        name2 = "Bs";
	pdf_Bs2DsDsstPiRho_Ds = pdf_SignalDs; //new RooCruijff(name.Data(), name.Data(),massDs, meanDs, sigma1Ds, sigma2Ds,alpha1Ds, alpha2Ds);
        //pdf_Bs2DsDsstPiRho_Ds = buildDoubleGEPDF_sim(massDs, meanDs, sigma1Ds, sigma2Ds, fracDs, 
	//					     fake, name.Data(), name2.Data(), false, debug);
	
	
	RooAbsPdf* pdf_Bs2DsPi_Ds = NULL;
	pdf_Bs2DsPi_Ds = pdf_SignalDs; 

	RooAbsPdf* pdf_Bs2DsPi_PIDK = NULL;
	RooAbsPdf* pdf_Bs2DsPi_PIDK1 = NULL;
	RooAbsPdf* pdf_Bs2DsPi_PIDK2 = NULL;

	RooAbsPdf* pdf_Bs2DsstPi_PIDK = NULL;
	RooAbsPdf* pdf_Bs2DsstPi_PIDK1 = NULL;
	RooAbsPdf* pdf_Bs2DsstPi_PIDK2 = NULL;

	RooAbsPdf* pdf_Bs2DsRho_PIDK = NULL;
	RooAbsPdf* pdf_Bs2DsRho_PIDK1 = NULL;
	RooAbsPdf* pdf_Bs2DsRho_PIDK2 = NULL;

	if ( pdf_Bs2DsPi_PIDK ) {}
	if ( pdf_Bs2DsPi_PIDK1 ) {}
	if ( pdf_Bs2DsPi_PIDK2 ) {}

	if ( pdf_Bs2DsstPi_PIDK ) {}
	if ( pdf_Bs2DsstPi_PIDK1 ) {}
	if ( pdf_Bs2DsstPi_PIDK2 ) {}
	
	if ( pdf_Bs2DsRho_PIDK ) {}
	if ( pdf_Bs2DsRho_PIDK1 ) {}
	if ( pdf_Bs2DsRho_PIDK2 ) {}

	if ( merge  == true )
	  {
	    name = "PIDKShape_expGauss_BsDsPi_down_"+mode;
            pdf_Bs2DsPi_PIDK1 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Bs2DsPi_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsPi_PIDK1->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	    name = "PIDKShape_expGauss_Bs2DsstPi_down";
            pdf_Bs2DsstPi_PIDK1 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Bs2DsstPi_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstPi_PIDK1->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	    name = "PIDKShape_expGauss_Bs2DsRho_down";
            pdf_Bs2DsRho_PIDK1 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Bs2DsRho_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsRho_PIDK1->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
            /*
              name = "PIDKShape_expGauss_Bs2DsstRho_down";
              pdf_Bs2DsstRho_PIDK1 = (RooAddPdf*)workID->pdf(name.Data());
              if( pdf_Bs2DsstRho_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstRho_PIDK1->GetName()<<endl;}
              else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    */

	    name = "PIDKShape_expGauss_BsDsPi_up_"+mode;
            pdf_Bs2DsPi_PIDK2 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Bs2DsPi_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsPi_PIDK2->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

            name = "PIDKShape_expGauss_Bs2DsstPi_up";
            pdf_Bs2DsstPi_PIDK2 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Bs2DsstPi_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstPi_PIDK2->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

            name = "PIDKShape_expGauss_Bs2DsRho_up";
            pdf_Bs2DsRho_PIDK2 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Bs2DsRho_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsRho_PIDK2->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
            /*
              name = "PIDKShape_expGauss_Bs2DsstRho_up";
              pdf_Bs2DsstRho_PIDK2 = (RooAddPdf*)workID->pdf(name.Data());
              if( pdf_Bs2DsstRho_PIDK2!= NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstRho_PIDK2->GetName()<<endl;}
              else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    */

	    name = "PIDKShape_expGauss_BsDsPi_both_"+mode;
	    pdf_Bs2DsPi_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsPi_PIDK2,*pdf_Bs2DsPi_PIDK1), RooArgList(lumRatio));
	    if( pdf_Bs2DsPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsPi_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	    name = "PIDKShape_expGauss_Bs2DsstPi_both";
            pdf_Bs2DsstPi_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsstPi_PIDK2,*pdf_Bs2DsstPi_PIDK1), RooArgList(lumRatio));
            if( pdf_Bs2DsstPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstPi_PIDK->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    
	    name = "PIDKShape_expGauss_Bs2DsRho_both";
            pdf_Bs2DsRho_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsRho_PIDK2,*pdf_Bs2DsRho_PIDK1), RooArgList(lumRatio));
            if( pdf_Bs2DsRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsRho_PIDK->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    /*
	      name = "PIDKShape_expGauss_Bs2DsstRho_both";
	      pdf_Bs2DsstRho_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Bs2DsstRho_PIDK2,*pdf_Bs2DsstRho_PIDK1), RooArgList(lumRatio));
	      if( pdf_Bs2DsstRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstRho_PIDK->GetName()<<endl;}
	      else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    */
	  }
	else
	  {
	    name = "PIDKShape_expGauss_BsDsPi_"+samplemode;
	    pdf_Bs2DsPi_PIDK = (RooAddPdf*)workID->pdf(name.Data());
	    if( pdf_Bs2DsPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsPi_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    
	    name = "PIDKShape_expGauss_Bs2DsstPi_"+sam;
	    pdf_Bs2DsstPi_PIDK = (RooAddPdf*)workID->pdf(name.Data());
	    if( pdf_Bs2DsstPi_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstPi_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    
	    name = "PIDKShape_expGauss_Bs2DsRho_"+sam;
	    pdf_Bs2DsRho_PIDK = (RooAddPdf*)workID->pdf(name.Data());
	    if( pdf_Bs2DsRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsRho_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    /*
	      name = "PIDKShape_expGauss_Bs2DsstRho_"+sam;
	      pdf_Bs2DsstRho_PIDK = (RooAddPdf*)workID->pdf(name.Data());
	      if( pdf_Bs2DsstRho_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Bs2DsstRho_PIDK->GetName()<<endl;}
	      else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    */
	  }

	RooAddPdf* pdf_Bs2DsDsstPiRho_PIDK = NULL;
        name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode+"_PIDK";
        pdf_Bs2DsDsstPiRho_PIDK = new RooAddPdf( name.Data(),
                                                 name.Data(),
                                                 RooArgList(*pdf_Bs2DsstPi_PIDK,*pdf_Bs2DsRho_PIDK),// *pdf_Bs2DsstRho_PIDK),
                                                 RooArgList(g2_f1)); //,g2_f3), rec);
	/*
	RooAddPdf* pdf_Bs2DsDsstPiRho_PIDK = NULL;
        name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode+"_PIDK";
	pdf_Bs2DsDsstPiRho_PIDK = new RooAddPdf( name.Data(),
						 name.Data(),
						 RooArgList(*pdf_Bs2DsPi_PIDK, *pdf_Bs2DsstPi_PIDK,*pdf_Bs2DsRho_PIDK),// *pdf_Bs2DsstRho_PIDK),
						 RooArgList(g2_f1,g2_f2), rec); //,g2_f3), rec); 
						 
	*/
        RooProdPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
        name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode+"_Tot";
        pdf_Bs2DsDsstPiRho_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs2DsDsstPiRho,*pdf_Bs2DsDsstPiRho_Ds, *pdf_Bs2DsDsstPiRho_PIDK));

        if( pdf_Bs2DsDsstPiRho_Tot != NULL ){
          if (debug == true) cout<<"Create "<<pdf_Bs2DsDsstPiRho_Tot->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot create PDF"<<endl;}

	RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
	name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
	epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho-> GetTitle(), 
						*pdf_Bs2DsDsstPiRho_Tot  , nBs2DsDsstPiRhoEvts   );
	if (debug == true){ if( epdf_Bs2DsDsstPiRho != NULL ){ cout<<"Create extended "<<epdf_Bs2DsDsstPiRho->GetName()<<endl; }
	  else { cout<<"Cannot create extendend PDF"<<endl;}}
	
	RooProdPdf* pdf_Bs2DsPi_Tot = NULL;
        name="PhysBkgBs2DsPiPdf_m_"+samplemode+"_Tot";
        pdf_Bs2DsPi_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs2DsPi,*pdf_Bs2DsPi_Ds, *pdf_Bs2DsPi_PIDK));

        if( pdf_Bs2DsPi_Tot != NULL ){
          if (debug == true) cout<<"Create "<<pdf_Bs2DsPi_Tot->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot create PDF"<<endl;}

        RooExtendPdf* epdf_Bs2DsPi   = NULL;
        name = "Bs2DsPiEPDF_m_"+samplemode;
        epdf_Bs2DsPi = new RooExtendPdf( name.Data() , pdf_Bs2DsPi-> GetTitle(),
                                                *pdf_Bs2DsPi_Tot  , nBs2DsPiEvts   );
        if (debug == true){ if( epdf_Bs2DsPi != NULL ){ cout<<"Create extended "<<epdf_Bs2DsPi->GetName()<<endl; }
          else { cout<<"Cannot create extendend PDF"<<endl;}}


	//-----------------------------------------//
	if (debug == true){
	  cout<<"---------------  Group 3 -----------------"<<endl;
	  cout<<"Lb->Dspi"<<endl;
          cout<<"Lb->Dsstpi"<<endl;
	}

	RooKeysPdf* pdf_Lb2DsstP = NULL;
	name = "PhysBkgLb2DsstpPdf_m_both";
	pdf_Lb2DsstP = (RooKeysPdf*)workID->pdf(name.Data());
	if (debug == true) {if( pdf_Lb2DsstP != NULL ){ cout<<"Read "<<pdf_Lb2DsstP->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

	RooKeysPdf* pdf_Lb2DsP = NULL;
	name = "PhysBkgLb2DspPdf_m_both";
	pdf_Lb2DsP = (RooKeysPdf*)workID->pdf(name.Data());
	if (debug == true){ if( pdf_Lb2DsP != NULL ){ cout<<"Read "<<pdf_Lb2DsP->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

	RooAddPdf* pdf_Lb2DsDsstP = NULL;
	name = "PhysBkgLb2DsDsstPPdf_m_"+samplemode;
	pdf_Lb2DsDsstP = new RooAddPdf( name.Data(),name.Data(),*pdf_Lb2DsP, *pdf_Lb2DsstP, g3_f1);

	if (debug == true)
	  {
	    if (pdf_Lb2DsDsstP != NULL)
	      { cout<<"Create doubleCB PDF: "<<pdf_Lb2DsDsstP->GetName()<<endl;}
	    else
	      {cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
	  }

	RooAbsPdf* pdf_Lb2DsDsstP_Ds = NULL;
	name = "PhysBkgLb2DsDsstPPdf_m_Ds_"+samplemode;
	pdf_Lb2DsDsstP_Ds = pdf_SignalDs; //new RooCruijff(name.Data(), name.Data(),massDs, meanDs, sigma1Ds, sigma2Ds,alpha1Ds, alpha2Ds);

        if (debug == true)
          {
            if (pdf_Lb2DsDsstP_Ds != NULL)
              { cout<<"Create doubleCB PDF: "<<pdf_Lb2DsDsstP_Ds->GetName()<<endl;}
            else
              {cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
          }
	
	RooAddPdf* pdf_Lb2Dsp_PIDK = NULL;
	RooAddPdf* pdf_Lb2Dsp_PIDK1 = NULL;
	RooAddPdf* pdf_Lb2Dsp_PIDK2 = NULL;

	RooAddPdf* pdf_Lb2Dsstp_PIDK = NULL;
	RooAddPdf* pdf_Lb2Dsstp_PIDK1 = NULL;
	RooAddPdf* pdf_Lb2Dsstp_PIDK2 = NULL;

	if ( pdf_Lb2Dsp_PIDK ) {}
	if ( pdf_Lb2Dsp_PIDK1 ) {}
	if ( pdf_Lb2Dsp_PIDK2 ) {}

	if ( pdf_Lb2Dsstp_PIDK ) {}
	if ( pdf_Lb2Dsstp_PIDK1 ) {}
	if ( pdf_Lb2Dsstp_PIDK2 ) {}

	if ( merge == true )
	  {
	    name = "PIDKTipleGaussian_Lb2Dsp_down";
            pdf_Lb2Dsp_PIDK1 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Lb2Dsp_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2Dsp_PIDK1->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

            name = "PIDKTipleGaussian_Lb2Dsstp_down";
            pdf_Lb2Dsstp_PIDK1 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Lb2Dsstp_PIDK1 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2Dsstp_PIDK1->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    
	    name = "PIDKTipleGaussian_Lb2Dsp_up";
            pdf_Lb2Dsp_PIDK2 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Lb2Dsp_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2Dsp_PIDK2->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

            name = "PIDKTipleGaussian_Lb2Dsstp_up";
            pdf_Lb2Dsstp_PIDK2 = (RooAddPdf*)workID->pdf(name.Data());
            if( pdf_Lb2Dsstp_PIDK2 != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2Dsstp_PIDK2->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	    name = "PIDKTipleGaussian_Lb2Dsp_both";
	    pdf_Lb2Dsp_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Lb2Dsp_PIDK2,*pdf_Lb2Dsp_PIDK1), RooArgList(lumRatio));
	    if( pdf_Lb2Dsp_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2Dsp_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}

	    name = "PIDKTipleGaussian_Lb2Dsstp_both";
            pdf_Lb2Dsstp_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Lb2Dsstp_PIDK2,*pdf_Lb2Dsstp_PIDK1), RooArgList(lumRatio));
            if( pdf_Lb2Dsstp_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2Dsstp_PIDK->GetName()<<endl;}
            else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	  }
	else
	  {
	    name = "PIDKTipleGaussian_Lb2Dsp_"+sam;
	    pdf_Lb2Dsp_PIDK = (RooAddPdf*)workID->pdf(name.Data());
	    if( pdf_Lb2Dsp_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2Dsp_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	    
	    name = "PIDKTipleGaussian_Lb2Dsstp_"+sam;
	    pdf_Lb2Dsstp_PIDK = (RooAddPdf*)workID->pdf(name.Data());
	    if( pdf_Lb2Dsstp_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2Dsstp_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	  }
	RooAddPdf* pdf_Lb2DsDsstP_PIDK = NULL;
        name = "PhysBkgLb2DsDsstPPdf_m_PIDK_"+samplemode;
        pdf_Lb2DsDsstP_PIDK = new RooAddPdf( name.Data(),name.Data(),*pdf_Lb2Dsp_PIDK, *pdf_Lb2Dsstp_PIDK, g3_f1);

        if (debug == true)
          {
            if (pdf_Lb2DsDsstP_PIDK != NULL)
              { cout<<"Create doubleCB PDF: "<<pdf_Lb2DsDsstP_PIDK->GetName()<<endl;}
            else
	      {cout<<"Cannot create doubleCB PDF"<<endl; return NULL;}
          }

	
	RooProdPdf* pdf_Lb2DsDsstP_Tot = NULL;
        name="PhysBkgLb2DsDsstPPdf_m_"+samplemode+"_Tot";
	pdf_Lb2DsDsstP_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Lb2DsDsstP,*pdf_Lb2DsDsstP_Ds, *pdf_Lb2DsDsstP_PIDK ));

	if( pdf_Lb2DsDsstP_Tot != NULL ){
          if (debug == true) cout<<"Create "<<pdf_Lb2DsDsstP_Tot->GetName()<<endl;}
        else { if (debug == true) cout<<"Cannot create PDF"<<endl;}

	RooExtendPdf* epdf_Lb2DsDsstP   = NULL;
	name = "Lb2DsDsstPEPDF_m_"+samplemode;
	epdf_Lb2DsDsstP = new RooExtendPdf( name.Data() , pdf_Lb2DsDsstP   -> GetTitle(), *pdf_Lb2DsDsstP_Tot  , nLb2DsDsstpEvts   );
	if (debug == true) {if( epdf_Lb2DsDsstP != NULL ){ cout<<"Create extended "<<epdf_Lb2DsDsstP->GetName()<<endl; }
	  else { cout<<"Cannot create extendend PDF"<<endl;}}

	//-----------------------------------------//

	RooKeysPdf* pdf_Lb2LcK = NULL;
	name = "PhysBkgLb2LcKPdf_m_both";
	pdf_Lb2LcK = (RooKeysPdf*)work->pdf(name.Data());
	if (debug == true){ if( pdf_Lb2LcK != NULL ){ cout<<"Read "<<pdf_Lb2LcK->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}

	RooKeysPdf* pdf_Lb2LcK_Ds = NULL;
	name = "PhysBkgLb2LcKPdf_m_both_Ds";
	pdf_Lb2LcK_Ds = (RooKeysPdf*)work->pdf(name.Data());
	if (debug == true){ if( pdf_Lb2LcK != NULL ){ cout<<"Read "<<pdf_Lb2LcK_Ds->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
	
	RooAbsPdf* pdf_Lb2LcK_PIDK = NULL;
	RooAbsPdf* pdf_Lb2LcK_PIDK1 = NULL;
	RooAbsPdf* pdf_Lb2LcK_PIDK2 = NULL;
	
	if ( pdf_Lb2LcK_PIDK ) {}
	if ( pdf_Lb2LcK_PIDK1 ) {}
	if ( pdf_Lb2LcK_PIDK2 ) {}


	if ( merge == true )
	  {
	    name = "PIDshape_Lb2LcK_down";
	    pdf_Lb2LcK_PIDK1 = GetRooBinned1DFromWorkspace(workID, name, debug); //(RooAddPdf*)workID->pdf(name.Data());
            
	    name = "PIDshape_Lb2LcK_up";
	    pdf_Lb2LcK_PIDK2 = GetRooBinned1DFromWorkspace(workID, name, debug); //(RooAddPdf*)workID->pdf(name.Data());
            
	    name = "PIDKShape_dCB_Lb2LcK_both";
            pdf_Lb2LcK_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Lb2LcK_PIDK2,*pdf_Lb2LcK_PIDK1), RooArgList(lumRatio));
            if( pdf_Lb2LcK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2LcK_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	  }
	else
	  {
	    name = "PIDKshape_Lb2LcK_"+sam;
	    pdf_Lb2LcK_PIDK = GetRooBinned1DFromWorkspace(workID, name, debug); //(RooAddPdf*)workID->pdf(name.Data());
	    if( pdf_Lb2LcK_PIDK != NULL ){ if (debug == true) cout<<"Read "<<pdf_Lb2LcK_PIDK->GetName()<<endl;}
	    else { if (debug == true) cout<<"Cannot read PDF"<<endl;}
	  }
	RooProdPdf* pdf_Lb2LcK_Tot = NULL;
	name="PhysBkgLb2LcKPdf_m_"+samplemode+"_Tot";
        pdf_Lb2LcK_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Lb2LcK,*pdf_Lb2LcK_Ds,*pdf_Lb2LcK_PIDK));

        if( pdf_Lb2LcK_Tot != NULL ){
          if (debug == true) cout<<"Create "<<pdf_Lb2LcK_Tot->GetName()<<endl;}
	else { if (debug == true) cout<<"Cannot create PDF"<<endl;}

	RooExtendPdf* epdf_Lb2LcK = NULL;
	name = "Lb2LcKEPDF_m_"+samplemode;
	epdf_Lb2LcK = new RooExtendPdf(name.Data() , pdf_Lb2LcK->GetTitle(), *pdf_Lb2LcK_Tot, nLb2LcKEvts );
	if (debug == true) {if( epdf_Lb2LcK != NULL ){ cout<<"Create extended "<<epdf_Lb2LcK->GetName()<<endl;}
	  else { cout<<"Cannot create extendend PDF"<<endl;}}

	
	//--------------------------------- FULL PDF --------------------------//
	
	RooAbsPdf* pdf_totBkg = NULL;
	name = "BkgEPDF_m_"+samplemode;
	pdf_totBkg = new RooAddPdf( name.Data(), name.Data(),
				    RooArgList(*epdf_combBkg,
					       *epdf_Bs2DsDsstPiRho,
					       *epdf_Bs2DsPi,
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

  RooAddPdf* GetRooAddPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug) {

    RooAddPdf* pdf = NULL;
    pdf = (RooAddPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf != NULL ){ cout<<"Read "<<pdf->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf;

  }

  RooAbsPdf* GetRooBinned1DFromWorkspace(RooWorkspace* work, TString& name, bool debug)
  {
    RooBinned1DQuinticBase<RooAbsPdf>* pdf = NULL;
    pdf = (RooBinned1DQuinticBase<RooAbsPdf>*)work->pdf(name.Data());
    RooAbsPdf* pdf2 = pdf;
    if (debug == true) {if( pdf2 != NULL ){ cout<<"Read "<<pdf2->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf2;
  }

}
