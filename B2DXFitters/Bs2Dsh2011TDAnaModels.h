#ifndef Bs2Dsh2011TDAnaModels_H
#define Bs2Dsh2011TDAnaModels_H 1


#include "RooRealVar.h"
#include "RooAbsPdf.h"
#include "RooResolutionModel.h"
#include "RooWorkspace.h"
#include "RooAddPdf.h"
#include "RooHistPdf.h"
#include "RooProdPdf.h"
#include "RooArgList.h"

namespace Bs2Dsh2011TDAnaModels {
  
  //===============================================================================
  // Double crystal ball function where:
  // mean, sigma1, sigma2 are RooRealVar
  // alpha1, alpha2, n1, n2 and fraction are double
  //===============================================================================

  RooAbsPdf* buildDoubleCBEPDF_fix( RooAbsReal& obs,
                                    RooRealVar& mean,
                                    RooRealVar& sigma1,
                                    double alpha1,
                                    double n1,
                                    RooRealVar& sigma2,
                                    double alpha2,
                                    double n2,
                                    double frac,
                                    RooRealVar& nEvents,
                                    const char* prefix,
                                    const char* bName,
                                    bool debug = false
                                    );

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
                                    bool debug = false);

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
                                   bool debug);

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
				    bool debug);

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
				   bool debug = false);

  RooAbsPdf* buildDoubleGEPDF_sim( RooAbsReal& obs,
                                   RooRealVar& mean,
                                   RooRealVar& sigma1,
                                   RooRealVar& sigma2,
                                   RooRealVar& frac,
                                   RooFormulaVar& nEvents,
                                   TString prefix,
                                   TString bName,
                                   bool extendend,
                                   bool debug = false);



  //===============================================================================
  // Double crystal ball function where:
  // mean, sigma1, sigma2 are RooFormulaVar
  // alpha1, alpha2, n1, n2 and fraction are double
  // this function is used in case:
  // Bd->DsPi (for Bs->DsPi mass model)
  // Bd->DsK (for Bs->DsK mass model)
  //===============================================================================


  RooAbsPdf* buildBdDsX(RooAbsReal& obs,
			RooFormulaVar &meanVar,
			RooFormulaVar &sigma1Var,
			double alpha1,
			double n1,
			RooFormulaVar &sigma2Var,
			double alpha2,
			double n2,
			double frac,
			TString& samplemode,
			TString &name,
			bool debug = false
			);

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
                         bool debug);

  		      
  //===============================================================================
  // Read Bs (or Ds for dsMass == true ) shape from workspace
  //===============================================================================

  RooAbsPdf* ObtainMassShape(RooWorkspace* work,
                             TString mode,
			     TString year, 
			     bool dsMass,
			     RooRealVar& lumRatio,
			     bool debug = false);

  //===============================================================================
  // Read PIDK shape from workspace 
  //===============================================================================

  RooAbsPdf* ObtainPIDKShape(RooWorkspace* work,
                             TString mode,
			     TString pol,
			     TString year,
                             RooRealVar& lumRatio,
			     bool DsMode = false,
			     bool debug = false);

  //===============================================================================
  // Create RooProdPdf with (Bs, Ds, PIDK) shapes from workspace  
  //===============================================================================
  
  RooProdPdf* ObtainRooProdPdfForMDFitter(RooWorkspace* work,
                                          TString mode,
					  TString pol,
					  TString year,
                                          RooRealVar& lumRatio,
					  RooAbsPdf* pdf_Ds = NULL,
					  Int_t dim = 3, 
                                          bool debug = false);

  RooProdPdf* GetRooProdPdfDim(TString& mode,
			       TString& samplemode, 
			       RooAbsPdf* pdf_Bs = NULL,
			       RooAbsPdf* pdf_Ds = NULL,
			       RooAbsPdf* pdf_PIDK = NULL,
			       Int_t dim = 3,
			       bool debug = false);
  //===============================================================================
  // Create RooProdPdf with (Bs mass, Ds mass, PIDK, time) shapes from workspace
  //===============================================================================

  RooProdPdf* ObtainRooProdPdfForFullFitter(RooWorkspace* work,
                                            TString mode,
                                            TString pol,
					    TString year,
                                            RooRealVar& lumRatio,
                                            RooAbsPdf* pdf_Time,
                                            RooAbsPdf* pdf_Ds = NULL,
                                            bool debug = false);

  //===============================================================================
  // Create combinatorial background shape for Ds mass: double exponential
  //===============================================================================

  RooAddPdf* ObtainComboBs(RooAbsReal& mass,
			   RooRealVar& cBVar,
			   RooRealVar& cBVar2,
			   RooRealVar& frac,
			   TString& Mode,
			   bool debug = false);

  //===============================================================================
  // Create combinatorial background shape for Ds mass: 
  //     exponential + signal double CB.
  //===============================================================================

  RooAddPdf* ObtainComboDs(RooAbsReal& massDs,
			   RooRealVar& cDVar,
			   RooRealVar& fracDsComb,
			   RooAbsPdf* pdf_SignalDs,
			   TString& Mode,
			   bool debug = false);
    
  //===============================================================================
  // Background 2D model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsPi_BKG_MDFitter( RooAbsReal& mass, RooAbsReal& massDs,
					 RooWorkspace* work,RooWorkspace* workInt,
					 RooAbsPdf* pdf_BdDsPi,
					 TString &samplemode, Int_t dim, bool debug = false);
  
  //===============================================================================
  // Background 2D model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf*  build_Bs2DsK_BKG_MDFitter(RooAbsReal& mass, RooAbsReal& massDs,
					RooWorkspace* work, RooWorkspace* workInt,
					RooAddPdf* pdf_Bd2DsK, 
					TString &samplemode, Int_t dim = 3, bool debug = false);

  //===============================================================================
  // Load RooKeysPdf from workspace.
  //===============================================================================
  RooKeysPdf* GetRooKeysPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug = false);
  
  //===============================================================================
  // Load RooHistPdf from workspace.
  //===============================================================================
  RooHistPdf* GetRooHistPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug = false);

  //===============================================================================
  // Load RooAddPdf from workspace.
  //===============================================================================
  RooAddPdf* GetRooAddPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug=false);

  //===============================================================================
  // Load RooBinned1DPdf from workspace.
  //===============================================================================
  RooAbsPdf* GetRooBinned1DFromWorkspace(RooWorkspace* work, TString& name, bool  debug = false);
  
  //===============================================================================
  // Load RooAbsPdf from workspace.
  //===============================================================================
  RooAbsPdf* GetRooAbsPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug  = false );

  //===============================================================================
  // Check PDF (whether is null).
  //===============================================================================
  bool CheckPDF(RooAbsPdf* pdf, bool debug = false);
  
  //===============================================================================
  // Check RooRealVar (whether is null).
  //===============================================================================
  bool CheckVar(RooRealVar* var, bool debug = false); 

  RooArgList* AddEPDF(RooArgList* list, RooExtendPdf* pdf, RooRealVar *numEvts, bool debug = false); 

  RooAbsPdf* build_Combinatorial_MDFitter(RooAbsReal& mass,
                                          RooAbsReal& massDs,
                                          RooWorkspace* work,
                                          RooWorkspace* workInt,
                                          TString samplemode,
					  std::vector <TString> types,
                                          std::vector <TString> pdfNames,
                                          std::vector <TString> pidk,
                                          Int_t dim,
                                          bool debug);

  RooAbsPdf* ObtainSignalMassShape(RooAbsReal& mass,
                                   RooWorkspace* work,
                                   RooWorkspace* workInt,
                                   TString samplemode,
                                   TString type,
				   bool extended, 
                                   bool debug);


  RooAbsPdf* build_Signal_MDFitter(RooAbsReal& mass,
                                   RooAbsReal& massDs,
                                   RooWorkspace* work,
                                   RooWorkspace* workInt,
                                   TString samplemode,
				   TString decay, 
                                   std::vector <TString> types,
                                   Int_t dim,
                                   bool debug);


}

#endif
