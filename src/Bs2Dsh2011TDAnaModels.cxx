

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
    alpha1Var = new RooRealVar( Form( "DblCBPDF_alpha1_%s_%s", bName, prefix ), Form( "'%s' %s DblCB PDF in %s - alpha1", prefix, 
										      bName, obs.GetName() ), alpha1);
    CheckVar( alpha1Var, debug );
    
    RooRealVar* alpha2Var = NULL;
    alpha2Var = new RooRealVar( Form( "DblCBPDF_alpha2_%s_%s", bName, prefix ),Form( "'%s' %s DblCB PDF in %s - alpha2", prefix, 
										     bName, obs.GetName() ),alpha2);
    CheckVar( alpha2Var, debug );

    RooRealVar* n1Var = NULL;
    n1Var =  new RooRealVar( Form( "DblCBPDF_n1_%s_%s", bName, prefix ), Form( "'%s' %s DblCB PDF in %s - n1", prefix, bName, obs.GetName() ), n1);
    CheckVar( n1Var, debug );

    RooRealVar* n2Var = NULL; 
    n2Var = new RooRealVar( Form("DblCBPDF_n2_%s_%s", bName, prefix ),Form( "'%s' %s DblCB PDF in %s - n2",prefix, bName, obs.GetName() ), n2);
    CheckVar( n2Var, debug); 

    RooRealVar* fracVar = NULL;
    fracVar = new RooRealVar( Form( "DblCBPDF_frac_%s_%s", bName, prefix ), Form( "'%s' %s DblCB PDF in %s - frac", prefix, bName, obs.GetName() ), frac);
    CheckVar( fracVar, debug );

    // ------------------------------------------ Create Single CB ----------------------------------------------------//
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Signle CB ---------------"<<endl;
    RooCBShape* pdf1 = NULL; 
    pdf1 = new RooCBShape( Form( "DblCBPDF_CB1_%s_%s", bName, prefix ), Form( "'%s' %s CB1 PDF in %s", prefix, bName, obs.GetName() ),
			   obs,meanVar, sigma1Var, *alpha1Var, *n1Var);
    CheckPDF( pdf1, debug ); 

    RooCBShape* pdf2 = NULL;
    pdf2 = new RooCBShape( Form( "DblCBPDF_CB2_%s_%s", bName, prefix ),Form( "'%s' %s CB2 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,meanVar, sigma2Var, *alpha2Var, *n2Var);
    CheckPDF( pdf2, debug);

    // ------------------------------------------ Create Double CB ----------------------------------------------------// 
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblCBPDF_%s_%s", bName, prefix ),Form( "'%s' %s DbleCB PDF in %s", prefix, bName, obs.GetName() ),
                                    *pdf1, *pdf2, *fracVar);
    CheckPDF( pdf, debug);
    
    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//

    RooExtendPdf* epdf = NULL;
    epdf = new RooExtendPdf( Form( "SigEPDF_%s", prefix ),Form( "SigEPDF_%s", prefix ),*pdf, nEvents);
    CheckPDF( epdf, debug );
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
    CheckPDF( pdf1, debug );

    RooCBShape* pdf2 = NULL;
    pdf2 = new RooCBShape( Form( "DblCBPDF%s%s_CB2", bName, prefix ),Form( "'%s' %s CB2 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,mean, sigma2, alpha2, n2);
    CheckPDF( pdf2, debug ); 

    // ------------------------------------------ Create Double CB ----------------------------------------------------//
    
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblCBPDF%s%s", bName, prefix ),Form( "'%s' %s DbleCB PDF in %s", prefix, bName, obs.GetName() ),
			 *pdf1, *pdf2, frac);
    CheckPDF( pdf, debug ); 

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
        cout<<"--------------- Create Single CB ---------------"<<endl;
      }
    RooCBShape* pdf1 = NULL;
    pdf1 = new RooCBShape( Form( "DblCBPDF%s_CB1", prefix ), Form( "'%s' %s CB1 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,mean, sigma1, alpha1, n1);
    CheckPDF( pdf1, debug ); 

    RooCBShape* pdf2 = NULL;
    pdf2 = new RooCBShape( Form( "DblCBPDF%s_CB2", prefix ),Form( "'%s' %s CB2 PDF in %s", prefix, bName, obs.GetName() ),
                           obs,mean, sigma2, alpha2, n2);
    CheckPDF( pdf2, debug);

    // ------------------------------------------ Create Double CB ----------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblCBPDF%s", prefix ),Form( "'%s' %s DbleCB PDF in %s", prefix, bName, obs.GetName() ), *pdf1, *pdf2, frac);
    CheckPDF( pdf, debug );

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
        cout<<"--------------- Create Single Gaussian ---------------"<<endl;
      }
    RooGaussian* pdf1 = NULL;
    pdf1 = new RooGaussian( Form( "DblGPDF%s_G1", prefix ), Form( "'%s' %s G1 PDF in %s", prefix, bName, obs.GetName() ), obs, mean, sigma1);
    CheckPDF( pdf1, debug);

    RooGaussian* pdf2 = NULL;
    pdf2 = new RooGaussian( Form( "DblGPDF%s_G2", prefix ),Form( "'%s' %s G2 PDF in %s", prefix, bName, obs.GetName() ), obs,mean, sigma2);
    CheckPDF( pdf2, debug);

    // ------------------------------------------ Create Double CB ----------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblGPDF%s", prefix ),Form( "'%s' %s DbleGaussian PDF in %s", prefix, bName, obs.GetName() ), *pdf1, *pdf2, frac);
    CheckPDF( pdf, debug); 

    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//
    
    RooExtendPdf* epdf = NULL;
    if (extendend == true)
      {
	epdf = new RooExtendPdf( Form( "SigGEPDF_%s", prefix ),Form( "SigGEPDF_%s", prefix ),*pdf, nEvents);
	CheckPDF( epdf, debug); 
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
        cout<<"--------------- Create Single Gaussian ---------------"<<endl;
      }
    RooGaussian* pdf1 = NULL;
    pdf1 = new RooGaussian( Form( "DblGPDF%s_G1", prefix ), Form( "'%s' %s G1 PDF in %s", prefix, bName, obs.GetName() ),  obs,mean, sigma1);
    CheckPDF( pdf1, debug );

    RooGaussian* pdf2 = NULL;
    pdf2 = new RooGaussian( Form( "DblGPDF%s_G2", prefix ),Form( "'%s' %s G2 PDF in %s", prefix, bName, obs.GetName() ), obs,mean, sigma2);
    CheckPDF( pdf2, debug);

    // ------------------------------------------ Create Double CB ----------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblGPDF%s", prefix ),Form( "'%s' %s DbleGaussian PDF in %s", prefix, bName, obs.GetName() ),  *pdf1, *pdf2, frac);
    CheckPDF( pdf, debug );

    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//

    RooExtendPdf* epdf = NULL;

    if (extendend == true)
      {
        epdf = new RooExtendPdf( Form( "SigGEPDF_%s", prefix ),Form( "SigGEPDF_%s", prefix ),*pdf, nEvents);
        CheckPDF( epdf, debug); 
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
			 TString& samplemode,
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
    name = "BdDsX_alpha1_"+samplemode;
    alpha1Var = new RooRealVar( name.Data(), name.Data(), alpha1);
    CheckVar( alpha1Var, debug);

    RooRealVar* alpha2Var = NULL;
    name = "BdDsX_alpha2_"+samplemode;
    alpha2Var = new RooRealVar( name.Data(), name.Data(),alpha2);
    CheckVar( alpha2Var, debug);

    RooRealVar* n1Var = NULL;
    name = "BdDsX_n1_"+samplemode;
    n1Var =  new RooRealVar( name.Data(), name.Data(), n1);
    CheckVar( n1Var, debug);

    RooRealVar* n2Var = NULL;
    name = "BdDsX_n2_"+samplemode;
    n2Var = new RooRealVar( name.Data(), name.Data(), n2);
    CheckVar( n2Var, debug);

    RooRealVar* fracVar = NULL;
    name = "BdDsX_frac_"+samplemode;
    fracVar = new RooRealVar( name.Data(), name.Data(), frac);
    CheckVar( fracVar, debug);

    // ------------------------------------------ Create Single CB ----------------------------------------------------//                                  
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Signle CB ---------------"<<endl;
    RooCBShape* pdf1 = NULL;
    name = "BdDsX_CB1_"+samplemode;
    pdf1 = new RooCBShape( name.Data(), name.Data(), obs,meanVar, sigma1Var, *alpha1Var, *n1Var);
    CheckPDF( pdf1, debug);

    RooCBShape* pdf2 = NULL;
    name = "BdDsX_CB2_"+samplemode;
    pdf2 = new RooCBShape( name.Data() , name.Data() ,obs,meanVar, sigma2Var, *alpha2Var, *n2Var);
    CheckPDF( pdf2, debug);

    // ------------------------------------------ Create Double CB ----------------------------------------------------//                                  
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB ---------------"<<endl;
    RooAddPdf* pdf = NULL;
    TString n="PhysBkg"+namemode+"Pdf_m_"+samplemode;
    pdf = new RooAddPdf( n.Data(),n.Data(),*pdf1, *pdf2, *fracVar);
    CheckPDF( pdf, debug);
 
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

    if ( toys ) {}
    TString m = "";
    TString name = "";

    TString sam = CheckPolarity(samplemode,debug);
    TString Mode = CheckDMode(samplemode,debug);
    if ( Mode == "" ) { Mode = CheckKKPiMode(samplemode, debug); }

    RooAddPdf* pdf_combBkg = NULL;
    pdf_combBkg = ObtainComboBs(mass, cB1Var, cB2Var, fracComb, Mode, debug);

    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;

    RooAbsPdf* pdf_Bd2DPi = NULL;
    m = "Bd2DPi";
    pdf_Bd2DPi = ObtainMassShape(work, m, false, lumRatio, debug);
    
    RooAbsPdf* pdf_Bs2DsRho = NULL;
    m = "Bs2DsRho";
    pdf_Bs2DsRho = ObtainMassShape(work, m, false, lumRatio, debug);

    RooAbsPdf* pdf_Bs2DsK = NULL;
    m = "Bs2DsK";
    pdf_Bs2DsK = ObtainMassShape(work, m, false, lumRatio, debug);

    RooAbsPdf* pdf_Bs2DsstRho = NULL;
    m = "Bs2DsstRho";
    pdf_Bs2DsstRho = ObtainMassShape(work, m, false, lumRatio, debug);

    RooAbsPdf* pdf_Bs2DsstPi = NULL;
    m = "Bs2DsstPi";
    pdf_Bs2DsstPi = ObtainMassShape(work, m, false, lumRatio, debug);

    RooAbsPdf* pdf_Bd2DsstPi = NULL;
    m = "Bd2DsstPi";
    pdf_Bd2DsstPi = ObtainMassShape(work, m, false, lumRatio, debug);

    RooAbsPdf* pdf_Lb2LcPi = NULL;
    m = "Lb2LcPi";
    pdf_Lb2LcPi = ObtainMassShape(work, m, false, lumRatio, debug);
    
    RooAbsPdf* pdf_Bd2DRho = NULL;
    m = "Bd2DRho";
    pdf_Bd2DRho = ObtainMassShape(work, m, false, lumRatio, debug);

    RooAbsPdf* pdf_Bd2DstPi = NULL;
    m = "Bd2DstPi";
    pdf_Bd2DstPi = ObtainMassShape(work, m, false, lumRatio, debug);

    // --------------------------------- Create RooAddPdf -------------------------------------------------//

    Bool_t rec=true;
    RooAddPdf* pdf_Bs2DsDsstPiRho = NULL;
    name = "PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode;
    pdf_Bs2DsDsstPiRho = new RooAddPdf( name.Data(),
					name.Data(),
					RooArgList(*pdf_Bs2DsstPi,*pdf_Bs2DsRho,*pdf_Bs2DsstRho),
					RooArgList(g1_f1,g1_f2), rec
					);
    CheckPDF(pdf_Bs2DsDsstPiRho);
   
    //----------------------------------- Create Extended model ----------------------------------------------//
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Extended model ---------------"<<endl;
    
    RooExtendPdf* epdf_combBkg   = NULL;
    name = "CombBkgEPDF_m_"+samplemode;
    epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg  , nCombBkgEvts   );
    CheckPDF( epdf_combBkg, debug );

    RooExtendPdf* epdf_Bd2DPi = NULL;
    name = "Bd2DPiEPDF_m_"+samplemode;
    epdf_Bd2DPi = new RooExtendPdf( name.Data(),pdf_Bd2DPi->GetTitle(), *pdf_Bd2DPi, nBd2DPiEvts);
    CheckPDF( epdf_Bd2DPi, debug ); 
    
    RooExtendPdf* epdf_BdDsPi = NULL;
    name = "Bd2DsPiEPDF_m_"+samplemode;
    epdf_BdDsPi = new RooExtendPdf(name.Data() , pdf_BdDsPi->GetTitle(), *pdf_BdDsPi, nBdDsPi );
    CheckPDF( epdf_BdDsPi, debug ); 

    RooExtendPdf* epdf_Bd2DsstPi = NULL;
    name = "Bd2DsstPiEPDF_m_"+samplemode;
    epdf_Bd2DsstPi = new RooExtendPdf(name.Data() , pdf_Bd2DsstPi->GetTitle(), *pdf_Bd2DsstPi, nBdDsstPi );
    CheckPDF( epdf_Bd2DsstPi, debug ); 

    RooExtendPdf* epdf_Lb2LcPi = NULL;
    name = "Lb2LcPiEPDF_m_"+samplemode;
    epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi->GetTitle(), *pdf_Lb2LcPi, nLb2LcPiEvts );
    CheckPDF( epdf_Lb2LcPi, debug ); 

    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho-> GetTitle(), *pdf_Bs2DsDsstPiRho  , nBs2DsDsstPiRhoEvts);
    CheckPDF( epdf_Bs2DsDsstPiRho, debug ); 

    RooExtendPdf* epdf_Bd2DstPi = NULL;
    name = "Bd2DstPiEPDF_m_"+samplemode;
    epdf_Bd2DstPi = new RooExtendPdf( name.Data() , pdf_Bd2DstPi-> GetTitle(), *pdf_Bd2DstPi  , nBd2DstPiEvts );
    CheckPDF( epdf_Bd2DstPi, debug ); 

    RooExtendPdf* epdf_Bd2DRho = NULL;
    name = "Bd2DRhoEPDF_m_"+samplemode;
    epdf_Bd2DRho= new RooExtendPdf( name.Data() , pdf_Bd2DRho-> GetTitle(), *pdf_Bd2DRho  , nBd2DRhoEvts );
    CheckPDF( epdf_Bd2DRho, debug ); 
    
    RooExtendPdf* epdf_Bs2DsK = NULL;
    name = "Bs2DsKEPDF_m_"+samplemode;
    epdf_Bs2DsK = new RooExtendPdf(name.Data() , pdf_Bs2DsK->GetTitle(), *pdf_Bs2DsK, nBs2DsKEvts );
    CheckPDF( epdf_Bs2DsK , debug ); 
    
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
					   *epdf_Bs2DsK));
  
    if (debug == true)
      {
	cout<<endl;
	if( pdf_totBkg != NULL ){ cout<<" ------------- CREATED TOTAL BACKGROUND PDF: SUCCESFULL------------"<<endl; }
	else { cout<<" ---------- CREATED TOTAL BACKGROUND PDF: FAILED ----------------"<<endl;}
      }
    return pdf_totBkg;
  }

  //===============================================================================
  // Read Bs (or Ds for dsMass == true ) shape from workspace
  //===============================================================================
  
  RooAbsPdf* ObtainMassShape(RooWorkspace* work,
                             TString& mode,
			     bool dsMass,
			     RooRealVar& lumRatio,
			     bool debug)
  {
    RooAbsPdf* pdf_Mass = NULL;
    RooAbsPdf* pdf_Mass1 = NULL;
    RooAbsPdf* pdf_Mass2 = NULL;

    TString name = "";
    TString Ds = "";
    if (dsMass == true ) { Ds = "_Ds"; }

    if ( mode == "Bd2DPi")
      {
        
	name = "PhysBkg"+mode+"Pdf_m_down_kpipi"+Ds;
	pdf_Mass1 = (RooKeysPdf*)work->pdf(name.Data());
	CheckPDF( pdf_Mass1, debug);
	
        name = "PhysBkg"+mode+"Pdf_m_up_kpipi"+Ds;
	pdf_Mass2 = (RooKeysPdf*)work->pdf(name.Data());
	CheckPDF( pdf_Mass2, debug);

	name = "PhysBkg"+mode+"Pdf_m_both_kpipi"+Ds;
        pdf_Mass = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Mass2,*pdf_Mass1), RooArgList(lumRatio));
      }
    else if ( mode.Contains("BsDsPi") == true or mode.Contains("Bs2DsPi") )
      {
	TString sam = CheckPolarity(mode,debug);
	TString dsfs = CheckDMode(mode,debug);
	if ( dsfs == "" ) { dsfs = CheckKKPiMode(mode, debug); }

	name = "PhysBkgBs2DsPiPdf_m_down_"+dsfs+Ds;
        pdf_Mass1 = (RooKeysPdf*)work->pdf(name.Data());
	CheckPDF( pdf_Mass1, debug);

	name = "PhysBkgBs2DsPiPdf_m_up_"+dsfs+Ds;
        pdf_Mass2 = (RooKeysPdf*)work->pdf(name.Data());
        CheckPDF( pdf_Mass2, debug);

	name = "PhysBkgBs2DsPiPdf_m_both_"+dsfs+Ds;
        pdf_Mass = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Mass2,*pdf_Mass1), RooArgList(lumRatio));
      }
    else
      {
	name = "PhysBkg"+mode+"Pdf_m_both"+Ds;
        pdf_Mass = (RooKeysPdf*)work->pdf(name.Data());
        
      }
    CheckPDF( pdf_Mass, debug);
    return pdf_Mass;
  }

  //===============================================================================
  // Read PIDK shape from workspace
  //===============================================================================

  RooAbsPdf* ObtainPIDKShape(RooWorkspace* work,
			     TString& mode,
			     TString& pol,
			     RooRealVar& lumRatio,
			     bool DsMode,
			     bool debug)
  {
    RooAbsPdf* pdf_PIDK = NULL;
    RooAbsPdf* pdf_PIDK1 = NULL;
    RooAbsPdf* pdf_PIDK2 = NULL;

    TString name = "";

    if ( pdf_PIDK ) {}
    if ( pdf_PIDK1 ) {}
    if ( pdf_PIDK2 ) {}

    TString dsFinalState = "";
    if ( DsMode == true ) 
      { 
	TString dsFS = CheckDMode(mode,debug);
	if ( dsFS == "" ) { dsFS = CheckKKPiMode(mode, debug); }
	if ( dsFS != "" ) { dsFinalState = "_"+dsFS;}

	if( mode.Contains("DsPi") == true ) { mode = "Bs2DsPi";}
	else if ( mode.Contains("DsK") == true ) { mode = "Bs2DsK";}
      }
    
    if ( pol == "both")
      {
        name ="PIDKShape_"+mode+"_down"+dsFinalState; 
        pdf_PIDK1 = GetRooBinned1DFromWorkspace(work, name, debug);

        name ="PIDKShape_"+mode+"_up"+dsFinalState; 
        pdf_PIDK2 = GetRooBinned1DFromWorkspace(work, name, debug);

        name = "PIDKShape_"+mode+"_both"+dsFinalState;
        pdf_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_PIDK2,*pdf_PIDK1), RooArgList(lumRatio));
      }
    else
      {
        name = "PIDKShape_"+mode+"_"+pol+dsFinalState;
        pdf_PIDK = (RooAddPdf*)work->pdf(name.Data());
      }

    CheckPDF( pdf_PIDK, debug );    
    return pdf_PIDK;
  }

  
  //===============================================================================
  // Create RooProdPdf with (Bs, Ds, PIDK) shapes from workspace
  //===============================================================================

  RooProdPdf* ObtainRooProdPdfForMDFitter(RooWorkspace* work,
					  TString& mode,
					  TString& pol,
					  RooRealVar& lumRatio,
					  RooAbsPdf* pdf_DsMass,
					  bool debug)
  {

    RooAbsPdf* pdf_Bs = NULL;
    RooAbsPdf* pdf_Ds = NULL;
    RooAbsPdf* pdf_PIDK = NULL;

    TString name = "";

    pdf_Bs = ObtainMassShape(work, mode, false, lumRatio, debug);    

    if ( pdf_DsMass == NULL )
      {
        pdf_Ds = ObtainMassShape(work, mode, true,  lumRatio, debug);
      }
    else
      {
	pdf_Ds = pdf_DsMass;
      }

    if ( mode.Contains("Bs2DsPi") == true || mode.Contains("Bs2DsK") ==true )
      {
	pdf_PIDK = ObtainPIDKShape(work, mode, pol, lumRatio, true, debug);
      }
    else
      {
        pdf_PIDK = ObtainPIDKShape(work, mode, pol, lumRatio, false, debug);
      }

    RooProdPdf* pdf_Tot = NULL;
    name="PhysBkg"+mode+"Pdf_m_"+pol+"_Tot";
    pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs,*pdf_Ds,*pdf_PIDK));
    CheckPDF( pdf_Tot, debug );

    return pdf_Tot;
  }

  //===============================================================================
  // Create RooProdPdf with (Bs mass, Ds mass, PIDK, time) shapes from workspace
  //===============================================================================

  RooProdPdf* ObtainRooProdPdfForFullFitter(RooWorkspace* work,
                                            TString& mode,
                                            TString& pol,
                                            RooRealVar& lumRatio,
                                            RooAbsPdf* pdf_Time,
                                            RooAbsPdf* pdf_DsMass,
                                            bool debug)
  {
    RooAbsPdf* pdf_Bs = NULL;
    RooAbsPdf* pdf_Ds = NULL;
    RooAbsPdf* pdf_PIDK = NULL;

    pdf_Bs = ObtainMassShape(work, mode, false, lumRatio, debug);
    if ( pdf_DsMass == NULL )
      {
	pdf_Ds = ObtainMassShape(work, mode, true,  lumRatio, debug);
      }
    else
      {
	pdf_Ds = pdf_DsMass;
      }

    if ( mode.Contains("Bs2DsPi") == true || mode.Contains("Bs2DsK") == true )
      {
        pdf_PIDK = ObtainPIDKShape(work, mode, pol, lumRatio, true, debug);
      }
    else
      {
        pdf_PIDK = ObtainPIDKShape(work, mode, pol, lumRatio, false, debug);
      }

    RooProdPdf* pdf_Tot = NULL;
    TString name="PhysBkg"+mode+"Pdf_m_"+pol+"_Tot";
    pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs,*pdf_Ds,*pdf_PIDK,*pdf_Time));
    CheckPDF( pdf_Tot, debug );

    return pdf_Tot;
  }

  
  //===============================================================================
  // Create combinatorial background shape for Ds mass: double exponential
  //===============================================================================

  RooAddPdf* ObtainComboBs(RooAbsReal& mass,
			   RooRealVar& cBVar,
			   RooRealVar& cB2Var,
			   RooRealVar& fracBsComb,
			   TString& Mode,
			   bool debug)
  {
    RooExponential* pdf_combBkg1 = NULL;
    TString name="CombBkgPDF1_m_"+Mode;
    pdf_combBkg1 = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, cBVar );

    RooExponential* pdf_combBkg2 = NULL;
    name="CombBkgPDF2_m_"+Mode;
    pdf_combBkg2 = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, cB2Var );

    RooAddPdf* pdf_combBkg = NULL;
    name="CombBkgPDF_"+Mode;
    pdf_combBkg = new RooAddPdf( name.Data(), name.Data(),  RooArgList(*pdf_combBkg1,*pdf_combBkg2), fracBsComb);
    
    CheckPDF( pdf_combBkg, debug);
    return pdf_combBkg;
  }

  //===============================================================================
  // Create combinatorial background shape for Ds mass:
  //     exponential + signal double CB.
  //===============================================================================
  
  RooAddPdf* ObtainComboDs(RooAbsReal& massDs,
			   RooRealVar& cDVar,
			   RooRealVar& fracDsComb,
			   RooAbsPdf* pdf_SignalDs,
			   TString& Mode,
			   bool debug)
  {
    RooExponential* pdf_combBkg_slope_Ds = NULL;
    TString name="CombBkgPDF_slope_"+Mode+"_Ds";
    pdf_combBkg_slope_Ds = new RooExponential( name.Data(), name.Data(), massDs, cDVar );

    RooAddPdf* pdf_combBkg_Ds = NULL;
    name="CombBkgPDF_"+Mode+"_Ds";
    pdf_combBkg_Ds = new RooAddPdf( name.Data(), name.Data(),  RooArgList(*pdf_combBkg_slope_Ds,*pdf_SignalDs), fracDsComb );
    
    CheckPDF( pdf_combBkg_Ds, debug);
    return pdf_combBkg_Ds;
  }


  //===============================================================================
  // Background 2D model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsPi_BKG_MDFitter( RooAbsReal& mass,
					 RooAbsReal& massDs,
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
    TString name="";
    RooRealVar fake_g1_f2 = g1_f2;
    RooRealVar fake_BdDsPi = nBdDsPi;

    TString m = "";
    TString sam = CheckPolarity(samplemode,debug);
    TString Mode = CheckDMode(samplemode,debug);
    if ( Mode == "" ) { Mode = CheckKKPiMode(samplemode, debug); }

    //RooAbsPdf* pdf_BdDsPi_Ds = NULL;
    //pdf_BdDsPi_Ds = pdf_SignalDs; 
    m = "Bs2DsPi_"+samplemode;
    RooAbsPdf* pdf_BdDsPi_PIDK = NULL;
    pdf_BdDsPi_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, true, debug);
    
    /*
    RooProdPdf* pdf_BdDsPi_Tot = NULL;
    name="PhysBkgBd2DsPiPdf_m_"+samplemode+"_Tot";
    pdf_BdDsPi_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_BdDsPi,*pdf_BdDsPi_Ds,*pdf_BdDsPi_PIDK));
    CheckPDF(pdf_BdDsPi_Tot, debug);
    
    RooExtendPdf* epdf_BdDsPi = NULL;
    name = "Bd2DsPiEPDF_m_"+samplemode;
    epdf_BdDsPi = new RooExtendPdf(name.Data() , pdf_BdDsPi_Ds->GetTitle(), *pdf_BdDsPi_Tot, nBdDsPi );
    CheckPDF(epdf_BdDsPi, debug);
    */
    
    // -------------------------------- Create Combinatorial Background --------------------------------------------//
   
    if (debug == true) cout<<"---------------  Create combinatorial background PDF -----------------"<<endl;
      
    RooAddPdf* pdf_combBkg = NULL;
    pdf_combBkg = ObtainComboBs(mass, cBVar, cB2Var, fracBsComb, Mode, debug);
    
    RooAddPdf* pdf_combBkg_Ds = NULL;
    pdf_combBkg_Ds = ObtainComboDs(massDs, cDVar, fracDsComb, pdf_SignalDs, Mode, debug); 
        
    RooAbsPdf* pdf_combBkg_PIDK1 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK2 = NULL;
    m = "Comb";
    pdf_combBkg_PIDK1 = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);
    m = "CombK";
    pdf_combBkg_PIDK2 = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);
    
    RooAddPdf* pdf_combBkg_PIDK = NULL;
    name = "ShapePIDKAll_Comb_"+samplemode;
    pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
				      name.Data(),
				      RooArgList(*pdf_combBkg_PIDK1,*pdf_combBkg_PIDK2), fracPIDComb);
    CheckPDF(pdf_combBkg_PIDK,debug);
    
    RooProdPdf* pdf_combBkg_Tot = NULL;
    name="CombBkgPDF_m_"+samplemode+"_Tot";
    pdf_combBkg_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_combBkg,*pdf_combBkg_Ds,*pdf_combBkg_PIDK));
    CheckPDF(pdf_combBkg_Tot, debug);

    RooExtendPdf* epdf_combBkg   = NULL;
    name = "CombBkgEPDF_m_"+samplemode;
    epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg_Tot  , nCombBkgEvts   );
    CheckPDF(epdf_combBkg, debug);


    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;
    
    RooProdPdf* pdf_Bd2DPi_Tot = NULL;
    m = "Bd2DPi";
    pdf_Bd2DPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, lumRatio, NULL, debug);

    RooExtendPdf* epdf_Bd2DPi    = NULL;
    name = "Bd2DPiEPDF_m_"+samplemode;
    epdf_Bd2DPi = new RooExtendPdf( name.Data(),pdf_Bd2DPi_Tot->GetTitle(), *pdf_Bd2DPi_Tot, nBd2DPiEvts);
    CheckPDF(epdf_Bd2DPi, debug);

    //-----------------------------------------//

    RooProdPdf* pdf_Bd2DsstPi_Tot = NULL;
    m = "Bd2DsstPi";
    pdf_Bd2DsstPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, lumRatio, pdf_SignalDs, debug);

    RooExtendPdf* epdf_Bd2DsstPi = NULL;
    name = "Bd2DsstPiEPDF_m_"+samplemode;
    epdf_Bd2DsstPi = new RooExtendPdf(name.Data() , pdf_Bd2DsstPi_Tot->GetTitle(), *pdf_Bd2DsstPi_Tot, nBdDsstPi );
    CheckPDF(epdf_Bd2DsstPi, debug);

    //-----------------------------------------//
    
    RooProdPdf* pdf_Lb2LcPi_Tot = NULL;
    m = "Lb2LcPi";
    pdf_Lb2LcPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, lumRatio, NULL, debug);

    RooExtendPdf* epdf_Lb2LcPi = NULL;
    name = "Lb2LcPiEPDF_m_"+samplemode;
    epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi_Tot->GetTitle(), *pdf_Lb2LcPi_Tot, nLb2LcPiEvts );
    CheckPDF(epdf_Lb2LcPi, debug);

    //-----------------------------------------//

    RooProdPdf* pdf_Bs2DsK_Tot = NULL;
    m = "Bs2DsK";
    pdf_Bs2DsK_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, lumRatio, pdf_SignalDs, debug);

    RooExtendPdf* epdf_Bs2DsK = NULL;
    name = "Bs2DsKEPDF_m_"+samplemode;
    epdf_Bs2DsK = new RooExtendPdf(name.Data() , pdf_Bs2DsK_Tot->GetTitle(), *pdf_Bs2DsK_Tot, nBs2DsKEvts );
    CheckPDF(epdf_Bs2DsK, debug);

    //-----------------------------------------//
    
    RooProdPdf* pdf_Bd2DRho_Tot = NULL;
    m = "Bd2DRho";
    pdf_Bd2DRho_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, lumRatio, NULL, debug);

    RooExtendPdf* epdf_Bd2DRho = NULL;
    name = "Bd2DRhoEPDF_m_"+samplemode;
    epdf_Bd2DRho= new RooExtendPdf( name.Data() , pdf_Bd2DRho_Tot-> GetTitle(), *pdf_Bd2DRho_Tot  , nBd2DRhoEvts );
    CheckPDF(epdf_Bd2DRho, debug);

    //-----------------------------------------//
    
    RooProdPdf* pdf_Bd2DstPi_Tot = NULL;
    m = "Bd2DstPi";
    pdf_Bd2DstPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, lumRatio, NULL, debug);

    RooExtendPdf* epdf_Bd2DstPi = NULL;
    name = "Bd2DstPiEPDF_m_"+samplemode;
    epdf_Bd2DstPi = new RooExtendPdf( name.Data() , pdf_Bd2DstPi_Tot-> GetTitle(), *pdf_Bd2DstPi_Tot  , nBd2DstPiEvts );
    CheckPDF(epdf_Bd2DstPi, debug);

    // --------------------------------- Create RooAddPdf -------------------------------------------------//
    //  Bool_t rec=true;
    /*
    RooAbsPdf* pdf_Bs2DsRho = NULL;
    RooAbsPdf* pdf_Bs2DsRho_PIDK = NULL;
    m = "Bs2DsRho";
    pdf_Bs2DsRho = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Bs2DsRho_PIDK = = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);

    RooAbsPdf* pdf_Bs2DsstRho = NULL;
    RooAddPdf* pdf_Bs2DsstRho_PIDK = NULL;
    m = "Bs2DsstRho";
    pdf_Bs2DsstRho = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Bs2DsRho_PIDK == ObtainPIDKShape(work, m, sam, lumRatio, false, debug);
    */

    RooAbsPdf* pdf_Bs2DsstPi = NULL;
    RooAbsPdf* pdf_Bs2DsstPi_PIDK = NULL;
    m = "Bs2DsstPi";
    pdf_Bs2DsstPi = ObtainMassShape(work, m, false, lumRatio, debug);
    m = "Bs2DsPi_"+samplemode;
    pdf_Bs2DsstPi_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, true, debug);
    
    RooAddPdf* pdf_Bs2DsDsstPiRho = NULL;
    name = "PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode;
    pdf_Bs2DsDsstPiRho = new RooAddPdf( name.Data(),
                                        name.Data(),
                                        RooArgList(*pdf_Bs2DsstPi, *pdf_BdDsPi), //, *pdf_Bs2DsRho), //,*pdf_Bs2DsstRho),
                                        RooArgList(g1_f1) //,g1_f2), rec
                                        );
    CheckPDF(pdf_Bs2DsDsstPiRho, debug);

    
    RooAbsPdf* pdf_Bs2DsDsstPiRho_Ds = NULL;
    pdf_Bs2DsDsstPiRho_Ds = pdf_SignalDs; 
    
    RooAddPdf* pdf_Bs2DsDsstPiRho_PIDK = NULL;
    name = "PhysBkgBs2DsDsstPiRhoPdf_PIDK_"+samplemode;
    pdf_Bs2DsDsstPiRho_PIDK = new RooAddPdf( name.Data(),
					     name.Data(),
					     RooArgList(*pdf_Bs2DsstPi_PIDK,*pdf_BdDsPi_PIDK), //, *pdf_Bs2DsRho_PIDK), //*pdf_Bs2DsstRho_PIDK),
					     RooArgList(g1_f1) //,g1_f2), rec
					     );
    CheckPDF(pdf_Bs2DsDsstPiRho_PIDK, debug);
    
    RooProdPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    name="PhysBkgBs2DsDsstPiPdf_m_"+samplemode+"_Tot";
    pdf_Bs2DsDsstPiRho_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs2DsDsstPiRho,*pdf_Bs2DsDsstPiRho_Ds,*pdf_Bs2DsDsstPiRho_PIDK));
    CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);

    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho-> GetTitle(), *pdf_Bs2DsDsstPiRho_Tot  , nBs2DsDsstPiRhoEvts);
    CheckPDF(epdf_Bs2DsDsstPiRho, debug);

    
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
    CheckPDF( epdf_combBkg, debug );
    
    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho-> GetTitle(), *pdf_Bs2DsDsstPiRho  , nBs2DsDsstPiRhoEvts   );
    CheckPDF( epdf_Bs2DsDsstPiRho, debug ); 

    RooExtendPdf* epdf_Bs2DsDsstKKst   = NULL;
    name = "Bs2DsDsstKKstEPDF_m_"+samplemode;
    epdf_Bs2DsDsstKKst = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstKKst   -> GetTitle(), *pdf_Bs2DsDsstKKst  , nBs2DsDssKKstEvts   );
    CheckPDF( epdf_Bs2DsDsstKKst, debug ); 

    RooExtendPdf* epdf_Lb2DsDsstP   = NULL;
    name = "Lb2DsDsstPEPDF_m_"+samplemode;
    epdf_Lb2DsDsstP = new RooExtendPdf( name.Data() , pdf_Lb2DsDsstP   -> GetTitle(), *pdf_Lb2DsDsstP  , nLb2DsDsstpEvts   );
    CheckPDF( epdf_Lb2DsDsstP, debug ); 

    RooExtendPdf* epdf_Bd2DK = NULL;
    name = "Bd2DKEPDF_m_"+samplemode;
    epdf_Bd2DK = new RooExtendPdf(name.Data() , pdf_Bd2DK->GetTitle(), *pdf_Bd2DK, nBd2DKEvts );
    CheckPDF( epdf_Bd2DK , debug ); 
    
    RooExtendPdf* epdf_Lb2LcK = NULL;
    name = "Lb2LcKEPDF_m_"+samplemode;
    epdf_Lb2LcK = new RooExtendPdf(name.Data() , pdf_Lb2LcK->GetTitle(), *pdf_Lb2LcK, nLb2LcKEvts );
    CheckPDF( epdf_Lb2LcK , debug ); 
    
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

  RooAbsPdf* build_Bs2DsK_BKG_MDFitter(RooAbsReal& mass,
				       RooAbsReal& massDs,
				       RooWorkspace* work,
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
    TString m = "";
    TString name="";

    TString sam = CheckPolarity(samplemode,debug);
    TString Mode = CheckDMode(samplemode,debug);
    if ( Mode == "" ) { Mode = CheckKKPiMode(samplemode, debug); }
  
    RooAbsPdf* pdf_Bd2DsK_PIDK = NULL;
    m = "Bs2DsK_"+samplemode;
    pdf_Bd2DsK_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, true, debug);
        
    // -------------------------------- Create Combinatorial Background --------------------------------------------//                       

    if (debug == true) { cout<<"---------------  Create combinatorial background PDF -----------------"<<endl; }
    
    RooExponential* pdf_combBkg = NULL;
    name="CombBkgPDF_m_"+samplemode;
    pdf_combBkg = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, cBVar);
    CheckPDF(pdf_combBkg, debug);

    RooAddPdf* pdf_combBkg_Ds = NULL;
    pdf_combBkg_Ds = ObtainComboDs(massDs, cDVar, fracComb, pdf_SignalDs, Mode, debug);

    RooAbsPdf* pdf_CombK_PIDK = NULL;
    RooAbsPdf* pdf_CombPi_PIDK = NULL;
    RooAbsPdf* pdf_CombP_PIDK = NULL;
    m = "CombPi";
    pdf_CombPi_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);
    m = "CombK";
    pdf_CombK_PIDK = ObtainPIDKShape(work, m, sam, lumRatio,  false, debug);
    m = "CombP";
    pdf_CombP_PIDK = ObtainPIDKShape(work, m, sam, lumRatio,  false, debug);
    
    RooAddPdf* pdf_combBkg_PIDK = NULL;
    name = "ShapePIDKAll_Comb_"+sam;
    pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
				      name.Data(),
				      RooArgList(*pdf_CombK_PIDK,*pdf_CombPi_PIDK, *pdf_CombP_PIDK), 
				      RooArgList(g4_f1,g4_f2), 
				      true);
    CheckPDF(pdf_combBkg_PIDK, debug);
     
    RooProdPdf* pdf_combBkg_Tot = NULL;
    name="CombBkgPDF_m_"+samplemode+"_Tot";
    pdf_combBkg_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_combBkg,*pdf_combBkg_Ds,*pdf_combBkg_PIDK));
    CheckPDF( pdf_combBkg_Tot, debug ); 

    RooExtendPdf* epdf_combBkg   = NULL;
    name = "CombBkgEPDF_m_"+samplemode;
    epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg_Tot->GetTitle(), *pdf_combBkg_Tot  , nCombBkgEvts   );
    CheckPDF( epdf_combBkg, debug ); 
      
    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//                      

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;
    
    RooProdPdf* pdf_Bd2DK_Tot = NULL;
    m = "Bd2DK";
    pdf_Bd2DK_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, lumRatio, NULL, debug);
  
    RooExtendPdf* epdf_Bd2DK    = NULL;
    name = "Bd2DKEPDF_m_"+samplemode;
    epdf_Bd2DK = new RooExtendPdf( name.Data(),pdf_Bd2DK_Tot->GetTitle(), *pdf_Bd2DK_Tot, nBd2DKEvts);
    CheckPDF( epdf_Bd2DK, debug ); 
    
    //-----------------------------------------//
	
    RooAbsPdf* pdf_Bs2DsKst = NULL;
    RooAbsPdf* pdf_Bs2DsKst_PIDK = NULL;
    m = "Bs2DsKst";
    pdf_Bs2DsKst = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Bs2DsKst_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);

    /*
    RooAbsPdf* pdf_Bs2DsstK = NULL;
    RooAbsPdf* pdf_Bs2DsstK_PIDK = NULL;
    m = "Bs2DsstK";
    pdf_Bs2DsstK = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Bs2DsstK_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);

    RooAbsPdf* pdf_Bs2DsstKst = NULL;
    RooAbsPdf* pdf_Bs2DsstKst_PIDK = NULL;
    m = "Bs2DsstKst";
    pdf_Bs2DsstKst = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Bs2DsstKst_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);
    */
 
    if (debug == true)
      {
	cout<<endl;
	cout<<"---------------  Create Groups -----------------"<<endl;
	cout<<"---------------  Group 1 -----------------"<<endl;
	cout<<"Bd->DsK"<<endl;
	//cout<<"Bs->Ds*K"<<endl;
	cout<<"Bs->DsK*"<<endl;
	//cout<<"Bs->Ds*K*"<<endl;
      }

    //Bool_t rec=true; //recursive build

    RooAddPdf* pdf_Bs2DsDsstKKst = NULL;
    name = "PhysBkgBs2DsDsstKKstPdf_m_"+samplemode;
    pdf_Bs2DsDsstKKst = new RooAddPdf( name.Data(),
					   name.Data(),
					   RooArgList(*pdf_Bd2DsK, *pdf_Bs2DsKst), //*pdf_Bs2DsstK,*pdf_Bs2DsstKst),
					   RooArgList(g1_f1) //g1_f2, g1_f3), 
					   //rec
					   );
    CheckPDF(pdf_Bs2DsDsstKKst, debug);

    RooAbsPdf* pdf_Bs2DsDsstKKst_Ds = NULL;
    pdf_Bs2DsDsstKKst_Ds = pdf_SignalDs; 
	
    RooAddPdf* pdf_Bs2DsDsstKKst_PIDK = NULL;
    name = "PhysBkgBs2DsDsstKKstPdf_m_"+samplemode+"_PIDK";
    pdf_Bs2DsDsstKKst_PIDK = new RooAddPdf( name.Data(),
						name.Data(),
						RooArgList(*pdf_Bd2DsK_PIDK, *pdf_Bs2DsKst_PIDK), //*pdf_Bs2DsstK_PIDK, *pdf_Bs2DsstKst_PIDK),
						RooArgList(g1_f1) //g1_f2, g1_f3), 
						//rec
						);
    CheckPDF(pdf_Bs2DsDsstKKst_PIDK, debug);

    RooProdPdf* pdf_Bs2DsDsstKKst_Tot = NULL;
    name="PhysBkgBs2DsDsstKKstPdf_m_"+samplemode+"_Tot";
    pdf_Bs2DsDsstKKst_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs2DsDsstKKst,*pdf_Bs2DsDsstKKst_Ds,*pdf_Bs2DsDsstKKst_PIDK));
    CheckPDF(pdf_Bs2DsDsstKKst_Tot, debug);

    RooExtendPdf* epdf_Bs2DsDsstKKst = NULL;
    name = "Bs2DsDsstKKstEPDF_m_"+samplemode;
    epdf_Bs2DsDsstKKst = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstKKst->GetTitle(), *pdf_Bs2DsDsstKKst_Tot  , nBs2DsDssKKstEvts   );
    CheckPDF( epdf_Bs2DsDsstKKst, debug );
 
    //-----------------------------------------//

    RooAbsPdf* pdf_Bs2DsstPi = NULL;
    RooAbsPdf* pdf_Bs2DsstPi_PIDK = NULL;
    m = "Bs2DsstPi";
    pdf_Bs2DsstPi = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Bs2DsstPi_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);

    RooAbsPdf* pdf_Bs2DsRho = NULL;
    RooAbsPdf* pdf_Bs2DsRho_PIDK = NULL;
    m = "Bs2DsRho";
    pdf_Bs2DsRho = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Bs2DsRho_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);

    /*
    RooAbsPdf* pdf_Bs2DsstRho = NULL;
    RooAbsPdf* pdf_Bs2DsstRho_PIDK = NULL;
    m = "Bs2DsstRho";
    pdf_Bs2DsstRho = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Bs2DsstRho_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);
    */
   	  
    if (debug == true){
      cout<<"---------------  Group 2 -----------------"<<endl;
      //cout<<"Bs->DsPi"<<endl;
      cout<<"Bs->Ds*Pi"<<endl;
      cout<<"Bs->DsRho"<<endl;
      //cout<<"Bs->Ds*Rho"<<endl;
    }

    /*
      RooAddPdf* pdf_Bs2DsDsstPiRho = NULL;
      name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode;
      pdf_Bs2DsDsstPiRho = new RooAddPdf( name.Data(),
      name.Data(),
      RooArgList(*pdf_Bs2DsPi, *pdf_Bs2DsstPi,*pdf_Bs2DsRho), // *pdf_Bs2DsstRho),
      RooArgList(g2_f1,g2_f2), rec); ///, g2_f3), rec);
    */
    
    RooAddPdf* pdf_Bs2DsDsstPiRho = NULL;
    name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode;
    pdf_Bs2DsDsstPiRho = new RooAddPdf( name.Data(),
					name.Data(),
					RooArgList(*pdf_Bs2DsstPi,*pdf_Bs2DsRho), //*pdf_Bs2DsstRho),
					RooArgList(g2_f1)); ///, g2_f3), rec);
    CheckPDF(pdf_Bs2DsDsstPiRho, debug);

    RooAbsPdf* pdf_Bs2DsDsstPiRho_Ds = NULL;
    pdf_Bs2DsDsstPiRho_Ds = pdf_SignalDs; 	
    
    RooAddPdf* pdf_Bs2DsDsstPiRho_PIDK = NULL;
    name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode+"_PIDK";
    pdf_Bs2DsDsstPiRho_PIDK = new RooAddPdf( name.Data(),
					     name.Data(),
					     RooArgList(*pdf_Bs2DsstPi_PIDK,*pdf_Bs2DsRho_PIDK),// *pdf_Bs2DsstRho_PIDK),
					     RooArgList(g2_f1)); //,g2_f3), rec);
    CheckPDF(pdf_Bs2DsDsstPiRho_PIDK, debug);

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
    CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);

    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho-> GetTitle(), 
					    *pdf_Bs2DsDsstPiRho_Tot  , nBs2DsDsstPiRhoEvts   );
    CheckPDF( epdf_Bs2DsDsstPiRho, debug ); 

    //-----------------------------------------//
    
    RooProdPdf* pdf_Bs2DsPi_Tot = NULL;
    m = "Bs2DsPi_"+samplemode;
    pdf_Bs2DsPi_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, lumRatio, pdf_SignalDs, debug);

    RooExtendPdf* epdf_Bs2DsPi   = NULL;
    name = "Bs2DsPiEPDF_m_"+samplemode;
    epdf_Bs2DsPi = new RooExtendPdf( name.Data() , pdf_Bs2DsPi_Tot-> GetTitle(),
				     *pdf_Bs2DsPi_Tot  , nBs2DsPiEvts   );
    CheckPDF( epdf_Bs2DsPi, debug ); 

    //-----------------------------------------//
    if (debug == true){
      cout<<"---------------  Group 3 -----------------"<<endl;
      cout<<"Lb->Dspi"<<endl;
      cout<<"Lb->Dsstpi"<<endl;
    }
    
    RooAbsPdf* pdf_Lb2DsstP = NULL;
    RooAbsPdf* pdf_Lb2DsstP_PIDK = NULL;
    m = "Lb2Dsstp";
    pdf_Lb2DsstP = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Lb2DsstP_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);

    RooAbsPdf* pdf_Lb2DsP = NULL;
    RooAbsPdf* pdf_Lb2DsP_PIDK = NULL;
    m = "Lb2Dsp";
    pdf_Lb2DsP = ObtainMassShape(work, m, false, lumRatio, debug);
    pdf_Lb2DsP_PIDK = ObtainPIDKShape(work, m, sam, lumRatio, false, debug);

    RooAddPdf* pdf_Lb2DsDsstP = NULL;
    name = "PhysBkgLb2DsDsstPPdf_m_"+samplemode;
    pdf_Lb2DsDsstP = new RooAddPdf( name.Data(),name.Data(),*pdf_Lb2DsP, *pdf_Lb2DsstP, g3_f1);
    CheckPDF( pdf_Lb2DsDsstP, debug );
    
    RooAbsPdf* pdf_Lb2DsDsstP_Ds = NULL;
    pdf_Lb2DsDsstP_Ds = pdf_SignalDs; 

    RooAddPdf* pdf_Lb2DsDsstP_PIDK = NULL;
    name = "PhysBkgLb2DsDsstPPdf_m_PIDK_"+samplemode;
    pdf_Lb2DsDsstP_PIDK = new RooAddPdf( name.Data(),name.Data(),*pdf_Lb2DsP_PIDK, *pdf_Lb2DsstP_PIDK, g3_f1);
    CheckPDF( pdf_Lb2DsDsstP_PIDK, debug );

    RooProdPdf* pdf_Lb2DsDsstP_Tot = NULL;
    name="PhysBkgLb2DsDsstPPdf_m_"+samplemode+"_Tot";
    pdf_Lb2DsDsstP_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Lb2DsDsstP,*pdf_Lb2DsDsstP_Ds, *pdf_Lb2DsDsstP_PIDK ));
    CheckPDF( pdf_Lb2DsDsstP_Tot, debug ); 
    
    RooExtendPdf* epdf_Lb2DsDsstP   = NULL;
    name = "Lb2DsDsstPEPDF_m_"+samplemode;
    epdf_Lb2DsDsstP = new RooExtendPdf( name.Data() , pdf_Lb2DsDsstP->GetTitle(), *pdf_Lb2DsDsstP_Tot  , nLb2DsDsstpEvts   );
    CheckPDF( epdf_Lb2DsDsstP, debug ); 
    
    //-----------------------------------------//
    
    RooProdPdf* pdf_Lb2LcK_Tot = NULL;
    m = "Lb2LcK";
    pdf_Lb2LcK_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, lumRatio, NULL, debug);

    RooExtendPdf* epdf_Lb2LcK = NULL;
    name = "Lb2LcKEPDF_m_"+samplemode;
    epdf_Lb2LcK = new RooExtendPdf(name.Data() , pdf_Lb2LcK_Tot->GetTitle(), *pdf_Lb2LcK_Tot, nLb2LcKEvts );
    CheckPDF( epdf_Lb2LcK , debug );     
	
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

  //===============================================================================
  // Load RooAddPdf from workspace.
  //===============================================================================

  RooAddPdf* GetRooAddPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug) {

    RooAddPdf* pdf = NULL;
    pdf = (RooAddPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf != NULL ){ cout<<"Read "<<pdf->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf;

  }

  //===============================================================================
  // Load RooBinned1DPdf from workspace.
  //===============================================================================

  RooAbsPdf* GetRooBinned1DFromWorkspace(RooWorkspace* work, TString& name, bool debug)
  {
    RooBinned1DQuinticBase<RooAbsPdf>* pdf = NULL;
    pdf = (RooBinned1DQuinticBase<RooAbsPdf>*)work->pdf(name.Data());
    RooAbsPdf* pdf2 = pdf;
    if (debug == true) {if( pdf2 != NULL ){ cout<<"Read "<<pdf2->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf2;
  }

  //===============================================================================
  // Check PDF (whether is null).
  //===============================================================================

  bool CheckPDF(RooAbsPdf* pdf, bool debug)
  {
    if( pdf != NULL )
      { 
	if (debug == true) cout<<"Create/Read "<<pdf->GetName()<<endl;
	return true;
      }
    else 
      { 
	if (debug == true) cout<<"Cannot create/read PDF"<<endl;
	return false;
      }
  }

  //===============================================================================
  // Check RooRealVar (whether is null).
  //===============================================================================

  bool CheckVar(RooRealVar* var, bool debug)
  {
    if (var != NULL)
      {
        if (debug == true) cout<<"Create RooRealVar: "<<var->GetName()<<endl;
	return true;
      }
    else {
      if (debug == true) cout<<"Cannot create RooRealVar"<<endl;
      return false;
    }
  }


}
