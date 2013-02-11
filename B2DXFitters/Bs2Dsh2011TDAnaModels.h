#ifndef Bs2Dsh2011TDAnaModels_H
#define Bs2Dsh2011TDAnaModels_H 1


#include "RooRealVar.h"
#include "RooAbsPdf.h"
#include "RooResolutionModel.h"
#include "RooWorkspace.h"
#include "RooAddPdf.h"
#include "RooHistPdf.h"

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
			TString &name,
			bool debug = false
			);
  
  //===============================================================================
  // Background model for Bs->DsPi mass fitter.
  //===============================================================================

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
                              //RooRealVar& N_Bkg_Tot,
                              TString &sam,
			      TString &samplemode,
                              bool toys,
                              bool debug = false
                              );

  //===============================================================================
  // Background model for Bs->DsK mass fitter.
  //===============================================================================
  
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

  //===============================================================================
  // Load RooKeysPdf from workspace.
  //===============================================================================

  RooKeysPdf* GetRooKeysPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug = false);
  RooHistPdf* GetRooHistPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug = false);
  
}

#endif
