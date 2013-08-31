//---------------------------------------------------------------------------//
//                                                                           //
//                                                                           //
//  Propertime resolution models for Bx -> Dx h                              //
//                                                                           //
//  Header file                                                              //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 19 / 05 / 2011                                                  //
//                                                                           //
//  Authors: Agnieszka Dziurda                                               //
//  Date   : 20/08/2013                                                      //
//                                                                           //
//---------------------------------------------------------------------------//

#ifndef PROPERTIMERESOLUTIONMODELS_H
#define PROPERTIMERESOLUTIONMODELS_H 1

// STL includes

// ROOT and RooFit includes
#include "RooRealVar.h"
#include "RooResolutionModel.h"


namespace PTResModels {
  
  //=============================================================================
  // Helper function returning a resolution model by name
  // Implemented models:
  //   "truth"          --> RooTruthModel
  //   "Gaussian"       --> RooGaussModel
  //   "DoubleGaussian" --> RooAddModel of 2 RooGaussModel
  //=============================================================================
  RooResolutionModel* getPTResolutionModel( const char* modelName,
                                            RooRealVar& time,
                                            const char* prefix = "Sig",
                                            bool debug = false,
                                            double scalingfactor = 1.,
                                            double biasonmean = 0.
                                            );
  
  //=============================================================================
  //
  //=============================================================================
  
  RooResolutionModel* tripleGausResolutionModel( RooRealVar& time,
                                                 bool fixparameters = true,
                                                 bool fixfractions = true,
                                                 bool extended = true,
                                                 bool debug = false,
                                                 double scalingfactor = 1.,
                                                 double biasonmean = 0.
                                                 );
  
  //=============================================================================
  //
  //=============================================================================
  RooResolutionModel* tripleGausResolutionModel( RooRealVar& time,
                                                 double scalingfactor,
                                                 double biasonmean, 
                                                 double sigma1,
                                                 double sigma2,
                                                 double sigma3,
                                                 double frac1,
                                                 double frac2,
						 bool debug = false
                                                 );

  //=============================================================================
  //
  //=============================================================================
  
  RooResolutionModel* tripleGausResolutionModel( RooRealVar& time,
                                                 double scalingfactor,
                                                 double biasonmean,
                                                 double sigma1,
                                                 double sigma2,
                                                 double sigma3,
                                                 double frac1,
                                                 double frac2,
                                                 double frac3,
						 bool debug = false
                                                 );


}

//=============================================================================

#endif  // PROPERTIMERESOLUTIONMODELS_H
