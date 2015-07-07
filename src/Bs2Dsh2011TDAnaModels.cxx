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

    //RooExtendPdf* epdf = NULL;
    //epdf = new RooExtendPdf( Form( "SigEPDF_%s", prefix ),Form( "SigEPDF_%s", prefix ),*pdf, nEvents);
    //CheckPDF( epdf, debug );
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
  // Double crystal ball function where sigmas are RooFormulaVar and other  parameters are RooRealVar                                                                                 
  //===============================================================================                                                                                                    

  RooAbsPdf* buildDoubleCBEPDF_sim( RooAbsReal& obs,
                                   RooRealVar& mean,
                                   RooFormulaVar& sigma1,
                                   RooRealVar& alpha1,
                                   RooRealVar& n1,
                                   RooFormulaVar& sigma2,
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
				   TString prefix,
				   TString bName,
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
    pdf1 = new RooGaussian( Form( "DblGPDF%s_G1", prefix.Data() ), Form( "'%s' %s G1 PDF in %s", prefix.Data(), bName.Data(), obs.GetName() ), obs, mean, sigma1);
    CheckPDF( pdf1, debug);

    RooGaussian* pdf2 = NULL;
    pdf2 = new RooGaussian( Form( "DblGPDF%s_G2", prefix.Data() ),Form( "'%s' %s G2 PDF in %s", prefix.Data(), bName.Data(), obs.GetName() ), obs,mean, sigma2);
    CheckPDF( pdf2, debug);

    // ------------------------------------------ Create Double CB ----------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblGPDF%s", prefix.Data() ),Form( "'%s' %s DbleGaussian PDF in %s", prefix.Data(), bName.Data(), obs.GetName() ), *pdf1, *pdf2, frac);
    CheckPDF( pdf, debug); 

    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//
    
    RooExtendPdf* epdf = NULL;
    if (extendend == true)
      {
	epdf = new RooExtendPdf( Form( "SigGEPDF_%s", prefix.Data() ),Form( "SigGEPDF_%s", prefix.Data() ),*pdf, nEvents);
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
                                   TString prefix,
                                   TString bName,
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
    pdf1 = new RooGaussian( Form( "DblGPDF%s_G1", prefix.Data() ), Form( "'%s' %s G1 PDF in %s", prefix.Data(), bName.Data(), obs.GetName() ),  obs,mean, sigma1);
    CheckPDF( pdf1, debug );

    RooGaussian* pdf2 = NULL;
    pdf2 = new RooGaussian( Form( "DblGPDF%s_G2", prefix.Data() ),Form( "'%s' %s G2 PDF in %s", prefix.Data(), bName.Data(), obs.GetName() ), obs,mean, sigma2);
    CheckPDF( pdf2, debug);

    // ------------------------------------------ Create Double CB ----------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB- --------------"<<endl;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( Form( "DblGPDF%s", prefix.Data() ),Form( "'%s' %s DbleGaussian PDF in %s", prefix.Data(), bName.Data(), obs.GetName() ),  *pdf1, *pdf2, frac);
    CheckPDF( pdf, debug );

    // ------------------------------------------ Create Extend Double CB ----------------------------------------------------//

    RooExtendPdf* epdf = NULL;

    if (extendend == true)
      {
        epdf = new RooExtendPdf( Form( "SigGEPDF_%s", prefix.Data() ),Form( "SigGEPDF_%s", prefix.Data() ),*pdf, nEvents);
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


  RooAbsPdf* buildBdDsX( RooAbsReal& obs,
                         RooFormulaVar &meanVar,
                         RooFormulaVar &sigma1Var,
                         RooRealVar &alpha1Var,
                         RooRealVar &n1Var,
                         RooFormulaVar &sigma2Var,
                         RooRealVar &alpha2Var,
                         RooRealVar &n2Var,
                         RooRealVar &fracVar,
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

    // ------------------------------------------ Create Single CB ----------------------------------------------------//                                                                         
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Signle CB ---------------"<<endl;
    RooCBShape* pdf1 = NULL;
    name = "Bd2DsX_CB1_"+samplemode;
    pdf1 = new RooCBShape( name.Data(), name.Data(), obs,meanVar, sigma1Var, alpha1Var, n1Var);
    CheckPDF( pdf1, debug);

    RooCBShape* pdf2 = NULL;
    name = "Bd2DsX_CB2_"+samplemode;
    pdf2 = new RooCBShape( name.Data() , name.Data() ,obs,meanVar, sigma2Var, alpha2Var, n2Var);
    CheckPDF( pdf2, debug);

    // ------------------------------------------ Create Double CB ----------------------------------------------------//                                                                         
    if (debug == true) cout<<endl;
    if (debug == true) cout<<"--------------- Create Double CB ---------------"<<endl;
    RooAddPdf* pdf = NULL;
    TString n="PhysBkg"+namemode+"Pdf_m_"+samplemode;
    pdf = new RooAddPdf( n.Data(),n.Data(),*pdf1, *pdf2, fracVar);
    CheckPDF( pdf, debug);

    return pdf;
  }

  //===============================================================================
  // Read Bs (or Ds for dsMass == true ) shape from workspace
  //===============================================================================
  
  RooAbsPdf* ObtainMassShape(RooWorkspace* work,
                             TString mode,
			     TString year,
			     bool dsMass,
			     RooRealVar& lumRatio,
			     bool debug)
  {
    RooAbsPdf* pdf_Mass = NULL;
    RooAbsPdf* pdf_Mass1 = NULL;
    RooAbsPdf* pdf_Mass2 = NULL;

    TString name = "";
    TString Ds = "";

    TString dsFS = CheckDMode(mode,debug);
    if ( dsFS == "" ) { dsFS = CheckKKPiMode(mode, debug); }
   
    if (dsMass == true ) { Ds = "_Ds"; }
    if ( year.Contains("_")  == false ) { year = "_"+year;} 

    if ( mode.Contains("Bd2DPi")== true && dsFS == "kpipi")
      {
        
	name = "PhysBkgBd2DPiPdf_m_down_kpipi"+year+Ds;
	pdf_Mass1 = (RooKeysPdf*)work->pdf(name.Data());
	CheckPDF( pdf_Mass1, debug);
	
        name = "PhysBkgBd2DPiPdf_m_up_kpipi"+year+Ds;
	pdf_Mass2 = (RooKeysPdf*)work->pdf(name.Data());
	CheckPDF( pdf_Mass2, debug);

	name = "PhysBkgBd2DPiPdf_m_both_kpipi"+year+Ds;
        pdf_Mass = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Mass2,*pdf_Mass1), RooArgList(lumRatio));
      }
    else if ( (mode.Contains("BsDsPi") == true || mode.Contains("Bs2DsPi") ) && dsFS != "" )
      {
	TString sam = CheckPolarity(mode,debug);
	TString dsfs = CheckDMode(mode,debug);
	if ( dsfs == "" ) { dsfs = CheckKKPiMode(mode, debug); }

	name = "PhysBkgBs2DsPiPdf_m_down_"+dsfs+year+Ds;
        pdf_Mass1 = (RooKeysPdf*)work->pdf(name.Data());
	CheckPDF( pdf_Mass1, debug);

	name = "PhysBkgBs2DsPiPdf_m_up_"+dsfs+year+Ds;
        pdf_Mass2 = (RooKeysPdf*)work->pdf(name.Data());
        CheckPDF( pdf_Mass2, debug);

	name = "PhysBkgBs2DsPiPdf_m_both_"+dsfs+year+Ds;
        pdf_Mass = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Mass2,*pdf_Mass1), RooArgList(lumRatio));
      }
    else
      {
	name = "PhysBkg"+mode+"Pdf_m_both"+year+Ds;
        pdf_Mass = (RooKeysPdf*)work->pdf(name.Data());
        
      }
    CheckPDF( pdf_Mass, debug);
    return pdf_Mass;
  }

  //===============================================================================
  // Read PIDK shape from workspace
  //===============================================================================

  RooAbsPdf* ObtainPIDKShape(RooWorkspace* work,
			     TString mode,
			     TString pol,
			     TString year,
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

    TString mode2 = "";
    TString dsFinalState = "";
    if ( year != "" ) { year = "_"+year; }
    if ( DsMode == true ) 
      { 
	TString dsFS = CheckDMode(mode,debug);
	if ( dsFS == "" ) { dsFS = CheckKKPiMode(mode, debug); }
	if ( dsFS != "" ) { dsFinalState = "_"+dsFS;}

	if( mode.Contains("DsPi") == true ) { mode2 = "Bs2DsPi";}
	else if ( mode.Contains("DsK") == true ) { mode2 = "Bs2DsK";}
      }
    else
      {
	mode2 = mode;
      }

    
    
    if ( pol == "both")
      {
        name ="PIDKShape_"+mode2+"_down"+dsFinalState+year; 
        pdf_PIDK1 = GetRooBinned1DFromWorkspace(work, name, debug);

        name ="PIDKShape_"+mode2+"_up"+dsFinalState+year; 
        pdf_PIDK2 = GetRooBinned1DFromWorkspace(work, name, debug);

        name = "PIDKShape_"+mode2+"_both"+dsFinalState+year;
        pdf_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_PIDK2,*pdf_PIDK1), RooArgList(lumRatio));

      }
    else
      {
        name = "PIDKShape_"+mode2+"_"+pol+dsFinalState+year;

        pdf_PIDK = (RooAddPdf*)work->pdf(name.Data());
      }

    CheckPDF( pdf_PIDK, debug );    
    return pdf_PIDK;
  }

  
  //===============================================================================
  // Create RooProdPdf with (Bs, Ds, PIDK) shapes from workspace
  //===============================================================================

  RooProdPdf* ObtainRooProdPdfForMDFitter(RooWorkspace* work,
					  TString mode,
					  TString pol,
					  TString year, 
					  RooRealVar& lumRatio,
					  RooAbsPdf* pdf_DsMass,
					  Int_t dim, 
					  bool debug)
  {

    RooAbsPdf* pdf_Bs = NULL;
    RooAbsPdf* pdf_Ds = NULL;
    RooAbsPdf* pdf_PIDK = NULL;

    TString name = "";
    TString mode2 = "";
    TString modeDs = "";
    TString Var = "";

    pdf_Bs = ObtainMassShape(work, mode, year, false, lumRatio, debug);  

    if ( dim > 1 )
      {
	if ( pdf_DsMass == NULL )
	  {
	    pdf_Ds = ObtainMassShape(work, mode, year, true, lumRatio, debug);
	  }
	else
	  {
	    pdf_Ds = pdf_DsMass;
	    TString namePDF = pdf_DsMass->GetName();
	    Var = CheckDMode(namePDF,debug);
	    if ( Var == "" ) { Var = CheckKKPiMode(namePDF, debug); }
	    modeDs = "_"+Var;
	    
	  }
      }

    if ( mode.Contains("Bs2DsPi") == true || (mode.Contains("Bs2DsK") ==true && mode.Contains("Bs2DsKst") == false) )
      {
	if ( dim > 2) 
	  {
	    pdf_PIDK = ObtainPIDKShape(work, mode, pol, year, lumRatio, true, debug);
	  }
	if ( mode.Contains("Bs2DsPi") == true) { mode2 = "Bs2DsPi"; } else { mode2 = "Bs2DsK"; }
	//Var = CheckDMode(mode,debug);
	//if ( Var == "" ) { Var = CheckKKPiMode(mode, debug); }
	//modeDs = "_"+Var;
      }
    else
      {
      
	if( mode.Contains("Bd2DPi") ) { mode2 = "Bd2DPi"; } else {mode2 = mode; }
	if (dim > 2)
	  {
	    pdf_PIDK = ObtainPIDKShape(work, mode2, pol, year, lumRatio, false, debug);
	  }
      }
    
    RooProdPdf* pdf_Tot = NULL;
    TString samplemode = pol+modeDs; 
    pdf_Tot = GetRooProdPdfDim(mode2, samplemode, pdf_Bs, pdf_Ds, pdf_PIDK, dim, debug);

    /*
      name="PhysBkg"+mode2+"Pdf_m_"+pol+modeDs+"_Tot";
      pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs,*pdf_Ds,*pdf_PIDK));
      CheckPDF( pdf_Tot, debug );
    */
    
    return pdf_Tot;
  }

  RooProdPdf* GetRooProdPdfDim(TString& mode, TString& samplemode, 
                               RooAbsPdf* pdf_Bs, RooAbsPdf* pdf_Ds, RooAbsPdf* pdf_PIDK,
                               Int_t dim, bool debug)
  {
    RooProdPdf* pdf_Tot = NULL;
    TString name="PhysBkg"+mode+"Pdf_m_"+samplemode+"_Tot";
    if ( dim == 1 )
      {
	if ( debug == true ) { std::cout<<"1D "; }
	pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs));
      }
    else if ( dim == 2) 
      {
	if (debug == true ) { std::cout<<"2D "; }
	pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs,*pdf_Ds));
      }
    else if ( dim == 3 )
      {
	if (debug == true ) { std::cout<<"3D "; }
	pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs,*pdf_Ds,*pdf_PIDK));
      }
    CheckPDF( pdf_Tot, debug );
    return pdf_Tot; 
  }

  //===============================================================================
  // Create RooProdPdf with (Bs mass, Ds mass, PIDK, time) shapes from workspace
  //===============================================================================

  RooProdPdf* ObtainRooProdPdfForFullFitter(RooWorkspace* work,
                                            TString mode,
                                            TString pol,
					    TString year,
                                            RooRealVar& lumRatio,
                                            RooAbsPdf* pdf_Time,
                                            RooAbsPdf* pdf_DsMass,
                                            bool debug)
  {
    RooAbsPdf* pdf_Bs = NULL;
    RooAbsPdf* pdf_Ds = NULL;
    RooAbsPdf* pdf_PIDK = NULL;

    pdf_Bs = ObtainMassShape(work, mode, year, false, lumRatio, debug);
    if ( pdf_DsMass == NULL )
      {
	pdf_Ds = ObtainMassShape(work, mode, year, true,  lumRatio, debug);
      }
    else
      {
	pdf_Ds = pdf_DsMass;
      }

    TString dmode = CheckDMode(mode, debug);
    if ( dmode == "" ) { dmode == CheckKKPiMode(mode,debug);}

    if ( dmode != "" )
      {
        pdf_PIDK = ObtainPIDKShape(work, mode, pol, year, lumRatio, true, debug);
      }
    else
      {
        pdf_PIDK = ObtainPIDKShape(work, mode, pol, year, lumRatio, false, debug);
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
					 RooWorkspace* workInt,
					 RooAbsPdf* pdf_Bd2DsPi,
					 TString &samplemode,
					 Int_t dim, 
					 bool debug
					 ){
    if (debug == true)
      {
        cout<<"------------------------------------"<<endl;
	cout<<"=====> Build background model BsDsPi"<<endl;
        cout<<"------------------------------------"<<endl;
      }

    RooArgList* list = new RooArgList();

    TString nCombBkgName = "nCombBkg_"+samplemode+"_Evts";
    RooRealVar* nCombBkgEvts = GetObservable(workInt, nCombBkgName, debug);
    Double_t valCombBkg = nCombBkgEvts->getValV();

    TString nBs2DsDsstPiRhoName = "nBs2DsDsstPiRho_"+samplemode+"_Evts";
    RooRealVar* nBs2DsDsstPiRhoEvts = GetObservable(workInt, nBs2DsDsstPiRhoName, debug);
    Double_t valBs2DsDsstPiRho = nBs2DsDsstPiRhoEvts->getValV();

    TString nBs2DsKName = "nBs2DsK_"+samplemode+"_Evts";
    RooRealVar* nBs2DsKEvts = GetObservable(workInt, nBs2DsKName, debug);
    Double_t valBs2DsK = nBs2DsKEvts->getValV();

    TString nBd2DPiName = "nBd2DPi_"+samplemode+"_Evts";
    RooRealVar*  nBd2DPiEvts = GetObservable(workInt, nBd2DPiName, debug);
    Double_t valBd2DPi = nBd2DPiEvts->getValV();

    TString nLb2LcPiName = "nLb2LcPi_"+samplemode+"_Evts";
    RooRealVar* nLb2LcPiEvts =  GetObservable(workInt, nLb2LcPiName, debug);
    Double_t valLb2LcPi = nLb2LcPiEvts->getValV();

    TString g1_f1_Name = "g1_f1_frac";
    RooRealVar* g1_f1 = GetObservable(workInt, g1_f1_Name, debug);

    TString mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }
    //Mode = GetModeCapital(Mode,debug);

    TString year = CheckDataYear(samplemode, debug); 
    if ( year != "" ) { year = "_"+year; }
    /*
    TString cB1VarName = "CombBkg_cB1_"+mode+year;
    RooRealVar* cB1Var = GetObservable(workInt, cB1VarName, debug);
    
    TString cB2VarName = "CombBkg_cB2_"+mode+year;
    RooRealVar* cB2Var = GetObservable(workInt, cB2VarName, debug);

    TString fracBsCombName = "CombBkg_fracCombB_"+mode+year;
    RooRealVar* fracBsComb =GetObservable(workInt, fracBsCombName, debug);

    RooRealVar* cDVar = NULL;
    RooRealVar* fracDsComb = NULL;
    if (dim > 1)
      {
	TString cDVarName = "CombBkg_cD_"+mode+year;
	cDVar =GetObservable(workInt, cDVarName, debug);

	TString fracDsCombName = "CombBkg_fracCombD_"+mode+year;
        fracDsComb =GetObservable(workInt, fracDsCombName, debug);
      }
    
    RooRealVar* fracPIDComb = NULL;
    if ( dim > 2)
      {
	TString fracPIDCombName = "CombBkg_fracPIDK1";
	fracPIDComb =GetObservable(workInt, fracPIDCombName, debug);
      }
    */
    TString lumRatioName = "lumRatio"+year;
    RooRealVar* lumRatio =GetObservable(workInt, lumRatioName, debug);

    RooAbsPdf* pdf_SignalDs = NULL;
    if (dim>1)
      {
	TString signalDsName = "Signal_CharmMass_"+samplemode;
	pdf_SignalDs = GetRooAbsPdfFromWorkspace(workInt, signalDsName, debug);
	CheckPDF(pdf_SignalDs, debug);
      }
                              
    // ------------------------------------------ Read BdDsPi ----------------------------------------------------//
    if (debug == true){
      cout<<"-------------------------- Read BdDsPi -------------------------------"<<endl;
      //if( pdf_BdDsPi != NULL ) { cout<<"Read "<<pdf_BdDsPi->GetName()<<endl;} else {cout<<"Cannot read BdDsPi pdf"<<endl; return NULL;}
    }
    TString name="";
    TString m = "";
    TString sam = CheckPolarity(samplemode,debug);
    TString y = CheckDataYear(samplemode,debug); 

    RooAbsPdf* pdf_Bd2DsPi_PIDK = NULL;
    RooAbsPdf* pdf_Bd2DsPi_Ds = NULL;
    RooProdPdf* pdf_Bd2DsPi_Tot = NULL;

    if ( valBs2DsDsstPiRho!= 0)
      {
	m = "Bs2DsPi_"+samplemode;
	if ( dim > 2 )
	  {
	    pdf_Bd2DsPi_PIDK = ObtainPIDKShape(work, m, sam, y, *lumRatio, true, debug);
	  }
	if (dim > 1)
	  {
	    pdf_Bd2DsPi_Ds = pdf_SignalDs;
	  }
	m = "Bd2DsPi";
	pdf_Bd2DsPi_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bd2DsPi, pdf_Bd2DsPi_Ds, pdf_Bd2DsPi_PIDK, dim, debug  );
      }
    // -------------------------------- Create Combinatorial Background --------------------------------------------//

    /*   
    if (debug == true) cout<<"---------------  Create combinatorial background PDF -----------------"<<endl;
      
    RooAddPdf* pdf_combBkg = NULL;
    RooAddPdf* pdf_combBkg_Ds = NULL;
    RooAbsPdf* pdf_combBkg_PIDK1 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK2 = NULL;
    RooAddPdf* pdf_combBkg_PIDK = NULL;
    RooProdPdf* pdf_combBkg_Tot = NULL;
    RooExtendPdf* epdf_combBkg   = NULL;

    if ( valCombBkg != 0.0 )
      {
	TString Mode = GetModeCapital(mode,debug);
	pdf_combBkg = ObtainComboBs(mass, *cB1Var, *cB2Var, *fracBsComb, Mode, debug);
    
	if ( dim > 1)
	  {
	    pdf_combBkg_Ds = ObtainComboDs(massDs, *cDVar, *fracDsComb, pdf_SignalDs, Mode, debug); 
	  }

	if (dim >2)
	  {
	    m = "CombPi";
	    pdf_combBkg_PIDK1 = ObtainPIDKShape(work, m, sam, y, *lumRatio, false, debug);
	    m = "CombK";
	    pdf_combBkg_PIDK2 = ObtainPIDKShape(work, m, sam, y, *lumRatio, false, debug);
	    
	    name = "ShapePIDKAll_Comb_"+samplemode;
	    pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
					      name.Data(),
					      RooArgList(*pdf_combBkg_PIDK1,*pdf_combBkg_PIDK2), *fracPIDComb);
	    CheckPDF(pdf_combBkg_PIDK,debug);
	  }

	m = "CombBkg";
	pdf_combBkg_Tot = GetRooProdPdfDim(m, samplemode, pdf_combBkg, pdf_combBkg_Ds, pdf_combBkg_PIDK, dim, debug  );
	
	name = "CombBkgEPDF_m_"+samplemode;
	epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg_Tot  , *nCombBkgEvts   );
	CheckPDF(epdf_combBkg, debug);
	list = AddEPDF(list, epdf_combBkg, nCombBkgEvts, debug);
      }
    */    
    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;
    
    RooProdPdf* pdf_Bd2DPi_Tot = NULL;
    RooExtendPdf* epdf_Bd2DPi    = NULL;
    if ( valBd2DPi != 0 )
      {
	m = "Bd2DPi_kpipi"+y;
	pdf_Bd2DPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);

	name = "Bd2DPiEPDF_m_"+samplemode;
	epdf_Bd2DPi = new RooExtendPdf( name.Data(),pdf_Bd2DPi_Tot->GetTitle(), *pdf_Bd2DPi_Tot, *nBd2DPiEvts);
	CheckPDF(epdf_Bd2DPi, debug);
	list = AddEPDF(list, epdf_Bd2DPi, nBd2DPiEvts, debug);
      }

    //-----------------------------------------//
    
    RooProdPdf* pdf_Lb2LcPi_Tot = NULL;
    RooExtendPdf* epdf_Lb2LcPi = NULL;
    if ( valLb2LcPi != 0.0 )
      {
	m = "Lb2LcPi";
	pdf_Lb2LcPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);
	
	name = "Lb2LcPiEPDF_m_"+samplemode;
	epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi_Tot->GetTitle(), *pdf_Lb2LcPi_Tot, *nLb2LcPiEvts );
	CheckPDF(epdf_Lb2LcPi, debug);
	list = AddEPDF(list, epdf_Lb2LcPi, nLb2LcPiEvts, debug);
      }

    //-----------------------------------------//

    RooProdPdf* pdf_Bs2DsK_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsK = NULL;
    if ( valBs2DsK != 0 )
      {
	m = "Bs2DsK";
	pdf_Bs2DsK_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bs2DsKEPDF_m_"+samplemode;
	epdf_Bs2DsK = new RooExtendPdf(name.Data() , pdf_Bs2DsK_Tot->GetTitle(), *pdf_Bs2DsK_Tot, *nBs2DsKEvts );
	CheckPDF(epdf_Bs2DsK, debug);
	list = AddEPDF(list, epdf_Bs2DsK, nBs2DsKEvts, debug);
      }

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
    RooAbsPdf* pdf_Bs2DsstPi_Ds = NULL;
    RooAbsPdf* pdf_Bs2DsstPi_PIDK = NULL;
    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    RooAddPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;

    if ( valBs2DsDsstPiRho!= 0)
      {
	m = "Bs2DsstPi";
	pdf_Bs2DsstPi = ObtainMassShape(work, m, y, false, *lumRatio, debug);

	if ( dim > 1)
	  {
	    pdf_Bs2DsstPi_Ds = pdf_SignalDs;
	  }

	if ( dim > 2 )
	  {
	    m = "Bs2DsPi_"+samplemode;
	    pdf_Bs2DsstPi_PIDK = ObtainPIDKShape(work, m, sam, y, *lumRatio, true, debug);
	  }

	m = "Bs2DsstPi";
	pdf_Bs2DsstPi_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bs2DsstPi, pdf_Bs2DsstPi_Ds, pdf_Bs2DsstPi_PIDK, dim, debug  );
	
	name="PhysBkgBs2DsDsstPiPdf_m_"+samplemode+"_Tot";
	pdf_Bs2DsDsstPiRho_Tot = new RooAddPdf( name.Data(),
						name.Data(),
						RooArgList(*pdf_Bs2DsstPi_Tot, *pdf_Bd2DsPi_Tot), //, *pdf_Bs2DsRho), //,*pdf_Bs2DsstRho),
						RooArgList(*g1_f1) //,g1_f2), rec
						);
	CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);

	name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
	epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho_Tot-> GetTitle(), *pdf_Bs2DsDsstPiRho_Tot  , *nBs2DsDsstPiRhoEvts);
	CheckPDF(epdf_Bs2DsDsstPiRho, debug);
	list = AddEPDF(list, epdf_Bs2DsDsstPiRho, nBs2DsDsstPiRhoEvts, debug);
      }
    
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(),*list);
    
    if (debug == true)
      {
	cout<<endl;
	if( pdf_totBkg != NULL ){ cout<<" ------------- CREATED TOTAL BACKGROUND PDF: SUCCESFULL------------"<<endl; }
	else { cout<<" ---------- CREATED TOTAL BACKGROUND PDF: FAILED ----------------"<<endl;}
      }
    return pdf_totBkg;
    
  }



  //===============================================================================
  // Background MD model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsK_BKG_MDFitter(RooAbsReal& mass,
				       RooAbsReal& massDs,
				       RooWorkspace* work,
				       RooWorkspace* workInt,
				       RooAddPdf* pdf_Bd2DsK,
				       TString &samplemode,
				       Int_t dim, 
				       bool debug){
    

    if (debug == true)
      {
        cout<<"--------------------------------------------------------"<<endl;
        cout<<"=====> Build background model BsDsK for simultaneous fit"<<endl;
	cout<<"--------------------------------------------------------"<<endl;
      }

    RooArgList* list = new RooArgList();
    
    TString nCombBkgName = "nCombBkg_"+samplemode+"_Evts";
    RooRealVar* nCombBkgEvts = GetObservable(workInt, nCombBkgName, debug);
    Double_t valCombBkg = nCombBkgEvts->getValV(); 
    
    TString nBsLb2DsDsstPPiRhoName = "nBsLb2DsDsstPPiRho_"+samplemode+"_Evts"; 
    RooRealVar* nBsLb2DsDsstPPiRhoEvts = GetObservable(workInt, nBsLb2DsDsstPPiRhoName, debug);                                           
    Double_t valBsLb2DsDsstPPiRho = nBsLb2DsDsstPPiRhoEvts->getValV(); 

    TString nBs2DsDssKKstName = "nBs2DsDsstKKst_"+samplemode+"_Evts";
    RooRealVar* nBs2DsDssKKstEvts = GetObservable(workInt, nBs2DsDssKKstName, debug);                                                     
    Double_t valBs2DsDssKKst = nBs2DsDssKKstEvts->getValV(); 

    TString nBd2DKName = "nBd2DK_"+samplemode+"_Evts";                                                                                       
    RooRealVar*  nBd2DKEvts = GetObservable(workInt, nBd2DKName, debug);
    Double_t valBd2DK = nBd2DKEvts->getValV(); 
                  
    TString nBd2DPiName = "nBd2DPi_"+samplemode+"_Evts";
    RooRealVar*  nBd2DPiEvts = GetObservable(workInt, nBd2DPiName, debug);
    Double_t valBd2DPi =nBd2DPiEvts->getValV();  

    TString nLb2LcKName = "nLb2LcK_"+samplemode+"_Evts";
    RooRealVar* nLb2LcKEvts =  GetObservable(workInt, nLb2LcKName, debug);
    Double_t valLb2LcK = nLb2LcKEvts->getValV(); 

    TString nLb2LcPiName = "nLb2LcPi_"+samplemode+"_Evts";
    RooRealVar* nLb2LcPiEvts =  GetObservable(workInt, nLb2LcPiName, debug);
    Double_t valLb2LcPi = nLb2LcPiEvts->getValV();

    TString g1_f1_Name = "g1_f1_frac";
    RooRealVar* g1_f1 = GetObservable(workInt, g1_f1_Name, debug);

    TString g2_f1_Name = "g2_f1_frac";
    RooRealVar* g2_f1 =GetObservable(workInt, g2_f1_Name, debug);
    
    TString g2_f2_Name = "g2_f2_frac";
    RooRealVar* g2_f2 =GetObservable(workInt, g2_f2_Name, debug);

    TString g3_f1_Name = "g3_f1_frac";
    RooRealVar* g3_f1 =GetObservable(workInt, g3_f1_Name, debug);

    /*
    RooRealVar* g4_f1 = NULL;
    RooRealVar* g4_f2 = NULL; 
    
    if( dim > 2)
      {
	TString g4_f1_Name = "CombBkg_fracPIDK1";
	g4_f1 =GetObservable(workInt, g4_f1_Name, debug);
	
	TString g4_f2_Name = "CombBkg_fracPIDK2";
	g4_f2 =GetObservable(workInt, g4_f2_Name, debug);
      }
    */
    TString g5_f1_Name = "g5_f1_frac";
    RooRealVar* g5_f1 =GetObservable(workInt, g5_f1_Name, debug);

    TString mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }
    TString Mode = GetModeCapital(mode,debug);
    TString y = CheckDataYear(samplemode,debug);
    TString year = CheckDataYear(samplemode, debug);
    if ( year != "" ) { year = "_"+year; }
    /*
    TString cBVarName = "CombBkg_cB_"+mode+year;  
    RooRealVar* cBVar = GetObservable(workInt, cBVarName, debug);

    RooRealVar* cDVar = NULL;
    RooRealVar* fracComb = NULL;
    if (dim > 1)
      {
	TString cDVarName = "CombBkg_cD_"+mode+year;
        cDVar =GetObservable(workInt, cDVarName, debug);
	
	TString fracCombName = "CombBkg_fracCombD_"+mode+year;
	fracComb =GetObservable(workInt, fracCombName, debug);
      }
    */
    TString lumRatioName = "lumRatio"+year;
    RooRealVar* lumRatio =GetObservable(workInt, lumRatioName, debug);

    RooAbsPdf* pdf_SignalDs = NULL; 
    if (dim > 1)
      {
	TString signalDsName = "Signal_CharmMass_"+samplemode;
	pdf_SignalDs = GetRooAbsPdfFromWorkspace(workInt, signalDsName, debug); 
	CheckPDF(pdf_SignalDs, debug);
      }

    // ------------------------------------------ Read BdDsK ----------------------------------------------------//
    if (debug == true)
      {
        cout<<"-------------------------- Read BdDsK -------------------------------"<<endl;
      }
    TString m = "";
    TString name="";

    TString sam = CheckPolarity(samplemode,debug);
  
    //RooAbsPdf* pdf_Bd2DsK = NULL;
    //TString Bd2DsKName = "PhysBkgBd2DsKPdf_m_"+Mode; 
    //pdf_Bd2DsK = GetRooAbsPdfFromWorkspace(workInt, Bd2DsKName, debug);
    //CheckPDF(pdf_Bd2DsK, debug);

    RooAbsPdf* pdf_Bd2DsK_PIDK = NULL;
    RooAbsPdf* pdf_Bd2DsK_Ds = NULL;
    RooProdPdf* pdf_Bd2DsK_Tot = NULL;

    if ( valBsLb2DsDsstPPiRho != 0.0 )
      {
	if( dim > 2)
	  {
	    m = "Bs2DsK_"+samplemode;
	    pdf_Bd2DsK_PIDK = ObtainPIDKShape(work, m, sam, y, *lumRatio, true, debug);
	  }
	if ( dim > 1 )
	  {
	    pdf_Bd2DsK_Ds = pdf_SignalDs;
	  }
	m = "Bd2DsK"; 
	pdf_Bd2DsK_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bd2DsK, pdf_Bd2DsK_Ds, pdf_Bd2DsK_PIDK, dim, debug  );
      }
    // -------------------------------- Create Combinatorial Background --------------------------------------------//                       
    /*
    if (debug == true) { cout<<"---------------  Create combinatorial background PDF -----------------"<<endl; }
    
    RooExponential* pdf_combBkg = NULL;
    RooAddPdf* pdf_combBkg_Ds = NULL;
    RooAbsPdf* pdf_CombK_PIDK = NULL;
    RooAbsPdf* pdf_CombPi_PIDK = NULL;
    RooAbsPdf* pdf_CombP_PIDK = NULL;
    RooAddPdf* pdf_combBkg_PIDK = NULL;
    RooProdPdf* pdf_combBkg_Tot = NULL;
    RooExtendPdf* epdf_combBkg   = NULL;

    if ( valCombBkg != 0.0 )
      {
	name="CombBkgPDF_m_"+samplemode;
	pdf_combBkg = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, *cBVar);
	CheckPDF(pdf_combBkg, debug);
	
	if ( dim > 1 )
	  {
	    pdf_combBkg_Ds = ObtainComboDs(massDs, *cDVar, *fracComb, pdf_SignalDs, Mode, debug);
	  }
	
	if ( dim > 2)
	  {
	    m = "CombPi";
	    pdf_CombPi_PIDK = ObtainPIDKShape(work, m, sam, y, *lumRatio, false, debug);
	    m = "CombK";
	    pdf_CombK_PIDK = ObtainPIDKShape(work, m, sam, y, *lumRatio,  false, debug);
	    m = "CombP";
	    pdf_CombP_PIDK = ObtainPIDKShape(work, m, sam, y, *lumRatio,  false, debug);
	    
	    name = "ShapePIDKAll_Comb_"+sam;
	    pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
					      name.Data(),
					      RooArgList(*pdf_CombK_PIDK,*pdf_CombPi_PIDK, *pdf_CombP_PIDK), 
					      RooArgList(*g4_f1,*g4_f2), 
					      true);
	    CheckPDF(pdf_combBkg_PIDK, debug);
	  }
	
	m = "CombBkg"; 
	pdf_combBkg_Tot = GetRooProdPdfDim(m, samplemode, pdf_combBkg, pdf_combBkg_Ds, pdf_combBkg_PIDK, dim, debug  );
	
	name = "CombBkgEPDF_m_"+samplemode;
	epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg_Tot->GetTitle(), *pdf_combBkg_Tot  , *nCombBkgEvts   );
	CheckPDF( epdf_combBkg, debug );
	list = AddEPDF(list, epdf_combBkg, nCombBkgEvts, debug);
      }
    */
    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//                      

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;
    
    RooProdPdf* pdf_Bd2DK_Tot = NULL;
    RooExtendPdf* epdf_Bd2DK  = NULL;

    if ( valBd2DK != 0.0 )
      {
	m = "Bd2DK";
	pdf_Bd2DK_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);
	
	name = "Bd2DKEPDF_m_"+samplemode;
	epdf_Bd2DK = new RooExtendPdf( name.Data(),pdf_Bd2DK_Tot->GetTitle(), *pdf_Bd2DK_Tot, *nBd2DKEvts);
	CheckPDF( epdf_Bd2DK, debug ); 
	list = AddEPDF(list, epdf_Bd2DK, nBd2DKEvts, debug);
      }
    //-----------------------------------------//
    
    RooProdPdf* pdf_Bd2DPi_Tot = NULL;
    RooExtendPdf* epdf_Bd2DPi    = NULL;

    if ( valBd2DPi != 0.0 )
      {
	m = "Bd2DPi";
	pdf_Bd2DPi_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);
	
	name = "Bd2DPiEPDF_m_"+samplemode;
	epdf_Bd2DPi = new RooExtendPdf( name.Data(),pdf_Bd2DPi_Tot->GetTitle(), *pdf_Bd2DPi_Tot, *nBd2DPiEvts);
	CheckPDF( epdf_Bd2DPi, debug );
	list = AddEPDF(list, epdf_Bd2DPi, nBd2DPiEvts, debug);
      }

    //-----------------------------------------//                                       

    if (debug == true)
      {
	cout<<endl;
	cout<<"---------------  Create Groups -----------------"<<endl;
	cout<<"---------------  Group 1 -----------------"<<endl;
	cout<<"Bd->DsK"<<endl;
	cout<<"Bs->DsK*"<<endl;
      }
        
    RooProdPdf* pdf_Bs2DsKst_Tot = NULL;
    RooAddPdf* pdf_Bs2DsDsstKKst_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsDsstKKst = NULL;

    if ( valBs2DsDssKKst != 0.0 )
      {
	//m = "Bs2DsKst";
	//pdf_Bs2DsKst_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	//name="PhysBkgBs2DsDsstKKstPdf_m_"+samplemode+"_Tot";
	//pdf_Bs2DsDsstKKst_Tot = new RooAddPdf(name.Data(), name.Data(), *pdf_Bd2DsK_Tot, *pdf_Bs2DsKst_Tot, *g1_f1);
	//CheckPDF(pdf_Bs2DsDsstKKst_Tot, debug);

	name = "Bs2DsDsstKKstEPDF_m_"+samplemode;
	epdf_Bs2DsDsstKKst = new RooExtendPdf( name.Data() , pdf_Bd2DsK_Tot->GetTitle(), *pdf_Bd2DsK_Tot, *nBs2DsDssKKstEvts   );
	CheckPDF( epdf_Bs2DsDsstKKst, debug );
	list = AddEPDF(list, epdf_Bs2DsDsstKKst, nBs2DsDssKKstEvts, debug);
      }
    //-----------------------------------------//
  	  
    if (debug == true){
      cout<<"---------------  Group 2 -----------------"<<endl;
      cout<<"Bs->Ds*Pi"<<endl;
      cout<<"Bs->DsRho"<<endl;
    }
    
    RooProdPdf* pdf_Bs2DsRho_Tot = NULL;
    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    RooProdPdf* pdf_Bs2DsPi_Tot = NULL;
    RooAddPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    
    if ( valBsLb2DsDsstPPiRho != 0.0 )
      {

	m = "Bs2DsRho";
	pdf_Bs2DsRho_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	m = "Bs2DsstPi";
	pdf_Bs2DsstPi_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	m = "Bs2DsPi_"+samplemode;
	pdf_Bs2DsPi_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode+"_Tot";
	pdf_Bs2DsDsstPiRho_Tot = new RooAddPdf(name.Data(), name.Data(), 
					       RooArgList(*pdf_Bs2DsPi_Tot,*pdf_Bs2DsstPi_Tot, *pdf_Bs2DsRho_Tot), 
					       RooArgList(*g2_f1,*g2_f2), true);
	CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);
      }
    /*    
    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho_Tot-> GetTitle(), 
					    *pdf_Bs2DsDsstPiRho_Tot  , nBs2DsDsstPiRhoEvts   );
    CheckPDF( epdf_Bs2DsDsstPiRho, debug ); 
    */
    
    //-----------------------------------------//
    if (debug == true){
      cout<<"---------------  Group 3 -----------------"<<endl;
      cout<<"Lb->Dspi"<<endl;
      cout<<"Lb->Dsstpi"<<endl;
    }
    
    RooProdPdf* pdf_Lb2Dsp_Tot = NULL;
    RooProdPdf* pdf_Lb2Dsstp_Tot = NULL;
    RooAddPdf* pdf_Lb2DsDsstP_Tot = NULL;
    RooAddPdf* pdf_BsLb2DsDsstPPiRho_Tot = NULL;
    RooExtendPdf* epdf_BsLb2DsDsstPPiRho   = NULL;

    if ( valBsLb2DsDsstPPiRho != 0.0 )
      {

	m = "Lb2Dsp";
	pdf_Lb2Dsp_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y ,*lumRatio, pdf_SignalDs, dim, debug);
	
	m = "Lb2Dsstp";
	pdf_Lb2Dsstp_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name="PhysBkgLb2DsDsstPPdf_m_"+samplemode+"_Tot";
	pdf_Lb2DsDsstP_Tot = new RooAddPdf(name.Data(), name.Data(), *pdf_Lb2Dsp_Tot, *pdf_Lb2Dsstp_Tot, *g3_f1);
	CheckPDF(pdf_Lb2DsDsstP_Tot, debug);
	
	name="PhysBkgBsLb2DsDsstPPiRhoPdf_m_"+samplemode+"_Tot";
	pdf_BsLb2DsDsstPPiRho_Tot = new RooAddPdf(name.Data(), name.Data(),
						  RooArgList(*pdf_Bs2DsDsstPiRho_Tot, *pdf_Lb2DsDsstP_Tot),
				 RooArgList(*g5_f1));
	CheckPDF(pdf_BsLb2DsDsstPPiRho_Tot, debug);
     
	/*
	  RooExtendPdf* epdf_Lb2DsDsstP   = NULL;
	  name = "Lb2DsDsstPEPDF_m_"+samplemode;
	  epdf_Lb2DsDsstP = new RooExtendPdf( name.Data() , pdf_Lb2DsDsstP_Tot->GetTitle(), *pdf_Lb2DsDsstP_Tot  , nLb2DsDsstpEvts   );
	  CheckPDF( epdf_Lb2DsDsstP, debug ); 
	*/
    
	name = "BsLb2DsDsstPPiRhoEPDF_m_"+samplemode;
	epdf_BsLb2DsDsstPPiRho = new RooExtendPdf( name.Data() , pdf_BsLb2DsDsstPPiRho_Tot-> GetTitle(),
						   *pdf_BsLb2DsDsstPPiRho_Tot  , *nBsLb2DsDsstPPiRhoEvts   );
	CheckPDF( epdf_BsLb2DsDsstPPiRho, debug );
	list = AddEPDF(list, epdf_BsLb2DsDsstPPiRho, nBsLb2DsDsstPPiRhoEvts, debug);
      }
    //-----------------------------------------//
    
    RooProdPdf* pdf_Lb2LcK_Tot = NULL;
    RooExtendPdf* epdf_Lb2LcK = NULL;

    if ( valLb2LcK != 0.0 )
      {
	m = "Lb2LcK";
	pdf_Lb2LcK_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y ,*lumRatio, NULL, dim, debug);
	
	name = "Lb2LcKEPDF_m_"+samplemode;
	epdf_Lb2LcK = new RooExtendPdf(name.Data() , pdf_Lb2LcK_Tot->GetTitle(), *pdf_Lb2LcK_Tot, *nLb2LcKEvts );
	CheckPDF( epdf_Lb2LcK , debug );
	list = AddEPDF(list, epdf_Lb2LcK, nLb2LcKEvts, debug);
      }
    //-----------------------------------------//                                                                                                          
    
    RooProdPdf* pdf_Lb2LcPi_Tot = NULL;
    RooExtendPdf* epdf_Lb2LcPi = NULL;
    
    if ( valLb2LcPi != 0.0 )
      {
	m = "Lb2LcPi";
	pdf_Lb2LcPi_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);
	
	name = "Lb2LcPiEPDF_m_"+samplemode;
	epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi_Tot->GetTitle(), *pdf_Lb2LcPi_Tot, *nLb2LcPiEvts );
	CheckPDF( epdf_Lb2LcPi , debug );
	list = AddEPDF(list, epdf_Lb2LcPi, nLb2LcPiEvts, debug);
      }
    
    //--------------------------------- FULL PDF --------------------------//
    
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(), *list); 
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
  // Load RooAbsPdf from workspace.
  //===============================================================================

  RooAbsPdf* GetRooAbsPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug)
  {
    RooAbsPdf* pdf = NULL;
    pdf = (RooAbsPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf != NULL ){ cout<<"Read "<<pdf->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf;
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


  RooArgList* AddEPDF(RooArgList* list, RooExtendPdf* pdf, RooRealVar *numEvts, bool debug)
  {
    Double_t ev = numEvts->getValV();
    if ( ev != 0.0 )
      {
	list->add(*pdf);
	if (debug == true )
	  {
	    std::cout<<"[INFO] "<<pdf->GetName()<<" added to pdf list with inital number of events:"<<ev<<std::endl; 
	  }
      }
    else
      {
	if (debug == true )
          {
	    std::cout<<"[INFO] "<<pdf->GetName()<<" NOT added to pdf list, number of events:"<<ev<<std::endl;
          }
      }
    return list; 
  }


  RooAbsPdf* build_Combinatorial_MDFitter(RooAbsReal& mass,
					  RooAbsReal& massDs,
					  RooWorkspace* work,
					  RooWorkspace* workInt,
					  TString samplemode,
					  std::vector <TString> types,
					  std::vector <TString> pdfNames, 
					  std::vector <TString> pidk, 
					  Int_t dim,
					  bool debug)
  {


    if (debug == true)
      {
        cout<<"--------------------------------------------------------"<<endl;
        cout<<"=====> Build combinatorial background model"<<endl;
        cout<<"--------------------------------------------------------"<<endl;
	cout<<"Types of shapes: "<<std::endl;
	cout<<"BeautyMass: "<<types[0]<<std::endl;
	cout<<"CharmMass: "<<types[1]<<std::endl;
	cout<<"BacPIDK: "<<types[2]<<" with components: Kaon = "<<pidk[0]<<" Pion = "<<pidk[1]<<" Proton = "<<pidk[2]<<std::endl; 
      }

    
    RooExtendPdf* epdf_combBkg   = NULL;
    
    RooArgList* listPDF = new RooArgList();
    RooArgList* listFrac = new RooArgList();

    TString nCombBkgName = "nCombBkg_"+samplemode+"_Evts";
    RooRealVar* nCombBkgEvts = GetObservable(workInt, nCombBkgName, debug);
    Double_t valCombBkg = nCombBkgEvts->getValV();
    
    RooAbsPdf* pdf_combBkg = NULL;
    RooAbsPdf* pdf_combBkg1 = NULL;
    RooAbsPdf* pdf_combBkg2 = NULL;
    RooAbsPdf* pdf_combBkg_Ds = NULL;
    RooAbsPdf* pdf_pidk[3]; 
    RooAbsPdf* pdf_combBkg_PIDK = NULL;
    RooProdPdf* pdf_combBkg_Tot = NULL;

    RooRealVar* cB1Var = NULL;
    RooRealVar* cB2Var =NULL;
    RooRealVar* fracBsComb =NULL;
    RooRealVar* widthComb = NULL;
    RooRealVar* meanComb = NULL;


    RooRealVar* cDVar = NULL;
    RooRealVar* fracDsComb = NULL;
    RooAbsPdf* pdf_SignalDs = NULL;

    RooRealVar* fracPIDK1 = NULL;
    RooRealVar* fracPIDK2 = NULL; 

    TString mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }
    TString Mode = GetModeCapital(mode,debug);

    TString y = CheckDataYear(samplemode,debug);
    TString year = CheckDataYear(samplemode, debug);
    if ( year != "" ) { year = "_"+year; }
    TString sam = CheckPolarity(samplemode,debug);


    if ( types[0] == "Exponential" ) 
      {
	TString cBVarName = "CombBkg_cB_"+mode+year;
	cB1Var = GetObservable(workInt, cBVarName, debug);
      }
    else if ( types[0] == "DoubleExponential" )
      {
	TString cB1VarName = "CombBkg_cB1_"+mode+year;
	cB1Var = GetObservable(workInt, cB1VarName, debug);

	TString cB2VarName = "CombBkg_cB2_"+mode+year;
	cB2Var = GetObservable(workInt, cB2VarName, debug);

	TString fracBsCombName = "CombBkg_fracCombB_"+mode+year;
	fracBsComb =GetObservable(workInt, fracBsCombName, debug);

      }
    else if ( types[0] == "ExponentialPlusGauss" )
      {
                                                                                                                                                                   
	    TString fracBsCombName = "CombBkg_fracCombB_"+mode+year;                                                                
	    TString widthCombName = "CombBkg_widthComb_"+mode+year;                                                                                                                 
	    TString meanCombName = "CombBkg_meanComb_"+mode+year;                                                                                                                    
	    TString cB1VarName = "CombBkg_cB_"+mode+year;                                                                                                                 
     
	    cB1Var = GetObservable(workInt, cB1VarName, debug);                                                                                                                       
	    fracBsComb =GetObservable(workInt, fracBsCombName, debug);                                                                                                                
	    widthComb =GetObservable(workInt, widthCombName, debug);                                                                                                                   
	    meanComb =GetObservable(workInt, meanCombName, debug);                                                                                               
      }
    
    if (dim > 1)
      {
	if ( types[1] == "ExponentialPlusSignal" )
	  {
	    TString cDVarName = "CombBkg_cD_"+mode+year;
	    cDVar =GetObservable(workInt, cDVarName, debug);

	    TString fracDsCombName = "CombBkg_fracCombD_"+mode+year;
	    fracDsComb =GetObservable(workInt, fracDsCombName, debug);
	    
	    TString signalDsName = "Signal_CharmMass_"+samplemode;
	    pdf_SignalDs = GetRooAbsPdfFromWorkspace(workInt, signalDsName, debug);
	    CheckPDF(pdf_SignalDs, debug);
	  
	  }
      }

    Int_t num = 0; 
    if( dim > 2)
      {
	if ( types[2] == "Fixed" )
	  {
 
	    for( int i = 0; i<3; i++ )
	      {
		if ( pidk[i] == "True" || pidk[i] == "true" ) { num++; } 
	      }

	    if (num > 1 )
	      {
		TString g4_f1_Name = "CombBkg_fracPIDK1";
		fracPIDK1 =GetObservable(workInt, g4_f1_Name, debug);
	      }
	    if ( num > 2 )
	      {
		TString g4_f2_Name = "CombBkg_fracPIDK2";
		fracPIDK2 =GetObservable(workInt, g4_f2_Name, debug);
	      }
	  }
      }

    TString lumRatioName = "lumRatio"+year;
    RooRealVar* lumRatio =GetObservable(workInt, lumRatioName, debug);

    if ( valCombBkg != 0.0 )
      {
        TString name="CombBkgPDF_m_"+samplemode;

	if ( types[0] == "Exponential" )
	  {
	    pdf_combBkg = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, *cB1Var);
	  }
	else if ( types[0] == "DoubleExponential" )
	  {
	    pdf_combBkg = ObtainComboBs(mass, *cB1Var, *cB2Var, *fracBsComb, Mode, debug);
	  }
	else if ( types[0] == "RooKeysPdf")
	  {
	    if (debug == true ) { std::cout<<"[INFO] Combinatorial taken as RooKeyPdf: "<<pdfNames[0]<<std::endl; } 
	    pdf_combBkg = (RooKeysPdf*)work->pdf(pdfNames[0].Data());
	  }
	else if ( types[0] == "ExponentialPlusGauss")
	  {
	    name="CombBkgExpoPDF_"+mode+year;                                                                                                                                          
            pdf_combBkg1 = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, *cB1Var);                                                                    
            name="CombBkgGaussPDF_"+mode+year;                                                                                                                                         
            pdf_combBkg2 = new RooGaussian(name.Data(),name.Data(),mass,*meanComb,*widthComb);                                                                                          
                                                                                                                                                                                      
            name="CombBkgPDF_"+mode+year;                                                                                                                                              
            pdf_combBkg = new RooAddPdf(name.Data(),name.Data(), RooArgList(*pdf_combBkg1,*pdf_combBkg2),*fracBsComb);              
	  }
	else
	  {
	    std::cout<<"[INFO] Wrong type of combinatorial shape for beautyMass"<<std::endl;
	    return NULL; 
	  }
	    
        CheckPDF(pdf_combBkg, debug);

        if ( dim > 1 )
          {
	    if ( types[1] == "ExponentialPlusSignal" ) 
	      {
		pdf_combBkg_Ds = ObtainComboDs(massDs, *cDVar, *fracDsComb, pdf_SignalDs, mode, debug);
	      }
	    else if ( types[1] == "RooKeysPdf")
	      {
		if (debug == true ) { std::cout<<"[INFO] Combinatorial taken as RooKeyPdf: "<<pdfNames[1]<<std::endl; }
		pdf_combBkg_Ds = (RooKeysPdf*)work->pdf(pdfNames[1].Data());
	      }
	    else
	      {
		std::cout<<"[INFO] Wrong type of combinatorial shape for charmMass"<<std::endl; 
		return NULL; 
	      }
          }

        if ( dim > 2)
          {
	    if ( types[2] == "RooKeysPdf")
              {
                if (debug == true ) { std::cout<<"[INFO] Combinatorial taken as RooKeyPdf: "<<pdfNames[2]<<std::endl; }
		pdf_combBkg_Ds = (RooKeysPdf*)work->pdf(pdfNames[2].Data());
              }
            else if ( types[2] == "Fixed" ) 
	      {
		
		TString m[] = {"CombPi","CombK","CombP"};

		for (int i = 0; i<3; i++ )
		  { 
		    if ( pidk[i] == "True" || pidk[i] == "true") 
		      { 
			pdf_pidk[i] = ObtainPIDKShape(work, m[i], sam, y, *lumRatio, false, debug);
			if ( pdf_pidk[i] != NULL )
			  {
			    std::cout<<"[INFO] Adding pdf: "<<pdf_pidk[i]->GetName()<<" to PIDK PDFs"<<std::endl; 
			    listPDF->add(*pdf_pidk[i]);
			  }
		      }
		  }
		
		if ( num > 1 ) { listFrac->add(*fracPIDK1); }
		if ( num > 2 ) { listFrac->add(*fracPIDK2); } 

		name = "ShapePIDKAll_Comb_"+sam;		
		pdf_combBkg_PIDK = new RooAddPdf( name.Data(), name.Data(), *listPDF, *listFrac, true);
		CheckPDF(pdf_combBkg_PIDK, debug);
	      }
          }
      }

    TString m = "CombBkg";
    pdf_combBkg_Tot = GetRooProdPdfDim(m, samplemode, pdf_combBkg, pdf_combBkg_Ds, pdf_combBkg_PIDK, dim, debug  );
    
    TString name = "CombBkgEPDF_m_"+samplemode;
    epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg_Tot->GetTitle(), *pdf_combBkg_Tot  , *nCombBkgEvts   );
    CheckPDF( epdf_combBkg, debug ); 
    
    return epdf_combBkg;
  
  }

  RooAbsPdf* ObtainSignalMassShape(RooAbsReal& mass,
                                   RooWorkspace* work,
                                   RooWorkspace* workInt,
                                   TString samplemode,
                                   TString type,
				   bool extended, 
                                   bool debug)
  {

    RooAbsPdf* pdf_Signal = NULL;
    RooAbsPdf* epdf_Signal = NULL;
    RooRealVar* nSigEvts = NULL; 
    Double_t valSig = 10.0; 
    TString varName = mass.GetName(); 

    if ( extended == true )
      {
	TString nSigName = "nSig_"+samplemode+"_Evts";
	nSigEvts = GetObservable(workInt, nSigName, debug);
	valSig = nSigEvts->getValV();
      }
    else
      {
	nSigEvts = new RooRealVar("fake","fake",valSig); 
      }
    RooRealVar* mean = NULL;
    RooRealVar* alpha1Var = NULL;
    RooRealVar* alpha2Var =NULL;
    RooRealVar* n1Var = NULL;
    RooRealVar* n2Var =NULL;
    RooRealVar* sigma1Var =NULL;
    RooRealVar* sigma2Var = NULL;
    RooRealVar* fracVar = NULL;
    RooFormulaVar* sigma1For = NULL;
    RooFormulaVar* sigma2For = NULL;
    RooRealVar* R = NULL;


    TString t = "_";
    TString mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }
    TString Mode = GetModeCapital(mode,debug);

    TString y = CheckDataYear(samplemode,debug);
    TString year = CheckDataYear(samplemode, debug);
    if ( year != "" ) { year = "_"+year; }
    TString sam = CheckPolarity(samplemode,debug);

    if ( type.Contains("DoubleCrystalBall") == true )
      {
        TString meanName = "Signal_"+varName+"_mean";
        mean = GetObservable(workInt, meanName, debug);

        TString alpha1Name = "Signal_"+varName+"_alpha1_"+samplemode;
        alpha1Var = GetObservable(workInt, alpha1Name, debug);

        TString alpha2Name = "Signal_"+varName+"_alpha2_"+samplemode;
        alpha2Var = GetObservable(workInt, alpha2Name, debug);

        TString n1Name = "Signal_"+varName+"_n1_"+samplemode;
        n1Var = GetObservable(workInt, n1Name, debug);

        TString n2Name = "Signal_"+varName+"_n2_"+samplemode;
        n2Var = GetObservable(workInt, n2Name, debug);

        TString sigma1Name = "Signal_"+varName+"_sigma1_"+samplemode;
        sigma1Var = GetObservable(workInt, sigma1Name, debug);

        TString sigma2Name = "Signal_"+varName+"_sigma2_"+samplemode;
        sigma2Var = GetObservable(workInt, sigma2Name, debug);

        TString fracName = "Signal_"+varName+"_frac_"+samplemode;
        fracVar = GetObservable(workInt, fracName, debug);

      }
    else if ( type == "DoubleGaussian" )
      {

	TString meanName = "Signal_"+varName+"_mean";
        mean = GetObservable(workInt, meanName, debug);

        TString sigma1Name = "Signal_"+varName+"_sigma1_"+samplemode;
        sigma1Var = GetObservable(workInt, sigma1Name, debug);

        TString sigma2Name = "Signal_"+varName+"_sigma2_"+samplemode;
        sigma2Var = GetObservable(workInt, sigma2Name, debug);

        TString fracName = "Signal_"+varName+"_frac_"+samplemode;
        fracVar = GetObservable(workInt, fracName, debug);
      }
    else 
      {
	std::cout<<"[ERROR] Wrong type of PDF: "<<type<<std::endl; 
	return NULL; 
      }

    TString bName = "";
    if ( varName.Contains("Beauty") == true  ||  varName.Contains("beauty") == true || varName.Contains("Bs") == true || varName.Contains("Bd") == true )
      {
	bName = "B"; 
      }
    else
      {
	bName = "D"; 
      }
    TString namePDF="Signal_"+varName+"_"+samplemode;
    TString name = ""; 

    if ( type == "DoubleCrystalBall" )
      {
	pdf_Signal = buildDoubleCBEPDF_sim(mass,*mean,
					   *sigma1Var, *alpha1Var, *n1Var,
					   *sigma2Var, *alpha2Var, *n2Var,
					   *fracVar,
					   *nSigEvts,samplemode,bName,debug);
	pdf_Signal->SetName(namePDF.Data());
      }
    else if ( type == "DoubleCrystalBallWithWidthRatio" )
      {
	TString name = TString("Signal_")+varName+TString("_R");
	R = new RooRealVar(name.Data(),name.Data(), 1.0, 0.8, 1.2);
	name = TString("Signal_") + varName + TString("_sigmaf1_")+samplemode;
	sigma1For = new RooFormulaVar(name.Data(), name.Data(),"@0*@1", RooArgList(*sigma1Var,*R));
	if ( debug == true ) { std::cout<<"[INFO] Create/read "<<name<<std::endl; }
	name = TString("Signal_") + varName + TString("_sigmaf2_")+samplemode;
	sigma2For = new RooFormulaVar(name.Data(), name.Data(),"@0*@1", RooArgList(*sigma2Var,*R));
	if ( debug == true ) { std::cout<<"[INFO] Create/read "<<name<<std::endl; }
	pdf_Signal = buildDoubleCBEPDF_sim(mass,*mean,
					   *sigma1For, *alpha1Var, *n1Var,
					   *sigma2For, *alpha2Var, *n2Var,
					   *fracVar,
					   *nSigEvts,samplemode,bName,debug);
	
	pdf_Signal->SetName(namePDF.Data());
      }
    else if ( type == "DoubleGaussian") 
      {
	pdf_Signal =  buildDoubleGEPDF_sim(mass,*mean, *sigma1Var, *sigma2Var,*fracVar, *nSigEvts, samplemode, bName, false, debug); 
	pdf_Signal->SetName(namePDF.Data());
      }
    else
      {
	if ( debug == true )
	  {
	    std::cout<<"[ERROR] Type of PDF: "<<type<<" is not specified. Please add to 'build_Signal_MDFitter' function."<<std::endl;
	  }
	return NULL;
      }
    CheckPDF(pdf_Signal, debug);

    if ( extended == true )
      {
	name = "SigEPDF_"+samplemode;
	epdf_Signal = new RooExtendPdf( name.Data() , pdf_Signal->GetTitle(), *pdf_Signal  , *nSigEvts   );
	CheckPDF( epdf_Signal, debug );
      }
    else
      {
	epdf_Signal = pdf_Signal;
      }

    return epdf_Signal; 
  }

  

  RooAbsPdf* build_Signal_MDFitter(RooAbsReal& mass,
				   RooAbsReal& massDs,
				   RooWorkspace* work,
				   RooWorkspace* workInt,
				   TString samplemode,
				   TString decay, 
				   std::vector <TString> types,
				   Int_t dim,
				   bool debug)
  {


    if (debug == true)
      {
        cout<<"--------------------------------------------------------"<<endl;
        cout<<"=====> Build signal  model"<<endl;
	cout<<"--------------------------------------------------------"<<endl;
	cout<<"Types of shapes: "<<std::endl;
        cout<<"BeautyMass: "<<types[0]<<std::endl;
        cout<<"CharmMass: "<<types[1]<<std::endl;
        cout<<"BacPIDK: "<<types[2]<<std::endl;
      }

    RooExtendPdf* epdf_Signal   = NULL;
    
    TString nSigName = "nSig_"+samplemode+"_Evts";
    RooRealVar* nSigEvts = GetObservable(workInt, nSigName, debug);
    Double_t valSig = nSigEvts->getValV();

    RooAbsPdf* pdf_Signal = NULL;
    RooAbsPdf* pdf_Signal_Ds = NULL;
    RooAbsPdf* pdf_Signal_PIDK = NULL;
    RooProdPdf* pdf_Signal_Tot = NULL;


    TString t = "_"; 
    TString mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }
    TString Mode = GetModeCapital(mode,debug);

    TString y = CheckDataYear(samplemode,debug);
    TString year = CheckDataYear(samplemode, debug);
    if ( year != "" ) { year = "_"+year; }
    TString sam = CheckPolarity(samplemode,debug);


    if ( valSig != 0.0 )
      {

	pdf_Signal = ObtainSignalMassShape(mass, work, workInt,
					   samplemode, types[0], false, debug);
	if ( dim > 1)
	  {
	    pdf_Signal_Ds = ObtainSignalMassShape(massDs, work, workInt,
						  samplemode, types[1], false, debug);
	  }

	if ( dim > 2 )
	  {
	    TString lumRatioName = "lumRatio"+year;
	    RooRealVar* lumRatio =GetObservable(workInt, lumRatioName, debug); 
	
	    TString namePID = decay+t+samplemode; 
	    pdf_Signal_PIDK = ObtainPIDKShape(work, namePID, sam,y, *lumRatio, true, debug);
	    CheckPDF(pdf_Signal_PIDK, debug);
	  }	
      }


    TString m = "Signal";
    pdf_Signal_Tot = GetRooProdPdfDim(m, samplemode, pdf_Signal, pdf_Signal_Ds, pdf_Signal_PIDK, dim, debug  );
    TString name = "SigProdPDF_"+samplemode;  
    pdf_Signal_Tot->SetName(name); 

    name = "SigEPDF_"+samplemode;
    epdf_Signal = new RooExtendPdf( name.Data() , pdf_Signal_Tot->GetTitle(), *pdf_Signal_Tot  , *nSigEvts   );
    CheckPDF( epdf_Signal, debug );

    return epdf_Signal; 
  }

}
