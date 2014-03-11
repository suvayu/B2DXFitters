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

    TString dsFS = CheckDMode(mode,debug);
    if ( dsFS == "" ) { dsFS = CheckKKPiMode(mode, debug); }
   
    if (dsMass == true ) { Ds = "_Ds"; }

    if ( mode.Contains("Bd2DPi")== true && dsFS == "kpipi")
      {
        
	name = "PhysBkgBd2DPiPdf_m_down_kpipi"+Ds;
	pdf_Mass1 = (RooKeysPdf*)work->pdf(name.Data());
	CheckPDF( pdf_Mass1, debug);
	
        name = "PhysBkgBd2DPiPdf_m_up_kpipi"+Ds;
	pdf_Mass2 = (RooKeysPdf*)work->pdf(name.Data());
	CheckPDF( pdf_Mass2, debug);

	name = "PhysBkgBd2DPiPdf_m_both_kpipi"+Ds;
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

    TString mode2 = "";
    TString dsFinalState = "";
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
        name ="PIDKShape_"+mode2+"_down"+dsFinalState; 
        pdf_PIDK1 = GetRooBinned1DFromWorkspace(work, name, debug);

        name ="PIDKShape_"+mode2+"_up"+dsFinalState; 
        pdf_PIDK2 = GetRooBinned1DFromWorkspace(work, name, debug);

        name = "PIDKShape_"+mode2+"_both"+dsFinalState;
        pdf_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_PIDK2,*pdf_PIDK1), RooArgList(lumRatio));
      }
    else
      {
        name = "PIDKShape_"+mode2+"_"+pol+dsFinalState;
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

    
    pdf_Bs = ObtainMassShape(work, mode, false, lumRatio, debug);    

    if ( dim > 1 )
      {
	if ( pdf_DsMass == NULL )
	  {
	    pdf_Ds = ObtainMassShape(work, mode, true,  lumRatio, debug);
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
	    pdf_PIDK = ObtainPIDKShape(work, mode, pol, lumRatio, true, debug);
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
	    pdf_PIDK = ObtainPIDKShape(work, mode2, pol, lumRatio, false, debug);
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
  // Background 2D model for Bs->DsPi (Ds--> HHHPi0) mass fitter.
  //===============================================================================
  RooAbsPdf* build_Bs2DsPi_BKG_HHHPi0( RooAbsReal& mass,
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

    TString nCombBkgName = "nCombBkg_"+samplemode+"_Evts";
    RooRealVar* nCombBkgEvts = GetObservable(workInt, nCombBkgName, debug);

    TString nBs2DsDsstPiRhoName = "nBs2DsDsstPiRho_"+samplemode+"_Evts";
    RooRealVar* nBs2DsDsstPiRhoEvts = GetObservable(workInt, nBs2DsDsstPiRhoName, debug);

    TString nBd2DPiName = "nBd2DPi_"+samplemode+"_Evts";
    RooRealVar*  nBd2DPiEvts = GetObservable(workInt, nBd2DPiName, debug);

    TString nLb2LcPiName = "nLb2LcPi_"+samplemode+"_Evts";
    RooRealVar* nLb2LcPiEvts =  GetObservable(workInt, nLb2LcPiName, debug);

    TString nBd2DsstPiName = "nBd2DsstPi_"+samplemode+"_Evts";
    RooRealVar*  nBd2DsstPiEvts = GetObservable(workInt, nBd2DsstPiName, debug);
    
    TString nBd2DsstRhoName = "nBd2DsstRho_"+samplemode+"_Evts";
    RooRealVar*  nBd2DsstRhoEvts = GetObservable(workInt, nBd2DsstRhoName, debug);

    //TString nBs2DsstRhoName = "nBs2DsstRho_"+samplemode+"_Evts";
    //RooRealVar*  nBs2DsstRhoEvts = GetObservable(workInt, nBs2DsstRhoName, debug);

    //TString nBd2DstPiName = "nBd2DstPi_"+samplemode+"_Evts";
    //RooRealVar*  nBd2DstPiEvts = GetObservable(workInt, nBd2DstPiName, debug);
    
    //TString nBd2DRhoName = "nBd2DRho_"+samplemode+"_Evts";
    //RooRealVar*  nBd2DRhoEvts = GetObservable(workInt, nBd2DRhoName, debug);

    TString g1_f1_Name = "g1_f1_frac";
    RooRealVar* g1_f1 = GetObservable(workInt, g1_f1_Name, debug);

    TString Mode = CheckDMode(samplemode,debug);
    if ( Mode == "" ) { Mode = CheckKKPiMode(samplemode, debug); }

    TString cB1VarName = "CombBkg_slope_Bs1_"+Mode;
    RooRealVar* cB1Var = GetObservable(workInt, cB1VarName, debug);
    
    //TString cB2VarName = "CombBkg_slope_Bs2_"+Mode;
    //RooRealVar* cB2Var = GetObservable(workInt, cB2VarName, debug);

    RooRealVar* cDVar = NULL;
    if (dim > 1)
      {
	TString cDVarName = "CombBkg_slope_Ds_"+Mode;
	cDVar =GetObservable(workInt, cDVarName, debug);
      }

    //TString fracBsCombName = "CombBkg_fracBsComb_"+Mode;
    //RooRealVar* fracBsComb =GetObservable(workInt, fracBsCombName, debug);

    RooRealVar* fracDsComb = NULL;
    if (dim>1)
      {
	TString fracDsCombName = "CombBkg_fracDsComb_"+Mode;
	fracDsComb =GetObservable(workInt, fracDsCombName, debug);
      }
    
    RooRealVar* fracPIDComb = NULL;
    if ( dim > 2)
      {
	TString fracPIDCombName = "CombBkg_fracPIDKComb";
	fracPIDComb =GetObservable(workInt, fracPIDCombName, debug);
      }
    
    TString lumRatioName = "lumRatio";
    RooRealVar* lumRatio =GetObservable(workInt, lumRatioName, debug);

    RooAbsPdf* pdf_SignalDs = NULL;
    if (dim>1)
      {
	TString signalDsName = "sigDs_"+samplemode;
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

    RooAbsPdf* pdf_Bd2DsPi_PIDK = NULL;
    m = "Bs2DsPi_"+samplemode;
    if ( dim > 2 )
      {
	pdf_Bd2DsPi_PIDK = ObtainPIDKShape(work, m, sam, *lumRatio, true, debug);
      }
    RooAbsPdf* pdf_Bd2DsPi_Ds = NULL;
    if (dim > 1)
      {
	pdf_Bd2DsPi_Ds = pdf_SignalDs;
      }

    RooProdPdf* pdf_Bd2DsPi_Tot = NULL;
    m = "Bd2DsPi";
    pdf_Bd2DsPi_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bd2DsPi, pdf_Bd2DsPi_Ds, pdf_Bd2DsPi_PIDK, dim, debug  );

    // -------------------------------- Create Combinatorial Background --------------------------------------------//
   
    if (debug == true) cout<<"---------------  Create combinatorial background PDF -----------------"<<endl;
      
    RooAbsPdf* pdf_combBkg = NULL;
    //pdf_combBkg = ObtainComboBs(mass, *cB1Var, *cB2Var, *fracBsComb, Mode, debug);
    pdf_combBkg = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, *cB1Var);
    
    RooAddPdf* pdf_combBkg_Ds = NULL;
    if ( dim > 1)
      {
	pdf_combBkg_Ds = ObtainComboDs(massDs, *cDVar, *fracDsComb, pdf_SignalDs, Mode, debug); 
      }

    RooAbsPdf* pdf_combBkg_PIDK1 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK2 = NULL;
    RooAddPdf* pdf_combBkg_PIDK = NULL;

    if (dim >2)
      {
	m = "Comb";
	pdf_combBkg_PIDK1 = ObtainPIDKShape(work, m, sam, *lumRatio, false, debug);
	m = "CombK";
	pdf_combBkg_PIDK2 = ObtainPIDKShape(work, m, sam, *lumRatio, false, debug);
	
	name = "ShapePIDKAll_Comb_"+samplemode;
	pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
					  name.Data(),
					  RooArgList(*pdf_combBkg_PIDK1,*pdf_combBkg_PIDK2), *fracPIDComb);
	CheckPDF(pdf_combBkg_PIDK,debug);
      }

    RooProdPdf* pdf_combBkg_Tot = NULL;
    m = "CombBkg";
    pdf_combBkg_Tot = GetRooProdPdfDim(m, samplemode, pdf_combBkg, pdf_combBkg_Ds, pdf_combBkg_PIDK, dim, debug  );

    RooExtendPdf* epdf_combBkg   = NULL;
    name = "CombBkgEPDF_m_"+samplemode;
    epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg_Tot  , *nCombBkgEvts   );
    CheckPDF(epdf_combBkg, debug);

    
    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;
    
    RooProdPdf* pdf_Bd2DPi_Tot = NULL;
    m = "Bd2DPii";
    pdf_Bd2DPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);

    RooExtendPdf* epdf_Bd2DPi    = NULL;
    name = "Bd2DPiEPDF_m_"+samplemode;
    epdf_Bd2DPi = new RooExtendPdf( name.Data(),pdf_Bd2DPi_Tot->GetTitle(), *pdf_Bd2DPi_Tot, *nBd2DPiEvts);
    CheckPDF(epdf_Bd2DPi, debug);

    //-----------------------------------------//

    RooProdPdf* pdf_Bd2DsstPi_Tot = NULL;
    m = "Bd2DsstPi";
    pdf_Bd2DsstPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);

    RooExtendPdf* epdf_Bd2DsstPi = NULL;
    name = "Bd2DsstPiEPDF_m_"+samplemode;
    epdf_Bd2DsstPi = new RooExtendPdf(name.Data() , pdf_Bd2DsstPi_Tot->GetTitle(), *pdf_Bd2DsstPi_Tot, *nBd2DsstPiEvts );
    CheckPDF(epdf_Bd2DsstPi, debug);

    //-----------------------------------------//
    /*
    RooProdPdf* pdf_Bd2DsstRho_Tot = NULL;
    m = "Bd2Dsstrho";
    pdf_Bd2DsstRho_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);

    RooExtendPdf* epdf_Bd2DsstRho = NULL;
    name = "Bd2DsstRhoEPDF_m_"+samplemode;
    epdf_Bd2DsstRho = new RooExtendPdf(name.Data() , pdf_Bd2DsstRho_Tot->GetTitle(), *pdf_Bd2DsstRho_Tot, *nBd2DsstRhoEvts );
    CheckPDF(epdf_Bd2DsstRho, debug);
    */
    //-----------------------------------------//
    /*
    RooProdPdf* pdf_Bs2DsstRho_Tot = NULL;
    m = "Bs2Dsstrho";
    pdf_Bs2DsstRho_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);

    RooExtendPdf* epdf_Bs2DsstRho = NULL;
    name = "Bs2DsstRhoEPDF_m_"+samplemode;
    epdf_Bs2DsstRho = new RooExtendPdf(name.Data() , pdf_Bs2DsstRho_Tot->GetTitle(), *pdf_Bs2DsstRho_Tot, *nBs2DsstRhoEvts );
    CheckPDF(epdf_Bs2DsstRho, debug);
    */
    //-----------------------------------------//

    RooProdPdf* pdf_Lb2LcPi_Tot = NULL;
    m = "Lb2LcPi";
    pdf_Lb2LcPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);

    RooExtendPdf* epdf_Lb2LcPi = NULL;
    name = "Lb2LcPiEPDF_m_"+samplemode;
    epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi_Tot->GetTitle(), *pdf_Lb2LcPi_Tot, *nLb2LcPiEvts );
    CheckPDF(epdf_Lb2LcPi, debug);

    // --------------------------------- Create RooAddPdf -------------------------------------------------/
    
    RooAbsPdf* pdf_Bs2DsstPi = NULL;
    RooAbsPdf* pdf_Bs2DsstPi_Ds = NULL;
    if ( dim > 1)
      {
	pdf_Bs2DsstPi_Ds = pdf_SignalDs;
      }

    RooAbsPdf* pdf_Bs2DsstPi_PIDK = NULL;
    m = "Bs2DsstPi";
    pdf_Bs2DsstPi = ObtainMassShape(work, m, false, *lumRatio, debug);
    if ( dim > 2 )
      {
	m = "Bs2DsPi_"+samplemode;
	pdf_Bs2DsstPi_PIDK = ObtainPIDKShape(work, m, sam, *lumRatio, true, debug);
      }

    m = "Bs2DsstPi";
    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    pdf_Bs2DsstPi_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bs2DsstPi, pdf_Bs2DsstPi_Ds, pdf_Bs2DsstPi_PIDK, dim, debug  );
    
    RooAddPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    name="PhysBkgBs2DsDsstPiPdf_m_"+samplemode+"_Tot";
    pdf_Bs2DsDsstPiRho_Tot = new RooAddPdf( name.Data(),
					    name.Data(),
					    RooArgList(*pdf_Bs2DsstPi_Tot, *pdf_Bd2DsPi_Tot), //, *pdf_Bs2DsRho), //,*pdf_Bs2DsstRho),
					    RooArgList(*g1_f1) //,g1_f2), rec
                                        );
    CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);

    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho_Tot-> GetTitle(), *pdf_Bs2DsDsstPiRho_Tot  , *nBs2DsDsstPiRhoEvts);
    CheckPDF(epdf_Bs2DsDsstPiRho, debug);

    
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(),
                                RooArgList(*epdf_combBkg,
                                           *epdf_Bd2DPi,
					   *epdf_Bs2DsDsstPiRho,
                                           *epdf_Lb2LcPi,
                                           *epdf_Bd2DsstPi
                                           //*epdf_Bd2DsstRho, 
                                           //*epdf_Bs2DsstRho 
                                           //*epdf_Bd2DsstPi,
                                           //*epdf_BdDsPi,
					   ));
					   
    
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

    TString nCombBkgName = "nCombBkg_"+samplemode+"_Evts";
    RooRealVar* nCombBkgEvts = GetObservable(workInt, nCombBkgName, debug);

    TString nBs2DsDsstPiRhoName = "nBs2DsDsstPiRho_"+samplemode+"_Evts";
    RooRealVar* nBs2DsDsstPiRhoEvts = GetObservable(workInt, nBs2DsDsstPiRhoName, debug);

    TString nBs2DsKName = "nBs2DsK_"+samplemode+"_Evts";
    RooRealVar* nBs2DsKEvts = GetObservable(workInt, nBs2DsKName, debug);

    TString nBd2DPiName = "nBd2DPi_"+samplemode+"_Evts";
    RooRealVar*  nBd2DPiEvts = GetObservable(workInt, nBd2DPiName, debug);

    TString nLb2LcPiName = "nLb2LcPi_"+samplemode+"_Evts";
    RooRealVar* nLb2LcPiEvts =  GetObservable(workInt, nLb2LcPiName, debug);

    TString nBd2DsstPiName = "nBd2DsstPi_"+samplemode+"_Evts";
    RooRealVar*  nBd2DsstPiEvts = GetObservable(workInt, nBd2DsstPiName, debug);
    
    TString nBd2DstPiName = "nBd2DstPi_"+samplemode+"_Evts";
    RooRealVar*  nBd2DstPiEvts = GetObservable(workInt, nBd2DstPiName, debug);
    
    TString nBd2DRhoName = "nBd2DRho_"+samplemode+"_Evts";
    RooRealVar*  nBd2DRhoEvts = GetObservable(workInt, nBd2DRhoName, debug);

    TString g1_f1_Name = "g1_f1_frac";
    RooRealVar* g1_f1 = GetObservable(workInt, g1_f1_Name, debug);

    TString Mode = CheckDMode(samplemode,debug);
    if ( Mode == "" ) { Mode = CheckKKPiMode(samplemode, debug); }

    TString cB1VarName = "CombBkg_slope_Bs1_"+Mode;
    RooRealVar* cB1Var = GetObservable(workInt, cB1VarName, debug);
    
    TString cB2VarName = "CombBkg_slope_Bs2_"+Mode;
    RooRealVar* cB2Var = GetObservable(workInt, cB2VarName, debug);

    RooRealVar* cDVar = NULL;
    if (dim > 1)
      {
	TString cDVarName = "CombBkg_slope_Ds_"+Mode;
	cDVar =GetObservable(workInt, cDVarName, debug);
      }

    TString fracBsCombName = "CombBkg_fracBsComb_"+Mode;
    RooRealVar* fracBsComb =GetObservable(workInt, fracBsCombName, debug);

    RooRealVar* fracDsComb = NULL;
    if (dim>1)
      {
	TString fracDsCombName = "CombBkg_fracDsComb_"+Mode;
	fracDsComb =GetObservable(workInt, fracDsCombName, debug);
      }
    
    RooRealVar* fracPIDComb = NULL;
    if ( dim > 2)
      {
	TString fracPIDCombName = "CombBkg_fracPIDKComb";
	fracPIDComb =GetObservable(workInt, fracPIDCombName, debug);
      }
    
    TString lumRatioName = "lumRatio";
    RooRealVar* lumRatio =GetObservable(workInt, lumRatioName, debug);

    RooAbsPdf* pdf_SignalDs = NULL;
    if (dim>1)
      {
	TString signalDsName = "DblCBPDF_Ds_"+samplemode;
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

    RooAbsPdf* pdf_Bd2DsPi_PIDK = NULL;
    m = "Bs2DsPi_"+samplemode;
    if ( dim > 2 )
      {
	pdf_Bd2DsPi_PIDK = ObtainPIDKShape(work, m, sam, *lumRatio, true, debug);
      }
    RooAbsPdf* pdf_Bd2DsPi_Ds = NULL;
    if (dim > 1)
      {
	pdf_Bd2DsPi_Ds = pdf_SignalDs;
      }

    RooProdPdf* pdf_Bd2DsPi_Tot = NULL;
    m = "Bd2DsPi";
    pdf_Bd2DsPi_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bd2DsPi, pdf_Bd2DsPi_Ds, pdf_Bd2DsPi_PIDK, dim, debug  );

    // -------------------------------- Create Combinatorial Background --------------------------------------------//
   
    if (debug == true) cout<<"---------------  Create combinatorial background PDF -----------------"<<endl;
      
    RooAddPdf* pdf_combBkg = NULL;
    pdf_combBkg = ObtainComboBs(mass, *cB1Var, *cB2Var, *fracBsComb, Mode, debug);
    
    RooAddPdf* pdf_combBkg_Ds = NULL;
    if ( dim > 1)
      {
	pdf_combBkg_Ds = ObtainComboDs(massDs, *cDVar, *fracDsComb, pdf_SignalDs, Mode, debug); 
      }

    RooAbsPdf* pdf_combBkg_PIDK1 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK2 = NULL;
    RooAddPdf* pdf_combBkg_PIDK = NULL;

    if (dim >2)
      {
	m = "Comb";
	pdf_combBkg_PIDK1 = ObtainPIDKShape(work, m, sam, *lumRatio, false, debug);
	m = "CombK";
	pdf_combBkg_PIDK2 = ObtainPIDKShape(work, m, sam, *lumRatio, false, debug);
	
	name = "ShapePIDKAll_Comb_"+samplemode;
	pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
					  name.Data(),
					  RooArgList(*pdf_combBkg_PIDK1,*pdf_combBkg_PIDK2), *fracPIDComb);
	CheckPDF(pdf_combBkg_PIDK,debug);
      }

    RooProdPdf* pdf_combBkg_Tot = NULL;
    m = "CombBkg";
    pdf_combBkg_Tot = GetRooProdPdfDim(m, samplemode, pdf_combBkg, pdf_combBkg_Ds, pdf_combBkg_PIDK, dim, debug  );

    RooExtendPdf* epdf_combBkg   = NULL;
    name = "CombBkgEPDF_m_"+samplemode;
    epdf_combBkg = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg_Tot  , *nCombBkgEvts   );
    CheckPDF(epdf_combBkg, debug);

    
    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;
    
    RooProdPdf* pdf_Bd2DPi_Tot = NULL;
    m = "Bd2DPi_kpipi";
    pdf_Bd2DPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);

    RooExtendPdf* epdf_Bd2DPi    = NULL;
    name = "Bd2DPiEPDF_m_"+samplemode;
    epdf_Bd2DPi = new RooExtendPdf( name.Data(),pdf_Bd2DPi_Tot->GetTitle(), *pdf_Bd2DPi_Tot, *nBd2DPiEvts);
    CheckPDF(epdf_Bd2DPi, debug);

    //-----------------------------------------//

    RooProdPdf* pdf_Bd2DsstPi_Tot = NULL;
    m = "Bd2DsstPi";
    pdf_Bd2DsstPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);

    RooExtendPdf* epdf_Bd2DsstPi = NULL;
    name = "Bd2DsstPiEPDF_m_"+samplemode;
    epdf_Bd2DsstPi = new RooExtendPdf(name.Data() , pdf_Bd2DsstPi_Tot->GetTitle(), *pdf_Bd2DsstPi_Tot, *nBd2DsstPiEvts );
    CheckPDF(epdf_Bd2DsstPi, debug);

    //-----------------------------------------//
    
    RooProdPdf* pdf_Lb2LcPi_Tot = NULL;
    m = "Lb2LcPi";
    pdf_Lb2LcPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);

    RooExtendPdf* epdf_Lb2LcPi = NULL;
    name = "Lb2LcPiEPDF_m_"+samplemode;
    epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi_Tot->GetTitle(), *pdf_Lb2LcPi_Tot, *nLb2LcPiEvts );
    CheckPDF(epdf_Lb2LcPi, debug);

    //-----------------------------------------//

    RooProdPdf* pdf_Bs2DsK_Tot = NULL;
    m = "Bs2DsK";
    pdf_Bs2DsK_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);

    RooExtendPdf* epdf_Bs2DsK = NULL;
    name = "Bs2DsKEPDF_m_"+samplemode;
    epdf_Bs2DsK = new RooExtendPdf(name.Data() , pdf_Bs2DsK_Tot->GetTitle(), *pdf_Bs2DsK_Tot, *nBs2DsKEvts );
    CheckPDF(epdf_Bs2DsK, debug);

    //-----------------------------------------//
    
    RooProdPdf* pdf_Bd2DRho_Tot = NULL;
    m = "Bd2DRho";
    pdf_Bd2DRho_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);

    RooExtendPdf* epdf_Bd2DRho = NULL;
    name = "Bd2DRhoEPDF_m_"+samplemode;
    epdf_Bd2DRho= new RooExtendPdf( name.Data() , pdf_Bd2DRho_Tot-> GetTitle(), *pdf_Bd2DRho_Tot  , *nBd2DRhoEvts );
    CheckPDF(epdf_Bd2DRho, debug);

    //-----------------------------------------//
    
    RooProdPdf* pdf_Bd2DstPi_Tot = NULL;
    m = "Bd2DstPi";
    pdf_Bd2DstPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);

    RooExtendPdf* epdf_Bd2DstPi = NULL;
    name = "Bd2DstPiEPDF_m_"+samplemode;
    epdf_Bd2DstPi = new RooExtendPdf( name.Data() , pdf_Bd2DstPi_Tot-> GetTitle(), *pdf_Bd2DstPi_Tot  , *nBd2DstPiEvts );
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
    RooAbsPdf* pdf_Bs2DsstPi_Ds = NULL;
    if ( dim > 1)
      {
	pdf_Bs2DsstPi_Ds = pdf_SignalDs;
      }

    RooAbsPdf* pdf_Bs2DsstPi_PIDK = NULL;
    m = "Bs2DsstPi";
    pdf_Bs2DsstPi = ObtainMassShape(work, m, false, *lumRatio, debug);
    if ( dim > 2 )
      {
	m = "Bs2DsPi_"+samplemode;
	pdf_Bs2DsstPi_PIDK = ObtainPIDKShape(work, m, sam, *lumRatio, true, debug);
      }

    m = "Bs2DsstPi";
    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    pdf_Bs2DsstPi_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bs2DsstPi, pdf_Bs2DsstPi_Ds, pdf_Bs2DsstPi_PIDK, dim, debug  );
    
    RooAddPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    name="PhysBkgBs2DsDsstPiPdf_m_"+samplemode+"_Tot";
    pdf_Bs2DsDsstPiRho_Tot = new RooAddPdf( name.Data(),
					    name.Data(),
					    RooArgList(*pdf_Bs2DsstPi_Tot, *pdf_Bd2DsPi_Tot), //, *pdf_Bs2DsRho), //,*pdf_Bs2DsstRho),
					    RooArgList(*g1_f1) //,g1_f2), rec
                                        );
    CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);

    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;
    name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
    epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho_Tot-> GetTitle(), *pdf_Bs2DsDsstPiRho_Tot  , *nBs2DsDsstPiRhoEvts);
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

    RooRealVar* g4_f1 = NULL;
    RooRealVar* g4_f2 = NULL; 
    if( dim > 2)
      {
	TString g4_f1_Name = "PID1_frac";
	g4_f1 =GetObservable(workInt, g4_f1_Name, debug);
	
	TString g4_f2_Name = "PID2_frac";
	g4_f2 =GetObservable(workInt, g4_f2_Name, debug);
      }
    TString g5_f1_Name = "g5_f1_frac";
    RooRealVar* g5_f1 =GetObservable(workInt, g5_f1_Name, debug);

    TString Mode = CheckDMode(samplemode,debug);
    if ( Mode == "" ) { Mode = CheckKKPiMode(samplemode, debug); }

    TString cBVarName = "CombBkg_slope_Bs_"+Mode;  
    RooRealVar* cBVar = GetObservable(workInt, cBVarName, debug);

    RooRealVar* cDVar = NULL;
    if (dim > 1)
      {
	TString cDVarName = "CombBkg_slope_Ds_"+Mode;
        cDVar =GetObservable(workInt, cDVarName, debug);
      }
    
    TString fracCombName = "CombBkg_fracComb_"+Mode;
    RooRealVar* fracComb =GetObservable(workInt, fracCombName, debug);

    TString lumRatioName = "lumRatio";
    RooRealVar* lumRatio =GetObservable(workInt, lumRatioName, debug);

    RooAbsPdf* pdf_SignalDs = NULL; 
    if (dim > 1)
      {
	TString signalDsName = "DblCBPDF_Ds_"+samplemode;
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
	    pdf_Bd2DsK_PIDK = ObtainPIDKShape(work, m, sam, *lumRatio, true, debug);
	  }
	if ( dim > 1 )
	  {
	    pdf_Bd2DsK_Ds = pdf_SignalDs;
	  }
	m = "Bd2DsK"; 
	pdf_Bd2DsK_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bd2DsK, pdf_Bd2DsK_Ds, pdf_Bd2DsK_PIDK, dim, debug  );
      }
    // -------------------------------- Create Combinatorial Background --------------------------------------------//                       

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
	    pdf_CombPi_PIDK = ObtainPIDKShape(work, m, sam, *lumRatio, false, debug);
	    m = "CombK";
	    pdf_CombK_PIDK = ObtainPIDKShape(work, m, sam, *lumRatio,  false, debug);
	    m = "CombP";
	    pdf_CombP_PIDK = ObtainPIDKShape(work, m, sam, *lumRatio,  false, debug);
	    
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
    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//                      

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;
    
    RooProdPdf* pdf_Bd2DK_Tot = NULL;
    RooExtendPdf* epdf_Bd2DK  = NULL;

    if ( valBd2DK != 0.0 )
      {
	m = "Bd2DK";
	pdf_Bd2DK_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);
	
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
	pdf_Bd2DPi_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);
	
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
	m = "Bs2DsKst";
	pdf_Bs2DsKst_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);
	
	name="PhysBkgBs2DsDsstKKstPdf_m_"+samplemode+"_Tot";
	pdf_Bs2DsDsstKKst_Tot = new RooAddPdf(name.Data(), name.Data(), *pdf_Bd2DsK_Tot, *pdf_Bs2DsKst_Tot, *g1_f1);
	CheckPDF(pdf_Bs2DsDsstKKst_Tot, debug);

	name = "Bs2DsDsstKKstEPDF_m_"+samplemode;
	epdf_Bs2DsDsstKKst = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstKKst_Tot->GetTitle(), *pdf_Bs2DsDsstKKst_Tot  , *nBs2DsDssKKstEvts   );
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
	pdf_Bs2DsRho_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);
	
	m = "Bs2DsstPi";
	pdf_Bs2DsstPi_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);
	
	m = "Bs2DsPi_"+samplemode;
	pdf_Bs2DsPi_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);
	
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
	pdf_Lb2Dsp_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);
	
	m = "Lb2Dsstp";
	pdf_Lb2Dsstp_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, pdf_SignalDs, dim, debug);
	
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
	pdf_Lb2LcK_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);
	
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
	pdf_Lb2LcPi_Tot = ObtainRooProdPdfForMDFitter(work, m, sam, *lumRatio, NULL, dim, debug);
	
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

}
