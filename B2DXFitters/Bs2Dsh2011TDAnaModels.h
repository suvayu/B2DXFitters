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
  RooAbsPdf* buildCrystalBallPDF( RooAbsReal& mass, RooWorkspace* workInt, TString samplemode, TString typemode, bool debug = false);

  RooAbsPdf* buildDoubleCrystalBallPDF( RooAbsReal& mass, RooWorkspace* workInt, TString samplemode,
					TString typemode, bool widthRatio, bool sharedMean, bool debug = false);
  
  //===============================================================================
  // Double gaussian function where all parameters are RooRealVar
  //===============================================================================

  RooAbsPdf* buildGaussPDF( RooAbsReal& mass, RooWorkspace* workInt, TString samplemode, TString typemode, bool shiftMean = false, bool debug = false);
  
  RooAbsPdf* buildDoubleGaussPDF( RooAbsReal& mass, RooWorkspace* workInt, TString samplemode,
                                  TString typemode, bool widthRatio, bool sharedMean, bool shiftMean, bool debug = false);

  RooAbsPdf* buildExponentialPlusGaussPDF(RooAbsReal& mass, RooWorkspace* workInt, TString samplemode, TString typemode, bool sharedMean, bool debug = false);

  RooAbsPdf* buildExponentialPDF(RooAbsReal& mass, RooWorkspace* workInt, TString samplemode, TString typemode, bool debug = false);

  RooAbsPdf* buildDoubleExponentialPDF(RooAbsReal& mass, RooWorkspace* workInt, TString samplemode, TString typemode, bool debug = false);
  
  RooAbsPdf* buildExponentialTimesLinearPDF(RooAbsReal& mass, RooWorkspace* workInt, TString samplemode, TString typemode, bool debug = false);

  RooAbsPdf* buildExponentialPlusSignalPDF(RooAbsReal& mass, RooWorkspace* workInt, TString samplemode, TString typemode, bool debug = false);

  RooAbsPdf* buildIpatiaPDF(RooAbsReal& mass, RooWorkspace* workInt, TString samplemode, TString typemode, bool shiftMean, bool scaleTails, bool debug = false);

  RooAbsPdf* buildApolloniosPDF(RooAbsReal& mass, RooWorkspace* workInt, TString samplemode, TString typemode, bool debug = false);

  RooAbsPdf* buildExponentialPlusDoubleCrystalBallPDF(RooAbsReal& mass, RooWorkspace* workInt, 
						      TString samplemode, TString typemode, bool widthRatio, bool sharedMean, bool debug = false);

  RooAbsPdf* buildComboPIDKPDF(RooAbsReal& mass, RooWorkspace* workInt, RooWorkspace* work, 
			       TString samplemode, TString typemode, TString merge, bool debug = false);
  
  RooAbsPdf* buildShiftedDoubleCrystalBallPDF(RooAbsReal& mass, RooWorkspace* workInt,
					      TString samplemode, TString typemode, bool debug = false);
  		      
  RooExtendPdf* buildExtendPdfSpecBkgMDFit( RooWorkspace* workInt, RooWorkspace* work,
					    TString samplemode, TString typemode, TString typemodeDs = "", TString merge = "", 
					    int dim = 1, TString signalDs = "", bool debug = false);

  RooProdPdf* buildProdPdfSpecBkgMDFit( RooWorkspace* workInt, RooWorkspace* work,
					TString samplemode, TString typemode, TString typemodeDs = "", TString merge = "",  
					int dim = 1, TString signalDs = "", bool debug = false);

  RooAbsPdf* buildMergedSpecBkgMDFit(RooWorkspace* workInt, RooWorkspace* work,
                                     TString samplemode, TString typemode, TString typemodeDs, TString merge,
                                     int dim, TString signalDs, bool debug = false);

  RooAbsPdf* buildMassPdfSpecBkgMDFit(RooWorkspace* work,
				     TString samplemode, TString typemode, TString typemodeDs = "",
				     bool charmShape = false, bool debug = false);

  RooAbsPdf* buildPIDKShapeMDFit(RooWorkspace* work,
				 TString samplemode, TString typemode, TString typemodeDs = "",
				 bool debug = false);
  

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
  // Background 2D model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsPi_BKG_MDFitter( RooAbsReal& mass, RooAbsReal& massDs,
					 RooWorkspace* work,RooWorkspace* workInt,
					 TString &samplemode, TString merge = "", Int_t dim = 1, bool debug = false);
  
  //===============================================================================
  // Background 2D model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf*  build_Bs2DsK_BKG_MDFitter(RooAbsReal& mass, RooAbsReal& massDs,
					RooWorkspace* work, RooWorkspace* workInt,
					TString &samplemode, TString merge = "", Int_t dim =1 , bool debug = false);

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

  Double_t  CheckEvts( RooWorkspace* workInt, TString samplemode, TString typemode, bool debug = false);
  //===============================================================================
  // Check PDF (whether is null).
  //===============================================================================
  bool CheckPDF(RooAbsPdf* pdf, bool debug = false);
  
  //===============================================================================
  // Check RooRealVar (whether is null).
  //===============================================================================
  bool CheckVar(RooRealVar* var, bool debug = false); 

  RooArgList* AddEPDF(RooArgList* list, RooExtendPdf* pdf, RooRealVar *numEvts, bool debug = false); 
  RooArgList* AddEPDF(RooArgList* list, RooExtendPdf* pdf, Double_t ev, bool debug = false);

  RooAbsPdf* ObtainSignalMassShape(RooAbsReal& mass,
                                   RooWorkspace* work,
                                   RooWorkspace* workInt,
                                   TString samplemode,
				   TString typemode, 
                                   TString type,
				   TString pdfName, 
				   bool extended, 
                                   bool debug);


  RooAbsPdf* build_SigOrCombo(RooAbsReal& mass,
			      RooAbsReal& massDs,
			      RooAbsReal& pidVar,
			      RooWorkspace* work,
			      RooWorkspace* workInt,
			      TString samplemode,
			      TString typemode, 
			      TString merge, 
			      TString decay, 
			      std::vector <TString> types,
			      std::vector <std::vector <TString> > pdfNames,
			      std::vector <TString> pidk,
			      Int_t dim,
			      bool debug);
  

  RooAbsPdf* mergePdf(RooAbsPdf* pdf1, RooAbsPdf* pdf2, TString merge, TString lum,RooWorkspace* workInt, bool debug = false);
  RooRealVar* tryVar(TString name, RooWorkspace* workInt, bool debug);
  RooAbsPdf* tryPdf(TString name, RooWorkspace* workInt, bool debug );
  RooAbsPdf* trySignal(TString samplemode, TString varName, RooWorkspace* workInt, bool debug); 

  TString findRooKeysPdf(std::vector <std::vector <TString> > pdfNames, TString var, TString smp, bool debug);


}

#endif
