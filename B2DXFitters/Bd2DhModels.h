//---------------------------------------------------------------------------//
//                                                                           //
//  RooFit models for Bd -> D h                                              //
//                                                                           //
//  Header file                                                              //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 18 / 05 / 2011                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

#ifndef BD2DHMODELS_H
#define BD2DHMODELS_H 1

// STL includes

// ROOT and RooFit includes
#include "RooRealVar.h"
#include "RooStringVar.h"
#include "RooAbsPdf.h"
#include "RooResolutionModel.h"
#include "RooWorkspace.h"
#include "TString.h"
#include "RooAbsReal.h" 

namespace Bd2DhModels {

  RooAbsPdf* build_Bd2DPi_BKG_MDFitter( RooAbsReal& mass,
					RooAbsReal& massDs,
					RooWorkspace* work,
					RooWorkspace* workInt,
					TString &samplemode,
					TString merge,
					Int_t dim,
					bool debug = true
					);

  RooAbsPdf* buildJohnsonSUPDF( RooAbsReal& obs,
                                RooWorkspace* workInt,
                                TString samplemode,
                                TString typemode,
                                bool debug = true);
  
  RooAbsPdf* buildJohnsonSUPlusGaussianPDF( RooAbsReal& obs,
                                            RooWorkspace* workInt,
                                            TString samplemode,
                                            TString typemode,
                                            bool debug = true);
  
  RooAbsPdf* buildJohnsonSUPlus2GaussianPDF( RooAbsReal& obs,
                                             RooWorkspace* workInt,
                                             TString samplemode,
                                             TString typemode,
                                             bool sameMean,
                                             bool debug);
  
} // end of namespace

//=============================================================================

#endif  // BD2DHMODELS_H
 
