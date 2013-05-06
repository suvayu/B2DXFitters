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
				   bool debug);

  RooAbsPdf* buildDoubleGEPDF_sim( RooAbsReal& obs,
                                   RooRealVar& mean,
                                   RooRealVar& sigma1,
                                   RooRealVar& sigma2,
                                   RooRealVar& frac,
                                   RooFormulaVar& nEvents,
                                   const char* prefix,
                                   const char* bName,
                                   bool extendend,
                                   bool debug);



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

  RooAbsPdf* buildBsDsPi_PIDK(RooAbsReal* obs,
                              Double_t c1Var,
                              Double_t c2Var,
                              Double_t f1Var,
                              Double_t f2Var,
                              Double_t sigmaVar,
                              Double_t meanVar,
			      TString& samplemode
			      );



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
                             RooRealVar& cDVar,
                             RooRealVar& fracComb,
			     TString &samplemode,
			     //bool merge,
			     RooRealVar& lumRatio,
			     bool debug);

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
                                            );

  RooAbsPdf* buildBsDsK_PIDK_DoubleGaussian(RooAbsReal* obs,
                                            Double_t mean1Var,
                                            Double_t mean3Var,
                                            Double_t sigma1Var,
                                            Double_t sigma3Var,
                                            Double_t f1Var,
                                            TString& samplemode,
                                            TString& type
                                            );

  RooAbsPdf* buildBsDsK_PIDK_Gaussian(RooAbsReal* obs,
                                      Double_t mean1Var,
                                      Double_t sigma1Var,
                                      TString& samplemode,
                                      TString& type
                                      );
  
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
                                      );




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
			   RooRealVar& g4_f1,
			   RooRealVar& g4_f2,
                           RooAbsPdf* pdf_SignalDs,
			   RooRealVar& cBVar,
			   RooRealVar& cDVar,
			   RooRealVar& fracComb,
			   TString &samplemode,
			   //bool merge,
			   RooRealVar& lumRatio,
			   bool debug);

  //===============================================================================
  // Load RooKeysPdf from workspace.
  //===============================================================================

  RooKeysPdf* GetRooKeysPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug = false);
  RooHistPdf* GetRooHistPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug = false);
  RooAddPdf* GetRooAddPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug=false);
}

#endif
