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
#include "B2DXFitters/Bs2DshDsHHHPi0Models.h"
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"

using namespace std;
using namespace GeneralUtils;
using namespace Bs2Dsh2011TDAnaModels;

namespace Bs2DshDsHHHPi0Models {

//Lorenzo
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
    
    RooArgList* list = new RooArgList();

    /*
    TString nCombBkgName = "nCombBkg_"+samplemode+"_Evts";
    RooRealVar* nCombBkgEvts = GetObservable(workInt, nCombBkgName, debug);
    Double_t valCombBkg = nCombBkgEvts->getValV();
    */
    TString nBs2DsDsstPiRhoName = "nBs2DsDsstPiRho_"+samplemode+"_Evts";
    RooRealVar* nBs2DsDsstPiRhoEvts = GetObservable(workInt, nBs2DsDsstPiRhoName, debug);
    Double_t valBs2DsDsstPiRho = nBs2DsDsstPiRhoEvts->getValV();

    TString nBd2DPiName = "nBd2DPi_"+samplemode+"_Evts";
    RooRealVar*  nBd2DPiEvts = GetObservable(workInt, nBd2DPiName, debug);
    Double_t valBd2DPi = nBd2DPiEvts->getValV();

    TString nLb2LcPiName = "nLb2LcPi_"+samplemode+"_Evts";
    RooRealVar* nLb2LcPiEvts =  GetObservable(workInt, nLb2LcPiName, debug);
    Double_t valLb2LcPiEvts = nLb2LcPiEvts->getValV();

    TString nBd2DsstPiName = "nBd2DsstPi_"+samplemode+"_Evts";
    RooRealVar*  nBd2DsstPiEvts = GetObservable(workInt, nBd2DsstPiName, debug);
    Double_t valBd2DsstPi = nBd2DsstPiEvts->getValV();

    TString g1_f1_Name = "g1_f1_frac";
    RooRealVar* g1_f1 = GetObservable(workInt, g1_f1_Name, debug);

    TString Mode = CheckDMode(samplemode,debug);
    if ( Mode == "" ) { Mode = CheckKKPiMode(samplemode, debug); }
    /*
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
    */
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
    }
    TString name="";
    TString m = "";
    TString sam = CheckPolarity(samplemode,debug);
    TString y = CheckDataYear(samplemode,debug); 

    RooAbsPdf* pdf_Bd2DsPi_PIDK = NULL;
    RooAbsPdf* pdf_Bd2DsPi_Ds = NULL;
    RooProdPdf* pdf_Bd2DsPi_Tot = NULL;

    if ( valBs2DsDsstPiRho != 0.0 )
      {
	m = "Bs2DsPi_"+samplemode;
	if ( dim > 2 )
	  {
	    pdf_Bd2DsPi_PIDK = ObtainPIDKShape(work, m, sam, y,*lumRatio, true, debug);
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
      
    RooAbsPdf* pdf_combBkg = NULL;
    RooAddPdf* pdf_combBkg_Ds = NULL;
    RooAbsPdf* pdf_combBkg_PIDK1 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK2 = NULL;
    RooAddPdf* pdf_combBkg_PIDK = NULL;
    RooProdPdf* pdf_combBkg_Tot = NULL;
    RooExtendPdf* epdf_combBkg   = NULL;

    if ( valCombBkg != 0.0 )
      {
	pdf_combBkg = ObtainComboBs(mass, *cB1Var, *cB2Var, *fracBsComb, Mode, debug);
    
	if ( dim > 1)
	  {
	    pdf_combBkg_Ds = ObtainComboDs(massDs, *cDVar, *fracDsComb, pdf_SignalDs, Mode, debug); 
	  }
	
	if (dim >2)
	  {
	    m = "Comb";
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
	m = "Bd2DPi";
	pdf_Bd2DPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);
	
	name = "Bd2DPiEPDF_m_"+samplemode;
	epdf_Bd2DPi = new RooExtendPdf( name.Data(),pdf_Bd2DPi_Tot->GetTitle(), *pdf_Bd2DPi_Tot, *nBd2DPiEvts);
	CheckPDF(epdf_Bd2DPi, debug);
	list = AddEPDF(list, epdf_Bd2DPi, nBd2DPiEvts, debug);
      }

    //-----------------------------------------//

    RooProdPdf* pdf_Bd2DsstPi_Tot = NULL;
    RooExtendPdf* epdf_Bd2DsstPi = NULL;
    
    if ( valBd2DsstPi != 0 )
      {
	m = "Bd2DsstPi";
	pdf_Bd2DsstPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bd2DsstPiEPDF_m_"+samplemode;
	epdf_Bd2DsstPi = new RooExtendPdf(name.Data() , pdf_Bd2DsstPi_Tot->GetTitle(), *pdf_Bd2DsstPi_Tot, *nBd2DsstPiEvts );
	CheckPDF(epdf_Bd2DsstPi, debug);
	list = AddEPDF(list, epdf_Bd2DsstPi, nBd2DsstPiEvts, debug);
      }

    RooProdPdf* pdf_Lb2LcPi_Tot = NULL;
    RooExtendPdf* epdf_Lb2LcPi = NULL;

    if ( valLb2LcPiEvts != 0 )
      {
	m = "Lb2LcPi";
	pdf_Lb2LcPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);

	name = "Lb2LcPiEPDF_m_"+samplemode;
	epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi_Tot->GetTitle(), *pdf_Lb2LcPi_Tot, *nLb2LcPiEvts );
	CheckPDF(epdf_Lb2LcPi, debug);
	list = AddEPDF(list, epdf_Lb2LcPi, nLb2LcPiEvts, debug);
      }
    // --------------------------------- Create RooAddPdf -------------------------------------------------/

    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    RooAddPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;

    if ( valBs2DsDsstPiRho != 0.0 )
      {
	m = "Bs2DsstPi";
	pdf_Bs2DsstPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name="PhysBkgBs2DsDsstPiPdf_m_"+samplemode+"_Tot";
	pdf_Bs2DsDsstPiRho_Tot = new RooAddPdf( name.Data(),
						name.Data(),
						RooArgList(*pdf_Bs2DsstPi_Tot, *pdf_Bd2DsPi_Tot), 
						RooArgList(*g1_f1) 
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
  // Background 3D model for Bs->DsK (Ds--> HHHPi0) mass fitter.
  //===============================================================================
  RooAbsPdf* build_Bs2DsK_BKG_HHHPi0( RooAbsReal& mass,
					 RooAbsReal& massDs,
					 RooWorkspace* work,
					 RooWorkspace* workInt,
					 RooAbsPdf* pdf_Bd2DsK,
					 TString &samplemode,
					 Int_t dim, 
					 bool debug
					 ){
    if (debug == true)
      {
        cout<<"------------------------------------"<<endl;
	cout<<"=====> Build background model BsDsK"<<endl;
        cout<<"------------------------------------"<<endl;
      }
    pdf_Bd2DsK = NULL;

    RooArgList* list = new RooArgList();
    /*
    TString nCombBkgName = "nCombBkg_"+samplemode+"_Evts";
    RooRealVar* nCombBkgEvts = GetObservable(workInt, nCombBkgName, debug);
    Double_t valCombBkg = nCombBkgEvts->getValV();
    */
    TString nBd2DKName = "nBd2DK_"+samplemode+"_Evts";                                                                                       
    RooRealVar*  nBd2DKEvts = GetObservable(workInt, nBd2DKName, debug);
    Double_t valBd2DK = nBd2DKEvts->getValV(); 

    TString nBd2DsKName = "nBd2DsK_"+samplemode+"_Evts";                                                                                       
    RooRealVar*  nBd2DsKEvts = GetObservable(workInt, nBd2DsKName, debug);
    Double_t valBd2DsK = nBd2DsKEvts->getValV();

    TString nBd2DsstKName = "nBd2DsstK_"+samplemode+"_Evts";                                                                                       
    RooRealVar*  nBd2DsstKEvts = GetObservable(workInt, nBd2DsstKName, debug);
    Double_t valBd2DsstK = nBd2DsstKEvts->getValV(); 

    TString nBs2DsstKName = "nBs2DsstK_"+samplemode+"_Evts";                                                                                       
    RooRealVar*  nBs2DsstKEvts = GetObservable(workInt, nBs2DsstKName, debug);
    Double_t valBs2DsstK = nBs2DsstKEvts->getValV(); 

    TString nLb2LcKName = "nLb2LcK_" +samplemode + "_Evts";
    RooRealVar* nLb2LcKEvts =  GetObservable(workInt, nLb2LcKName, debug);
    Double_t valLb2LcK = nLb2LcKEvts->getValV(); 
	
    TString nBs2DsDsstPiRhoName = "nBs2DsDsstPi_"+samplemode+"_Evts";
    RooRealVar* nBs2DsDsstPiRhoEvts = GetObservable(workInt, nBs2DsDsstPiRhoName, debug);
    Double_t valBs2DsDsstPiRho = nBs2DsDsstPiRhoEvts->getValV();
    

    TString g1_f1_Name = "g1_f1_frac";
    RooRealVar* g1_f1 = GetObservable(workInt, g1_f1_Name, debug);

    TString Mode = CheckDMode(samplemode,debug);
    if ( Mode == "" ) { Mode = CheckKKPiMode(samplemode, debug); }
    /*
    TString cB1VarName = "CombBkg_slope_Bs1_"+Mode;
    RooRealVar* cB1Var = GetObservable(workInt, cB1VarName, debug);
    
    RooRealVar* cDVar = NULL;
    if (dim > 1)
      {
	TString cDVarName = "CombBkg_slope_Ds_"+Mode;
	cDVar =GetObservable(workInt, cDVarName, debug);
      }

   
    RooRealVar* fracDsComb = NULL;
    if (dim>1)
      {
	TString fracDsCombName = "CombBkg_fracDsComb_"+Mode;
	fracDsComb =GetObservable(workInt, fracDsCombName, debug);
      }
    */
    RooRealVar* g4_f1 = NULL;
    if( dim > 2)
      {
        TString g4_f1_Name = "PID1_frac";
        g4_f1 =GetObservable(workInt, g4_f1_Name, debug);
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
                              
    // ------------------------------------------ Read BsDsK ----------------------------------------------------//
    if (debug == true){
      cout<<"-------------------------- Read BsDsK -------------------------------"<<endl;
    }
    TString name="";
    TString m = "";
    TString sam = CheckPolarity(samplemode,debug);
    TString y = CheckDataYear(samplemode,debug); 

    // -------------------------------- Create Combinatorial Background --------------------------------------------//
    /*
    if (debug == true) cout<<"---------------  Create combinatorial background PDF -----------------"<<endl;
      
    RooAbsPdf* pdf_combBkg = NULL;
    RooAddPdf* pdf_combBkg_Ds = NULL;
    RooAbsPdf* pdf_CombK_PIDK = NULL;
    RooAbsPdf* pdf_CombPi_PIDK = NULL;
    RooAddPdf* pdf_combBkg_PIDK = NULL;
    RooProdPdf* pdf_combBkg_Tot = NULL;
    RooExtendPdf* epdf_combBkg   = NULL;


    if ( valCombBkg != 0.0 )
      {
	pdf_combBkg = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, *cB1Var);
    
	if ( dim > 1)
	  {
	    pdf_combBkg_Ds = ObtainComboDs(massDs, *cDVar, *fracDsComb, pdf_SignalDs, Mode, debug); 
	  }

	if (dim >2)
	  {
	    m = "CombPi";
	    pdf_CombPi_PIDK = ObtainPIDKShape(work, m, sam, y, *lumRatio, false, debug);
	    m = "CombK";
	    pdf_CombK_PIDK = ObtainPIDKShape(work, m, sam, y, *lumRatio,  false, debug);
	    
	    name = "ShapePIDKAll_Comb_"+sam;
	    pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
					      name.Data(),
					      RooArgList(*pdf_CombK_PIDK,*pdf_CombPi_PIDK),
					      RooArgList(*g4_f1),
					      true);
	    CheckPDF(pdf_combBkg_PIDK, debug);
	    
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
    
    RooProdPdf* pdf_Bd2DK_Tot = NULL;
    RooExtendPdf* epdf_Bd2DK = NULL;
    if ( valBd2DK != 0)
      {
	m = "Bd2DK";
	pdf_Bd2DK_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);
	
	name = "Bd2DKEPDF_m_"+samplemode;
	epdf_Bd2DK = new RooExtendPdf(name.Data() , pdf_Bd2DK_Tot->GetTitle(), *pdf_Bd2DK_Tot, *nBd2DKEvts );
	CheckPDF(epdf_Bd2DK, debug);
	list = AddEPDF(list,  epdf_Bd2DK, nBd2DKEvts, debug);
      }


    RooProdPdf* pdf_Bd2DsK_Tot = NULL;
    RooExtendPdf* epdf_Bd2DsK = NULL;
    if ( valBd2DsK != 0 )
      {
	m = "Bd2DsK";
	pdf_Bd2DsK_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bd2DsKEPDF_m_"+samplemode;
	epdf_Bd2DsK = new RooExtendPdf(name.Data() , pdf_Bd2DsK_Tot->GetTitle(), *pdf_Bd2DsK_Tot, *nBd2DsKEvts );
	CheckPDF(epdf_Bd2DsK, debug);
	list = AddEPDF(list,  epdf_Bd2DsK, nBd2DsKEvts, debug);
      }

    RooProdPdf* pdf_Bd2DsstK_Tot = NULL;
    RooExtendPdf* epdf_Bd2DsstK = NULL;
    if ( valBd2DsstK != 0)
      {
	m = "Bd2DsstK";
	pdf_Bd2DsstK_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bd2DsstKEPDF_m_"+samplemode;
	epdf_Bd2DsstK = new RooExtendPdf(name.Data() , pdf_Bd2DsstK_Tot->GetTitle(), *pdf_Bd2DsstK_Tot, *nBd2DsstKEvts );
	CheckPDF(epdf_Bd2DsstK, debug);
	list = AddEPDF(list,  epdf_Bd2DsstK, nBd2DsstKEvts, debug);
      }

    RooProdPdf* pdf_Bs2DsstK_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsstK = NULL;
    if ( valBs2DsstK != 0)
      {
	m = "Bs2DsstK";
	pdf_Bs2DsstK_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);

	name = "Bs2DsstKEPDF_m_"+samplemode;
	epdf_Bs2DsstK = new RooExtendPdf(name.Data() , pdf_Bs2DsstK_Tot->GetTitle(), *pdf_Bs2DsstK_Tot, *nBs2DsstKEvts );
	CheckPDF(epdf_Bs2DsstK, debug);
	list = AddEPDF(list,  epdf_Bs2DsstK, nBs2DsstKEvts, debug);
      }

    RooProdPdf* pdf_Lb2LcK_Tot = NULL;
    RooExtendPdf* epdf_Lb2LcK = NULL;
    if ( valLb2LcK != 0)
      {
	m = "Lb2LcK";
	pdf_Lb2LcK_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);

	name = "Lb2LcKEPDF_m_"+samplemode;
	epdf_Lb2LcK = new RooExtendPdf(name.Data() , pdf_Lb2LcK_Tot->GetTitle(), *pdf_Lb2LcK_Tot, *nLb2LcKEvts );
	CheckPDF(epdf_Lb2LcK, debug);
	list = AddEPDF(list,  epdf_Lb2LcK, nLb2LcKEvts, debug);
      }

    RooProdPdf* pdf_Bs2DsPi_Tot = NULL;
    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    RooAddPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;

    if ( valBs2DsDsstPiRho != 0.0 )
      {
	m = "Bs2DsPi";
	pdf_Bs2DsPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
   
	m = "Bs2DsstPi";
	pdf_Bs2DsstPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name="PhysBkgBs2DsDsstPiPdf_m_"+samplemode+"_Tot";
	pdf_Bs2DsDsstPiRho_Tot = new RooAddPdf( name.Data(),
						name.Data(),
						RooArgList(*pdf_Bs2DsPi_Tot, *pdf_Bs2DsstPi_Tot), //, *pdf_Bs2DsRho), //,*pdf_Bs2DsstRho),
						RooArgList(*g1_f1) //,g1_f2), rec
						);
	CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);
       
	name = "Bs2DsDsstPiEPDF_m_"+samplemode;
	epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho_Tot-> GetTitle(), *pdf_Bs2DsDsstPiRho_Tot  , *nBs2DsDsstPiRhoEvts);
	CheckPDF(epdf_Bs2DsDsstPiRho, debug);
	list = AddEPDF(list,  epdf_Bs2DsDsstPiRho, nBs2DsDsstPiRhoEvts, debug);
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

}
