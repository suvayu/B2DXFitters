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
				   bool debug = false);

  RooAbsPdf* buildDoubleGEPDF_sim( RooAbsReal& obs,
                                   RooRealVar& mean,
                                   RooRealVar& sigma1,
                                   RooRealVar& sigma2,
                                   RooRealVar& frac,
                                   RooFormulaVar& nEvents,
                                   const char* prefix,
                                   const char* bName,
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
  
  //===============================================================================
  // Background model for Bs->DsPi mass fitter.
  //===============================================================================
  /*
  RooAbsPdf* buildBsDsPi_sim( RooRealVar& mass,
			      RooWorkspace* work,
                              RooRealVar& nCombBkgEvts,
                              RooRealVar& nBd2DPiEvts,
                              //RooFormulaVar&  nBd2DPiEvts,
			      RooRealVar& nBs2DsDsstPiRhoEvts,
                              RooRealVar& g1_f1,
			      RooRealVar& g1_f2,
                              RooRealVar& nLb2LcPiEvts,
                              RooRealVar& nBdDsPi,
                              RooAbsPdf* pdf_BdDsPi,
			      RooRealVar& nBdDsstPi,
			      RooRealVar& nBd2DsRhoEvts,
                              RooRealVar& nBd2DstPiEvts,
			      RooRealVar& nBs2DsKEvts,
                              RooRealVar& cB1Var,
                              RooRealVar& cB2Var,
                              RooRealVar& fracComb,
			      TString &samplemode,
			      RooRealVar& lumRatio,
                              bool toys,
                              bool debug = false
                              );
  */			      
  //===============================================================================
  // Read Bs (or Ds for dsMass == true ) shape from workspace
  //===============================================================================

  RooAbsPdf* ObtainMassShape(RooWorkspace* work,
                             TString& mode,
			     bool dsMass,
			     RooRealVar& lumRatio,
			     bool debug = false);

  //===============================================================================
  // Read PIDK shape from workspace 
  //===============================================================================

  RooAbsPdf* ObtainPIDKShape(RooWorkspace* work,
                             TString& mode,
			     TString& pol,
                             RooRealVar& lumRatio,
			     bool DsMode = false,
			     bool debug = false);

  //===============================================================================
  // Create RooProdPdf with (Bs, Ds, PIDK) shapes from workspace  
  //===============================================================================
  
  RooProdPdf* ObtainRooProdPdfForMDFitter(RooWorkspace* work,
                                          TString& mode,
					  TString& pol,
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
                                            TString& mode,
                                            TString& pol,
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
  // Background 2D model for Bs->DsPi (Ds --> HHHPi0) mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsPi_BKG_HHHPi0( RooAbsReal& mass,
					 RooAbsReal& massDs,
					 RooWorkspace* work,
					 RooWorkspace* workInt,
					 /*
					 RooRealVar& nCombBkgEvts,
					 RooRealVar& nBd2DPiEvts,
					 RooRealVar& nBs2DsDsstPiRhoEvts,
					 RooRealVar& g1_f1,
					 RooRealVar& g1_f2,
					 RooRealVar& nLb2LcPiEvts,
					 RooRealVar& nBdDsPi,
					 */
					 RooAbsPdf* pdf_BdDsPi,
					 /*
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
					 */
					 TString &samplemode,
					 Int_t dim, 
					 //RooRealVar& lumRatio,
					 bool debug);


  //===============================================================================
  // Background 2D model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsPi_BKG_MDFitter( RooAbsReal& mass,
					 RooAbsReal& massDs,
					 RooWorkspace* work,
					 RooWorkspace* workInt,
					 /*
					 RooRealVar& nCombBkgEvts,
					 RooRealVar& nBd2DPiEvts,
					 RooRealVar& nBs2DsDsstPiRhoEvts,
					 RooRealVar& g1_f1,
					 RooRealVar& g1_f2,
					 RooRealVar& nLb2LcPiEvts,
					 RooRealVar& nBdDsPi,
					 */
					 RooAbsPdf* pdf_BdDsPi,
					 /*
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
					 */
					 TString &samplemode,
					 Int_t dim, 
					 //RooRealVar& lumRatio,
					 bool debug);

  //===============================================================================
  // Background model for Bs->DsK mass fitter.
  //===============================================================================
  /*
  RooAbsPdf* buildBsDsK_sim(RooRealVar& mass,
                            RooWorkspace* work,
			    RooAddPdf* pdf,
                            RooRealVar& nCombBkgEvts,
			    RooRealVar& nBs2DsDsstPiRhoEvts,
                            //RooFormulaVar& nBs2DsDsstPiRhoEvts,
			    RooRealVar& nBs2DsDssKKstEvts,
                            RooRealVar& nLb2DsDsstpEvts,
                            //RooFormulaVar& nBd2DKEvts,
                            RooRealVar& nBd2DKEvts,
                            RooRealVar& nLb2LcKEvts,
			    RooRealVar&g1_f1,
                            RooRealVar& g1_f2,
                            RooRealVar& g1_f3,
			    RooRealVar& g2_f1,
			    RooRealVar& g2_f2,
			    RooRealVar& g2_f3,
			    RooRealVar& g3_f1,
			    TString &sample,
			    TString &mode,
			    bool toys,
			    bool debug = false);

  */			    
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
}

#endif
